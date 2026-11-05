# 14 – Neo4j Graph Data Model Specification
## Groupware AI Chatbot Project – Architecture B Baseline

> [!IMPORTANT]
> **Architectural Alignment**:
> This document specifies the target **Neo4j 5.x Graph Data Model** for **Architecture B** (Hybrid Operational & Semantic Knowledge Graph).
> - **Operational Graph**: Captures organizational hierarchy, user memberships, role-based access control (RBAC), project structures, sprint lifecycles, and approval workflows.
> - **Semantic / Knowledge Graph**: Connects enterprise knowledge artifacts (notices, community posts, meeting notes, project deliverables) to organizational context, topics, and authors.
> - **Vector RAG Separation**: Unstructured textual bodies (chat messages, forum markdown bodies, file attachments) are indexed in a high-dimensional Vector Store. Neo4j models structural topologies, references, and metadata.

---

## 1. Neo4j Node Labels & Property Specifications

All node labels, source tables, primary keys, and required property types are strictly defined:

| Node Label | Source PostgreSQL Table | Business Role | Primary Identifier | Mandatory Properties & Data Types | Optional / Nullable Properties |
|---|---|---|---|---|---|
| `:Tenant` | `public.tenants` | Enterprise Isolation Boundary | `id`: Integer | `id`: Integer, `code`: String, `name`: String, `status`: String | `created_at`: DateTime |
| `:User` | `public.users`, `public.user_profiles` | Core Enterprise Actor | `id`: Integer | `id`: Integer, `tenant_id`: Integer, `username`: String, `email`: String, `full_name`: String, `status`: String, `is_active`: Boolean | `department_id`: Integer, `created_at`: DateTime |
| `:Department` | `public.departments` | Organizational Hierarchy Unit | `id`: Integer | `id`: Integer, `tenant_id`: Integer, `code`: String, `name`: String | `parent_department_id`: Integer, `manager_user_id`: Integer |
| `:Role` | `public.roles` | Access Control Role Definition | `id`: Integer | `id`: Integer, `tenant_id`: Integer, `code`: String, `name`: String | `description`: String |
| `:Permission` | `public.permissions` | Granular Security Capability | `id`: Integer | `id`: Integer, `tenant_id`: Integer, `code`: String, `name`: String | `module`: String, `action`: String |
| `:Project` | `public.projects` | Collaborative Work Initiative | `id`: Integer | `id`: Integer, `tenant_id`: Integer, `code`: String, `name`: String, `status`: String, `created_by_user_id`: Integer | `start_date`: Date, `target_date`: Date, `description`: String |
| `:Ticket` | `public.tickets` | Task / Issue Execution Item | `id`: Integer | `id`: Integer, `tenant_id`: Integer, `ticket_number`: String, `title`: String, `priority`: String, `status`: String, `project_id`: Integer, `created_by_user_id`: Integer | `sprint_id`: Integer, `kanban_column_id`: Integer, `assignee_user_id`: Integer, `due_date`: Date |
| `:Sprint` | `public.sprints` | Agile Project Iteration | `id`: Integer | `id`: Integer, `project_id`: Integer, `name`: String, `status`: String | `start_date`: Date, `end_date`: Date |
| `:KanbanColumn` | `public.kanban_columns` | Workflow Board Stage | `id`: Integer | `id`: Integer, `project_id`: Integer, `name`: String, `column_order`: Integer | None |
| `:ApprovalRequest` | `public.approval_requests` | Formal Enterprise Governance | `id`: Integer | `id`: Integer, `tenant_id`: Integer, `code`: String, `title`: String, `status`: String, `created_by_user_id`: Integer | `template_id`: Integer, `created_at`: DateTime |
| `:WorkflowTemplate`| `public.workflow_templates` | Standard Approval Process | `id`: Integer | `id`: Integer, `tenant_id`: Integer, `code`: String, `name`: String, `is_active`: Boolean | `description`: String |
| `:ScheduleEvent` | `public.schedule_events` | Calendar Appointment / Meeting | `id`: Integer | `id`: Integer, `tenant_id`: Integer, `title`: String, `event_date`: Date, `start_time`: LocalTime, `end_time`: LocalTime, `created_by_user_id`: Integer | `room_id`: Integer, `status`: String |
| `:ScheduleRoom` | `public.schedule_rooms` | Meeting Facility / Room | `id`: Integer | `id`: Integer, `tenant_id`: Integer, `name`: String, `capacity`: Integer | `location`: String |
| `:Notice` | `public.notices` | Official Enterprise Broadcast | `id`: Integer | `id`: Integer, `tenant_id`: Integer, `title`: String, `status`: String, `created_by_user_id`: Integer | `published_at`: DateTime |
| `:CommunityPost` | `public.community_posts` | Informal Forum / Knowledge Sharing | `id`: Integer | `id`: Integer, `tenant_id`: Integer, `title`: String, `author_user_id`: Integer | `category_id`: Integer, `created_at`: DateTime |
| `:Asset` | `public.assets` | Company Equipment / Resource | `id`: Integer | `id`: Integer, `tenant_id`: Integer, `asset_code`: String, `name`: String, `status`: String | `assigned_user_id`: Integer, `department_id`: Integer |
| `:FileMetadata` | `public.files` | Stored Document Registry | `id`: Integer | `id`: Integer, `tenant_id`: Integer, `file_name`: String, `file_size`: Integer, `mime_type`: String, `uploaded_by_user_id`: Integer | `storage_path`: String, `created_at`: DateTime |
| `:ChatConversation`| `public.chat_conversations`| Messaging Channel / Room Topology | `id`: Integer | `id`: Integer, `tenant_id`: Integer, `title`: String, `type`: String, `is_direct`: Boolean | `created_at`: DateTime |
| `:Audience` | `public.audiences` | Targeted Recipient Grouping | `id`: Integer | `id`: Integer, `tenant_id`: Integer, `name`: String, `target_type`: String | `description`: String |

