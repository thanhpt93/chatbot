# 26 – Phase 1.1 Neo4j Performance, Constraints & Indexes Design
## Groupware AI Chatbot Project – Database Infrastructure Standard

> [!NOTE]
> This specification defines the complete Neo4j 5.x DDL suite required for primary key uniqueness, multi-tenant range isolation, property lookups, and fulltext entity resolution.
> **Scope**: Pre-deployment specification for Phase 2 implementation.

---

## 1. Uniqueness Constraints (Primary Identifier Integrity)

Every graph node label representing a physical PostgreSQL entity must have an explicit uniqueness constraint:

```cypher
// 1. Core Organizational & Security Constraints
CREATE CONSTRAINT cst_tenant_id IF NOT EXISTS FOR (t:Tenant) REQUIRE t.id IS UNIQUE;
CREATE CONSTRAINT cst_user_id IF NOT EXISTS FOR (u:User) REQUIRE u.id IS UNIQUE;
CREATE CONSTRAINT cst_department_id IF NOT EXISTS FOR (d:Department) REQUIRE d.id IS UNIQUE;
CREATE CONSTRAINT cst_role_id IF NOT EXISTS FOR (r:Role) REQUIRE r.id IS UNIQUE;
CREATE CONSTRAINT cst_permission_id IF NOT EXISTS FOR (p:Permission) REQUIRE p.id IS UNIQUE;

// 2. Project, Task & Work Management Constraints
CREATE CONSTRAINT cst_project_id IF NOT EXISTS FOR (p:Project) REQUIRE p.id IS UNIQUE;
CREATE CONSTRAINT cst_ticket_id IF NOT EXISTS FOR (t:Ticket) REQUIRE t.id IS UNIQUE;
CREATE CONSTRAINT cst_sprint_id IF NOT EXISTS FOR (s:Sprint) REQUIRE s.id IS UNIQUE;
CREATE CONSTRAINT cst_kanban_id IF NOT EXISTS FOR (k:KanbanColumn) REQUIRE k.id IS UNIQUE;

// 3. Approval Workflow Constraints
CREATE CONSTRAINT cst_approval_id IF NOT EXISTS FOR (a:ApprovalRequest) REQUIRE a.id IS UNIQUE;
CREATE CONSTRAINT cst_workflow_id IF NOT EXISTS FOR (w:WorkflowTemplate) REQUIRE w.id IS UNIQUE;

// 4. Collaborative Knowledge, Calendar & Resources
CREATE CONSTRAINT cst_event_id IF NOT EXISTS FOR (e:ScheduleEvent) REQUIRE e.id IS UNIQUE;
CREATE CONSTRAINT cst_room_id IF NOT EXISTS FOR (r:ScheduleRoom) REQUIRE r.id IS UNIQUE;
CREATE CONSTRAINT cst_notice_id IF NOT EXISTS FOR (n:Notice) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT cst_post_id IF NOT EXISTS FOR (p:Post) REQUIRE p.id IS UNIQUE;
CREATE CONSTRAINT cst_asset_id IF NOT EXISTS FOR (a:Asset) REQUIRE a.id IS UNIQUE;
CREATE CONSTRAINT cst_asset_cat_id IF NOT EXISTS FOR (c:AssetCategory) REQUIRE c.id IS UNIQUE;
CREATE CONSTRAINT cst_file_id IF NOT EXISTS FOR (f:FileMetadata) REQUIRE f.id IS UNIQUE;
CREATE CONSTRAINT cst_conversation_id IF NOT EXISTS FOR (c:ChatConversation) REQUIRE c.id IS UNIQUE;
CREATE CONSTRAINT cst_audience_id IF NOT EXISTS FOR (a:Audience) REQUIRE a.id IS UNIQUE;
CREATE CONSTRAINT cst_leave_balance_id IF NOT EXISTS FOR (lb:LeaveBalance) REQUIRE lb.id IS UNIQUE;
CREATE CONSTRAINT cst_attendance_id IF NOT EXISTS FOR (ar:AttendanceRecord) REQUIRE ar.id IS UNIQUE;
CREATE CONSTRAINT cst_contract_id IF NOT EXISTS FOR (ch:ContractHistory) REQUIRE ch.id IS UNIQUE;
```

