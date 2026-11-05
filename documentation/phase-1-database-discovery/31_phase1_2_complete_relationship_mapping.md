# 31 – Phase 1.2 / 1.2.1 / 1.2.2 Complete Relationship Mapping Specification
## Groupware AI Chatbot Project – Exhaustive PostgreSQL-to-Neo4j Relationship Contracts

> [!IMPORTANT]
> **Work Package 3 Objective (Updated in Phase 1.2.1 & Phase 1.2.2)**:
> In Phase 1.1, `21_phase1_1_final_graph_data_model.md` listed **31 operational relationship rows** (and 5 semantic relationships), whereas `24_phase1_1_final_source_to_graph_mapping.md` only provided extraction SQL and Cypher contracts for **4 relationships** (`[:ASSIGNED_TO]` on Ticket, `[:PARTICIPATES_IN]`, `[:ATTENDS_EVENT]`, `[:HAS_ROLE]`) — leaving **27 operational relationships and all semantic relationships completely unmapped**!
> This document reconciles **every single relationship** in the canonical Graph Model (**45 Evaluated Relationships: 42 Approved MVP, 1 Blocked, 2 Future**) with its verified PostgreSQL source table, column join, cardinality, match rate, tenant validation rule, orphan handling contract, and executable SQL + Cypher specification (including Phase 1.2.1 & Phase 1.2.2 fixes for **DEFECT 02 & CRITICAL-01** `RM-37` Attendance active-membership resolution, **CRITICAL-02** `RM-36` LeaveBalance tenant derivation, **DEFECT 03** `RM-20` Approval Participant properties, **DEFECT 04** `RM-25`–`RM-27`/`RM-29` Audience dual-scope ownership, **HIGH-05** `RM-04` Manager active tenant membership, **DEFECT 06** `RM-03` Department membership lifecycle filtering, and **DEFECT 07** relationship count reconciliation).

---

## 1. Forensic Investigation of Critical Relationships (Section 7.2 Requirements)

### 1.1 Ticket Assignment (`[:ASSIGNED_TO]`, `RM-13`)
- **Source Table**: `public.ticket_assignees` (`1,008` rows, PK `id` `int8`, unique constraint `uq_ticket_assignees_ticket_user (ticket_id, user_id)`).
- **Columns**: `id` (`int8` NOT NULL), `ticket_id` (`int8` NOT NULL, `660` distinct tickets), `user_id` (`int8` NOT NULL, `77` distinct users), `assigned_at` (`timestamptz`), `assigned_by_user_id` (`int8`, `37` distinct users).
- **Data Profile**:
  - `ticket_id -> tickets.id`: `599/660` distinct tickets match (`90.76%`); `61` distinct ticket IDs were purged in historical cleanup.
  - `user_id -> users.id`: `64/77` distinct users match (`83.12%`); `13` distinct user IDs were purged into `_backup_cleanup_20261005.users_deleted`.
  - Multiple assignees per ticket exist (`1,008` assignments across `660` tickets -> N:M cardinality).
- **Target Edge**: `(:Ticket)-[r:ASSIGNED_TO {id, assigned_at, assigned_by_user_id, last_synced_at}]->(:User)`.

### 1.2 Project Membership (`[:MEMBER_OF_PROJECT]`, `RM-10`)
- **Source Table**: `public.project_members` (`356` rows, PK `id` `int8`, unique constraint `uq_project_members_project_user (project_id, user_id)`).
- **Columns**: `id` (`int8` NOT NULL), `project_id` (`int8` NOT NULL, `67` distinct projects), `user_id` (`int8` NOT NULL, `151` distinct users), `role` (`text`: `'member'`: `246`, `'owner'`: `72`, `'admin'`: `38`), `joined_at` (`timestamptz`), `invited_by_user_id` (`int8`).
- **Data Profile**:
  - `project_id -> projects.id`: `65/67` match (`97.01%`).
  - `user_id -> users.id`: `133/151` match (`88.08%`, `18` archived in Oct 5 cleanup).
  - Multiple owners per project exist (`72` `'owner'` rows across `65` projects -> N:M cardinality).
- **Target Edge**: `(:User)-[m:MEMBER_OF_PROJECT {id, role, joined_at, invited_by_user_id, last_synced_at}]->(:Project)`.

### 1.3 Department Membership (`[:MEMBER_OF_DEPARTMENT]`, `RM-03` — DEFECT 06), Hierarchy (`[:SUB_DEPARTMENT_OF]`, `RM-05`) & Manager (`[:MANAGES]`, `RM-04` — HIGH-05)
- **Department Membership (`public.department_members`, `RM-03` — DEFECT 06 Resolution)**:
  - **Source Table**: `public.department_members` (`397` rows, PK `id` `int8`, unique constraint `ux_department_members_tenant_assignment_period (tenant_id, department_id, user_id, effective_to)` and partial unique index `ux_department_members_tenant_primary_active_user (tenant_id, user_id) WHERE is_primary = true AND effective_to IS NULL`).
  - **Physical Columns**: `id` (`int8` NOT NULL), `tenant_id` (`int8` NOT NULL), `department_id` (`int4` NOT NULL), `user_id` (`int4` NOT NULL), `role_in_department` (`varchar` NOT NULL), `is_primary` (`bool` NOT NULL), `effective_from` (`date` NOT NULL), `effective_to` (`date`, nullable: **`349` rows have `effective_to IS NULL` (active)**, **`48` rows have `effective_to IS NOT NULL` (historical/ended)**), `created_at` (`timestamptz`), `updated_at` (`timestamptz`), `created_by_user_id` (`int8`), `updated_by_user_id` (`int8`).
  - **Lifecycle Contract**: All `397` rows are synchronized into Neo4j keyed by `{id: toInteger(row.id)}` with explicit lifecycle properties `effective_from`, `effective_to`, and derived boolean `is_active = (row.effective_to IS NULL)` alongside `tenant_id`, `role_in_department`, `is_primary`, `updated_at`, `last_synced_at`. All current-state chatbot queries (`Q01`, `Q08`, `Q13`) **MUST** filter `WHERE dm.is_active = true AND dm.tenant_id = $tenant_id` (and SQL validation queries **MUST** filter `AND dm.effective_to IS NULL`), whereas historical audit queries may inspect `dm.is_active = false`.
- **Department Hierarchy (`departments.parent_id`, `RM-05`)**:
  - Source column: `public.departments.parent_id` (`int4`, nullable). **Never use `parent_department_id`**.
  - Profile: `103` total departments; `53` root departments (`parent_id IS NULL`), `50` child departments (`parent_id IS NOT NULL`, `16` distinct parent departments, `100.0%` match to `departments.id`, `0` cross-tenant edges, max depth = `4`).
  - Target Edge: `(:Department)-[:SUB_DEPARTMENT_OF]->(:Department)` (N:1).
- **Department Manager (`departments.manager_user_id`, `RM-04` — HIGH-05 Resolution)**:
  - Source column: `public.departments.manager_user_id` (`int4`, **nullable**).
  - Profile: `21` departments have `manager_user_id IS NOT NULL` (`82` are `NULL`). Thus the relationship is **OPTIONAL** (`0..1` manager per department).
  - Furthermore, those `21` departments reference `18` distinct users (`users.id` `6`, `12`, and `149` each manage `2` departments!). Therefore, the true cardinality of `(:User)-[:MANAGES]->(:Department)` is **1:N** (one user can manage multiple departments, and a department has at most one manager), **NOT `1:1`** as erroneously claimed in Phase 1.1 Document `21`!
  - **HIGH-05 Active Manager Membership Rule**: A user may only hold an active `[:MANAGES {tenant_id: d.tenant_id}]` edge over a department `d` if the user is globally active/non-deleted (`u.is_active = true AND u.is_deleted = false`) AND holds an active, non-deleted tenant membership in `d.tenant_id` (`m.status = 'active' AND m.is_deleted = false`). Both `RM-04` (ETL) and `Q01` (`Doc 34`) enforce this invariant.

### 1.4 Approval Workflow (`approval_requests`, `approval_workflow_templates`, `approval_participants` — DEFECT 03 Resolution)
- **`approval_participants` (`[:PARTICIPATES_IN]`, `RM-20` — DEFECT 03 Resolution)**:
  - **Source Table**: `public.approval_participants` (`12,720` rows, PK `id` `int8`, unique constraint `approval_participants_request_id_user_id_participant_role_key (request_id, user_id, participant_role)`).
  - **Verified Physical Columns (`9` columns total)**:
    1. `id` (`int8` NOT NULL)
    2. `request_id` (`int8` NOT NULL)
    3. `user_id` (`int8` NOT NULL)
    4. `participant_role` (`varchar` NOT NULL: `'APPROVER'` `5,162`, `'REFERRER'` `4,276`, `'AGREEMENTOR'` `3,282`)
    5. `sequence_order` (`int4` NOT NULL)
    6. `action_status` (`varchar` NOT NULL: `'APPROVED'` `7,736`, `'ACKNOWLEDGED'` `4,221`, `'SKIPPED'` `494`, `'PENDING'` `159`, `'RETURN'` `44`, `'REJECTED'` `33`, `'WAITING'` `33`)
    7. `acted_at` (`timestamptz`, nullable)
    8. `note` (`text`, nullable — excluded from graph properties per Tier 1 data minimization)
    9. `created_at` (`timestamptz` NOT NULL)
  - **Correction of Phase 1.1 / Phase 1.2 Property Defect**: `public.approval_participants` does **NOT** contain `step_order`, `step_name`, or `is_required` (those columns exist only on `public.approval_workflow_steps`, which belongs to the unlinked/blocked `approval_workflow_templates` table). Therefore, `[:PARTICIPATES_IN]` (`RM-20`) maps **strictly** the physical columns `id`, `participant_role`, `sequence_order`, `action_status`, `acted_at`, `created_at` (plus `last_synced_at`), and all Cypher/SQL queries (`Q05` in `Doc 34` and `RM-20` in `Doc 38`) reference `sequence_order`.
  - Because the unique key is `(request_id, user_id, participant_role)`, the **same user can participate in the same request under different roles** (e.g. `APPROVER` and `REFERRER`). Therefore, `MERGE (u)-[p:PARTICIPATES_IN {participant_role: row.participant_role}]->(a)` is mandatory to avoid overwriting edges.
