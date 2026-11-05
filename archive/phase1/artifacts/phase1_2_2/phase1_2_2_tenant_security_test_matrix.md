# Phase 1.2.2 Multi-Tenant Security & Lifecycle Test Matrix (`SEC-01` – `SEC-25` & Attendance `Cases A–E`)
## Groupware AI Chatbot – PostgreSQL 18.6 + Neo4j + Vector Database

**Validation Level:** `STATICALLY VALIDATED` & `EXECUTED (SYNTHETIC FIXTURE)` (Live Neo4j Server Runtime: `NOT EXECUTED`)

## 1. Mandatory Attendance Lifecycle & Multi-Tenant Resolution Cases (`CRITICAL-01` — Cases A–E for `user_id` & `employee_number`)

| Case ID | Resolution Path | Fixture Record ID | Membership `status` | `is_deleted` | Expected Outcome | Observed Status | Loaded to Neo4j? | Verification Result |
|---|---|---|---|---|---|---|---|---|
| **Case A (`user_id`)** | `valid_user_tenant` | `1001` (`user_id=101`, `EMP-101`) | `'active'` | `false` | Accept (`RESOLVED_BY_USER_ID`) | `RESOLVED_BY_USER_ID` | `True` (`tenant_id=1`) | **`PASS`** |
| **Case B (`user_id`)** | `valid_user_tenant` | `1002` (`user_id=106`, `EMP-106`) | `'inactive'` | `false` | Reject (`INVALID_TENANT`) | `INVALID_TENANT` | `False` (Quarantined) | **`PASS`** |
| **Case C (`user_id`)** | `valid_user_tenant` | `1003` (`user_id=102`, `EMP-102`) | `'suspended'` | `false` | Reject (`INVALID_TENANT`) | `INVALID_TENANT` | `False` (Quarantined) | **`PASS`** |
| **Case D (`user_id`)** | `valid_user_tenant` | `1004` (`user_id=103`, `EMP-103`) | `'active'` | `true` | Reject (`INVALID_TENANT`) | `INVALID_TENANT` | `False` (Quarantined) | **`PASS`** |
| **Case E (`user_id`)** | `valid_user_tenant` | `1005` (`user_id=107`, `EMP-107`) | `'inactive'` | `true` | Reject (`INVALID_TENANT`) | `INVALID_TENANT` | `False` (Quarantined) | **`PASS`** |
| **Case A (`employee_number`)** | `emp_number_resolution` | `1006` (`user_id=NULL`, `EMP-105`) | `'active'` in T1 (`'suspended'` in T2) | `false` | Accept (`RESOLVED_BY_EMPLOYEE_NUMBER`) | `RESOLVED_BY_EMPLOYEE_NUMBER` | `True` (`tenant_id=1`, `user_id=105`) | **`PASS`** |
| **Case B (`employee_number`)** | `emp_number_resolution` | `1007` (`user_id=NULL`, `EMP-106`) | `'inactive'` | `false` | Reject (`UNRESOLVED`) | `UNRESOLVED` | `False` (Quarantined) | **`PASS`** |
| **Case C (`employee_number`)** | `emp_number_resolution` | `1008` (`user_id=NULL`, `EMP-102`) | `'suspended'` | `false` | Reject (`UNRESOLVED`) | `UNRESOLVED` | `False` (Quarantined) | **`PASS`** |
| **Case D (`employee_number`)** | `emp_number_resolution` | `1009` (`user_id=NULL`, `EMP-103`) | `'active'` | `true` | Reject (`UNRESOLVED`) | `UNRESOLVED` | `False` (Quarantined) | **`PASS`** |
| **Case E (`employee_number`)** | `emp_number_resolution` | `1010` (`user_id=NULL`, `EMP-107`) | `'inactive'` | `true` | Reject (`UNRESOLVED`) | `UNRESOLVED` | `False` (Quarantined) | **`PASS`** |
| **Multi-Tenant Active (`employee_number`)** | `emp_number_resolution` | `1011` (`user_id=NULL`, `EMP-104`) | `'active'` in T1 & T2 | `false` | Reject (`AMBIGUOUS`) | `AMBIGUOUS` | `False` (Quarantined) | **`PASS`** |

## 2. Mandatory LeaveBalance Multi-Tenant Resolution Cases (`CRITICAL-02`)

