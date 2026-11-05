# 03 – Data Dictionary
## Groupware AI Chatbot Project – Phase 1: Database Discovery

> [!NOTE]
> This data dictionary provides full column-level technical metadata for all core business tables in the `public` schema. It details column data types, precision, nullability, defaults, primary keys, foreign keys, and descriptions.

---
## Approval & Workflow Management

### Table: `public.approval_activity_logs`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 20,960
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('approval_activity_logs_id_seq'::regclass)` | YES | - | - |
| `request_id` | `bigint(64,0)` | NO | - | - | - | - |
| `actor_user_id` | `integer(32,0)` | YES | - | - | - | - |
| `event_type` | `character varying(50)` | NO | - | - | - | - |
| `from_status` | `character varying(20)` | YES | - | - | - | - |
| `to_status` | `character varying(20)` | YES | - | - | - | - |
| `metadata` | `jsonb` | YES | `'{}'::jsonb` | - | - | - |
| `created_at` | `timestamp with time zone` | YES | `now()` | - | - | - |

---

### Table: `public.approval_attachments`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 1,736
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('approval_attachments_id_seq'::regclass)` | YES | - | - |
| `request_id` | `bigint(64,0)` | NO | - | - | - | - |
| `file_id` | `bigint(64,0)` | NO | - | - | - | - |
| `sort_order` | `integer(32,0)` | YES | `0` | - | - | - |
| `created_at` | `timestamp with time zone` | YES | `now()` | - | - | - |

---

### Table: `public.approval_comment_attachments`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 12
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('approval_comment_attachments_id_seq'::regclass)` | YES | - | - |
| `comment_id` | `bigint(64,0)` | NO | - | - | - | - |
| `file_id` | `bigint(64,0)` | NO | - | - | - | - |
| `sort_order` | `integer(32,0)` | NO | `0` | - | - | - |
| `created_at` | `timestamp with time zone` | NO | `now()` | - | - | - |

---

### Table: `public.approval_comments`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 551
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('approval_comments_id_seq'::regclass)` | YES | - | - |
| `request_id` | `bigint(64,0)` | NO | - | - | - | - |
| `author_user_id` | `integer(32,0)` | NO | - | - | - | - |
| `content` | `text` | NO | - | - | - | - |
| `created_at` | `timestamp with time zone` | YES | `now()` | - | - | - |
| `is_deleted` | `boolean` | YES | `false` | - | - | - |
| `deleted_at` | `timestamp with time zone` | YES | - | - | - | - |
| `parent_comment_id` | `bigint(64,0)` | YES | - | - | - | - |

---

### Table: `public.approval_comp_off_usages`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 142
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('approval_comp_off_usages_id_seq'::regclass)` | YES | - | - |
| `weekend_work_entry_id` | `bigint(64,0)` | NO | - | - | - | - |
| `vacation_request_id` | `bigint(64,0)` | NO | - | - | - | - |
| `user_id` | `bigint(64,0)` | NO | - | - | - | - |
| `used_minutes` | `integer(32,0)` | NO | - | - | - | - |
| `used_date` | `date` | YES | - | - | - | - |
| `status` | `character varying(30)` | NO | `'USED'::character varying` | - | - | - |
| `created_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `updated_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `is_deleted` | `boolean` | NO | `false` | - | - | - |
| `deleted_at` | `timestamp with time zone` | YES | - | - | - | - |
| `deleted_by_id` | `bigint(64,0)` | YES | - | - | - | - |

---

### Table: `public.approval_explanation_entries`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 1,880
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('approval_explanation_entries_id_seq'::regclass)` | YES | - | - |
| `request_id` | `bigint(64,0)` | NO | - | - | - | - |
| `sequence_order` | `integer(32,0)` | NO | - | - | - | - |
| `member_order` | `integer(32,0)` | NO | `1` | - | - | - |
| `user_id` | `bigint(64,0)` | NO | - | - | - | - |
| `explanation_date` | `date` | NO | - | - | - | - |
| `explanation_type` | `character varying(50)` | NO | - | - | - | - |
| `check_in_time` | `time without time zone` | YES | - | - | - | - |
| `check_out_time` | `time without time zone` | YES | - | - | - | - |
| `created_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `updated_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `reason` | `text` | NO | `''::text` | - | - | - |

---

### Table: `public.approval_overtime_entries`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 1,916
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('approval_overtime_entries_id_seq'::regclass)` | YES | - | - |
| `request_id` | `bigint(64,0)` | NO | - | - | - | - |
| `sequence_order` | `integer(32,0)` | NO | - | - | - | - |
| `user_id` | `bigint(64,0)` | NO | - | - | - | - |
| `overtime_date` | `date` | NO | - | - | - | - |
| `overtime_start_time` | `time without time zone` | NO | - | - | - | - |
| `overtime_end_time` | `time without time zone` | NO | - | - | - | - |
| `created_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `updated_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `member_order` | `integer(32,0)` | NO | `1` | - | - | - |
| `break_minutes` | `integer(32,0)` | NO | `0` | - | - | - |

---

### Table: `public.approval_overtime_request_links`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 35
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('approval_overtime_request_links_id_seq'::regclass)` | YES | - | - |
| `parent_request_id` | `bigint(64,0)` | NO | - | - | - | - |
| `source_request_id` | `bigint(64,0)` | NO | - | - | - | - |
| `created_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `updated_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `is_deleted` | `boolean` | NO | `false` | - | - | - |
| `deleted_at` | `timestamp with time zone` | YES | - | - | - | - |
| `deleted_by_id` | `bigint(64,0)` | YES | - | - | - | - |

---

### Table: `public.approval_participants`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 12,720
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('approval_participants_id_seq'::regclass)` | YES | - | - |
| `request_id` | `bigint(64,0)` | NO | - | - | - | - |
| `user_id` | `integer(32,0)` | NO | - | - | - | - |
| `participant_role` | `character varying(20)` | NO | - | - | - | - |
| `sequence_order` | `integer(32,0)` | YES | `0` | - | - | - |
| `action_status` | `character varying(20)` | YES | `'PENDING'::character varying` | - | - | - |
| `acted_at` | `timestamp with time zone` | YES | - | - | - | - |
| `note` | `text` | YES | - | - | - | - |
| `created_at` | `timestamp with time zone` | YES | `now()` | - | - | - |

---

### Table: `public.approval_requests`
- **Description**: Approval requests (vacation/report/expense)
- **Row Count**: 4,709
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('approval_requests_id_seq'::regclass)` | YES | - | - |
| `code` | `character varying(50)` | YES | - | - | - | - |
| `request_type` | `character varying(20)` | NO | - | - | - | - |
| `status` | `character varying(20)` | NO | `'TEMPORARY'::character varying` | - | - | - |
| `title` | `text` | YES | - | - | - | - |
| `reason` | `text` | YES | - | - | - | - |
| `created_by_user_id` | `integer(32,0)` | NO | - | - | - | - |
| `created_at` | `timestamp with time zone` | YES | `now()` | - | - | - |
| `updated_at` | `timestamp with time zone` | YES | `now()` | - | - | - |
| `submitted_at` | `timestamp with time zone` | YES | - | - | - | - |
| `completed_at` | `timestamp with time zone` | YES | - | - | - | - |
| `start_date` | `date` | YES | - | - | - | - |
| `start_half` | `character varying(2)` | YES | - | - | - | - |
| `end_date` | `date` | YES | - | - | - | - |
| `end_half` | `character varying(2)` | YES | - | - | - | - |
| `total_days` | `numeric(6,2)` | YES | - | - | - | - |
| `payload` | `jsonb` | YES | `'{}'::jsonb` | - | - | - |
| `is_deleted` | `boolean` | YES | `false` | - | - | - |
| `deleted_at` | `timestamp with time zone` | YES | - | - | - | - |
| `leave_type` | `character varying(50)` | YES | - | - | - | - |

---

### Table: `public.approval_vacation_request_segments`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 2,688
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('approval_vacation_request_segments_id_seq'::regclass)` | YES | - | - |
| `request_id` | `bigint(64,0)` | NO | - | - | - | - |
| `user_id` | `bigint(64,0)` | NO | - | - | - | - |
| `leave_type` | `character varying(100)` | YES | - | - | - | - |
| `start_date` | `date` | NO | - | - | - | - |
| `start_half` | `character varying(10)` | NO | `'AM'::character varying` | - | - | - |
| `end_date` | `date` | NO | - | - | - | - |
| `end_half` | `character varying(10)` | NO | `'PM'::character varying` | - | - | - |
| `total_days` | `numeric(5,2)` | NO | `0` | - | - | - |
| `sort_order` | `integer(32,0)` | NO | `0` | - | - | - |
| `created_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `updated_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `is_deleted` | `boolean` | NO | `false` | - | - | - |
| `deleted_at` | `timestamp with time zone` | YES | - | - | - | - |
| `deleted_by_id` | `bigint(64,0)` | YES | - | - | - | - |

---

### Table: `public.approval_weekend_work_entries`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 1,246
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('approval_weekend_work_entries_id_seq'::regclass)` | YES | - | - |
| `request_id` | `bigint(64,0)` | NO | - | - | - | - |
| `sequence_order` | `integer(32,0)` | NO | `1` | - | - | - |
| `member_order` | `integer(32,0)` | NO | `1` | - | - | - |
| `user_id` | `bigint(64,0)` | NO | - | - | - | - |
| `work_date` | `date` | NO | - | - | - | - |
| `coverage` | `character varying(10)` | NO | `'FULL'::character varying` | - | - | - |
| `break_minutes` | `integer(32,0)` | NO | `0` | - | - | - |
| `created_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `updated_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `is_comp_off_used` | `boolean` | NO | `false` | - | - | - |
| `comp_off_used_at` | `timestamp with time zone` | YES | - | - | - | - |
| `comp_off_used_by_request_id` | `bigint(64,0)` | YES | - | - | - | - |

---

### Table: `public.approval_workflow_steps`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 27
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('approval_workflow_steps_id_seq'::regclass)` | YES | - | - |
| `template_id` | `bigint(64,0)` | NO | - | - | - | - |
| `participant_role` | `character varying(20)` | NO | - | - | - | - |
| `step_order` | `integer(32,0)` | NO | - | - | - | - |
| `assignee_type` | `character varying(20)` | NO | - | - | - | - |
| `assignee_value` | `text` | NO | - | - | - | - |
| `is_required` | `boolean` | NO | `true` | - | - | - |
| `created_at` | `timestamp with time zone` | YES | `now()` | - | - | - |
| `updated_at` | `timestamp with time zone` | YES | `now()` | - | - | - |

---

### Table: `public.approval_workflow_templates`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 9
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('approval_workflow_templates_id_seq'::regclass)` | YES | - | - |
| `code` | `text` | NO | - | - | - | - |
| `name` | `text` | NO | - | - | - | - |
| `request_type` | `character varying(50)` | NO | - | - | - | - |
| `is_active` | `boolean` | NO | `true` | - | - | - |
| `priority` | `integer(32,0)` | NO | `0` | - | - | - |
| `created_at` | `timestamp with time zone` | YES | `now()` | - | - | - |
| `updated_at` | `timestamp with time zone` | YES | `now()` | - | - | - |

---

### Table: `public.expense_catalog_translations`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 304
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `integer(32,0)` | NO | - | YES | - | - |
| `expense_catalog_id` | `integer(32,0)` | NO | - | - | - | - |
| `locale` | `character varying(10)` | NO | - | - | - | - |
| `name` | `character varying(200)` | NO | - | - | - | - |
| `description` | `text` | YES | - | - | - | - |
| `created_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `updated_at` | `timestamp with time zone` | NO | `now()` | - | - | - |

---

### Table: `public.expense_catalogs`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 76
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `integer(32,0)` | NO | - | YES | - | - |
| `code` | `character varying(100)` | NO | - | - | - | - |
| `name` | `character varying(200)` | NO | - | - | - | - |
| `parent_id` | `integer(32,0)` | YES | - | - | - | - |
| `sort_order` | `integer(32,0)` | NO | `0` | - | - | - |
| `description` | `text` | YES | - | - | - | - |
| `is_active` | `boolean` | NO | `true` | - | - | - |
| `created_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `updated_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `expense_type` | `character varying(20)` | NO | `'non-fixed'::character varying` | - | - | - |

---

### Table: `public.regulation_attachment_versions`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 36
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('regulation_attachment_versions_id_seq'::regclass)` | YES | - | - |
| `attachment_id` | `bigint(64,0)` | NO | - | - | - | - |
| `version_number` | `integer(32,0)` | NO | - | - | - | - |
| `file_id` | `bigint(64,0)` | NO | - | - | - | - |
| `previous_file_id` | `bigint(64,0)` | YES | - | - | - | - |
| `source` | `character varying(32)` | NO | `'initial'::character varying` | - | - | - |
| `created_by_user_id` | `bigint(64,0)` | YES | - | - | - | - |
| `created_at` | `timestamp with time zone` | NO | `now()` | - | - | - |

---

### Table: `public.regulation_attachments`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 33
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('regulation_attachments_id_seq'::regclass)` | YES | - | - |
| `regulation_id` | `bigint(64,0)` | NO | - | - | - | - |
| `file_id` | `bigint(64,0)` | NO | - | - | - | - |
| `sort_order` | `integer(32,0)` | YES | `0` | - | - | - |
| `created_at` | `timestamp with time zone` | YES | `now()` | - | - | - |

---

### Table: `public.regulations`
- **Description**: Internal regulations documents
- **Row Count**: 97
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('regulations_id_seq'::regclass)` | YES | - | - |
| `title` | `text` | NO | - | - | - | - |
| `content` | `text` | YES | - | - | - | - |
| `version` | `character varying(20)` | YES | `'1.0'::character varying` | - | - | - |
| `status` | `character varying(20)` | YES | `'DRAFT'::character varying` | - | - | - |
| `audience_id` | `integer(32,0)` | YES | - | - | - | - |
| `created_by_user_id` | `integer(32,0)` | NO | - | - | - | - |
| `created_at` | `timestamp with time zone` | YES | `now()` | - | - | - |
| `updated_at` | `timestamp with time zone` | YES | `now()` | - | - | - |
| `published_at` | `timestamp with time zone` | YES | - | - | - | - |
| `effective_from` | `date` | YES | - | - | - | - |
| `effective_to` | `date` | YES | - | - | - | - |
| `is_deleted` | `boolean` | YES | `false` | - | - | - |
| `deleted_at` | `timestamp with time zone` | YES | - | - | - | - |
| `category` | `text` | YES | - | - | - | - |

---

### Table: `public.rule_details`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 92
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('rule_details_id_seq'::regclass)` | YES | - | - |
| `rule_id` | `bigint(64,0)` | NO | - | - | - | - |
| `parent_id` | `bigint(64,0)` | YES | - | - | - | - |
| `operator_id` | `smallint(16,0)` | NO | - | - | - | - |
| `field_name` | `text` | YES | - | - | - | - |
| `field_value` | `text` | YES | - | - | - | - |
| `node_level` | `integer(32,0)` | NO | - | - | - | - |
| `display_order` | `integer(32,0)` | NO | `0` | - | - | - |
| `description` | `text` | YES | - | - | - | - |

---

### Table: `public.rule_operators`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 14
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `smallint(16,0)` | NO | `nextval('rule_operators_id_seq'::regclass)` | YES | - | - |
| `code` | `text` | NO | - | - | - | - |
| `name` | `text` | NO | - | - | - | - |
| `arity` | `smallint(16,0)` | NO | - | - | - | - |

---

### Table: `public.rules`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 23
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('rules_id_seq'::regclass)` | YES | - | - |
| `code` | `text` | NO | - | - | - | - |
| `name` | `text` | NO | - | - | - | - |
| `target_view` | `text` | NO | - | - | - | - |
| `key_column` | `text` | NO | - | - | - | - |
| `category` | `integer(32,0)` | NO | - | - | - | - |
| `select_fields` | `text` | YES | - | - | - | - |
| `is_active` | `boolean` | NO | `true` | - | - | - |

---

## Asset & Equipment Management

### Table: `public.asset_activity_logs`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 0
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('asset_activity_logs_id_seq'::regclass)` | YES | - | - |
| `asset_id` | `bigint(64,0)` | NO | - | - | - | - |
| `actor_user_id` | `integer(32,0)` | YES | - | - | - | - |
| `event_type` | `character varying(50)` | NO | - | - | - | - |
| `old_value` | `jsonb` | YES | - | - | - | - |
| `new_value` | `jsonb` | YES | - | - | - | - |
| `metadata` | `jsonb` | YES | `'{}'::jsonb` | - | - | - |
| `created_at` | `timestamp with time zone` | YES | `now()` | - | - | - |

---

### Table: `public.asset_assignments`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 1,147
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('asset_assignments_id_seq'::regclass)` | YES | - | - |
| `asset_id` | `bigint(64,0)` | NO | - | - | - | - |
| `assignment_type` | `character varying(20)` | NO | - | - | - | - |
| `from_user_id` | `integer(32,0)` | YES | - | - | - | - |
| `from_department_id` | `integer(32,0)` | YES | - | - | - | - |
| `to_user_id` | `integer(32,0)` | YES | - | - | - | - |
| `to_department_id` | `integer(32,0)` | YES | - | - | - | - |
| `assigned_date` | `date` | NO | - | - | - | - |
| `return_date` | `date` | YES | - | - | - | - |
| `actual_return_date` | `date` | YES | - | - | - | - |
| `reason` | `text` | YES | - | - | - | - |
| `note` | `text` | YES | - | - | - | - |
| `approval_request_id` | `bigint(64,0)` | YES | - | - | - | - |
| `status` | `character varying(20)` | YES | `'COMPLETED'::character varying` | - | - | - |
| `created_by_user_id` | `integer(32,0)` | NO | - | - | - | - |
| `created_at` | `timestamp with time zone` | YES | `now()` | - | - | - |
| `ticket_code` | `character varying(32)` | NO | - | - | - | - |

---

### Table: `public.asset_attachments`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 0
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('asset_attachments_id_seq'::regclass)` | YES | - | - |
| `asset_id` | `bigint(64,0)` | NO | - | - | - | - |
| `file_id` | `bigint(64,0)` | NO | - | - | - | - |
| `attachment_type` | `character varying(20)` | YES | `'DOCUMENT'::character varying` | - | - | - |
| `sort_order` | `integer(32,0)` | YES | `0` | - | - | - |
| `created_at` | `timestamp with time zone` | YES | `now()` | - | - | - |

---

### Table: `public.asset_categories`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 30
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `integer(32,0)` | NO | `nextval('asset_categories_id_seq'::regclass)` | YES | - | - |
| `code` | `character varying(50)` | NO | - | - | - | - |
| `name` | `character varying(150)` | NO | - | - | - | - |
| `parent_id` | `integer(32,0)` | YES | - | - | - | - |
| `sort_order` | `integer(32,0)` | YES | `0` | - | - | - |
| `is_active` | `boolean` | YES | `true` | - | - | - |
| `created_at` | `timestamp with time zone` | YES | `now()` | - | - | - |
| `updated_at` | `timestamp with time zone` | YES | `now()` | - | - | - |

---

### Table: `public.asset_disposals`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 0
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('asset_disposals_id_seq'::regclass)` | YES | - | - |
| `asset_id` | `bigint(64,0)` | NO | - | - | - | - |
| `disposal_type` | `character varying(20)` | NO | - | - | - | - |
| `disposal_date` | `date` | NO | - | - | - | - |
| `disposal_value` | `numeric(18,2)` | YES | `0` | - | - | - |
| `book_value` | `numeric(18,2)` | YES | `0` | - | - | - |
| `gain_loss` | `numeric(18,2)` | YES | `0` | - | - | - |
| `buyer_info` | `text` | YES | - | - | - | - |
| `reason` | `text` | NO | - | - | - | - |
| `approval_request_id` | `bigint(64,0)` | YES | - | - | - | - |
| `status` | `character varying(20)` | YES | `'PENDING'::character varying` | - | - | - |
| `created_by_user_id` | `integer(32,0)` | NO | - | - | - | - |
| `created_at` | `timestamp with time zone` | YES | `now()` | - | - | - |

---

### Table: `public.asset_inventory_items`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 0
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('asset_inventory_items_id_seq'::regclass)` | YES | - | - |
| `session_id` | `bigint(64,0)` | NO | - | - | - | - |
| `asset_id` | `bigint(64,0)` | NO | - | - | - | - |
| `expected_location` | `text` | YES | - | - | - | - |
| `actual_location` | `text` | YES | - | - | - | - |
| `expected_status` | `character varying(20)` | YES | - | - | - | - |
| `actual_status` | `character varying(20)` | YES | - | - | - | - |
| `checked_by_user_id` | `integer(32,0)` | YES | - | - | - | - |
| `checked_at` | `timestamp with time zone` | YES | - | - | - | - |
| `note` | `text` | YES | - | - | - | - |
| `created_at` | `timestamp with time zone` | YES | `now()` | - | - | - |

---

### Table: `public.asset_inventory_sessions`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 0
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('asset_inventory_sessions_id_seq'::regclass)` | YES | - | - |
| `code` | `character varying(50)` | NO | - | - | - | - |
| `name` | `character varying(255)` | NO | - | - | - | - |
| `description` | `text` | YES | - | - | - | - |
| `start_date` | `date` | NO | - | - | - | - |
| `end_date` | `date` | YES | - | - | - | - |
| `scope_type` | `character varying(20)` | YES | `'ALL'::character varying` | - | - | - |
| `scope_department_id` | `integer(32,0)` | YES | - | - | - | - |
| `scope_category_id` | `integer(32,0)` | YES | - | - | - | - |
| `status` | `character varying(20)` | YES | `'DRAFT'::character varying` | - | - | - |
| `total_assets` | `integer(32,0)` | YES | `0` | - | - | - |
| `matched_count` | `integer(32,0)` | YES | `0` | - | - | - |
| `missing_count` | `integer(32,0)` | YES | `0` | - | - | - |
| `surplus_count` | `integer(32,0)` | YES | `0` | - | - | - |
| `damaged_count` | `integer(32,0)` | YES | `0` | - | - | - |
| `completed_at` | `timestamp with time zone` | YES | - | - | - | - |
| `summary` | `text` | YES | - | - | - | - |
| `created_by_user_id` | `integer(32,0)` | NO | - | - | - | - |
| `created_at` | `timestamp with time zone` | YES | `now()` | - | - | - |
| `updated_at` | `timestamp with time zone` | YES | `now()` | - | - | - |

