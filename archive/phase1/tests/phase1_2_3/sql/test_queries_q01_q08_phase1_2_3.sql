-- =============================================================================
-- PHASE 1.2.3 CANONICAL SQL TEST QUERIES (Q01, Q08)
-- Groupware AI Chatbot - Output Contract Hardening & Cross-Tenant Security Gate
-- =============================================================================

-- -----------------------------------------------------------------------------
-- [Q01] Department Hierarchy, Active Manager, Detailed Sub-Departments and Active Employees
-- -----------------------------------------------------------------------------
WITH sub_depts AS (
    SELECT
        sub.parent_id AS department_id,
        jsonb_agg(
            jsonb_build_object(
                'id', sub.id,
                'name', sub.name
            ) ORDER BY sub.id
        ) AS sub_departments
    FROM public.departments sub
    WHERE sub.tenant_id = :tenant_id
      AND sub.is_active = true
      AND sub.parent_id IS NOT NULL
    GROUP BY sub.parent_id
),
active_dept_emps AS (
    SELECT
        dm.department_id,
        jsonb_agg(
            jsonb_build_object(
                'id', emp.id,
                'display_name', COALESCE(up_emp.display_name, emp.username),
                'role_in_department', dm.role_in_department,
                'is_primary', dm.is_primary,
                'effective_from', dm.effective_from
            ) ORDER BY emp.id
        ) AS active_employees
    FROM public.department_members dm
    JOIN public.users emp
      ON emp.id = dm.user_id
     AND emp.is_active = true
     AND emp.is_deleted = false
    JOIN public.tenant_user_memberships m_emp
      ON m_emp.user_id = emp.id
     AND m_emp.tenant_id = dm.tenant_id
     AND m_emp.status = 'active'
     AND m_emp.is_deleted = false
    LEFT JOIN public.user_profiles up_emp
      ON up_emp.user_id = emp.id
     AND up_emp.tenant_id = dm.tenant_id
    WHERE dm.tenant_id = :tenant_id
      AND dm.effective_to IS NULL
    GROUP BY dm.department_id
)
SELECT
    d.id AS department_id,
    d.code AS department_code,
    d.name AS department_name,
    COALESCE(d.is_active, false) AS is_active,
    mgr.id AS manager_id,
    COALESCE(up_mgr.display_name, mgr.username) AS manager_name,
    COALESCE(sd.sub_departments, '[]'::jsonb) AS sub_departments,
    COALESCE(ae.active_employees, '[]'::jsonb) AS active_employees
FROM public.tenants t
-- Caller Authorization Guard
JOIN public.users req
  ON req.id = :requesting_user_id
 AND req.is_active = true
 AND req.is_deleted = false
JOIN public.tenant_user_memberships req_m
  ON req_m.user_id = req.id
 AND req_m.tenant_id = t.id
 AND req_m.status = 'active'
 AND req_m.is_deleted = false
-- Target Department
JOIN public.departments d
  ON d.tenant_id = t.id
 AND t.id = :tenant_id
 AND t.is_deleted = false
-- Active Manager (HIGH-05)
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
-- Detailed Pre-Aggregated Collections
LEFT JOIN sub_depts sd
  ON sd.department_id = d.id
LEFT JOIN active_dept_emps ae
  ON ae.department_id = d.id
WHERE (d.id = :department_id OR (:dept_search IS NOT NULL AND LOWER(d.name) LIKE '%' || LOWER(:dept_search) || '%'))
ORDER BY d.id ASC;

-- -----------------------------------------------------------------------------
-- [Q08] Published Notices & Corrected Multi-Source Audience Tenant Isolation
-- -----------------------------------------------------------------------------
WITH user_unambiguous_tenant AS (
    SELECT m.user_id, MIN(m.tenant_id) AS tenant_id
    FROM public.tenant_user_memberships m
    WHERE m.status = 'active' AND m.is_deleted = false
    GROUP BY m.user_id
    HAVING COUNT(DISTINCT m.tenant_id) = 1
),
audience_dept_tenants AS (
    SELECT
        adm.audience_id,
        COUNT(DISTINCT d.tenant_id) AS dept_tenant_cnt,
        MIN(d.tenant_id) AS dept_tenant_id
    FROM public.audience_department_members adm
    JOIN public.departments d ON d.id = adm.department_id
    GROUP BY adm.audience_id
),
audience_user_tenants AS (
    SELECT
        aum.audience_id,
        COUNT(DISTINCT ut.tenant_id) AS user_tenant_cnt,
        MIN(ut.tenant_id) AS user_tenant_id,
        COUNT(aum.user_id) AS total_users,
        COUNT(ut.user_id) AS resolved_users
    FROM public.audience_user_members aum
    LEFT JOIN user_unambiguous_tenant ut ON ut.user_id = aum.user_id
    GROUP BY aum.audience_id
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
-- Creator tenant membership
JOIN user_unambiguous_tenant ut_nt
  ON ut_nt.user_id = nt.created_by_user_id
JOIN public.tenants t
  ON t.id = ut_nt.tenant_id
 AND t.id = :tenant_id
 AND t.is_deleted = false
JOIN public.audiences au
  ON au.id = nt.audience_id
 AND au.is_active = true
-- Requesting User Caller Authorization
JOIN public.users u_caller
  ON u_caller.id = :requesting_user_id
 AND u_caller.is_active = true
 AND u_caller.is_deleted = false
JOIN public.tenant_user_memberships m_caller
  ON m_caller.user_id = u_caller.id
 AND m_caller.tenant_id = t.id
 AND m_caller.status = 'active'
 AND m_caller.is_deleted = false
-- Audience Membership Tenants
LEFT JOIN user_unambiguous_tenant ut_au
  ON ut_au.user_id = au.owner_user_id
LEFT JOIN audience_dept_tenants adt
  ON adt.audience_id = au.id
LEFT JOIN audience_user_tenants aut
  ON aut.audience_id = au.id
WHERE nt.is_published = true
  AND nt.is_deleted = false
  AND (
      au.is_system = true
      OR (
          au.is_system = false
          -- Independent Multi-Source Tenant Isolation:
          -- 1. If owner is present: must be unambiguous and belong to t.id
          AND (au.owner_user_id IS NULL OR ut_au.tenant_id = t.id)
          -- 2. If department members exist: ALL departments must belong to t.id (no cross-tenant)
          AND (adt.audience_id IS NULL OR (adt.dept_tenant_cnt = 1 AND adt.dept_tenant_id = t.id))
          -- 3. If user members exist: ALL users must be unambiguous and belong to t.id (no cross-tenant or ambiguous)
          AND (aut.audience_id IS NULL OR (aut.total_users = aut.resolved_users AND aut.user_tenant_cnt = 1 AND aut.user_tenant_id = t.id))
          -- Caller must be recipient (either directly or via department membership)
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