- **`approval_requests` to `approval_workflow_templates` (`[:USES_TEMPLATE]`, `RM-19`)**:
  - **Forensic Audit**:
    1. `approval_requests` has **NO `template_id` or `workflow_template_id` column**.
    2. `approval_workflow_templates` (`9` rows) has **NO unique constraint on `request_type`**.
    3. `approval_requests` contains `9` rows with `request_type = 'crd_acceptance'`, which has **0 matching rows** in `approval_workflow_templates`.
    4. `approval_workflow_templates` has **no `tenant_id` column**.
  - **Architectural Decision**: **`[:USES_TEMPLATE]` (`RM-19`) is REJECTED / BLOCKED for MVP** (Decision SD-01).

### 1.5 Schedule (`schedule_events`, `schedule_event_participants`, `schedule_rooms`)
- **`schedule_events.user_id` (`[:ORGANIZED_BY]`, `RM-21`)**: `349` events, `29` distinct organizer user IDs (`25` active in `users`, `4` archived in `_backup_cleanup_20261005.users_deleted`, `86.21%` active match). Cardinality: N:1.
- **`schedule_events.room_id` (`[:HELD_IN]`, `RM-22`)**: `242` events have `room_id IS NOT NULL` (`107` have `room_id IS NULL`), referencing `5` distinct rooms (`100.0%` match to `schedule_rooms.id`).
- **`schedule_event_participants` (`[:ATTENDS_EVENT]`, `RM-23`)**: `1,241` rows, unique constraint `(event_id, user_id)`. `event_id -> schedule_events.id` is `100%` (`281/281`); `user_id -> users.id` is `87.65%` (`71/81` distinct users active, `10` archived in Oct 5 cleanup).

### 1.6 Notice, Post, and Audience (`notices`, `talk_posts`, `audiences`, `audience_department_members`, `audience_user_members` — DEFECT 04 Resolution)
- `audiences` (`116` rows) operates under the **Dual-Scope Ownership Contract (`Doc 29` Section 3.2 & `Doc 30` `NM-20`)**:
  - **System Audience (`is_system = true`, `1` row: `id = 1`, `audience_type = 'ALL'`)**: Modeled as a **Global System Template Node** (`a.is_system = true`, `a.tenant_id IS NULL`). It has **0** `[:INCLUDES_DEPARTMENT]` (`RM-26`) and **0** `[:INCLUDES_USER]` (`RM-27`) edges.
  - **Custom Audience (`is_system = false`, `115` rows)**: Modeled as a **Tenant-Scoped Node** (`a.is_system = false`, `a.tenant_id IS NOT NULL`).
  - **Targeting Edges (`RM-25` `(:Notice)-[:TARGETED_TO]->(:Audience)` & `RM-29` `(:Post)-[:TARGETED_TO]->(:Audience)`)**: Enforce `WHERE (a.is_system = false AND a.tenant_id = src.tenant_id) OR (a.is_system = true AND a.tenant_id IS NULL)`.
  - **Membership Edges (`RM-26` `[:INCLUDES_DEPARTMENT]` & `RM-27` `[:INCLUDES_USER]`)**: Restricted strictly to custom audiences (`WHERE a.is_system = false AND a.tenant_id IS NOT NULL`) where the target `:Department` or `:User` belongs to `a.tenant_id`.

### 1.7 Chat (`chat_conversations`, `chat_conversation_members`)
- Preserves **ChatMessage Option A** (zero `ChatMessage` nodes in Neo4j).
- `chat_conversations` (`329` rows: `299` `DIRECT`, `30` `GROUP`) has `created_by_user_id` -> mapped as `(:ChatConversation)-[:CREATED_BY]->(:User)` (`RM-35`).
- `chat_conversation_members` (`783` rows, unique `(conversation_id, user_id)`) -> mapped as `(:User)-[m:MEMBER_OF_CONVERSATION {id, role, joined_at, is_pinned, is_muted, is_deleted, last_synced_at}]->(:ChatConversation)` (`RM-34`).

---

## 2. Complete Relationship Inventory & Mapping Matrix (45 Evaluated Relationships: 42 Approved MVP, 1 Blocked, 2 Future)