---

### Table: `public.asset_maintenance`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 0
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('asset_maintenance_id_seq'::regclass)` | YES | - | - |
| `asset_id` | `bigint(64,0)` | NO | - | - | - | - |
| `maintenance_type` | `character varying(20)` | NO | - | - | - | - |
| `title` | `character varying(255)` | NO | - | - | - | - |
| `description` | `text` | YES | - | - | - | - |
| `scheduled_date` | `date` | YES | - | - | - | - |
| `started_at` | `timestamp with time zone` | YES | - | - | - | - |
| `completed_at` | `timestamp with time zone` | YES | - | - | - | - |
| `vendor` | `character varying(255)` | YES | - | - | - | - |
| `cost` | `numeric(18,2)` | YES | `0` | - | - | - |
| `status` | `character varying(20)` | YES | `'SCHEDULED'::character varying` | - | - | - |
| `result` | `text` | YES | - | - | - | - |
| `created_by_user_id` | `integer(32,0)` | NO | - | - | - | - |
| `created_at` | `timestamp with time zone` | YES | `now()` | - | - | - |
| `updated_at` | `timestamp with time zone` | YES | `now()` | - | - | - |

---

### Table: `public.assets`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 685
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('assets_id_seq'::regclass)` | YES | - | - |
| `code` | `character varying(50)` | NO | - | - | - | - |
| `name` | `character varying(255)` | NO | - | - | - | - |
| `description` | `text` | YES | - | - | - | - |
| `category_id` | `integer(32,0)` | NO | - | - | - | - |
| `purchase_date` | `date` | YES | - | - | - | - |
| `purchase_price` | `numeric(18,2)` | YES | `0` | - | - | - |
| `supplier` | `character varying(255)` | YES | - | - | - | - |
| `invoice_number` | `character varying(100)` | YES | - | - | - | - |
| `warranty_expiry_date` | `date` | YES | - | - | - | - |
| `current_value` | `numeric(18,2)` | YES | `0` | - | - | - |
| `status` | `character varying(20)` | YES | `'ACTIVE'::character varying` | - | - | - |
| `location` | `text` | YES | - | - | - | - |
| `department_id` | `integer(32,0)` | YES | - | - | - | - |
| `assigned_user_id` | `integer(32,0)` | YES | - | - | - | - |
| `serial_number` | `character varying(100)` | YES | - | - | - | - |
| `model` | `character varying(100)` | YES | - | - | - | - |
| `manufacturer` | `character varying(100)` | YES | - | - | - | - |
| `specifications` | `jsonb` | YES | `'{}'::jsonb` | - | - | - |
| `barcode` | `character varying(100)` | YES | - | - | - | - |
| `qr_code_url` | `text` | YES | - | - | - | - |
| `created_by_user_id` | `integer(32,0)` | NO | - | - | - | - |
| `created_at` | `timestamp with time zone` | YES | `now()` | - | - | - |
| `updated_at` | `timestamp with time zone` | YES | `now()` | - | - | - |
| `is_deleted` | `boolean` | YES | `false` | - | - | - |
| `deleted_at` | `timestamp with time zone` | YES | - | - | - | - |
| `acquisition_type` | `character varying(20)` | NO | `'PURCHASE'::character varying` | - | - | - |
| `lease_start_date` | `date` | YES | - | - | - | - |
| `lease_end_date` | `date` | YES | - | - | - | - |
| `lease_vendor` | `character varying(255)` | YES | - | - | - | - |
| `lease_contract_number` | `character varying(100)` | YES | - | - | - | - |
| `lease_monthly_fee` | `numeric(18,2)` | YES | `0` | - | - | - |
| `lease_deposit` | `numeric(18,2)` | YES | `0` | - | - | - |
| `unit` | `character varying(50)` | YES | - | - | - | - |
| `quantity` | `integer(32,0)` | NO | `1` | - | - | - |
| `condition` | `character varying(100)` | YES | - | - | - | - |

---

## Attendance & Leave Management

### Table: `public.attendance_allowances`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 114
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('attendance_allowances_id_seq'::regclass)` | YES | - | - |
| `approval_request_id` | `bigint(64,0)` | NO | - | - | - | - |
| `user_id` | `bigint(64,0)` | NO | - | - | - | - |
| `allowance_type` | `character varying(80)` | NO | - | - | - | - |
| `work_date` | `date` | NO | - | - | - | - |
| `start_time` | `time without time zone` | NO | - | - | - | - |
| `end_time` | `time without time zone` | NO | - | - | - | - |
| `minutes` | `integer(32,0)` | NO | - | - | - | - |
| `status` | `character varying(30)` | NO | `'APPROVED'::character varying` | - | - | - |
| `approved_at` | `timestamp with time zone` | YES | - | - | - | - |
| `created_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `updated_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `is_deleted` | `boolean` | NO | `false` | - | - | - |
| `deleted_at` | `timestamp with time zone` | YES | - | - | - | - |
| `deleted_by_id` | `bigint(64,0)` | YES | - | - | - | - |

---

### Table: `public.attendance_daily_records`
- **Description**: One attendance summary row per employee per work date.
- **Row Count**: 54,489
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('attendance_daily_records_id_seq'::regclass)` | YES | - | - |
| `employee_code` | `character varying(50)` | NO | - | - | - | - |
| `user_id` | `bigint(64,0)` | YES | - | - | - | - |
| `username` | `character varying(50)` | YES | - | - | - | - |
| `full_name` | `character varying(255)` | YES | - | - | - | - |
| `work_date` | `date` | NO | - | - | - | - |
| `first_check_in` | `timestamp with time zone` | YES | - | - | - | - |
| `last_check_out` | `timestamp with time zone` | YES | - | - | - | - |
| `swipe_count` | `integer(32,0)` | NO | `0` | - | - | - |
| `first_event_id` | `bigint(64,0)` | YES | - | - | - | - |
| `last_event_id` | `bigint(64,0)` | YES | - | - | - | - |
| `status` | `character varying(30)` | NO | `'present'::character varying` | - | - | - |
| `is_late` | `boolean` | NO | `false` | - | - | - |
| `is_early_leave` | `boolean` | NO | `false` | - | - | - |
| `actual_minutes` | `integer(32,0)` | NO | `0` | - | - | - |
| `metadata` | `jsonb` | NO | `'{}'::jsonb` | - | - | - |
| `created_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `updated_at` | `timestamp with time zone` | NO | `now()` | - | - | - |

---

### Table: `public.attendance_face_events`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 1,415
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | - | YES | - | - |
| `session_id` | `character varying(64)` | NO | - | - | - | - |
| `seq` | `integer(32,0)` | YES | - | - | - | - |
| `event_type` | `character varying(30)` | NO | - | - | - | - |
| `event_code` | `character varying(50)` | YES | - | - | - | - |
| `message` | `text` | YES | - | - | - | - |
| `created_at` | `timestamp with time zone` | NO | `now()` | - | - | - |

---

### Table: `public.attendance_face_sessions`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 240
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | - | YES | - | - |
| `session_id` | `character varying(64)` | NO | - | - | - | - |
| `user_id` | `bigint(64,0)` | NO | - | - | - | - |
| `username` | `character varying(100)` | NO | - | - | - | - |
| `device_id` | `character varying(200)` | NO | - | - | - | - |
| `platform` | `character varying(50)` | NO | - | - | - | - |
| `app_version` | `character varying(50)` | YES | - | - | - | - |
| `mode` | `character varying(30)` | NO | `'attendance'::character varying` | - | - | - |
| `status` | `character varying(30)` | NO | - | - | - | - |
| `connection_id` | `character varying(200)` | NO | - | - | - | - |
| `last_frame_seq` | `integer(32,0)` | NO | `0` | - | - | - |
| `started_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `ended_at` | `timestamp with time zone` | YES | - | - | - | - |
| `result_code` | `character varying(50)` | YES | - | - | - | - |
| `final_confidence` | `double precision(53,0)` | YES | - | - | - | - |
| `attendance_record_id` | `bigint(64,0)` | YES | - | - | - | - |

---

### Table: `public.attendance_face_start_audits`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 312
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | - | YES | - | - |
| `user_id` | `bigint(64,0)` | NO | - | - | - | - |
| `device_id` | `character varying(200)` | NO | - | - | - | - |
| `session_id` | `character varying(64)` | YES | - | - | - | - |
| `lat` | `double precision(53,0)` | YES | - | - | - | - |
| `lng` | `double precision(53,0)` | YES | - | - | - | - |
| `accuracy_m` | `double precision(53,0)` | YES | - | - | - | - |
| `ip_address` | `inet` | YES | - | - | - | - |
| `captured_at_client` | `timestamp with time zone` | YES | - | - | - | - |
| `received_at_server` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `distance_m` | `double precision(53,0)` | YES | - | - | - | - |
| `decision` | `character varying(20)` | NO | - | - | - | - |
| `reason_code` | `character varying(50)` | YES | - | - | - | - |
| `mock_location_status` | `character varying(20)` | NO | `'unsupported'::character varying` | - | - | - |
| `root_status` | `character varying(20)` | NO | `'unsupported'::character varying` | - | - | - |
| `jailbreak_status` | `character varying(20)` | NO | `'unsupported'::character varying` | - | - | - |
| `app_version` | `character varying(50)` | YES | - | - | - | - |
| `platform` | `character varying(50)` | NO | - | - | - | - |
| `raw_payload` | `jsonb` | YES | - | - | - | - |

---

### Table: `public.attendance_geofence_change_history`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 1
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | - | YES | - | - |
| `geofence_code` | `character varying(50)` | NO | - | - | - | - |
| `geofence_name` | `character varying(255)` | NO | - | - | - | - |
| `old_lat` | `double precision(53,0)` | YES | - | - | - | - |
| `old_lng` | `double precision(53,0)` | YES | - | - | - | - |
| `old_radius_meters` | `double precision(53,0)` | YES | - | - | - | - |
| `old_is_active` | `boolean` | YES | - | - | - | - |
| `new_lat` | `double precision(53,0)` | NO | - | - | - | - |
| `new_lng` | `double precision(53,0)` | NO | - | - | - | - |
| `new_radius_meters` | `double precision(53,0)` | NO | - | - | - | - |
| `new_is_active` | `boolean` | NO | - | - | - | - |
| `changed_by_user_id` | `bigint(64,0)` | NO | - | - | - | - |
| `changed_at` | `timestamp with time zone` | NO | `now()` | - | - | - |

---

### Table: `public.attendance_geofences`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 1
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | - | YES | - | - |
| `code` | `character varying(50)` | NO | - | - | - | - |
| `name` | `character varying(255)` | NO | - | - | - | - |
| `lat` | `double precision(53,0)` | NO | - | - | - | - |
| `lng` | `double precision(53,0)` | NO | - | - | - | - |
| `radius_meters` | `double precision(53,0)` | NO | `50` | - | - | - |
| `is_active` | `boolean` | NO | `true` | - | - | - |
| `created_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `updated_at` | `timestamp with time zone` | NO | `now()` | - | - | - |

---

### Table: `public.attendance_ingest_event_backups`
- **Description**: Immutable backup copy of all raw attendance ingest events before compaction.
- **Row Count**: 176,971
- **Primary Key**: `backup_id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `backup_id` | `bigint(64,0)` | NO | `nextval('attendance_ingest_event_backups_backup_id_seq'::regclass)` | YES | - | - |
| `source_event_id` | `bigint(64,0)` | NO | - | - | - | - |
| `external_event_id` | `character varying(128)` | YES | - | - | - | - |
| `employee_code` | `character varying(50)` | NO | - | - | - | - |
| `user_id` | `bigint(64,0)` | YES | - | - | - | - |
| `username` | `character varying(50)` | YES | - | - | - | - |
| `full_name` | `character varying(255)` | YES | - | - | - | - |
| `work_date` | `date` | NO | - | - | - | - |
| `event_time` | `timestamp with time zone` | NO | - | - | - | - |
| `event_type` | `character varying(30)` | NO | - | - | - | - |
| `device_id` | `character varying(100)` | YES | - | - | - | - |
| `device_name` | `character varying(255)` | YES | - | - | - | - |
| `location` | `character varying(255)` | YES | - | - | - | - |
| `confidence` | `numeric(8,4)` | YES | - | - | - | - |
| `image_url` | `text` | YES | - | - | - | - |
| `raw_payload` | `jsonb` | NO | `'{}'::jsonb` | - | - | - |
| `received_by_user_id` | `bigint(64,0)` | YES | - | - | - | - |
| `source_created_at` | `timestamp with time zone` | YES | - | - | - | - |
| `backed_up_at` | `timestamp with time zone` | NO | `now()` | - | - | - |

---

### Table: `public.attendance_ingest_events`
- **Description**: Raw attendance events inserted by authenticated attendance clients.
- **Row Count**: 143,255
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('attendance_ingest_events_id_seq'::regclass)` | YES | - | - |
| `external_event_id` | `character varying(128)` | YES | - | - | - | - |
| `employee_code` | `character varying(50)` | NO | - | - | - | - |
| `user_id` | `bigint(64,0)` | YES | - | - | - | - |
| `username` | `character varying(50)` | YES | - | - | - | - |
| `full_name` | `character varying(255)` | YES | - | - | - | - |
| `work_date` | `date` | NO | - | - | - | - |
| `event_time` | `timestamp with time zone` | NO | - | - | - | - |
| `event_type` | `character varying(30)` | NO | `'face_recognition'::character varying` | - | - | - |
| `device_id` | `character varying(100)` | YES | - | - | - | - |
| `device_name` | `character varying(255)` | YES | - | - | - | - |
| `location` | `character varying(255)` | YES | - | - | - | - |
| `confidence` | `numeric(8,4)` | YES | - | - | - | - |
| `image_url` | `text` | YES | - | - | - | - |
| `raw_payload` | `jsonb` | NO | `'{}'::jsonb` | - | - | - |
| `received_by_user_id` | `bigint(64,0)` | YES | - | - | - | - |
| `created_at` | `timestamp with time zone` | NO | `now()` | - | - | - |

---

### Table: `public.attendance_logs`
- **Description**: Clock-in/out events
- **Row Count**: 106
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('attendance_logs_id_seq'::regclass)` | YES | - | - |
| `user_id` | `integer(32,0)` | NO | - | - | - | - |
| `event_type` | `character varying(10)` | NO | - | - | - | - |
| `event_at` | `timestamp with time zone` | NO | - | - | - | - |
| `source` | `character varying(30)` | YES | - | - | - | - |
| `ip_address` | `inet` | YES | - | - | - | - |
| `user_agent` | `text` | YES | - | - | - | - |
| `metadata` | `jsonb` | YES | `'{}'::jsonb` | - | - | - |
| `created_at` | `timestamp with time zone` | YES | `now()` | - | - | - |

---

### Table: `public.attendance_policy_assignments`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 13
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('attendance_policy_assignments_id_seq'::regclass)` | YES | - | - |
| `user_id` | `bigint(64,0)` | NO | - | - | - | - |
| `assignment_type` | `character varying(50)` | NO | - | - | - | - |
| `attendance_mode` | `character varying(20)` | YES | - | - | - | - |
| `required_hours` | `numeric(4,2)` | NO | - | - | - | - |
| `credited_bonus_hours` | `numeric(4,2)` | NO | `0` | - | - | - |
| `credited_hours_cap` | `numeric(4,2)` | NO | - | - | - | - |
| `satisfy_attendance_by_required_hours` | `boolean` | NO | `false` | - | - | - |
| `effective_from` | `date` | NO | - | - | - | - |
| `effective_to` | `date` | YES | - | - | - | - |
| `reason` | `character varying(255)` | YES | - | - | - | - |
| `metadata` | `jsonb` | NO | `'{}'::jsonb` | - | - | - |
| `is_active` | `boolean` | NO | `true` | - | - | - |
| `created_at` | `timestamp without time zone` | NO | `now()` | - | - | - |
| `updated_at` | `timestamp without time zone` | NO | `now()` | - | - | - |
| `created_by_user_id` | `bigint(64,0)` | YES | - | - | - | - |
| `updated_by_user_id` | `bigint(64,0)` | YES | - | - | - | - |

---

### Table: `public.attendance_policy_settings`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 1
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('attendance_policy_settings_id_seq'::regclass)` | YES | - | - |
| `morning_start_time` | `time without time zone` | NO | `'08:00:00'::time without time zone` | - | - | - |
| `morning_end_time` | `time without time zone` | NO | `'12:00:00'::time without time zone` | - | - | - |
| `afternoon_start_time` | `time without time zone` | NO | `'13:00:00'::time without time zone` | - | - | - |
| `afternoon_end_time` | `time without time zone` | NO | `'17:00:00'::time without time zone` | - | - | - |
| `morning_late_after` | `time without time zone` | NO | `'08:06:00'::time without time zone` | - | - | - |
| `afternoon_late_after` | `time without time zone` | NO | `'13:06:00'::time without time zone` | - | - | - |
| `updated_by_user_id` | `bigint(64,0)` | YES | - | - | - | - |
| `created_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `updated_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `weekday_overtime_multiplier` | `numeric(6,2)` | NO | `1.5` | - | - | - |
| `weekend_overtime_multiplier` | `numeric(6,2)` | NO | `2.0` | - | - | - |
| `holiday_overtime_multiplier` | `numeric(6,2)` | NO | `3.0` | - | - | - |
| `flex_check_in_from` | `time without time zone` | NO | `'08:00:00'::time without time zone` | - | - | - |
| `flex_check_in_to` | `time without time zone` | NO | `'09:00:00'::time without time zone` | - | - | - |
| `flex_break_start` | `time without time zone` | NO | `'12:00:00'::time without time zone` | - | - | - |
| `flex_break_end` | `time without time zone` | NO | `'13:00:00'::time without time zone` | - | - | - |
| `flex_required_hours` | `numeric(6,2)` | NO | `8.0` | - | - | - |
| `flex_afternoon_late_after` | `time without time zone` | NO | `'13:00:00'::time without time zone` | - | - | - |
| `flex_morning_late_after` | `time without time zone` | NO | `'08:06:00'::time without time zone` | - | - | - |
| `is_active` | `boolean` | NO | `true` | - | - | - |
| `overtime_day_start_time` | `time without time zone` | NO | `'17:30:00'::time without time zone` | - | - | - |
| `overtime_day_end_time` | `time without time zone` | NO | `'22:00:00'::time without time zone` | - | - | - |
| `overtime_night_start_time` | `time without time zone` | NO | `'22:00:00'::time without time zone` | - | - | - |
| `overtime_night_end_time` | `time without time zone` | NO | `'06:00:00'::time without time zone` | - | - | - |
| `weekday_day_overtime_multiplier` | `numeric(6,2)` | NO | `1.5` | - | - | - |
| `weekday_night_overtime_multiplier` | `numeric(6,2)` | NO | `1.5` | - | - | - |
| `weekend_day_overtime_multiplier` | `numeric(6,2)` | NO | `2.0` | - | - | - |
| `weekend_night_overtime_multiplier` | `numeric(6,2)` | NO | `2.0` | - | - | - |
| `holiday_day_overtime_multiplier` | `numeric(6,2)` | NO | `3.0` | - | - | - |
| `holiday_night_overtime_multiplier` | `numeric(6,2)` | NO | `3.0` | - | - | - |

---

### Table: `public.holiday_catalog_translations`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 28
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `integer(32,0)` | NO | - | YES | - | - |
| `holiday_catalog_id` | `integer(32,0)` | NO | - | - | - | - |
| `locale` | `character varying(10)` | NO | - | - | - | - |
| `name` | `character varying(200)` | NO | - | - | - | - |
| `description` | `text` | YES | - | - | - | - |
| `created_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `updated_at` | `timestamp with time zone` | NO | `now()` | - | - | - |

---

### Table: `public.holiday_catalogs`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 7
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `integer(32,0)` | NO | - | YES | - | - |
| `name` | `character varying(200)` | NO | - | - | - | - |
| `start_date` | `date` | NO | - | - | - | - |
| `end_date` | `date` | NO | - | - | - | - |
| `day_type` | `character varying(20)` | NO | `'HOLIDAY'::character varying` | - | - | - |
| `description` | `text` | YES | - | - | - | - |
| `is_recurring_annual` | `boolean` | NO | `false` | - | - | - |
| `is_active` | `boolean` | NO | `true` | - | - | - |
| `created_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `updated_at` | `timestamp with time zone` | NO | `now()` | - | - | - |

---

