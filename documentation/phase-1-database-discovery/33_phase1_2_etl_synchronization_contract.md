# PHASE 1.2 / 1.2.1 / 1.2.2 – ETL & SYNCHRONIZATION CONTRACT SPECIFICATION (WORK PACKAGE 5)
## Groupware AI Chatbot – PostgreSQL 18.6 to Neo4j + Vector Database

**Document ID:** `33_phase1_2_etl_synchronization_contract.md`  
**Phase:** Phase 1.2 / Phase 1.2.1 / Phase 1.2.2 – ETL Lifecycle, Tenant Security & Runtime Evidence Hardening (Updates Phase 1.2 Baseline for **DEFECT 01**, **DEFECT 02**, **CRITICAL-01**, **CRITICAL-02**, **CRITICAL-06**)  
**Date:** 2026-11-05  
**Status:** Canonical Architecture Specification  
**Evidence Level:** `DESIGNED` & `STATICALLY VALIDATED` (Verified against `30_phase1_2_complete_node_mapping.md`, `31_phase1_2_complete_relationship_mapping.md`, and `artifacts/database-discovery/schema_inventory.json`)

---

## 1. Executive Summary & Architectural Scope

In Phase 1.1 (`24_phase1_1_final_source_to_graph_mapping.md`), ETL mapping was specified as one-time `MERGE ... SET` statements without a synchronization lifecycle contract. In Phase 1.2.1, this document was updated to resolve **DEFECT 01** (synchronizing all Node IDs `NM-01`–`NM-25` and Relationship IDs `RM-01`–`RM-45`) and **DEFECT 02** (enforcing the 6-step attendance resolution quarantine rule).

In **Phase 1.2.2**, this contract is further hardened to resolve:
1. **`CRITICAL-01` (Attendance Active Membership Validation)**: Enforces `m.status = 'active' AND m.is_deleted = false AND COALESCE(u.is_deleted, false) = false` (`Rule MEM-ACTIVE`) in `NM-22` (`:AttendanceRecord`) and `RM-37` (`[:HAS_ATTENDANCE]`), and documents active vs. historical membership rules across all ETL waves.
2. **`CRITICAL-02` (`NM-21` `:LeaveBalance` Tenant Derivation & Dual-Table Incremental Trigger)**: Enforces unambiguous tenant derivation (`user_unambiguous_leave_tenant`) across `tenant_user_memberships` and `user_profiles` (`COUNT(DISTINCT tenant_id) = 1`), multi-table watermark tracking (`GREATEST(yb.updated_at, MAX(mb.updated_at))`), and multi-tenant ambiguity quarantine (`SD-07`).
3. **`CRITICAL-06` (Per-Node Reconciliation & Safe Hard-Delete Contract)**: Replaces generic `SELECT id` reconciliation with a **7-Pattern, 24-Node Per-Node Reconciliation & Safe Deletion Specification** covering synthetic keys (`NM-24` `:Tag.tag_key`), 6-step conditionally eligible records (`NM-22` `:AttendanceRecord`), multi-table aggregations (`NM-21` `:LeaveBalance`), dual-scope nodes (`NM-20` `:Audience`), transitive-tenant CTEs, and a `5%` circuit-breaker safety threshold (`MAX_DELETE_RATIO = 0.05`). Also corrects the Wave 3 header count to **`11 Nodes`** (`5 + 3 + 11 + 5 = 24 Approved MVP Nodes`).

---

## 2. The 15 Mandatory ETL Lifecycle Behaviors

### 2.1 Behavior 1: Initial Full Load (5-Wave Topological Order — Canonical IDs)

To guarantee that target nodes exist before relationships are created and that parent tenant contexts (`:Tenant`, `:Project`, `:Department`) are established before child entities, the initial full load MUST execute in **5 deterministic topological waves** using the exact canonical IDs from `Doc 30` and `Doc 31` (`5 + 3 + 11 + 5 = 24 Approved MVP Nodes` and `42 Approved MVP Relationships`):

#### Wave 1 – Root Identity, Organization & Global Catalogs (5 Nodes)
1. `NM-01` (`:Tenant` <- `public.tenants`, `1` row)
2. `NM-02` (`:User` <- `public.users` + `LEFT JOIN public.user_profiles` on default membership, `360` rows)
3. `NM-03` (`:Department` <- `public.departments`, `103` rows — retain all `103` rows including `is_active = false`)
4. `NM-04` (`:Role` <- `public.roles`, `42` rows)
5. `NM-05` (`:Permission` <- `public.permissions`, `247` rows)

#### Wave 2 – Facility, Asset & Dual-Scope Targeting Catalogs (3 Nodes)
6. `NM-13` (`:ScheduleRoom` <- `public.schedule_rooms`, `13` rows — retain all `13` rows)
7. `NM-17` (`:AssetCategory` <- `public.asset_categories`, `30` rows)
8. `NM-20` (`:Audience` <- `public.audiences`, `116` rows — Dual-Scope: `1` system template with `tenant_id = NULL`, `115` custom tenant-scoped rows with `tenant_id IS NOT NULL`)

#### Wave 3 – Primary Operational Domain Nodes (11 Nodes)
9. `NM-06` (`:Project` <- `public.projects`, `65` rows)
10. `NM-08` (`:Sprint` <- `public.project_sprints`, `40` rows)
11. `NM-09` (`:KanbanColumn` <- `public.kanban_columns`, `268` rows)
12. `NM-07` (`:Ticket` <- `public.tickets`, `668` rows)
13. `NM-10` (`:ApprovalRequest` <- `public.approval_requests`, `4,709` rows)
14. `NM-12` (`:ScheduleEvent` <- `public.schedule_events`, `349` rows)
15. `NM-14` (`:Notice` <- `public.notices`, `99` rows)
16. `NM-15` (`:Post` <- `public.talk_posts`, `247` rows)
17. `NM-16` (`:Asset` <- `public.assets`, `685` rows)
18. `NM-18` (`:FileMetadata` <- `public.files`, `3,255` rows)
19. `NM-19` (`:ChatConversation` <- `public.chat_conversations`, `329` rows — ChatMessage Option A)

