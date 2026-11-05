import os

DOC_DIR = r"documentation\phase-1-database-discovery"
os.makedirs(DOC_DIR, exist_ok=True)

# ==========================================
# 1. GENERATE 11_business_entity_master_catalog.md
# ==========================================
def generate_11():
    print("Generating 11_business_entity_master_catalog.md...")
    content = """# 11 – Business Entity Master Catalog
## Groupware AI Chatbot Project – Phase 1: Review & Final Correction

> [!NOTE]
> This document establishes the **authoritative, reconciled Business Entity Master Catalog** for the Groupware project. It resolves all previous catalog inconsistencies, incorporates verified PostgreSQL source data types, distinguishes creator vs. owner roles, and provides formal architectural classification and Graph candidacy for all 23 investigated business entities.

---

## 1. Architectural Entity Classification Framework

Entities are classified into six rigorous architectural categories based on actual database schema and data profiling:

1. **Core Business Entity (CBE)**: Primary, high-value domain entities representing the central nouns of enterprise operations. Modeled as primary nodes in the Business Knowledge Graph.
2. **Supporting / Reference Entity (SRE)**: Master data, lookup taxonomy, or organizational units that give structure and context to Core Entities. Modeled as taxonomy nodes or relationship attributes.
3. **Security & Authorization Entity (SAE)**: Identity, role-based access control (RBAC), and access boundaries. Essential for query-time access control.
4. **Event / Transactional Entity (ETE)**: High-frequency operational occurrences, discrete interactions, or event logs.
5. **Historical / State Balance Entity (HBE)**: Point-in-time snapshots, cumulative counters, and accrual ledgers.
6. **Operational / Infrastructure Entity (OIE)**: Technical plumbing, telemetry, and background job queues. Strictly excluded from the Business Knowledge Graph.

---

## 2. Business Entity Master Catalog (23 Evaluated Entities)

| # | Entity Name | Architectural Classification | Source Tables | Primary Identifier | Verified Data Type | Tenant Scope | Active Count | Graph Candidacy | Graph Recommendation & Rationale |
|---|---|---|---|---|---|---|---|---|---|
| 1 | **Tenant** | Security & Auth | `tenants` | `tenants.id` | bigint | Global (Pooled) | 1 | **Included (Root Context)** | Multi-tenancy root boundary. Current database operates with 1 active pooled tenant (`legacy-default`, id=1). |
| 2 | **User** | Core Business Entity | `users`, `user_profiles`, `user_sessions` | `users.id` | **integer (int4)** | Scoped via Membership | 360 | **Included (Primary Node)** | Central actor node `(:User)` connected to departments, tasks, projects, approvals, and chats. |
| 3 | **Department** | Core Business Entity | `departments`, `department_members` | `departments.id` | bigint | `tenant_id = 1` | 103 | **Included (Primary Node)** | Core organizational hierarchy node `(:Department)` with recursive parent-child tree. |
| 4 | **Role** | Security & Auth | `roles`, `user_role_assignments` | `roles.id` | bigint | `tenant_id = 1` | 42 | **Included (Security Node)** | Security role node `(:Role)` mapping organizational permissions to users. |
| 5 | **Permission** | Security & Auth | `permissions`, `role_permissions`, `user_permissions` | `permissions.id` | bigint | System / Pooled | 247 | **Included (Dedicated Node)** | Dedicated `(:Permission)` node enabling access-aware chatbot filtering in LangGraph agents. |
| 6 | **Project** | Core Business Entity | `projects`, `project_members`, `project_tags` | `projects.id` | bigint | Non-tenant / Implicit | 65 | **Included (Primary Node)** | Workspace and collaboration hub `(:Project)`. Creator is `created_by_user_id`; ownership derived from `project_members`. |
| 7 | **Ticket (Task)** | Core Business Entity | `tickets`, `ticket_assignees`, `ticket_checklists` | `tickets.id` | bigint | Non-tenant / Implicit | 668 | **Included (Primary Node)** | Discrete work item node `(:Ticket)` with priority, deadlines, and multi-user assignments. |
| 8 | **KanbanColumn** | Supporting / Reference | `kanban_columns` | `kanban_columns.id` | bigint | Project-scoped | 268 | **Included (Workflow Node)** | Workflow state node `(:KanbanColumn)`. Defines the true workflow state and lifecycle of tickets. |
| 9 | **Sprint** | Supporting / Reference | `project_sprints` | `project_sprints.id` | bigint | Project-scoped | 40 | **Included (Timebox Node)** | Timeboxed agile iteration node `(:Sprint)` organizing tickets within projects. |
| 10 | **ApprovalRequest** | Core Business Entity | `approval_requests`, `approval_participants`, `approval_activity_logs` | `approval_requests.id` | bigint | Non-tenant / Implicit | 4,709 | **Included (Primary Node)** | Electronic workflow document `(:ApprovalRequest)` for leave, overtime, and business expenses. |
| 11 | **WorkflowTemplate** | Supporting / Reference | `approval_workflow_templates`, `approval_workflow_steps` | `approval_workflow_templates.id` | bigint | Non-tenant / Implicit | 9 | **Included (Template Node)** | Signoff route configuration node `(:WorkflowTemplate)` defining multi-step approval stages. |
| 12 | **AttendanceRecord** | Event / Transactional | `attendance_daily_records` | `attendance_daily_records.id` | bigint | Non-tenant / Implicit | 54,489 | **Included (Daily Fact Node)** | Daily employee attendance summary `(:AttendanceRecord)`. Excludes raw biometric swipe streams. |
| 13 | **LeaveBalance** | Historical / State Balance | `user_leave_monthly_balances`, `user_leave_year_balances` | `user_leave_year_balances.id` | bigint | Non-tenant / Implicit | 353 (Yearly) | **Included (Balance Node)** | Annual leave ledger node `(:LeaveBalance)` tracking remaining, used, and accrued paid vacation. |
| 14 | **ScheduleEvent** | Core Business Entity | `schedule_events`, `schedule_event_participants` | `schedule_events.id` | bigint | Non-tenant / Implicit | 349 | **Included (Calendar Node)** | Appointment and meeting node `(:ScheduleEvent)` with `event_date`, `start_time`, `end_time`, organizer, and attendees. |
| 15 | **ScheduleRoom** | Supporting / Reference | `schedule_rooms` | `schedule_rooms.id` | bigint | Non-tenant / Implicit | 13 | **Included (Resource Node)** | Physical conference and meeting room node `(:ScheduleRoom)` with seating capacities. |
| 16 | **ChatConversation** | Core Business Entity | `chat_conversations`, `chat_conversation_members` | `chat_conversations.id` | bigint | Non-tenant / Implicit | 329 | **Included (Channel Node)** | Direct and group communication channel node `(:ChatConversation)`. |
| 17 | **ChatMessage** | Event / Transactional | `chat_messages`, `chat_message_attachments`, `chat_message_mentions` | `chat_messages.id` | bigint | Non-tenant / Implicit | 6,108 | **VECTOR RAG ONLY** | Message stream. Indexed in Vector Store for semantic RAG search; exclude raw text nodes from Graph. |
| 18 | **Notice** | Core Business Entity | `notices`, `notice_attachments`, `notice_reads` | `notices.id` | bigint | Non-tenant / Implicit | 99 | **Included (Broadcast Node)** | Company-wide announcements and administrative bulletin node `(:Notice)`. |
| 19 | **Notification** | Operational / Event | `notifications`, `notification_recipients` | `notifications.id` | bigint | Non-tenant / Implicit | 3,735 | **Excluded from Core Graph** | Ephemeral system push alerts. High turnover, low analytical relationship value for chatbot. |
| 20 | **CommunityPost** | Core Business Entity | `talk_posts`, `talk_post_comments`, `talk_post_tags` | `talk_posts.id` | bigint | Non-tenant / Implicit | 247 | **Included (Social Node)** | Internal social feed and knowledge-sharing post node `(:CommunityPost)`. |
| 21 | **File** | Supporting / Reference | `files` | `files.id` | bigint | Non-tenant / Implicit | 3,255 | **METADATA-ONLY Node** | Attachment metadata node `(:File)` linking documents to tickets, notices, and approvals (excludes binary payload). |
| 22 | **Asset** | Core Business Entity | `assets`, `asset_assignments`, `asset_categories` | `assets.id` | bigint | Non-tenant / Implicit | 685 | **Included (Resource Node)** | IT hardware and company equipment node `(:Asset)` tracking user assignments. |
| 23 | **Audience** | Supporting / Reference | `audiences`, `audience_department_members`, `audience_user_members` | `audiences.id` | bigint | Non-tenant / Implicit | 116 | **Included (Targeting Node)** | Target distribution group node `(:Audience)` controlling notice and policy visibility. |

---

## 3. Verified User ID Data Types & Foreign Key Diversity

> [!IMPORTANT]
> **Canonical Schema Fact**: Direct database inspection confirms that `users.id`, `user_profiles.id`, and `user_profiles.user_id` are of type **`integer(32,0)`** (`int4`), NOT `bigint`.
> 
> However, foreign key columns referencing `users.id` vary across physical tables: certain tables utilize `integer`, while others utilize `bigint`. The canonical data types must be respected individually during ETL:

| Table Name | Column Name | Verified PostgreSQL Data Type | Canonical UDT Name | Nullable | Cardinality to `users.id` | Semantic Meaning |
|---|---|---|---|---|---|---|
| `users` | `id` | **integer** | `int4` | NO (PK) | 1:1 (Self) | Primary employee identifier |
| `user_profiles` | `id` | **integer** | `int4` | NO (PK) | 1:1 | Profile record identifier |
| `user_profiles` | `user_id` | **integer** | `int4` | NO | 1:1 | Foreign reference to `users.id` |
| `tenant_user_memberships` | `user_id` | **integer** | `int4` | NO | Many:1 | Tenant pool membership |
| `department_members` | `user_id` | **bigint** | `int8` | NO | Many:1 | Department organizational membership |
| `departments` | `manager_user_id` | **bigint** | `int8` | YES | Many:1 | Department head / supervisor |
| `projects` | `created_by_user_id` | **bigint** | `int8` | YES | Many:1 | Project Creator |
| `projects` | `deleted_by_id` | **bigint** | `int8` | YES | Many:1 | User who soft-deleted project |
| `projects` | `approved_by_user_id` | **bigint** | `int8` | YES | Many:1 | Executive approver of project |
| `project_members` | `user_id` | **bigint** | `int8` | NO | Many:1 | Project member / owner / admin |
| `tickets` | `created_by_user_id` | **bigint** | `int8` | YES | Many:1 | Ticket Creator / Reporter |
| `tickets` | `deleted_by_id` | **bigint** | `int8` | YES | Many:1 | User who deleted ticket |
| `ticket_assignees` | `user_id` | **bigint** | `int8` | NO | Many:1 | Assigned worker / developer |
| `ticket_assignees` | `assigned_by_user_id` | **bigint** | `int8` | YES | Many:1 | Lead who assigned ticket |
| `approval_requests` | `requester_id` | **bigint** | `int8` | NO | Many:1 | Submitter of approval document |
| `approval_participants` | `user_id` | **bigint** | `int8` | NO | Many:1 | Signoff approver or reviewer |
| `attendance_daily_records` | `user_id` | **bigint** | `int8` | NO | Many:1 | Employee daily attendance record |
| `schedule_events` | `user_id` | **bigint** | `int8` | NO | Many:1 | Event organizer |
| `schedule_event_participants` | `user_id` | **bigint** | `int8` | NO | Many:1 | Invited attendee |
| `chat_messages` | `sender_user_id` | **bigint** | `int8` | NO | Many:1 | Message author |
| `notices` | `author_id` | **bigint** | `int8` | NO | Many:1 | Bulletin author |
| `assets` | `current_holder_id` | **bigint** | `int8` | YES | Many:1 | Current equipment custodian |
| `asset_assignments` | `user_id` | **bigint** | `int8` | NO | Many:1 | Historical equipment recipient |

---

## 4. Discovered Role Disambiguation: Creator, Owner, Member, and Approver

A critical finding from Phase 1 database discovery is the semantic separation of enterprise roles:

1. **Project Creator**:
   - Source: `projects.created_by_user_id` (`bigint`).
   - Represents the specific user account that initialized the project record.
2. **Project Owner**:
   - Source: `project_members.role = 'owner'` (`role` varchar, `user_id` bigint).
   - Represents executive responsibility and business ownership of the project. There are 72 project owner assignments across 65 projects (some projects have co-owners).
3. **Project Member**:
   - Source: `project_members.role = 'member'` (246 records) or `'admin'` (38 records).
   - Represents operational staffing allocations.
4. **Approval Reviewer / Approver**:
   - Source: `approval_participants.user_id` (`bigint`) with `status` (`approved`, `rejected`, `pending`).
   - Represents designated workflow signoff authority.

---

## 5. Master Entity Model Diagram

```mermaid
classDiagram
    class User {
        +integer id
        +string username
        +string email
        +string display_name
        +string employee_number
        +string position
        +string grade
        +boolean is_active
        +boolean is_resigned
    }
    class Department {
        +bigint id
        +string code
        +string name
        +integer depth
        +string path
        +bigint manager_user_id
    }
    class Project {
        +bigint id
        +string key
        +string name
        +string status
        +bigint created_by_user_id
        +bigint approved_by_user_id
    }
    class Ticket {
        +bigint id
        +bigint project_id
        +bigint column_id
        +string title
        +string priority
        +bigint created_by_user_id
    }
    class ApprovalRequest {
        +bigint id
        +string code
        +string title
        +string status
        +bigint requester_id
    }
    class ScheduleEvent {
        +bigint id
        +date event_date
        +time start_time
        +time end_time
        +string title
        +bigint room_id
        +bigint user_id
    }

    User "1" <-- "many" Department : managed_by
    Department "1" <-- "many" User : member_of
    Project "1" <-- "many" Ticket : contains
    User "1" <-- "many" Project : created_by
    User "many" <..> "many" Project : project_members (owner/admin/member)
    User "1" <-- "many" Ticket : created_by
    User "many" <..> "many" Ticket : ticket_assignees
    User "1" <-- "many" ApprovalRequest : requested_by
    User "many" <..> "many" ApprovalRequest : approval_participants
    User "1" <-- "many" ScheduleEvent : organized_by
```
"""
    with open(os.path.join(DOC_DIR, "11_business_entity_master_catalog.md"), "w", encoding="utf-8") as f:
        f.write(content)
    print("Saved 11_business_entity_master_catalog.md successfully.")

