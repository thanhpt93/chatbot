// =============================================================================
// PHASE 1.2.2 CANONICAL CYPHER TEST QUERIES (Q01, Q05, Q08, Q11, Q14)
// Groupware AI Chatbot - Multi-Tenant Isolation & Lifecycle Verification
// =============================================================================

// [Q01] Department Hierarchy, Active Manager (HIGH-05), and Active Roster (DEFECT 06)
MATCH (d:Department {tenant_id: $tenant_id, is_active: true})-[:BELONGS_TO_TENANT]->(t:Tenant {id: $tenant_id, is_deleted: false})
OPTIONAL MATCH (d)-[:SUB_DEPARTMENT_OF]->(parent:Department {tenant_id: $tenant_id})
OPTIONAL MATCH (mgr:User {is_active: true, is_deleted: false})-[:MANAGES {tenant_id: $tenant_id}]->(d)
WHERE mgr IS NULL OR EXISTS {
    MATCH (mgr)-[:MEMBER_OF {tenant_id: $tenant_id, status: 'active', is_deleted: false}]->(t)
}
OPTIONAL MATCH (u:User {is_active: true, is_deleted: false})-[dm:MEMBER_OF_DEPARTMENT {tenant_id: $tenant_id, is_active: true}]->(d)
WHERE dm IS NULL OR (
    dm.effective_to IS NULL
    AND EXISTS {
        MATCH (u)-[:MEMBER_OF {tenant_id: $tenant_id, status: 'active', is_deleted: false}]->(t)
    }
)
RETURN d.id AS dept_id,
       d.code AS dept_code,
       d.name AS dept_name,
       d.depth AS depth,
       parent.code AS parent_code,
       mgr.id AS manager_id,
       mgr.display_name AS manager_name,
       count(DISTINCT u) AS active_member_count
ORDER BY d.depth ASC, d.path ASC;

// [Q05] Pending Approval Requests (CRITICAL-03 Tenant Isolation Parity)
MATCH (u:User {id: $current_user_id, is_active: true, is_deleted: false})
      -[:MEMBER_OF {tenant_id: $tenant_id, status: 'active', is_deleted: false}]->(t:Tenant {id: $tenant_id, is_deleted: false})
MATCH (u)-[ap:PARTICIPATES_IN {action_status: 'PENDING'}]->(ar:ApprovalRequest {tenant_id: $tenant_id, status: 'IN_PROGRESS', is_deleted: false})
MATCH (ar)-[:CREATED_BY]->(req:User {is_deleted: false})
RETURN ar.id AS request_id,
       ar.code AS code,
       ar.request_type AS request_type,
       ar.title AS title,
       ar.status AS status,
       req.display_name AS requester_name,
       ap.participant_role AS participant_role,
       ap.sequence_order AS sequence_order,
       ap.action_status AS action_status,
       ar.submitted_at AS submitted_at
ORDER BY ar.submitted_at ASC, ap.sequence_order ASC;

// [Q08] Published Notices & Dual-Scope Audience Resolution (CRITICAL-04 Tenant Isolation Parity)
MATCH (u:User {id: $current_user_id, is_active: true, is_deleted: false})
      -[:MEMBER_OF {tenant_id: $tenant_id, status: 'active', is_deleted: false}]->(t:Tenant {id: $tenant_id, is_deleted: false})
MATCH (nt:Notice {tenant_id: $tenant_id, is_published: true, is_deleted: false})-[:TARGETED_TO]->(au:Audience {is_active: true})
WHERE (au.is_system = true AND au.tenant_id IS NULL)
   OR (
       au.is_system = false
       AND au.tenant_id = $tenant_id
       AND (
           EXISTS { MATCH (au)-[:INCLUDES_USER]->(u) }
           OR EXISTS {
               MATCH (u)-[dm:MEMBER_OF_DEPARTMENT {tenant_id: $tenant_id, is_active: true}]->(d:Department {tenant_id: $tenant_id, is_active: true})
               WHERE dm.effective_to IS NULL
               MATCH (au)-[:INCLUDES_DEPARTMENT]->(d)
           }
       )
   )
RETURN DISTINCT nt.id AS notice_id,
                nt.title AS title,
                nt.notice_type AS notice_type,
                nt.priority AS priority,
                au.name AS audience_name,
                au.audience_type AS audience_type,
                nt.published_at AS published_at
ORDER BY nt.published_at DESC;
