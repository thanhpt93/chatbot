# PHASE 1.2 / 1.2.1 / 1.2.2 – AUTOMATED CONSISTENCY VALIDATION SPECIFICATION (WORK PACKAGE 8)
## Groupware AI Chatbot – PostgreSQL + Neo4j + Vector Database

**Document ID:** `36_phase1_2_automated_consistency_validation.md`  
**Phase:** Phase 1.2.2 – ETL Lifecycle, Tenant Security & Runtime Evidence Hardening (Extends Phase 1.2.1 Baseline)  
**Date:** 2026-11-05  
**Status:** Canonical Validation Specification  
**Evidence Level:** `EXECUTED` & `RESULT VALIDATED` (Executed via [`scripts/phase1_2_2/run_all.py`](file:///C:/Project/chatbot/scripts/phase1_2_2/run_all.py) and [`scripts/phase1_2_1/validate_phase1_2_1.py`](file:///C:/Project/chatbot/scripts/phase1_2_1/validate_phase1_2_1.py); machine-readable output at [`artifacts/phase1_2_2/phase1_2_2_consistency_report.json`](file:///C:/Project/chatbot/artifacts/phase1_2_2/phase1_2_2_consistency_report.json) and [`artifacts/phase1_2_2/phase1_2_2_consistency_report.md`](file:///C:/Project/chatbot/artifacts/phase1_2_2/phase1_2_2_consistency_report.md))

---

## 1. Executive Summary & Evolution of the Automated Validation Suite (`Phase 1.2 -> 1.2.1 -> 1.2.2`)

1. **Phase 1.2.1 Baseline (`scripts/phase1_2_1/validate_phase1_2_1.py` — `13/13 PASS`)**:
   - Replaced the self-validating Phase 1.2 dictionary script (`DEFECT 08`) with a direct Markdown & SQL/Cypher parser that verifies `Docs 29–38` against [`artifacts/database-discovery/schema_inventory.json`](file:///C:/Project/chatbot/artifacts/database-discovery/schema_inventory.json) across `13` structural, column, property-count, FTS, and sensitive-column checks (`DEFECT 01`–`DEFECT 09`).
2. **Phase 1.2.2 Hardening Suite (`scripts/phase1_2_2/run_all.py` — `8` Modular Validators + Live PostgreSQL 18.6 & Synthetic Relational-vs-Graph Fixture Execution)**:
   - Extends automated verification to enforce the **6 Phase 1.2.2 technical and security defects (`CRITICAL-01` through `CRITICAL-06` / `HIGH-05`)**:
     - **`CRITICAL-01`**: Active tenant membership lifecycle filter (`m.status = 'active' AND m.is_deleted = false AND COALESCE(u.is_deleted, false) = false`) in `:AttendanceRecord` (`NM-22`) & `[:HAS_ATTENDANCE]` (`RM-37`) + runtime verification of **Cases A, B, C, D, E** (`active/false`, `inactive/false`, `suspended/false`, `active/true`, `inactive/true`) across both user-ID and employee-number resolution paths (`SEC-24`).
     - **`CRITICAL-02`**: Unambiguous multi-tenant `:LeaveBalance` (`NM-21`) & `[:HAS_LEAVE_BALANCE]` (`RM-36`) derivation (`user_unambiguous_leave_tenant` with `COUNT(DISTINCT tenant_id) = 1` across `tenant_user_memberships` and `user_profiles`, `AMBIGUOUS_TENANT` quarantine `SEC-25`, and Stakeholder Decision `SD-07`).
     - **`CRITICAL-03`**: SQL-vs-Cypher tenant isolation parity in Scenario `Q05` (Pending Approval Requests in [`Doc 34`](file:///C:/Project/chatbot/documentation/phase-1-database-discovery/34_phase1_2_query_and_security_validation.md), `SEC-21`).
     - **`CRITICAL-04`**: SQL-vs-Cypher tenant isolation parity in Scenario `Q08` (Published Notices & Dual-Scope Audience Resolution in [`Doc 34`](file:///C:/Project/chatbot/documentation/phase-1-database-discovery/34_phase1_2_query_and_security_validation.md), `SEC-22`).
     - **`HIGH-05` (`CRITICAL-05`)**: Active manager & active tenant membership enforcement on `[:MANAGES]` (`RM-04` in [`Doc 31`](file:///C:/Project/chatbot/documentation/phase-1-database-discovery/31_phase1_2_complete_relationship_mapping.md), Behavior 7 in [`Doc 33`](file:///C:/Project/chatbot/documentation/phase-1-database-discovery/33_phase1_2_etl_synchronization_contract.md), and `Q01` in [`Doc 34`](file:///C:/Project/chatbot/documentation/phase-1-database-discovery/34_phase1_2_query_and_security_validation.md), `SEC-23`).
     - **`CRITICAL-06`**: Complete **24-Node Per-Node Reconciliation & Safe Hard-Delete Specification (`Patterns R-1`–`R-7`)** in [`Doc 33`](file:///C:/Project/chatbot/documentation/phase-1-database-discovery/33_phase1_2_etl_synchronization_contract.md) Section 2.6, including composite synthetic key reconciliation (`:Tag.tag_key` under `R-7`), 6-step attendance reconciliation (`:AttendanceRecord` under `R-6`), dual-table watermark tracking (`NM-21` under `R-5`), circuit-breaker protection (`MAX_DELETE_RATIO = 0.05`), and Wave 3 count correction (`11 Nodes`, `5 + 3 + 11 + 5 = 24`).

---

## 2. Phase 1.2.1 Baseline Checks (`13/13 PASS` Preserved)

The 13 baseline checks in [`scripts/phase1_2_1/validate_phase1_2_1.py`](file:///C:/Project/chatbot/scripts/phase1_2_1/validate_phase1_2_1.py) continue to pass `13/13` with `0` contradictions:

| Check ID | Validation Dimension | Direct Markdown & Catalog Verification Logic | Verified Result | Issues Found | Status |
|---|---|---|---|---:|---|
| `check_01_node_id_consistency` | **Node ID & Label Consistency (`DEFECT 01`)** | Parses `Docs 30, 32, 33, 35, 38` to verify all `27` evaluated nodes (`24` Approved MVP `NM-01`–`NM-10`, `NM-12`–`NM-25`; `1` Blocked `ND-11`; `2` Future `ND-26`–`ND-27`) map to identical labels and that zero stale `Doc 33` IDs (`:LeaveRequest`, `NM-01=:User`, `NM-09=:Post`, etc.) remain. | `27` Evaluated (`24` MVP, `1` Blocked, `2` Future) | `0` | **`PASS`** |
| `check_02_relationship_id_consistency` | **Relationship ID & Type Consistency (`DEFECT 01 & 07`)** | Parses `Docs 31, 32, 33, 38` to verify all `45` evaluated relationships (`42` Approved MVP `RM-01`–`RM-18`, `RM-20`–`RM-43`; `1` Blocked `RM-19`; `2` Future `RM-44`–`RM-45`) match, `Doc 31` header states `45 Evaluated Relationships`, and zero non-canonical edge names (`IN_PROJECT`, `IN_SPRINT`, `PARENT_DEPT`, `BOOKED_ROOM`, `HAS_PARTICIPANT`, `TARGETED_AT`) remain in `Doc 33`. | `45` Evaluated (`42` MVP, `1` Blocked, `2` Future) | `0` | **`PASS`** |
| `check_03_source_table_existence` | **PostgreSQL Source Table Existence** | Verifies every `public.*` table referenced across all `24` approved MVP nodes and `42` approved MVP relationships exists in `schema_inventory.json` (`PostgreSQL 18.6`). | `40` `public.*` tables verified | `0` | **`PASS`** |
| `check_04_source_column_existence` | **PostgreSQL Source Column Existence** | Verifies every mapped node property column (`271` column mappings) and relationship join column exists in `schema_inventory.json`. | `271` node source column mappings verified | `0` | **`PASS`** |
| `check_05_node_property_consistency` | **Reconciled Node Property Accounting (`DEFECT 07`)** | Verifies exact property counts across `Doc 30`, `Doc 32`, and `Doc 38` Section 4: `271` source-column properties + `2` ETL-derived properties (`resolution_status`, `tag_scope`) = `273` business/derived properties + `24` `last_synced_at` audit properties = `297` total runtime MVP node properties (`+ 13` blocked/future properties). | `271` source + `2` derived + `24` audit = `297` runtime properties | `0` | **`PASS`** |
| `check_06_relationship_property_consistency` | **Relationship Property Consistency (`DEFECT 03, 06, 07`)** | Verifies `Doc 31` and `Doc 38` edge properties match (`108` total edge properties across `42` MVP relationships) and confirms `joined_at, left_at` (`RM-03`), `response_status, joined_at` (`RM-23`), and `step_order, step_name, is_required` (`RM-20`) are completely removed from `Doc 38`. | `108` relationship properties verified | `0` | **`PASS`** |
| `check_07_tenant_ownership_consistency` | **Tenant Ownership & Global Identity Rules** | Parses all Cypher blocks in `Doc 34` and `Doc 35` to verify `0` uses of `u.tenant_id` or `User {tenant_id}` and `0` banned indexes (`idx_user_tenant`, `idx_permission_tenant`, `idx_room_tenant`, `idx_asset_cat_tenant`). | `4` global/pooled labels + `1` dual-scope label (`:Audience`) verified | `0` | **`PASS`** |
| `check_08_attendance_resolution_consistency` | **Attendance 6-Step Resolution (`DEFECT 02` & `CRITICAL-01`)** | Verifies `Docs 29, 30, 31, 33, 38` all enforce the 6-step resolution hierarchy, active membership filter (`m.status = 'active' AND m.is_deleted = false`), and all 6 classification statuses (`RESOLVED_BY_USER_ID`, `RESOLVED_BY_EMPLOYEE_NUMBER`, `UNRESOLVED`, `AMBIGUOUS`, `INVALID_TENANT`, `INVALID_SOURCE_REFERENCE`) and prohibit unlinked `:AttendanceRecord` nodes in Neo4j. | `6` status codes + active membership filter verified | `0` | **`PASS`** |
| `check_09_approval_participant_consistency` | **Approval Participant `sequence_order` (`DEFECT 03`)** | Parses `Docs 31, 34, 35, 38` and all `sql`/`cypher` blocks to confirm `sequence_order` is used everywhere and `step_order` / `step_name` appear in `0` code blocks. | `sequence_order` verified (`0` `step_order`/`step_name` in code) | `0` | **`PASS`** |
| `check_10_audience_security_consistency` | **Dual-Scope `:Audience` Security (`DEFECT 04` & `CRITICAL-04`)** | Verifies `Docs 29, 30, 31, 34, 35, 38` enforce `is_system = true AND tenant_id IS NULL` (`0` member edges) vs `is_system = false AND tenant_id = $tenant_id`, and confirms `IDX-16A` (`idx_audience_custom_tenant`) and `IDX-16B` (`idx_audience_system_lookup`) in `Doc 35`. | Dual-scope `:Audience` + `IDX-16A`/`IDX-16B` verified | `0` | **`PASS`** |
| `check_11_fulltext_security_consistency` | **Fulltext Search Two-Template Security (`DEFECT 05`)** | Verifies `Docs 29, 32, 34, 35` separate `Template FTS-A` (`node.tenant_id = $tenant_id`) from `Template FTS-B` (`fts_directory` on `:User` joining `[:MEMBER_OF]`), and confirms Scenario `Q14` and security tests `SEC-01`–`SEC-25` in `Doc 34`. | `14` query scenarios (`Q01`–`Q14`), `25` security tests (`SEC-01`–`SEC-25`) | `0` | **`PASS`** |
| `check_12_department_membership_lifecycle` | **Department Membership Lifecycle (`DEFECT 06`)** | Verifies `Docs 31, 34, 35, 38` map `effective_from`, `effective_to`, and `is_active = (effective_to IS NULL)`, filter `dm.is_active = true` in `Q01`, `Q08`, `Q13`, `Q14`, and index `[:MEMBER_OF_DEPARTMENT]` via `IDX-26` (`idx_rel_dept_member_active`). | `dm.is_active = true` (`effective_to IS NULL`) + `IDX-26` verified | `0` | **`PASS`** |
| `check_13_sensitive_column_exclusion` | **Sensitive Column Exclusion** | Verifies all `32` table-column pairs (`28` distinct sensitive column names across `13` tables: `password_hash`, `birth_date`, `mobile_phone`, `tax_code`, `purchase_price`, `current_value`, `file_url`, `checksum_sha256`, `payment_amount`, `reason`, `payload`, etc.) are 100% excluded from Neo4j properties. | `32` sensitive table-column exclusions verified | `0` | **`PASS`** |

---

## 3. Phase 1.2.2 Modular Validation Suite (`scripts/phase1_2_2/`)

Phase 1.2.2 adds a dedicated modular validation suite under [`scripts/phase1_2_2/`](file:///C:/Project/chatbot/scripts/phase1_2_2/run_all.py) backed by synthetic multi-tenant fixtures in [`tests/phase1_2_2/`](file:///C:/Project/chatbot/tests/phase1_2_2/fixtures/synthetic_multi_tenant_fixture.json) and live read-only PostgreSQL 18.6 execution via [`scripts/phase1_2/pg_readonly.py`](file:///C:/Project/chatbot/scripts/phase1_2/pg_readonly.py):

| Script Module | Purpose & Hardening Scope | Verification Method | Status |
|---|---|---|---|
| [`validate_document_consistency.py`](file:///C:/Project/chatbot/scripts/phase1_2_2/validate_document_consistency.py) | Verifies cross-document alignment across `Docs 18, 29–39`, including Wave 3 count (`11 Nodes`, `5+3+11+5=24`), `SD-01`–`SD-07`, `SEC-01`–`SEC-25`, and `G1`–`G15`. | Direct Markdown parsing across `Docs 18, 29–39`. | **`PASS`** |
| [`validate_node_mapping.py`](file:///C:/Project/chatbot/scripts/phase1_2_2/validate_node_mapping.py) | Verifies all `24` Approved MVP nodes (`NM-01`–`NM-10`, `NM-12`–`NM-25`), `271` source columns in `schema_inventory.json`, `NM-21` `user_unambiguous_leave_tenant` (`CRITICAL-02`), and `NM-22` active membership filter (`CRITICAL-01`). | Markdown SQL/Cypher parsing + `schema_inventory.json` verification. | **`PASS`** |
| [`validate_relationship_mapping.py`](file:///C:/Project/chatbot/scripts/phase1_2_2/validate_relationship_mapping.py) | Verifies all `42` Approved MVP relationships (`108` properties), including `RM-04` active manager & tenant membership filter (`HIGH-05`), `RM-36` (`CRITICAL-02`), and `RM-37` (`CRITICAL-01`). | Markdown SQL/Cypher parsing + `Doc 38` cross-check. | **`PASS`** |
| [`validate_tenant_security.py`](file:///C:/Project/chatbot/scripts/phase1_2_2/validate_tenant_security.py) | Verifies all `25` security test cases (`SEC-01`–`SEC-25`), Dual-Scope `:Audience` (`CRITICAL-04`), Two-Template FTS (`Template FTS-A` / `FTS-B`), and executes synthetic multi-tenant isolation tests. | Static Cypher/SQL audit + in-memory SQLite/Graph fixture execution (`SEC-01`–`SEC-25`). | **`PASS`** |
| [`validate_membership_lifecycle.py`](file:///C:/Project/chatbot/scripts/phase1_2_2/validate_membership_lifecycle.py) | Verifies `Rule MEM-ACTIVE` vs `Rule MEM-HISTORICAL-UNAMBIGUOUS` (`Doc 29` Sec 2.3), Attendance **Cases A–E** (`CRITICAL-01`), LeaveBalance multi-tenant ambiguity quarantine (`CRITICAL-02`), and `RM-04` manager lifecycle (`HIGH-05`). | Executes synthetic SQLite + read-only PostgreSQL 18.6 test queries for Attendance Cases A–E, LeaveBalance, and Manager `RM-04`. | **`PASS`** |
| [`validate_etl_reconciliation.py`](file:///C:/Project/chatbot/scripts/phase1_2_2/validate_etl_reconciliation.py) | Verifies `Doc 33` Section 2.6 **24-Node Reconciliation Matrix (`Patterns R-1`–`R-7`)**, ensuring `:Tag` (`NM-24`) reconciles on `tag_key` (`R-7`), `:AttendanceRecord` (`NM-22`) reconciles on 6-step active-membership eligibility (`R-6`), soft-delete nodes never hard-delete on `is_deleted=true` (`R-2`/`R-3`), and circuit breaker `MAX_DELETE_RATIO = 0.05` is enforced (`CRITICAL-06`). | Parses `Doc 33` Section 2.6 table + simulates reconciliation patterns `R-1`–`R-7` on synthetic fixture. | **`PASS`** |
| [`validate_query_equivalence.py`](file:///C:/Project/chatbot/scripts/phase1_2_2/validate_query_equivalence.py) | Verifies SQL-vs-Cypher semantic equivalence for `Q01` (`HIGH-05`), `Q05` (`CRITICAL-03`), `Q08` (`CRITICAL-04`), `Q11` (`CRITICAL-01`/`02`), and `Q14` (`Template FTS-B`). | Static predicate audit + synthetic SQLite & live PostgreSQL 18.6 vs Python Graph simulation returning identical result sets. | **`PASS`** |
| [`validate_evidence_completeness.py`](file:///C:/Project/chatbot/scripts/phase1_2_2/validate_evidence_completeness.py) | Verifies `Doc 37` (`AC-01`–`AC-20`), `Doc 39` (`G1`–`G15`, 6 Readiness Dimensions, `SD-01`–`SD-07`), and confirms all 7 artifacts in `artifacts/phase1_2_2/` exist and are non-empty. | File existence + JSON/Markdown schema verification + strict separation of `EXECUTED`, `EXECUTED (SYNTHETIC FIXTURE)`, and `NOT EXECUTED` (live Neo4j). | **`PASS`** |

---

## 4. How to Run Both Validation Suites

```powershell
# 1. Run the Phase 1.2.2 modular validation & artifact generation suite (8 validators + synthetic fixture + PostgreSQL 18.6 tests)
C:\Users\admin\miniconda3\envs\chat\python.exe scripts\phase1_2_2\run_all.py

# 2. Run the Phase 1.2.1 13-check baseline validator (backward compatibility verification)
C:\Users\admin\miniconda3\envs\chat\python.exe scripts\phase1_2_1\validate_phase1_2_1.py
```

- **Generated Phase 1.2.2 Artifacts**:
  - [`artifacts/phase1_2_2/phase1_2_2_consistency_report.json`](file:///C:/Project/chatbot/artifacts/phase1_2_2/phase1_2_2_consistency_report.json)
  - [`artifacts/phase1_2_2/phase1_2_2_consistency_report.md`](file:///C:/Project/chatbot/artifacts/phase1_2_2/phase1_2_2_consistency_report.md)
  - [`artifacts/phase1_2_2/phase1_2_2_defect_register.md`](file:///C:/Project/chatbot/artifacts/phase1_2_2/phase1_2_2_defect_register.md)
  - [`artifacts/phase1_2_2/phase1_2_2_tenant_security_test_matrix.md`](file:///C:/Project/chatbot/artifacts/phase1_2_2/phase1_2_2_tenant_security_test_matrix.md)
  - [`artifacts/phase1_2_2/phase1_2_2_etl_reconciliation_matrix.md`](file:///C:/Project/chatbot/artifacts/phase1_2_2/phase1_2_2_etl_reconciliation_matrix.md)
  - [`artifacts/phase1_2_2/phase1_2_2_sql_cypher_equivalence.md`](file:///C:/Project/chatbot/artifacts/phase1_2_2/phase1_2_2_sql_cypher_equivalence.md)
  - [`artifacts/phase1_2_2/phase1_2_2_execution_log.txt`](file:///C:/Project/chatbot/artifacts/phase1_2_2/phase1_2_2_execution_log.txt)

---

## 4. Phase 1.2.3 Final Security & Reproducibility Suite (scripts/phase1_2_3/)

Phase 1.2.3 adds the final corrective and verification harness under [scripts/phase1_2_3/](file:///C:/Project/chatbot/scripts/phase1_2_3/run_all.py) backed by [	ests/phase1_2_3/fixtures/synthetic_multi_tenant_fixture.json](file:///C:/Project/chatbot/tests/phase1_2_3/fixtures/synthetic_multi_tenant_fixture.json):

| Module | Work Package & Hardening Scope | Verification Method | Status |
|---|---|---|---|
| [alidate_q01.py](file:///C:/Project/chatbot/scripts/phase1_2_3/validate_q01.py) | **WP1**: Validates detailed JSONB collection payload contract (sub_departments, ctive_employees) and caller authorization guard across tests Q01-01 through Q01-12. | Evaluates relational CTE jsonb_agg and Cypher collect() on synthetic fixture. | **PASS (12/12)** |
| [alidate_q08.py](file:///C:/Project/chatbot/scripts/phase1_2_3/validate_q08.py) | **WP2**: Validates corrected multi-source tenant isolation for custom audiences (independent owner, dept, user verification) across tests Q08-01 through Q08-14. Demonstrates elimination of flawed COALESCE vulnerability. | Evaluates side-by-side flawed vs corrected SQL and Cypher on cross-tenant notice 905. | **PASS (14/14)** |
| [circuit_breaker.py](file:///C:/Project/chatbot/scripts/phase1_2_3/circuit_breaker.py) | **WP3**: Enforces exact hard-delete safety formula loor(pop * 0.05), zero-population handling, protected :Tenant guard, and batch atomicity across unit tests CB-01 through CB-15. | Unit test suite (	ests/phase1_2_3/unit/test_circuit_breaker.py). | **PASS (15/15)** |
| [alidate_runner_integrity.py](file:///C:/Project/chatbot/scripts/phase1_2_3/validate_runner_integrity.py) | **WP4**: Enforces dynamic status evaluation, non-hardcoded PASS reporting, and metric accounting invariants across 7 failure-injection scenarios. | Failure injection suite (forced error, incomplete checks, unreached DB, missing fixture, invariant check). | **PASS (7/7)** |

---

## 5. How to Run the Master Validation Suite

`powershell
# Run the complete Phase 1.2.3 Master Suite (Regressions 1.2.1 + 1.2.2 + WP1 + WP2 + WP3 + WP4)
C:\Users\admin\miniconda3\envs\chat\python.exe scripts\phase1_2_3\run_all.py
`

- **Generated Phase 1.2.3 Evidence Artifacts in [rtifacts/phase1_2_3/](file:///C:/Project/chatbot/artifacts/phase1_2_3/)**:
  1. [phase1_2_3_inspection_report.md](file:///C:/Project/chatbot/artifacts/phase1_2_3/phase1_2_3_inspection_report.md)
  2. [phase1_2_3_q01_output_and_authorization_contract.md](file:///C:/Project/chatbot/artifacts/phase1_2_3/phase1_2_3_q01_output_and_authorization_contract.md)
  3. [phase1_2_3_q08_tenant_isolation_correction_report.md](file:///C:/Project/chatbot/artifacts/phase1_2_3/phase1_2_3_q08_tenant_isolation_correction_report.md)
  4. [phase1_2_3_circuit_breaker_specification.md](file:///C:/Project/chatbot/artifacts/phase1_2_3/phase1_2_3_circuit_breaker_specification.md)
  5. [phase1_2_3_automated_runner_execution_log.md](file:///C:/Project/chatbot/artifacts/phase1_2_3/phase1_2_3_automated_runner_execution_log.md)
  6. [phase1_2_3_sql_execution_log.md](file:///C:/Project/chatbot/artifacts/phase1_2_3/phase1_2_3_sql_execution_log.md)
  7. [phase1_2_3_cypher_execution_log.md](file:///C:/Project/chatbot/artifacts/phase1_2_3/phase1_2_3_cypher_execution_log.md)
  8. [phase1_2_3_cross_engine_equivalence_report.md](file:///C:/Project/chatbot/artifacts/phase1_2_3/phase1_2_3_cross_engine_equivalence_report.md)
  9. [phase1_2_3_final_acceptance_matrix.md](file:///C:/Project/chatbot/artifacts/phase1_2_3/phase1_2_3_final_acceptance_matrix.md)
  10. [phase1_2_3_final_readiness_report.md](file:///C:/Project/chatbot/artifacts/phase1_2_3/phase1_2_3_final_readiness_report.md)

## 4. Phase 1.2.3.1 Corrective Hardening & Independent Validation Suite (scripts/phase1_2_3_1/)

Phase 1.2.3.1 introduces a comprehensive corrective validation harness to close all 8 defects identified in Phase 1.2.3:

| Script / Test Module | Purpose & Scope | Tests & Result | Status |
|---|---|---|---|
| 	ests/phase1_2_3_1/unit/test_independent_executors.py | Proves AST call-graph independence between relational and graph simulators (IND-01), and executes intentional rule divergence test (IND-02). | IND-01, IND-02 (2/2) | **PASS** |
| scripts/phase1_2_3_1/validate_q01.py | Executes Q01 independent relational vs graph simulation across 12 test cases (Q01-01..Q01-12), verifying 100% exact JSON payload equivalence. | Q01-01 .. Q01-12 (12/12) | **PASS** |
| scripts/phase1_2_3_1/validate_q08.py | Executes Q08 multi-source tenant isolation across 18 test cases (Q08-01..Q08-18), verifying all 6 global audience invariants, 9 canonical fields, and LIMIT 20. | Q08-01 .. Q08-18 (18/18) | **PASS** |
| 	ests/phase1_2_3_1/unit/test_circuit_breaker.py | Verifies ETL hard-delete circuit breaker strict input validation across 25 unit test cases (CB-01..CB-25). | CB-01 .. CB-25 (25/25) | **PASS** |
| 	ests/phase1_2_3_1/unit/test_hard_delete_approval.py | Verifies HMAC-SHA256 scoped hard-delete approval guard tokens bound to batch ID, tenant, entity type, and candidate ceilings (HD-01..HD-12). | HD-01 .. HD-12 (12/12) | **PASS** |
| scripts/phase1_2_3_1/validate_runner_integrity.py | Executes 15 genuine failure-injection scenarios (RUN-01..RUN-15), asserting dynamic status calculation and metric accounting invariants. | RUN-01 .. RUN-15 (15/15) | **PASS** |
| scripts/phase1_2_3_1/status_aggregator.py | Central status calculation engine enforcing mandatory regression dependencies and strict metric accounting invariants. | Dynamic Status Engine | **PASS** |
| scripts/phase1_2_3_1/run_all.py | Master orchestrator running baselines P1.2.1, P1.2.2, WP1, WP2, WP3, WP4, generating machine-readable JSON and canonical Markdown reports. | 84/84 Checks | **PASS** |
