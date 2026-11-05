# 04 – Database Relationships & Junction Catalog
## Groupware AI Chatbot Project – Phase 1: Database Discovery

> [!IMPORTANT]
> The database strictly separates **explicit foreign keys** (enforced by DB constraints) from **inferred relationships** (enforced by application logic/data evidence).
> 
> In the Groupware database:
> - **Explicit DB Foreign Keys**: **2** (only inside `hangfire` schema)
> - **Inferred Domain Relationships**: **276** (validated against real table data)
> - **Junction / Mapping Tables**: **31**

---

## 1. Explicit Foreign Key Constraints (2)

| Constraint Name | Source Table | Source Column | Target Table | Target Column | Cardinality | Action Rules |
|---|---|---|---|---|---|---|
| `jobparameter_jobid_fkey` | `hangfire.jobparameter` | `jobid` | `hangfire.job` | `id` | Many-to-One | CASCADE / CASCADE |
| `state_jobid_fkey` | `hangfire.state` | `jobid` | `hangfire.job` | `id` | Many-to-One | CASCADE / CASCADE |

---

## 2. Inferred Relationships – High Confidence (100% Data Match)

Sample of high-confidence relationships where every distinct foreign identifier matches an existing record in the target primary entity:

| Source Table | Source Column | Target Entity Table | Target Column | Cardinality | Data Match Rate | Confidence |
|---|---|---|---|---|---|---|
| `action_translations` | `action_id` | `actions` | `id` | Many-to-One | 100.0% (22 distinct) | Inferred (High - 100% Match) |
| `alert_action_outbox` | `tenant_id` | `tenants` | `id` | Many-to-One | 100.0% (1 distinct) | Inferred (High - 100% Match) |
| `alert_action_outbox` | `alert_event_id` | `alert_events` | `id` | Many-to-One | 100.0% (27 distinct) | Inferred (High - 100% Match) |
| `alert_action_outbox` | `conversation_id` | `chat_conversations` | `id` | Many-to-One | 100.0% (1 distinct) | Inferred (High - 100% Match) |
| `alert_events` | `tenant_id` | `tenants` | `id` | Many-to-One | 100.0% (1 distinct) | Inferred (High - 100% Match) |
| `alert_route_destinations` | `tenant_id` | `tenants` | `id` | Many-to-One | 100.0% (1 distinct) | Inferred (High - 100% Match) |
| `alert_route_destinations` | `conversation_id` | `chat_conversations` | `id` | Many-to-One | 100.0% (1 distinct) | Inferred (High - 100% Match) |
| `alert_route_destinations` | `deleted_by_id` | `users` | `id` | Many-to-One | 100.0% (1 distinct) | Inferred (High - 100% Match) |
| `alert_routes` | `tenant_id` | `tenants` | `id` | Many-to-One | 100.0% (1 distinct) | Inferred (High - 100% Match) |
| `alert_routes` | `created_by_id` | `users` | `id` | Many-to-One | 100.0% (1 distinct) | Inferred (High - 100% Match) |
| `alert_routes` | `updated_by_id` | `users` | `id` | Many-to-One | 100.0% (1 distinct) | Inferred (High - 100% Match) |
| `alert_sources` | `tenant_id` | `tenants` | `id` | Many-to-One | 100.0% (1 distinct) | Inferred (High - 100% Match) |
| `alert_sources` | `created_by_id` | `users` | `id` | Many-to-One | 100.0% (2 distinct) | Inferred (High - 100% Match) |
| `alert_webhook_receipts` | `tenant_id` | `tenants` | `id` | Many-to-One | 100.0% (1 distinct) | Inferred (High - 100% Match) |
| `approval_attachments` | `file_id` | `files` | `id` | Many-to-One | 100.0% (1736 distinct) | Inferred (High - 100% Match) |
| `approval_comment_attachments` | `file_id` | `files` | `id` | Many-to-One | 100.0% (12 distinct) | Inferred (High - 100% Match) |
| `approval_comp_off_usages` | `user_id` | `users` | `id` | Many-to-One | 100.0% (36 distinct) | Inferred (High - 100% Match) |
| `approval_explanation_entries` | `user_id` | `users` | `id` | Many-to-One | 100.0% (316 distinct) | Inferred (High - 100% Match) |
| `approval_overtime_entries` | `user_id` | `users` | `id` | Many-to-One | 100.0% (139 distinct) | Inferred (High - 100% Match) |
| `approval_vacation_request_segments` | `user_id` | `users` | `id` | Many-to-One | 100.0% (292 distinct) | Inferred (High - 100% Match) |
| `approval_vacation_request_segments` | `deleted_by_id` | `users` | `id` | Many-to-One | 100.0% (165 distinct) | Inferred (High - 100% Match) |
| `approval_weekend_work_entries` | `user_id` | `users` | `id` | Many-to-One | 100.0% (86 distinct) | Inferred (High - 100% Match) |
| `asset_assignments` | `asset_id` | `assets` | `id` | Many-to-One | 100.0% (675 distinct) | Inferred (High - 100% Match) |
| `assets` | `department_id` | `departments` | `id` | Many-to-One | 100.0% (23 distinct) | Inferred (High - 100% Match) |
| `attendance_allowances` | `approval_request_id` | `approval_requests` | `id` | Many-to-One | 100.0% (114 distinct) | Inferred (High - 100% Match) |
| `attendance_allowances` | `user_id` | `users` | `id` | Many-to-One | 100.0% (72 distinct) | Inferred (High - 100% Match) |
| `attendance_daily_records` | `user_id` | `users` | `id` | Many-to-One | 100.0% (279 distinct) | Inferred (High - 100% Match) |
| `attendance_face_sessions` | `user_id` | `users` | `id` | Many-to-One | 100.0% (18 distinct) | Inferred (High - 100% Match) |
| `attendance_face_start_audits` | `user_id` | `users` | `id` | Many-to-One | 100.0% (20 distinct) | Inferred (High - 100% Match) |
| `attendance_ingest_event_backups` | `user_id` | `users` | `id` | Many-to-One | 100.0% (243 distinct) | Inferred (High - 100% Match) |
| `attendance_ingest_events` | `user_id` | `users` | `id` | Many-to-One | 100.0% (247 distinct) | Inferred (High - 100% Match) |
| `attendance_logs` | `user_id` | `users` | `id` | Many-to-One | 100.0% (16 distinct) | Inferred (High - 100% Match) |
| `attendance_policy_assignments` | `user_id` | `users` | `id` | Many-to-One | 100.0% (11 distinct) | Inferred (High - 100% Match) |
| `audience_department_members` | `audience_id` | `audiences` | `id` | Many-to-One | 100.0% (90 distinct) | Inferred (High - 100% Match) |
| `audience_department_members` | `department_id` | `departments` | `id` | Many-to-One | 100.0% (28 distinct) | Inferred (High - 100% Match) |
| `audience_user_members` | `audience_id` | `audiences` | `id` | Many-to-One | 100.0% (33 distinct) | Inferred (High - 100% Match) |
| `audience_user_members` | `user_id` | `users` | `id` | Many-to-One | 100.0% (15 distinct) | Inferred (High - 100% Match) |
| `bot_threads` | `user_id` | `users` | `id` | Many-to-One | 100.0% (351 distinct) | Inferred (High - 100% Match) |
| `bot_threads` | `deleted_by_id` | `users` | `id` | Many-to-One | 100.0% (16 distinct) | Inferred (High - 100% Match) |
| `chat_audit_log` | `user_id` | `users` | `id` | Many-to-One | 100.0% (111 distinct) | Inferred (High - 100% Match) |
| `chat_audit_log` | `conversation_id` | `chat_conversations` | `id` | Many-to-One | 100.0% (174 distinct) | Inferred (High - 100% Match) |
| `chat_conversation_members` | `conversation_id` | `chat_conversations` | `id` | Many-to-One | 100.0% (329 distinct) | Inferred (High - 100% Match) |
| `chat_conversation_members` | `deleted_by_id` | `users` | `id` | Many-to-One | 100.0% (6 distinct) | Inferred (High - 100% Match) |
| `chat_group_notes` | `conversation_id` | `chat_conversations` | `id` | Many-to-One | 100.0% (3 distinct) | Inferred (High - 100% Match) |
| `chat_message_attachments` | `conversation_id` | `chat_conversations` | `id` | Many-to-One | 100.0% (55 distinct) | Inferred (High - 100% Match) |
| `chat_message_attachments` | `message_id` | `chat_messages` | `id` | Many-to-One | 100.0% (312 distinct) | Inferred (High - 100% Match) |
| `chat_message_hidden_for_users` | `message_id` | `chat_messages` | `id` | Many-to-One | 100.0% (13 distinct) | Inferred (High - 100% Match) |
| `chat_message_hidden_for_users` | `user_id` | `users` | `id` | Many-to-One | 100.0% (5 distinct) | Inferred (High - 100% Match) |
| `chat_message_links` | `message_id` | `chat_messages` | `id` | Many-to-One | 100.0% (267 distinct) | Inferred (High - 100% Match) |
| `chat_message_mentions` | `message_id` | `chat_messages` | `id` | Many-to-One | 100.0% (279 distinct) | Inferred (High - 100% Match) |

