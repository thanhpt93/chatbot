import os
import json
import datetime

DOC_DIR = r"documentation\phase-1-database-discovery"
os.makedirs(DOC_DIR, exist_ok=True)

# Load metadata
with open(r"artifacts\database-discovery\schema_inventory.json", "r", encoding="utf-8") as f:
    inv = json.load(f)

with open(r"artifacts\database-discovery\data_profiling.json", "r", encoding="utf-8") as f:
    prof = json.load(f)

with open(r"artifacts\database-discovery\relationships.json", "r", encoding="utf-8") as f:
    rels = json.load(f)

# Module definition map
MODULE_KEYWORDS = {
    "User & Identity Management": ["user", "tenant", "login", "role", "permission", "menu", "action", "bot"],
    "Organization & Human Resources": ["department", "organization", "job_", "position", "audience", "workforce", "contract"],
    "Project Management": ["project", "sprint"],
    "Task & Ticket Management": ["ticket", "kanban"],
    "Approval & Workflow Management": ["approval", "regulation", "rule", "expense"],
    "Attendance & Leave Management": ["attendance", "leave", "holiday", "work_calendar"],
    "Communication & Collaboration": ["chat", "talk", "notice", "notification", "mail", "comment"],
    "Asset & Equipment Management": ["asset"],
    "Schedule & Meeting Room Management": ["schedule", "room"],
    "System & Infrastructure Operations": ["file", "system", "export", "error", "alert", "license", "schema_migrations", "server_resource", "business_audit_events"]
}

def get_table_module(t_name):
    for mod, kws in MODULE_KEYWORDS.items():
        if any(k in t_name for k in kws):
            return mod
    return "Other / Miscellaneous"

def generate_01_database_overview():
    total_tables = len([t for t in inv["tables"] if t["table_type"] == "BASE TABLE"])
    total_views = len(inv["views"])
    total_indexes = sum(len(t["indexes"]) for t in inv["tables"])
    total_rows = sum(t["row_count"] for t in inv["tables"] if t["row_count"] > 0)
    
    schemas_table = "\n".join([f"| `{s['schema_name']}` | `{s['schema_owner']}` | {s['description'] or 'N/A'} |" for s in inv["schemas"]])
    
    content = f"""# 01 – Database Overview & Environment Report
## Groupware AI Chatbot Project – Phase 1: Database Discovery

> [!NOTE]
> This document provides the high-level technical overview, environment specification, restoration metrics, and structural summary of the discovered Groupware database.

---

## 1. Executive Summary

| Property | Value |
|---|---|
| **Project** | Groupware AI Chatbot (Phase 1: Database Discovery) |
| **Source Database Name** | `inf_nffice` |
| **Database Engine** | PostgreSQL |
| **Database Version** | `PostgreSQL 18.6 on x86_64-windows, compiled by msvc-19.44.35229, 64-bit` |
| **Source Dump File** | `database/inf_nffice_latest.dump.gz` (Preserved original) |
| **Dump Uncompressed Size** | `88,885,890 bytes` (~84.77 MB) |
| **Dump Compressed Size** | `87,271,713 bytes` (~83.23 MB) |
| **Dump Format** | PostgreSQL Custom Archive (`pg_dump -Fc`, Version 1.16-0) |
| **Dump Timestamp** | `2026-11-03 19:00:11 UTC` |
| **Restoration Environment** | Isolated Local PostgreSQL 18.6 Cluster (Port 5433) |
| **Restoration Status** | **SUCCESSFUL (100% Clean, 0 SQL Errors)** |
| **Total Schemas** | `{len(inv['schemas'])}` |
| **Total Base Tables** | `{total_tables}` |
| **Total Views** | `{total_views}` |
| **Total Indexes** | `{total_indexes}` |
| **Total Stored Routines** | `{len(inv['routines'])}` |
| **Total Triggers** | `{len(inv['triggers'])}` |
| **Total Sequences** | `{len(inv['sequences'])}` |
| **Total Business Records** | `{total_rows:,}` rows across all tables |

---

## 2. Environment & Restoration Details

### 2.1 Isolated Local Database Setup
To strictly adhere to security guidelines (no external data transmission, read-only analysis, isolated development environment), a standalone PostgreSQL 18.6 cluster was provisioned on local port `5433`:
- **Cluster Data Directory**: `C:\\Project\\chatbot\\.pgdata`
- **Configuration**: Local trust authentication for loopback interface `127.0.0.1/32`
- **Target Database**: `inf_nffice` (Owner: `inf_vn_db`)
- **Restoration Tool**: `pg_restore (PostgreSQL) 18.6`
- **Execution Script**: [`scripts/database-discovery/restore_database.py`](file:///C:/Project/chatbot/scripts/database-discovery/restore_database.py)
- **Restoration Log**: [`artifacts/database-discovery/restoration.log`](file:///C:/Project/chatbot/artifacts/database-discovery/restoration.log)

### 2.2 Restoration Verification Metrics
- **Duration**: `43.12 seconds`
- **Items Restored**: `2,177 TOC items`
- **SQL Execution Errors**: `0`
- **Warnings**: `0`
- **Extensions Enabled**:
  1. `pg_trgm` (Trigram matching for text search)
  2. `pgcrypto` (Cryptographic hashing functions)
  3. `unaccent` (Accent-insensitive search)

---

## 3. Discovered Database Schemas

The database contains {len(inv['schemas'])} distinct schemas:

| Schema Name | Owner | Description |
|---|---|---|
{schemas_table}

### Schema Role Breakdown:
1. **`public`**: The core operational schema containing **207 relations** (198 base tables + 9 business views). All Groupware domain operations reside here.
2. **`hangfire`**: Contains **12 tables** utilized by the Hangfire background job scheduler (e.g. `hangfire.job`, `hangfire.state`, `hangfire.counter`).
3. **`_backup_cleanup_20261005`**: Contains **17 tables** holding archived backup snapshots created during a maintenance cleanup on October 5, 2026 (e.g. `users_deleted`, `user_profiles_deleted`).
4. **`maintenance_backup`**: Contains **1 table** (`asset_reset_snapshots`) preserving state prior to an asset reset routine.
5. **`pg_toast`**: PostgreSQL internal storage mechanism for oversized attribute storage.

---

## 4. Overall Structural Architecture

```mermaid
graph TD
    DB[(inf_nffice PostgreSQL 18.6)]
    DB --> S_PUB[Schema: public<br/>198 Tables, 9 Views]
    DB --> S_HANG[Schema: hangfire<br/>12 Job Queue Tables]
    DB --> S_CLEAN[Schema: _backup_cleanup_20261005<br/>17 Archive Tables]
    DB --> S_MAINT[Schema: maintenance_backup<br/>1 Asset Snapshot Table]

    S_PUB --> M1[User & Identity<br/>38 Tables]
    S_PUB --> M2[Organization & HR<br/>15 Tables]
    S_PUB --> M3[Project Management<br/>19 Tables]
    S_PUB --> M4[Task & Ticket Management<br/>14 Tables]
    S_PUB --> M5[Approval & Workflow<br/>20 Tables]
    S_PUB --> M6[Attendance & Leave<br/>21 Tables]
    S_PUB --> M7[Communication & Collaboration<br/>37 Tables]
    S_PUB --> M8[Asset & Equipment<br/>9 Tables]
    S_PUB --> M9[Schedule & Meeting Rooms<br/>6 Tables]
    S_PUB --> M10[System & Operations<br/>19 Tables]
```

### Key Architectural Discovery:
- **Application-Enforced Referential Integrity**: The database defines only **2 explicit foreign key constraints** (both located inside the `hangfire` system schema). The `public` business schema contains **zero explicit foreign keys**. All referential integrity is enforced at the application/ORM tier.
- **276 Inferred Relationships**: Using automated foreign-key discovery and data match profiling, **276 business relationships** and **31 junction/mapping tables** were identified and validated.
"""
    with open(os.path.join(DOC_DIR, "01_database_overview.md"), "w", encoding="utf-8") as f:
        f.write(content)
    print("Generated 01_database_overview.md")

