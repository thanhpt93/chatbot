# PHASE 1.2 / 1.2.1 – FINAL NEO4J CONSTRAINTS & INDEXES SPECIFICATION (WORK PACKAGE 7)
## Groupware AI Chatbot – PostgreSQL + Neo4j + Vector Database

**Document ID:** `35_phase1_2_final_neo4j_constraints_indexes.md`  
**Phase:** Phase 1.2 / Phase 1.2.1 – Final Technical Defect Correction  
**Date:** 2026-11-05  
**Status:** Canonical Architecture Specification (Supersedes `26_phase1_1_neo4j_index_constraint_design.md`; updated in Phase 1.2.1 for **DEFECT 03, 04, 05, 06**)  
**Evidence Level:** `STATICALLY VALIDATED – NOT EXECUTED` (Verified against Neo4j 5.x Cypher DDL syntax and Phase 1.2.1 canonical node/relationship mappings `30` & `31`)

---

## 1. Executive Summary & Corrections from Phase 1.1 & Phase 1.2

Phase 1.1 (`26_phase1_1_neo4j_index_constraint_design.md`) and initial Phase 1.2 drafts contained invalid index definitions or incomplete fulltext security rules, all of which are resolved herein:

1. **Removed `idx_user_tenant` (`ON (u:User) ON (u.tenant_id)`)**: `:User` (`NM-02`) is a global account node and has **no `tenant_id` property**. Tenant membership is indexed on the `[:MEMBER_OF]` relationship (`idx_rel_member_of_status`) and `:Tenant(id)`.
2. **Removed `idx_permission_tenant` (`ON (p:Permission) ON (p.tenant_id)`)**: `public.permissions` (`NM-05`) is a global catalog and has **no `tenant_id` column**.
3. **Removed `idx_room_tenant` (`ON (sr:ScheduleRoom) ON (sr.tenant_id)`)**: `public.schedule_rooms` (`NM-13`) has **no `tenant_id` column**.
4. **Removed `idx_asset_cat_tenant` (`ON (ac:AssetCategory) ON (ac.tenant_id)`)**: `public.asset_categories` (`NM-17`) has **no `tenant_id` column**.
5. **Dual-Scope `:Audience` (`NM-20`) Indexes (`IDX-16A` & `IDX-16B` — DEFECT 04 Resolution)**: Because `:Audience` has both a Global System Template (`is_system = true`, `tenant_id IS NULL`) and Custom Tenant-Scoped nodes (`is_system = false`, `tenant_id IS NOT NULL`), two complementary indexes are defined: `idx_audience_custom_tenant` on `(au.tenant_id, au.audience_type, au.is_active)` and `idx_audience_system_lookup` on `(au.is_system, au.audience_type, au.is_active)`.
6. **Department Membership Lifecycle Index (`IDX-26` — DEFECT 06 Resolution)**: Added relationship range index `idx_rel_dept_member_active` on `()-[dm:MEMBER_OF_DEPARTMENT]-() ON (dm.tenant_id, dm.is_active)` (where `dm.is_active = (dm.effective_to IS NULL)` tracks `effective_from` and `effective_to` lifecycle boundaries) to support active department roster queries (`Q01`, `Q08`, `Q13`, `Q14`).
7. **Fulltext Index Security Separation (`FTS-01`–`FTS-04` — DEFECT 05 Resolution)**: Explicitly separates **Template FTS-A** (`WHERE node.tenant_id = $tenant_id` for tenant-scoped domain indexes `fts_work_items`, `fts_communications`, `fts_files`) from **Template FTS-B** (`MATCH (u)-[m:MEMBER_OF {status: 'active', is_deleted: false}]->(:Tenant {id: $tenant_id})` for the global `:User` index `fts_directory`).

---

## 2. Category 1: Required Uniqueness Constraints (`CST-01` – `CST-25`)

Every approved MVP node label (`24` labels) has a mandatory uniqueness constraint on its canonical primary key, plus secondary natural key constraints for `:Tenant(tenant_key)`, `:User(email)`, `:Permission(code)`, `:ScheduleRoom(name)`, `:AssetCategory(code)`, and `:Audience(code)` (`30` total uniqueness constraints across the `24` approved MVP labels).

