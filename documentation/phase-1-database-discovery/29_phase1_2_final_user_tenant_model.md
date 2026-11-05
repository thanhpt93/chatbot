# 29 – Phase 1.2 / 1.2.1 / 1.2.2 Final User, Tenant, Dual-Scope Audience & Fulltext Security Model
## Groupware AI Chatbot Project – Canonical Identity, Multi-Tenant & Authorization Architecture

> [!IMPORTANT]
> **Work Package 1 Objective (Updated in Phase 1.2.1 & Phase 1.2.2)**:
> This document establishes **one canonical User and Tenant model** across the Graph Data Model, Source-to-Graph Mapping, Chatbot Cypher Queries, Neo4j Indexes, and Evidence Validation Matrix. It supersedes `12_tenant_and_authorization_model.md`, `13_tenant_and_authorization_discovery.md`, and `22_phase1_1_tenant_authorization_finalization.md`, and incorporates all **Phase 1.2.1 (`DEFECT 02`, `DEFECT 04`, `DEFECT 05`, `DEFECT 06`, `DEFECT 09`)** and **Phase 1.2.2 (`CRITICAL-01`, `CRITICAL-02`, `CRITICAL-03`, `CRITICAL-04`, `HIGH-05`)** technical and security corrections.

---

## 1. Physical PostgreSQL Schema Truth (Verified from `schema_inventory.json` & Data Profiling)

### 1.1 Identity & Tenant Tables (`public` schema)

| Physical Table | Physical Rows | Primary Key | Tenant Key Column | Key Uniqueness / Check Constraints | Verified Physical Columns |
|---|---:|---|---|---|---|
| `public.tenants` | **1** | `id` (`int8`) | Self (`id`) | `tenants_pkey (id)`<br>`ux_tenants_tenant_key (lower(tenant_key))` | `id`, `tenant_key` (`varchar` NOT NULL = `'default'`), `name` (`'Default Tenant'`), `status` (`'active'`), `isolation_mode` (`'shared_db'`), `is_default` (`true`), `is_deleted` (`false`), `created_at`, `updated_at` (**Note: There is NO `code` column on `public.tenants`**) |
| `public.users` | **360** | `id` (`int4`) | **NONE** (Global Account) | `users_pkey (id)`<br>`users_username_key (username)`<br>`users_email_key (email)` | `id`, `username`, `email`, `password_hash`, `is_active` (`220 true`, `140 false`), `is_deleted` (`353 false`, `7 true`), `email_verified`, `created_at`, `updated_at`, `deleted_at`, `deleted_by` |
| `public.tenant_user_memberships` | **360** | `id` (`int8`) | `tenant_id` (`int8` NOT NULL) | `ux_tenant_user_memberships_active_pair (tenant_id, user_id) WHERE is_deleted = false` | `id`, `tenant_id` (`100% = 1`), `user_id` (`360 distinct users`), `status` (`360 'active'`), `is_default` (`360 true`), `joined_at`, `invited_by`, `is_deleted` (`360 false`), `created_at`, `updated_at` |
| `public.user_profiles` | **360** | `id` (`int4`) | `tenant_id` (`int8` NOT NULL) | `ux_user_profiles_tenant_user (tenant_id, user_id)` | `id`, `user_id` (`int4` NOT NULL), `tenant_id` (`int8` NOT NULL = `1`), `display_name`, `employee_number` (`69 non-null`, `291 null` — **NO UNIQUE CONSTRAINT**), `department_id` (`297 non-null`, `63 null`), `position`, `grade`, `duty`, `is_resigned` (`140 true`, `220 false`), `attendance_mode`, `birth_date`, `mobile_phone`, `address`, `tax_code`, `created_at`, `updated_at` |
| `public.departments` | **103** | `id` (`int4`) | `tenant_id` (`int8` NOT NULL) | `departments_pkey (id)` | `id`, `tenant_id` (`100% = 1`), `code`, `name`, `parent_id` (`50 non-null`), `manager_user_id` (`21 non-null` across `18 distinct users`), `depth`, `path`, `department_type`, `is_active` (`27 true`, `76 false`), `effective_from`, `effective_to`, `created_at`, `updated_at` |
| `public.department_members` | **359** | `id` (`int8`) | `tenant_id` (`int8` NOT NULL) | `department_members_pkey (id)` | `id`, `tenant_id` (`100% = 1`), `department_id` (`25 distinct depts`), `user_id` (`358 distinct users`), `role_in_department`, `is_primary`, `effective_from` (`date` NOT NULL), `effective_to` (`date` nullable), `created_at`, `updated_at` (**Note: There are NO `joined_at` or `left_at` columns**) |

