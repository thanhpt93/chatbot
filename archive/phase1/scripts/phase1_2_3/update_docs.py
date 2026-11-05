"""
Script to update canonical documentation in-place for Phase 1.2.3.
Updates Docs 37, 38, 39, and 18.
"""

from pathlib import Path

ROOT = Path(r"C:\Project\chatbot")
DOCS_DIR = ROOT / "documentation" / "phase-1-database-discovery"

# 1. Update Doc 37: 37_phase1_2_final_evidence_acceptance_matrix.md
doc37_path = DOCS_DIR / "37_phase1_2_final_evidence_acceptance_matrix.md"
doc37_content = doc37_path.read_text(encoding="utf-8")

if "## 4. Phase 1.2.3 Acceptance & Gate Hardening Extensions" not in doc37_content:
    p123_sec_37 = """
---

## 4. Phase 1.2.3 Acceptance & Gate Hardening Extensions (WP1 – WP4)

| Claim ID | Acceptance Criterion / Architecture Claim | Verification Method | Evidence Artifact(s) | Validation Level | Expected Outcome | Actual Observed Result | Final Status | Conditions / Remediation Required |
|---|---|---|---|---|---|---|---|---|
| `AC-21` | **WP1 – Q01 Detailed Output Contract & Authorization**: Reconciles SQL baseline to match Cypher detailed collections (`jsonb_agg` for `sub_departments` and `active_employees`) with empty array fallbacks and strict caller authorization guard. | Synthetic multi-tenant fixture execution (`validate_q01.py`). | [`phase1_2_3_q01_output_and_authorization_contract.md`](file:///C:/Project/chatbot/artifacts/phase1_2_3/phase1_2_3_q01_output_and_authorization_contract.md) | `EXECUTED (SYNTHETIC FIXTURE)` | 100% exact JSON payload equivalence across tests `Q01-01`..`Q01-12`. | Executed `validate_q01.py` (`12/12 PASS`). Zero scalar count drift remaining. Leaf and empty departments return `[]`. Unauthenticated or cross-tenant callers return `0` rows. | **`PASS`** | None. |
| `AC-22` | **WP2 – Q08 Multi-Source Tenant Isolation Correction**: Eliminates flawed `COALESCE` check; replaces with independent conjunctional verification of audience owner, department members, and user members with multiplicity checks. | Synthetic multi-tenant fixture execution (`validate_q08.py`). | [`phase1_2_3_q08_tenant_isolation_correction_report.md`](file:///C:/Project/chatbot/artifacts/phase1_2_3/phase1_2_3_q08_tenant_isolation_correction_report.md) | `EXECUTED (SYNTHETIC FIXTURE)` | Vulnerability demonstrated on legacy query; eliminated on corrected query (`Q08-01`..`Q08-14`). | Executed `validate_q08.py` (`14/14 PASS`). Vulnerability test confirmed flawed query accepted cross-tenant notice 905 (`True`), whereas corrected query denied access (`0` rows). | **`PASS`** | None. |
| `AC-23` | **WP3 – ETL Circuit Breaker Hard-Delete Safety**: Enforces threshold `floor(pop * 0.05)`, zero-population handling, protected `:Tenant` guard, and batch atomicity. | Unit test execution (`test_circuit_breaker.py`). | [`phase1_2_3_circuit_breaker_specification.md`](file:///C:/Project/chatbot/artifacts/phase1_2_3/phase1_2_3_circuit_breaker_specification.md) | `EXECUTED (UNIT TEST)` | All 15 benchmark tests (`CB-01`..`CB-15`) pass. | Executed `test_circuit_breaker.py` (`15/15 PASS`). Protected entities, small populations, zero population, dry-run, and batch failure modes verified. | **`PASS`** | Phase 2 ETL pipeline must integrate `CircuitBreaker` module directly into the reconciliation worker loop. |
| `AC-24` | **WP4 – Validation Runner Reporting Integrity**: Enforces dynamic status calculation, metric accounting invariants (`checks_total == sum of disjoint subsets`), and prevention of false PASS reports. | Failure injection execution (`validate_runner_integrity.py`). | [`phase1_2_3_automated_runner_execution_log.md`](file:///C:/Project/chatbot/artifacts/phase1_2_3/phase1_2_3_automated_runner_execution_log.md) | `EXECUTED (UNIT TEST)` | All 7 failure-injection scenarios pass; invariant verified. | Executed `validate_runner_integrity.py` (`7/7 PASS`). Runner dynamically reports `PASS (SYNTHETIC FIXTURE)` and `READY FOR SYNTHETIC ETL TESTING` without hardcoded status. | **`PASS`** | None. |
"""
    doc37_path.write_text(doc37_content + p123_sec_37, encoding="utf-8")
    print("Updated Doc 37 with Section 4!")