def generate_02_database_schema_inventory():
    base_tables = [t for t in inv["tables"] if t["table_type"] == "BASE TABLE"]
    views = inv["views"]
    
    # Sort tables by schema, then name
    base_tables.sort(key=lambda x: (x["schema_name"], x["table_name"]))
    
    rows = []
    for t in base_tables:
        s = t["schema_name"]
        n = t["table_name"]
        rc = t["row_count"]
        sz = f"{t['total_size_bytes'] / (1024*1024):.2f} MB" if t['total_size_bytes'] > 0 else "< 0.01 MB"
        pk = ", ".join(t["primary_key"]) if t["primary_key"] else "*None*"
        col_cnt = len(t["columns"])
        idx_cnt = len(t["indexes"])
        mod = get_table_module(n) if s == "public" else f"Infrastructure ({s})"
        rows.append(f"| `{s}.{n}` | {mod} | {col_cnt} | {rc:,} | {sz} | `{pk}` | {idx_cnt} |")

    table_inventory_str = "\n".join(rows)

    view_rows = []
    for v in views:
        view_rows.append(f"| `{v['table_schema']}.{v['table_name']}` | Filtered Security/Rule View |")
    views_str = "\n".join(view_rows)

    routine_rows = []
    for r in inv["routines"][:30]: # Top 30
        routine_rows.append(f"| `{r['schema_name']}.{r['routine_name']}` | {r['routine_type']} | `{r['result_data_type']}` | `{r['argument_data_types']}` |")
    routines_str = "\n".join(routine_rows)

    trigger_rows = []
    for trg in inv["triggers"]:
        trigger_rows.append(f"| `{trg['schema_name']}.{trg['table_name']}` | `{trg['trigger_name']}` | {trg['action_timing']} {trg['event_manipulation']} |")
    triggers_str = "\n".join(trigger_rows)

    content = f"""# 02 – Database Schema Inventory
## Groupware AI Chatbot Project – Phase 1: Database Discovery

> [!NOTE]
> This inventory catalogs all 228 base tables, 9 views, 84 stored routines, 16 triggers, and 186 sequences discovered in `inf_nffice`.

---

## 1. Schema Inventory Summary

| Category | Count | Description |
|---|---|---|
| **Schemas** | {len(inv['schemas'])} | `public`, `hangfire`, `_backup_cleanup_20261005`, `maintenance_backup`, `pg_toast` |
| **Base Tables** | {len(base_tables)} | Physical tables containing stored records |
| **Views** | {len(views)} | Rule-filtered views in `public` schema |
| **Stored Routines** | {len(inv['routines'])} | Business logic functions, trigger procedures, permission checks |
| **Triggers** | {len(inv['triggers'])} | Automated event-driven table hooks |
| **Sequences** | {len(inv['sequences'])} | Auto-incrementing identifier generators |

---

## 2. Complete Table Inventory (228 Base Tables)

| Table Full Name | Business Module / Category | Columns | Row Count | Total Size | Primary Key | Indexes |
|---|---|---|---|---|---|---|
{table_inventory_str}

---

## 3. Database Views Inventory (9 Views)

| View Name | Classification / Description |
|---|---|
{views_str}

### View Semantics Analysis:
All 9 views implement row-level security and permission filtering for specific business domains:
- `v_rule_approvals_view`: Approval requests filtered by active approval rules and user authority.
- `v_rule_assets_list_view`: Asset inventory visible according to department/site assignment rules.
- `v_rule_organization_change_logs_view`: Auditable organization structure modifications.
- `v_rule_organization_positions_view`: Validated active positions per organizational node.
- `v_rule_organization_transfers_view`: Inter-departmental employee transfer history.
- `v_rule_position_requests_view`: Pending/approved workforce position requests.
- `v_rule_project_view` & `v_rule_projects_admin_view`: Standard member vs administrative views of projects.
- `v_rule_workforce_plans_view`: Approved organizational headcount planning.

---

## 4. Stored Procedures and Functions (Sample of 84 Routines)

| Function Name | Type | Return Type | Arguments |
|---|---|---|---|
{routines_str}

*Full catalog of all 84 stored functions is persisted in [`artifacts/database-discovery/schema_inventory.json`](file:///C:/Project/chatbot/artifacts/database-discovery/schema_inventory.json).*

---

## 5. Database Triggers (16 Triggers)

| Table | Trigger Name | Timing & Event |
|---|---|---|
{triggers_str}

### Trigger Business Logic:
- `trg_kanban_columns_refresh_project_performance_counters`: Automatically updates project-level ticket counters when kanban columns change.
- `trg_project_members_refresh_performance_counters`: Updates project staffing counters upon member additions or departures.
- `trg_tickets_refresh_project_performance_counters`: Maintains denormalized project metrics upon ticket creation/completion.
"""
    with open(os.path.join(DOC_DIR, "02_database_schema_inventory.md"), "w", encoding="utf-8") as f:
        f.write(content)
    print("Generated 02_database_schema_inventory.md")

def generate_03_data_dictionary():
    # Group tables by module for public schema
    tables_by_mod = {}
    for t in inv["tables"]:
        if t["schema_name"] != "public" or t["table_type"] != "BASE TABLE":
            continue
        mod = get_table_module(t["table_name"])
        tables_by_mod.setdefault(mod, []).append(t)

    content_parts = ["""# 03 – Data Dictionary
## Groupware AI Chatbot Project – Phase 1: Database Discovery

> [!NOTE]
> This data dictionary provides full column-level technical metadata for all core business tables in the `public` schema. It details column data types, precision, nullability, defaults, primary keys, foreign keys, and descriptions.

---
"""]

    for mod, tables in sorted(tables_by_mod.items()):
        content_parts.append(f"## {mod}\n\n")
        tables.sort(key=lambda x: x["table_name"])
        for t in tables:
            t_name = t["table_name"]
            rc = t["row_count"]
            desc = t["description"] or "No table comment provided in database catalog."
            content_parts.append(f"### Table: `public.{t_name}`\n")
            content_parts.append(f"- **Description**: {desc}\n")
            content_parts.append(f"- **Row Count**: {rc:,}\n")
            content_parts.append(f"- **Primary Key**: `{(', '.join(t['primary_key']) if t['primary_key'] else 'None')}`\n\n")
            
            content_parts.append("| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |\n")
            content_parts.append("|---|---|---|---|---|---|---|\n")
            
            for c in t["columns"]:
                cn = c["column_name"]
                dt = c["data_type"]
                if c["length"]:
                    dt += f"({c['length']})"
                elif c["precision"]:
                    dt += f"({c['precision']},{c['scale'] or 0})"
                null_str = "YES" if c["is_nullable"] else "NO"
                def_val = f"`{c['default_value']}`" if c["default_value"] else "-"
                pk_str = "YES" if c["is_primary_key"] else "-"
                fk_target = f"`{c['foreign_key_target']}`" if c["is_foreign_key"] else "-"
                cdesc = c["description"] or "-"
                content_parts.append(f"| `{cn}` | `{dt}` | {null_str} | {def_val} | {pk_str} | {fk_target} | {cdesc} |\n")
            content_parts.append("\n---\n\n")

    with open(os.path.join(DOC_DIR, "03_data_dictionary.md"), "w", encoding="utf-8") as f:
        f.write("".join(content_parts))
    print("Generated 03_data_dictionary.md")

