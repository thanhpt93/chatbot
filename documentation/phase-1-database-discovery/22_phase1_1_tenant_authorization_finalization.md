# 22 – Phase 1.1 Tenant Isolation & Authorization Architecture
## Groupware AI Chatbot Project – Multi-Tenancy & Security Baseline

> [!IMPORTANT]
> **Security & Governance Standards**:
> 1. Multi-tenancy is an architectural imperative. The graph must support multiple tenants even if the current development snapshot contains only one active tenant (`tenant_id = 1`). Never hardcode `tenant_id = 1`!
> 2. The LLM must NEVER independently determine or enforce user authorization. Authorization boundaries must be strictly evaluated by the backend application layer before queries reach the graph or before retrieved data is synthesized.

---

## 1. Physical Schema Discovery: User & Tenant Model

### 1.1 Physical Schema Reality
Analysis of PostgreSQL system catalogs reveals key structural facts:
1. **The `users` table does NOT contain a `tenant_id` column**:
   - `users`: `id` (integer), `username`, `email`, `password_hash`, `is_active`, `is_deleted`.
2. **Tenant membership is established through satellite structures**:
   - `user_profiles.tenant_id`: `bigint` (360 rows, populated).
   - `tenant_user_memberships`: Junction table mapping `user_id` (`bigint`) to `tenant_id` (`bigint`) with `status`, `is_default`, and `joined_at`.
3. **Data Type Divergence**:
   - `users.id` is `integer` (`int4`).
   - `tenant_user_memberships.user_id` is `bigint` (`int8`).
   - `tenant_user_memberships.tenant_id` is `bigint` (`int8`).

### 1.2 Graph Modeling Strategy
To combine strict multi-tenant isolation with high-performance graph traversal:
- **Structural Membership Edge**: Model `(:User)-[:MEMBER_OF {joined_at: DateTime, is_default: Boolean}]->(:Tenant)`.
- **Property-Level Invalidation Key**: During ETL ingestion, inject `tenant_id: Integer` as a native property on each `:User` node (derived from `user_profiles.tenant_id` or active `tenant_user_memberships`).
- **Indexed Tenant Filtering**: Create a Range Index on `(u:User {tenant_id})`. Every query executed by the application backend must inject `WHERE u.tenant_id = $session_tenant_id`.

---

## 2. Tenant Ownership Derivation Rules

Because several PostgreSQL tables do not contain a physical `tenant_id` column, the graph ingestion pipeline must follow deterministic, verified derivation rules:

