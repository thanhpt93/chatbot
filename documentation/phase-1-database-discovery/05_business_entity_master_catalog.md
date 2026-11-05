# 05 / 11 – Business Entity Master Catalog
## Groupware AI Chatbot Project – Phase 1: Canonical Baseline & Architectural Reconciliation

> [!NOTE]
> This document establishes the **authoritative Business Entity Master Catalog** for the Groupware project. It resolves all previous catalog variations, explicitly distinguishes **Source Entity**, **Graph Entity**, and **Vector RAG Entity**, incorporates verified PostgreSQL source data types, and defines architectural candidacy for all 23 investigated business entities.
>
> *(Both `05_business_entity_master_catalog.md` and `11_business_entity_master_catalog.md` represent the identical, synchronized canonical deliverable to preserve legacy cross-references).*

---

## 1. Architectural Concept Disambiguation

To prevent design conflation, Phase 1 strictly distinguishes three operational concepts:

1. **Source Entity (Relational Database)**: A normalized business concept physically stored across one or more relational tables in PostgreSQL (`users`, `user_profiles`, `tickets`, `ticket_assignees`).
2. **Graph Entity (Neo4j Node & Edges)**: A high-value business concept materialized as a labeled node in Neo4j (`(:User)`, `(:Project)`, `(:Ticket)`) connected via explicit graph edges. Optimized for relational traversals, organizational hierarchy, permissions, and workflow dependencies.
3. **Vector RAG Entity (Vector Store / Document Retrieval)**: Unstructured text content, message streams, or large attachment payloads (`chat_messages`, `notices.content`) converted into vector embeddings. Optimized for semantic similarity retrieval and hybrid RAG search without causing graph node explosion.

---

## 2. Business Entity Master Catalog (23 Evaluated Entities)