# ==========================================
# 2. GENERATE 13_tenant_and_authorization_discovery.md
# ==========================================
def generate_13():
    print("Generating 13_tenant_and_authorization_discovery.md...")
    content = """# 13 – Multi-Tenant Architecture & Authorization Discovery
## Groupware AI Chatbot Project – Phase 1: Review & Final Correction

> [!NOTE]
> This document details the multi-tenant architecture, tenant-membership mapping, indirect tenant scoping for business tables, and RBAC authorization structures discovered in the PostgreSQL database.

---

## 1. Multi-Tenant Architecture & Membership Analysis

### A. The Tenant Root Boundary
- Physical Table: `tenants` (schema `public`).
- Total Records: **1 active record**.
  - `id`: `1`
  - `name`: `Default Tenant`
  - `slug`: `legacy-default`
  - `status`: `active`
- **Architectural Pattern**: The current system operates in a **Single-Tenant Pooled Architecture** under Tenant 1 (`legacy-default`). The data model is multi-tenant capable, but populated with a single production tenant.

### B. Full Schema & Records of `tenant_user_memberships`
Inspection of `tenant_user_memberships` reveals:
- Columns:
  - `id`: `bigint` (Primary Key)
  - `tenant_id`: `bigint`
  - `user_id`: `integer`
  - `status`: `character varying(50)`
  - `is_default`: `boolean`
  - `joined_at`: `timestamp with time zone`
  - `created_by_id`, `updated_by_id`, `is_deleted`, `deleted_at`, `deleted_by_id`, `created_at`, `updated_at`
- Constraint Check: The only table constraint is the primary key `tenant_user_memberships_pkey` on `id`. There is **no composite unique constraint** on `(tenant_id, user_id)`.
- Record Population: Exactly **360 records**.
  - Exactly matches the 360 rows in `users`.
  - All 360 records have `tenant_id = 1`, `status = 'active'`, and `is_default = true`.
- **Multi-Tenant Capability Assessment**:
  - *Can a user belong to multiple tenants?* **Yes, architecturally.** The absence of a unique constraint on `user_id` allows a user to have multiple membership rows across different `tenant_id`s.
  - *Does any user currently belong to multiple tenants?* **No.** In the current data snapshot, each user is mapped 1:1 strictly to Tenant 1.

### C. Tenant Scoping of `user_profiles`
- The `user_profiles` table contains a direct `tenant_id` column.
- All 360 profile records have `tenant_id = 1`.
- `user_profiles` is strictly tenant-specific.

---

## 2. Inferred Tenant Scoping for Non-Tenant Tables

A significant architectural characteristic of the database is that core business tables **do not contain a direct `tenant_id` column**:

| Core Business Table | Has Direct `tenant_id`? | Inferred Tenant Association Path | Transitive Reliability |
|---|---|---|---|
| `departments` | **YES** (`tenant_id = 1`) | Direct column in table | 100% DB-enforced |
| `projects` | **NO** | `projects.created_by_user_id -> users.id -> tenant_user_memberships.tenant_id` | Transitive via Creator |
| `project_members` | **NO** | `project_members.user_id -> users.id -> tenant_user_memberships.tenant_id` | Transitive via Member |
| `tickets` | **NO** | `tickets.project_id -> projects -> creator -> tenant_id` | Transitive via Project |
| `approval_requests` | **NO** | `approval_requests.requester_id -> users.id -> tenant_id` | Transitive via Requester |
| `attendance_daily_records` | **NO** | `attendance_daily_records.user_id -> users.id -> tenant_id` | Transitive via Employee |
| `chat_conversations` | **NO** | `chat_conversations.creator_id -> users.id -> tenant_id` | Transitive via Creator |
| `chat_messages` | **NO** | `chat_messages.sender_user_id -> users.id -> tenant_id` | Transitive via Sender |
| `notices` | **NO** | `notices.author_id -> users.id -> tenant_id` | Transitive via Author |
| `schedule_events` | **NO** | `schedule_events.user_id -> users.id -> tenant_id` | Transitive via Organizer |
| `assets` | **NO** | `assets.current_holder_id -> users.id -> tenant_id` | Transitive via Custodian |

### Architectural Implication: Business Rule Dependency
Because tenant isolation for these core tables is not enforced by foreign keys or database triggers, **tenant boundaries rely strictly on application-level business logic**. If a user belongs to Tenant 1, all projects, tickets, and approvals created by that user are assumed to belong to Tenant 1.

---

## 3. Recommended Phase 2 Multi-Tenant Isolation Strategy

To ensure absolute multi-tenant security in the AI Chatbot and Knowledge Graph:

1. **ETL Node Stamping**: During Phase 2 graph ingestion, the ETL pipeline must explicitly inject a `tenant_id: 1` property on **every node** (`:User`, `:Project`, `:Ticket`, `:Department`, `:ApprovalRequest`, `:ScheduleEvent`), resolving transitive ownership at ingest time.
2. **Graph Schema Indexing**: Create a composite index or range index on `(:Label {tenant_id})` across all primary node labels.
3. **Query Boundary Enforcement**: Every Cypher query executed by LangGraph chatbot agents must inject a tenant filter parameter:
   ```cypher
   MATCH (u:User {tenant_id: $tenantId})-[:MEMBER_OF]->(d:Department {tenant_id: $tenantId})
   WHERE u.email = $userEmail
   RETURN u, d
   ```

---

## 4. RBAC Authorization & Permission Precedence Discovery

### A. Authorization Data Assets
- `roles`: 42 defined roles (e.g., `SuperAdmin`, `HRManager`, `ProjectManager`, `Employee`).
- `permissions`: 247 discrete operational permissions (e.g., `ticket:read`, `approval:create`, `salary:view`).
- `role_permissions`: 1,535 active role-to-permission mappings.
- `user_role_assignments`: 448 active user-to-role assignments.
- `user_permissions`: **51 records** representing direct per-user overrides:
  - `is_granted = true`: **19 records** (Direct Allow override).
  - `is_granted = false`: **32 records** (Direct Deny override).

### B. Precedence Evaluation: Unverified Business Rule

> [!WARNING]
> **Definitive Architectural Status**:
> The hypothetical rule **`Direct Deny > Direct Grant > Role Grant`** is a standard enterprise RBAC pattern and is supported by the presence of `is_granted = false` in `user_permissions`.
> 
> However, because backend application source code is **NOT present** in the database dump, this precedence rule MUST be explicitly classified as an **UNVERIFIED BUSINESS RULE / HYPOTHESIS**.
> 
> It must NOT be documented as a verified implementation until confirmed by reviewing backend application source code or consulting system engineers in Phase 2.
"""
    with open(os.path.join(DOC_DIR, "13_tenant_and_authorization_discovery.md"), "w", encoding="utf-8") as f:
        f.write(content)
    print("Saved 13_tenant_and_authorization_discovery.md successfully.")