### 1.2 Historical / Purged User Context (`_backup_cleanup_20261005` schema)
- On `2026-10-05`, a database cleanup archived **21 deleted accounts** into `_backup_cleanup_20261005.users_deleted` (`21` rows), `_backup_cleanup_20261005.user_profiles_deleted` (`21` rows), and `_backup_cleanup_20261005.tenant_user_memberships_deleted` (`21` rows, all with `tenant_id = 1`).
- Because operational tables (`projects`, `project_members`, `tickets`, `ticket_assignees`, `approval_requests`, `approval_participants`, `schedule_events`, `schedule_event_participants`, `chat_conversations`, `chat_conversation_members`, `files`) do **not** have physical foreign keys enforcing cascading deletes against `public.users`, several historical operational rows still reference those 21 archived `user_id` values (`2` in `projects.created_by_user_id`, `18` in `project_members.user_id`, `2` in `tickets.created_by_user_id`, `13` in `ticket_assignees.user_id`, `1` in `approval_requests.created_by_user_id`, `4` in `schedule_events.user_id`, `12` in `chat_conversations.created_by_user_id`).

---

## 2. Canonical User & Tenant Graph Architecture Decision

### 2.1 Why `:User` MUST NOT Carry a Scalar `tenant_id` Property
1. `public.users` has **no `tenant_id` column**; it is a global authentication account table (`id`, `username`, `email`).
2. `public.tenant_user_memberships` models a **many-to-many (`N:M`)** relationship between `users` and `tenants` (`ux_tenant_user_memberships_active_pair (tenant_id, user_id)`).
3. `public.user_profiles` is **not** `1:1` with `users`; its unique index is `ux_user_profiles_tenant_user (tenant_id, user_id)`, meaning a user can hold one profile per tenant.
4. Putting a scalar `u.tenant_id` property on `:User` would overwrite tenant ownership whenever a user belongs to more than one tenant, and caused the Phase 1.1 contradiction where `Doc 21` and `Doc 24` disagreed on whether `:User` had `tenant_id`.

### 2.2 Canonical Graph Pattern: `(:User)-[:MEMBER_OF]->(:Tenant)`
- **`:Tenant` (`NM-01`)**:
  - Uniqueness key: `t.id` (`int8` from `public.tenants.id`).
  - Business key: `t.tenant_key` (`varchar` from `public.tenants.tenant_key`, **never** `t.code`).
- **`:User` (`NM-02`)**:
  - Uniqueness key: `u.id` (`int4` from `public.users.id`).
  - Properties on `:User`: `id`, `username`, `email`, `display_name` (fallback from default profile `m.is_default = true`), `is_active`, `is_deleted`, `created_at`, `updated_at`, `last_synced_at`.
  - **Strict Prohibition**: `:User` **NEVER** has a `tenant_id` property, and `idx_user_tenant` is **prohibited**.
- **`(:User)-[m:MEMBER_OF]->(:Tenant)` (`RM-01`)**:
  - Extracted from `public.tenant_user_memberships m` `LEFT JOIN public.user_profiles up ON up.user_id = m.user_id AND up.tenant_id = m.tenant_id`.
  - Carries both membership lifecycle state (`id`, `tenant_id`, `status`, `is_default`, `joined_at`, `is_deleted`) and tenant-scoped profile attributes (`display_name`, `employee_number`, `department_id`, `position`, `grade`, `duty`, `is_resigned`, `attendance_mode`, `updated_at`, `last_synced_at`).

### 2.3 Canonical Tenant Membership Lifecycle Semantics: Active vs. Historical (`CRITICAL-01` & `CRITICAL-02`)
Across the entire ETL and Query architecture, membership predicates on `public.tenant_user_memberships` and `[:MEMBER_OF]` are governed by two distinct, explicitly defined lifecycle tiers:

