"""Module 5: Membership lifecycle validator (executes synthetic SQLite fixture for Attendance Cases A-E, LeaveBalance CRITICAL-02, and Manager RM-04 HIGH-05)."""
import json
import sqlite3
from pathlib import Path

ROOT = Path(r"C:\Project\chatbot")
FIXTURE_PATH = ROOT / "tests" / "phase1_2_2" / "fixtures" / "synthetic_multi_tenant_fixture.json"
EXPECTED_PATH = ROOT / "tests" / "phase1_2_2" / "expected" / "expected_test_results.json"


def build_sqlite_db(fixture: dict) -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.executescript(
        """
        CREATE TABLE tenants (id INTEGER PRIMARY KEY, tenant_key TEXT, name TEXT, status TEXT, isolation_mode TEXT, is_default INTEGER, is_deleted INTEGER);
        CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, email TEXT, is_active INTEGER, is_deleted INTEGER);
        CREATE TABLE tenant_user_memberships (id INTEGER PRIMARY KEY, tenant_id INTEGER, user_id INTEGER, status TEXT, is_default INTEGER, is_deleted INTEGER);
        CREATE TABLE user_profiles (id INTEGER PRIMARY KEY, tenant_id INTEGER, user_id INTEGER, display_name TEXT, employee_number TEXT, department_id INTEGER, is_default INTEGER, is_resigned INTEGER);
        CREATE TABLE departments (id INTEGER PRIMARY KEY, tenant_id INTEGER, code TEXT, name TEXT, parent_id INTEGER, manager_user_id INTEGER, depth INTEGER, path TEXT, department_type TEXT, is_active INTEGER);
        CREATE TABLE department_members (id INTEGER PRIMARY KEY, tenant_id INTEGER, department_id INTEGER, user_id INTEGER, role_in_department TEXT, is_primary INTEGER, effective_from TEXT, effective_to TEXT);
        CREATE TABLE attendance_daily_records (id INTEGER PRIMARY KEY, user_id INTEGER, employee_code TEXT, work_date TEXT, status TEXT, is_late INTEGER, is_early_leave INTEGER, actual_minutes INTEGER, case_id TEXT);
        CREATE TABLE user_leave_year_balances (id INTEGER PRIMARY KEY, user_id INTEGER, year INTEGER, opening_days REAL, carryover_days REAL, seniority_days REAL, manual_adjustment_days REAL, remaining_days REAL, carryover_available_days REAL, case_id TEXT);
        CREATE TABLE user_leave_monthly_balances (id INTEGER PRIMARY KEY, user_id INTEGER, year INTEGER, month INTEGER, accrued_days REAL, used_days REAL);
        CREATE TABLE approval_requests (id INTEGER PRIMARY KEY, code TEXT, request_type TEXT, status TEXT, title TEXT, created_by_user_id INTEGER, submitted_at TEXT, is_deleted INTEGER);
        CREATE TABLE approval_participants (id INTEGER PRIMARY KEY, request_id INTEGER, user_id INTEGER, participant_role TEXT, sequence_order INTEGER, action_status TEXT);
        CREATE TABLE audiences (id INTEGER PRIMARY KEY, code TEXT, name TEXT, audience_type TEXT, is_system INTEGER, owner_user_id INTEGER, is_active INTEGER);
        CREATE TABLE audience_department_members (id INTEGER PRIMARY KEY, audience_id INTEGER, department_id INTEGER);
        CREATE TABLE audience_user_members (id INTEGER PRIMARY KEY, audience_id INTEGER, user_id INTEGER);
        CREATE TABLE notices (id INTEGER PRIMARY KEY, title TEXT, notice_type TEXT, priority TEXT, audience_id INTEGER, created_by_user_id INTEGER, is_published INTEGER, published_at TEXT, is_deleted INTEGER);
        CREATE TABLE project_tags (id INTEGER PRIMARY KEY, project_id INTEGER, name TEXT, color TEXT);
        CREATE TABLE talk_tags (id INTEGER PRIMARY KEY, name TEXT, color TEXT);
        """
    )
    for t in fixture["tenants"]:
        cur.execute("INSERT INTO tenants VALUES (?,?,?,?,?,?,?)", (t["id"], t["tenant_key"], t["name"], t["status"], t["isolation_mode"], int(t["is_default"]), int(t["is_deleted"])))
    for u in fixture["users"]:
        cur.execute("INSERT INTO users VALUES (?,?,?,?,?)", (u["id"], u["username"], u["email"], int(u["is_active"]), int(u["is_deleted"])))
    for m in fixture["tenant_user_memberships"]:
        cur.execute("INSERT INTO tenant_user_memberships VALUES (?,?,?,?,?,?)", (m["id"], m["tenant_id"], m["user_id"], m["status"], int(m["is_default"]), int(m["is_deleted"])))
    for up in fixture["user_profiles"]:
        cur.execute("INSERT INTO user_profiles VALUES (?,?,?,?,?,?,?,?)", (up["id"], up["tenant_id"], up["user_id"], up["display_name"], up["employee_number"], up["department_id"], int(up["is_default"]), int(up["is_resigned"])))
    for d in fixture["departments"]:
        cur.execute("INSERT INTO departments VALUES (?,?,?,?,?,?,?,?,?,?)", (d["id"], d["tenant_id"], d["code"], d["name"], d["parent_id"], d["manager_user_id"], d["depth"], d["path"], d["department_type"], int(d["is_active"])))
    for dm in fixture["department_members"]:
        cur.execute("INSERT INTO department_members VALUES (?,?,?,?,?,?,?,?)", (dm["id"], dm["tenant_id"], dm["department_id"], dm["user_id"], dm["role_in_department"], int(dm["is_primary"]), dm["effective_from"], dm["effective_to"]))
    for a in fixture["attendance_daily_records"]:
        cur.execute("INSERT INTO attendance_daily_records VALUES (?,?,?,?,?,?,?,?,?)", (a["id"], a["user_id"], a["employee_code"], a["work_date"], a["status"], int(a["is_late"]), int(a["is_early_leave"]), a["actual_minutes"], a["case_id"]))
    for yb in fixture["user_leave_year_balances"]:
        cur.execute("INSERT INTO user_leave_year_balances VALUES (?,?,?,?,?,?,?,?,?,?)", (yb["id"], yb["user_id"], yb["year"], yb["opening_days"], yb["carryover_days"], yb["seniority_days"], yb["manual_adjustment_days"], yb["remaining_days"], yb["carryover_available_days"], yb["case_id"]))
    for mb in fixture["user_leave_monthly_balances"]:
        cur.execute("INSERT INTO user_leave_monthly_balances VALUES (?,?,?,?,?,?)", (mb["id"], mb["user_id"], mb["year"], mb["month"], mb["accrued_days"], mb["used_days"]))
    for ar in fixture["approval_requests"]:
        cur.execute("INSERT INTO approval_requests VALUES (?,?,?,?,?,?,?,?)", (ar["id"], ar["code"], ar["request_type"], ar["status"], ar["title"], ar["created_by_user_id"], ar["submitted_at"], int(ar["is_deleted"])))
    for ap in fixture["approval_participants"]:
        cur.execute("INSERT INTO approval_participants VALUES (?,?,?,?,?,?)", (ap["id"], ap["request_id"], ap["user_id"], ap["participant_role"], ap["sequence_order"], ap["action_status"]))
    for au in fixture["audiences"]:
        cur.execute("INSERT INTO audiences VALUES (?,?,?,?,?,?,?)", (au["id"], au["code"], au["name"], au["audience_type"], int(au["is_system"]), au["owner_user_id"], int(au["is_active"])))
    for adm in fixture["audience_department_members"]:
        cur.execute("INSERT INTO audience_department_members VALUES (?,?,?)", (adm["id"], adm["audience_id"], adm["department_id"]))
    for aum in fixture["audience_user_members"]:
        cur.execute("INSERT INTO audience_user_members VALUES (?,?,?)", (aum["id"], aum["audience_id"], aum["user_id"]))
    for nt in fixture["notices"]:
        cur.execute("INSERT INTO notices VALUES (?,?,?,?,?,?,?,?,?)", (nt["id"], nt["title"], nt["notice_type"], nt["priority"], nt["audience_id"], nt["created_by_user_id"], int(nt["is_published"]), nt["published_at"], int(nt["is_deleted"])))
    for pt in fixture["project_tags"]:
        cur.execute("INSERT INTO project_tags VALUES (?,?,?,?)", (pt["id"], pt["project_id"], pt["name"], pt["color"]))
    for tt in fixture["talk_tags"]:
        cur.execute("INSERT INTO talk_tags VALUES (?,?,?)", (tt["id"], tt["name"], tt["color"]))
    conn.commit()
    return conn


