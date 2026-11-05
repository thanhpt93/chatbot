# 23 – Phase 1.1 Data Classification & Scope Reconciliation
## Groupware AI Chatbot Project – Six-Tier Governance Register & Privacy Baseline

> [!NOTE]
> This document resolves the conflicting classification counts between the preliminary schema inventory and the Data Classification document, providing an authoritative table-by-table classification across all 228 base tables.

---

## 1. Resolution of Classification Tier Discrepancy

### 1.1 The Numerical Conflict
- Preliminary Inventory classification reported: Tier 1 (23), Tier 2 (125), Tier 3 (7), Tier 4 (11), Tier 5 (39), Tier 6 (23). Total = 228.
- Previous Data Classification document reported: Tier 1 (16), Tier 2 (147), Tier 3 (8), Tier 4 (11), Tier 5 (23), Tier 6 (23). Total = 228.

### 1.2 Root Cause of the Discrepancy
The discrepancy arose from different definitions of Tier 1 vs Tier 2 and Tier 2 vs Tier 5:
1. **Tier 1 Definition**: The preliminary inventory included all user-facing domain entities in Tier 1 (23 tables, including `kanban_columns`, `sprints`, `audiences`). The Data Classification report restricted Tier 1 strictly to the 16 core transaction anchors.
2. **Tier 2 Purification**: The preliminary inventory categorized 16 technical logging/migration tables under Tier 5, whereas early drafts left them in Tier 2.

### 1.3 Reconciled Authoritative Six-Tier Architecture

| Data Tier | Scope & Business Description | Physical Table Count | Graph Modeling Boundary & Decision |
|---|---|---|---|
| **Tier 1: Core Business Entities** | Primary business anchors: Users, Departments, Projects, Tasks, Approvals, Notices, Talk Posts, Assets, Calendar. | **16 tables** | **INCLUDE IN FULL** (Primary Nodes & Relationships) |
| **Tier 2: Supporting & Reference Data**| True business taxonomies, sprint iterations, kanban stages, meeting rooms, workflow templates, file metadata. *(Purified: technical tables moved to Tier 5)*. | **147 tables** | **INCLUDE (Metadata / Taxonomy)** (Active business tables included; empty business tables deferred) |
| **Tier 3: Security & Access Control** | Roles, permissions, role-permission mappings, direct user permission overrides, tenant memberships. | **8 tables** | **INCLUDE (Security Context)** (Dedicated nodes / security properties for query-time access control filtering) |
| **Tier 4: Event & Transactional Data** | Pre-calculated daily attendance summaries, chat stream metadata, read receipts. | **11 tables** | **PARTIALLY INCLUDE** (Aggregate facts included in Neo4j; `chat_messages` indexed in Vector Store for semantic RAG) |
| **Tier 5: Operational & System Telemetry** | High-volume server logs, error queues, raw biometric clock swipes, device tokens, Hangfire queues, migrations. | **23 tables** | **STRICTLY EXCLUDE** (High churn, technical plumbing with zero graph query value) |
| **Tier 6: Historical & Maintenance Backups**| Purged records in `_backup_cleanup_20261005`, `maintenance_backup`, user contract history snapshots. | **23 tables** | **STRICTLY EXCLUDE / MASKED** (Archived maintenance snapshots excluded; employment contracts masked) |
| **TOTAL BASE TABLES** | Exhaustive coverage across all PostgreSQL schemas | **228 tables** | Complete, mathematically verified accounting |

---

## 2. Table-by-Table Classification Register for Disputed & Sensitive Tables

| Table Name | Schema | Tier | Personal Data? | Sensitive / Financial? | Graph Scope Decision | Vector DB Scope | Redaction & Security Policy |
|---|---|---|---|---|---|---|---|
| `users` | `public` | Tier 1 | YES | YES (Password) | **INCLUDE** | Exclude | **Redact** `password_hash`, `email_verification_token`. |
| `user_profiles` | `public` | Tier 1 | YES | NO | **INCLUDE** | Metadata | Mask personal mobile/fax numbers if restricted by policy. |
| `user_contract_histories`| `public` | Tier 6 | YES | YES (Salary) | **PARTIAL / MASKED**| Exclude | **STRICTLY REDACT** all financial fields (`salary_amount`, `base_salary`, bonuses, bank accounts). |
| `attendance_face_events` | `public` | Tier 5 | YES | YES (Biometrics) | **STRICTLY EXCLUDE**| Exclude | Biometric face hashes must never leave PostgreSQL. |
| `attendance_daily_records`| `public` | Tier 4 | YES | NO | **INCLUDE (Extended)**| Exclude | Daily aggregate attendance facts (working minutes, status). |
| `files` | `public` | Tier 2 | NO | NO | **INCLUDE (Metadata)**| Document RAG | Only ingest metadata (`original_name`, `size_bytes`, `content_type`). No storage paths. |
| `chat_messages` | `public` | Tier 4 | YES | NO | **EXCLUDE (Option A)**| **PRIMARY VECTOR RAG**| Ingested into Vector Database for semantic search. |
| `chat_conversations` | `public` | Tier 1 | NO | NO | **INCLUDE** | Channel Metadata | Channel and room topology modeled in Neo4j. |
| `system_logs` | `public` | Tier 5 | NO | NO | **STRICTLY EXCLUDE**| Exclude | High churn operational log (729,544 rows). Zero graph value. |
| `error_tracking_outbox` | `public` | Tier 5 | NO | NO | **STRICTLY EXCLUDE**| Exclude | Outbox event queue (201,186 rows). Zero graph value. |
| `schema_migrations` | `public` | Tier 5 | NO | NO | **STRICTLY EXCLUDE**| Exclude | DDL migration history. Zero graph value. |
| `hangfire.*` (12 tables) | `hangfire` | Tier 5 | NO | NO | **STRICTLY EXCLUDE**| Exclude | Scheduler queues, locks, server states. |
| `_backup_*` (17 tables) | backup | Tier 6 | YES | YES | **STRICTLY EXCLUDE**| Exclude | Historical archive snapshots from Oct 5, 2026 cleanup. |
| `maintenance_backup.*` | backup | Tier 6 | YES | YES | **STRICTLY EXCLUDE**| Exclude | Maintenance backup table (`users_backup`). |

---

## 3. Strict HR Privacy & Compensation Masking Policy

The table `user_contract_histories` (457 rows) contains valuable employment tenure history but also highly sensitive compensation records. It is governed by a **Strict Partial / Masked Inclusion Policy**:

### A. Permitted Attributes for Knowledge Graph Ingestion:
- `id`: Unique contract record identifier.
- `user_id`: Foreign reference to `(:User)`.
- `contract_type`: Employment type (e.g., `full_time`, `probation`, `contractor`).
- `start_date`: Contract commencement date.
- `end_date`: Contract conclusion date.
- `status`: Active or completed status.
- `created_at`: Creation timestamp.

### B. Prohibited Attributes (STRICT FULL REDACTION / MUST NEVER BE INGESTED):
- `salary_amount`: **PROHIBITED (EXCLUDE)**.
- `base_salary`: **PROHIBITED (EXCLUDE)**.
- `allowances`: **PROHIBITED (EXCLUDE)**.
- `bonus`: **PROHIBITED (EXCLUDE)**.
- `insurance_salary`: **PROHIBITED (EXCLUDE)**.
- `tax_deduction_dependents`: **PROHIBITED (EXCLUDE)**.
- `bank_account_number`: **PROHIBITED (EXCLUDE)**.
