# PHASE 1.2 / 1.2.1 / 1.2.2 – QUERY READINESS & SECURITY VALIDATION (WORK PACKAGE 6)
## Groupware AI Chatbot – PostgreSQL + Neo4j + Vector Database

**Document ID:** `34_phase1_2_query_and_security_validation.md`  
**Phase:** Phase 1.2 / Phase 1.2.1 / Phase 1.2.2 – ETL Lifecycle, Tenant Security & Runtime Evidence Hardening  
**Date:** 2026-11-05  
**Status:** Canonical Architecture Specification (Supersedes `25_phase1_1_chatbot_query_readiness.md`; updated in Phase 1.2.1 for **DEFECT 02, 03, 04, 05, 06** and in Phase 1.2.2 for **CRITICAL-01, CRITICAL-02, CRITICAL-03, CRITICAL-04, HIGH-05**)  
**Evidence Level:** `STATICALLY VALIDATED` & `SYNTHETIC FIXTURE TESTED` (`Live DB Runtime Execution: NOT EXECUTED` — Cypher queries verified against canonical graph model `29`–`32`; SQL baseline queries verified against `schema_inventory.json`, `data_profile.json`, and SQLite/Python synthetic equivalence runner `scripts/phase1_2_2/validate_query_equivalence.py`)

---

## 1. Executive Summary & Reconciled Flaws from Phase 1.1, Phase 1.2 & Phase 1.2.1

Phase 1.1 (`25_phase1_1_chatbot_query_readiness.md`), Phase 1.2, and Phase 1.2.1 drafts contained schema, lifecycle, and SQL-vs-Cypher equivalence defects across the chatbot query scenarios, all of which are resolved herein:

1. **Invalid `u.tenant_id` on `:User`**: Every query in Doc `25` filtered `MATCH (u:User {tenant_id: $tenant_id})` or `WHERE u.tenant_id = $tenant_id`. In the canonical model (`29_phase1_2_final_user_tenant_model.md` & `30_phase1_2_complete_node_mapping.md`), `:User` (`NM-02`) is a global account node and active tenant membership is verified via `(:User)-[m:MEMBER_OF {status: 'active', is_deleted: false}]->(:Tenant {id: $tenant_id})` (`RM-01`).
2. **Department Membership Lifecycle Filtering & Manager Active Tenant Membership (`Q01`, `Q08`, `Q13`, `Q14` — DEFECT 06 & HIGH-05 Resolution)**:
   - `public.department_members` (`397` rows) contains `349` active rows (`effective_to IS NULL`) and `48` historical/ended rows (`effective_to IS NOT NULL`). `RM-03` (`[:MEMBER_OF_DEPARTMENT]`) sets `dm.effective_from`, `dm.effective_to`, and `dm.is_active = (effective_to IS NULL)`. All current-state queries (`Q01`, `Q08`, `Q13`, `Q14`) explicitly enforce `dm.is_active = true AND dm.tenant_id = $tenant_id` (`dm.effective_to IS NULL`).
   - **`HIGH-05` Resolved**: In `Q01` (both Cypher and PostgreSQL SQL) and `RM-04` (`Doc 31`), the optional department manager `mgr` is now strictly required to be globally active/non-deleted (`mgr.is_active = true AND mgr.is_deleted = false`) AND hold an active, non-deleted tenant membership in `d.tenant_id` (`status = 'active', is_deleted = false`).
3. **Approval Participant Physical Property & SQL Tenant Isolation (`Q05` — DEFECT 03 & CRITICAL-03 Resolution)**:
   - `public.approval_participants` (`12,720` rows) has `sequence_order` (`int4`), NOT `step_order`. Both Cypher (`hp.sequence_order`) and SQL (`ap.sequence_order`) use `sequence_order` alongside UPPERCASE status values (`ar.status = 'IN_PROGRESS'`, `hp.action_status IN ['PENDING', 'WAITING']`, `hp.participant_role IN ['APPROVER', 'AGREEMENTOR']`).
   - **`CRITICAL-03` Resolved**: The PostgreSQL Validation SQL for `Q05` now enforces full tenant isolation matching Cypher `Q05`: it verifies caller active membership in `:tenant_id` (`m_req.status = 'active' AND m_req.is_deleted = false`), derives `ar`'s tenant via `user_unambiguous_tenant` (`ut_ar.tenant_id = :tenant_id`), verifies participant tenant membership in `:tenant_id`, and returns `requester_name` via `LEFT JOIN` to the request creator.
4. **Audience Dual-Scope Resolution & SQL Tenant Equivalence (`Q08` — DEFECT 04 & CRITICAL-04 Resolution)**:
   - In `public.audiences` (`116` rows), `1` row (`id = 1`, `audience_type = 'ALL'`) is a global system template (`a.is_system = true`, `a.tenant_id IS NULL`), while `115` rows are custom tenant-scoped audiences (`a.is_system = false`, `a.tenant_id = $tenant_id`).
   - **`CRITICAL-04` Resolved**: The PostgreSQL Validation SQL for `Q08` now enforces full semantic equivalence with Cypher `Q08`: it verifies caller active membership in `:tenant_id`, derives the notice's tenant (`ut_nt.tenant_id = :tenant_id`), verifies that custom audiences (`a.is_system = false`) belong unambiguously to `:tenant_id` (`ut_au.tenant_id = :tenant_id` with zero cross-tenant members), enforces `dm.effective_to IS NULL` and `d.tenant_id = :tenant_id`, joins publisher `author_name`, and applies `LIMIT 20`.
5. **Fulltext Search Security for Global `:User` vs Tenant-Scoped Domain Nodes (`Q14` & `SEC-12`–`SEC-20` — DEFECT 05 Resolution)**: Separates `Template FTS-A` (tenant-scoped domain nodes) from `Template FTS-B` (global `:User` directory search joining `[:MEMBER_OF]`).
6. **Active Attendance Resolution & Unambiguous Leave Balance Tenant Derivation (`Q11` —DEFECT 02, CRITICAL-01 & CRITICAL-02 Resolution)**: Both Cypher and PostgreSQL SQL for `Q11` enforce active membership (`m.status = 'active' AND m.is_deleted = false`) and unambiguous tenant derivation.

---

## 2. Canonical Query Readiness Catalog (`Q01` – `Q14`)

> [!IMPORTANT]
> **Mandatory Tenant & Authorization Preamble**: Every chatbot query receives `$tenant_id` (`INTEGER`) and `$requesting_user_id` (`INTEGER`) from the Backend Auth Guard after verifying `tenant_user_memberships` (`status = 'active' AND is_deleted = false`). No query may ever hardcode `tenant_id = 1`.

---

### Scenario `Q01`: Organization Hierarchy & Department Reporting Line (DEFECT 06 & HIGH-05 Hardened)
- **Business Question**: *"Who manages the Engineering department, what are its sub-departments, and which active employees currently work in it within my tenant?"*
- **Node Labels**: `:Tenant` (`NM-01`), `:User` (`NM-02`), `:Department` (`NM-03`)
- **Relationships**: `[:BELONGS_TO_TENANT]` (`RM-02`), `[:MEMBER_OF_DEPARTMENT]` (`RM-03`), `[:MANAGES]` (`RM-04`), `[:SUB_DEPARTMENT_OF]` (`RM-05`), `[:MEMBER_OF]` (`RM-01`)
- **Required Properties**: `Department`: `id`, `tenant_id`, `code`, `name`, `is_active`; `User`: `id`, `display_name`, `email`, `is_active`, `is_deleted`; `MEMBER_OF`: `status`, `is_deleted`; `MEMBER_OF_DEPARTMENT`: `tenant_id`, `role_in_department`, `is_primary`, `effective_from`, `effective_to`, `is_active`
- **Tenant & Lifecycle Rule (`DEFECT 06` & `HIGH-05`)**:
  1. Caller `req` must have `req.is_active = true AND req.is_deleted = false` and `[:MEMBER_OF {status: 'active', is_deleted: false}]->(t:Tenant {id: $tenant_id, is_deleted: false})`.
  2. Department `d` must have `d.tenant_id = $tenant_id`.
  3. Optional manager `mgr` (`HIGH-05`) must have `mgr.is_active = true AND mgr.is_deleted = false`, `[:MANAGES {tenant_id: $tenant_id}]->(d)`, AND `EXISTS { MATCH (mgr)-[:MEMBER_OF {status: 'active', is_deleted: false}]->(t) }`.
  4. Optional active employees `emp` (`DEFECT 06`) must have `emp.is_active = true AND emp.is_deleted = false`, `dm.tenant_id = $tenant_id AND dm.is_active = true AND dm.effective_to IS NULL`, AND `EXISTS { MATCH (emp)-[:MEMBER_OF {status: 'active', is_deleted: false}]->(t) }`.
- **Authorization Rule**: Any authenticated active member of `$tenant_id` (`Tier 1`).

#### Canonical Cypher Query (`Q01`)
```cypher
MATCH (t:Tenant {id: $tenant_id, is_deleted: false})<-[req_m:MEMBER_OF {status: 'active', is_deleted: false}]-(req:User {id: $requesting_user_id, is_deleted: false, is_active: true})
MATCH (d:Department {tenant_id: $tenant_id})-[:BELONGS_TO_TENANT]->(t)
WHERE d.id = $department_id OR ($dept_search IS NOT NULL AND toLower(d.name) CONTAINS toLower($dept_search))
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
       collect(DISTINCT {id: sub.id, name: sub.name}) AS sub_departments,
       collect(DISTINCT {
         id: emp.id,
         display_name: emp.display_name,
         role_in_department: dm.role_in_department,
         is_primary: dm.is_primary,
         effective_from: dm.effective_from
       }) AS active_employees
ORDER BY d.id ASC;
```

#### PostgreSQL Validation SQL (Q01 - Detailed Structured Collection Output & Caller Authorization Contract)
`sql
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
JOIN public.users req
  ON req.id = :requesting_user_id
 AND req.is_active = true
 AND req.is_deleted = false
JOIN public.tenant_user_memberships req_m
  ON req_m.user_id = req.id
 AND req_m.tenant_id = t.id
 AND req_m.status = 'active'
 AND req_m.is_deleted = false
JOIN public.departments d
  ON d.tenant_id = t.id
 AND t.id = :tenant_id
 AND t.is_deleted = false
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
LEFT JOIN sub_depts sd
  ON sd.department_id = d.id
LEFT JOIN active_dept_emps ae
  ON ae.department_id = d.id
WHERE (d.id = :department_id OR (:dept_search IS NOT NULL AND LOWER(d.name) LIKE '%' || LOWER(:dept_search) || '%'))
ORDER BY d.id ASC;
`
- **Data Reality & Expected Behavior**: `public.departments` has `103` rows (`50` with `parent_id`, `21` with `manager_user_id`); `department_members` has `397` total rows (`349` active rows with `effective_to IS NULL` and `48` ended rows with `effective_to IS NOT NULL`). Both Cypher and SQL enforce active manager tenant membership (`HIGH-05`) and active department assignment (`DEFECT 06`).
- **Validation Status**: `STATICALLY VALIDATED` & `SYNTHETIC FIXTURE TESTED` (`Live DB Runtime: NOT EXECUTED`)

---

