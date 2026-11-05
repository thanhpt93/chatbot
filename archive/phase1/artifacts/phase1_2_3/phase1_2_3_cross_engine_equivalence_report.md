# Phase 1.2.3 Cross-Engine Equivalence Report

**Execution Timestamp**: `2026-11-05T07:29:39.456155+00:00`  
**Comparison Engines**: PostgreSQL 18.6 (Relational SQL) vs Neo4j 5.26+ (Graph Cypher)  
**Equivalence Metric**: 100% Exact JSON Payload Equivalence  

---

## 1. Summary of Equivalence Results

| Query Scenario | Test Range | Total Tests | SQL Status | Cypher Status | Cross-Engine Equivalence |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Q01 – Org Hierarchy** | `Q01-01` .. `Q01-12` | 12 | `12/12 PASS` | `12/12 PASS` | `100% IDENTICAL` |
| **Q08 – Published Notices** | `Q08-01` .. `Q08-14` | 14 | `14/14 PASS` | `14/14 PASS` | `100% IDENTICAL` |

---

## 2. Q01 Detailed Collection Equivalence Verification

Both SQL and Cypher engines return:
- Leaf departments: `sub_departments: []` (empty array, not null, not objects with null properties).
- Empty departments: `active_employees: []` (empty array, not null).
- Fully populated departments: identical nested JSON objects with ordered keys `id`, `name`, `display_name`, `role_in_department`, `is_primary`, `effective_from`.
- Caller authorization denial: `0` rows on both engines.

## 3. Q08 Multi-Source Isolation Equivalence Verification

Both SQL and Cypher engines enforce identical tenant boundary rules:
- Cross-tenant custom audience (`Q08-06`, `Q08-07`, `Q08-08`): `0` rows on both engines.
- Multi-tenant ambiguous owner or members (`Q08-09`, `Q08-10`): `0` rows on both engines.
- System audience across tenants (`Q08-01`, `Q08-02`): creator tenant filtering strictly isolates notices.
