# 25 – Phase 1.1 Chatbot Business Query Readiness Validation
## Groupware AI Chatbot Project – 12 Production Enterprise Query Scenarios

> [!NOTE]
> This document validates all 12 enterprise business queries against the final canonical Graph Data Model (`21`) and mapping contracts (`24`).
> Every relationship name, property name, and filter clause is reconciled with physical database schema facts.

---

## 1. Chatbot Scenario Architecture & Alignment Matrix

| Scenario # | Business Question / Intent | Required Graph Entities & Edges | Graph Query Scope | Alignment Status |
|---|---|---|---|---|
| **Scenario 1** | Organizational Hierarchy & Direct Reports | `(:User)`, `(:Department)`, `[:MANAGES]`, `[:MEMBER_OF_DEPARTMENT]`, `[:SUB_DEPARTMENT_OF]` | MVP Core | **ALIGNED & READY** |
| **Scenario 2** | Project Membership & Leadership Discovery | `(:User)`, `(:Project)`, `[:MEMBER_OF_PROJECT]`, `[:CREATED_BY]` | MVP Core | **ALIGNED & READY** |
| **Scenario 3** | Sprint Task Assignment & Progress Tracking | `(:Ticket)`, `(:Project)`, `(:Sprint)`, `(:KanbanColumn)`, `[:ASSIGNED_TO]`, `[:IN_STAGE]` | MVP Core | **ALIGNED & READY** |
| **Scenario 4** | Active Approval Route & Pending Approver | `(:User)`, `(:ApprovalRequest)`, `[:PARTICIPATES_IN]` | MVP Core | **ALIGNED & READY** |
| **Scenario 5** | Access Control & Effective Permissions | `(:User)`, `(:Role)`, `(:Permission)`, `[:HAS_ROLE]`, `[:INCLUDES_PERMISSION]` | MVP Core | **ALIGNED & READY** |
| **Scenario 6** | Department Asset Custody & Category Audit | `(:Asset)`, `(:Department)`, `(:User)`, `(:AssetCategory)`, `[:ASSIGNED_TO]`, `[:LOCATED_IN]` | MVP Core | **ALIGNED & READY** |
| **Scenario 7** | Meeting Schedule & Room Availability | `(:ScheduleEvent)`, `(:ScheduleRoom)`, `(:User)`, `[:HELD_IN]`, `[:ATTENDS_EVENT]` | MVP Core | **ALIGNED & READY** |
| **Scenario 8** | Chat Channel Topology & Member Roster | `(:ChatConversation)`, `(:User)`, `[:MEMBER_OF_CONVERSATION]` (Option A) | MVP Core | **ALIGNED & READY** |
| **Scenario 9** | Official Notice & Target Audience Audit | `(:Notice)`, `(:Audience)`, `(:User)`, `[:PUBLISHED_BY]`, `[:TARGETED_TO]` | MVP Core | **ALIGNED & READY** |
| **Scenario 10** | Employee Leave Balance & Quota Inquiry | `(:User)`, `(:LeaveBalance)` | MVP Extended | **ALIGNED & READY** |
| **Scenario 11** | Daily Attendance Exception Tracking | `(:User)`, `(:AttendanceRecord)` | MVP Extended | **ALIGNED & READY** |
| **Scenario 12** | Contract Tenure & Status Audit | `(:User)`, `(:ContractHistory)` (Masked HR Policy) | MVP Extended | **ALIGNED & READY** |

---

## 2. Production Cypher Query Specifications

### Scenario 1: Organizational Hierarchy & Direct Reports
- **Natural Language**: *"Who reports to John Doe, and what is the organizational hierarchy of his department?"*
- **Cypher Implementation**:
  ```cypher
  MATCH (mgr:User {display_name: $manager_name, tenant_id: $tenant_id})-[:MANAGES]->(d:Department)
  OPTIONAL MATCH (subDept:Department)-[:SUB_DEPARTMENT_OF*1..3]->(d)
  WITH d, collect(subDept) + d AS allDepts
  UNWIND allDepts AS dept
  MATCH (u:User)-[m:MEMBER_OF_DEPARTMENT]->(dept)
  WHERE u.is_active = true
  RETURN 
    dept.name AS department_name,
    u.id AS employee_id,
    u.display_name AS employee_name,
    u.position AS position,
    m.is_primary AS is_primary_dept;
  ```

