# 21 – Phase 1.1 Final Neo4j Graph Data Model Specification
## Groupware AI Chatbot Project – Architecture B Canonical Standard

> [!IMPORTANT]
> **Architectural Standard**:
> This document defines the definitive **Neo4j 5.x Graph Data Model** for **Architecture B** (Hybrid Operational Graph + Semantic Knowledge Graph).
> Every node label, relationship type, property name, and datatype is verified against real PostgreSQL system catalogs and aligned with the Chatbot Query Readiness scenarios.

---

## 1. Operational Graph: Node Reconciliation Matrix

| Node Label | Exact PostgreSQL Table | Primary Key | Mandatory Neo4j Properties & Types | Optional Properties | Tenant Scope | Privacy Tier | Scope Status |
|---|---|---|---|---|---|---|---|
| `:Tenant` | `public.tenants` | `id` (int8) | `id`: Integer, `code`: String, `name`: String, `status`: String | `created_at`: DateTime | Root Tenant | Tier 1 | **MVP Core** |
| `:User` | `public.users` JOIN `public.user_profiles` | `users.id` (int4) | `id`: Integer, `tenant_id`: Integer, `username`: String, `email`: String, `display_name`: String, `is_active`: Boolean | `department_id`: Integer, `employee_number`: String, `position`: String, `grade`: String | Multi-Tenant | Tier 1 (PII Masked) | **MVP Core** |
| `:Department` | `public.departments` | `id` (int4) | `id`: Integer, `tenant_id`: Integer, `code`: String, `name`: String, `is_active`: Boolean | `parent_id`: Integer, `manager_user_id`: Integer, `depth`: Integer | Direct Tenant | Tier 1 | **MVP Core** |
| `:Role` | `public.roles` | `id` (int4) | `id`: Integer, `tenant_id`: Integer, `code`: String, `name`: String, `is_active`: Boolean | `description`: String, `level`: Integer | Direct Tenant | Tier 3 | **MVP Core** |
| `:Permission` | `public.permissions` | `id` (int4) | `id`: Integer, `tenant_id`: Integer, `code`: String, `resource_type`: String | `action_id`: Integer, `description`: String | Direct Tenant | Tier 3 | **MVP Core** |
| `:Project` | `public.projects` | `id` (int8) | `id`: Integer, `tenant_id`: Integer, `key`: String, `name`: String, `status`: String, `created_by_user_id`: Integer | `description`: String, `start_date`: DateTime, `end_date`: DateTime | Transitive Tenant | Tier 1 | **MVP Core** |
| `:Ticket` | `public.tickets` | `id` (int8) | `id`: Integer, `tenant_id`: Integer, `code`: String, `title`: String, `priority`: String, `status`: String, `project_id`: Integer, `created_by_user_id`: Integer | `column_id`: Integer, `sprint_id`: Integer, `due_date`: DateTime, `estimated_hours`: Float | Transitive Tenant | Tier 1 | **MVP Core** |
| `:Sprint` | `public.project_sprints` | `id` (int8) | `id`: Integer, `project_id`: Integer, `name`: String, `status`: String | `start_date`: Date, `end_date`: Date, `goal`: String | Transitive Tenant | Tier 2 | **MVP Core** |
| `:KanbanColumn` | `public.kanban_columns` | `id` (int8) | `id`: Integer, `project_id`: Integer, `title`: String, `position`: Integer | `status_group`: String | Transitive Tenant | Tier 2 | **MVP Core** |
| `:ApprovalRequest` | `public.approval_requests`| `id` (int8) | `id`: Integer, `tenant_id`: Integer, `code`: String, `title`: String, `status`: String, `request_type`: String, `created_by_user_id`: Integer | `submitted_at`: DateTime, `total_days`: Float, `leave_type`: String | Transitive Tenant | Tier 1 | **MVP Core** |
| `:WorkflowTemplate`| `public.approval_workflow_templates`| `id` (int8)| `id`: Integer, `tenant_id`: Integer, `code`: String, `name`: String, `request_type`: String, `is_active`: Boolean | `priority`: Integer | Direct Tenant | Tier 2 | **MVP Core** |
| `:ScheduleEvent` | `public.schedule_events` | `id` (int8) | `id`: Integer, `tenant_id`: Integer, `title`: String, `event_date`: Date, `start_time`: LocalTime, `end_time`: LocalTime, `user_id`: Integer | `room_id`: Integer, `location`: String, `description`: String | Transitive Tenant | Tier 1 | **MVP Core** |
| `:ScheduleRoom` | `public.schedule_rooms` | `id` (int4) | `id`: Integer, `tenant_id`: Integer, `name`: String, `capacity`: Integer, `is_active`: Boolean | `location`: String, `description`: String | Direct Tenant | Tier 2 | **MVP Core** |
| `:Notice` | `public.notices` | `id` (int8) | `id`: Integer, `tenant_id`: Integer, `title`: String, `is_published`: Boolean, `created_by_user_id`: Integer | `published_at`: DateTime, `notice_type`: String, `audience_id`: Integer | Transitive Tenant | Tier 1 | **MVP Core** |
| `:Post` | `public.talk_posts` | `id` (int8) | `id`: Integer, `tenant_id`: Integer, `title`: String, `author_user_id`: Integer, `created_at`: DateTime | `audience_id`: Integer, `category_id`: Integer | Transitive Tenant | Tier 1 | **MVP Core** |
| `:Asset` | `public.assets` | `id` (int8) | `id`: Integer, `tenant_id`: Integer, `code`: String, `name`: String, `status`: String | `assigned_user_id`: Integer, `department_id`: Integer, `category_id`: Integer | Transitive Tenant | Tier 1 | **MVP Core** |
| `:AssetCategory` | `public.asset_categories` | `id` (int4) | `id`: Integer, `tenant_id`: Integer, `code`: String, `name`: String | `description`: String | Direct Tenant | Tier 2 | **MVP Core** |
| `:FileMetadata` | `public.files` | `id` (int8) | `id`: Integer, `tenant_id`: Integer, `original_name`: String, `content_type`: String, `size_bytes`: Integer, `uploaded_by_user_id`: Integer | `file_ext`: String, `uploaded_at`: DateTime | Transitive Tenant | Tier 2 | **MVP Core** |
| `:ChatConversation`| `public.chat_conversations`| `id` (int8)| `id`: Integer, `tenant_id`: Integer, `title`: String, `conversation_type`: String | `created_by_user_id`: Integer, `created_at`: DateTime | Transitive Tenant | Tier 1 | **MVP Core (Option A)**|
| `:Audience` | `public.audiences` | `id` (int4) | `id`: Integer, `tenant_id`: Integer, `name`: String, `audience_type`: String, `is_active`: Boolean | `code`: String, `description`: String | Direct Tenant | Tier 2 | **MVP Core** |
| `:LeaveBalance` | `public.user_leave_monthly_balances`| `id` (int8)| `id`: Integer, `tenant_id`: Integer, `user_id`: Integer, `year`: Integer, `month`: Integer, `remaining_days`: Float | `total_days`: Float, `used_days`: Float | Transitive Tenant | Tier 4 | **MVP Extended** |
| `:AttendanceRecord`| `public.attendance_daily_records` | `id` (int8)| `id`: Integer, `tenant_id`: Integer, `user_id`: Integer, `work_date`: Date, `status`: String | `working_minutes`: Integer, `overtime_minutes`: Integer | Transitive Tenant | Tier 4 | **MVP Extended** |
| `:ContractHistory` | `public.user_contract_histories` | `id` (int4) | `id`: Integer, `tenant_id`: Integer, `user_id`: Integer, `contract_type`: String, `status`: String | `start_date`: Date, `end_date`: Date | Transitive Tenant | Tier 6 (Masked) | **MVP Extended** |