#### Wave 4 – HR Operational Nodes & Approved MVP Semantic Nodes (5 Nodes)
20. `NM-21` (`:LeaveBalance` <- `public.user_leave_year_balances` + `public.user_leave_monthly_balances`, `353` rows — `user_unambiguous_leave_tenant` `CRITICAL-02`)
21. `NM-22` (`:AttendanceRecord` <- `public.attendance_daily_records`, `24,764` resolved rows loaded; `29,725` unresolved rows quarantined — `m.status = 'active' AND m.is_deleted = false` `CRITICAL-01`)
22. `NM-23` (`:ContractHistory` <- `public.user_contract_histories`, `457` rows)
23. `NM-24` (`:Tag` <- `public.project_tags` `20` + `public.talk_tags` `10` = `30` rows via synthetic `tag_key`)
24. `NM-25` (`:KnowledgeDocument` <- `public.project_common_documents`, `40` rows)

*(Note: `ND-11` `:WorkflowTemplate` is `MVP – BLOCKED`; `ND-26` `:Topic` and `ND-27` `:BusinessConcept` are `FUTURE` and excluded from MVP ETL waves.)*

#### Wave 5 – All Approved MVP Graph Relationships (42 Relationships: `RM-01`–`RM-18`, `RM-20`–`RM-43`)
- **Group 5A (Identity, Org & RBAC — 8 Relationships)**:
  - `RM-01`: `(:User)-[:MEMBER_OF]->(:Tenant)` (`public.tenant_user_memberships` + `LEFT JOIN public.user_profiles`)
  - `RM-02`: `(:Department)-[:BELONGS_TO_TENANT]->(:Tenant)` (`public.departments`)
  - `RM-03`: `(:User)-[:MEMBER_OF_DEPARTMENT]->(:Department)` (`public.department_members` — sets `effective_from`, `effective_to`, `is_active`)
  - `RM-04`: `(:User)-[:MANAGES]->(:Department)` (`public.departments.manager_user_id` — `HIGH-05` active manager membership guard)
  - `RM-05`: `(:Department)-[:SUB_DEPARTMENT_OF]->(:Department)` (`public.departments.parent_id`)
  - `RM-06`: `(:User)-[:HAS_ROLE]->(:Role)` (`public.user_role_assignments`)
  - `RM-07`: `(:Role)-[:INCLUDES_PERMISSION]->(:Permission)` (`public.role_permissions`)
  - `RM-08`: `(:User)-[:DIRECT_PERMISSION]->(:Permission)` (`public.user_permissions`)
- **Group 5B (Project, Ticket, Sprint & Kanban — 9 Relationships)**:
  - `RM-09`: `(:Project)-[:CREATED_BY]->(:User)` (`public.projects.created_by_user_id`)
  - `RM-10`: `(:User)-[:MEMBER_OF_PROJECT]->(:Project)` (`public.project_members`)
  - `RM-11`: `(:Ticket)-[:BELONGS_TO_PROJECT]->(:Project)` (`public.tickets.project_id`)
  - `RM-12`: `(:Ticket)-[:CREATED_BY]->(:User)` (`public.tickets.created_by_user_id`)
  - `RM-13`: `(:Ticket)-[:ASSIGNED_TO]->(:User)` (`public.ticket_assignees`)
  - `RM-14`: `(:Ticket)-[:PART_OF_SPRINT]->(:Sprint)` (`public.tickets.sprint_id`)
  - `RM-15`: `(:Ticket)-[:IN_STAGE]->(:KanbanColumn)` (`public.tickets.column_id`)
  - `RM-16`: `(:Sprint)-[:SPRINT_OF_PROJECT]->(:Project)` (`public.project_sprints.project_id`)
  - `RM-17`: `(:KanbanColumn)-[:COLUMN_OF_PROJECT]->(:Project)` (`public.kanban_columns.project_id`)
- **Group 5C (Approvals, Schedule, Notices, Posts & Audiences — 11 Relationships; `RM-19` Blocked)**:
  - `RM-18`: `(:ApprovalRequest)-[:CREATED_BY]->(:User)` (`public.approval_requests.created_by_user_id`)
  - *(`RM-19`: `[:USES_TEMPLATE]` is `REJECTED / BLOCKED` and excluded from ETL)*
  - `RM-20`: `(:User)-[:PARTICIPATES_IN]->(:ApprovalRequest)` (`public.approval_participants` — keyed by `participant_role`, stores `sequence_order`)
  - `RM-21`: `(:ScheduleEvent)-[:ORGANIZED_BY]->(:User)` (`public.schedule_events.user_id`)
  - `RM-22`: `(:ScheduleEvent)-[:HELD_IN]->(:ScheduleRoom)` (`public.schedule_events.room_id`)
  - `RM-23`: `(:User)-[:ATTENDS_EVENT]->(:ScheduleEvent)` (`public.schedule_event_participants`)
  - `RM-24`: `(:Notice)-[:PUBLISHED_BY]->(:User)` (`public.notices.created_by_user_id`)
  - `RM-25`: `(:Notice)-[:TARGETED_TO]->(:Audience)` (`public.notices.audience_id` — Dual-Scope validated)
  - `RM-26`: `(:Audience)-[:INCLUDES_DEPARTMENT]->(:Department)` (`public.audience_department_members` — custom audiences only, `a.is_system = false`)
  - `RM-27`: `(:Audience)-[:INCLUDES_USER]->(:User)` (`public.audience_user_members` — custom audiences only, `a.is_system = false`)
  - `RM-28`: `(:Post)-[:AUTHORED_BY]->(:User)` (`public.talk_posts.author_user_id`)
  - `RM-29`: `(:Post)-[:TARGETED_TO]->(:Audience)` (`public.talk_posts.audience_id` — Dual-Scope validated)
- **Group 5D (Assets, Files, Chat & HR — 9 Relationships)**:
  - `RM-30`: `(:Asset)-[:ASSIGNED_TO]->(:User)` (`public.assets.assigned_user_id`)
  - `RM-31`: `(:Asset)-[:LOCATED_IN]->(:Department)` (`public.assets.department_id`)
  - `RM-32`: `(:Asset)-[:CATEGORIZED_AS]->(:AssetCategory)` (`public.assets.category_id`)
  - `RM-33`: `(:FileMetadata)-[:UPLOADED_BY]->(:User)` (`public.files.uploaded_by_user_id`)
  - `RM-34`: `(:User)-[:MEMBER_OF_CONVERSATION]->(:ChatConversation)` (`public.chat_conversation_members`)
  - `RM-35`: `(:ChatConversation)-[:CREATED_BY]->(:User)` (`public.chat_conversations.created_by_user_id`)
  - `RM-36`: `(:User)-[:HAS_LEAVE_BALANCE]->(:LeaveBalance)` (`public.user_leave_year_balances` — `user_unambiguous_leave_tenant` `CRITICAL-02`)
  - `RM-37`: `(:User)-[:HAS_ATTENDANCE]->(:AttendanceRecord)` (`public.attendance_daily_records` — 6-Step active-membership resolved `CRITICAL-01`)
  - `RM-38`: `(:User)-[:HAS_CONTRACT]->(:ContractHistory)` (`public.user_contract_histories`)