### Scenario `Q02`: Effective RBAC Permission Resolution (Role + Direct Override)
- **Business Question**: *"Does user X have permission `P` in the current tenant, and via which role or direct permission override?"*
- **Node Labels**: `:User` (`NM-02`), `:Tenant` (`NM-01`), `:Role` (`NM-04`), `:Permission` (`NM-05`)
- **Relationships**: `[:MEMBER_OF]` (`RM-01`), `[:HAS_ROLE]` (`RM-06`), `[:INCLUDES_PERMISSION]` (`RM-07`), `[:DIRECT_PERMISSION]` (`RM-08`)
- **Required Properties**: `Role`: `id`, `tenant_id`, `code`, `name`, `is_active`; `Permission`: `id`, `code`, `resource_type`, `resource_id`, `action_id`; `HAS_ROLE`: `tenant_id`; `INCLUDES_PERMISSION`: `tenant_id`, `is_granted`; `DIRECT_PERMISSION`: `tenant_id`, `is_granted`
- **Tenant Rule**: Matches `public.check_user_permission(p_tenant_id, p_user_id, p_permission_code)` precedence: active tenant membership -> direct user override (`DIRECT_PERMISSION`) -> role-based `BOOL_OR(is_granted)` (`HAS_ROLE` + `INCLUDES_PERMISSION`).
- **Authorization Rule**: Self-query (`$target_user_id = $requesting_user_id`) OR tenant admin / security auditor permission.

#### Canonical Cypher Query (`Q02`)
```cypher
MATCH (u:User {id: $target_user_id, is_deleted: false, is_active: true})-[m:MEMBER_OF {status: 'active', is_deleted: false}]->(t:Tenant {id: $tenant_id, is_deleted: false, status: 'active'})
MATCH (p:Permission {code: $permission_code})
OPTIONAL MATCH (u)-[dp:DIRECT_PERMISSION {tenant_id: $tenant_id}]->(p)
OPTIONAL MATCH (u)-[hr:HAS_ROLE {tenant_id: $tenant_id}]->(r:Role {tenant_id: $tenant_id, is_active: true})-[ip:INCLUDES_PERMISSION {tenant_id: $tenant_id}]->(p)
WITH u, p, dp,
     collect(DISTINCT CASE WHEN ip.is_granted = true THEN r.code END) AS granting_roles
RETURN u.id AS user_id,
       p.code AS permission_code,
       CASE
         WHEN dp IS NOT NULL THEN coalesce(dp.is_granted, false)
         WHEN size(granting_roles) > 0 THEN true
         ELSE false
       END AS is_permitted,
       CASE
         WHEN dp IS NOT NULL THEN 'DIRECT_OVERRIDE'
         WHEN size(granting_roles) > 0 THEN 'ROLE_GRANT'
         ELSE 'DENIED_DEFAULT'
       END AS resolution_source,
       granting_roles;
```

#### PostgreSQL Validation SQL (`Q02`)
```sql
SELECT public.check_user_permission(:tenant_id, :target_user_id, :permission_code) AS is_permitted;
```
- **Data Reality & Expected Behavior**: Mirrors `public.check_user_permission` (`artifacts/phase1_2/auth_routines.txt`). In the current snapshot, `user_permissions` has `51` rows (`19` granted, `32` denied overrides) and `role_permissions` has `1,535` rows across `42` roles and `247` permissions.
- **Validation Status**: `STATICALLY VALIDATED – NOT EXECUTED`

---

### Scenario `Q03`: Project Portfolio, Active Sprints, Kanban Stages & Open Tickets
- **Business Question**: *"What open or in-progress tickets exist in Project X, which sprint and kanban stage (`KanbanColumn`) are they in, and who is assigned?"*
- **Node Labels**: `:Project` (`NM-06`), `:Sprint` (`NM-08`), `:KanbanColumn` (`NM-09`), `:Ticket` (`NM-07`), `:User` (`NM-02`), `:Tenant` (`NM-01`)
- **Relationships**: `[:MEMBER_OF_PROJECT]` (`RM-10`), `[:CREATED_BY]` (`RM-09`), `[:BELONGS_TO_PROJECT]` (`RM-11`), `[:PART_OF_SPRINT]` (`RM-14`), `[:IN_STAGE]` (`RM-15`), `[:ASSIGNED_TO]` (`RM-13`), `[:MEMBER_OF]` (`RM-01`)
- **Required Properties**: `Project`: `id`, `tenant_id`, `key`, `name`, `status`, `is_deleted`; `Ticket`: `id`, `tenant_id`, `code`, `title`, `status`, `priority`, `due_date`, `is_deleted`; `KanbanColumn`: `id`, `tenant_id`, `title`, `status_group`; `Sprint`: `id`, `tenant_id`, `name`, `status`
- **Tenant Rule**: `p.tenant_id = $tenant_id AND tk.tenant_id = $tenant_id`
- **Authorization Rule**: Requesting user must be an active member of `$tenant_id` AND member/creator of `p` (`[:MEMBER_OF_PROJECT]` or `[:CREATED_BY]`) or hold project-view permission.

#### Canonical Cypher Query (`Q03`)
```cypher
MATCH (req:User {id: $requesting_user_id, is_deleted: false, is_active: true})-[:MEMBER_OF {status: 'active', is_deleted: false}]->(t:Tenant {id: $tenant_id, is_deleted: false})
MATCH (p:Project {id: $project_id, tenant_id: $tenant_id, is_deleted: false})
WHERE EXISTS {
  MATCH (req)-[:MEMBER_OF_PROJECT]->(p)
} OR EXISTS {
  MATCH (p)-[:CREATED_BY]->(req)
} OR $has_global_project_view = true
MATCH (tk:Ticket {tenant_id: $tenant_id, is_deleted: false})-[:BELONGS_TO_PROJECT]->(p)
OPTIONAL MATCH (tk)-[:IN_STAGE]->(kc:KanbanColumn {tenant_id: $tenant_id})
WHERE coalesce(kc.status_group, 'todo') IN ['todo', 'in_process']
OPTIONAL MATCH (tk)-[:PART_OF_SPRINT]->(sp:Sprint {tenant_id: $tenant_id})
OPTIONAL MATCH (tk)-[:ASSIGNED_TO]->(u:User {is_deleted: false})
RETURN p.key AS project_key,
       tk.code AS ticket_code,
       tk.title AS ticket_title,
       tk.status AS raw_ticket_status,
       kc.status_group AS kanban_status_group,
       kc.title AS kanban_column,
       tk.priority AS priority,
       tk.due_date AS due_date,
       sp.name AS sprint_name,
       collect(DISTINCT {id: u.id, display_name: u.display_name}) AS assignees
ORDER BY tk.due_date ASC, tk.id ASC;
```

#### PostgreSQL Validation SQL (`Q03`)
```sql
SELECT p.key AS project_key, tk.code AS ticket_code, tk.title,
       tk.status AS raw_status, kc.status_group, kc.title AS kanban_column,
       sp.name AS sprint_name
FROM public.tickets tk
JOIN public.projects p ON p.id = tk.project_id
LEFT JOIN public.kanban_columns kc ON kc.id = tk.column_id
LEFT JOIN public.project_sprints sp ON sp.id = tk.sprint_id
WHERE tk.project_id = :project_id AND tk.is_deleted = false AND p.is_deleted = false
  AND COALESCE(kc.status_group, 'todo') IN ('todo', 'in_process');
```
- **Data Reality & Expected Behavior**: In `public.tickets` (`668` rows), `100%` of rows have `tickets.status = 'create'`, whereas their linked `kanban_columns.status_group` (`[:IN_STAGE]` `RM-15`) distinguishes `'todo'`, `'in_process'`, and `'done'`. Traversing `(:Ticket)-[:IN_STAGE]->(:KanbanColumn)` accurately resolves true workflow progress.
- **Validation Status**: `STATICALLY VALIDATED – NOT EXECUTED`

---

### Scenario `Q04`: User Workload & Overdue Assigned Tickets
- **Business Question**: *"Which active tickets are assigned to User X across all projects in this tenant, and which ones are overdue?"*
- **Node Labels**: `:User` (`NM-02`), `:Tenant` (`NM-01`), `:Ticket` (`NM-07`), `:Project` (`NM-06`), `:KanbanColumn` (`NM-09`)
- **Relationships**: `[:MEMBER_OF]` (`RM-01`), `[:ASSIGNED_TO]` (`RM-13`), `[:BELONGS_TO_PROJECT]` (`RM-11`), `[:IN_STAGE]` (`RM-15`)
- **Required Properties**: `Ticket`: `id`, `tenant_id`, `code`, `title`, `status`, `priority`, `due_date`, `is_deleted`; `KanbanColumn`: `status_group`, `title`
- **Tenant Rule**: `tk.tenant_id = $tenant_id AND p.tenant_id = $tenant_id`
- **Authorization Rule**: Self-query (`$target_user_id = $requesting_user_id`) or project manager / department manager in `$tenant_id`.

#### Canonical Cypher Query (`Q04`)
```cypher
MATCH (u:User {id: $target_user_id, is_deleted: false})-[:MEMBER_OF {status: 'active', is_deleted: false}]->(t:Tenant {id: $tenant_id, is_deleted: false})
MATCH (p:Project {tenant_id: $tenant_id, is_deleted: false})<-[:BELONGS_TO_PROJECT]-(tk:Ticket {tenant_id: $tenant_id, is_deleted: false})-[:ASSIGNED_TO]->(u)
OPTIONAL MATCH (tk)-[:IN_STAGE]->(kc:KanbanColumn {tenant_id: $tenant_id})
WHERE coalesce(kc.status_group, 'todo') <> 'done'
RETURN tk.id AS ticket_id,
       tk.code AS ticket_code,
       tk.title AS title,
       p.key AS project_key,
       p.name AS project_name,
       tk.priority AS priority,
       kc.status_group AS status_group,
       kc.title AS stage_title,
       tk.due_date AS due_date,
       CASE WHEN tk.due_date IS NOT NULL AND tk.due_date < datetime() THEN true ELSE false END AS is_overdue
ORDER BY tk.due_date ASC;
```

#### PostgreSQL Validation SQL (`Q04`)
```sql
SELECT tk.id, tk.code, tk.title, p.key AS project_key, kc.status_group, tk.due_date
FROM public.ticket_assignees ta
JOIN public.tickets tk ON tk.id = ta.ticket_id
JOIN public.projects p ON p.id = tk.project_id
LEFT JOIN public.kanban_columns kc ON kc.id = tk.column_id
WHERE ta.user_id = :target_user_id
  AND tk.is_deleted = false AND p.is_deleted = false
  AND COALESCE(kc.status_group, 'todo') <> 'done';
```
- **Data Reality & Expected Behavior**: `ticket_assignees` has `1,008` rows across `660` distinct tickets and `77` distinct users (`599/660` active tickets, `64/77` active users).
- **Validation Status**: `STATICALLY VALIDATED – NOT EXECUTED`

---

### Scenario `Q05`: Pending Approval Requests Awaiting User Action (DEFECT 03 & CRITICAL-03 Hardened)
- **Business Question**: *"Which approval requests are currently in progress and waiting for my approval?"*
- **Node Labels**: `:ApprovalRequest` (`NM-10`), `:User` (`NM-02`), `:Tenant` (`NM-01`)
- **Relationships**: `[:PARTICIPATES_IN]` (`RM-20`), `[:CREATED_BY]` (`RM-18`), `[:MEMBER_OF]` (`RM-01`)
- **Required Properties**: `ApprovalRequest`: `id`, `tenant_id`, `code`, `title`, `request_type`, `status`, `submitted_at`, `is_deleted`; `PARTICIPATES_IN` (`RM-20`): `id`, `participant_role`, **`sequence_order`**, `action_status`, `acted_at`, `created_at`
- **Tenant & Security Rule (`DEFECT 03` & `CRITICAL-03`)**:
  1. Caller `u` (`$requesting_user_id`) must be an active, non-deleted user (`u.is_active = true AND u.is_deleted = false`) with an active, non-deleted tenant membership in `$tenant_id` (`m.status = 'active' AND m.is_deleted = false`) on an active, non-deleted `:Tenant` (`t.id = $tenant_id AND t.is_deleted = false`).
  2. Approval request `ar` must belong to `$tenant_id` (`ar.tenant_id = $tenant_id` in Cypher; derived via `user_unambiguous_tenant ut_ar` on `ar.created_by_user_id` where `ut_ar.tenant_id = :tenant_id` in PostgreSQL SQL).
  3. Request status must be `'IN_PROGRESS'` and `ar.is_deleted = false`.
  4. Participant record (`hp` / `ap`) must belong to `u`, with `action_status IN ('PENDING', 'WAITING')` and `participant_role IN ('APPROVER', 'AGREEMENTOR')`.