| Rel ID | Relationship Type | Source Node | Target Node | Source Table & Columns | Join Logic | Cardinality | Match Rate & Confidence | Status |
|---|---|---|---|---|---|---|---|---|
| **RM-01** | `[:MEMBER_OF]` | `:User` | `:Tenant` | `public.tenant_user_memberships` (`user_id`, `tenant_id`) + `LEFT JOIN user_profiles` | `u.id = m.user_id` AND `t.id = m.tenant_id` | N:M | `360/360` (`100.0%` High) | **MVP – APPROVED** |
| **RM-02** | `[:BELONGS_TO_TENANT]` | `:Department` | `:Tenant` | `public.departments` (`id`, `tenant_id`) | `d.id = dept.id` AND `t.id = dept.tenant_id` | N:1 | `103/103` (`100.0%` High) | **MVP – APPROVED** |
| **RM-03** | `[:MEMBER_OF_DEPARTMENT]` | `:User` | `:Department` | `public.department_members` (`id`, `user_id`, `department_id`, `tenant_id`, `role_in_department`, `is_primary`, `effective_from`, `effective_to`, `updated_at`) | `u.id = dm.user_id` AND `d.id = dm.department_id` (`is_active = (effective_to IS NULL)`) | N:M | `358/358` users, `25/25` depts (`100.0%` High; `349` active, `48` historical) | **MVP – APPROVED** |
| **RM-04** | `[:MANAGES]` | `:User` | `:Department` | `public.departments` (`manager_user_id`, `id`) | `u.id = d.manager_user_id` (`WHERE manager_user_id IS NOT NULL` AND `m.status = 'active' AND m.is_deleted = false` — **`HIGH-05`**) | **1:N** (Optional on Dept: 21/103) | `18/18` distinct users (`100.0%` High) | **MVP – APPROVED** |
| **RM-05** | `[:SUB_DEPARTMENT_OF]` | `:Department` | `:Department` | `public.departments` (`id`, `parent_id`) | `child.id = d.id` AND `parent.id = d.parent_id` (`WHERE parent_id IS NOT NULL`) | N:1 (Optional: 50/103) | `16/16` parent depts (`100.0%` High) | **MVP – APPROVED** |
| **RM-06** | `[:HAS_ROLE]` | `:User` | `:Role` | `public.user_role_assignments` (`user_id`, `role_id`, `tenant_id`) | `u.id = ura.user_id` AND `r.id = ura.role_id` | N:M | `360/360` users, `11/11` roles (`100.0%` High) | **MVP – APPROVED** |
| **RM-07** | `[:INCLUDES_PERMISSION]` | `:Role` | `:Permission` | `public.role_permissions` (`role_id`, `permission_id`, `tenant_id`, `is_granted`) | `r.id = rp.role_id` AND `p.id = rp.permission_id` | N:M | `42/42` roles (`100%`), `245/247` perms (`99.19%` Medium - 2 orphan perm IDs) | **MVP – APPROVED** |
| **RM-08** | `[:DIRECT_PERMISSION]` | `:User` | `:Permission` | `public.user_permissions` (`user_id`, `permission_id`, `tenant_id`, `is_granted`) | `u.id = up.user_id` AND `p.id = up.permission_id` | N:M | `32/32` users, `22/22` perms (`100.0%` High) | **MVP – APPROVED** |
| **RM-09** | `[:CREATED_BY]` | `:Project` | `:User` | `public.projects` (`id`, `created_by_user_id`) | `p.id = proj.id` AND `u.id = proj.created_by_user_id` | N:1 | `18/20` creators active (`90.00%` Medium - 2 archived in Oct 5 cleanup) | **MVP – APPROVED** |
| **RM-10** | `[:MEMBER_OF_PROJECT]` | `:User` | `:Project` | `public.project_members` (`user_id`, `project_id`, `role`) | `u.id = pm.user_id` AND `p.id = pm.project_id` | N:M | `65/67` projects (`97.01%`), `133/151` users (`88.08%` Medium) | **MVP – APPROVED** |
| **RM-11** | `[:BELONGS_TO_PROJECT]` | `:Ticket` | `:Project` | `public.tickets` (`id`, `project_id`) | `t.id = tkt.id` AND `p.id = tkt.project_id` | N:1 | `29/29` distinct projects (`100.0%` High) | **MVP – APPROVED** |
| **RM-12** | `[:CREATED_BY]` | `:Ticket` | `:User` | `public.tickets` (`id`, `created_by_user_id`) | `t.id = tkt.id` AND `u.id = tkt.created_by_user_id` | N:1 | `28/30` distinct users (`93.33%` Medium - 2 archived) | **MVP – APPROVED** |
| **RM-13** | `[:ASSIGNED_TO]` | `:Ticket` | `:User` | `public.ticket_assignees` (`ticket_id`, `user_id`) | `t.id = ta.ticket_id` AND `u.id = ta.user_id` | N:M | `599/660` tickets (`90.76%`), `64/77` users (`83.12%` Medium) | **MVP – APPROVED** |
| **RM-14** | `[:PART_OF_SPRINT]` | `:Ticket` | `:Sprint` | `public.tickets` (`id`, `sprint_id`) | `t.id = tkt.id` AND `s.id = tkt.sprint_id` (`WHERE sprint_id IS NOT NULL`) | N:1 (Optional: 263/668) | `33/33` distinct sprints (`100.0%` High) | **MVP – APPROVED** |
| **RM-15** | `[:IN_STAGE]` | `:Ticket` | `:KanbanColumn` | `public.tickets` (`id`, `column_id`) | `t.id = tkt.id` AND `k.id = tkt.column_id` (`WHERE column_id IS NOT NULL`) | N:1 | `64/64` distinct columns (`100.0%` High) | **MVP – APPROVED** |
| **RM-16** | `[:SPRINT_OF_PROJECT]` | `:Sprint` | `:Project` | `public.project_sprints` (`id`, `project_id`) | `s.id = sp.id` AND `p.id = sp.project_id` | N:1 | `25/25` distinct projects (`100.0%` High) | **MVP – APPROVED** |
| **RM-17** | `[:COLUMN_OF_PROJECT]` | `:KanbanColumn` | `:Project` | `public.kanban_columns` (`id`, `project_id`) | `k.id = kc.id` AND `p.id = kc.project_id` | N:1 | `65/65` distinct projects (`100.0%` High) | **MVP – APPROVED** |
| **RM-18** | `[:CREATED_BY]` | `:ApprovalRequest` | `:User` | `public.approval_requests` (`id`, `created_by_user_id`) | `a.id = ar.id` AND `u.id = ar.created_by_user_id` | N:1 | `317/318` distinct creators (`99.69%` Medium - 1 archived) | **MVP – APPROVED** |
| **RM-19** | `[:USES_TEMPLATE]` | `:ApprovalRequest` | `:WorkflowTemplate` | `approval_requests.request_type` vs `approval_workflow_templates.request_type` | Non-FK string association (`request_type` not unique in schema, missing `'crd_acceptance'`, no `tenant_id` on template) | Unverified | Partial (`7/8` request types) / **Unverified** | **REJECTED / BLOCKED** (Decision SD-01) |
| **RM-20** | `[:PARTICIPATES_IN]` | `:User` | `:ApprovalRequest` | `public.approval_participants` (`id`, `user_id`, `request_id`, `participant_role`, `sequence_order`, `action_status`, `acted_at`, `created_at`) | `u.id = ap.user_id` AND `a.id = ap.request_id` (keyed by `participant_role`) | N:M (Multi-role per user/request) | `4,699/4,699` requests (`100%`), `58/59` users (`98.31%` Medium) | **MVP – APPROVED** |
| **RM-21** | `[:ORGANIZED_BY]` | `:ScheduleEvent` | `:User` | `public.schedule_events` (`id`, `user_id`) | `e.id = se.id` AND `u.id = se.user_id` | N:1 | `25/29` distinct users (`86.21%` Medium - 4 archived) | **MVP – APPROVED** |
| **RM-22** | `[:HELD_IN]` | `:ScheduleEvent` | `:ScheduleRoom` | `public.schedule_events` (`id`, `room_id`) | `e.id = se.id` AND `r.id = se.room_id` (`WHERE room_id IS NOT NULL`) | N:1 (Optional: 242/349) | `5/5` distinct rooms (`100.0%` High) | **MVP – APPROVED** |
| **RM-23** | `[:ATTENDS_EVENT]` | `:User` | `:ScheduleEvent` | `public.schedule_event_participants` (`user_id`, `event_id`) | `u.id = sep.user_id` AND `e.id = sep.event_id` | N:M | `281/281` events (`100%`), `71/81` users (`87.65%` Medium) | **MVP – APPROVED** |
| **RM-24** | `[:PUBLISHED_BY]` | `:Notice` | `:User` | `public.notices` (`id`, `created_by_user_id`) | `n.id = nt.id` AND `u.id = nt.created_by_user_id` | N:1 | `5/5` distinct users (`100.0%` High) | **MVP – APPROVED** |
| **RM-25** | `[:TARGETED_TO]` | `:Notice` | `:Audience` | `public.notices` (`id`, `audience_id`) | `n.id = nt.id` AND `a.id = nt.audience_id` (`WHERE (a.is_system = false AND a.tenant_id = n.tenant_id) OR (a.is_system = true AND a.tenant_id IS NULL)`) | N:1 | `15/15` distinct audiences (`100.0%` High) | **MVP – APPROVED** |
| **RM-26** | `[:INCLUDES_DEPARTMENT]` | `:Audience` | `:Department` | `public.audience_department_members` (`audience_id`, `department_id`) | `a.id = adm.audience_id` AND `d.id = adm.department_id` (`WHERE a.is_system = false AND a.tenant_id = d.tenant_id`) | N:M | `90/90` custom audiences, `28/28` depts (`100.0%` High) | **MVP – APPROVED** |
| **RM-27** | `[:INCLUDES_USER]` | `:Audience` | `:User` | `public.audience_user_members` (`audience_id`, `user_id`) | `a.id = aum.audience_id` AND `u.id = aum.user_id` (`WHERE a.is_system = false AND a.tenant_id IS NOT NULL`) | N:M | `33/33` custom audiences, `15/15` users (`100.0%` High) | **MVP – APPROVED** |
| **RM-28** | `[:AUTHORED_BY]` | `:Post` | `:User` | `public.talk_posts` (`id`, `author_user_id`) | `p.id = tp.id` AND `u.id = tp.author_user_id` | N:1 | Verified logical ref (`talk_posts.author_user_id -> users.id`) | **MVP – APPROVED** |
| **RM-29** | `[:TARGETED_TO]` | `:Post` | `:Audience` | `public.talk_posts` (`id`, `audience_id`) | `p.id = tp.id` AND `a.id = tp.audience_id` (`WHERE (a.is_system = false AND a.tenant_id = p.tenant_id) OR (a.is_system = true AND a.tenant_id IS NULL)`) | N:1 | `81/81` distinct audiences (`100.0%` High) | **MVP – APPROVED** |
| **RM-30** | `[:ASSIGNED_TO]` | `:Asset` | `:User` | `public.assets` (`id`, `assigned_user_id`) | `a.id = ast.id` AND `u.id = ast.assigned_user_id` (`WHERE assigned_user_id IS NOT NULL`) | N:1 (Optional: 550/685) | `202/202` distinct users (`100.0%` High) | **MVP – APPROVED** |
| **RM-31** | `[:LOCATED_IN]` | `:Asset` | `:Department` | `public.assets` (`id`, `department_id`) | `a.id = ast.id` AND `d.id = ast.department_id` (`WHERE department_id IS NOT NULL`) | N:1 (Optional: 549/685) | `23/23` distinct depts (`100.0%` High) | **MVP – APPROVED** |
| **RM-32** | `[:CATEGORIZED_AS]` | `:Asset` | `:AssetCategory` | `public.assets` (`id`, `category_id`) | `a.id = ast.id` AND `c.id = ast.category_id` | N:1 | `11/11` distinct categories (`100.0%` High) | **MVP – APPROVED** |
| **RM-33** | `[:UPLOADED_BY]` | `:FileMetadata` | `:User` | `public.files` (`id`, `uploaded_by_user_id`) | `f.id = fl.id` AND `u.id = fl.uploaded_by_user_id` | N:1 | `188` distinct uploaders (`files.uploaded_by_user_id -> users.id`) | **MVP – APPROVED** |
| **RM-34** | `[:MEMBER_OF_CONVERSATION]` | `:User` | `:ChatConversation` | `public.chat_conversation_members` (`user_id`, `conversation_id`) | `u.id = ccm.user_id` AND `c.id = ccm.conversation_id` | N:M | `329/329` convs (`100%`), `177/205` users (`86.34%` Medium - 28 archived) | **MVP – APPROVED** |
| **RM-35** | `[:CREATED_BY]` | `:ChatConversation` | `:User` | `public.chat_conversations` (`id`, `created_by_user_id`) | `c.id = cc.id` AND `u.id = cc.created_by_user_id` | N:1 | `95/107` distinct creators (`88.79%` Medium - 12 archived) | **MVP – APPROVED** |
| **RM-36** | `[:HAS_LEAVE_BALANCE]` | `:User` | `:LeaveBalance` | `public.user_leave_year_balances` (`user_id`, `id`) | `u.id = yb.user_id` AND `lb.id = yb.id` (`user_unambiguous_leave_tenant` — **`CRITICAL-02`**) | 1:N (1 per year) | `353/353` users (`100.0%` High) | **MVP – APPROVED** |
| **RM-37** | `[:HAS_ATTENDANCE]` | `:User` | `:AttendanceRecord` | `public.attendance_daily_records` (`user_id`/`employee_code`, `id`) | 6-Step Active-Membership Resolution (`RESOLVED_BY_USER_ID` or unambiguous `RESOLVED_BY_EMPLOYEE_NUMBER` with `m.status = 'active' AND m.is_deleted = false` — **`CRITICAL-01`**); `u.id = ar.user_id` | 1:N | `100.0%` of loaded `:AttendanceRecord` nodes (`UNRESOLVED`/`AMBIGUOUS`/`INVALID_TENANT` quarantined) | **MVP – APPROVED** |
| **RM-38** | `[:HAS_CONTRACT]` | `:User` | `:ContractHistory` | `public.user_contract_histories` (`user_id`, `id`) | `u.id = ch.user_id` AND `c.id = ch.id` | 1:N | `351/351` users (`100.0%` High) | **MVP – APPROVED** |
| **RM-39** | `[:HAS_TAG]` | `:Project` | `:Tag` | `public.project_tags` (`project_id`, `id`) | `p.id = pt.project_id` AND `tg.tag_key = 'project:' || pt.id` | 1:N | `2/3` projects active (`66.67%` Medium - 1 project purged) | **MVP – APPROVED** (Semantic) |
| **RM-40** | `[:TAGGED_WITH]` | `:Ticket` | `:Tag` | `public.ticket_tags` (`ticket_id`, `tag_id`) | `t.id = tt.ticket_id` AND `tg.tag_key = 'project:' || tt.tag_id` | N:M | `8/8` tags (`100%`), `10/59` tickets active (`16.95%` Medium - 49 tickets purged) | **MVP – APPROVED** (Semantic) |
| **RM-41** | `[:TAGGED_WITH]` | `:Post` | `:Tag` | `public.talk_post_tags` (`post_id`, `tag_id`) | `p.id = tpt.post_id` AND `tg.tag_key = 'talk:' || tpt.tag_id` | N:M | `42` posts, `10` active `talk_tags` | **MVP – APPROVED** (Semantic) |
| **RM-42** | `[:ASSOCIATED_WITH]` | `:KnowledgeDocument` | `:Project` | `public.project_common_documents` (`id`, `project_id`) | `kd.id = pcd.id` AND `p.id = pcd.project_id` | N:1 | `7/7` projects (`100.0%` High) | **MVP – APPROVED** (Semantic) |
| **RM-43** | `[:STORED_AS_FILE]` | `:KnowledgeDocument` | `:FileMetadata` | `public.project_common_documents` (`id`, `file_id`) | `kd.id = pcd.id` AND `f.id = pcd.file_id` | 1:1 | `40/40` files (`100.0%` High) | **MVP – APPROVED** (Semantic) |
| **RM-44** | `[:COVERS_TOPIC]` | `:Notice` | `:Topic` | None (No physical table in PostgreSQL) | NLP extraction pipeline (Future) | N:M | Unverified (No source table) | **FUTURE** |
| **RM-45** | `[:REFERENCES_CONCEPT]` | `:KnowledgeDocument` | `:BusinessConcept` | None (No physical table in PostgreSQL) | Ontology extraction pipeline (Future) | N:M | Unverified (No source table) | **FUTURE** |