| Lifecycle Rule ID | Predicate Definition | Exact Where / Match Clause | Mandatory Usage Scope | Architectural Justification |
|---|---|---|---|---|
| **Rule `MEM-ACTIVE` (Strict Current Active Membership)** | User account is active/non-deleted AND tenant membership is currently `'active'` and non-deleted. | **SQL**: `m.status = 'active' AND m.is_deleted = false AND COALESCE(u.is_deleted, false) = false`<br>**Cypher**: `(u:User {is_deleted: false})-[:MEMBER_OF {status: 'active', is_deleted: false}]->(t:Tenant {id: $tenant_id, is_deleted: false})` | 1. **All Runtime Chatbot Queries (`Q01`–`Q14`)** caller preambles & directory lookups.<br>2. **`NM-22` (`:AttendanceRecord`) & `RM-37` (`[:HAS_ATTENDANCE]`)** 6-step resolution (`CRITICAL-01`).<br>3. **`RM-04` (`[:MANAGES]`)** department manager edge & **`Q01`** manager projection (`HIGH-05`).<br>4. **`RM-13` (`[:ASSIGNED_TO]` on `:Ticket`)** and **`RM-27` (`[:INCLUDES_USER]` on `:Audience`)**. | Current operational actions, biometric attendance resolution, active managerial authority, and live query access require an active, non-suspended, non-deleted tenant membership. |
| **Rule `MEM-HISTORICAL-UNAMBIGUOUS` (Historical Single-Tenant Creator / Owner Derivation)** | User has (or historically had in `_backup_cleanup_20261005.tenant_user_memberships_deleted`) non-deleted membership(s) in **exactly one** distinct tenant (`COUNT(DISTINCT tenant_id) = 1`). | **SQL**: `SELECT user_id, min(tenant_id) AS tenant_id FROM (SELECT user_id, tenant_id FROM public.tenant_user_memberships WHERE is_deleted = false UNION SELECT user_id, tenant_id FROM _backup_cleanup_20261005.tenant_user_memberships_deleted) u GROUP BY user_id HAVING count(DISTINCT tenant_id) = 1` | **Historical Business Artifact Ownership**:<br>`NM-06` (`:Project`), `NM-07` (`:Ticket`), `NM-08` (`:Sprint`), `NM-09` (`:KanbanColumn`), `NM-10` (`:ApprovalRequest`), `NM-12` (`:ScheduleEvent`), `NM-14` (`:Notice`), `NM-15` (`:Post`), `NM-16` (`:Asset`), `NM-18` (`:FileMetadata`), `NM-19` (`:ChatConversation`), `NM-20` (`:Audience` custom owner), `NM-21` (`:LeaveBalance` with `user_profiles` match, `CRITICAL-02`), `NM-24` (`:Tag`), `NM-25` (`:KnowledgeDocument`). | When an employee resigns or becomes `inactive`, the projects, tickets, approvals, notices, posts, files, and historical annual leave balances they created or accrued in their tenant remain corporate records of that tenant and must **not** be orphaned or deleted. |

---

## 3. Deterministic Tenant Ownership Rules for All 27 Evaluated Node Labels

Every graph node label falls into one of **four explicit tenant ownership categories**:

