# 24 – Phase 1.1 Final Source-to-Graph Mapping Specification
## Groupware AI Chatbot Project – PostgreSQL to Neo4j Executable ETL Contract

> [!IMPORTANT]
> **Strict ETL Engineering Rules**:
> 1. **NO SELECT ***: All extraction SQL queries must explicitly declare the exact column names being selected. Under no circumstances may `SELECT *` be used in production ingestion specifications.
> 2. **Canonical Table & Column Fidelity**: Every table and column referenced herein is verified against the actual PostgreSQL schema. Erroneous names from earlier drafts (e.g., `sprints`, `workflow_templates`, `community_posts`, `projects.code`, `tickets.ticket_number`, `approval_request_participants`) are permanently replaced by canonical physical names.
> 3. **Defensive Ingestion**: Null handling, soft-delete filtering (`WHERE is_deleted = false AND deleted_at IS NULL`), and orphan reference safety (`OPTIONAL MATCH`) are mandated for all ingestion scripts.

---

## 1. Node Extraction SQL & Ingestion Cypher Contracts

### 1.1 `:Tenant` Node Mapping
- **Source Table**: `public.tenants`
- **Extraction SQL**:
  ```sql
  SELECT 
    id, 
    code, 
    name, 
    status, 
    created_at 
  FROM tenants;
  ```
- **Cypher Ingestion Contract**:
  ```cypher
  UNWIND $batch AS row
  MERGE (t:Tenant {id: toInteger(row.id)})
  ON CREATE SET 
    t.code = row.code,
    t.name = row.name,
    t.status = row.status,
    t.created_at = datetime(row.created_at);
  ```

### 1.2 `:User` Node Mapping
- **Source Tables**: `public.users` INNER JOIN `public.user_profiles` ON `users.id = user_profiles.user_id`
- **Extraction SQL**:
  ```sql
  SELECT 
    u.id AS user_id,
    p.tenant_id AS tenant_id,
    u.username AS username,
    u.email AS email,
    p.display_name AS display_name,
    u.is_active AS is_active,
    p.department_id AS department_id,
    p.employee_number AS employee_number,
    p.position AS position,
    p.grade AS grade,
    u.created_at AS created_at
  FROM users u
  INNER JOIN user_profiles p ON u.id = p.user_id
  WHERE u.is_deleted = false 
    AND u.deleted_at IS NULL;
  ```
- **Cypher Ingestion Contract**:
  ```cypher
  UNWIND $batch AS row
  MERGE (u:User {id: toInteger(row.user_id)})
  ON CREATE SET 
    u.tenant_id = toInteger(row.tenant_id),
    u.username = row.username,
    u.email = row.email,
    u.display_name = row.display_name,
    u.is_active = row.is_active,
    u.department_id = toInteger(row.department_id),
    u.employee_number = row.employee_number,
    u.position = row.position,
    u.grade = row.grade,
    u.created_at = datetime(row.created_at);
  ```

### 1.3 `:Department` Node Mapping
- **Source Table**: `public.departments`
- **Extraction SQL**:
  ```sql
  SELECT 
    id, 
    tenant_id, 
    code, 
    name, 
    parent_id, 
    manager_user_id, 
    depth, 
    is_active 
  FROM departments
  WHERE is_active = true;
  ```
- **Cypher Ingestion Contract**:
  ```cypher
  UNWIND $batch AS row
  MERGE (d:Department {id: toInteger(row.id)})
  ON CREATE SET 
    d.tenant_id = toInteger(row.tenant_id),
    d.code = row.code,
    d.name = row.name,
    d.parent_id = toInteger(row.parent_id),
    d.manager_user_id = toInteger(row.manager_user_id),
    d.depth = toInteger(row.depth),
    d.is_active = row.is_active;
  ```