---

## 3. Executable SQL Extraction & Cypher Upsert Contracts (All 42 Approved MVP Relationships)

### RM-01: `(:User)-[:MEMBER_OF]->(:Tenant)`
- **Source Tables**: `public.tenant_user_memberships` LEFT JOIN `public.user_profiles` ON `(tenant_id, user_id)`
- **Null / Orphan / Duplicate / Update / Delete Rules**:
  - Unique active constraint: `ux_tenant_user_memberships_active_pair (tenant_id, user_id) WHERE is_deleted = false`.
  - Updates `status`, `is_default`, `is_deleted`, and tenant-scoped profile properties (`display_name`, `employee_number`, `department_id`, `position`, `grade`, `duty`, `is_resigned`, `attendance_mode`) via `ON MATCH SET`.
```sql
SELECT
  m.id AS membership_id,
  m.user_id,
  m.tenant_id,
  m.status,
  m.is_default,
  m.joined_at,
  m.is_deleted,
  up.display_name,
  up.employee_number,
  up.department_id,
  up.position,
  up.grade,
  up.duty,
  up.is_resigned,
  up.attendance_mode,
  m.updated_at
FROM public.tenant_user_memberships m
INNER JOIN public.users u ON u.id = m.user_id
INNER JOIN public.tenants t ON t.id = m.tenant_id
LEFT JOIN public.user_profiles up
  ON up.user_id = m.user_id
 AND up.tenant_id = m.tenant_id;
```
```cypher
UNWIND $batch AS row
MATCH (u:User {id: toInteger(row.user_id)})
MATCH (t:Tenant {id: toInteger(row.tenant_id)})
MERGE (u)-[m:MEMBER_OF]->(t)
ON CREATE SET
  m.id = toInteger(row.membership_id),
  m.tenant_id = toInteger(row.tenant_id),
  m.status = row.status,
  m.is_default = row.is_default,
  m.joined_at = CASE WHEN row.joined_at IS NOT NULL THEN datetime(row.joined_at) ELSE null END,
  m.is_deleted = row.is_deleted,
  m.display_name = row.display_name,
  m.employee_number = row.employee_number,
  m.department_id = CASE WHEN row.department_id IS NOT NULL THEN toInteger(row.department_id) ELSE null END,
  m.position = row.position,
  m.grade = row.grade,
  m.duty = row.duty,
  m.is_resigned = row.is_resigned,
  m.attendance_mode = row.attendance_mode,
  m.updated_at = datetime(row.updated_at),
  m.last_synced_at = datetime()
ON MATCH SET
  m.id = toInteger(row.membership_id),
  m.status = row.status,
  m.is_default = row.is_default,
  m.is_deleted = row.is_deleted,
  m.display_name = row.display_name,
  m.employee_number = row.employee_number,
  m.department_id = CASE WHEN row.department_id IS NOT NULL THEN toInteger(row.department_id) ELSE null END,
  m.position = row.position,
  m.grade = row.grade,
  m.duty = row.duty,
  m.is_resigned = row.is_resigned,
  m.attendance_mode = row.attendance_mode,
  m.updated_at = datetime(row.updated_at),
  m.last_synced_at = datetime();
```

### RM-02: `(:Department)-[:BELONGS_TO_TENANT]->(:Tenant)`
```sql
SELECT
  d.id AS department_id,
  d.tenant_id
FROM public.departments d
INNER JOIN public.tenants t ON t.id = d.tenant_id;
```
```cypher
UNWIND $batch AS row
MATCH (d:Department {id: toInteger(row.department_id)})
MATCH (t:Tenant {id: toInteger(row.tenant_id)})
WHERE d.tenant_id = t.id
MERGE (d)-[r:BELONGS_TO_TENANT]->(t)
ON CREATE SET r.last_synced_at = datetime()
ON MATCH SET r.last_synced_at = datetime();
```

### RM-03: `(:User)-[:MEMBER_OF_DEPARTMENT]->(:Department)` (DEFECT 06 Lifecycle Filtering Support)
- **Lifecycle Semantics**: Synchronizes all `397` rows (`349` active where `effective_to IS NULL` -> `m.is_active = true`; `48` historical where `effective_to IS NOT NULL` -> `m.is_active = false`). Current-state queries (`Q01`, `Q08`, `Q13`) filter `m.is_active = true AND m.tenant_id = $tenant_id`.
```sql
SELECT
  dm.id,
  dm.user_id,
  dm.department_id,
  dm.tenant_id,
  dm.role_in_department,
  dm.is_primary,
  dm.effective_from,
  dm.effective_to,
  dm.updated_at
FROM public.department_members dm
INNER JOIN public.users u ON u.id = dm.user_id
INNER JOIN public.departments d ON d.id = dm.department_id
WHERE dm.tenant_id = d.tenant_id;
```
```cypher
UNWIND $batch AS row
MATCH (u:User {id: toInteger(row.user_id)})
MATCH (d:Department {id: toInteger(row.department_id), tenant_id: toInteger(row.tenant_id)})
WHERE EXISTS {
  MATCH (u)-[:MEMBER_OF {is_deleted: false}]->(:Tenant {id: d.tenant_id})
}
MERGE (u)-[m:MEMBER_OF_DEPARTMENT {id: toInteger(row.id)}]->(d)
ON CREATE SET
  m.tenant_id = toInteger(row.tenant_id),
  m.role_in_department = row.role_in_department,
  m.is_primary = row.is_primary,
  m.effective_from = date(row.effective_from),
  m.effective_to = CASE WHEN row.effective_to IS NOT NULL THEN date(row.effective_to) ELSE null END,
  m.is_active = (row.effective_to IS NULL),
  m.updated_at = datetime(row.updated_at),
  m.last_synced_at = datetime()
ON MATCH SET
  m.tenant_id = toInteger(row.tenant_id),
  m.role_in_department = row.role_in_department,
  m.is_primary = row.is_primary,
  m.effective_from = date(row.effective_from),
  m.effective_to = CASE WHEN row.effective_to IS NOT NULL THEN date(row.effective_to) ELSE null END,
  m.is_active = (row.effective_to IS NULL),
  m.updated_at = datetime(row.updated_at),
  m.last_synced_at = datetime();
```

### RM-04: `(:User)-[:MANAGES]->(:Department)` (HIGH-05 Active Manager Tenant Membership Guard)
- **HIGH-05 Resolution**: Requires the department manager `u` to be an active, non-deleted user (`u.is_active = true AND u.is_deleted = false`) with an active, non-deleted tenant membership in `d.tenant_id` (`m.status = 'active' AND m.is_deleted = false`).
```sql
SELECT
  d.id AS department_id,
  d.manager_user_id,
  d.tenant_id
FROM public.departments d
INNER JOIN public.users u
  ON u.id = d.manager_user_id
 AND COALESCE(u.is_active, false) = true
 AND COALESCE(u.is_deleted, false) = false
INNER JOIN public.tenant_user_memberships m
  ON m.user_id = d.manager_user_id
 AND m.tenant_id = d.tenant_id
 AND m.status = 'active'
 AND m.is_deleted = false
WHERE d.manager_user_id IS NOT NULL;
```
```cypher
UNWIND $batch AS row
MATCH (u:User {id: toInteger(row.manager_user_id), is_active: true, is_deleted: false})
MATCH (d:Department {id: toInteger(row.department_id), tenant_id: toInteger(row.tenant_id)})
WHERE EXISTS {
  MATCH (u)-[:MEMBER_OF {status: 'active', is_deleted: false}]->(:Tenant {id: d.tenant_id, is_deleted: false})
}
MERGE (u)-[r:MANAGES]->(d)
ON CREATE SET r.tenant_id = toInteger(row.tenant_id), r.last_synced_at = datetime()
ON MATCH SET r.tenant_id = toInteger(row.tenant_id), r.last_synced_at = datetime();
```

### RM-05: `(:Department)-[:SUB_DEPARTMENT_OF]->(:Department)`
```sql
SELECT
  child.id AS child_id,
  child.parent_id AS parent_id,
  child.tenant_id
FROM public.departments child
INNER JOIN public.departments parent ON parent.id = child.parent_id
WHERE child.parent_id IS NOT NULL
  AND child.tenant_id = parent.tenant_id;
```
```cypher
UNWIND $batch AS row
MATCH (child:Department {id: toInteger(row.child_id), tenant_id: toInteger(row.tenant_id)})
MATCH (parent:Department {id: toInteger(row.parent_id), tenant_id: toInteger(row.tenant_id)})
MERGE (child)-[r:SUB_DEPARTMENT_OF]->(parent)
ON CREATE SET r.tenant_id = toInteger(row.tenant_id), r.last_synced_at = datetime()
ON MATCH SET r.last_synced_at = datetime();
```