- **Group 5E (Semantic Knowledge Graph — 5 Approved MVP Relationships; `RM-44`, `RM-45` Future)**:
  - `RM-39`: `(:Project)-[:HAS_TAG]->(:Tag)` (`public.project_tags`)
  - `RM-40`: `(:Ticket)-[:TAGGED_WITH]->(:Tag)` (`public.ticket_tags`)
  - `RM-41`: `(:Post)-[:TAGGED_WITH]->(:Tag)` (`public.talk_post_tags`)
  - `RM-42`: `(:KnowledgeDocument)-[:ASSOCIATED_WITH]->(:Project)` (`public.project_common_documents.project_id`)
  - `RM-43`: `(:KnowledgeDocument)-[:STORED_AS_FILE]->(:FileMetadata)` (`public.project_common_documents.file_id`)

---

### 2.2 Behavior 2: Incremental Synchronization (Watermark & Keyset Pagination)
- **Tables with `updated_at` (`21` of `24` node sources)**:
  - Extract rows where `updated_at >= :last_watermark_ts - INTERVAL '5 minutes'` (5-minute safety overlap window for clock skew and long-running transactions).
  - **Multi-Table Watermark for `NM-21` (`:LeaveBalance` — `CRITICAL-02`)**: Because `:LeaveBalance` aggregates `public.user_leave_year_balances` (`yb`) and `public.user_leave_monthly_balances` (`mb`), incremental extraction selects any `(user_id, year)` where `yb.updated_at >= :watermark` **OR** `EXISTS (SELECT 1 FROM public.user_leave_monthly_balances mb WHERE mb.user_id = yb.user_id AND mb.year = yb.year AND mb.updated_at >= :watermark)`.
- **Append-Only / Timestamp-Limited Tables (`permissions`, `files`, `project_tags`, `talk_tags`, `ticket_assignees`, `role_permissions`, `user_permissions`, `user_role_assignments`, `approval_participants`)**:
  - Use `created_at` / `uploaded_at` / `granted_at` / `assigned_at` + monotonic primary key `id > :last_max_id`, combined with full keyset diffing during the periodic reconciliation job.
- **No-PK Junction Table (`public.talk_post_tags`, `63` rows -> `RM-41`)**:
  - Synchronized via `SELECT DISTINCT post_id, tag_id FROM public.talk_post_tags` per modified post or full-table refresh (`63` rows takes `<5ms`).

### 2.3 Behavior 3: Node Property Update (`ON CREATE SET` vs `ON MATCH SET`)
- Every Cypher contract in `Doc 30` explicitly separates immutable creation properties (`created_at`, `created_by_user_id`) in `ON CREATE SET` from mutable business properties in `ON MATCH SET`, and always updates `n.last_synced_at = datetime()`.

### 2.4 Behavior 4: Relationship Property Update
- Every relationship with properties (`RM-01`, `RM-03`, `RM-04`, `RM-06`, `RM-07`, `RM-08`, `RM-10`, `RM-13`, `RM-20`, `RM-23`, `RM-26`, `RM-27`, `RM-34`, `RM-37`) updates mutable attributes (`status`, `action_status`, `acted_at`, `role`, `is_granted`, `effective_to`, `is_active`, `resolution_status`, `last_synced_at`) via `ON MATCH SET`.

### 2.5 Behavior 5: Soft Delete Synchronization (`is_deleted = true` / `is_active = false`)
- When a source row transitions to `is_deleted = true` (`tenants`, `users`, `tenant_user_memberships`, `projects`, `tickets`, `approval_requests`, `schedule_events`, `notices`, `talk_posts`, `assets`, `files`, `chat_conversation_members`, `project_common_documents`) or `is_active = false` (`users`, `departments`, `roles`, `schedule_rooms`, `asset_categories`, `audiences`), the node or edge is **retained** in Neo4j with `is_deleted = true` / `is_active = false`.
- **Exception (`CRITICAL-01` & `HIGH-05`)**: When a `tenant_user_memberships` row transitions to `status <> 'active'` or `is_deleted = true`, `RM-01` updates `m.status` and `m.is_deleted` on `[:MEMBER_OF]`, while `NM-22`/`RM-37` (`:AttendanceRecord`) and `RM-04` (`[:MANAGES]`) revoke/quarantine active-only dependent nodes/edges during reconciliation.

---

### 2.6 Behavior 6: Per-Node Hard Delete & Eligibility Reconciliation Contract (`CRITICAL-06` Resolution)

> [!CAUTION]
> **Prohibition of Generic `SELECT id` Hard-Delete (`CRITICAL-06`)**:
> A generic reconciliation template such as `SELECT id FROM public.<table_name>` followed by `MATCH (n:<Label>) WHERE NOT (n.id IN $valid_source_ids) DETACH DELETE n` is **architecturally unsafe and strictly prohibited** because:
> 1. **`:Tag` (`NM-24`)** is a union of two tables (`public.project_tags` and `public.talk_tags`) keyed by synthetic string **`tg.tag_key`** (`'project:' || id` and `'talk:' || id`) and has **no `tg.id` property** (`tg.id IS NULL` for all `:Tag` nodes — running `WHERE NOT (n.id IN ...)` would delete 100% of `:Tag` nodes!).
> 2. **`:AttendanceRecord` (`NM-22`)** only loads rows from `public.attendance_daily_records` whose 6-step classification is `RESOLVED_BY_USER_ID` or `RESOLVED_BY_EMPLOYEE_NUMBER` with active membership (`m.status = 'active' AND m.is_deleted = false`). Reconciling against raw `SELECT id FROM public.attendance_daily_records` would fail to remove records whose user membership became `inactive`/`suspended`/`deleted` or whose `employee_number` became ambiguous.
> 3. **`:LeaveBalance` (`NM-21`)** aggregates `public.user_leave_year_balances` and `public.user_leave_monthly_balances` and filters via `user_unambiguous_leave_tenant`.
> 4. **`:Audience` (`NM-20`)** and **12 Transitive-Tenant Nodes (`NM-06`–`NM-10`, `NM-12`, `NM-14`–`NM-16`, `NM-18`–`NM-19`, `NM-25`)** filter out rows with unresolvable/ambiguous tenant ownership via their extraction CTEs.