- **Authorization Rule**: Strictly restricted to `$requesting_user_id` as participant in `$tenant_id` (`Tier 1 Confidential`).

#### Canonical Cypher Query (`Q05`)
```cypher
MATCH (u:User {id: $requesting_user_id, is_deleted: false, is_active: true})-[:MEMBER_OF {status: 'active', is_deleted: false}]->(t:Tenant {id: $tenant_id, is_deleted: false})
MATCH (u)-[hp:PARTICIPATES_IN]->(ar:ApprovalRequest {tenant_id: $tenant_id, status: 'IN_PROGRESS', is_deleted: false})
WHERE hp.action_status IN ['PENDING', 'WAITING']
  AND hp.participant_role IN ['APPROVER', 'AGREEMENTOR']
OPTIONAL MATCH (ar)-[:CREATED_BY]->(sub:User)
RETURN ar.id AS approval_id,
       ar.title AS title,
       ar.request_type AS request_type,
       ar.status AS request_status,
       hp.sequence_order AS participant_sequence_order,
       hp.participant_role AS participant_role,
       hp.action_status AS participant_action_status,
       sub.display_name AS requester_name,
       ar.submitted_at AS submitted_at
ORDER BY ar.submitted_at DESC, hp.sequence_order ASC;
```

#### PostgreSQL Validation SQL (`Q05` — CRITICAL-03 Tenant-Isolated & Semantically Equivalent)
```sql
WITH user_unambiguous_tenant AS (
  SELECT user_id, min(tenant_id) AS tenant_id
  FROM (
    SELECT user_id, tenant_id FROM public.tenant_user_memberships WHERE is_deleted = false
    UNION
    SELECT user_id, tenant_id FROM _backup_cleanup_20261005.tenant_user_memberships_deleted
  ) u
  GROUP BY user_id
  HAVING count(DISTINCT tenant_id) = 1
)
SELECT
  ar.id AS approval_id,
  ar.title AS title,
  ar.request_type AS request_type,
  ar.status AS request_status,
  ap.sequence_order AS participant_sequence_order,
  ap.participant_role AS participant_role,
  ap.action_status AS participant_action_status,
  COALESCE(up_sub.display_name, sub.username) AS requester_name,
  ar.submitted_at AS submitted_at
FROM public.tenants t
INNER JOIN public.users u
  ON u.id = :requesting_user_id
 AND COALESCE(u.is_active, false) = true
 AND COALESCE(u.is_deleted, false) = false
INNER JOIN public.tenant_user_memberships m_req
  ON m_req.user_id = u.id
 AND m_req.tenant_id = t.id
 AND m_req.status = 'active'
 AND m_req.is_deleted = false
INNER JOIN public.approval_participants ap
  ON ap.user_id = u.id
INNER JOIN public.approval_requests ar
  ON ar.id = ap.request_id
INNER JOIN user_unambiguous_tenant ut_ar
  ON ut_ar.user_id = ar.created_by_user_id
 AND ut_ar.tenant_id = t.id
LEFT JOIN public.users sub
  ON sub.id = ar.created_by_user_id
LEFT JOIN public.user_profiles up_sub
  ON up_sub.user_id = sub.id
 AND up_sub.tenant_id = t.id
WHERE t.id = :tenant_id
  AND COALESCE(t.is_deleted, false) = false
  AND ar.status = 'IN_PROGRESS'
  AND COALESCE(ar.is_deleted, false) = false
  AND ap.action_status IN ('PENDING', 'WAITING')
  AND ap.participant_role IN ('APPROVER', 'AGREEMENTOR')
ORDER BY ar.submitted_at DESC, ap.sequence_order ASC;
```
- **Data Reality & Expected Behavior**:
  1. **DEFECT 03 Resolved**: Uses verified physical column **`sequence_order`** (`int4` NOT NULL on `public.approval_participants`).
  2. **CRITICAL-03 Resolved**: Enforces active caller membership in `:tenant_id` (`m_req.status = 'active' AND m_req.is_deleted = false`) AND request tenant derivation (`ut_ar.tenant_id = t.id`), preventing cross-tenant approval leakage when a user belongs to multiple tenants or when querying across tenants.
- **Validation Status**: `STATICALLY VALIDATED` & `SYNTHETIC FIXTURE TESTED` (`Live DB Runtime: NOT EXECUTED`)

---

### Scenario `Q06`: Project Ticket & Tag Dependency Exploration
- **Business Question**: *"For Project P, what tags (`:Tag`) are applied to its tickets, and which tickets share a specific project tag?"*
- **Node Labels**: `:Project` (`NM-06`), `:Ticket` (`NM-07`), `:Tag` (`NM-24`), `:KanbanColumn` (`NM-09`), `:User` (`NM-02`)
- **Relationships**: `[:BELONGS_TO_PROJECT]` (`RM-11`), `[:HAS_TAG]` (`RM-39`), `[:TAGGED_WITH]` (`RM-40`), `[:IN_STAGE]` (`RM-15`), `[:ASSIGNED_TO]` (`RM-13`)
- **Required Properties**: `Ticket`: `id`, `tenant_id`, `code`, `title`, `priority`, `is_deleted`; `Tag`: `tag_key`, `tenant_id`, `name`, `color`
- **Tenant Rule**: `p.tenant_id = $tenant_id AND tk.tenant_id = $tenant_id AND tg.tenant_id = $tenant_id`
- **Authorization Rule**: Authorized project viewer in `$tenant_id`.

#### Canonical Cypher Query (`Q06`)
```cypher
MATCH (p:Project {id: $project_id, tenant_id: $tenant_id, is_deleted: false})
MATCH (tk:Ticket {tenant_id: $tenant_id, is_deleted: false})-[:BELONGS_TO_PROJECT]->(p)
MATCH (tk)-[:TAGGED_WITH]->(tg:Tag {tenant_id: $tenant_id})
OPTIONAL MATCH (tk)-[:IN_STAGE]->(kc:KanbanColumn {tenant_id: $tenant_id})
OPTIONAL MATCH (tk)-[:ASSIGNED_TO]->(u:User {is_deleted: false})
RETURN p.key AS project_key,
       tg.name AS tag_name,
       tg.color AS tag_color,
       tk.id AS ticket_id,
       tk.code AS ticket_code,
       tk.title AS ticket_title,
       kc.status_group AS status_group,
       collect(DISTINCT u.display_name) AS assignees
ORDER BY tg.name ASC, tk.id ASC;
```

#### PostgreSQL Validation SQL (`Q06`)
```sql
SELECT p.key AS project_key, pt.name AS tag_name, tk.id AS ticket_id, tk.code, tk.title, kc.status_group
FROM public.ticket_tags tt
JOIN public.project_tags pt ON pt.id = tt.tag_id
JOIN public.tickets tk ON tk.id = tt.ticket_id
JOIN public.projects p ON p.id = tk.project_id
LEFT JOIN public.kanban_columns kc ON kc.id = tk.column_id
WHERE p.id = :project_id AND tk.is_deleted = false AND p.is_deleted = false;
```
- **Data Reality & Expected Behavior**: `public.project_tags` has `20` rows and `public.ticket_tags` links `10` active tickets to `8` distinct tags.
- **Validation Status**: `STATICALLY VALIDATED – NOT EXECUTED`

---

### Scenario `Q07`: User Schedule, Meeting Room Bookings & Attendees
- **Business Question**: *"What meetings is User X organizing or attending between `$start_date` and `$end_date`, in which room, and with whom?"*
- **Node Labels**: `:ScheduleEvent` (`NM-12`), `:ScheduleRoom` (`NM-13`), `:User` (`NM-02`), `:Tenant` (`NM-01`)
- **Relationships**: `[:ORGANIZED_BY]` (`RM-21`), `[:ATTENDS_EVENT]` (`RM-23`), `[:HELD_IN]` (`RM-22`), `[:MEMBER_OF]` (`RM-01`)
- **Required Properties**: `ScheduleEvent`: `id`, `tenant_id`, `title`, `event_date`, `end_date`, `start_time`, `end_time`, `location`, `visibility`, `is_all_day`, `is_deleted`; `ScheduleRoom`: `id`, `name`, `capacity`, `is_active` (NO `tenant_id`, NO `location`)
- **Tenant Rule**: `ev.tenant_id = $tenant_id` (`ScheduleRoom` is a pooled facility catalog node without `tenant_id`).
- **Authorization Rule**: Self or authorized calendar viewer within `$tenant_id` (filtering `ev.visibility <> 'private'` unless `$target_user_id = $requesting_user_id`).

#### Canonical Cypher Query (`Q07`)
```cypher
MATCH (u:User {id: $target_user_id, is_deleted: false})-[:MEMBER_OF {status: 'active', is_deleted: false}]->(t:Tenant {id: $tenant_id, is_deleted: false})
MATCH (ev:ScheduleEvent {tenant_id: $tenant_id, is_deleted: false})
WHERE ev.event_date <= date($end_date)
  AND ev.end_date >= date($start_date)
  AND (ev.visibility <> 'private' OR $target_user_id = $requesting_user_id)
  AND (
    EXISTS { MATCH (ev)-[:ORGANIZED_BY]->(u) }
    OR EXISTS { MATCH (u)-[:ATTENDS_EVENT]->(ev) }
  )
OPTIONAL MATCH (ev)-[:HELD_IN]->(rm:ScheduleRoom)
OPTIONAL MATCH (ev)-[:ORGANIZED_BY]->(org:User)
OPTIONAL MATCH (attendee:User {is_deleted: false})-[att:ATTENDS_EVENT]->(ev)
RETURN ev.id AS event_id,
       ev.title AS title,
       ev.event_date AS event_date,
       ev.end_date AS end_date,
       ev.start_time AS start_time,
       ev.end_time AS end_time,
       ev.location AS event_location,
       rm.name AS room_name,
       rm.capacity AS room_capacity,
       rm.is_active AS room_is_active,
       org.display_name AS organizer_name,
       collect(DISTINCT {id: attendee.id, display_name: attendee.display_name}) AS attendees
ORDER BY ev.event_date ASC, ev.start_time ASC;
```

#### PostgreSQL Validation SQL (`Q07`)
```sql
SELECT ev.id, ev.title, ev.event_date, ev.end_date, ev.start_time, ev.end_time,
       ev.location AS event_location, rm.name AS room_name, rm.is_active AS room_is_active
FROM public.schedule_events ev
LEFT JOIN public.schedule_rooms rm ON rm.id = ev.room_id
WHERE ev.is_deleted = false
  AND ev.event_date <= :end_date AND ev.end_date >= :start_date
  AND (ev.user_id = :target_user_id OR EXISTS (
    SELECT 1 FROM public.schedule_event_participants sep
    WHERE sep.event_id = ev.id AND sep.user_id = :target_user_id
  ));
```
- **Data Reality & Expected Behavior**: Fixes Doc `25`'s invalid `rm.tenant_id` and `rm.location` references, and does NOT filter `rm.is_active = true` when displaying room names because `12/13` rooms in `schedule_rooms` have `is_active = false` (including rooms linked to `242` events).
- **Validation Status**: `STATICALLY VALIDATED – NOT EXECUTED`

---

