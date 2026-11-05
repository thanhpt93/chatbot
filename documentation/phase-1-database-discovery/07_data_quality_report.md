# 07 – Data Quality & Profiling Report
## Groupware AI Chatbot Project – Phase 1: Database Discovery

> [!NOTE]
> This report evaluates data integrity, completeness, anomalies, orphan records, and potential risks identified during read-only profiling of the restored Groupware database.

---

## 1. Summary of Data Quality Findings

| Integrity Dimension | Evaluation | Discovered Metric | Risk Level |
|---|---|---|---|
| **Primary Key Completeness** | Excellent | 197 out of 198 base tables have explicit PKs (Only `talk_post_tags` lacks PK) | **LOW** |
| **Primary Key Uniqueness** | Flawless | 0 duplicate primary key values found across all tables | **NONE** |
| **Database Foreign Keys** | Non-existent in `public` | 0 FK constraints in `public` schema (2 in `hangfire` only) | **MEDIUM** |
| **Inferred Referential Integrity** | Very High (~92.5%) | 247 of 276 inferred relationships have 100% data match | **LOW** |
| **Orphan Data in Child Tables** | Moderate | 29 inferred relationships show orphan values due to historical user cleanup | **MEDIUM** |
| **Soft Deletion Consistency** | High | 56 tables use `deleted_at`, 57 use `is_deleted` | **LOW** |
| **NULL Value Discipline** | Good | Critical business codes and titles are consistently NOT NULL | **LOW** |

---

## 2. In-Depth Quality Dimension Analysis

### 2.1 Absence of Database Foreign Key Constraints in `public`
- **Observation**: The operational schema `public` contains **0 foreign key constraints**.
- **Impact**: The relational database engine does not enforce referential integrity at the storage layer; referential integrity is maintained entirely by application-level code.
- **Consequence for Phase 2 (Graph Modeling)**: When extracting relationships for Neo4j ETL, we cannot query `information_schema.referential_constraints` for table joins. Instead, the ETL must follow the validated relationship catalog documented in [`04_database_relationships.md`](file:///C:/Project/chatbot/documentation/phase-1-database-discovery/04_database_relationships.md).

### 2.2 Orphan Records Resulting from Historical Maintenance
- **Observation**: 29 relationships exhibit broken referential links with match rates ranging between 16.9% and 98.9%.
- **Root Cause Identified**: On October 5, 2026, an administrative data purge/cleanup was executed. Deleted users, profiles, and associated records were transferred to schema `_backup_cleanup_20261005` (which contains `users_deleted`, `user_profiles_deleted`, `department_members_deleted`, etc.).
- **Concrete Evidence**:
  - `project_members.user_id`: 18 distinct user IDs reference users that were deleted/archived.
  - `chat_conversation_members.user_id`: 28 distinct user IDs point to deleted users.
  - `ticket_tags.ticket_id`: 49 distinct ticket IDs point to deleted tickets.
- **Recommendation for Phase 2**: During Graph ETL, when importing nodes and edges, orphan relationships pointing to non-existent nodes must be safely handled (e.g., using `OPTIONAL MATCH` or omitting orphan edges) to avoid ETL failure.

### 2.3 Soft Deletion Patterns
- **Observation**: 56 tables implement `deleted_at` (timestamp) and 57 implement `is_deleted` (boolean).
- **Major Entities Affected**: `users`, `departments`, `projects`, `tickets`, `files`.
- **Chatbot Implication**: AI chatbot queries (e.g., *"How many active projects do we have?"* or *"Who is in the Design department?"*) MUST filter by `is_deleted = false` and `deleted_at IS NULL` to avoid including soft-deleted historical records.

### 2.4 Status Field Consistency
- **Observation**: Status fields across different tables use varying capitalization conventions:
  - `projects.status`: lowercase (`new`, `in_progress`)
  - `projects.approval_status`: UPPERCASE (`APPROVED`, `PENDING_APPROVAL`)
  - `approval_requests.status`: UPPERCASE (`COMPLETED`, `CANCELLED`, `IN_PROGRESS`, `REJECTED`, `RETURNED`)
  - `tickets.status`: lowercase (`create`)
  - `tickets.priority`: lowercase (`urgent`, `high`, `medium`, `low`)
  - `assets.status`: UPPERCASE (`IN_USE`, `ACTIVE`)
- **Recommendation**: Standardize or normalize status string casing during Phase 2 Graph ETL to provide uniform querying in Cypher.

---

## 3. Data Profile Catalog for Major Tables

| Table | Row Count | Primary Key | Key Columns Analyzed | NULL % | Distinct Values |
|---|---|---|---|---|---|
| `users` | 360 | `id` (bigint) | `email`, `username`, `is_active` | 0.0% | 360 emails, 360 usernames |
| `user_profiles` | 360 | `id` (bigint) | `user_id`, `display_name`, `department_id` | 0.0% user_id, 3.6% dept_id | 360 user_ids, 29 distinct depts |
| `departments` | 103 | `id` (bigint) | `code`, `name`, `parent_id`, `manager_user_id` | 0% code, 6.8% parent_id | 103 codes, 8 parent depts, 20 managers |
| `projects` | 65 | `id` (bigint) | `key`, `name`, `status`, `approval_status` | 0% key, 0% status | 65 keys, 2 statuses |
| `tickets` | 668 | `id` (bigint) | `code`, `title`, `project_id`, `priority` | 0% code, 0% project_id | 668 codes, 65 projects, 4 priorities |
| `approval_requests` | 4,709 | `id` (bigint) | `request_type`, `status`, `leave_type` | 0% type, 0% status | 8 request types, 7 statuses |
| `attendance_daily_records` | 54,489 | `id` (bigint) | `user_id`, `work_date`, `status` | 0% user_id, 0% date | 344 distinct users, 274 work dates |
| `assets` | 685 | `id` (bigint) | `code`, `name`, `status`, `current_holder_id` | 0% code, 19.8% holder_id | 685 codes, 224 distinct holders |
| `schedule_events` | 349 | `id` (bigint) | `title`, `start_time`, `visibility` | 0% title, 0% start_time | 267 distinct titles |
| `chat_conversations` | 329 | `id` (bigint) | `title`, `creator_id` | 0% creator_id | 329 conversations |
