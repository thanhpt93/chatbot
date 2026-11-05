# Phase 1.2.3 Deliverable: ETL Circuit Breaker Specification & Safety Hardening

**Phase**: 1.2.3 – Final Security Correction & Evidence Reproducibility Gate  
**Work Package**: WP3  
**Scope**: Graph Reconciliation Hard-Delete Safety (Reconciliation Pattern R-7)  
**Modules**: `scripts/phase1_2_3/circuit_breaker.py`, `scripts/phase1_2_3/reconciliation_safety.py`  
**Status**: APPROVED & 100% UNIT TESTED (`CB-01` .. `CB-15`)  

---

## 1. Problem Context & Architectural Purpose

Under Reconciliation Pattern `R-7` (Hard-Delete Cleanup for hard-deleted PostgreSQL source records), the ETL reconciles Neo4j graph nodes against PostgreSQL primary keys.
If a bug, network partition, truncated ETL query, or accidental drop of a table occurs in PostgreSQL, a naive reconciliation process would detect massive "missing" keys and **catastrophically delete operational graph nodes in Neo4j**.

The **Circuit Breaker** acts as an automated safety gate that halts reconciliation before any destructive graph deletion can occur if candidate deletions exceed the safety threshold.

---

## 2. Specification & Arithmetic Rules

### 2.1 Threshold Formula
```python
max_allowed_delete_count = math.floor(eligible_graph_node_count * 0.05)
```
The threshold ratio is strictly `5%` (`0.05`) with integer truncation via floor:
- Population `100`: `floor(100 * 0.05) = 5`. Up to 5 deletions allowed; 6 causes immediate trip.
- Population `20`: `floor(20 * 0.05) = 1`. 1 allowed; 2 causes immediate trip.
- Population `19`: `floor(19 * 0.05) = 0`. Zero deletions allowed; any deletion attempts trip.
- Population `1000`: `floor(1000 * 0.05) = 50`. 50 allowed; 51 causes immediate trip.

### 2.2 Safety Invariants & Boundary Handlers

1. **Extraction Completeness Invariant**:
   - If `extraction_complete == False` (e.g. database query timed out or pagination failed), deletion is immediately aborted (`reason: INCOMPLETE_EXTRACTION`).
2. **Protected Entity Invariant**:
   - `:Tenant` (`NM-01`) nodes can **NEVER** be deleted by automated reconciliation. `max_allowed_delete_count = 0`. Any deletion candidate causes immediate abort (`reason: PROTECTED_ENTITY_TYPE`).
3. **Zero Population Anomaly Invariant**:
   - `eligible_graph_node_count == 0` and `candidate_delete_count == 0`: ALLOW (`reason: NO_OP_ZERO_POP`).
   - `eligible_graph_node_count == 0` and `candidate_delete_count > 0`: ABORT (`reason: ZERO_POP_NONZERO_DELETE`).
4. **Dry-Run Mode**:
   - When `dry_run == True`, trips are recorded as `decision: SIMULATED_TRIP` with detailed audit logging, without executing Cypher deletions.
5. **Batch Reconciliation Atomicity**:
   - If multiple entities are processed in a single batch (e.g., Department, Task, Project), and any single entity trips the circuit breaker, the entire batch is aborted (`decision: BATCH_ABORT`).

---

## 3. Implementation Modules

### 3.1 `scripts/phase1_2_3/circuit_breaker.py`
Provides the `CircuitBreaker` class with:
- `evaluate(entity_type, eligible_graph_node_count, candidate_delete_count, extraction_complete, dry_run)`
- `evaluate_batch(batch_requests, dry_run)`

### 3.2 `scripts/phase1_2_3/reconciliation_safety.py`
Provides the `ReconciliationSafetyController` class with:
- Default `hard_delete_enabled = False` (`SAFE_MODE`).
- Audit logging for all planned deletions.
- Integration between the Circuit Breaker and Neo4j execution dispatch.

---

## 4. Test Verification Suite (CB-01 through CB-15)

All 15 benchmark test cases were executed and passed (`15/15 PASS`):

| Test ID | Entity Type | Population | Candidate Deletes | Extr. Complete | Dry Run | Expected Decision | Actual Decision | Max Allowed | Reason / Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `CB-01` | Department | 100 | 3 | True | False | `ALLOW` | `ALLOW` | 5 | `WITHIN_THRESHOLD` (**PASS**) |
| `CB-02` | Department | 100 | 5 | True | False | `ALLOW` | `ALLOW` | 5 | `WITHIN_THRESHOLD` (**PASS**) |
| `CB-03` | Department | 100 | 6 | True | False | `ABORT` | `ABORT` | 5 | `THRESHOLD_EXCEEDED` (**PASS**) |
| `CB-04` | Project | 20 | 1 | True | False | `ALLOW` | `ALLOW` | 1 | `WITHIN_THRESHOLD` (**PASS**) |
| `CB-05` | Project | 20 | 2 | True | False | `ABORT` | `ABORT` | 1 | `THRESHOLD_EXCEEDED` (**PASS**) |
| `CB-06` | Task | 19 | 0 | True | False | `ALLOW` | `ALLOW` | 0 | `WITHIN_THRESHOLD` (**PASS**) |
| `CB-07` | Task | 19 | 1 | True | False | `ABORT` | `ABORT` | 0 | `THRESHOLD_EXCEEDED` (**PASS**) |
| `CB-08` | Notice | 0 | 0 | True | False | `ALLOW` | `ALLOW` | 0 | `NO_OP_ZERO_POP` (**PASS**) |
| `CB-09` | Notice | 0 | 1 | True | False | `ABORT` | `ABORT` | 0 | `ZERO_POP_NONZERO_DELETE` (**PASS**) |
| `CB-10` | User | 1000 | 50 | True | False | `ALLOW` | `ALLOW` | 50 | `WITHIN_THRESHOLD` (**PASS**) |
| `CB-11` | User | 1000 | 51 | True | False | `ABORT` | `ABORT` | 50 | `THRESHOLD_EXCEEDED` (**PASS**) |
| `CB-12` | Tenant | 50 | 1 | True | False | `ABORT` | `ABORT` | 0 | `PROTECTED_ENTITY_TYPE` (**PASS**) |
| `CB-13` | Department | 100 | 1 | False | False | `ABORT` | `ABORT` | 0 | `INCOMPLETE_EXTRACTION` (**PASS**) |
| `CB-14` | Department | 100 | 10 | True | True | `SIMULATED_TRIP` | `SIMULATED_TRIP` | 5 | `THRESHOLD_EXCEEDED_DRY_RUN` (**PASS**) |
| `CB-15` | Batch | Multi | Multi | True | False | `BATCH_ABORT` | `BATCH_ABORT` | N/A | `Tripped by Task` (**PASS**) |