#### 2.6.1 The 7 Canonical Reconciliation Patterns (`R-1` through `R-7`)

| Pattern ID | Pattern Name | Applicable Node IDs | Graph Identity Key | Authoritative Source Reconciliation Set (`$eligible_keys`) | Deletion / Quarantine Action When Graph Node Key Not in `$eligible_keys` |
|---|---|---|---|---|---|
| **`R-1`** | **Direct-PK Single-Table Nodes** | `NM-01` (`:Tenant`), `NM-03` (`:Department`), `NM-04` (`:Role`), `NM-05` (`:Permission`), `NM-13` (`:ScheduleRoom`), `NM-17` (`:AssetCategory`), `NM-23` (`:ContractHistory`) | `n.id` (`INTEGER`) | `SELECT id FROM public.<source_table>` (all physical rows are eligible; no CTE filtering) | If source row was physically deleted in PostgreSQL: verify circuit breaker (`<= 5%`), log to `etl_reconciliation_audit`, then `DETACH DELETE n`. |
| **`R-2`** | **Global Account Identity Node** | `NM-02` (`:User`) | `u.id` (`INTEGER`) | `SELECT u.id FROM public.users u` (`LEFT JOIN` to `user_profiles` never filters out `users.id`) | Prefer soft-delete (`u.is_deleted = true, u.is_active = false`). Only `DETACH DELETE u` if `u.id` is physically absent from `public.users` AND circuit breaker passes. |
| **`R-3`** | **Transitive-Tenant Eligible-PK Nodes** | `NM-06` (`:Project`), `NM-07` (`:Ticket`), `NM-08` (`:Sprint`), `NM-09` (`:KanbanColumn`), `NM-10` (`:ApprovalRequest`), `NM-12` (`:ScheduleEvent`), `NM-14` (`:Notice`), `NM-15` (`:Post`), `NM-16` (`:Asset`), `NM-18` (`:FileMetadata`), `NM-19` (`:ChatConversation`), `NM-25` (`:KnowledgeDocument`) | `n.id` (`INTEGER`) | Exact `SELECT <id>` from the canonical `NM-*` extraction query in `Doc 30` (including `user_unambiguous_tenant` / parent `:Project` / `:Department` tenant join) | 1. If `n.id` still exists in `public.<source_table>` but failed tenant resolution (`AMBIGUOUS_TENANT` / `INVALID_TENANT`), log to `etl_quarantine_log` and `DETACH DELETE n` (plus purge corresponding Vector DB chunks).<br>2. If `n.id` no longer exists in `public.<source_table>`, `DETACH DELETE n` (and purge Vector DB chunks for `NM-14, NM-15, NM-18, NM-19, NM-25`). |
| **`R-4`** | **Dual-Scope Validated `:Audience` Node** | `NM-20` (`:Audience`) | `a.id` (`INTEGER`) | Exact `SELECT a.id` from the `NM-20` Dual-Scope SQL query in `Doc 30` (`Case 1` system template with `0` members OR `Case 2` custom audience with single matching tenant across owner + `adm` + `aum`) | If an `:Audience` node in Neo4j is no longer in `$eligible_keys` (e.g., a custom audience acquired cross-tenant members or a system audience acquired member rows), log `CROSS_TENANT_VIOLATION` to `etl_quarantine_log` and `DETACH DELETE a`. |
| **`R-5`** | **Multi-Table Aggregated `:LeaveBalance` Node** | `NM-21` (`:LeaveBalance`) | `lb.id` (`INTEGER`, from `user_leave_year_balances.id`) | Exact `SELECT yb.id` from the `NM-21` SQL query in `Doc 30` (`public.user_leave_year_balances yb INNER JOIN user_unambiguous_leave_tenant ult ON ult.user_id = yb.user_id`) | 1. When `user_leave_monthly_balances` rows are updated/deleted, re-run `NM-21` upsert to recompute `accrued_days` and `used_days` on `lb` (do **not** delete `lb` if `yb.id` still exists).<br>2. If `yb.id` is deleted or `ult` becomes ambiguous (`>1` tenant), quarantine (`AMBIGUOUS_TENANT` if in `yb`) and `DETACH DELETE lb`. |
| **`R-6`** | **6-Step Active-Membership Resolved `:AttendanceRecord` Node** | `NM-22` (`:AttendanceRecord`) | `ar.id` (`INTEGER`, from `attendance_daily_records.id`) | Exact `SELECT id FROM classified_attendance WHERE resolution_status IN ('RESOLVED_BY_USER_ID', 'RESOLVED_BY_EMPLOYEE_NUMBER')` (enforcing `m.status = 'active' AND m.is_deleted = false`, `CRITICAL-01`) | If a previously loaded `ar.id` is no longer in `$eligible_keys` (e.g., user membership became `inactive`/`suspended`/`deleted`, or `employee_number` became `AMBIGUOUS`/`UNRESOLVED`), insert/update its new status in `etl_quarantine_log` and execute `DETACH DELETE ar` so `0` ineligible or unlinked `:AttendanceRecord` nodes remain in Neo4j. |
| **`R-7`** | **Synthetic-Key Union `:Tag` Node** | `NM-24` (`:Tag`) | **`tg.tag_key` (`STRING`: `'project:' \|\| pt.id` or `'talk:' \|\| tt.id`)** | Exact `SELECT tag_key` from the `NM-24` `UNION ALL` SQL query in `Doc 30` (`project_tags` + `talk_tags` with unambiguous tenant) | Reconcile **strictly on `tg.tag_key`**: `MATCH (tg:Tag) WHERE NOT (tg.tag_key IN $eligible_tag_keys) DETACH DELETE tg`. **Never reference `tg.id`**. |

#### 2.6.2 Complete 24-Node Reconciliation & Deletion Matrix (`NM-01`–`NM-10`, `NM-12`–`NM-25`)

