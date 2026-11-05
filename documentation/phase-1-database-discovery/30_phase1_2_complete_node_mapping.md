# 30 – Phase 1.2 / 1.2.1 / 1.2.2 Complete Node Mapping Specification
## Groupware AI Chatbot Project – Exhaustive PostgreSQL-to-Neo4j Node Contracts

> [!IMPORTANT]
> **Work Package 2 Objective (Updated in Phase 1.2.1 & Phase 1.2.2)**:
> In Phase 1.1, `21_phase1_1_final_graph_data_model.md` defined **23 operational node labels** (plus 4 semantic labels), whereas `24_phase1_1_final_source_to_graph_mapping.md` only provided mapping contracts for **17 nodes** (omitting `:Role`, `:Permission`, `:AssetCategory`, `:Audience`, `:LeaveBalance`, `:AttendanceRecord`) and contained multiple column-level contradictions against the physical PostgreSQL schema.
> This document establishes **100% node mapping reconciliation** across all 27 evaluated graph node labels (23 operational + 4 semantic), with standardized canonical Node IDs (`NM-01`..`NM-10`, `ND-11`, `NM-12`..`NM-25`, `ND-26`, `ND-27`), explicit column lists (**NO `SELECT *`**), verified PostgreSQL data types, `ON CREATE SET` / `ON MATCH SET` update semantics, per-node reconciliation keys (**`CRITICAL-06`**), deterministic `:LeaveBalance` tenant derivation (**`CRITICAL-02`**), and strict 6-step `:AttendanceRecord` active-membership resolution (**`DEFECT 02` & `CRITICAL-01`**).

---

## 1. Master Node Classification & Reconciliation Register

| Node ID | Node Label | Source Schema & Table | Physical Rows | Phase 1.1 Mapping Status | Phase 1.2 Final Scope Classification | Classification Rationale & Schema Corrections Applied |
|---|---|---|---:|---|---|---|
| **NM-01** | `:Tenant` | `public.tenants` | 1 | Mapped (with invalid column `code`) | **MVP – APPROVED** | Corrected nonexistent `tenants.code` to physical column `tenants.tenant_key` (`varchar` NOT NULL). |
| **NM-02** | `:User` | `public.users` (+ `public.user_profiles` for default display) | 360 | Mapped (with `INNER JOIN` & `tenant_id` on `:User`) | **MVP – APPROVED** | Removed scalar `u.tenant_id` from `:User` (global identity); changed `INNER JOIN` to `LEFT JOIN user_profiles` on default membership so users without profiles are never silently dropped. |
| **NM-03** | `:Department` | `public.departments` | 103 | Mapped (filtered `is_active = true`, losing 76 depts) | **MVP – APPROVED** | Removed `WHERE is_active = true` filter that dropped 76/103 departments referenced by users/assets; retained `is_active` as a boolean node property. |
| **NM-04** | `:Role` | `public.roles` | 42 | **MISSING IN 24** | **MVP – APPROVED** | Added complete mapping contract from `public.roles` (`id`, `tenant_id`, `code`, `name`, `description`, `level`, `is_active`, `is_system`). |
| **NM-05** | `:Permission` | `public.permissions` | 247 | **MISSING IN 24** (had nonexistent `tenant_id` in `21`) | **MVP – APPROVED** | Added complete mapping contract from `public.permissions`. Removed nonexistent `tenant_id` from `:Permission` (global catalog; tenant scope lives on grant relationships). |
| **NM-06** | `:Project` | `public.projects` | 65 | Mapped | **MVP – APPROVED** | Replaced fragile `LEFT JOIN user_profiles` with deterministic tenant derivation CTE (`tenant_user_memberships` + backup audit fallback). |
| **NM-07** | `:Ticket` | `public.tickets` | 668 | Mapped (missing `tenant_id` in `24`) | **MVP – APPROVED** | Added `tenant_id` derivation via parent `projects.id` so `Ticket.tenant_id` matches Graph Model and range index. |
| **NM-08** | `:Sprint` | `public.project_sprints` | 40 | Mapped (`date()` on `timestamptz`) | **MVP – APPROVED** | Added `tenant_id` via parent project; corrected `start_date`/`end_date` transform to `datetime()` (`timestamptz`). |
| **NM-09** | `:KanbanColumn` | `public.kanban_columns` | 268 | Mapped | **MVP – APPROVED** | Added `tenant_id` via parent project; aligned `title`, `status_group`, `position`, `is_default`. |
| **NM-10** | `:ApprovalRequest` | `public.approval_requests` | 4,709 | Mapped (missing `tenant_id` in `24`) | **MVP – APPROVED** | Added `tenant_id` derivation from `created_by_user_id` membership; documented that `code` is 100% NULL (`4,709/4,709` NULLs) in current snapshot. |
| **ND-11** | `:WorkflowTemplate` | `public.approval_workflow_templates` | 9 | Mapped (claimed `tenant_id` in `21`) | **MVP – BLOCKED** | Physical table has **NO `tenant_id`** and **NO `created_by`** column, and `request_type` is not an FK from `approval_requests` (`crd_acceptance` has no template; `overtime_aggregate` and `report` have no requests). Blocked pending Stakeholder Decision **SD-01**. |
| **NM-12** | `:ScheduleEvent` | `public.schedule_events` | 349 | Mapped (missing `tenant_id` and `end_date` in `24`) | **MVP – APPROVED** | Added `tenant_id` derivation from organizer `user_id` and included `end_date` (`date` NOT NULL) and `visibility`. |
| **NM-13** | `:ScheduleRoom` | `public.schedule_rooms` | 13 | Mapped (claimed `tenant_id` & `location` in `21`, filtered `is_active=true` in `24`) | **MVP – APPROVED** (Pooled Resource) | Removed nonexistent `tenant_id` and `location` columns from `:ScheduleRoom`. Removed `WHERE is_active = true` filter (which dropped 12 of 13 rooms, including rooms with active bookings!). |
| **NM-14** | `:Notice` | `public.notices` | 99 | Mapped (missing `is_deleted = false` filter & `tenant_id` in `24`) | **MVP – APPROVED** | Added `tenant_id` derivation from `created_by_user_id` and added soft-delete handling (`84` of `99` notices have `is_deleted = true`). |
| **NM-15** | `:Post` | `public.talk_posts` | 247 | Mapped (with nonexistent `category_id` in `21` and missing `tenant_id` in `24`) | **MVP – APPROVED** | Removed nonexistent `category_id` from `:Post`; added `tenant_id` derivation from `author_user_id`. |
| **NM-16** | `:Asset` | `public.assets` | 685 | Mapped (missing `tenant_id` & `serial_number` in `24`) | **MVP – APPROVED** | Added `tenant_id` derivation (`department_id` -> `departments.tenant_id`, fallback `assigned_user_id`/`created_by_user_id`) and included `serial_number`. Redacted financial columns (`purchase_price`, `current_value`, `lease_monthly_fee`, `lease_deposit`). |
| **NM-17** | `:AssetCategory` | `public.asset_categories` | 30 | **MISSING IN 24** (claimed `tenant_id` & `description` in `21`) | **MVP – APPROVED** | Added complete mapping contract. Removed nonexistent `tenant_id` and `description` columns (table has `id, code, name, parent_id, sort_order, is_active, created_at, updated_at`). |
| **NM-18** | `:FileMetadata` | `public.files` | 3,255 | Mapped (missing `tenant_id` & `is_deleted` in `24`) | **MVP – APPROVED** | Added `tenant_id` derivation from `uploaded_by_user_id` and soft-delete status (`is_deleted`). Excluded `file_url` and `checksum_sha256`. |
| **NM-19** | `:ChatConversation` | `public.chat_conversations` | 329 | Mapped (missing `tenant_id` in `24`) | **MVP – APPROVED** | Preserved ChatMessage Option A. Added `tenant_id` derivation from `created_by_user_id` and active conversation members. |
| **NM-20** | `:Audience` | `public.audiences` | 116 | **MISSING IN 24** (claimed `tenant_id` & `description` in `21`) | **MVP – APPROVED** (Dual-Scope Contract) | Added complete mapping contract from `public.audiences` (`id, code, name, audience_type, is_system, owner_user_id, is_active`). Removed nonexistent `description` column. System audiences (`is_system = true`, `1` row) have `tenant_id = null` (global system template); custom audiences (`is_system = false`, `115` rows) derive `tenant_id` from `owner_user_id` and member tables (**DEFECT 04**). |
| **NM-21** | `:LeaveBalance` | `public.user_leave_year_balances` & `public.user_leave_monthly_balances` | 353 (Year)<br>4,238 (Month) | **MISSING IN 24** (`21` conflated monthly table with annual `remaining_days` column) | **MVP – APPROVED** (`:LeaveBalance` from `user_leave_year_balances`; `:LeaveMonthlyBalance` optional/deferred) | Resolved schema conflict & tenant derivation (**`CRITICAL-02`**): `remaining_days` exists **only** on `user_leave_year_balances` (`353` rows), whereas `user_leave_monthly_balances` (`4,238` rows) has `accrued_days`, `used_days`, `pending_accrued_days`. Derives `tenant_id` via `user_unambiguous_leave_tenant` (`tenant_user_memberships` + `user_profiles`, `COUNT(DISTINCT tenant_id) = 1`), preserving single-tenant historical balances while quarantining multi-tenant ambiguity (`AMBIGUOUS_TENANT`, `SD-07`). |
| **NM-22** | `:AttendanceRecord` | `public.attendance_daily_records` | 54,489 | **MISSING IN 24** (`21` invented `working_minutes` & `overtime_minutes`) | **MVP – APPROVED** (With 6-State Quarantine) | Added complete mapping contract. Corrected nonexistent `working_minutes`/`overtime_minutes` to physical columns `actual_minutes`, `is_late`, `is_early_leave`, `first_check_in`, `last_check_out`, `employee_code`. Enforces 6-step deterministic user/tenant resolution with **active membership check `m.status = 'active' AND m.is_deleted = false`** (`RESOLVED_BY_USER_ID` and unambiguous `RESOLVED_BY_EMPLOYEE_NUMBER` only; `UNRESOLVED`, `AMBIGUOUS`, `INVALID_TENANT`, `INVALID_SOURCE_REFERENCE` quarantined — **`DEFECT 02` & `CRITICAL-01`**). |
| **NM-23** | `:ContractHistory` | `public.user_contract_histories` | 457 | Mapped (with nonexistent columns `start_date`, `end_date`, `status`!) | **MVP – APPROVED** (Strict HR Policy) | **Critical Fix**: `user_contract_histories` does **not** have `start_date`, `end_date`, or `status`! Its physical columns are `contract_period_from` (`date`), `contract_period_to` (`date`), and `is_current` (`bool` NOT NULL). Also proved `user_contract_histories` has **zero** salary/bonus columns in PostgreSQL. |
| **NM-24** | `:Tag` | `public.project_tags` (20) & `public.talk_tags` (10) | 30 | Unmapped in `24` | **MVP – APPROVED** (Semantic) | Mapped with composite business key (`tag_scope`, `source_id`) via synthetic `tag_key` (`'project:' || id` / `'talk:' || id`) so `project_tags` and `talk_tags` do not collide on `id`. Reconciled strictly by `tag_key` (**`CRITICAL-06`**). |
| **NM-25** | `:KnowledgeDocument` | `public.project_common_documents` (40) JOIN `public.files` | 40 | Unmapped in `24` | **MVP – APPROVED** (Semantic) | Mapped from `project_common_documents` (`id, project_id, file_id, title, sort_order, uploaded_by_id, is_deleted`) excluding payment columns (`payment_amount`, etc.). |
| **ND-26** | `:Topic` | None (No physical table in PostgreSQL) | 0 | Unmapped in `24` | **FUTURE** | No source table exists in PostgreSQL (`tags`/`topics` absent). Classified as **FUTURE** (NLP extraction phase). |
| **ND-27** | `:BusinessConcept` | None (No physical table in PostgreSQL) | 0 | Unmapped in `24` | **FUTURE** | Classified as **FUTURE** (Ontology phase). |

---

## 2. Detailed Investigation of Previously Unmapped & Disputed Entities (Section 6.2 Requirements)

### 2.1 `:User` (NM-02)
- **Findings**: `public.users` has 360 rows (`id` `int4`, `is_active`: 220 true / 140 false, `is_deleted`: 353 false / 7 true). All 360 users currently have 1 profile in `user_profiles` (`tenant_id = 1`) and 1 active membership in `tenant_user_memberships` (`tenant_id = 1`).
- **Correction**: Do not assign a single `tenant_id` property to `:User`. Use `LEFT JOIN user_profiles` (filtered on default membership `is_default = true`) only to populate fallback display metadata (`display_name`), while storing tenant-specific profile attributes on `(:User)-[m:MEMBER_OF]->(:Tenant)`. Synchronize `is_deleted` and `is_active` as explicit boolean properties so queries filter `WHERE u.is_deleted = false AND u.is_active = true`.

### 2.2 `:Role` (NM-04) and `:Permission` (NM-05)
- **Findings**:
  - `public.roles` (42 rows, PK `id` `int4`) has `tenant_id` (`int8` NOT NULL = 1), `code`, `name`, `description`, `level`, `is_active` (11 true, 31 false), `is_system` (7 true, 35 false). Unique index: `ux_roles_tenant_code (tenant_id, lower(code))`. Thus **roles are tenant-scoped** (with system roles replicated/scoped per tenant).
  - `public.permissions` (247 rows, PK `id` `int4`) has `code`, `resource_type` (`'menu'`: 245, `'organization-workforce-position-requests'`: 1, `'system_policy'`: 1), `resource_id`, `action_id`, `description`, `rule_id`. **It has NO `tenant_id` column.** Thus **permissions are a global catalog**.
  - Assignments: `user_role_assignments` (448 rows) has `tenant_id` (`int8` NOT NULL); `role_permissions` (1,535 rows) has `tenant_id` (`int8` NOT NULL) and `is_granted` (`bool`: 1,365 true, 170 false); `user_permissions` (51 rows) has `tenant_id` (`int8` NOT NULL) and `is_granted` (`bool`: 19 true, 32 false).

