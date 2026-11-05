# 12 / 13 – Multi-Tenant Architecture & Authorization Specification
## Groupware AI Chatbot Project – Phase 1: Canonical Baseline & Architectural Reconciliation

> [!NOTE]
> This document establishes the **authoritative Multi-Tenant Architecture & Authorization Specification** for the Groupware AI Chatbot. It defines the six tenant ownership categories, the Neo4j multi-tenant graph strategy, tenant-isolation enforcement rules, and evaluates RBAC authorization mechanisms based on verified database evidence.
>
> *(Both `12_tenant_and_authorization_model.md` and `13_tenant_and_authorization_discovery.md` represent the identical, synchronized canonical deliverable to preserve legacy cross-references).*

---

## 1. Multi-Tenant Architecture & Membership Analysis

### A. The Tenant Root Boundary
- Physical Table: `tenants` (schema `public`).
- Record Population: Exactly **1 active record**.
  - `id`: `1`
  - `name`: `Default Tenant`
  - `slug`: `legacy-default`
  - `status`: `active`
- **Architectural Pattern**: The current system operates in a **Single-Tenant Pooled Architecture** under Tenant 1 (`legacy-default`). The database schema is multi-tenant capable, but populated with a single production tenant snapshot.

### B. Full Schema & Records of `tenant_user_memberships`
Inspection of `tenant_user_memberships` reveals:
- Columns:
  - `id`: `bigint` (Primary Key)
  - `tenant_id`: `bigint`
  - `user_id`: `integer`
  - `status`: `character varying(50)`
  - `is_default`: `boolean`
  - `joined_at`: `timestamp with time zone`
  - Audit columns: `created_by_id`, `updated_by_id`, `is_deleted`, `deleted_at`, `deleted_by_id`, `created_at`, `updated_at`.
- Constraint Check: The only table constraint is the primary key `tenant_user_memberships_pkey` on `id`. There is **no composite unique constraint** on `(tenant_id, user_id)` at the DDL level.
- Record Population: Exactly **360 records**.
  - Exactly matches the 360 rows in `users`.
  - All 360 records have `tenant_id = 1`, `status = 'active'`, and `is_default = true`.
- **Multi-Tenant Capability Assessment**:
  - *Can a user belong to multiple tenants?* **Yes, architecturally.** The absence of a unique constraint on `user_id` allows a user to have multiple membership rows across different `tenant_id`s in future multi-tenant rollouts.
  - *Does any user currently belong to multiple tenants?* **No.** In the current data snapshot, each user is mapped 1:1 strictly to Tenant 1.

---

## 2. Six Tenant Ownership Categories

For every graph entity in the Groupware system, tenant ownership is categorized into six architectural classes:

| Tenant Ownership Category | Definition & Criteria | Target Entities & Tables | Source of Truth for Ownership | Neo4j Graph Materialization Strategy |
|---|---|---|---|---|
| **1. Direct Tenant-Owned** | Table possesses a physical, direct `tenant_id` column. | `departments`, `user_profiles`, `tenant_user_memberships`. | Source table column `tenant_id`. | Node property `tenant_id` populated directly from source column; edge `(:Department)-[:BELONGS_TO]->(:Tenant)`. |
| **2. Global / Shared Master** | System-wide reference data, taxonomy, or resource definitions shared across tenants. | `roles`, `permissions`, `schedule_rooms`, `asset_categories`. | Global system configuration. | Nodes marked `{is_global: true}`; tenant-specific assignments link users to global roles. |
| **3. User Membership Scoped** | Global employee actor associated with tenants via explicit membership edges. | `users` (`users.id`). | `tenant_user_memberships`. | Central actor node `(:User)` connected to tenant via `(:User)-[:MEMBER_OF {status: 'active', is_default: true}]->(:Tenant {id: 1})`. |
| **4. Tenant-Scoped Relationship** | Edges that must never cross tenant boundaries under any circumstances. | All organizational edges (`[:MANAGES]`, `[:MEMBER_OF]`, `[:ASSIGNED_TO]`). | Application tenant context. | Cypher query traversal enforces matching `tenant_id` on both endpoints: `WHERE a.tenant_id = b.tenant_id`. |
| **5. Derived Transitive Association** | Table lacks a direct `tenant_id` column; tenant ownership is transitively derived from creator or department. | `projects`, `tickets`, `approval_requests`, `schedule_events`, `notices`, `assets`. | Transitive path: `creator_user_id -> users.id -> tenant_user_memberships.tenant_id`. | **ETL Injection Rule**: The ingestion pipeline explicitly injects property `tenant_id: 1` onto every derived node at ingest time. |
| **6. Unresolved Tenant Ownership** | Records lacking valid creator, department, or membership links (legacy orphan data). | 0 records in active core business data (orphan test records reside in backup). | Unresolved. | Discarded during ingestion or flagged with `tenant_id: -1` (Quarantine). |

