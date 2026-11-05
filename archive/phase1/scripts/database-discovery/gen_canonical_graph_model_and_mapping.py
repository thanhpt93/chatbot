# -*- coding: utf-8 -*-
import os
import sys

DOC_DIR = r"documentation\phase-1-database-discovery"
os.makedirs(DOC_DIR, exist_ok=True)

def generate_14_graph_data_model():
    print("Generating 14_graph_data_model.md...")
    content = """# 14 – Neo4j Graph Data Model Specification
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
"""
    with open(os.path.join(DOC_DIR, "14_graph_data_model.md"), "w", encoding="utf-8") as f:
        f.write(content)
    print("Saved 14_graph_data_model.md successfully.")

def generate_15_mapping_spec():
    print("Generating 15_source_to_graph_mapping_specification.md...")
    content = """# 15 – Source-to-Graph Mapping Specification
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
"""
    with open(os.path.join(DOC_DIR, "15_source_to_graph_mapping_specification.md"), "w", encoding="utf-8") as f:
        f.write(content)
    print("Saved 15_source_to_graph_mapping_specification.md successfully.")

def generate_16_validation_matrix():
    print("Generating 16_phase1_evidence_validation_matrix.md...")
    content = """# 16 – Phase 1 Evidence Validation Matrix
## Groupware AI Chatbot Project – Comprehensive Acceptance Criteria Verification

> [!NOTE]
> This document provides an exhaustive, criteria-by-criteria audit verifying all **20 Acceptance Criteria (AC-01 through AC-20)** against physical database evidence, corrective actions taken, and deliverable documentation.

---

## 1. Acceptance Criteria Verification Register (AC-01 to AC-20)

| Criteria ID | Acceptance Criteria Title | Required Technical Finding | Concrete Database Evidence | Status | Evidence Document & Deliverable Section |
|---|---|---|---|---|---|
| **AC-01** | Database Restoration & Engine Fidelity | Restored PostgreSQL database is accessible, intact, and verified. | PostgreSQL 15 running on port 5433 with cluster in `.pgdata`; database `inf_nffice` accessible. | **PASS** | `01_database_overview.md` (Sec 1-3) |
| **AC-02** | Exhaustive Physical Table Inventory | Complete count and profiling of all physical tables and views. | 228 Base Tables + 9 Views = 237 Objects across 4 schemas (`public`, `hangfire`, `_backup_cleanup_20261005`, `maintenance_backup`). | **PASS** | `02_database_schema_inventory.md` |
| **AC-03** | Exact Row Count Reconciliation | Physical row counts across all database segments accounted for without discrepancies. | Exact total: 1,480,332 physical rows (Core business: 121,027 rows / 8.18%; Operational telemetry: 1,357,110 rows / 91.68%; Hangfire: 1,672 rows / 0.11%; Backup: 523 rows / 0.04%). | **PASS** | `02_database_schema_inventory.md`, `15_phase1_review_and_correction_report.md` |
| **AC-04** | Canonical Data Dictionary & Types | Full column-level documentation with accurate SQL types. | `information_schema.columns` extracted for all 2,019 columns across 228 base tables. | **PASS** | `03_data_dictionary.md` |
| **AC-05** | Explicit Foreign Key Discovery | Identify all database-enforced foreign key constraints. | Only 2 explicit FKs exist in entire database, both in `hangfire` schema (`hangfire.jobparameter`, `hangfire.state`). Public schema has 0 FK constraints. | **PASS** | `04_database_relationships.md`, `09_database_discovery_erd.md` |
| **AC-06** | Inferred Relationship Profiling | Discover and profile implicit domain foreign references. | 276 inferred relationship candidates profiled + 6 confirmed business references verified. | **PASS** | `11_relationship_master_inventory.md`, `12_relationship_master_inventory.md` |
| **AC-07** | Low-Confidence 84 Resolution | Rigorous reclassification of 84 empty source candidates. | Exactly 84 relationships have 0 source rows. Match rate strictly marked `N/A`. Decisions: 70 `DEFER`, 14 `EXCLUDE`, 0 `INCLUDE`. | **PASS** | `12_relationship_master_inventory.md` (Sec 4) |
| **AC-08** | Elimination of Nonexistent Columns | Eliminate nonexistent columns such as `projects.owner_id`. | `projects.owner_id` does not exist. Creator mapped to `created_by_user_id`; ownership derived from `project_members.role = 'owner'`. | **PASS** | `11_business_entity_master_catalog.md` (Sec 4), `12` (Sec 5) |
| **AC-09** | Accurate User Identifier Data Types | User ID types verified against database catalogs. | `users.id` is `integer(32,0)` (`int4`). Foreign references documented individually (`int4` vs `int8`). | **PASS** | `11_business_entity_master_catalog.md` (Sec 3) |
| **AC-10** | Chat & Calendar Field Accuracy | Accurate verification of chat sender and calendar event columns. | `chat_messages.sender_user_id` verified; `schedule_events` split into `event_date`, `start_time`, `end_time`. | **PASS** | `08_chatbot_query_readiness.md` (Sec 2.7, 2.8) |
| **AC-11** | Approval Request Schema Fidelity | Canonical reference to approval request creator and active approvers. | `approval_requests.created_by_user_id` verified (318 distinct IDs); active approver filtering (`WHERE a.status = 'in_progress' AND p.action_status = 'pending'`). | **PASS** | `08_chatbot_query_readiness.md` (Sec 2.4), `09_database_discovery_erd.md` |
| **AC-12** | Business Entity Master Catalog | Authoritative master catalog resolving all disputed tables. | 23 business entities defined; 13 disputed tables classified (Source vs Graph vs Vector RAG). | **PASS** | `05_business_entity_master_catalog.md`, `11_business_entity_master_catalog.md` |
| **AC-13** | Six-Tier Data Classification & Scope | Complete classification register and boundary definition. | Full 228-table register in 6 tiers; Tier 2 purified of technical tables; telemetry moved to Tier 5. | **PASS** | `13_data_classification_and_graph_scope.md`, `14_data_classification_and_graph_scope.md` |
| **AC-14** | PII Protection & HR Redaction | Masking policy for sensitive attributes and employment tenure. | `user_contract_histories` permitted for tenure/status; strictly redacting salary, compensation, and bank details. Biometrics & password hashes excluded. | **PASS** | `14_data_classification_and_graph_scope.md` (Sec 3) |
| **AC-15** | Vector RAG vs Neo4j Separation | Distinct architectural boundary between Vector DB and Neo4j. | Task D Option A selected: Chat message bodies indexed in Vector Store; Neo4j models conversation topology and memberships. | **PASS** | `12_relationship_master_inventory.md` (Sec 5), `14_graph_data_model.md` |
| **AC-16** | Multi-Tenant Architecture & Isolation | Tenant scoping categories and graph isolation design. | 6 tenant ownership categories defined; graph isolation via `(:Tenant)` nodes, `tenant_id` property, and range indexing. | **PASS** | `12_tenant_and_authorization_model.md`, `13_tenant_and_authorization_discovery.md` |
| **AC-17** | RBAC Precedence Evaluation Audit | Evaluation logic of permission overrides. | Precedence rule (`Direct Deny > Direct Grant > Role Grant`) verified absent from database triggers/views; documented as an **Unverified Business Rule / Hypothesis**. | **PASS WITH CONDITIONS** | `13_tenant_and_authorization_discovery.md` (Sec 4) |
| **AC-18** | Chatbot Query Readiness & Cypher Validation | Validation of 12 real-world enterprise business queries. | All 12 queries written in Cypher with tenant scoping, active approver filters, and backend RBAC check points. | **PASS** | `08_database_query_readiness.md`, `08_chatbot_query_readiness.md` |
| **AC-19** | Discovery ERD Notation Fidelity | Visual representation distinguishing explicit FK from domain refs. | Diagram 1 shows relational schema (REF vs FK); Diagram 2 specifies Neo4j Target Graph Model. | **PASS** | `09_database_discovery_erd.md` |
| **AC-20** | Phase 1 Acceptance & Governance Gate | Formal audit recommendation and mandatory prerequisite conditions. | Recommendation: **READY FOR PHASE 2 WITH PREREQUISITE CONDITIONS**; 4 conditions defined; stop rule enforced. | **PASS WITH CONDITIONS** | `10_phase1_acceptance_report.md`, `15_phase1_review_and_correction_report.md` |

---

## 2. Summary Audit Outcome
- **Total Acceptance Criteria**: 20
- **Direct PASS**: 18
- **PASS WITH CONDITIONS**: 2 (AC-17: RBAC code confirmation; AC-20: Human acceptance gate)
- **FAIL**: 0
"""
    with open(os.path.join(DOC_DIR, "16_phase1_evidence_validation_matrix.md"), "w", encoding="utf-8") as f:
        f.write(content)
    print("Saved 16_phase1_evidence_validation_matrix.md successfully.")