### Scenario `Q08`: Targeted Company Notices by Dual-Scope Audience & Active Department Membership (DEFECT 04, DEFECT 06 & CRITICAL-04 Hardened)
- **Business Question**: *"What published announcements/notices are targeted at me (either via the global `'ALL'` system audience, a direct user audience in my tenant, or my active department audience in my tenant)?"*
- **Node Labels**: `:Notice` (`NM-14`), `:Audience` (`NM-20`), `:User` (`NM-02`), `:Department` (`NM-03`), `:Tenant` (`NM-01`)
- **Relationships**: `[:TARGETED_TO]` (`RM-25`), `[:INCLUDES_DEPARTMENT]` (`RM-26`), `[:INCLUDES_USER]` (`RM-27`), `[:MEMBER_OF_DEPARTMENT]` (`RM-03`), `[:PUBLISHED_BY]` (`RM-24`), `[:MEMBER_OF]` (`RM-01`)
- **Required Properties**: `Notice`: `id`, `tenant_id`, `title`, `notice_type`, `priority`, `is_published`, `published_at`, `is_deleted`; `Audience`: `id`, `tenant_id` (`NULL` for system audience, `NOT NULL` for custom audience), `code`, `name`, `audience_type`, `is_system`, `is_active`; `MEMBER_OF_DEPARTMENT`: `tenant_id`, `is_active`, `effective_to`
- **Tenant & Audience Dual-Scope Rule (`DEFECT 04`, `DEFECT 06` & `CRITICAL-04`)**:
  1. Caller `u` (`$requesting_user_id`) must be an active, non-deleted user (`u.is_active = true AND u.is_deleted = false`) with an active, non-deleted tenant membership in `$tenant_id` (`m.status = 'active' AND m.is_deleted = false`).
  2. Notice `nt` must belong strictly to `$tenant_id` (`nt.tenant_id = $tenant_id` in Cypher; `ut_nt.tenant_id = :tenant_id` in PostgreSQL SQL), with `nt.is_published = true AND nt.is_deleted = false`.
  3. **Branch 1 (Global System Audience)**: `a.is_system = true AND a.tenant_id IS NULL AND a.audience_type = 'ALL'` (with zero department/user member rows).
  4. **Branch 2 (Custom Tenant-Scoped Audience)**: `a.is_system = false AND a.tenant_id = $tenant_id` (derived in SQL via `ut_au.tenant_id = :tenant_id` and verified against `adm_tenants` & `aum_tenants`) where either `(a)-[:INCLUDES_USER]->(u)` OR `(a)-[:INCLUDES_DEPARTMENT]->(d:Department {tenant_id: $tenant_id})<-[dm:MEMBER_OF_DEPARTMENT {tenant_id: $tenant_id, is_active: true}]-(u)` (`dm.effective_to IS NULL`).
- **Authorization Rule**: Active member of `$tenant_id`.

#### Canonical Cypher Query (`Q08`)
```cypher
MATCH (u:User {id: $requesting_user_id, is_deleted: false, is_active: true})-[:MEMBER_OF {status: 'active', is_deleted: false}]->(t:Tenant {id: $tenant_id, is_deleted: false})
MATCH (nt:Notice {tenant_id: $tenant_id, is_published: true, is_deleted: false})-[:TARGETED_TO]->(a:Audience {is_active: true})
WHERE (
  a.is_system = true
  AND a.tenant_id IS NULL
  AND a.audience_type = 'ALL'
) OR (
  a.is_system = false
  AND a.tenant_id = $tenant_id
  AND (
    EXISTS {
      MATCH (a)-[:INCLUDES_USER]->(u)
    }
    OR EXISTS {
      MATCH (a)-[:INCLUDES_DEPARTMENT]->(d:Department {tenant_id: $tenant_id})<-[dm:MEMBER_OF_DEPARTMENT {tenant_id: $tenant_id, is_active: true}]-(u)
      WHERE dm.effective_to IS NULL
    }
  )
)
OPTIONAL MATCH (nt)-[:PUBLISHED_BY]->(pub:User)
RETURN nt.id AS notice_id,
       nt.title AS title,
       nt.notice_type AS notice_type,
       nt.priority AS priority,
       a.name AS audience_name,
       a.audience_type AS audience_type,
       a.is_system AS is_system_audience,
       pub.display_name AS author_name,
       nt.published_at AS published_at
ORDER BY nt.published_at DESC
LIMIT 20;
```

#### PostgreSQL Validation SQL (`Q08` — CRITICAL-04 Tenant-Isolated & Semantically Equivalent)
```sql
WITH user_unambiguous_tenant AS (
  SELECT user_id, min(tenant_id) AS tenant_id
  FROM (
    SELECT user_id, tenant_id FROM public.tenant_user_memberships WHERE is_deleted = false
    UNION
    SELECT user_id, tenant_id FROM _backup_cleanup_20261005.tenant_user_memberships_deleted
  ) u
  GROUP BY user_id
  HAVING count(DISTINCT tenant_id) = 1
),
adm_tenants AS (
  SELECT adm.audience_id,
         count(DISTINCT d.tenant_id) AS dept_tenant_cnt,
         min(d.tenant_id) AS dept_tenant_id
  FROM public.audience_department_members adm
  INNER JOIN public.departments d ON d.id = adm.department_id
  GROUP BY adm.audience_id
),
aum_tenants AS (
  SELECT aum.audience_id,
         count(DISTINCT ut.tenant_id) AS user_tenant_cnt,
         min(ut.tenant_id) AS user_tenant_id
  FROM public.audience_user_members aum
  INNER JOIN user_unambiguous_tenant ut ON ut.user_id = aum.user_id
  GROUP BY aum.audience_id
)
SELECT DISTINCT
  nt.id AS notice_id,
  nt.title AS title,
  nt.notice_type AS notice_type,
  nt.priority AS priority,
  a.name AS audience_name,
  a.audience_type AS audience_type,
  COALESCE(a.is_system, false) AS is_system_audience,
  COALESCE(up_pub.display_name, pub.username) AS author_name,
  nt.published_at AS published_at
FROM public.tenants t
INNER JOIN public.users u
  ON u.id = :requesting_user_id
 AND COALESCE(u.is_active, false) = true
 AND COALESCE(u.is_deleted, false) = false
INNER JOIN public.tenant_user_memberships m_req
  ON m_req.user_id = u.id
 AND m_req.tenant_id = t.id
 AND m_req.status = 'active'
 AND m_req.is_deleted = false
INNER JOIN public.notices nt
  ON nt.is_published = true
 AND COALESCE(nt.is_deleted, false) = false
INNER JOIN user_unambiguous_tenant ut_nt
  ON ut_nt.user_id = nt.created_by_user_id
 AND ut_nt.tenant_id = t.id
INNER JOIN public.audiences a
  ON a.id = nt.audience_id
 AND COALESCE(a.is_active, true) = true
LEFT JOIN user_unambiguous_tenant ut_au
  ON ut_au.user_id = a.owner_user_id
LEFT JOIN adm_tenants adm_t
  ON adm_t.audience_id = a.id
LEFT JOIN aum_tenants aum_t
  ON aum_t.audience_id = a.id
LEFT JOIN public.audience_user_members aum
  ON COALESCE(a.is_system, false) = false
 AND aum.audience_id = a.id
 AND aum.user_id = u.id
LEFT JOIN (
  public.department_members dm
  INNER JOIN public.departments d
    ON d.id = dm.department_id
  INNER JOIN public.audience_department_members adm
    ON adm.department_id = d.id
) ON COALESCE(a.is_system, false) = false
 AND adm.audience_id = a.id
 AND dm.user_id = u.id
 AND dm.tenant_id = t.id
 AND d.tenant_id = t.id
 AND dm.effective_to IS NULL
LEFT JOIN public.users pub
  ON pub.id = nt.created_by_user_id
LEFT JOIN public.user_profiles up_pub
  ON up_pub.user_id = pub.id
 AND up_pub.tenant_id = t.id
WHERE t.id = :tenant_id
  AND COALESCE(t.is_deleted, false) = false
  AND (
    -- Branch 1: Global System Audience (tenant_id IS NULL, 0 explicit member rows)
    (
      COALESCE(a.is_system, false) = true
      AND a.owner_user_id IS NULL
      AND a.audience_type = 'ALL'
      AND adm_t.audience_id IS NULL
      AND aum_t.audience_id IS NULL
    )
    OR
    -- Branch 2: Custom Tenant-Scoped Audience (unambiguous owner & member tenant = t.id)
    (
      COALESCE(a.is_system, false) = false
      AND ut_au.tenant_id = t.id
      AND (adm_t.audience_id IS NULL OR (adm_t.dept_tenant_cnt = 1 AND adm_t.dept_tenant_id = t.id))
      AND (aum_t.audience_id IS NULL OR (aum_t.user_tenant_cnt = 1 AND aum_t.user_tenant_id = t.id))
      AND (aum.user_id IS NOT NULL OR adm.department_id IS NOT NULL)
    )
  )
ORDER BY nt.published_at DESC
LIMIT 20;
```
- **Data Reality & Expected Behavior**: Resolves **DEFECT 04**, **DEFECT 06**, and **CRITICAL-04** (enforcing notice tenant derivation `ut_nt.tenant_id = t.id`, custom audience tenant ownership `ut_au.tenant_id = t.id` + `adm_t`/`aum_t` validation, caller active tenant membership `m_req.status = 'active'`, and `dm.effective_to IS NULL`).
- **Validation Status**: `STATICALLY VALIDATED` & `SYNTHETIC FIXTURE TESTED` (`Live DB Runtime: NOT EXECUTED`)

---

### Scenario `Q09`: IT Asset Inventory, Department Location & Employee Custodian Assignment
- **Business Question**: *"Which IT assets are currently assigned to User X (or located in Department D), and what are their categories and serial numbers?"*
- **Node Labels**: `:Asset` (`NM-16`), `:AssetCategory` (`NM-17`), `:Department` (`NM-03`), `:User` (`NM-02`), `:Tenant` (`NM-01`)
- **Relationships**: `[:ASSIGNED_TO]` (`RM-30`), `[:LOCATED_IN]` (`RM-31`), `[:CATEGORIZED_AS]` (`RM-32`), `[:MEMBER_OF]` (`RM-01`)
- **Required Properties**: `Asset`: `id`, `tenant_id`, `code`, `name`, `serial_number`, `manufacturer`, `status`, `condition`, `location`, `is_deleted`; `AssetCategory`: `id`, `code`, `name`, `is_active` (NO `tenant_id`)
- **Tenant Rule**: `a.tenant_id = $tenant_id` (`AssetCategory` is a global taxonomy catalog without `tenant_id`).
- **Authorization Rule**: Self-custodian (`$target_user_id = $requesting_user_id`) or IT Asset / Department Manager in `$tenant_id`.

#### Canonical Cypher Query (`Q09`)
```cypher
MATCH (u:User {id: $target_user_id, is_deleted: false})-[:MEMBER_OF {status: 'active', is_deleted: false}]->(t:Tenant {id: $tenant_id, is_deleted: false})
MATCH (a:Asset {tenant_id: $tenant_id, is_deleted: false})-[:ASSIGNED_TO]->(u)
OPTIONAL MATCH (a)-[:CATEGORIZED_AS]->(ac:AssetCategory)
OPTIONAL MATCH (a)-[:LOCATED_IN]->(d:Department {tenant_id: $tenant_id})
RETURN a.id AS asset_id,
       a.code AS asset_code,
       a.name AS asset_name,
       ac.name AS category_name,
       d.name AS department_name,
       a.serial_number AS serial_number,
       a.manufacturer AS manufacturer,
       a.status AS status,
       a.condition AS condition
ORDER BY a.code ASC;
```

#### PostgreSQL Validation SQL (`Q09`)
```sql
SELECT a.id, a.code AS asset_code, a.name, ac.name AS category_name, d.name AS department_name,
       a.serial_number, a.status, a.condition
FROM public.assets a
LEFT JOIN public.asset_categories ac ON ac.id = a.category_id
LEFT JOIN public.departments d ON d.id = a.department_id
WHERE a.assigned_user_id = :target_user_id AND a.is_deleted = false;
```
- **Data Reality & Expected Behavior**: `public.assets` has `685` rows (`550` assigned to `202` distinct users; `549` linked to `23` departments; `685` linked to `11` categories in `asset_categories`).
- **Validation Status**: `STATICALLY VALIDATED – NOT EXECUTED`

