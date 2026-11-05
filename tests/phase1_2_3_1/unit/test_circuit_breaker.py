"""
Unit Tests for Hard-Delete Circuit Breaker (Phase 1.2.3.1 WP3).
Covers test cases CB-01 through CB-25, including strict input validation (DEF-P1231-04).
"""

import unittest
import math
import sys
from pathlib import Path

# Ensure project root is in sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.phase1_2_3_1.circuit_breaker import CircuitBreaker, CircuitBreakerResult


class TestCircuitBreaker(unittest.TestCase):
    def setUp(self):
        self.cb = CircuitBreaker(threshold_ratio=0.05)

    def test_cb_01_within_threshold(self):
        # 4 <= floor(100 * 0.05) = 5
        res = self.cb.evaluate("User", 100, 4)
        self.assertTrue(res.allowed)
        self.assertEqual(res.decision, "ALLOW")
        self.assertEqual(res.reason, "WITHIN_THRESHOLD")

    def test_cb_02_at_threshold_boundary(self):
        # 5 <= 5
        res = self.cb.evaluate("Department", 100, 5)
        self.assertTrue(res.allowed)
        self.assertEqual(res.decision, "ALLOW")

    def test_cb_03_breach_by_one(self):
        # 6 > 5
        res = self.cb.evaluate("User", 100, 6)
        self.assertFalse(res.allowed)
        self.assertEqual(res.decision, "ABORT")
        self.assertEqual(res.reason, "THRESHOLD_EXCEEDED")

    def test_cb_04_massive_breach(self):
        res = self.cb.evaluate("User", 1000, 500)
        self.assertFalse(res.allowed)
        self.assertEqual(res.decision, "ABORT")

    def test_cb_05_incomplete_extraction(self):
        res = self.cb.evaluate("User", 100, 1, extraction_complete=False)
        self.assertFalse(res.allowed)
        self.assertEqual(res.reason, "INCOMPLETE_EXTRACTION")

    def test_cb_06_protected_entity_zero_candidate(self):
        res = self.cb.evaluate("Tenant", 10, 0)
        self.assertTrue(res.allowed)
        self.assertEqual(res.reason, "NO_OP_PROTECTED_ENTITY")

    def test_cb_07_protected_entity_tenant_breach(self):
        res = self.cb.evaluate("Tenant", 10, 1)
        self.assertFalse(res.allowed)
        self.assertEqual(res.reason, "PROTECTED_ENTITY_TYPE")

    def test_cb_08_protected_entity_nm01_breach(self):
        res = self.cb.evaluate("NM-01", 10, 1)
        self.assertFalse(res.allowed)
        self.assertEqual(res.reason, "PROTECTED_ENTITY_TYPE")

    def test_cb_09_zero_population_zero_candidates(self):
        res = self.cb.evaluate("Notice", 0, 0)
        self.assertTrue(res.allowed)
        self.assertEqual(res.reason, "NO_OP_ZERO_POP")

    def test_cb_10_zero_population_nonzero_candidates(self):
        res = self.cb.evaluate("Notice", 0, 1)
        self.assertFalse(res.allowed)
        self.assertEqual(res.reason, "ZERO_POP_NONZERO_DELETE")

    def test_cb_11_dry_run_within_threshold(self):
        res = self.cb.evaluate("Task", 100, 3, dry_run=True)
        self.assertTrue(res.allowed)
        self.assertEqual(res.decision, "ALLOW")
        self.assertTrue(res.dry_run)

    def test_cb_12_dry_run_exceeding_threshold(self):
        res = self.cb.evaluate("Task", 100, 10, dry_run=True)
        self.assertFalse(res.allowed)
        self.assertEqual(res.decision, "SIMULATED_TRIP")
        self.assertEqual(res.reason, "THRESHOLD_EXCEEDED_DRY_RUN")

    def test_cb_13_batch_all_allowed(self):
        reqs = [
            {"entity_type": "User", "eligible_graph_node_count": 100, "candidate_delete_count": 3},
            {"entity_type": "Department", "eligible_graph_node_count": 50, "candidate_delete_count": 2}
        ]
        batch = self.cb.evaluate_batch(reqs)
        self.assertTrue(batch["batch_allowed"])
        self.assertEqual(batch["overall_decision"], "ALLOW")

    def test_cb_14_batch_atomic_abort(self):
        reqs = [
            {"entity_type": "User", "eligible_graph_node_count": 100, "candidate_delete_count": 3},
            {"entity_type": "Department", "eligible_graph_node_count": 50, "candidate_delete_count": 10}  # trips (10 > 2)
        ]
        batch = self.cb.evaluate_batch(reqs)
        self.assertFalse(batch["batch_allowed"])
        self.assertEqual(batch["overall_decision"], "BATCH_ABORT")
        self.assertEqual(batch["tripped_entity"], "Department")

    def test_cb_15_small_population_rounding(self):
        # floor(19 * 0.05) = floor(0.95) = 0. Any candidate must trip.
        res = self.cb.evaluate("Project", 19, 1)
        self.assertFalse(res.allowed)
        self.assertEqual(res.max_allowed_delete_count, 0)
        self.assertEqual(res.reason, "THRESHOLD_EXCEEDED")

    # --- DEF-P1231-04 Input Validation Tests (CB-16 to CB-25) ---

    def test_cb_16_negative_candidate_count(self):
        res = self.cb.evaluate("User", 100, -1)
        self.assertFalse(res.allowed)
        self.assertEqual(res.reason, "INVALID_INPUT_NEGATIVE_CANDIDATES")

    def test_cb_17_negative_population_count(self):
        res = self.cb.evaluate("User", -100, 2)
        self.assertFalse(res.allowed)
        self.assertEqual(res.reason, "INVALID_INPUT_NEGATIVE_POPULATION")

    def test_cb_18_candidates_exceed_population(self):
        res = self.cb.evaluate("User", 50, 60)
        self.assertFalse(res.allowed)
        self.assertEqual(res.reason, "INVALID_INPUT_CANDIDATES_EXCEED_POPULATION")

    def test_cb_19_nan_population(self):
        res = self.cb.evaluate("User", float("nan"), 5)
        self.assertFalse(res.allowed)
        self.assertEqual(res.reason, "INVALID_INPUT_NAN_INF_POPULATION")

    def test_cb_20_inf_candidate_count(self):
        res = self.cb.evaluate("User", 100, float("inf"))
        self.assertFalse(res.allowed)
        self.assertEqual(res.reason, "INVALID_INPUT_NAN_INF_CANDIDATES")

    def test_cb_21_non_numeric_candidates(self):
        res = self.cb.evaluate("User", 100, "five")
        self.assertFalse(res.allowed)
        self.assertEqual(res.reason, "INVALID_INPUT_NON_NUMERIC_CANDIDATES")

    def test_cb_22_empty_entity_type(self):
        res = self.cb.evaluate("", 100, 2)
        self.assertFalse(res.allowed)
        self.assertEqual(res.reason, "INVALID_INPUT_EMPTY_ENTITY_TYPE")

    def test_cb_23_unapproved_entity_type(self):
        res = self.cb.evaluate("UNKNOWN_DROP_TABLE", 100, 2)
        self.assertFalse(res.allowed)
        self.assertEqual(res.reason, "INVALID_INPUT_UNAPPROVED_ENTITY_TYPE")

    def test_cb_24_duplicate_candidate_keys(self):
        res = self.cb.evaluate("User", 100, 2, candidate_keys=[101, 101])
        self.assertFalse(res.allowed)
        self.assertEqual(res.reason, "INVALID_INPUT_DUPLICATE_CANDIDATE_KEYS")

    def test_cb_25_invalid_tenant_id(self):
        res = self.cb.evaluate("User", 100, 2, tenant_id=-5)
        self.assertFalse(res.allowed)
        self.assertEqual(res.reason, "INVALID_INPUT_TENANT_ID")


if __name__ == "__main__":
    unittest.main()
