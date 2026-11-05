# Phase 1.2.2 Automated Validation & Synthetic Fixture Suite (`scripts/phase1_2_2/`)

This directory contains the modular validation and synthetic multi-tenant fixture verification suite for **Phase 1.2.2 – ETL Lifecycle, Tenant Security & Runtime Evidence Hardening**.

## Validator Modules

1. `validate_document_consistency.py`: Verifies cross-document alignment across `Docs 18, 29–39`, Wave 3 count (`11 Nodes`, `5+3+11+5=24`), `SD-01`–`SD-07`, `SEC-01`–`SEC-25`, and `G1`–`G15`.
2. `validate_node_mapping.py`: Verifies all `24` Approved MVP nodes (`271` source columns, `297` runtime properties), `NM-21` `user_unambiguous_leave_tenant` (`CRITICAL-02`), and `NM-22` active membership filter (`CRITICAL-01`).
3. `validate_relationship_mapping.py`: Verifies all `42` Approved MVP relationships (`108` properties), including `RM-04` active manager & tenant membership (`HIGH-05`), `RM-36` (`CRITICAL-02`), and `RM-37` (`CRITICAL-01`).
4. `validate_tenant_security.py`: Verifies all `25` security test cases (`SEC-01`–`SEC-25`), Dual-Scope `:Audience` (`CRITICAL-04`), and Two-Template FTS (`Template FTS-A` / `FTS-B`).
5. `validate_membership_lifecycle.py`: Executes the synthetic SQLite + Graph fixture (`tests/phase1_2_2/`) to verify `Rule MEM-ACTIVE` vs `Rule MEM-HISTORICAL-UNAMBIGUOUS`, Attendance **Cases A–E** (`CRITICAL-01`), LeaveBalance ambiguity quarantine (`CRITICAL-02`), and Department Manager lifecycle (`HIGH-05`).
6. `validate_etl_reconciliation.py`: Verifies `Doc 33` Section 2.6 **24-Node Per-Node Reconciliation Matrix (`Patterns R-1`–`R-7`)**, composite synthetic key reconciliation (`:Tag.tag_key`), soft-delete retention (`R-2`/`R-3`), and circuit breaker (`MAX_DELETE_RATIO = 0.05`, `CRITICAL-06`).
7. `validate_query_equivalence.py`: Executes SQL-vs-Cypher semantic equivalence tests on the synthetic multi-tenant fixture for `Q01` (`HIGH-05`), `Q05` (`CRITICAL-03`), `Q08` (`CRITICAL-04`), `Q11` (`CRITICAL-01`/`02`), and `Q14` (`Template FTS-B`).
8. `validate_evidence_completeness.py`: Verifies `Doc 37` (`AC-01`–`AC-20`), `Doc 39` (`G1`–`G15`, 6 Readiness Dimensions, `SD-01`–`SD-07`), and confirms all 7 artifacts in `artifacts/phase1_2_2/` exist and are non-empty.
9. `run_all.py`: Orchestrates all 8 validator modules, generates the 7 artifacts in `artifacts/phase1_2_2/`, and exits with code `0` only if all checks pass.

## Usage

```powershell
C:\Users\admin\miniconda3\envs\chat\python.exe scripts\phase1_2_2\run_all.py
```