| # | Entity Name | Business Meaning | Source Table(s) | Primary Identifier (Source Type) | Candidate Graph Label | Business Domain | Graph Scope | Tenant Ownership Model | Data Sensitivity | Node Representation Type | Decision Rationale & Evidence Basis |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **Tenant** | Multi-tenancy root boundary | `tenants` | `id` (bigint) | `:Tenant` | Security & Tenant | **INCLUDE (Full)** | Global Root | Corporate System | **Graph Node** | Root multi-tenancy anchor node. Database operates with 1 active pooled tenant (`legacy-default`, id=1). |
| 2 | **User** | Central employee actor | `users`, `user_profiles` | `users.id` (**integer / int4**) | `:User` | User & Org | **INCLUDE (Full)** | Membership-Scoped | PII (Employee Profile) | **Graph Node** | Central actor node. Mask sensitive phone, tax_code, birth_date year; redact password_hash. |
| 3 | **Department** | Organizational unit tree | `departments`, `department_members` | `departments.id` (bigint) | `:Department` | User & Org | **INCLUDE (Full)** | `tenant_id = 1` | Corporate Structure | **Graph Node** | Core organizational tree with recursive parent-child hierarchy and manager links. |
| 4 | **Role** | Organizational RBAC role | `roles`, `user_role_assignments` | `roles.id` (bigint) | `:Role` | Security & Auth | **INCLUDE (Full)** | `tenant_id = 1` | Security Control | **Graph Node** | Security role nodes mapping system permissions to employees. |
| 5 | **Permission** | Granular authorization grant | `permissions`, `role_permissions`, `user_permissions` | `permissions.id` (bigint) | `:Permission` | Security & Auth | **INCLUDE (Dedicated Node)** | Global / Pooled | Security Control | **Graph Node** | Dedicated nodes enabling access-aware chatbot filtering in LangGraph agents. |
| 6 | **Project** | Collaboration workspace | `projects`, `project_members`, `project_tags` | `projects.id` (bigint) | `:Project` | Project & Task | **INCLUDE (Full)** | Derived Transitive | Corporate Business | **Graph Node** | Project workspace hub. Creator: `created_by_user_id`; Owner: `project_members.role = 'owner'`. |
| 7 | **Ticket** | Work task / issue item | `tickets`, `ticket_assignees`, `ticket_checklists` | `tickets.id` (bigint) | `:Ticket` | Project & Task | **INCLUDE (Full)** | Derived Transitive | Corporate Business | **Graph Node** | Discrete work item node with priority, deadlines, and multi-user assignments. |
| 8 | **KanbanColumn** | Task workflow stage | `kanban_columns` | `kanban_columns.id` (bigint) | `:KanbanColumn` | Project & Task | **INCLUDE (Full)** | Project-Scoped | Workflow State | **Graph Node** | Workflow state container defining active status and stage of tickets. |
| 9 | **Sprint** | Timeboxed agile iteration | `project_sprints` | `project_sprints.id` (bigint) | `:Sprint` | Project & Task | **INCLUDE (Full)** | Project-Scoped | Project Schedule | **Graph Node** | Timeboxed iteration container grouping project tickets. |
| 10 | **ApprovalRequest** | Electronic workflow document | `approval_requests`, `approval_participants` | `approval_requests.id` (bigint) | `:ApprovalRequest` | Workflow & Approval | **INCLUDE (Full)** | Derived Transitive | Corporate Business | **Graph Node** | Document signoff node. Creator: `created_by_user_id` (integer); Signoff: `approval_participants`. |
| 11 | **WorkflowTemplate** | Approval routing template | `approval_workflow_templates`, `approval_workflow_steps` | `approval_workflow_templates.id` (bigint) | `:WorkflowTemplate` | Workflow & Approval | **INCLUDE (Full)** | Derived Transitive | Workflow Template | **Graph Node** | Route configuration node defining multi-step sequential approval stages. |
| 12 | **AttendanceRecord** | Daily attendance summary fact | `attendance_daily_records` | `attendance_daily_records.id` (bigint) | `:AttendanceRecord` | HR & Attendance | **INCLUDE (Fact Node)** | Derived Transitive | Work Times Fact | **Graph Node** | Pre-calculated daily employee attendance summary (`work_date`, `is_late`, `actual_minutes`). |
| 13 | **LeaveBalance** | Annual leave ledger balance | `user_leave_year_balances` | `user_leave_year_balances.id` (bigint) | `:LeaveBalance` | HR & Attendance | **INCLUDE (Full)** | Derived Transitive | Employee Benefit | **Graph Node** | Annual paid vacation balance node tracking remaining, used, and accrued days. |
| 14 | **ScheduleEvent** | Meeting / calendar appointment | `schedule_events`, `schedule_event_participants` | `schedule_events.id` (bigint) | `:ScheduleEvent` | Calendar & Resource | **INCLUDE (Full)** | Derived Transitive | Corporate Calendar | **Graph Node** | Calendar event node with discrete `event_date`, `start_time`, `end_time`, and attendees. |
| 15 | **ScheduleRoom** | Physical conference room | `schedule_rooms` | `schedule_rooms.id` (bigint) | `:ScheduleRoom` | Calendar & Resource | **INCLUDE (Full)** | Derived Transitive | Physical Resource | **Graph Node** | Meeting room resource node with seating capacity for reservation conflict checks. |
| 16 | **ChatConversation** | Chat channel / room | `chat_conversations`, `chat_conversation_members` | `chat_conversations.id` (bigint) | `:ChatConversation` | Messenger & Chat | **INCLUDE (Full)** | Derived Transitive | Communication Channel | **Graph Node** | Channel node representing direct and group chat channels and employee memberships. |
| 17 | **ChatMessage** | Message text stream | `chat_messages` | `chat_messages.id` (bigint) | N/A | Messenger & Chat | **VECTOR RAG ONLY** | Derived Transitive | User Text Interaction | **Vector RAG Entity** | **Option A Selected**: Stored in Vector DB with chunk embeddings. Excluded from Neo4j node graph. |
| 18 | **Notice** | Corporate broadcast bulletin | `notices`, `notice_reads` | `notices.id` (bigint) | `:Notice` | Board & Community | **INCLUDE (Full)** | Derived Transitive | Public Corporate | **Graph Node** | Company-wide administrative announcement and policy bulletin node. |
| 19 | **Notification** | Ephemeral system alert | `notifications`, `notification_recipients` | `notifications.id` (bigint) | N/A | Core Administration | **EXCLUDE** | Derived Transitive | System Telemetry | **Excluded** | High turnover, ephemeral delivery logs with zero analytical graph query value. |
| 20 | **CommunityPost** | Internal social feed post | `talk_posts`, `talk_post_comments` | `talk_posts.id` (bigint) | `:CommunityPost` | Board & Community | **INCLUDE (Full)** | Derived Transitive | Internal Social | **Graph Node** | Knowledge-sharing and internal discussion post node. |
| 21 | **File** | Attachment document metadata | `files` | `files.id` (bigint) | `:File` | File Management | **METADATA-ONLY** | Derived Transitive | Attachment Metadata | **Graph Node** | Document metadata node linking files to tickets, notices, and approvals (excludes binary content). |
| 22 | **Asset** | Corporate hardware equipment | `assets`, `asset_assignments` | `assets.id` (bigint) | `:Asset` | Asset Management | **INCLUDE (Full)** | Derived Transitive | IT Equipment | **Graph Node** | Hardware asset node tracking assigned employee (`assigned_user_id`) and categories. |
| 23 | **Audience** | Notice target distribution group | `audiences`, `audience_department_members` | `audiences.id` (bigint) | `:Audience` | Board & Community | **INCLUDE (Full)** | Derived Transitive | Targeting Group | **Graph Node** | Target distribution group controlling bulletin and policy visibility. |

