"""
Validation Runner Integrity & Failure Injection Suite (Phase 1.2.3.1 WP4).
Executes genuine failure injection scenarios and asserts that the validation harness
possesses reporting integrity and cannot emit a false PASS under failure conditions (DEF-P1231-07).
"""

import sys
from pathlib import Path

# Ensure project root is in sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from typing import Dict, Any, List
from scripts.phase1_2_3_1.status_aggregator import StatusAggregator


class RunnerIntegrityValidator:
    """
    Executes 15 failure injection and invariant scenarios (RUN-01 through RUN-15).
    """

    def run_all_checks(self) -> Dict[str, Any]:
        results = []
        all_passed = True

        test_cases = [
            {
                "id": "RUN-01",
                "desc": "Baseline all pass returns PASS (SYNTHETIC FIXTURE & INDEPENDENT SIMULATION)",
                "action": lambda: StatusAggregator.evaluate_metrics(50, 50, 50, 0, p121_passed=True, p122_passed=True),
                "validator": lambda r: r["overall_status"] == "PASS (SYNTHETIC FIXTURE & INDEPENDENT SIMULATION)" and r["invariant_holds"]
            },
            {
                "id": "RUN-02",
                "desc": "Single test failure forces FAIL (TEST FAILURES DETECTED) and NOT READY",
                "action": lambda: StatusAggregator.evaluate_metrics(50, 50, 49, 1, p121_passed=True, p122_passed=True),
                "validator": lambda r: r["overall_status"] == "FAIL (TEST FAILURES DETECTED)" and "NOT READY" in r["readiness_outcome"]
            },
            {
                "id": "RUN-03",
                "desc": "Multiple test failures force FAIL and reports exact failure count",
                "action": lambda: StatusAggregator.evaluate_metrics(50, 50, 45, 5, p121_passed=True, p122_passed=True),
                "validator": lambda r: r["overall_status"] == "FAIL (TEST FAILURES DETECTED)" and "5 CHECKS FAILED" in r["readiness_outcome"]
            },
            {
                "id": "RUN-04",
                "desc": "Metric accounting total discrepancy detected and rejected",
                "action": lambda: StatusAggregator.evaluate_metrics(50, 40, 40, 0),
                "validator": lambda r: r["overall_status"] == "FAIL (METRIC ACCOUNTING DISCREPANCY)" and not r["invariant_holds"]
            },
            {
                "id": "RUN-05",
                "desc": "Execution accounting discrepancy (executed != passed + failed) detected and rejected",
                "action": lambda: StatusAggregator.evaluate_metrics(50, 50, 40, 5),
                "validator": lambda r: r["overall_status"] == "FAIL (EXECUTION ACCOUNTING DISCREPANCY)" and not r["invariant_holds"]
            },
            {
                "id": "RUN-06",
                "desc": "Blocked checks injection correctly changes status to BLOCKED",
                "action": lambda: StatusAggregator.evaluate_metrics(50, 48, 48, 0, checks_blocked=2),
                "validator": lambda r: r["overall_status"] == "BLOCKED" and "2 CHECKS BLOCKED" in r["readiness_outcome"]
            },
            {
                "id": "RUN-07",
                "desc": "Unexecuted checks injection correctly changes status to PARTIAL",
                "action": lambda: StatusAggregator.evaluate_metrics(50, 0, 0, 0, checks_not_executed=50),
                "validator": lambda r: r["overall_status"] == "PARTIAL" and "NOT READY" in r["readiness_outcome"]
            },
            {
                "id": "RUN-08",
                "desc": "Phase 1.2.1 regression failure injection forces overall FAIL",
                "action": lambda: StatusAggregator.evaluate_metrics(50, 50, 50, 0, p121_passed=False, p122_passed=True),
                "validator": lambda r: r["overall_status"] == "FAIL (REGRESSION FAILURE)" and "Phase 1.2.1" in r["readiness_outcome"]
            },
            {
                "id": "RUN-09",
                "desc": "Phase 1.2.2 regression failure injection forces overall FAIL",
                "action": lambda: StatusAggregator.evaluate_metrics(50, 50, 50, 0, p121_passed=True, p122_passed=False),
                "validator": lambda r: r["overall_status"] == "FAIL (REGRESSION FAILURE)" and "Phase 1.2.2" in r["readiness_outcome"]
            },
            {
                "id": "RUN-10",
                "desc": "Both regressions failed injection forces overall FAIL and lists both",
                "action": lambda: StatusAggregator.evaluate_metrics(50, 50, 50, 0, p121_passed=False, p122_passed=False),
                "validator": lambda r: r["overall_status"] == "FAIL (REGRESSION FAILURE)" and "Phase 1.2.1, Phase 1.2.2" in r["readiness_outcome"]
            },
            {
                "id": "RUN-11",
                "desc": "Mock Q01 failure double properly cascades to overall FAIL in aggregator",
                "action": lambda: StatusAggregator.aggregate_suite_reports(
                    {"Q01": {"total_tests": 12, "passed_tests": 11, "failed_tests": 1}}, p121_passed=True, p122_passed=True
                ),
                "validator": lambda r: r["overall_status"] == "FAIL (TEST FAILURES DETECTED)" and r["checks_failed"] == 1
            },
            {
                "id": "RUN-12",
                "desc": "Mock Q08 failure double properly cascades to overall FAIL in aggregator",
                "action": lambda: StatusAggregator.aggregate_suite_reports(
                    {"Q08": {"total_tests": 18, "passed_tests": 17, "failed_tests": 1}}, p121_passed=True, p122_passed=True
                ),
                "validator": lambda r: r["overall_status"] == "FAIL (TEST FAILURES DETECTED)" and r["checks_failed"] == 1
            },
            {
                "id": "RUN-13",
                "desc": "Mock Circuit Breaker failure double cascades to overall FAIL in aggregator",
                "action": lambda: StatusAggregator.aggregate_suite_reports(
                    {"CB": {"total_tests": 25, "passed_tests": 24, "failed_tests": 1}}, p121_passed=True, p122_passed=True
                ),
                "validator": lambda r: r["overall_status"] == "FAIL (TEST FAILURES DETECTED)"
            },
            {
                "id": "RUN-14",
                "desc": "Subprocess exit code failure handling",
                "action": lambda: StatusAggregator.evaluate_metrics(30, 30, 30, 0, p121_passed=(1 == 0)),
                "validator": lambda r: r["overall_status"] == "FAIL (REGRESSION FAILURE)"
            },
            {
                "id": "RUN-15",
                "desc": "Live DB connected success returns PASS (LIVE DATABASE)",
                "action": lambda: StatusAggregator.evaluate_metrics(50, 50, 50, 0, p121_passed=True, p122_passed=True, live_db_connected=True),
                "validator": lambda r: r["overall_status"] == "PASS (LIVE DATABASE)" and r["readiness_outcome"] == "READY FOR PRODUCTION ETL DEPLOYMENT"
            }
        ]

        for tc in test_cases:
            res = tc["action"]()
            passed = tc["validator"](res)
            if not passed:
                all_passed = False

            results.append({
                "test_id": tc["id"],
                "description": tc["desc"],
                "passed": passed,
                "output_status": res.get("overall_status"),
                "readiness": res.get("readiness_outcome")
            })

        return {
            "all_passed": all_passed,
            "total_tests": len(results),
            "passed_tests": sum(1 for r in results if r["passed"]),
            "failed_tests": sum(1 for r in results if not r["passed"]),
            "results": results
        }


if __name__ == "__main__":
    v = RunnerIntegrityValidator()
    rep = v.run_all_checks()
    print(f"Runner Integrity Suite: {'PASS' if rep['all_passed'] else 'FAIL'} ({rep['passed_tests']}/{rep['total_tests']})")
    for r in rep["results"]:
        status = "PASS" if r["passed"] else "FAIL"
        print(f"[{status}] {r['test_id']}: {r['description']} -> {r['output_status']}")