| Constraint ID | Target Label | Node ID | Property | Backing PostgreSQL Source Key | Purpose |
|---|---|---|---|---|---|
| `CST-01` | `:Tenant` | `NM-01` | `t.id` | `tenants.id` (`PK`) | ETL `MERGE` & tenant anchor |
| `CST-01B` | `:Tenant` | `NM-01` | `t.tenant_key` | `tenants.tenant_key` (`UNIQUE`) | Tenant lookup by `tenant_key` |
| `CST-02` | `:User` | `NM-02` | `u.id` | `users.id` (`PK`) | ETL `MERGE` & user lookup |
| `CST-02B` | `:User` | `NM-02` | `u.email` | `users.email` (`UNIQUE`) | Identity lookup by email |
| `CST-03` | `:Department` | `NM-03` | `d.id` | `departments.id` (`PK`) | ETL `MERGE` |
| `CST-04` | `:Role` | `NM-04` | `r.id` | `roles.id` (`PK`) | ETL `MERGE` |
| `CST-05` | `:Permission` | `NM-05` | `p.id` | `permissions.id` (`PK`) | ETL `MERGE` |
| `CST-05B` | `:Permission` | `NM-05` | `p.code` | `permissions.code` (`UNIQUE`) | RBAC resolution (`Q02`) |
| `CST-06` | `:Project` | `NM-06` | `pr.id` | `projects.id` (`PK`) | ETL `MERGE` |
| `CST-07` | `:Ticket` | `NM-07` | `tk.id` | `tickets.id` (`PK`) | ETL `MERGE` |
| `CST-08` | `:Sprint` | `NM-08` | `sp.id` | `project_sprints.id` (`PK`) | ETL `MERGE` |
| `CST-09` | `:KanbanColumn` | `NM-09` | `kc.id` | `kanban_columns.id` (`PK`) | ETL `MERGE` |
| `CST-10` | `:ApprovalRequest` | `NM-10` | `ar.id` | `approval_requests.id` (`PK`) | ETL `MERGE` |
| `CST-12` | `:ScheduleEvent` | `NM-12` | `ev.id` | `schedule_events.id` (`PK`) | ETL `MERGE` |
| `CST-13` | `:ScheduleRoom` | `NM-13` | `sr.id` | `schedule_rooms.id` (`PK`) | ETL `MERGE` |
| `CST-13B` | `:ScheduleRoom` | `NM-13` | `sr.name` | `schedule_rooms.name` (`UNIQUE`) | Room lookup by name |
| `CST-14` | `:Notice` | `NM-14` | `nt.id` | `notices.id` (`PK`) | ETL `MERGE` |
| `CST-15` | `:Post` | `NM-15` | `po.id` | `talk_posts.id` (`PK`) | ETL `MERGE` |
| `CST-16` | `:Asset` | `NM-16` | `as.id` | `assets.id` (`PK`) | ETL `MERGE` |
| `CST-17` | `:AssetCategory` | `NM-17` | `ac.id` | `asset_categories.id` (`PK`) | ETL `MERGE` |
| `CST-17B` | `:AssetCategory` | `NM-17` | `ac.code` | `asset_categories.code` (`UNIQUE`) | Category lookup by code |
| `CST-18` | `:FileMetadata` | `NM-18` | `fm.id` | `files.id` (`PK`) | ETL `MERGE` |
| `CST-19` | `:ChatConversation` | `NM-19` | `cc.id` | `chat_conversations.id` (`PK`) | ETL `MERGE` |
| `CST-20` | `:Audience` | `NM-20` | `au.id` | `audiences.id` (`PK`) | ETL `MERGE` |
| `CST-20B` | `:Audience` | `NM-20` | `au.code` | `audiences.code` (`UNIQUE`) | Audience lookup by code |
| `CST-21` | `:LeaveBalance` | `NM-21` | `lb.id` | `user_leave_year_balances.id` (`PK`) | ETL `MERGE` |
| `CST-22` | `:AttendanceRecord` | `NM-22` | `at.id` | `attendance_daily_records.id` (`PK`) | ETL `MERGE` |
| `CST-23` | `:ContractHistory` | `NM-23` | `ch.id` | `user_contract_histories.id` (`PK`) | ETL `MERGE` |
| `CST-24` | `:Tag` | `NM-24` | `tg.tag_key` | Composite `tag_scope + ':' + id` | Prevents `project_tags` vs `talk_tags` collision |
| `CST-25` | `:KnowledgeDocument` | `NM-25` | `kd.id` | `project_common_documents.id` (`PK`) | Hybrid Graph-Vector join (`Q10`) |

