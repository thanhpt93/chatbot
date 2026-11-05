"""
Reconciliation Safety & Scoped Hard-Delete Approval Guard (Phase 1.2.3.1 WP3).
Enforces cryptographic and scope-bound approval tokens tied to exact batch ID,
tenant scope, entity type, and candidate counts (DEF-P1231-05).
Destructive operations remain strictly disabled by default.
"""

import hmac
import hashlib
import time
import uuid
import logging
from typing import Dict, Any, List, Optional, Tuple, Set
from dataclasses import dataclass
from .circuit_breaker import CircuitBreaker, CircuitBreakerResult

logger = logging.getLogger("reconciliation_safety")


@dataclass
class ApprovalToken:
    token_id: str
    batch_id: str
    tenant_id: int
    entity_type: str
    max_approved_deletes: int
    issued_at: float
    expires_at: float
    signature: str
    is_revoked: bool = False


class ScopedApprovalGuard:
    """
    Cryptographic and Scope-Bound Approval Guard (DEF-P1231-05).
    Ensures hard-delete operations cannot execute without an explicit,
    unexpired, unrevoked token bound to the exact tenant, batch ID,
    entity type, and approved deletion ceiling.
    """

    def __init__(self, secret_key: bytes = b"phase1_2_3_1_reconciliation_guard_key"):
        self.secret_key = secret_key
        self.revoked_tokens: Set[str] = set()

    def _compute_signature(
        self,
        token_id: str,
        batch_id: str,
        tenant_id: int,
        entity_type: str,
        max_approved_deletes: int,
        expires_at: float
    ) -> str:
        payload = f"{token_id}|{batch_id}|{tenant_id}|{entity_type}|{max_approved_deletes}|{expires_at:.4f}"
        return hmac.new(self.secret_key, payload.encode("utf-8"), hashlib.sha256).hexdigest()

    def generate_token(
        self,
        batch_id: str,
        tenant_id: int,
        entity_type: str,
        max_approved_deletes: int,
        ttl_seconds: int = 300
    ) -> ApprovalToken:
        """Issues a new cryptographic approval token bound to exact scope."""
        token_id = str(uuid.uuid4())
        now = time.time()
        expires_at = now + ttl_seconds
        sig = self._compute_signature(
            token_id=token_id,
            batch_id=batch_id,
            tenant_id=tenant_id,
            entity_type=entity_type,
            max_approved_deletes=max_approved_deletes,
            expires_at=expires_at
        )
        return ApprovalToken(
            token_id=token_id,
            batch_id=batch_id,
            tenant_id=tenant_id,
            entity_type=entity_type,
            max_approved_deletes=max_approved_deletes,
            issued_at=now,
            expires_at=expires_at,
            signature=sig
        )

    def revoke_token(self, token_id: str):
        """Revokes a previously issued approval token."""
        self.revoked_tokens.add(token_id)

    def validate_token(
        self,
        token: Optional[ApprovalToken],
        batch_id: str,
        tenant_id: int,
        entity_type: str,
        candidate_count: int
    ) -> Tuple[bool, str]:
        """Validates scope matching, cryptographic signature, expiration, and revocation."""
        if token is None:
            return False, "TOKEN_MISSING"

        if token.token_id in self.revoked_tokens or token.is_revoked:
            return False, "TOKEN_REVOKED"

        if time.time() > token.expires_at:
            return False, "TOKEN_EXPIRED"

        expected_sig = self._compute_signature(
            token_id=token.token_id,
            batch_id=token.batch_id,
            tenant_id=token.tenant_id,
            entity_type=token.entity_type,
            max_approved_deletes=token.max_approved_deletes,
            expires_at=token.expires_at
        )
        if not hmac.compare_digest(expected_sig, token.signature):
            return False, "TOKEN_SIGNATURE_INVALID"

        # Scope bindings check:
        if token.batch_id != batch_id:
            return False, f"TOKEN_BATCH_MISMATCH (expected {batch_id}, got {token.batch_id})"

        if token.tenant_id != tenant_id:
            return False, f"TOKEN_TENANT_MISMATCH (expected {tenant_id}, got {token.tenant_id})"

        if token.entity_type != entity_type:
            return False, f"TOKEN_ENTITY_TYPE_MISMATCH (expected {entity_type}, got {token.entity_type})"

        if candidate_count > token.max_approved_deletes:
            return False, f"TOKEN_COUNT_EXCEEDED (approved {token.max_approved_deletes}, candidate {candidate_count})"

        return True, "TOKEN_VALID"