### Table: `public.leave_catalog_translations`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 88
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `integer(32,0)` | NO | - | YES | - | - |
| `leave_catalog_id` | `integer(32,0)` | NO | - | - | - | - |
| `locale` | `character varying(10)` | NO | - | - | - | - |
| `name` | `character varying(200)` | NO | - | - | - | - |
| `description` | `text` | YES | - | - | - | - |
| `created_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `updated_at` | `timestamp with time zone` | NO | `now()` | - | - | - |

---

### Table: `public.leave_catalogs`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 22
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `integer(32,0)` | NO | - | YES | - | - |
| `code` | `character varying(100)` | NO | - | - | - | - |
| `name` | `character varying(200)` | NO | - | - | - | - |
| `parent_id` | `integer(32,0)` | YES | - | - | - | - |
| `sort_order` | `integer(32,0)` | NO | `0` | - | - | - |
| `description` | `text` | YES | - | - | - | - |
| `is_active` | `boolean` | NO | `true` | - | - | - |
| `created_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `updated_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `is_system` | `boolean` | NO | `false` | - | - | - |
| `max_requests_per_year` | `integer(32,0)` | YES | - | - | - | - |
| `max_days_per_year` | `numeric(6,2)` | YES | - | - | - | - |

---

### Table: `public.leave_policy_settings`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 1
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `smallint(16,0)` | NO | `1` | YES | - | - |
| `monthly_accrual_threshold_percent` | `numeric(5,2)` | NO | `100` | - | - | - |
| `seniority_years_per_extra_day` | `numeric(7,2)` | NO | `5` | - | - | - |
| `updated_by_user_id` | `bigint(64,0)` | YES | - | - | - | - |
| `created_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `updated_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `max_carryover_days` | `numeric(7,2)` | NO | `0` | - | - | - |
| `carryover_reset_month` | `smallint(16,0)` | NO | `3` | - | - | - |
| `carryover_reset_day` | `smallint(16,0)` | NO | `31` | - | - | - |

---

### Table: `public.work_calendar_default_periods`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 1
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('work_calendar_default_periods_id_seq'::regclass)` | YES | - | - |
| `tenant_id` | `bigint(64,0)` | NO | - | - | - | - |
| `work_calendar_template_id` | `bigint(64,0)` | NO | - | - | - | - |
| `effective_from` | `date` | NO | - | - | - | - |
| `effective_to` | `date` | YES | - | - | - | - |
| `created_by_id` | `bigint(64,0)` | YES | - | - | - | - |
| `updated_by_id` | `bigint(64,0)` | YES | - | - | - | - |
| `is_deleted` | `boolean` | NO | `false` | - | - | - |
| `deleted_at` | `timestamp with time zone` | YES | - | - | - | - |
| `deleted_by_id` | `bigint(64,0)` | YES | - | - | - | - |
| `created_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `updated_at` | `timestamp with time zone` | NO | `now()` | - | - | - |

---

### Table: `public.work_calendar_template_day_versions`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 14
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('work_calendar_template_day_versions_id_seq'::regclass)` | YES | - | - |
| `tenant_id` | `bigint(64,0)` | NO | - | - | - | - |
| `work_calendar_template_id` | `bigint(64,0)` | NO | - | - | - | - |
| `day_of_week` | `smallint(16,0)` | NO | - | - | - | - |
| `coverage` | `character varying(20)` | NO | - | - | - | - |
| `effective_from` | `date` | NO | - | - | - | - |
| `effective_to` | `date` | YES | - | - | - | - |
| `created_by_id` | `bigint(64,0)` | YES | - | - | - | - |
| `updated_by_id` | `bigint(64,0)` | YES | - | - | - | - |
| `is_deleted` | `boolean` | NO | `false` | - | - | - |
| `deleted_at` | `timestamp with time zone` | YES | - | - | - | - |
| `deleted_by_id` | `bigint(64,0)` | YES | - | - | - | - |
| `created_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `updated_at` | `timestamp with time zone` | NO | `now()` | - | - | - |

---

### Table: `public.work_calendar_template_days`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 14
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('work_calendar_template_days_id_seq'::regclass)` | YES | - | - |
| `tenant_id` | `bigint(64,0)` | NO | - | - | - | - |
| `work_calendar_template_id` | `bigint(64,0)` | NO | - | - | - | - |
| `day_of_week` | `smallint(16,0)` | NO | - | - | - | - |
| `coverage` | `character varying(20)` | NO | `'off'::character varying` | - | - | - |
| `is_deleted` | `boolean` | NO | `false` | - | - | - |
| `deleted_at` | `timestamp with time zone` | YES | - | - | - | - |
| `deleted_by_id` | `bigint(64,0)` | YES | - | - | - | - |
| `created_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `updated_at` | `timestamp with time zone` | NO | `now()` | - | - | - |

---

### Table: `public.work_calendar_templates`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 2
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('work_calendar_templates_id_seq'::regclass)` | YES | - | - |
| `tenant_id` | `bigint(64,0)` | NO | - | - | - | - |
| `name` | `character varying(150)` | NO | - | - | - | - |
| `description` | `text` | YES | - | - | - | - |
| `is_default` | `boolean` | NO | `false` | - | - | - |
| `is_active` | `boolean` | NO | `true` | - | - | - |
| `created_by_id` | `bigint(64,0)` | YES | - | - | - | - |
| `updated_by_id` | `bigint(64,0)` | YES | - | - | - | - |
| `is_deleted` | `boolean` | NO | `false` | - | - | - |
| `deleted_at` | `timestamp with time zone` | YES | - | - | - | - |
| `deleted_by_id` | `bigint(64,0)` | YES | - | - | - | - |
| `created_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `updated_at` | `timestamp with time zone` | NO | `now()` | - | - | - |

---

## Communication & Collaboration

### Table: `public.chat_audit_log`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 23,021
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('chat_audit_log_id_seq'::regclass)` | YES | - | - |
| `user_id` | `bigint(64,0)` | NO | - | - | - | - |
| `conversation_id` | `bigint(64,0)` | NO | - | - | - | - |
| `action` | `character varying(50)` | NO | - | - | - | - |
| `ip_address` | `inet` | YES | - | - | - | - |
| `created_at` | `timestamp with time zone` | NO | `now()` | - | - | - |

---

### Table: `public.chat_conversation_members`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 783
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('chat_conversation_members_id_seq'::regclass)` | YES | - | - |
| `conversation_id` | `bigint(64,0)` | NO | - | - | - | - |
| `user_id` | `integer(32,0)` | NO | - | - | - | - |
| `role` | `character varying(20)` | YES | `'MEMBER'::character varying` | - | - | - |
| `joined_at` | `timestamp with time zone` | YES | `now()` | - | - | - |
| `last_read_message_id` | `bigint(64,0)` | YES | - | - | - | - |
| `last_delivered_message_id` | `bigint(64,0)` | YES | - | - | - | - |
| `is_pinned` | `boolean` | NO | `false` | - | - | - |
| `is_muted` | `boolean` | NO | `false` | - | - | - |
| `archived_at` | `timestamp with time zone` | YES | - | - | - | - |
| `is_marked_unread` | `boolean` | NO | `false` | - | - | - |
| `hidden_at` | `timestamp with time zone` | YES | - | - | - | - |
| `last_visible_message_id` | `bigint(64,0)` | YES | - | - | - | - |
| `unread_count` | `integer(32,0)` | NO | `0` | - | - | - |
| `last_read_message_seq` | `bigint(64,0)` | NO | `0` | - | - | - |
| `last_visible_message_seq` | `bigint(64,0)` | YES | - | - | - | - |
| `nickname` | `character varying(100)` | YES | - | - | - | - |
| `history_cleared_message_seq` | `bigint(64,0)` | NO | `0` | - | - | - |
| `is_deleted` | `boolean` | NO | `false` | - | - | - |
| `deleted_at` | `timestamp with time zone` | YES | - | - | - | - |
| `deleted_by_id` | `bigint(64,0)` | YES | - | - | - | - |

---

### Table: `public.chat_conversations`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 329
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('chat_conversations_id_seq'::regclass)` | YES | - | - |
| `conversation_type` | `character varying(20)` | NO | `'DIRECT'::character varying` | - | - | - |
| `direct_key` | `text` | YES | - | - | - | - |
| `title` | `text` | YES | - | - | - | - |
| `created_by_user_id` | `integer(32,0)` | YES | - | - | - | - |
| `created_at` | `timestamp with time zone` | YES | `now()` | - | - | - |
| `updated_at` | `timestamp with time zone` | YES | `now()` | - | - | - |
| `avatar_url` | `text` | YES | - | - | - | - |
| `metadata` | `jsonb` | YES | - | - | - | - |
| `last_message_id` | `bigint(64,0)` | YES | - | - | - | - |
| `last_message_seq` | `bigint(64,0)` | NO | `0` | - | - | - |
| `theme` | `character varying(20)` | NO | `'classic'::character varying` | - | - | - |
| `active_emoji` | `character varying(16)` | NO | `'👍'::character varying` | - | - | - |

---

### Table: `public.chat_group_notes`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 22
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('chat_group_notes_id_seq'::regclass)` | YES | - | - |
| `conversation_id` | `bigint(64,0)` | NO | - | - | - | - |
| `creator_id` | `bigint(64,0)` | NO | - | - | - | - |
| `title` | `character varying(500)` | NO | - | - | - | - |
| `content` | `text` | NO | - | - | - | - |
| `is_pinned` | `boolean` | NO | `false` | - | - | - |
| `created_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `updated_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `is_deleted` | `boolean` | NO | `false` | - | - | - |
| `deleted_at` | `timestamp with time zone` | YES | - | - | - | - |
| `deleted_by_id` | `bigint(64,0)` | YES | - | - | - | - |

---

### Table: `public.chat_message_attachments`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 343
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('chat_message_attachments_id_seq'::regclass)` | YES | - | - |
| `conversation_id` | `bigint(64,0)` | NO | - | - | - | - |
| `message_id` | `bigint(64,0)` | YES | - | - | - | - |
| `uploader_user_id` | `integer(32,0)` | NO | - | - | - | - |
| `original_file_name` | `text` | NO | - | - | - | - |
| `stored_file_name` | `text` | NO | - | - | - | - |
| `relative_path` | `text` | NO | - | - | - | - |
| `mime_type` | `character varying(150)` | YES | - | - | - | - |
| `file_size_bytes` | `bigint(64,0)` | NO | - | - | - | - |
| `file_ext` | `character varying(20)` | YES | - | - | - | - |
| `width` | `integer(32,0)` | YES | - | - | - | - |
| `height` | `integer(32,0)` | YES | - | - | - | - |
| `duration_seconds` | `integer(32,0)` | YES | - | - | - | - |
| `created_at` | `timestamp with time zone` | YES | `now()` | - | - | - |
| `expires_at` | `timestamp with time zone` | NO | - | - | - | - |
| `is_deleted` | `boolean` | NO | `false` | - | - | - |
| `deleted_at` | `timestamp with time zone` | YES | - | - | - | - |
| `cleanup_completed_at` | `timestamp with time zone` | YES | - | - | - | - |
| `checksum_sha256` | `character varying(64)` | YES | - | - | - | - |

---

### Table: `public.chat_message_links`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 267
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('chat_message_links_id_seq'::regclass)` | YES | - | - |
| `message_id` | `bigint(64,0)` | NO | - | - | - | - |
| `parent_message_id` | `bigint(64,0)` | NO | - | - | - | - |
| `created_at` | `timestamp with time zone` | YES | `now()` | - | - | - |
| `thread_root_message_id` | `bigint(64,0)` | YES | - | - | - | - |

---

### Table: `public.chat_message_mentions`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 316
- **Primary Key**: `message_id, user_id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `message_id` | `bigint(64,0)` | NO | - | YES | - | - |
| `user_id` | `bigint(64,0)` | NO | - | YES | - | - |
| `created_at` | `timestamp with time zone` | YES | `now()` | - | - | - |

---

### Table: `public.chat_message_poll_options`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 20
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('chat_message_poll_options_id_seq'::regclass)` | YES | - | - |
| `message_id` | `bigint(64,0)` | NO | - | - | - | - |
| `option_text` | `character varying(500)` | NO | - | - | - | - |
| `created_at` | `timestamp with time zone` | YES | `now()` | - | - | - |

---

### Table: `public.chat_message_poll_votes`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 44
- **Primary Key**: `option_id, user_id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `option_id` | `bigint(64,0)` | NO | - | YES | - | - |
| `user_id` | `bigint(64,0)` | NO | - | YES | - | - |
| `created_at` | `timestamp with time zone` | YES | `now()` | - | - | - |

---

### Table: `public.chat_message_polls`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 7
- **Primary Key**: `message_id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `message_id` | `bigint(64,0)` | NO | - | YES | - | - |
| `question` | `character varying(1000)` | NO | - | - | - | - |
| `allow_multiple_votes` | `boolean` | YES | `false` | - | - | - |
| `closed_at` | `timestamp with time zone` | YES | - | - | - | - |
| `created_at` | `timestamp with time zone` | YES | `now()` | - | - | - |

---

### Table: `public.chat_messages`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 6,108
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('chat_messages_id_seq'::regclass)` | YES | - | - |
| `conversation_id` | `bigint(64,0)` | NO | - | - | - | - |
| `sender_user_id` | `integer(32,0)` | NO | - | - | - | - |
| `content` | `text` | NO | - | - | - | - |
| `created_at` | `timestamp with time zone` | YES | `now()` | - | - | - |
| `forwarded_from_message_id` | `bigint(64,0)` | YES | - | - | - | - |
| `edited_at` | `timestamp with time zone` | YES | - | - | - | - |
| `pinned_by_user_id` | `bigint(64,0)` | YES | - | - | - | - |
| `pinned_at` | `timestamp without time zone` | YES | - | - | - | - |
| `recalled_by_user_id` | `bigint(64,0)` | YES | - | - | - | - |
| `recalled_at` | `timestamp with time zone` | YES | - | - | - | - |
| `message_seq` | `bigint(64,0)` | YES | - | - | - | - |
| `is_system` | `boolean` | NO | `false` | - | - | - |
| `message_type` | `character varying(30)` | NO | `'TEXT'::character varying` | - | - | - |
| `sticker_id` | `bigint(64,0)` | YES | - | - | - | - |
| `metadata` | `jsonb` | NO | `'{}'::jsonb` | - | - | - |

---

### Table: `public.chat_realtime_outbox`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 0
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('chat_realtime_outbox_id_seq'::regclass)` | YES | - | - |
| `conversation_id` | `bigint(64,0)` | YES | - | - | - | - |
| `user_id` | `bigint(64,0)` | YES | - | - | - | - |
| `event_name` | `character varying(120)` | NO | - | - | - | - |
| `payload` | `jsonb` | NO | `'{}'::jsonb` | - | - | - |
| `status` | `character varying(20)` | NO | `'pending'::character varying` | - | - | - |
| `attempt_count` | `integer(32,0)` | NO | `0` | - | - | - |
| `available_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `locked_at` | `timestamp with time zone` | YES | - | - | - | - |
| `locked_by` | `character varying(160)` | YES | - | - | - | - |
| `last_error` | `text` | YES | - | - | - | - |
| `created_at` | `timestamp with time zone` | NO | `now()` | - | - | - |

---

### Table: `public.chat_shared_links`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 140
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('chat_shared_links_id_seq'::regclass)` | YES | - | - |
| `message_id` | `bigint(64,0)` | NO | - | - | - | - |
| `conversation_id` | `bigint(64,0)` | NO | - | - | - | - |
| `url` | `character varying(2048)` | NO | - | - | - | - |
| `title` | `character varying(500)` | YES | - | - | - | - |
| `created_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `updated_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `is_deleted` | `boolean` | NO | `false` | - | - | - |
| `deleted_at` | `timestamp with time zone` | YES | - | - | - | - |
| `deleted_by_id` | `bigint(64,0)` | YES | - | - | - | - |

---

### Table: `public.chat_sticker_packs`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 39
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('chat_sticker_packs_id_seq'::regclass)` | YES | - | - |
| `name` | `character varying(255)` | NO | - | - | - | - |
| `slug` | `character varying(120)` | NO | - | - | - | - |
| `description` | `text` | YES | - | - | - | - |
| `cover_url` | `text` | YES | - | - | - | - |
| `sort_order` | `integer(32,0)` | NO | `0` | - | - | - |
| `is_active` | `boolean` | NO | `true` | - | - | - |
| `is_deleted` | `boolean` | NO | `false` | - | - | - |
| `deleted_at` | `timestamp with time zone` | YES | - | - | - | - |
| `deleted_by_id` | `bigint(64,0)` | YES | - | - | - | - |
| `created_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `updated_at` | `timestamp with time zone` | NO | `now()` | - | - | - |

---

### Table: `public.chat_stickers`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 609
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('chat_stickers_id_seq'::regclass)` | YES | - | - |
| `pack_id` | `bigint(64,0)` | NO | - | - | - | - |
| `name` | `character varying(255)` | NO | - | - | - | - |
| `image_url` | `text` | YES | - | - | - | - |
| `animated_url` | `text` | YES | - | - | - | - |
| `asset_type` | `character varying(30)` | NO | `'WEBP'::character varying` | - | - | - |
| `shortcut` | `character varying(80)` | YES | - | - | - | - |
| `width` | `integer(32,0)` | YES | - | - | - | - |
| `height` | `integer(32,0)` | YES | - | - | - | - |
| `sort_order` | `integer(32,0)` | NO | `0` | - | - | - |
| `is_active` | `boolean` | NO | `true` | - | - | - |
| `is_deleted` | `boolean` | NO | `false` | - | - | - |
| `deleted_at` | `timestamp with time zone` | YES | - | - | - | - |
| `deleted_by_id` | `bigint(64,0)` | YES | - | - | - | - |
| `created_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `updated_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `thumbnail_url` | `text` | YES | - | - | - | - |
| `display_url` | `text` | YES | - | - | - | - |

---

### Table: `public.chat_task_assignees`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 6
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('chat_task_assignees_id_seq'::regclass)` | YES | - | - |
| `task_id` | `bigint(64,0)` | NO | - | - | - | - |
| `user_id` | `bigint(64,0)` | NO | - | - | - | - |
| `created_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `updated_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `is_deleted` | `boolean` | NO | `false` | - | - | - |
| `deleted_at` | `timestamp with time zone` | YES | - | - | - | - |
| `deleted_by_id` | `bigint(64,0)` | YES | - | - | - | - |

---

### Table: `public.chat_tasks`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 5
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('chat_tasks_id_seq'::regclass)` | YES | - | - |
| `conversation_id` | `bigint(64,0)` | NO | - | - | - | - |
| `creator_id` | `bigint(64,0)` | NO | - | - | - | - |
| `title` | `character varying(500)` | NO | - | - | - | - |
| `description` | `text` | YES | - | - | - | - |
| `due_date` | `timestamp with time zone` | YES | - | - | - | - |
| `status` | `character varying(50)` | NO | `'TODO'::character varying` | - | - | - |
| `created_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `updated_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `is_deleted` | `boolean` | NO | `false` | - | - | - |
| `deleted_at` | `timestamp with time zone` | YES | - | - | - | - |
| `deleted_by_id` | `bigint(64,0)` | YES | - | - | - | - |

---

### Table: `public.chat_thread_participants`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 6
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('chat_thread_participants_id_seq'::regclass)` | YES | - | - |
| `thread_id` | `bigint(64,0)` | NO | - | - | - | - |
| `user_id` | `bigint(64,0)` | NO | - | - | - | - |
| `last_read_message_id` | `bigint(64,0)` | YES | - | - | - | - |
| `last_read_at` | `timestamp with time zone` | YES | - | - | - | - |
| `unread_count` | `integer(32,0)` | NO | `0` | - | - | - |
| `is_following` | `boolean` | NO | `true` | - | - | - |
| `is_deleted` | `boolean` | NO | `false` | - | - | - |
| `deleted_at` | `timestamp with time zone` | YES | - | - | - | - |
| `deleted_by_id` | `bigint(64,0)` | YES | - | - | - | - |
| `created_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `updated_at` | `timestamp with time zone` | NO | `now()` | - | - | - |

---

### Table: `public.chat_threads`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 2
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('chat_threads_id_seq'::regclass)` | YES | - | - |
| `conversation_id` | `bigint(64,0)` | NO | - | - | - | - |
| `root_message_id` | `bigint(64,0)` | NO | - | - | - | - |
| `reply_count` | `bigint(64,0)` | NO | `0` | - | - | - |
| `last_reply_message_id` | `bigint(64,0)` | YES | - | - | - | - |
| `last_reply_at` | `timestamp with time zone` | YES | - | - | - | - |
| `created_by_id` | `bigint(64,0)` | NO | - | - | - | - |
| `is_deleted` | `boolean` | NO | `false` | - | - | - |
| `deleted_at` | `timestamp with time zone` | YES | - | - | - | - |
| `deleted_by_id` | `bigint(64,0)` | YES | - | - | - | - |
| `created_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `updated_at` | `timestamp with time zone` | NO | `now()` | - | - | - |

---

### Table: `public.comment_mentions`
- **Description**: @mentions in comments for notifications
- **Row Count**: 0
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('comment_mentions_id_seq'::regclass)` | YES | - | - |
| `comment_id` | `bigint(64,0)` | NO | - | - | - | - |
| `mentioned_user_id` | `bigint(64,0)` | NO | - | - | - | - |
| `created_at` | `timestamp with time zone` | YES | `now()` | - | - | - |

---

### Table: `public.mail_send_logs`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 25,315
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('mail_send_logs_id_seq'::regclass)` | YES | - | - |
| `trace_id` | `character varying(120)` | NO | - | - | - | - |
| `purpose` | `character varying(100)` | NO | - | - | - | - |
| `related_user_id` | `bigint(64,0)` | YES | - | - | - | - |
| `recipient_email_masked` | `character varying(255)` | NO | - | - | - | - |
| `recipient_domain` | `character varying(255)` | YES | - | - | - | - |
| `recipient_hash` | `character(64)` | YES | - | - | - | - |
| `subject` | `text` | YES | - | - | - | - |
| `status` | `character varying(20)` | NO | - | - | - | - |
| `error_type` | `character varying(120)` | YES | - | - | - | - |
| `error_message` | `text` | YES | - | - | - | - |
| `attachment_count` | `integer(32,0)` | NO | `0` | - | - | - |
| `duration_ms` | `integer(32,0)` | YES | - | - | - | - |
| `smtp_host` | `character varying(255)` | YES | - | - | - | - |
| `smtp_port` | `integer(32,0)` | YES | - | - | - | - |
| `security_mode` | `character varying(50)` | YES | - | - | - | - |
| `source_app` | `character varying(30)` | NO | `'api'::character varying` | - | - | - |
| `created_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `recipient_email` | `character varying(255)` | YES | - | - | - | - |

---

### Table: `public.notice_attachments`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 40
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('notice_attachments_id_seq'::regclass)` | YES | - | - |
| `notice_id` | `bigint(64,0)` | NO | - | - | - | - |
| `file_id` | `bigint(64,0)` | NO | - | - | - | - |
| `sort_order` | `integer(32,0)` | YES | `0` | - | - | - |
| `created_at` | `timestamp with time zone` | YES | `now()` | - | - | - |