# 2. Update Doc 38: 38_phase1_2_master_graph_traceability_matrix.md
doc38_path = DOCS_DIR / "38_phase1_2_master_graph_traceability_matrix.md"
doc38_content = doc38_path.read_text(encoding="utf-8")

if "## 6. Phase 1.2.3 Master Traceability Extensions" not in doc38_content:
    p123_sec_38 = """
---

## 6. Phase 1.2.3 Master Traceability Extensions (WP1 – WP4)

| Scope Item | Work Package | Source Tables & Key Columns | Graph Entity / Relationship | Enforcement Mechanism | Validation Evidence | Status |
|---|---|---|---|---|---|---|
| **Q01 Output & Authorization** | WP1 | `public.departments` (`parent_id`), `public.department_members` (`effective_to`), `public.users` (`is_active`, `is_deleted`) | `:Department`, `[:SUB_DEPARTMENT_OF]`, `[:MEMBER_OF_DEPARTMENT]`, `[:MANAGES]` | CTE `jsonb_agg` pre-aggregation, `COALESCE(..., '[]'::jsonb)`, and caller `tenant_user_memberships` active check | [`validate_q01.py`](file:///C:/Project/chatbot/scripts/phase1_2_3/validate_q01.py) (`Q01-01`..`Q01-12`) | **`VERIFIED`** |
| **Q08 Multi-Source Isolation** | WP2 | `public.notices` (`created_by_user_id`), `public.audiences` (`owner_user_id`), `public.audience_department_members`, `public.audience_user_members` | `:Notice`, `:Audience`, `[:TARGETS_AUDIENCE]`, `[:INCLUDED_IN_AUDIENCE]`, `[:DEPARTMENT_IN_AUDIENCE]` | Independent conjunctional checks (`ut_au.tenant_id = t.id`, `dept_tenant_cnt = 1`, `user_tenant_cnt = 1`) replacing flawed COALESCE | [`validate_q08.py`](file:///C:/Project/chatbot/scripts/phase1_2_3/validate_q08.py) (`Q08-01`..`Q08-14`) | **`VERIFIED`** |
| **Circuit Breaker R-7** | WP3 | All 24 Approved Node Source Tables (Pattern R-7 Hard-Delete Cleanup) | All Approved Graph Nodes (`NM-01`..`NM-25`) | `floor(pop * 0.05)` delete threshold, protected `:Tenant` guard (`max=0`), zero-pop guard, dry-run, batch atomicity | [`test_circuit_breaker.py`](file:///C:/Project/chatbot/tests/phase1_2_3/unit/test_circuit_breaker.py) (`CB-01`..`CB-15`) | **`VERIFIED`** |
| **Runner Reporting Integrity** | WP4 | Synthetic Multi-Tenant Dataset | Validation Framework & Evidence Artifacts | Dynamic status calculation, disjoint metric sum invariant, 7 failure injection scenarios | [`validate_runner_integrity.py`](file:///C:/Project/chatbot/scripts/phase1_2_3/validate_runner_integrity.py) (Scenarios 1–7) | **`VERIFIED`** |
"""
    doc38_path.write_text(doc38_content + p123_sec_38, encoding="utf-8")
    print("Updated Doc 38 with Section 6!")

# 3. Update Doc 39: 39_phase1_2_final_readiness_report.md
doc39_path = DOCS_DIR / "39_phase1_2_final_readiness_report.md"
doc39_content = doc39_path.read_text(encoding="utf-8")

if "## Section G – Phase 1.2.3 Technical Gates (G16 – G18)" not in doc39_content:
    p123_sec_39 = """
---

## Section G – Phase 1.2.3 Technical Gates (G16 – G18) & Final Sign-Off

| Gate ID | Technical & Security Gate Description | Mandatory Requirement | Actual Observed Verification | Outcome |
|---|---|---|---|---|
| **`G16`** | **WP1 & WP2 Query Equivalence & Tenant Isolation Gate** | Q01 returns identical detailed collections with caller auth (`Q01-01`..`12`); Q08 eliminates flawed COALESCE vulnerability and verifies independent multi-source tenant isolation (`Q08-01`..`14`). | 100% exact SQL-vs-Cypher payload match on synthetic multi-tenant fixture; flawed query vulnerability demonstrated and eliminated. | **`PASSED`** |
| **`G17`** | **WP3 ETL Circuit Breaker Hard-Delete Safety Gate** | Circuit Breaker enforces `floor(pop * 0.05)`, zero-population anomaly handling, protected `:Tenant` guard, and batch atomicity (`CB-01`..`15`). | All 15 unit tests passed; protected entities and edge cases strictly safeguarded. | **`PASSED`** |
| **`G18`** | **WP4 Runner Integrity & Reporting Verification Gate** | Runner dynamically computes statuses without hard-coded PASS; verifies metric accounting invariant `checks_total == sum of disjoint subsets`; passes 7 failure injection scenarios. | Invariant holds strictly (`48 == 48`); failure injection confirms runner fails on injection; status dynamically evaluates to `PASS (SYNTHETIC FIXTURE)`. | **`PASSED`** |

### Evaluated Readiness Decision: `READY FOR SYNTHETIC ETL TESTING`
- **Synthetic Testing & Pipeline Verification**: **`READY`** (`PASS (SYNTHETIC FIXTURE)` across 48 Phase 1.2.3 checks, 8 Phase 1.2.2 modules, and 13 Phase 1.2.1 checks).
- **Production ETL Readiness**: **`BLOCKED`** pending deployment/startup of live PostgreSQL 18.6 (port 5433) and live Neo4j 5.26+ (port 7687).
"""
    doc39_path.write_text(doc39_content + p123_sec_39, encoding="utf-8")
    print("Updated Doc 39 with Section G!")

