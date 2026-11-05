# 18 – Phase 1, Phase 1.1, Phase 1.2, Phase 1.2.1 & Phase 1.2.2 Canonical Document Control Register
## Groupware AI Chatbot Project – Database Discovery & Graph Architecture Baseline

> [!IMPORTANT]
> **Document Governance Standard (Updated in Phase 1.2.2 — 2026-11-05)**:
> This register serves as the authoritative document control catalog for all deliverables across **Phase 1 (`01`–`17`)**, **Phase 1.1 (`18`–`28`)**, and **Phase 1.2 / 1.2.1 / 1.2.2 (`29`–`39`)**. Every document is classified by its lifecycle status (`CANONICAL`, `SUPERSEDED`, `ARCHIVED`, or `NEEDS UPDATE`), replacing document reference, and known issues.
> Historical documents are preserved for auditability, and the existing **Phase 1.2 CANONICAL (`29`–`39`)** deliverables have been updated in place during **Phase 1.2.1** (`Final Technical Defect Correction`) and **Phase 1.2.2** (`ETL Lifecycle, Tenant Security & Runtime Evidence Hardening`) to represent the single reconciled baseline for Phase 2 implementation.

---

## 1. Authoritative Document Control Matrix (`01` – `39`)

| File Name | Functional Responsibility | Document Status | Canonical Replacement | Identified Issues / Reconciliation Notes |
|---|---|---|---|---|
| `01_database_overview.md` | Executive Architecture & Restoration Report | **CANONICAL (Phase 1 Baseline)** | `39_phase1_2_final_readiness_report.md` | Note: Actual restored engine in `schema_inventory.json` is `PostgreSQL 18.6 on x86_64-windows` (`228` base tables + `9` views = `237` objects; `1,480,332` rows). |
| `02_database_schema_inventory.md` | Exhaustive Schema & Physical Table Counts | **CANONICAL (Phase 1 Baseline)** | `36_phase1_2_automated_consistency_validation.md` | Details all 228 Base Tables and 9 Views across 4 schemas (`public`, `hangfire`, `_backup_cleanup_20261005`, `maintenance_backup`). |
| `03_data_dictionary.md` | Column-Level Data Dictionary | **SUPERSEDED** | `30_phase1_2_complete_node_mapping.md` | Documents 198 `public` tables (2,225 columns). |
| `04_database_relationships.md` | Initial Relationship Discovery Overview | **SUPERSEDED** | `31_phase1_2_complete_relationship_mapping.md` | Early automated discovery report; superseded by Phase 1.2.2 relationship contracts. |
| `05_business_entity_catalog.md` | Initial Entity Investigation Draft | **SUPERSEDED** | `30_phase1_2_complete_node_mapping.md` | Outdated attribute names and entity list. |
| `05_business_entity_master_catalog.md` | Authoritative 23 Business Entity Catalog | **SUPERSEDED** | `30_phase1_2_complete_node_mapping.md` | Superseded by the 27-node Phase 1.2.2 evaluation (`24` Approved MVP, `1` Blocked, `2` Future). |
| `06_business_module_classification.md` | Business Domain Module Taxonomies | **CANONICAL (Phase 1 Baseline)** | None (Self) | Accurate business domain decomposition. |
| `07_data_quality_report.md` | Initial Data Quality & Profiling Report | **SUPERSEDED** | `31_phase1_2_complete_relationship_mapping.md` & `artifacts/phase1_2/data_profile.txt` | Superseded by exact match-rate and orphan profiling in Phase 1.2.2. |
| `08_chatbot_query_readiness.md` | Chatbot Query Readiness (Legacy Name) | **SUPERSEDED** | `34_phase1_2_query_and_security_validation.md` | Synchronized twin of `08_database_query_readiness.md`; superseded by `Doc 34` (`Q01`–`Q14`). |
| `08_database_query_readiness.md` | Enterprise Business Query Validation | **SUPERSEDED** | `34_phase1_2_query_and_security_validation.md` | Reconciled in `Doc 34` (`Q01`–`Q14`, including Community Posts `Q13` and User Directory FTS `Q14`). |
| `09_database_discovery_erd.md` | Visual Relational Schema & Target Graph ERD | **CANONICAL (Phase 1 Baseline)** | `32_phase1_2_final_graph_architecture.md` | Distinguishes relational domain references (`REF`) from explicit foreign keys (`FK`). |
| `10_phase1_acceptance_report.md` | Phase 1 Acceptance Report | **SUPERSEDED** | `39_phase1_2_final_readiness_report.md` | Superseded by Phase 1.2.2 Final Readiness Report. |
| `11_business_entity_master_catalog.md` | Business Entity Master Catalog (Twin) | **SUPERSEDED** | `30_phase1_2_complete_node_mapping.md` | Superseded by `Doc 30`. |
| `11_relationship_master_inventory.md` | Relationship Master Inventory (Twin) | **SUPERSEDED** | `31_phase1_2_complete_relationship_mapping.md` | Superseded by `Doc 31`. |
| `12_relationship_master_inventory.md` | Complete 278-Relationship Inventory | **CANONICAL (Relational Inventory)** | `31_phase1_2_complete_relationship_mapping.md` | Full row-level relational register; graph relationships are governed by `Doc 31`. |
| `12_tenant_and_authorization_model.md` | Multi-Tenant Architecture & RBAC Model | **SUPERSEDED** | `29_phase1_2_final_user_tenant_model.md` | Superseded by `Doc 29`. |
| `13_tenant_and_authorization_discovery.md` | Tenant & Authorization Discovery | **SUPERSEDED** | `29_phase1_2_final_user_tenant_model.md` | Superseded by `Doc 29`. |
| `13_data_classification_and_graph_scope.md` | Six-Tier Data Classification Register | **SUPERSEDED** | `30_phase1_2_complete_node_mapping.md` & `38_phase1_2_master_graph_traceability_matrix.md` | Superseded by Phase 1.2.2 classification and redaction contracts. |
| `14_data_classification_and_graph_scope.md` | Data Classification & Graph Boundaries | **SUPERSEDED** | `30_phase1_2_complete_node_mapping.md` & `38_phase1_2_master_graph_traceability_matrix.md` | Superseded by Phase 1.2.2 classification and redaction contracts. |
| `14_graph_data_model.md` | Neo4j Graph Model Specification | **SUPERSEDED** | `32_phase1_2_final_graph_architecture.md` | Superseded by Phase 1.2.2 Final Graph Architecture. |
| `15_phase1_review_and_correction_report.md` | Phase 1 Review & Correction Master | **SUPERSEDED** | `39_phase1_2_final_readiness_report.md` | Superseded by `Doc 39`. |
| `15_source_to_graph_mapping_specification.md`| Source-to-Graph Mapping Contract | **SUPERSEDED** | `30_phase1_2_complete_node_mapping.md` & `31_phase1_2_complete_relationship_mapping.md` | Superseded by `Docs 30 & 31`. |
| `16_phase1_evidence_validation_matrix.md` | Requirements Evidence Matrix (AC-01 - AC-20)| **SUPERSEDED** | `37_phase1_2_final_evidence_acceptance_matrix.md` | Superseded by `Doc 37`. |
| `17_phase1_decision_log.md` | Architectural Decision Log (ADR-01 - ADR-07)| **CANONICAL (Decision Baseline)** | `39_phase1_2_final_readiness_report.md` | Formal record of initial ADRs; extended in `Doc 39` (`AD-01`–`AD-07`, `SD-01`–`SD-07`). |
| `18_phase1_1_canonical_document_register.md` | Master Document Control Register | **CANONICAL** | None (Self) | Master catalog and governance authority across Phases 1, 1.1, 1.2, 1.2.1, and 1.2.2 (This document). |
| `19_phase1_1_database_schema_reconciliation.md`| Phase 1.1 Database Schema Audit | **SUPERSEDED** | `36_phase1_2_automated_consistency_validation.md` & `37_phase1_2_final_evidence_acceptance_matrix.md` | Contained false claims (`telemetry_events` 401,944 rows, `maintenance_backup.users_backup`, 12 no-PK tables instead of 19). Corrected in Phase 1.2. |
| `20_phase1_1_relationship_reconciliation.md` | Phase 1.1 Relationship Audit | **SUPERSEDED** | `31_phase1_2_complete_relationship_mapping.md` | Superseded by complete 45-relationship mapping in `Doc 31`. |
| `21_phase1_1_final_graph_data_model.md` | Phase 1.1 Graph Model | **SUPERSEDED** | `32_phase1_2_final_graph_architecture.md` | Contained scalar `User.tenant_id`, non-existent columns (`ContractHistory.start_date/end_date/status`, `AttendanceRecord.working_minutes`, `Post.category_id`, `Permission.tenant_id`), and unverified `:WorkflowTemplate`. |
| `22_phase1_1_tenant_authorization_finalization.md`| Phase 1.1 Tenant & RBAC Model | **SUPERSEDED** | `29_phase1_2_final_user_tenant_model.md` | Missed `public.check_user_permission(...)` routine and `tenants.tenant_key` column. Reconciled in `Doc 29`. |
| `23_phase1_1_data_classification_reconciliation.md`| Phase 1.1 Classification Register | **SUPERSEDED** | `30_phase1_2_complete_node_mapping.md` & `38_phase1_2_master_graph_traceability_matrix.md` | Claimed non-existent `telemetry_events` and claimed `user_contract_histories` had salary columns (`0` exist). Reconciled in `Docs 30 & 38`. |
| `24_phase1_1_final_source_to_graph_mapping.md` | Phase 1.1 Source-to-Graph Mapping | **SUPERSEDED** | `30_phase1_2_complete_node_mapping.md`, `31_phase1_2_complete_relationship_mapping.md`, `33_phase1_2_etl_synchronization_contract.md` | Mapped only 17 of 23 operational nodes and 4 of 31 operational relationships; filtered out inactive departments/rooms referenced by FKs. Reconciled in `Docs 30, 31, 33`. |
| `25_phase1_1_chatbot_query_readiness.md` | Phase 1.1 Chatbot Queries | **SUPERSEDED** | `34_phase1_2_query_and_security_validation.md` | Used invalid `u.tenant_id`, lowercase `'pending'` on uppercase `approval_requests.status`, and non-existent HR columns. Reconciled in `Doc 34`. |
| `26_phase1_1_neo4j_index_constraint_design.md`| Phase 1.1 Neo4j Constraints & Indexes | **SUPERSEDED** | `35_phase1_2_final_neo4j_constraints_indexes.md` | Included invalid `idx_user_tenant`, `idx_permission_tenant`, `idx_room_tenant`, `idx_asset_cat_tenant`. Reconciled in `Doc 35`. |
| `27_phase1_1_final_evidence_validation_matrix.md`| Phase 1.1 Evidence Matrix | **SUPERSEDED** | `37_phase1_2_final_evidence_acceptance_matrix.md` | Overstated `PASS` on unexecuted Cypher and incomplete mappings. Reconciled in `Doc 37`. |
| `28_phase1_1_final_readiness_report.md` | Phase 1.1 Readiness Report | **SUPERSEDED** | `39_phase1_2_final_readiness_report.md` | Superseded by Phase 1.2.2 Final Readiness Report (`Doc 39`). |
| **`29_phase1_2_final_user_tenant_model.md`** | **WP1: Final User, Tenant, Lifecycle, Audience & FTS Security Model** | **CANONICAL (Phase 1.2.2)** | None (Self) | Reconciles global `:User` + `[:MEMBER_OF]->(:Tenant)`, Section 2.3 Membership Lifecycle Rules (`Rule MEM-ACTIVE` vs `Rule MEM-HISTORICAL-UNAMBIGUOUS`), 6-step `:AttendanceRecord` active-membership resolution (`CRITICAL-01` Cases A–E), `:LeaveBalance` multi-tenant safety (`CRITICAL-02`, `SD-07`), Dual-Scope `:Audience` (`DEFECT 04`), and Two-Template FTS (`DEFECT 05`). |
| **`30_phase1_2_complete_node_mapping.md`** | **WP2: Complete Node Mapping Specification** | **CANONICAL (Phase 1.2.2)** | None (Self) | Exhaustive SQL + Cypher mapping for all 24 Approved MVP nodes (`NM-01`–`NM-25`, `271` source cols, `297` runtime props), Graph Identity Keys (`id` vs `tag_key`), `NM-21` (`CRITICAL-02`), and `NM-22` (`CRITICAL-01`). |
| **`31_phase1_2_complete_relationship_mapping.md`** | **WP3: Complete Relationship Mapping Specification** | **CANONICAL (Phase 1.2.2)** | None (Self) | Exhaustive SQL + Cypher mapping for all 45 evaluated relationships (`42` Approved MVP, `1` Blocked `RM-19`, `2` Future `RM-44`–`RM-45`), including `RM-04` active manager & tenant membership (`HIGH-05`), `RM-36` (`CRITICAL-02`), and `RM-37` (`CRITICAL-01`). |
| **`32_phase1_2_final_graph_architecture.md`** | **WP4: Final Graph Architecture (Architecture B)** | **CANONICAL (Phase 1.2.2)** | None (Self) | Reconciles Operational Graph, Semantic Knowledge Graph, ChatMessage Option A, Vector DB linking keys, and `Template FTS-A`/`FTS-B`. |
| **`33_phase1_2_etl_synchronization_contract.md`** | **WP5: ETL & Synchronization Contract** | **CANONICAL (Phase 1.2.2)** | None (Self) | Defines all 15 ETL lifecycle behaviors, Wave 3 count (`11 Nodes`), Section 2.6 **24-Node Per-Node Reconciliation & Safe Hard-Delete Specification (`Patterns R-1`–`R-7`, `CRITICAL-06`)**, and circuit breaker (`MAX_DELETE_RATIO = 0.05`). |
| **`34_phase1_2_query_and_security_validation.md`** | **WP6: Query Readiness & Security Validation** | **CANONICAL (Phase 1.2.2)** | None (Self) | 14 reconciled Cypher + SQL query scenarios (`Q01`–`Q14`), Section 4 SQL-vs-Cypher Equivalence Matrix (`Q01`, `Q05`, `Q08`, `CRITICAL-03`, `CRITICAL-04`, `HIGH-05`), and 25 security test contracts (`SEC-01`–`SEC-25`). |
| **`35_phase1_2_final_neo4j_constraints_indexes.md`** | **WP7: Final Neo4j Constraints & Indexes** | **CANONICAL (Phase 1.2.2)** | None (Self) | 30 uniqueness constraints, 27 composite/relationship lookup indexes (`IDX-01`–`IDX-26` incl. `IDX-16A`/`16B`), 4 optional indexes, and 4 fulltext indexes (`Template FTS-A`/`FTS-B`). |
| **`36_phase1_2_automated_consistency_validation.md`** | **WP8: Automated Consistency Validation** | **CANONICAL (Phase 1.2.2)** | None (Self) | Documents `scripts/phase1_2_2/run_all.py` (`8` modular validators + synthetic fixture tests) and `scripts/phase1_2_1/validate_phase1_2_1.py` (`13/13` baseline checks). |
| **`37_phase1_2_final_evidence_acceptance_matrix.md`** | **WP9: Final Evidence & Acceptance Matrix** | **CANONICAL (Phase 1.2.2)** | None (Self) | Audits `AC-01`–`AC-20` with strict separation of `EXECUTED`, `EXECUTED (SYNTHETIC FIXTURE)`, `STATICALLY VALIDATED`, `NOT VERIFIED` (`AC-05B`), `NOT EXECUTED` (live Neo4j `AC-15`, `AC-17`), and `BLOCKED` (`AC-08`). |
| **`38_phase1_2_master_graph_traceability_matrix.md`** | **Section 14: Master Graph Traceability Matrix** | **CANONICAL (Phase 1.2.2)** | None (Self) | End-to-end traceability across all 27 nodes (including reconciliation patterns `R-1`–`R-7`) and 45 relationships + Section 4 Reconciled Property Count Breakdown Table (`DEFECT 07`). |
| **`39_phase1_2_final_readiness_report.md`** | **Sections 15–19: Final Readiness Report** | **CANONICAL (Phase 1.2.2)** | None (Self) | Evaluates all 6 Readiness Dimensions, Gates `G1`–`G15`, Open Stakeholder Decisions `SD-01`–`SD-07`, and concludes `READY FOR PHASE 2 WITH CONDITIONS`. |

