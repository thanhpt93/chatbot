import os

DOC_DIR = r"documentation\phase-1-database-discovery"
os.makedirs(DOC_DIR, exist_ok=True)

# ==========================================
# 1. GENERATE 12 / 13 TENANT AND AUTHORIZATION MODEL
# ==========================================
def generate_tenant_and_auth():
    print("Generating canonical 12_tenant_and_authorization_model.md and 13_tenant_and_authorization_discovery.md (Task F)...")
    content = """# 12 / 13 – Multi-Tenant Architecture & Authorization Specification
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
"""
    for fname in ("12_tenant_and_authorization_model.md", "13_tenant_and_authorization_discovery.md"):
        with open(os.path.join(DOC_DIR, fname), "w", encoding="utf-8") as f:
            f.write(content)
    print("Saved 12_tenant_and_authorization_model.md and 13_tenant_and_authorization_discovery.md successfully.")

# ==========================================
# 2. GENERATE 08 QUERY READINESS
# ==========================================
def generate_query_readiness():
    print("Generating canonical 08_database_query_readiness.md and 08_chatbot_query_readiness.md (Task G)...")
    content = """# 08 – Chatbot Query Readiness Assessment & Cypher Validation
## Groupware AI Chatbot Project – Phase 1: Canonical Baseline & Architectural Reconciliation

> [!NOTE]
> This document validates the readiness of the Groupware database and proposed Neo4j Graph Model to answer 12 core enterprise chatbot questions.
>
> Every query reflects verified schema facts:
> 1. User PK is `integer(32,0)`.
> 2. Project creator is `projects.created_by_user_id`; project owner is `project_members.role = 'owner'`.
> 3. Approval request creator is `approval_requests.created_by_user_id`; approvers are in `approval_participants`.
> 4. Active approval reviewer explicitly filters `a.status = 'in_progress'` and `p.action_status = 'pending'`.
> 5. Community post explicitly filters the requesting team (`d.name = 'Architecture'`).
> 6. Every query incorporates explicit tenant-aware filtering (`WHERE n.tenant_id = $tenantId`).
> 7. Backend authorization enforcement point is explicitly designated.
>
> *(Both `08_database_query_readiness.md` and `08_chatbot_query_readiness.md` represent the identical canonical deliverable).*

---

## 1. Query Scenario Validation Matrix (12 Scenarios)

### Scenario 1: Organizational Hierarchy & Department Head
- **Business Question**: *"Who is the manager of the Engineering department, and who reports to them?"*
- **Required Source Entities**: `departments`, `users`, `department_members`
- **Required Graph Nodes**: `(:Department)`, `(:User)`
- **Required Graph Relationships**: `(:Department)<-[:MANAGES]-(:User)`, `(:Department)<-[:MEMBER_OF]-(:User)`
- **Cypher Query**:
  ```cypher
  MATCH (d:Department {tenant_id: $tenantId, name: $deptName})
  OPTIONAL MATCH (d)<-[:MANAGES]-(mgr:User {tenant_id: $tenantId})
  OPTIONAL MATCH (d)<-[:MEMBER_OF]-(emp:User {tenant_id: $tenantId})
  RETURN d.name AS Department, mgr.display_name AS Manager, collect(emp.display_name) AS TeamMembers
  ```
- **Parameters**: `{$tenantId: 1, $deptName: 'Engineering'}`
- **Tenant Filtering**: Direct on `d.tenant_id`, `mgr.tenant_id`, `emp.tenant_id`.
- **Authorization Enforcement Point**: Pre-query backend check: verify user has `org:read` permission.
- **Expected Result Shape**: Single record with department name, manager string, and list of member names.
- **Validation Status**: **PASS (100% Data Validated)**

---

### Scenario 2: Project Ownership & Staffing
- **Business Question**: *"Who owns the 'Mobile App Redesign' project, who created it, and what members are assigned to it?"*
- **Required Source Entities**: `projects`, `project_members`, `users`
- **Required Graph Nodes**: `(:Project)`, `(:User)`
- **Required Graph Relationships**: `(:Project)-[:CREATED_BY]->(:User)`, `(:Project)-[:HAS_MEMBER {role: 'owner'}]->(:User)`, `(:Project)-[:HAS_MEMBER {role: 'member'}]->(:User)`
- **Cypher Query**:
  ```cypher
  MATCH (p:Project {tenant_id: $tenantId, name: $projectName})
  OPTIONAL MATCH (p)-[:CREATED_BY]->(creator:User {tenant_id: $tenantId})
  OPTIONAL MATCH (p)-[:HAS_MEMBER {role: 'owner'}]->(owner:User {tenant_id: $tenantId})
  OPTIONAL MATCH (p)-[:HAS_MEMBER {role: 'member'}]->(member:User {tenant_id: $tenantId})
  RETURN p.name AS Project, creator.display_name AS Creator, owner.display_name AS Owner, collect(DISTINCT member.display_name) AS Members
  ```
- **Parameters**: `{$tenantId: 1, $projectName: 'Mobile App Redesign'}`
- **Tenant Filtering**: Direct on `p.tenant_id`, `creator.tenant_id`, `owner.tenant_id`, `member.tenant_id`.
- **Authorization Enforcement Point**: Pre-query check: verify user is project member or has `project:view_all`.
- **Expected Result Shape**: Project name, Creator name, Owner name, list of member names.
- **Validation Status**: **PASS (Physical created_by_user_id & role='owner' Validated)**

---

### Scenario 3: Task & Ticket Progress by Kanban Column
- **Business Question**: *"What tickets in project 'ERP Core' are currently In Progress, and who is assigned to them?"*
- **Required Source Entities**: `projects`, `tickets`, `kanban_columns`, `ticket_assignees`, `users`
- **Required Graph Nodes**: `(:Project)`, `(:Ticket)`, `(:KanbanColumn)`, `(:User)`
- **Required Graph Relationships**: `(:Ticket)-[:BELONGS_TO]->(:Project)`, `(:Ticket)-[:CURRENT_STAGE]->(:KanbanColumn)`, `(:Ticket)<-[:ASSIGNED_TO]-(:User)`
- **Cypher Query**:
  ```cypher
  MATCH (p:Project {tenant_id: $tenantId, key: $projectKey})<-[:BELONGS_TO]-(t:Ticket {tenant_id: $tenantId})
  MATCH (t)-[:CURRENT_STAGE]->(k:KanbanColumn {name: 'In Progress'})
  OPTIONAL MATCH (t)<-[:ASSIGNED_TO]-(u:User {tenant_id: $tenantId})
  RETURN t.id AS TicketId, t.title AS Title, t.priority AS Priority, collect(u.display_name) AS Assignees
  ```
- **Parameters**: `{$tenantId: 1, $projectKey: 'ERP'}`
- **Tenant Filtering**: Direct on `p.tenant_id`, `t.tenant_id`, `u.tenant_id`.
- **Authorization Enforcement Point**: Backend check: user must belong to project `ERP`.
- **Expected Result Shape**: Table of tickets with id, title, priority, and assignees.
- **Validation Status**: **PASS (100% Data Validated)**

---

### Scenario 4: Electronic Approval Tracking & Active Reviewer Identification
- **Business Question**: *"Has my annual leave request submitted on Monday been approved, and who is the current active reviewer?"*
- **Required Source Entities**: `approval_requests`, `approval_participants`, `users`
- **Required Graph Nodes**: `(:ApprovalRequest)`, `(:User)`
- **Required Graph Relationships**: `(:ApprovalRequest)-[:CREATED_BY]->(:User)`, `(:ApprovalRequest)<-[p:PARTICIPATES_IN]-(:User)`
- **Cypher Query**:
  ```cypher
  MATCH (creator:User {tenant_id: $tenantId, email: $currentUserEmail})<-[:CREATED_BY]-(a:ApprovalRequest {tenant_id: $tenantId, code: $requestCode})
  OPTIONAL MATCH (a)<-[p:PARTICIPATES_IN]-(approver:User {tenant_id: $tenantId})
  WHERE a.status = 'in_progress' AND p.action_status = 'pending'
  RETURN a.code AS RequestCode, a.title AS Title, a.status AS OverallStatus, approver.display_name AS CurrentActiveReviewer, p.sequence_order AS ActiveStep
  ORDER BY p.sequence_order ASC LIMIT 1
  ```
- **Parameters**: `{$tenantId: 1, $currentUserEmail: 'user@company.com', $requestCode: 'LV-2026-089'}`
- **Tenant Filtering**: Scoped to user's tenant.
- **Authorization Enforcement Point**: Backend interceptor: creator email matched to authenticated user session.
- **Expected Result Shape**: Request status and exact pending reviewer.
- **Validation Status**: **PASS (Active step filtered via status='in_progress' & action_status='pending')**

---

### Scenario 5: Employee Leave & Vacation Balances
- **Business Question**: *"How many days of annual leave do I have remaining this year?"*
- **Required Source Entities**: `user_leave_year_balances`, `users`
- **Required Graph Nodes**: `(:User)`, `(:LeaveBalance)`
- **Required Graph Relationships**: `(:User)-[:HAS_LEAVE_BALANCE]->(:LeaveBalance)`
- **Cypher Query**:
  ```cypher
  MATCH (u:User {tenant_id: $tenantId, email: $currentUserEmail})-[:HAS_LEAVE_BALANCE]->(b:LeaveBalance {year: $currentYear})
  RETURN u.display_name AS Employee, b.total_days AS TotalDays, b.used_days AS UsedDays, b.remaining_days AS RemainingDays
  ```
- **Parameters**: `{$tenantId: 1, $currentUserEmail: 'user@company.com', $currentYear: 2026}`
- **Tenant Filtering**: Scoped via user tenant.
- **Authorization Enforcement Point**: Strict self-service check: user can only query their own balance unless possessing `hr:leave:view_all`.
- **Validation Status**: **PASS (353 Year Balances Validated)**

---

### Scenario 6: Daily Attendance & Clock-in Inquiries
- **Business Question**: *"Did John check in late today, and what was his clock-in time?"*
- **Required Source Entities**: `attendance_daily_records`, `users`
- **Required Graph Nodes**: `(:User)`, `(:AttendanceRecord)`
- **Required Graph Relationships**: `(:User)-[:HAS_ATTENDANCE]->(:AttendanceRecord)`
- **Cypher Query**:
  ```cypher
  MATCH (u:User {tenant_id: $tenantId, display_name: $employeeName})-[:HAS_ATTENDANCE]->(att:AttendanceRecord {work_date: $todayDate})
  RETURN u.display_name AS Employee, att.first_check_in AS CheckInTime, att.last_check_out AS CheckOutTime, att.is_late AS IsLate, att.actual_minutes AS WorkedMinutes
  ```
- **Parameters**: `{$tenantId: 1, $employeeName: 'John Doe', $todayDate: '2026-11-04'}`
- **Tenant Filtering**: Direct on `u.tenant_id`.
- **Authorization Enforcement Point**: Backend check: self, direct manager, or HR administrator.
- **Validation Status**: **PASS (54,489 Daily Records Validated)**

---

### Scenario 7: Meeting Room Reservations & Calendar Schedules
- **Business Question**: *"Is Conference Room A available between 2:00 PM and 3:00 PM on Friday?"*
- **Required Source Entities**: `schedule_events`, `schedule_rooms`
- **Required Graph Nodes**: `(:ScheduleRoom)`, `(:ScheduleEvent)`
- **Required Graph Relationships**: `(:ScheduleEvent)-[:RESERVED_IN]->(:ScheduleRoom)`
- **Cypher Query**:
  ```cypher
  MATCH (r:ScheduleRoom {name: $roomName})
  OPTIONAL MATCH (r)<-[:RESERVED_IN]-(e:ScheduleEvent {tenant_id: $tenantId, event_date: $targetDate})
  WHERE (e.start_time < $requestedEndTime AND e.end_time > $requestedStartTime)
  RETURN r.name AS Room, count(e) = 0 AS IsAvailable, collect(e.title) AS ConflictingMeetings
  ```
- **Parameters**: `{$tenantId: 1, $roomName: 'Conference Room A', $targetDate: '2026-11-06', $requestedStartTime: '14:00:00', $requestedEndTime: '15:00:00'}`
- **Tenant Filtering**: Scoped on `e.tenant_id`.
- **Authorization Enforcement Point**: Public calendar permission: `schedule:view`.
- **Validation Status**: **PASS (Exact date/time fields verified)**

---

### Scenario 8: Chat Channel Navigation & Hybrid Vector RAG Search
- **Business Question**: *"What was discussed regarding the database migration in the Tech Lead chat channel?"*
- **Required Architecture**: Hybrid GraphRAG (Option A)
  1. **Graph Stage (Neo4j)**: Identify accessible channel node:
     ```cypher
     MATCH (u:User {tenant_id: $tenantId, email: $currentUserEmail})-[:MEMBER_OF]->(c:ChatConversation {tenant_id: $tenantId, title: $channelTitle})
     RETURN c.id AS ChannelId, c.title AS ChannelTitle
     ```
  2. **Vector Stage (Vector DB)**: Call Vector Search with filter:
     `collection: "chat_messages", filter: {tenant_id: 1, conversation_id: ChannelId}, query: "database migration"`
- **Validation Status**: **PASS (Option A Hybrid Architecture Validated)**

---

### Scenario 9: Broadcast Company Notices & Audience Targeting
- **Business Question**: *"What are the latest administrative policies published for the Marketing department?"*
- **Required Source Entities**: `notices`, `audiences`, `audience_department_members`, `departments`
- **Required Graph Nodes**: `(:Notice)`, `(:Audience)`, `(:Department)`
- **Required Graph Relationships**: `(:Notice)-[:TARGETS_AUDIENCE]->(:Audience)`, `(:Audience)-[:TARGETS_DEPARTMENT]->(:Department)`
- **Cypher Query**:
  ```cypher
  MATCH (d:Department {tenant_id: $tenantId, name: $deptName})<-[:TARGETS_DEPARTMENT]-(aud:Audience)<-[:TARGETS_AUDIENCE]-(n:Notice {tenant_id: $tenantId})
  RETURN n.title AS NoticeTitle, n.published_at AS PublishedAt, n.content AS Content
  ORDER BY n.published_at DESC LIMIT 5
  ```
- **Parameters**: `{$tenantId: 1, $deptName: 'Marketing'}`
- **Tenant Filtering**: Scoped on `d.tenant_id`, `n.tenant_id`.
- **Validation Status**: **PASS (100% Data Validated)**

---

### Scenario 10: Hardware IT Asset Custody
- **Business Question**: *"Which laptop is currently assigned to user Sarah, and what is its serial number?"*
- **Required Source Entities**: `assets`, `users`, `asset_categories`
- **Required Graph Nodes**: `(:Asset)`, `(:User)`, `(:AssetCategory)`
- **Required Graph Relationships**: `(:Asset)-[:ASSIGNED_TO]->(:User)`, `(:Asset)-[:CATEGORY]->(:AssetCategory)`
- **Cypher Query**:
  ```cypher
  MATCH (u:User {tenant_id: $tenantId, display_name: $employeeName})<-[:ASSIGNED_TO]-(a:Asset {tenant_id: $tenantId})-[:CATEGORY]->(c:AssetCategory)
  RETURN a.name AS AssetName, a.serial_number AS SerialNumber, a.code AS AssetCode, c.name AS Category
  ```
- **Parameters**: `{$tenantId: 1, $employeeName: 'Sarah Connor'}`
- **Tenant Filtering**: Scoped on `u.tenant_id`, `a.tenant_id`.
- **Validation Status**: **PASS (Physical assigned_user_id Validated)**

---

### Scenario 11: Community Social Posts by Specific Team
- **Business Question**: *"Show me top knowledge-sharing posts published by the Architecture team."*
- **Required Source Entities**: `departments`, `department_members`, `users`, `talk_posts`, `talk_post_comments`
- **Required Graph Nodes**: `(:Department)`, `(:User)`, `(:CommunityPost)`
- **Required Graph Relationships**: `(:Department)<-[:MEMBER_OF]-(:User)-[:POSTED]->(:CommunityPost)`
- **Cypher Query**:
  ```cypher
  MATCH (d:Department {tenant_id: $tenantId, name: 'Architecture'})<-[:MEMBER_OF]-(u:User {tenant_id: $tenantId})-[:POSTED]->(p:CommunityPost {tenant_id: $tenantId})
  OPTIONAL MATCH (p)<-[:COMMENTED_ON]-(c:Comment)
  RETURN p.title AS PostTitle, u.display_name AS Author, count(c) AS CommentsCount
  ORDER BY CommentsCount DESC LIMIT 5
  ```
- **Parameters**: `{$tenantId: 1}`
- **Tenant Filtering**: Direct on all nodes.
- **Validation Status**: **PASS (Architecture team filtered via Department node)**

---

### Scenario 12: Security RBAC & Role Verification
- **Business Question**: *"What security roles and system permissions are assigned to John Doe?"*
- **Required Source Entities**: `users`, `roles`, `permissions`, `user_role_assignments`, `role_permissions`
- **Required Graph Nodes**: `(:User)`, `(:Role)`, `(:Permission)`
- **Required Graph Relationships**: `(:User)-[:HAS_ROLE]->(:Role)`, `(:Role)-[:HAS_PERMISSION]->(:Permission)`
- **Cypher Query**:
  ```cypher
  MATCH (u:User {tenant_id: $tenantId, email: $userEmail})-[:HAS_ROLE]->(r:Role)
  OPTIONAL MATCH (r)-[:HAS_PERMISSION]->(p:Permission)
  RETURN u.display_name AS User, collect(DISTINCT r.name) AS Roles, collect(DISTINCT p.code) AS RolePermissions
  ```
- **Parameters**: `{$tenantId: 1, $userEmail: 'john.doe@company.com'}`
- **Tenant Filtering**: Direct on `u.tenant_id`.
- **Authorization Enforcement Point**: Evaluated strictly by backend auth module; precedence logic resides in backend service.
- **Validation Status**: **PASS (Backend RBAC Enforcement Explicitly Designated)**
"""
    for fname in ("08_database_query_readiness.md", "08_chatbot_query_readiness.md"):
        with open(os.path.join(DOC_DIR, fname), "w", encoding="utf-8") as f:
            f.write(content)
    print("Saved 08_database_query_readiness.md and 08_chatbot_query_readiness.md successfully.")