---

### Table: `public.notice_comments`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 0
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('notice_comments_id_seq'::regclass)` | YES | - | - |
| `notice_id` | `bigint(64,0)` | NO | - | - | - | - |
| `author_user_id` | `integer(32,0)` | NO | - | - | - | - |
| `content` | `text` | NO | - | - | - | - |
| `created_at` | `timestamp with time zone` | YES | `now()` | - | - | - |
| `is_deleted` | `boolean` | YES | `false` | - | - | - |
| `deleted_at` | `timestamp with time zone` | YES | - | - | - | - |

---

### Table: `public.notice_reads`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 1,392
- **Primary Key**: `notice_id, user_id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `notice_id` | `bigint(64,0)` | NO | - | YES | - | - |
| `user_id` | `bigint(64,0)` | NO | - | YES | - | - |
| `read_at` | `timestamp with time zone` | YES | `now()` | - | - | - |

---

### Table: `public.notices`
- **Description**: Company notices
- **Row Count**: 99
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('notices_id_seq'::regclass)` | YES | - | - |
| `title` | `text` | NO | - | - | - | - |
| `content` | `text` | YES | - | - | - | - |
| `notice_type` | `character varying(100)` | YES | - | - | - | - |
| `audience_id` | `integer(32,0)` | YES | - | - | - | - |
| `created_by_user_id` | `integer(32,0)` | NO | - | - | - | - |
| `created_at` | `timestamp with time zone` | YES | `now()` | - | - | - |
| `updated_at` | `timestamp with time zone` | YES | `now()` | - | - | - |
| `is_published` | `boolean` | YES | `true` | - | - | - |
| `published_at` | `timestamp with time zone` | YES | - | - | - | - |
| `is_deleted` | `boolean` | YES | `false` | - | - | - |
| `deleted_at` | `timestamp with time zone` | YES | - | - | - | - |
| `priority` | `character varying(20)` | YES | - | - | - | - |

---

### Table: `public.notification_device_registrations`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 70
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('notification_device_registrations_id_seq'::regclass)` | YES | - | - |
| `user_id` | `bigint(64,0)` | NO | - | - | - | - |
| `device_id` | `character varying(191)` | NO | - | - | - | - |
| `platform` | `character varying(32)` | NO | - | - | - | - |
| `provider` | `character varying(32)` | NO | `'expo'::character varying` | - | - | - |
| `push_token` | `text` | NO | - | - | - | - |
| `app_version` | `character varying(64)` | YES | - | - | - | - |
| `locale` | `character varying(16)` | YES | - | - | - | - |
| `is_active` | `boolean` | NO | `true` | - | - | - |
| `last_registered_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `last_seen_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `created_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `updated_at` | `timestamp with time zone` | NO | `now()` | - | - | - |

---

### Table: `public.notification_dispatch_outbox`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 0
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('notification_dispatch_outbox_id_seq'::regclass)` | YES | - | - |
| `recipient_id` | `bigint(64,0)` | NO | - | - | - | - |
| `user_id` | `integer(32,0)` | NO | - | - | - | - |
| `event_name` | `character varying(50)` | NO | - | - | - | - |
| `status` | `character varying(20)` | NO | `'pending'::character varying` | - | - | - |
| `attempt_count` | `integer(32,0)` | NO | `0` | - | - | - |
| `available_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `locked_at` | `timestamp with time zone` | YES | - | - | - | - |
| `locked_by` | `character varying(100)` | YES | - | - | - | - |
| `last_error` | `text` | YES | - | - | - | - |
| `created_at` | `timestamp with time zone` | NO | `now()` | - | - | - |

---

### Table: `public.notification_recipients`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 9,456
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('notification_recipients_id_seq'::regclass)` | YES | - | - |
| `notification_id` | `bigint(64,0)` | NO | - | - | - | - |
| `user_id` | `integer(32,0)` | NO | - | - | - | - |
| `is_read` | `boolean` | YES | `false` | - | - | - |
| `read_at` | `timestamp with time zone` | YES | - | - | - | - |
| `created_at` | `timestamp with time zone` | YES | `now()` | - | - | - |
| `is_seen` | `boolean` | YES | `false` | - | - | - |
| `seen_at` | `timestamp with time zone` | YES | - | - | - | - |

---

### Table: `public.notifications`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 3,735
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('notifications_id_seq'::regclass)` | YES | - | - |
| `actor_user_id` | `integer(32,0)` | YES | - | - | - | - |
| `type` | `character varying(50)` | NO | - | - | - | - |
| `title` | `text` | NO | - | - | - | - |
| `body` | `text` | YES | - | - | - | - |
| `href` | `text` | YES | - | - | - | - |
| `metadata` | `jsonb` | YES | `'{}'::jsonb` | - | - | - |
| `created_at` | `timestamp with time zone` | YES | `now()` | - | - | - |

---

### Table: `public.talk_post_attachments`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 157
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('talk_post_attachments_id_seq'::regclass)` | YES | - | - |
| `post_id` | `bigint(64,0)` | NO | - | - | - | - |
| `file_id` | `bigint(64,0)` | NO | - | - | - | - |
| `sort_order` | `integer(32,0)` | YES | `0` | - | - | - |
| `created_at` | `timestamp with time zone` | YES | `now()` | - | - | - |

---

### Table: `public.talk_post_comment_attachments`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 0
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('talk_post_comment_attachments_id_seq'::regclass)` | YES | - | - |
| `comment_id` | `bigint(64,0)` | NO | - | - | - | - |
| `file_id` | `bigint(64,0)` | NO | - | - | - | - |
| `sort_order` | `integer(32,0)` | NO | `0` | - | - | - |
| `created_at` | `timestamp with time zone` | NO | `now()` | - | - | - |

---

### Table: `public.talk_post_comment_edit_history`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 5
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('talk_post_comment_edit_history_id_seq'::regclass)` | YES | - | - |
| `comment_id` | `bigint(64,0)` | NO | - | - | - | - |
| `edited_by_user_id` | `bigint(64,0)` | NO | - | - | - | - |
| `previous_content` | `text` | NO | - | - | - | - |
| `new_content` | `text` | NO | - | - | - | - |
| `edited_at` | `timestamp with time zone` | NO | `now()` | - | - | - |

---

### Table: `public.talk_post_comments`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 165
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('talk_post_comments_id_seq'::regclass)` | YES | - | - |
| `post_id` | `bigint(64,0)` | NO | - | - | - | - |
| `author_user_id` | `integer(32,0)` | NO | - | - | - | - |
| `parent_comment_id` | `bigint(64,0)` | YES | - | - | - | - |
| `content` | `text` | NO | - | - | - | - |
| `created_at` | `timestamp with time zone` | YES | `now()` | - | - | - |
| `updated_at` | `timestamp with time zone` | YES | `now()` | - | - | - |
| `is_deleted` | `boolean` | YES | `false` | - | - | - |
| `deleted_at` | `timestamp with time zone` | YES | - | - | - | - |
| `edited_at` | `boolean` | NO | `false` | - | - | - |

---

### Table: `public.talk_post_stats`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 247
- **Primary Key**: `post_id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `post_id` | `bigint(64,0)` | NO | - | YES | - | - |
| `post_created_at` | `timestamp with time zone` | NO | - | - | - | - |
| `comment_count` | `integer(32,0)` | NO | `0` | - | - | - |
| `reaction_count` | `integer(32,0)` | NO | `0` | - | - | - |
| `updated_at` | `timestamp with time zone` | NO | `now()` | - | - | - |

---

### Table: `public.talk_post_tags`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 51
- **Primary Key**: `None`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `post_id` | `bigint(64,0)` | NO | - | - | - | - |
| `tag_id` | `bigint(64,0)` | NO | - | - | - | - |
| `created_at` | `timestamp with time zone` | NO | `now()` | - | - | - |

---

### Table: `public.talk_posts`
- **Description**: Talkbox posts
- **Row Count**: 247
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('talk_posts_id_seq'::regclass)` | YES | - | - |
| `author_user_id` | `integer(32,0)` | NO | - | - | - | - |
| `audience_id` | `integer(32,0)` | YES | - | - | - | - |
| `title` | `text` | YES | - | - | - | - |
| `content` | `text` | NO | - | - | - | - |
| `created_at` | `timestamp with time zone` | YES | `now()` | - | - | - |
| `updated_at` | `timestamp with time zone` | YES | `now()` | - | - | - |
| `is_deleted` | `boolean` | YES | `false` | - | - | - |
| `deleted_at` | `timestamp with time zone` | YES | - | - | - | - |

---

### Table: `public.talk_tags`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 10
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('talk_tags_id_seq'::regclass)` | YES | - | - |
| `name` | `character varying(80)` | NO | - | - | - | - |
| `created_at` | `timestamp with time zone` | NO | `now()` | - | - | - |

---

## Organization & Human Resources

### Table: `public.audience_department_members`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 100
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `integer(32,0)` | NO | `nextval('audience_department_members_id_seq'::regclass)` | YES | - | - |
| `audience_id` | `integer(32,0)` | NO | - | - | - | - |
| `department_id` | `integer(32,0)` | NO | - | - | - | - |
| `created_at` | `timestamp with time zone` | YES | `now()` | - | - | - |

---

### Table: `public.audiences`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 116
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `integer(32,0)` | NO | `nextval('audiences_id_seq'::regclass)` | YES | - | - |
| `code` | `character varying(50)` | YES | - | - | - | - |
| `name` | `character varying(150)` | YES | - | - | - | - |
| `audience_type` | `character varying(20)` | NO | - | - | - | - |
| `is_system` | `boolean` | YES | `false` | - | - | - |
| `owner_user_id` | `integer(32,0)` | YES | - | - | - | - |
| `is_active` | `boolean` | YES | `true` | - | - | - |
| `metadata` | `jsonb` | YES | `'{}'::jsonb` | - | - | - |
| `created_at` | `timestamp with time zone` | YES | `now()` | - | - | - |
| `updated_at` | `timestamp with time zone` | YES | `now()` | - | - | - |

---

### Table: `public.contract_type_catalogs`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 4
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `integer(32,0)` | NO | `nextval('contract_type_catalogs_id_seq'::regclass)` | YES | - | - |
| `code` | `character varying(100)` | NO | - | - | - | - |
| `name` | `character varying(255)` | NO | - | - | - | - |
| `description` | `text` | YES | - | - | - | - |
| `is_system` | `boolean` | NO | `false` | - | - | - |
| `is_active` | `boolean` | NO | `true` | - | - | - |
| `created_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `updated_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `leave_accrual_mode` | `character varying(20)` | NO | `'usable'::character varying` | - | - | - |

---

### Table: `public.department_members`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 397
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('department_members_id_seq'::regclass)` | YES | - | - |
| `department_id` | `integer(32,0)` | NO | - | - | - | - |
| `user_id` | `integer(32,0)` | NO | - | - | - | - |
| `position_id` | `bigint(64,0)` | YES | - | - | - | - |
| `role_in_department` | `character varying(100)` | YES | - | - | - | - |
| `is_primary` | `boolean` | NO | `true` | - | - | - |
| `effective_from` | `date` | NO | `CURRENT_DATE` | - | - | - |
| `effective_to` | `date` | YES | - | - | - | - |
| `created_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `updated_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `tenant_id` | `bigint(64,0)` | NO | - | - | - | - |

---

### Table: `public.departments`
- **Description**: Organization departments tree
- **Row Count**: 103
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `integer(32,0)` | NO | `nextval('departments_id_seq'::regclass)` | YES | - | - |
| `code` | `character varying(50)` | YES | - | - | - | - |
| `name` | `character varying(150)` | NO | - | - | - | - |
| `parent_id` | `integer(32,0)` | YES | - | - | - | - |
| `sort_order` | `integer(32,0)` | YES | `0` | - | - | - |
| `depth` | `integer(32,0)` | YES | `0` | - | - | - |
| `path` | `text` | YES | - | - | - | - |
| `is_active` | `boolean` | YES | `true` | - | - | - |
| `metadata` | `jsonb` | YES | `'{}'::jsonb` | - | - | - |
| `created_at` | `timestamp with time zone` | YES | `now()` | - | - | - |
| `updated_at` | `timestamp with time zone` | YES | `now()` | - | - | - |
| `manager_user_id` | `integer(32,0)` | YES | - | - | - | - |
| `department_type` | `character varying(50)` | NO | `'department'::character varying` | - | - | - |
| `level` | `character varying(50)` | YES | - | - | - | - |
| `color` | `character varying(30)` | YES | - | - | - | - |
| `company_id` | `integer(32,0)` | YES | - | - | - | - |
| `site_id` | `integer(32,0)` | YES | - | - | - | - |
| `cost_center_id` | `integer(32,0)` | YES | - | - | - | - |
| `effective_from` | `date` | YES | - | - | - | - |
| `effective_to` | `date` | YES | - | - | - | - |
| `tenant_id` | `bigint(64,0)` | NO | - | - | - | - |

---

### Table: `public.job_grades`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 8
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('job_grades_id_seq'::regclass)` | YES | - | - |
| `code` | `character varying(50)` | NO | - | - | - | - |
| `name` | `character varying(200)` | NO | - | - | - | - |
| `level_order` | `integer(32,0)` | NO | `0` | - | - | - |
| `description` | `text` | YES | - | - | - | - |
| `is_active` | `boolean` | NO | `true` | - | - | - |
| `created_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `updated_at` | `timestamp with time zone` | NO | `now()` | - | - | - |

---

### Table: `public.job_titles`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 10
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('job_titles_id_seq'::regclass)` | YES | - | - |
| `code` | `character varying(50)` | NO | - | - | - | - |
| `name` | `character varying(200)` | NO | - | - | - | - |
| `description` | `text` | YES | - | - | - | - |
| `is_active` | `boolean` | NO | `true` | - | - | - |
| `created_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `updated_at` | `timestamp with time zone` | NO | `now()` | - | - | - |

---

### Table: `public.organization_change_logs`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 129
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('organization_change_logs_id_seq'::regclass)` | YES | - | - |
| `entity_type` | `character varying(50)` | NO | - | - | - | - |
| `entity_id` | `bigint(64,0)` | NO | - | - | - | - |
| `change_type` | `character varying(50)` | NO | - | - | - | - |
| `before_data` | `jsonb` | YES | - | - | - | - |
| `after_data` | `jsonb` | YES | - | - | - | - |
| `reason` | `text` | YES | - | - | - | - |
| `effective_date` | `date` | YES | - | - | - | - |
| `created_by_user_id` | `integer(32,0)` | YES | - | - | - | - |
| `created_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `tenant_id` | `bigint(64,0)` | NO | - | - | - | - |

---

### Table: `public.organization_positions`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 0
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('organization_positions_id_seq'::regclass)` | YES | - | - |
| `code` | `character varying(80)` | NO | - | - | - | - |
| `title` | `character varying(200)` | NO | - | - | - | - |
| `department_id` | `integer(32,0)` | NO | - | - | - | - |
| `job_title_id` | `bigint(64,0)` | YES | - | - | - | - |
| `grade_id` | `bigint(64,0)` | YES | - | - | - | - |
| `manager_position_id` | `bigint(64,0)` | YES | - | - | - | - |
| `headcount` | `integer(32,0)` | NO | `1` | - | - | - |
| `status` | `character varying(30)` | NO | `'open'::character varying` | - | - | - |
| `location` | `character varying(200)` | YES | - | - | - | - |
| `description` | `text` | YES | - | - | - | - |
| `effective_from` | `date` | NO | `CURRENT_DATE` | - | - | - |
| `effective_to` | `date` | YES | - | - | - | - |
| `is_active` | `boolean` | NO | `true` | - | - | - |
| `created_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `updated_at` | `timestamp with time zone` | NO | `now()` | - | - | - |

---

### Table: `public.organization_transfers`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 2
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('organization_transfers_id_seq'::regclass)` | YES | - | - |
| `user_id` | `integer(32,0)` | NO | - | - | - | - |
| `from_department_id` | `integer(32,0)` | YES | - | - | - | - |
| `to_department_id` | `integer(32,0)` | NO | - | - | - | - |
| `from_position_id` | `bigint(64,0)` | YES | - | - | - | - |
| `to_position_id` | `bigint(64,0)` | YES | - | - | - | - |
| `effective_date` | `date` | NO | `CURRENT_DATE` | - | - | - |
| `status` | `character varying(30)` | NO | `'planned'::character varying` | - | - | - |
| `reason` | `text` | YES | - | - | - | - |
| `applied_at` | `timestamp with time zone` | YES | - | - | - | - |
| `created_by_user_id` | `integer(32,0)` | YES | - | - | - | - |
| `created_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `updated_at` | `timestamp with time zone` | NO | `now()` | - | - | - |

---

### Table: `public.position_assignments`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 0
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('position_assignments_id_seq'::regclass)` | YES | - | - |
| `position_id` | `bigint(64,0)` | NO | - | - | - | - |
| `user_id` | `integer(32,0)` | NO | - | - | - | - |
| `assignment_type` | `character varying(30)` | NO | `'primary'::character varying` | - | - | - |
| `effective_from` | `date` | NO | `CURRENT_DATE` | - | - | - |
| `effective_to` | `date` | YES | - | - | - | - |
| `created_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `updated_at` | `timestamp with time zone` | NO | `now()` | - | - | - |

---

### Table: `public.position_requests`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 1
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('position_requests_id_seq'::regclass)` | YES | - | - |
| `request_type` | `character varying(30)` | NO | `'new_position'::character varying` | - | - | - |
| `status` | `character varying(30)` | NO | `'draft'::character varying` | - | - | - |
| `department_id` | `integer(32,0)` | NO | - | - | - | - |
| `position_id` | `bigint(64,0)` | YES | - | - | - | - |
| `title` | `character varying(200)` | NO | - | - | - | - |
| `requested_headcount` | `integer(32,0)` | NO | `1` | - | - | - |
| `reason` | `text` | YES | - | - | - | - |
| `target_date` | `date` | YES | - | - | - | - |
| `requested_by_user_id` | `integer(32,0)` | YES | - | - | - | - |
| `approval_request_id` | `bigint(64,0)` | YES | - | - | - | - |
| `created_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `updated_at` | `timestamp with time zone` | NO | `now()` | - | - | - |

---

### Table: `public.work_calendar_department_assignments`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 1
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('work_calendar_department_assignments_id_seq'::regclass)` | YES | - | - |
| `tenant_id` | `bigint(64,0)` | NO | - | - | - | - |
| `department_id` | `bigint(64,0)` | NO | - | - | - | - |
| `work_calendar_template_id` | `bigint(64,0)` | NO | - | - | - | - |
| `effective_from` | `date` | NO | - | - | - | - |
| `effective_to` | `date` | YES | - | - | - | - |
| `reason` | `text` | YES | - | - | - | - |
| `is_active` | `boolean` | NO | `true` | - | - | - |
| `created_by_id` | `bigint(64,0)` | YES | - | - | - | - |
| `updated_by_id` | `bigint(64,0)` | YES | - | - | - | - |
| `is_deleted` | `boolean` | NO | `false` | - | - | - |
| `deleted_at` | `timestamp with time zone` | YES | - | - | - | - |
| `deleted_by_id` | `bigint(64,0)` | YES | - | - | - | - |
| `created_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `updated_at` | `timestamp with time zone` | NO | `now()` | - | - | - |

---

### Table: `public.workforce_plan_items`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 0
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('workforce_plan_items_id_seq'::regclass)` | YES | - | - |
| `plan_id` | `bigint(64,0)` | NO | - | - | - | - |
| `department_id` | `integer(32,0)` | NO | - | - | - | - |
| `job_title_id` | `bigint(64,0)` | YES | - | - | - | - |
| `grade_id` | `bigint(64,0)` | YES | - | - | - | - |
| `planned_headcount` | `integer(32,0)` | NO | `0` | - | - | - |
| `approved_headcount` | `integer(32,0)` | NO | `0` | - | - | - |
| `budget_amount` | `numeric(18,2)` | YES | - | - | - | - |
| `notes` | `text` | YES | - | - | - | - |
| `created_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `updated_at` | `timestamp with time zone` | NO | `now()` | - | - | - |

---

### Table: `public.workforce_plans`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 1
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('workforce_plans_id_seq'::regclass)` | YES | - | - |
| `code` | `character varying(80)` | NO | - | - | - | - |
| `name` | `character varying(200)` | NO | - | - | - | - |
| `fiscal_year` | `integer(32,0)` | NO | - | - | - | - |
| `department_id` | `integer(32,0)` | YES | - | - | - | - |
| `scenario` | `character varying(50)` | NO | `'base'::character varying` | - | - | - |
| `status` | `character varying(30)` | NO | `'draft'::character varying` | - | - | - |
| `notes` | `text` | YES | - | - | - | - |
| `created_by_user_id` | `integer(32,0)` | YES | - | - | - | - |
| `created_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `updated_at` | `timestamp with time zone` | NO | `now()` | - | - | - |

---

## Project Management

### Table: `public.project_activity_logs`
- **Description**: Audit trail for project activities
- **Row Count**: 4,389
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('project_activity_logs_id_seq'::regclass)` | YES | - | - |
| `project_id` | `bigint(64,0)` | NO | - | - | - | - |
| `ticket_id` | `bigint(64,0)` | YES | - | - | - | - |
| `user_id` | `bigint(64,0)` | YES | - | - | - | - |
| `action_type` | `text` | NO | - | - | - | CREATE_TICKET | UPDATE_TICKET | MOVE_COLUMN | COMMENT | ASSIGN | etc. |
| `entity_type` | `text` | YES | - | - | - | - |
| `old_value` | `text` | YES | - | - | - | - |
| `new_value` | `text` | YES | - | - | - | - |
| `metadata` | `jsonb` | YES | `'{}'::jsonb` | - | - | - |
| `created_at` | `timestamp with time zone` | YES | `now()` | - | - | - |

