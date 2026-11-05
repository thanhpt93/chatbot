# 20 – Phase 1.1 Relationship Master Inventory & Metrics Reconciliation
## Groupware AI Chatbot Project – Referential Audit & Stale Metric Resolution

> [!IMPORTANT]
> **Audit Objective**:
> This document resolves the conflicting relationship metrics between early discovery drafts and the authoritative Relationship Master Inventory. It provides the exact mathematical proof resolving the stale *"247 of 276 relationships have 100% match"* claim, audits all 278 discovered relationships, and solidifies the 84 Low-Confidence relationships.

---

## 1. Forensic Resolution of the Stale "247" Metric

### 1.1 The Stale Metric Conflict
- Early discovery documents (such as `07_data_quality_report.md`) stated: *"247 of 276 inferred relationships had 100% data match"*.
- However, the corrected Relationship Master Inventory (`12_relationship_master_inventory.md`) identified only **163 High Confidence** relationships, **28 Medium Confidence**, **1 Zero Match**, and **84 Low Confidence**.
- How could 247 relationships have 100% match if only 163 were High Confidence?

### 1.2 Mathematical Proof & Discovery Code Analysis
Inspection of the original automated relationship profiling script (`scripts/database-discovery/discover_relationships.py` and `artifacts/database-discovery/relationships.json`) reveals the exact line of code responsible:

```python
# From legacy discover_relationships.py:
if source_distinct_count == 0:
    match_rate = 100.0  # Erroneous default assigned to empty tables!
else:
    match_rate = (matched_distinct_count / source_distinct_count) * 100.0
```

Because 84 candidate relationship pairs originated from **completely empty tables** (`source_distinct_count == 0`), the discovery script defaulted their match rate to `100.0%`!

### 1.3 Exact Mathematical Reconciliation:
$$	ext{Populated Tables with 100\% Match (High Confidence)} = 163$$
$$	ext{Empty Source Tables Erroneously Given 100\% Match} = 84$$
$$\mathbf{163 + 84 = 247}$$

- **Authoritative Correction**: Zero observations cannot be claimed as a 100% match. For all 84 relationships where `source_distinct_count == 0`, the match rate is strictly corrected to **`N/A`** (Not Applicable / Undefined).
- **True Inferred Relationships Breakdown**:
  - **High Confidence (100.0% match, source > 0)**: **163**
  - **Medium Confidence (16.95% to 99.19% match, source > 0)**: **28**
  - **Low Confidence (source = 0, match % = N/A)**: **84**
  - **Zero Match / Invalid (0.0% match, source > 0)**: **1** (`attendance_ingest_events.user_id`)
  - **TOTAL INFERRED RELATIONSHIPS**: **276**
- Adding the **2 Explicit Foreign Keys** in the `hangfire` schema yields the grand total:
  $$\mathbf{276 	ext{ inferred}} + \mathbf{2 	ext{ explicit FK}} = \mathbf{278 	ext{ Total Relationships}}$$

---

## 2. Reconciled Relationship Master Summary

| Category | Relationship Count | Match Rate Range | Root Cause / Evidence Source | Graph Modeling Decision |
|---|---|---|---|---|
| **Explicit Foreign Keys** | 2 | 100.0% | Database constraints in `hangfire` schema (`jobparameter`, `state`). | **STRICTLY EXCLUDE** (Hangfire infrastructure) |
| **High Confidence Inferred** | 163 | 100.0% | Fully verified referential integrity across populated active business tables. | **INCLUDE** (Operational & Semantic Graph Edges) |
| **Medium Confidence Inferred** | 28 | 16.95% - 99.19% | Partial matches caused by October 5, 2026 administrative cleanup into `_backup_cleanup_20261005`. | **INCLUDE WITH DEFENSIVE ETL** (`OPTIONAL MATCH` / Null checking) |
| **Low Confidence Inferred** | 84 | **N/A** (0 source rows) | Empty candidate tables in development database (e.g. `audit_logs`, `broadcasts`). | **0 INCLUDE / 70 DEFER / 14 EXCLUDE** |
| **Invalid / Zero Match** | 1 | 0.0% | `attendance_ingest_events.user_id -> users.id` (Stale raw telemetry queue). | **STRICTLY EXCLUDE** |
| **TOTAL DISCOVERED** | **278** | -- | Exhaustive profiling of all candidate references | Complete mathematical accounting |

---

## 3. Audit of the 84 Low-Confidence Relationships

The 84 relationships originating from empty tables are rigorously partitioned to prevent phantom graph edges from entering Phase 2:

1. **70 Deferred Relationships (`DEFER (SCHEMA-ONLY CANDIDATE)`)**:
   - Valid business domain tables that currently contain 0 rows in the development database (e.g., `bulletin_boards`, `form_templates`, `e_signatures`, `surveys`, `event_calendars`).
   - *Policy*: Do not create graph edges in Phase 2 initial load. Retain schema mapping contracts in mapping registry for future ETL activation when business data is generated.
2. **14 Excluded Relationships (`EXCLUDE (SCHEMA-ONLY CANDIDATE)`)**:
   - Technical, operational logging, or ephemeral tables (e.g., `login_history_archives`, `api_token_traces`, `outbox_deadletter_events`).
   - *Policy*: Permanently excluded from Knowledge Graph ingestion.

---

## 4. Verification of 6 Additional Core Business References (R-01 to R-06)

In addition to the 278 discovered relationships, 6 critical business references were verified through direct column profiling:

| ID | Source Table & Column | Target Table & Column | Source Type | Target Type | Distinct IDs | Match Rate | Verified Semantics & Target Graph Edge |
|---|---|---|---|---|---|---|---|
| **R-01** | `projects.created_by_user_id` | `users.id` | `bigint` | `integer` | 20 | 90.00% | Project creator identity -> `(:Project)-[:CREATED_BY]->(:User)` |
| **R-02** | `approval_requests.created_by_user_id` | `users.id` | `integer` | `integer` | 318 | 99.69% | Approval request requester -> `(:ApprovalRequest)-[:CREATED_BY]->(:User)` |
| **R-03** | `departments.manager_user_id` | `users.id` | `integer` | `integer` | 18 | 100.00% | Department organizational head -> `(:User)-[:MANAGES]->(:Department)` |
| **R-04** | `tickets.created_by_user_id` | `users.id` | `bigint` | `integer` | 30 | 93.33% | Ticket creator identity -> `(:Ticket)-[:CREATED_BY]->(:User)` |
| **R-05** | `chat_messages.sender_user_id` | `users.id` | `integer` | `integer` | 130 | 90.77% | Message author metadata -> Vector DB retrieval metadata |
| **R-06** | `assets.assigned_user_id` | `users.id` | `integer` | `integer` | 202 | 100.00% | Asset custodian -> `(:Asset)-[:ASSIGNED_TO]->(:User)` |

*(Note on R-06: Verified column is `assigned_user_id`. The column `current_holder_id` does not exist).*