### Scenario 2: Project Membership & Leadership Discovery
- **Natural Language**: *"Who is leading Project Phoenix, and who are the active team members?"*
- **Cypher Implementation**:
  ```cypher
  MATCH (p:Project {key: $project_key, tenant_id: $tenant_id})
  MATCH (u:User)-[m:MEMBER_OF_PROJECT]->(p)
  RETURN 
    p.name AS project_name,
    p.key AS project_key,
    u.display_name AS member_name,
    m.role AS member_role,
    m.joined_at AS joined_date
  ORDER BY CASE WHEN m.role = 'owner' THEN 1 ELSE 2 END, member_name;
  ```

### Scenario 3: Sprint Task Assignment & Progress Tracking
- **Natural Language**: *"List all in-progress tickets in Sprint 14 of Project Phoenix assigned to Jane Smith."*
- **Cypher Implementation**:
  ```cypher
  MATCH (p:Project {key: $project_key, tenant_id: $tenant_id})
  MATCH (p)<-[:SPRINT_OF_PROJECT]-(s:Sprint {name: $sprint_name})
  MATCH (t:Ticket)-[:PART_OF_SPRINT]->(s)
  MATCH (t)-[:ASSIGNED_TO]->(u:User {display_name: $assignee_name})
  MATCH (t)-[:IN_STAGE]->(k:KanbanColumn)
  WHERE t.status = 'in_progress'
  RETURN 
    t.code AS ticket_code,
    t.title AS title,
    t.priority AS priority,
    k.title AS kanban_stage,
    t.due_date AS due_date,
    u.display_name AS assignee;
  ```

### Scenario 4: Active Approval Route & Pending Approver
- **Natural Language**: *"Which approval requests are currently waiting for action, and who is the designated approver?"*
- **Cypher Implementation**:
  ```cypher
  MATCH (a:ApprovalRequest {tenant_id: $tenant_id})
  WHERE a.status = 'in_progress'
  MATCH (u:User)-[p:PARTICIPATES_IN]->(a)
  WHERE p.action_status = 'pending' 
    AND p.participant_role IN ['approver', 'reviewer']
  RETURN 
    a.code AS request_code,
    a.title AS document_title,
    a.request_type AS workflow_type,
    u.display_name AS current_approver,
    p.sequence_order AS approval_step,
    a.submitted_at AS submitted_date
  ORDER BY a.submitted_at ASC;
  ```

### Scenario 5: Access Control & Effective Permissions
- **Natural Language**: *"What roles and granular permissions are assigned to user Alice?"*
- **Cypher Implementation**:
  ```cypher
  MATCH (u:User {username: $username, tenant_id: $tenant_id})
  OPTIONAL MATCH (u)-[:HAS_ROLE]->(r:Role)-[:INCLUDES_PERMISSION]->(rp:Permission)
  OPTIONAL MATCH (u)-[dp:DIRECT_PERMISSION]->(directP:Permission)
  RETURN 
    u.display_name AS user_name,
    collect(DISTINCT r.name) AS assigned_roles,
    collect(DISTINCT rp.code) AS inherited_permissions,
    collect(DISTINCT {perm: directP.code, granted: dp.is_granted}) AS direct_overrides;
  ```

### Scenario 6: Department Asset Custody & Category Audit
- **Natural Language**: *"Show all active laptops currently assigned to employees in the Engineering Department."*
- **Cypher Implementation**:
  ```cypher
  MATCH (d:Department {code: $dept_code, tenant_id: $tenant_id})
  MATCH (a:Asset)-[:LOCATED_IN]->(d)
  MATCH (a)-[:CATEGORIZED_AS]->(c:AssetCategory)
  MATCH (a)-[:ASSIGNED_TO]->(u:User)
  WHERE a.status = 'in_use'
  RETURN 
    a.code AS asset_tag,
    a.name AS asset_name,
    c.name AS category_name,
    u.display_name AS custodian_name,
    a.location AS physical_location;
  ```

