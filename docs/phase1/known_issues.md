# Phase 1 Known Issues, Architectural Decisions & Environmental Limitations

This document captures the known technical limitations, environmental constraints, architectural invariants, and domain contracts established during Phase 1 (Database Discovery & Graph Foundation) for the Groupware AI Chatbot project. Any engineer continuing into Phase 2 or maintenance must review and respect these specifications.

---

## 1. PostgreSQL Live Database Unavailability
- **Condition**: During Phase 1 execution, the local PostgreSQL instance on ports `5433` and `5432` was offline / unreachable in the automated execution environment.
- **Impact & Mitigation**:
  - Live query execution against PostgreSQL could not be executed directly in runtime pipelines.
  - Verification was completed using `artifacts/database-discovery/schema_inventory.json`, `data_profiling.json`, and isolated SQLite/in-memory synthetic fixtures that mirror PostgreSQL schema types, primary keys, and foreign keys.
- **Phase 2 Prerequisite**:
  - Prior to executing live ETL synchronization, PostgreSQL container/service must be provisioned and accessible with read-only credentials, and verified via `scripts/phase1_2/pg_readonly.py`.

---

## 2. Neo4j Live Database Unavailability
- **Condition**: Local Neo4j instance on port `7687` (Bolt protocol) was offline / unreachable in the automated test runner environment.
- **Impact & Mitigation**:
  - Cypher queries could not be executed directly against an active Neo4j graph engine.
  - Queries were verified through static AST parsing, grammar validation, and an independent Cypher simulator (`tests/phase1_2_3_1/test_cypher_engine.py`) to confirm syntactic validity, parameterized projections, and tenant filter enforcement.
- **Phase 2 Prerequisite**:
  - Live Neo4j instance (version 5.x enterprise or community) must be provisioned. Neo4j constraints defined in `documentation/phase-1-database-discovery/35_phase1_2_final_neo4j_constraints_indexes.md` must be executed and confirmed prior to initial batch ingestion.

---

## 3. Attendance Cross-Tenant Membership Resolution Contract
- **Contract Definition**:
  - Attendance records (`attendance_record`) record employee attendance. While an employee (`User`) belongs to a primary `Tenant`, users may temporarily work across sub-entities or departments.
  - **Resolution Invariant**: The graph projection of `Attendance` must link strictly to the User's authoritative `tenant_id` at the time of check-in, verified against the organizational hierarchy.
  - Cross-tenant attendance queries are strictly prohibited unless mediated by a global admin context.

---

## 4. LeaveBalance Historical Membership Contract
- **Contract Definition**:
  - `LeaveBalance` entities represent annual, sick, or special leave allocations.
  - When an employee is reassigned across departments or business units within a tenant, historical leave balances must preserve their historical tenant context and allocation period.
  - Historical leave balances must not be retroactively reassigned or aggregated across disparate tenant boundaries.

---

## 5. Audience Global/System vs. Custom/Tenant Ownership Model
- **Contract Definition**:
  - Notices and announcements target specific `Audience` groups.
  - **Dual Ownership**:
    1. **System Audiences**: Global system-wide audiences (e.g., all active employees, system announcements) have `tenant_id = NULL` or `is_system = TRUE`. They are readable by all authenticated tenants.
    2. **Tenant Audiences**: Custom audiences created by tenant administrators (e.g., specific departments, project teams) must have an explicit `tenant_id` and are strictly isolated to that tenant.
  - **Invariant**: Any query filtering on `Audience` must apply `WHERE (a.tenant_id = $tenant_id OR a.is_system = true)` to prevent data leakage.

---

## 6. Hard-Delete Circuit Breaker & Scoped Approval Guard
- **Specification (CB-01 to CB-25, HD-01 to HD-12)**:
  - In automated ETL synchronization, hard deletes (`DETACH DELETE` in Neo4j or `DELETE FROM` in relational tables) carry high risk of catastrophic data loss.
  - **Circuit Breaker Rule**:
    - If the number of detected deletions in a single batch exceeds the threshold (`MAX_DELETE_RATIO = 0.05` / 5% of existing entity count) or an absolute ceiling (`MAX_DELETE_ABSOLUTE = 100`), the ETL job aborts immediately and trips the breaker.
  - **Scoped Approval Guard**:
    - Any legitimate bulk deletion requires an explicit, cryptographically signed approval token containing the authorized operator ID, target entity type, tenant scope, and expiration timestamp.
    - Automated background synchronization jobs are never permitted to bypass this guard.

---

## 7. Soft-Delete Tombstone Semantics
- **Specification**:
  - Approved entities in PostgreSQL utilize soft-delete semantics (`deleted_at IS NOT NULL` or `is_deleted = TRUE` or `status = 'DELETED'`).
  - **Tombstone Invariant in Neo4j**:
    - In Neo4j, soft-deleted entities are marked with property `is_deleted: true` and `deleted_at: datetime()`.
    - Active business queries must include `WHERE n.is_deleted = false` or `WHERE NOT coalesce(n.is_deleted, false)`.
    - Tombstone propagation ensures that child relationships (e.g., memberships, assignments) are deactivated without severing graph provenance.

---

## 8. ChatMessage Option A Architecture Decision
- **Strict Invariant**:
  - **ChatMessage Option A is approved and permanent**: Individual `ChatMessage` nodes are **NEVER** created in Neo4j.
  - Chat message content, raw text, and vector embeddings belong strictly in the Vector Database (and source relational store).
  - Neo4j represents only high-level structural conversation topology (e.g., `Channel`, `ConversationSession`, user participation edges).
  - Graph queries must not attempt to traverse or aggregate chat message text nodes in Neo4j.

---

## 9. AST Independence & Parser Isolation
- **Design Principle**:
  - The verification harness must maintain strict independence between the query generator and the query validator.
  - Tautological testing (where the test runner uses the same regex or formatting rules as the generator) is prohibited.
  - Validation must employ an independent Abstract Syntax Tree (AST) parser to verify that all Cypher and SQL statements conform to multi-tenant isolation, parameterized inputs, and syntax grammar without relying on shared internal parser heuristics.

---

## 10. Low-Confidence Relationship Inferences (84 Untracked References)
- **Status: REQUIRES SOURCE CONFIRMATION**:
  - During Phase 1 database discovery, automated analysis identified 84 potential foreign key / junction relationships that lack explicit database constraints in the PostgreSQL schema.
  - These relationships are classified as **low-confidence** or **unconfirmed business inferences**.
  - **Rule for Phase 2**: No unconfirmed relationship may be promoted to an active Neo4j relationship type without explicit confirmation from the domain database owner or business analyst. They are tracked in `documentation/phase-1-database-discovery/06_untracked_foreign_keys_and_implicit_relationships.md`.

---

## 11. Multi-Source Tenant Validation & Parameter Isolation
- **Vulnerability Guard (Scenario Q08)**:
  - In Phase 1.2.3 investigation, an architectural vulnerability was identified where tenant filtering could be bypassed if an API caller provided a mismatched `tenant_id` parameter while referencing an entity belonging to another tenant.
  - **Mandatory Security Rule**:
    - All operational queries must derive `tenant_id` from the authenticated session context (JWT/OAuth claims), **NEVER** trust client-supplied entity parameter headers.
    - In ETL and query execution, multi-source verification confirms that the entity's stored `tenant_id` matches the session `tenant_id` before projecting or returning any node attributes.