### 1.4 `:Project` Node Mapping
- **Source Table**: `public.projects` JOIN `public.user_profiles` ON `projects.created_by_user_id = user_profiles.user_id`
- **Extraction SQL**:
  ```sql
  SELECT 
    p.id AS project_id,
    prof.tenant_id AS tenant_id,
    p.key AS project_key,
    p.name AS name,
    p.status AS status,
    p.created_by_user_id AS created_by_user_id,
    p.start_date AS start_date,
    p.end_date AS end_date,
    p.description AS description
  FROM projects p
  LEFT JOIN user_profiles prof ON p.created_by_user_id = prof.user_id
  WHERE p.is_deleted = false 
    AND p.deleted_at IS NULL;
  ```
- **Cypher Ingestion Contract**:
  ```cypher
  UNWIND $batch AS row
  MERGE (p:Project {id: toInteger(row.project_id)})
  ON CREATE SET 
    p.tenant_id = toInteger(row.tenant_id),
    p.key = row.project_key,
    p.name = row.name,
    p.status = row.status,
    p.created_by_user_id = toInteger(row.created_by_user_id),
    p.start_date = datetime(row.start_date),
    p.end_date = datetime(row.end_date),
    p.description = row.description;
  ```

### 1.5 `:Ticket` Node Mapping
- **Source Table**: `public.tickets`
- **Extraction SQL**:
  ```sql
  SELECT 
    t.id AS ticket_id,
    t.project_id AS project_id,
    t.sprint_id AS sprint_id,
    t.column_id AS column_id,
    t.code AS ticket_code,
    t.title AS title,
    t.priority AS priority,
    t.status AS status,
    t.created_by_user_id AS created_by_user_id,
    t.due_date AS due_date,
    t.estimated_hours AS estimated_hours
  FROM tickets t
  WHERE t.is_deleted = false 
    AND t.deleted_at IS NULL;
  ```
- **Cypher Ingestion Contract**:
  ```cypher
  UNWIND $batch AS row
  MERGE (t:Ticket {id: toInteger(row.ticket_id)})
  ON CREATE SET 
    t.project_id = toInteger(row.project_id),
    t.sprint_id = toInteger(row.sprint_id),
    t.column_id = toInteger(row.column_id),
    t.code = row.ticket_code,
    t.title = row.title,
    t.priority = row.priority,
    t.status = row.status,
    t.created_by_user_id = toInteger(row.created_by_user_id),
    t.due_date = datetime(row.due_date),
    t.estimated_hours = toFloat(row.estimated_hours);
  ```

### 1.6 `:Sprint` Node Mapping (Table: `project_sprints`)
- **Source Table**: `public.project_sprints`
- **Extraction SQL**:
  ```sql
  SELECT 
    id, 
    project_id, 
    name, 
    goal, 
    start_date, 
    end_date, 
    status 
  FROM project_sprints;
  ```
- **Cypher Ingestion Contract**:
  ```cypher
  UNWIND $batch AS row
  MERGE (s:Sprint {id: toInteger(row.id)})
  ON CREATE SET 
    s.project_id = toInteger(row.project_id),
    s.name = row.name,
    s.goal = row.goal,
    s.start_date = date(row.start_date),
    s.end_date = date(row.end_date),
    s.status = row.status;
  ```

### 1.7 `:KanbanColumn` Node Mapping
- **Source Table**: `public.kanban_columns`
- **Extraction SQL**:
  ```sql
  SELECT 
    id, 
    project_id, 
    title, 
    position, 
    status_group 
  FROM kanban_columns;
  ```
- **Cypher Ingestion Contract**:
  ```cypher
  UNWIND $batch AS row
  MERGE (k:KanbanColumn {id: toInteger(row.id)})
  ON CREATE SET 
    k.project_id = toInteger(row.project_id),
    k.title = row.title,
    k.position = toInteger(row.position),
    k.status_group = row.status_group;
  ```

### 1.8 `:ApprovalRequest` Node Mapping
- **Source Table**: `public.approval_requests`
- **Extraction SQL**:
  ```sql
  SELECT 
    id, 
    code, 
    request_type, 
    status, 
    title, 
    reason, 
    created_by_user_id, 
    submitted_at, 
    completed_at, 
    total_days, 
    leave_type 
  FROM approval_requests
  WHERE is_deleted = false 
    AND deleted_at IS NULL;
  ```