### 2.3 `:AssetCategory` (NM-17)
- **Findings**:
  - `public.asset_categories` has 30 rows, PK `id` (`int4`), columns: `id`, `code` (`varchar` NOT NULL, unique), `name` (`varchar` NOT NULL), `parent_id` (`int4`, nullable: 4 root categories, 26 subcategories), `sort_order` (`int4`), `is_active` (`bool`: 29 true, 1 false), `created_at`, `updated_at`.
  - **Correction**: `asset_categories` has **NO `tenant_id`** and **NO `description`** column (both were invented in Phase 1.1 `21`). All 685 rows in `public.assets` have a non-null `category_id` (`int4`) that matches `asset_categories.id` (`100.0%` match across 11 active categories).

### 2.4 `:Audience` (NM-20 — DEFECT 04 Resolution)
- **Findings**:
  - `public.audiences` has 116 rows, PK `id` (`int4`), columns: `id`, `code` (`varchar`, unique), `name` (`varchar`), `audience_type` (`varchar` NOT NULL: `'MIXED'`: 63, `'DEPARTMENT'`: 30, `'USER'`: 19, `'CUSTOM'`: 3, `'ALL'`: 1), `is_system` (`bool`: 1 true, 115 false), `owner_user_id` (`int4`: 115 non-null, 1 null for `id=1` `'All employees'`), `is_active` (`bool`: 115 true, 1 false), `metadata` (`jsonb`), `created_at`, `updated_at`.
  - Target membership tables: `public.audience_department_members` (100 rows, PK `id`, `audience_id` `int4` -> `audiences.id` 100%, `department_id` `int4` -> `departments.id` 100%) and `public.audience_user_members` (39 rows, PK `id`, `audience_id` `int4` -> `audiences.id` 100%, `user_id` `int4` -> `users.id` 100%).
  - **DEFECT 04 Dual-Scope Ownership Resolution**:
    1. **System Audience (`is_system = true`, `1` row: `id = 1`)**: Modeled as a **Global System Template Node** (`a.is_system = true`, `a.tenant_id = null`). It is **never** assigned an arbitrary `default_tenant` `tenant_id`, and it **never** carries `[:INCLUDES_DEPARTMENT]` or `[:INCLUDES_USER]` edges.
    2. **Custom Audience (`is_system = false`, `115` rows)**: Modeled as a **Tenant-Scoped Node** (`a.is_system = false`, `a.tenant_id = toInteger(row.tenant_id)` NOT NULL) where `tenant_id` is derived unambiguously from `owner_user_id` and verified against all linked `audience_department_members` and `audience_user_members`. Any custom audience with missing or cross-tenant ownership/membership is quarantined.

### 2.5 `:LeaveBalance` (NM-21 — CRITICAL-02 Resolution)
- **Findings**:
  - The database has **two distinct leave balance tables**:
    1. `public.user_leave_year_balances` (353 rows, PK `id` `int8`, unique key `uq_user_leave_year_balances_user_year (user_id, year)`, **NO `tenant_id` column**): columns `id`, `user_id` (`int8`), `year` (`int4`, all `2026`), `opening_days`, `carryover_days`, `seniority_days`, `manual_adjustment_days`, `remaining_days` (`numeric` NOT NULL), `carryover_granted_days`, `carryover_used_before_reset_days`, `carryover_expired_days`, `carryover_available_days`, `note`, `updated_by_user_id`, `created_at`, `updated_at`.
    2. `public.user_leave_monthly_balances` (4,238 rows, PK `id` `int8`, unique key `uq_user_leave_monthly_balances_user_year_month (user_id, year, month)`, **NO `tenant_id` column**): columns `id`, `user_id` (`int8`), `year` (`int4`), `month` (`int4`, 1..12), `accrued_days` (`numeric`), `used_days` (`numeric`), `pending_accrued_days` (`numeric`), `note`, `updated_by_user_id`, `created_at`, `updated_at`.
- **CRITICAL-02 Tenant Derivation, Active vs. Historical Retention & Quarantine Contract**:
  1. **Multi-Table Grain & Aggregation**: `:LeaveBalance` (`NM-21`) is anchored on `public.user_leave_year_balances` (`yb.id`, `1` node per `(user_id, year)`) joined with the aggregated annual `SUM(mb.accrued_days)` and `SUM(mb.used_days)` from `public.user_leave_monthly_balances` (`LEFT JOIN monthly_agg ma ON ma.user_id = yb.user_id AND ma.year = yb.year`).
  2. **Deterministic Tenant Derivation (`user_unambiguous_leave_tenant`)**:
     - Joins `public.tenant_user_memberships m` (`m.is_deleted = false AND m.status IN ('active', 'inactive', 'suspended')`) with `public.user_profiles up` (`up.user_id = m.user_id AND up.tenant_id = m.tenant_id`) and `public.users u` (`u.id = m.user_id AND COALESCE(u.is_deleted, false) = false`).
     - Groups by `m.user_id` with `HAVING count(DISTINCT m.tenant_id) = 1`.
     - **Why both `'active'` and `'inactive'/'suspended'` non-deleted memberships are included in the ETL derivation CTE**: Annual leave balances (`user_leave_year_balances`) are statutory HR records that must be retained for HR Admin audit even after an employee resigns (`up.is_resigned = true`, `140` rows) or becomes `inactive`, provided the employee belongs to a single unambiguous tenant (`count(DISTINCT m.tenant_id) = 1`). At query time, Scenario `Q11` (`Doc 34`) enforces `(:User)-[:MEMBER_OF {status: 'active', is_deleted: false}]->(:Tenant {id: $tenant_id})` for self-service access, blocking inactive/suspended users from self-querying while preserving historical ledger integrity.
     - **Multi-Tenant Duplicate / Ambiguity Prevention**: Because `uq_user_leave_year_balances_user_year (user_id, year)` has no `tenant_id` column, if a user has non-deleted memberships in `>1` tenant (`count(DISTINCT m.tenant_id) > 1`), the row is **excluded from `NM-21`** and routed to `etl_quarantine_log` (`reason = 'AMBIGUOUS_TENANT'`). If `count(DISTINCT m.tenant_id) = 0` (no non-deleted membership), it is quarantined with `reason = 'INVALID_TENANT'`.
     - **Schema Confirmation (`SD-07` — `NEEDS SOURCE CONFIRMATION`)**: Before onboarding multi-tenant shared employees, Engineering must confirm whether `tenant_id BIGINT NOT NULL` will be added to `public.user_leave_year_balances` and `public.user_leave_monthly_balances`.

### 2.6 `:AttendanceRecord` (NM-22 — DEFECT 02 & CRITICAL-01 Resolution)
- **Findings**:
  - `public.attendance_daily_records` has 54,489 rows, PK `id` (`int8`), unique constraint `uq_attendance_daily_records_employee_date (employee_code, work_date)`.
  - Columns: `id`, `employee_code` (`varchar` NOT NULL, 665 distinct codes), `user_id` (`int8`, **nullable**: 24,764 non-null across 279 distinct users; **29,725 rows have `user_id IS NULL`**!), `username`, `full_name`, `work_date` (`date` NOT NULL, range `2025-05-24` to `2026-11-03`), `first_check_in` (`timestamptz`), `last_check_out` (`timestamptz`), `swipe_count` (`int4`), `first_event_id` (`int8`), `last_event_id` (`int8`), `status` (`varchar` NOT NULL: **100% of rows (`54,489`) have `status = 'present'`**), `is_late` (`bool` NOT NULL: **100% `false`**), `is_early_leave` (`bool` NOT NULL: **100% `false`**), `actual_minutes` (`int4` NOT NULL), `metadata` (`jsonb`), `created_at`, `updated_at`.
  - **DEFECT 02 & CRITICAL-01 6-Step Resolution & Active Membership Quarantine Contract**:
    1. Because `user_profiles.employee_number` has **no physical `UNIQUE` constraint** in PostgreSQL, a naive `OR (a.user_id IS NULL AND up.employee_number = a.employee_code)` join without deduplication/ambiguity checking could fan out if two profiles ever shared an `employee_number`.
    2. Furthermore (**`CRITICAL-01`**), both `valid_user_tenant` and `emp_number_resolution` CTEs in `NM-22` (`Doc 30`) and `RM-37` (`Doc 31`) strictly enforce **Rule `MEM-ACTIVE`**:
       `m.status = 'active' AND m.is_deleted = false AND COALESCE(u.is_deleted, false) = false`.
    3. The 6 classification states are:
       - **`RESOLVED_BY_USER_ID`**: `a.user_id IS NOT NULL`, exists in `public.users` (`u.is_deleted = false`), and has an unambiguous active `(user_id, tenant_id)` in `user_profiles` + `tenant_user_memberships` (`m.status = 'active' AND m.is_deleted = false`, `Case A`).
       - **`RESOLVED_BY_EMPLOYEE_NUMBER`**: `a.user_id IS NULL`, and `a.employee_code` matches **exactly one** `user_id` (`u.is_deleted = false`) and **exactly one** `tenant_id` in `user_profiles` (`emp_number_resolution.user_cnt = 1 AND emp_number_resolution.tenant_cnt = 1`) with active tenant membership (`m.status = 'active' AND m.is_deleted = false`, `Case A`).
       - **`UNRESOLVED`** (`0` active matches on `employee_code`), **`AMBIGUOUS`** (`>1` matching `user_id` or `tenant_id`), **`INVALID_TENANT`** (including `Case B: status='inactive', is_deleted=false`, `Case C: status='suspended', is_deleted=false`, `Case D: status='active', is_deleted=true`, `Case E: status='inactive', is_deleted=true`), and **`INVALID_SOURCE_REFERENCE`** (`a.user_id IS NOT NULL` not in `users.id` or `u.is_deleted = true`) are **quarantined** to `etl_quarantine_log` and **never** loaded as orphan `:AttendanceRecord` nodes in Neo4j.
       - Every loaded `:AttendanceRecord` node stores `ar.resolution_status` (`'RESOLVED_BY_USER_ID'` or `'RESOLVED_BY_EMPLOYEE_NUMBER'`) and is linked 1:1 to its `:User` via `(:User)-[:HAS_ATTENDANCE]->(:AttendanceRecord)` (`RM-37`).

### 2.7 `:ContractHistory` (NM-23)
- **Findings**:
  - `public.user_contract_histories` has 457 rows, PK `id` (`int8`), columns: `id`, `user_id` (`int8` NOT NULL, 351 distinct users, 100% match to `users.id`), `contract_type` (`varchar`: `'LC'`: 246, `'TC'`: 84, `'PC'`: 80, `'JC'`: 46, `'LC-1 year'`: 1), `contract_period_from` (`date`), `contract_period_to` (`date`), `is_current` (`bool` NOT NULL: 351 true, 106 false), `note` (`text`), `created_at`, `updated_at`, `created_by_user_id`, `updated_by_user_id`, `tenant_id` (`int8` NOT NULL = 1).

---

## 3. Complete Node Mapping Contracts (Approved MVP Nodes)

### 3.1 Summary Contract Matrix for All Approved MVP Nodes