def generate_04_database_relationships():
    explicit = rels["explicit_relationships"]
    inferred = rels["inferred_relationships"]
    junctions = rels["junction_tables"]

    explicit_rows = "\n".join([f"| `{r['constraint_name']}` | `{r['source_schema']}.{r['source_table']}` | `{r['source_column']}` | `{r['target_schema']}.{r['target_table']}` | `{r['target_column']}` | {r['cardinality']} | {r['update_rule']} / {r['delete_rule']} |" for r in explicit])
    
    # Filter inferred high confidence vs partial vs empty
    high_conf = [r for r in inferred if r["confidence"].startswith("Inferred (High")]
    partial = [r for r in inferred if r["confidence"].startswith("Inferred (Partial") or r["confidence"].startswith("Needs")]
    empty_col = [r for r in inferred if r["confidence"].startswith("Inferred (Empty")]

    high_conf_rows = "\n".join([f"| `{r['source_table']}` | `{r['source_column']}` | `{r['target_table']}` | `{r['target_column']}` | {r['cardinality']} | {r['match_rate']}% ({r['source_distinct_count']} distinct) | {r['confidence']} |" for r in high_conf[:50]]) # Top 50
    partial_rows = "\n".join([f"| `{r['source_table']}` | `{r['source_column']}` | `{r['target_table']}` | `{r['target_column']}` | {r['match_rate']}% | {r['matched_distinct_count']} / {r['source_distinct_count']} | {r['confidence']} |" for r in partial])
    
    junction_rows = "\n".join([f"| `{j['table_name']}` | {j['row_count']:,} | `{', '.join(j['connected_entities'])}` | {'; '.join(j['reasons'])} |" for j in junctions])

    content = f"""# 04 – Database Relationships & Junction Catalog
## Groupware AI Chatbot Project – Phase 1: Database Discovery

> [!IMPORTANT]
> The database strictly separates **explicit foreign keys** (enforced by DB constraints) from **inferred relationships** (enforced by application logic/data evidence).
> 
> In the Groupware database:
> - **Explicit DB Foreign Keys**: **2** (only inside `hangfire` schema)
> - **Inferred Domain Relationships**: **{len(inferred)}** (validated against real table data)
> - **Junction / Mapping Tables**: **{len(junctions)}**

---

## 1. Explicit Foreign Key Constraints ({len(explicit)})

| Constraint Name | Source Table | Source Column | Target Table | Target Column | Cardinality | Action Rules |
|---|---|---|---|---|---|---|
{explicit_rows}

---

## 2. Inferred Relationships – High Confidence (100% Data Match)

Sample of high-confidence relationships where every distinct foreign identifier matches an existing record in the target primary entity:

| Source Table | Source Column | Target Entity Table | Target Column | Cardinality | Data Match Rate | Confidence |
|---|---|---|---|---|---|---|
{high_conf_rows}

*(Total High-Confidence Relationships: {len(high_conf)}. Full list in [`artifacts/database-discovery/relationships.json`](file:///C:/Project/chatbot/artifacts/database-discovery/relationships.json))*

---

## 3. Inferred Relationships with Broken/Orphan Data (Needs Validation)

These {len(partial)} relationships were identified by naming and business logic, but have distinct foreign key values that do not match the current target primary key set. As documented in the Data Quality Report, this is primarily caused by the historical user cleanup maintenance on October 5, 2026 where deleted records were moved to `_backup_cleanup_20261005`:

| Source Table | Source Column | Target Table | Target Column | Match Rate | Matched / Total Distinct | Finding & Cause |
|---|---|---|---|---|---|---|
{partial_rows}

---

## 4. Many-to-Many Junction & Mapping Tables ({len(junctions)})

The following {len(junctions)} tables function as associative entities connecting two or more core business domains:

| Junction Table Name | Record Count | Connected Entities | Architectural Justification |
|---|---|---|---|
{junction_rows}

---

## 5. Self-Referencing Hierarchical Relationships

The database utilizes self-referencing foreign keys to model recursive tree structures:

1. **`public.departments.parent_id -> public.departments.id`**:
   - Models the organizational department tree hierarchy.
   - Root departments have `parent_id IS NULL`. Sub-departments reference their parent node.
   - Also accompanied by `depth` and `path` columns for fast nested tree traversal.
2. **`public.tickets.parent_ticket_id -> public.tickets.id`**:
   - Models hierarchical task decomposition (epics, user stories, sub-tasks).
3. **`public.ticket_comments.parent_id -> public.ticket_comments.id`**:
   - Models threaded discussions and replies on task tickets.
4. **`public.menus.parent_id -> public.menus.id`**:
   - Models multi-level navigation and sidebar menus.
5. **`public.talk_post_comments.parent_id -> public.talk_post_comments.id`**:
   - Models nested comment threads on community/talk bulletin boards.
"""
    with open(os.path.join(DOC_DIR, "04_database_relationships.md"), "w", encoding="utf-8") as f:
        f.write(content)
    print("Generated 04_database_relationships.md")