| Entity Label | Source Table | Direct `tenant_id` Column? | Derivation Logic & Rule | Verification Status | Fallback / Conflict Handling |
|---|---|---|---|---|---|
| `:Tenant` | `public.tenants` | Yes (`id`) | Root isolation entity. | **VERIFIED** | None |
| `:User` | `users` / `user_profiles` | Yes (in `user_profiles`) | Extracted directly from `user_profiles.tenant_id`. | **VERIFIED** | If null, lookup `tenant_user_memberships.is_default = true`. |
| `:Department`| `public.departments` | Yes (`tenant_id`) | Extracted directly from `departments.tenant_id`. | **VERIFIED** | If null, marked `UNRESOLVED`. |
| `:Role` | `public.roles` | Yes (in `user_role_assignments`)| Extracted from `user_role_assignments.tenant_id` or default system tenant. | **VERIFIED** | System roles marked global or replicated per tenant. |
| `:Permission`| `public.permissions` | Yes (in assignment tables)| Associated to tenant through role assignments. | **VERIFIED** | Standard permission catalog. |
| `:Project` | `public.projects` | No | Derived transitively from creator: `users.id = projects.created_by_user_id` -> `user_profiles.tenant_id`. | **VERIFIED IN DATA** | 65/65 projects created by users belonging to Tenant 1. |
| `:Ticket` | `public.tickets` | No | Derived transitively from parent project: `projects.id = tickets.project_id`. | **VERIFIED IN DATA** | All parent projects have verified tenant ownership. |
| `:Sprint` | `public.project_sprints` | No | Derived transitively from parent project: `projects.id = project_sprints.project_id`. | **VERIFIED IN DATA** | All parent projects have verified tenant ownership. |
| `:KanbanColumn`| `public.kanban_columns` | No | Derived transitively from parent project: `projects.id = kanban_columns.project_id`. | **VERIFIED IN DATA** | All parent projects have verified tenant ownership. |
| `:ApprovalRequest`| `public.approval_requests`| No | Derived transitively from requester: `users.id = approval_requests.created_by_user_id`. | **VERIFIED IN DATA** | 318/318 creators map to verified tenant profiles. |
| `:WorkflowTemplate`| `approval_workflow_templates`| No | Derived from creator or designated as tenant-scoped template. | **RULE CANDIDATE** | Inherited from active tenant configuration. |
| `:ScheduleEvent` | `public.schedule_events` | No | Derived transitively from event organizer: `users.id = schedule_events.user_id`. | **VERIFIED IN DATA** | All organizers map to verified tenant profiles. |
| `:ScheduleRoom` | `public.schedule_rooms` | No | Associated to tenant via site/facility management. | **RULE CANDIDATE** | Scoped to tenant facility settings. |
| `:Notice` | `public.notices` | No | Derived transitively from author: `users.id = notices.created_by_user_id`. | **VERIFIED IN DATA** | All authors belong to verified tenant. |
| `:Post` | `public.talk_posts` | No | Derived transitively from author: `users.id = talk_posts.author_user_id`. | **VERIFIED IN DATA** | All authors belong to verified tenant. |
| `:Asset` | `public.assets` | No | Derived from department affiliation: `departments.id = assets.department_id`. | **VERIFIED IN DATA** | Fallback to `assigned_user_id` profile tenant. |
| `:FileMetadata` | `public.files` | No | Derived from uploader: `users.id = files.uploaded_by_user_id`. | **VERIFIED IN DATA** | All uploaders map to verified tenant profiles. |
| `:ChatConversation`| `chat_conversations` | No | Derived from creator: `users.id = chat_conversations.created_by_user_id`. | **VERIFIED IN DATA** | All group/channel creators belong to verified tenant. |

### 2.4 Prevention of Cross-Tenant Relationships
During ETL ingestion, the pipeline must enforce **Strict Tenant Integrity Validation**:
- If `source.tenant_id != target.tenant_id`, the ingestion script must abort edge creation and log a **Security Violation Incident**.
- Cross-tenant relationships are strictly prohibited in the Knowledge Graph.

---

## 3. Role-Based Access Control (RBAC) Architecture

### 3.1 Physical Security Tables in PostgreSQL
- `roles`: System and custom role definitions (e.g. `ADMIN`, `MANAGER`, `STAFF`).
- `permissions`: Atomic capabilities defined by `resource_type` and `action_id`.
- `user_role_assignments`: Maps users to roles with `tenant_id`.
- `role_permissions`: Maps roles to permissions with `is_granted = true/false`.
- `user_permissions`: Direct per-user overrides with `is_granted = true/false` (51 rows in database).

### 3.2 RBAC Precedence Evaluation: Unverified Hypothesis
- Earlier documentation asserted the precedence hierarchy:
  $$\mathbf{Direct\ Deny} > \mathbf{Direct\ Grant} > \mathbf{Role\ Grant}$$
- **Formal Status**: This precedence order is an **UNVERIFIED BUSINESS RULE / HYPOTHESIS**.
- Database triggers, stored procedures, and views **do not implement** permission evaluation logic. The evaluation algorithm is executed entirely within compiled backend application code.
- **Mandatory Prerequisite**: The chatbot development team must inspect backend service code (or verify with application maintainers) to confirm the exact resolution algorithm before Phase 3 authorization filters are implemented.

### 3.3 Graph Authorization Query Contract
In Neo4j, user effective permissions are queried via graph traversal:
```cypher
// Check if user has explicit or role-based permission
MATCH (u:User {id: $user_id, tenant_id: $tenant_id})
OPTIONAL MATCH (u)-[d:DIRECT_PERMISSION]->(p:Permission {code: $permission_code})
OPTIONAL MATCH (u)-[:HAS_ROLE]->(r:Role)-[rp:INCLUDES_PERMISSION]->(p)
RETURN 
  CASE 
    WHEN d.is_granted = false THEN 'DENIED'
    WHEN d.is_granted = true THEN 'GRANTED'
    WHEN rp.is_granted = true THEN 'GRANTED'
    ELSE 'DENIED'
  END AS access_decision;
```
*(Note: Decision logic will be updated to match the verified backend algorithm).*