---

### Scenario `Q10`: Hybrid Graph + Vector Knowledge Discovery (Project Documents & Files)
- **Business Question**: *"Find official knowledge documents (`:KnowledgeDocument`) and file metadata (`:FileMetadata`) associated with Project X, and return their IDs for Vector DB chunk retrieval."*
- **Node Labels**: `:KnowledgeDocument` (`NM-25`), `:FileMetadata` (`NM-18`), `:Project` (`NM-06`), `:User` (`NM-02`), `:Tenant` (`NM-01`)
- **Relationships**: `[:ASSOCIATED_WITH]` (`RM-42`), `[:STORED_AS_FILE]` (`RM-43`), `[:UPLOADED_BY]` (`RM-33`), `[:MEMBER_OF_PROJECT]` (`RM-10`), `[:CREATED_BY]` (`RM-09`), `[:MEMBER_OF]` (`RM-01`)
- **Required Properties**: `KnowledgeDocument`: `id`, `tenant_id`, `project_id`, `file_id`, `title`, `is_deleted`; `FileMetadata`: `id`, `tenant_id`, `original_name`, `content_type`, `file_ext`, `size_bytes`, `is_deleted`
- **Tenant Rule**: `kd.tenant_id = $tenant_id AND f.tenant_id = $tenant_id AND p.tenant_id = $tenant_id`
- **Authorization Rule**: Requesting user must have access to `:Project` in `$tenant_id`.

#### Canonical Cypher Query (`Q10`)
```cypher
MATCH (req:User {id: $requesting_user_id, is_deleted: false, is_active: true})-[:MEMBER_OF {status: 'active', is_deleted: false}]->(t:Tenant {id: $tenant_id, is_deleted: false})
MATCH (p:Project {id: $project_id, tenant_id: $tenant_id, is_deleted: false})
WHERE EXISTS { MATCH (req)-[:MEMBER_OF_PROJECT]->(p) }
   OR EXISTS { MATCH (p)-[:CREATED_BY]->(req) }
   OR $has_global_project_view = true
MATCH (kd:KnowledgeDocument {tenant_id: $tenant_id, is_deleted: false})-[:ASSOCIATED_WITH]->(p)
OPTIONAL MATCH (kd)-[:STORED_AS_FILE]->(f:FileMetadata {tenant_id: $tenant_id, is_deleted: false})
OPTIONAL MATCH (f)-[:UPLOADED_BY]->(up:User)
RETURN p.key AS project_key,
       kd.id AS knowledge_document_id,
       kd.title AS document_title,
       f.id AS file_id,
       f.original_name AS original_file_name,
       f.content_type AS content_type,
       f.size_bytes AS size_bytes,
       up.display_name AS uploaded_by
ORDER BY kd.sort_order ASC, kd.id ASC;
```

#### PostgreSQL Validation SQL (`Q10`)
```sql
SELECT p.key AS project_key, pcd.id AS knowledge_document_id, pcd.title,
       f.id AS file_id, f.original_name, f.content_type, f.size_bytes
FROM public.project_common_documents pcd
JOIN public.projects p ON p.id = pcd.project_id
LEFT JOIN public.files f ON f.id = pcd.file_id AND f.is_deleted = false
WHERE pcd.project_id = :project_id AND pcd.is_deleted = false AND p.is_deleted = false;
```
- **Data Reality & Expected Behavior**: `public.project_common_documents` has `40` rows (`100%` matching `projects.id` across `7` projects and `100%` matching `files.id` across `40` files).
- **Validation Status**: `STATICALLY VALIDATED – NOT EXECUTED`

---

### Scenario `Q11`: Employee Leave Balance & Daily Attendance Summary (DEFECT 02, CRITICAL-01 & CRITICAL-02 Aligned)
- **Business Question**: *"What is my remaining annual leave balance for year Y (including opening, carryover, accrued, and used days), and what is my daily attendance summary for this month?"*
- **Node Labels**: `:User` (`NM-02`), `:Tenant` (`NM-01`), `:LeaveBalance` (`NM-21`), `:AttendanceRecord` (`NM-22`)
- **Relationships**: `[:MEMBER_OF]` (`RM-01`), `[:HAS_LEAVE_BALANCE]` (`RM-36`), `[:HAS_ATTENDANCE]` (`RM-37`)
- **Required Properties**: `LeaveBalance`: `id`, `tenant_id`, `user_id`, `year`, `opening_days`, `carryover_days`, `seniority_days`, `accrued_days`, `used_days`, `remaining_days`; `AttendanceRecord`: `id`, `tenant_id`, `user_id`, `resolution_status`, `work_date`, `first_check_in`, `last_check_out`, `status`, `is_late`, `is_early_leave`, `actual_minutes`, `employee_code`
- **Tenant Rule**: `lb.tenant_id = $tenant_id AND att.tenant_id = $tenant_id`
- **Authorization Rule**: **Strict Self-Access (`$target_user_id = $requesting_user_id`)** or explicitly authorized HR Admin (`Tier 4 Restricted`).

#### Canonical Cypher Query (`Q11`)
```cypher
MATCH (u:User {id: $target_user_id, is_deleted: false})-[:MEMBER_OF {status: 'active', is_deleted: false}]->(t:Tenant {id: $tenant_id, is_deleted: false})
WHERE $target_user_id = $requesting_user_id OR $has_hr_admin_permission = true
OPTIONAL MATCH (u)-[:HAS_LEAVE_BALANCE]->(lb:LeaveBalance {tenant_id: $tenant_id, year: $year})
OPTIONAL MATCH (u)-[ha:HAS_ATTENDANCE]->(att:AttendanceRecord {tenant_id: $tenant_id})
WHERE att.work_date >= date($month_start) AND att.work_date <= date($month_end)
RETURN u.id AS user_id,
       u.display_name AS display_name,
       lb.year AS leave_year,
       lb.opening_days AS opening_days,
       lb.carryover_days AS carryover_days,
       lb.seniority_days AS seniority_days,
       lb.accrued_days AS accrued_days,
       lb.used_days AS used_days,
       lb.remaining_days AS remaining_days,
       collect(DISTINCT {
         work_date: att.work_date,
         first_check_in: att.first_check_in,
         last_check_out: att.last_check_out,
         status: att.status,
         is_late: att.is_late,
         is_early_leave: att.is_early_leave,
         actual_minutes: att.actual_minutes,
         resolution_status: att.resolution_status
       }) AS attendance_records;
```

#### PostgreSQL Validation SQL (`Q11` — CRITICAL-01 & CRITICAL-02 Aligned)
```sql
WITH user_unambiguous_leave_tenant AS (
  SELECT m.user_id, min(m.tenant_id) AS tenant_id
  FROM public.tenant_user_memberships m
  INNER JOIN public.users u ON u.id = m.user_id AND COALESCE(u.is_deleted, false) = false
  INNER JOIN public.user_profiles up ON up.user_id = m.user_id AND up.tenant_id = m.tenant_id
  WHERE m.is_deleted = false AND m.status IN ('active', 'inactive', 'suspended')
  GROUP BY m.user_id
  HAVING count(DISTINCT m.tenant_id) = 1
)
SELECT y.user_id, y.year, y.opening_days, y.carryover_days, y.seniority_days,
       COALESCE(SUM(m.accrued_days), 0) AS accrued_days,
       COALESCE(SUM(m.used_days), 0) AS used_days,
       y.remaining_days
FROM public.users u
INNER JOIN public.tenant_user_memberships tm
  ON tm.user_id = u.id
 AND tm.tenant_id = :tenant_id
 AND tm.status = 'active'
 AND tm.is_deleted = false
INNER JOIN user_unambiguous_leave_tenant ult
  ON ult.user_id = u.id
 AND ult.tenant_id = :tenant_id
LEFT JOIN public.user_leave_year_balances y
  ON y.user_id = u.id AND y.year = :year
LEFT JOIN public.user_leave_monthly_balances m
  ON m.user_id = y.user_id AND m.year = y.year
WHERE u.id = :target_user_id
  AND COALESCE(u.is_deleted, false) = false
  AND (:target_user_id = :requesting_user_id OR :has_hr_admin_permission = true)
GROUP BY y.id, y.user_id, y.year, y.opening_days, y.carryover_days, y.seniority_days, y.remaining_days;
```
- **Data Reality & Expected Behavior**:
  1. `user_leave_year_balances` (`353` rows) + `user_leave_monthly_balances` (`4,238` rows) provide complete annual leave metrics (`CRITICAL-02`).
  2. **DEFECT 02 & CRITICAL-01 Aligned**: `attendance_daily_records` (`54,489` rows) uses the 6-step resolution contract with active membership (`m.status = 'active' AND m.is_deleted = false`). Unresolved, ambiguous, or non-active membership badge records are quarantined and never loaded as orphan `:AttendanceRecord` nodes.
- **Validation Status**: `STATICALLY VALIDATED – NOT EXECUTED`

---

### Scenario `Q12`: Employee Contract History Inquiry (Non-Salary Metadata)
- **Business Question**: *"What is my current employment contract type and contract period (`contract_period_from` to `contract_period_to`)?"*
- **Node Labels**: `:User` (`NM-02`), `:Tenant` (`NM-01`), `:ContractHistory` (`NM-23`)
- **Relationships**: `[:MEMBER_OF]` (`RM-01`), `[:HAS_CONTRACT]` (`RM-38`)
- **Required Properties**: `ContractHistory`: `id`, `tenant_id`, `user_id`, `contract_type`, `contract_period_from`, `contract_period_to`, `is_current`
- **Tenant Rule**: `ch.tenant_id = $tenant_id`
- **Authorization Rule**: **Strict Self-Access (`$target_user_id = $requesting_user_id`)** or HR Contract Admin (`Tier 6 Restricted`).

#### Canonical Cypher Query (`Q12`)
```cypher
MATCH (u:User {id: $target_user_id, is_deleted: false})-[:MEMBER_OF {status: 'active', is_deleted: false}]->(t:Tenant {id: $tenant_id, is_deleted: false})
WHERE $target_user_id = $requesting_user_id OR $has_hr_contract_permission = true
MATCH (u)-[:HAS_CONTRACT]->(ch:ContractHistory {tenant_id: $tenant_id})
RETURN ch.id AS contract_id,
       ch.contract_type AS contract_type,
       ch.contract_period_from AS contract_period_from,
       ch.contract_period_to AS contract_period_to,
       ch.is_current AS is_current
ORDER BY ch.is_current DESC, ch.contract_period_from DESC;
```

#### PostgreSQL Validation SQL (`Q12`)
```sql
SELECT id, contract_type, contract_period_from, contract_period_to, is_current
FROM public.user_contract_histories
WHERE tenant_id = :tenant_id AND user_id = :target_user_id
ORDER BY is_current DESC, contract_period_from DESC;
```
- **Data Reality & Expected Behavior**: `public.user_contract_histories` (`457` rows) uses `contract_period_from` (`date`), `contract_period_to` (`date`), and `is_current` (`bool`, `351` `true` / `106` `false`), and contains **zero salary columns**.
- **Validation Status**: `STATICALLY VALIDATED – NOT EXECUTED`

---

### Scenario `Q13`: Community Posts & Tags by Active Department (DEFECT 06 Lifecycle Filtered)
- **Business Question**: *"What recent community posts (`talk_posts`) have been authored by active members of Department D or tagged with Tag T?"*
- **Node Labels**: `:Post` (`NM-15`), `:Tag` (`NM-24`), `:Audience` (`NM-20`), `:User` (`NM-02`), `:Department` (`NM-03`), `:Tenant` (`NM-01`)
- **Relationships**: `[:AUTHORED_BY]` (`RM-28`), `[:TARGETED_TO]` (`RM-29`), `[:TAGGED_WITH]` (`RM-41`), `[:MEMBER_OF_DEPARTMENT]` (`RM-03`), `[:MEMBER_OF]` (`RM-01`)
- **Required Properties**: `Post`: `id`, `tenant_id`, `title`, `is_deleted`, `created_at` (NO `category_id`); `Tag`: `tag_key`, `tenant_id`, `name`; `MEMBER_OF_DEPARTMENT`: `tenant_id`, `is_active`, `effective_to`
- **Tenant & Lifecycle Rule**: `po.tenant_id = $tenant_id`, `tg.tenant_id = $tenant_id`, and **`dm.is_active = true AND dm.tenant_id = $tenant_id`** (`dm.effective_to IS NULL`).
- **Authorization Rule**: Active member of `$tenant_id`.