class ReconciliationSafetyController:
    """
    Master safety controller enforcing that hard deletes in Neo4j:
    1. Are gated by the 5% Circuit Breaker threshold.
    2. Require an active hard_delete_enabled flag.
    3. Require a valid, unexpired, unrevoked ScopedApprovalToken matching the batch and tenant.
    4. Are fully audited in an immutable execution log.
    """

    def __init__(
        self,
        hard_delete_enabled: bool = False,
        threshold_ratio: float = 0.05,
        secret_key: bytes = b"phase1_2_3_1_reconciliation_guard_key"
    ):
        # Destructive operations are disabled by default
        self.hard_delete_enabled = hard_delete_enabled
        self.circuit_breaker = CircuitBreaker(threshold_ratio=threshold_ratio)
        self.approval_guard = ScopedApprovalGuard(secret_key=secret_key)
        self.audit_log: List[Dict[str, Any]] = []

    def request_deletion_plan(
        self,
        entity_type: str,
        eligible_graph_node_count: int,
        candidate_delete_ids: List[Any],
        batch_id: Optional[str] = None,
        tenant_id: Optional[int] = None,
        approval_token: Optional[ApprovalToken] = None,
        extraction_complete: bool = True,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Plans, validates, and gates deletion execution.
        """
        candidate_count = len(candidate_delete_ids) if isinstance(candidate_delete_ids, list) else 0

        # Step 1: Circuit Breaker Evaluation (with strict input validation)
        cb_res = self.circuit_breaker.evaluate(
            entity_type=entity_type,
            eligible_graph_node_count=eligible_graph_node_count,
            candidate_delete_count=candidate_count,
            candidate_keys=candidate_delete_ids if isinstance(candidate_delete_ids, list) else None,
            tenant_id=tenant_id,
            extraction_complete=extraction_complete,
            dry_run=dry_run
        )

        can_execute = False
        execution_status = "BLOCKED"
        token_valid = False
        token_reason = "NOT_EVALUATED"

        if not cb_res.allowed:
            execution_status = f"CIRCUIT_BREAKER_{cb_res.decision}"
            can_execute = False
        elif dry_run:
            execution_status = "DRY_RUN_EVALUATED"
            can_execute = False
        elif not self.hard_delete_enabled:
            execution_status = "DISABLED_BY_SAFETY_MODE"
            can_execute = False
        else:
            # Circuit breaker passed, not dry run, hard_delete_enabled is True.
            # Must validate Scoped Approval Token!
            if batch_id is None or tenant_id is None:
                execution_status = "MISSING_BATCH_OR_TENANT_SCOPE"
                can_execute = False
            else:
                token_valid, token_reason = self.approval_guard.validate_token(
                    token=approval_token,
                    batch_id=batch_id,
                    tenant_id=tenant_id,
                    entity_type=entity_type,
                    candidate_count=candidate_count
                )
                if token_valid:
                    execution_status = "AUTHORIZED"
                    can_execute = True
                else:
                    execution_status = f"APPROVAL_GUARD_DENIED_{token_reason}"
                    can_execute = False

        record = {
            "batch_id": batch_id,
            "tenant_id": tenant_id,
            "entity_type": entity_type,
            "eligible_graph_node_count": eligible_graph_node_count,
            "candidate_count": candidate_count,
            "max_allowed": cb_res.max_allowed_delete_count,
            "cb_decision": cb_res.decision,
            "cb_reason": cb_res.reason,
            "token_valid": token_valid,
            "token_reason": token_reason,
            "can_execute": can_execute,
            "execution_status": execution_status,
            "dry_run": dry_run
        }
        self.audit_log.append(record)
        return record
