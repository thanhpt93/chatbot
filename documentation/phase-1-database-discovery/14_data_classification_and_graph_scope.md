# 13 / 14 – Data Classification & Graph Scope Architecture
## Groupware AI Chatbot Project – Phase 1: Canonical Baseline

> [!NOTE]
> This document establishes the **authoritative Six-Tier Data Classification Register**, enforces privacy, PII protection, and masking rules, resolves disputed tables, and sets explicit boundaries for Phase 2 Neo4j Knowledge Graph modeling.
>
> *(Both `13_data_classification_and_graph_scope.md` and `14_data_classification_and_graph_scope.md` represent the identical, synchronized canonical deliverable to preserve legacy cross-references).*

---

## 1. Six-Tier Data Classification Architecture

All 228 physical base tables in the PostgreSQL database are classified into six structural tiers:

| Data Tier | Scope & Description | Table Count | Graph Modeling Boundary & Strategy |
|---|---|---|---|
| **Tier 1: Core Business Data** | Central enterprise entities: Users, Departments, Projects, Tasks, Approvals, Assets, Notices, Posts, Schedule Events. | 16 tables | **INCLUDE IN FULL** (Primary Nodes & Relationships in Neo4j) |
| **Tier 2: Supporting & Reference Data** | True business taxonomies, sprint iterations, kanban stages, meeting rooms, workflow templates, file metadata. *(Purified: technical tables moved to Tier 5)*. | 147 tables | **INCLUDE (Metadata / Taxonomy)** (Active business tables included; empty business tables deferred) |
| **Tier 3: Security & Access Control** | Roles, permissions, role-permission links, direct overrides, tenant memberships. | 8 tables | **INCLUDE (Security Context)** (Dedicated nodes / security properties for query-time access control filtering) |
| **Tier 4: Event & Transactional Data** | Pre-calculated daily attendance summaries, chat stream metadata, read receipts. | 11 tables | **PARTIALLY INCLUDE** (Aggregate facts included in Neo4j; `chat_messages` indexed in Vector Store for semantic RAG) |
| **Tier 5: Operational & System Telemetry** | High-volume server logs, error queues, raw biometric clock swipes, device tokens, Hangfire queues, migrations. | 23 tables | **STRICTLY EXCLUDE** (High churn, technical plumbing with zero graph query value) |
| **Tier 6: Historical & Maintenance Backups** | Purged records in `_backup_cleanup_20261005`, `maintenance_backup`, user contract history snapshots. | 23 tables | **STRICTLY EXCLUDE / MASKED** (Archived maintenance snapshots excluded; employment contracts masked) |
| **TOTAL BASE TABLES** | Exhaustive coverage across all PostgreSQL schemas | **228 tables** | Complete, mathematically verified accounting |

---

## 2. Refined Tier 2 Purification & Technical Separation

In accordance with architectural review, Tier 2 has been purified to contain **strictly business-supporting data**. The following technical, infrastructure, and operational tables previously conflated with Tier 2 are authoritatively reclassified into Tier 5 (Operational / Telemetry) and **strictly excluded from the Knowledge Graph**:

1. `schema_migrations`: DDL schema migration history $ightarrow$ **Tier 5 (EXCLUDE)**.
2. `license_audit_events`: Software licensing audit events $ightarrow$ **Tier 5 (EXCLUDE)**.
3. `license_runtime_states`: Deployment license leases $ightarrow$ **Tier 5 (EXCLUDE)**.
4. `login_qr_challenges`: Ephemeral mobile QR authentication sessions $ightarrow$ **Tier 5 (EXCLUDE)**.
5. `server_resource_nodes`: Cluster hardware telemetry $ightarrow$ **Tier 5 (EXCLUDE)**.
6. `notification_device_registrations`: Mobile push device tokens $ightarrow$ **Tier 5 (EXCLUDE)**.

---

## 3. Tier 6 HR Exception Policy: `user_contract_histories`

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
- `bank_name`: **PROHIBITED (EXCLUDE)**.

---

## 4. Privacy, PII & Security Governance Rules

To protect corporate confidential and personal data, the following mandatory redactions and masking rules must be enforced during ETL prior to Graph ingestion:

1. **Authentication Credentials & Tokens**:
   - `users.password_hash`: **FULL REDACTION** (Do not load into Graph).
   - `users.email_verification_token`: **FULL REDACTION**.
   - `user_sessions.token`: **FULL REDACTION** (Table excluded).
2. **Biometric & Sensor Telemetry**:
   - `attendance_face_events.face_template_hash`: **FULL REDACTION** (Table excluded).
   - `attendance_face_events.sensor_metadata`: **FULL REDACTION**.
3. **Sensitive HR & Financial Data**:
   - `user_contract_histories.salary_amount`: **FULL REDACTION**.
   - `user_profiles.tax_code`: **MASK** (Format: `XXX-XXX-****`).
   - `user_profiles.birth_date`: **MASK YEAR** (Redact birth year; retain month and day for birthday greetings).
   - `user_profiles.address`: **MASK STREET** (Retain city/district; redact street address).
   - `user_profiles.phone`: **MASK** (Format: `***-***-1234`).
