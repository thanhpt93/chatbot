# 19 – Phase 1.1 Database Schema & Data Dictionary Reconciliation
## Groupware AI Chatbot Project – Baseline Verification & Discrepancy Resolution

> [!NOTE]
> This document resolves all mathematical and structural discrepancies across the physical PostgreSQL database (`inf_nffice`), the Schema Inventory, and the Data Dictionary.

---

## 1. Database Object & Row Count Verification

Exhaustive verification against PostgreSQL system catalogs (`information_schema.tables`) establishes the exact baseline:

| Schema Name | Base Tables | Views | Total Objects | Physical Rows | Row Percentage | Primary Business / Technical Purpose |
|---|---|---|---|---|---|---|
| `public` | 198 | 9 | 207 | 1,478,137 | 99.85% | Core enterprise applications, user profiles, projects, tickets, communication, telemetry. |
| `hangfire` | 12 | 0 | 12 | 1,672 | 0.11% | Background job queues, locks, states, and scheduler execution records. |
| `_backup_cleanup_20261005` | 17 | 0 | 17 | 462 | 0.03% | Purged historical snapshots archived during maintenance on October 5, 2026. |
| `maintenance_backup` | 1 | 0 | 1 | 61 | < 0.01% | System maintenance backup snapshot (`maintenance_backup.users_backup`). |
| **TOTAL** | **228** | **9** | **237** | **1,480,332** | **100.00%** | Full physical database accounting |

### Verification of Physical Rows by Architectural Domain
- **Core Business Transactional Data**: **121,027 rows** (8.18%) across operational tables (`users`, `user_profiles`, `projects`, `tickets`, `approval_requests`, `schedule_events`, `notices`, `talk_posts`, `assets`, `files`, `chat_conversations`, `chat_conversation_members`, `attendance_daily_records`, etc.).
- **Operational & System Telemetry**: **1,357,110 rows** (91.68%) across high-churn technical log tables (`system_logs`: 729,544 rows; `error_tracking_outbox`: 201,186 rows; `attendance_face_events`: 1,415 rows; `chat_audit_log`: 23,021 rows; `telemetry_events`: 401,944 rows).
- **Background Job Plumbing**: **1,672 rows** (0.11%) in `hangfire`.
- **Archival Snapshots**: **523 rows** (0.04%) in backup schemas.

---

## 2. Data Dictionary Coverage Discrepancy Resolution

### 2.1 The Historical Discrepancy
- The earlier Acceptance Matrix claimed: *"2,019 columns across 228 base tables"*.
- The file `03_data_dictionary.md` contained 198 table sections and 2,225 column rows.
- This created a conflict: Why did the Acceptance Matrix report fewer columns (2,019) than `03_data_dictionary.md` (2,225), and why did `03_data_dictionary.md` document only 198 tables instead of 228?

### 2.2 Mathematical Evidence & Resolution
System catalog analysis (`information_schema.columns`) reveals the exact column distribution:

| Schema Name | Physical Base Tables | Documented in `03_data_dictionary.md` | Total Columns in Base Tables | Average Columns / Table | Status |
|---|---|---|---|---|---|
| `public` | 198 | 198 (100%) | **2,225** | 11.24 | Fully Documented in `03` |
| `hangfire` | 12 | 0 (0%) | **58** | 4.83 | Omitted from `03` (Infrastructure) |
| `_backup_cleanup_20261005` | 17 | 0 (0%) | **205** | 12.06 | Omitted from `03` (Archive) |
| `maintenance_backup` | 1 | 0 (0%) | **5** | 5.00 | Omitted from `03` (Archive) |
| **Total Base Tables** | **228** | **198** (86.8%) | **2,493** | **10.93** | True Base Table Column Total |
| `public` (Views) | 9 | 0 (0%) | **60** | 6.67 | Documented in Schema Inventory |
| **TOTAL DATABASE OBJECTS**| **237** | **198** | **2,553** | **10.77** | True Complete Database Column Total |

### 2.3 Findings & Resolution:
1. **The Origin of the "2,019" Claim**: The figure 2,019 was an early preliminary count that filtered out certain audit columns (`created_at`, `updated_at`, `deleted_at`) or excluded system tables before full restoration completed. It was mathematically incorrect.
2. **The True Baseline Fact**:
   - Total base tables in PostgreSQL: **228 tables**.
   - Total columns in physical base tables: **2,493 columns**.
   - Total columns in the 198 `public` base tables: **2,225 columns**.
   - Total columns across all 237 database objects (including 9 views): **2,553 columns**.
3. **Data Dictionary Coverage**: `03_data_dictionary.md` provides 100% column-level documentation for all 198 `public` domain tables (2,225 columns). The 30 non-public tables (268 columns) belong to infrastructure (`hangfire`) and historical cold backups, which are completely excluded from the Knowledge Graph. Full metadata for all 228 tables is recorded in `02_database_schema_inventory.md` and `artifacts/database-discovery/schema_inventory.json`.

---

## 3. Structural Metadata & Integrity Analysis

### 3.1 Primary Key Integrity
- **Tables with Primary Keys**: 216 of 228 base tables have explicitly defined primary keys (94.7%).
- **Tables without Primary Keys**: 12 tables lack physical primary key constraints:
  - `hangfire.aggregatedcounter`: Key-value counter aggregation table.
  - `hangfire.counter`: Raw job counter table.
  - `_backup_cleanup_20261005` tables (10 tables copied via `SELECT INTO` without constraint cloning).
- **Domain Business Tables**: 100% of core business tables in `public` have explicit primary keys (e.g. `users.id`, `projects.id`, `tickets.id`, `approval_requests.id`).

### 3.2 Foreign Key Constraints vs Domain Inferred References
- **Explicit Foreign Key Constraints**: Exactly **2 explicit FK constraints** exist in the entire database, both located in the `hangfire` schema (`hangfire.jobparameter` and `hangfire.state`).
- **Public Schema Foreign Keys**: Exactly **0 physical FK constraints** exist in `public`. All enterprise entity relationships are implicit/logical references maintained by application software logic.