### RM-06: `(:User)-[:HAS_ROLE]->(:Role)`
```sql
SELECT
  ura.id,
  ura.user_id,
  ura.role_id,
  ura.tenant_id,
  ura.assigned_at,
  ura.assigned_by
FROM public.user_role_assignments ura
INNER JOIN public.users u ON u.id = ura.user_id
INNER JOIN public.roles r ON r.id = ura.role_id
WHERE ura.tenant_id = r.tenant_id;
```
```cypher
UNWIND $batch AS row
MATCH (u:User {id: toInteger(row.user_id)})
MATCH (r:Role {id: toInteger(row.role_id), tenant_id: toInteger(row.tenant_id)})
WHERE EXISTS {
  MATCH (u)-[:MEMBER_OF {is_deleted: false}]->(:Tenant {id: r.tenant_id})
}
MERGE (u)-[rel:HAS_ROLE {tenant_id: toInteger(row.tenant_id)}]->(r)
ON CREATE SET
  rel.id = toInteger(row.id),
  rel.assigned_at = CASE WHEN row.assigned_at IS NOT NULL THEN datetime(row.assigned_at) ELSE null END,
  rel.assigned_by = CASE WHEN row.assigned_by IS NOT NULL THEN toInteger(row.assigned_by) ELSE null END,
  rel.last_synced_at = datetime()
ON MATCH SET
  rel.assigned_at = CASE WHEN row.assigned_at IS NOT NULL THEN datetime(row.assigned_at) ELSE null END,
  rel.assigned_by = CASE WHEN row.assigned_by IS NOT NULL THEN toInteger(row.assigned_by) ELSE null END,
  rel.last_synced_at = datetime();
```

### RM-07: `(:Role)-[:INCLUDES_PERMISSION]->(:Permission)`
```sql
SELECT
  rp.id,
  rp.role_id,
  rp.permission_id,
  rp.tenant_id,
  COALESCE(rp.is_granted, false) AS is_granted,
  rp.granted_at,
  rp.granted_by
FROM public.role_permissions rp
INNER JOIN public.roles r ON r.id = rp.role_id
INNER JOIN public.permissions p ON p.id = rp.permission_id
WHERE rp.tenant_id = r.tenant_id;
```
```cypher
UNWIND $batch AS row
MATCH (r:Role {id: toInteger(row.role_id), tenant_id: toInteger(row.tenant_id)})
MATCH (p:Permission {id: toInteger(row.permission_id)})
MERGE (r)-[rel:INCLUDES_PERMISSION {tenant_id: toInteger(row.tenant_id)}]->(p)
ON CREATE SET
  rel.id = toInteger(row.id),
  rel.is_granted = row.is_granted,
  rel.granted_at = CASE WHEN row.granted_at IS NOT NULL THEN datetime(row.granted_at) ELSE null END,
  rel.granted_by = CASE WHEN row.granted_by IS NOT NULL THEN toInteger(row.granted_by) ELSE null END,
  rel.last_synced_at = datetime()
ON MATCH SET
  rel.is_granted = row.is_granted,
  rel.granted_at = CASE WHEN row.granted_at IS NOT NULL THEN datetime(row.granted_at) ELSE null END,
  rel.granted_by = CASE WHEN row.granted_by IS NOT NULL THEN toInteger(row.granted_by) ELSE null END,
  rel.last_synced_at = datetime();
```

### RM-08: `(:User)-[:DIRECT_PERMISSION]->(:Permission)`
```sql
SELECT
  up.id,
  up.user_id,
  up.permission_id,
  up.tenant_id,
  COALESCE(up.is_granted, false) AS is_granted,
  up.granted_at,
  up.granted_by
FROM public.user_permissions up
INNER JOIN public.users u ON u.id = up.user_id
INNER JOIN public.permissions p ON p.id = up.permission_id;
```
```cypher
UNWIND $batch AS row
MATCH (u:User {id: toInteger(row.user_id)})
MATCH (p:Permission {id: toInteger(row.permission_id)})
WHERE EXISTS {
  MATCH (u)-[:MEMBER_OF {is_deleted: false}]->(:Tenant {id: toInteger(row.tenant_id)})
}
MERGE (u)-[rel:DIRECT_PERMISSION {tenant_id: toInteger(row.tenant_id)}]->(p)
ON CREATE SET
  rel.id = toInteger(row.id),
  rel.is_granted = row.is_granted,
  rel.granted_at = CASE WHEN row.granted_at IS NOT NULL THEN datetime(row.granted_at) ELSE null END,
  rel.granted_by = CASE WHEN row.granted_by IS NOT NULL THEN toInteger(row.granted_by) ELSE null END,
  rel.last_synced_at = datetime()
ON MATCH SET
  rel.is_granted = row.is_granted,
  rel.granted_at = CASE WHEN row.granted_at IS NOT NULL THEN datetime(row.granted_at) ELSE null END,
  rel.granted_by = CASE WHEN row.granted_by IS NOT NULL THEN toInteger(row.granted_by) ELSE null END,
  rel.last_synced_at = datetime();
```

### RM-09: `(:Project)-[:CREATED_BY]->(:User)`
```sql
SELECT
  p.id AS project_id,
  p.created_by_user_id AS user_id
FROM public.projects p
INNER JOIN public.users u ON u.id = p.created_by_user_id;
```
```cypher
UNWIND $batch AS row
MATCH (p:Project {id: toInteger(row.project_id)})
MATCH (u:User {id: toInteger(row.user_id)})
WHERE EXISTS {
  MATCH (u)-[:MEMBER_OF]->(:Tenant {id: p.tenant_id})
}
MERGE (p)-[r:CREATED_BY]->(u)
ON CREATE SET r.last_synced_at = datetime()
ON MATCH SET r.last_synced_at = datetime();
```

### RM-10: `(:User)-[:MEMBER_OF_PROJECT]->(:Project)`
```sql
SELECT
  pm.id,
  pm.project_id,
  pm.user_id,
  pm.role,
  pm.joined_at,
  pm.invited_by_user_id
FROM public.project_members pm
INNER JOIN public.projects p ON p.id = pm.project_id
INNER JOIN public.users u ON u.id = pm.user_id;
```
```cypher
UNWIND $batch AS row
MATCH (u:User {id: toInteger(row.user_id)})
MATCH (p:Project {id: toInteger(row.project_id)})
WHERE EXISTS {
  MATCH (u)-[:MEMBER_OF {is_deleted: false}]->(:Tenant {id: p.tenant_id})
}
MERGE (u)-[m:MEMBER_OF_PROJECT]->(p)
ON CREATE SET
  m.id = toInteger(row.id),
  m.role = row.role,
  m.joined_at = CASE WHEN row.joined_at IS NOT NULL THEN datetime(row.joined_at) ELSE null END,
  m.invited_by_user_id = CASE WHEN row.invited_by_user_id IS NOT NULL THEN toInteger(row.invited_by_user_id) ELSE null END,
  m.last_synced_at = datetime()
ON MATCH SET
  m.role = row.role,
  m.joined_at = CASE WHEN row.joined_at IS NOT NULL THEN datetime(row.joined_at) ELSE null END,
  m.invited_by_user_id = CASE WHEN row.invited_by_user_id IS NOT NULL THEN toInteger(row.invited_by_user_id) ELSE null END,
  m.last_synced_at = datetime();
```

### RM-11: `(:Ticket)-[:BELONGS_TO_PROJECT]->(:Project)`
```sql
SELECT
  t.id AS ticket_id,
  t.project_id
FROM public.tickets t
INNER JOIN public.projects p ON p.id = t.project_id;
```
```cypher
UNWIND $batch AS row
MATCH (t:Ticket {id: toInteger(row.ticket_id)})
MATCH (p:Project {id: toInteger(row.project_id)})
WHERE t.tenant_id = p.tenant_id
MERGE (t)-[r:BELONGS_TO_PROJECT]->(p)
ON CREATE SET r.last_synced_at = datetime()
ON MATCH SET r.last_synced_at = datetime();
```

### RM-12: `(:Ticket)-[:CREATED_BY]->(:User)`
```sql
SELECT
  t.id AS ticket_id,
  t.created_by_user_id AS user_id
FROM public.tickets t
INNER JOIN public.users u ON u.id = t.created_by_user_id;
```
```cypher
UNWIND $batch AS row
MATCH (t:Ticket {id: toInteger(row.ticket_id)})
MATCH (u:User {id: toInteger(row.user_id)})
WHERE EXISTS {
  MATCH (u)-[:MEMBER_OF]->(:Tenant {id: t.tenant_id})
}
MERGE (t)-[r:CREATED_BY]->(u)
ON CREATE SET r.last_synced_at = datetime()
ON MATCH SET r.last_synced_at = datetime();
```

### RM-13: `(:Ticket)-[:ASSIGNED_TO]->(:User)`
```sql
SELECT
  ta.id,
  ta.ticket_id,
  ta.user_id,
  ta.assigned_at,
  ta.assigned_by_user_id
FROM public.ticket_assignees ta
INNER JOIN public.tickets t ON t.id = ta.ticket_id
INNER JOIN public.users u ON u.id = ta.user_id;
```
```cypher
UNWIND $batch AS row
MATCH (t:Ticket {id: toInteger(row.ticket_id)})
MATCH (u:User {id: toInteger(row.user_id)})
WHERE EXISTS {
  MATCH (u)-[:MEMBER_OF {is_deleted: false}]->(:Tenant {id: t.tenant_id})
}
MERGE (t)-[r:ASSIGNED_TO]->(u)
ON CREATE SET
  r.id = toInteger(row.id),
  r.assigned_at = CASE WHEN row.assigned_at IS NOT NULL THEN datetime(row.assigned_at) ELSE null END,
  r.assigned_by_user_id = CASE WHEN row.assigned_by_user_id IS NOT NULL THEN toInteger(row.assigned_by_user_id) ELSE null END,
  r.last_synced_at = datetime()
ON MATCH SET
  r.assigned_at = CASE WHEN row.assigned_at IS NOT NULL THEN datetime(row.assigned_at) ELSE null END,
  r.assigned_by_user_id = CASE WHEN row.assigned_by_user_id IS NOT NULL THEN toInteger(row.assigned_by_user_id) ELSE null END,
  r.last_synced_at = datetime();
```

