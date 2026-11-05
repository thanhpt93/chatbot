# Phase 1.2.3.1 Circuit Breaker & Hard-Delete Safety Report
## Strict Input Validation & Scoped Approval Guard (WP3)

**Execution Date**: 2026-11-05  
**Circuit Breaker Suite**: `25/25 PASS` (`CB-01` to `CB-25`)  
**Hard-Delete Approval Suite**: `12/12 PASS` (`HD-01` to `HD-12`)  

---

## 1. Circuit Breaker Input Validation Hardening (DEF-P1231-04)

All edge cases, non-numeric values, negative counts, NaN, Infinity, excessive candidate counts, invalid entity labels, and duplicate candidate keys are rejected before any threshold calculations:
- Negative candidates (`cand=-1`): Rejected with `INVALID_INPUT_NEGATIVE_CANDIDATES`.
- Negative population (`pop=-100`): Rejected with `INVALID_INPUT_NEGATIVE_POPULATION`.
- Candidates exceeding population (`cand=150, pop=100`): Rejected with `INVALID_INPUT_CANDIDATES_EXCEED_POPULATION`.
- NaN / Infinity: Rejected with `INVALID_INPUT_NAN_INF_*`.
- Unapproved labels: Rejected with `INVALID_INPUT_UNAPPROVED_ENTITY_TYPE`.
- Duplicate keys: Rejected with `INVALID_INPUT_DUPLICATE_CANDIDATE_KEYS`.
- Protected entities (`Tenant`, `NM-01`): Auto-delete blocked (`PROTECTED_ENTITY_TYPE`).

---

## 2. Scoped Hard-Delete Approval Guard (DEF-P1231-05)

Destructive deletion operations are disabled by default. When enabled, deletion plans require a valid, HMAC-SHA256 signed `ApprovalToken` bound strictly to:
- Specific `batch_id`
- Specific `tenant_id`
- Specific `entity_type`
- Maximum approved deletion count
- Unexpired timestamp
- Unrevoked status