# ==========================================
# 3. GENERATE 08_chatbot_query_readiness.md
# ==========================================
def generate_08():
    print("Generating 08_chatbot_query_readiness.md...")
    content = """# 08 – Chatbot Query Readiness Assessment
## Groupware AI Chatbot Project – Phase 1: Review & Final Correction

> [!NOTE]
> This document evaluates the readiness of the Groupware database to answer typical enterprise chatbot questions, utilizing the exact, verified schema column names, data types, and relationship paths established during Phase 1.

---

## 1. Schema Synchronization Summary

In accordance with Phase 1 evidence validation, all query scenarios reflect canonical schema facts:
1. **User Identifier**: `users.id` is `integer(32,0)`, joined to foreign user references.
2. **Project Creator**: Uses `projects.created_by_user_id` (`bigint`).
3. **Project Owner**: Uses junction table `project_members` where `role = 'owner'` (the column `projects.owner_id` does NOT exist).
4. **Chat Message Sender**: Uses `chat_messages.sender_user_id` (`bigint`), NOT `sender_id`.
5. **Schedule Events**: Uses `schedule_events.event_date` (`date`), `schedule_events.start_time` (`time`), and `schedule_events.end_time` (`time`).

---

## 2. Chatbot Business Query Scenarios & Graph Traversal Alignment

### Scenario 1: Organizational Hierarchy & Department Head
- **Chatbot Prompt**: *"Who is the manager of the Engineering department, and who reports to them?"*
- **Source Tables**: `departments`, `users`, `department_members`
- **Relational Path**: `departments.manager_user_id -> users.id` (Manager); `departments.id <- department_members.department_id` and `department_members.user_id -> users.id` (Members)
- **Graph Cypher Traversal**:
  ```cypher
  MATCH (d:Department {name: 'Engineering'})<-[:MANAGES]-(mgr:User)
  OPTIONAL MATCH (d)<-[:MEMBER_OF]-(emp:User)
  RETURN mgr.display_name AS Manager, collect(emp.display_name) AS TeamMembers
  ```
- **Readiness Status**: **READY (100% Data Match)**

---

### Scenario 2: Project Ownership & Staffing
- **Chatbot Prompt**: *"Who owns the 'Mobile App Redesign' project, who created it, and what members are assigned to it?"*
- **Source Tables**: `projects`, `project_members`, `users`
- **Relational Path**:
  - Creator: `projects.created_by_user_id -> users.id`
  - Owner: `project_members.project_id = projects.id AND project_members.role = 'owner' -> users.id`
  - Members: `project_members.project_id = projects.id AND project_members.role = 'member' -> users.id`
- **Graph Cypher Traversal**:
  ```cypher
  MATCH (p:Project {name: 'Mobile App Redesign'})
  OPTIONAL MATCH (p)-[:CREATED_BY]->(creator:User)
  OPTIONAL MATCH (p)-[:HAS_MEMBER {role: 'owner'}]->(owner:User)
  OPTIONAL MATCH (p)-[:HAS_MEMBER {role: 'member'}]->(member:User)
  RETURN p.name, creator.display_name AS Creator, owner.display_name AS Owner, collect(member.display_name) AS Members
  ```
- **Readiness Status**: **READY (Verified Ownership Model)**

---

### Scenario 3: Task & Ticket Progress by Kanban Column
- **Chatbot Prompt**: *"What tickets in project 'ERP Core' are currently In Progress, and who is assigned to them?"*
- **Source Tables**: `projects`, `tickets`, `kanban_columns`, `ticket_assignees`, `users`
- **Relational Path**: `projects.id <- tickets.project_id`; `tickets.column_id -> kanban_columns.id` (`kanban_columns.name = 'In Progress'`); `tickets.id <- ticket_assignees.ticket_id` -> `users.id`
- **Graph Cypher Traversal**:
  ```cypher
  MATCH (p:Project {key: 'ERP'})<-[:BELONGS_TO]-(t:Ticket)-[:CURRENT_STAGE]->(k:KanbanColumn {name: 'In Progress'})
  OPTIONAL MATCH (t)<-[:ASSIGNED_TO]-(u:User)
  RETURN t.title, t.priority, collect(u.display_name) AS Assignees
  ```
- **Readiness Status**: **READY (100% Data Match)**

---

### Scenario 4: Electronic Approval Tracking
- **Chatbot Prompt**: *"Has my annual leave request submitted on Monday been approved, and who is the current reviewer?"*
- **Source Tables**: `approval_requests`, `approval_participants`, `users`
- **Relational Path**: `approval_requests.requester_id -> users.id`; `approval_requests.id <- approval_participants.approval_request_id` -> `users.id`
- **Graph Cypher Traversal**:
  ```cypher
  MATCH (req:User {email: $currentUserEmail})<-[:REQUESTED_BY]-(a:ApprovalRequest {code: 'LV-2026-089'})
  MATCH (a)-[p:REVIEWED_BY]->(approver:User)
  RETURN a.title, a.status, approver.display_name, p.status AS StepStatus, p.step_order
  ORDER BY p.step_order ASC
  ```
- **Readiness Status**: **READY (100% Data Match)**

---

### Scenario 5: Employee Leave & Vacation Balances
- **Chatbot Prompt**: *"How many days of annual leave do I have remaining this year?"*
- **Source Tables**: `user_leave_year_balances`, `users`
- **Relational Path**: `user_leave_year_balances.user_id -> users.id`
- **Graph Cypher Traversal**:
  ```cypher
  MATCH (u:User {email: $currentUserEmail})-[:HAS_LEAVE_BALANCE]->(b:LeaveBalance {year: 2026})
  RETURN b.total_days, b.used_days, b.remaining_days
  ```
- **Readiness Status**: **READY (353 Verified Records)**

---

### Scenario 6: Daily Attendance & Clock-in Inquiries
- **Chatbot Prompt**: *"Did John check in late today, and what was his clock-in time?"*
- **Source Tables**: `attendance_daily_records`, `users`
- **Relational Path**: `attendance_daily_records.user_id -> users.id`
- **Graph Cypher Traversal**:
  ```cypher
  MATCH (u:User {display_name: 'John Doe'})-[:HAS_ATTENDANCE]->(att:AttendanceRecord {work_date: $todayDate})
  RETURN att.first_check_in, att.last_check_out, att.is_late, att.actual_minutes
  ```
- **Readiness Status**: **READY (54,489 Verified Daily Records)**

---

### Scenario 7: Meeting Room Reservations & Calendar Schedules
- **Chatbot Prompt**: *"Is Conference Room A available between 2:00 PM and 3:00 PM on Friday?"*
- **Source Tables**: `schedule_events`, `schedule_rooms`
- **Relational Path**: `schedule_events.room_id -> schedule_rooms.id`; `schedule_events.event_date`, `schedule_events.start_time`, `schedule_events.end_time`
- **Graph Cypher Traversal**:
  ```cypher
  MATCH (r:ScheduleRoom {name: 'Conference Room A'})
  OPTIONAL MATCH (r)<-[:RESERVED_IN]-(e:ScheduleEvent {event_date: $targetDate})
  WHERE (e.start_time < $requestedEndTime AND e.end_time > $requestedStartTime)
  RETURN r.name, count(e) = 0 AS IsAvailable, collect(e.title) AS ConflictingMeetings
  ```
- **Readiness Status**: **READY (Exact Date/Time Fields Verified)**

---

### Scenario 8: Chat Channel & Conversation Search
- **Chatbot Prompt**: *"What was discussed regarding the database migration in the Tech Lead chat channel?"*
- **Source Architecture**: Hybrid (Knowledge Graph Channel Navigation + Vector RAG Message Content)
- **Relational Path**: `chat_conversations.id <- chat_messages.conversation_id`; `chat_messages.sender_user_id -> users.id`
- **Execution Pattern**:
  1. Graph Agent navigates to channel `(:ChatConversation {title: 'Tech Lead'})`.
  2. Vector RAG Agent performs semantic similarity search across embeddings of `chat_messages.content` tagged with `conversation_id`.
  3. Returns synthesized summary with citations to message timestamp and `sender_user_id`.
- **Readiness Status**: **READY (Hybrid Graph-RAG Architecture Required)**

---

### Scenario 9: Broadcast Company Notices & Audience Targeting
- **Chatbot Prompt**: *"What are the latest administrative policies published for the Marketing department?"*
- **Source Tables**: `notices`, `audiences`, `audience_department_members`, `departments`
- **Relational Path**: `notices.id <- notice_audiences -> audiences.id <- audience_department_members.department_id`
- **Graph Cypher Traversal**:
  ```cypher
  MATCH (d:Department {name: 'Marketing'})<-[:TARGETS_DEPARTMENT]-(aud:Audience)<-[:BROADCAST_TO]-(n:Notice)
  RETURN n.title, n.published_at, n.content
  ORDER BY n.published_at DESC LIMIT 5
  ```
- **Readiness Status**: **READY (100% Data Match)**

---

### Scenario 10: Hardware IT Asset Custody
- **Chatbot Prompt**: *"Which laptop is currently assigned to user Sarah, and what is its serial number?"*
- **Source Tables**: `assets`, `users`, `asset_categories`
- **Relational Path**: `assets.current_holder_id -> users.id`; `assets.category_id -> asset_categories.id`
- **Graph Cypher Traversal**:
  ```cypher
  MATCH (u:User {display_name: 'Sarah Connor'})<-[:ASSIGNED_TO]-(a:Asset)-[:CATEGORY]->(c:AssetCategory)
  RETURN a.name, a.serial_number, a.asset_code, c.name AS Category
  ```
- **Readiness Status**: **READY (685 Verified Asset Records)**

---

### Scenario 11: Community Social Posts & Knowledge Sharing
- **Chatbot Prompt**: *"Show me top knowledge-sharing posts published by the Architecture team."*
- **Source Tables**: `talk_posts`, `users`, `talk_post_comments`
- **Relational Path**: `talk_posts.author_id -> users.id`
- **Graph Cypher Traversal**:
  ```cypher
  MATCH (u:User)-[:POSTED]->(p:CommunityPost)
  OPTIONAL MATCH (p)<-[:COMMENTED_ON]-(c:Comment)
  RETURN p.title, u.display_name, count(c) AS CommentsCount
  ORDER BY CommentsCount DESC LIMIT 5
  ```
- **Readiness Status**: **READY (247 Active Posts)**

---

### Scenario 12: Security RBAC & Permission Verification
- **Chatbot Prompt**: *"Can John Doe approve budget expense requests?"*
- **Source Tables**: `users`, `user_role_assignments`, `role_permissions`, `permissions`, `user_permissions`
- **Evaluation Rule (Hypothesis)**: Direct Deny (`user_permissions.is_granted = false`) > Direct Grant (`is_granted = true`) > Role Grant.
- **Graph Cypher Traversal**:
  ```cypher
  MATCH (u:User {email: $userEmail})
  OPTIONAL MATCH (u)-[up:HAS_DIRECT_PERMISSION]->(p:Permission {code: 'expense:approve'})
  OPTIONAL MATCH (u)-[:HAS_ROLE]->(r:Role)-[:HAS_PERMISSION]->(p)
  RETURN CASE 
    WHEN up.is_granted = false THEN false
    WHEN up.is_granted = true THEN true
    WHEN r IS NOT NULL THEN true
    ELSE false END AS IsAuthorized
  ```
- **Readiness Status**: **READY WITH CONDITIONS (Precedence subject to backend verification)**
"""
    with open(os.path.join(DOC_DIR, "08_chatbot_query_readiness.md"), "w", encoding="utf-8") as f:
        f.write(content)
    print("Saved 08_chatbot_query_readiness.md successfully.")