| Contract ID | Node Label | Source Schema.Table | Source PK & Graph Identity Key (`CRITICAL-06`) | Source Columns (Explicit) | Target Neo4j Properties | Tenant Ownership Rule | Classification & Sensitivity | Soft Delete, Reconciliation & Null Handling (`CRITICAL-06`) | Uniqueness & Indexes | Validation Status |
|---|---|---|---|---|---|---|---|---|---|---|
| **NM-01** | `:Tenant` | `public.tenants` | PG PK: `id` (`int8`)<br>Graph Key: `t.id` (`INTEGER`) | `id, tenant_key, name, status, isolation_mode, is_default, is_deleted, created_at, updated_at` | `id, tenant_key, name, status, isolation_mode, is_default, is_deleted, created_at, updated_at, last_synced_at` | Root entity (`t.id`) | Tier 1 (Corporate System) | Retain node with `is_deleted` flag; reconcile against `SELECT id FROM public.tenants` | `UNIQUE (t.id)`, `INDEX (t.tenant_key)` | **STATICALLY VALIDATED** |
| **NM-02** | `:User` | `public.users` + `LEFT JOIN user_profiles` | PG PK: `users.id` (`int4`)<br>Graph Key: `u.id` (`INTEGER`) | `u.id, u.username, u.email, u.is_active, u.is_deleted, u.created_at, u.updated_at, up.display_name` | `id, username, email, display_name, is_active, is_deleted, created_at, updated_at, last_synced_at` | Global Identity; scoped via `[:MEMBER_OF]->(:Tenant)` | Tier 1 (PII: redact `password_hash`, `email_verification_token`, `birth_date`, `mobile_phone`, `address`, `tax_code`) | Sync `is_active` and `is_deleted` flags on node; reconcile against `SELECT id FROM public.users` | `UNIQUE (u.id)`, `INDEX (u.username)`, `INDEX (u.email)`, `INDEX (u.display_name)` | **STATICALLY VALIDATED** |
| **NM-03** | `:Department` | `public.departments` | PG PK: `id` (`int4`)<br>Graph Key: `d.id` (`INTEGER`) | `id, tenant_id, code, name, parent_id, manager_user_id, depth, path, department_type, is_active, effective_from, effective_to, created_at, updated_at` | `id, tenant_id, code, name, depth, path, department_type, is_active, effective_from, effective_to, created_at, updated_at, last_synced_at` | Direct: `departments.tenant_id` (`int8` NOT NULL) | Tier 1 (Corporate Org) | Ingest all 103 rows (do not drop `is_active = false`); reconcile against `SELECT id FROM public.departments` | `UNIQUE (d.id)`, `INDEX (d.tenant_id)`, `INDEX (d.code)` | **STATICALLY VALIDATED** |
| **NM-04** | `:Role` | `public.roles` | PG PK: `id` (`int4`)<br>Graph Key: `r.id` (`INTEGER`) | `id, tenant_id, code, name, description, level, is_active, is_system, created_at, updated_at` | `id, tenant_id, code, name, description, level, is_active, is_system, created_at, updated_at, last_synced_at` | Direct: `roles.tenant_id` (`int8` NOT NULL) | Tier 3 (Security RBAC) | Ingest all 42 roles with `is_active` boolean; reconcile against `SELECT id FROM public.roles` | `UNIQUE (r.id)`, `INDEX (r.tenant_id)`, `INDEX (r.code)` | **STATICALLY VALIDATED** |
| **NM-05** | `:Permission` | `public.permissions` | PG PK: `id` (`int4`)<br>Graph Key: `p.id` (`INTEGER`) | `id, code, resource_type, resource_id, action_id, rule_id, description, created_at` | `id, code, resource_type, resource_id, action_id, rule_id, description, created_at, last_synced_at` | Global Catalog (Tenant scoped on `[:INCLUDES_PERMISSION]` & `[:DIRECT_PERMISSION]`) | Tier 3 (Security RBAC) | No soft-delete column; reconcile against `SELECT id FROM public.permissions` | `UNIQUE (p.id)`, `UNIQUE (p.code)` | **STATICALLY VALIDATED** |
| **NM-06** | `:Project` | `public.projects` | PG PK: `id` (`int8`)<br>Graph Key: `p.id` (`INTEGER`) | `id, key, name, description, status, status_id, approval_status, service_type, classification, created_by_user_id, start_date, end_date, is_deleted, created_at, updated_at` | `id, tenant_id, key, name, description, status, status_id, approval_status, service_type, classification, created_by_user_id, start_date, end_date, is_deleted, created_at, updated_at, last_synced_at` | Transitive via creator/member tenant membership (`MEM-HISTORICAL-UNAMBIGUOUS`) | Tier 1 (Exclude `payment_terms`) | Sync `is_deleted` boolean; reconcile against eligible `NM-06` CTE `SELECT p.id` | `UNIQUE (p.id)`, `INDEX (p.tenant_id)`, `INDEX (p.key)` | **STATICALLY VALIDATED** |
| **NM-07** | `:Ticket` | `public.tickets` | PG PK: `id` (`int8`)<br>Graph Key: `t.id` (`INTEGER`) | `id, project_id, sprint_id, column_id, parent_ticket_id, code, title, priority, status, created_by_user_id, due_date, start_date, completed_at, estimated_hours, actual_hours, is_deleted, created_at, updated_at` | `id, tenant_id, project_id, sprint_id, column_id, parent_ticket_id, code, title, priority, status, created_by_user_id, due_date, start_date, completed_at, estimated_hours, actual_hours, is_deleted, created_at, updated_at, last_synced_at` | Transitive via parent `:Project.tenant_id` | Tier 1 (Exclude `unit_price`, `quantity`, `note`) | Sync `is_deleted` boolean; reconcile against eligible `NM-07` CTE `SELECT t.id` | `UNIQUE (t.id)`, `INDEX (t.tenant_id)`, `INDEX (t.code)` | **STATICALLY VALIDATED** |
| **NM-08** | `:Sprint` | `public.project_sprints` | PG PK: `id` (`int8`)<br>Graph Key: `s.id` (`INTEGER`) | `id, project_id, name, goal, start_date, end_date, status, created_at, updated_at` | `id, tenant_id, project_id, name, goal, start_date, end_date, status, created_at, updated_at, last_synced_at` | Transitive via parent `:Project.tenant_id` | Tier 2 (Project Schedule) | No soft-delete column; reconcile against eligible `NM-08` CTE `SELECT s.id` | `UNIQUE (s.id)`, `INDEX (s.tenant_id)` | **STATICALLY VALIDATED** |
| **NM-09** | `:KanbanColumn` | `public.kanban_columns` | PG PK: `id` (`int8`)<br>Graph Key: `k.id` (`INTEGER`) | `id, project_id, title, status_group, position, is_default, created_at, updated_at` | `id, tenant_id, project_id, title, status_group, position, is_default, created_at, updated_at, last_synced_at` | Transitive via parent `:Project.tenant_id` | Tier 2 (Workflow Stage) | No soft-delete column; reconcile against eligible `NM-09` CTE `SELECT k.id` | `UNIQUE (k.id)`, `INDEX (k.tenant_id)` | **STATICALLY VALIDATED** |
| **NM-10** | `:ApprovalRequest` | `public.approval_requests` | PG PK: `id` (`int8`)<br>Graph Key: `a.id` (`INTEGER`) | `id, code, request_type, status, title, created_by_user_id, submitted_at, completed_at, start_date, end_date, total_days, leave_type, is_deleted, created_at, updated_at` | `id, tenant_id, code, request_type, status, title, created_by_user_id, submitted_at, completed_at, start_date, end_date, total_days, leave_type, is_deleted, created_at, updated_at, last_synced_at` | Transitive via `created_by_user_id` membership (`MEM-HISTORICAL-UNAMBIGUOUS`) | Tier 1 (Exclude `reason` & `payload` jsonb from graph properties) | Sync `is_deleted` boolean; reconcile against eligible `NM-10` CTE `SELECT a.id` | `UNIQUE (a.id)`, `INDEX (a.tenant_id)`, `INDEX (a.code)` | **STATICALLY VALIDATED** |
| **NM-12** | `:ScheduleEvent` | `public.schedule_events` | PG PK: `id` (`int8`)<br>Graph Key: `e.id` (`INTEGER`) | `id, user_id, title, description, event_date, end_date, start_time, end_time, room_id, location, visibility, is_all_day, recurrence_type, is_deleted, created_at, updated_at` | `id, tenant_id, user_id, title, description, event_date, end_date, start_time, end_time, room_id, location, visibility, is_all_day, recurrence_type, is_deleted, created_at, updated_at, last_synced_at` | Transitive via organizer `user_id` membership (`MEM-HISTORICAL-UNAMBIGUOUS`) | Tier 1 (Enforce `visibility` filter for `'private'` events; exclude `notes`, `customer`) | Sync `is_deleted` boolean; reconcile against eligible `NM-12` CTE `SELECT e.id` | `UNIQUE (e.id)`, `INDEX (e.tenant_id)`, `INDEX (e.event_date)` | **STATICALLY VALIDATED** |
| **NM-13** | `:ScheduleRoom` | `public.schedule_rooms` | PG PK: `id` (`int4`)<br>Graph Key: `r.id` (`INTEGER`) | `id, name, capacity, description, sort_order, is_active, created_at, updated_at` | `id, name, capacity, description, sort_order, is_active, created_at, updated_at, last_synced_at` | Pooled Facility Resource (No `tenant_id` in source table; isolated via `:ScheduleEvent.tenant_id`) | Tier 2 (Facility Resource) | Ingest all 13 rooms with `is_active` boolean; reconcile against `SELECT id FROM public.schedule_rooms` | `UNIQUE (r.id)`, `UNIQUE (r.name)` | **STATICALLY VALIDATED** |
| **NM-14** | `:Notice` | `public.notices` | PG PK: `id` (`int8`)<br>Graph Key: `n.id` (`INTEGER`) | `id, title, notice_type, priority, audience_id, created_by_user_id, is_published, published_at, is_deleted, created_at, updated_at` | `id, tenant_id, title, notice_type, priority, audience_id, created_by_user_id, is_published, published_at, is_deleted, created_at, updated_at, last_synced_at` | Transitive via `created_by_user_id` membership (`MEM-HISTORICAL-UNAMBIGUOUS`) | Tier 1 (Full `content` body indexed in Vector DB, not Neo4j) | Sync `is_deleted` and `is_published`; reconcile against eligible `NM-14` CTE `SELECT n.id` | `UNIQUE (n.id)`, `INDEX (n.tenant_id)` | **STATICALLY VALIDATED** |
| **NM-15** | `:Post` | `public.talk_posts` | PG PK: `id` (`int8`)<br>Graph Key: `p.id` (`INTEGER`) | `id, author_user_id, audience_id, title, is_deleted, created_at, updated_at` | `id, tenant_id, author_user_id, audience_id, title, is_deleted, created_at, updated_at, last_synced_at` | Transitive via `author_user_id` membership (`MEM-HISTORICAL-UNAMBIGUOUS`) | Tier 1 (Full `content` body in Vector DB; `category_id` removed) | Sync `is_deleted` boolean; reconcile against eligible `NM-15` CTE `SELECT p.id` | `UNIQUE (p.id)`, `INDEX (p.tenant_id)` | **STATICALLY VALIDATED** |
| **NM-16** | `:Asset` | `public.assets` | PG PK: `id` (`int8`)<br>Graph Key: `a.id` (`INTEGER`) | `id, code, name, description, category_id, status, location, department_id, assigned_user_id, serial_number, manufacturer, acquisition_type, condition, created_by_user_id, is_deleted, created_at, updated_at` | `id, tenant_id, code, name, description, category_id, status, location, department_id, assigned_user_id, serial_number, manufacturer, acquisition_type, condition, created_by_user_id, is_deleted, created_at, updated_at, last_synced_at` | Transitive via `department_id -> departments.tenant_id` (fallback `assigned_user_id` / `created_by_user_id`) | Tier 1 (Exclude `purchase_price`, `current_value`, `lease_monthly_fee`, `lease_deposit`, `invoice_number`) | Sync `is_deleted` boolean; reconcile against eligible `NM-16` CTE `SELECT a.id` | `UNIQUE (a.id)`, `INDEX (a.tenant_id)`, `INDEX (a.code)` | **STATICALLY VALIDATED** |
| **NM-17** | `:AssetCategory` | `public.asset_categories` | PG PK: `id` (`int4`)<br>Graph Key: `c.id` (`INTEGER`) | `id, code, name, parent_id, sort_order, is_active, created_at, updated_at` | `id, code, name, parent_id, sort_order, is_active, created_at, updated_at, last_synced_at` | Global Taxonomy Catalog (No `tenant_id` in source table) | Tier 2 (Taxonomy Catalog) | Ingest all 30 rows with `is_active` boolean; reconcile against `SELECT id FROM public.asset_categories` | `UNIQUE (c.id)`, `UNIQUE (c.code)` | **STATICALLY VALIDATED** |
| **NM-18** | `:FileMetadata` | `public.files` | PG PK: `id` (`int8`)<br>Graph Key: `f.id` (`INTEGER`) | `id, storage_provider, original_name, content_type, file_ext, size_bytes, uploaded_by_user_id, uploaded_at, request_type, is_deleted` | `id, tenant_id, storage_provider, original_name, content_type, file_ext, size_bytes, uploaded_by_user_id, uploaded_at, request_type, is_deleted, last_synced_at` | Transitive via `uploaded_by_user_id` membership (`MEM-HISTORICAL-UNAMBIGUOUS`) | Tier 2 (Strictly exclude `file_url` and `checksum_sha256`) | Sync `is_deleted` boolean; reconcile against eligible `NM-18` CTE `SELECT f.id` | `UNIQUE (f.id)`, `INDEX (f.tenant_id)` | **STATICALLY VALIDATED** |
| **NM-19** | `:ChatConversation` | `public.chat_conversations` | PG PK: `id` (`int8`)<br>Graph Key: `c.id` (`INTEGER`) | `id, conversation_type, title, created_by_user_id, last_message_seq, created_at, updated_at` | `id, tenant_id, conversation_type, title, created_by_user_id, last_message_seq, created_at, updated_at, last_synced_at` | Transitive via `created_by_user_id` & active `chat_conversation_members` | Tier 1 (Option A: exclude `direct_key`, `avatar_url`, and all `chat_messages` rows) | Omit null `title`; reconcile against eligible `NM-19` CTE `SELECT c.id` | `UNIQUE (c.id)`, `INDEX (c.tenant_id)` | **STATICALLY VALIDATED** |
| **NM-20** | `:Audience` | `public.audiences` | PG PK: `id` (`int4`)<br>Graph Key: `a.id` (`INTEGER`) | `id, code, name, audience_type, is_system, owner_user_id, is_active, created_at, updated_at` | `id, tenant_id, code, name, audience_type, is_system, owner_user_id, is_active, created_at, updated_at, last_synced_at` | **Dual-Scope (DEFECT 04)**: System audience (`is_system = true`) has `tenant_id = null`; Custom audience (`is_system = false`) derives `tenant_id` from `owner_user_id` + member tables | Tier 2 (Targeting Group; exclude `metadata` jsonb) | Reconcile against dual-scope validated `NM-20` CTE `SELECT a.id`; quarantine if custom audience loses valid tenant match | `UNIQUE (a.id)`, `UNIQUE (a.code)`, `INDEX (a.tenant_id, a.audience_type, a.is_active)`, `INDEX (a.is_system, a.audience_type, a.is_active)` | **STATICALLY VALIDATED** |
| **NM-21** | `:LeaveBalance` | `public.user_leave_year_balances` + `user_leave_monthly_balances` | PG PK: `yb.id` (`int8`)<br>Graph Key: `lb.id` (`INTEGER`) | `yb.id, yb.user_id, yb.year, yb.opening_days, yb.carryover_days, yb.seniority_days, yb.manual_adjustment_days, yb.remaining_days, yb.carryover_available_days, yb.created_at, yb.updated_at` + `SUM(mb.accrued_days), SUM(mb.used_days)` | `id, tenant_id, user_id, year, opening_days, carryover_days, seniority_days, manual_adjustment_days, accrued_days, used_days, remaining_days, carryover_available_days, created_at, updated_at, last_synced_at` | **Unambiguous Leave Tenant (`CRITICAL-02`)**: `user_profiles` + `tenant_user_memberships` (`m.is_deleted = false`, `COUNT(DISTINCT tenant_id) = 1`) | Tier 4 (HR Benefit Ledger: self/HR access only; exclude `note`) | Recompute `accrued_days`/`used_days` when `user_leave_monthly_balances` changes; reconcile `lb.id` against eligible `NM-21` CTE (`SD-07`) | `UNIQUE (lb.id)`, `INDEX (lb.tenant_id)`, `INDEX (lb.user_id, lb.year)` | **STATICALLY VALIDATED** |
| **NM-22** | `:AttendanceRecord` | `public.attendance_daily_records` | PG PK: `id` (`int8`)<br>Graph Key: `ar.id` (`INTEGER`) | `id, employee_code, user_id, work_date, first_check_in, last_check_out, swipe_count, status, is_late, is_early_leave, actual_minutes, created_at, updated_at` | `id, tenant_id, employee_code, user_id, resolution_status, work_date, first_check_in, last_check_out, swipe_count, status, is_late, is_early_leave, actual_minutes, created_at, updated_at, last_synced_at` | **6-Step Active Membership Resolution (`DEFECT 02` & `CRITICAL-01`)**: `RESOLVED_BY_USER_ID` or unambiguous `RESOLVED_BY_EMPLOYEE_NUMBER` with `m.status = 'active' AND m.is_deleted = false` | Tier 4 (HR Attendance Fact: self/HR access only; exclude `metadata`) | Reconcile `ar.id` strictly against eligible `classified_attendance WHERE resolution_status IN ('RESOLVED_BY_USER_ID','RESOLVED_BY_EMPLOYEE_NUMBER')`; delete & quarantine if membership becomes inactive/ambiguous | `UNIQUE (ar.id)`, `INDEX (ar.tenant_id)`, `INDEX (ar.user_id, ar.work_date)` | **STATICALLY VALIDATED** |
| **NM-23** | `:ContractHistory` | `public.user_contract_histories` | PG PK: `id` (`int8`)<br>Graph Key: `ch.id` (`INTEGER`) | `id, tenant_id, user_id, contract_type, contract_period_from, contract_period_to, is_current, created_at, updated_at` | `id, tenant_id, user_id, contract_type, contract_period_from, contract_period_to, is_current, created_at, updated_at, last_synced_at` | Direct: `user_contract_histories.tenant_id` (`int8` NOT NULL) | Tier 6 (HR Employment History: exclude `note`; zero salary columns exist in table) | Retain historical rows (`is_current = false`) alongside current (`is_current = true`); reconcile against `SELECT id FROM public.user_contract_histories` | `UNIQUE (ch.id)`, `INDEX (ch.tenant_id)`, `INDEX (ch.user_id)` | **STATICALLY VALIDATED** |
| **NM-24** | `:Tag` | `public.project_tags` & `public.talk_tags` | PG PK: `pt.id` / `tt.id` (`int8`)<br>Graph Key: **`tg.tag_key` (`STRING`)** | `project_tags`: `id, project_id, name, color, created_at`<br>`talk_tags`: `id, name, created_at` | `tag_key, source_id, tag_scope, project_id, tenant_id, name, color, created_at, last_synced_at` | Transitive via `:Project.tenant_id` (`project_tags`) or post authors (`talk_tags`) | Tier 2 (Semantic Taxonomy) | **Synthetic Key (`CRITICAL-06`)**: `tag_key = tag_scope + ':' + id`; reconcile strictly by `tg.tag_key` against union of eligible `project:` and `talk:` keys (NEVER by `tg.id`) | `UNIQUE (tg.tag_key)`, `INDEX (tg.tenant_id)`, `INDEX (tg.name)` | **STATICALLY VALIDATED** |
| **NM-25** | `:KnowledgeDocument` | `public.project_common_documents` | PG PK: `id` (`int8`)<br>Graph Key: `kd.id` (`INTEGER`) | `id, project_id, file_id, title, sort_order, uploaded_by_id, is_deleted, created_at, updated_at` | `id, tenant_id, project_id, file_id, title, sort_order, uploaded_by_id, is_deleted, created_at, updated_at, last_synced_at` | Transitive via parent `:Project.tenant_id` | Tier 2 (Exclude `payment_installment`, `payment_terms`, `payment_project_total`, `payment_percentage`, `payment_amount`) | Sync `is_deleted` boolean; reconcile against eligible `NM-25` CTE `SELECT pcd.id` | `UNIQUE (kd.id)`, `INDEX (kd.tenant_id)` | **STATICALLY VALIDATED** |