### Executable Cypher DDL – Category 1 (Uniqueness Constraints)
```cypher
// Identity & RBAC
CREATE CONSTRAINT cst_tenant_id IF NOT EXISTS FOR (t:Tenant) REQUIRE t.id IS UNIQUE;
CREATE CONSTRAINT cst_tenant_key IF NOT EXISTS FOR (t:Tenant) REQUIRE t.tenant_key IS UNIQUE;
CREATE CONSTRAINT cst_user_id IF NOT EXISTS FOR (u:User) REQUIRE u.id IS UNIQUE;
CREATE CONSTRAINT cst_user_email IF NOT EXISTS FOR (u:User) REQUIRE u.email IS UNIQUE;
CREATE CONSTRAINT cst_department_id IF NOT EXISTS FOR (d:Department) REQUIRE d.id IS UNIQUE;
CREATE CONSTRAINT cst_role_id IF NOT EXISTS FOR (r:Role) REQUIRE r.id IS UNIQUE;
CREATE CONSTRAINT cst_permission_id IF NOT EXISTS FOR (p:Permission) REQUIRE p.id IS UNIQUE;
CREATE CONSTRAINT cst_permission_code IF NOT EXISTS FOR (p:Permission) REQUIRE p.code IS UNIQUE;

// Project, Collaboration & Workflow
CREATE CONSTRAINT cst_project_id IF NOT EXISTS FOR (pr:Project) REQUIRE pr.id IS UNIQUE;
CREATE CONSTRAINT cst_ticket_id IF NOT EXISTS FOR (tk:Ticket) REQUIRE tk.id IS UNIQUE;
CREATE CONSTRAINT cst_sprint_id IF NOT EXISTS FOR (sp:Sprint) REQUIRE sp.id IS UNIQUE;
CREATE CONSTRAINT cst_kanban_column_id IF NOT EXISTS FOR (kc:KanbanColumn) REQUIRE kc.id IS UNIQUE;
CREATE CONSTRAINT cst_approval_request_id IF NOT EXISTS FOR (ar:ApprovalRequest) REQUIRE ar.id IS UNIQUE;
CREATE CONSTRAINT cst_schedule_event_id IF NOT EXISTS FOR (ev:ScheduleEvent) REQUIRE ev.id IS UNIQUE;
CREATE CONSTRAINT cst_schedule_room_id IF NOT EXISTS FOR (sr:ScheduleRoom) REQUIRE sr.id IS UNIQUE;
CREATE CONSTRAINT cst_schedule_room_name IF NOT EXISTS FOR (sr:ScheduleRoom) REQUIRE sr.name IS UNIQUE;
CREATE CONSTRAINT cst_notice_id IF NOT EXISTS FOR (nt:Notice) REQUIRE nt.id IS UNIQUE;
CREATE CONSTRAINT cst_post_id IF NOT EXISTS FOR (po:Post) REQUIRE po.id IS UNIQUE;
CREATE CONSTRAINT cst_asset_id IF NOT EXISTS FOR (as:Asset) REQUIRE as.id IS UNIQUE;
CREATE CONSTRAINT cst_asset_category_id IF NOT EXISTS FOR (ac:AssetCategory) REQUIRE ac.id IS UNIQUE;
CREATE CONSTRAINT cst_asset_category_code IF NOT EXISTS FOR (ac:AssetCategory) REQUIRE ac.code IS UNIQUE;
CREATE CONSTRAINT cst_file_metadata_id IF NOT EXISTS FOR (fm:FileMetadata) REQUIRE fm.id IS UNIQUE;
CREATE CONSTRAINT cst_chat_conversation_id IF NOT EXISTS FOR (cc:ChatConversation) REQUIRE cc.id IS UNIQUE;
CREATE CONSTRAINT cst_audience_id IF NOT EXISTS FOR (au:Audience) REQUIRE au.id IS UNIQUE;
CREATE CONSTRAINT cst_audience_code IF NOT EXISTS FOR (au:Audience) REQUIRE au.code IS UNIQUE;

// HR & Semantic Layer
CREATE CONSTRAINT cst_leave_balance_id IF NOT EXISTS FOR (lb:LeaveBalance) REQUIRE lb.id IS UNIQUE;
CREATE CONSTRAINT cst_attendance_record_id IF NOT EXISTS FOR (at:AttendanceRecord) REQUIRE at.id IS UNIQUE;
CREATE CONSTRAINT cst_contract_history_id IF NOT EXISTS FOR (ch:ContractHistory) REQUIRE ch.id IS UNIQUE;
CREATE CONSTRAINT cst_tag_key IF NOT EXISTS FOR (tg:Tag) REQUIRE tg.tag_key IS UNIQUE;
CREATE CONSTRAINT cst_knowledge_doc_id IF NOT EXISTS FOR (kd:KnowledgeDocument) REQUIRE kd.id IS UNIQUE;
```