| Node ID | Node Label | Pattern | Source Table(s) | Graph Identity Key | Eligible Source Key Query Summary | Soft-Delete Property | Hard-Delete & Stale-State Policy | Connected Edges Cleaned Up on Delete | Vector DB Cleanup Required? |
|---|---|---|---|---|---|---|---|---|---|
| **`NM-01`** | `:Tenant` | `R-1` | `public.tenants` | `t.id` (`int8`) | `SELECT id FROM public.tenants` | `t.is_deleted` | Never hard-delete active tenant; only `DETACH DELETE` if physically removed from `public.tenants` (circuit breaker `0%` auto-delete; requires manual approval). | `RM-01`, `RM-02` | Yes (all collections by `tenant_id`) |
| **`NM-02`** | `:User` | `R-2` | `public.users` (`LEFT JOIN user_profiles`) | `u.id` (`int4`) | `SELECT id FROM public.users` | `u.is_deleted`, `u.is_active` | Retain soft-deleted users (`u.is_deleted = true`). If physically purged (like Oct 5 cleanup), `DETACH DELETE u` and quarantine dangling references. | `RM-01`, `RM-03`, `RM-04`, `RM-06`, `RM-08`–`RM-10`, `RM-12`, `RM-13`, `RM-18`, `RM-20`, `RM-21`, `RM-23`, `RM-24`, `RM-27`, `RM-28`, `RM-30`, `RM-33`–`RM-38` | No |
| **`NM-03`** | `:Department` | `R-1` | `public.departments` | `d.id` (`int4`) | `SELECT id FROM public.departments` | `d.is_active`, `d.effective_to` | Retain inactive departments (`is_active = false`). `DETACH DELETE d` only if `d.id` physically deleted from `public.departments`. | `RM-02`–`RM-05`, `RM-26`, `RM-31` | No |
| **`NM-04`** | `:Role` | `R-1` | `public.roles` | `r.id` (`int4`) | `SELECT id FROM public.roles` | `r.is_active` | Retain inactive roles (`is_active = false`). `DETACH DELETE r` only if physically deleted from `public.roles`. | `RM-06`, `RM-07` | No |
| **`NM-05`** | `:Permission` | `R-1` | `public.permissions` | `p.id` (`int4`) | `SELECT id FROM public.permissions` | None | `DETACH DELETE p` if `p.id` physically deleted from `public.permissions`. | `RM-07`, `RM-08` | No |
| **`NM-06`** | `:Project` | `R-3` | `public.projects` + `user_unambiguous_tenant` | `p.id` (`int8`) | `NM-06` CTE `SELECT p.id` | `p.is_deleted` | Sync `p.is_deleted = true`. `DETACH DELETE p` if physically deleted or creator tenant becomes ambiguous (quarantine). | `RM-09`–`RM-11`, `RM-16`, `RM-17`, `RM-39`, `RM-42` | Yes (`knowledge_document_chunks` by `project_id`) |
| **`NM-07`** | `:Ticket` | `R-3` | `public.tickets` + `projects` + `user_unambiguous_tenant` | `t.id` (`int8`) | `NM-07` CTE `SELECT t.id` | `t.is_deleted` | Sync `t.is_deleted = true`. `DETACH DELETE t` if physically deleted or parent project ineligible. | `RM-11`–`RM-15`, `RM-40` | No |
| **`NM-08`** | `:Sprint` | `R-3` | `public.project_sprints` + `projects` + `user_unambiguous_tenant` | `s.id` (`int8`) | `NM-08` CTE `SELECT s.id` | None (`s.status`) | `DETACH DELETE s` if physically deleted from `public.project_sprints` or parent project ineligible. | `RM-14`, `RM-16` | No |
| **`NM-09`** | `:KanbanColumn` | `R-3` | `public.kanban_columns` + `projects` + `user_unambiguous_tenant` | `k.id` (`int8`) | `NM-09` CTE `SELECT k.id` | None | `DETACH DELETE k` if physically deleted from `public.kanban_columns` or parent project ineligible. | `RM-15`, `RM-17` | No |
| **`NM-10`** | `:ApprovalRequest` | `R-3` | `public.approval_requests` + `user_unambiguous_tenant` | `a.id` (`int8`) | `NM-10` CTE `SELECT a.id` | `a.is_deleted` | Sync `a.is_deleted = true`. `DETACH DELETE a` if physically deleted or creator tenant ambiguous. | `RM-18`, `RM-20` | No |
| **`NM-12`** | `:ScheduleEvent` | `R-3` | `public.schedule_events` + `user_unambiguous_tenant` | `e.id` (`int8`) | `NM-12` CTE `SELECT e.id` | `e.is_deleted` | Sync `e.is_deleted = true`. `DETACH DELETE e` if physically deleted or organizer tenant ambiguous. | `RM-21`–`RM-23` | No |
| **`NM-13`** | `:ScheduleRoom` | `R-1` | `public.schedule_rooms` | `r.id` (`int4`) | `SELECT id FROM public.schedule_rooms` | `r.is_active` | Retain `is_active = false`. `DETACH DELETE r` only if physically deleted from `public.schedule_rooms`. | `RM-22` | No |
| **`NM-14`** | `:Notice` | `R-3` | `public.notices` + `user_unambiguous_tenant` | `n.id` (`int8`) | `NM-14` CTE `SELECT n.id` | `n.is_deleted`, `n.is_published` | Sync `n.is_deleted = true`. `DETACH DELETE n` if physically deleted or publisher tenant ambiguous. | `RM-24`, `RM-25` | Yes (`knowledge_document_chunks` by `notice_id`) |
| **`NM-15`** | `:Post` | `R-3` | `public.talk_posts` + `user_unambiguous_tenant` | `p.id` (`int8`) | `NM-15` CTE `SELECT p.id` | `p.is_deleted` | Sync `p.is_deleted = true`. `DETACH DELETE p` if physically deleted or author tenant ambiguous. | `RM-28`, `RM-29`, `RM-41` | Yes (`knowledge_document_chunks` by `post_id`) |
| **`NM-16`** | `:Asset` | `R-3` | `public.assets` + `departments` + `user_unambiguous_tenant` | `a.id` (`int8`) | `NM-16` CTE `SELECT a.id` | `a.is_deleted` | Sync `a.is_deleted = true`. `DETACH DELETE a` if physically deleted or department/user tenant conflict occurs (quarantine). | `RM-30`–`RM-32` | No |
| **`NM-17`** | `:AssetCategory` | `R-1` | `public.asset_categories` | `c.id` (`int4`) | `SELECT id FROM public.asset_categories` | `c.is_active` | Retain `is_active = false`. `DETACH DELETE c` only if physically deleted from `public.asset_categories`. | `RM-32` | No |
| **`NM-18`** | `:FileMetadata` | `R-3` | `public.files` + `user_unambiguous_tenant` | `f.id` (`int8`) | `NM-18` CTE `SELECT f.id` | `f.is_deleted` | Sync `f.is_deleted = true`. `DETACH DELETE f` if physically deleted or uploader tenant ambiguous. | `RM-33`, `RM-43` | Yes (`knowledge_document_chunks` by `file_id`) |
| **`NM-19`** | `:ChatConversation` | `R-3` | `public.chat_conversations` + `user_unambiguous_tenant` | `c.id` (`int8`) | `NM-19` CTE `SELECT c.id` | None | `DETACH DELETE c` if physically deleted from `public.chat_conversations` or creator tenant ambiguous. | `RM-34`, `RM-35` | Yes (`chat_message_chunks` by `conversation_id`) |
| **`NM-20`** | `:Audience` | `R-4` | `public.audiences` + `adm_tenants` + `aum_tenants` | `a.id` (`int4`) | `NM-20` Dual-Scope CTE `SELECT a.id` | `a.is_active` | If custom audience acquires cross-tenant members or system audience acquires member rows, quarantine (`CROSS_TENANT_VIOLATION`) and `DETACH DELETE a`. | `RM-25`–`RM-27`, `RM-29` | No |
| **`NM-21`** | `:LeaveBalance` | `R-5` | `public.user_leave_year_balances` + `user_leave_monthly_balances` + `user_unambiguous_leave_tenant` | `lb.id` (`int8`, `yb.id`) | `NM-21` CTE `SELECT yb.id` | None | Recompute sums on monthly changes; if `yb.id` deleted or user acquires `>1` tenant (`AMBIGUOUS_TENANT`), quarantine and `DETACH DELETE lb`. | `RM-36` | No |
| **`NM-22`** | `:AttendanceRecord` | `R-6` | `public.attendance_daily_records` + 6-Step Active-Membership CTE | `ar.id` (`int8`) | `NM-22` CTE `SELECT id WHERE resolution_status IN ('RESOLVED_BY_USER_ID','RESOLVED_BY_EMPLOYEE_NUMBER')` | None | If `ar.id` is physically deleted OR its resolution status changes to `UNRESOLVED`/`AMBIGUOUS`/`INVALID_TENANT` (e.g., `m.status <> 'active'`), quarantine and `DETACH DELETE ar`. | `RM-37` | No |
| **`NM-23`** | `:ContractHistory` | `R-1` | `public.user_contract_histories` | `ch.id` (`int8`) | `SELECT id FROM public.user_contract_histories` | `ch.is_current` | Retain `is_current = false` historical contracts. `DETACH DELETE ch` only if physically deleted from `public.user_contract_histories`. | `RM-38` | No |
| **`NM-24`** | `:Tag` | `R-7` | `public.project_tags` UNION ALL `public.talk_tags` | **`tg.tag_key` (`STRING`)** | `NM-24` CTE `SELECT tag_key` (`'project:'\|\|pt.id` UNION `'talk:'\|\|tt.id`) | None | Reconcile strictly on `tg.tag_key`: `WHERE NOT (tg.tag_key IN $eligible_tag_keys) DETACH DELETE tg`. **Never use `tg.id`**. | `RM-39`–`RM-41` | No |
| **`NM-25`** | `:KnowledgeDocument` | `R-3` | `public.project_common_documents` + `projects` + `user_unambiguous_tenant` | `kd.id` (`int8`) | `NM-25` CTE `SELECT pcd.id` | `kd.is_deleted` | Sync `kd.is_deleted = true`. `DETACH DELETE kd` if physically deleted from `project_common_documents` or parent project ineligible. | `RM-42`, `RM-43` | Yes (`knowledge_document_chunks` by `knowledge_document_id`) |