---

## 4. Executable SQL Extraction & Cypher Upsert Contracts (All 24 Approved MVP Nodes)

> [!NOTE]
> Every Cypher contract below defines both `ON CREATE SET` and `ON MATCH SET` (with `last_synced_at = datetime()`) to satisfy Work Package 5 update lifecycle requirements.

### NM-01: `:Tenant`
```sql
SELECT
  t.id,
  t.tenant_key,
  t.name,
  t.status,
  t.isolation_mode,
  t.is_default,
  t.is_deleted,
  t.created_at,
  t.updated_at
FROM public.tenants t;
```
```cypher
UNWIND $batch AS row
MERGE (t:Tenant {id: toInteger(row.id)})
ON CREATE SET
  t.tenant_key = row.tenant_key,
  t.name = row.name,
  t.status = row.status,
  t.isolation_mode = row.isolation_mode,
  t.is_default = row.is_default,
  t.is_deleted = row.is_deleted,
  t.created_at = datetime(row.created_at),
  t.updated_at = datetime(row.updated_at),
  t.last_synced_at = datetime()
ON MATCH SET
  t.tenant_key = row.tenant_key,
  t.name = row.name,
  t.status = row.status,
  t.isolation_mode = row.isolation_mode,
  t.is_default = row.is_default,
  t.is_deleted = row.is_deleted,
  t.updated_at = datetime(row.updated_at),
  t.last_synced_at = datetime();
```

### NM-02: `:User` (Global Identity)
```sql
SELECT
  u.id AS user_id,
  u.username,
  u.email,
  COALESCE(up.display_name, u.username) AS display_name,
  COALESCE(u.is_active, false) AS is_active,
  u.is_deleted,
  u.created_at,
  u.updated_at
FROM public.users u
LEFT JOIN public.tenant_user_memberships m
  ON m.user_id = u.id
 AND m.is_default = true
 AND m.is_deleted = false
LEFT JOIN public.user_profiles up
  ON up.user_id = u.id
 AND up.tenant_id = m.tenant_id;
```
```cypher
UNWIND $batch AS row
MERGE (u:User {id: toInteger(row.user_id)})
ON CREATE SET
  u.username = row.username,
  u.email = row.email,
  u.display_name = row.display_name,
  u.is_active = row.is_active,
  u.is_deleted = row.is_deleted,
  u.created_at = CASE WHEN row.created_at IS NOT NULL THEN datetime(row.created_at) ELSE null END,
  u.updated_at = CASE WHEN row.updated_at IS NOT NULL THEN datetime(row.updated_at) ELSE null END,
  u.last_synced_at = datetime()
ON MATCH SET
  u.username = row.username,
  u.email = row.email,
  u.display_name = row.display_name,
  u.is_active = row.is_active,
  u.is_deleted = row.is_deleted,
  u.updated_at = CASE WHEN row.updated_at IS NOT NULL THEN datetime(row.updated_at) ELSE null END,
  u.last_synced_at = datetime();
```

### NM-03: `:Department`
```sql
SELECT
  d.id,
  d.tenant_id,
  d.code,
  d.name,
  d.depth,
  d.path,
  d.department_type,
  COALESCE(d.is_active, false) AS is_active,
  d.effective_from,
  d.effective_to,
  d.created_at,
  d.updated_at
FROM public.departments d;
```
```cypher
UNWIND $batch AS row
MERGE (d:Department {id: toInteger(row.id)})
ON CREATE SET
  d.tenant_id = toInteger(row.tenant_id),
  d.code = row.code,
  d.name = row.name,
  d.depth = toInteger(row.depth),
  d.path = row.path,
  d.department_type = row.department_type,
  d.is_active = row.is_active,
  d.effective_from = CASE WHEN row.effective_from IS NOT NULL THEN date(row.effective_from) ELSE null END,
  d.effective_to = CASE WHEN row.effective_to IS NOT NULL THEN date(row.effective_to) ELSE null END,
  d.created_at = CASE WHEN row.created_at IS NOT NULL THEN datetime(row.created_at) ELSE null END,
  d.updated_at = CASE WHEN row.updated_at IS NOT NULL THEN datetime(row.updated_at) ELSE null END,
  d.last_synced_at = datetime()
ON MATCH SET
  d.tenant_id = toInteger(row.tenant_id),
  d.code = row.code,
  d.name = row.name,
  d.depth = toInteger(row.depth),
  d.path = row.path,
  d.department_type = row.department_type,
  d.is_active = row.is_active,
  d.effective_from = CASE WHEN row.effective_from IS NOT NULL THEN date(row.effective_from) ELSE null END,
  d.effective_to = CASE WHEN row.effective_to IS NOT NULL THEN date(row.effective_to) ELSE null END,
  d.updated_at = CASE WHEN row.updated_at IS NOT NULL THEN datetime(row.updated_at) ELSE null END,
  d.last_synced_at = datetime();
```

### NM-04: `:Role`
```sql
SELECT
  r.id,
  r.tenant_id,
  r.code,
  r.name,
  r.description,
  r.level,
  COALESCE(r.is_active, false) AS is_active,
  COALESCE(r.is_system, false) AS is_system,
  r.created_at,
  r.updated_at
FROM public.roles r;
```
```cypher
UNWIND $batch AS row
MERGE (r:Role {id: toInteger(row.id)})
ON CREATE SET
  r.tenant_id = toInteger(row.tenant_id),
  r.code = row.code,
  r.name = row.name,
  r.description = row.description,
  r.level = toInteger(row.level),
  r.is_active = row.is_active,
  r.is_system = row.is_system,
  r.created_at = CASE WHEN row.created_at IS NOT NULL THEN datetime(row.created_at) ELSE null END,
  r.updated_at = CASE WHEN row.updated_at IS NOT NULL THEN datetime(row.updated_at) ELSE null END,
  r.last_synced_at = datetime()
ON MATCH SET
  r.tenant_id = toInteger(row.tenant_id),
  r.code = row.code,
  r.name = row.name,
  r.description = row.description,
  r.level = toInteger(row.level),
  r.is_active = row.is_active,
  r.is_system = row.is_system,
  r.updated_at = CASE WHEN row.updated_at IS NOT NULL THEN datetime(row.updated_at) ELSE null END,
  r.last_synced_at = datetime();
```

### NM-05: `:Permission` (Global Catalog)
```sql
SELECT
  p.id,
  p.code,
  p.resource_type,
  p.resource_id,
  p.action_id,
  p.rule_id,
  p.description,
  p.created_at
FROM public.permissions p;
```
```cypher
UNWIND $batch AS row
MERGE (p:Permission {id: toInteger(row.id)})
ON CREATE SET
  p.code = row.code,
  p.resource_type = row.resource_type,
  p.resource_id = CASE WHEN row.resource_id IS NOT NULL THEN toInteger(row.resource_id) ELSE null END,
  p.action_id = CASE WHEN row.action_id IS NOT NULL THEN toInteger(row.action_id) ELSE null END,
  p.rule_id = CASE WHEN row.rule_id IS NOT NULL THEN toInteger(row.rule_id) ELSE null END,
  p.description = row.description,
  p.created_at = CASE WHEN row.created_at IS NOT NULL THEN datetime(row.created_at) ELSE null END,
  p.last_synced_at = datetime()
ON MATCH SET
  p.code = row.code,
  p.resource_type = row.resource_type,
  p.resource_id = CASE WHEN row.resource_id IS NOT NULL THEN toInteger(row.resource_id) ELSE null END,
  p.action_id = CASE WHEN row.action_id IS NOT NULL THEN toInteger(row.action_id) ELSE null END,
  p.rule_id = CASE WHEN row.rule_id IS NOT NULL THEN toInteger(row.rule_id) ELSE null END,
  p.description = row.description,
  p.last_synced_at = datetime();
```

