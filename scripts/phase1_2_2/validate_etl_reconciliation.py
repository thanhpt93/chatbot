"""Module 6: ETL Reconciliation & Safe Hard-Delete validator (CRITICAL-06, Patterns R-1..R-7 across all 24 MVP nodes)."""
import json
from pathlib import Path
from validate_membership_lifecycle import build_sqlite_db

ROOT = Path(r"C:\Project\chatbot")
DOCS_DIR = ROOT / "documentation" / "phase-1-database-discovery"
FIXTURE_PATH = ROOT / "tests" / "phase1_2_2" / "fixtures" / "synthetic_multi_tenant_fixture.json"
EXPECTED_PATH = ROOT / "tests" / "phase1_2_2" / "expected" / "expected_test_results.json"


def run_check() -> dict:
    issues = []
    doc33 = (DOCS_DIR / "33_phase1_2_etl_synchronization_contract.md").read_text(encoding="utf-8")

    # Verify all 7 patterns R-1..R-7 and all 24 Approved MVP Node IDs in Section 2.6
    sec26_start = doc33.find("### 2.6 Behavior 6: Per-Node Hard Delete & Eligibility Reconciliation Contract")
    sec27_start = doc33.find("### 2.7 Behavior 7:")
    sec26 = doc33[sec26_start:sec27_start] if sec26_start != -1 and sec27_start != -1 else ""

    for pat in ["R-1", "R-2", "R-3", "R-4", "R-5", "R-6", "R-7"]:
        if pat not in sec26:
            issues.append(f"Doc 33 Section 2.6 missing reconciliation pattern {pat}")

    mvp_ids = [f"NM-{i:02d}" for i in range(1, 26) if i != 11]
    for nm in mvp_ids:
        if nm not in sec26:
            issues.append(f"Doc 33 Section 2.6 reconciliation matrix missing node {nm}")

    if "MAX_DELETE_RATIO" not in sec26 or "0.05" not in sec26:
        issues.append("Doc 33 Section 2.6 missing circuit breaker MAX_DELETE_RATIO (0.05 / 5%)")
    if "WHERE NOT (tg.tag_key IN $eligible_tag_keys)" not in sec26:
        issues.append("Doc 33 Section 2.6 missing synthetic key reconciliation WHERE NOT (tg.tag_key IN $eligible_tag_keys) for :Tag (NM-24)")

    # Execute synthetic Tag (NM-24) reconciliation key extraction on SQLite fixture
    fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    expected = json.loads(EXPECTED_PATH.read_text(encoding="utf-8"))
    conn = build_sqlite_db(fixture)
    cur = conn.cursor()
    tag_keys = [
        r[0]
        for r in cur.execute(
            """
            SELECT 'project:' || id AS tag_key FROM project_tags
            UNION ALL
            SELECT 'talk:' || id AS tag_key FROM talk_tags
            ORDER BY tag_key
            """
        ).fetchall()
    ]
    if tag_keys != expected["expected_tag_reconciliation_keys"]:
        issues.append(f"Synthetic Tag (NM-24) reconciliation keys mismatch: {tag_keys} != {expected['expected_tag_reconciliation_keys']}")

    # Simulate Neo4j Tag reconciliation: stale tag 'project:999' is purged while eligible_tag_keys are preserved
    simulated_neo4j_tags = ["project:1", "project:2", "talk:1", "project:999"]
    purged_tags = [k for k in simulated_neo4j_tags if k not in set(tag_keys)]
    if purged_tags != ["project:999"]:
        issues.append(f"Tag R-7 reconciliation simulation failed: purged={purged_tags}")

    conn.close()
    return {
        "module": "validate_etl_reconciliation",
        "status": "PASS" if not issues else "FAIL",
        "execution_level": "EXECUTED (SYNTHETIC FIXTURE)",
        "reconciliation_patterns_verified": ["R-1", "R-2", "R-3", "R-4", "R-5", "R-6", "R-7"],
        "mvp_nodes_covered": 24,
        "circuit_breaker": "MAX_DELETE_RATIO = 0.05 (5%)",
        "synthetic_tag_keys_verified": tag_keys,
        "issues": issues,
    }


if __name__ == "__main__":
    res = run_check()
    print(f"[{res['module']}] {res['status']} (issues={len(res['issues'])}) {res['issues']}")