#### 2.6.3 Executable Per-Pattern Cypher Reconciliation Templates & Circuit-Breaker Guard

1. **Circuit-Breaker Pre-Condition (Mandatory Before Any Hard Delete)**:
   - Let `N_graph` be the current node count for label `<Label>` in Neo4j, and `N_delete` be the count of nodes in Neo4j whose identity key is not in `$eligible_keys`.
   - If `N_graph > 0` and `(N_delete::float / N_graph::float) > 0.05` (`MAX_DELETE_RATIO = 5%`, or `> 0%` for `:Tenant`), the ETL worker **MUST ABORT** the hard-delete step for `<Label>`, raise alert `RECONCILIATION_CIRCUIT_BREAKER_TRIPPED`, and keep existing nodes intact pending operator review.

2. **Cypher Reconciliation for Integer-Keyed Nodes (`Patterns R-1, R-2, R-3, R-4, R-5, R-6`: `NM-01`–`NM-10`, `NM-12`–`NM-23`, `NM-25`)**:
```cypher
// $eligible_ids is produced by the exact NM-* SQL query (or direct PK query for R-1/R-2)
MATCH (n:<Label>)
WHERE NOT (n.id IN $eligible_ids)
WITH collect(n) AS stale_nodes, count(n) AS delete_cnt
CALL apoc.util.validate(
  delete_cnt > $max_allowed_delete_count,
  'RECONCILIATION_CIRCUIT_BREAKER_TRIPPED for label <Label>: %d candidates exceed threshold',
  [delete_cnt]
)
UNWIND stale_nodes AS target_node
DETACH DELETE target_node
RETURN count(target_node) AS deleted_count;
```

3. **Cypher Reconciliation for Synthetic-Key `:Tag` Nodes (`Pattern R-7`: `NM-24`)**:
```cypher
// $eligible_tag_keys is produced by the exact NM-24 UNION ALL query ('project:1', 'talk:1', ...)
MATCH (tg:Tag)
WHERE NOT (tg.tag_key IN $eligible_tag_keys)
WITH collect(tg) AS stale_tags, count(tg) AS delete_cnt
CALL apoc.util.validate(
  delete_cnt > $max_allowed_delete_count,
  'RECONCILIATION_CIRCUIT_BREAKER_TRIPPED for :Tag: %d candidates exceed threshold',
  [delete_cnt]
)
UNWIND stale_tags AS target_tag
DETACH DELETE target_tag
RETURN count(target_tag) AS deleted_tag_count;
```

---


#### 2.6.3 Circuit Breaker Safety Engine Specification (Phase 1.2.3 WP3 Hardening)

To safeguard against catastrophic mass deletion during automated reconciliation (e.g. from table truncation, partial network failures, or unhandled query exceptions), every hard-delete reconciliation wave is gated by the Python Circuit Breaker module (scripts/phase1_2_3/circuit_breaker.py):

1. **Threshold Arithmetic**:
   \\text{max\\_allowed\\_delete\\_count} = \\lfloor \\text{eligible\\_graph\\_node\\_count} \\times 0.05 \\rfloor
   Integer truncation (math.floor) is strictly applied:
   - Population = 100 -> Max allowed = 5
   - Population = 20 -> Max allowed = 1
   - Population = 19 -> Max allowed = 0
   - Population = 1000 -> Max allowed = 50
