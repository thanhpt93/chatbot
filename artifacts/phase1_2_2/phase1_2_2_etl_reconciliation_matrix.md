# Phase 1.2.2 ETL Per-Node Reconciliation & Safe Hard-Delete Matrix (`CRITICAL-06`)
## Groupware AI Chatbot – PostgreSQL 18.6 + Neo4j + Vector Database

**Source Specification:** [`33_phase1_2_etl_synchronization_contract.md`](file:///C:/Project/chatbot/documentation/phase-1-database-discovery/33_phase1_2_etl_synchronization_contract.md) (Section 2.6)  
**Validation Status:** `STATICALLY VALIDATED` & `EXECUTED (SYNTHETIC FIXTURE)` (`24/24` Approved MVP Nodes Covered across `Patterns R-1`–`R-7`)

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