### RM-14: `(:Ticket)-[:PART_OF_SPRINT]->(:Sprint)`
```sql
SELECT
  t.id AS ticket_id,
  t.sprint_id
FROM public.tickets t
INNER JOIN public.project_sprints s ON s.id = t.sprint_id
WHERE t.sprint_id IS NOT NULL
  AND t.project_id = s.project_id;
```
```cypher
UNWIND $batch AS row
MATCH (t:Ticket {id: toInteger(row.ticket_id)})
MATCH (s:Sprint {id: toInteger(row.sprint_id)})
WHERE t.tenant_id = s.tenant_id AND t.project_id = s.project_id
MERGE (t)-[r:PART_OF_SPRINT]->(s)
ON CREATE SET r.last_synced_at = datetime()
ON MATCH SET r.last_synced_at = datetime();
```

### RM-15: `(:Ticket)-[:IN_STAGE]->(:KanbanColumn)`
```sql
SELECT
  t.id AS ticket_id,
  t.column_id
FROM public.tickets t
INNER JOIN public.kanban_columns k ON k.id = t.column_id
WHERE t.column_id IS NOT NULL
  AND t.project_id = k.project_id;
```
```cypher
UNWIND $batch AS row
MATCH (t:Ticket {id: toInteger(row.ticket_id)})
MATCH (k:KanbanColumn {id: toInteger(row.column_id)})
WHERE t.tenant_id = k.tenant_id AND t.project_id = k.project_id
MERGE (t)-[r:IN_STAGE]->(k)
ON CREATE SET r.last_synced_at = datetime()
ON MATCH SET r.last_synced_at = datetime();
```

### RM-16: `(:Sprint)-[:SPRINT_OF_PROJECT]->(:Project)`
```sql
SELECT
  s.id AS sprint_id,
  s.project_id
FROM public.project_sprints s
INNER JOIN public.projects p ON p.id = s.project_id;
```
```cypher
UNWIND $batch AS row
MATCH (s:Sprint {id: toInteger(row.sprint_id)})
MATCH (p:Project {id: toInteger(row.project_id)})
WHERE s.tenant_id = p.tenant_id
MERGE (s)-[r:SPRINT_OF_PROJECT]->(p)
ON CREATE SET r.last_synced_at = datetime()
ON MATCH SET r.last_synced_at = datetime();
```

### RM-17: `(:KanbanColumn)-[:COLUMN_OF_PROJECT]->(:Project)`
```sql
SELECT
  k.id AS column_id,
  k.project_id
FROM public.kanban_columns k
INNER JOIN public.projects p ON p.id = k.project_id;
```
```cypher
UNWIND $batch AS row
MATCH (k:KanbanColumn {id: toInteger(row.column_id)})
MATCH (p:Project {id: toInteger(row.project_id)})
WHERE k.tenant_id = p.tenant_id
MERGE (k)-[r:COLUMN_OF_PROJECT]->(p)
ON CREATE SET r.last_synced_at = datetime()
ON MATCH SET r.last_synced_at = datetime();
```

### RM-18: `(:ApprovalRequest)-[:CREATED_BY]->(:User)`
```sql
SELECT
  a.id AS request_id,
  a.created_by_user_id AS user_id
FROM public.approval_requests a
INNER JOIN public.users u ON u.id = a.created_by_user_id;
```
```cypher
UNWIND $batch AS row
MATCH (a:ApprovalRequest {id: toInteger(row.request_id)})
MATCH (u:User {id: toInteger(row.user_id)})
WHERE EXISTS {
  MATCH (u)-[:MEMBER_OF]->(:Tenant {id: a.tenant_id})
}
MERGE (a)-[r:CREATED_BY]->(u)
ON CREATE SET r.last_synced_at = datetime()
ON MATCH SET r.last_synced_at = datetime();
```

### RM-20: `(:User)-[:PARTICIPATES_IN]->(:ApprovalRequest)` (DEFECT 03 Verified Physical Columns)
- **Verified Physical Columns on `public.approval_participants`**: `id`, `request_id`, `user_id`, `participant_role`, `sequence_order`, `action_status`, `acted_at`, `created_at` (`note` excluded per Tier 1 data minimization; `step_order`, `step_name`, `is_required` do not exist on `approval_participants`).
```sql
SELECT
  ap.id,
  ap.request_id,
  ap.user_id,
  ap.participant_role,
  ap.sequence_order,
  ap.action_status,
  ap.acted_at,
  ap.created_at
FROM public.approval_participants ap
INNER JOIN public.approval_requests a ON a.id = ap.request_id
INNER JOIN public.users u ON u.id = ap.user_id;
```
```cypher
UNWIND $batch AS row
MATCH (u:User {id: toInteger(row.user_id)})
MATCH (a:ApprovalRequest {id: toInteger(row.request_id)})
WHERE EXISTS {
  MATCH (u)-[:MEMBER_OF {is_deleted: false}]->(:Tenant {id: a.tenant_id})
}
MERGE (u)-[p:PARTICIPATES_IN {participant_role: row.participant_role}]->(a)
ON CREATE SET
  p.id = toInteger(row.id),
  p.sequence_order = toInteger(row.sequence_order),
  p.action_status = row.action_status,
  p.acted_at = CASE WHEN row.acted_at IS NOT NULL THEN datetime(row.acted_at) ELSE null END,
  p.created_at = CASE WHEN row.created_at IS NOT NULL THEN datetime(row.created_at) ELSE null END,
  p.last_synced_at = datetime()
ON MATCH SET
  p.id = toInteger(row.id),
  p.sequence_order = toInteger(row.sequence_order),
  p.action_status = row.action_status,
  p.acted_at = CASE WHEN row.acted_at IS NOT NULL THEN datetime(row.acted_at) ELSE null END,
  p.created_at = CASE WHEN row.created_at IS NOT NULL THEN datetime(row.created_at) ELSE null END,
  p.last_synced_at = datetime();
```

### RM-21: `(:ScheduleEvent)-[:ORGANIZED_BY]->(:User)`
```sql
SELECT
  e.id AS event_id,
  e.user_id
FROM public.schedule_events e
INNER JOIN public.users u ON u.id = e.user_id;
```
```cypher
UNWIND $batch AS row
MATCH (e:ScheduleEvent {id: toInteger(row.event_id)})
MATCH (u:User {id: toInteger(row.user_id)})
WHERE EXISTS {
  MATCH (u)-[:MEMBER_OF]->(:Tenant {id: e.tenant_id})
}
MERGE (e)-[r:ORGANIZED_BY]->(u)
ON CREATE SET r.last_synced_at = datetime()
ON MATCH SET r.last_synced_at = datetime();
```

### RM-22: `(:ScheduleEvent)-[:HELD_IN]->(:ScheduleRoom)`
```sql
SELECT
  e.id AS event_id,
  e.room_id
FROM public.schedule_events e
INNER JOIN public.schedule_rooms r ON r.id = e.room_id
WHERE e.room_id IS NOT NULL;
```
```cypher
UNWIND $batch AS row
MATCH (e:ScheduleEvent {id: toInteger(row.event_id)})
MATCH (r:ScheduleRoom {id: toInteger(row.room_id)})
MERGE (e)-[rel:HELD_IN]->(r)
ON CREATE SET rel.last_synced_at = datetime()
ON MATCH SET rel.last_synced_at = datetime();
```

### RM-23: `(:User)-[:ATTENDS_EVENT]->(:ScheduleEvent)`
```sql
SELECT
  sep.id,
  sep.event_id,
  sep.user_id,
  sep.status,
  COALESCE(sep.is_required, false) AS is_required,
  sep.updated_at
FROM public.schedule_event_participants sep
INNER JOIN public.schedule_events e ON e.id = sep.event_id
INNER JOIN public.users u ON u.id = sep.user_id;
```
```cypher
UNWIND $batch AS row
MATCH (u:User {id: toInteger(row.user_id)})
MATCH (e:ScheduleEvent {id: toInteger(row.event_id)})
WHERE EXISTS {
  MATCH (u)-[:MEMBER_OF {is_deleted: false}]->(:Tenant {id: e.tenant_id})
}
MERGE (u)-[r:ATTENDS_EVENT]->(e)
ON CREATE SET
  r.id = toInteger(row.id),
  r.status = row.status,
  r.is_required = row.is_required,
  r.updated_at = CASE WHEN row.updated_at IS NOT NULL THEN datetime(row.updated_at) ELSE null END,
  r.last_synced_at = datetime()
ON MATCH SET
  r.status = row.status,
  r.is_required = row.is_required,
  r.updated_at = CASE WHEN row.updated_at IS NOT NULL THEN datetime(row.updated_at) ELSE null END,
  r.last_synced_at = datetime();
```

### RM-24: `(:Notice)-[:PUBLISHED_BY]->(:User)`
```sql
SELECT
  n.id AS notice_id,
  n.created_by_user_id AS user_id
FROM public.notices n
INNER JOIN public.users u ON u.id = n.created_by_user_id;
```
```cypher
UNWIND $batch AS row
MATCH (n:Notice {id: toInteger(row.notice_id)})
MATCH (u:User {id: toInteger(row.user_id)})
WHERE EXISTS {
  MATCH (u)-[:MEMBER_OF]->(:Tenant {id: n.tenant_id})
}
MERGE (n)-[r:PUBLISHED_BY]->(u)
ON CREATE SET r.last_synced_at = datetime()
ON MATCH SET r.last_synced_at = datetime();
```

### RM-25: `(:Notice)-[:TARGETED_TO]->(:Audience)` (DEFECT 04 Dual-Scope Guard)
```sql
SELECT
  n.id AS notice_id,
  n.audience_id
FROM public.notices n
INNER JOIN public.audiences a ON a.id = n.audience_id
WHERE n.audience_id IS NOT NULL;
```
```cypher
UNWIND $batch AS row
MATCH (n:Notice {id: toInteger(row.notice_id)})
MATCH (a:Audience {id: toInteger(row.audience_id)})
WHERE (a.is_system = false AND a.tenant_id = n.tenant_id)
   OR (a.is_system = true AND a.tenant_id IS NULL)
MERGE (n)-[r:TARGETED_TO]->(a)
ON CREATE SET r.last_synced_at = datetime()
ON MATCH SET r.last_synced_at = datetime();
```