2. **Boundary Conditions & Anomaly Prevention**:
   - **Zero Population**: If eligible_graph_node_count == 0, candidate_delete_count == 0 is allowed (NO_OP_ZERO_POP), while any candidate deletion > 0 immediately aborts (ZERO_POP_NONZERO_DELETE).
   - **Protected Entities**: :Tenant (NM-01) nodes can never be automatically hard-deleted (max_allowed = 0). Any deletion attempt aborts with PROTECTED_ENTITY_TYPE.
   - **Incomplete Extraction**: If source extraction fails or is incomplete (extraction_complete = False), the operation aborts with INCOMPLETE_EXTRACTION.
   - **Dry-Run Mode**: Evaluates threshold logic and returns SIMULATED_TRIP without modifying the Neo4j graph.
   - **Batch Atomicity**: In a multi-entity batch, if any entity trips the circuit breaker, the entire batch is aborted (BATCH_ABORT).

---

### 2.7 Behavior 7: Stale Relationship Removal on Reassignment or Revocation
When a foreign key or junction table membership changes in PostgreSQL, stale edges in Neo4j MUST be removed or deactivated within the same ETL transaction:
1. **Single-Valued FK Edges (`RM-04` `[:MANAGES]`, `RM-05` `[:SUB_DEPARTMENT_OF]`, `RM-14` `[:PART_OF_SPRINT]`, `RM-15` `[:IN_STAGE]`, `RM-22` `[:HELD_IN]`, `RM-25` & `RM-29` `[:TARGETED_TO]`, `RM-30` `[:ASSIGNED_TO]` on `:Asset`, `RM-31` `[:LOCATED_IN]`, `RM-32` `[:CATEGORIZED_AS]`)**:
   - Before or immediately after merging the new edge, delete any existing edge of that type pointing to a different target node, or delete the edge when the source FK column is set to `NULL` (or when the manager in `RM-04` loses active tenant membership `m.status = 'active' AND m.is_deleted = false`, `HIGH-05`):
```cypher
// Example 1: Ticket moved to a new KanbanColumn or Sprint (RM-15 / RM-14)
UNWIND $batch AS row
MATCH (t:Ticket {id: toInteger(row.ticket_id)})-[old_rel:IN_STAGE]->(old_col:KanbanColumn)
WHERE row.column_id IS NULL OR old_col.id <> toInteger(row.column_id)
DELETE old_rel;

// Example 2: Department manager removed or manager membership deactivated (RM-04 — HIGH-05)
MATCH (u:User)-[r:MANAGES]->(d:Department)
WHERE NOT (d.id IN $active_managed_dept_ids)
   OR coalesce(u.is_active, false) = false
   OR coalesce(u.is_deleted, false) = true
   OR NOT EXISTS {
     MATCH (u)-[:MEMBER_OF {status: 'active', is_deleted: false}]->(:Tenant {id: d.tenant_id, is_deleted: false})
   }
DELETE r;
```
2. **Junction-Table Edges (`RM-03` `department_members`, `RM-06` `user_role_assignments`, `RM-07` `role_permissions`, `RM-08` `user_permissions`, `RM-10` `project_members`, `RM-13` `ticket_assignees`, `RM-20` `approval_participants`, `RM-23` `schedule_event_participants`, `RM-26` `audience_department_members`, `RM-27` `audience_user_members`, `RM-34` `chat_conversation_members`, `RM-40` `ticket_tags`, `RM-41` `talk_post_tags`)**:
   - Reconcile active edge IDs per parent entity (`DELETE r` where `NOT (r.id IN $valid_edge_ids)` or `(post_id, tag_key)` pair no longer exists in `talk_post_tags`).

---

### 2.8 Behavior 8: Orphan Handling & Quarantine Table Contract (`DEFECT 02`, `CRITICAL-01`, `CRITICAL-02`)
- **Strict Quarantine Policy**:
  1. Any relationship row referencing a missing parent/target ID (e.g. `18` `project_members` rows and `13` `ticket_assignees` rows referencing Oct 5 purged users; `2` `role_permissions` rows referencing non-existent permission IDs) is **rejected** from graph edge creation and written to `public.etl_quarantine_log`.
  2. **Attendance Record Quarantine (`NM-22` & `RM-37` — DEFECT 02 & CRITICAL-01 Resolution)**:
     - Every row in `public.attendance_daily_records` (`54,489` rows) is evaluated by the **6-Step Deterministic Resolution Hierarchy** (`Doc 29` Section 3.1, `Doc 30` `NM-22`, `Doc 31` `RM-37`) enforcing **`m.status = 'active' AND m.is_deleted = false AND COALESCE(u.is_deleted, false) = false`** (`Cases A–E`).
     - Only rows classified as **`RESOLVED_BY_USER_ID`** (`24,764` rows) or **`RESOLVED_BY_EMPLOYEE_NUMBER`** (`0` rows on current snapshot) are loaded as `:AttendanceRecord` nodes and linked via `(:User)-[:HAS_ATTENDANCE]->(:AttendanceRecord)`.
     - All rows classified as **`UNRESOLVED`** (`29,725` rows), **`AMBIGUOUS`** (`0` rows), **`INVALID_TENANT`** (`0` rows on current snapshot; catches `Cases B, C, D, E` where membership is `inactive`, `suspended`, or `is_deleted = true`), or **`INVALID_SOURCE_REFERENCE`** (`0` rows) are **quarantined** to `public.etl_quarantine_log` and **MUST NEVER** be created as unlinked `:AttendanceRecord` nodes in Neo4j.
  3. **Leave Balance Quarantine (`NM-21` & `RM-36` — CRITICAL-02 Resolution)**:
     - Any row in `public.user_leave_year_balances` whose `user_id` has `>1` distinct non-deleted tenant memberships (`AMBIGUOUS_TENANT`) or `0` non-deleted tenant memberships (`INVALID_TENANT`) is quarantined to `public.etl_quarantine_log` and excluded from Neo4j.