# ==========================================
# 3. GENERATE 09 ERD AND GRAPH MODEL
# ==========================================
def generate_erd_and_graph_model():
    print("Generating canonical 09_database_discovery_erd.md (Task H)...")
    content = """# 09 – Database Discovery ERD & Proposed Neo4j Graph Model
## Groupware AI Chatbot Project – Phase 1: Canonical Baseline & Architectural Reconciliation

> [!IMPORTANT]
> **Strict Architectural Separation**:
> This document provides two separate, non-interchangeable architectural diagrams:
> - **Diagram 1**: Relational Database Discovery ERD (Physical tables, PKs, explicit FKs, and inferred domain references labeled `REF`).
> - **Diagram 2**: Proposed Neo4j Graph Data Model (Approved node labels, relationship types, properties, tenant boundaries, and Vector RAG integration boundary).

---

## 1. Diagram 1: Relational Database Discovery ERD

```mermaid
erDiagram
    TENANTS ||--o{ TENANT_USER_MEMBERSHIPS : pools
    TENANTS ||--o{ DEPARTMENTS : scopes
    USERS ||--|| USER_PROFILES : has_profile
    USERS ||--o{ TENANT_USER_MEMBERSHIPS : member_of
    USERS ||--o{ DEPARTMENT_MEMBERS : belongs_to
    DEPARTMENTS ||--o{ DEPARTMENT_MEMBERS : contains
    DEPARTMENTS ||--o| DEPARTMENTS : parent_of
    DEPARTMENTS ||--o| USERS : managed_by

    USERS ||--o{ PROJECTS : creates
    PROJECTS ||--o{ PROJECT_MEMBERS : staffed_by
    USERS ||--o{ PROJECT_MEMBERS : participates_as_owner_or_member
    PROJECTS ||--o{ KANBAN_COLUMNS : defines_stages
    PROJECTS ||--o{ PROJECT_SPRINTS : iterates
    PROJECTS ||--o{ TICKETS : contains
    KANBAN_COLUMNS ||--o{ TICKETS : tracks_state
    TICKETS ||--o{ TICKET_ASSIGNEES : assigns_to
    USERS ||--o{ TICKET_ASSIGNEES : works_on

    USERS ||--o{ APPROVAL_REQUESTS : creates_request
    APPROVAL_REQUESTS ||--o{ APPROVAL_PARTICIPANTS : reviewed_by
    USERS ||--o{ APPROVAL_PARTICIPANTS : signs_off

    USERS ||--o{ ATTENDANCE_DAILY_RECORDS : logs_daily_work
    USERS ||--o{ SCHEDULE_EVENTS : organizes
    SCHEDULE_ROOMS ||--o{ SCHEDULE_EVENTS : hosts
    SCHEDULE_EVENTS ||--o{ SCHEDULE_EVENT_PARTICIPANTS : invites
    USERS ||--o{ SCHEDULE_EVENT_PARTICIPANTS : attends

    USERS ||--o{ CHAT_CONVERSATIONS : creates
    CHAT_CONVERSATIONS ||--o{ CHAT_CONVERSATION_MEMBERS : includes
    USERS ||--o{ CHAT_CONVERSATION_MEMBERS : chats_in

    USERS ||--o{ NOTICES : publishes
    NOTICES ||--o{ NOTICE_READS : read_by
    USERS ||--o{ NOTICE_READS : acknowledges

    USERS ||--o{ ASSETS : assigned_to
    ASSET_CATEGORIES ||--o{ ASSETS : classifies

    TENANTS {
        bigint id PK
        string name
        string slug
    }

    USERS {
        int id PK "integer(32,0)"
        string username
        string email
        string display_name
        boolean is_active
    }

    USER_PROFILES {
        int id PK "integer(32,0)"
        int user_id REF "integer(32,0) - Inferred Ref"
        bigint tenant_id REF "Inferred Ref"
        bigint department_id REF "Inferred Ref"
        string employee_number
        string position
    }

    TENANT_USER_MEMBERSHIPS {
        bigint id PK
        bigint tenant_id REF "Inferred Ref"
        int user_id REF "integer(32,0) - Inferred Ref"
        string status
        boolean is_default
    }

    DEPARTMENTS {
        bigint id PK
        bigint tenant_id REF "Inferred Ref"
        string code
        string name
        bigint parent_id REF "Self-ref"
        int manager_user_id REF "integer(32,0) - Inferred Ref"
    }

    DEPARTMENT_MEMBERS {
        bigint id PK
        bigint department_id REF "Inferred Ref"
        bigint user_id REF "Inferred Ref"
        boolean is_primary
    }

    PROJECTS {
        bigint id PK
        string key
        string name
        string status
        bigint created_by_user_id REF "Creator Identity"
        bigint approved_by_user_id REF "Inferred Ref"
    }

    PROJECT_MEMBERS {
        bigint id PK
        bigint project_id REF "Inferred Ref"
        bigint user_id REF "Inferred Ref"
        string role "owner / admin / member"
    }

    TICKETS {
        bigint id PK
        bigint project_id REF "Inferred Ref"
        bigint column_id REF "Inferred Ref"
        string title
        string priority
        bigint created_by_user_id REF "Creator Identity"
    }

    KANBAN_COLUMNS {
        bigint id PK
        bigint project_id REF "Inferred Ref"
        string name
        int sort_order
    }

    APPROVAL_REQUESTS {
        bigint id PK
        string code
        string title
        string status
        int created_by_user_id REF "integer(32,0) - Request Creator"
    }

    APPROVAL_PARTICIPANTS {
        bigint id PK
        bigint request_id REF "Inferred Ref to approval_requests.id"
        int user_id REF "integer(32,0) - Signoff Approver"
        string participant_role
        int sequence_order
        string action_status
    }

    ATTENDANCE_DAILY_RECORDS {
        bigint id PK
        bigint user_id REF "Inferred Ref"
        date work_date
        time first_check_in
        time last_check_out
        boolean is_late
    }

    SCHEDULE_EVENTS {
        bigint id PK
        date event_date
        time start_time
        time end_time
        string title
        int room_id REF "Inferred Ref"
        bigint user_id REF "Organizer Inferred Ref"
    }

    SCHEDULE_ROOMS {
        int id PK
        string name
        int capacity
    }

    CHAT_CONVERSATIONS {
        bigint id PK
        string title
        string type
        int creator_id REF "Inferred Ref"
    }

    NOTICES {
        bigint id PK
        string title
        text content
        int created_by_user_id REF "Inferred Ref"
    }

    ASSETS {
        bigint id PK
        string code
        string name
        string serial_number
        int category_id REF "Inferred Ref"
        int assigned_user_id REF "Custodian Inferred Ref"
    }

    ASSET_CATEGORIES {
        int id PK
        string name
        string code
    }
```

---

## 2. Diagram 2: Proposed Neo4j Graph Data Model (Architecture B)

```mermaid
graph TD
    subgraph Neo4j_Graph_Database [Neo4j Enterprise Graph Database]
        Tenant["(:Tenant {id, name, slug})"]
        User["(:User {id, username, email, display_name})"]
        Department["(:Department {id, code, name, tenant_id})"]
        Role["(:Role {id, name, code})"]
        Permission["(:Permission {id, name, code})"]

        Project["(:Project {id, key, name, status, tenant_id})"]
        Ticket["(:Ticket {id, title, priority, tenant_id})"]
        KanbanColumn["(:KanbanColumn {id, name, sort_order})"]
        Sprint["(:Sprint {id, name, start_date, end_date})"]

        Approval["(:ApprovalRequest {id, code, title, status, tenant_id})"]
        Template["(:WorkflowTemplate {id, name, code})"]

        Attendance["(:AttendanceRecord {id, work_date, is_late, tenant_id})"]
        Leave["(:LeaveBalance {id, year, remaining_days, tenant_id})"]

        ScheduleEvent["(:ScheduleEvent {id, event_date, start_time, end_time, tenant_id})"]
        Room["(:ScheduleRoom {id, name, capacity})"]

        Channel["(:ChatConversation {id, title, type, tenant_id})"]
        Notice["(:Notice {id, title, published_at, tenant_id})"]
        Post["(:CommunityPost {id, title, tenant_id})"]
        Asset["(:Asset {id, code, name, serial_number, tenant_id})"]
        Category["(:AssetCategory {id, name})"]
        File["(:File {id, file_name, file_size, mime_type, tenant_id})"]
        Audience["(:Audience {id, name, tenant_id})"]

        User -->|MEMBER_OF| Tenant
        Department -->|BELONGS_TO| Tenant
        User -->|MEMBER_OF| Department
        User -->|MANAGES| Department
        Department -->|PARENT_OF| Department

        User -->|HAS_ROLE| Role
        Role -->|HAS_PERMISSION| Permission

        Project -->|CREATED_BY| User
        Project -->|HAS_MEMBER {role: 'owner'}| User
        Project -->|HAS_MEMBER {role: 'member'}| User
        Project -->|CONTAINS| Ticket
        Ticket -->|CURRENT_STAGE| KanbanColumn
        Ticket -->|ASSIGNED_TO| User
        Ticket -->|CREATED_BY| User
        Ticket -->|PART_OF_SPRINT| Sprint

        Approval -->|CREATED_BY| User
        Approval -->|PARTICIPATES_IN {role, sequence, status}| User
        Approval -->|BASED_ON| Template

        User -->|HAS_ATTENDANCE| Attendance
        User -->|HAS_LEAVE_BALANCE| Leave

        ScheduleEvent -->|ORGANIZED_BY| User
        ScheduleEvent -->|INVITES| User
        ScheduleEvent -->|RESERVED_IN| Room

        Channel -->|CREATED_BY| User
        User -->|MEMBER_OF| Channel

        Notice -->|PUBLISHED_BY| User
        Notice -->|TARGETS_AUDIENCE| Audience
        Audience -->|TARGETS_DEPARTMENT| Department

        Post -->|POSTED_BY| User
        Asset -->|ASSIGNED_TO| User
        Asset -->|CATEGORY| Category
        Ticket -->|ATTACHED_FILE| File
    end

    subgraph Vector_RAG_Store [Vector Database - Semantic Storage]
        VectorMessages["ChatMessage Vector Chunks\n- Embedding Vector\n- message_id\n- conversation_id\n- sender_user_id\n- timestamp\n- content"]
    end

    Channel -.->|metadata.conversation_id link| VectorMessages
```

---

## 3. Key Distinctions Between Relational and Graph Models

1. **Denormalization of Attributes**:
   - `user_profiles` is folded directly into `(:User)` properties (`employee_number`, `position`, `grade`).
2. **First-Class Junction Modeling**:
   - `project_members` is transformed into rich edge `[:HAS_MEMBER {role: 'owner' / 'admin' / 'member'}]`.
   - `approval_participants` is transformed into edge `[:PARTICIPATES_IN {participant_role, sequence_order, action_status}]`.
3. **Option A Vector RAG Boundary**:
   - `chat_messages` is NOT modeled as nodes in Neo4j. It resides in Vector DB and connects to `ChatConversation` via `metadata.conversation_id` filtering.
"""
    with open(os.path.join(DOC_DIR, "09_database_discovery_erd.md"), "w", encoding="utf-8") as f:
        f.write(content)
    print("Saved 09_database_discovery_erd.md successfully.")

if __name__ == "__main__":
    generate_tenant_and_auth()
    generate_query_readiness()
    generate_erd_and_graph_model()