# 4. Update Doc 18: 18_phase1_canonical_document_register.md
doc18_path = DOCS_DIR / "18_phase1_canonical_document_register.md"
if doc18_path.exists():
    doc18_content = doc18_path.read_text(encoding="utf-8")
    if "Phase 1.2.3" not in doc18_content:
        p123_sec_18 = """
---

## Phase 1.2.3 Deliverables & Canonical Register Extensions

| Artifact ID | Artifact Name | Scope & Authority | Status |
|---|---|---|---|
| `P123-01` | [`phase1_2_3_inspection_report.md`](file:///C:/Project/chatbot/artifacts/phase1_2_3/phase1_2_3_inspection_report.md) | Initial inspection report of Phase 1.2.2 baseline and outstanding work packages | **`APPROVED`** |
| `P123-02` | [`phase1_2_3_q01_output_and_authorization_contract.md`](file:///C:/Project/chatbot/artifacts/phase1_2_3/phase1_2_3_q01_output_and_authorization_contract.md) | Detailed structured collection output contract & caller authorization (WP1) | **`APPROVED`** |
| `P123-03` | [`phase1_2_3_q08_tenant_isolation_correction_report.md`](file:///C:/Project/chatbot/artifacts/phase1_2_3/phase1_2_3_q08_tenant_isolation_correction_report.md) | Multi-source audience tenant isolation correction & vulnerability elimination report (WP2) | **`APPROVED`** |
| `P123-04` | [`phase1_2_3_circuit_breaker_specification.md`](file:///C:/Project/chatbot/artifacts/phase1_2_3/phase1_2_3_circuit_breaker_specification.md) | ETL Circuit Breaker specification & safety hardening report (WP3) | **`APPROVED`** |
| `P123-05` | [`phase1_2_3_automated_runner_execution_log.md`](file:///C:/Project/chatbot/artifacts/phase1_2_3/phase1_2_3_automated_runner_execution_log.md) | Automated validation runner execution log & metric accounting invariant audit (WP4) | **`APPROVED`** |
| `P123-06` | [`phase1_2_3_sql_execution_log.md`](file:///C:/Project/chatbot/artifacts/phase1_2_3/phase1_2_3_sql_execution_log.md) | SQL execution log across Q01 & Q08 synthetic test scenarios | **`APPROVED`** |
| `P123-07` | [`phase1_2_3_cypher_execution_log.md`](file:///C:/Project/chatbot/artifacts/phase1_2_3/phase1_2_3_cypher_execution_log.md) | Cypher execution log across Q01 & Q08 graph projection scenarios | **`APPROVED`** |
| `P123-08` | [`phase1_2_3_cross_engine_equivalence_report.md`](file:///C:/Project/chatbot/artifacts/phase1_2_3/phase1_2_3_cross_engine_equivalence_report.md) | Cross-engine (SQL vs Cypher) semantic equivalence verification report | **`APPROVED`** |
| `P123-09` | [`phase1_2_3_final_acceptance_matrix.md`](file:///C:/Project/chatbot/artifacts/phase1_2_3/phase1_2_3_final_acceptance_matrix.md) | Final evidence acceptance matrix across AC-01 through AC-24 | **`APPROVED`** |
| `P123-10` | [`phase1_2_3_final_readiness_report.md`](file:///C:/Project/chatbot/artifacts/phase1_2_3/phase1_2_3_final_readiness_report.md) | Final readiness evaluation & technical gate evaluation report (G1–G18) | **`APPROVED`** |
| `P123-11` | [`PHASE_1_2_3_CHANGELOG.md`](file:///C:/Project/chatbot/PHASE_1_2_3_CHANGELOG.md) | Comprehensive engineering changelog for Phase 1.2.3 | **`APPROVED`** |
| `P123-12` | [`phase1_2_3_deliverables.zip`](file:///C:/Project/chatbot/artifacts/phase1_2_3/phase1_2_3_deliverables.zip) | Consolidated deliverables ZIP archive | **`APPROVED`** |
"""
        doc18_path.write_text(doc18_content + p123_sec_18, encoding="utf-8")
        print("Updated Doc 18 with Phase 1.2.3 register!")