---

### Table: `public.project_code_approvers`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 7
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('project_code_approvers_id_seq'::regclass)` | YES | - | - |
| `project_id` | `bigint(64,0)` | NO | - | - | - | - |
| `user_id` | `bigint(64,0)` | NO | - | - | - | - |
| `created_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `updated_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `is_deleted` | `boolean` | NO | `false` | - | - | - |
| `deleted_at` | `timestamp with time zone` | YES | - | - | - | - |
| `deleted_by_id` | `bigint(64,0)` | YES | - | - | - | - |

---

### Table: `public.project_code_daily_sequences`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 5
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `code_prefix` | `character varying(10)` | NO | - | - | - | - |
| `date_stamp` | `character varying(6)` | NO | - | - | - | - |
| `current_seq` | `integer(32,0)` | NO | `0` | - | - | - |
| `updated_at` | `timestamp with time zone` | YES | `now()` | - | - | - |
| `id` | `bigint(64,0)` | NO | `nextval('project_code_daily_sequences_id_seq'::regclass)` | YES | - | - |
| `created_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `is_deleted` | `boolean` | NO | `false` | - | - | - |
| `deleted_at` | `timestamp with time zone` | YES | - | - | - | - |
| `deleted_by_id` | `bigint(64,0)` | YES | - | - | - | - |

---

### Table: `public.project_common_documents`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 40
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('project_common_documents_id_seq'::regclass)` | YES | - | - |
| `project_id` | `bigint(64,0)` | NO | - | - | - | - |
| `file_id` | `bigint(64,0)` | NO | - | - | - | - |
| `title` | `character varying(500)` | YES | - | - | - | - |
| `sort_order` | `integer(32,0)` | NO | `0` | - | - | - |
| `uploaded_by_id` | `bigint(64,0)` | NO | - | - | - | - |
| `is_deleted` | `boolean` | NO | `false` | - | - | - |
| `deleted_at` | `timestamp with time zone` | YES | - | - | - | - |
| `deleted_by_id` | `bigint(64,0)` | YES | - | - | - | - |
| `created_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `updated_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `payment_installment` | `bigint(64,0)` | YES | - | - | - | - |
| `payment_terms` | `character varying(50)` | YES | - | - | - | - |
| `payment_project_total` | `numeric(18,0)` | YES | - | - | - | - |
| `payment_percentage` | `numeric(5,2)` | YES | - | - | - | - |
| `payment_amount` | `numeric(18,0)` | YES | - | - | - | - |

---

### Table: `public.project_custom_fields`
- **Description**: Custom field definitions per project (Notion-like)
- **Row Count**: 0
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('project_custom_fields_id_seq'::regclass)` | YES | - | - |
| `project_id` | `bigint(64,0)` | NO | - | - | - | - |
| `name` | `text` | NO | - | - | - | - |
| `field_type` | `text` | NO | - | - | - | text | number | date | select | multi_select | user | url | checkbox |
| `options` | `jsonb` | YES | `'[]'::jsonb` | - | - | - |
| `is_required` | `boolean` | YES | `false` | - | - | - |
| `position` | `integer(32,0)` | YES | `0` | - | - | - |
| `created_at` | `timestamp with time zone` | YES | `now()` | - | - | - |

---

### Table: `public.project_members`
- **Description**: Project team members with roles
- **Row Count**: 356
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('project_members_id_seq'::regclass)` | YES | - | - |
| `project_id` | `bigint(64,0)` | NO | - | - | - | - |
| `user_id` | `bigint(64,0)` | NO | - | - | - | - |
| `role` | `text` | YES | `'member'::text` | - | - | owner | admin | member | viewer |
| `joined_at` | `timestamp with time zone` | YES | `now()` | - | - | - |
| `invited_by_user_id` | `bigint(64,0)` | YES | - | - | - | - |

---

### Table: `public.project_receivable_reminders`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 0
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('project_receivable_reminders_id_seq'::regclass)` | YES | - | - |
| `project_id` | `bigint(64,0)` | NO | - | - | - | - |
| `installment` | `bigint(64,0)` | NO | - | - | - | - |
| `kind` | `text` | NO | - | - | - | - |
| `claimed_at` | `timestamp with time zone` | NO | - | - | - | - |
| `sent_at` | `timestamp with time zone` | YES | - | - | - | - |
| `created_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `updated_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `is_deleted` | `boolean` | NO | `false` | - | - | - |
| `deleted_at` | `timestamp with time zone` | YES | - | - | - | - |
| `deleted_by_id` | `bigint(64,0)` | YES | - | - | - | - |

---

### Table: `public.project_receivables`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 0
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('project_receivables_id_seq'::regclass)` | YES | - | - |
| `project_id` | `bigint(64,0)` | NO | - | - | - | - |
| `installment` | `bigint(64,0)` | NO | - | - | - | - |
| `payment_terms` | `text` | NO | - | - | - | - |
| `project_total` | `numeric(20,0)` | NO | - | - | - | - |
| `amount` | `numeric(20,0)` | NO | - | - | - | - |
| `issued_at` | `timestamp with time zone` | NO | - | - | - | - |
| `expected_collection_at` | `timestamp with time zone` | NO | - | - | - | - |
| `collected_at` | `timestamp with time zone` | YES | - | - | - | - |
| `collected_by_id` | `bigint(64,0)` | YES | - | - | - | - |
| `created_by_id` | `bigint(64,0)` | NO | - | - | - | - |
| `created_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `updated_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `is_deleted` | `boolean` | NO | `false` | - | - | - |
| `deleted_at` | `timestamp with time zone` | YES | - | - | - | - |
| `deleted_by_id` | `bigint(64,0)` | YES | - | - | - | - |

---

### Table: `public.project_sprints`
- **Description**: Sprints/milestones for agile project management
- **Row Count**: 40
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('project_sprints_id_seq'::regclass)` | YES | - | - |
| `project_id` | `bigint(64,0)` | NO | - | - | - | - |
| `name` | `text` | NO | - | - | - | - |
| `goal` | `text` | YES | - | - | - | - |
| `start_date` | `timestamp with time zone` | YES | - | - | - | - |
| `end_date` | `timestamp with time zone` | YES | - | - | - | - |
| `status` | `text` | YES | `'planning'::text` | - | - | planning | active | completed |
| `created_at` | `timestamp with time zone` | YES | `now()` | - | - | - |
| `updated_at` | `timestamp with time zone` | YES | `now()` | - | - | - |

---

### Table: `public.project_statuses`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 5
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `integer(32,0)` | NO | - | YES | - | - |
| `code` | `character varying(64)` | NO | - | - | - | - |
| `name` | `character varying(160)` | NO | - | - | - | - |
| `description` | `character varying(255)` | YES | - | - | - | - |
| `color_variant` | `character varying(32)` | NO | `'muted'::character varying` | - | - | - |
| `stage` | `character varying(32)` | NO | - | - | - | - |
| `sort_order` | `integer(32,0)` | NO | `0` | - | - | - |
| `is_default` | `boolean` | NO | `false` | - | - | - |
| `is_active` | `boolean` | NO | `true` | - | - | - |
| `is_system` | `boolean` | NO | `false` | - | - | - |
| `created_at` | `timestamp without time zone` | NO | `now()` | - | - | - |
| `updated_at` | `timestamp without time zone` | NO | `now()` | - | - | - |

---

### Table: `public.project_tags`
- **Description**: Tags/labels for categorizing tickets within a project
- **Row Count**: 20
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('project_tags_id_seq'::regclass)` | YES | - | - |
| `project_id` | `bigint(64,0)` | NO | - | - | - | - |
| `name` | `text` | NO | - | - | - | - |
| `color` | `text` | YES | - | - | - | - |
| `created_at` | `timestamp with time zone` | YES | `now()` | - | - | - |

---

### Table: `public.project_templates`
- **Description**: Reusable project templates
- **Row Count**: 3
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('project_templates_id_seq'::regclass)` | YES | - | - |
| `name` | `text` | NO | - | - | - | - |
| `description` | `text` | YES | - | - | - | - |
| `template_data` | `jsonb` | NO | - | - | - | - |
| `created_by_user_id` | `bigint(64,0)` | YES | - | - | - | - |
| `is_public` | `boolean` | YES | `false` | - | - | - |
| `created_at` | `timestamp with time zone` | YES | `now()` | - | - | - |

---

### Table: `public.project_views`
- **Description**: Saved view configurations for projects
- **Row Count**: 0
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('project_views_id_seq'::regclass)` | YES | - | - |
| `project_id` | `bigint(64,0)` | NO | - | - | - | - |
| `created_by_user_id` | `bigint(64,0)` | YES | - | - | - | - |
| `name` | `text` | NO | - | - | - | - |
| `view_type` | `text` | YES | `'kanban'::text` | - | - | kanban | list | calendar | timeline |
| `filters` | `jsonb` | YES | `'{}'::jsonb` | - | - | - |
| `sort_by` | `jsonb` | YES | `'[]'::jsonb` | - | - | - |
| `visible_fields` | `jsonb` | YES | `'[]'::jsonb` | - | - | - |
| `group_by` | `text` | YES | - | - | - | - |
| `is_default` | `boolean` | YES | `false` | - | - | - |
| `is_shared` | `boolean` | YES | `true` | - | - | - |
| `created_at` | `timestamp with time zone` | YES | `now()` | - | - | - |
| `updated_at` | `timestamp with time zone` | YES | `now()` | - | - | - |

---

### Table: `public.projects`
- **Description**: Projects for project management module
- **Row Count**: 65
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('projects_id_seq'::regclass)` | YES | - | - |
| `name` | `text` | NO | - | - | - | - |
| `key` | `text` | NO | - | - | - | Unique project key used for ticket codes (e.g., NFF -> NFF-1, NFF-2) |
| `description` | `text` | YES | - | - | - | - |
| `icon` | `text` | YES | - | - | - | Lucide icon name for UI display |
| `color_code` | `text` | YES | `'primary'::text` | - | - | System color class (primary/success/warning/info/destructive/secondary) |
| `status` | `text` | YES | `'new'::text` | - | - | active | archived | completed |
| `created_by_user_id` | `bigint(64,0)` | NO | - | - | - | - |
| `created_at` | `timestamp with time zone` | YES | `now()` | - | - | - |
| `updated_at` | `timestamp with time zone` | YES | `now()` | - | - | - |
| `metadata` | `jsonb` | YES | `'{}'::jsonb` | - | - | - |
| `is_deleted` | `boolean` | YES | `false` | - | - | - |
| `deleted_at` | `timestamp with time zone` | YES | - | - | - | - |
| `deleted_by_id` | `bigint(64,0)` | YES | - | - | - | - |
| `status_id` | `integer(32,0)` | NO | - | - | - | - |
| `start_date` | `timestamp with time zone` | YES | - | - | - | - |
| `end_date` | `timestamp with time zone` | YES | - | - | - | - |
| `sort_order` | `integer(32,0)` | NO | `0` | - | - | - |
| `activity_logging_mode` | `text` | NO | `'full'::text` | - | - | - |
| `members_count` | `integer(32,0)` | NO | `0` | - | - | - |
| `tickets_count` | `integer(32,0)` | NO | `0` | - | - | - |
| `completed_tickets_count` | `integer(32,0)` | NO | `0` | - | - | - |
| `client_code` | `character varying(50)` | YES | - | - | - | - |
| `service_type` | `character varying(20)` | YES | `'DATA'::character varying` | - | - | - |
| `classification` | `character varying(20)` | YES | `'BODYSHOP'::character varying` | - | - | - |
| `stage` | `character varying(20)` | YES | `'BASE'::character varying` | - | - | - |
| `period_ym` | `character varying(10)` | YES | - | - | - | - |
| `phase_round` | `character varying(20)` | YES | `'1st'::character varying` | - | - | - |
| `contract_file_id` | `bigint(64,0)` | YES | - | - | - | - |
| `approval_status` | `character varying(30)` | YES | `'APPROVED'::character varying` | - | - | - |
| `approved_by_user_id` | `bigint(64,0)` | YES | - | - | - | - |
| `approved_at` | `timestamp with time zone` | YES | - | - | - | - |
| `reject_reason` | `text` | YES | - | - | - | - |
| `plan_code` | `character varying(50)` | YES | - | - | - | - |
| `approver_user_ids` | `ARRAY` | YES | `'{}'::bigint[]` | - | - | - |
| `contract_translation_file_id` | `bigint(64,0)` | YES | - | - | - | - |
| `payment_terms` | `character varying(50)` | YES | - | - | - | - |

---

## Schedule & Meeting Room Management

### Table: `public.schedule_categories`
- **Description**: Master data: Event categories/priorities
- **Row Count**: 7
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `integer(32,0)` | NO | `nextval('schedule_categories_id_seq'::regclass)` | YES | - | - |
| `name` | `character varying(100)` | NO | - | - | - | - |
| `color_code` | `character varying(50)` | YES | - | - | - | - |
| `sort_order` | `integer(32,0)` | YES | `0` | - | - | - |
| `is_active` | `boolean` | YES | `true` | - | - | - |
| `created_at` | `timestamp with time zone` | YES | `now()` | - | - | - |
| `updated_at` | `timestamp with time zone` | YES | `now()` | - | - | - |

---

### Table: `public.schedule_event_attachments`
- **Description**: Links events to uploaded files
- **Row Count**: 11
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('schedule_event_attachments_id_seq'::regclass)` | YES | - | - |
| `event_id` | `bigint(64,0)` | NO | - | - | - | - |
| `file_id` | `bigint(64,0)` | NO | - | - | - | References files table for actual file data |
| `sort_order` | `integer(32,0)` | YES | `0` | - | - | - |
| `created_at` | `timestamp with time zone` | YES | `now()` | - | - | - |

---

### Table: `public.schedule_event_participants`
- **Description**: Event participants/attendees with RSVP status
- **Row Count**: 1,241
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('schedule_event_participants_id_seq'::regclass)` | YES | - | - |
| `event_id` | `bigint(64,0)` | NO | - | - | - | - |
| `user_id` | `bigint(64,0)` | NO | - | - | - | - |
| `status` | `character varying(20)` | YES | `'pending'::character varying` | - | - | RSVP status: pending | accepted | declined | tentative |
| `is_required` | `boolean` | YES | `false` | - | - | True for required attendees, false for optional |
| `created_at` | `timestamp with time zone` | YES | `now()` | - | - | - |
| `updated_at` | `timestamp with time zone` | YES | `now()` | - | - | - |

---