---

## 2. Document Governance Policies
1. **Preservation of Audit Trail**: No historical documents from Phase 1 (`01`–`17`) or Phase 1.1 (`18`–`28`) are deleted. Superseded files are preserved in `documentation/phase-1-database-discovery/` for auditability.
2. **Authority Hierarchy**: If any conflict arises between documents, the strict hierarchy of authority is:
   `Phase 1.2.2 Updated Canonical Deliverables (29–39)` > `Automated Consistency Reports (artifacts/phase1_2_2/phase1_2_2_consistency_report.json & artifacts/phase1_2_1/phase1_2_1_consistency_report.json)` > `Phase 1.1 Deliverables (18–28)` > `Phase 1 Deliverables (01–17)`.

---

## Phase 1.2.3 Deliverables & Canonical Register Extensions

| Artifact ID | Artifact Name | Scope & Authority | Status |
|---|---|---|---|
| P123-01 | [phase1_2_3_inspection_report.md](file:///C:/Project/chatbot/artifacts/phase1_2_3/phase1_2_3_inspection_report.md) | Initial inspection report of Phase 1.2.2 baseline and outstanding work packages | **APPROVED** |
| P123-02 | [phase1_2_3_q01_output_and_authorization_contract.md](file:///C:/Project/chatbot/artifacts/phase1_2_3/phase1_2_3_q01_output_and_authorization_contract.md) | Detailed structured collection output contract & caller authorization (WP1) | **APPROVED** |
| P123-03 | [phase1_2_3_q08_tenant_isolation_correction_report.md](file:///C:/Project/chatbot/artifacts/phase1_2_3/phase1_2_3_q08_tenant_isolation_correction_report.md) | Multi-source audience tenant isolation correction & vulnerability elimination report (WP2) | **APPROVED** |
| P123-04 | [phase1_2_3_circuit_breaker_specification.md](file:///C:/Project/chatbot/artifacts/phase1_2_3/phase1_2_3_circuit_breaker_specification.md) | ETL Circuit Breaker specification & safety hardening report (WP3) | **APPROVED** |
| P123-05 | [phase1_2_3_automated_runner_execution_log.md](file:///C:/Project/chatbot/artifacts/phase1_2_3/phase1_2_3_automated_runner_execution_log.md) | Automated validation runner execution log & metric accounting invariant audit (WP4) | **APPROVED** |
| P123-06 | [phase1_2_3_sql_execution_log.md](file:///C:/Project/chatbot/artifacts/phase1_2_3/phase1_2_3_sql_execution_log.md) | SQL execution log across Q01 & Q08 synthetic test scenarios | **APPROVED** |
| P123-07 | [phase1_2_3_cypher_execution_log.md](file:///C:/Project/chatbot/artifacts/phase1_2_3/phase1_2_3_cypher_execution_log.md) | Cypher execution log across Q01 & Q08 graph projection scenarios | **APPROVED** |
| P123-08 | [phase1_2_3_cross_engine_equivalence_report.md](file:///C:/Project/chatbot/artifacts/phase1_2_3/phase1_2_3_cross_engine_equivalence_report.md) | Cross-engine (SQL vs Cypher) semantic equivalence verification report | **APPROVED** |
| P123-09 | [phase1_2_3_final_acceptance_matrix.md](file:///C:/Project/chatbot/artifacts/phase1_2_3/phase1_2_3_final_acceptance_matrix.md) | Final evidence acceptance matrix across AC-01 through AC-24 | **APPROVED** |
| P123-10 | [phase1_2_3_final_readiness_report.md](file:///C:/Project/chatbot/artifacts/phase1_2_3/phase1_2_3_final_readiness_report.md) | Final readiness evaluation & technical gate evaluation report (G1–G18) | **APPROVED** |
| P123-11 | [PHASE_1_2_3_CHANGELOG.md](file:///C:/Project/chatbot/PHASE_1_2_3_CHANGELOG.md) | Comprehensive engineering changelog for Phase 1.2.3 | **APPROVED** |
| P123-12 | [phase1_2_3_deliverables.zip](file:///C:/Project/chatbot/artifacts/phase1_2_3/phase1_2_3_deliverables.zip) | Consolidated deliverables ZIP archive | **APPROVED** |

## Phase 1.2.3.1 Deliverables & Defect Closure Register Extensions

| Artifact ID | Artifact Name | Scope & Authority | Status |
|---|---|---|---|
| P1231-01 | [phase1_2_3_1_inspection_report.md](file:///C:/Project/chatbot/artifacts/phase1_2_3_1/phase1_2_3_1_inspection_report.md) | Inspection report auditing defects DEF-P1231-01 through 08 | **APPROVED** |
| P1231-02 | [phase1_2_3_1_defect_register.md](file:///C:/Project/chatbot/artifacts/phase1_2_3_1/phase1_2_3_1_defect_register.md) | Master Defect Register tracking root cause, test, and resolution | **APPROVED** |
| P1231-03 | [q01_equivalence_report.md](file:///C:/Project/chatbot/artifacts/phase1_2_3_1/q01_equivalence_report.md) | True relational vs graph independent equivalence report (WP1) | **APPROVED** |
| P1231-04 | [q08_security_report.md](file:///C:/Project/chatbot/artifacts/phase1_2_3_1/q08_security_report.md) | Multi-source isolation & 6 global invariants verification report (WP2) | **APPROVED** |
| P1231-05 | [circuit_breaker_report.md](file:///C:/Project/chatbot/artifacts/phase1_2_3_1/circuit_breaker_report.md) | Strict input validation & scoped approval guard report (WP3) | **APPROVED** |
| P1231-06 | [runner_integrity_report.md](file:///C:/Project/chatbot/artifacts/phase1_2_3_1/runner_integrity_report.md) | Runner integrity & genuine failure injection report (WP4) | **APPROVED** |
| P1231-07 | [regression_report.json](file:///C:/Project/chatbot/artifacts/phase1_2_3_1/regression_report.json) | Machine-readable master regression evidence JSON | **APPROVED** |
| P1231-08 | [regression_report.md](file:///C:/Project/chatbot/artifacts/phase1_2_3_1/regression_report.md) | Master regression report incorporating P1.2.1, P1.2.2, WP1-WP4 | **APPROVED** |
| P1231-09 | [execution_log.txt](file:///C:/Project/chatbot/artifacts/phase1_2_3_1/execution_log.txt) | Immutable master validation runner execution log | **APPROVED** |
| P1231-10 | [readiness_report.md](file:///C:/Project/chatbot/artifacts/phase1_2_3_1/readiness_report.md) | Final readiness & production gate certification report | **APPROVED** |
| P1231-11 | [PHASE_1_2_3_1_CHANGELOG.md](file:///C:/Project/chatbot/PHASE_1_2_3_1_CHANGELOG.md) | Engineering changelog for Phase 1.2.3.1 | **APPROVED** |
| P1231-12 | [phase1_2_3_1_deliverables.zip](file:///C:/Project/chatbot/artifacts/phase1_2_3_1/phase1_2_3_1_deliverables.zip) | Complete deliverable archive including Docs 01–39 & SHA-256 manifest | **APPROVED** |