---

## 2. Neo4j Relationship Specifications

Relationships represent validated business references, explicit foreign keys, and semantic links:

| Relationship Type | Source Node | Target Node | Direction | Cardinality | Ingestion Source Table / Query | Relationship Properties |
|---|---|---|---|---|---|---|
| `[:BELONGS_TO]` | `:User` | `:Tenant` | `(u)->(t)` | N:1 | `tenant_user_memberships` | `joined_at`: DateTime |
| `[:BELONGS_TO]` | `:Department` | `:Tenant` | `(d)->(t)` | N:1 | `departments.tenant_id` | None |
| `[:MEMBER_OF]` | `:User` | `:Department` | `(u)->(d)` | N:M | `department_members` | `is_primary`: Boolean, `joined_at`: DateTime |
| `[:MANAGES]` | `:User` | `:Department` | `(u)->(d)` | 1:1 | `departments.manager_user_id` | None |
| `[:SUB_DEPARTMENT_OF]` | `:Department` | `:Department` | `(d1)->(d2)` | N:1 | `departments.parent_department_id` | None |
| `[:HAS_ROLE]` | `:User` | `:Role` | `(u)->(r)` | N:M | `user_roles` | `assigned_at`: DateTime |
| `[:INCLUDES_PERMISSION]`| `:Role` | `:Permission` | `(r)->(p)` | N:M | `role_permissions` | None |
| `[:DIRECT_PERMISSION]` | `:User` | `:Permission` | `(u)->(p)` | N:M | `user_permissions` | `is_granted`: Boolean |
| `[:CREATED_BY]` | `:Project` | `:User` | `(p)->(u)` | N:1 | `projects.created_by_user_id` | None |
| `[:MEMBER_OF_PROJECT]` | `:User` | `:Project` | `(u)->(p)` | N:M | `project_members` | `role`: String (e.g. `'owner'`), `joined_at`: DateTime |
| `[:BELONGS_TO_PROJECT]`| `:Ticket` | `:Project` | `(t)->(p)` | N:1 | `tickets.project_id` | None |
| `[:ASSIGNED_TO]` | `:Ticket` | `:User` | `(t)->(u)` | N:1 | `tickets.assignee_user_id` | None |
| `[:CREATED_BY]` | `:Ticket` | `:User` | `(t)->(u)` | N:1 | `tickets.created_by_user_id` | None |
| `[:PART_OF_SPRINT]` | `:Ticket` | `:Sprint` | `(t)->(s)` | N:1 | `tickets.sprint_id` | None |
| `[:IN_STAGE]` | `:Ticket` | `:KanbanColumn` | `(t)->(k)` | N:1 | `tickets.kanban_column_id` | None |
| `[:BELONGS_TO_PROJECT]`| `:Sprint` | `:Project` | `(s)->(p)` | N:1 | `sprints.project_id` | None |
| `[:BELONGS_TO_PROJECT]`| `:KanbanColumn` | `:Project` | `(k)->(p)` | N:1 | `kanban_columns.project_id` | None |
| `[:CREATED_BY]` | `:ApprovalRequest` | `:User` | `(a)->(u)` | N:1 | `approval_requests.created_by_user_id` | None |
| `[:BASED_ON_TEMPLATE]` | `:ApprovalRequest` | `:WorkflowTemplate` | `(a)->(w)` | N:1 | `approval_requests.template_id` | None |
| `[:PARTICIPATES_IN]` | `:User` | `:ApprovalRequest` | `(u)->(a)` | N:M | `approval_request_participants` | `step_number`: Integer, `role`: String, `action_status`: String |
| `[:ORGANIZED_BY]` | `:ScheduleEvent` | `:User` | `(e)->(u)` | N:1 | `schedule_events.created_by_user_id` | None |
| `[:HELD_IN]` | `:ScheduleEvent` | `:ScheduleRoom` | `(e)->(r)` | N:1 | `schedule_events.room_id` | None |
| `[:ATTENDS_EVENT]` | `:User` | `:ScheduleEvent` | `(u)->(e)` | N:M | `schedule_event_attendees` | `status`: String |
| `[:PUBLISHED_BY]` | `:Notice` | `:User` | `(n)->(u)` | N:1 | `notices.created_by_user_id` | None |
| `[:AUTHORED_BY]` | `:CommunityPost` | `:User` | `(c)->(u)` | N:1 | `community_posts.author_user_id` | None |
| `[:ASSIGNED_TO]` | `:Asset` | `:User` | `(a)->(u)` | N:1 | `assets.assigned_user_id` | None |
| `[:LOCATED_IN]` | `:Asset` | `:Department` | `(a)->(d)` | N:1 | `assets.department_id` | None |
| `[:UPLOADED_BY]` | `:FileMetadata` | `:User` | `(f)->(u)` | N:1 | `files.uploaded_by_user_id` | None |
| `[:MEMBER_OF_CONVERSATION]`| `:User` | `:ChatConversation` | `(u)->(c)` | N:M | `chat_conversation_members` | `joined_at`: DateTime, `is_muted`: Boolean |