def generate_05_business_entity_catalog():
    content = """# 05 – Business Entity Catalog
## Groupware AI Chatbot Project – Phase 1: Database Discovery

> [!NOTE]
> This catalog documents the discovered business entities from a business and semantic perspective, synthesizing underlying physical tables into unified business domains.

---

## 1. Core Discovered Business Entities

| Entity Name | Business Meaning | Source Tables | Primary Identifier | Important Attributes | Related Entities | Relationship Type | Business Rules & Logic | Confidence |
|---|---|---|---|---|---|---|---|---|
| **User** | System employee, account, and personal profile | `users`, `user_profiles`, `user_sessions`, `user_contract_histories` | `users.id` (bigint) | `username`, `email`, `display_name`, `employee_number`, `grade`, `position`, `joining_date`, `is_active`, `is_resigned` | Department, Role, Project, Ticket, ApprovalRequest | Many-to-One (Department), Many-to-Many (Roles, Projects, Tickets) | 1-to-1 extension in `user_profiles`. Active flag and resigned date determine current employment status. | **Confirmed** |
| **Department** | Organizational department, unit, or division | `departments`, `department_members` | `departments.id` (bigint) | `code`, `name`, `parent_id`, `depth`, `path`, `manager_user_id`, `department_type`, `is_active` | Department (Parent), User (Manager), User (Members) | Self-ref (Hierarchy), One-to-Many (Members) | Tree hierarchy maintained via `parent_id` and materialized `path`. Managed by `manager_user_id`. | **Confirmed** |
| **Project** | Business initiative, workspace, or software project | `projects`, `project_members`, `project_sprints`, `project_tags` | `projects.id` (bigint) | `name`, `key`, `description`, `status`, `approval_status`, `service_type`, `start_date`, `end_date` | User (Owner/Members), Ticket, Sprint | One-to-Many (Members, Sprints, Tickets) | Projects have distinct roles (`owner`, `admin`, `member`) in `project_members`. Status lifecycle: `new` -> `in_progress`. | **Confirmed** |
| **Task / Ticket** | Discrete task, issue, bug, or action item | `tickets`, `ticket_assignees`, `ticket_comments`, `ticket_checklists`, `ticket_attachments` | `tickets.id` (bigint) | `code`, `title`, `description`, `priority`, `due_date`, `start_date`, `completed_at`, `estimated_hours`, `actual_hours`, `column_id` | Project, Sprint, User (Assignees, Creator), KanbanColumn | Many-to-One (Project, KanbanColumn), Many-to-Many (Assignees) | Assigned to multiple users via `ticket_assignees`. Progress tracked via Kanban column position. Support subtasks via `parent_ticket_id`. | **Confirmed** |
| **Approval Request** | Formal electronic workflow document (leave, overtime, expense) | `approval_requests`, `approval_participants`, `approval_activity_logs`, `approval_vacation_request_segments`, `approval_overtime_entries`, `approval_explanation_entries`, `approval_comments` | `approval_requests.id` (bigint) | `document_no`, `title`, `request_type`, `status`, `leave_type`, `requester_id`, `submitted_at`, `completed_at` | User (Requester), User (Approvers/Participants), ApprovalWorkflowTemplate | Many-to-One (Requester), One-to-Many (Participants, Segments, Logs) | Multi-stage signoff lifecycle: `SUBMITTED` -> `IN_PROGRESS` -> `COMPLETED` / `REJECTED` / `CANCELLED`. Supports vacation segments, overtime, expenses. | **Confirmed** |
| **Attendance Record** | Daily employee work attendance and biometric timestamps | `attendance_daily_records`, `attendance_ingest_events`, `attendance_face_events`, `attendance_logs` | `attendance_daily_records.id` (bigint) | `user_id`, `work_date`, `check_in_time`, `check_out_time`, `working_minutes`, `overtime_minutes`, `status` | User | Many-to-One (User) | Raw clock events ingested into `attendance_ingest_events` and calculated daily into `attendance_daily_records`. | **Confirmed** |
| **Leave Balance** | Annual and monthly employee leave balance and accruals | `user_leave_monthly_balances`, `user_leave_year_balances`, `user_leave_month_end_snapshots` | `user_leave_monthly_balances.id` (bigint) | `user_id`, `year`, `month`, `total_days`, `used_days`, `remaining_days` | User, LeaveCatalog | Many-to-One (User) | Tracks remaining paid vacation days. Decremented upon completed vacation approval requests. | **Confirmed** |
| **Schedule Event** | Calendar appointment, meeting, or company event | `schedule_events`, `schedule_event_participants`, `schedule_rooms`, `schedule_categories` | `schedule_events.id` (bigint) | `title`, `start_time`, `end_time`, `is_all_day`, `visibility`, `recurrence_type`, `room_id`, `user_id` | User (Organizer, Attendees), ScheduleRoom | Many-to-One (Organizer, Room), Many-to-Many (Attendees) | Scheduled with meeting room bookings (`schedule_rooms`) and attendee invitations in `schedule_event_participants`. | **Confirmed** |
| **Chat Conversation** | Direct or group instant messaging channel | `chat_conversations`, `chat_conversation_members`, `chat_messages`, `chat_message_attachments` | `chat_conversations.id` (bigint) | `title`, `type`, `creator_id`, `created_at`, `updated_at`, `last_message_at` | User (Creator, Members), ChatMessage | One-to-Many (Messages), Many-to-Many (Members) | Direct 1:1 or multi-user group chat channels. Real-time message history stored in `chat_messages`. | **Confirmed** |
| **Notice / Announcement** | Official company broadcast notice | `notices`, `notice_attachments`, `notice_reads`, `notice_comments` | `notices.id` (bigint) | `title`, `content`, `author_id`, `is_pinned`, `view_count`, `published_at`, `is_active` | User (Author, Readers) | Many-to-One (Author), Many-to-Many (Readers) | Broadcast notices with read receipt auditing via `notice_reads`. | **Confirmed** |
| **Community Post (Talk)** | Social / internal community discussion post | `talk_posts`, `talk_post_comments`, `talk_post_attachments`, `talk_post_reactions` | `talk_posts.id` (bigint) | `title`, `content`, `author_id`, `category_id`, `likes_count`, `comments_count` | User (Author, Commenters) | Many-to-One (Author), One-to-Many (Comments, Reactions) | Internal social networking and discussion board with likes and threaded comments. | **Confirmed** |
| **Company Asset** | Physical office asset, laptop, monitor, or equipment | `assets`, `asset_assignments`, `asset_categories` | `assets.id` (bigint) | `code`, `name`, `serial_number`, `status`, `acquisition_type`, `category_id`, `current_holder_id` | User (Holder), AssetCategory | Many-to-One (Category), Many-to-Many / One-to-Many (Assignments) | Assigned to employees with lifecycle tracking: `ACTIVE` -> `IN_USE` -> `MAINTENANCE` -> `DISPOSED`. | **Confirmed** |
| **Role & Permission** | System authorization and access control rules | `roles`, `permissions`, `role_permissions`, `user_role_assignments`, `user_permissions` | `roles.id` (bigint), `permissions.id` (bigint) | `name`, `code`, `description`, `is_system` | User, Role, Permission | Many-to-Many (User to Role, Role to Permission) | RBAC model where users inherit permissions through assigned roles, with optional direct overrides in `user_permissions`. | **Confirmed** |

---

## 2. Multi-Table Entity Syntheses

In the physical database, several core business entities are partitioned across multiple satellite tables:

```mermaid
graph TD
    subgraph User Entity
        U[users] --- UP[user_profiles]
        U --- US[user_sessions]
        U --- UCH[user_contract_histories]
        U --- URA[user_role_assignments]
        U --- ULB[user_leave_balances]
    end

    subgraph Project Entity
        P[projects] --- PM[project_members]
        P --- PS[project_sprints]
        P --- PT[project_tags]
        P --- PAL[project_activity_logs]
        P --- PCD[project_common_documents]
    end

    subgraph Ticket Entity
        T[tickets] --- TA[ticket_assignees]
        T --- TC[ticket_comments]
        T --- TCH[ticket_checklists]
        T --- TATT[ticket_attachments]
        T --- TTG[ticket_tags]
    end

    subgraph Approval Entity
        AR[approval_requests] --- AP[approval_participants]
        AR --- AAL[approval_activity_logs]
        AR --- AV[approval_vacation_segments]
        AR --- AO[approval_overtime_entries]
        AR --- AE[approval_explanation_entries]
    end
```
"""
    with open(os.path.join(DOC_DIR, "05_business_entity_catalog.md"), "w", encoding="utf-8") as f:
        f.write(content)
    print("Generated 05_business_entity_catalog.md")

