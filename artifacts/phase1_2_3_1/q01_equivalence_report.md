# Phase 1.2.3.1 Q01 Independent Equivalence Report
## True Relational vs Graph Engine Equivalence Proof (WP1)

**Execution Date**: 2026-11-05  
**Total Tests**: 12  
**Passed**: 12  
**Failed**: 0  
**Payload Equivalence**: 100%  

---

## 1. Test Execution Results

| Test ID | Description | Relational Status | Graph Status | Payload Equivalence | Result |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `Q01-01` | Valid department query with sub-departments and active employees | `PASS` | `PASS` | `100% Identical` | **`PASS`** |
| `Q01-02` | Leaf department (0 sub-departments) returns empty array [] | `PASS` | `PASS` | `100% Identical` | **`PASS`** |
| `Q01-03` | Empty department (0 active employees) returns empty array [] | `PASS` | `PASS` | `100% Identical` | **`PASS`** |
| `Q01-04` | Department with inactive user manager has manager_id null | `PASS` | `PASS` | `100% Identical` | **`PASS`** |
| `Q01-05` | Department with manager having suspended tenant membership has manager_id null | `PASS` | `PASS` | `100% Identical` | **`PASS`** |
| `Q01-06` | Department with manager having deleted tenant membership has manager_id null | `PASS` | `PASS` | `100% Identical` | **`PASS`** |
| `Q01-07` | Department with cross-tenant manager has manager_id null | `PASS` | `PASS` | `100% Identical` | **`PASS`** |
| `Q01-08` | Requesting user with suspended membership is denied (0 rows) | `PASS` | `PASS` | `100% Identical` | **`PASS`** |
| `Q01-09` | Requesting user with deleted membership is denied (0 rows) | `PASS` | `PASS` | `100% Identical` | **`PASS`** |
| `Q01-10` | Cross-tenant requesting user is denied (0 rows) | `PASS` | `PASS` | `100% Identical` | **`PASS`** |
| `Q01-11` | Former employee with effective_to IS NOT NULL is excluded | `PASS` | `PASS` | `100% Identical` | **`PASS`** |
| `Q01-12` | Department member with suspended tenant membership is excluded | `PASS` | `PASS` | `100% Identical` | **`PASS`** |

---

## 2. Independence Verification
- **AST Call-Graph Proof (`IND-01`)**: Verified zero imports or references between `tests/phase1_2_3_1/relational/` and `tests/phase1_2_3_1/graph/`.
- **Intentional Rule Divergence (`IND-02`)**: Verified that modifying graph traversal rules immediately causes detectable payload divergence against SQL output, proving independent execution.