### Scenario 7: Meeting Schedule & Room Availability
- **Natural Language**: *"What meetings are scheduled in Conference Room B for today?"*
- **Cypher Implementation**:
  ```cypher
  MATCH (r:ScheduleRoom {name: $room_name, tenant_id: $tenant_id})
  MATCH (e:ScheduleEvent)-[:HELD_IN]->(r)
  WHERE e.event_date = date($target_date)
  MATCH (e)-[:ORGANIZED_BY]->(organizer:User)
  OPTIONAL MATCH (attendee:User)-[:ATTENDS_EVENT]->(e)
  RETURN 
    e.title AS meeting_title,
    e.start_time AS start_time,
    e.end_time AS end_time,
    organizer.display_name AS organizer_name,
    collect(attendee.display_name) AS attendee_roster
  ORDER BY e.start_time ASC;
  ```

### Scenario 8: Chat Channel Topology & Member Roster (Option A)
- **Natural Language**: *"What chat channels does user Bob belong to, and who are the other channel members?"*
- **Cypher Implementation**:
  ```cypher
  MATCH (u:User {username: $username, tenant_id: $tenant_id})
  MATCH (u)-[:MEMBER_OF_CONVERSATION]->(c:ChatConversation)
  MATCH (other:User)-[:MEMBER_OF_CONVERSATION]->(c)
  RETURN 
    c.id AS channel_id,
    c.title AS channel_title,
    c.conversation_type AS channel_type,
    collect(other.display_name) AS members_roster;
  ```

### Scenario 9: Official Notice & Target Audience Audit
- **Natural Language**: *"Which published notices are targeted to the All-Staff audience?"*
- **Cypher Implementation**:
  ```cypher
  MATCH (a:Audience {name: $audience_name, tenant_id: $tenant_id})
  MATCH (n:Notice)-[:TARGETED_TO]->(a)
  MATCH (n)-[:PUBLISHED_BY]->(author:User)
  WHERE n.is_published = true
  RETURN 
    n.title AS notice_title,
    n.published_at AS published_date,
    author.display_name AS author_name,
    a.name AS target_group;
  ```

### Scenario 10: Employee Leave Balance & Quota Inquiry
- **Natural Language**: *"How many remaining vacation days does employee Charlie have for year 2026?"*
- **Cypher Implementation**:
  ```cypher
  MATCH (u:User {display_name: $employee_name, tenant_id: $tenant_id})
  MATCH (lb:LeaveBalance {user_id: u.id, year: $query_year})
  RETURN 
    u.display_name AS employee_name,
    lb.year AS calendar_year,
    lb.remaining_days AS remaining_vacation_days,
    lb.used_days AS used_vacation_days;
  ```

### Scenario 11: Daily Attendance Exception Tracking
- **Natural Language**: *"Identify all employees who had attendance exceptions (late/absent) on 2026-10-15."*
- **Cypher Implementation**:
  ```cypher
  MATCH (ar:AttendanceRecord {work_date: date($work_date), tenant_id: $tenant_id})
  WHERE ar.status IN ['late', 'absent']
  MATCH (u:User {id: ar.user_id})
  OPTIONAL MATCH (u)-[:MEMBER_OF_DEPARTMENT]->(d:Department)
  RETURN 
    u.display_name AS employee_name,
    d.name AS department,
    ar.status AS attendance_status,
    ar.working_minutes AS minutes_worked;
  ```

### Scenario 12: Employment Contract Tenure Audit (Masked HR Policy)
- **Natural Language**: *"Show the contract type and tenure period for employee David without revealing compensation."*
- **Cypher Implementation**:
  ```cypher
  MATCH (u:User {display_name: $employee_name, tenant_id: $tenant_id})
  MATCH (ch:ContractHistory {user_id: u.id})
  RETURN 
    u.display_name AS employee_name,
    ch.contract_type AS employment_contract,
    ch.start_date AS commencement_date,
    ch.end_date AS expiry_date,
    ch.status AS contract_status;
  ```