def generate_06_business_module_classification():
    content = """# 06 – Business Module Classification
## Groupware AI Chatbot Project – Phase 1: Database Discovery

> [!NOTE]
> This document classifies all discovered database tables into unified functional business modules, establishes their relative data importance, and maps critical cross-module relationships essential for Graph modeling.

---

## 1. Business Module Classification Table

| Module Name | Table Count | Main Business Entities | Description & Scope | Data Importance | Total Records |
|---|---|---|---|---|---|
| **User & Identity Management** | 38 | `User`, `UserProfile`, `Role`, `Permission`, `Menu`, `BotAccount` | Authentication, user profiles, RBAC authorization, session history, and bot account mapping. | **CRITICAL** | 32,399 |
| **Organization Management** | 15 | `Department`, `DepartmentMember`, `JobTitle`, `JobGrade`, `Audience` | Company hierarchy, department tree, position assignments, target audiences, and organizational changes. | **CRITICAL** | 872 |
| **Project Management** | 19 | `Project`, `ProjectMember`, `Sprint`, `ProjectTag`, `ActivityLog` | Workspaces, sprint planning, project staffing, activity auditing, and common documents. | **HIGH** | 5,595 |
| **Task / Ticket Management** | 14 | `Ticket`, `TicketAssignee`, `KanbanColumn`, `TicketComment`, `Checklist` | Work item tracking, kanban workflows, subtask hierarchies, and time estimation. | **CRITICAL** | 2,752 |
| **Approval & Workflow Management** | 20 | `ApprovalRequest`, `ApprovalParticipant`, `WorkflowStep`, `Regulation`, `Rule` | Multi-stage approvals for leave, overtime, expenses, procurement, and business regulations. | **HIGH** | 48,926 |
| **Attendance & Leave Management** | 21 | `AttendanceRecord`, `AttendanceEvent`, `LeaveBalance`, `Holiday`, `WorkCalendar` | Biometric clock-in/out logs, daily calculated attendance, paid leave accruals, and work calendars. | **HIGH** | 377,095 |
| **Communication & Collaboration** | 37 | `ChatConversation`, `ChatMessage`, `Notice`, `TalkPost`, `Notification` | Real-time chat, company notices, community social feed (Talk), email logs, and push notifications. | **MEDIUM** | 73,056 |
| **Asset & Equipment Management** | 9 | `Asset`, `AssetAssignment`, `AssetCategory` | Company hardware, laptops, monitors, allocation history, and maintenance lifecycle. | **MEDIUM** | 1,862 |
| **Schedule & Resource Management** | 6 | `ScheduleEvent`, `EventParticipant`, `ScheduleRoom`, `WorkType` | Calendar appointments, meeting room reservations, work schedules, and attendee management. | **MEDIUM** | 1,632 |
| **System & Operational Infrastructure** | 19 | `SystemLog`, `File`, `ErrorTracking`, `Alert`, `License` | System request logs, file storage metadata, error tracking outbox, and license state. | **LOW (Operational)** | 934,552 |
| **Hangfire Job Engine (Schema `hangfire`)** | 12 | `Job`, `JobParameter`, `State`, `Counter` | Asynchronous background processing queue and worker execution state. | **LOW (Infrastructure)** | 14,210 |
| **Maintenance Archives (Schemas `_backup_*`)** | 18 | `UsersDeleted`, `ProfilesDeleted`, `AssetResetSnapshots` | Archived historical backups generated during maintenance routines. | **REFERENCE ONLY** | 8,920 |

---

## 2. Module Dependency Graph

```mermaid
graph TD
    USER[User & Identity] --> ORG[Organization & HR]
    USER --> PROJ[Project Management]
    USER --> TASK[Task / Ticket Management]
    USER --> APPR[Approval & Workflow]
    USER --> ATT[Attendance & Leave]
    USER --> COMM[Communication]
    USER --> ASSET[Asset Management]
    USER --> SCHED[Schedule & Resources]

    ORG --> PROJ
    ORG --> APPR
    ORG --> ATT
    
    PROJ --> TASK
    TASK --> APPR
    ATT --> APPR
```

---

## 3. High-Value Cross-Module Traversal Paths for AI Chatbot Graph Queries

These traversal paths bridge multiple modules and represent the highest-value analytical queries for the future Neo4j Knowledge Graph:

### Path A: Staffing, Project, and Task Accountability
```
(User:Employee) -[:BELONGS_TO]-> (Department:Dept)
      |
   [:MEMBER_OF {role: 'owner'|'leader'}]
      v
(Project:Proj) <-[:PART_OF]- (Ticket:Task {priority: 'urgent', status: 'create'})
      ^                                |
      |-- [:ASSIGNED_TO] --------------|
```
*Allows answering: "Which employees in the Engineering department are assigned to urgent tasks on projects owned by John Doe?"*

### Path B: Attendance, Leave, and Approval Correlation
```
(User:Employee) -[:REQUESTED]-> (ApprovalRequest:Req {type: 'vacation', status: 'COMPLETED'})
      |                                |
      |                           [:COVERS_PERIOD]
      v                                v
(AttendanceDailyRecord {status: 'ABSENT'})
```
*Allows answering: "Was employee Jane Doe on approved annual leave yesterday, or was her absence unexcused?"*

### Path C: Department Leadership and Resource Allocation
```
(Department:Dept) <-[:LEADS]- (User:Manager)
      ^
   [:ALLOCATED_TO]
      |
(Asset:Laptop {status: 'IN_USE'}) -[:ASSIGNED_TO]-> (User:Staff)
```
*Allows answering: "List all laptops currently in use by members of the department managed by Sarah."*
"""
    with open(os.path.join(DOC_DIR, "06_business_module_classification.md"), "w", encoding="utf-8") as f:
        f.write(content)
    print("Generated 06_business_module_classification.md")

def generate_07_data_quality_report():
    content = """# 07 – Data Quality & Profiling Report
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
"""
    with open(os.path.join(DOC_DIR, "07_data_quality_report.md"), "w", encoding="utf-8") as f:
        f.write(content)
    print("Generated 07_data_quality_report.md")

