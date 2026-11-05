"""Module 3: Relationship mapping validator for Phase 1.2.2 (RM-01..RM-45, HIGH-05, CRITICAL-01, CRITICAL-02)."""
from pathlib import Path

ROOT = Path(r"C:\Project\chatbot")
DOCS_DIR = ROOT / "documentation" / "phase-1-database-discovery"


def run_check() -> dict:
    issues = []
    doc31 = (DOCS_DIR / "31_phase1_2_complete_relationship_mapping.md").read_text(encoding="utf-8")
    doc38 = (DOCS_DIR / "38_phase1_2_master_graph_traceability_matrix.md").read_text(encoding="utf-8")

    # Verify all 42 MVP relationships + RM-19 Blocked + RM-44..45 Future
    for i in range(1, 46):
        rm_id = f"RM-{i:02d}"
        if rm_id not in doc31:
            issues.append(f"Doc 31 missing relationship {rm_id}")
        if rm_id not in doc38:
            issues.append(f"Doc 38 missing relationship {rm_id}")

    # Verify HIGH-05 on RM-04 [:MANAGES]
    rm04_start = doc31.find("### RM-04:")
    rm05_start = doc31.find("### RM-05:")
    rm04_block = doc31[rm04_start:rm05_start] if rm04_start != -1 and rm05_start != -1 else doc31
    for req_token in [
        "COALESCE(u.is_active, false) = true",
        "COALESCE(u.is_deleted, false) = false",
        "m.status = 'active'",
        "m.is_deleted = false",
        "MATCH (u)-[:MEMBER_OF {status: 'active', is_deleted: false}]->(:Tenant {id: d.tenant_id, is_deleted: false})",
    ]:
        if req_token not in rm04_block:
            issues.append(f"Doc 31 RM-04 missing required HIGH-05 token: {req_token}")

    # Verify CRITICAL-02 on RM-36 [:HAS_LEAVE_BALANCE]
    rm36_start = doc31.find("### RM-36:")
    rm37_start = doc31.find("### RM-37:")
    rm36_block = doc31[rm36_start:rm37_start] if rm36_start != -1 and rm37_start != -1 else doc31
    if "user_unambiguous_leave_tenant" not in rm36_block:
        issues.append("Doc 31 RM-36 missing user_unambiguous_leave_tenant CTE (CRITICAL-02).")

    # Verify CRITICAL-01 on RM-37 [:HAS_ATTENDANCE]
    rm38_start = doc31.find("### RM-38:")
    rm37_block = doc31[rm37_start:rm38_start] if rm37_start != -1 and rm38_start != -1 else doc31
    if rm37_block.count("m.status = 'active'") < 2:
        issues.append("Doc 31 RM-37 must enforce m.status = 'active' in both resolution CTEs and Cypher (CRITICAL-01).")

    return {
        "module": "validate_relationship_mapping",
        "status": "PASS" if not issues else "FAIL",
        "approved_mvp_relationships": 42,
        "relationship_properties": 108,
        "issues": issues,
    }


if __name__ == "__main__":
    res = run_check()
    print(f"[{res['module']}] {res['status']} (issues={len(res['issues'])}) {res['issues']}")