| Ownership Category | Node Labels | Tenant Rule & Enforcement |
|---|---|---|
| **Category A: Root Tenant Entity (`1` label)** | `:Tenant` (`NM-01`) | Root tenant container identified by `t.id` (`int8`). |
| **Category B: Direct Physical `tenant_id` Column (`3` labels)** | `:Department` (`NM-03`), `:Role` (`NM-04`), `:ContractHistory` (`NM-23`) | Source table has a physical `tenant_id` (`int8` NOT NULL) column. Synced directly to `node.tenant_id`. |
| **Category C: Transitive Deterministic `tenant_id` (`15` Approved MVP labels + `2` Future)** | `:Project` (`NM-06`), `:Ticket` (`NM-07`), `:Sprint` (`NM-08`), `:KanbanColumn` (`NM-09`), `:ApprovalRequest` (`NM-10`), `:ScheduleEvent` (`NM-12`), `:Notice` (`NM-14`), `:Post` (`NM-15`), `:Asset` (`NM-16`), `:FileMetadata` (`NM-18`), `:ChatConversation` (`NM-19`), `:LeaveBalance` (`NM-21`), `:AttendanceRecord` (`NM-22`), `:Tag` (`NM-24`), `:KnowledgeDocument` (`NM-25`), plus Future `:Topic` (`ND-26`), `:BusinessConcept` (`ND-27`) | Source table has no physical `tenant_id` column. ETL deterministically derives `tenant_id` from parent project, department, or unambiguous user tenant membership (`COUNT(DISTINCT tenant_id) = 1`). Any row with `0` or `>1` candidate tenants is **quarantined** to `etl_quarantine_log` and never loaded into Neo4j. |
| **Category D: Dual-Scope Ownership (`1` label — DEFECT 04 Resolution)** | `:Audience` (`NM-20`) | **Dual-Scope Model**:<br>1. **Global System Audience (`is_system = true`)**: `a.tenant_id = NULL` (`1` row: `id = 1`, `code = 'ALL_EMPLOYEES'`, `audience_type = 'ALL'`, `owner_user_id = NULL`). Never assigned a default `tenant_id`, and **never** allowed to have `[:INCLUDES_DEPARTMENT]` or `[:INCLUDES_USER]` edges.<br>2. **Custom Tenant-Scoped Audience (`is_system = false`)**: `a.tenant_id = <int8>` (`NOT NULL`, `115` rows), derived from `owner_user_id` and verified against `audience_department_members` and `audience_user_members`. |
| **Category E: Global / Pooled Catalog Entities (`4` Approved MVP labels + `1` Blocked)** | `:User` (`NM-02`), `:Permission` (`NM-05`), `:ScheduleRoom` (`NM-13`), `:AssetCategory` (`NM-17`), plus Blocked `:WorkflowTemplate` (`ND-11`) | **Never** carry a `tenant_id` property on the node. Isolated at query time via `[:MEMBER_OF]` (`:User`), `[:INCLUDES_PERMISSION]` / `[:DIRECT_PERMISSION]` (`:Permission`), `:ScheduleEvent.tenant_id` (`:ScheduleRoom`), and `:Asset.tenant_id` (`:AssetCategory`). |

### 3.1 Deterministic 6-Step Resolution Contract for `:AttendanceRecord` (`NM-22` & `RM-37` — DEFECT 02 & CRITICAL-01 Resolution)

`public.attendance_daily_records` (`54,489` rows) has a nullable `user_id` (`24,764` non-null; `29,725` `NULL`) and a non-null `employee_code` (`665` distinct values). Meanwhile, `public.user_profiles.employee_number` (`69` non-null values) has **no physical `UNIQUE` constraint** in PostgreSQL.

To prevent duplicate/ambiguous joins (`OR (a.user_id IS NULL AND up.employee_number = a.employee_code)`), cross-tenant attribution, inactive/suspended membership leakage (`CRITICAL-01`), or unlinked orphan `:AttendanceRecord` nodes in Neo4j, both `NM-22` (`Doc 30`) and `RM-37` (`Doc 31`) enforce the following **6-Step Deterministic Resolution Hierarchy** using **Rule `MEM-ACTIVE` (`m.status = 'active' AND m.is_deleted = false AND u.is_deleted = false`)**:

| Step | Condition Evaluated on `attendance_daily_records a` | Classification Status (`resolution_status`) | Current Snapshot Row Count | ETL Action (`Doc 30`, `Doc 31`, `Doc 33`) |
|---:|---|---|---:|---|
| **Step 1** | `a.user_id IS NOT NULL`, but `a.user_id` does not exist in `public.users.id` (or `u.is_deleted = true`) | **`INVALID_SOURCE_REFERENCE`** | `0` | **Quarantine** to `etl_quarantine_log` (`reason = 'INVALID_SOURCE_REFERENCE'`). Do **not** create `:AttendanceRecord` node. |
| **Step 2** | `a.user_id IS NOT NULL`, exists in `public.users` (`u.is_deleted = false`), and maps to **exactly one** `tenant_id` in `user_profiles` joined with active `tenant_user_memberships` (`m.status = 'active' AND m.is_deleted = false`) | **`RESOLVED_BY_USER_ID`** | **`24,764`** | **Load** `:AttendanceRecord` (`ar.user_id = a.user_id`, `ar.tenant_id = vut.tenant_id`, `ar.resolution_status = 'RESOLVED_BY_USER_ID'`) and create `(:User)-[:HAS_ATTENDANCE]->(:AttendanceRecord)`. |
| **Step 3** | `a.user_id IS NOT NULL`, exists in `public.users`, but has `0` active memberships (`m.status <> 'active'` or `m.is_deleted = true`) or `>1` distinct `tenant_id` in `user_profiles` / `tenant_user_memberships` | **`INVALID_TENANT`** | `0` | **Quarantine** to `etl_quarantine_log` (`reason = 'INVALID_TENANT'`). Do **not** create `:AttendanceRecord` node. |
| **Step 4** | `a.user_id IS NULL`, and `a.employee_code` matches **0** rows in `public.user_profiles.employee_number` (with active membership `m.status = 'active' AND m.is_deleted = false`) | **`UNRESOLVED`** | **`29,725`** | **Quarantine** to `etl_quarantine_log` (`reason = 'UNRESOLVED'`). Do **not** create unlinked `:AttendanceRecord` node in Neo4j. |
| **Step 5** | `a.user_id IS NULL`, and `a.employee_code` matches `>1` distinct `user_id` or `>1` distinct `tenant_id` in `public.user_profiles` (`user_cnt > 1 OR tenant_cnt > 1`) | **`AMBIGUOUS`** | `0` | **Quarantine** to `etl_quarantine_log` (`reason = 'AMBIGUOUS'`). Do **not** create `:AttendanceRecord` node. |
| **Step 6** | `a.user_id IS NULL`, and `a.employee_code` matches **exactly 1** `user_id` (`u.is_deleted = false`) and **exactly 1** `tenant_id` in `public.user_profiles` (`user_cnt = 1 AND tenant_cnt = 1`) with an active `tenant_user_memberships` row (`m.status = 'active' AND m.is_deleted = false`) | **`RESOLVED_BY_EMPLOYEE_NUMBER`** | `0` (on current snapshot; supported dynamically) | **Load** `:AttendanceRecord` (`ar.user_id = enr.resolved_user_id`, `ar.tenant_id = enr.resolved_tenant_id`, `ar.resolution_status = 'RESOLVED_BY_EMPLOYEE_NUMBER'`) and create `(:User)-[:HAS_ATTENDANCE]->(:AttendanceRecord)`. |

#### Mandatory Membership Lifecycle Test Cases for Attendance Resolution (`Cases A–E` — `CRITICAL-01`)

| Test Case ID | `tenant_user_memberships.status` | `tenant_user_memberships.is_deleted` | Eligibility in `valid_user_tenant` & `emp_number_resolution` CTEs | Resulting `resolution_status` | Graph Load Outcome |
|---|---|---|---|---|---|
| **`Case A`** | `'active'` | `false` | **Eligible (`TRUE`)** | `RESOLVED_BY_USER_ID` (if `a.user_id IS NOT NULL`) or `RESOLVED_BY_EMPLOYEE_NUMBER` (if unambiguous `employee_code`) | **Loaded** into `:AttendanceRecord` (`NM-22`) and linked via `[:HAS_ATTENDANCE]` (`RM-37`). |
| **`Case B`** | `'inactive'` | `false` | **Excluded (`FALSE`)** | `INVALID_TENANT` (when `a.user_id IS NOT NULL`) or `UNRESOLVED` (when `a.user_id IS NULL`) | **Rejected & Quarantined** (`0` nodes/edges created). |
| **`Case C`** | `'suspended'` | `false` | **Excluded (`FALSE`)** | `INVALID_TENANT` (when `a.user_id IS NOT NULL`) or `UNRESOLVED` (when `a.user_id IS NULL`) | **Rejected & Quarantined** (`0` nodes/edges created). |
| **`Case D`** | `'active'` | `true` | **Excluded (`FALSE`)** | `INVALID_TENANT` (when `a.user_id IS NOT NULL`) or `UNRESOLVED` (when `a.user_id IS NULL`) | **Rejected & Quarantined** (`0` nodes/edges created). |
| **`Case E`** | `'inactive'` | `true` | **Excluded (`FALSE`)** | `INVALID_TENANT` (when `a.user_id IS NOT NULL`) or `UNRESOLVED` (when `a.user_id IS NULL`) | **Rejected & Quarantined** (`0` nodes/edges created). |

> [!WARNING]
> **Hard Architectural Invariant (`DEFECT 02` & `CRITICAL-01`)**:
> Neo4j **MUST NEVER** contain unlinked `:AttendanceRecord` nodes or attendance nodes resolved through non-active (`status <> 'active'`) or soft-deleted (`is_deleted = true`) tenant memberships. The count of `:AttendanceRecord` nodes in Neo4j must always equal the count of `(:User)-[:HAS_ATTENDANCE]->(:AttendanceRecord)` relationships (`24,764` on the current snapshot).