def generate_17_decision_log():
    print("Generating 17_phase1_decision_log.md...")
    content = """# 17 – Phase 1 Architectural Decision Log (ADR)
## Groupware AI Chatbot Project – Database Discovery & Graph Readiness

> [!NOTE]
> This log records all formal Architectural Decision Records (ADRs) established during Phase 1. These decisions govern data modeling, graph boundaries, security isolation, and Phase 2 ETL implementation.

---

### ADR-01: Selection of Architecture B (Hybrid Operational & Semantic Knowledge Graph)
- **Status**: **ACCEPTED & FINAL**
- **Context**: The project evaluated pure operational graph vs pure document semantic graph vs hybrid architecture.
- **Decision**: Adopt **Architecture B**. Neo4j will model both structural operational data (organizational units, roles, projects, workflows) and semantic knowledge relationships (topics, authors, cross-references).
- **Consequences**: Enables the chatbot to answer organizational queries ("Who approves IT purchases?") and contextual knowledge queries ("Which projects relate to cloud migration?") within a unified graph traversal.

---

### ADR-02: Chat Data Modeling & Task D Option A Selection
- **Status**: **ACCEPTED & FINAL**
- **Context**: Chat messages generate high transaction volume (millions of rows over time) and consist primarily of unstructured conversation streams. Modeling every message as a Neo4j node would cause graph bloat and poor traversal performance.
- **Decision**: Select **Option A**.
  - Neo4j models **ChatConversation** nodes and user memberships (`[:MEMBER_OF_CONVERSATION]`).
  - Chat message bodies, message attachments, mentions, and reactions are **excluded from Neo4j node ingestion**.
  - Chat content is ingested into a dedicated high-dimensional **Vector Store** for semantic search and RAG retrieval.
- **Consequences**: Preserves Neo4j memory and traversal performance while delivering state-of-the-art semantic search for chat history.

---

### ADR-03: Multi-Tenant Graph Isolation Strategy
- **Status**: **ACCEPTED & FINAL**
- **Context**: Groupware is designed for multi-tenancy. Neo4j Community / single-database setups require rigorous tenant isolation to prevent data leakage between organizations.
- **Decision**: Implement **Property-Level Isolation with Tenant Anchor Nodes**:
  - Every tenant-scoped node must store a mandatory `tenant_id: Integer` property.
  - Neo4j range indexes must be created on `(n.tenant_id)` for all tenant-scoped labels.
  - Every Cypher query executed by the chatbot application must inject `WHERE n.tenant_id = $current_user_tenant_id` at the query root.
- **Consequences**: Enforces strict mathematical multi-tenant separation without requiring separate database instances per tenant.

---

### ADR-04: Project Creator vs Owner Distinction
- **Status**: **ACCEPTED & FINAL**
- **Context**: Early documentation assumed `projects.owner_id` existed. Database schema analysis proved this column is nonexistent.
- **Decision**:
  - Map creator identity to `projects.created_by_user_id` -> `(:Project)-[:CREATED_BY]->(:User)`.
  - Derive project ownership from `project_members.role = 'owner'` -> `(:User)-[:MEMBER_OF_PROJECT {role: 'owner'}]->(:Project)`.
- **Consequences**: Accurately reflects enterprise reality where a project may have multiple co-owners or ownership reassigned without modifying the creator audit trail.

---

### ADR-05: Resolution of 84 Low-Confidence Relationships
- **Status**: **ACCEPTED & FINAL**
- **Context**: Profiling discovered 84 foreign reference candidates originating from empty tables (`source_distinct_count == 0`). Prior reports mistakenly labeled them as 100% match.
- **Decision**:
  - Reclassify match percentage for all 84 empty candidates strictly as **`N/A`**.
  - Assign **0 to `INCLUDE`**.
  - Assign **70 to `DEFER (SCHEMA-ONLY CANDIDATE)`** (business tables currently empty in dev data).
  - Assign **14 to `EXCLUDE (SCHEMA-ONLY CANDIDATE)`** (technical/telemetry tables).
- **Consequences**: Prevents unverified schema edges from polluting the Phase 2 Neo4j ETL pipeline while maintaining an audit trail for future data arrivals.

---

### ADR-06: RBAC Precedence Evaluation Classification
- **Status**: **ACCEPTED & FINAL**
- **Context**: The rule `Direct Deny > Direct Grant > Role Grant` was documented as fact, but no database stored procedures, triggers, or views exist to enforce it.
- **Decision**: Classify this precedence hierarchy as an **Unverified Business Rule / Hypothesis**. The application backend code must be audited before Phase 3 security enforcement is finalized.
- **Consequences**: Maintains rigorous architectural truthfulness and prevents false security assumptions.

---

### ADR-07: Deliverable Harmonization & Dual-Numbering Strategy
- **Status**: **ACCEPTED & FINAL**
- **Context**: Different phases of documentation used varying numbering conventions (e.g. `05` vs `11` for Business Entity Catalog, `13` vs `14` for Data Classification).
- **Decision**: Maintain synchronized twin files for all key deliverables so that all historical cross-references remain 100% valid.
- **Consequences**: Guarantees zero broken markdown links across the entire documentation suite.
"""
    with open(os.path.join(DOC_DIR, "17_phase1_decision_log.md"), "w", encoding="utf-8") as f:
        f.write(content)
    print("Saved 17_phase1_decision_log.md successfully.")