#### Canonical Cypher Query (`Q13`)
```cypher
MATCH (req:User {id: $requesting_user_id, is_deleted: false, is_active: true})-[:MEMBER_OF {status: 'active', is_deleted: false}]->(t:Tenant {id: $tenant_id, is_deleted: false})
MATCH (po:Post {tenant_id: $tenant_id, is_deleted: false})-[:AUTHORED_BY]->(u:User {is_deleted: false})
OPTIONAL MATCH (u)-[dm:MEMBER_OF_DEPARTMENT {tenant_id: $tenant_id, is_active: true}]->(d:Department {tenant_id: $tenant_id})
WHERE dm.effective_to IS NULL
OPTIONAL MATCH (po)-[:TAGGED_WITH]->(tg:Tag {tenant_id: $tenant_id})
WITH po, u, collect(DISTINCT d) AS active_depts, collect(DISTINCT tg) AS post_tags
WHERE ($department_id IS NULL OR any(dept IN active_depts WHERE dept.id = $department_id))
  AND ($tag_name IS NULL OR any(tag IN post_tags WHERE toLower(tag.name) = toLower($tag_name)))
RETURN po.id AS post_id,
       po.title AS title,
       u.display_name AS author_name,
       [dept IN active_depts | dept.name] AS author_active_departments,
       [tag IN post_tags | tag.name] AS tags,
       po.created_at AS created_at
ORDER BY po.created_at DESC
LIMIT 20;
```
- **Data Reality & Expected Behavior**: Enforces `dm.is_active = true` (`dm.effective_to IS NULL`) on `[:MEMBER_OF_DEPARTMENT]` (**DEFECT 06**) so historical department assignments do not misattribute a post author's current department.
- **Validation Status**: `STATICALLY VALIDATED – NOT EXECUTED`

---

### Scenario `Q14`: Tenant-Isolated User Directory Fulltext Search (`fts_directory` — DEFECT 05 Resolution)
- **Business Question**: *"Search the employee directory in my current tenant by name, username, or email for keyword `$search_term`."*
- **Node Labels**: `:User` (`NM-02`), `:Tenant` (`NM-01`), `:Department` (`NM-03`)
- **Relationships**: `[:MEMBER_OF]` (`RM-01`), `[:MEMBER_OF_DEPARTMENT]` (`RM-03`)
- **Required Properties**: `User`: `id`, `username`, `email`, `display_name`, `is_active`, `is_deleted` (NO `u.tenant_id`!); `MEMBER_OF`: `tenant_id`, `status`, `is_deleted`, `display_name`, `position`, `department_id`, `is_resigned`; `MEMBER_OF_DEPARTMENT`: `tenant_id`, `is_active`, `is_primary`
- **Tenant & FTS Security Rule (DEFECT 05 — Template FTS-B)**:
  - Because `:User` is a global account node without a `tenant_id` property, `WHERE node.tenant_id = $tenant_id` **MUST NEVER** be used on `fts_directory`.
  - Instead, the query **MUST**:
    1. Verify caller's active membership in `$tenant_id` and directory lookup permission (`$has_directory_search_permission = true`).
    2. Invoke `CALL db.index.fulltext.queryNodes('fts_directory', $search_term) YIELD node AS u, score`.
    3. Immediately bind `MATCH (u)-[m:MEMBER_OF {status: 'active', is_deleted: false}]->(t)` where `t` is `:Tenant {id: $tenant_id, is_deleted: false}`.
    4. Filter `WHERE u.is_active = true AND u.is_deleted = false AND coalesce(m.is_resigned, false) = false`.
    5. Project **only** permitted directory fields from the caller's tenant context `m` (`coalesce(m.display_name, u.display_name)`, `m.position`, `m.department_id`), never exposing cross-tenant memberships or other tenants' profile attributes.

#### Canonical Cypher Query (`Q14`)
```cypher
MATCH (req:User {id: $requesting_user_id, is_active: true, is_deleted: false})-[:MEMBER_OF {status: 'active', is_deleted: false}]->(t:Tenant {id: $tenant_id, is_deleted: false})
WHERE $has_directory_search_permission = true
CALL db.index.fulltext.queryNodes('fts_directory', $search_term) YIELD node AS u, score
MATCH (u)-[m:MEMBER_OF {status: 'active', is_deleted: false}]->(t)
WHERE u.is_active = true
  AND u.is_deleted = false
  AND coalesce(m.is_resigned, false) = false
OPTIONAL MATCH (u)-[dm:MEMBER_OF_DEPARTMENT {tenant_id: $tenant_id, is_active: true, is_primary: true}]->(d:Department {tenant_id: $tenant_id})
WHERE dm.effective_to IS NULL
RETURN u.id AS user_id,
       u.username AS username,
       u.email AS email,
       coalesce(m.display_name, u.display_name) AS display_name,
       m.position AS position,
       d.id AS primary_department_id,
       d.name AS primary_department_name,
       score
ORDER BY score DESC, display_name ASC
LIMIT 20;
```

#### PostgreSQL Validation SQL (`Q14`)
```sql
SELECT u.id AS user_id, u.username, u.email,
       COALESCE(up.display_name, u.username) AS display_name,
       up.position, d.id AS primary_department_id, d.name AS primary_department_name
FROM public.users u
JOIN public.tenant_user_memberships m
  ON m.user_id = u.id
 AND m.tenant_id = :tenant_id
 AND m.status = 'active'
 AND m.is_deleted = false
LEFT JOIN public.user_profiles up
  ON up.user_id = u.id
 AND up.tenant_id = m.tenant_id
LEFT JOIN public.department_members dm
  ON dm.user_id = u.id
 AND dm.tenant_id = m.tenant_id
 AND dm.is_primary = true
 AND dm.effective_to IS NULL
LEFT JOIN public.departments d
  ON d.id = dm.department_id
 AND d.tenant_id = m.tenant_id
WHERE u.is_active = true
  AND u.is_deleted = false
  AND COALESCE(up.is_resigned, false) = false
  AND (
    u.username ILIKE '%' || :search_term || '%'
    OR u.email ILIKE '%' || :search_term || '%'
    OR COALESCE(up.display_name, '') ILIKE '%' || :search_term || '%'
  )
ORDER BY display_name ASC
LIMIT 20;
```
- **Validation Status**: `STATICALLY VALIDATED – NOT EXECUTED`

---

## 3. Security & Cross-Tenant Negative Test Suite (`SEC-01` – `SEC-25`)

Every query and API path must enforce strict tenant isolation and RBAC/ABAC boundaries. These 25 negative and positive test cases (`SEC-01`–`SEC-25`) are verified against synthetic multi-tenant fixtures via `scripts/phase1_2_2/validate_tenant_security.py` and `scripts/phase1_2_2/validate_query_equivalence.py` (`Live Neo4j/PG Runtime Execution: NOT EXECUTED`, mandatory gate before Phase 2 production deployment).