### RM-26: `(:Audience)-[:INCLUDES_DEPARTMENT]->(:Department)` (DEFECT 04 Custom Audience Guard)
```sql
SELECT
  adm.id,
  adm.audience_id,
  adm.department_id,
  adm.created_at
FROM public.audience_department_members adm
INNER JOIN public.audiences a ON a.id = adm.audience_id
INNER JOIN public.departments d ON d.id = adm.department_id
WHERE COALESCE(a.is_system, false) = false;
```
```cypher
UNWIND $batch AS row
MATCH (a:Audience {id: toInteger(row.audience_id)})
MATCH (d:Department {id: toInteger(row.department_id)})
WHERE a.is_system = false
  AND a.tenant_id IS NOT NULL
  AND a.tenant_id = d.tenant_id
MERGE (a)-[r:INCLUDES_DEPARTMENT]->(d)
ON CREATE SET r.id = toInteger(row.id), r.created_at = datetime(row.created_at), r.last_synced_at = datetime()
ON MATCH SET r.last_synced_at = datetime();
```

### RM-27: `(:Audience)-[:INCLUDES_USER]->(:User)` (DEFECT 04 Custom Audience Guard)
```sql
SELECT
  aum.id,
  aum.audience_id,
  aum.user_id,
  aum.created_at
FROM public.audience_user_members aum
INNER JOIN public.audiences a ON a.id = aum.audience_id
INNER JOIN public.users u ON u.id = aum.user_id
WHERE COALESCE(a.is_system, false) = false;
```
```cypher
UNWIND $batch AS row
MATCH (a:Audience {id: toInteger(row.audience_id)})
MATCH (u:User {id: toInteger(row.user_id)})
WHERE a.is_system = false
  AND a.tenant_id IS NOT NULL
  AND EXISTS {
    MATCH (u)-[:MEMBER_OF {is_deleted: false}]->(:Tenant {id: a.tenant_id})
  }
MERGE (a)-[r:INCLUDES_USER]->(u)
ON CREATE SET r.id = toInteger(row.id), r.created_at = datetime(row.created_at), r.last_synced_at = datetime()
ON MATCH SET r.last_synced_at = datetime();
```

### RM-28: `(:Post)-[:AUTHORED_BY]->(:User)`
```sql
SELECT
  p.id AS post_id,
  p.author_user_id AS user_id
FROM public.talk_posts p
INNER JOIN public.users u ON u.id = p.author_user_id;
```
```cypher
UNWIND $batch AS row
MATCH (p:Post {id: toInteger(row.post_id)})
MATCH (u:User {id: toInteger(row.user_id)})
WHERE EXISTS {
  MATCH (u)-[:MEMBER_OF]->(:Tenant {id: p.tenant_id})
}
MERGE (p)-[r:AUTHORED_BY]->(u)
ON CREATE SET r.last_synced_at = datetime()
ON MATCH SET r.last_synced_at = datetime();
```

### RM-29: `(:Post)-[:TARGETED_TO]->(:Audience)` (DEFECT 04 Dual-Scope Guard)
```sql
SELECT
  p.id AS post_id,
  p.audience_id
FROM public.talk_posts p
INNER JOIN public.audiences a ON a.id = p.audience_id
WHERE p.audience_id IS NOT NULL;
```
```cypher
UNWIND $batch AS row
MATCH (p:Post {id: toInteger(row.post_id)})
MATCH (a:Audience {id: toInteger(row.audience_id)})
WHERE (a.is_system = false AND a.tenant_id = p.tenant_id)
   OR (a.is_system = true AND a.tenant_id IS NULL)
MERGE (p)-[r:TARGETED_TO]->(a)
ON CREATE SET r.last_synced_at = datetime()
ON MATCH SET r.last_synced_at = datetime();
```

### RM-30: `(:Asset)-[:ASSIGNED_TO]->(:User)`
```sql
SELECT
  a.id AS asset_id,
  a.assigned_user_id AS user_id
FROM public.assets a
INNER JOIN public.users u ON u.id = a.assigned_user_id
WHERE a.assigned_user_id IS NOT NULL;
```
```cypher
UNWIND $batch AS row
MATCH (a:Asset {id: toInteger(row.asset_id)})
MATCH (u:User {id: toInteger(row.user_id)})
WHERE EXISTS {
  MATCH (u)-[:MEMBER_OF {is_deleted: false}]->(:Tenant {id: a.tenant_id})
}
MERGE (a)-[r:ASSIGNED_TO]->(u)
ON CREATE SET r.last_synced_at = datetime()
ON MATCH SET r.last_synced_at = datetime();
```

### RM-31: `(:Asset)-[:LOCATED_IN]->(:Department)`
```sql
SELECT
  a.id AS asset_id,
  a.department_id
FROM public.assets a
INNER JOIN public.departments d ON d.id = a.department_id
WHERE a.department_id IS NOT NULL;
```
```cypher
UNWIND $batch AS row
MATCH (a:Asset {id: toInteger(row.asset_id)})
MATCH (d:Department {id: toInteger(row.department_id)})
WHERE a.tenant_id = d.tenant_id
MERGE (a)-[r:LOCATED_IN]->(d)
ON CREATE SET r.last_synced_at = datetime()
ON MATCH SET r.last_synced_at = datetime();
```

### RM-32: `(:Asset)-[:CATEGORIZED_AS]->(:AssetCategory)`
```sql
SELECT
  a.id AS asset_id,
  a.category_id
FROM public.assets a
INNER JOIN public.asset_categories c ON c.id = a.category_id;
```
```cypher
UNWIND $batch AS row
MATCH (a:Asset {id: toInteger(row.asset_id)})
MATCH (c:AssetCategory {id: toInteger(row.category_id)})
MERGE (a)-[r:CATEGORIZED_AS]->(c)
ON CREATE SET r.last_synced_at = datetime()
ON MATCH SET r.last_synced_at = datetime();
```

### RM-33: `(:FileMetadata)-[:UPLOADED_BY]->(:User)`
```sql
SELECT
  f.id AS file_id,
  f.uploaded_by_user_id AS user_id
FROM public.files f
INNER JOIN public.users u ON u.id = f.uploaded_by_user_id
WHERE f.uploaded_by_user_id IS NOT NULL;
```
```cypher
UNWIND $batch AS row
MATCH (f:FileMetadata {id: toInteger(row.file_id)})
MATCH (u:User {id: toInteger(row.user_id)})
WHERE EXISTS {
  MATCH (u)-[:MEMBER_OF]->(:Tenant {id: f.tenant_id})
}
MERGE (f)-[r:UPLOADED_BY]->(u)
ON CREATE SET r.last_synced_at = datetime()
ON MATCH SET r.last_synced_at = datetime();
```

### RM-34: `(:User)-[:MEMBER_OF_CONVERSATION]->(:ChatConversation)`
```sql
SELECT
  ccm.id,
  ccm.conversation_id,
  ccm.user_id,
  ccm.role,
  ccm.joined_at,
  ccm.is_pinned,
  ccm.is_muted,
  ccm.is_deleted
FROM public.chat_conversation_members ccm
INNER JOIN public.chat_conversations c ON c.id = ccm.conversation_id
INNER JOIN public.users u ON u.id = ccm.user_id;
```
```cypher
UNWIND $batch AS row
MATCH (u:User {id: toInteger(row.user_id)})
MATCH (c:ChatConversation {id: toInteger(row.conversation_id)})
WHERE EXISTS {
  MATCH (u)-[:MEMBER_OF {is_deleted: false}]->(:Tenant {id: c.tenant_id})
}
MERGE (u)-[m:MEMBER_OF_CONVERSATION]->(c)
ON CREATE SET
  m.id = toInteger(row.id),
  m.role = row.role,
  m.joined_at = CASE WHEN row.joined_at IS NOT NULL THEN datetime(row.joined_at) ELSE null END,
  m.is_pinned = row.is_pinned,
  m.is_muted = row.is_muted,
  m.is_deleted = row.is_deleted,
  m.last_synced_at = datetime()
ON MATCH SET
  m.role = row.role,
  m.is_pinned = row.is_pinned,
  m.is_muted = row.is_muted,
  m.is_deleted = row.is_deleted,
  m.last_synced_at = datetime();
```

### RM-35: `(:ChatConversation)-[:CREATED_BY]->(:User)`
```sql
SELECT
  c.id AS conversation_id,
  c.created_by_user_id AS user_id
FROM public.chat_conversations c
INNER JOIN public.users u ON u.id = c.created_by_user_id
WHERE c.created_by_user_id IS NOT NULL;
```
```cypher
UNWIND $batch AS row
MATCH (c:ChatConversation {id: toInteger(row.conversation_id)})
MATCH (u:User {id: toInteger(row.user_id)})
WHERE EXISTS {
  MATCH (u)-[:MEMBER_OF]->(:Tenant {id: c.tenant_id})
}
MERGE (c)-[r:CREATED_BY]->(u)
ON CREATE SET r.last_synced_at = datetime()
ON MATCH SET r.last_synced_at = datetime();
```

### RM-36: `(:User)-[:HAS_LEAVE_BALANCE]->(:LeaveBalance)` (CRITICAL-02 Unambiguous Leave Tenant Alignment)
- **Strict Alignment with `Doc 29` Section 3.2 and `Doc 30` `NM-21`**:
  - Uses `user_unambiguous_leave_tenant` (`tenant_user_memberships` + `user_profiles`, `COUNT(DISTINCT tenant_id) = 1`) so every `[:HAS_LEAVE_BALANCE]` edge matches `NM-21` 1:1 and multi-tenant ambiguity is quarantined.
