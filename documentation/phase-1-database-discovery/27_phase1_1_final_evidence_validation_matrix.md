# 27 – Phase 1.1 Final Evidence Validation Matrix
## Groupware AI Chatbot Project – Traceable Verification Audit

> [!NOTE]
> This matrix audits all technical findings, architectural decisions, and acceptance claims against tangible database evidence. It clearly distinguishes verified facts from unverified business hypotheses.

---

## 1. Traceable Evidence Verification Matrix

| # | Technical Area / Claim | Concrete Database Evidence | Validation Method | Result | Traceable Deliverable | Remaining Notes / Conditions |
|---|---|---|---|---|---|---|
| **1** | PostgreSQL Engine & Restoration | PostgreSQL 15 on port 5433 with cluster `.pgdata` (`inf_nffice`). | Restoration log & live startup verification | **PASS** | `01_database_overview.md` | Fully verified against cluster. |
| **2** | Exhaustive Physical Table Count | 228 Base Tables + 9 Views = 237 physical objects. | System catalogs (`information_schema.tables`) | **PASS** | `02`, `19` | Exact physical accounting. |
| **3** | Exact Database Row Counts | Exactly 1,480,332 physical rows across all schemas. | Automated aggregation across all 228 base tables | **PASS** | `02`, `19` | Exact physical accounting. |
| **4** | Data Dictionary Coverage | 2,493 base table columns (2,225 in `public`; 268 in hangfire/backup). | System catalogs (`information_schema.columns`) | **PASS** | `03`, `19` | 2,019 legacy claim refuted. |
| **5** | Explicit Foreign Key Discovery | Only 2 explicit FKs exist in entire database, both in `hangfire`. | System catalogs (`table_constraints`) | **PASS** | `04`, `09`, `20` | Zero FK constraints in public. |
| **6** | Stale 247 Relationship Metric | Formula defaulted empty tables (84) to 100% (163 + 84 = 247). | Discovery code inspection (`discover_relationships.py`) | **PASS** | `20_phase1_1_relationship_reconciliation.md` | Mathematical proof documented. |
| **7** | Low-Confidence 84 Reconciliation | 84 empty source tables: match % = N/A, 0 INCLUDE, 70 DEFER, 14 EXCLUDE. | Data profiling output (`relationships.json`) | **PASS** | `20_phase1_1_relationship_reconciliation.md` | Excluded from active graph. |
| **8** | Elimination of Nonexistent Columns | `projects.owner_id` does not exist; creator in `created_by_user_id`. | System catalogs (`information_schema.columns`) | **PASS** | `21`, `24` | Ownership derived from members. |
| **9** | Correct User ID Data Types | `users.id` is `integer(32,0)` (`int4`); foreign user references vary. | System catalogs (`information_schema.columns`) | **PASS** | `21`, `24` | Type diversity documented. |
| **10**| Chat & Calendar Field Names | `chat_messages.sender_user_id`; `schedule_events.user_id`. | System catalogs (`information_schema.columns`) | **PASS** | `24`, `25` | Verified against physical schema. |
| **11**| Approval Request Creator & Routing | `approval_requests.created_by_user_id`; active approver filter. | System catalogs & data profiling | **PASS** | `24`, `25` | Active approver filter validated. |
| **12**| Real Source Table Names | `project_sprints`, `approval_workflow_templates`, `talk_posts`. | System catalogs (`information_schema.tables`) | **PASS** | `21`, `24` | Replaced legacy informal names. |
| **13**| Ticket Assignment Model | Many-to-many via `ticket_assignees` junction table. | System catalogs (`information_schema.tables`) | **PASS** | `21`, `24` | Model reflects junction reality. |
| **14**| File Metadata Exposure Safety | Metadata only (`original_name`, `size_bytes`); no storage paths. | System catalogs (`files` table) | **PASS** | `21`, `24` | Safe metadata-only policy. |
| **15**| Chat Message Option A | No `ChatMessage` nodes in Neo4j; messages in Vector Store. | Architecture Decision Record (ADR-02) | **PASS** | `21`, `28` | Option A preserved. |
| **16**| Six-Tier Classification Reconciliation| Table-by-table classification across all 228 base tables. | Classification register audit | **PASS** | `23_phase1_1_data_classification_reconciliation.md`| Purified Tier 2, telemetry in 5. |
| **17**| HR Compensation Redaction | Full redaction of salary, bonus, allowances in contract history. | Data governance policy specification | **PASS** | `23_phase1_1_data_classification_reconciliation.md`| Zero salary fields in graph. |
| **18**| Multi-Tenant Isolation Strategy | Property injection (`tenant_id`), range indexing, session filter. | Tenant model specification | **PASS** | `22_phase1_1_tenant_authorization_finalization.md`| Multi-tenant design enforced. |
| **19**| RBAC Precedence Evaluation | `Direct Deny > Direct Grant > Role Grant` evaluated in code. | Static analysis of database catalogs | **PASS WITH CONDITIONS** | `22_phase1_1_tenant_authorization_finalization.md`| Labeled Unverified Hypothesis. |
| **20**| Chatbot Query Readiness | 12 business queries aligned with final graph model and Cypher. | Static Cypher syntax validation | **PASS** | `25_phase1_1_chatbot_query_readiness.md` | Aligned with canonical schema. |
