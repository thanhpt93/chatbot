"""
Unit Tests for Scoped Hard-Delete Approval Guard (Phase 1.2.3.1 WP3).
Covers test cases HD-01 through HD-12 (DEF-P1231-05).
"""

import unittest
import time
import sys
from pathlib import Path

# Ensure project root is in sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.phase1_2_3_1.reconciliation_safety import (
    ReconciliationSafetyController,
    ScopedApprovalGuard,
    ApprovalToken
)


class TestHardDeleteApprovalGuard(unittest.TestCase):
    def setUp(self):
        self.guard = ScopedApprovalGuard()
        self.controller = ReconciliationSafetyController(hard_delete_enabled=False)

    def test_hd_01_disabled_by_default(self):
        # Destructive operations disabled by default
        plan = self.controller.request_deletion_plan(
            entity_type="User",
            eligible_graph_node_count=100,
            candidate_delete_ids=[101, 102],
            batch_id="BATCH-01",
            tenant_id=1,
            dry_run=False
        )
        self.assertFalse(plan["can_execute"])
        self.assertEqual(plan["execution_status"], "DISABLED_BY_SAFETY_MODE")

    def test_hd_02_dry_run_evaluated(self):
        plan = self.controller.request_deletion_plan(
            entity_type="User",
            eligible_graph_node_count=100,
            candidate_delete_ids=[101, 102],
            batch_id="BATCH-01",
            tenant_id=1,
            dry_run=True
        )
        self.assertFalse(plan["can_execute"])
        self.assertEqual(plan["execution_status"], "DRY_RUN_EVALUATED")

    def test_hd_03_circuit_breaker_trip_blocks(self):
        ctrl = ReconciliationSafetyController(hard_delete_enabled=True)
        # 10 candidates exceeds 5% of 100 (=5)
        plan = ctrl.request_deletion_plan(
            entity_type="User",
            eligible_graph_node_count=100,
            candidate_delete_ids=list(range(10)),
            batch_id="BATCH-01",
            tenant_id=1
        )
        self.assertFalse(plan["can_execute"])
        self.assertEqual(plan["execution_status"], "CIRCUIT_BREAKER_ABORT")

    def test_hd_04_valid_token_authorized(self):
        ctrl = ReconciliationSafetyController(hard_delete_enabled=True)
        token = ctrl.approval_guard.generate_token(
            batch_id="BATCH-01",
            tenant_id=1,
            entity_type="User",
            max_approved_deletes=5
        )
        plan = ctrl.request_deletion_plan(
            entity_type="User",
            eligible_graph_node_count=100,
            candidate_delete_ids=[101, 102],
            batch_id="BATCH-01",
            tenant_id=1,
            approval_token=token
        )
        self.assertTrue(plan["can_execute"])
        self.assertEqual(plan["execution_status"], "AUTHORIZED")

    def test_hd_05_missing_token_denied(self):
        ctrl = ReconciliationSafetyController(hard_delete_enabled=True)
        plan = ctrl.request_deletion_plan(
            entity_type="User",
            eligible_graph_node_count=100,
            candidate_delete_ids=[101, 102],
            batch_id="BATCH-01",
            tenant_id=1,
            approval_token=None
        )
        self.assertFalse(plan["can_execute"])
        self.assertIn("TOKEN_MISSING", plan["execution_status"])

    def test_hd_06_missing_batch_or_tenant_scope(self):
        ctrl = ReconciliationSafetyController(hard_delete_enabled=True)
        plan = ctrl.request_deletion_plan(
            entity_type="User",
            eligible_graph_node_count=100,
            candidate_delete_ids=[101, 102],
            batch_id=None,
            tenant_id=None
        )
        self.assertFalse(plan["can_execute"])
        self.assertEqual(plan["execution_status"], "MISSING_BATCH_OR_TENANT_SCOPE")

    def test_hd_07_batch_id_mismatch(self):
        ctrl = ReconciliationSafetyController(hard_delete_enabled=True)
        token = ctrl.approval_guard.generate_token(
            batch_id="BATCH-01",
            tenant_id=1,
            entity_type="User",
            max_approved_deletes=5
        )
        plan = ctrl.request_deletion_plan(
            entity_type="User",
            eligible_graph_node_count=100,
            candidate_delete_ids=[101, 102],
            batch_id="BATCH-OTHER",
            tenant_id=1,
            approval_token=token
        )
        self.assertFalse(plan["can_execute"])
        self.assertIn("TOKEN_BATCH_MISMATCH", plan["execution_status"])

    def test_hd_08_tenant_id_mismatch(self):
        ctrl = ReconciliationSafetyController(hard_delete_enabled=True)
        token = ctrl.approval_guard.generate_token(
            batch_id="BATCH-01",
            tenant_id=1,
            entity_type="User",
            max_approved_deletes=5
        )
        plan = ctrl.request_deletion_plan(
            entity_type="User",
            eligible_graph_node_count=100,
            candidate_delete_ids=[101, 102],
            batch_id="BATCH-01",
            tenant_id=2,  # mismatched tenant
            approval_token=token
        )
        self.assertFalse(plan["can_execute"])
        self.assertIn("TOKEN_TENANT_MISMATCH", plan["execution_status"])

    def test_hd_09_entity_type_mismatch(self):
        ctrl = ReconciliationSafetyController(hard_delete_enabled=True)
        token = ctrl.approval_guard.generate_token(
            batch_id="BATCH-01",
            tenant_id=1,
            entity_type="Department",  # token is for Department
            max_approved_deletes=5
        )
        plan = ctrl.request_deletion_plan(
            entity_type="User",  # request is for User
            eligible_graph_node_count=100,
            candidate_delete_ids=[101, 102],
            batch_id="BATCH-01",
            tenant_id=1,
            approval_token=token
        )
        self.assertFalse(plan["can_execute"])
        self.assertIn("TOKEN_ENTITY_TYPE_MISMATCH", plan["execution_status"])

    def test_hd_10_candidate_count_exceeded(self):
        ctrl = ReconciliationSafetyController(hard_delete_enabled=True)
        token = ctrl.approval_guard.generate_token(
            batch_id="BATCH-01",
            tenant_id=1,
            entity_type="User",
            max_approved_deletes=2  # token only approves 2 deletes
        )
        plan = ctrl.request_deletion_plan(
            entity_type="User",
            eligible_graph_node_count=100,
            candidate_delete_ids=[101, 102, 103],  # 3 candidates
            batch_id="BATCH-01",
            tenant_id=1,
            approval_token=token
        )
        self.assertFalse(plan["can_execute"])
        self.assertIn("TOKEN_COUNT_EXCEEDED", plan["execution_status"])

    def test_hd_11_expired_token(self):
        ctrl = ReconciliationSafetyController(hard_delete_enabled=True)
        token = ctrl.approval_guard.generate_token(
            batch_id="BATCH-01",
            tenant_id=1,
            entity_type="User",
            max_approved_deletes=5,
            ttl_seconds=-1  # expired immediately
        )
        plan = ctrl.request_deletion_plan(
            entity_type="User",
            eligible_graph_node_count=100,
            candidate_delete_ids=[101],
            batch_id="BATCH-01",
            tenant_id=1,
            approval_token=token
        )
        self.assertFalse(plan["can_execute"])
        self.assertIn("TOKEN_EXPIRED", plan["execution_status"])

    def test_hd_12_revoked_token(self):
        ctrl = ReconciliationSafetyController(hard_delete_enabled=True)
        token = ctrl.approval_guard.generate_token(
            batch_id="BATCH-01",
            tenant_id=1,
            entity_type="User",
            max_approved_deletes=5
        )
        ctrl.approval_guard.revoke_token(token.token_id)
        plan = ctrl.request_deletion_plan(
            entity_type="User",
            eligible_graph_node_count=100,
            candidate_delete_ids=[101],
            batch_id="BATCH-01",
            tenant_id=1,
            approval_token=token
        )
        self.assertFalse(plan["can_execute"])
        self.assertIn("TOKEN_REVOKED", plan["execution_status"])


if __name__ == "__main__":
    unittest.main()