---

## 3. Category 2: Required Composite & Lookup Indexes (`IDX-01` – `IDX-26`)

Every tenant-scoped node label (`19` labels, including custom `:Audience` via `IDX-16A` and global system `:Audience` via `IDX-16B`) and tenant/status/lifecycle-scoped relationship (`[:MEMBER_OF]`, `[:MEMBER_OF_DEPARTMENT]`, `[:HAS_ROLE]`, `[:DIRECT_PERMISSION]`, `[:PARTICIPATES_IN]`) has a composite `RANGE` index to support tenant-isolated query execution (`Q01`–`Q14`) and ETL reconciliation (`33_phase1_2_etl_synchronization_contract.md`).

| Index ID | Target Entity | Indexed Properties | Supported Queries & ETL Operations |
|---|---|---|---|
| `IDX-01` | `:Department` | `(tenant_id, is_active)` | `Q01`, `Q08`, `Q13`, `Q14` |
| `IDX-02` | `:Role` | `(tenant_id, code, is_active)` | `Q02` RBAC role lookup |
| `IDX-03` | `:Project` | `(tenant_id, is_deleted, status)` | `Q03`, `Q04`, `Q10` |
| `IDX-04` | `:Project` | `(tenant_id, key)` | Project lookup by key (`Q03`, `Q06`, `Q10`) |
| `IDX-05` | `:Ticket` | `(tenant_id, is_deleted, status)` | `Q03`, `Q04`, `Q06` |
| `IDX-06` | `:Ticket` | `(tenant_id, code)` | Ticket lookup by code (`Q03`, `Q04`, `Q06`) |
| `IDX-07` | `:Sprint` | `(tenant_id, project_id, status)` | `Q03` sprint lookup |
| `IDX-08` | `:KanbanColumn` | `(tenant_id, project_id, status_group)` | `Q03`, `Q04`, `Q06` stage filtering |
| `IDX-09` | `:ApprovalRequest` | `(tenant_id, status, is_deleted)` | `Q05` (`status = 'IN_PROGRESS'`) |
| `IDX-10` | `:ScheduleEvent` | `(tenant_id, is_deleted, event_date, end_date)` | `Q07` calendar date-window scan |
| `IDX-11` | `:Notice` | `(tenant_id, is_published, is_deleted, published_at)` | `Q08` notice feed |
| `IDX-12` | `:Post` | `(tenant_id, is_deleted, created_at)` | `Q13` recent posts by tenant |
| `IDX-13` | `:Asset` | `(tenant_id, is_deleted, code)` | `Q09` asset inventory |
| `IDX-14` | `:FileMetadata` | `(tenant_id, is_deleted, request_type)` | `Q10` file lookup |
| `IDX-15` | `:ChatConversation` | `(tenant_id, conversation_type)` | `SEC-07` & chat topology |
| `IDX-16A` | `:Audience` | `(tenant_id, audience_type, is_active)` | `Q08` custom tenant-scoped audience resolution (`is_system = false`) |
| `IDX-16B` | `:Audience` | `(is_system, audience_type, is_active)` | `Q08` global system audience template lookup (`is_system = true, tenant_id IS NULL`) |
| `IDX-17` | `:LeaveBalance` | `(tenant_id, user_id, year)` | `Q11` annual balance lookup |
| `IDX-18` | `:AttendanceRecord` | `(tenant_id, user_id, work_date)` | `Q11` monthly attendance |
| `IDX-19` | `:ContractHistory` | `(tenant_id, user_id, is_current)` | `Q12` active contract lookup |
| `IDX-20` | `:Tag` | `(tenant_id, name)` | `Q06`, `Q13` tag filtering |
| `IDX-21` | `:KnowledgeDocument` | `(tenant_id, project_id, is_deleted)` | `Q10` project document lookup |
| `IDX-22` | `[:MEMBER_OF]` | `(status, is_deleted)` | `Q01`–`Q14` active tenant membership preamble |
| `IDX-23` | `[:HAS_ROLE]` | `(tenant_id)` | `Q02` RBAC resolution |
| `IDX-24` | `[:DIRECT_PERMISSION]` | `(tenant_id, is_granted)` | `Q02` RBAC override resolution |
| `IDX-25` | `[:PARTICIPATES_IN]` | `(action_status, participant_role, sequence_order)` | `Q05` pending approval participant lookup (**DEFECT 03**) |
| `IDX-26` | `[:MEMBER_OF_DEPARTMENT]` | `(tenant_id, is_active)` | `Q01`, `Q08`, `Q13`, `Q14` active department membership filtering (`effective_to IS NULL`, **DEFECT 06**) |