| Fixture Record ID | `user_id` | Scenario Description | Expected Outcome | Observed Outcome | Quarantine Reason | Verification Result |
|---|---|---|---|---|---|---|
| `501` | `101` | Active single-tenant user (`tenant_id = 1`) | Loaded (`tenant_id = 1`) | Loaded (`tenant_id = 1`) | `None` | **`PASS`** |
| `502` | `106` | Resigned single-tenant user (`tenant_id = 1`, `status = 'inactive'`) | Retained (`tenant_id = 1`) | Retained (`tenant_id = 1`) | `None` | **`PASS`** |
| `503` | `104` | Multi-tenant user active in `tenant_id = 1` and `tenant_id = 2` | Quarantined | Quarantined | `AMBIGUOUS_TENANT` | **`PASS`** |
| `504` | `105` | User with membership history in `tenant_id = 1` (active) and `tenant_id = 2` (suspended) | Quarantined | Quarantined | `AMBIGUOUS_TENANT` | **`PASS`** |

## 3. Mandatory Department Manager Lifecycle Cases (`HIGH-05` — All 6 Cases)

| Case | Fixture Dept ID | Manager `user.is_active` | Manager `user.is_deleted` | Membership `status` | Membership `is_deleted` | Expected `[:MANAGES]` / `Q01` Manager | Observed Result | Status |
|---|---|---|---|---|---|---|---|---|
| **Case 1** | `10` (`ENG-T1`, `mgr=101`) | `true` | `false` | `'active'` | `false` | `manager_id = 101` (`Alice Alpha`) | `manager_id = 101` | **`PASS`** |
| **Case 2** | `13` (`FIN-T1`, `mgr=106`) | `false` | `false` | `'inactive'` | `false` | `NULL` (Excluded) | `manager_id = NULL` | **`PASS`** |
| **Case 3** | `11` (`QA-T1`, `mgr=102`) | `true` | `false` | `'suspended'` | `false` | `NULL` (Excluded) | `manager_id = NULL` | **`PASS`** |
| **Case 4** | `14` (`HR-T1`, `mgr=108`) | `false` | `true` | `'active'` | `false` | `NULL` (Excluded) | `manager_id = NULL` | **`PASS`** |
| **Case 5** | `15` (`LEG-T1`, `mgr=103`) | `true` | `false` | `'active'` | `true` | `NULL` (Excluded) | `manager_id = NULL` | **`PASS`** |
| **Case 6** | `12` (`OPS-T1`, `mgr=202`) | `true` | `false` | `'active'` in Tenant 2 (`0` in Tenant 1) | `false` | `NULL` (Cross-tenant blocked) | `manager_id = NULL` | **`PASS`** |

## 4. Security Test Suite Summary (`SEC-01` – `SEC-25`)

- **`SEC-01`–`SEC-12`**: Domain cross-tenant isolation (`:Project`, `:Ticket`, `:ApprovalRequest`, `:ScheduleEvent`, `:FileMetadata`, `:ChatConversation`, `:LeaveBalance`, `:ContractHistory`, soft-delete, RBAC `check_user_permission`, domain FTS `Template FTS-A`) — **`STATICALLY VALIDATED` & `PASS`**.
- **`SEC-13`–`SEC-20`**: Global `:User` Fulltext Search (`fts_directory` `Template FTS-B`) positive and negative isolation tests — **`STATICALLY VALIDATED` & `PASS`**.
- **`SEC-21` (`CRITICAL-01`)**: Inactive/suspended/soft-deleted membership attendance quarantine (`Cases A–E`) — **`EXECUTED (SYNTHETIC FIXTURE)` & `PASS`**.
- **`SEC-22` (`CRITICAL-03`)**: `Q05` SQL & Cypher cross-tenant approval request isolation across Tenant A (`701`) and Tenant B (`702`) contexts for multi-tenant user `104`, single-tenant user `101`, and suspended user `102` (`0` rows) — **`EXECUTED (SYNTHETIC FIXTURE)` & `PASS`**.
- **`SEC-23` (`CRITICAL-04`)**: `Q08` SQL & Cypher cross-tenant notice & custom audience isolation (`Notice 901` global system audience in T1, `Notice 902` custom audience in T1, `Notice 903` in T2 blocked in T1, `Notice 904` with T2 custom audience blocked in T1, cross-tenant user `101` in T2 custom audience blocked, suspended user `102` blocked) — **`EXECUTED (SYNTHETIC FIXTURE)` & `PASS`**.
- **`SEC-24` (`HIGH-05`)**: `RM-04` & `Q01` inactive/suspended/deleted/cross-tenant department manager exclusion (`Depts 11, 12, 13, 14, 15` manager nulled) — **`EXECUTED (SYNTHETIC FIXTURE)` & `PASS`**.
- **`SEC-25` (`CRITICAL-02`)**: Multi-tenant `:LeaveBalance` ambiguity quarantine (`Records 503 & 504` -> `AMBIGUOUS_TENANT`) and single-tenant historical retention (`Record 502`) — **`EXECUTED (SYNTHETIC FIXTURE)` & `PASS`**.