- **Cypher Ingestion Contract**:
  ```cypher
  UNWIND $batch AS row
  MERGE (a:ApprovalRequest {id: toInteger(row.id)})
  ON CREATE SET 
    a.code = row.code,
    a.request_type = row.request_type,
    a.status = row.status,
    a.title = row.title,
    a.reason = row.reason,
    a.created_by_user_id = toInteger(row.created_by_user_id),
    a.submitted_at = datetime(row.submitted_at),
    a.completed_at = datetime(row.completed_at),
    a.total_days = toFloat(row.total_days),
    a.leave_type = row.leave_type;
  ```

### 1.9 `:WorkflowTemplate` Node Mapping (Table: `approval_workflow_templates`)
- **Source Table**: `public.approval_workflow_templates`
- **Extraction SQL**:
  ```sql
  SELECT 
    id, 
    code, 
    name, 
    request_type, 
    priority, 
    is_active 
  FROM approval_workflow_templates
  WHERE is_active = true;
  ```
- **Cypher Ingestion Contract**:
  ```cypher
  UNWIND $batch AS row
  MERGE (w:WorkflowTemplate {id: toInteger(row.id)})
  ON CREATE SET 
    w.code = row.code,
    w.name = row.name,
    w.request_type = row.request_type,
    w.priority = toInteger(row.priority),
    w.is_active = row.is_active;
  ```

### 1.10 `:ScheduleEvent` Node Mapping
- **Source Table**: `public.schedule_events`
- **Extraction SQL**:
  ```sql
  SELECT 
    id, 
    user_id, 
    title, 
    description, 
    event_date, 
    start_time, 
    end_time, 
    room_id, 
    location, 
    visibility 
  FROM schedule_events
  WHERE is_deleted = false 
    AND deleted_at IS NULL;
  ```
- **Cypher Ingestion Contract**:
  ```cypher
  UNWIND $batch AS row
  MERGE (e:ScheduleEvent {id: toInteger(row.id)})
  ON CREATE SET 
    e.user_id = toInteger(row.user_id),
    e.title = row.title,
    e.description = row.description,
    e.event_date = date(row.event_date),
    e.start_time = time(row.start_time),
    e.end_time = time(row.end_time),
    e.room_id = toInteger(row.room_id),
    e.location = row.location,
    e.visibility = row.visibility;
  ```

### 1.11 `:ScheduleRoom` Node Mapping
- **Source Table**: `public.schedule_rooms`
- **Extraction SQL**:
  ```sql
  SELECT 
    id, 
    name, 
    capacity, 
    description, 
    sort_order, 
    is_active 
  FROM schedule_rooms
  WHERE is_active = true;
  ```
- **Cypher Ingestion Contract**:
  ```cypher
  UNWIND $batch AS row
  MERGE (r:ScheduleRoom {id: toInteger(row.id)})
  ON CREATE SET 
    r.name = row.name,
    r.capacity = toInteger(row.capacity),
    r.description = row.description,
    r.sort_order = toInteger(row.sort_order),
    r.is_active = row.is_active;
  ```

### 1.12 `:Notice` Node Mapping
- **Source Table**: `public.notices`
- **Extraction SQL**:
  ```sql
  SELECT 
    id, 
    title, 
    notice_type, 
    audience_id, 
    created_by_user_id, 
    is_published, 
    published_at 
  FROM notices
  WHERE is_published = true;
  ```
- **Cypher Ingestion Contract**:
  ```cypher
  UNWIND $batch AS row
  MERGE (n:Notice {id: toInteger(row.id)})
  ON CREATE SET 
    n.title = row.title,
    n.notice_type = row.notice_type,
    n.audience_id = toInteger(row.audience_id),
    n.created_by_user_id = toInteger(row.created_by_user_id),
    n.is_published = row.is_published,
    n.published_at = datetime(row.published_at);
  ```

### 1.13 `:Post` Node Mapping (Table: `talk_posts`)
- **Source Table**: `public.talk_posts`
- **Extraction SQL**:
  ```sql
  SELECT 
    id, 
    author_user_id, 
    audience_id, 
    title, 
    created_at 
  FROM talk_posts
  WHERE is_deleted = false 
    AND deleted_at IS NULL;
  ```