# ==========================================
# 4. GENERATE 09_database_discovery_erd.md
# ==========================================
def generate_09():
    print("Generating 09_database_discovery_erd.md...")
    content = """# 09 – Database Discovery Entity-Relationship Diagram (ERD)
## Groupware AI Chatbot Project – Phase 1: Review & Final Correction

> [!NOTE]
> This document visualizes the core enterprise schema discovered in PostgreSQL, featuring **verified source data types** (`integer` for user IDs), exact column names (`projects.created_by_user_id`, `chat_messages.sender_user_id`), and relationship cardinalities and confidence levels.

---

## 1. Discovered Core Domain ERD

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

    USERS ||--o{ APPROVAL_REQUESTS : requests
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
    CHAT_CONVERSATIONS ||--o{ CHAT_MESSAGES : stream
    USERS ||--o{ CHAT_MESSAGES : sends

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
        int user_id FK "integer(32,0)"
        bigint tenant_id
        bigint department_id
        string employee_number
        string position
    }

    TENANT_USER_MEMBERSHIPS {
        bigint id PK
        bigint tenant_id
        int user_id FK "integer(32,0)"
        string status
        boolean is_default
    }

    DEPARTMENTS {
        bigint id PK
        bigint tenant_id
        string code
        string name
        bigint parent_id FK
        bigint manager_user_id FK
    }

    DEPARTMENT_MEMBERS {
        bigint id PK
        bigint department_id FK
        bigint user_id FK
        boolean is_primary
    }

    PROJECTS {
        bigint id PK
        string key
        string name
        string status
        bigint created_by_user_id FK "Creator identity"
        bigint approved_by_user_id FK
    }

    PROJECT_MEMBERS {
        bigint id PK
        bigint project_id FK
        bigint user_id FK
        string role "owner / admin / member"
    }

    TICKETS {
        bigint id PK
        bigint project_id FK
        bigint column_id FK
        string title
        string priority
        bigint created_by_user_id FK
    }

    KANBAN_COLUMNS {
        bigint id PK
        bigint project_id FK
        string name
        int sort_order
    }

    APPROVAL_REQUESTS {
        bigint id PK
        string code
        string title
        string status
        bigint requester_id FK
    }

    APPROVAL_PARTICIPANTS {
        bigint id PK
        bigint approval_request_id FK
        bigint user_id FK
        string status
        int step_order
    }

    ATTENDANCE_DAILY_RECORDS {
        bigint id PK
        bigint user_id FK
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
        bigint room_id FK
        bigint user_id FK "Organizer"
    }

    SCHEDULE_ROOMS {
        bigint id PK
        string name
        int capacity
    }

    CHAT_CONVERSATIONS {
        bigint id PK
        string title
        string type
        bigint creator_id FK
    }

    CHAT_MESSAGES {
        bigint id PK
        bigint conversation_id FK
        bigint sender_user_id FK "Exact column name"
        text content
    }

    NOTICES {
        bigint id PK
        string title
        text content
        bigint author_id FK
    }

    ASSETS {
        bigint id PK
        string name
        string serial_number
        bigint category_id FK
        bigint current_holder_id FK
    }

    ASSET_CATEGORIES {
        bigint id PK
        string name
        string code
    }
```

---

## 2. Key Physical Schema Design Patterns

1. **Synthetic User Primary Key**: `users.id` is standard integer (`int4`), while modern transactional domain tables utilize `bigint` for foreign references to support enterprise scale.
2. **Explicit Creator vs Staffing Ownership**:
   - Creator is stamped in `created_by_user_id`.
   - Ownership is decoupled into `project_members.role = 'owner'` to support co-ownership and team role transitions without DDL modifications.
3. **Temporal Partitioning for Calendar**:
   - `schedule_events` decouples `event_date` (`date`) from `start_time` and `end_time` (`time without time zone`), optimizing room reservation conflict detection.
4. **Denormalized Daily Attendance Summary**:
   - `attendance_daily_records` pre-aggregates high-velocity biometric swipes into business-ready daily facts, avoiding costly on-the-fly table scans of millions of sensor events.
"""
    with open(os.path.join(DOC_DIR, "09_database_discovery_erd.md"), "w", encoding="utf-8") as f:
        f.write(content)
    print("Saved 09_database_discovery_erd.md successfully.")

if __name__ == "__main__":
    generate_11()
    generate_13()
    generate_08()
    generate_09()