---

## 3. Disputed Items Resolution Register

To eliminate ambiguity across all Phase 1 documentation, the 13 disputed tables identified during review are authoritatively resolved below:

| Disputed Table Name | Row Count | Architectural Classification | Final Graph Decision | Representation Type | Authoritative Justification |
|---|---|---|---|---|---|
| `approval_activity_logs` | 20,960 | Business Audit History | **EXCLUDE** | Relational Audit Only | Detailed technical change history of approval fields. Core signoff state is fully captured in `approval_participants`. Graph inclusion would cause unnecessary edge bloat. |
| `user_sessions` | 6,274 | Security Telemetry | **EXCLUDE** | Relational Security Only | Contains active JWT auth tokens, client IP addresses, and user agent strings. Highly sensitive security data with zero business graph value. |
| `notifications` | 3,735 | Application Event | **EXCLUDE** | Ephemeral Operational | Ephemeral push alerts. Rapid lifecycle, high churn, no relationship traversal value. |
| `notification_recipients` | 9,456 | Application Event | **EXCLUDE** | Ephemeral Operational | Delivery status tracking per user device. Operational telemetry. |
| `project_activity_logs` | 4,389 | Business Audit History | **EXCLUDE** | Relational Audit Only | Historical field edit logs on projects and tickets. Relevant only for relational compliance audit. |
| `bot_messages` | 7,436 | Legacy Bot Chat Stream | **EXCLUDE** | Legacy / Vector RAG | Legacy experimental bot chat messages. Excluded from Neo4j; historical text belongs in Vector Store if needed. |
| `bot_requests` | 3,543 | System Telemetry | **EXCLUDE** | Technical Telemetry | LLM provider API request telemetry, token consumption, and latency metrics. Zero business knowledge value. |
| `bot_threads` | 610 | Bot Chat Container | **EXCLUDE** | Legacy Operational | Bot conversation threads from previous experiments. Excluded from business graph. |
| `mail_send_logs` | 25,315 | System Telemetry | **EXCLUDE** | Technical Telemetry | SMTP delivery receipts, message IDs, and server trace logs. Technical infrastructure data. |
| `schema_migrations` | 4 | System Infrastructure | **EXCLUDE** | DDL Version Tracking | Database migration history tracking. Completely non-business. |
| `license_audit_events` | 115 | Security Audit | **EXCLUDE** | Relational Compliance | Software licensing audit events and customer lease verification. Excluded from business graph. |
| `login_qr_challenges` | 142 | Security Telemetry | **EXCLUDE** | Ephemeral Operational | Ephemeral mobile QR login sessions and device approval challenges. Zero business knowledge value. |
| `server_resource_nodes` | 0 | Infrastructure Telemetry | **EXCLUDE** | Infrastructure Telemetry | Server hardware cluster nodes and resource metrics. Empty technical table. |

---

## 4. Discovered Role Disambiguation: Creator, Owner, Member, and Approver

A critical finding from Phase 1 database discovery is the semantic separation of enterprise roles:

1. **Project Creator vs. Owner**:
   - Creator: `projects.created_by_user_id` (`bigint`). Tracks the specific account that initialized the project.
   - Owner: `project_members.role = 'owner'` (`role` varchar, `user_id` bigint). Tracks executive responsibility and business ownership (**72 active assignments** across 65 projects).
2. **Project Member**:
   - `project_members.role = 'member'` (246 records) or `'admin'` (38 records). Tracks operational staffing allocations.
3. **Approval Request Creator vs. Approvers**:
   - Creator: `approval_requests.created_by_user_id` (`integer`, 0 nulls, 318 distinct users). Tracks the employee submitting the document.
   - Approvers: `approval_participants.user_id` (`integer`) with `request_id`, `sequence_order`, and `action_status`. Tracks the multi-step signoff chain.
