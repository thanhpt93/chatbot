# Phase 1.2.2 SQL-vs-Cypher Semantic Equivalence Report (`CRITICAL-03`, `CRITICAL-04`, `HIGH-05`)
## Groupware AI Chatbot – PostgreSQL 18.6 + Neo4j + Vector Database

**Validation Level:** `STATICALLY VALIDATED` & `EXECUTED (SYNTHETIC FIXTURE)` (In-memory SQLite relational execution vs Python Graph traversal simulation over [`synthetic_multi_tenant_fixture.json`](file:///C:/Project/chatbot/tests/phase1_2_2/fixtures/synthetic_multi_tenant_fixture.json))

## 1. Equivalence Summary Matrix

| Query Scenario | Defect Hardened | SQL vs Cypher Row Parity | Observed Rows (`tenant_id = 1` / `tenant_id = 2`) | Blocked Cross-Tenant / Invalid Rows | Status |
|---|---|---|---|---|---|
| **`Q01` (Department Hierarchy & Active Roster)** | `HIGH-05` & `DEFECT 06` | `True` (`6` rows in T1) | Dept `10` (`manager_id=101`, `active_member_count=2`), Depts `11, 12, 13, 14, 15` (`manager_id=NULL`, `active_member_count=0`) | Inactive manager (`106`), suspended manager (`102`), deleted user manager (`108`), deleted membership manager (`103`), cross-tenant manager (`202`), ended dept membership (`dm.id=3`), Tenant 2 Dept `20` | **`PASS`** |
| **`Q05` (Pending Approval Requests)** | `CRITICAL-03` & `DEFECT 03` | `True` (`1` row in T1 for `101` & `104`; `1` row in T2 for `104`; `0` rows for `102`) | T1 context (`101` & `104`): Request `701` (`APR-T1-01`); T2 context (`104`): Request `702` (`APR-T2-01`) | Tenant 2 Request `702` blocked in T1 context; Tenant 1 Request `701` blocked in T2 context; soft-deleted Request `703` (`APR-T1-DEL`) blocked; suspended user `102` returns `0` rows | **`PASS`** |
| **`Q08` (Published Notices & Dual-Scope Audience)** | `CRITICAL-04` & `DEFECT 04` | `True` (`2` rows in T1 for `101`; `1` row in T2 for `201`; `0` rows for `102`) | T1 (`user 101`): Notice `902` (`T1 Custom Eng Notice`) & Notice `901` (`T1 System All Notice`); T2 (`user 201`): Notice `903` (`T2 System All Notice`) | Tenant 2 System All Notice `903` blocked in T1; cross-tenant mismatched Audience Notice `904` blocked in T1; cross-tenant direct user (`101` in `AUD_T2_ENG`) blocked; suspended user `102` returns `0` rows | **`PASS`** |

## 2. Exact Verified Output Payloads (`EXECUTED (SYNTHETIC FIXTURE)`)

```json
{
  "Q01_Tenant1": [
    {
      "dept_id": 10,
      "dept_code": "ENG-T1",
      "dept_name": "Engineering Alpha (Case 1: Active Mgr + Active Mem)",
      "depth": 1,
      "parent_code": null,
      "manager_id": 101,
      "manager_name": "Alice Alpha",
      "active_member_count": 2
    },
    {
      "dept_id": 11,
      "dept_code": "QA-T1",
      "dept_name": "QA Alpha (Case 3: Suspended Mem Mgr)",
      "depth": 2,
      "parent_code": "ENG-T1",
      "manager_id": null,
      "manager_name": null,
      "active_member_count": 0
    },
    {
      "dept_id": 12,
      "dept_code": "OPS-T1",
      "dept_name": "Ops Alpha (Case 6: Cross-Tenant Mgr)",
      "depth": 2,
      "parent_code": "ENG-T1",
      "manager_id": null,
      "manager_name": null,
      "active_member_count": 0
    },
    {
      "dept_id": 13,
      "dept_code": "FIN-T1",
      "dept_name": "Finance Alpha (Case 2: Inactive User + Inactive Mem Mgr)",
      "depth": 2,
      "parent_code": "ENG-T1",
      "manager_id": null,
      "manager_name": null,
      "active_member_count": 0
    },
    {
      "dept_id": 14,
      "dept_code": "HR-T1",
      "dept_name": "HR Alpha (Case 4: Deleted User Mgr)",
      "depth": 2,
      "parent_code": "ENG-T1",
      "manager_id": null,
      "manager_name": null,
      "active_member_count": 0
    },
    {
      "dept_id": 15,
      "dept_code": "LEG-T1",
      "dept_name": "Legal Alpha (Case 5: Deleted Mem Mgr)",
      "depth": 2,
      "parent_code": "ENG-T1",
      "manager_id": null,
      "manager_name": null,
      "active_member_count": 0
    }
  ],
  "Q05_Tenant1_User101": [
    {
      "request_id": 701,
      "code": "APR-T1-01",
      "request_type": "leave",
      "title": "T1 Leave Request",
      "status": "IN_PROGRESS",
      "requester_name": "Eve T1 Active",
      "participant_role": "approver",
      "sequence_order": 1,
      "action_status": "PENDING",
      "submitted_at": "2026-10-02T09:00:00Z"
    }
  ],
  "Q05_Tenant1_MultiTenantUser104": [
    {
      "request_id": 701,
      "code": "APR-T1-01",
      "request_type": "leave",
      "title": "T1 Leave Request",
      "status": "IN_PROGRESS",
      "requester_name": "Eve T1 Active",
      "participant_role": "approver",
      "sequence_order": 2,
      "action_status": "PENDING",
      "submitted_at": "2026-10-02T09:00:00Z"
    }
  ],
  "Q05_Tenant2_MultiTenantUser104": [
    {
      "request_id": 702,
      "code": "APR-T2-01",
      "request_type": "leave",
      "title": "T2 Leave Request",
      "status": "IN_PROGRESS",
      "requester_name": "Grace Beta",
      "participant_role": "approver",
      "sequence_order": 3,
      "action_status": "PENDING",
      "submitted_at": "2026-10-02T10:00:00Z"
    }
  ],
  "Q08_Tenant1_User101": [
    {
      "notice_id": 902,
      "title": "T1 Custom Eng Notice",
      "notice_type": "dept",
      "priority": "normal",
      "audience_name": "T1 Engineering Custom",
      "audience_type": "CUSTOM",
      "published_at": "2026-10-03T09:00:00Z"
    },
    {
      "notice_id": 901,
      "title": "T1 System All Notice",
      "notice_type": "general",
      "priority": "high",
      "audience_name": "All Company",
      "audience_type": "ALL",
      "published_at": "2026-10-03T08:00:00Z"
    }
  ],
  "Q08_Tenant2_User201": [
    {
      "notice_id": 903,
      "title": "T2 System All Notice (Must NOT leak to T1)",
      "notice_type": "general",
      "priority": "high",
      "audience_name": "All Company",
      "audience_type": "ALL",
      "published_at": "2026-10-03T10:00:00Z"
    }
  ]
}
```