### NM-06: `:Project`
```sql
WITH user_unambiguous_tenant AS (
  SELECT user_id, min(tenant_id) AS tenant_id
  FROM (
    SELECT user_id, tenant_id FROM public.tenant_user_memberships WHERE is_deleted = false
    UNION
    SELECT user_id, tenant_id FROM _backup_cleanup_20261005.tenant_user_memberships_deleted
  ) u
  GROUP BY user_id
  HAVING count(DISTINCT tenant_id) = 1
)
SELECT
  p.id AS project_id,
  ut.tenant_id AS tenant_id,
  p.key AS project_key,
  p.name,
  p.description,
  p.status,
  p.status_id,
  p.approval_status,
  p.service_type,
  p.classification,
  p.created_by_user_id,
  p.start_date,
  p.end_date,
  COALESCE(p.is_deleted, false) AS is_deleted,
  p.created_at,
  p.updated_at
FROM public.projects p
INNER JOIN user_unambiguous_tenant ut
  ON ut.user_id = p.created_by_user_id;
```
```cypher
UNWIND $batch AS row
MERGE (p:Project {id: toInteger(row.project_id)})
ON CREATE SET
  p.tenant_id = toInteger(row.tenant_id),
  p.key = row.project_key,
  p.name = row.name,
  p.description = row.description,
  p.status = row.status,
  p.status_id = toInteger(row.status_id),
  p.approval_status = row.approval_status,
  p.service_type = row.service_type,
  p.classification = row.classification,
  p.created_by_user_id = toInteger(row.created_by_user_id),
  p.start_date = CASE WHEN row.start_date IS NOT NULL THEN datetime(row.start_date) ELSE null END,
  p.end_date = CASE WHEN row.end_date IS NOT NULL THEN datetime(row.end_date) ELSE null END,
  p.is_deleted = row.is_deleted,
  p.created_at = CASE WHEN row.created_at IS NOT NULL THEN datetime(row.created_at) ELSE null END,
  p.updated_at = CASE WHEN row.updated_at IS NOT NULL THEN datetime(row.updated_at) ELSE null END,
  p.last_synced_at = datetime()
ON MATCH SET
  p.tenant_id = toInteger(row.tenant_id),
  p.key = row.project_key,
  p.name = row.name,
  p.description = row.description,
  p.status = row.status,
  p.status_id = toInteger(row.status_id),
  p.approval_status = row.approval_status,
  p.service_type = row.service_type,
  p.classification = row.classification,
  p.created_by_user_id = toInteger(row.created_by_user_id),
  p.start_date = CASE WHEN row.start_date IS NOT NULL THEN datetime(row.start_date) ELSE null END,
  p.end_date = CASE WHEN row.end_date IS NOT NULL THEN datetime(row.end_date) ELSE null END,
  p.is_deleted = row.is_deleted,
  p.updated_at = CASE WHEN row.updated_at IS NOT NULL THEN datetime(row.updated_at) ELSE null END,
  p.last_synced_at = datetime();
```

### NM-07: `:Ticket`
```sql
WITH user_unambiguous_tenant AS (
  SELECT user_id, min(tenant_id) AS tenant_id
  FROM (
    SELECT user_id, tenant_id FROM public.tenant_user_memberships WHERE is_deleted = false
    UNION
    SELECT user_id, tenant_id FROM _backup_cleanup_20261005.tenant_user_memberships_deleted
  ) u
  GROUP BY user_id
  HAVING count(DISTINCT tenant_id) = 1
)
SELECT
  t.id AS ticket_id,
  ut.tenant_id AS tenant_id,
  t.project_id,
  t.sprint_id,
  t.column_id,
  t.parent_ticket_id,
  t.code AS ticket_code,
  t.title,
  t.priority,
  t.status,
  t.created_by_user_id,
  t.due_date,
  t.start_date,
  t.completed_at,
  t.estimated_hours,
  t.actual_hours,
  COALESCE(t.is_deleted, false) AS is_deleted,
  t.created_at,
  t.updated_at
FROM public.tickets t
INNER JOIN public.projects p ON p.id = t.project_id
INNER JOIN user_unambiguous_tenant ut ON ut.user_id = p.created_by_user_id;
```
```cypher
UNWIND $batch AS row
MERGE (t:Ticket {id: toInteger(row.ticket_id)})
ON CREATE SET
  t.tenant_id = toInteger(row.tenant_id),
  t.project_id = toInteger(row.project_id),
  t.sprint_id = CASE WHEN row.sprint_id IS NOT NULL THEN toInteger(row.sprint_id) ELSE null END,
  t.column_id = CASE WHEN row.column_id IS NOT NULL THEN toInteger(row.column_id) ELSE null END,
  t.parent_ticket_id = CASE WHEN row.parent_ticket_id IS NOT NULL THEN toInteger(row.parent_ticket_id) ELSE null END,
  t.code = row.ticket_code,
  t.title = row.title,
  t.priority = row.priority,
  t.status = row.status,
  t.created_by_user_id = toInteger(row.created_by_user_id),
  t.due_date = CASE WHEN row.due_date IS NOT NULL THEN datetime(row.due_date) ELSE null END,
  t.start_date = CASE WHEN row.start_date IS NOT NULL THEN datetime(row.start_date) ELSE null END,
  t.completed_at = CASE WHEN row.completed_at IS NOT NULL THEN datetime(row.completed_at) ELSE null END,
  t.estimated_hours = CASE WHEN row.estimated_hours IS NOT NULL THEN toFloat(row.estimated_hours) ELSE null END,
  t.actual_hours = CASE WHEN row.actual_hours IS NOT NULL THEN toFloat(row.actual_hours) ELSE null END,
  t.is_deleted = row.is_deleted,
  t.created_at = CASE WHEN row.created_at IS NOT NULL THEN datetime(row.created_at) ELSE null END,
  t.updated_at = CASE WHEN row.updated_at IS NOT NULL THEN datetime(row.updated_at) ELSE null END,
  t.last_synced_at = datetime()
ON MATCH SET
  t.tenant_id = toInteger(row.tenant_id),
  t.project_id = toInteger(row.project_id),
  t.sprint_id = CASE WHEN row.sprint_id IS NOT NULL THEN toInteger(row.sprint_id) ELSE null END,
  t.column_id = CASE WHEN row.column_id IS NOT NULL THEN toInteger(row.column_id) ELSE null END,
  t.parent_ticket_id = CASE WHEN row.parent_ticket_id IS NOT NULL THEN toInteger(row.parent_ticket_id) ELSE null END,
  t.code = row.ticket_code,
  t.title = row.title,
  t.priority = row.priority,
  t.status = row.status,
  t.due_date = CASE WHEN row.due_date IS NOT NULL THEN datetime(row.due_date) ELSE null END,
  t.start_date = CASE WHEN row.start_date IS NOT NULL THEN datetime(row.start_date) ELSE null END,
  t.completed_at = CASE WHEN row.completed_at IS NOT NULL THEN datetime(row.completed_at) ELSE null END,
  t.estimated_hours = CASE WHEN row.estimated_hours IS NOT NULL THEN toFloat(row.estimated_hours) ELSE null END,
  t.actual_hours = CASE WHEN row.actual_hours IS NOT NULL THEN toFloat(row.actual_hours) ELSE null END,
  t.is_deleted = row.is_deleted,
  t.updated_at = CASE WHEN row.updated_at IS NOT NULL THEN datetime(row.updated_at) ELSE null END,
  t.last_synced_at = datetime();
```

### NM-08: `:Sprint`
```sql
WITH user_unambiguous_tenant AS (
  SELECT user_id, min(tenant_id) AS tenant_id
  FROM (
    SELECT user_id, tenant_id FROM public.tenant_user_memberships WHERE is_deleted = false
    UNION
    SELECT user_id, tenant_id FROM _backup_cleanup_20261005.tenant_user_memberships_deleted
  ) u
  GROUP BY user_id
  HAVING count(DISTINCT tenant_id) = 1
)
SELECT
  s.id,
  ut.tenant_id,
  s.project_id,
  s.name,
  s.goal,
  s.start_date,
  s.end_date,
  s.status,
  s.created_at,
  s.updated_at
FROM public.project_sprints s
INNER JOIN public.projects p ON p.id = s.project_id
INNER JOIN user_unambiguous_tenant ut ON ut.user_id = p.created_by_user_id;
```
```cypher
UNWIND $batch AS row
MERGE (s:Sprint {id: toInteger(row.id)})
ON CREATE SET
  s.tenant_id = toInteger(row.tenant_id),
  s.project_id = toInteger(row.project_id),
  s.name = row.name,
  s.goal = row.goal,
  s.start_date = CASE WHEN row.start_date IS NOT NULL THEN datetime(row.start_date) ELSE null END,
  s.end_date = CASE WHEN row.end_date IS NOT NULL THEN datetime(row.end_date) ELSE null END,
  s.status = row.status,
  s.created_at = CASE WHEN row.created_at IS NOT NULL THEN datetime(row.created_at) ELSE null END,
  s.updated_at = CASE WHEN row.updated_at IS NOT NULL THEN datetime(row.updated_at) ELSE null END,
  s.last_synced_at = datetime()
ON MATCH SET
  s.tenant_id = toInteger(row.tenant_id),
  s.project_id = toInteger(row.project_id),
  s.name = row.name,
  s.goal = row.goal,
  s.start_date = CASE WHEN row.start_date IS NOT NULL THEN datetime(row.start_date) ELSE null END,
  s.end_date = CASE WHEN row.end_date IS NOT NULL THEN datetime(row.end_date) ELSE null END,
  s.status = row.status,
  s.updated_at = CASE WHEN row.updated_at IS NOT NULL THEN datetime(row.updated_at) ELSE null END,
  s.last_synced_at = datetime();
```

### NM-09: `:KanbanColumn`
```sql
WITH user_unambiguous_tenant AS (
  SELECT user_id, min(tenant_id) AS tenant_id
  FROM (
    SELECT user_id, tenant_id FROM public.tenant_user_memberships WHERE is_deleted = false
    UNION
    SELECT user_id, tenant_id FROM _backup_cleanup_20261005.tenant_user_memberships_deleted
  ) u
  GROUP BY user_id
  HAVING count(DISTINCT tenant_id) = 1
)
SELECT
  k.id,
  ut.tenant_id,
  k.project_id,
  k.title,
  k.status_group,
  k.position,
  COALESCE(k.is_default, false) AS is_default,
  k.created_at,
  k.updated_at
FROM public.kanban_columns k
INNER JOIN public.projects p ON p.id = k.project_id
INNER JOIN user_unambiguous_tenant ut ON ut.user_id = p.created_by_user_id;
```
```cypher
UNWIND $batch AS row
MERGE (k:KanbanColumn {id: toInteger(row.id)})
ON CREATE SET
  k.tenant_id = toInteger(row.tenant_id),
  k.project_id = toInteger(row.project_id),
  k.title = row.title,
  k.status_group = row.status_group,
  k.position = toInteger(row.position),
  k.is_default = row.is_default,
  k.created_at = CASE WHEN row.created_at IS NOT NULL THEN datetime(row.created_at) ELSE null END,
  k.updated_at = CASE WHEN row.updated_at IS NOT NULL THEN datetime(row.updated_at) ELSE null END,
  k.last_synced_at = datetime()
ON MATCH SET
  k.tenant_id = toInteger(row.tenant_id),
  k.project_id = toInteger(row.project_id),
  k.title = row.title,
  k.status_group = row.status_group,
  k.position = toInteger(row.position),
  k.is_default = row.is_default,
  k.updated_at = CASE WHEN row.updated_at IS NOT NULL THEN datetime(row.updated_at) ELSE null END,
  k.last_synced_at = datetime();
```

### NM-10: `:ApprovalRequest`
```sql
WITH user_unambiguous_tenant AS (
  SELECT user_id, min(tenant_id) AS tenant_id
  FROM (
    SELECT user_id, tenant_id FROM public.tenant_user_memberships WHERE is_deleted = false
    UNION
    SELECT user_id, tenant_id FROM _backup_cleanup_20261005.tenant_user_memberships_deleted
  ) u
  GROUP BY user_id
  HAVING count(DISTINCT tenant_id) = 1
)
SELECT
  a.id,
  ut.tenant_id,
  a.code,
  a.request_type,
  a.status,
  a.title,
  a.created_by_user_id,
  a.submitted_at,
  a.completed_at,
  a.start_date,
  a.end_date,
  a.total_days,
  a.leave_type,
  COALESCE(a.is_deleted, false) AS is_deleted,
  a.created_at,
  a.updated_at
FROM public.approval_requests a
INNER JOIN user_unambiguous_tenant ut
  ON ut.user_id = a.created_by_user_id;
```
```cypher
UNWIND $batch AS row
MERGE (a:ApprovalRequest {id: toInteger(row.id)})
ON CREATE SET
  a.tenant_id = toInteger(row.tenant_id),
  a.code = row.code,
  a.request_type = row.request_type,
  a.status = row.status,
  a.title = row.title,
  a.created_by_user_id = toInteger(row.created_by_user_id),
  a.submitted_at = CASE WHEN row.submitted_at IS NOT NULL THEN datetime(row.submitted_at) ELSE null END,
  a.completed_at = CASE WHEN row.completed_at IS NOT NULL THEN datetime(row.completed_at) ELSE null END,
  a.start_date = CASE WHEN row.start_date IS NOT NULL THEN date(row.start_date) ELSE null END,
  a.end_date = CASE WHEN row.end_date IS NOT NULL THEN date(row.end_date) ELSE null END,
  a.total_days = CASE WHEN row.total_days IS NOT NULL THEN toFloat(row.total_days) ELSE null END,
  a.leave_type = row.leave_type,
  a.is_deleted = row.is_deleted,
  a.created_at = CASE WHEN row.created_at IS NOT NULL THEN datetime(row.created_at) ELSE null END,
  a.updated_at = CASE WHEN row.updated_at IS NOT NULL THEN datetime(row.updated_at) ELSE null END,
  a.last_synced_at = datetime()
ON MATCH SET
  a.tenant_id = toInteger(row.tenant_id),
  a.code = row.code,
  a.request_type = row.request_type,
  a.status = row.status,
  a.title = row.title,
  a.submitted_at = CASE WHEN row.submitted_at IS NOT NULL THEN datetime(row.submitted_at) ELSE null END,
  a.completed_at = CASE WHEN row.completed_at IS NOT NULL THEN datetime(row.completed_at) ELSE null END,
  a.start_date = CASE WHEN row.start_date IS NOT NULL THEN date(row.start_date) ELSE null END,
  a.end_date = CASE WHEN row.end_date IS NOT NULL THEN date(row.end_date) ELSE null END,
  a.total_days = CASE WHEN row.total_days IS NOT NULL THEN toFloat(row.total_days) ELSE null END,
  a.leave_type = row.leave_type,
  a.is_deleted = row.is_deleted,
  a.updated_at = CASE WHEN row.updated_at IS NOT NULL THEN datetime(row.updated_at) ELSE null END,
  a.last_synced_at = datetime();
```