---

## 3. Neo4j 5.x Constraints & Indexes Specification

### 3.1 Uniqueness Constraints (Primary Key Enforcement)
```cypher
// 1. Core Organizational & Security Constraints
CREATE CONSTRAINT cst_tenant_id IF NOT EXISTS FOR (t:Tenant) REQUIRE t.id IS UNIQUE;
CREATE CONSTRAINT cst_user_id IF NOT EXISTS FOR (u:User) REQUIRE u.id IS UNIQUE;
CREATE CONSTRAINT cst_department_id IF NOT EXISTS FOR (d:Department) REQUIRE d.id IS UNIQUE;
CREATE CONSTRAINT cst_role_id IF NOT EXISTS FOR (r:Role) REQUIRE r.id IS UNIQUE;
CREATE CONSTRAINT cst_permission_id IF NOT EXISTS FOR (p:Permission) REQUIRE p.id IS UNIQUE;

// 2. Project & Work Management Constraints
CREATE CONSTRAINT cst_project_id IF NOT EXISTS FOR (p:Project) REQUIRE p.id IS UNIQUE;
CREATE CONSTRAINT cst_ticket_id IF NOT EXISTS FOR (t:Ticket) REQUIRE t.id IS UNIQUE;
CREATE CONSTRAINT cst_sprint_id IF NOT EXISTS FOR (s:Sprint) REQUIRE s.id IS UNIQUE;
CREATE CONSTRAINT cst_kanban_id IF NOT EXISTS FOR (k:KanbanColumn) REQUIRE k.id IS UNIQUE;

// 3. Approval & Workflow Constraints
CREATE CONSTRAINT cst_approval_id IF NOT EXISTS FOR (a:ApprovalRequest) REQUIRE a.id IS UNIQUE;
CREATE CONSTRAINT cst_workflow_id IF NOT EXISTS FOR (w:WorkflowTemplate) REQUIRE w.id IS UNIQUE;

// 4. Collaborative Knowledge, Calendar & Resources
CREATE CONSTRAINT cst_event_id IF NOT EXISTS FOR (e:ScheduleEvent) REQUIRE e.id IS UNIQUE;
CREATE CONSTRAINT cst_room_id IF NOT EXISTS FOR (r:ScheduleRoom) REQUIRE r.id IS UNIQUE;
CREATE CONSTRAINT cst_notice_id IF NOT EXISTS FOR (n:Notice) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT cst_post_id IF NOT EXISTS FOR (c:CommunityPost) REQUIRE c.id IS UNIQUE;
CREATE CONSTRAINT cst_asset_id IF NOT EXISTS FOR (a:Asset) REQUIRE a.id IS UNIQUE;
CREATE CONSTRAINT cst_file_id IF NOT EXISTS FOR (f:FileMetadata) REQUIRE f.id IS UNIQUE;
CREATE CONSTRAINT cst_conversation_id IF NOT EXISTS FOR (c:ChatConversation) REQUIRE c.id IS UNIQUE;
CREATE CONSTRAINT cst_audience_id IF NOT EXISTS FOR (a:Audience) REQUIRE a.id IS UNIQUE;
```

