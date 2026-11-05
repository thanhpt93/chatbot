"""
Validator Module for Scenario Q01 (WP1 & WP5).
Runs test cases Q01-01 through Q01-12 across independent Relational and Graph executors.
Enforces 100% exact JSON payload equivalence using strict ResultNormalizer.
"""

import sys
from pathlib import Path

# Ensure project root is in sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from typing import Dict, Any, List
from tests.phase1_2_3_1.relational.q01_relational_executor import Q01RelationalExecutor
from tests.phase1_2_3_1.graph.q01_graph_executor import Q01GraphExecutor
from tests.phase1_2_3_1.common.result_normalizer import ResultNormalizer


class Q01IndependentValidator:
    def __init__(self):
        self.rel_exec = Q01RelationalExecutor()
        self.graph_exec = Q01GraphExecutor()

    def run_all_checks(self) -> Dict[str, Any]:
        results = []
        all_passed = True

        test_cases = [
            {
                "id": "Q01-01",
                "desc": "Valid department query with sub-departments and active employees",
                "params": {"tenant_id": 1, "requesting_user_id": 101, "department_id": 10},
                "validator": lambda res: (
                    len(res) == 1
                    and res[0]["department_id"] == 10
                    and res[0]["manager_id"] == 101
                    and len(res[0]["sub_departments"]) == 5
                    and len(res[0]["active_employees"]) == 2
                )
            },
            {
                "id": "Q01-02",
                "desc": "Leaf department (0 sub-departments) returns empty array []",
                "params": {"tenant_id": 1, "requesting_user_id": 101, "department_id": 16},
                "validator": lambda res: (
                    len(res) == 1
                    and res[0]["sub_departments"] == []
                    and isinstance(res[0]["sub_departments"], list)
                )
            },
            {
                "id": "Q01-03",
                "desc": "Empty department (0 active employees) returns empty array []",
                "params": {"tenant_id": 1, "requesting_user_id": 101, "department_id": 16},
                "validator": lambda res: (
                    len(res) == 1
                    and res[0]["active_employees"] == []
                    and isinstance(res[0]["active_employees"], list)
                )
            },
            {
                "id": "Q01-04",
                "desc": "Department with inactive user manager has manager_id null",
                "params": {"tenant_id": 1, "requesting_user_id": 101, "department_id": 13},
                "validator": lambda res: len(res) == 1 and res[0]["manager_id"] is None
            },
            {
                "id": "Q01-05",
                "desc": "Department with manager having suspended tenant membership has manager_id null",
                "params": {"tenant_id": 1, "requesting_user_id": 101, "department_id": 11},
                "validator": lambda res: len(res) == 1 and res[0]["manager_id"] is None
            },
            {
                "id": "Q01-06",
                "desc": "Department with manager having deleted tenant membership has manager_id null",
                "params": {"tenant_id": 1, "requesting_user_id": 101, "department_id": 15},
                "validator": lambda res: len(res) == 1 and res[0]["manager_id"] is None
            },
            {
                "id": "Q01-07",
                "desc": "Department with cross-tenant manager has manager_id null",
                "params": {"tenant_id": 1, "requesting_user_id": 101, "department_id": 12},
                "validator": lambda res: len(res) == 1 and res[0]["manager_id"] is None
            },
            {
                "id": "Q01-08",
                "desc": "Requesting user with suspended membership is denied (0 rows)",
                "params": {"tenant_id": 1, "requesting_user_id": 102, "department_id": 10},
                "validator": lambda res: len(res) == 0
            },
            {
                "id": "Q01-09",
                "desc": "Requesting user with deleted membership is denied (0 rows)",
                "params": {"tenant_id": 1, "requesting_user_id": 103, "department_id": 10},
                "validator": lambda res: len(res) == 0
            },
            {
                "id": "Q01-10",
                "desc": "Cross-tenant requesting user is denied (0 rows)",
                "params": {"tenant_id": 1, "requesting_user_id": 201, "department_id": 10},
                "validator": lambda res: len(res) == 0
            },
            {
                "id": "Q01-11",
                "desc": "Former employee with effective_to IS NOT NULL is excluded",
                "params": {"tenant_id": 1, "requesting_user_id": 101, "department_id": 10},
                "validator": lambda res: (
                    len(res) == 1
                    and not any(emp["id"] == 104 for emp in res[0]["active_employees"])
                )
            },
            {
                "id": "Q01-12",
                "desc": "Department member with suspended tenant membership is excluded",
                "params": {"tenant_id": 1, "requesting_user_id": 101, "department_id": 10},
                "validator": lambda res: (
                    len(res) == 1
                    and not any(emp["id"] == 102 for emp in res[0]["active_employees"])
                )
            }
        ]

        for tc in test_cases:
            p = tc["params"]
            raw_rel = self.rel_exec.execute_relational_q01(
                tenant_id=p["tenant_id"],
                requesting_user_id=p["requesting_user_id"],
                department_id=p["department_id"]
            )
            raw_graph = self.graph_exec.execute_graph_q01(
                tenant_id=p["tenant_id"],
                requesting_user_id=p["requesting_user_id"],
                department_id=p["department_id"]
            )

            norm_rel = ResultNormalizer.normalize_q01_payload(raw_rel)
            norm_graph = ResultNormalizer.normalize_q01_payload(raw_graph)

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
            "total_tests": len(results),
            "passed_tests": sum(1 for r in results if r["passed"]),
            "failed_tests": sum(1 for r in results if not r["passed"]),
            "results": results
        }


if __name__ == "__main__":
    validator = Q01IndependentValidator()
    report = validator.run_all_checks()
    print(f"Q01 Validation Suite: {'PASS' if report['all_passed'] else 'FAIL'} ({report['passed_tests']}/{report['total_tests']})")
    for r in report["results"]:
        status = "PASS" if r["passed"] else "FAIL"
        print(f"[{status}] {r['test_id']}: {r['description']} (rows={r['row_count']}, eq={r['equivalent']})")