- **Cypher Ingestion Contract**:
  ```cypher
  UNWIND $batch AS row
  MERGE (p:Post {id: toInteger(row.id)})
  ON CREATE SET 
    p.author_user_id = toInteger(row.author_user_id),
    p.audience_id = toInteger(row.audience_id),
    p.title = row.title,
    p.created_at = datetime(row.created_at);
  ```

### 1.14 `:Asset` Node Mapping
- **Source Table**: `public.assets`
- **Extraction SQL**:
  ```sql
  SELECT 
    id, 
    code, 
    name, 
    description, 
    category_id, 
    status, 
    location, 
    department_id, 
    assigned_user_id 
  FROM assets
  WHERE is_deleted = false 
    AND deleted_at IS NULL;
  ```
- **Cypher Ingestion Contract**:
  ```cypher
  UNWIND $batch AS row
  MERGE (a:Asset {id: toInteger(row.id)})
  ON CREATE SET 
    a.code = row.code,
    a.name = row.name,
    a.description = row.description,
    a.category_id = toInteger(row.category_id),
    a.status = row.status,
    a.location = row.location,
    a.department_id = toInteger(row.department_id),
    a.assigned_user_id = toInteger(row.assigned_user_id);
  ```

### 1.15 `:FileMetadata` Node Mapping
- **Source Table**: `public.files`
- **Extraction SQL**:
  ```sql
  SELECT 
    id, 
    storage_provider, 
    original_name, 
    content_type, 
    file_ext, 
    size_bytes, 
    uploaded_by_user_id, 
    uploaded_at 
  FROM files;
  ```
- **Cypher Ingestion Contract**:
  ```cypher
  UNWIND $batch AS row
  MERGE (f:FileMetadata {id: toInteger(row.id)})
  ON CREATE SET 
    f.storage_provider = row.storage_provider,
    f.original_name = row.original_name,
    f.content_type = row.content_type,
    f.file_ext = row.file_ext,
    f.size_bytes = toInteger(row.size_bytes),
    f.uploaded_by_user_id = toInteger(row.uploaded_by_user_id),
    f.uploaded_at = datetime(row.uploaded_at);
  ```

### 1.16 `:ChatConversation` Node Mapping (Option A)
- **Source Table**: `public.chat_conversations`
- **Extraction SQL**:
  ```sql
  SELECT 
    id, 
    conversation_type, 
    title, 
    created_by_user_id, 
    created_at 
  FROM chat_conversations;
  ```
- **Cypher Ingestion Contract**:
  ```cypher
  UNWIND $batch AS row
  MERGE (c:ChatConversation {id: toInteger(row.id)})
  ON CREATE SET 
    c.conversation_type = row.conversation_type,
    c.title = row.title,
    c.created_by_user_id = toInteger(row.created_by_user_id),
    c.created_at = datetime(row.created_at);
  ```

### 1.17 `:ContractHistory` Node Mapping (Masked HR Policy)
- **Source Table**: `public.user_contract_histories`
- **Extraction SQL**:
  ```sql
  SELECT 
    id, 
    user_id, 
    contract_type, 
    start_date, 
    end_date, 
    status, 
    created_at 
  FROM user_contract_histories;
  ```
- **Cypher Ingestion Contract**:
  ```cypher
  UNWIND $batch AS row
  MERGE (ch:ContractHistory {id: toInteger(row.id)})
  ON CREATE SET 
    ch.user_id = toInteger(row.user_id),
    ch.contract_type = row.contract_type,
    ch.start_date = date(row.start_date),
    ch.end_date = date(row.end_date),
    ch.status = row.status,
    ch.created_at = datetime(row.created_at);
  ```

---

## 2. Relationship Ingestion Contracts

### 2.1 Ticket Assignment Junction Mapping
- **Source Table**: `public.ticket_assignees`
- **Extraction SQL**:
  ```sql
  SELECT 
    id, 
    ticket_id, 
    user_id, 
    assigned_at 
  FROM ticket_assignees;
  ```