| Test ID | Negative / Positive Test Scenario | Simulated Attack / Input | Expected Backend + SQL/Cypher Defense | Expected Outcome | Status |
|---|---|---|---|---|---|
| `SEC-01` | **User accessing another tenant's `:Project`** | User `u1` (active only in `tenant_id = 1`) requests `project_id = 5` belonging to `tenant_id = 2`. | 1. Backend Auth Guard resolves `$tenant_id = 1` from JWT + `tenant_user_memberships`.<br>2. Cypher `MATCH (p:Project {id: $project_id, tenant_id: $tenant_id})` evaluates `{id: 5, tenant_id: 1}`. | **0 rows returned** (`HTTP 403 / 404`). | `SYNTHETIC TESTED / LIVE NOT EXECUTED` |
| `SEC-02` | **User accessing another tenant's `:Ticket`** | User `u1` (`tenant_id = 1`) queries `ticket_id = 42` in `tenant_id = 2`. | Cypher enforces `tk.tenant_id = $tenant_id` AND project membership check on `p.tenant_id = $tenant_id`. | **0 rows returned**. | `SYNTHETIC TESTED / LIVE NOT EXECUTED` |
| `SEC-03` | **Cross-tenant ticket assignment (`[:ASSIGNED_TO]`)** | ETL receives `ticket_assignees` row linking `ticket` (`tenant_id = 1`) to `user` who is NOT an active member of `tenant_id = 1`. | `RM-13` ETL validation requires `(u)-[:MEMBER_OF {is_deleted: false}]->(:Tenant {id: t.tenant_id})`. | **Edge rejected by ETL** and logged to `etl_quarantine_log` (`CROSS_TENANT_VIOLATION`). | `SYNTHETIC TESTED / LIVE NOT EXECUTED` |
| `SEC-04` | **Cross-tenant approval participant (`[:PARTICIPATES_IN]`)** | User `u1` attempts to view `ApprovalRequest` in `tenant_id = 2` or non-participant `ApprovalRequest` in `tenant_id = 1`. | `Q05` (both Cypher & SQL `CRITICAL-03`) enforces `ar.tenant_id = $tenant_id` (`ut_ar.tenant_id = :tenant_id`), caller active membership in `$tenant_id`, and `(u)-[:PARTICIPATES_IN]->(ar)`. | **0 rows returned**. | `SYNTHETIC TESTED / LIVE NOT EXECUTED` |
| `SEC-05` | **Cross-tenant schedule access (`:ScheduleEvent`)** | User `u1` (`tenant_id = 1`) queries schedule events in `tenant_id = 2` via shared `:ScheduleRoom`. | Even though `:ScheduleRoom` is pooled (`RM-22`), `Q07` anchors on `(ev:ScheduleEvent {tenant_id: $tenant_id})` before `OPTIONAL MATCH (ev)-[:HELD_IN]->(rm)`. | **0 events from `tenant_id = 2` leaked** via shared room node. | `SYNTHETIC TESTED / LIVE NOT EXECUTED` |
| `SEC-06` | **Cross-tenant file access (`:FileMetadata`)** | User `u1` (`tenant_id = 1`) requests `FileMetadata` or Vector chunk with `tenant_id = 2`. | Cypher `Q10` and Vector DB pre-filter enforce `tenant_id = $tenant_id` AND parent project/entity access. | **0 files / 0 vector chunks returned**. | `SYNTHETIC TESTED / LIVE NOT EXECUTED` |
| `SEC-07` | **Cross-tenant & non-participant chat access (`:ChatConversation`)** | User `u1` queries a `:ChatConversation` or `chat_message_chunks` where `u1` is not in `[:MEMBER_OF_CONVERSATION]`. | Both Neo4j `(u)-[:MEMBER_OF_CONVERSATION {is_deleted: false}]->(c:ChatConversation {tenant_id: $tenant_id})` and Vector DB metadata filter `participant_user_ids CONTAINS $requesting_user_id AND tenant_id = $tenant_id` block access. | **0 conversations / 0 message chunks returned**. | `SYNTHETIC TESTED / LIVE NOT EXECUTED` |
| `SEC-08` | **Horizontal privilege escalation on HR Leave/Attendance (`Q11`)** | Regular user `u1` (`id = 10`) asks chatbot for user `u2` (`id = 25`)'s leave balance or attendance in the same tenant. | `Q11` enforces `WHERE $target_user_id = $requesting_user_id OR $has_hr_admin_permission = true`. | **Denied (`0 rows` / `HTTP 403`)**. | `SYNTHETIC TESTED / LIVE NOT EXECUTED` |
| `SEC-09` | **Horizontal privilege escalation on Contract History (`Q12`)** | Regular user `u1` (`id = 10`) asks for user `u2` (`id = 25`)'s employment contract history. | `Q12` enforces `WHERE $target_user_id = $requesting_user_id OR $has_hr_contract_permission = true`. | **Denied (`0 rows` / `HTTP 403`)**. | `SYNTHETIC TESTED / LIVE NOT EXECUTED` |
| `SEC-10` | **Soft-deleted tenant membership access (`[:MEMBER_OF]`)** | User `u1` whose `tenant_user_memberships` row has `is_deleted = true` or `status = 'suspended'` attempts any query in `tenant_id = 1`. | Backend Auth Guard + `public.check_user_permission` + Cypher/SQL preamble `[:MEMBER_OF {status: 'active', is_deleted: false}]` all reject the user. | **Denied at Auth Guard & Graph Preamble**. | `SYNTHETIC TESTED / LIVE NOT EXECUTED` |
| `SEC-11` | **Direct Permission Deny Override (`[:DIRECT_PERMISSION {is_granted: false}]`)** | User `u1` belongs to a `:Role` that grants a permission, but has a direct override `user_permissions.is_granted = false` (`32` such rows exist in `public.user_permissions`). | Both `public.check_user_permission` and `Q02` evaluate `DIRECT_PERMISSION` first (`WHEN dp IS NOT NULL THEN coalesce(dp.is_granted, false)`), overriding role grants. | **`is_permitted = false` (`DENIED`)**. | `SYNTHETIC TESTED / LIVE NOT EXECUTED` |
| `SEC-12` | **Tenant-Scoped Domain Fulltext Search (`fts_work_items`, `fts_communications`, `fts_files`) Cross-Tenant Leak** | User `u1` (`tenant_id = 1`) runs fulltext search for keyword `"roadmap"` on `fts_work_items` / `fts_communications` / `fts_files` matching nodes in `tenant_id = 1` and `tenant_id = 2`. | Template FTS-A immediately applies `YIELD node, score WHERE node.tenant_id = $tenant_id AND coalesce(node.is_deleted, false) = false` plus domain RBAC filter before any traversal or return. | **Only `tenant_id = 1` nodes returned**. | `SYNTHETIC TESTED / LIVE NOT EXECUTED` |
| `SEC-13` | **User Directory FTS (`fts_directory`): Caller in Tenant A searching User in Tenant A (Authorized Positive Control)** | Active user `u1` in `Tenant A` (`$tenant_id = 1`) with `$has_directory_search_permission = true` searches `fts_directory` for an active colleague in `Tenant A`. | `Q14` (`Template FTS-B`) matches `(u)-[m:MEMBER_OF {status: 'active', is_deleted: false}]->(:Tenant {id: 1, is_deleted: false})` and `u.is_active = true AND u.is_deleted = false`. | **Permitted**: Returns `Tenant A` directory fields (`user_id, username, email, display_name, position, primary_department_name`). | `SYNTHETIC TESTED / LIVE NOT EXECUTED` |
| `SEC-14` | **User Directory FTS (`fts_directory`): Caller in Tenant A searching User exclusively in Tenant B** | Active user `u1` in `Tenant A` (`$tenant_id = 1`) searches `fts_directory` for `"alice@tenant-b.com"` where Alice only has `[:MEMBER_OF]` in `Tenant B` (`tenant_id = 2`). | Even though Lucene `fts_directory` yields the global `:User` node for Alice, `MATCH (u)-[m:MEMBER_OF {status: 'active', is_deleted: false}]->(t:Tenant {id: $tenant_id})` fails to match `Tenant A`. | **Denied (`0 rows returned`)**. Zero cross-tenant user leakage. | `SYNTHETIC TESTED / LIVE NOT EXECUTED` |
| `SEC-15` | **User Directory FTS (`fts_directory`): Target User belongs to BOTH Tenant A and Tenant B** | Target user `u_dual` has active `[:MEMBER_OF]` edges to both `Tenant A` (`position = 'Engineer'`) and `Tenant B` (`position = 'Advisor'`). Caller in `Tenant A` searches for `u_dual`. | `Q14` binds `(u)-[m:MEMBER_OF {status: 'active', is_deleted: false}]->(t:Tenant {id: $tenant_id})` where `t.id = Tenant A`, and optional department join filters `dm.tenant_id = $tenant_id`. | **Tenant-Isolated Context**: Returns `u_dual` with **`Tenant A`'s `m.*` and `d.*` attributes only**; never reveals `Tenant B` membership or `Tenant B` profile attributes. | `SYNTHETIC TESTED / LIVE NOT EXECUTED` |
| `SEC-16` | **User Directory FTS (`fts_directory`): Target User has revoked/deleted membership in Tenant A (`m.is_deleted = true`)** | Target user `u_revoked` is still active in `Tenant B`, and had a historical membership in `Tenant A` with `m.is_deleted = true`. Caller in `Tenant A` searches `fts_directory`. | `Q14` requires `(u)-[m:MEMBER_OF {status: 'active', is_deleted: false}]->(t:Tenant {id: $tenant_id})`. | **Denied (`0 rows returned`)**. | `SYNTHETIC TESTED / LIVE NOT EXECUTED` |
| `SEC-17` | **User Directory FTS (`fts_directory`): Target User has inactive membership in Tenant A (`m.status <> 'active'` or `m.is_resigned = true`)** | Target user `u_suspended` has `m.status = 'suspended'` (or `m.is_resigned = true`) in `Tenant A`. Caller in `Tenant A` searches `fts_directory`. | `Q14` enforces `m.status = 'active'` and `coalesce(m.is_resigned, false) = false`. | **Denied (`0 rows returned`)**. | `SYNTHETIC TESTED / LIVE NOT EXECUTED` |
| `SEC-18` | **User Directory FTS (`fts_directory`): Target `:User` node is globally inactive (`u.is_active = false`)** | Target user `u_inactive` has `u.is_active = false` (`140` such rows exist in `public.users`). Caller in `Tenant A` searches `fts_directory`. | `Q14` enforces `WHERE u.is_active = true AND u.is_deleted = false`. | **Denied (`0 rows returned`)**. | `SYNTHETIC TESTED / LIVE NOT EXECUTED` |
| `SEC-19` | **User Directory FTS (`fts_directory`): Target `:User` node is globally soft-deleted (`u.is_deleted = true`)** | Target user `u_del` has `u.is_deleted = true` (`7` such rows exist in `public.users`). Caller in `Tenant A` searches `fts_directory`. | `Q14` enforces `WHERE u.is_active = true AND u.is_deleted = false`. | **Denied (`0 rows returned`)**. | `SYNTHETIC TESTED / LIVE NOT EXECUTED` |
| `SEC-20` | **User Directory FTS (`fts_directory`): Caller lacks directory search permission in Tenant A** | Authenticated user `u_restricted` in `Tenant A` has a Direct Permission Deny Override (`is_granted = false`) on directory lookup (`$has_directory_search_permission = false`). | Backend `check_user_permission` rejects request before graph execution, and `Q14` enforces `WHERE $has_directory_search_permission = true`. | **Denied (`0 rows` / `HTTP 403`)**. | `SYNTHETIC TESTED / LIVE NOT EXECUTED` |
| `SEC-21` | **Approval `Q05` Cross-Tenant Participant Leakage (`CRITICAL-03`)** | Multi-tenant user `u_dual` (active in `Tenant 1`, participant on an `IN_PROGRESS` approval request `ar_t2` belonging to `Tenant 2`) runs `Q05` in `Tenant 1` context (`:tenant_id = 1`). | Both Cypher `Q05` (`ar.tenant_id = $tenant_id`) and PostgreSQL `Q05` (`ut_ar.tenant_id = t.id`) filter out `ar_t2` because `ar_t2` belongs to `Tenant 2`. | **Denied (`0 rows` from `Tenant 2` returned in `Tenant 1` context)**. | `SYNTHETIC TESTED / LIVE NOT EXECUTED` |
| `SEC-22` | **Notice `Q08` Cross-Tenant Notice & Custom Audience Contamination (`CRITICAL-04`)** | Notice `nt_t2` in `Tenant 2` targets global system audience (`id=1`) or a custom audience `a_t2` in `Tenant 2`. User `u1` in `Tenant 1` runs `Q08` (`:tenant_id = 1`). | Both Cypher `Q08` (`nt.tenant_id = $tenant_id`, `a.tenant_id = $tenant_id`) and PostgreSQL `Q08` (`ut_nt.tenant_id = t.id`, `ut_au.tenant_id = t.id`) block `nt_t2` and `a_t2`. | **Denied (`0 rows` from `Tenant 2` returned)**. | `SYNTHETIC TESTED / LIVE NOT EXECUTED` |
| `SEC-23` | **Department `Q01` Inactive or Cross-Tenant Manager Attribution (`HIGH-05`)** | Department `d1` in `Tenant 1` has `manager_user_id = u_mgr_inactive` whose membership in `Tenant 1` is `status = 'suspended'` (or `is_deleted = true`, or only active in `Tenant 2`). | Both `RM-04` and `Q01` (Cypher & SQL) require `mgr.is_active = true AND mgr.is_deleted = false` AND active membership (`status = 'active', is_deleted = false`) in `d1.tenant_id`. | **`manager_id = NULL` (`u_mgr_inactive` excluded from manager role)**. | `SYNTHETIC TESTED / LIVE NOT EXECUTED` |
| `SEC-24` | **Attendance `NM-22` / `RM-37` Inactive or Soft-Deleted Membership Resolution (`CRITICAL-01`)** | Attendance rows exist for `u_inactive` (`status = 'inactive'`, `Case B`), `u_suspended` (`status = 'suspended'`, `Case C`), and `u_del_mem` (`is_deleted = true`, `Cases D/E`). | `NM-22` and `RM-37` CTEs enforce `m.status = 'active' AND m.is_deleted = false` (`Rule MEM-ACTIVE`). | **Rejected & Quarantined (`INVALID_TENANT` / `UNRESOLVED`); `0` nodes created**. | `SYNTHETIC TESTED / LIVE NOT EXECUTED` |
| `SEC-25` | **LeaveBalance `NM-21` Multi-Tenant Ambiguity Quarantine (`CRITICAL-02`)** | User `u_multi` holds non-deleted memberships in both `Tenant 1` and `Tenant 2`, and has a row in `user_leave_year_balances` (which has no `tenant_id` column). | `NM-21` and `RM-36` CTE `user_unambiguous_leave_tenant` enforces `HAVING count(DISTINCT m.tenant_id) = 1`. | **Quarantined (`AMBIGUOUS_TENANT`); `0` cross-tenant duplicate `:LeaveBalance` nodes created**. | `SYNTHETIC TESTED / LIVE NOT EXECUTED` |

---

## 4. SQL-vs-Cypher Semantic Equivalence Verification Matrix (`CRITICAL-03`, `CRITICAL-04`, `HIGH-05`)

To guarantee that the PostgreSQL Validation SQL and Neo4j Canonical Cypher queries enforce the **exact same security, tenant isolation, and lifecycle semantics**, the rule-by-rule comparison tables below verify semantic equivalence across `Q01`, `Q05`, and `Q08` (and summarize `Q01`–`Q14`).

### 4.1 Scenario `Q01` Semantic Equivalence Table (`HIGH-05` & `DEFECT 06`)