### 3.2 Deterministic Tenant Derivation Contract for `:LeaveBalance` (`NM-21` & `RM-36` — `CRITICAL-02` Resolution)

1. **Physical Schema Reality**:
   - `public.user_leave_year_balances` (`353` rows, PK `id` `int8`) has unique constraint `uq_user_leave_year_balances_user_year (user_id, year)` and **no `tenant_id` column**.
   - `public.user_leave_monthly_balances` (`4,238` rows, PK `id` `int8`) has unique constraint `uq_user_leave_monthly_balances_user_year_month (user_id, year, month)` and **no `tenant_id` column**.
   - `public.user_profiles` (`360` rows) has `tenant_id` (`int8` NOT NULL) with unique index `ux_user_profiles_tenant_user (tenant_id, user_id)`.
   - `public.tenant_user_memberships` (`360` rows) has `tenant_id` (`int8` NOT NULL), `user_id` (`int4` NOT NULL), `status` (`varchar`), and `is_deleted` (`bool`).
2. **Active vs. Historical Leave Balance Retention Rule (`CRITICAL-02`)**:
   - Annual leave balances (`user_leave_year_balances`) are statutory HR financial/entitlement records for a given `(user_id, year)` (`2026`). Even when an employee transitions to `is_resigned = true` (`140` users in `user_profiles`) or `m.status IN ('inactive', 'suspended')`, their annual leave ledger for that year remains an auditable HR record of that tenant.
   - However, because `user_leave_year_balances` is keyed by `(user_id, year)` without `tenant_id`, tenant derivation is only deterministic if the user belongs to **exactly one** non-deleted tenant across `tenant_user_memberships` (`m.is_deleted = false AND m.status IN ('active', 'inactive', 'suspended')`) corroborated by `user_profiles` (`up.tenant_id = m.tenant_id`).
   - Therefore, `NM-21` (`Doc 30`) and `RM-36` (`Doc 31`) derive `tenant_id` via `user_unambiguous_leave_tenant`:
     - **Case 1 (Single Active Membership — `m.status = 'active' AND m.is_deleted = false`, `count(DISTINCT m.tenant_id) = 1`)**: Loaded into `:LeaveBalance` with `lb.tenant_id = m.tenant_id` (`353/353` rows on current snapshot). Accessible to both self-service (`Q11`) and HR Admin.
     - **Case 2 (Single Historical Non-Deleted Membership — `m.status IN ('inactive', 'suspended') AND m.is_deleted = false`, `count(DISTINCT m.tenant_id) = 1`)**: Loaded into `:LeaveBalance` with `lb.tenant_id = m.tenant_id` for HR Admin audit queries; blocked from self-service in `Q11` because `Q11` requires `[:MEMBER_OF {status: 'active', is_deleted: false}]` for the caller/target user.
     - **Case 3 (Multi-Tenant User — `count(DISTINCT m.tenant_id) > 1`)**: **Quarantined** to `etl_quarantine_log` with `reason = 'AMBIGUOUS_TENANT'` (`0` rows on current snapshot). Never duplicated across tenants or assigned arbitrarily to a default tenant.
     - **Case 4 (No Valid Membership / Soft-Deleted Membership — `count(DISTINCT m.tenant_id) = 0` or `m.is_deleted = true` only)**: **Quarantined** to `etl_quarantine_log` with `reason = 'INVALID_TENANT'`.
3. **Source Schema Confirmation Item (`SD-07` — `NEEDS SOURCE CONFIRMATION`)**:
   - Because `uq_user_leave_year_balances_user_year (user_id, year)` and `uq_user_leave_monthly_balances_user_year_month (user_id, year, month)` lack `tenant_id`, a user simultaneously employed in two tenants in the same calendar year cannot store two separate annual leave balances in PostgreSQL. This is formally logged as Stakeholder Decision **`SD-07` (`NEEDS SOURCE CONFIRMATION`)**: before onboarding multi-tenant shared employees, add `tenant_id BIGINT NOT NULL` to `user_leave_year_balances` and `user_leave_monthly_balances`.

### 3.3 Authoritative RBAC & Permission Precedence (`AC-05A` Verified vs `AC-05B` External Backend)