### Table: `public.schedule_events`
- **Description**: Main calendar events table
- **Row Count**: 349
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('schedule_events_id_seq'::regclass)` | YES | - | - |
| `user_id` | `bigint(64,0)` | NO | - | - | - | - |
| `group_id` | `bigint(64,0)` | YES | - | - | - | Links related events (recurring events share same group_id) |
| `title` | `character varying(255)` | NO | - | - | - | - |
| `description` | `text` | YES | - | - | - | - |
| `notes` | `text` | YES | - | - | - | - |
| `event_date` | `date` | NO | - | - | - | - |
| `start_time` | `time without time zone` | NO | - | - | - | - |
| `end_time` | `time without time zone` | NO | - | - | - | - |
| `type_id` | `integer(32,0)` | YES | - | - | - | - |
| `category_id` | `integer(32,0)` | YES | - | - | - | - |
| `room_id` | `integer(32,0)` | YES | - | - | - | - |
| `location` | `text` | YES | - | - | - | - |
| `visibility` | `character varying(20)` | YES | `'public'::character varying` | - | - | public: visible to others, private: only creator can see |
| `is_all_day` | `boolean` | YES | `false` | - | - | True for all-day events (ignores start_time/end_time) |
| `customer` | `character varying(20)` | YES | `'confirmed'::character varying` | - | - | confirmed | tentative | cancelled |
| `recurrence_type` | `character varying(20)` | YES | `'none'::character varying` | - | - | none | daily | weekly | monthly |
| `recurrence_end_date` | `date` | YES | - | - | - | - |
| `created_at` | `timestamp with time zone` | YES | `now()` | - | - | - |
| `updated_at` | `timestamp with time zone` | YES | `now()` | - | - | - |
| `is_deleted` | `boolean` | YES | `false` | - | - | - |
| `deleted_at` | `timestamp with time zone` | YES | - | - | - | - |
| `deleted_by_id` | `bigint(64,0)` | YES | - | - | - | - |
| `end_date` | `date` | NO | - | - | - | - |
| `updated_by_id` | `bigint(64,0)` | YES | - | - | - | - |

---

### Table: `public.schedule_rooms`
- **Description**: Master data: Available meeting rooms for booking
- **Row Count**: 13
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `integer(32,0)` | NO | `nextval('schedule_rooms_id_seq'::regclass)` | YES | - | - |
| `name` | `character varying(255)` | NO | - | - | - | - |
| `capacity` | `integer(32,0)` | YES | - | - | - | Maximum number of attendees |
| `description` | `text` | YES | - | - | - | - |
| `sort_order` | `integer(32,0)` | YES | `0` | - | - | - |
| `is_active` | `boolean` | YES | `true` | - | - | - |
| `created_at` | `timestamp with time zone` | YES | `now()` | - | - | - |
| `updated_at` | `timestamp with time zone` | YES | `now()` | - | - | - |

---

### Table: `public.schedule_work_types`
- **Description**: Master data: Work/event types for calendar events
- **Row Count**: 11
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `integer(32,0)` | NO | `nextval('schedule_work_types_id_seq'::regclass)` | YES | - | - |
| `name` | `character varying(100)` | NO | - | - | - | - |
| `color_code` | `character varying(50)` | YES | - | - | - | System color class name (primary/success/warning/info/destructive/secondary) for UI display |
| `icon` | `character varying(50)` | YES | - | - | - | Lucide icon name |
| `sort_order` | `integer(32,0)` | YES | `0` | - | - | - |
| `is_active` | `boolean` | YES | `true` | - | - | - |
| `created_at` | `timestamp with time zone` | YES | `now()` | - | - | - |
| `updated_at` | `timestamp with time zone` | YES | `now()` | - | - | - |

---

## System & Infrastructure Operations

### Table: `public.alert_acknowledgements`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 0
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('alert_acknowledgements_id_seq'::regclass)` | YES | - | - |
| `tenant_id` | `bigint(64,0)` | NO | - | - | - | - |
| `alert_event_id` | `bigint(64,0)` | NO | - | - | - | - |
| `user_id` | `bigint(64,0)` | NO | - | - | - | - |
| `action` | `character varying(30)` | NO | - | - | - | - |
| `comment` | `text` | YES | - | - | - | - |
| `is_deleted` | `boolean` | NO | `false` | - | - | - |
| `deleted_at` | `timestamp with time zone` | YES | - | - | - | - |
| `deleted_by_id` | `bigint(64,0)` | YES | - | - | - | - |
| `created_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `updated_at` | `timestamp with time zone` | NO | `now()` | - | - | - |

---

### Table: `public.alert_events`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 29
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('alert_events_id_seq'::regclass)` | YES | - | - |
| `tenant_id` | `bigint(64,0)` | NO | - | - | - | - |
| `source_id` | `bigint(64,0)` | NO | - | - | - | - |
| `latest_receipt_id` | `bigint(64,0)` | NO | - | - | - | - |
| `provider_event_id` | `character varying(255)` | YES | - | - | - | - |
| `fingerprint` | `character varying(128)` | NO | - | - | - | - |
| `correlation_key` | `character varying(255)` | YES | - | - | - | - |
| `provider_status` | `character varying(30)` | NO | - | - | - | - |
| `handling_status` | `character varying(30)` | NO | `'OPEN'::character varying` | - | - | - |
| `severity` | `character varying(30)` | NO | `'UNKNOWN'::character varying` | - | - | - |
| `title` | `character varying(500)` | NO | - | - | - | - |
| `summary` | `text` | YES | - | - | - | - |
| `description` | `text` | YES | - | - | - | - |
| `resource_type` | `character varying(100)` | YES | - | - | - | - |
| `resource_key` | `character varying(255)` | YES | - | - | - | - |
| `labels` | `jsonb` | NO | `'{}'::jsonb` | - | - | - |
| `annotations` | `jsonb` | NO | `'{}'::jsonb` | - | - | - |
| `starts_at` | `timestamp with time zone` | YES | - | - | - | - |
| `ends_at` | `timestamp with time zone` | YES | - | - | - | - |
| `first_seen_at` | `timestamp with time zone` | NO | - | - | - | - |
| `last_seen_at` | `timestamp with time zone` | NO | - | - | - | - |
| `occurrence_count` | `bigint(64,0)` | NO | `1` | - | - | - |
| `lifecycle_version` | `bigint(64,0)` | NO | `1` | - | - | - |
| `acknowledged_at` | `timestamp with time zone` | YES | - | - | - | - |
| `acknowledged_by_id` | `bigint(64,0)` | YES | - | - | - | - |
| `acknowledgement_comment` | `text` | YES | - | - | - | - |
| `external_url` | `text` | YES | - | - | - | - |
| `runbook_url` | `text` | YES | - | - | - | - |
| `is_deleted` | `boolean` | NO | `false` | - | - | - |
| `deleted_at` | `timestamp with time zone` | YES | - | - | - | - |
| `deleted_by_id` | `bigint(64,0)` | YES | - | - | - | - |
| `created_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `updated_at` | `timestamp with time zone` | NO | `now()` | - | - | - |

---

### Table: `public.alert_route_destinations`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 10
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('alert_route_destinations_id_seq'::regclass)` | YES | - | - |
| `tenant_id` | `bigint(64,0)` | NO | - | - | - | - |
| `route_id` | `bigint(64,0)` | NO | - | - | - | - |
| `destination_type` | `character varying(40)` | NO | - | - | - | - |
| `target_user_id` | `bigint(64,0)` | YES | - | - | - | - |
| `conversation_id` | `bigint(64,0)` | YES | - | - | - | - |
| `actor_user_id` | `bigint(64,0)` | YES | - | - | - | - |
| `is_active` | `boolean` | NO | `true` | - | - | - |
| `is_deleted` | `boolean` | NO | `false` | - | - | - |
| `deleted_at` | `timestamp with time zone` | YES | - | - | - | - |
| `deleted_by_id` | `bigint(64,0)` | YES | - | - | - | - |
| `created_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `updated_at` | `timestamp with time zone` | NO | `now()` | - | - | - |

---

### Table: `public.alert_routes`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 2
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('alert_routes_id_seq'::regclass)` | YES | - | - |
| `tenant_id` | `bigint(64,0)` | NO | - | - | - | - |
| `name` | `character varying(150)` | NO | - | - | - | - |
| `priority` | `integer(32,0)` | NO | `100` | - | - | - |
| `source_id` | `bigint(64,0)` | YES | - | - | - | - |
| `severity` | `character varying(30)` | YES | - | - | - | - |
| `provider_status` | `character varying(30)` | YES | - | - | - | - |
| `label_matchers` | `jsonb` | NO | `'{}'::jsonb` | - | - | - |
| `continue_matching` | `boolean` | NO | `false` | - | - | - |
| `is_enabled` | `boolean` | NO | `true` | - | - | - |
| `created_by_id` | `bigint(64,0)` | NO | - | - | - | - |
| `updated_by_id` | `bigint(64,0)` | YES | - | - | - | - |
| `is_deleted` | `boolean` | NO | `false` | - | - | - |
| `deleted_at` | `timestamp with time zone` | YES | - | - | - | - |
| `deleted_by_id` | `bigint(64,0)` | YES | - | - | - | - |
| `created_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `updated_at` | `timestamp with time zone` | NO | `now()` | - | - | - |

---

### Table: `public.alert_sources`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 3
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('alert_sources_id_seq'::regclass)` | YES | - | - |
| `tenant_id` | `bigint(64,0)` | NO | - | - | - | - |
| `name` | `character varying(150)` | NO | - | - | - | - |
| `provider` | `character varying(30)` | NO | - | - | - | - |
| `auth_type` | `character varying(30)` | NO | - | - | - | - |
| `endpoint_key_hash` | `character varying(64)` | NO | - | - | - | - |
| `secret_ciphertext` | `text` | NO | - | - | - | - |
| `signature_header` | `character varying(100)` | YES | - | - | - | - |
| `timestamp_header` | `character varying(100)` | YES | - | - | - | - |
| `allowed_clock_skew_seconds` | `integer(32,0)` | NO | `300` | - | - | - |
| `is_active` | `boolean` | NO | `true` | - | - | - |
| `created_by_id` | `bigint(64,0)` | NO | - | - | - | - |
| `updated_by_id` | `bigint(64,0)` | YES | - | - | - | - |
| `is_deleted` | `boolean` | NO | `false` | - | - | - |
| `deleted_at` | `timestamp with time zone` | YES | - | - | - | - |
| `deleted_by_id` | `bigint(64,0)` | YES | - | - | - | - |
| `created_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `updated_at` | `timestamp with time zone` | NO | `now()` | - | - | - |

---

### Table: `public.alert_webhook_receipts`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 58
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('alert_webhook_receipts_id_seq'::regclass)` | YES | - | - |
| `tenant_id` | `bigint(64,0)` | NO | - | - | - | - |
| `source_id` | `bigint(64,0)` | NO | - | - | - | - |
| `delivery_key` | `character varying(160)` | NO | - | - | - | - |
| `payload_hash` | `character varying(64)` | NO | - | - | - | - |
| `raw_payload` | `jsonb` | NO | - | - | - | - |
| `request_headers` | `jsonb` | NO | `'{}'::jsonb` | - | - | - |
| `remote_ip` | `character varying(64)` | YES | - | - | - | - |
| `status` | `character varying(30)` | NO | `'PENDING'::character varying` | - | - | - |
| `attempt_count` | `integer(32,0)` | NO | `0` | - | - | - |
| `next_attempt_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `locked_at` | `timestamp with time zone` | YES | - | - | - | - |
| `locked_by` | `character varying(200)` | YES | - | - | - | - |
| `processed_at` | `timestamp with time zone` | YES | - | - | - | - |
| `error_message` | `text` | YES | - | - | - | - |
| `received_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `is_deleted` | `boolean` | NO | `false` | - | - | - |
| `deleted_at` | `timestamp with time zone` | YES | - | - | - | - |
| `deleted_by_id` | `bigint(64,0)` | YES | - | - | - | - |
| `created_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `updated_at` | `timestamp with time zone` | NO | `now()` | - | - | - |

---

### Table: `public.business_audit_events`
- **Description**: Append-only business audit stream. It is not an application diagnostic log and requires a separate access/retention policy.
- **Row Count**: 0
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('business_audit_events_id_seq'::regclass)` | YES | - | - |
| `tenant_id` | `bigint(64,0)` | YES | - | - | - | - |
| `actor_user_id` | `bigint(64,0)` | YES | - | - | - | - |
| `module` | `character varying(80)` | NO | - | - | - | - |
| `event_name` | `character varying(160)` | NO | - | - | - | - |
| `subject_type` | `character varying(120)` | NO | - | - | - | - |
| `subject_id` | `bigint(64,0)` | YES | - | - | - | - |
| `summary` | `text` | NO | - | - | - | - |
| `metadata` | `jsonb` | NO | `'{}'::jsonb` | - | - | - |
| `is_deleted` | `boolean` | NO | `false` | - | - | - |
| `deleted_at` | `timestamp with time zone` | YES | - | - | - | - |
| `deleted_by_id` | `bigint(64,0)` | YES | - | - | - | - |
| `created_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `updated_at` | `timestamp with time zone` | NO | `now()` | - | - | - |

---

### Table: `public.error_catalogs`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 53
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('error_catalogs_id_seq'::regclass)` | YES | - | - |
| `code` | `character varying(50)` | NO | - | - | - | - |
| `module` | `character varying(80)` | NO | - | - | - | - |
| `http_status` | `integer(32,0)` | NO | - | - | - | - |
| `severity` | `character varying(30)` | NO | `'error'::character varying` | - | - | - |
| `title_vi` | `character varying(255)` | NO | - | - | - | - |
| `title_en` | `character varying(255)` | NO | - | - | - | - |
| `title_ko` | `character varying(255)` | NO | - | - | - | - |
| `title_ja` | `character varying(255)` | YES | - | - | - | - |
| `description_vi` | `text` | YES | - | - | - | - |
| `description_en` | `text` | YES | - | - | - | - |
| `description_ko` | `text` | YES | - | - | - | - |
| `description_ja` | `text` | YES | - | - | - | - |
| `user_action_vi` | `text` | YES | - | - | - | - |
| `user_action_en` | `text` | YES | - | - | - | - |
| `user_action_ko` | `text` | YES | - | - | - | - |
| `user_action_ja` | `text` | YES | - | - | - | - |
| `support_action` | `text` | YES | - | - | - | - |
| `is_active` | `boolean` | NO | `true` | - | - | - |
| `is_deleted` | `boolean` | NO | `false` | - | - | - |
| `deleted_at` | `timestamp with time zone` | YES | - | - | - | - |
| `deleted_by_id` | `bigint(64,0)` | YES | - | - | - | - |
| `created_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `updated_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `catalog_key` | `character varying(120)` | NO | - | - | - | - |
| `is_public` | `boolean` | NO | `false` | - | - | - |
| `retryable` | `boolean` | NO | `false` | - | - | - |
| `owner_team` | `character varying(120)` | NO | `'platform'::character varying` | - | - | - |
| `aliases` | `ARRAY` | NO | `ARRAY[]::text[]` | - | - | - |
| `is_deprecated` | `boolean` | NO | `false` | - | - | - |
| `replacement_code` | `character varying(50)` | YES | - | - | - | - |
| `catalog_version` | `character varying(32)` | NO | `'legacy'::character varying` | - | - | - |

---

### Table: `public.error_tracking_outbox`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 201,186
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('error_tracking_outbox_id_seq'::regclass)` | YES | - | - |
| `support_code` | `character varying(64)` | NO | - | - | - | - |
| `payload_json` | `jsonb` | NO | - | - | - | - |
| `status` | `character varying(20)` | NO | `'pending'::character varying` | - | - | - |
| `attempt_count` | `integer(32,0)` | NO | `0` | - | - | - |
| `locked_by` | `character varying(255)` | YES | - | - | - | - |
| `locked_at` | `timestamp with time zone` | YES | - | - | - | - |
| `available_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `last_error` | `text` | YES | - | - | - | - |
| `created_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `sent_at` | `timestamp with time zone` | YES | - | - | - | - |

---

### Table: `public.export_requests`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 203
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('export_requests_id_seq'::regclass)` | YES | - | - |
| `export_request_id` | `character varying(64)` | NO | - | - | - | - |
| `export_type` | `character varying(50)` | NO | - | - | - | - |
| `status` | `character varying(20)` | NO | - | - | - | - |
| `requested_by_user_id` | `integer(32,0)` | NO | - | - | - | - |
| `format` | `character varying(20)` | NO | - | - | - | - |
| `locale` | `character varying(10)` | NO | - | - | - | - |
| `hangfire_job_id` | `text` | YES | - | - | - | - |
| `file_id` | `bigint(64,0)` | YES | - | - | - | - |
| `error` | `text` | YES | - | - | - | - |
| `created_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `started_at` | `timestamp with time zone` | YES | - | - | - | - |
| `completed_at` | `timestamp with time zone` | YES | - | - | - | - |
| `updated_at` | `timestamp with time zone` | NO | `now()` | - | - | - |

---

### Table: `public.files`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 3,255
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('files_id_seq'::regclass)` | YES | - | - |
| `storage_provider` | `character varying(30)` | YES | `'nfs'::character varying` | - | - | - |
| `file_url` | `text` | NO | - | - | - | URL hoặc đường dẫn lưu trữ file |
| `original_name` | `text` | NO | - | - | - | - |
| `content_type` | `character varying(255)` | YES | - | - | - | - |
| `file_ext` | `character varying(20)` | YES | - | - | - | - |
| `size_bytes` | `bigint(64,0)` | YES | - | - | - | - |
| `checksum_sha256` | `character varying(64)` | YES | - | - | - | - |
| `uploaded_by_user_id` | `integer(32,0)` | YES | - | - | - | - |
| `uploaded_at` | `timestamp with time zone` | YES | `now()` | - | - | - |
| `is_deleted` | `boolean` | YES | `false` | - | - | - |
| `deleted_at` | `timestamp with time zone` | YES | - | - | - | - |
| `metadata` | `jsonb` | YES | `'{}'::jsonb` | - | - | - |
| `deleted_by_id` | `integer(32,0)` | YES | - | - | - | ID của user đã xóa file này |
| `request_type` | `character varying(50)` | YES | - | - | - | - |

---

### Table: `public.license_audit_events`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 115
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('license_audit_events_id_seq'::regclass)` | YES | - | - |
| `event_type` | `character varying(80)` | NO | - | - | - | - |
| `status_before` | `character varying(50)` | YES | - | - | - | - |
| `status_after` | `character varying(50)` | YES | - | - | - | - |
| `error_code` | `character varying(80)` | YES | - | - | - | - |
| `actor_user_id` | `bigint(64,0)` | YES | - | - | - | - |
| `request_id` | `character varying(100)` | YES | - | - | - | - |
| `metadata` | `jsonb` | NO | `'{}'::jsonb` | - | - | - |
| `is_deleted` | `boolean` | NO | `false` | - | - | - |
| `deleted_at` | `timestamp with time zone` | YES | - | - | - | - |
| `deleted_by_id` | `bigint(64,0)` | YES | - | - | - | - |
| `created_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `updated_at` | `timestamp with time zone` | NO | `now()` | - | - | - |

---

### Table: `public.license_runtime_states`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 1
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('license_runtime_states_id_seq'::regclass)` | YES | - | - |
| `runtime_key` | `character varying(50)` | NO | `'primary'::character varying` | - | - | - |
| `deployment_id` | `uuid` | NO | - | - | - | - |
| `signed_token` | `text` | YES | - | - | - | - |
| `token_digest` | `character varying(64)` | YES | - | - | - | - |
| `lease_id` | `character varying(100)` | YES | - | - | - | - |
| `license_id` | `character varying(100)` | YES | - | - | - | - |
| `customer_id` | `character varying(100)` | YES | - | - | - | - |
| `edition` | `character varying(50)` | NO | `'unactivated'::character varying` | - | - | - |
| `status` | `character varying(50)` | NO | `'unactivated'::character varying` | - | - | - |
| `features` | `jsonb` | NO | `'[]'::jsonb` | - | - | - |
| `limits` | `jsonb` | NO | `'{}'::jsonb` | - | - | - |
| `activated_at` | `timestamp with time zone` | YES | - | - | - | - |
| `issued_at` | `timestamp with time zone` | YES | - | - | - | - |
| `absolute_expires_at` | `timestamp with time zone` | YES | - | - | - | - |
| `lease_expires_at` | `timestamp with time zone` | YES | - | - | - | - |
| `grace_until` | `timestamp with time zone` | YES | - | - | - | - |
| `last_validated_at` | `timestamp with time zone` | YES | - | - | - | - |
| `highest_trusted_time` | `timestamp with time zone` | YES | - | - | - | - |
| `last_validation_error_code` | `character varying(80)` | YES | - | - | - | - |
| `is_deleted` | `boolean` | NO | `false` | - | - | - |
| `deleted_at` | `timestamp with time zone` | YES | - | - | - | - |
| `deleted_by_id` | `bigint(64,0)` | YES | - | - | - | - |
| `created_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `updated_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `last_online_attempt_at` | `timestamp with time zone` | YES | - | - | - | - |
| `last_online_error_code` | `character varying(80)` | YES | - | - | - | - |
| `renewal_lock_id` | `uuid` | YES | - | - | - | - |
| `renewal_lock_until` | `timestamp with time zone` | YES | - | - | - | - |

---

### Table: `public.schema_migrations`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 77
- **Primary Key**: `migration_name`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `migration_name` | `text` | NO | - | YES | - | - |
| `checksum_sha256` | `character(64)` | NO | - | - | - | - |
| `applied_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `applied_by` | `text` | NO | - | - | - | - |
| `execution_ms` | `bigint(64,0)` | NO | - | - | - | - |
| `source` | `character varying(32)` | NO | - | - | - | - |

---

### Table: `public.server_resource_nodes`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 9
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('server_resource_nodes_id_seq'::regclass)` | YES | - | - |
| `instance` | `character varying(128)` | NO | - | - | - | - |
| `name` | `character varying(128)` | NO | - | - | - | - |
| `role` | `character varying(64)` | NO | - | - | - | - |
| `sort_order` | `integer(32,0)` | NO | `0` | - | - | - |
| `is_active` | `boolean` | NO | `true` | - | - | - |
| `created_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `updated_at` | `timestamp with time zone` | NO | `now()` | - | - | - |

---

### Table: `public.system_logs`
- **Description**: System activity and error logs
- **Row Count**: 729,544
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('system_logs_id_seq'::regclass)` | YES | - | - |
| `level` | `character varying(20)` | NO | `'info'::character varying` | - | - | - |
| `event` | `character varying(100)` | NO | - | - | - | - |
| `message` | `text` | YES | - | - | - | - |
| `user_id` | `bigint(64,0)` | YES | - | - | - | - |
| `request_id` | `character varying(100)` | YES | - | - | - | - |
| `route` | `character varying(255)` | YES | - | - | - | - |
| `method` | `character varying(10)` | YES | - | - | - | - |
| `status_code` | `integer(32,0)` | YES | - | - | - | - |
| `ip_address` | `character varying(50)` | YES | - | - | - | - |
| `user_agent` | `text` | YES | - | - | - | - |
| `request` | `text` | YES | - | - | - | Legacy compatibility column. New request logs store [metadata-only]. |
| `response` | `text` | YES | - | - | - | Legacy compatibility column. New request logs store [metadata-only]. |
| `details` | `jsonb` | YES | `'{}'::jsonb` | - | - | - |
| `error_stack` | `text` | YES | - | - | - | Legacy compatibility column. New request logs do not persist raw exception stacks. |
| `created_at` | `timestamp with time zone` | YES | `now()` | - | - | - |
| `error_code` | `character varying(50)` | YES | - | - | - | - |
| `trace_id` | `character varying(32)` | YES | - | - | - | - |
| `span_id` | `character varying(16)` | YES | - | - | - | - |
| `original_error_code` | `character varying(80)` | YES | - | - | - | - |
| `catalog_version` | `character varying(32)` | YES | - | - | - | - |
| `retryable` | `boolean` | YES | - | - | - | - |
| `module` | `character varying(80)` | YES | - | - | - | - |
| `route_template` | `character varying(255)` | YES | - | - | - | - |
| `duration_ms` | `bigint(64,0)` | YES | - | - | - | - |
| `service` | `character varying(120)` | YES | - | - | - | - |
| `service_version` | `character varying(80)` | YES | - | - | - | - |
| `deployment` | `character varying(120)` | YES | - | - | - | - |
| `environment` | `character varying(80)` | YES | - | - | - | - |
| `tenant_id` | `bigint(64,0)` | YES | - | - | - | - |
| `support_code` | `character varying(64)` | YES | - | - | - | - |

---

### Table: `public.system_settings`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 7
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('system_settings_id_seq'::regclass)` | YES | - | - |
| `setting_key` | `character varying(100)` | NO | - | - | - | - |
| `setting_value` | `text` | YES | - | - | - | - |
| `created_at` | `timestamp with time zone` | YES | `now()` | - | - | - |
| `updated_at` | `timestamp with time zone` | YES | `now()` | - | - | - |

---

## Task & Ticket Management

### Table: `public.asset_disposal_ticket_items`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 0
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('asset_disposal_ticket_items_id_seq'::regclass)` | YES | - | - |
| `ticket_id` | `bigint(64,0)` | NO | - | - | - | - |
| `asset_id` | `bigint(64,0)` | NO | - | - | - | - |
| `asset_code` | `character varying(50)` | NO | - | - | - | - |
| `asset_name` | `character varying(255)` | NO | - | - | - | - |
| `created_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `updated_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `disposal_value` | `numeric(18,2)` | NO | `0` | - | - | - |

---

### Table: `public.asset_disposal_tickets`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 0
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('asset_disposal_tickets_id_seq'::regclass)` | YES | - | - |
| `legacy_disposal_id` | `bigint(64,0)` | YES | - | - | - | - |
| `disposal_type` | `character varying(20)` | NO | - | - | - | - |
| `disposal_date` | `date` | NO | - | - | - | - |
| `disposal_value` | `numeric(18,2)` | YES | `0` | - | - | - |
| `book_value` | `numeric(18,2)` | YES | `0` | - | - | - |
| `gain_loss` | `numeric(18,2)` | YES | `0` | - | - | - |
| `asset_count` | `integer(32,0)` | NO | `0` | - | - | - |
| `buyer_info` | `text` | YES | - | - | - | - |
| `reason` | `text` | NO | - | - | - | - |
| `approval_request_id` | `bigint(64,0)` | YES | - | - | - | - |
| `status` | `character varying(20)` | NO | `'PENDING'::character varying` | - | - | - |
| `created_by_user_id` | `integer(32,0)` | NO | - | - | - | - |
| `created_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `updated_at` | `timestamp with time zone` | NO | `now()` | - | - | - |

---

### Table: `public.asset_maintenance_ticket_items`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 0
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('asset_maintenance_ticket_items_id_seq'::regclass)` | YES | - | - |
| `ticket_id` | `bigint(64,0)` | NO | - | - | - | - |
| `asset_id` | `bigint(64,0)` | NO | - | - | - | - |
| `asset_code` | `character varying(50)` | NO | - | - | - | - |
| `asset_name` | `character varying(255)` | NO | - | - | - | - |
| `created_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `updated_at` | `timestamp with time zone` | NO | `now()` | - | - | - |

---

### Table: `public.asset_maintenance_tickets`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 0
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('asset_maintenance_tickets_id_seq'::regclass)` | YES | - | - |
| `legacy_maintenance_id` | `bigint(64,0)` | YES | - | - | - | - |
| `maintenance_type` | `character varying(20)` | NO | - | - | - | - |
| `title` | `character varying(255)` | NO | - | - | - | - |
| `description` | `text` | YES | - | - | - | - |
| `scheduled_date` | `date` | YES | - | - | - | - |
| `started_at` | `timestamp with time zone` | YES | - | - | - | - |
| `completed_at` | `timestamp with time zone` | YES | - | - | - | - |
| `vendor` | `character varying(255)` | YES | - | - | - | - |
| `cost` | `numeric(18,2)` | YES | `0` | - | - | - |
| `asset_count` | `integer(32,0)` | NO | `0` | - | - | - |
| `status` | `character varying(20)` | NO | `'SCHEDULED'::character varying` | - | - | - |
| `result` | `text` | YES | - | - | - | - |
| `created_by_user_id` | `integer(32,0)` | NO | - | - | - | - |
| `created_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `updated_at` | `timestamp with time zone` | NO | `now()` | - | - | - |

---

### Table: `public.kanban_columns`
- **Description**: Kanban board columns for each project
- **Row Count**: 268
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('kanban_columns_id_seq'::regclass)` | YES | - | - |
| `project_id` | `bigint(64,0)` | NO | - | - | - | - |
| `title` | `text` | NO | - | - | - | - |
| `status_group` | `text` | NO | `'todo'::text` | - | - | todo | in_process | completed |
| `color_class` | `text` | YES | - | - | - | - |
| `position` | `integer(32,0)` | YES | `0` | - | - | Sort order for displaying columns |
| `is_default` | `boolean` | YES | `false` | - | - | New tickets go to this column by default |
| `ticket_limit` | `integer(32,0)` | YES | - | - | - | Work-in-progress limit (0 = unlimited) |
| `created_at` | `timestamp with time zone` | YES | `now()` | - | - | - |
| `updated_at` | `timestamp with time zone` | YES | `now()` | - | - | - |

