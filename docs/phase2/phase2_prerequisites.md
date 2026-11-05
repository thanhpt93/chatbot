# Phase 2 Prerequisites & Handover Architecture Guide

## 1. Executive Handover Summary

This document defines the handover status, ready foundation components, environmental prerequisites, missing dependencies, and items requiring source confirmation for the transition into **Phase 2 – Graph Pipeline & Ingestion Implementation**.

Phase 1 (Database Discovery & Graph Foundation) has established:
- Complete relational schema inventory across 67 tables.
- Approved Node and Relationship mapping specifications (24 nodes, 43 relationships).
- Multi-tenant security rules and automated validation suites (84/84 passing checks).
- ETL reconciliation patterns (R-1 through R-7), hard-delete circuit breakers, and scoped approval guards.

---

## 2. Component Readiness Matrix

| Classification | Category | Component | Description & Location | Phase 2 Readiness Status |
| :--- | :--- | :--- | :--- | :--- |
| **AVAILABLE** | Graph Schema | 24 Approved Nodes | Full property, primary key, and tenant ownership specs in `documentation/phase-1-database-discovery/30_phase1_2_complete_node_mapping.md` | **READY FOR INGESTION** |
| **AVAILABLE** | Graph Schema | Approved Relationships | Master relationship IDs and edge mappings in `documentation/phase-1-database-discovery/31_phase1_2_complete_relationship_mapping.md` | **READY FOR INGESTION** |
| **AVAILABLE** | Security | Multi-Tenant Model | Tenant isolation rules, global vs tenant audiences in `documentation/phase-1-database-discovery/29_phase1_2_final_user_tenant_model.md` | **READY FOR IMPLEMENTATION** |
| **AVAILABLE** | ETL Spec | Reconciliation Rules | Patterns R-1 to R-7 in `documentation/phase-1-database-discovery/33_phase1_2_etl_synchronization_contract.md` | **READY FOR IMPLEMENTATION** |
| **AVAILABLE** | Constraints | Neo4j Constraints/Indexes | Cypher DDL for unique constraints and indexes in `documentation/phase-1-database-discovery/35_phase1_2_final_neo4j_constraints_indexes.md` | **READY FOR EXECUTION** |
| **AVAILABLE** | Automation | Circuit Breaker & Guard | ETL Circuit Breaker (CB-01 to CB-25) & Scoped Hard-Delete Approval Guard in `scripts/phase1_2_3_1/circuit_breaker.py` | **READY FOR ETL INTEGRATION** |
| **AVAILABLE** | Regression | Consistency Validators | Phase 1.2.1, 1.2.2, and 1.2.3.1 test runners in `scripts/` and `tests/` | **READY FOR CI/CD** |
| **AVAILABLE-UNVALIDATED** | Runtime DB | Live PostgreSQL Queries | Query templates verified against schema inventory and SQLite mock; requires live PostgreSQL connection | **REQUIRES LIVE DB VALIDATION** |
| **AVAILABLE-UNVALIDATED** | Runtime DB | Live Neo4j Cypher Execution | Cypher templates verified against AST parser and Cypher simulator; requires live Neo4j instance | **REQUIRES LIVE DB VALIDATION** |
| **MISSING** | Infrastructure | Live PostgreSQL Container | Running PostgreSQL instance with Groupware database restored on port `5432` or `5433` | **TO BE PROVISIONED IN PHASE 2** |
| **MISSING** | Infrastructure | Live Neo4j 5.x Instance | Running Neo4j instance with APOC plugin enabled on Bolt port `7687` | **TO BE PROVISIONED IN PHASE 2** |
| **MISSING** | Storage | Vector Database (Qdrant/Milvus) | Dedicated Vector DB for ChatMessage content embeddings (ChatMessage Option A) | **TO BE PROVISIONED IN PHASE 2** |
| **MISSING** | ETL Engine | Streaming / CDC Pipeline | Debezium / Kafka or scheduled micro-batch pipeline to trigger ETL jobs | **TO BE BUILT IN PHASE 2** |
| **NEEDS SOURCE CONFIRMATION** | Data Model | 84 Untracked Implicit FKs | Potential junction and foreign key references without schema constraints (`06_untracked_foreign_keys_and_implicit_relationships.md`) | **REQUIRES DOMAIN OWNER SIGN-OFF** |

---

## 3. Detailed Prerequisites for Phase 2 Kickoff

### 3.1 Infrastructure Setup (Mandatory Step 1)
1. **PostgreSQL Environment**:
   - Restore `database/inf_nffice_latest.dump` using `scripts/database-discovery/restore_database.py`.
   - Verify connection via `scripts/phase1_2/pg_readonly.py`.
   - Ensure read-only credentials for the ETL extraction worker.
2. **Neo4j Environment**:
   - Launch Neo4j 5.x Enterprise / Community.
   - Run constraint creation script: execute all Cypher statements from Doc 35 (`35_phase1_2_final_neo4j_constraints_indexes.md`).
   - Validate index creation using `SHOW CONSTRAINTS` and `SHOW INDEXES`.
3. **Vector Database**:
   - Deploy selected Vector DB (e.g. Qdrant / Milvus / pgvector).
   - Configure collection schema for ChatMessage content according to ChatMessage Option A.

### 3.2 Security and Circuit Breaker Integration
- All ingestion scripts must integrate `CircuitBreaker` and `ScopedHardDeleteApprovalGuard` from `scripts/phase1_2_3_1/circuit_breaker.py`.
- Any delete operation exceeding `MAX_DELETE_RATIO = 0.05` or `MAX_DELETE_ABSOLUTE = 100` must trigger a hard halt.
- Multi-source tenant validation must enforce session tenant claim checks on all incoming mutations.

### 3.3 Traceability & Acceptance
- Phase 2 implementation must maintain full traceability against the master traceability matrix in `documentation/phase-1-database-discovery/38_phase1_2_master_graph_traceability_matrix.md`.
- No new Node label or Relationship type may be introduced into Neo4j without updating the canonical documentation suite.