1. **`AC-05A` — PostgreSQL Stored Authorization Routine (`EXECUTED` & `RESULT VALIDATED` -> `PASS`)**:
   - Extracted from `pg_proc` (`artifacts/phase1_2/auth_routines.txt`): `public.check_user_permission(p_tenant_id bigint, p_user_id bigint, p_permission_code character varying) RETURNS boolean`.
   - Exact 4-Step Evaluation Order:
     1. **Active Tenant Membership Gate**: Checks `EXISTS (SELECT 1 FROM public.tenant_user_memberships m WHERE m.tenant_id = p_tenant_id AND m.user_id = p_user_id AND m.status = 'active' AND m.is_deleted = false)`. If `false`, immediately returns `FALSE`.
     2. **Permission Code Lookup**: Looks up `v_permission_id` from `public.permissions WHERE lower(code) = lower(trim(p_permission_code))`. If `NULL`, returns `FALSE`.
     3. **Direct User Permission Override (`user_permissions` — Highest Precedence)**: Checks `SELECT up.is_granted FROM public.user_permissions up WHERE up.tenant_id = p_tenant_id AND up.user_id = p_user_id AND up.permission_id = v_permission_id`. If a row exists (`19` grant rows, `32` deny rows in current DB), returns `up.is_granted` immediately (a direct `false` overrides all role grants!).
     4. **Role Permission Aggregation (`user_role_assignments` + `roles` + `role_permissions`)**: Computes `COALESCE(BOOL_OR(rp.is_granted), FALSE)` across all active roles (`r.is_active = true AND r.tenant_id = p_tenant_id`).
2. **`AC-05B` — External Application Backend Source Code Inspection (`NOT VERIFIED`)**:
   - The current workspace (`C:\Project\chatbot`) contains only the database discovery artifacts, documentation, and validation scripts. The external C#/.NET Groupware backend application source code repository is not present in this workspace. Therefore, while database-level RBAC logic (`AC-05A`) is 100% verified (`PASS`), external application controller/middleware inspection (`AC-05B`) is strictly classified as **`NOT VERIFIED`** (`MISSING EVIDENCE`) until the backend code repository is mounted in Phase 2.

---

## 4. Dual-Scope `:Audience` & Fulltext Search Security Architecture (`DEFECT 04` & `DEFECT 05`)

### 4.1 Dual-Scope `:Audience` (`NM-20`) Security Contract (`DEFECT 04`)

In `public.audiences` (`116` rows):
- **Row `id = 1`**: `code = 'ALL_EMPLOYEES'`, `name = 'All employees'`, `audience_type = 'ALL'`, `is_system = true`, `owner_user_id = NULL`, `is_active = true`. It has **`0` rows** in `audience_department_members` and **`0` rows** in `audience_user_members`.
- **Rows `id = 2..116` (`115` rows)**: `is_system = false`, `owner_user_id IS NOT NULL` (`100%` belong to `tenant_id = 1`), linked to `100` rows in `audience_department_members` (`28` depts, all `tenant_id = 1`) and `39` rows in `audience_user_members` (`15` users, all `tenant_id = 1`).

**Mandatory Dual-Scope Rules**:
1. **System Audience (`a.is_system = true`)**:
   - Stored in Neo4j with `a.is_system = true` and **`a.tenant_id = null`**.
   - **Never** assigned a default tenant (`tenant_id = 1` is forbidden on `is_system = true`).
   - **Never** permitted to have `(:Audience)-[:INCLUDES_DEPARTMENT]->(:Department)` (`RM-26`) or `(:Audience)-[:INCLUDES_USER]->(:User)` (`RM-27`) edges.
   - When a `:Notice` (`n.tenant_id = $tenant_id`) or `:Post` (`p.tenant_id = $tenant_id`) targets a system audience (`a.is_system = true AND a.tenant_id IS NULL AND a.audience_type = 'ALL'`), visibility is restricted strictly to active members of `n.tenant_id` / `p.tenant_id` (`MATCH (req:User)-[:MEMBER_OF {status: 'active', is_deleted: false}]->(:Tenant {id: $tenant_id})` where `n.tenant_id = $tenant_id`).
