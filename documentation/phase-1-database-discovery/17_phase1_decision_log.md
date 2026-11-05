# 17 – Phase 1 Architectural Decision Log (ADR)
## Groupware AI Chatbot Project – Database Discovery & Graph Readiness

> [!NOTE]
> This log records all formal Architectural Decision Records (ADRs) established during Phase 1. These decisions govern data modeling, graph boundaries, security isolation, and Phase 2 ETL implementation.

---

### ADR-01: Selection of Architecture B (Hybrid Operational & Semantic Knowledge Graph)
- **Status**: **ACCEPTED & FINAL**
- **Context**: The project evaluated pure operational graph vs pure document semantic graph vs hybrid architecture.
- **Decision**: Adopt **Architecture B**. Neo4j will model both structural operational data (organizational units, roles, projects, workflows) and semantic knowledge relationships (topics, authors, cross-references).
- **Consequences**: Enables the chatbot to answer organizational queries ("Who approves IT purchases?") and contextual knowledge queries ("Which projects relate to cloud migration?") within a unified graph traversal.

---

### ADR-02: Chat Data Modeling & Task D Option A Selection
- **Status**: **ACCEPTED & FINAL**
- **Context**: Chat messages generate high transaction volume (millions of rows over time) and consist primarily of unstructured conversation streams. Modeling every message as a Neo4j node would cause graph bloat and poor traversal performance.
- **Decision**: Select **Option A**.
  - Neo4j models **ChatConversation** nodes and user memberships (`[:MEMBER_OF_CONVERSATION]`).
  - Chat message bodies, message attachments, mentions, and reactions are **excluded from Neo4j node ingestion**.
  - Chat content is ingested into a dedicated high-dimensional **Vector Store** for semantic search and RAG retrieval.
- **Consequences**: Preserves Neo4j memory and traversal performance while delivering state-of-the-art semantic search for chat history.

---

### ADR-03: Multi-Tenant Graph Isolation Strategy
- **Status**: **ACCEPTED & FINAL**
- **Context**: Groupware is designed for multi-tenancy. Neo4j Community / single-database setups require rigorous tenant isolation to prevent data leakage between organizations.
- **Decision**: Implement **Property-Level Isolation with Tenant Anchor Nodes**:
  - Every tenant-scoped node must store a mandatory `tenant_id: Integer` property.
  - Neo4j range indexes must be created on `(n.tenant_id)` for all tenant-scoped labels.
  - Every Cypher query executed by the chatbot application must inject `WHERE n.tenant_id = $current_user_tenant_id` at the query root.
- **Consequences**: Enforces strict mathematical multi-tenant separation without requiring separate database instances per tenant.

---

### ADR-04: Project Creator vs Owner Distinction
- **Status**: **ACCEPTED & FINAL**
- **Context**: Early documentation assumed `projects.owner_id` existed. Database schema analysis proved this column is nonexistent.
- **Decision**:
  - Map creator identity to `projects.created_by_user_id` -> `(:Project)-[:CREATED_BY]->(:User)`.
  - Derive project ownership from `project_members.role = 'owner'` -> `(:User)-[:MEMBER_OF_PROJECT {role: 'owner'}]->(:Project)`.
- **Consequences**: Accurately reflects enterprise reality where a project may have multiple co-owners or ownership reassigned without modifying the creator audit trail.

---

### ADR-05: Resolution of 84 Low-Confidence Relationships
- **Status**: **ACCEPTED & FINAL**
- **Context**: Profiling discovered 84 foreign reference candidates originating from empty tables (`source_distinct_count == 0`). Prior reports mistakenly labeled them as 100% match.
- **Decision**:
  - Reclassify match percentage for all 84 empty candidates strictly as **`N/A`**.
  - Assign **0 to `INCLUDE`**.
  - Assign **70 to `DEFER (SCHEMA-ONLY CANDIDATE)`** (business tables currently empty in dev data).
  - Assign **14 to `EXCLUDE (SCHEMA-ONLY CANDIDATE)`** (technical/telemetry tables).
- **Consequences**: Prevents unverified schema edges from polluting the Phase 2 Neo4j ETL pipeline while maintaining an audit trail for future data arrivals.

---

### ADR-06: RBAC Precedence Evaluation Classification
- **Status**: **ACCEPTED & FINAL**
- **Context**: The rule `Direct Deny > Direct Grant > Role Grant` was documented as fact, but no database stored procedures, triggers, or views exist to enforce it.
- **Decision**: Classify this precedence hierarchy as an **Unverified Business Rule / Hypothesis**. The application backend code must be audited before Phase 3 security enforcement is finalized.
- **Consequences**: Maintains rigorous architectural truthfulness and prevents false security assumptions.

---

### ADR-07: Deliverable Harmonization & Dual-Numbering Strategy
- **Status**: **ACCEPTED & FINAL**
- **Context**: Different phases of documentation used varying numbering conventions (e.g. `05` vs `11` for Business Entity Catalog, `13` vs `14` for Data Classification).
- **Decision**: Maintain synchronized twin files for all key deliverables so that all historical cross-references remain 100% valid.
- **Consequences**: Guarantees zero broken markdown links across the entire documentation suite.