---

## 2. Operational Graph: Relationship Reconciliation Matrix

| Relationship Type | Source Node | Target Node | Direction | Cardinality | Underlying Table & Column Join | Relationship Properties |
|---|---|---|---|---|---|---|
| `[:MEMBER_OF]` | `:User` | `:Tenant` | `(u)->(t)` | N:M | `tenant_user_memberships` (`user_id` -> `tenant_id`) | `joined_at`: DateTime, `is_default`: Boolean |
| `[:BELONGS_TO_TENANT]` | `:Department` | `:Tenant` | `(d)->(t)` | N:1 | `departments.tenant_id` -> `tenants.id` | None |
| `[:MEMBER_OF_DEPARTMENT]` | `:User` | `:Department`| `(u)->(d)` | N:M | `department_members` (`user_id` -> `department_id`) | `is_primary`: Boolean, `joined_at`: DateTime |
| `[:MANAGES]` | `:User` | `:Department`| `(u)->(d)` | 1:1 | `departments.manager_user_id` -> `users.id` | None |
| `[:SUB_DEPARTMENT_OF]` | `:Department` | `:Department`| `(d1)->(d2)`| N:1 | `departments.parent_id` -> `departments.id` | None |
| `[:HAS_ROLE]` | `:User` | `:Role` | `(u)->(r)` | N:M | `user_role_assignments` (`user_id` -> `role_id`) | `assigned_at`: DateTime, `assigned_by`: Integer |
| `[:INCLUDES_PERMISSION]` | `:Role` | `:Permission`| `(r)->(p)` | N:M | `role_permissions` (`role_id` -> `permission_id`) | `is_granted`: Boolean |
| `[:DIRECT_PERMISSION]` | `:User` | `:Permission`| `(u)->(p)` | N:M | `user_permissions` (`user_id` -> `permission_id`) | `is_granted`: Boolean |
| `[:CREATED_BY]` | `:Project` | `:User` | `(p)->(u)` | N:1 | `projects.created_by_user_id` -> `users.id` | None |
| `[:MEMBER_OF_PROJECT]` | `:User` | `:Project` | `(u)->(p)` | N:M | `project_members` (`user_id` -> `project_id`) | `role`: String (e.g. `'owner'`), `joined_at`: DateTime |
| `[:BELONGS_TO_PROJECT]` | `:Ticket` | `:Project` | `(t)->(p)` | N:1 | `tickets.project_id` -> `projects.id` | None |
| `[:CREATED_BY]` | `:Ticket` | `:User` | `(t)->(u)` | N:1 | `tickets.created_by_user_id` -> `users.id` | None |
| `[:ASSIGNED_TO]` | `:Ticket` | `:User` | `(t)->(u)` | N:M | `ticket_assignees` (`ticket_id` -> `user_id`) | `assigned_at`: DateTime |
| `[:PART_OF_SPRINT]` | `:Ticket` | `:Sprint` | `(t)->(s)` | N:1 | `tickets.sprint_id` -> `project_sprints.id` | None |
| `[:IN_STAGE]` | `:Ticket` | `:KanbanColumn`| `(t)->(k)` | N:1 | `tickets.column_id` -> `kanban_columns.id` | None |
| `[:SPRINT_OF_PROJECT]` | `:Sprint` | `:Project` | `(s)->(p)` | N:1 | `project_sprints.project_id` -> `projects.id`| None |
| `[:COLUMN_OF_PROJECT]` | `:KanbanColumn` | `:Project`| `(k)->(p)` | N:1 | `kanban_columns.project_id` -> `projects.id` | None |
| `[:CREATED_BY]` | `:ApprovalRequest` | `:User` | `(a)->(u)` | N:1 | `approval_requests.created_by_user_id` -> `users.id` | None |
| `[:USES_TEMPLATE]` | `:ApprovalRequest` | `:WorkflowTemplate`| `(a)->(w)`| N:1 | `approval_requests.request_type = w.request_type` | None |
| `[:PARTICIPATES_IN]` | `:User` | `:ApprovalRequest`| `(u)->(a)`| N:M | `approval_participants` (`user_id` -> `request_id`) | `participant_role`: String, `sequence_order`: Integer, `action_status`: String |
| `[:ORGANIZED_BY]` | `:ScheduleEvent` | `:User` | `(e)->(u)` | N:1 | `schedule_events.user_id` -> `users.id` | None |
| `[:HELD_IN]` | `:ScheduleEvent` | `:ScheduleRoom`| `(e)->(r)` | N:1 | `schedule_events.room_id` -> `schedule_rooms.id` | None |
| `[:ATTENDS_EVENT]` | `:User` | `:ScheduleEvent`| `(u)->(e)` | N:M | `schedule_event_participants` (`user_id` -> `event_id`) | `status`: String, `is_required`: Boolean |
| `[:PUBLISHED_BY]` | `:Notice` | `:User` | `(n)->(u)` | N:1 | `notices.created_by_user_id` -> `users.id` | None |
| `[:TARGETED_TO]` | `:Notice` | `:Audience` | `(n)->(a)` | N:1 | `notices.audience_id` -> `audiences.id` | None |
| `[:AUTHORED_BY]` | `:Post` | `:User` | `(p)->(u)` | N:1 | `talk_posts.author_user_id` -> `users.id` | None |
| `[:ASSIGNED_TO]` | `:Asset` | `:User` | `(a)->(u)` | N:1 | `assets.assigned_user_id` -> `users.id` | None |
| `[:LOCATED_IN]` | `:Asset` | `:Department` | `(a)->(d)` | N:1 | `assets.department_id` -> `departments.id` | None |
| `[:CATEGORIZED_AS]` | `:Asset` | `:AssetCategory`| `(a)->(c)` | N:1 | `assets.category_id` -> `asset_categories.id` | None |
| `[:UPLOADED_BY]` | `:FileMetadata` | `:User` | `(f)->(u)` | N:1 | `files.uploaded_by_user_id` -> `users.id` | None |
| `[:MEMBER_OF_CONVERSATION]` | `:User` | `:ChatConversation`| `(u)->(c)`| N:M | `chat_conversation_members` (`user_id` -> `conversation_id`) | `role`: String, `joined_at`: DateTime, `is_muted`: Boolean |

