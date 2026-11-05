# Phase 1.2.3.1 Q08 Multi-Source Security & Invariant Report
## Multi-Tenant Notice Isolation & Global Invariants Verification (WP2)

**Execution Date**: 2026-11-05  
**Total Tests**: 18  
**Passed**: 18  
**Failed**: 0  
**Legacy Vulnerability Demonstrated**: `True`  

---

## 1. Test Matrix Results (Q08-01 through Q08-18)

| Test ID | Scenario Description | Relational | Graph | Equivalence | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `Q08-01` | Valid Global Notice satisfies all 6 invariants and is visible to active T1 user | `PASS` | `PASS` | `Identical` | **`PASS`** |
| `Q08-02` | Valid Custom Notice with pure T1 audience is visible to active recipient caller (105) | `PASS` | `PASS` | `Identical` | **`PASS`** |
| `Q08-03` | Notice with Pure T2 Audience queried in T1 is denied (0 rows) | `PASS` | `PASS` | `Identical` | **`PASS`** |
| `Q08-04` | Cross-tenant leak prevention: Custom audience with T2 dept member is denied | `PASS` | `PASS` | `Identical` | **`PASS`** |
| `Q08-05` | Cross-tenant leak prevention: Custom audience with T2 user member is denied | `PASS` | `PASS` | `Identical` | **`PASS`** |
| `Q08-06` | Cross-tenant leak prevention: Custom audience with T2 owner is denied in T1 | `PASS` | `PASS` | `Identical` | **`PASS`** |
| `Q08-07` | Mixed audience containing both T1 and T2 members is denied | `PASS` | `PASS` | `Identical` | **`PASS`** |
| `Q08-08` | Custom audience with suspended owner is denied | `PASS` | `PASS` | `Identical` | **`PASS`** |
| `Q08-09` | Global Audience Invariant 4: System audience with owner_user_id set is denied | `PASS` | `PASS` | `Identical` | **`PASS`** |
| `Q08-10` | Global Audience Invariant 2: System audience with tenant_id NOT NULL is denied | `PASS` | `PASS` | `Identical` | **`PASS`** |
| `Q08-11` | Global Audience Invariant 5: System audience with department members is denied | `PASS` | `PASS` | `Identical` | **`PASS`** |
| `Q08-12` | Global Audience Invariant 6: System audience with direct user members is denied | `PASS` | `PASS` | `Identical` | **`PASS`** |
| `Q08-13` | Global Audience Invariant 3: System audience with audience_type != 'ALL' is denied | `PASS` | `PASS` | `Identical` | **`PASS`** |
| `Q08-14` | Custom audience targeting department 10 is visible to department member 101 | `PASS` | `PASS` | `Identical` | **`PASS`** |
| `Q08-15` | Custom audience containing soft-deleted user member is denied (quarantined) | `PASS` | `PASS` | `Identical` | **`PASS`** |
| `Q08-16` | Custom audience containing ambiguous multi-tenant user is denied (quarantined) | `PASS` | `PASS` | `Identical` | **`PASS`** |
| `Q08-17` | Notice created by user from Tenant 2 is excluded when querying Tenant 1 | `PASS` | `PASS` | `Identical` | **`PASS`** |
| `Q08-18` | Custom audience referencing non-existent department (999) is denied | `PASS` | `PASS` | `Identical` | **`PASS`** |

---

## 2. Invariants & Output Contract Verification
- **6 Global Audience Invariants**: Verified that global audience notices require `is_system = true`, `tenant_id IS NULL`, `audience_type = 'ALL'`, `owner_user_id IS NULL`, 0 department members, and 0 user members.
- **Independent Multi-Source Validation**: Verified that custom audiences independently validate owner tenant, all department member tenants, and all user member tenants without fallback masking.
- **Canonical 9-Field Output**: All queries output `notice_id`, `title`, `notice_type`, `priority`, `audience_name`, `audience_type`, `is_system_audience`, `author_name`, and `published_at` with `LIMIT 20`.