### Executable Cypher DDL – Category 2 (Required Lookup Indexes)
```cypher
// Node Composite Range Indexes
CREATE INDEX idx_department_tenant_active IF NOT EXISTS FOR (d:Department) ON (d.tenant_id, d.is_active);
CREATE INDEX idx_role_tenant_code IF NOT EXISTS FOR (r:Role) ON (r.tenant_id, r.code, r.is_active);
CREATE INDEX idx_project_tenant_status IF NOT EXISTS FOR (pr:Project) ON (pr.tenant_id, pr.is_deleted, pr.status);
CREATE INDEX idx_project_tenant_key IF NOT EXISTS FOR (pr:Project) ON (pr.tenant_id, pr.key);
CREATE INDEX idx_ticket_tenant_status IF NOT EXISTS FOR (tk:Ticket) ON (tk.tenant_id, tk.is_deleted, tk.status);
CREATE INDEX idx_ticket_tenant_code IF NOT EXISTS FOR (tk:Ticket) ON (tk.tenant_id, tk.code);
CREATE INDEX idx_sprint_tenant_project IF NOT EXISTS FOR (sp:Sprint) ON (sp.tenant_id, sp.project_id, sp.status);
CREATE INDEX idx_kanban_col_tenant_group IF NOT EXISTS FOR (kc:KanbanColumn) ON (kc.tenant_id, kc.project_id, kc.status_group);
CREATE INDEX idx_approval_tenant_status IF NOT EXISTS FOR (ar:ApprovalRequest) ON (ar.tenant_id, ar.status, ar.is_deleted);
CREATE INDEX idx_schedule_event_tenant_date IF NOT EXISTS FOR (ev:ScheduleEvent) ON (ev.tenant_id, ev.is_deleted, ev.event_date, ev.end_date);
CREATE INDEX idx_notice_tenant_published IF NOT EXISTS FOR (nt:Notice) ON (nt.tenant_id, nt.is_published, nt.is_deleted, nt.published_at);
CREATE INDEX idx_post_tenant_created IF NOT EXISTS FOR (po:Post) ON (po.tenant_id, po.is_deleted, po.created_at);
CREATE INDEX idx_asset_tenant_code IF NOT EXISTS FOR (as:Asset) ON (as.tenant_id, as.is_deleted, as.code);
CREATE INDEX idx_file_tenant_type IF NOT EXISTS FOR (fm:FileMetadata) ON (fm.tenant_id, fm.is_deleted, fm.request_type);
CREATE INDEX idx_chat_conv_tenant_type IF NOT EXISTS FOR (cc:ChatConversation) ON (cc.tenant_id, cc.conversation_type);
CREATE INDEX idx_audience_custom_tenant IF NOT EXISTS FOR (au:Audience) ON (au.tenant_id, au.audience_type, au.is_active);
CREATE INDEX idx_audience_system_lookup IF NOT EXISTS FOR (au:Audience) ON (au.is_system, au.audience_type, au.is_active);
CREATE INDEX idx_leave_balance_tenant_user_year IF NOT EXISTS FOR (lb:LeaveBalance) ON (lb.tenant_id, lb.user_id, lb.year);
CREATE INDEX idx_attendance_tenant_user_date IF NOT EXISTS FOR (at:AttendanceRecord) ON (at.tenant_id, at.user_id, at.work_date);
CREATE INDEX idx_contract_tenant_user_current IF NOT EXISTS FOR (ch:ContractHistory) ON (ch.tenant_id, ch.user_id, ch.is_current);
CREATE INDEX idx_tag_tenant_name IF NOT EXISTS FOR (tg:Tag) ON (tg.tenant_id, tg.name);
CREATE INDEX idx_kdoc_tenant_project IF NOT EXISTS FOR (kd:KnowledgeDocument) ON (kd.tenant_id, kd.project_id, kd.is_deleted);

// Relationship Range Indexes
CREATE INDEX idx_rel_member_of_status IF NOT EXISTS FOR ()-[m:MEMBER_OF]-() ON (m.status, m.is_deleted);
CREATE INDEX idx_rel_has_role_tenant IF NOT EXISTS FOR ()-[hr:HAS_ROLE]-() ON (hr.tenant_id);
CREATE INDEX idx_rel_direct_perm_tenant IF NOT EXISTS FOR ()-[dp:DIRECT_PERMISSION]-() ON (dp.tenant_id, dp.is_granted);
CREATE INDEX idx_rel_participates_in_status IF NOT EXISTS FOR ()-[hp:PARTICIPATES_IN]-() ON (hp.action_status, hp.participant_role, hp.sequence_order);
CREATE INDEX idx_rel_dept_member_active IF NOT EXISTS FOR ()-[dm:MEMBER_OF_DEPARTMENT]-() ON (dm.tenant_id, dm.is_active);
```