---

## 3. Multi-Tenant Graph Strategy (Neo4j Architecture)

To ensure absolute multi-tenant data isolation and high-performance querying in the AI Chatbot:

1. **Root Tenant Node**:
   ```cypher
   (:Tenant {id: 1, name: 'Default Tenant', slug: 'legacy-default', status: 'active'})
   ```
2. **Mandatory Property Stamping**:
   - The ETL pipeline explicitly stamps the property `tenant_id: 1` on **every single business node** (`:User`, `:Project`, `:Ticket`, `:Department`, `:ApprovalRequest`, `:ScheduleEvent`, `:Asset`, `:Notice`).
3. **Graph Range Indexing for Isolation**:
   - Range indexes are created on `tenant_id` across all primary labels:
     ```cypher
     CREATE INDEX user_tenant_idx FOR (n:User) ON (n.tenant_id);
     CREATE INDEX project_tenant_idx FOR (n:Project) ON (n.tenant_id);
     CREATE INDEX ticket_tenant_idx FOR (n:Ticket) ON (n.tenant_id);
     CREATE INDEX dept_tenant_idx FOR (n:Department) ON (n.tenant_id);
     CREATE INDEX approval_tenant_idx FOR (n:ApprovalRequest) ON (n.tenant_id);
     ```
4. **Backend Query Boundary Enforcement**:
   - Every Cypher query executed by LangGraph multi-agent tools must inject a `$tenantId` parameter supplied by the authenticated user's session token:
     ```cypher
     MATCH (p:Project {tenant_id: $tenantId})<-[:BELONGS_TO]-(t:Ticket {tenant_id: $tenantId})
     WHERE p.key = $projectKey
     RETURN t.title, t.priority
     ```

---

## 4. RBAC Authorization & Security Rules

### A. Authorization Data Assets in PostgreSQL
- `roles`: 42 defined roles (e.g., `SuperAdmin`, `HRManager`, `ProjectManager`, `Employee`).
- `permissions`: 247 discrete operational permissions (e.g., `ticket:read`, `approval:create`, `salary:view`).
- `role_permissions`: 1,535 active role-to-permission mappings.
- `user_role_assignments`: 448 active user-to-role assignments.
- `user_permissions`: **51 records** representing direct per-user overrides:
  - `is_granted = true`: **19 records** (Direct Allow override).
  - `is_granted = false`: **32 records** (Direct Deny override).

### B. Precedence Evaluation Status: Unverified Business Rule

> [!WARNING]
> **Status: UNVERIFIED BUSINESS RULE / HYPOTHESIS**
> The rule `Direct Deny > Direct Grant > Role Grant` is a standard enterprise RBAC pattern and is supported by the existence of `is_granted = false` records in `user_permissions`.
> 
> However, because backend application source code is **NOT present** in the database dump, this precedence rule MUST be explicitly classified as an **UNVERIFIED BUSINESS RULE**.
> 
> It must NOT be encoded into Cypher queries or trusted as fact until confirmed by backend engineering in Phase 2.

### C. Four Cardinal Security Governance Rules for AI Chatbot

1. **LLM Never Determines Authorization**: The Large Language Model must NEVER be prompted to decide whether a user is allowed to see data. Access control is strictly enforced by deterministic code.
2. **Graph Relationships Are Not Proof of Permission**: The presence of an edge in Neo4j (e.g., `(:User)-[:MEMBER_OF]->(:Project)`) does NOT automatically grant permission to read confidential project budgets.
3. **Backend Authorization Interceptor**: The backend API / LangGraph orchestration layer must evaluate user permissions from JWT claims, inject tenant and scope filters into queries, and validate results before passing them to LLM generation nodes.
4. **Vector Retrieval Enforces Tenant and ACL Filters**: All Vector DB queries against `chat_messages` or document embeddings must apply metadata filters: `filter: {tenant_id: $tenantId, conversation_id: {$in: $accessibleChannels}}`.