### NM-12: `:ScheduleEvent`
```sql
WITH user_unambiguous_tenant AS (
  SELECT user_id, min(tenant_id) AS tenant_id
  FROM (
    SELECT user_id, tenant_id FROM public.tenant_user_memberships WHERE is_deleted = false
    UNION
    SELECT user_id, tenant_id FROM _backup_cleanup_20261005.tenant_user_memberships_deleted
  ) u
  GROUP BY user_id
  HAVING count(DISTINCT tenant_id) = 1
)
SELECT
  e.id,
  ut.tenant_id,
  e.user_id,
  e.title,
  e.description,
  e.event_date,
  e.end_date,
  e.start_time,
  e.end_time,
  e.room_id,
  e.location,
  e.visibility,
  COALESCE(e.is_all_day, false) AS is_all_day,
  e.recurrence_type,
  COALESCE(e.is_deleted, false) AS is_deleted,
  e.created_at,
  e.updated_at
FROM public.schedule_events e
INNER JOIN user_unambiguous_tenant ut
  ON ut.user_id = e.user_id;
```
```cypher
UNWIND $batch AS row
MERGE (e:ScheduleEvent {id: toInteger(row.id)})
ON CREATE SET
  e.tenant_id = toInteger(row.tenant_id),
  e.user_id = toInteger(row.user_id),
  e.title = row.title,
  e.description = row.description,
  e.event_date = date(row.event_date),
  e.end_date = date(row.end_date),
  e.start_time = localtime(row.start_time),
  e.end_time = localtime(row.end_time),
  e.room_id = CASE WHEN row.room_id IS NOT NULL THEN toInteger(row.room_id) ELSE null END,
  e.location = row.location,
  e.visibility = row.visibility,
  e.is_all_day = row.is_all_day,
  e.recurrence_type = row.recurrence_type,
  e.is_deleted = row.is_deleted,
  e.created_at = CASE WHEN row.created_at IS NOT NULL THEN datetime(row.created_at) ELSE null END,
  e.updated_at = CASE WHEN row.updated_at IS NOT NULL THEN datetime(row.updated_at) ELSE null END,
  e.last_synced_at = datetime()
ON MATCH SET
  e.tenant_id = toInteger(row.tenant_id),
  e.user_id = toInteger(row.user_id),
  e.title = row.title,
  e.description = row.description,
  e.event_date = date(row.event_date),
  e.end_date = date(row.end_date),
  e.start_time = localtime(row.start_time),
  e.end_time = localtime(row.end_time),
  e.room_id = CASE WHEN row.room_id IS NOT NULL THEN toInteger(row.room_id) ELSE null END,
  e.location = row.location,
  e.visibility = row.visibility,
  e.is_all_day = row.is_all_day,
  e.recurrence_type = row.recurrence_type,
  e.is_deleted = row.is_deleted,
  e.updated_at = CASE WHEN row.updated_at IS NOT NULL THEN datetime(row.updated_at) ELSE null END,
  e.last_synced_at = datetime();
```

### NM-13: `:ScheduleRoom`
```sql
SELECT
  r.id,
  r.name,
  r.capacity,
  r.description,
  r.sort_order,
  COALESCE(r.is_active, false) AS is_active,
  r.created_at,
  r.updated_at
FROM public.schedule_rooms r;
```
```cypher
UNWIND $batch AS row
MERGE (r:ScheduleRoom {id: toInteger(row.id)})
ON CREATE SET
  r.name = row.name,
  r.capacity = CASE WHEN row.capacity IS NOT NULL THEN toInteger(row.capacity) ELSE null END,
  r.description = row.description,
  r.sort_order = toInteger(row.sort_order),
  r.is_active = row.is_active,
  r.created_at = CASE WHEN row.created_at IS NOT NULL THEN datetime(row.created_at) ELSE null END,
  r.updated_at = CASE WHEN row.updated_at IS NOT NULL THEN datetime(row.updated_at) ELSE null END,
  r.last_synced_at = datetime()
ON MATCH SET
  r.name = row.name,
  r.capacity = CASE WHEN row.capacity IS NOT NULL THEN toInteger(row.capacity) ELSE null END,
  r.description = row.description,
  r.sort_order = toInteger(row.sort_order),
  r.is_active = row.is_active,
  r.updated_at = CASE WHEN row.updated_at IS NOT NULL THEN datetime(row.updated_at) ELSE null END,
  r.last_synced_at = datetime();
```

### NM-14: `:Notice`
```sql
WITH user_unambiguous_tenant AS (
  SELECT user_id, min(tenant_id) AS tenant_id
  FROM public.tenant_user_memberships
  WHERE is_deleted = false
  GROUP BY user_id
  HAVING count(DISTINCT tenant_id) = 1
)
SELECT
  n.id,
  ut.tenant_id,
  n.title,
  n.notice_type,
  n.priority,
  n.audience_id,
  n.created_by_user_id,
  COALESCE(n.is_published, false) AS is_published,
  n.published_at,
  COALESCE(n.is_deleted, false) AS is_deleted,
  n.created_at,
  n.updated_at
FROM public.notices n
INNER JOIN user_unambiguous_tenant ut
  ON ut.user_id = n.created_by_user_id;
```
```cypher
UNWIND $batch AS row
MERGE (n:Notice {id: toInteger(row.id)})
ON CREATE SET
  n.tenant_id = toInteger(row.tenant_id),
  n.title = row.title,
  n.notice_type = row.notice_type,
  n.priority = row.priority,
  n.audience_id = CASE WHEN row.audience_id IS NOT NULL THEN toInteger(row.audience_id) ELSE null END,
  n.created_by_user_id = toInteger(row.created_by_user_id),
  n.is_published = row.is_published,
  n.published_at = CASE WHEN row.published_at IS NOT NULL THEN datetime(row.published_at) ELSE null END,
  n.is_deleted = row.is_deleted,
  n.created_at = CASE WHEN row.created_at IS NOT NULL THEN datetime(row.created_at) ELSE null END,
  n.updated_at = CASE WHEN row.updated_at IS NOT NULL THEN datetime(row.updated_at) ELSE null END,
  n.last_synced_at = datetime()
ON MATCH SET
  n.tenant_id = toInteger(row.tenant_id),
  n.title = row.title,
  n.notice_type = row.notice_type,
  n.priority = row.priority,
  n.audience_id = CASE WHEN row.audience_id IS NOT NULL THEN toInteger(row.audience_id) ELSE null END,
  n.is_published = row.is_published,
  n.published_at = CASE WHEN row.published_at IS NOT NULL THEN datetime(row.published_at) ELSE null END,
  n.is_deleted = row.is_deleted,
  n.updated_at = CASE WHEN row.updated_at IS NOT NULL THEN datetime(row.updated_at) ELSE null END,
  n.last_synced_at = datetime();
```

### NM-15: `:Post`
```sql
WITH user_unambiguous_tenant AS (
  SELECT user_id, min(tenant_id) AS tenant_id
  FROM (
    SELECT user_id, tenant_id FROM public.tenant_user_memberships WHERE is_deleted = false
    UNION
    SELECT user_id, tenant_id FROM _backup_cleanup_20261005.tenant_user_memberships_deleted
  ) u
  GROUP BY user_id
  HAVING count(DISTINCT tenant_id) = 1
)
SELECT
  p.id,
  ut.tenant_id,
  p.author_user_id,
  p.audience_id,
  p.title,
  COALESCE(p.is_deleted, false) AS is_deleted,
  p.created_at,
  p.updated_at
FROM public.talk_posts p
INNER JOIN user_unambiguous_tenant ut
  ON ut.user_id = p.author_user_id;
```
```cypher
UNWIND $batch AS row
MERGE (p:Post {id: toInteger(row.id)})
ON CREATE SET
  p.tenant_id = toInteger(row.tenant_id),
  p.author_user_id = toInteger(row.author_user_id),
  p.audience_id = CASE WHEN row.audience_id IS NOT NULL THEN toInteger(row.audience_id) ELSE null END,
  p.title = row.title,
  p.is_deleted = row.is_deleted,
  p.created_at = CASE WHEN row.created_at IS NOT NULL THEN datetime(row.created_at) ELSE null END,
  p.updated_at = CASE WHEN row.updated_at IS NOT NULL THEN datetime(row.updated_at) ELSE null END,
  p.last_synced_at = datetime()
ON MATCH SET
  p.tenant_id = toInteger(row.tenant_id),
  p.author_user_id = toInteger(row.author_user_id),
  p.audience_id = CASE WHEN row.audience_id IS NOT NULL THEN toInteger(row.audience_id) ELSE null END,
  p.title = row.title,
  p.is_deleted = row.is_deleted,
  p.updated_at = CASE WHEN row.updated_at IS NOT NULL THEN datetime(row.updated_at) ELSE null END,
  p.last_synced_at = datetime();
```

### NM-16: `:Asset`
```sql
WITH user_unambiguous_tenant AS (
  SELECT user_id, min(tenant_id) AS tenant_id
  FROM public.tenant_user_memberships
  WHERE is_deleted = false
  GROUP BY user_id
  HAVING count(DISTINCT tenant_id) = 1
)
SELECT
  a.id,
  COALESCE(d.tenant_id, ut_assign.tenant_id, ut_create.tenant_id) AS tenant_id,
  a.code,
  a.name,
  a.description,
  a.category_id,
  a.status,
  a.location,
  a.department_id,
  a.assigned_user_id,
  a.serial_number,
  a.manufacturer,
  a.acquisition_type,
  a.condition,
  a.created_by_user_id,
  COALESCE(a.is_deleted, false) AS is_deleted,
  a.created_at,
  a.updated_at
FROM public.assets a
LEFT JOIN public.departments d ON d.id = a.department_id
LEFT JOIN user_unambiguous_tenant ut_assign ON ut_assign.user_id = a.assigned_user_id
LEFT JOIN user_unambiguous_tenant ut_create ON ut_create.user_id = a.created_by_user_id
WHERE COALESCE(d.tenant_id, ut_assign.tenant_id, ut_create.tenant_id) IS NOT NULL
  AND (d.tenant_id IS NULL OR ut_assign.tenant_id IS NULL OR d.tenant_id = ut_assign.tenant_id);
```
```cypher
UNWIND $batch AS row
MERGE (a:Asset {id: toInteger(row.id)})
ON CREATE SET
  a.tenant_id = toInteger(row.tenant_id),
  a.code = row.code,
  a.name = row.name,
  a.description = row.description,
  a.category_id = toInteger(row.category_id),
  a.status = row.status,
  a.location = row.location,
  a.department_id = CASE WHEN row.department_id IS NOT NULL THEN toInteger(row.department_id) ELSE null END,
  a.assigned_user_id = CASE WHEN row.assigned_user_id IS NOT NULL THEN toInteger(row.assigned_user_id) ELSE null END,
  a.serial_number = row.serial_number,
  a.manufacturer = row.manufacturer,
  a.acquisition_type = row.acquisition_type,
  a.condition = row.condition,
  a.created_by_user_id = toInteger(row.created_by_user_id),
  a.is_deleted = row.is_deleted,
  a.created_at = CASE WHEN row.created_at IS NOT NULL THEN datetime(row.created_at) ELSE null END,
  a.updated_at = CASE WHEN row.updated_at IS NOT NULL THEN datetime(row.updated_at) ELSE null END,
  a.last_synced_at = datetime()
ON MATCH SET
  a.tenant_id = toInteger(row.tenant_id),
  a.code = row.code,
  a.name = row.name,
  a.description = row.description,
  a.category_id = toInteger(row.category_id),
  a.status = row.status,
  a.location = row.location,
  a.department_id = CASE WHEN row.department_id IS NOT NULL THEN toInteger(row.department_id) ELSE null END,
  a.assigned_user_id = CASE WHEN row.assigned_user_id IS NOT NULL THEN toInteger(row.assigned_user_id) ELSE null END,
  a.serial_number = row.serial_number,
  a.manufacturer = row.manufacturer,
  a.acquisition_type = row.acquisition_type,
  a.condition = row.condition,
  a.is_deleted = row.is_deleted,
  a.updated_at = CASE WHEN row.updated_at IS NOT NULL THEN datetime(row.updated_at) ELSE null END,
  a.last_synced_at = datetime();
```