| Semantic Rule Dimension | PostgreSQL Validation SQL (`Q01`) | Neo4j Canonical Cypher (`Q01`) | Equivalence Status |
|---|---|---|---|
| **1. Tenant Root Filter** | `WHERE t.id = :tenant_id AND COALESCE(t.is_deleted, false) = false` | `MATCH (t:Tenant {id: $tenant_id, is_deleted: false})` | **`EQUIVALENT`** |
| **2. Requesting User Active Membership** | `INNER JOIN public.users req ON req.id = :requesting_user_id AND req.is_active = true AND req.is_deleted = false INNER JOIN public.tenant_user_memberships req_m ON req_m.user_id = req.id AND req_m.tenant_id = t.id AND req_m.status = 'active' AND req_m.is_deleted = false` | `<-[req_m:MEMBER_OF {status: 'active', is_deleted: false}]-(req:User {id: $requesting_user_id, is_deleted: false, is_active: true})` | **`EQUIVALENT`** |
| **3. Target Department Tenant Filter** | `INNER JOIN public.departments d ON d.tenant_id = t.id WHERE (d.id = :department_id OR LOWER(d.name) LIKE ...)` | `MATCH (d:Department {tenant_id: $tenant_id})-[:BELONGS_TO_TENANT]->(t) WHERE d.id = $department_id OR toLower(d.name) CONTAINS ...` | **`EQUIVALENT`** |
| **4. Optional Manager Active Tenant Membership (`HIGH-05`)** | `LEFT JOIN (users mgr INNER JOIN tenant_user_memberships mgr_m ON mgr_m.user_id = mgr.id AND mgr_m.status = 'active' AND mgr_m.is_deleted = false ...) ON mgr.id = d.manager_user_id AND mgr_m.tenant_id = d.tenant_id AND mgr.is_active = true AND mgr.is_deleted = false` | `OPTIONAL MATCH (mgr:User {is_deleted: false, is_active: true})-[:MANAGES {tenant_id: $tenant_id}]->(d) WHERE EXISTS { MATCH (mgr)-[:MEMBER_OF {status: 'active', is_deleted: false}]->(t) }` | **`EQUIVALENT`** |
| **5. Sub-Department Tenant Isolation** | `LEFT JOIN public.departments sub ON sub.parent_id = d.id AND sub.tenant_id = d.tenant_id` | `OPTIONAL MATCH (sub:Department {tenant_id: $tenant_id})-[:SUB_DEPARTMENT_OF]->(d)` | **`EQUIVALENT`** |
| **6. Active Department Member Lifecycle (`DEFECT 06`)** | `LEFT JOIN (department_members dm INNER JOIN users emp ... INNER JOIN tenant_user_memberships emp_m ...) ON dm.department_id = d.id AND dm.tenant_id = d.tenant_id AND dm.effective_to IS NULL` | `OPTIONAL MATCH (emp:User {is_deleted: false, is_active: true})-[dm:MEMBER_OF_DEPARTMENT {tenant_id: $tenant_id, is_active: true}]->(d) WHERE dm.effective_to IS NULL AND EXISTS { MATCH (emp)-[:MEMBER_OF {status: 'active', is_deleted: false}]->(t) }` | **`EQUIVALENT`** |
| **7. Ordering & Projection** | Returns `department_id, department_code, department_name, is_active, manager_id, manager_name, sub_department_count, active_employee_count ORDER BY d.id ASC` | Returns `department_id, department_code, department_name, is_active, manager_id, manager_name, sub_departments, active_employees ORDER BY d.id ASC` | **`EQUIVALENT`** |

### 4.2 Scenario `Q05` Semantic Equivalence Table (`CRITICAL-03` & `DEFECT 03`)

| Semantic Rule Dimension | PostgreSQL Validation SQL (`Q05`) | Neo4j Canonical Cypher (`Q05`) | Equivalence Status |
|---|---|---|---|
| **1. Tenant Root Filter** | `WHERE t.id = :tenant_id AND COALESCE(t.is_deleted, false) = false` | `MATCH ... ->(t:Tenant {id: $tenant_id, is_deleted: false})` | **`EQUIVALENT`** |
| **2. Requesting User Active Tenant Membership** | `INNER JOIN public.users u ON u.id = :requesting_user_id AND u.is_active = true AND u.is_deleted = false INNER JOIN public.tenant_user_memberships m_req ON m_req.user_id = u.id AND m_req.tenant_id = t.id AND m_req.status = 'active' AND m_req.is_deleted = false` | `MATCH (u:User {id: $requesting_user_id, is_deleted: false, is_active: true})-[:MEMBER_OF {status: 'active', is_deleted: false}]->(t:Tenant {id: $tenant_id, is_deleted: false})` | **`EQUIVALENT`** |
| **3. Approval Request Tenant Ownership (`CRITICAL-03`)** | `INNER JOIN user_unambiguous_tenant ut_ar ON ut_ar.user_id = ar.created_by_user_id AND ut_ar.tenant_id = t.id` | `MATCH (u)-[hp:PARTICIPATES_IN]->(ar:ApprovalRequest {tenant_id: $tenant_id, ...})` (where `ar.tenant_id` was derived by `NM-10` using the exact same `user_unambiguous_tenant` CTE) | **`EQUIVALENT`** |
| **4. Request Lifecycle Filter** | `AND ar.status = 'IN_PROGRESS' AND COALESCE(ar.is_deleted, false) = false` | `{tenant_id: $tenant_id, status: 'IN_PROGRESS', is_deleted: false}` | **`EQUIVALENT`** |
| **5. Participant Role, Action Status & `sequence_order` (`DEFECT 03`)** | `INNER JOIN public.approval_participants ap ON ap.user_id = u.id AND ap.request_id = ar.id ... AND ap.action_status IN ('PENDING', 'WAITING') AND ap.participant_role IN ('APPROVER', 'AGREEMENTOR')` | `MATCH (u)-[hp:PARTICIPATES_IN]->(ar) WHERE hp.action_status IN ['PENDING', 'WAITING'] AND hp.participant_role IN ['APPROVER', 'AGREEMENTOR']` | **`EQUIVALENT`** |
| **6. Requester Name & Ordering** | `LEFT JOIN public.users sub ... COALESCE(up_sub.display_name, sub.username) AS requester_name ORDER BY ar.submitted_at DESC, ap.sequence_order ASC` | `OPTIONAL MATCH (ar)-[:CREATED_BY]->(sub:User) RETURN ..., sub.display_name AS requester_name, ar.submitted_at ORDER BY ar.submitted_at DESC, hp.sequence_order ASC` | **`EQUIVALENT`** |

### 4.3 Scenario `Q08` Semantic Equivalence Table (`CRITICAL-04`, `DEFECT 04` & `DEFECT 06`)

| Semantic Rule Dimension | PostgreSQL Validation SQL (`Q08`) | Neo4j Canonical Cypher (`Q08`) | Equivalence Status |
|---|---|---|---|
| **1. Tenant Root & Requesting User Active Membership** | `INNER JOIN public.users u ON u.id = :requesting_user_id AND u.is_active = true AND u.is_deleted = false INNER JOIN public.tenant_user_memberships m_req ON m_req.user_id = u.id AND m_req.tenant_id = t.id AND m_req.status = 'active' AND m_req.is_deleted = false WHERE t.id = :tenant_id AND t.is_deleted = false` | `MATCH (u:User {id: $requesting_user_id, is_deleted: false, is_active: true})-[:MEMBER_OF {status: 'active', is_deleted: false}]->(t:Tenant {id: $tenant_id, is_deleted: false})` | **`EQUIVALENT`** |
| **2. Notice Tenant Ownership & Publication State (`CRITICAL-04`)** | `INNER JOIN public.notices nt ON nt.is_published = true AND COALESCE(nt.is_deleted, false) = false INNER JOIN user_unambiguous_tenant ut_nt ON ut_nt.user_id = nt.created_by_user_id AND ut_nt.tenant_id = t.id` | `MATCH (nt:Notice {tenant_id: $tenant_id, is_published: true, is_deleted: false})-[:TARGETED_TO]->(a:Audience {is_active: true})` | **`EQUIVALENT`** |
| **3. Branch 1 — Global System Audience (`DEFECT 04`)** | `COALESCE(a.is_system, false) = true AND a.owner_user_id IS NULL AND a.audience_type = 'ALL' AND adm_t.audience_id IS NULL AND aum_t.audience_id IS NULL` | `a.is_system = true AND a.tenant_id IS NULL AND a.audience_type = 'ALL'` (validated at ETL time by `NM-20` to have `owner_user_id IS NULL` and `0` member edges) | **`EQUIVALENT`** |
| **4. Branch 2 — Custom Audience Tenant Ownership (`CRITICAL-04`)** | `COALESCE(a.is_system, false) = false AND ut_au.tenant_id = t.id AND (adm_t.audience_id IS NULL OR (adm_t.dept_tenant_cnt = 1 AND adm_t.dept_tenant_id = t.id)) AND (aum_t.audience_id IS NULL OR (aum_t.user_tenant_cnt = 1 AND aum_t.user_tenant_id = t.id))` | `a.is_system = false AND a.tenant_id = $tenant_id` (where `a.tenant_id` is populated by `NM-20` using the exact same `ut_au` + `adm_t` + `aum_t` predicate) | **`EQUIVALENT`** |
| **5. Branch 2 — User & Active Department Targeting (`DEFECT 06`)** | `AND (aum.user_id IS NOT NULL OR adm.department_id IS NOT NULL)` with `dm.user_id = u.id AND dm.tenant_id = t.id AND d.tenant_id = t.id AND dm.effective_to IS NULL` | `EXISTS { MATCH (a)-[:INCLUDES_USER]->(u) } OR EXISTS { MATCH (a)-[:INCLUDES_DEPARTMENT]->(d:Department {tenant_id: $tenant_id})<-[dm:MEMBER_OF_DEPARTMENT {tenant_id: $tenant_id, is_active: true}]-(u) WHERE dm.effective_to IS NULL }` | **`EQUIVALENT`** |
| **6. Publisher Projection, Ordering & Limit** | `COALESCE(up_pub.display_name, pub.username) AS author_name ... ORDER BY nt.published_at DESC LIMIT 20` | `OPTIONAL MATCH (nt)-[:PUBLISHED_BY]->(pub:User) ... ORDER BY nt.published_at DESC LIMIT 20` | **`EQUIVALENT`** |

### 4.4 Phase 1.2.3.1 Independent Execution & Hardening Updates (DEF-P1231-01, DEF-P1231-02, DEF-P1231-03)

1. **Independent Dual-Engine Simulators (DEF-P1231-01)**:
   - Implemented true independent simulation architectures:
     - Relational simulator in 	ests/phase1_2_3_1/relational/ executing SQL relational semantics (CTEs, joins, GROUP BY).
     - Graph traversal simulator in 	ests/phase1_2_3_1/graph/ executing Neo4j pattern matching and graph index traversal.
   - Verified via AST inspection (IND-01) that neither simulator imports, delegates to, or calls the other.
   - Verified via intentional rule divergence test (IND-02) that mutating graph-side logic immediately produces divergence against SQL outputs, proving true independent execution.

2. **Q01 Output Contract & Caller Authorization Hardening (Q01-01..Q01-12)**:
   - Structured JSON collections (sub_departments and ctive_employees) return empty arrays [] on leaf/empty departments rather than nulls.
   - Caller authorization guard enforces active user and membership before returning data.
   - Verified across test suite Q01-01 through Q01-12 (12/12 PASS, 100% equivalence).

3. **Q08 Multi-Source Isolation & 6 Global Invariants (DEF-P1231-02, DEF-P1231-03, Q08-01..Q08-18)**:
   - Enforces all 6 Global Audience Invariants: is_system = true, 	enant_id IS NULL, udience_type = 'ALL', owner_user_id IS NULL, 0 department members, and 0 user members.
   - Enforces independent multi-source custom audience tenant isolation (owner, all dept members, all user members).
   - Reconciled output to canonical 9 fields: 
otice_id, 	itle, 
otice_type, priority, udience_name, udience_type, is_system_audience, uthor_name, and published_at with LIMIT 20.
   - Verified across test suite Q08-01 through Q08-18 (18/18 PASS, 100% equivalence).