```sql
CREATE TABLE IF NOT EXISTS public.etl_quarantine_log (
    quarantine_id       BIGSERIAL PRIMARY KEY,
    etl_run_id          UUID NOT NULL,
    mapping_id          VARCHAR(16) NOT NULL,   -- e.g. 'NM-21', 'NM-22', 'RM-37', 'NM-20', 'RM-07'
    source_table        VARCHAR(128) NOT NULL,
    source_record_id    VARCHAR(128) NOT NULL,
    quarantine_reason   VARCHAR(64) NOT NULL,   -- 'UNRESOLVED', 'AMBIGUOUS', 'AMBIGUOUS_TENANT', 'INVALID_TENANT', 'INVALID_SOURCE_REFERENCE', 'CROSS_TENANT_VIOLATION'
    diagnostic_payload  JSONB NOT NULL,
    detected_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    resolved_at         TIMESTAMPTZ NULL
);
```

### 2.9 Behavior 9: Duplicate Source Row Handling
- Deduplicate `public.talk_post_tags` (no PK) via `SELECT DISTINCT post_id, tag_id`.
- For `approval_participants` (`RM-20`), key `MERGE (u)-[p:PARTICIPATES_IN {participant_role: row.participant_role}]->(a)` by `participant_role` to match the physical composite unique constraint `(request_id, user_id, participant_role)`.
- For `department_members` (`RM-03`), key `MERGE (u)-[m:MEMBER_OF_DEPARTMENT {id: toInteger(row.id)}]->(d)` by `id` to preserve historical assignment periods while filtering active memberships via `m.is_active = true`.

### 2.10 Behavior 10: Tenant Validation Before Graph Write
- Every node in Category B and Category C (`NM-03`, `NM-04`, `NM-06`–`NM-10`, `NM-12`, `NM-14`–`NM-16`, `NM-18`–`NM-19`, `NM-21`–`NM-25`) must have a non-null integer `tenant_id` verified before `UNWIND $batch`.
- For `:Audience` (`NM-20` — Dual-Scope), ETL enforces `(is_system = true AND tenant_id IS NULL AND member_count = 0) OR (is_system = false AND tenant_id IS NOT NULL)`.
- Every relationship `MERGE` in `Doc 31` includes an explicit `WHERE` guard verifying that start and end nodes belong to the exact same `tenant_id` (and `status = 'active', is_deleted = false` for `RM-04` and `RM-37`).

### 2.11 Behavior 11: Retry & Dead-Letter Queue (DLQ) Policy
- Transient Neo4j errors (`TransientError`, deadlock, network timeout) are retried up to **3 times** with exponential backoff (`1s`, `4s`, `16s` + jitter).
- Permanent errors (`ConstraintValidationFailed`, type conversion failure) route the failed batch/row to `public.etl_quarantine_log` without halting unrelated domain waves.

### 2.12 Behavior 12: Idempotency Guarantee
- All node and relationship writes use `MERGE` on canonical uniqueness keys (`id`, `tag_key`, `participant_role`) with deterministic `ON CREATE SET` / `ON MATCH SET` clauses. Re-running any batch `N` times produces the exact same graph state.

### 2.13 Behavior 13: Batch Size & Transaction Boundaries
- **Nodes (`Wave 1`–`Wave 4`)**: `1,000` rows per Neo4j transaction (`UNWIND $batch`).
- **Relationships (`Wave 5`)**: `2,000` rows per Neo4j transaction (`UNWIND $batch`).

### 2.14 Behavior 14: Checkpoint & Watermark Recovery (`public.etl_sync_checkpoints`)
```sql
CREATE TABLE IF NOT EXISTS public.etl_sync_checkpoints (
    mapping_id          VARCHAR(16) PRIMARY KEY, -- 'NM-01'..'NM-25', 'RM-01'..'RM-43'
    source_table        VARCHAR(128) NOT NULL,
    last_watermark_ts   TIMESTAMPTZ NULL,
    last_max_id         BIGINT NULL,
    last_run_id         UUID NOT NULL,
    last_run_status     VARCHAR(32) NOT NULL,    -- 'SUCCESS', 'PARTIAL_QUARANTINE', 'FAILED'
    rows_extracted      BIGINT NOT NULL DEFAULT 0,
    rows_upserted       BIGINT NOT NULL DEFAULT 0,
    rows_deleted        BIGINT NOT NULL DEFAULT 0,
    rows_quarantined    BIGINT NOT NULL DEFAULT 0,
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```
- Watermarks are advanced **only after** the Neo4j transaction commits.

### 2.15 Behavior 15: Post-Load Reconciliation & Count Verification
After every full or incremental ETL cycle, the reconciliation runner compares PostgreSQL eligible counts (`count_sql_eligible`) against Neo4j node/edge counts (`count_cypher`) and quarantine counts (`count_quarantined`):
$$\text{Count}_{\text{PostgreSQL Physical}} = \text{Count}_{\text{Neo4j Loaded}} + \text{Count}_{\text{Quarantined}}$$
Any discrepancy `> 0` raises an immediate data governance alert (`ETL_RECONCILIATION_MISMATCH`).

### 2.16 Behavior 16: Phase 1.2.3.1 Circuit Breaker Input Validation & Scoped Approval Guard (DEF-P1231-04, DEF-P1231-05)
To eliminate failure modes identified in Phase 1.2.3 Review:
1. **Strict Circuit Breaker Input Validation (DEF-P1231-04, CB-01..CB-25)**:
   - The Circuit Breaker strictly validates all arguments before performing threshold ratio calculations:
     - Rejects negative candidate counts (candidate_delete_count < 0, e.g. -1) with INVALID_INPUT_NEGATIVE_CANDIDATES.
     - Rejects negative populations (eligible_graph_node_count < 0) with INVALID_INPUT_NEGATIVE_POPULATION.
     - Rejects candidate counts exceeding total population (candidates > population) with INVALID_INPUT_CANDIDATES_EXCEED_POPULATION.
     - Rejects non-numeric, NaN, and Infinity values with INVALID_INPUT_NAN_INF_*.
     - Rejects unapproved entity types or empty strings with INVALID_INPUT_UNAPPROVED_ENTITY_TYPE.
     - Rejects duplicate candidate keys with INVALID_INPUT_DUPLICATE_CANDIDATE_KEYS.
     - Rejects invalid tenant IDs with INVALID_INPUT_TENANT_ID.
2. **Cryptographic & Scoped Hard-Delete Approval Guard (DEF-P1231-05, HD-01..HD-12)**:
   - Destructive hard-deletion remains disabled by default (hard_delete_enabled = false).
   - When enabled, deletion requests require an HMAC-SHA256 signed ApprovalToken cryptographically bound to:
     - Exact atch_id
     - Exact 	enant_id
     - Exact entity_type
     - Maximum approved candidate count ceiling (candidate_count <= max_approved_deletes)
     - Strict expiration timestamp and revocation tracking (
evoked_tokens).