*(Total High-Confidence Relationships: 163. Full list in [`artifacts/database-discovery/relationships.json`](file:///C:/Project/chatbot/artifacts/database-discovery/relationships.json))*

---

## 3. Inferred Relationships with Broken/Orphan Data (Needs Validation)

These 29 relationships were identified by naming and business logic, but have distinct foreign key values that do not match the current target primary key set. As documented in the Data Quality Report, this is primarily caused by the historical user cleanup maintenance on October 5, 2026 where deleted records were moved to `_backup_cleanup_20261005`:

| Source Table | Source Column | Target Table | Target Column | Match Rate | Matched / Total Distinct | Finding & Cause |
|---|---|---|---|---|---|---|
| `approval_participants` | `user_id` | `users` | `id` | 98.31% | 58 / 59 | Inferred (Partial - Broken Refs) |
| `asset_assignments` | `approval_request_id` | `approval_requests` | `id` | 0.0% | 0 / 2 | Needs Validation (Low Match Rate) |
| `chat_conversation_members` | `user_id` | `users` | `id` | 86.34% | 177 / 205 | Needs Validation (Low Match Rate) |
| `chat_message_reactions` | `user_id` | `users` | `id` | 83.33% | 35 / 42 | Needs Validation (Low Match Rate) |
| `files` | `deleted_by_id` | `users` | `id` | 96.84% | 92 / 95 | Inferred (Partial - Broken Refs) |
| `notice_reads` | `notice_id` | `notices` | `id` | 98.98% | 97 / 98 | Inferred (Partial - Broken Refs) |
| `project_activity_logs` | `project_id` | `projects` | `id` | 97.01% | 65 / 67 | Inferred (Partial - Broken Refs) |
| `project_activity_logs` | `ticket_id` | `tickets` | `id` | 96.45% | 652 / 676 | Inferred (Partial - Broken Refs) |
| `project_activity_logs` | `user_id` | `users` | `id` | 96.55% | 56 / 58 | Inferred (Partial - Broken Refs) |
| `project_members` | `project_id` | `projects` | `id` | 97.01% | 65 / 67 | Inferred (Partial - Broken Refs) |
| `project_members` | `user_id` | `users` | `id` | 88.08% | 133 / 151 | Needs Validation (Low Match Rate) |
| `project_tags` | `project_id` | `projects` | `id` | 66.67% | 2 / 3 | Needs Validation (Low Match Rate) |
| `projects` | `deleted_by_id` | `users` | `id` | 75.0% | 3 / 4 | Needs Validation (Low Match Rate) |
| `role_permissions` | `permission_id` | `permissions` | `id` | 99.19% | 245 / 247 | Inferred (Partial - Broken Refs) |
| `roles` | `created_by` | `users` | `id` | 66.67% | 4 / 6 | Needs Validation (Low Match Rate) |
| `schedule_event_participants` | `user_id` | `users` | `id` | 87.65% | 71 / 81 | Needs Validation (Low Match Rate) |
| `schedule_events` | `user_id` | `users` | `id` | 86.21% | 25 / 29 | Needs Validation (Low Match Rate) |
| `schedule_events` | `deleted_by_id` | `users` | `id` | 87.5% | 7 / 8 | Needs Validation (Low Match Rate) |
| `schedule_events` | `updated_by_id` | `users` | `id` | 86.67% | 26 / 30 | Needs Validation (Low Match Rate) |
| `talk_post_comment_reactions` | `user_id` | `users` | `id` | 43.75% | 7 / 16 | Needs Validation (Low Match Rate) |
| `talk_post_reactions` | `user_id` | `users` | `id` | 84.81% | 67 / 79 | Needs Validation (Low Match Rate) |
| `ticket_assignees` | `ticket_id` | `tickets` | `id` | 90.76% | 599 / 660 | Inferred (Partial - Broken Refs) |
| `ticket_assignees` | `user_id` | `users` | `id` | 83.12% | 64 / 77 | Needs Validation (Low Match Rate) |
| `ticket_assignees` | `assigned_by_user_id` | `users` | `id` | 94.59% | 35 / 37 | Inferred (Partial - Broken Refs) |
| `ticket_checklists` | `ticket_id` | `tickets` | `id` | 25.0% | 5 / 20 | Needs Validation (Low Match Rate) |
| `ticket_comments` | `ticket_id` | `tickets` | `id` | 65.71% | 23 / 35 | Needs Validation (Low Match Rate) |
| `ticket_comments` | `user_id` | `users` | `id` | 90.0% | 18 / 20 | Inferred (Partial - Broken Refs) |
| `ticket_tags` | `ticket_id` | `tickets` | `id` | 16.95% | 10 / 59 | Needs Validation (Low Match Rate) |
| `tickets` | `deleted_by_id` | `users` | `id` | 92.86% | 13 / 14 | Inferred (Partial - Broken Refs) |

---

## 4. Many-to-Many Junction & Mapping Tables (31)

The following 31 tables function as associative entities connecting two or more core business domains:

| Junction Table Name | Record Count | Connected Entities | Architectural Justification |
|---|---|---|---|
| `asset_attachments` | 0 | `public.files, public.assets` | References 2 distinct entities: public.files, public.assets; Compact mapping structure (<= 10 columns) |
| `asset_disposal_ticket_items` | 0 | `public.tickets, public.assets` | References 2 distinct entities: public.tickets, public.assets; Compact mapping structure (<= 10 columns) |
| `asset_maintenance_ticket_items` | 0 | `public.tickets, public.assets` | References 2 distinct entities: public.tickets, public.assets; Compact mapping structure (<= 10 columns) |
| `audience_department_members` | 100 | `public.audiences, public.departments` | References 2 distinct entities: public.audiences, public.departments; Compact mapping structure (<= 10 columns) |
| `audience_user_members` | 39 | `public.audiences, public.users` | References 2 distinct entities: public.audiences, public.users; Compact mapping structure (<= 10 columns) |
| `chat_audit_log` | 23,021 | `public.users, public.chat_conversations` | References 2 distinct entities: public.users, public.chat_conversations; Compact mapping structure (<= 10 columns) |
| `chat_conversation_members` | 783 | `public.users, public.chat_conversations` | References 2 distinct entities: public.users, public.chat_conversations; Naming convention matches associative/junction entity |
| `chat_message_hidden_for_users` | 14 | `public.users, public.chat_messages` | References 2 distinct entities: public.users, public.chat_messages; Compact mapping structure (<= 10 columns) |
| `chat_message_mentions` | 316 | `public.users, public.chat_messages` | References 2 distinct entities: public.users, public.chat_messages; Compact mapping structure (<= 10 columns) |
| `chat_shared_links` | 140 | `public.users, public.chat_messages, public.chat_conversations` | References 3 distinct entities: public.users, public.chat_messages, public.chat_conversations; Compact mapping structure (<= 10 columns) |
| `department_members` | 397 | `public.tenants, public.users, public.departments` | References 3 distinct entities: public.tenants, public.users, public.departments; Naming convention matches associative/junction entity |
| `menu_actions` | 246 | `public.menus, public.actions` | References 2 distinct entities: public.menus, public.actions; Compact mapping structure (<= 10 columns) |
| `notice_attachments` | 40 | `public.files, public.notices` | References 2 distinct entities: public.files, public.notices; Compact mapping structure (<= 10 columns) |
| `notice_reads` | 1,392 | `public.users, public.notices` | References 2 distinct entities: public.users, public.notices; Compact mapping structure (<= 10 columns) |
| `notification_recipients` | 9,456 | `public.users, public.notifications` | References 2 distinct entities: public.users, public.notifications; Compact mapping structure (<= 10 columns) |
| `permissions` | 247 | `public.rules, public.actions` | References 2 distinct entities: public.rules, public.actions; Compact mapping structure (<= 10 columns) |
| `project_activity_logs` | 4,389 | `public.users, public.projects, public.tickets` | References 3 distinct entities: public.users, public.projects, public.tickets; Compact mapping structure (<= 10 columns) |
| `project_code_approvers` | 7 | `public.users, public.projects` | References 2 distinct entities: public.users, public.projects; Compact mapping structure (<= 10 columns) |
| `regulation_attachments` | 33 | `public.regulations, public.files` | References 2 distinct entities: public.regulations, public.files; Compact mapping structure (<= 10 columns) |
| `role_permissions` | 1,535 | `public.tenants, public.roles, public.permissions` | References 3 distinct entities: public.tenants, public.roles, public.permissions; Compact mapping structure (<= 10 columns) |
| `ticket_assignees` | 1,008 | `public.users, public.tickets` | References 2 distinct entities: public.users, public.tickets; Compact mapping structure (<= 10 columns) |
| `ticket_attachments` | 24 | `public.users, public.tickets, public.files` | References 3 distinct entities: public.users, public.tickets, public.files; Compact mapping structure (<= 10 columns) |
| `ticket_supervisors` | 44 | `public.users, public.tickets` | References 2 distinct entities: public.users, public.tickets; Compact mapping structure (<= 10 columns) |
| `ticket_time_logs` | 0 | `public.users, public.tickets` | References 2 distinct entities: public.users, public.tickets; Compact mapping structure (<= 10 columns) |
| `ticket_watchers` | 0 | `public.users, public.tickets` | References 2 distinct entities: public.users, public.tickets; Compact mapping structure (<= 10 columns) |
| `user_department_data_scopes` | 3 | `public.tenants, public.users, public.departments` | References 3 distinct entities: public.tenants, public.users, public.departments; Naming convention matches associative/junction entity |
| `user_permissions` | 51 | `public.tenants, public.users, public.permissions` | References 3 distinct entities: public.tenants, public.users, public.permissions; Compact mapping structure (<= 10 columns) |
| `user_restore_history` | 4 | `public.tenants, public.users` | References 2 distinct entities: public.tenants, public.users; Compact mapping structure (<= 10 columns) |
| `user_role_assignments` | 448 | `public.tenants, public.users, public.roles` | References 3 distinct entities: public.tenants, public.users, public.roles; Compact mapping structure (<= 10 columns) |
| `work_calendar_department_assignments` | 1 | `public.tenants, public.work_calendar_templates, public.users, public.departments` | References 4 distinct entities: public.tenants, public.work_calendar_templates, public.users, public.departments; Naming convention matches associative/junction entity |
| `work_calendar_template_days` | 14 | `public.tenants, public.work_calendar_templates, public.users` | References 3 distinct entities: public.tenants, public.work_calendar_templates, public.users; Compact mapping structure (<= 10 columns) |

---

## 5. Self-Referencing Hierarchical Relationships

The database utilizes self-referencing foreign keys to model recursive tree structures:

1. **`public.departments.parent_id -> public.departments.id`**:
   - Models the organizational department tree hierarchy.
   - Root departments have `parent_id IS NULL`. Sub-departments reference their parent node.
   - Also accompanied by `depth` and `path` columns for fast nested tree traversal.
2. **`public.tickets.parent_ticket_id -> public.tickets.id`**:
   - Models hierarchical task decomposition (epics, user stories, sub-tasks).
3. **`public.ticket_comments.parent_id -> public.ticket_comments.id`**:
   - Models threaded discussions and replies on task tickets.
4. **`public.menus.parent_id -> public.menus.id`**:
   - Models multi-level navigation and sidebar menus.
5. **`public.talk_post_comments.parent_id -> public.talk_post_comments.id`**:
   - Models nested comment threads on community/talk bulletin boards.
