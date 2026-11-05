"""
Validator Module for Scenario Q08 (WP2 & WP5).
Runs test cases Q08-01 through Q08-18 across independent Relational and Graph executors.
Enforces 100% exact JSON payload equivalence using strict ResultNormalizer.
Includes vulnerability reproduction demonstrating that legacy COALESCE allows cross-tenant leakage.
"""

import sys
from pathlib import Path

# Ensure project root is in sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from typing import Dict, Any, List
from tests.phase1_2_3_1.relational.q08_relational_executor import Q08RelationalExecutor
from tests.phase1_2_3_1.graph.q08_graph_executor import Q08GraphExecutor
from tests.phase1_2_3_1.common.result_normalizer import ResultNormalizer
from tests.phase1_2_3_1.common.fixture_loader import FixtureLoader


class Q08IndependentValidator:
    def __init__(self):
        self.fixture = FixtureLoader.load_fixture()
        self.rel_exec = Q08RelationalExecutor(self.fixture)
        self.graph_exec = Q08GraphExecutor(self.fixture)

    def execute_legacy_vulnerable_sql(
        self,
        tenant_id: int,
        requesting_user_id: int,
        notice_id: int
    ) -> List[Dict[str, Any]]:
        """
        Demonstrates the legacy COALESCE vulnerability where cross-tenant departments
        or users were masked by the owner tenant.
        """
        nt = next((n for n in self.fixture["notices"] if n["id"] == notice_id), None)
        if not nt:
            return []
        au = next((a for a in self.fixture["audiences"] if a["id"] == nt["audience_id"]), None)
        if not au:
            return []

        # Legacy flaw: evaluated audience tenant as COALESCE(au.tenant_id, owner_tenant)
        # without verifying department and user member tenant boundaries
        owner_t = None
        for m in self.fixture["tenant_user_memberships"]:
            if m["user_id"] == au.get("owner_user_id") and m["status"] == "active" and not m["is_deleted"]:
                owner_t = m["tenant_id"]
                break

        effective_tenant = au.get("tenant_id") or owner_t
        if effective_tenant == tenant_id:
            return [{
                "notice_id": nt["id"],
                "title": nt["title"],
                "notice_type": nt["notice_type"],
                "priority": nt["priority"],
                "audience_name": au["name"],
                "audience_type": au["audience_type"],
                "is_system_audience": au.get("is_system", False),
                "author_name": "Alice Alpha",
                "published_at": nt["published_at"]
            }]
        return []

    def run_all_checks(self) -> Dict[str, Any]:
        results = []
        all_passed = True

        test_cases = [
            # Q08-01: Valid Global Notice
            {
                "id": "Q08-01",
                "desc": "Valid Global Notice satisfies all 6 invariants and is visible to active T1 user",
                "params": {"tenant_id": 1, "requesting_user_id": 101, "notice_id": 901},
                "validator": lambda res: len(res) == 1 and res[0]["notice_id"] == 901 and res[0]["is_system_audience"] is True
            },
            # Q08-02: Valid Custom Notice
            {
                "id": "Q08-02",
                "desc": "Valid Custom Notice with pure T1 audience is visible to active recipient caller (105)",
                "params": {"tenant_id": 1, "requesting_user_id": 105, "notice_id": 902},
                "validator": lambda res: len(res) == 1 and res[0]["notice_id"] == 902 and res[0]["is_system_audience"] is False
            },
            # Q08-03: Notice with T2 Audience (Deny in T1)
            {
                "id": "Q08-03",
                "desc": "Notice with Pure T2 Audience queried in T1 is denied (0 rows)",
                "params": {"tenant_id": 1, "requesting_user_id": 101, "notice_id": 903},
                "validator": lambda res: len(res) == 0
            },
            # Q08-04: Vulnerability - Owner T1, User T1, Dept T2
            {
                "id": "Q08-04",
                "desc": "Cross-tenant leak prevention: Custom audience with T2 dept member is denied",
                "params": {"tenant_id": 1, "requesting_user_id": 105, "notice_id": 904},
                "validator": lambda res: len(res) == 0
            },
            # Q08-05: Vulnerability - Owner T1, User T2, Dept T1
            {
                "id": "Q08-05",
                "desc": "Cross-tenant leak prevention: Custom audience with T2 user member is denied",
                "params": {"tenant_id": 1, "requesting_user_id": 101, "notice_id": 905},
                "validator": lambda res: len(res) == 0
            },
            # Q08-06: Vulnerability - Owner T2, User T1, Dept T1
            {
                "id": "Q08-06",
                "desc": "Cross-tenant leak prevention: Custom audience with T2 owner is denied in T1",
                "params": {"tenant_id": 1, "requesting_user_id": 105, "notice_id": 906},
                "validator": lambda res: len(res) == 0
            },
            # Q08-07: Mixed Memberships T1 & T2
            {
                "id": "Q08-07",
                "desc": "Mixed audience containing both T1 and T2 members is denied",
                "params": {"tenant_id": 1, "requesting_user_id": 105, "notice_id": 907},
                "validator": lambda res: len(res) == 0
            },
            # Q08-08: Missing Valid Owner (Suspended)
            {
                "id": "Q08-08",
                "desc": "Custom audience with suspended owner is denied",
                "params": {"tenant_id": 1, "requesting_user_id": 101, "notice_id": 908},
                "validator": lambda res: len(res) == 0
            },
            # Q08-09: Global Invariant 4 Violated (Global with Owner)
            {
                "id": "Q08-09",
                "desc": "Global Audience Invariant 4: System audience with owner_user_id set is denied",
                "params": {"tenant_id": 1, "requesting_user_id": 101, "notice_id": 909},
                "validator": lambda res: len(res) == 0
            },
            # Q08-10: Global Invariant 2 Violated (Global with Tenant not null)
            {
                "id": "Q08-10",
                "desc": "Global Audience Invariant 2: System audience with tenant_id NOT NULL is denied",
                "params": {"tenant_id": 1, "requesting_user_id": 101, "notice_id": 910},
                "validator": lambda res: len(res) == 0
            },
            # Q08-11: Global Invariant 5 Violated (Global with Dept Members)
            {
                "id": "Q08-11",
                "desc": "Global Audience Invariant 5: System audience with department members is denied",
                "params": {"tenant_id": 1, "requesting_user_id": 101, "notice_id": 911},
                "validator": lambda res: len(res) == 0
            },
            # Q08-12: Global Invariant 6 Violated (Global with User Members)
            {
                "id": "Q08-12",
                "desc": "Global Audience Invariant 6: System audience with direct user members is denied",
                "params": {"tenant_id": 1, "requesting_user_id": 101, "notice_id": 912},
                "validator": lambda res: len(res) == 0
            },
            # Q08-13: Global Invariant 3 Violated (Global Type != ALL)
            {
                "id": "Q08-13",
                "desc": "Global Audience Invariant 3: System audience with audience_type != 'ALL' is denied",
                "params": {"tenant_id": 1, "requesting_user_id": 101, "notice_id": 913},
                "validator": lambda res: len(res) == 0
            },
            # Q08-14: Custom Audience with Valid Dept Member
            {
                "id": "Q08-14",
                "desc": "Custom audience targeting department 10 is visible to department member 101",
                "params": {"tenant_id": 1, "requesting_user_id": 101, "notice_id": 914},
                "validator": lambda res: len(res) == 1 and res[0]["notice_id"] == 914
            },
            # Q08-15: Custom Audience with Deleted User Member
            {
                "id": "Q08-15",
                "desc": "Custom audience containing soft-deleted user member is denied (quarantined)",
                "params": {"tenant_id": 1, "requesting_user_id": 101, "notice_id": 915},
                "validator": lambda res: len(res) == 0
            },
            # Q08-16: Custom Audience with Multi-Tenant Ambiguous User
            {
                "id": "Q08-16",
                "desc": "Custom audience containing ambiguous multi-tenant user is denied (quarantined)",
                "params": {"tenant_id": 1, "requesting_user_id": 101, "notice_id": 916},
                "validator": lambda res: len(res) == 0
            },
            # Q08-17: Cross-Tenant Notice Creator
            {
                "id": "Q08-17",
                "desc": "Notice created by user from Tenant 2 is excluded when querying Tenant 1",
                "params": {"tenant_id": 1, "requesting_user_id": 101, "notice_id": 917},
                "validator": lambda res: len(res) == 0
            },
            # Q08-18: Custom Audience with Invalid Department Reference
            {
                "id": "Q08-18",
                "desc": "Custom audience referencing non-existent department (999) is denied",
                "params": {"tenant_id": 1, "requesting_user_id": 101, "notice_id": 918},
                "validator": lambda res: len(res) == 0
            }
        ]

        # Vulnerability demonstration check
        vuln_res_904 = self.execute_legacy_vulnerable_sql(tenant_id=1, requesting_user_id=105, notice_id=904)
        vuln_res_905 = self.execute_legacy_vulnerable_sql(tenant_id=1, requesting_user_id=101, notice_id=905)
        vuln_demonstrated = (len(vuln_res_904) > 0 or len(vuln_res_905) > 0)

        for tc in test_cases:
            p = tc["params"]
            raw_rel = self.rel_exec.execute_relational_q08(
                tenant_id=p["tenant_id"],
                requesting_user_id=p["requesting_user_id"],
                notice_id=p["notice_id"]
            )
            raw_graph = self.graph_exec.execute_graph_q08(
                tenant_id=p["tenant_id"],
                requesting_user_id=p["requesting_user_id"],
                notice_id=p["notice_id"]
            )

            norm_rel = ResultNormalizer.normalize_q08_payload(raw_rel)
            norm_graph = ResultNormalizer.normalize_q08_payload(raw_graph)

            rel_ok = tc["validator"](norm_rel)
            graph_ok = tc["validator"](norm_graph)
            equivalent, diff_msg = ResultNormalizer.compare_payloads(norm_rel, norm_graph)

            passed = (rel_ok and graph_ok and equivalent)
            if not passed:
                all_passed = False

            results.append({
                "test_id": tc["id"],
                "description": tc["desc"],
                "passed": passed,
                "rel_passed": rel_ok,
                "graph_passed": graph_ok,
                "equivalent": equivalent,
                "diff_msg": diff_msg if not equivalent else None,
                "row_count": len(norm_rel)
            })

        return {
            "all_passed": all_passed,
            "vulnerability_demonstrated": vuln_demonstrated,
            "total_tests": len(results),
            "passed_tests": sum(1 for r in results if r["passed"]),
            "failed_tests": sum(1 for r in results if not r["passed"]),
            "results": results
        }


if __name__ == "__main__":
    validator = Q08IndependentValidator()
    report = validator.run_all_checks()
    print(f"Q08 Vulnerability Demonstrated (Flawed SQL accepted cross-tenant notice): {report['vulnerability_demonstrated']}")
    print(f"Q08 Validation Suite: {'PASS' if report['all_passed'] else 'FAIL'} ({report['passed_tests']}/{report['total_tests']})")
    for r in report["results"]:
        status = "PASS" if r["passed"] else "FAIL"
        print(f"[{status}] {r['test_id']}: {r['description']} (rows={r['row_count']}, eq={r['equivalent']})")
