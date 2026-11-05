"""
ETL Hard-Delete Circuit Breaker (Phase 1.2.3.1 WP3).
Implements strict input validation, threshold evaluation, entity safety rules,
and batch reconciliation protection for Reconciliation Pattern R-7.
Guards Neo4j graph against catastrophic mass deletions during ETL.
"""

import math
from typing import Dict, Any, List, Optional, Set
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
    tenant_id: Optional[int] = None


class CircuitBreaker:
    """
    Hard-Delete Circuit Breaker for Graph Reconciliation (R-7).
    Guards Neo4j graph against catastrophic deletions during ETL synchronization.
    Strictly validates all inputs before threshold evaluation (DEF-P1231-04).
    """

    DEFAULT_THRESHOLD_RATIO = 0.05
    PROTECTED_ENTITIES = {"Tenant", "NM-01"}
    
    # 24 Approved Nodes from Phase 1 Architecture
    APPROVED_ENTITIES = {
        "Tenant", "User", "Department", "Role", "Permission",
        "Group", "Project", "Task", "Notice", "Audience",
        "ApprovalDocument", "ApprovalStep", "ApprovalLine",
        "AttendanceRecord", "LeaveRequest", "LeaveBalance",
        "Schedule", "Resource", "Reservation", "FileMetadata",
        "Comment", "Reaction", "Tag", "ActivityLog",
        # Support NM-01 through NM-24 mapping aliases
        *[f"NM-{i:02d}" for i in range(1, 25)]
    }

    def __init__(self, threshold_ratio: float = DEFAULT_THRESHOLD_RATIO):
        if not isinstance(threshold_ratio, (int, float)) or math.isnan(threshold_ratio) or math.isinf(threshold_ratio):
            raise ValueError(f"Invalid threshold_ratio: {threshold_ratio}")
        if threshold_ratio <= 0.0 or threshold_ratio > 1.0:
            raise ValueError(f"threshold_ratio must be between 0.0 and 1.0, got {threshold_ratio}")
        self.threshold_ratio = float(threshold_ratio)

    def evaluate(
        self,
        entity_type: str,
        eligible_graph_node_count: Any,
        candidate_delete_count: Any,
        candidate_keys: Optional[List[Any]] = None,
        tenant_id: Optional[Any] = None,
        extraction_complete: bool = True,
        dry_run: bool = False
    ) -> CircuitBreakerResult:
        """
        Strictly validates inputs and evaluates deletion candidates against safety thresholds.
        """
        # --- 1. STRICT INPUT VALIDATION ---

        # 1.1 Validate Entity Type
        if not isinstance(entity_type, str) or not entity_type.strip():
            return CircuitBreakerResult(
                allowed=False,
                decision="ABORT",
                reason="INVALID_INPUT_EMPTY_ENTITY_TYPE",
                eligible_graph_node_count=0,
                candidate_delete_count=0,
                max_allowed_delete_count=0,
                entity_type=str(entity_type),
                dry_run=dry_run,
                tenant_id=tenant_id if isinstance(tenant_id, int) else None
            )

        if entity_type not in self.APPROVED_ENTITIES:
            return CircuitBreakerResult(
                allowed=False,
                decision="ABORT",
                reason="INVALID_INPUT_UNAPPROVED_ENTITY_TYPE",
                eligible_graph_node_count=0,
                candidate_delete_count=0,
                max_allowed_delete_count=0,
                entity_type=entity_type,
                dry_run=dry_run,
                tenant_id=tenant_id if isinstance(tenant_id, int) else None
            )

        # 1.2 Validate Numeric Types (NaN, Inf, non-numeric)
        if not isinstance(eligible_graph_node_count, (int, float)) or isinstance(eligible_graph_node_count, bool):
            return CircuitBreakerResult(
                allowed=False,
                decision="ABORT",
                reason="INVALID_INPUT_NON_NUMERIC_POPULATION",
                eligible_graph_node_count=0,
                candidate_delete_count=0,
                max_allowed_delete_count=0,
                entity_type=entity_type,
                dry_run=dry_run
            )

        if not isinstance(candidate_delete_count, (int, float)) or isinstance(candidate_delete_count, bool):
            return CircuitBreakerResult(
                allowed=False,
                decision="ABORT",
                reason="INVALID_INPUT_NON_NUMERIC_CANDIDATES",
                eligible_graph_node_count=0,
                candidate_delete_count=0,
                max_allowed_delete_count=0,
                entity_type=entity_type,
                dry_run=dry_run
            )

        if math.isnan(eligible_graph_node_count) or math.isinf(eligible_graph_node_count):
            return CircuitBreakerResult(
                allowed=False,
                decision="ABORT",
                reason="INVALID_INPUT_NAN_INF_POPULATION",
                eligible_graph_node_count=0,
                candidate_delete_count=0,
                max_allowed_delete_count=0,
                entity_type=entity_type,
                dry_run=dry_run
            )

        if math.isnan(candidate_delete_count) or math.isinf(candidate_delete_count):
            return CircuitBreakerResult(
                allowed=False,
                decision="ABORT",
                reason="INVALID_INPUT_NAN_INF_CANDIDATES",
                eligible_graph_node_count=0,
                candidate_delete_count=0,
                max_allowed_delete_count=0,
                entity_type=entity_type,
                dry_run=dry_run
            )

        pop_count = int(eligible_graph_node_count)
        cand_count = int(candidate_delete_count)

        # 1.3 Validate Negative Values
        if pop_count < 0:
            return CircuitBreakerResult(
                allowed=False,
                decision="ABORT",
                reason="INVALID_INPUT_NEGATIVE_POPULATION",
                eligible_graph_node_count=pop_count,
                candidate_delete_count=cand_count,
                max_allowed_delete_count=0,
                entity_type=entity_type,
                dry_run=dry_run
            )

        if cand_count < 0:
            return CircuitBreakerResult(
                allowed=False,
                decision="ABORT",
                reason="INVALID_INPUT_NEGATIVE_CANDIDATES",
                eligible_graph_node_count=pop_count,
                candidate_delete_count=cand_count,
                max_allowed_delete_count=0,
                entity_type=entity_type,
                dry_run=dry_run
            )

        # 1.4 Validate Zero-Population or Candidates <= Population
        if pop_count == 0 and cand_count > 0:
            return CircuitBreakerResult(
                allowed=False,
                decision="ABORT",
                reason="ZERO_POP_NONZERO_DELETE",
                eligible_graph_node_count=0,
                candidate_delete_count=cand_count,
                max_allowed_delete_count=0,
                entity_type=entity_type,
                dry_run=dry_run
            )

        if pop_count > 0 and cand_count > pop_count:
            return CircuitBreakerResult(
                allowed=False,
                decision="ABORT",
                reason="INVALID_INPUT_CANDIDATES_EXCEED_POPULATION",
                eligible_graph_node_count=pop_count,
                candidate_delete_count=cand_count,
                max_allowed_delete_count=0,
                entity_type=entity_type,
                dry_run=dry_run
            )

        # 1.5 Validate Candidate Keys Uniqueness & Count Consistency
        if candidate_keys is not None:
            if not isinstance(candidate_keys, list):
                return CircuitBreakerResult(
                    allowed=False,
                    decision="ABORT",
                    reason="INVALID_INPUT_CANDIDATE_KEYS_NOT_LIST",
                    eligible_graph_node_count=pop_count,
                    candidate_delete_count=cand_count,
                    max_allowed_delete_count=0,
                    entity_type=entity_type,
                    dry_run=dry_run
                )
            if len(candidate_keys) != len(set(candidate_keys)):
                return CircuitBreakerResult(
                    allowed=False,
                    decision="ABORT",
                    reason="INVALID_INPUT_DUPLICATE_CANDIDATE_KEYS",
                    eligible_graph_node_count=pop_count,
                    candidate_delete_count=cand_count,
                    max_allowed_delete_count=0,
                    entity_type=entity_type,
                    dry_run=dry_run
                )
            if len(candidate_keys) != cand_count:
                return CircuitBreakerResult(
                    allowed=False,
                    decision="ABORT",
                    reason="INVALID_INPUT_CANDIDATE_COUNT_MISMATCH",
                    eligible_graph_node_count=pop_count,
                    candidate_delete_count=cand_count,
                    max_allowed_delete_count=0,
                    entity_type=entity_type,
                    dry_run=dry_run
                )

        # 1.6 Validate Tenant Scope
        parsed_tenant_id = None
        if tenant_id is not None:
            if not isinstance(tenant_id, int) or isinstance(tenant_id, bool) or tenant_id <= 0:
                return CircuitBreakerResult(
                    allowed=False,
                    decision="ABORT",
                    reason="INVALID_INPUT_TENANT_ID",
                    eligible_graph_node_count=pop_count,
                    candidate_delete_count=cand_count,
                    max_allowed_delete_count=0,
                    entity_type=entity_type,
                    dry_run=dry_run
                )
            parsed_tenant_id = tenant_id

        # --- 2. EXTRACTION COMPLETENESS CHECK ---
        if not extraction_complete:
            return CircuitBreakerResult(
                allowed=False,
                decision="ABORT",
                reason="INCOMPLETE_EXTRACTION",
                eligible_graph_node_count=pop_count,
                candidate_delete_count=cand_count,
                max_allowed_delete_count=0,
                entity_type=entity_type,
                dry_run=dry_run,
                tenant_id=parsed_tenant_id
            )

        # --- 3. PROTECTED ENTITY CHECK (Tenant nodes can never be auto-deleted) ---
        if entity_type in self.PROTECTED_ENTITIES:
            if cand_count > 0:
                return CircuitBreakerResult(
                    allowed=False,
                    decision="ABORT",
                    reason="PROTECTED_ENTITY_TYPE",
                    eligible_graph_node_count=pop_count,
                    candidate_delete_count=cand_count,
                    max_allowed_delete_count=0,
                    entity_type=entity_type,
                    dry_run=dry_run,
                    tenant_id=parsed_tenant_id
                )
            else:
                return CircuitBreakerResult(
                    allowed=True,
                    decision="ALLOW",
                    reason="NO_OP_PROTECTED_ENTITY",
                    eligible_graph_node_count=pop_count,
                    candidate_delete_count=0,
                    max_allowed_delete_count=0,
                    entity_type=entity_type,
                    dry_run=dry_run,
                    tenant_id=parsed_tenant_id
                )

        # --- 4. ZERO-POPULATION HANDLING ---
        if pop_count == 0:
            return CircuitBreakerResult(
                allowed=True,
                decision="ALLOW",
                reason="NO_OP_ZERO_POP",
                eligible_graph_node_count=0,
                candidate_delete_count=0,
                max_allowed_delete_count=0,
                entity_type=entity_type,
                dry_run=dry_run,
                tenant_id=parsed_tenant_id
            )

        # --- 5. THRESHOLD CALCULATION & EVALUATION ---
        max_allowed = math.floor(pop_count * self.threshold_ratio)

        if cand_count <= max_allowed:
            return CircuitBreakerResult(
                allowed=True,
                decision="ALLOW",
                reason="WITHIN_THRESHOLD",
                eligible_graph_node_count=pop_count,
                candidate_delete_count=cand_count,
                max_allowed_delete_count=max_allowed,
                entity_type=entity_type,
                dry_run=dry_run,
                tenant_id=parsed_tenant_id
            )
        else:
            # Breach detected!
            if dry_run:
                return CircuitBreakerResult(
                    allowed=False,
                    decision="SIMULATED_TRIP",
                    reason="THRESHOLD_EXCEEDED_DRY_RUN",
                    eligible_graph_node_count=pop_count,
                    candidate_delete_count=cand_count,
                    max_allowed_delete_count=max_allowed,
                    entity_type=entity_type,
                    dry_run=True,
                    tenant_id=parsed_tenant_id
                )
            else:
                return CircuitBreakerResult(
                    allowed=False,
                    decision="ABORT",
                    reason="THRESHOLD_EXCEEDED",
                    eligible_graph_node_count=pop_count,
                    candidate_delete_count=cand_count,
                    max_allowed_delete_count=max_allowed,
                    entity_type=entity_type,
                    dry_run=False,
                    tenant_id=parsed_tenant_id
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
        tripped_reason = None

        for req in batch_requests:
            res = self.evaluate(
                entity_type=req.get("entity_type", "Unknown"),
                eligible_graph_node_count=req.get("eligible_graph_node_count", 0),
                candidate_delete_count=req.get("candidate_delete_count", 0),
                candidate_keys=req.get("candidate_keys"),
                tenant_id=req.get("tenant_id"),
                extraction_complete=req.get("extraction_complete", True),
                dry_run=dry_run
            )
            results.append(res)
            if not res.allowed:
                batch_allowed = False
                if tripped_entity is None:
                    tripped_entity = res.entity_type
                    tripped_reason = res.reason

        return {
            "batch_allowed": batch_allowed,
            "overall_decision": "ALLOW" if batch_allowed else ("SIMULATED_TRIP" if dry_run else "BATCH_ABORT"),
            "tripped_entity": tripped_entity,
            "tripped_reason": tripped_reason,
            "results": results
        }