### NM-17: `:AssetCategory`
```sql
SELECT
  c.id,
  c.code,
  c.name,
  c.parent_id,
  c.sort_order,
  COALESCE(c.is_active, true) AS is_active,
  c.created_at,
  c.updated_at
FROM public.asset_categories c;
```
```cypher
UNWIND $batch AS row
MERGE (c:AssetCategory {id: toInteger(row.id)})
ON CREATE SET
  c.code = row.code,
  c.name = row.name,
  c.parent_id = CASE WHEN row.parent_id IS NOT NULL THEN toInteger(row.parent_id) ELSE null END,
  c.sort_order = toInteger(row.sort_order),
  c.is_active = row.is_active,
  c.created_at = CASE WHEN row.created_at IS NOT NULL THEN datetime(row.created_at) ELSE null END,
  c.updated_at = CASE WHEN row.updated_at IS NOT NULL THEN datetime(row.updated_at) ELSE null END,
  c.last_synced_at = datetime()
ON MATCH SET
  c.code = row.code,
  c.name = row.name,
  c.parent_id = CASE WHEN row.parent_id IS NOT NULL THEN toInteger(row.parent_id) ELSE null END,
  c.sort_order = toInteger(row.sort_order),
  c.is_active = row.is_active,
  c.updated_at = CASE WHEN row.updated_at IS NOT NULL THEN datetime(row.updated_at) ELSE null END,
  c.last_synced_at = datetime();
```

### NM-18: `:FileMetadata`
```sql
WITH user_unambiguous_tenant AS (
  SELECT user_id, min(tenant_id) AS tenant_id
  FROM (
    SELECT user_id, tenant_id FROM public.tenant_user_memberships WHERE is_deleted = false
    UNION
    SELECT user_id, tenant_id FROM _backup_cleanup_20261005.tenant_user_memberships_deleted
  ) u
  GROUP BY user_id
  HAVING count(DISTINCT tenant_id) = 1
)
SELECT
  f.id,
  ut.tenant_id,
  f.storage_provider,
  f.original_name,
  f.content_type,
  f.file_ext,
  f.size_bytes,
  f.uploaded_by_user_id,
  f.uploaded_at,
  f.request_type,
  COALESCE(f.is_deleted, false) AS is_deleted
FROM public.files f
INNER JOIN user_unambiguous_tenant ut
  ON ut.user_id = f.uploaded_by_user_id;
```
```cypher
UNWIND $batch AS row
MERGE (f:FileMetadata {id: toInteger(row.id)})
ON CREATE SET
  f.tenant_id = toInteger(row.tenant_id),
  f.storage_provider = row.storage_provider,
  f.original_name = row.original_name,
  f.content_type = row.content_type,
  f.file_ext = row.file_ext,
  f.size_bytes = toInteger(row.size_bytes),
  f.uploaded_by_user_id = toInteger(row.uploaded_by_user_id),
  f.uploaded_at = CASE WHEN row.uploaded_at IS NOT NULL THEN datetime(row.uploaded_at) ELSE null END,
  f.request_type = row.request_type,
  f.is_deleted = row.is_deleted,
  f.last_synced_at = datetime()
ON MATCH SET
  f.tenant_id = toInteger(row.tenant_id),
  f.storage_provider = row.storage_provider,
  f.original_name = row.original_name,
  f.content_type = row.content_type,
  f.file_ext = row.file_ext,
  f.size_bytes = toInteger(row.size_bytes),
  f.request_type = row.request_type,
  f.is_deleted = row.is_deleted,
  f.last_synced_at = datetime();
```

### NM-19: `:ChatConversation` (ChatMessage Option A)
```sql
WITH user_unambiguous_tenant AS (
  SELECT user_id, min(tenant_id) AS tenant_id
  FROM (
    SELECT user_id, tenant_id FROM public.tenant_user_memberships WHERE is_deleted = false
    UNION
    SELECT user_id, tenant_id FROM _backup_cleanup_20261005.tenant_user_memberships_deleted
  ) u
  GROUP BY user_id
  HAVING count(DISTINCT tenant_id) = 1
)
SELECT
  c.id,
  ut.tenant_id,
  c.conversation_type,
  c.title,
  c.created_by_user_id,
  c.last_message_seq,
  c.created_at,
  c.updated_at
FROM public.chat_conversations c
INNER JOIN user_unambiguous_tenant ut
  ON ut.user_id = c.created_by_user_id;
```
```cypher
UNWIND $batch AS row
MERGE (c:ChatConversation {id: toInteger(row.id)})
ON CREATE SET
  c.tenant_id = toInteger(row.tenant_id),
  c.conversation_type = row.conversation_type,
  c.title = row.title,
  c.created_by_user_id = toInteger(row.created_by_user_id),
  c.last_message_seq = toInteger(row.last_message_seq),
  c.created_at = CASE WHEN row.created_at IS NOT NULL THEN datetime(row.created_at) ELSE null END,
  c.updated_at = CASE WHEN row.updated_at IS NOT NULL THEN datetime(row.updated_at) ELSE null END,
  c.last_synced_at = datetime()
ON MATCH SET
  c.tenant_id = toInteger(row.tenant_id),
  c.conversation_type = row.conversation_type,
  c.title = row.title,
  c.last_message_seq = toInteger(row.last_message_seq),
  c.updated_at = CASE WHEN row.updated_at IS NOT NULL THEN datetime(row.updated_at) ELSE null END,
  c.last_synced_at = datetime();
```

### NM-20: `:Audience` (Dual-Scope Ownership — DEFECT 04 Resolution)
- **System Audience (`is_system = true`)**: Global template (`a.tenant_id = null`), never assigned a default tenant, and validated to have `0` department/user member rows.
- **Custom Audience (`is_system = false`)**: Tenant-scoped (`a.tenant_id = toInteger(row.tenant_id)` NOT NULL), derived from `owner_user_id` and verified against `audience_department_members` and `audience_user_members`.
```sql
WITH user_unambiguous_tenant AS (
  SELECT user_id, min(tenant_id) AS tenant_id
  FROM (
    SELECT user_id, tenant_id FROM public.tenant_user_memberships WHERE is_deleted = false
    UNION
    SELECT user_id, tenant_id FROM _backup_cleanup_20261005.tenant_user_memberships_deleted
  ) u
  GROUP BY user_id
  HAVING count(DISTINCT tenant_id) = 1
),
adm_tenants AS (
  SELECT adm.audience_id,
         count(DISTINCT d.tenant_id) AS dept_tenant_cnt,
         min(d.tenant_id) AS dept_tenant_id
  FROM public.audience_department_members adm
  INNER JOIN public.departments d ON d.id = adm.department_id
  GROUP BY adm.audience_id
),
aum_tenants AS (
  SELECT aum.audience_id,
         count(DISTINCT ut.tenant_id) AS user_tenant_cnt,
         min(ut.tenant_id) AS user_tenant_id
  FROM public.audience_user_members aum
  INNER JOIN user_unambiguous_tenant ut ON ut.user_id = aum.user_id
  GROUP BY aum.audience_id
)
SELECT
  a.id,
  CASE
    WHEN COALESCE(a.is_system, false) = true THEN NULL::bigint
    ELSE ut.tenant_id
  END AS tenant_id,
  a.code,
  a.name,
  a.audience_type,
  COALESCE(a.is_system, false) AS is_system,
  a.owner_user_id,
  COALESCE(a.is_active, true) AS is_active,
  a.created_at,
  a.updated_at
FROM public.audiences a
LEFT JOIN user_unambiguous_tenant ut ON ut.user_id = a.owner_user_id
LEFT JOIN adm_tenants adm ON adm.audience_id = a.id
LEFT JOIN aum_tenants aum ON aum.audience_id = a.id
WHERE (
  -- Case 1: Global System Audience (tenant_id IS NULL, no explicit member rows)
  COALESCE(a.is_system, false) = true
  AND a.owner_user_id IS NULL
  AND adm.audience_id IS NULL
  AND aum.audience_id IS NULL
) OR (
  -- Case 2: Custom Tenant-Scoped Audience (unambiguous owner & member tenant match)
  COALESCE(a.is_system, false) = false
  AND ut.tenant_id IS NOT NULL
  AND (adm.audience_id IS NULL OR (adm.dept_tenant_cnt = 1 AND adm.dept_tenant_id = ut.tenant_id))
  AND (aum.audience_id IS NULL OR (aum.user_tenant_cnt = 1 AND aum.user_tenant_id = ut.tenant_id))
);
```
```cypher
UNWIND $batch AS row
MERGE (a:Audience {id: toInteger(row.id)})
ON CREATE SET
  a.tenant_id = CASE WHEN row.is_system = true OR row.tenant_id IS NULL THEN null ELSE toInteger(row.tenant_id) END,
  a.code = row.code,
  a.name = row.name,
  a.audience_type = row.audience_type,
  a.is_system = row.is_system,
  a.owner_user_id = CASE WHEN row.owner_user_id IS NOT NULL THEN toInteger(row.owner_user_id) ELSE null END,
  a.is_active = row.is_active,
  a.created_at = CASE WHEN row.created_at IS NOT NULL THEN datetime(row.created_at) ELSE null END,
  a.updated_at = CASE WHEN row.updated_at IS NOT NULL THEN datetime(row.updated_at) ELSE null END,
  a.last_synced_at = datetime()
ON MATCH SET
  a.tenant_id = CASE WHEN row.is_system = true OR row.tenant_id IS NULL THEN null ELSE toInteger(row.tenant_id) END,
  a.code = row.code,
  a.name = row.name,
  a.audience_type = row.audience_type,
  a.is_system = row.is_system,
  a.owner_user_id = CASE WHEN row.owner_user_id IS NOT NULL THEN toInteger(row.owner_user_id) ELSE null END,
  a.is_active = row.is_active,
  a.updated_at = CASE WHEN row.updated_at IS NOT NULL THEN datetime(row.updated_at) ELSE null END,
  a.last_synced_at = datetime();
```

### NM-21: `:LeaveBalance` (Unambiguous Leave Tenant Derivation — CRITICAL-02 Resolution)
- **Strict Alignment with `Doc 29` Section 3.2 and `Doc 31` `RM-36`**:
  - Derives `tenant_id` via `user_unambiguous_leave_tenant`, joining `public.tenant_user_memberships m` (`m.is_deleted = false AND m.status IN ('active', 'inactive', 'suspended')`), `public.user_profiles up` (`up.user_id = m.user_id AND up.tenant_id = m.tenant_id`), and `public.users u` (`COALESCE(u.is_deleted, false) = false`) with `HAVING count(DISTINCT m.tenant_id) = 1`.
  - Preserves historical annual leave balances for resigned/inactive employees in a single tenant (`Case 1` active & `Case 2` historical single-tenant), while quarantining any multi-tenant user (`count(DISTINCT m.tenant_id) > 1` -> `AMBIGUOUS_TENANT`) or user without non-deleted membership (`INVALID_TENANT`).
```sql
WITH monthly_agg AS (
  SELECT
    mb.user_id,
    mb.year,
    SUM(mb.accrued_days) AS accrued_days,
    SUM(mb.used_days) AS used_days
  FROM public.user_leave_monthly_balances mb
  GROUP BY mb.user_id, mb.year
),
user_unambiguous_leave_tenant AS (
  SELECT
    m.user_id,
    min(m.tenant_id) AS tenant_id
  FROM public.tenant_user_memberships m
  INNER JOIN public.users u
    ON u.id = m.user_id
   AND COALESCE(u.is_deleted, false) = false
  INNER JOIN public.user_profiles up
    ON up.user_id = m.user_id
   AND up.tenant_id = m.tenant_id
  WHERE m.is_deleted = false
    AND m.status IN ('active', 'inactive', 'suspended')
  GROUP BY m.user_id
  HAVING count(DISTINCT m.tenant_id) = 1
)
SELECT
  yb.id,
  ult.tenant_id,
  yb.user_id,
  yb.year,
  yb.opening_days,
  yb.carryover_days,
  yb.seniority_days,
  yb.manual_adjustment_days,
  COALESCE(ma.accrued_days, 0) AS accrued_days,
  COALESCE(ma.used_days, 0) AS used_days,
  yb.remaining_days,
  yb.carryover_available_days,
  yb.created_at,
  yb.updated_at
FROM public.user_leave_year_balances yb
INNER JOIN user_unambiguous_leave_tenant ult ON ult.user_id = yb.user_id
LEFT JOIN monthly_agg ma ON ma.user_id = yb.user_id AND ma.year = yb.year;
```
```cypher
UNWIND $batch AS row
MERGE (lb:LeaveBalance {id: toInteger(row.id)})
ON CREATE SET
  lb.tenant_id = toInteger(row.tenant_id),
  lb.user_id = toInteger(row.user_id),
  lb.year = toInteger(row.year),
  lb.opening_days = toFloat(row.opening_days),
  lb.carryover_days = toFloat(row.carryover_days),
  lb.seniority_days = toFloat(row.seniority_days),
  lb.manual_adjustment_days = toFloat(row.manual_adjustment_days),
  lb.accrued_days = toFloat(row.accrued_days),
  lb.used_days = toFloat(row.used_days),
  lb.remaining_days = toFloat(row.remaining_days),
  lb.carryover_available_days = toFloat(row.carryover_available_days),
  lb.created_at = datetime(row.created_at),
  lb.updated_at = datetime(row.updated_at),
  lb.last_synced_at = datetime()
ON MATCH SET
  lb.tenant_id = toInteger(row.tenant_id),
  lb.user_id = toInteger(row.user_id),
  lb.year = toInteger(row.year),
  lb.opening_days = toFloat(row.opening_days),
  lb.carryover_days = toFloat(row.carryover_days),
  lb.seniority_days = toFloat(row.seniority_days),
  lb.manual_adjustment_days = toFloat(row.manual_adjustment_days),
  lb.accrued_days = toFloat(row.accrued_days),
  lb.used_days = toFloat(row.used_days),
  lb.remaining_days = toFloat(row.remaining_days),
  lb.carryover_available_days = toFloat(row.carryover_available_days),
  lb.updated_at = datetime(row.updated_at),
  lb.last_synced_at = datetime();
```