---

### Table: `public.ticket_assignees`
- **Description**: Users assigned to work on tickets (supports multi-assignee)
- **Row Count**: 1,008
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('ticket_assignees_id_seq'::regclass)` | YES | - | - |
| `ticket_id` | `bigint(64,0)` | NO | - | - | - | - |
| `user_id` | `bigint(64,0)` | NO | - | - | - | - |
| `assigned_at` | `timestamp with time zone` | YES | `now()` | - | - | - |
| `assigned_by_user_id` | `bigint(64,0)` | YES | - | - | - | - |

---

### Table: `public.ticket_attachments`
- **Description**: Files attached to tickets
- **Row Count**: 24
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('ticket_attachments_id_seq'::regclass)` | YES | - | - |
| `ticket_id` | `bigint(64,0)` | NO | - | - | - | - |
| `user_id` | `bigint(64,0)` | NO | - | - | - | - |
| `file_id` | `bigint(64,0)` | YES | - | - | - | - |
| `file_name` | `text` | NO | - | - | - | - |
| `file_url` | `text` | NO | - | - | - | - |
| `file_type` | `text` | YES | - | - | - | - |
| `file_size` | `bigint(64,0)` | YES | - | - | - | - |
| `uploaded_at` | `timestamp with time zone` | YES | `now()` | - | - | - |

---

### Table: `public.ticket_checklists`
- **Description**: Checklist items within tickets
- **Row Count**: 24
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('ticket_checklists_id_seq'::regclass)` | YES | - | - |
| `ticket_id` | `bigint(64,0)` | NO | - | - | - | - |
| `title` | `text` | NO | - | - | - | - |
| `is_completed` | `boolean` | YES | `false` | - | - | - |
| `position` | `integer(32,0)` | YES | `0` | - | - | - |
| `completed_by_user_id` | `bigint(64,0)` | YES | - | - | - | - |
| `completed_at` | `timestamp with time zone` | YES | - | - | - | - |
| `created_at` | `timestamp with time zone` | YES | `now()` | - | - | - |

---

### Table: `public.ticket_comment_attachments`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 3
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('ticket_comment_attachments_id_seq'::regclass)` | YES | - | - |
| `comment_id` | `bigint(64,0)` | NO | - | - | - | - |
| `file_id` | `bigint(64,0)` | NO | - | - | - | - |
| `sort_order` | `integer(32,0)` | NO | `0` | - | - | - |
| `created_at` | `timestamp with time zone` | YES | `now()` | - | - | - |

---

### Table: `public.ticket_comments`
- **Description**: Comments/discussions on tickets with threading support
- **Row Count**: 40
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('ticket_comments_id_seq'::regclass)` | YES | - | - |
| `ticket_id` | `bigint(64,0)` | NO | - | - | - | - |
| `user_id` | `bigint(64,0)` | NO | - | - | - | - |
| `parent_id` | `bigint(64,0)` | YES | - | - | - | Parent comment ID for threaded replies |
| `content` | `text` | YES | - | - | - | - |
| `created_at` | `timestamp with time zone` | YES | `now()` | - | - | - |
| `updated_at` | `timestamp with time zone` | YES | `now()` | - | - | - |
| `is_deleted` | `boolean` | YES | `false` | - | - | - |
| `deleted_at` | `timestamp with time zone` | YES | - | - | - | - |

---

### Table: `public.ticket_custom_field_values`
- **Description**: Actual values for custom fields on tickets
- **Row Count**: 0
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('ticket_custom_field_values_id_seq'::regclass)` | YES | - | - |
| `ticket_id` | `bigint(64,0)` | NO | - | - | - | - |
| `field_id` | `bigint(64,0)` | NO | - | - | - | - |
| `value_text` | `text` | YES | - | - | - | - |
| `value_number` | `numeric(18,4)` | YES | - | - | - | - |
| `value_date` | `timestamp with time zone` | YES | - | - | - | - |
| `value_json` | `jsonb` | YES | - | - | - | - |

---

### Table: `public.ticket_relations`
- **Description**: Dependencies and relationships between tickets
- **Row Count**: 0
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('ticket_relations_id_seq'::regclass)` | YES | - | - |
| `source_ticket_id` | `bigint(64,0)` | NO | - | - | - | - |
| `target_ticket_id` | `bigint(64,0)` | NO | - | - | - | - |
| `relation_type` | `text` | NO | - | - | - | blocks | blocked_by | relates_to | duplicates |
| `created_by_user_id` | `bigint(64,0)` | YES | - | - | - | - |
| `created_at` | `timestamp with time zone` | YES | `now()` | - | - | - |

---

### Table: `public.ticket_supervisors`
- **Description**: Ticket supervisors (người giám sát) mapping
- **Row Count**: 44
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('ticket_supervisors_id_seq'::regclass)` | YES | - | - |
| `ticket_id` | `bigint(64,0)` | NO | - | - | - | Ticket id |
| `user_id` | `bigint(64,0)` | NO | - | - | - | Supervisor user id |
| `assigned_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `assigned_by_user_id` | `bigint(64,0)` | YES | - | - | - | Who assigned supervisor |

---

### Table: `public.ticket_tags`
- **Description**: Tags attached to tickets
- **Row Count**: 96
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('ticket_tags_id_seq'::regclass)` | YES | - | - |
| `ticket_id` | `bigint(64,0)` | NO | - | - | - | - |
| `tag_id` | `bigint(64,0)` | NO | - | - | - | - |

---

### Table: `public.ticket_templates`
- **Description**: Reusable ticket templates
- **Row Count**: 0
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('ticket_templates_id_seq'::regclass)` | YES | - | - |
| `project_id` | `bigint(64,0)` | YES | - | - | - | - |
| `name` | `text` | NO | - | - | - | - |
| `title_template` | `text` | YES | - | - | - | - |
| `description_template` | `text` | YES | - | - | - | - |
| `default_priority` | `text` | YES | - | - | - | - |
| `default_tags` | `jsonb` | YES | `'[]'::jsonb` | - | - | - |
| `checklist_items` | `jsonb` | YES | `'[]'::jsonb` | - | - | - |
| `created_at` | `timestamp with time zone` | YES | `now()` | - | - | - |

---

### Table: `public.ticket_time_logs`
- **Description**: Time tracking entries for tickets
- **Row Count**: 0
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('ticket_time_logs_id_seq'::regclass)` | YES | - | - |
| `ticket_id` | `bigint(64,0)` | NO | - | - | - | - |
| `user_id` | `bigint(64,0)` | NO | - | - | - | - |
| `description` | `text` | YES | - | - | - | - |
| `started_at` | `timestamp with time zone` | NO | - | - | - | - |
| `ended_at` | `timestamp with time zone` | YES | - | - | - | - |
| `duration_minutes` | `integer(32,0)` | YES | - | - | - | - |
| `is_billable` | `boolean` | YES | `false` | - | - | - |
| `created_at` | `timestamp with time zone` | YES | `now()` | - | - | - |

---

### Table: `public.ticket_types`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 258
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | - | YES | - | - |
| `project_id` | `bigint(64,0)` | NO | - | - | - | - |
| `name` | `character varying(100)` | NO | - | - | - | - |
| `icon` | `character varying(80)` | YES | - | - | - | - |
| `color` | `character varying(32)` | YES | - | - | - | - |
| `position` | `integer(32,0)` | NO | `0` | - | - | - |
| `is_default` | `boolean` | NO | `false` | - | - | - |
| `is_deleted` | `boolean` | NO | `false` | - | - | - |
| `created_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `updated_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `created_by_user_id` | `bigint(64,0)` | YES | - | - | - | - |
| `updated_by_user_id` | `bigint(64,0)` | YES | - | - | - | - |

---

### Table: `public.ticket_watchers`
- **Description**: Users watching tickets for notifications
- **Row Count**: 0
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('ticket_watchers_id_seq'::regclass)` | YES | - | - |
| `ticket_id` | `bigint(64,0)` | NO | - | - | - | - |
| `user_id` | `bigint(64,0)` | NO | - | - | - | - |
| `created_at` | `timestamp with time zone` | YES | `now()` | - | - | - |

---

### Table: `public.tickets`
- **Description**: Main tickets/tasks/issues table
- **Row Count**: 668
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('tickets_id_seq'::regclass)` | YES | - | - |
| `project_id` | `bigint(64,0)` | NO | - | - | - | - |
| `sprint_id` | `bigint(64,0)` | YES | - | - | - | - |
| `parent_ticket_id` | `bigint(64,0)` | YES | - | - | - | - |
| `code` | `text` | YES | - | - | - | Human-readable ticket code (e.g., NFF-123) |
| `title` | `text` | NO | - | - | - | - |
| `description` | `text` | YES | - | - | - | - |
| `priority` | `text` | YES | `'medium'::text` | - | - | urgent | high | medium | low |
| `due_date` | `timestamp with time zone` | YES | - | - | - | - |
| `start_date` | `timestamp with time zone` | YES | - | - | - | - |
| `completed_at` | `timestamp with time zone` | YES | - | - | - | - |
| `estimated_hours` | `numeric(10,2)` | YES | - | - | - | - |
| `story_points` | `integer(32,0)` | YES | - | - | - | - |
| `comments_count` | `integer(32,0)` | YES | `0` | - | - | - |
| `attachments_count` | `integer(32,0)` | YES | `0` | - | - | - |
| `checklists_count` | `integer(32,0)` | YES | `0` | - | - | - |
| `checklists_completed` | `integer(32,0)` | YES | `0` | - | - | - |
| `position` | `bigint(64,0)` | YES | `0` | - | - | Sort order within kanban column for drag & drop |
| `created_by_user_id` | `bigint(64,0)` | NO | - | - | - | - |
| `created_at` | `timestamp with time zone` | YES | `now()` | - | - | - |
| `updated_at` | `timestamp with time zone` | YES | `now()` | - | - | - |
| `is_deleted` | `boolean` | YES | `false` | - | - | - |
| `deleted_at` | `timestamp with time zone` | YES | - | - | - | - |
| `deleted_by_id` | `bigint(64,0)` | YES | - | - | - | - |
| `note` | `text` | YES | - | - | - | - |
| `status` | `text` | NO | `'create'::text` | - | - | - |
| `column_id` | `bigint(64,0)` | YES | - | - | - | - |
| `actual_hours` | `numeric(10,2)` | YES | - | - | - | Actual time spent in hours (manual) |
| `type_id` | `bigint(64,0)` | YES | - | - | - | - |
| `quantity` | `numeric(18,4)` | NO | `0` | - | - | - |
| `unit_price` | `numeric(18,2)` | NO | `0` | - | - | - |

---

## User & Identity Management

### Table: `public.action_translations`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 88
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `integer(32,0)` | NO | `nextval('action_translations_id_seq'::regclass)` | YES | - | - |
| `action_id` | `integer(32,0)` | NO | - | - | - | - |
| `locale` | `character varying(10)` | NO | - | - | - | - |
| `name` | `character varying(100)` | NO | - | - | - | - |
| `description` | `text` | YES | - | - | - | - |

---

### Table: `public.actions`
- **Description**: Available actions (VIEW, CREATE, UPDATE, DELETE, etc.)
- **Row Count**: 39
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `integer(32,0)` | NO | `nextval('actions_id_seq'::regclass)` | YES | - | - |
| `code` | `character varying(50)` | NO | - | - | - | - |
| `name` | `character varying(100)` | NO | - | - | - | - |
| `description` | `text` | YES | - | - | - | - |
| `category` | `character varying(50)` | YES | `'CRUD'::character varying` | - | - | - |
| `created_at` | `timestamp with time zone` | YES | `now()` | - | - | - |

---

### Table: `public.alert_action_outbox`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 85
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('alert_action_outbox_id_seq'::regclass)` | YES | - | - |
| `tenant_id` | `bigint(64,0)` | NO | - | - | - | - |
| `alert_event_id` | `bigint(64,0)` | NO | - | - | - | - |
| `route_destination_id` | `bigint(64,0)` | NO | - | - | - | - |
| `lifecycle_version` | `bigint(64,0)` | NO | - | - | - | - |
| `provider_status` | `character varying(30)` | NO | - | - | - | - |
| `destination_type` | `character varying(40)` | NO | - | - | - | - |
| `target_user_id` | `bigint(64,0)` | YES | - | - | - | - |
| `conversation_id` | `bigint(64,0)` | YES | - | - | - | - |
| `actor_user_id` | `bigint(64,0)` | YES | - | - | - | - |
| `payload` | `jsonb` | NO | - | - | - | - |
| `status` | `character varying(30)` | NO | `'PENDING'::character varying` | - | - | - |
| `attempt_count` | `integer(32,0)` | NO | `0` | - | - | - |
| `next_attempt_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `locked_at` | `timestamp with time zone` | YES | - | - | - | - |
| `locked_by` | `character varying(200)` | YES | - | - | - | - |
| `completed_at` | `timestamp with time zone` | YES | - | - | - | - |
| `result_reference_id` | `bigint(64,0)` | YES | - | - | - | - |
| `error_message` | `text` | YES | - | - | - | - |
| `is_deleted` | `boolean` | NO | `false` | - | - | - |
| `deleted_at` | `timestamp with time zone` | YES | - | - | - | - |
| `deleted_by_id` | `bigint(64,0)` | YES | - | - | - | - |
| `created_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `updated_at` | `timestamp with time zone` | NO | `now()` | - | - | - |

---

### Table: `public.audience_user_members`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 39
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('audience_user_members_id_seq'::regclass)` | YES | - | - |
| `audience_id` | `integer(32,0)` | NO | - | - | - | - |
| `user_id` | `integer(32,0)` | NO | - | - | - | - |
| `created_at` | `timestamp with time zone` | YES | `now()` | - | - | - |

---

### Table: `public.bot_account_mappings`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 0
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('bot_account_mappings_id_seq'::regclass)` | YES | - | - |
| `user_id` | `bigint(64,0)` | NO | - | - | - | - |
| `chatbot_user_id` | `text` | NO | - | - | - | - |
| `chatbot_user_version` | `integer(32,0)` | NO | - | - | - | - |
| `updated_by_id` | `bigint(64,0)` | NO | - | - | - | - |
| `created_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `updated_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `is_deleted` | `boolean` | NO | `false` | - | - | - |
| `deleted_at` | `timestamp with time zone` | YES | - | - | - | - |
| `deleted_by_id` | `bigint(64,0)` | YES | - | - | - | - |

---

### Table: `public.bot_chat_realtime_outbox`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 0
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('bot_chat_realtime_outbox_id_seq'::regclass)` | YES | - | - |
| `user_id` | `bigint(64,0)` | NO | - | - | - | - |
| `event_name` | `character varying(120)` | NO | - | - | - | - |
| `payload` | `jsonb` | NO | `'{}'::jsonb` | - | - | - |
| `status` | `character varying(20)` | NO | `'pending'::character varying` | - | - | - |
| `attempt_count` | `integer(32,0)` | NO | `0` | - | - | - |
| `available_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `locked_at` | `timestamp with time zone` | YES | - | - | - | - |
| `locked_by` | `character varying(160)` | YES | - | - | - | - |
| `last_error` | `text` | YES | - | - | - | - |
| `created_at` | `timestamp with time zone` | NO | `now()` | - | - | - |

---

### Table: `public.bot_messages`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 7,436
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('bot_messages_id_seq'::regclass)` | YES | - | - |
| `thread_id` | `bigint(64,0)` | NO | - | - | - | - |
| `sender_type` | `character varying(16)` | NO | - | - | - | - |
| `content` | `text` | NO | - | - | - | - |
| `provider_message_id` | `text` | YES | - | - | - | - |
| `metadata` | `jsonb` | NO | `'{}'::jsonb` | - | - | - |
| `created_at` | `timestamp with time zone` | NO | `now()` | - | - | - |

---

### Table: `public.bot_requests`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 3,543
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('bot_requests_id_seq'::regclass)` | YES | - | - |
| `thread_id` | `bigint(64,0)` | NO | - | - | - | - |
| `user_message_id` | `bigint(64,0)` | NO | - | - | - | - |
| `status` | `character varying(24)` | NO | - | - | - | - |
| `provider_request_id` | `text` | YES | - | - | - | - |
| `response_message_id` | `bigint(64,0)` | YES | - | - | - | - |
| `attempt_count` | `integer(32,0)` | NO | `0` | - | - | - |
| `last_error` | `text` | YES | - | - | - | - |
| `metadata` | `jsonb` | NO | `'{}'::jsonb` | - | - | - |
| `created_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `updated_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `completed_at` | `timestamp with time zone` | YES | - | - | - | - |

---

### Table: `public.bot_threads`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 610
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('bot_threads_id_seq'::regclass)` | YES | - | - |
| `user_id` | `bigint(64,0)` | NO | - | - | - | - |
| `provider_thread_id` | `text` | YES | - | - | - | - |
| `last_read_message_id` | `bigint(64,0)` | YES | - | - | - | - |
| `last_read_at` | `timestamp with time zone` | YES | - | - | - | - |
| `last_message_at` | `timestamp with time zone` | YES | - | - | - | - |
| `metadata` | `jsonb` | NO | `'{}'::jsonb` | - | - | - |
| `created_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `updated_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `title` | `character varying(80)` | YES | - | - | - | - |
| `client_thread_id` | `uuid` | YES | - | - | - | - |
| `is_default` | `boolean` | NO | `false` | - | - | - |
| `is_deleted` | `boolean` | NO | `false` | - | - | - |
| `deleted_at` | `timestamp with time zone` | YES | - | - | - | - |
| `deleted_by_id` | `bigint(64,0)` | YES | - | - | - | - |

---

### Table: `public.chat_message_hidden_for_users`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 14
- **Primary Key**: `message_id, user_id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `message_id` | `bigint(64,0)` | NO | - | YES | - | - |
| `user_id` | `bigint(64,0)` | NO | - | YES | - | - |
| `hidden_at` | `timestamp with time zone` | NO | `now()` | - | - | - |

---

### Table: `public.chat_message_reactions`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 421
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('chat_message_reactions_id_seq'::regclass)` | YES | - | - |
| `message_id` | `bigint(64,0)` | NO | - | - | - | - |
| `user_id` | `integer(32,0)` | NO | - | - | - | - |
| `reaction_code` | `character varying(20)` | NO | - | - | - | - |
| `created_at` | `timestamp with time zone` | YES | `now()` | - | - | - |

---