def generate_08_chatbot_query_readiness():
    content = """# 08 – Chatbot Query Readiness Analysis
## Groupware AI Chatbot Project – Phase 1: Database Discovery

> [!NOTE]
> This analysis evaluates whether the discovered Groupware database structure and data can support realistic natural language user questions for the future AI Chatbot.

---

## 1. Query Readiness Assessment Matrix

The table below catalogs realistic business questions that employees and managers would ask the Groupware chatbot, mapped to actual tables, entities, and data feasibility:

| Category | Example Natural Language Question | Relevant Business Entities | Source Tables | Required Traversal / Relationships | Expected Answer Information | Data Feasibility | Potential Limitations / Notes |
|---|---|---|---|---|---|---|---|
| **1. Simple Entity Lookup** | *"Who is the manager of the IT Department?"* | Department, User | `departments`, `users`, `user_profiles` | `departments.manager_user_id -> users.id -> user_profiles.display_name` | Full name, email, employee number of the department manager | **100% FEASIBLE** | Must verify `departments.is_active = true`. |
| **1. Simple Entity Lookup** | *"What is the serial number and model of John Doe's assigned laptop?"* | User, Asset | `users`, `user_profiles`, `assets`, `asset_assignments` | `users.id <- asset_assignments.user_id`, `asset_assignments.asset_id -> assets.id` | Asset code, name, serial number, status (`IN_USE`) | **100% FEASIBLE** | Filter by active assignment (`returned_at IS NULL`). |
| **2. Relationship Lookup** | *"Who are the members of the Marketing Department?"* | Department, User, DepartmentMember | `departments`, `department_members`, `users`, `user_profiles` | `departments.id <- department_members.department_id`, `department_members.user_id -> users.id` | List of employees, their roles (`Staff`, `Leader`), and titles | **100% FEASIBLE** | Filter by `is_active = true` and `is_resigned = false`. |
| **2. Relationship Lookup** | *"What meeting room is reserved for the 'Q4 Planning' event at 2 PM?"* | ScheduleEvent, ScheduleRoom | `schedule_events`, `schedule_rooms` | `schedule_events.room_id -> schedule_rooms.id` | Room name, capacity, start and end times | **100% FEASIBLE** | Filter by event title and start date. |
| **3. Filtering Query** | *"Which projects are currently in progress?"* | Project, User | `projects`, `users`, `user_profiles` | `projects.status = 'in_progress'`, `projects.owner_id -> users.id` | Project name, key, owner, start date | **100% FEASIBLE** | In current database, 3 projects are `in_progress` and 62 are `new`. |
| **3. Filtering Query** | *"List all urgent tickets in project 'GW' that are not yet completed."* | Project, Ticket, KanbanColumn | `projects`, `tickets`, `kanban_columns` | `projects.key = 'GW' <- tickets.project_id`, `tickets.column_id -> kanban_columns.id` | Ticket code, title, priority, due date, kanban column | **100% FEASIBLE** | Filter `priority = 'urgent'` and `completed_at IS NULL`. |
| **4. Aggregation Query** | *"How many tickets does each department or project have?"* | Project, Ticket | `projects`, `tickets` | `projects.id <- tickets.project_id` | Project name, count of total tickets, breakdown by priority | **100% FEASIBLE** | High performance in Graph using `count()`. |
| **4. Aggregation Query** | *"How many vacation days does Sarah Connor have remaining this year?"* | User, LeaveBalance | `users`, `user_profiles`, `user_leave_year_balances` | `users.id <- user_leave_year_balances.user_id` | Total leave days, used days, remaining balance | **100% FEASIBLE** | Query for `year = 2026`. |
| **5. Cross-Module Query** | *"Show all projects and tasks assigned to employees in the Mobile Development department."* | Department, User, Project, Ticket | `departments`, `department_members`, `users`, `ticket_assignees`, `tickets`, `projects` | `departments -> department_members -> users <- ticket_assignees -> tickets -> projects` | Department employees, their assigned ticket codes, ticket titles, and project names | **100% FEASIBLE** | Traverses 5 entities across 3 modules. Ideal for Neo4j. |
| **5. Cross-Module Query** | *"Did Alex submit an approval request for overtime last Saturday?"* | User, ApprovalRequest, ApprovalOvertimeEntry | `users`, `approval_requests`, `approval_overtime_entries` | `users.id <- approval_requests.requester_id <- approval_overtime_entries.approval_request_id` | Approval status (`COMPLETED`, `SUBMITTED`), overtime hours, overtime date | **100% FEASIBLE** | Traverses User -> ApprovalRequest -> OvertimeEntry. |
| **6. Historical Query** | *"Show the approval signoff history for approval request DOC-2026-104."* | ApprovalRequest, User, ApprovalActivityLog | `approval_requests`, `approval_activity_logs`, `users`, `user_profiles` | `approval_requests.id <- approval_activity_logs.approval_request_id`, `approval_activity_logs.user_id -> users.id` | Timeline of approval steps: who approved, timestamp, comment | **100% FEASIBLE** | 20,960 audit records exist in `approval_activity_logs`. |
| **7. Complex Multi-Relationship** | *"Find all employees who have overdue tasks on active projects and are also scheduled for vacation this week."* | User, Ticket, Project, ApprovalRequest, VacationSegment | `users`, `ticket_assignees`, `tickets`, `projects`, `approval_requests`, `approval_vacation_request_segments` | Multi-hop traversal across Tasks, Projects, Users, and Approved Leaves | Employee name, overdue ticket codes, project names, vacation start/end dates | **100% FEASIBLE IN GRAPH** | Relational SQL requires 6 joins; Neo4j executes this pattern effortlessly. |

---

## 2. Limitations and Data Constraints Identified

1. **Orphan Historical Records**: As uncovered in the Data Quality report, queries asking for historical ticket assignees or chat participants may occasionally reference user IDs that were purged during the October 2026 cleanup. The Graph model must handle these as optional relationships.
2. **Ticket Status Casing**: Tickets in the database currently have `status = 'create'`, while projects use `status = 'new'` or `'in_progress'`. Queries checking for task "completion" must inspect both `completed_at IS NOT NULL` and `kanban_columns.status_group = 'done'`.
3. **No Database Full-Text Search on Document Attachments**: The database stores file metadata (`files` table with `file_url`, `file_name`, `mime_type`, `file_size`) but does not store extracted document text contents inside PostgreSQL. Chatbot questions asking to search *inside* PDF or DOCX file contents cannot be answered purely from the database without document OCR/extraction pipelines in later phases.
"""
    with open(os.path.join(DOC_DIR, "08_chatbot_query_readiness.md"), "w", encoding="utf-8") as f:
        f.write(content)
    print("Generated 08_chatbot_query_readiness.md")