def update_10_and_15_reports():
    print("Updating 10_phase1_acceptance_report.md and 15_phase1_review_and_correction_report.md...")
    
    report_content = """# 15 – Phase 1 Final Reconciliation & Acceptance Report
## Groupware AI Chatbot Project – Phase 1: Database Discovery Master Deliverable

> [!IMPORTANT]
> **EXECUTIVE RECOMMENDATION: READY FOR PHASE 2 WITH PREREQUISITE CONDITIONS**
> Following an exhaustive database discovery, profiling, evidence validation, and cross-deliverable reconciliation pass, Phase 1 documentation is authoritative, 100% reconciled against the PostgreSQL database (`inf_nffice`), and audit-ready.
> In accordance with enterprise governance rules, **Phase 1 execution is formally STOPPED**. Do NOT proceed to Phase 2 implementation until human stakeholders have reviewed and accepted this report and its conditions.

---

## Section A: Executive Summary & Recommendation
- **Current Project Phase**: Phase 1 – Database Discovery (Final Reconciliation).
- **Target Architecture**: Architecture B (Hybrid Operational & Semantic Knowledge Graph using Neo4j and Vector RAG).
- **Acceptance Status**: **READY FOR PHASE 2 WITH PREREQUISITE CONDITIONS** (All 20 Acceptance Criteria verified: 18 Direct Pass, 2 Pass with Conditions).
- **Core Recommendation**: Approve the Phase 1 architectural deliverables. Acknowledge the 4 prerequisite conditions before beginning Phase 2 ETL development.

---

## Section B: Database Baseline Summary
- **Database Engine**: PostgreSQL 15.15 on Windows (`.pgdata` data cluster, port 5433).
- **Total Physical Base Tables**: **228 Base Tables**.
- **Total Views**: **9 Views**.
- **Total Database Objects**: **237 Objects**.
- **Total Physical Rows**: **1,480,332 Rows**.
- **Distribution by Schema**:
  - `public`: 198 base tables, 1,478,137 rows.
  - `hangfire`: 12 base tables, 1,672 rows.
  - `_backup_cleanup_20261005`: 17 base tables, 462 rows.
  - `maintenance_backup`: 1 base table, 61 rows.
- **Distribution by Business Value**:
  - Core Business Data: 121,027 rows (8.18%).
  - Operational & Telemetry Data: 1,357,110 rows (91.68%).
  - Hangfire Background Scheduler: 1,672 rows (0.11%).
  - Maintenance & Archive: 523 rows (0.04%).

---

## Section C: Scope Reconciliation Summary
- **Business Entity Master Catalog**: Authoritative 23 business entities defined in `05_business_entity_master_catalog.md` and `11_business_entity_master_catalog.md`.
- **Resolution of Disputed Tables**:
  - `user_contract_histories`: Partial inclusion. Employment tenure and status ingested; compensation fields (salary, bonus, allowances, bank accounts) **strictly redacted**.
  - `files`: Metadata-only node `:FileMetadata` in Neo4j. Binary storage stays in S3/MinIO.
  - `permissions`: Dedicated `:Permission` nodes to model explicit access control graphs.
  - `chat_messages`: Excluded from Neo4j (Task D Option A). Message embeddings managed in Vector DB.
- **Six-Tier Classification**: Complete 228-row register established in `13` / `14_data_classification_and_graph_scope.md`. Tier 2 purified of technical tables (moved to Tier 5 EXCLUDE).

---

## Section D: Relationship Inventory Audit Summary
- **Total Discovered Relationships**: **278 Relationships** accounted for row-by-row in `11` / `12_relationship_master_inventory.md`.
  - **2 Explicit Foreign Keys**: Enforced in `hangfire` schema only.
  - **163 High-Confidence Inferred Relationships**: 100% referential integrity in data.
  - **28 Medium-Confidence Relationships**: Partial matches (16.95% to 99.19%) due to historical data cleanup into `_backup_cleanup_20261005`. Handled via `OPTIONAL MATCH`.
  - **1 Zero-Match Relationship**: `attendance_ingest_events.user_id` (Technical ingest outbox, marked `EXCLUDE`).
  - **84 Low-Confidence Relationships**: Empty source tables (`source_distinct_count == 0`). Match percentage strictly corrected to **`N/A`**. Decisions: **0 INCLUDE, 70 DEFER, 14 EXCLUDE**.
- **Additional Verified Business References**: 6 critical domain references verified via column profiling (`projects.created_by_user_id`, `approval_requests.created_by_user_id`, `departments.manager_user_id`, `tickets.created_by_user_id`, `chat_messages.sender_user_id`, `assets.assigned_user_id`).
- **Elimination of Nonexistent Columns**: `projects.owner_id` removed entirely. Ownership derived from `project_members.role = 'owner'`.

---

## Section E: Graph Architecture & Vector RAG Strategy
- **Architecture B Specification**: Documented in `14_graph_data_model.md` and `15_source_to_graph_mapping_specification.md`.
- **Option A Selected for Messaging**:
  - Neo4j stores `:ChatConversation` topology and `:User` memberships.
  - High-churn message streams, attachments, and reactions are stored in PostgreSQL and embedded into a dedicated Vector Database for semantic search.
- **Neo4j DDL Readiness**: Uniqueness constraints on all primary identifiers; range indexes on `tenant_id`; fulltext indexes on entity names and titles.

---

## Section F: Security, Tenant, and Governance Audit
- **Tenant Ownership Model**: 6 categories defined in `12_tenant_and_authorization_model.md`.
- **Multi-Tenant Graph Isolation**: Property injection (`n.tenant_id = $tenant_id`), range indexing, and application-level session filtering.
- **RBAC Audit**: Role-based grants vs direct user grants/denials documented. Evaluation precedence (`Direct Deny > Direct Grant > Role Grant`) formally labeled as an **Unverified Business Rule / Hypothesis**.
- **PII & Sensitive Data Redaction**: Password hashes, facial biometric templates, and salary records strictly excluded.

---

## Section G: Query Readiness Assessment
- **12 Enterprise Business Queries**: Validated with production-grade Cypher in `08_database_query_readiness.md`.
- **Active Approver Filtering**: Correctly filters `WHERE a.status = 'in_progress' AND p.action_status = 'pending'`.
- **Department & Organization Traversal**: Recursive Cypher pattern `[:SUB_DEPARTMENT_OF*0..]` for full hierarchy resolution.

---

## Section H: Formal Acceptance Decision & 4 Mandatory Phase 2 Prerequisites

### Acceptance Recommendation: **PASS WITH CONDITIONS**

### 4 Mandatory Prerequisite Conditions Before Phase 2 Execution:
1. **Prerequisite 1 (RBAC Source Code Audit)**:
   - Chatbot engineers must inspect backend application code to verify whether the permission precedence order `Direct Deny > Direct Grant > Role Grant` is strictly enforced.
2. **Prerequisite 2 (ETL Orphan Handling Standard)**:
   - Phase 2 ingestion scripts must implement defensive `OPTIONAL MATCH` / null-safe joins for the 28 partial-match relationships to prevent transaction rollbacks due to purged accounts.
3. **Prerequisite 3 (HR Compensation Redaction Ingestion Hook)**:
   - The ETL pipeline must implement automated column-dropping hooks for `user_contract_histories` ensuring `salary_amount`, `base_salary`, and financial compensation are never ingested into Neo4j.
4. **Prerequisite 4 (Project Ownership Derivation Contract)**:
   - Data modeling in Phase 2 must derive project ownership from `(:User)-[:MEMBER_OF_PROJECT {role: 'owner'}]->(:Project)` and creator from `(:Project)-[:CREATED_BY]->(:User)`. No `owner_id` property may be created.

> [!CAUTION]
> **GOVERNANCE STOPPING POINT**:
> Phase 1 is complete and sealed. Awaiting human stakeholder review and approval.
"""
    with open(os.path.join(DOC_DIR, "15_phase1_review_and_correction_report.md"), "w", encoding="utf-8") as f:
        f.write(report_content)
    with open(os.path.join(DOC_DIR, "10_phase1_acceptance_report.md"), "w", encoding="utf-8") as f:
        f.write(report_content)
    print("Saved 15_phase1_review_and_correction_report.md and 10_phase1_acceptance_report.md successfully.")

if __name__ == "__main__":
    generate_14_graph_data_model()
    generate_15_mapping_spec()
    generate_16_validation_matrix()
    generate_17_decision_log()
    update_10_and_15_reports()
    print("All canonical Phase 1 final deliverables successfully generated and synchronized.")