### NM-22: `:AttendanceRecord` (6-Step Deterministic Active-Membership Resolution — DEFECT 02 & CRITICAL-01 Resolution)
- **Strict Alignment with `Doc 29` Section 3.1 and `Doc 31` `RM-37`**:
  - Both `valid_user_tenant` and `emp_number_resolution` CTEs explicitly enforce **`m.status = 'active' AND m.is_deleted = false AND COALESCE(u.is_deleted, false) = false`** (`Rule MEM-ACTIVE`, `Case A`).
  - Only rows classified as `RESOLVED_BY_USER_ID` or `RESOLVED_BY_EMPLOYEE_NUMBER` (where `employee_code` maps to **exactly one** `user_id` and **exactly one** `tenant_id` in `user_profiles` with active tenant membership `m.status = 'active' AND m.is_deleted = false`) are extracted into `:AttendanceRecord`.
  - Rows with `m.status IN ('inactive', 'suspended')` (`Cases B, C, E`), `m.is_deleted = true` (`Cases D, E`), `UNRESOLVED`, `AMBIGUOUS`, `INVALID_TENANT`, or `INVALID_SOURCE_REFERENCE` are routed to `etl_quarantine_log` and are **never** loaded as unlinked `:AttendanceRecord` nodes in Neo4j.
```sql
WITH valid_user_tenant AS (
  SELECT
    up.user_id,
    min(up.tenant_id) AS tenant_id
  FROM public.user_profiles up
  INNER JOIN public.users u
    ON u.id = up.user_id
   AND COALESCE(u.is_deleted, false) = false
  INNER JOIN public.tenant_user_memberships m
    ON m.user_id = up.user_id
   AND m.tenant_id = up.tenant_id
   AND m.status = 'active'
   AND m.is_deleted = false
  GROUP BY up.user_id
  HAVING count(DISTINCT up.tenant_id) = 1
),
emp_number_resolution AS (
  SELECT
    up.employee_number,
    count(DISTINCT up.user_id) AS user_cnt,
    count(DISTINCT up.tenant_id) AS tenant_cnt,
    min(up.user_id) AS resolved_user_id,
    min(up.tenant_id) AS resolved_tenant_id
  FROM public.user_profiles up
  INNER JOIN public.users u
    ON u.id = up.user_id
   AND COALESCE(u.is_deleted, false) = false
  INNER JOIN public.tenant_user_memberships m
    ON m.user_id = up.user_id
   AND m.tenant_id = up.tenant_id
   AND m.status = 'active'
   AND m.is_deleted = false
  WHERE up.employee_number IS NOT NULL
  GROUP BY up.employee_number
),
classified_attendance AS (
  SELECT
    a.id,
    a.employee_code,
    a.user_id AS source_user_id,
    a.work_date,
    a.first_check_in,
    a.last_check_out,
    a.swipe_count,
    a.status,
    a.is_late,
    a.is_early_leave,
    a.actual_minutes,
    a.created_at,
    a.updated_at,
    CASE
      WHEN a.user_id IS NOT NULL AND (u_direct.id IS NULL OR COALESCE(u_direct.is_deleted, false) = true) THEN 'INVALID_SOURCE_REFERENCE'
      WHEN a.user_id IS NOT NULL AND vut.user_id IS NULL THEN 'INVALID_TENANT'
      WHEN a.user_id IS NOT NULL AND vut.user_id IS NOT NULL THEN 'RESOLVED_BY_USER_ID'
      WHEN a.user_id IS NULL AND enr.employee_number IS NULL THEN 'UNRESOLVED'
      WHEN a.user_id IS NULL AND (enr.user_cnt > 1 OR enr.tenant_cnt > 1) THEN 'AMBIGUOUS'
      WHEN a.user_id IS NULL AND enr.user_cnt = 1 AND enr.tenant_cnt = 1 THEN 'RESOLVED_BY_EMPLOYEE_NUMBER'
      ELSE 'INVALID_TENANT'
    END AS resolution_status,
    CASE
      WHEN a.user_id IS NOT NULL THEN vut.user_id
      WHEN a.user_id IS NULL AND enr.user_cnt = 1 AND enr.tenant_cnt = 1 THEN enr.resolved_user_id
      ELSE NULL
    END AS resolved_user_id,
    CASE
      WHEN a.user_id IS NOT NULL THEN vut.tenant_id
      WHEN a.user_id IS NULL AND enr.user_cnt = 1 AND enr.tenant_cnt = 1 THEN enr.resolved_tenant_id
      ELSE NULL
    END AS tenant_id
  FROM public.attendance_daily_records a
  LEFT JOIN public.users u_direct ON u_direct.id = a.user_id
  LEFT JOIN valid_user_tenant vut ON vut.user_id = a.user_id
  LEFT JOIN emp_number_resolution enr ON a.user_id IS NULL AND enr.employee_number = a.employee_code
)
SELECT
  id,
  tenant_id,
  employee_code,
  resolved_user_id,
  resolution_status,
  work_date,
  first_check_in,
  last_check_out,
  swipe_count,
  status,
  is_late,
  is_early_leave,
  actual_minutes,
  created_at,
  updated_at
FROM classified_attendance
WHERE resolution_status IN ('RESOLVED_BY_USER_ID', 'RESOLVED_BY_EMPLOYEE_NUMBER');
```
```cypher
UNWIND $batch AS row
MERGE (ar:AttendanceRecord {id: toInteger(row.id)})
ON CREATE SET
  ar.tenant_id = toInteger(row.tenant_id),
  ar.employee_code = row.employee_code,
  ar.user_id = toInteger(row.resolved_user_id),
  ar.resolution_status = row.resolution_status,
  ar.work_date = date(row.work_date),
  ar.first_check_in = CASE WHEN row.first_check_in IS NOT NULL THEN datetime(row.first_check_in) ELSE null END,
  ar.last_check_out = CASE WHEN row.last_check_out IS NOT NULL THEN datetime(row.last_check_out) ELSE null END,
  ar.swipe_count = toInteger(row.swipe_count),
  ar.status = row.status,
  ar.is_late = row.is_late,
  ar.is_early_leave = row.is_early_leave,
  ar.actual_minutes = toInteger(row.actual_minutes),
  ar.created_at = datetime(row.created_at),
  ar.updated_at = datetime(row.updated_at),
  ar.last_synced_at = datetime()
ON MATCH SET
  ar.tenant_id = toInteger(row.tenant_id),
  ar.employee_code = row.employee_code,
  ar.user_id = toInteger(row.resolved_user_id),
  ar.resolution_status = row.resolution_status,
  ar.work_date = date(row.work_date),
  ar.first_check_in = CASE WHEN row.first_check_in IS NOT NULL THEN datetime(row.first_check_in) ELSE null END,
  ar.last_check_out = CASE WHEN row.last_check_out IS NOT NULL THEN datetime(row.last_check_out) ELSE null END,
  ar.swipe_count = toInteger(row.swipe_count),
  ar.status = row.status,
  ar.is_late = row.is_late,
  ar.is_early_leave = row.is_early_leave,
  ar.actual_minutes = toInteger(row.actual_minutes),
  ar.updated_at = datetime(row.updated_at),
  ar.last_synced_at = datetime();
```

### NM-23: `:ContractHistory`
```sql
SELECT
  ch.id,
  ch.tenant_id,
  ch.user_id,
  ch.contract_type,
  ch.contract_period_from,
  ch.contract_period_to,
  ch.is_current,
  ch.created_at,
  ch.updated_at
FROM public.user_contract_histories ch;
```
```cypher
UNWIND $batch AS row
MERGE (ch:ContractHistory {id: toInteger(row.id)})
ON CREATE SET
  ch.tenant_id = toInteger(row.tenant_id),
  ch.user_id = toInteger(row.user_id),
  ch.contract_type = row.contract_type,
  ch.contract_period_from = CASE WHEN row.contract_period_from IS NOT NULL THEN date(row.contract_period_from) ELSE null END,
  ch.contract_period_to = CASE WHEN row.contract_period_to IS NOT NULL THEN date(row.contract_period_to) ELSE null END,
  ch.is_current = row.is_current,
  ch.created_at = datetime(row.created_at),
  ch.updated_at = datetime(row.updated_at),
  ch.last_synced_at = datetime()
ON MATCH SET
  ch.tenant_id = toInteger(row.tenant_id),
  ch.user_id = toInteger(row.user_id),
  ch.contract_type = row.contract_type,
  ch.contract_period_from = CASE WHEN row.contract_period_from IS NOT NULL THEN date(row.contract_period_from) ELSE null END,
  ch.contract_period_to = CASE WHEN row.contract_period_to IS NOT NULL THEN date(row.contract_period_to) ELSE null END,
  ch.is_current = row.is_current,
  ch.updated_at = datetime(row.updated_at),
  ch.last_synced_at = datetime();
```

### NM-24: `:Tag` (Semantic Taxonomy from `project_tags` and `talk_tags` — CRITICAL-06 Synthetic Key `tag_key`)
```sql
WITH user_unambiguous_tenant AS (
  SELECT user_id, min(tenant_id) AS tenant_id
  FROM (
    SELECT user_id, tenant_id FROM public.tenant_user_memberships WHERE is_deleted = false
    UNION
    SELECT user_id, tenant_id FROM _backup_cleanup_20261005.tenant_user_memberships_deleted
  ) u
  GROUP BY user_id
  HAVING count(DISTINCT tenant_id) = 1
)
SELECT
  'project:' || pt.id::text AS tag_key,
  pt.id AS source_id,
  'project' AS tag_scope,
  pt.project_id AS project_id,
  ut.tenant_id AS tenant_id,
  pt.name AS name,
  pt.color AS color,
  pt.created_at AS created_at
FROM public.project_tags pt
INNER JOIN public.projects p ON p.id = pt.project_id
INNER JOIN user_unambiguous_tenant ut ON ut.user_id = p.created_by_user_id
UNION ALL
SELECT
  'talk:' || tt.id::text AS tag_key,
  tt.id AS source_id,
  'talk' AS tag_scope,
  NULL::bigint AS project_id,
  min(ut.tenant_id) AS tenant_id,
  tt.name AS name,
  NULL::text AS color,
  tt.created_at AS created_at
FROM public.talk_tags tt
INNER JOIN public.talk_post_tags tpt ON tpt.tag_id = tt.id
INNER JOIN public.talk_posts tp ON tp.id = tpt.post_id
INNER JOIN user_unambiguous_tenant ut ON ut.user_id = tp.author_user_id
GROUP BY tt.id, tt.name, tt.created_at
HAVING count(DISTINCT ut.tenant_id) = 1;
```
```cypher
UNWIND $batch AS row
MERGE (tg:Tag {tag_key: row.tag_key})
ON CREATE SET
  tg.source_id = toInteger(row.source_id),
  tg.tag_scope = row.tag_scope,
  tg.project_id = CASE WHEN row.project_id IS NOT NULL THEN toInteger(row.project_id) ELSE null END,
  tg.tenant_id = toInteger(row.tenant_id),
  tg.name = row.name,
  tg.color = row.color,
  tg.created_at = CASE WHEN row.created_at IS NOT NULL THEN datetime(row.created_at) ELSE null END,
  tg.last_synced_at = datetime()
ON MATCH SET
  tg.name = row.name,
  tg.color = row.color,
  tg.last_synced_at = datetime();
```

### NM-25: `:KnowledgeDocument` (Semantic Document Node from `project_common_documents`)
```sql
WITH user_unambiguous_tenant AS (
  SELECT user_id, min(tenant_id) AS tenant_id
  FROM (
    SELECT user_id, tenant_id FROM public.tenant_user_memberships WHERE is_deleted = false
    UNION
    SELECT user_id, tenant_id FROM _backup_cleanup_20261005.tenant_user_memberships_deleted
  ) u
  GROUP BY user_id
  HAVING count(DISTINCT tenant_id) = 1
)
SELECT
  pcd.id,
  ut.tenant_id,
  pcd.project_id,
  pcd.file_id,
  COALESCE(pcd.title, f.original_name) AS title,
  pcd.sort_order,
  pcd.uploaded_by_id,
  pcd.is_deleted,
  pcd.created_at,
  pcd.updated_at
FROM public.project_common_documents pcd
INNER JOIN public.projects p ON p.id = pcd.project_id
INNER JOIN user_unambiguous_tenant ut ON ut.user_id = p.created_by_user_id
LEFT JOIN public.files f ON f.id = pcd.file_id;
```
```cypher
UNWIND $batch AS row
MERGE (kd:KnowledgeDocument {id: toInteger(row.id)})
ON CREATE SET
  kd.tenant_id = toInteger(row.tenant_id),
  kd.project_id = toInteger(row.project_id),
  kd.file_id = toInteger(row.file_id),
  kd.title = row.title,
  kd.sort_order = toInteger(row.sort_order),
  kd.uploaded_by_id = toInteger(row.uploaded_by_id),
  kd.is_deleted = row.is_deleted,
  kd.created_at = datetime(row.created_at),
  kd.updated_at = datetime(row.updated_at),
  kd.last_synced_at = datetime()
ON MATCH SET
  kd.tenant_id = toInteger(row.tenant_id),
  kd.project_id = toInteger(row.project_id),
  kd.file_id = toInteger(row.file_id),
  kd.title = row.title,
  kd.sort_order = toInteger(row.sort_order),
  kd.is_deleted = row.is_deleted,
  kd.updated_at = datetime(row.updated_at),
  kd.last_synced_at = datetime();
```