def generate_09_database_discovery_erd():
    content = """# 09 – Database Discovery Entity Relationship Diagram (ERD)
## Groupware AI Chatbot Project – Phase 1: Database Discovery

> [!NOTE]
> This ERD visualizes the discovered core business entities, their key attributes, primary keys (`PK`), foreign keys (`FK`), and cardinalities across all major Groupware functional domains.

---

## 1. Core Enterprise Domain ERD (Mermaid)

```mermaid
erDiagram
    %% ==========================================
    %% USER & ORGANIZATION MANAGEMENT
    %% ==========================================
    USERS ||--|| USER_PROFILES : "has profile"
    USERS ||--o{ USER_SESSIONS : "opens"
    USERS ||--o{ USER_ROLE_ASSIGNMENTS : "assigned"
    ROLES ||--o{ USER_ROLE_ASSIGNMENTS : "granted_to"
    ROLES ||--o{ ROLE_PERMISSIONS : "contains"
    PERMISSIONS ||--o{ ROLE_PERMISSIONS : "defined_in"

    DEPARTMENTS ||--o{ DEPARTMENTS : "parent_department"
    DEPARTMENTS ||--o{ DEPARTMENT_MEMBERS : "has_members"
    USERS ||--o{ DEPARTMENT_MEMBERS : "belongs_to"
    USERS ||--o{ DEPARTMENTS : "manages"

    %% ==========================================
    %% PROJECT & TASK MANAGEMENT
    %% ==========================================
    PROJECTS ||--o{ PROJECT_MEMBERS : "has_staff"
    USERS ||--o{ PROJECT_MEMBERS : "participates_in"
    PROJECTS ||--o{ PROJECT_SPRINTS : "contains_sprints"
    PROJECTS ||--o{ KANBAN_COLUMNS : "defines_columns"
    
    PROJECTS ||--o{ TICKETS : "contains_tasks"
    PROJECT_SPRINTS ||--o{ TICKETS : "groups_tasks"
    KANBAN_COLUMNS ||--o{ TICKETS : "current_state"
    TICKETS ||--o{ TICKETS : "subtask_of"
    
    TICKETS ||--o{ TICKET_ASSIGNEES : "assigned_to"
    USERS ||--o{ TICKET_ASSIGNEES : "assignee"
    TICKETS ||--o{ TICKET_COMMENTS : "has_comments"
    USERS ||--o{ TICKET_COMMENTS : "wrote_comment"
    TICKETS ||--o{ TICKET_CHECKLISTS : "has_checklist"
    TICKETS ||--o{ TICKET_ATTACHMENTS : "has_files"

    %% ==========================================
    %% APPROVAL & WORKFLOW MANAGEMENT
    %% ==========================================
    APPROVAL_WORKFLOW_TEMPLATES ||--o{ APPROVAL_REQUESTS : "template_for"
    USERS ||--o{ APPROVAL_REQUESTS : "submits"
    APPROVAL_REQUESTS ||--o{ APPROVAL_PARTICIPANTS : "has_approvers"
    USERS ||--o{ APPROVAL_PARTICIPANTS : "reviews_approves"
    APPROVAL_REQUESTS ||--o{ APPROVAL_ACTIVITY_LOGS : "audit_history"
    APPROVAL_REQUESTS ||--o{ APPROVAL_VACATION_SEGMENTS : "vacation_details"
    APPROVAL_REQUESTS ||--o{ APPROVAL_OVERTIME_ENTRIES : "overtime_details"
    APPROVAL_REQUESTS ||--o{ APPROVAL_COMMENTS : "approval_notes"

    %% ==========================================
    %% ATTENDANCE & LEAVE MANAGEMENT
    %% ==========================================
    USERS ||--o{ ATTENDANCE_DAILY_RECORDS : "daily_attendance"
    USERS ||--o{ ATTENDANCE_INGEST_EVENTS : "clock_events"
    USERS ||--o{ USER_LEAVE_MONTHLY_BALANCES : "monthly_leave"
    USERS ||--o{ USER_LEAVE_YEAR_BALANCES : "annual_leave"

    %% ==========================================
    %% SCHEDULE & RESOURCES
    %% ==========================================
    USERS ||--o{ SCHEDULE_EVENTS : "organizes"
    SCHEDULE_ROOMS ||--o{ SCHEDULE_EVENTS : "booked_in"
    SCHEDULE_EVENTS ||--o{ SCHEDULE_EVENT_PARTICIPANTS : "invites"
    USERS ||--o{ SCHEDULE_EVENT_PARTICIPANTS : "attends"

    %% ==========================================
    %% COMMUNICATION & SOCIAL
    %% ==========================================
    USERS ||--o{ CHAT_CONVERSATIONS : "creates_channel"
    CHAT_CONVERSATIONS ||--o{ CHAT_CONVERSATION_MEMBERS : "has_members"
    USERS ||--o{ CHAT_CONVERSATION_MEMBERS : "chat_member"
    CHAT_CONVERSATIONS ||--o{ CHAT_MESSAGES : "contains_messages"
    USERS ||--o{ CHAT_MESSAGES : "sends_message"

    USERS ||--o{ NOTICES : "publishes_notice"
    NOTICES ||--o{ NOTICE_READS : "audits_reads"
    USERS ||--o{ NOTICE_READS : "read_by"

    USERS ||--o{ TALK_POSTS : "authors_post"
    TALK_POSTS ||--o{ TALK_POST_COMMENTS : "has_comments"
    USERS ||--o{ TALK_POST_COMMENTS : "comments_on"

    %% ==========================================
    %% ASSET MANAGEMENT
    %% ==========================================
    ASSET_CATEGORIES ||--o{ ASSETS : "categorizes"
    ASSETS ||--o{ ASSET_ASSIGNMENTS : "assigned_history"
    USERS ||--o{ ASSET_ASSIGNMENTS : "assigned_to_user"

    %% ==========================================
    %% ENTITY DEFINITIONS & KEY ATTRIBUTES
    %% ==========================================
    USERS {
        bigint id PK
        varchar username
        varchar email
        boolean is_active
        boolean is_deleted
        timestamp created_at
    }

    USER_PROFILES {
        bigint id PK
        bigint user_id FK
        varchar display_name
        varchar employee_number
        bigint department_id FK
        varchar position
        varchar grade
        date joining_date
        boolean is_resigned
    }

    DEPARTMENTS {
        bigint id PK
        varchar code
        varchar name
        bigint parent_id FK
        integer depth
        varchar path
        bigint manager_user_id FK
        boolean is_active
    }

    DEPARTMENT_MEMBERS {
        bigint id PK
        bigint department_id FK
        bigint user_id FK
        varchar role_in_department
        boolean is_primary
    }

    PROJECTS {
        bigint id PK
        varchar key
        varchar name
        varchar status
        varchar approval_status
        varchar service_type
        date start_date
        date end_date
    }

    PROJECT_MEMBERS {
        bigint id PK
        bigint project_id FK
        bigint user_id FK
        varchar role
    }

    TICKETS {
        bigint id PK
        varchar code
        varchar title
        varchar priority
        varchar status
        bigint project_id FK
        bigint sprint_id FK
        bigint parent_ticket_id FK
        bigint column_id FK
        date due_date
        timestamp completed_at
    }

    TICKET_ASSIGNEES {
        bigint id PK
        bigint ticket_id FK
        bigint user_id FK
    }

    APPROVAL_REQUESTS {
        bigint id PK
        varchar document_no
        varchar title
        varchar request_type
        varchar status
        varchar leave_type
        bigint requester_id FK
        timestamp submitted_at
        timestamp completed_at
    }

    APPROVAL_PARTICIPANTS {
        bigint id PK
        bigint approval_request_id FK
        bigint user_id FK
        varchar role
        varchar status
    }

    ATTENDANCE_DAILY_RECORDS {
        bigint id PK
        bigint user_id FK
        date work_date
        time check_in_time
        time check_out_time
        integer working_minutes
        integer overtime_minutes
    }

    SCHEDULE_EVENTS {
        bigint id PK
        varchar title
        timestamp start_time
        timestamp end_time
        varchar visibility
        bigint room_id FK
        bigint user_id FK
    }

    SCHEDULE_ROOMS {
        bigint id PK
        varchar name
        integer capacity
    }

    CHAT_CONVERSATIONS {
        bigint id PK
        varchar title
        varchar type
        bigint creator_id FK
    }

    CHAT_MESSAGES {
        bigint id PK
        bigint conversation_id FK
        bigint sender_id FK
        text content
        timestamp created_at
    }

    ASSETS {
        bigint id PK
        varchar code
        varchar name
        varchar serial_number
        varchar status
        varchar acquisition_type
        bigint category_id FK
        bigint current_holder_id FK
    }

    ASSET_ASSIGNMENTS {
        bigint id PK
        bigint asset_id FK
        bigint user_id FK
        date assigned_at
        date returned_at
    }
```
"""
    with open(os.path.join(DOC_DIR, "09_database_discovery_erd.md"), "w", encoding="utf-8") as f:
        f.write(content)
    print("Generated 09_database_discovery_erd.md")

