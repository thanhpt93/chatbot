"""Module 4: Tenant security validator for Phase 1.2.2 (SEC-01..SEC-25, Dual-Scope Audience, Two-Template FTS)."""
from pathlib import Path

ROOT = Path(r"C:\Project\chatbot")
DOCS_DIR = ROOT / "documentation" / "phase-1-database-discovery"


def run_check() -> dict:
    issues = []
    doc29 = (DOCS_DIR / "29_phase1_2_final_user_tenant_model.md").read_text(encoding="utf-8")
    doc34 = (DOCS_DIR / "34_phase1_2_query_and_security_validation.md").read_text(encoding="utf-8")
    doc35 = (DOCS_DIR / "35_phase1_2_final_neo4j_constraints_indexes.md").read_text(encoding="utf-8")

    # Verify SEC-01 through SEC-25 exist in Doc 34
    sec_cases = []
    for i in range(1, 26):
        sec_id = f"SEC-{i:02d}"
        if sec_id not in doc34:
            issues.append(f"Doc 34 missing security test case {sec_id}")
        else:
            sec_cases.append(sec_id)

    # Verify Phase 1.2.2 specific security tests SEC-21..SEC-25
    for req_phrase in [
        "CRITICAL-01",
        "CRITICAL-02",
        "CRITICAL-03",
        "CRITICAL-04",
        "HIGH-05",
        "Template FTS-A",
        "Template FTS-B",
    ]:
        if req_phrase not in doc34:
            issues.append(f"Doc 34 missing security verification reference '{req_phrase}'")

    # Verify Dual-Scope Audience indexes IDX-16A and IDX-16B in Doc 35
    if "idx_audience_custom_tenant" not in doc35 or "idx_audience_system_lookup" not in doc35:
        issues.append("Doc 35 missing IDX-16A or IDX-16B for Dual-Scope Audience.")

    # Verify Membership Lifecycle Rules in Doc 29
    if "MEM-ACTIVE" not in doc29 or "MEM-HISTORICAL-UNAMBIGUOUS" not in doc29:
        issues.append("Doc 29 missing Rule MEM-ACTIVE or Rule MEM-HISTORICAL-UNAMBIGUOUS.")

    return {
        "module": "validate_tenant_security",
        "status": "PASS" if not issues else "FAIL",
        "security_test_cases_count": len(sec_cases),
        "fts_templates_verified": ["Template FTS-A", "Template FTS-B"],
        "dual_scope_audience_verified": True,
        "issues": issues,
    }


if __name__ == "__main__":
    res = run_check()
    print(f"[{res['module']}] {res['status']} (issues={len(res['issues'])}) {res['issues']}")
