# 15 – Source-to-Graph Mapping Specification
## Groupware AI Chatbot Project – PostgreSQL to Neo4j ETL Contract

> [!NOTE]
> This specification defines the exact mapping contracts, datatype conversion rules, null handling, orphan resolution, and soft-delete filtering required for Phase 2 ETL pipeline implementation.
> **Scope**: Architecture B (Operational & Semantic Knowledge Graph).

---

## 1. Relational-to-Graph Datatype Conversion Standard

PostgreSQL data types must be mapped to native Neo4j 5.x property types according to the standard matrix:

| PostgreSQL Data Type | Canonical Storage Format | Neo4j Property Type | Conversion Rule & Handling |
|---|---|---|---|
| `integer` (`int4`) | 32-bit signed int | `Integer` | Native integer conversion. |
| `bigint` (`int8`) | 64-bit signed int | `Integer` | Neo4j natively supports 64-bit signed integers. |
| `character varying`, `text` | UTF-8 text string | `String` | Trim whitespace; empty strings preserved or converted to null depending on field semantics. |
| `boolean` (`bool`) | `TRUE`, `FALSE` | `Boolean` | Direct mapping to Neo4j boolean. |
| `timestamp with time zone` | ISO-8601 with offset | `DateTime` | Ingest via Neo4j `datetime()` function (`datetime('2026-03-29T10:00:00Z')`). |
| `timestamp without time zone` | Local wall timestamp | `LocalDateTime` | Ingest via `localdatetime()`. |
| `date` | `YYYY-MM-DD` | `Date` | Ingest via Neo4j `date('YYYY-MM-DD')`. |
| `time without time zone` | `HH:MM:SS` | `LocalTime` or `String` | Stored as `time('HH:MM:SS')` or formatted string for simple display. |
| `json`, `jsonb` | JSON string / document | `String` or Unnested Props | Flatten relevant business properties or store as JSON string if raw audit needed. |

---

## 2. Table-to-Node Ingestion Specifications

| Target Neo4j Label | Source Table | Ingestion SQL Filter | Primary Identifier Mapping | Properties Mapped | Soft-Delete Filter Clause |
|---|---|---|---|---|---|
| `:Tenant` | `public.tenants` | `SELECT * FROM tenants` | `id` -> `t.id` | `code`, `name`, `status`, `created_at` | None |
| `:User` | `public.users` JOIN `public.user_profiles` | `SELECT u.id, u.tenant_id, u.username, u.email, u.status, u.is_active, p.full_name, p.department_id, u.created_at FROM users u LEFT JOIN user_profiles p ON u.id = p.user_id` | `u.id` -> `u.id` | `tenant_id`, `username`, `email`, `status`, `is_active`, `full_name`, `created_at` | `WHERE u.is_deleted = false AND u.deleted_at IS NULL` |
| `:Department` | `public.departments` | `SELECT * FROM departments` | `id` -> `d.id` | `tenant_id`, `code`, `name`, `parent_department_id`, `manager_user_id` | `WHERE is_active = true` |
| `:Role` | `public.roles` | `SELECT * FROM roles` | `id` -> `r.id` | `tenant_id`, `code`, `name`, `description` | None |
| `:Permission` | `public.permissions` | `SELECT * FROM permissions` | `id` -> `p.id` | `tenant_id`, `code`, `name`, `module`, `action` | None |
| `:Project` | `public.projects` | `SELECT * FROM projects` | `id` -> `p.id` | `tenant_id`, `code`, `name`, `status`, `created_by_user_id`, `start_date`, `target_date`, `description` | `WHERE is_deleted = false` |
| `:Ticket` | `public.tickets` | `SELECT * FROM tickets` | `id` -> `t.id` | `tenant_id`, `ticket_number`, `title`, `priority`, `status`, `project_id`, `sprint_id`, `kanban_column_id`, `created_by_user_id`, `assignee_user_id`, `due_date` | `WHERE is_deleted = false` |
| `:Sprint` | `public.sprints` | `SELECT * FROM sprints` | `id` -> `s.id` | `project_id`, `name`, `status`, `start_date`, `end_date` | None |
| `:KanbanColumn` | `public.kanban_columns` | `SELECT * FROM kanban_columns` | `id` -> `k.id` | `project_id`, `name`, `column_order` | None |
| `:ApprovalRequest` | `public.approval_requests`| `SELECT * FROM approval_requests` | `id` -> `a.id` | `tenant_id`, `code`, `title`, `status`, `created_by_user_id`, `template_id`, `created_at` | `WHERE is_deleted = false` |
| `:WorkflowTemplate`| `public.workflow_templates`| `SELECT * FROM workflow_templates` | `id` -> `w.id` | `tenant_id`, `code`, `name`, `is_active`, `description` | None |
| `:ScheduleEvent` | `public.schedule_events` | `SELECT * FROM schedule_events` | `id` -> `e.id` | `tenant_id`, `title`, `event_date`, `start_time`, `end_time`, `created_by_user_id`, `room_id`, `status` | None |
| `:ScheduleRoom` | `public.schedule_rooms` | `SELECT * FROM schedule_rooms` | `id` -> `r.id` | `tenant_id`, `name`, `capacity`, `location` | `WHERE is_active = true` |
| `:Notice` | `public.notices` | `SELECT * FROM notices` | `id` -> `n.id` | `tenant_id`, `title`, `status`, `created_by_user_id`, `published_at` | `WHERE is_deleted = false` |
| `:CommunityPost` | `public.community_posts` | `SELECT * FROM community_posts` | `id` -> `c.id` | `tenant_id`, `title`, `author_user_id`, `category_id`, `created_at` | `WHERE is_deleted = false` |
| `:Asset` | `public.assets` | `SELECT * FROM assets` | `id` -> `a.id` | `tenant_id`, `asset_code`, `name`, `status`, `assigned_user_id`, `department_id` | `WHERE is_deleted = false` |
| `:FileMetadata` | `public.files` | `SELECT * FROM files` | `id` -> `f.id` | `tenant_id`, `file_name`, `file_size`, `mime_type`, `uploaded_by_user_id`, `storage_path`, `created_at` | `WHERE is_deleted = false` |
| `:ChatConversation`| `public.chat_conversations`| `SELECT * FROM chat_conversations` | `id` -> `c.id` | `tenant_id`, `title`, `type`, `is_direct`, `created_at` | `WHERE is_deleted = false` |