### 3.2 Tenant Isolation Range Indexes (Multi-Tenant Performance)
```cypher
CREATE INDEX idx_user_tenant IF NOT EXISTS FOR (u:User) ON (u.tenant_id);
CREATE INDEX idx_department_tenant IF NOT EXISTS FOR (d:Department) ON (d.tenant_id);
CREATE INDEX idx_project_tenant IF NOT EXISTS FOR (p:Project) ON (p.tenant_id);
CREATE INDEX idx_ticket_tenant IF NOT EXISTS FOR (t:Ticket) ON (t.tenant_id);
CREATE INDEX idx_approval_tenant IF NOT EXISTS FOR (a:ApprovalRequest) ON (a.tenant_id);
CREATE INDEX idx_event_tenant IF NOT EXISTS FOR (e:ScheduleEvent) ON (e.tenant_id);
CREATE INDEX idx_notice_tenant IF NOT EXISTS FOR (n:Notice) ON (n.tenant_id);
CREATE INDEX idx_post_tenant IF NOT EXISTS FOR (c:CommunityPost) ON (c.tenant_id);
CREATE INDEX idx_asset_tenant IF NOT EXISTS FOR (a:Asset) ON (a.tenant_id);
CREATE INDEX idx_file_tenant IF NOT EXISTS FOR (f:FileMetadata) ON (f.tenant_id);
CREATE INDEX idx_conversation_tenant IF NOT EXISTS FOR (c:ChatConversation) ON (c.tenant_id);
```

### 3.3 Text & Fulltext Lookup Indexes (Entity Resolution for Chatbot)
```cypher
CREATE INDEX idx_user_email IF NOT EXISTS FOR (u:User) ON (u.email);
CREATE INDEX idx_user_username IF NOT EXISTS FOR (u:User) ON (u.username);
CREATE INDEX idx_ticket_number IF NOT EXISTS FOR (t:Ticket) ON (t.ticket_number);
CREATE INDEX idx_project_code IF NOT EXISTS FOR (p:Project) ON (p.code);
CREATE FULLTEXT INDEX fts_user_name IF NOT EXISTS FOR (u:User) ON EACH [u.full_name, u.username];
CREATE FULLTEXT INDEX fts_project_search IF NOT EXISTS FOR (p:Project) ON EACH [p.name, p.code];
CREATE FULLTEXT INDEX fts_ticket_search IF NOT EXISTS FOR (t:Ticket) ON EACH [t.title, t.ticket_number];
```
