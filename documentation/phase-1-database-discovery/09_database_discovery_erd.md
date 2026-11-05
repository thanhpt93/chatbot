# 09 – Database Discovery ERD & Proposed Neo4j Graph Model
## Groupware AI Chatbot Project – Phase 1: Canonical Baseline & Architectural Reconciliation

> [!IMPORTANT]
> **Strict Architectural Separation**:
> This document provides two separate, non-interchangeable architectural diagrams:
> - **Diagram 1**: Relational Database Discovery ERD (Physical tables, PKs, explicit FKs, and inferred domain references labeled `REF`).
> - **Diagram 2**: Proposed Neo4j Graph Data Model (Approved node labels, relationship types, properties, tenant boundaries, and Vector RAG integration boundary).

---

## 1. Diagram 1: Relational Database Discovery ERD

```mermaid
erDiagram
    TENANTS ||--o{ TENANT_USER_MEMBERSHIPS : pools
    TENANTS ||--o{ DEPARTMENTS : scopes
    USERS ||--|| USER_PROFILES : has_profile
    USERS ||--o{ TENANT_USER_MEMBERSHIPS : member_of
    USERS ||--o{ DEPARTMENT_MEMBERS : belongs_to
    DEPARTMENTS ||--o{ DEPARTMENT_MEMBERS : contains
    DEPARTMENTS ||--o| DEPARTMENTS : parent_of
    DEPARTMENTS ||--o| USERS : managed_by

    USERS ||--o{ PROJECTS : creates
    PROJECTS ||--o{ PROJECT_MEMBERS : staffed_by
    USERS ||--o{ PROJECT_MEMBERS : participates_as_owner_or_member
    PROJECTS ||--o{ KANBAN_COLUMNS : defines_stages
    PROJECTS ||--o{ PROJECT_SPRINTS : iterates
    PROJECTS ||--o{ TICKETS : contains
    KANBAN_COLUMNS ||--o{ TICKETS : tracks_state
    TICKETS ||--o{ TICKET_ASSIGNEES : assigns_to
    USERS ||--o{ TICKET_ASSIGNEES : works_on

    USERS ||--o{ APPROVAL_REQUESTS : creates_request
    APPROVAL_REQUESTS ||--o{ APPROVAL_PARTICIPANTS : reviewed_by
    USERS ||--o{ APPROVAL_PARTICIPANTS : signs_off

    USERS ||--o{ ATTENDANCE_DAILY_RECORDS : logs_daily_work
    USERS ||--o{ SCHEDULE_EVENTS : organizes
    SCHEDULE_ROOMS ||--o{ SCHEDULE_EVENTS : hosts
    SCHEDULE_EVENTS ||--o{ SCHEDULE_EVENT_PARTICIPANTS : invites
    USERS ||--o{ SCHEDULE_EVENT_PARTICIPANTS : attends

    USERS ||--o{ CHAT_CONVERSATIONS : creates
    CHAT_CONVERSATIONS ||--o{ CHAT_CONVERSATION_MEMBERS : includes
    USERS ||--o{ CHAT_CONVERSATION_MEMBERS : chats_in

    USERS ||--o{ NOTICES : publishes
    NOTICES ||--o{ NOTICE_READS : read_by
    USERS ||--o{ NOTICE_READS : acknowledges

    USERS ||--o{ ASSETS : assigned_to
    ASSET_CATEGORIES ||--o{ ASSETS : classifies

    TENANTS {
        bigint id PK
        string name
        string slug
    }

    USERS {
        int id PK "integer(32,0)"
        string username
        string email
        string display_name
        boolean is_active
    }

    USER_PROFILES {
        int id PK "integer(32,0)"
        int user_id REF "integer(32,0) - Inferred Ref"
        bigint tenant_id REF "Inferred Ref"
        bigint department_id REF "Inferred Ref"
        string employee_number
        string position
    }

    TENANT_USER_MEMBERSHIPS {
        bigint id PK
        bigint tenant_id REF "Inferred Ref"
        int user_id REF "integer(32,0) - Inferred Ref"
        string status
        boolean is_default
    }

    DEPARTMENTS {
        bigint id PK
        bigint tenant_id REF "Inferred Ref"
        string code
        string name
        bigint parent_id REF "Self-ref"
        int manager_user_id REF "integer(32,0) - Inferred Ref"
    }

    DEPARTMENT_MEMBERS {
        bigint id PK
        bigint department_id REF "Inferred Ref"
        bigint user_id REF "Inferred Ref"
        boolean is_primary
    }

    PROJECTS {
        bigint id PK
        string key
        string name
        string status
        bigint created_by_user_id REF "Creator Identity"
        bigint approved_by_user_id REF "Inferred Ref"
    }

    PROJECT_MEMBERS {
        bigint id PK
        bigint project_id REF "Inferred Ref"
        bigint user_id REF "Inferred Ref"
        string role "owner / admin / member"
    }

    TICKETS {
        bigint id PK
        bigint project_id REF "Inferred Ref"
        bigint column_id REF "Inferred Ref"
        string title
        string priority
        bigint created_by_user_id REF "Creator Identity"
    }

    KANBAN_COLUMNS {
        bigint id PK
        bigint project_id REF "Inferred Ref"
        string name
        int sort_order
    }

    APPROVAL_REQUESTS {
        bigint id PK
        string code
        string title
        string status
        int created_by_user_id REF "integer(32,0) - Request Creator"
    }

    APPROVAL_PARTICIPANTS {
        bigint id PK
        bigint request_id REF "Inferred Ref to approval_requests.id"
        int user_id REF "integer(32,0) - Signoff Approver"
        string participant_role
        int sequence_order
        string action_status
    }

    ATTENDANCE_DAILY_RECORDS {
        bigint id PK
        bigint user_id REF "Inferred Ref"
        date work_date
        time first_check_in
        time last_check_out
        boolean is_late
    }

    SCHEDULE_EVENTS {
        bigint id PK
        date event_date
        time start_time
        time end_time
        string title
        int room_id REF "Inferred Ref"
        bigint user_id REF "Organizer Inferred Ref"
    }

    SCHEDULE_ROOMS {
        int id PK
        string name
        int capacity
    }

    CHAT_CONVERSATIONS {
        bigint id PK
        string title
        string type
        int creator_id REF "Inferred Ref"
    }

    NOTICES {
        bigint id PK
        string title
        text content
        int created_by_user_id REF "Inferred Ref"
    }

    ASSETS {
        bigint id PK
        string code
        string name
        string serial_number
        int category_id REF "Inferred Ref"
        int assigned_user_id REF "Custodian Inferred Ref"
    }

    ASSET_CATEGORIES {
        int id PK
        string name
        string code
    }
```