---

## 4. Category 3: Optional Performance Indexes (`OPT-IDX-01` – `OPT-IDX-04`)

```cypher
CREATE INDEX opt_idx_user_username IF NOT EXISTS FOR (u:User) ON (u.username);
CREATE INDEX opt_idx_ticket_tenant_due_date IF NOT EXISTS FOR (tk:Ticket) ON (tk.tenant_id, tk.due_date);
CREATE INDEX opt_idx_asset_serial IF NOT EXISTS FOR (as:Asset) ON (as.tenant_id, as.serial_number);
CREATE INDEX opt_idx_attendance_emp_code IF NOT EXISTS FOR (at:AttendanceRecord) ON (at.tenant_id, at.employee_code);
```

---

## 5. Category 4: Fulltext Indexes & Mandatory Two-Template Tenant Security Guard (`FTS-01` – `FTS-04` — DEFECT 05 Resolution)

> [!WARNING]
> **Critical Security Rule (`DEFECT 05` — `SEC-12` to `SEC-20`)**:
> Neo4j Fulltext Indexes (`FULLTEXT`) index text across all nodes globally. Because `:User` (`NM-02`) is a **Global Identity Node** without a `u.tenant_id` property, applying `WHERE node.tenant_id = $tenant_id` to `fts_directory` **fails** (`0` rows), whereas omitting a tenant filter leaks cross-tenant users!
> Therefore, **two mandatory post-FTS security templates** govern the 4 fulltext indexes:
> 1. **Template FTS-A (`FTS-01` `fts_work_items`, `FTS-02` `fts_communications`, `FTS-03` `fts_files`)**:
>    Every indexed label (`Project`, `Ticket`, `Sprint`, `Notice`, `Post`, `KnowledgeDocument`, `FileMetadata`) is tenant-scoped (`node.tenant_id IS NOT NULL`). Every query calling these indexes **MUST immediately filter**:
>    `YIELD node, score WHERE node.tenant_id = $tenant_id AND coalesce(node.is_deleted, false) = false`
>    followed by the domain RBAC predicate.
> 2. **Template FTS-B (`FTS-04` `fts_directory` on `:User` — Scenario `Q14`)**:
>    Every query calling `fts_directory` **MUST NEVER** filter `u.tenant_id`. Instead, it **MUST** verify the caller's directory search permission and immediately join the yielded `:User` node to the caller's active `:Tenant`:
>    ```cypher
>    CALL db.index.fulltext.queryNodes('fts_directory', $search_term) YIELD node AS u, score
>    MATCH (u)-[m:MEMBER_OF {status: 'active', is_deleted: false}]->(t:Tenant {id: $tenant_id, is_deleted: false})
>    WHERE u.is_active = true AND u.is_deleted = false AND coalesce(m.is_resigned, false) = false
>    ```
>    and project only permitted tenant-scoped directory attributes (`u.id, u.username, u.email, coalesce(m.display_name, u.display_name), m.position`).