def run_check() -> dict:
    issues = []
    fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    expected = json.loads(EXPECTED_PATH.read_text(encoding="utf-8"))
    conn = build_sqlite_db(fixture)
    cur = conn.cursor()

    # 1. Execute CRITICAL-01 6-Step Attendance Resolution SQL across Cases A-E (for both user_id and employee_number)
    attendance_sql = """
    WITH valid_user_tenant AS (
        SELECT
            up.user_id,
            MIN(up.tenant_id) AS tenant_id,
            COUNT(DISTINCT up.tenant_id) AS tenant_cnt
        FROM user_profiles up
        JOIN tenant_user_memberships m
          ON m.user_id = up.user_id
         AND m.tenant_id = up.tenant_id
         AND m.status = 'active'
         AND m.is_deleted = 0
        JOIN users u
          ON u.id = up.user_id
         AND COALESCE(u.is_deleted, 0) = 0
        GROUP BY up.user_id
    ),
    emp_number_resolution AS (
        SELECT
            up.employee_number,
            MIN(up.user_id) AS resolved_user_id,
            MIN(up.tenant_id) AS resolved_tenant_id,
            COUNT(DISTINCT up.user_id) AS user_cnt,
            COUNT(DISTINCT up.tenant_id) AS tenant_cnt
        FROM user_profiles up
        JOIN tenant_user_memberships m
          ON m.user_id = up.user_id
         AND m.tenant_id = up.tenant_id
         AND m.status = 'active'
         AND m.is_deleted = 0
        JOIN users u
          ON u.id = up.user_id
         AND COALESCE(u.is_deleted, 0) = 0
        WHERE up.employee_number IS NOT NULL
          AND TRIM(up.employee_number) <> ''
        GROUP BY up.employee_number
    )
    SELECT
        a.id,
        a.case_id,
        CASE
            WHEN a.user_id IS NOT NULL AND vut.user_id IS NOT NULL AND vut.tenant_cnt = 1 THEN vut.tenant_id
            WHEN a.user_id IS NULL AND enr.user_cnt = 1 AND enr.tenant_cnt = 1 THEN enr.resolved_tenant_id
            ELSE NULL
        END AS tenant_id,
        CASE
            WHEN a.user_id IS NOT NULL AND vut.user_id IS NOT NULL AND vut.tenant_cnt = 1 THEN a.user_id
            WHEN a.user_id IS NULL AND enr.user_cnt = 1 AND enr.tenant_cnt = 1 THEN enr.resolved_user_id
            ELSE NULL
        END AS resolved_user_id,
        CASE
            WHEN a.user_id IS NOT NULL AND vut.user_id IS NOT NULL AND vut.tenant_cnt = 1 THEN 'RESOLVED_BY_USER_ID'
            WHEN a.user_id IS NOT NULL AND (u_raw.id IS NULL OR COALESCE(u_raw.is_deleted, 0) = 1) THEN 'INVALID_SOURCE_REFERENCE'
            WHEN a.user_id IS NOT NULL AND (vut.user_id IS NULL OR vut.tenant_cnt <> 1) THEN 'INVALID_TENANT'
            WHEN a.user_id IS NULL AND enr.user_cnt = 1 AND enr.tenant_cnt = 1 THEN 'RESOLVED_BY_EMPLOYEE_NUMBER'
            WHEN a.user_id IS NULL AND (enr.user_cnt > 1 OR enr.tenant_cnt > 1) THEN 'AMBIGUOUS'
            ELSE 'UNRESOLVED'
        END AS resolution_status
    FROM attendance_daily_records a
    LEFT JOIN users u_raw ON u_raw.id = a.user_id
    LEFT JOIN valid_user_tenant vut ON vut.user_id = a.user_id
    LEFT JOIN emp_number_resolution enr ON enr.employee_number = a.employee_code
    ORDER BY a.id;
    """
    att_rows = [dict(r) for r in cur.execute(attendance_sql).fetchall()]
    for r in att_rows:
        exp = expected["expected_attendance_resolution"][str(r["id"])]
        loaded = r["resolution_status"] in ("RESOLVED_BY_USER_ID", "RESOLVED_BY_EMPLOYEE_NUMBER")
        if r["resolution_status"] != exp["status"] or loaded != exp["loaded_to_neo4j"] or r["tenant_id"] != exp["tenant_id"]:
            issues.append(f"Attendance Case mismatch on id={r['id']}: got {r}, expected {exp}")

    # 2. Execute CRITICAL-02 LeaveBalance Resolution SQL
    leave_sql = """
    WITH user_unambiguous_leave_tenant AS (
        SELECT
            m.user_id,
            MIN(m.tenant_id) AS tenant_id
        FROM tenant_user_memberships m
        JOIN users u
          ON u.id = m.user_id
         AND COALESCE(u.is_deleted, 0) = 0
        JOIN user_profiles up
          ON up.user_id = m.user_id
         AND up.tenant_id = m.tenant_id
        WHERE m.is_deleted = 0
          AND m.status IN ('active', 'inactive', 'suspended')
        GROUP BY m.user_id
        HAVING COUNT(DISTINCT m.tenant_id) = 1
    )
    SELECT
        yb.id,
        yb.user_id,
        yb.case_id,
        ut.tenant_id,
        CASE WHEN ut.tenant_id IS NOT NULL THEN 1 ELSE 0 END AS loaded_to_neo4j,
        CASE WHEN ut.tenant_id IS NULL THEN 'AMBIGUOUS_TENANT' ELSE NULL END AS quarantine_reason
    FROM user_leave_year_balances yb
    LEFT JOIN user_unambiguous_leave_tenant ut ON ut.user_id = yb.user_id
    ORDER BY yb.id;
    """
    leave_rows = [dict(r) for r in cur.execute(leave_sql).fetchall()]
    for r in leave_rows:
        exp = expected["expected_leave_balance_resolution"][str(r["id"])]
        if bool(r["loaded_to_neo4j"]) != exp["loaded_to_neo4j"] or r["tenant_id"] != exp["tenant_id"] or r["quarantine_reason"] != exp["quarantine_reason"]:
            issues.append(f"LeaveBalance Case mismatch on id={r['id']}: got {r}, expected {exp}")

    # 3. Execute HIGH-05 RM-04 Department Manager Active Lifecycle SQL across all 6 manager cases
    mgr_sql = """
    SELECT
        d.id AS dept_id,
        mgr.id AS manager_id,
        up.display_name AS manager_name
    FROM departments d
    LEFT JOIN (
        SELECT u.id, m.tenant_id
        FROM users u
        JOIN tenant_user_memberships m
          ON m.user_id = u.id
         AND m.status = 'active'
         AND m.is_deleted = 0
        WHERE u.is_active = 1
          AND u.is_deleted = 0
    ) mgr
      ON mgr.id = d.manager_user_id
     AND mgr.tenant_id = d.tenant_id
    LEFT JOIN user_profiles up
      ON up.user_id = mgr.id
     AND up.tenant_id = d.tenant_id
    WHERE d.tenant_id = 1
    ORDER BY d.id;
    """
    mgr_rows = [dict(r) for r in cur.execute(mgr_sql).fetchall()]
    for r in mgr_rows:
        exp = expected["expected_department_managers_t1"][str(r["dept_id"])]
        if r["manager_id"] != exp["manager_id"] or r["manager_name"] != exp["manager_name"]:
            issues.append(f"Department Manager RM-04 mismatch on dept_id={r['dept_id']}: got {r}, expected {exp}")

    conn.close()
    return {
        "module": "validate_membership_lifecycle",
        "status": "PASS" if not issues else "FAIL",
        "execution_level": "EXECUTED (SYNTHETIC FIXTURE)",
        "attendance_cases_verified": att_rows,
        "leave_balance_cases_verified": leave_rows,
        "department_manager_cases_verified": mgr_rows,
        "issues": issues,
    }


if __name__ == "__main__":
    res = run_check()
    print(f"[{res['module']}] {res['status']} (issues={len(res['issues'])}) {res['issues']}")