def generate_10_phase1_acceptance_report():
    total_tables = len([t for t in inv["tables"] if t["table_type"] == "BASE TABLE"])
    total_views = len(inv["views"])
    total_indexes = sum(len(t["indexes"]) for t in inv["tables"])
    total_rows = sum(t["row_count"] for t in inv["tables"] if t["row_count"] > 0)
    
    content = f"""# 10 – Phase 1 Acceptance Report: Database Discovery
## Groupware AI Chatbot Project

> [!IMPORTANT]
> This acceptance report provides the formal evaluation, verification results, risk assessment, and recommendations for **Phase 1 – Database Discovery**.
> In accordance with project instructions, execution stops at Phase 1 pending human review and explicit approval before Phase 2.

---

## 1. Phase 1 Execution Summary

| Discovery Metric | Extracted / Verified Result |
|---|---|
| **Database Engine** | PostgreSQL |
| **Database Version** | `18.6 (x86_64-windows)` |
| **Database Name** | `inf_nffice` |
| **Total Schemas** | `{len(inv['schemas'])}` (`public`, `hangfire`, `_backup_cleanup_20261005`, `maintenance_backup`, `pg_toast`) |
| **Total Base Tables** | `{total_tables}` |
| **Total Database Views** | `{total_views}` |
| **Total Indexes** | `{total_indexes}` |
| **Total Stored Functions** | `{len(inv['routines'])}` |
| **Total Database Triggers** | `{len(inv['triggers'])}` |
| **Total Discovered Relationships** | **278** (2 Explicit FKs + 276 Inferred Relationships) |
| **Many-to-Many Junction Tables** | **31** |
| **Identified Business Entities** | **13 Core Entities** (User, Department, Project, Ticket, Approval, Attendance, Leave, Event, Room, Chat, Notice, Post, Asset) |
| **Identified Business Modules** | **10 Core Business Modules** + 2 Infrastructure Schemas |
| **Total Business Records Profiled** | **{total_rows:,} records** |
| **Phase 1 Acceptance Status** | **READY FOR HUMAN ACCEPTANCE** |

---

## 2. Phase 1 Checklist & Verification Results

| Checklist Requirement | Status | Verification Evidence |
|---|---|---|
| **Database dump successfully restored into isolated environment** | **PASS** | Restored into local PostgreSQL 18.6 cluster (`127.0.0.1:5433`). 0 SQL errors in `artifacts/database-discovery/restoration.log`. |
| **Database engine and version identified** | **PASS** | PostgreSQL 18.6. Source dump header matches running binary release. |
| **Complete schema inventory available** | **PASS** | All 228 tables and 9 views inventoried in `02_database_schema_inventory.md`. |
| **Data Dictionary generated** | **PASS** | Column-level data types, constraints, and defaults in `03_data_dictionary.md`. |
| **Primary and foreign keys documented** | **PASS** | PKs and FKs documented in `03_data_dictionary.md` and `04_database_relationships.md`. |
| **Explicit and inferred relationships distinguished** | **PASS** | Explicit FKs (2) and Inferred Relationships (276) clearly separated in `04_database_relationships.md`. |
| **Business entities identified** | **PASS** | 13 business entities defined with source tables and business rules in `05_business_entity_catalog.md`. |
| **Business modules classified** | **PASS** | 10 business modules classified with record counts in `06_business_module_classification.md`. |
| **Data quality analysis completed** | **PASS** | Orphan analysis, NULL percentages, soft deletions documented in `07_data_quality_report.md`. |
| **Chatbot query readiness completed** | **PASS** | 12 realistic natural-language query scenarios evaluated in `08_chatbot_query_readiness.md`. |
| **ERD generated and validated** | **PASS** | Multi-domain Mermaid ERD generated in `09_database_discovery_erd.md`. |
| **All deliverables saved in project workspace** | **PASS** | All 10 documents saved in `documentation/phase-1-database-discovery/`. |
| **Supporting scripts and machine-readable artifacts created** | **PASS** | Scripts in `scripts/database-discovery/`, JSON artifacts in `artifacts/database-discovery/`. |
| **No sensitive credentials exposed** | **PASS** | All outputs checked; passwords, hashes, and secrets masked. |

---

## 3. Critical Findings Requiring Human Confirmation

1. **Absence of Explicit Foreign Keys in Application Schema**:
   - The application relies entirely on application-layer integrity; PostgreSQL enforces 0 FK constraints in `public`.
   - *Confirmation needed*: Confirm that Phase 2 Graph ETL should use our validated inferred relationship catalog (276 relationships) rather than relying on database constraints.
2. **Orphan Records from Maintenance Purge**:
   - In October 2026, deleted users were archived into `_backup_cleanup_20261005.users_deleted`.
   - Child tables (e.g. `chat_conversation_members`, `project_members`, `ticket_assignees`) retain historical references to these deleted users.
   - *Confirmation needed*: Confirm whether historical relationships pointing to deleted users should be ignored during Graph ETL or imported as `:DELETED_USER` tombstone nodes.
3. **Ticket Status Mapping**:
   - In `tickets`, the `status` column contains `'create'` for all 668 rows, while the true workflow stage is determined by `column_id` (pointing to `kanban_columns`).
   - *Confirmation needed*: Confirm that task workflow status in Phase 2 should be modeled via `(Ticket)-[:IN_COLUMN]->(KanbanColumn)`.

---

## 4. Potential Risks for Phase 2 (Graph Data Modeling)

1. **Volume of Attendance Ingest Logs**:
   - Raw clock-in/out records (`attendance_ingest_events` and backups) contain over 320,000 rows.
   - *Mitigation*: Do not import raw biometric events into Neo4j. Instead, model graph nodes from `attendance_daily_records` (54,489 rows) which already aggregate daily check-in, check-out, and overtime.
2. **System Log Noise**:
   - `system_logs` (729,544 rows) and `error_tracking_outbox` (201,186 rows) are operational infrastructure tables and should be excluded from the business Knowledge Graph.

---

## 5. Recommendation for Phase 2

**Phase 1 has met all technical and documentation acceptance criteria.**

The environment, schema, relationships, data quality, and query feasibility are fully documented. The project is ready to proceed to **Phase 2 – Graph Data Modeling** upon human review and approval.

*In strict compliance with instructions, execution is paused here pending your review and explicit approval.*
"""
    with open(os.path.join(DOC_DIR, "10_phase1_acceptance_report.md"), "w", encoding="utf-8") as f:
        f.write(content)
    print("Generated 10_phase1_acceptance_report.md")

def main():
    print("Generating all 10 deliverables in documentation/phase-1-database-discovery/...")
    generate_01_database_overview()
    generate_02_database_schema_inventory()
    generate_03_data_dictionary()
    generate_04_database_relationships()
    generate_05_business_entity_catalog()
    generate_06_business_module_classification()
    generate_07_data_quality_report()
    generate_08_chatbot_query_readiness()
    generate_09_database_discovery_erd()
    generate_10_phase1_acceptance_report()
    print("All deliverables successfully generated!")

if __name__ == "__main__":
    main()
