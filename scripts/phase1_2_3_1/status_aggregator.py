"""
Central Status Aggregator & Invariant Accounting Engine (Phase 1.2.3.1 WP4).
Enforces dynamic status calculation, mandatory regression dependencies,
and strict metric accounting invariants (DEF-P1231-06).
"""

from typing import Dict, Any, List, Optional


class StatusAggregator:
    """
    Central calculation engine for Phase 1.2.3.1 validation results.
    Enforces that:
    1. A single failed regression (P1.2.1, P1.2.2) immediately forces overall FAIL and NOT READY.
    2. Any test failure in Q01, Q08, Circuit Breaker, Hard-Delete, or Runner Integrity forces overall FAIL and NOT READY.
    3. Accounting invariant: checks_total == checks_executed + checks_blocked + checks_not_executed + checks_needs_source_confirmation
    4. Accounting invariant: checks_executed == checks_passed + checks_failed
    """

    @classmethod
    def evaluate_metrics(
        cls,
        checks_total: int,
        checks_executed: int,
        checks_passed: int,
        checks_failed: int,
        checks_blocked: int = 0,
        checks_not_executed: int = 0,
        checks_needs_source_confirmation: int = 0,
        p121_passed: bool = True,
        p122_passed: bool = True,
        live_db_connected: bool = False
    ) -> Dict[str, Any]:
        # Invariant 1: Total must equal sum of disjoint categories
        expected_total = checks_executed + checks_blocked + checks_not_executed + checks_needs_source_confirmation
        if checks_total != expected_total:
            return {
                "overall_status": "FAIL (METRIC ACCOUNTING DISCREPANCY)",
                "readiness_outcome": "NOT READY - METRIC ACCOUNTING DISCREPANCY",
                "invariant_holds": False,
                "error": f"Accounting discrepancy: total ({checks_total}) != sum of categories ({expected_total})",
                "checks_total": checks_total,
                "checks_executed": checks_executed,
                "checks_passed": checks_passed,
                "checks_failed": checks_failed,
                "checks_blocked": checks_blocked,
                "checks_not_executed": checks_not_executed,
                "checks_needs_source_confirmation": checks_needs_source_confirmation
            }

        # Invariant 2: checks_executed must equal passed + failed
        if checks_executed != (checks_passed + checks_failed):
            return {
                "overall_status": "FAIL (EXECUTION ACCOUNTING DISCREPANCY)",
                "readiness_outcome": "NOT READY - EXECUTION ACCOUNTING DISCREPANCY",
                "invariant_holds": False,
                "error": f"Execution discrepancy: executed ({checks_executed}) != passed ({checks_passed}) + failed ({checks_failed})",
                "checks_total": checks_total,
                "checks_executed": checks_executed,
                "checks_passed": checks_passed,
                "checks_failed": checks_failed,
                "checks_blocked": checks_blocked,
                "checks_not_executed": checks_not_executed,
                "checks_needs_source_confirmation": checks_needs_source_confirmation
            }

        # Mandatory Regression Check (DEF-P1231-06)
        if not p121_passed or not p122_passed:
            failed_reg = []
            if not p121_passed:
                failed_reg.append("Phase 1.2.1")
            if not p122_passed:
                failed_reg.append("Phase 1.2.2")
            return {
                "overall_status": "FAIL (REGRESSION FAILURE)",
                "readiness_outcome": f"NOT READY - REGRESSION FAILED ({', '.join(failed_reg)})",
                "invariant_holds": True,
                "error": f"Mandatory regression check failed: {', '.join(failed_reg)}",
                "checks_total": checks_total,
                "checks_executed": checks_executed,
                "checks_passed": checks_passed,
                "checks_failed": checks_failed,
                "checks_blocked": checks_blocked,
                "checks_not_executed": checks_not_executed,
                "checks_needs_source_confirmation": checks_needs_source_confirmation
            }

        # Test failure check
        if checks_failed > 0:
            return {
                "overall_status": "FAIL (TEST FAILURES DETECTED)",
                "readiness_outcome": f"NOT READY - {checks_failed} CHECKS FAILED",
                "invariant_holds": True,
                "error": f"{checks_failed} validation checks failed",
                "checks_total": checks_total,
                "checks_executed": checks_executed,
                "checks_passed": checks_passed,
                "checks_failed": checks_failed,
                "checks_blocked": checks_blocked,
                "checks_not_executed": checks_not_executed,
                "checks_needs_source_confirmation": checks_needs_source_confirmation
            }

        # Blocked checks
        if checks_blocked > 0:
            return {
                "overall_status": "BLOCKED",
                "readiness_outcome": f"NOT READY - {checks_blocked} CHECKS BLOCKED",
                "invariant_holds": True,
                "checks_total": checks_total,
                "checks_executed": checks_executed,
                "checks_passed": checks_passed,
                "checks_failed": checks_failed,
                "checks_blocked": checks_blocked,
                "checks_not_executed": checks_not_executed,
                "checks_needs_source_confirmation": checks_needs_source_confirmation
            }

        # Unexecuted checks
        if checks_not_executed > 0:
            if checks_passed > 0 and not live_db_connected:
                return {
                    "overall_status": "PASS (SYNTHETIC ONLY)",
                    "readiness_outcome": "READY FOR SYNTHETIC ETL TESTING",
                    "invariant_holds": True,
                    "checks_total": checks_total,
                    "checks_executed": checks_executed,
                    "checks_passed": checks_passed,
                    "checks_failed": checks_failed,
                    "checks_blocked": checks_blocked,
                    "checks_not_executed": checks_not_executed,
                    "checks_needs_source_confirmation": checks_needs_source_confirmation
                }
            else:
                return {
                    "overall_status": "PARTIAL",
                    "readiness_outcome": "NOT READY - UNEXECUTED CHECKS REMAINING",
                    "invariant_holds": True,
                    "checks_total": checks_total,
                    "checks_executed": checks_executed,
                    "checks_passed": checks_passed,
                    "checks_failed": checks_failed,
                    "checks_blocked": checks_blocked,
                    "checks_not_executed": checks_not_executed,
                    "checks_needs_source_confirmation": checks_needs_source_confirmation
                }

        # All executed, 0 failed, 0 blocked, 0 not executed
        if live_db_connected:
            return {
                "overall_status": "PASS (LIVE DATABASE)",
                "readiness_outcome": "READY FOR PRODUCTION ETL DEPLOYMENT",
                "invariant_holds": True,
                "checks_total": checks_total,
                "checks_executed": checks_executed,
                "checks_passed": checks_passed,
                "checks_failed": checks_failed,
                "checks_blocked": checks_blocked,
                "checks_not_executed": checks_not_executed,
                "checks_needs_source_confirmation": checks_needs_source_confirmation
            }
        else:
            return {
                "overall_status": "PASS (SYNTHETIC FIXTURE & INDEPENDENT SIMULATION)",
                "readiness_outcome": "READY FOR SYNTHETIC ETL TESTING",
                "invariant_holds": True,
                "checks_total": checks_total,
                "checks_executed": checks_executed,
                "checks_passed": checks_passed,
                "checks_failed": checks_failed,
                "checks_blocked": checks_blocked,
                "checks_not_executed": checks_not_executed,
                "checks_needs_source_confirmation": checks_needs_source_confirmation
            }

    @classmethod
    def aggregate_suite_reports(
        cls,
        module_reports: Dict[str, Dict[str, Any]],
        p121_passed: bool = True,
        p122_passed: bool = True,
        live_db_connected: bool = False
    ) -> Dict[str, Any]:
        """
        Aggregates multiple module test report dictionaries into a master report.
        """
        total = 0
        passed = 0
        failed = 0
        blocked = 0
        not_executed = 0
        needs_src = 0

        for mod_name, rep in module_reports.items():
            total += rep.get("total_tests", 0)
            passed += rep.get("passed_tests", 0)
            failed += rep.get("failed_tests", 0)
            blocked += rep.get("blocked_tests", 0)
            not_executed += rep.get("not_executed_tests", 0)
            needs_src += rep.get("needs_source_confirmation_tests", 0)

        executed = passed + failed

        evaluation = cls.evaluate_metrics(
            checks_total=total,
            checks_executed=executed,
            checks_passed=passed,
            checks_failed=failed,
            checks_blocked=blocked,
            checks_not_executed=not_executed,
            checks_needs_source_confirmation=needs_src,
            p121_passed=p121_passed,
            p122_passed=p122_passed,
            live_db_connected=live_db_connected
        )

        return {
            **evaluation,
            "module_reports": module_reports
        }
