// =============================================================================
// PHASE 1.2.3 CANONICAL CYPHER TEST QUERIES (Q01, Q08)
// Groupware AI Chatbot - Output Contract Hardening & Cross-Tenant Security Gate
// =============================================================================

// -----------------------------------------------------------------------------
// [Q01] Department Hierarchy, Active Manager, Detailed Sub-Departments and Active Employees
// -----------------------------------------------------------------------------
MATCH (t:Tenant {id: $tenant_id, is_deleted: false})<-[req_m:MEMBER_OF {status: 'active', is_deleted: false}]-(req:User {id: $requesting_user_id, is_deleted: false, is_active: true})
MATCH (d:Department {tenant_id: $tenant_id})-[:BELONGS_TO_TENANT]->(t)
WHERE (d.id = $department_id OR ($dept_search IS NOT NULL AND toLower(d.name) CONTAINS toLower($dept_search)))
OPTIONAL MATCH (mgr:User {is_deleted: false, is_active: true})-[:MANAGES {tenant_id: $tenant_id}]->(d)
WHERE EXISTS {
  MATCH (mgr)-[:MEMBER_OF {status: 'active', is_deleted: false}]->(t)
}
OPTIONAL MATCH (sub:Department {tenant_id: $tenant_id})-[:SUB_DEPARTMENT_OF]->(d)
OPTIONAL MATCH (emp:User {is_deleted: false, is_active: true})-[dm:MEMBER_OF_DEPARTMENT {tenant_id: $tenant_id, is_active: true}]->(d)
WHERE dm.effective_to IS NULL
  AND EXISTS {
    MATCH (emp)-[:MEMBER_OF {status: 'active', is_deleted: false}]->(t)
  }
RETURN d.id AS department_id,
       d.code AS department_code,
       d.name AS department_name,
       d.is_active AS is_active,
       mgr.id AS manager_id,
       mgr.display_name AS manager_name,
       collect(DISTINCT CASE WHEN sub IS NOT NULL THEN {id: sub.id, name: sub.name} END) AS sub_departments,
       collect(DISTINCT CASE WHEN emp IS NOT NULL THEN {
         id: emp.id,
         display_name: emp.display_name,
         role_in_department: dm.role_in_department,
         is_primary: dm.is_primary,
         effective_from: dm.effective_from
       } END) AS active_employees
ORDER BY d.id ASC;

// -----------------------------------------------------------------------------
// [Q08] Published Notices & Dual-Scope Audience Resolution
// -----------------------------------------------------------------------------
MATCH (t:Tenant {id: $tenant_id, is_deleted: false})<-[m:MEMBER_OF {status: 'active', is_deleted: false}]-(u:User {id: $requesting_user_id, is_deleted: false, is_active: true})
MATCH (n:Notice {tenant_id: $tenant_id, is_published: true, is_deleted: false})-[:TARGETS_AUDIENCE]->(a:Audience {is_active: true})
WHERE a.is_system = true OR (
    a.is_system = false AND a.tenant_id = $tenant_id AND (
        EXISTS { MATCH (u)-[:INCLUDED_IN_AUDIENCE]->(a) }
        OR EXISTS { MATCH (u)-[dm:MEMBER_OF_DEPARTMENT {tenant_id: $tenant_id, is_active: true}]->(d:Department {tenant_id: $tenant_id, is_active: true})-[:DEPARTMENT_IN_AUDIENCE]->(a) WHERE dm.effective_to IS NULL }
    )
)
RETURN DISTINCT n.id AS notice_id,
       n.title AS title,
       n.notice_type AS notice_type,
       n.priority AS priority,
       a.name AS audience_name,
       a.audience_type AS audience_type,
       n.published_at AS published_at
ORDER BY n.published_at DESC;