---

## 2. Multi-Tenant Range Indexes (Partition Performance)

To guarantee high traversal performance and strict multi-tenant isolation, range indexes are created on `tenant_id`:

```cypher
CREATE INDEX idx_user_tenant IF NOT EXISTS FOR (u:User) ON (u.tenant_id);
CREATE INDEX idx_department_tenant IF NOT EXISTS FOR (d:Department) ON (d.tenant_id);
CREATE INDEX idx_project_tenant IF NOT EXISTS FOR (p:Project) ON (p.tenant_id);
CREATE INDEX idx_ticket_tenant IF NOT EXISTS FOR (t:Ticket) ON (t.tenant_id);
CREATE INDEX idx_approval_tenant IF NOT EXISTS FOR (a:ApprovalRequest) ON (a.tenant_id);
CREATE INDEX idx_event_tenant IF NOT EXISTS FOR (e:ScheduleEvent) ON (e.tenant_id);
CREATE INDEX idx_notice_tenant IF NOT EXISTS FOR (n:Notice) ON (n.tenant_id);
CREATE INDEX idx_post_tenant IF NOT EXISTS FOR (p:Post) ON (p.tenant_id);
CREATE INDEX idx_asset_tenant IF NOT EXISTS FOR (a:Asset) ON (a.tenant_id);
CREATE INDEX idx_file_tenant IF NOT EXISTS FOR (f:FileMetadata) ON (f.tenant_id);
CREATE INDEX idx_conversation_tenant IF NOT EXISTS FOR (c:ChatConversation) ON (c.tenant_id);
```

---

## 3. High-Frequency Property Lookup Indexes

```cypher
// User Identity Lookups
CREATE INDEX idx_user_username IF NOT EXISTS FOR (u:User) ON (u.username);
CREATE INDEX idx_user_email IF NOT EXISTS FOR (u:User) ON (u.email);
CREATE INDEX idx_user_display_name IF NOT EXISTS FOR (u:User) ON (u.display_name);

// Project & Work Lookups
CREATE INDEX idx_project_key IF NOT EXISTS FOR (p:Project) ON (p.key);
CREATE INDEX idx_ticket_code IF NOT EXISTS FOR (t:Ticket) ON (t.code);
CREATE INDEX idx_approval_code IF NOT EXISTS FOR (a:ApprovalRequest) ON (a.code);
CREATE INDEX idx_asset_code IF NOT EXISTS FOR (a:Asset) ON (a.code);
```

---

## 4. Fulltext Search Indexes (Chatbot Entity Resolution)

Fulltext indexes allow the chatbot to perform fuzzy matching and natural language entity resolution:

```cypher
CREATE FULLTEXT INDEX fts_user_search IF NOT EXISTS 
FOR (u:User) ON EACH [u.display_name, u.username, u.email];

CREATE FULLTEXT INDEX fts_project_search IF NOT EXISTS 
FOR (p:Project) ON EACH [p.name, p.key, p.description];

CREATE FULLTEXT INDEX fts_ticket_search IF NOT EXISTS 
FOR (t:Ticket) ON EACH [t.title, t.code];

CREATE FULLTEXT INDEX fts_notice_search IF NOT EXISTS 
FOR (n:Notice) ON EACH [n.title];

CREATE FULLTEXT INDEX fts_asset_search IF NOT EXISTS 
FOR (a:Asset) ON EACH [a.name, a.code];
```

---

## 5. Performance Guidelines & Anti-Patterns

1. **Avoid Display Name Identifiers**: Display names can change. All relationship merges and graph traversals must use immutable primary identifiers (`id`, `key`, `code`).
2. **Mandatory Tenant Prefix**: Every query pattern executed by the chatbot application must anchor on tenant ID (`WHERE n.tenant_id = $session_tenant_id`) to leverage range indexes.
3. **Sparse Properties**: Null properties from PostgreSQL must be omitted rather than stored as empty strings, optimizing Neo4j memory utilization.