---

## 3. Relationship Ingestion & Cypher Mapping Specification

All relationship ingestions must follow defensive pattern standards:

### 3.1 Core Organizational Structure Ingestion
```cypher
// User to Department Membership
UNWIND $batch AS row
MATCH (u:User {id: row.user_id})
MATCH (d:Department {id: row.department_id})
MERGE (u)-[r:MEMBER_OF]->(d)
ON CREATE SET r.is_primary = row.is_primary, r.joined_at = datetime(row.joined_at);

// Department Manager (1:1)
UNWIND $batch AS row
MATCH (u:User {id: row.manager_user_id})
MATCH (d:Department {id: row.id})
MERGE (u)-[:MANAGES]->(d);

// Sub-department Hierarchy
UNWIND $batch AS row
MATCH (d1:Department {id: row.id})
MATCH (d2:Department {id: row.parent_department_id})
MERGE (d1)-[:SUB_DEPARTMENT_OF]->(d2);
```

### 3.2 Work Management & Ownership Ingestion
```cypher
// Project Creator (Direct FK)
UNWIND $batch AS row
MATCH (p:Project {id: row.id})
MATCH (u:User {id: row.created_by_user_id})
MERGE (p)-[:CREATED_BY]->(u);

// Project Membership & Ownership Derivation
UNWIND $batch AS row
MATCH (u:User {id: row.user_id})
MATCH (p:Project {id: row.project_id})
MERGE (u)-[r:MEMBER_OF_PROJECT]->(p)
ON CREATE SET r.role = row.role, r.joined_at = datetime(row.joined_at);

// Ticket Creator & Assignee
UNWIND $batch AS row
MATCH (t:Ticket {id: row.id})
MATCH (uCreator:User {id: row.created_by_user_id})
MERGE (t)-[:CREATED_BY]->(uCreator)
WITH t, row
WHERE row.assignee_user_id IS NOT NULL
MATCH (uAssignee:User {id: row.assignee_user_id})
MERGE (t)-[:ASSIGNED_TO]->(uAssignee);
```

### 3.3 Approval Workflow Ingestion
```cypher
// Approval Request Creator
UNWIND $batch AS row
MATCH (a:ApprovalRequest {id: row.id})
MATCH (u:User {id: row.created_by_user_id})
MERGE (a)-[:CREATED_BY]->(u);

// Approval Participants (Reviewers & Approvers)
UNWIND $batch AS row
MATCH (u:User {id: row.user_id})
MATCH (a:ApprovalRequest {id: row.approval_request_id})
MERGE (u)-[r:PARTICIPATES_IN]->(a)
ON CREATE SET 
  r.step_number = row.step_number,
  r.role = row.role,
  r.action_status = row.action_status;
```

---

## 4. Defensive ETL Rules: Nulls, Orphans & Soft-Deletes

### 4.1 Null Property Handling
Neo4j does not store null properties. Ingest scripts must omit setting properties when source values are NULL:
- **Rule**: If `row.room_id IS NULL`, do not create a `[:HELD_IN]` relationship.
- **Rule**: If an optional text attribute is NULL, do not set the property key on the node (keeps the graph sparse and memory efficient).

### 4.2 Handling of the 28 Partial-Match (Orphan) Relationships
Due to historical data maintenance cleanups (records purged into `_backup_cleanup_20261005`), several tables contain dangling foreign references (e.g. `role_permissions` where role IDs were purged):
- **Rule**: ETL pipelines must use `MATCH (source) ... OPTIONAL MATCH (target) ... WITH source, target WHERE target IS NOT NULL MERGE (source)-[:REL]->(target)`.
- Under no circumstances should an ETL job abort due to a missing target entity. Missing target references must be logged as telemetry warnings.

### 4.3 Soft-Delete Ingestion Enforcement
- **Rule**: Records marked with `is_deleted = true` or having a non-null `deleted_at` timestamp must be strictly excluded from the active Knowledge Graph during initial load and ongoing CDC (Change Data Capture) replication.
