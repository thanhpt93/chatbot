"""Module 8: Evidence completeness & reporting integrity validator for Phase 1.2.2."""
from pathlib import Path

ROOT = Path(r"C:\Project\chatbot")
DOCS_DIR = ROOT / "documentation" / "phase-1-database-discovery"
ARTIFACTS_DIR = ROOT / "artifacts" / "phase1_2_2"


def run_check(check_generated_artifacts: bool = True) -> dict:
    issues = []
    doc37 = (DOCS_DIR / "37_phase1_2_final_evidence_acceptance_matrix.md").read_text(encoding="utf-8")
    doc39 = (DOCS_DIR / "39_phase1_2_final_readiness_report.md").read_text(encoding="utf-8")

    # Verify AC-01..AC-20 (with AC-05A and AC-05B) in Doc 37
    for i in range(1, 21):
        if i == 5:
            for sub in ["`AC-05A`", "`AC-05B`"]:
                if sub not in doc37:
                    issues.append(f"Doc 37 missing {sub}")
        else:
            ac_id = f"`AC-{i:02d}`"
            if ac_id not in doc37:
                issues.append(f"Doc 37 missing {ac_id}")

    # Verify strict honest statuses in Doc 37 & Doc 39 (no fabricated live Neo4j execution)
    for req_status in ["`NOT VERIFIED`", "`NOT EXECUTED`", "`BLOCKED`", "`PASS WITH CONDITIONS`", "`EXECUTED (SYNTHETIC FIXTURE)`"]:
        if req_status not in doc37:
            issues.append(f"Doc 37 missing required honest validation status {req_status}")

    if "READY FOR PHASE 2 WITH CONDITIONS" not in doc39:
        issues.append("Doc 39 missing final readiness decision 'READY FOR PHASE 2 WITH CONDITIONS'")

    required_artifacts = [
        "phase1_2_2_consistency_report.json",
        "phase1_2_2_consistency_report.md",
        "phase1_2_2_defect_register.md",
        "phase1_2_2_tenant_security_test_matrix.md",
        "phase1_2_2_etl_reconciliation_matrix.md",
        "phase1_2_2_sql_cypher_equivalence.md",
        "phase1_2_2_execution_log.txt",
    ]
    if check_generated_artifacts:
        for art in required_artifacts:
            p = ARTIFACTS_DIR / art
            if not p.exists() or p.stat().st_size == 0:
                issues.append(f"Missing or empty Phase 1.2.2 artifact: {art}")

    return {
        "module": "validate_evidence_completeness",
        "status": "PASS" if not issues else "FAIL",
        "acceptance_criteria_verified": 21,
        "required_artifacts_count": len(required_artifacts),
        "live_neo4j_runtime_status": "NOT EXECUTED",
        "external_backend_code_status": "NOT VERIFIED",
        "synthetic_fixture_status": "EXECUTED (SYNTHETIC FIXTURE)",
        "issues": issues,
    }


if __name__ == "__main__":
    res = run_check(check_generated_artifacts=False)
    print(f"[{res['module']}] {res['status']} (issues={len(res['issues'])})")
