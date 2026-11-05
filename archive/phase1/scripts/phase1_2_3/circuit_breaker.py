"""
ETL Circuit Breaker Implementation (Phase 1.2.3 WP3)
Defines the hard-delete threshold evaluation, entity safety rules,
and batch reconciliation protection.
"""

import math
from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class CircuitBreakerResult:
    allowed: bool
    decision: str  # ALLOW, ABORT, SIMULATED_TRIP
    reason: str
    eligible_graph_node_count: int
    candidate_delete_count: int
    max_allowed_delete_count: int
    entity_type: str
    dry_run: bool


class CircuitBreaker:
    """
    Hard-Delete Circuit Breaker for Graph Reconciliation (R-7).
    Guards Neo4j graph against catastrophic mass deletions during ETL.
    """

    DEFAULT_THRESHOLD_RATIO = 0.05
    PROTECTED_ENTITIES = {"Tenant", "NM-01"}

    def __init__(self, threshold_ratio: float = DEFAULT_THRESHOLD_RATIO):
        self.threshold_ratio = threshold_ratio

    def evaluate(
        self,
        entity_type: str,
        eligible_graph_node_count: int,
        candidate_delete_count: int,
        extraction_complete: bool = True,
        dry_run: bool = False
    ) -> CircuitBreakerResult:
        """
        Evaluates deletion candidates against the safety threshold.
        """
        # Rule 1: Extraction completeness check
        if not extraction_complete:
            return CircuitBreakerResult(
                allowed=False,
                decision="ABORT",
                reason="INCOMPLETE_EXTRACTION",
                eligible_graph_node_count=eligible_graph_node_count,
                candidate_delete_count=candidate_delete_count,
                max_allowed_delete_count=0,
                entity_type=entity_type,
                dry_run=dry_run
            )

        # Rule 2: Protected entity check (Tenant nodes can never be auto-deleted)
        if entity_type in self.PROTECTED_ENTITIES:
            max_allowed = 0
            if candidate_delete_count > 0:
                return CircuitBreakerResult(
                    allowed=False,
                    decision="ABORT",
                    reason="PROTECTED_ENTITY_TYPE",
                    eligible_graph_node_count=eligible_graph_node_count,
                    candidate_delete_count=candidate_delete_count,
                    max_allowed_delete_count=max_allowed,
                    entity_type=entity_type,
                    dry_run=dry_run
                )
            else:
                return CircuitBreakerResult(
                    allowed=True,
                    decision="ALLOW",
                    reason="NO_OP_PROTECTED_ENTITY",
                    eligible_graph_node_count=eligible_graph_node_count,
                    candidate_delete_count=candidate_delete_count,
                    max_allowed_delete_count=max_allowed,
                    entity_type=entity_type,
                    dry_run=dry_run
                )

        # Rule 3: Zero-population handling
        if eligible_graph_node_count == 0:
            if candidate_delete_count == 0:
                return CircuitBreakerResult(
                    allowed=True,
                    decision="ALLOW",
                    reason="NO_OP_ZERO_POP",
                    eligible_graph_node_count=0,
                    candidate_delete_count=0,
                    max_allowed_delete_count=0,
                    entity_type=entity_type,
                    dry_run=dry_run
                )
            else:
                return CircuitBreakerResult(
                    allowed=False,
                    decision="ABORT",
                    reason="ZERO_POP_NONZERO_DELETE",
                    eligible_graph_node_count=0,
                    candidate_delete_count=candidate_delete_count,
                    max_allowed_delete_count=0,
                    entity_type=entity_type,
                    dry_run=dry_run
                )

        # Rule 4: Threshold calculation: floor(eligible_graph_node_count * threshold_ratio)
        max_allowed = math.floor(eligible_graph_node_count * self.threshold_ratio)

        # Rule 5: Candidate count evaluation
        if candidate_delete_count <= max_allowed:
            return CircuitBreakerResult(
                allowed=True,
                decision="ALLOW",
                reason="WITHIN_THRESHOLD",
                eligible_graph_node_count=eligible_graph_node_count,
                candidate_delete_count=candidate_delete_count,
                max_allowed_delete_count=max_allowed,
                entity_type=entity_type,
                dry_run=dry_run
            )
        else:
            # Breach detected!
            if dry_run:
                return CircuitBreakerResult(
                    allowed=False,
                    decision="SIMULATED_TRIP",
                    reason="THRESHOLD_EXCEEDED_DRY_RUN",
                    eligible_graph_node_count=eligible_graph_node_count,
                    candidate_delete_count=candidate_delete_count,
                    max_allowed_delete_count=max_allowed,
                    entity_type=entity_type,
                    dry_run=True
                )
            else:
                return CircuitBreakerResult(
                    allowed=False,
                    decision="ABORT",
                    reason="THRESHOLD_EXCEEDED",
                    eligible_graph_node_count=eligible_graph_node_count,
                    candidate_delete_count=candidate_delete_count,
                    max_allowed_delete_count=max_allowed,
                    entity_type=entity_type,
                    dry_run=False
                )

    def evaluate_batch(
        self,
        batch_requests: List[Dict[str, Any]],
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Evaluates a batch of reconciliation deletion requests.
        Atomic abort: if any single entity trips, the whole batch fails.
        """
        results = []
        batch_allowed = True
        tripped_entity = None

        for req in batch_requests:
            res = self.evaluate(
                entity_type=req.get("entity_type", "Unknown"),
                eligible_graph_node_count=req.get("eligible_graph_node_count", 0),
                candidate_delete_count=req.get("candidate_delete_count", 0),
                extraction_complete=req.get("extraction_complete", True),
                dry_run=dry_run
            )
            results.append(res)
            if not res.allowed:
                batch_allowed = False
                if tripped_entity is None:
                    tripped_entity = res.entity_type

        return {
            "batch_allowed": batch_allowed,
            "overall_decision": "ALLOW" if batch_allowed else ("SIMULATED_TRIP" if dry_run else "BATCH_ABORT"),
            "tripped_entity": tripped_entity,
            "results": results
        }