2. **Custom Audience (`a.is_system = false`)**:
   - Stored in Neo4j with `a.is_system = false` and **`a.tenant_id = <int8>` (`NOT NULL`)**.
   - ETL (`NM-20`, `RM-25`, `RM-26`, `RM-27`, `RM-29`) verifies that `owner_user_id`, all `audience_department_members`, all `audience_user_members`, and any targeting `:Notice` or `:Post` share the **exact same `tenant_id`**.
   - Any custom audience with `tenant_id IS NULL` or cross-tenant members is **quarantined** to `etl_quarantine_log`.

### 4.2 Fulltext Search Tenant Security Contract (`DEFECT 05`)

Neo4j Fulltext (`FULLTEXT`) indexes (`db.index.fulltext.queryNodes`) evaluate Lucene text matching globally across all nodes carrying the indexed label before Cypher `WHERE` predicates execute. Because our graph contains **two distinct node scoping models** inside fulltext indexes, we enforce **two separate mandatory Cypher post-filter templates**:

#### Template FTS-A: Tenant-Scoped Domain Fulltext Indexes (`fts_work_items`, `fts_communications`, `fts_files`)
- **Applies to**:
  - `fts_work_items` (`:Project`, `:Ticket`, `:Sprint` — all carry `node.tenant_id` NOT NULL)
  - `fts_communications` (`:Notice`, `:Post`, `:KnowledgeDocument` — all carry `node.tenant_id` NOT NULL)
  - `fts_files` (`:FileMetadata` — carries `node.tenant_id` NOT NULL)
- **Mandatory Post-FTS Filter**:
```cypher
MATCH (req:User {id: $requesting_user_id, is_active: true, is_deleted: false})
      -[:MEMBER_OF {status: 'active', is_deleted: false}]->(t:Tenant {id: $tenant_id, is_deleted: false})
CALL db.index.fulltext.queryNodes($index_name, $search_term) YIELD node, score
WHERE node.tenant_id = $tenant_id
  AND coalesce(node.is_deleted, false) = false
```
*(Followed immediately by domain-level RBAC/visibility predicates for the matched label.)*

#### Template FTS-B: Global `:User` Directory Fulltext Index (`fts_directory`)
- **Applies to**:
  - `fts_directory` on `:User` (`[u.display_name, u.username, u.email]`).
- **Why Template FTS-A Cannot Be Used on `fts_directory`**:
  - `:User` (`NM-02`) is a global account node and **does NOT have a `u.tenant_id` property**. Writing `WHERE node.tenant_id = $tenant_id` on `fts_directory` would always evaluate to `null = $tenant_id` (`FALSE`) and return **0 rows**! Conversely, omitting tenant filtering on `fts_directory` would leak users from other tenants (`Cross-Tenant User Enumeration Vulnerability`).
- **Mandatory Post-FTS Tenant Membership Join (`Template FTS-B` — Scenario `Q14`)**:
```cypher
// Step 1: Verify caller is an active, non-deleted member of $tenant_id with directory lookup permission
MATCH (req:User {id: $requesting_user_id, is_active: true, is_deleted: false})
      -[:MEMBER_OF {status: 'active', is_deleted: false}]->(t:Tenant {id: $tenant_id, is_deleted: false})
WHERE $has_directory_search_permission = true

// Step 2: Query global User fulltext index
CALL db.index.fulltext.queryNodes('fts_directory', $search_term) YIELD node AS u, score

// Step 3: Mandatory tenant isolation join — target user MUST have an active, non-deleted membership in the caller's $tenant_id
MATCH (u)-[m:MEMBER_OF {status: 'active', is_deleted: false}]->(t)
WHERE u.is_active = true
  AND u.is_deleted = false
  AND coalesce(m.is_resigned, false) = false

// Step 4: Optional active department resolution strictly within $tenant_id
OPTIONAL MATCH (u)-[dm:MEMBER_OF_DEPARTMENT {tenant_id: $tenant_id, is_active: true, is_primary: true}]->(d:Department {tenant_id: $tenant_id})
WHERE dm.effective_to IS NULL

// Step 5: Return ONLY tenant-scoped directory projection (never expose other tenants' memberships or sensitive PII)
RETURN u.id AS user_id,
       u.username AS username,
       u.email AS email,
       coalesce(m.display_name, u.display_name) AS display_name,
       m.position AS position,
       d.id AS primary_department_id,
       d.name AS primary_department_name,
       score
ORDER BY score DESC, display_name ASC
LIMIT 20;
```