```sql
WITH user_unambiguous_leave_tenant AS (
  SELECT
    m.user_id,
    min(m.tenant_id) AS tenant_id
  FROM public.tenant_user_memberships m
  INNER JOIN public.users u
    ON u.id = m.user_id
   AND COALESCE(u.is_deleted, false) = false
  INNER JOIN public.user_profiles up
    ON up.user_id = m.user_id
   AND up.tenant_id = m.tenant_id
  WHERE m.is_deleted = false
    AND m.status IN ('active', 'inactive', 'suspended')
  GROUP BY m.user_id
  HAVING count(DISTINCT m.tenant_id) = 1
)
SELECT
  yb.id AS leave_balance_id,
  yb.user_id,
  ult.tenant_id
FROM public.user_leave_year_balances yb
INNER JOIN user_unambiguous_leave_tenant ult ON ult.user_id = yb.user_id;
```
```cypher
UNWIND $batch AS row
MATCH (u:User {id: toInteger(row.user_id)})
MATCH (lb:LeaveBalance {id: toInteger(row.leave_balance_id), tenant_id: toInteger(row.tenant_id)})
WHERE EXISTS {
  MATCH (u)-[:MEMBER_OF {is_deleted: false}]->(:Tenant {id: lb.tenant_id})
}
MERGE (u)-[r:HAS_LEAVE_BALANCE]->(lb)
ON CREATE SET r.last_synced_at = datetime()
ON MATCH SET r.last_synced_at = datetime();
```

### RM-37: `(:User)-[:HAS_ATTENDANCE]->(:AttendanceRecord)` (DEFECT 02 & CRITICAL-01 6-Step Active-Membership Resolution Alignment)
- **Strict Alignment with `Doc 29` Section 3.1 and `Doc 30` `NM-22`**:
  - Uses the exact same 6-step resolution CTE as `NM-22` (`RESOLVED_BY_USER_ID` and unambiguous `RESOLVED_BY_EMPLOYEE_NUMBER` with **`m.status = 'active' AND m.is_deleted = false AND COALESCE(u.is_deleted, false) = false`**), ensuring 100% 1:1 correspondence between loaded `:AttendanceRecord` nodes and `[:HAS_ATTENDANCE]` edges.
```sql
WITH valid_user_tenant AS (
  SELECT
    up.user_id,
    min(up.tenant_id) AS tenant_id
  FROM public.user_profiles up
  INNER JOIN public.users u
    ON u.id = up.user_id
   AND COALESCE(u.is_deleted, false) = false
  INNER JOIN public.tenant_user_memberships m
    ON m.user_id = up.user_id
   AND m.tenant_id = up.tenant_id
   AND m.status = 'active'
   AND m.is_deleted = false
  GROUP BY up.user_id
  HAVING count(DISTINCT up.tenant_id) = 1
),
emp_number_resolution AS (
  SELECT
    up.employee_number,
    count(DISTINCT up.user_id) AS user_cnt,
    count(DISTINCT up.tenant_id) AS tenant_cnt,
    min(up.user_id) AS resolved_user_id,
    min(up.tenant_id) AS resolved_tenant_id
  FROM public.user_profiles up
  INNER JOIN public.users u
    ON u.id = up.user_id
   AND COALESCE(u.is_deleted, false) = false
  INNER JOIN public.tenant_user_memberships m
    ON m.user_id = up.user_id
   AND m.tenant_id = up.tenant_id
   AND m.status = 'active'
   AND m.is_deleted = false
  WHERE up.employee_number IS NOT NULL
  GROUP BY up.employee_number
),
classified_attendance AS (
  SELECT
    a.id AS attendance_id,
    CASE
      WHEN a.user_id IS NOT NULL AND (u_direct.id IS NULL OR COALESCE(u_direct.is_deleted, false) = true) THEN 'INVALID_SOURCE_REFERENCE'
      WHEN a.user_id IS NOT NULL AND vut.user_id IS NULL THEN 'INVALID_TENANT'
      WHEN a.user_id IS NOT NULL AND vut.user_id IS NOT NULL THEN 'RESOLVED_BY_USER_ID'
      WHEN a.user_id IS NULL AND enr.employee_number IS NULL THEN 'UNRESOLVED'
      WHEN a.user_id IS NULL AND (enr.user_cnt > 1 OR enr.tenant_cnt > 1) THEN 'AMBIGUOUS'
      WHEN a.user_id IS NULL AND enr.user_cnt = 1 AND enr.tenant_cnt = 1 THEN 'RESOLVED_BY_EMPLOYEE_NUMBER'
      ELSE 'INVALID_TENANT'
    END AS resolution_status,
    CASE
      WHEN a.user_id IS NOT NULL THEN vut.user_id
      WHEN a.user_id IS NULL AND enr.user_cnt = 1 AND enr.tenant_cnt = 1 THEN enr.resolved_user_id
      ELSE NULL
    END AS user_id,
    CASE
      WHEN a.user_id IS NOT NULL THEN vut.tenant_id
      WHEN a.user_id IS NULL AND enr.user_cnt = 1 AND enr.tenant_cnt = 1 THEN enr.resolved_tenant_id
      ELSE NULL
    END AS tenant_id
  FROM public.attendance_daily_records a
  LEFT JOIN public.users u_direct ON u_direct.id = a.user_id
  LEFT JOIN valid_user_tenant vut ON vut.user_id = a.user_id
  LEFT JOIN emp_number_resolution enr ON a.user_id IS NULL AND enr.employee_number = a.employee_code
)
SELECT
  attendance_id,
  user_id,
  tenant_id,
  resolution_status
FROM classified_attendance
WHERE resolution_status IN ('RESOLVED_BY_USER_ID', 'RESOLVED_BY_EMPLOYEE_NUMBER');
```
```cypher
UNWIND $batch AS row
MATCH (u:User {id: toInteger(row.user_id), is_deleted: false})
MATCH (ar:AttendanceRecord {id: toInteger(row.attendance_id), tenant_id: toInteger(row.tenant_id)})
WHERE EXISTS {
  MATCH (u)-[:MEMBER_OF {status: 'active', is_deleted: false}]->(:Tenant {id: ar.tenant_id, is_deleted: false})
}
MERGE (u)-[r:HAS_ATTENDANCE]->(ar)
ON CREATE SET
  r.resolution_status = row.resolution_status,
  r.last_synced_at = datetime()
ON MATCH SET
  r.resolution_status = row.resolution_status,
  r.last_synced_at = datetime();
```

### RM-38: `(:User)-[:HAS_CONTRACT]->(:ContractHistory)`
```sql
SELECT
  ch.id AS contract_id,
  ch.user_id,
  ch.tenant_id
FROM public.user_contract_histories ch
INNER JOIN public.users u ON u.id = ch.user_id;
```
```cypher
UNWIND $batch AS row
MATCH (u:User {id: toInteger(row.user_id)})
MATCH (ch:ContractHistory {id: toInteger(row.contract_id), tenant_id: toInteger(row.tenant_id)})
WHERE EXISTS {
  MATCH (u)-[:MEMBER_OF {is_deleted: false}]->(:Tenant {id: ch.tenant_id})
}
MERGE (u)-[r:HAS_CONTRACT]->(ch)
ON CREATE SET r.last_synced_at = datetime()
ON MATCH SET r.last_synced_at = datetime();
```

### RM-39 to RM-43: Semantic Graph Relationships (`[:HAS_TAG]`, `[:TAGGED_WITH]`, `[:ASSOCIATED_WITH]`, `[:STORED_AS_FILE]`)
```sql
-- RM-39: (:Project)-[:HAS_TAG]->(:Tag)
SELECT pt.project_id, 'project:' || pt.id::text AS tag_key
FROM public.project_tags pt
INNER JOIN public.projects p ON p.id = pt.project_id;

-- RM-40: (:Ticket)-[:TAGGED_WITH]->(:Tag)
SELECT tt.ticket_id, 'project:' || tt.tag_id::text AS tag_key
FROM public.ticket_tags tt
INNER JOIN public.tickets t ON t.id = tt.ticket_id
INNER JOIN public.project_tags pt ON pt.id = tt.tag_id AND pt.project_id = t.project_id;

-- RM-41: (:Post)-[:TAGGED_WITH]->(:Tag)
SELECT DISTINCT tpt.post_id, 'talk:' || tpt.tag_id::text AS tag_key
FROM public.talk_post_tags tpt
INNER JOIN public.talk_posts p ON p.id = tpt.post_id
INNER JOIN public.talk_tags tt ON tt.id = tpt.tag_id;

-- RM-42 & RM-43: (:KnowledgeDocument)-[:ASSOCIATED_WITH]->(:Project) & [:STORED_AS_FILE]->(:FileMetadata)
SELECT pcd.id AS doc_id, pcd.project_id, pcd.file_id
FROM public.project_common_documents pcd
INNER JOIN public.projects p ON p.id = pcd.project_id
INNER JOIN public.files f ON f.id = pcd.file_id;
```
```cypher
// RM-39
UNWIND $batch AS row
MATCH (p:Project {id: toInteger(row.project_id)})
MATCH (tg:Tag {tag_key: row.tag_key})
WHERE p.tenant_id = tg.tenant_id
MERGE (p)-[r:HAS_TAG]->(tg)
SET r.last_synced_at = datetime();

// RM-40
UNWIND $batch AS row
MATCH (t:Ticket {id: toInteger(row.ticket_id)})
MATCH (tg:Tag {tag_key: row.tag_key})
WHERE t.tenant_id = tg.tenant_id
MERGE (t)-[r:TAGGED_WITH]->(tg)
SET r.last_synced_at = datetime();

// RM-41
UNWIND $batch AS row
MATCH (p:Post {id: toInteger(row.post_id)})
MATCH (tg:Tag {tag_key: row.tag_key})
WHERE p.tenant_id = tg.tenant_id
MERGE (p)-[r:TAGGED_WITH]->(tg)
SET r.last_synced_at = datetime();

// RM-42 & RM-43
UNWIND $batch AS row
MATCH (kd:KnowledgeDocument {id: toInteger(row.doc_id)})
MATCH (p:Project {id: toInteger(row.project_id)})
MATCH (f:FileMetadata {id: toInteger(row.file_id)})
WHERE kd.tenant_id = p.tenant_id AND kd.tenant_id = f.tenant_id
MERGE (kd)-[r1:ASSOCIATED_WITH]->(p)
SET r1.last_synced_at = datetime()
MERGE (kd)-[r2:STORED_AS_FILE]->(f)
SET r2.last_synced_at = datetime();
```