---

## 3. Semantic / Knowledge Graph Architecture

In accordance with **Architecture B**, the Semantic Graph links operational entities to enterprise knowledge:

### 3.1 Semantic Node Specifications
| Semantic Label | Business Meaning | Source of Truth | Neo4j Role | Vector Store Role | Scope |
|---|---|---|---|---|---|
| `:Topic` | High-level enterprise subject or knowledge domain | NLP Extraction / Tag Catalog | Organizes projects, notices, documents | Topic embeddings for semantic routing | **MVP Semantic** |
| `:Tag` | Keyword or taxonomy classification | Source Tags (`project_tags`, `ticket_tags`) | Categorical graph navigation | Keyword filtering metadata | **MVP Semantic** |
| `:KnowledgeDocument` | Enterprise policy, manual, or technical spec | `files`, `project_common_documents` | Structural metadata & author links | Document chunk embeddings for Vector RAG | **MVP Semantic** |
| `:BusinessConcept` | Enterprise domain term (e.g. "Annual Leave Policy") | Business Glossary / Ontology | Semantic anchor for chatbot reasoning | Concept semantic definition embeddings | **Future Phase** |

### 3.2 Semantic Relationship Types
- `(:Project)-[:TAGGED_WITH]->(:Tag)`: Connects projects to taxonomy tags.
- `(:Ticket)-[:TAGGED_WITH]->(:Tag)`: Connects tasks to technical tags.
- `(:Notice)-[:COVERS_TOPIC]->(:Topic)`: Connects official notices to high-level topics.
- `(:KnowledgeDocument)-[:REFERENCES_CONCEPT]->(:BusinessConcept)`: Future semantic reasoning link.
- `(:KnowledgeDocument)-[:ASSOCIATED_WITH]->(:Project)`: Links common project documentation.

### 3.3 Boundary Enforcement (Option A for Chat & Unstructured Text)
- Chat messages are **strictly kept out of Neo4j**. No `(:ChatMessage)` or `(:KnowledgeChunk)` nodes exist in the graph.
- All high-dimensional text chunks (chat message text, talk post markdown bodies, file OCR text) reside in the **Vector Database**.
- Retrieval is handled by a two-stage hybrid pipeline:
  1. *Graph Traversal Stage*: Filters candidates by tenant, user permissions, project membership, and department context.
  2. *Vector Similarity Stage*: Queries top-K similar chunks within the graph-filtered entity boundaries.