---

## 2. Diagram 2: Proposed Neo4j Graph Data Model (Architecture B)

```mermaid
graph TD
    subgraph Neo4j_Graph_Database [Neo4j Enterprise Graph Database]
        Tenant["(:Tenant {id, name, slug})"]
        User["(:User {id, username, email, display_name})"]
        Department["(:Department {id, code, name, tenant_id})"]
        Role["(:Role {id, name, code})"]
        Permission["(:Permission {id, name, code})"]

        Project["(:Project {id, key, name, status, tenant_id})"]
        Ticket["(:Ticket {id, title, priority, tenant_id})"]
        KanbanColumn["(:KanbanColumn {id, name, sort_order})"]
        Sprint["(:Sprint {id, name, start_date, end_date})"]

        Approval["(:ApprovalRequest {id, code, title, status, tenant_id})"]
        Template["(:WorkflowTemplate {id, name, code})"]

        Attendance["(:AttendanceRecord {id, work_date, is_late, tenant_id})"]
        Leave["(:LeaveBalance {id, year, remaining_days, tenant_id})"]

        ScheduleEvent["(:ScheduleEvent {id, event_date, start_time, end_time, tenant_id})"]
        Room["(:ScheduleRoom {id, name, capacity})"]

        Channel["(:ChatConversation {id, title, type, tenant_id})"]
        Notice["(:Notice {id, title, published_at, tenant_id})"]
        Post["(:CommunityPost {id, title, tenant_id})"]
        Asset["(:Asset {id, code, name, serial_number, tenant_id})"]
        Category["(:AssetCategory {id, name})"]
        File["(:File {id, file_name, file_size, mime_type, tenant_id})"]
        Audience["(:Audience {id, name, tenant_id})"]

        User -->|MEMBER_OF| Tenant
        Department -->|BELONGS_TO| Tenant
        User -->|MEMBER_OF| Department
        User -->|MANAGES| Department
        Department -->|PARENT_OF| Department

        User -->|HAS_ROLE| Role
        Role -->|HAS_PERMISSION| Permission

        Project -->|CREATED_BY| User
        Project -->|HAS_MEMBER {role: 'owner'}| User
        Project -->|HAS_MEMBER {role: 'member'}| User
        Project -->|CONTAINS| Ticket
        Ticket -->|CURRENT_STAGE| KanbanColumn
        Ticket -->|ASSIGNED_TO| User
        Ticket -->|CREATED_BY| User
        Ticket -->|PART_OF_SPRINT| Sprint

        Approval -->|CREATED_BY| User
        Approval -->|PARTICIPATES_IN {role, sequence, status}| User
        Approval -->|BASED_ON| Template

        User -->|HAS_ATTENDANCE| Attendance
        User -->|HAS_LEAVE_BALANCE| Leave

        ScheduleEvent -->|ORGANIZED_BY| User
        ScheduleEvent -->|INVITES| User
        ScheduleEvent -->|RESERVED_IN| Room

        Channel -->|CREATED_BY| User
        User -->|MEMBER_OF| Channel

        Notice -->|PUBLISHED_BY| User
        Notice -->|TARGETS_AUDIENCE| Audience
        Audience -->|TARGETS_DEPARTMENT| Department

        Post -->|POSTED_BY| User
        Asset -->|ASSIGNED_TO| User
        Asset -->|CATEGORY| Category
        Ticket -->|ATTACHED_FILE| File
    end

    subgraph Vector_RAG_Store [Vector Database - Semantic Storage]
        VectorMessages["ChatMessage Vector Chunks
- Embedding Vector
- message_id
- conversation_id
- sender_user_id
- timestamp
- content"]
    end

    Channel -.->|metadata.conversation_id link| VectorMessages
```

---

## 3. Key Distinctions Between Relational and Graph Models

1. **Denormalization of Attributes**:
   - `user_profiles` is folded directly into `(:User)` properties (`employee_number`, `position`, `grade`).
2. **First-Class Junction Modeling**:
   - `project_members` is transformed into rich edge `[:HAS_MEMBER {role: 'owner' / 'admin' / 'member'}]`.
   - `approval_participants` is transformed into edge `[:PARTICIPATES_IN {participant_role, sequence_order, action_status}]`.
3. **Option A Vector RAG Boundary**:
   - `chat_messages` is NOT modeled as nodes in Neo4j. It resides in Vector DB and connects to `ChatConversation` via `metadata.conversation_id` filtering.