- **Cypher Ingestion Contract**:
  ```cypher
  UNWIND $batch AS row
  MATCH (t:Ticket {id: toInteger(row.ticket_id)})
  MATCH (u:User {id: toInteger(row.user_id)})
  MERGE (t)-[r:ASSIGNED_TO]->(u)
  ON CREATE SET r.assigned_at = datetime(row.assigned_at);
  ```

### 2.2 Approval Participants Ingestion
- **Source Table**: `public.approval_participants`
- **Extraction SQL**:
  ```sql
  SELECT 
    id, 
    request_id, 
    user_id, 
    participant_role, 
    sequence_order, 
    action_status, 
    acted_at, 
    note 
  FROM approval_participants;
  ```
- **Cypher Ingestion Contract**:
  ```cypher
  UNWIND $batch AS row
  MATCH (u:User {id: toInteger(row.user_id)})
  MATCH (a:ApprovalRequest {id: toInteger(row.request_id)})
  MERGE (u)-[p:PARTICIPATES_IN]->(a)
  ON CREATE SET 
    p.participant_role = row.participant_role,
    p.sequence_order = toInteger(row.sequence_order),
    p.action_status = row.action_status,
    p.acted_at = datetime(row.acted_at),
    p.note = row.note;
  ```

### 2.3 Schedule Event Participants Ingestion
- **Source Table**: `public.schedule_event_participants`
- **Extraction SQL**:
  ```sql
  SELECT 
    id, 
    event_id, 
    user_id, 
    status, 
    is_required 
  FROM schedule_event_participants;
  ```
- **Cypher Ingestion Contract**:
  ```cypher
  UNWIND $batch AS row
  MATCH (u:User {id: toInteger(row.user_id)})
  MATCH (e:ScheduleEvent {id: toInteger(row.event_id)})
  MERGE (u)-[r:ATTENDS_EVENT]->(e)
  ON CREATE SET 
    r.status = row.status,
    r.is_required = row.is_required;
  ```

### 2.4 User Role Assignments Ingestion
- **Source Table**: `public.user_role_assignments`
- **Extraction SQL**:
  ```sql
  SELECT 
    id, 
    user_id, 
    role_id, 
    assigned_at, 
    assigned_by, 
    tenant_id 
  FROM user_role_assignments;
  ```
- **Cypher Ingestion Contract**:
  ```cypher
  UNWIND $batch AS row
  MATCH (u:User {id: toInteger(row.user_id)})
  MATCH (r:Role {id: toInteger(row.role_id)})
  MERGE (u)-[rel:HAS_ROLE]->(r)
  ON CREATE SET 
    rel.assigned_at = datetime(row.assigned_at),
    rel.assigned_by = toInteger(row.assigned_by),
    rel.tenant_id = toInteger(row.tenant_id);
  ```

---

## 3. Production ETL Synchronization Contract

| Lifecycle Event | PostgreSQL Source Trigger / CDC | Neo4j Graph Synchronization Action |
|---|---|---|
| **Initial Load** | Full table export in batches of 2,000 rows | `UNWIND $batch ... MERGE (n:Label {id: ...}) ON CREATE SET ...` |
| **Incremental Insert** | Debezium / Kafka CDC event `op = 'c'` | `MERGE (n:Label {id: ...}) ON CREATE SET ...` |
| **Incremental Update** | Debezium / Kafka CDC event `op = 'u'` | `MATCH (n:Label {id: ...}) SET n += $properties` |
| **Soft Delete** | Update event with `is_deleted = true` | `MATCH (n:Label {id: ...}) DETACH DELETE n` (Removes from active graph) |
| **Hard Delete** | Debezium / Kafka CDC event `op = 'd'` | `MATCH (n:Label {id: ...}) DETACH DELETE n` |
| **Orphan Handling** | Partial match during foreign reference load | Ingestion Cypher must use `MATCH (src) OPTIONAL MATCH (tgt) WITH src, tgt WHERE tgt IS NOT NULL MERGE (src)-[:REL]->(tgt)` |
| **Retry & Idempotency** | Network partition or deadlocks | Exponential backoff retry with 3 attempts; all ingestion statements idempotent via `MERGE` |
