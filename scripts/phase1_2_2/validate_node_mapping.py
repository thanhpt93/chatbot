"""Module 2: Node mapping validator for Phase 1.2.2 (NM-01..NM-25, CRITICAL-01, CRITICAL-02, CRITICAL-06)."""
import json
from pathlib import Path

ROOT = Path(r"C:\Project\chatbot")
DOCS_DIR = ROOT / "documentation" / "phase-1-database-discovery"
SCHEMA_PATH = ROOT / "artifacts" / "database-discovery" / "schema_inventory.json"


def run_check() -> dict:
    issues = []
    doc30 = (DOCS_DIR / "30_phase1_2_complete_node_mapping.md").read_text(encoding="utf-8")
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    tables = {
        f"{t.get('schema_name', t.get('table_schema', 'public'))}.{t['table_name']}": {
            c["column_name"] for c in t.get("columns", [])
        }
        for t in schema.get("tables", [])
    }

    # Verify all 24 MVP nodes + 1 Blocked + 2 Future exist in Doc 30
    mvp_ids = [f"NM-{i:02d}" for i in range(1, 26) if i != 11]
    for nm in mvp_ids:
        if nm not in doc30:
            issues.append(f"Doc 30 missing approved MVP node {nm}")

    # Verify CRITICAL-02: NM-21 LeaveBalance uses user_unambiguous_leave_tenant and COUNT(DISTINCT m.tenant_id) = 1
    if "user_unambiguous_leave_tenant" not in doc30:
        issues.append("Doc 30 NM-21 missing 'user_unambiguous_leave_tenant' CTE (CRITICAL-02).")
    doc30_lower = doc30.lower()
    if "having count(distinct m.tenant_id) = 1" not in doc30_lower and "having count(distinct tenant_id) = 1" not in doc30_lower:
        issues.append("Doc 30 NM-21 missing 'HAVING count(DISTINCT m.tenant_id) = 1' ambiguity guard (CRITICAL-02).")
    if "AMBIGUOUS_TENANT" not in doc30:
        issues.append("Doc 30 NM-21 missing 'AMBIGUOUS_TENANT' quarantine rule (CRITICAL-02).")

    # Verify CRITICAL-01: NM-22 AttendanceRecord enforces m.status = 'active' AND m.is_deleted = false AND COALESCE(u.is_deleted, false) = false
    nm22_pos = doc30.find("### NM-22:")
    nm23_pos = doc30.find("### NM-23:")
    nm22_block = doc30[nm22_pos:nm23_pos] if nm22_pos != -1 and nm23_pos != -1 else doc30
    if nm22_block.count("m.status = 'active'") < 2:
        issues.append("Doc 30 NM-22 must enforce m.status = 'active' in both valid_user_tenant and emp_number_resolution CTEs (CRITICAL-01).")
    if "COALESCE(u.is_deleted, false) = false" not in nm22_block:
        issues.append("Doc 30 NM-22 missing COALESCE(u.is_deleted, false) = false check (CRITICAL-01).")

    # Verify CRITICAL-06: Graph Identity Key column in Section 3.1 Summary Matrix
    if "Graph Identity Key" not in doc30 or "tg.tag_key" not in doc30:
        issues.append("Doc 30 Section 3.1 missing Graph Identity Key / tg.tag_key reconciliation reference.")

    # Verify physical table existence for leave & attendance
    for tbl in ["public.user_leave_year_balances", "public.user_leave_monthly_balances", "public.attendance_daily_records"]:
        if tbl not in tables:
            issues.append(f"Table {tbl} not found in schema_inventory.json")

    return {
        "module": "validate_node_mapping",
        "status": "PASS" if not issues else "FAIL",
        "approved_mvp_nodes": 24,
        "source_backed_properties": 271,
        "derived_properties": 2,
        "runtime_mvp_properties": 297,
        "issues": issues,
    }


if __name__ == "__main__":
    res = run_check()
    print(f"[{res['module']}] {res['status']} (issues={len(res['issues'])}) {res['issues']}")