```cypher
// FTS-01: Tenant-Scoped Work Items (Template FTS-A: require WHERE node.tenant_id = $tenant_id)
CREATE FULLTEXT INDEX fts_work_items IF NOT EXISTS
FOR (n:Project|Ticket|Sprint) ON EACH [n.key, n.code, n.name, n.title, n.description];

// FTS-02: Tenant-Scoped Communications & Documents (Template FTS-A: require WHERE node.tenant_id = $tenant_id)
CREATE FULLTEXT INDEX fts_communications IF NOT EXISTS
FOR (n:Notice|Post|KnowledgeDocument) ON EACH [n.title];

// FTS-03: Tenant-Scoped File Metadata (Template FTS-A: require WHERE f.tenant_id = $tenant_id)
CREATE FULLTEXT INDEX fts_files IF NOT EXISTS
FOR (f:FileMetadata) ON EACH [f.original_name];

// FTS-04: Global User Directory (Template FTS-B: require MATCH (u)-[m:MEMBER_OF {status: 'active', is_deleted: false}]->(:Tenant {id: $tenant_id}))
CREATE FULLTEXT INDEX fts_directory IF NOT EXISTS
FOR (u:User) ON EACH [u.display_name, u.username, u.email];
```

---

## 6. Category 5: Blocked & Future Indexes (Do NOT Execute in MVP)

```cypher
// BLOCKED (ND-11 :WorkflowTemplate - requires tenant_id and request_type FK remediation per Decision SD-01)
// CREATE CONSTRAINT cst_workflow_template_id IF NOT EXISTS FOR (wt:WorkflowTemplate) REQUIRE wt.id IS UNIQUE;

// FUTURE PHASE 2+ (ND-26 :Topic, ND-27 :BusinessConcept)
// CREATE CONSTRAINT cst_topic_id IF NOT EXISTS FOR (tp:Topic) REQUIRE tp.topic_id IS UNIQUE;
// CREATE CONSTRAINT cst_business_concept_id IF NOT EXISTS FOR (bc:BusinessConcept) REQUIRE bc.concept_id IS UNIQUE;
```