### Table: `public.login_qr_challenges`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 142
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('login_qr_challenges_id_seq'::regclass)` | YES | - | - |
| `public_id` | `uuid` | NO | - | - | - | - |
| `secret_hash` | `text` | NO | - | - | - | - |
| `status` | `character varying(24)` | NO | - | - | - | - |
| `user_code` | `character varying(16)` | NO | - | - | - | - |
| `requested_platform` | `character varying(16)` | NO | `'web'::character varying` | - | - | - |
| `requested_device_name` | `character varying(255)` | YES | - | - | - | - |
| `requested_user_agent` | `text` | YES | - | - | - | - |
| `requested_ip_address` | `character varying(64)` | YES | - | - | - | - |
| `requested_locale` | `character varying(16)` | YES | - | - | - | - |
| `approved_by_user_id` | `bigint(64,0)` | YES | - | - | - | - |
| `approved_mobile_session_id` | `bigint(64,0)` | YES | - | - | - | - |
| `approved_device_id` | `character varying(255)` | YES | - | - | - | - |
| `approved_device_name` | `character varying(255)` | YES | - | - | - | - |
| `approved_ip_address` | `character varying(64)` | YES | - | - | - | - |
| `approved_at` | `timestamp with time zone` | YES | - | - | - | - |
| `denied_at` | `timestamp with time zone` | YES | - | - | - | - |
| `consumed_at` | `timestamp with time zone` | YES | - | - | - | - |
| `consumed_session_id` | `bigint(64,0)` | YES | - | - | - | - |
| `expires_at` | `timestamp with time zone` | NO | - | - | - | - |
| `created_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `updated_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `requested_device_id` | `character varying(255)` | YES | - | - | - | - |

---

### Table: `public.menu_actions`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 246
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `integer(32,0)` | NO | `nextval('menu_actions_id_seq'::regclass)` | YES | - | - |
| `menu_id` | `integer(32,0)` | NO | - | - | - | - |
| `action_id` | `integer(32,0)` | NO | - | - | - | - |
| `display_name` | `character varying(100)` | YES | - | - | - | - |
| `created_at` | `timestamp with time zone` | YES | `now()` | - | - | - |

---

### Table: `public.menu_translations`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 298
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `integer(32,0)` | NO | `nextval('menu_translations_id_seq'::regclass)` | YES | - | - |
| `menu_id` | `integer(32,0)` | NO | - | - | - | - |
| `locale` | `character varying(10)` | NO | - | - | - | - |
| `name` | `character varying(100)` | NO | - | - | - | - |
| `description` | `text` | YES | - | - | - | - |

---

### Table: `public.menus`
- **Description**: Menu structure for the application
- **Row Count**: 77
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `integer(32,0)` | NO | `nextval('menus_id_seq'::regclass)` | YES | - | - |
| `code` | `character varying(50)` | NO | - | - | - | - |
| `name` | `character varying(100)` | NO | - | - | - | - |
| `path` | `character varying(255)` | YES | - | - | - | - |
| `icon` | `character varying(50)` | YES | - | - | - | - |
| `parent_id` | `integer(32,0)` | YES | - | - | - | - |
| `sort_order` | `integer(32,0)` | YES | `0` | - | - | - |
| `is_active` | `boolean` | YES | `true` | - | - | - |
| `metadata` | `jsonb` | YES | `'{}'::jsonb` | - | - | - |
| `created_at` | `timestamp with time zone` | YES | `now()` | - | - | - |
| `updated_at` | `timestamp with time zone` | YES | `now()` | - | - | - |

---

### Table: `public.permissions`
- **Description**: Permission definitions
- **Row Count**: 247
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `integer(32,0)` | NO | `nextval('permissions_id_seq'::regclass)` | YES | - | - |
| `code` | `character varying(100)` | NO | - | - | - | - |
| `resource_type` | `character varying(50)` | NO | - | - | - | - |
| `resource_id` | `integer(32,0)` | YES | - | - | - | - |
| `action_id` | `integer(32,0)` | YES | - | - | - | - |
| `description` | `text` | YES | - | - | - | - |
| `created_at` | `timestamp with time zone` | YES | `now()` | - | - | - |
| `rule_id` | `bigint(64,0)` | YES | - | - | - | - |

---

### Table: `public.role_permissions`
- **Description**: Permissions granted to roles
- **Row Count**: 1,535
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `integer(32,0)` | NO | `nextval('role_permissions_id_seq'::regclass)` | YES | - | - |
| `role_id` | `integer(32,0)` | NO | - | - | - | - |
| `permission_id` | `integer(32,0)` | NO | - | - | - | - |
| `is_granted` | `boolean` | YES | `true` | - | - | - |
| `granted_at` | `timestamp with time zone` | YES | `now()` | - | - | - |
| `granted_by` | `integer(32,0)` | YES | - | - | - | - |
| `tenant_id` | `bigint(64,0)` | NO | - | - | - | - |

---

### Table: `public.roles`
- **Description**: Role definitions for RBAC
- **Row Count**: 42
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `integer(32,0)` | NO | `nextval('roles_id_seq'::regclass)` | YES | - | - |
| `code` | `character varying(50)` | NO | - | - | - | - |
| `name` | `character varying(100)` | NO | - | - | - | - |
| `description` | `text` | YES | - | - | - | - |
| `level` | `integer(32,0)` | NO | `99` | - | - | - |
| `is_active` | `boolean` | YES | `true` | - | - | - |
| `is_system` | `boolean` | YES | `false` | - | - | - |
| `created_at` | `timestamp with time zone` | YES | `now()` | - | - | - |
| `updated_at` | `timestamp with time zone` | YES | `now()` | - | - | - |
| `created_by` | `integer(32,0)` | YES | - | - | - | - |
| `tenant_id` | `bigint(64,0)` | NO | - | - | - | - |

---

### Table: `public.talk_post_comment_reactions`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 41
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('talk_post_comment_reactions_id_seq'::regclass)` | YES | - | - |
| `comment_id` | `bigint(64,0)` | NO | - | - | - | - |
| `user_id` | `integer(32,0)` | NO | - | - | - | - |
| `reaction_type` | `character varying(20)` | YES | `'LIKE'::character varying` | - | - | - |
| `created_at` | `timestamp with time zone` | YES | `now()` | - | - | - |

---

### Table: `public.talk_post_reactions`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 210
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('talk_post_reactions_id_seq'::regclass)` | YES | - | - |
| `post_id` | `bigint(64,0)` | NO | - | - | - | - |
| `user_id` | `integer(32,0)` | NO | - | - | - | - |
| `reaction_type` | `character varying(20)` | YES | `'LIKE'::character varying` | - | - | - |
| `created_at` | `timestamp with time zone` | YES | `now()` | - | - | - |

---

### Table: `public.tenant_domains`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 0
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('tenant_domains_id_seq'::regclass)` | YES | - | - |
| `tenant_id` | `bigint(64,0)` | NO | - | - | - | - |
| `host` | `character varying(253)` | NO | - | - | - | - |
| `is_primary` | `boolean` | NO | `false` | - | - | - |
| `is_verified` | `boolean` | NO | `false` | - | - | - |
| `created_by_id` | `bigint(64,0)` | YES | - | - | - | - |
| `updated_by_id` | `bigint(64,0)` | YES | - | - | - | - |
| `is_deleted` | `boolean` | NO | `false` | - | - | - |
| `deleted_at` | `timestamp with time zone` | YES | - | - | - | - |
| `deleted_by_id` | `bigint(64,0)` | YES | - | - | - | - |
| `created_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `updated_at` | `timestamp with time zone` | NO | `now()` | - | - | - |

---

### Table: `public.tenant_user_memberships`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 360
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('tenant_user_memberships_id_seq'::regclass)` | YES | - | - |
| `tenant_id` | `bigint(64,0)` | NO | - | - | - | - |
| `user_id` | `bigint(64,0)` | NO | - | - | - | - |
| `status` | `character varying(32)` | NO | `'invited'::character varying` | - | - | - |
| `is_default` | `boolean` | NO | `false` | - | - | - |
| `joined_at` | `timestamp with time zone` | YES | - | - | - | - |
| `created_by_id` | `bigint(64,0)` | YES | - | - | - | - |
| `updated_by_id` | `bigint(64,0)` | YES | - | - | - | - |
| `is_deleted` | `boolean` | NO | `false` | - | - | - |
| `deleted_at` | `timestamp with time zone` | YES | - | - | - | - |
| `deleted_by_id` | `bigint(64,0)` | YES | - | - | - | - |
| `created_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `updated_at` | `timestamp with time zone` | NO | `now()` | - | - | - |

---

### Table: `public.tenants`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 1
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('tenants_id_seq'::regclass)` | YES | - | - |
| `tenant_key` | `character varying(64)` | NO | - | - | - | - |
| `name` | `character varying(255)` | NO | - | - | - | - |
| `status` | `character varying(32)` | NO | `'provisioning'::character varying` | - | - | - |
| `isolation_mode` | `character varying(32)` | NO | `'pooled'::character varying` | - | - | - |
| `is_default` | `boolean` | NO | `false` | - | - | - |
| `created_by_id` | `bigint(64,0)` | YES | - | - | - | - |
| `updated_by_id` | `bigint(64,0)` | YES | - | - | - | - |
| `is_deleted` | `boolean` | NO | `false` | - | - | - |
| `deleted_at` | `timestamp with time zone` | YES | - | - | - | - |
| `deleted_by_id` | `bigint(64,0)` | YES | - | - | - | - |
| `created_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `updated_at` | `timestamp with time zone` | NO | `now()` | - | - | - |

---

### Table: `public.ticket_comment_reactions`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 2
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('ticket_comment_reactions_id_seq'::regclass)` | YES | - | - |
| `comment_id` | `bigint(64,0)` | NO | - | - | - | - |
| `user_id` | `bigint(64,0)` | NO | - | - | - | - |
| `reaction_type` | `character varying(20)` | NO | `'LIKE'::character varying` | - | - | - |
| `created_at` | `timestamp with time zone` | NO | `now()` | - | - | - |

---

### Table: `public.user_approval_favorites`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 40
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `integer(32,0)` | NO | `nextval('user_approval_favorites_id_seq'::regclass)` | YES | - | - |
| `owner_user_id` | `integer(32,0)` | NO | - | - | - | - |
| `favorite_user_id` | `integer(32,0)` | NO | - | - | - | - |
| `favorite_role` | `character varying(20)` | NO | - | - | - | - |
| `sort_order` | `integer(32,0)` | YES | `0` | - | - | - |
| `created_at` | `timestamp with time zone` | YES | `now()` | - | - | - |

---

### Table: `public.user_chat_sticker_packs`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 27
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('user_chat_sticker_packs_id_seq'::regclass)` | YES | - | - |
| `user_id` | `bigint(64,0)` | NO | - | - | - | - |
| `pack_id` | `bigint(64,0)` | NO | - | - | - | - |
| `is_deleted` | `boolean` | NO | `false` | - | - | - |
| `deleted_at` | `timestamp with time zone` | YES | - | - | - | - |
| `deleted_by_id` | `bigint(64,0)` | YES | - | - | - | - |
| `created_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `updated_at` | `timestamp with time zone` | NO | `now()` | - | - | - |

---

### Table: `public.user_contract_histories`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 457
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('user_contract_histories_id_seq'::regclass)` | YES | - | - |
| `user_id` | `bigint(64,0)` | NO | - | - | - | - |
| `contract_type` | `character varying(100)` | YES | - | - | - | - |
| `contract_period_from` | `date` | YES | - | - | - | - |
| `contract_period_to` | `date` | YES | - | - | - | - |
| `is_current` | `boolean` | NO | `true` | - | - | - |
| `note` | `text` | YES | - | - | - | - |
| `created_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `updated_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `created_by_user_id` | `bigint(64,0)` | YES | - | - | - | - |
| `updated_by_user_id` | `bigint(64,0)` | YES | - | - | - | - |
| `tenant_id` | `bigint(64,0)` | NO | - | - | - | - |

---

### Table: `public.user_department_data_scopes`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 3
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('user_department_data_scopes_id_seq'::regclass)` | YES | - | - |
| `tenant_id` | `bigint(64,0)` | NO | - | - | - | - |
| `user_id` | `bigint(64,0)` | NO | - | - | - | - |
| `permission_code` | `character varying(150)` | NO | - | - | - | - |
| `department_id` | `bigint(64,0)` | NO | - | - | - | - |
| `include_descendants` | `boolean` | NO | `false` | - | - | - |
| `is_deleted` | `boolean` | NO | `false` | - | - | - |
| `deleted_at` | `timestamp with time zone` | YES | - | - | - | - |
| `deleted_by_id` | `bigint(64,0)` | YES | - | - | - | - |
| `created_by_id` | `bigint(64,0)` | YES | - | - | - | - |
| `created_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `updated_at` | `timestamp with time zone` | NO | `now()` | - | - | - |

---

### Table: `public.user_favorites`
- **Description**: User bookmarks/favorites for quick access
- **Row Count**: 0
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('user_favorites_id_seq'::regclass)` | YES | - | - |
| `user_id` | `bigint(64,0)` | NO | - | - | - | - |
| `entity_type` | `text` | NO | - | - | - | - |
| `entity_id` | `bigint(64,0)` | NO | - | - | - | - |
| `created_at` | `timestamp with time zone` | YES | `now()` | - | - | - |

---

### Table: `public.user_leave_month_end_snapshots`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 4,308
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('user_leave_month_end_snapshots_id_seq'::regclass)` | YES | - | - |
| `user_id` | `bigint(64,0)` | NO | - | - | - | - |
| `year` | `integer(32,0)` | NO | - | - | - | - |
| `month` | `integer(32,0)` | NO | - | - | - | - |
| `carryover_remaining_days` | `numeric(7,2)` | NO | `0` | - | - | - |
| `manual_remaining_days` | `numeric(7,2)` | NO | `0` | - | - | - |
| `seniority_remaining_days` | `numeric(7,2)` | NO | `0` | - | - | - |
| `monthly_remaining_days` | `numeric(7,2)` | NO | `0` | - | - | - |
| `total_remaining_days` | `numeric(7,2)` | NO | `0` | - | - | - |
| `current_month_accrued_days` | `numeric(7,2)` | NO | `0` | - | - | - |
| `used_days` | `numeric(7,2)` | NO | `0` | - | - | - |
| `updated_by_user_id` | `bigint(64,0)` | YES | - | - | - | - |
| `created_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `updated_at` | `timestamp with time zone` | NO | `now()` | - | - | - |

---

### Table: `public.user_leave_monthly_balances`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 4,238
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('user_leave_monthly_balances_id_seq'::regclass)` | YES | - | - |
| `user_id` | `bigint(64,0)` | NO | - | - | - | - |
| `year` | `integer(32,0)` | NO | - | - | - | - |
| `month` | `integer(32,0)` | NO | - | - | - | - |
| `accrued_days` | `numeric(7,2)` | NO | `0` | - | - | - |
| `used_days` | `numeric(7,2)` | NO | `0` | - | - | - |
| `note` | `text` | YES | - | - | - | - |
| `updated_by_user_id` | `bigint(64,0)` | YES | - | - | - | - |
| `created_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `updated_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `pending_accrued_days` | `numeric(7,2)` | NO | `0` | - | - | - |

---

### Table: `public.user_leave_year_balances`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 353
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('user_leave_year_balances_id_seq'::regclass)` | YES | - | - |
| `user_id` | `bigint(64,0)` | NO | - | - | - | - |
| `year` | `integer(32,0)` | NO | - | - | - | - |
| `opening_days` | `numeric(7,2)` | NO | `0` | - | - | - |
| `carryover_days` | `numeric(7,2)` | NO | `0` | - | - | - |
| `seniority_days` | `numeric(7,2)` | NO | `0` | - | - | - |
| `manual_adjustment_days` | `numeric(7,2)` | NO | `0` | - | - | - |
| `note` | `text` | YES | - | - | - | - |
| `updated_by_user_id` | `bigint(64,0)` | YES | - | - | - | - |
| `created_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `updated_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `remaining_days` | `numeric(6,2)` | NO | `0` | - | - | - |
| `carryover_granted_days` | `numeric(7,2)` | NO | `0` | - | - | - |
| `carryover_used_before_reset_days` | `numeric(7,2)` | NO | `0` | - | - | - |
| `carryover_expired_days` | `numeric(7,2)` | NO | `0` | - | - | - |
| `carryover_available_days` | `numeric(7,2)` | NO | `0` | - | - | - |

---

### Table: `public.user_permissions`
- **Description**: Direct permission assignments to users (override role permissions)
- **Row Count**: 51
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `integer(32,0)` | NO | `nextval('user_permissions_id_seq'::regclass)` | YES | - | - |
| `user_id` | `integer(32,0)` | NO | - | - | - | - |
| `permission_id` | `integer(32,0)` | NO | - | - | - | - |
| `is_granted` | `boolean` | YES | `true` | - | - | TRUE = grant permission, FALSE = explicitly deny |
| `granted_at` | `timestamp with time zone` | YES | `now()` | - | - | - |
| `granted_by` | `integer(32,0)` | YES | - | - | - | - |
| `tenant_id` | `bigint(64,0)` | NO | - | - | - | - |

---

### Table: `public.user_profiles`
- **Description**: User profile + HR info
- **Row Count**: 360
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `integer(32,0)` | NO | `nextval('user_profiles_id_seq'::regclass)` | YES | - | - |
| `user_id` | `integer(32,0)` | NO | - | - | - | - |
| `display_name` | `character varying(150)` | YES | - | - | - | - |
| `avatar_url` | `text` | YES | - | - | - | - |
| `birth_date` | `date` | YES | - | - | - | - |
| `mobile_phone` | `character varying(30)` | YES | - | - | - | - |
| `office_phone` | `character varying(30)` | YES | - | - | - | - |
| `fax_number` | `character varying(30)` | YES | - | - | - | - |
| `employee_number` | `character varying(50)` | YES | - | - | - | - |
| `department_id` | `integer(32,0)` | YES | - | - | - | - |
| `grade` | `character varying(50)` | YES | - | - | - | - |
| `duty` | `character varying(50)` | YES | - | - | - | - |
| `joining_date` | `date` | YES | - | - | - | - |
| `locale` | `character varying(10)` | YES | `'vi'::character varying` | - | - | - |
| `timezone` | `character varying(50)` | YES | - | - | - | - |
| `created_at` | `timestamp with time zone` | YES | `now()` | - | - | - |
| `updated_at` | `timestamp with time zone` | YES | `now()` | - | - | - |
| `bio` | `text` | YES | - | - | - | User biography or about me text |
| `address` | `text` | YES | - | - | - | User physical address |
| `social_links` | `jsonb` | YES | `'[]'::jsonb` | - | - | JSON array of social media links [{platform, url, icon}] |
| `cover_image_url` | `text` | YES | - | - | - | URL for profile cover/banner image |
| `eng_name` | `character varying(255)` | YES | - | - | - | English name for international display |
| `gender` | `character varying(20)` | YES | - | - | - | Gender (Male/Female) |
| `section` | `character varying(100)` | YES | - | - | - | Sub-department or team name |
| `contract_type` | `character varying(100)` | YES | - | - | - | Contract type (e.g., LC-2 year, Permanent, Probation) |
| `contract_period_from` | `date` | YES | - | - | - | Contract start date |
| `contract_period_to` | `date` | YES | - | - | - | Contract end date |
| `position` | `character varying(100)` | YES | - | - | - | Job title/position (e.g., General Director, Head of Division) |
| `is_resigned` | `boolean` | NO | `false` | - | - | - |
| `resigned_at` | `timestamp with time zone` | YES | - | - | - | - |
| `attendance_mode` | `character varying(20)` | NO | `'fixed'::character varying` | - | - | - |
| `tenant_id` | `bigint(64,0)` | NO | - | - | - | - |
| `tax_code` | `character varying(50)` | YES | - | - | - | - |

---

### Table: `public.user_restore_history`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 4
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('user_restore_history_id_seq'::regclass)` | YES | - | - |
| `user_id` | `bigint(64,0)` | NO | - | - | - | - |
| `restored_by_user_id` | `bigint(64,0)` | NO | - | - | - | - |
| `restored_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `previous_deleted_at` | `timestamp with time zone` | YES | - | - | - | - |
| `tenant_id` | `bigint(64,0)` | NO | - | - | - | - |

---

### Table: `public.user_role_assignments`
- **Description**: Assigns roles to users (supports multi-role)
- **Row Count**: 448
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `integer(32,0)` | NO | `nextval('user_role_assignments_id_seq'::regclass)` | YES | - | - |
| `user_id` | `integer(32,0)` | NO | - | - | - | - |
| `role_id` | `integer(32,0)` | NO | - | - | - | - |
| `assigned_at` | `timestamp with time zone` | YES | `now()` | - | - | - |
| `assigned_by` | `integer(32,0)` | YES | - | - | - | - |
| `tenant_id` | `bigint(64,0)` | NO | - | - | - | - |

---

### Table: `public.user_sessions`
- **Description**: No table comment provided in database catalog.
- **Row Count**: 6,274
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `bigint(64,0)` | NO | `nextval('user_sessions_id_seq'::regclass)` | YES | - | - |
| `user_id` | `bigint(64,0)` | NO | - | - | - | - |
| `platform` | `character varying(16)` | NO | - | - | - | - |
| `refresh_token_hash` | `text` | NO | - | - | - | - |
| `session_key` | `uuid` | NO | - | - | - | - |
| `device_id` | `character varying(191)` | YES | - | - | - | - |
| `device_name` | `character varying(255)` | YES | - | - | - | - |
| `user_agent` | `text` | YES | - | - | - | - |
| `ip_address` | `character varying(64)` | YES | - | - | - | - |
| `is_active` | `boolean` | NO | `true` | - | - | - |
| `created_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `last_seen_at` | `timestamp with time zone` | NO | `now()` | - | - | - |
| `expires_at` | `timestamp with time zone` | NO | - | - | - | - |
| `revoked_at` | `timestamp with time zone` | YES | - | - | - | - |
| `revoked_reason` | `character varying(64)` | YES | - | - | - | - |
| `impersonated_by_user_id` | `bigint(64,0)` | YES | - | - | - | - |
| `impersonation_started_at` | `timestamp with time zone` | YES | - | - | - | - |
| `public_ip_address` | `character varying(64)` | YES | - | - | - | - |
| `tenant_id` | `bigint(64,0)` | YES | - | - | - | - |

---

### Table: `public.users`
- **Description**: User accounts for the system
- **Row Count**: 360
- **Primary Key**: `id`

| Column Name | Data Type | Nullable | Default | PK | FK Target | Description |
|---|---|---|---|---|---|---|
| `id` | `integer(32,0)` | NO | `nextval('users_id_seq'::regclass)` | YES | - | - |
| `username` | `character varying(50)` | NO | - | - | - | - |
| `email` | `character varying(255)` | NO | - | - | - | - |
| `password_hash` | `character varying(255)` | YES | - | - | - | - |
| `created_at` | `timestamp with time zone` | YES | `now()` | - | - | - |
| `updated_at` | `timestamp with time zone` | YES | `now()` | - | - | - |
| `last_login` | `timestamp with time zone` | YES | - | - | - | - |
| `is_active` | `boolean` | YES | `true` | - | - | - |
| `email_verified` | `boolean` | YES | `false` | - | - | - |
| `email_verification_token` | `character varying(255)` | YES | - | - | - | - |
| `email_verification_expires_at` | `timestamp with time zone` | YES | - | - | - | - |
| `is_deleted` | `boolean` | NO | `false` | - | - | Soft delete flag - TRUE means user is deleted |
| `deleted_at` | `timestamp with time zone` | YES | - | - | - | Timestamp when user was soft deleted |
| `edited_by_id` | `bigint(64,0)` | YES | - | - | - | ID of user who last edited this record |
| `restored_at` | `timestamp with time zone` | YES | - | - | - | - |

---

