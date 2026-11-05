-- =============================================================================
-- PHASE 1.2.2 CANONICAL SQL TEST QUERIES (Q01, Q05, Q08, Q11, Q14)
-- Groupware AI Chatbot - Multi-Tenant Isolation & Lifecycle Verification
-- =============================================================================

-- [Q01] Department Hierarchy, Active Manager (HIGH-05), and Active Roster (DEFECT 06)
SELECT
    d.id AS dept_id,
    d.code AS dept_code,
    d.name AS dept_name,
    d.depth,
    p.code AS parent_code,
    mgr.id AS manager_id,
    COALESCE(up_mgr.display_name, mgr.username) AS manager_name,
    COUNT(DISTINCT u_mem.id) AS active_member_count
FROM public.departments d
JOIN public.tenants t
  ON t.id = d.tenant_id
 AND t.id = :tenant_id
 AND t.is_deleted = false
LEFT JOIN public.departments p
  ON p.id = d.parent_id
 AND p.tenant_id = d.tenant_id
LEFT JOIN (
    SELECT u.id, u.username, m.tenant_id
    FROM public.users u
    JOIN public.tenant_user_memberships m
      ON m.user_id = u.id
     AND m.status = 'active'
     AND m.is_deleted = false
    WHERE u.is_active = true
      AND u.is_deleted = false
) mgr
  ON mgr.id = d.manager_user_id
 AND mgr.tenant_id = d.tenant_id
LEFT JOIN public.user_profiles up_mgr
  ON up_mgr.user_id = mgr.id
 AND up_mgr.tenant_id = d.tenant_id
LEFT JOIN public.department_members dm
  ON dm.department_id = d.id
 AND dm.tenant_id = d.tenant_id
 AND dm.effective_to IS NULL
LEFT JOIN public.tenant_user_memberships m_mem
  ON m_mem.user_id = dm.user_id
 AND m_mem.tenant_id = d.tenant_id
 AND m_mem.status = 'active'
 AND m_mem.is_deleted = false
LEFT JOIN public.users u_mem
  ON u_mem.id = m_mem.user_id
 AND u_mem.is_active = true
 AND u_mem.is_deleted = false
WHERE d.is_active = true
GROUP BY d.id, d.code, d.name, d.depth, d.path, p.code, mgr.id, up_mgr.display_name, mgr.username
ORDER BY d.depth ASC, d.path ASC;

-- [Q05] Pending Approval Requests (CRITICAL-03 Tenant Isolation Parity)
WITH user_unambiguous_tenant AS (
    SELECT m.user_id, MIN(m.tenant_id) AS tenant_id
    FROM public.tenant_user_memberships m
    WHERE m.status = 'active' AND m.is_deleted = false
    GROUP BY m.user_id
    HAVING COUNT(DISTINCT m.tenant_id) = 1
)
SELECT
    ar.id AS request_id,
    ar.code,
    ar.request_type,
    ar.title,
    ar.status,
    COALESCE(up_req.display_name, req.username) AS requester_name,
    ap.participant_role,
    ap.sequence_order,
    ap.action_status,
    ar.submitted_at
FROM public.approval_requests ar
JOIN user_unambiguous_tenant ut_ar
  ON ut_ar.user_id = ar.created_by_user_id
 AND ut_ar.tenant_id = :tenant_id
JOIN public.tenants t
  ON t.id = ut_ar.tenant_id
 AND t.is_deleted = false
JOIN public.approval_participants ap
  ON ap.request_id = ar.id
JOIN public.users u_caller
  ON u_caller.id = ap.user_id
 AND u_caller.is_active = true
 AND u_caller.is_deleted = false
JOIN public.tenant_user_memberships m_caller
  ON m_caller.user_id = u_caller.id
 AND m_caller.tenant_id = :tenant_id
 AND m_caller.status = 'active'
 AND m_caller.is_deleted = false
JOIN public.users req
  ON req.id = ar.created_by_user_id
 AND req.is_deleted = false
LEFT JOIN public.user_profiles up_req
  ON up_req.user_id = req.id
 AND up_req.tenant_id = :tenant_id
WHERE ap.user_id = :current_user_id
  AND ar.is_deleted = false
  AND ar.status = 'IN_PROGRESS'
  AND ap.action_status = 'PENDING'
ORDER BY ar.submitted_at ASC, ap.sequence_order ASC;

-- [Q08] Published Notices & Dual-Scope Audience Resolution (CRITICAL-04 Tenant Isolation Parity)
WITH user_unambiguous_tenant AS (
    SELECT m.user_id, MIN(m.tenant_id) AS tenant_id
    FROM public.tenant_user_memberships m
    WHERE m.status = 'active' AND m.is_deleted = false
    GROUP BY m.user_id
    HAVING COUNT(DISTINCT m.tenant_id) = 1
)
SELECT DISTINCT
    nt.id AS notice_id,
    nt.title,
    nt.notice_type,
    nt.priority,
    au.name AS audience_name,
    au.audience_type,
    nt.published_at
FROM public.notices nt
JOIN user_unambiguous_tenant ut_nt
  ON ut_nt.user_id = nt.created_by_user_id
JOIN public.tenants t
  ON t.id = ut_nt.tenant_id
 AND t.id = :tenant_id
 AND t.is_deleted = false
JOIN public.audiences au
  ON au.id = nt.audience_id
 AND au.is_active = true
LEFT JOIN user_unambiguous_tenant ut_au
  ON ut_au.user_id = au.owner_user_id
LEFT JOIN (
    SELECT adm.audience_id, MIN(d.tenant_id) AS tenant_id
    FROM public.audience_department_members adm
    JOIN public.departments d ON d.id = adm.department_id
    GROUP BY adm.audience_id
    HAVING COUNT(DISTINCT d.tenant_id) = 1
) adm_t ON adm_t.audience_id = au.id
LEFT JOIN (
    SELECT aum.audience_id, MIN(ut.tenant_id) AS tenant_id
    FROM public.audience_user_members aum
    JOIN user_unambiguous_tenant ut ON ut.user_id = aum.user_id
    GROUP BY aum.audience_id
    HAVING COUNT(DISTINCT ut.tenant_id) = 1
) aum_t ON aum_t.audience_id = au.id
JOIN public.users u_caller
  ON u_caller.id = :current_user_id
 AND u_caller.is_active = true
 AND u_caller.is_deleted = false
JOIN public.tenant_user_memberships m_caller
  ON m_caller.user_id = u_caller.id
 AND m_caller.tenant_id = t.id
 AND m_caller.status = 'active'
 AND m_caller.is_deleted = false
WHERE nt.is_published = true
  AND nt.is_deleted = false
  AND (
      au.is_system = true
      OR (
          au.is_system = false
          AND COALESCE(ut_au.tenant_id, adm_t.tenant_id, aum_t.tenant_id) = t.id
          AND (
              EXISTS (
                  SELECT 1
                  FROM public.audience_user_members aum
                  WHERE aum.audience_id = au.id
                    AND aum.user_id = u_caller.id
              )
              OR EXISTS (
                  SELECT 1
                  FROM public.audience_department_members adm
                  JOIN public.departments d
                    ON d.id = adm.department_id
                   AND d.tenant_id = t.id
                   AND d.is_active = true
                  JOIN public.department_members dm
                    ON dm.department_id = d.id
                   AND dm.user_id = u_caller.id
                   AND dm.tenant_id = t.id
                   AND dm.effective_to IS NULL
                  WHERE adm.audience_id = au.id
              )
          )
      )
  )
ORDER BY nt.published_at DESC;
