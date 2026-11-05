"""
Unit tests for ETL Circuit Breaker (CB-01 to CB-15)
Phase 1.2.3 WP3 Verification
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.phase1_2_3.circuit_breaker import CircuitBreaker


def run_circuit_breaker_tests():
    cb = CircuitBreaker(threshold_ratio=0.05)
    test_cases = [
        {"id": "CB-01", "entity": "Department", "pop": 100, "del": 3, "extr": True, "dry": False, "exp_dec": "ALLOW", "exp_max": 5},
        {"id": "CB-02", "entity": "Department", "pop": 100, "del": 5, "extr": True, "dry": False, "exp_dec": "ALLOW", "exp_max": 5},
        {"id": "CB-03", "entity": "Department", "pop": 100, "del": 6, "extr": True, "dry": False, "exp_dec": "ABORT", "exp_max": 5, "exp_reason": "THRESHOLD_EXCEEDED"},
        {"id": "CB-04", "entity": "Project", "pop": 20, "del": 1, "extr": True, "dry": False, "exp_dec": "ALLOW", "exp_max": 1},
        {"id": "CB-05", "entity": "Project", "pop": 20, "del": 2, "extr": True, "dry": False, "exp_dec": "ABORT", "exp_max": 1, "exp_reason": "THRESHOLD_EXCEEDED"},
        {"id": "CB-06", "entity": "Task", "pop": 19, "del": 0, "extr": True, "dry": False, "exp_dec": "ALLOW", "exp_max": 0},
        {"id": "CB-07", "entity": "Task", "pop": 19, "del": 1, "extr": True, "dry": False, "exp_dec": "ABORT", "exp_max": 0, "exp_reason": "THRESHOLD_EXCEEDED"},
        {"id": "CB-08", "entity": "Notice", "pop": 0, "del": 0, "extr": True, "dry": False, "exp_dec": "ALLOW", "exp_max": 0, "exp_reason": "NO_OP_ZERO_POP"},
        {"id": "CB-09", "entity": "Notice", "pop": 0, "del": 1, "extr": True, "dry": False, "exp_dec": "ABORT", "exp_max": 0, "exp_reason": "ZERO_POP_NONZERO_DELETE"},
        {"id": "CB-10", "entity": "User", "pop": 1000, "del": 50, "extr": True, "dry": False, "exp_dec": "ALLOW", "exp_max": 50},
        {"id": "CB-11", "entity": "User", "pop": 1000, "del": 51, "extr": True, "dry": False, "exp_dec": "ABORT", "exp_max": 50, "exp_reason": "THRESHOLD_EXCEEDED"},
        {"id": "CB-12", "entity": "Tenant", "pop": 50, "del": 1, "extr": True, "dry": False, "exp_dec": "ABORT", "exp_max": 0, "exp_reason": "PROTECTED_ENTITY_TYPE"},
        {"id": "CB-13", "entity": "Department", "pop": 100, "del": 1, "extr": False, "dry": False, "exp_dec": "ABORT", "exp_max": 0, "exp_reason": "INCOMPLETE_EXTRACTION"},
        {"id": "CB-14", "entity": "Department", "pop": 100, "del": 10, "extr": True, "dry": True, "exp_dec": "SIMULATED_TRIP", "exp_max": 5, "exp_reason": "THRESHOLD_EXCEEDED_DRY_RUN"},
    ]

    results = []
    all_passed = True

    for tc in test_cases:
        res = cb.evaluate(
            entity_type=tc["entity"],
            eligible_graph_node_count=tc["pop"],
            candidate_delete_count=tc["del"],
            extraction_complete=tc["extr"],
            dry_run=tc["dry"]
        )

        passed = (
            res.decision == tc["exp_dec"]
            and res.max_allowed_delete_count == tc["exp_max"]
        )
        if "exp_reason" in tc and res.reason != tc["exp_reason"]:
            passed = False

        if not passed:
            all_passed = False

        results.append({
            "test_id": tc["id"],
            "entity": tc["entity"],
            "pop": tc["pop"],
            "candidates": tc["del"],
            "expected_decision": tc["exp_dec"],
            "actual_decision": res.decision,
            "max_allowed": res.max_allowed_delete_count,
            "reason": res.reason,
            "passed": passed
        })

    # Test CB-15: Batch test
    batch_requests = [
        {"entity_type": "Department", "eligible_graph_node_count": 100, "candidate_delete_count": 2, "extraction_complete": True},
        {"entity_type": "Task", "eligible_graph_node_count": 50, "candidate_delete_count": 10, "extraction_complete": True}  # 10 > 2 (trips!)
    ]
    batch_res = cb.evaluate_batch(batch_requests, dry_run=False)
    cb15_passed = (
        batch_res["batch_allowed"] is False
        and batch_res["overall_decision"] == "BATCH_ABORT"
        and batch_res["tripped_entity"] == "Task"
    )
    if not cb15_passed:
        all_passed = False

    results.append({
        "test_id": "CB-15",
        "entity": "Multi-Entity Batch",
        "pop": "N/A",
        "candidates": "N/A",
        "expected_decision": "BATCH_ABORT",
        "actual_decision": batch_res["overall_decision"],
        "max_allowed": "N/A",
        "reason": f"Tripped by {batch_res['tripped_entity']}",
        "passed": cb15_passed
    })

    return {
        "all_passed": all_passed,
        "total_tests": len(results),
        "passed_tests": sum(1 for r in results if r["passed"]),
        "failed_tests": sum(1 for r in results if not r["passed"]),
        "results": results
    }


if __name__ == "__main__":
    report = run_circuit_breaker_tests()
    print(f"CB Test Suite Result: {'PASS' if report['all_passed'] else 'FAIL'} ({report['passed_tests']}/{report['total_tests']})")
    for r in report["results"]:
        status = "PASS" if r["passed"] else "FAIL"
        print(f"[{status}] {r['test_id']}: decision={r['actual_decision']}, max_allowed={r['max_allowed']}, reason={r['reason']}")
