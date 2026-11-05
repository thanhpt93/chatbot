"""
Reconciliation Safety & Audit Hardening (Phase 1.2.3 WP3)
Provides safety guards, audit trail logging, and dry-run execution
for Graph Hard-Delete Reconciliation (Pattern R-7).
"""

import logging
from typing import Dict, Any, List
from .circuit_breaker import CircuitBreaker, CircuitBreakerResult

logger = logging.getLogger("reconciliation_safety")


class ReconciliationSafetyController:
    """
    Enforces that hard deletes in Neo4j are strictly controlled, audited,
    and gated by the 5% Circuit Breaker threshold.
    """

    def __init__(self, hard_delete_enabled: bool = False, threshold_ratio: float = 0.05):
        # Destructive operations are disabled by default
        self.hard_delete_enabled = hard_delete_enabled
        self.circuit_breaker = CircuitBreaker(threshold_ratio=threshold_ratio)
        self.audit_log: List[Dict[str, Any]] = []

    def request_deletion_plan(
        self,
        entity_type: str,
        eligible_graph_node_count: int,
        candidate_delete_ids: List[Any],
        extraction_complete: bool = True,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Plans and authorizes a deletion execution.
        """
        candidate_count = len(candidate_delete_ids)
        cb_res = self.circuit_breaker.evaluate(
            entity_type=entity_type,
            eligible_graph_node_count=eligible_graph_node_count,
            candidate_delete_count=candidate_count,
            extraction_complete=extraction_complete,
            dry_run=dry_run
        )

        can_execute = False
        execution_status = "BLOCKED"

        if not self.hard_delete_enabled and not dry_run:
            execution_status = "DISABLED_BY_SAFETY_MODE"
            can_execute = False
        elif dry_run:
            execution_status = "DRY_RUN_EVALUATED"
            can_execute = False
        elif cb_res.allowed:
            execution_status = "AUTHORIZED"
            can_execute = True
        else:
            execution_status = f"CIRCUIT_BREAKER_{cb_res.decision}"
            can_execute = False

        record = {
            "entity_type": entity_type,
            "eligible_graph_node_count": eligible_graph_node_count,
            "candidate_count": candidate_count,
            "max_allowed": cb_res.max_allowed_delete_count,
            "cb_decision": cb_res.decision,
            "cb_reason": cb_res.reason,
            "can_execute": can_execute,
            "execution_status": execution_status,
            "dry_run": dry_run
        }
        self.audit_log.append(record)
        return record
