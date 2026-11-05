"""
Unit Tests for Runner Failure Injection (Phase 1.2.3.1 WP4).
Covers test cases RUN-01 through RUN-15 using genuine test doubles and failure injections (DEF-P1231-07).
"""

import unittest
import sys
from pathlib import Path

# Ensure project root is in sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.phase1_2_3_1.status_aggregator import StatusAggregator


class TestRunnerFailureInjection(unittest.TestCase):

    def test_run_01_baseline_all_pass(self):
        res = StatusAggregator.evaluate_metrics(
            checks_total=50, checks_executed=50, checks_passed=50, checks_failed=0,
            p121_passed=True, p122_passed=True, live_db_connected=False
        )
        self.assertEqual(res["overall_status"], "PASS (SYNTHETIC FIXTURE & INDEPENDENT SIMULATION)")
        self.assertEqual(res["readiness_outcome"], "READY FOR SYNTHETIC ETL TESTING")
        self.assertTrue(res["invariant_holds"])

    def test_run_02_single_failure_injection(self):
        res = StatusAggregator.evaluate_metrics(
            checks_total=50, checks_executed=50, checks_passed=49, checks_failed=1,
            p121_passed=True, p122_passed=True
        )
        self.assertEqual(res["overall_status"], "FAIL (TEST FAILURES DETECTED)")
        self.assertIn("NOT READY", res["readiness_outcome"])

    def test_run_03_multiple_failure_injection(self):
        res = StatusAggregator.evaluate_metrics(
            checks_total=50, checks_executed=50, checks_passed=45, checks_failed=5,
            p121_passed=True, p122_passed=True
        )
        self.assertEqual(res["overall_status"], "FAIL (TEST FAILURES DETECTED)")
        self.assertIn("5 CHECKS FAILED", res["readiness_outcome"])

    def test_run_04_total_invariant_violation(self):
        # 50 != 40 + 0 + 0 + 0
        res = StatusAggregator.evaluate_metrics(
            checks_total=50, checks_executed=40, checks_passed=40, checks_failed=0
        )
        self.assertEqual(res["overall_status"], "FAIL (METRIC ACCOUNTING DISCREPANCY)")
        self.assertFalse(res["invariant_holds"])

    def test_run_05_execution_invariant_violation(self):
        # executed (50) != passed (40) + failed (5)
        res = StatusAggregator.evaluate_metrics(
            checks_total=50, checks_executed=50, checks_passed=40, checks_failed=5
        )
        self.assertEqual(res["overall_status"], "FAIL (EXECUTION ACCOUNTING DISCREPANCY)")
        self.assertFalse(res["invariant_holds"])

    def test_run_06_blocked_checks_injection(self):
        res = StatusAggregator.evaluate_metrics(
            checks_total=50, checks_executed=48, checks_passed=48, checks_failed=0,
            checks_blocked=2
        )
        self.assertEqual(res["overall_status"], "BLOCKED")
        self.assertIn("2 CHECKS BLOCKED", res["readiness_outcome"])

    def test_run_07_unexecuted_checks_injection(self):
        res = StatusAggregator.evaluate_metrics(
            checks_total=50, checks_executed=0, checks_passed=0, checks_failed=0,
            checks_not_executed=50
        )
        self.assertEqual(res["overall_status"], "PARTIAL")
        self.assertIn("NOT READY", res["readiness_outcome"])

    def test_run_08_p121_regression_failure_injection(self):
        # DEF-P1231-06: Even if all 50 current checks pass, failed P1.2.1 forces FAIL
        res = StatusAggregator.evaluate_metrics(
            checks_total=50, checks_executed=50, checks_passed=50, checks_failed=0,
            p121_passed=False, p122_passed=True
        )
        self.assertEqual(res["overall_status"], "FAIL (REGRESSION FAILURE)")
        self.assertIn("Phase 1.2.1", res["readiness_outcome"])

    def test_run_09_p122_regression_failure_injection(self):
        # DEF-P1231-06: Even if all 50 current checks pass, failed P1.2.2 forces FAIL
        res = StatusAggregator.evaluate_metrics(
            checks_total=50, checks_executed=50, checks_passed=50, checks_failed=0,
            p121_passed=True, p122_passed=False
        )
        self.assertEqual(res["overall_status"], "FAIL (REGRESSION FAILURE)")
        self.assertIn("Phase 1.2.2", res["readiness_outcome"])

    def test_run_10_both_regressions_failed_injection(self):
        res = StatusAggregator.evaluate_metrics(
            checks_total=50, checks_executed=50, checks_passed=50, checks_failed=0,
            p121_passed=False, p122_passed=False
        )
        self.assertEqual(res["overall_status"], "FAIL (REGRESSION FAILURE)")
        self.assertIn("Phase 1.2.1, Phase 1.2.2", res["readiness_outcome"])

    def test_run_11_mock_q01_failure_double(self):
        mock_reports = {
            "Q01": {"total_tests": 12, "passed_tests": 11, "failed_tests": 1},
            "Q08": {"total_tests": 18, "passed_tests": 18, "failed_tests": 0}
        }
        res = StatusAggregator.aggregate_suite_reports(mock_reports, p121_passed=True, p122_passed=True)
        self.assertEqual(res["overall_status"], "FAIL (TEST FAILURES DETECTED)")
        self.assertEqual(res["checks_failed"], 1)

    def test_run_12_mock_q08_failure_double(self):
        mock_reports = {
            "Q01": {"total_tests": 12, "passed_tests": 12, "failed_tests": 0},
            "Q08": {"total_tests": 18, "passed_tests": 17, "failed_tests": 1}
        }
        res = StatusAggregator.aggregate_suite_reports(mock_reports, p121_passed=True, p122_passed=True)
        self.assertEqual(res["overall_status"], "FAIL (TEST FAILURES DETECTED)")
        self.assertEqual(res["checks_failed"], 1)

    def test_run_13_mock_circuit_breaker_failure_double(self):
        mock_reports = {
            "CB": {"total_tests": 25, "passed_tests": 24, "failed_tests": 1}
        }
        res = StatusAggregator.aggregate_suite_reports(mock_reports, p121_passed=True, p122_passed=True)
        self.assertEqual(res["overall_status"], "FAIL (TEST FAILURES DETECTED)")

    def test_run_14_subprocess_failure_handling(self):
        # Simulates subprocess returncode != 0
        proc_exit_code = 1
        p121_passed = (proc_exit_code == 0)
        res = StatusAggregator.evaluate_metrics(
            checks_total=30, checks_executed=30, checks_passed=30, checks_failed=0,
            p121_passed=p121_passed
        )
        self.assertEqual(res["overall_status"], "FAIL (REGRESSION FAILURE)")

    def test_run_15_live_db_connected_success(self):
        res = StatusAggregator.evaluate_metrics(
            checks_total=50, checks_executed=50, checks_passed=50, checks_failed=0,
            p121_passed=True, p122_passed=True, live_db_connected=True
        )
        self.assertEqual(res["overall_status"], "PASS (LIVE DATABASE)")
        self.assertEqual(res["readiness_outcome"], "READY FOR PRODUCTION ETL DEPLOYMENT")


if __name__ == "__main__":
    unittest.main()
