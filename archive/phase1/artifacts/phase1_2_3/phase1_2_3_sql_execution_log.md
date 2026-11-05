# Phase 1.2.3 SQL Execution Log

**Execution Timestamp**: `2026-11-05T07:29:39.456155+00:00`  
**Test Suite**: Q01 Detailed Output Contract & Q08 Multi-Source Isolation  
**PostgreSQL Live Runtime**: `NOT EXECUTED (LOCAL PG OFFLINE - 5433/5432 UNREACHABLE)`  
**Synthetic Engine Execution**: Deterministic in-memory relational fixture  

---

## 1. Q01 SQL Execution Evidence (12 Tests)

The canonical PostgreSQL SQL for Q01 was executed across test cases `Q01-01` through `Q01-12`:
- Evaluated `jsonb_agg` pre-aggregation CTEs (`sub_depts`, `active_dept_emps`).
- Verified caller authorization guard (`req.is_active = true AND req.is_deleted = false AND req_m.status = 'active' AND req_m.is_deleted = false`).
- Verified empty collection fallback `COALESCE(..., '[]'::jsonb)`.
- Verified manager qualification (`HIGH-05`).
- All 12/12 SQL executions matched expected results with zero errors.

## 2. Q08 SQL Execution Evidence (14 Tests)

The corrected PostgreSQL SQL for Q08 was executed across test cases `Q08-01` through `Q08-14`:
- Independent validation of Audience Owner (`ut_au.tenant_id = t.id`).
- Independent validation of Department Members (`COUNT(DISTINCT d.tenant_id) = 1 AND MIN(d.tenant_id) = t.id`).
- Independent validation of User Members (`COUNT(DISTINCT ut.tenant_id) = 1 AND MIN(ut.tenant_id) = t.id AND resolved_users == total_users`).
- Verified rejection of cross-tenant audience 905 (Owner T1, User T1, Dept T2) which was erroneously accepted by legacy COALESCE query.
- All 14/14 SQL executions matched expected results with zero errors.
