# -*- coding: utf-8 -*-
"""Phase 1.2 - Read-only data profiling for the User/Tenant model, tenant ownership,
relationship cardinality and orphan analysis. Output: artifacts/phase1_2/data_profile.json"""
import datetime, decimal, json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from pg_readonly import readonly_connection

Q = {
    # ---------------- User / Tenant ----------------
    "users_total": "SELECT count(*) FROM users",
    "users_by_flags": "SELECT is_active, is_deleted, count(*) FROM users GROUP BY 1,2 ORDER BY 1,2",
    "users_without_profile": "SELECT count(*) FROM users u WHERE NOT EXISTS (SELECT 1 FROM user_profiles p WHERE p.user_id=u.id)",
    "users_with_multiple_profiles": "SELECT count(*) FROM (SELECT user_id FROM user_profiles GROUP BY user_id HAVING count(*)>1) x",
    "profiles_orphan_user": "SELECT count(*) FROM user_profiles p WHERE NOT EXISTS (SELECT 1 FROM users u WHERE u.id=p.user_id)",
    "profiles_by_tenant": "SELECT tenant_id, count(*) FROM user_profiles GROUP BY 1 ORDER BY 1",
    "tenants": "SELECT id, tenant_key, status, isolation_mode, is_default, is_deleted FROM tenants ORDER BY id",
    "memberships_by_status": "SELECT status, is_default, is_deleted, count(*) FROM tenant_user_memberships GROUP BY 1,2,3 ORDER BY 1,2,3",
    "users_without_membership": "SELECT count(*) FROM users u WHERE NOT EXISTS (SELECT 1 FROM tenant_user_memberships m WHERE m.user_id=u.id AND m.is_deleted=false)",
    "users_with_multiple_active_memberships": "SELECT count(*) FROM (SELECT user_id FROM tenant_user_memberships WHERE is_deleted=false AND status='active' GROUP BY user_id HAVING count(*)>1) x",
    "memberships_orphan_user": "SELECT count(*) FROM tenant_user_memberships m WHERE NOT EXISTS (SELECT 1 FROM users u WHERE u.id=m.user_id)",
    "profile_tenant_without_membership": "SELECT count(*) FROM user_profiles p WHERE NOT EXISTS (SELECT 1 FROM tenant_user_memberships m WHERE m.user_id=p.user_id AND m.tenant_id=p.tenant_id AND m.is_deleted=false)",
    "membership_user_id_max": "SELECT max(user_id), max(tenant_id) FROM tenant_user_memberships",
    # ---------------- Departments ----------------
    "departments_by_tenant": "SELECT tenant_id, is_active, count(*) FROM departments GROUP BY 1,2 ORDER BY 1,2",
    "departments_parent_orphan": "SELECT count(*) FROM departments d WHERE d.parent_id IS NOT NULL AND NOT EXISTS (SELECT 1 FROM departments p WHERE p.id=d.parent_id)",
    "departments_parent_cross_tenant": "SELECT count(*) FROM departments d JOIN departments p ON p.id=d.parent_id WHERE p.tenant_id<>d.tenant_id",
    "departments_manager_null_vs_set": "SELECT (manager_user_id IS NULL) AS mgr_null, count(*) FROM departments GROUP BY 1",
    "departments_manager_orphan": "SELECT count(*) FROM departments d WHERE d.manager_user_id IS NOT NULL AND NOT EXISTS (SELECT 1 FROM users u WHERE u.id=d.manager_user_id)",
    "department_members_active_vs_ended": "SELECT (effective_to IS NULL) AS active, is_primary, count(*) FROM department_members GROUP BY 1,2 ORDER BY 1,2",
    "department_members_cross_tenant": "SELECT count(*) FROM department_members dm JOIN departments d ON d.id=dm.department_id WHERE d.tenant_id<>dm.tenant_id",
    "department_members_orphans": "SELECT sum(CASE WHEN u.id IS NULL THEN 1 ELSE 0 END) AS no_user, sum(CASE WHEN d.id IS NULL THEN 1 ELSE 0 END) AS no_dept FROM department_members dm LEFT JOIN users u ON u.id=dm.user_id LEFT JOIN departments d ON d.id=dm.department_id",
    # ---------------- RBAC ----------------
    "roles_by_tenant": "SELECT tenant_id, is_active, is_system, count(*) FROM roles GROUP BY 1,2,3 ORDER BY 1,2,3",
    "ura_role_tenant_mismatch": "SELECT count(*) FROM user_role_assignments a JOIN roles r ON r.id=a.role_id WHERE r.tenant_id<>a.tenant_id",
    "ura_orphans": "SELECT sum(CASE WHEN u.id IS NULL THEN 1 ELSE 0 END), sum(CASE WHEN r.id IS NULL THEN 1 ELSE 0 END) FROM user_role_assignments a LEFT JOIN users u ON u.id=a.user_id LEFT JOIN roles r ON r.id=a.role_id",
    "role_permissions_granted": "SELECT is_granted, count(*) FROM role_permissions GROUP BY 1 ORDER BY 1",
    "role_permissions_orphans": "SELECT sum(CASE WHEN r.id IS NULL THEN 1 ELSE 0 END), sum(CASE WHEN p.id IS NULL THEN 1 ELSE 0 END) FROM role_permissions rp LEFT JOIN roles r ON r.id=rp.role_id LEFT JOIN permissions p ON p.id=rp.permission_id",
    "role_permissions_tenant_mismatch": "SELECT count(*) FROM role_permissions rp JOIN roles r ON r.id=rp.role_id WHERE r.tenant_id<>rp.tenant_id",
    "user_permissions_granted": "SELECT is_granted, count(*) FROM user_permissions GROUP BY 1 ORDER BY 1",
    "user_permissions_orphans": "SELECT sum(CASE WHEN u.id IS NULL THEN 1 ELSE 0 END), sum(CASE WHEN p.id IS NULL THEN 1 ELSE 0 END) FROM user_permissions up LEFT JOIN users u ON u.id=up.user_id LEFT JOIN permissions p ON p.id=up.permission_id",
    "permissions_by_resource_type": "SELECT resource_type, count(*) FROM permissions GROUP BY 1 ORDER BY 2 DESC",
    # ---------------- Projects / Tickets ----------------
    "projects_by_deleted": "SELECT is_deleted, count(*) FROM projects GROUP BY 1",
    "projects_creator_orphan": "SELECT count(*) FROM projects p WHERE NOT EXISTS (SELECT 1 FROM users u WHERE u.id=p.created_by_user_id)",
    "projects_creator_multi_membership": "SELECT count(*) FROM projects p WHERE (SELECT count(*) FROM tenant_user_memberships m WHERE m.user_id=p.created_by_user_id AND m.is_deleted=false)>1",
    "project_members_roles": "SELECT role, count(*) FROM project_members GROUP BY 1 ORDER BY 2 DESC",
    "project_members_orphans": "SELECT sum(CASE WHEN u.id IS NULL THEN 1 ELSE 0 END), sum(CASE WHEN p.id IS NULL THEN 1 ELSE 0 END) FROM project_members pm LEFT JOIN users u ON u.id=pm.user_id LEFT JOIN projects p ON p.id=pm.project_id",
    "projects_without_owner_member": "SELECT count(*) FROM projects p WHERE NOT EXISTS (SELECT 1 FROM project_members pm WHERE pm.project_id=p.id AND pm.role='owner')",
    "projects_with_multiple_owners": "SELECT count(*) FROM (SELECT project_id FROM project_members WHERE role='owner' GROUP BY 1 HAVING count(*)>1) x",
    "tickets_by_deleted": "SELECT is_deleted, count(*) FROM tickets GROUP BY 1",
    "tickets_project_orphan": "SELECT count(*) FROM tickets t WHERE NOT EXISTS (SELECT 1 FROM projects p WHERE p.id=t.project_id)",
    "tickets_sprint_orphan": "SELECT count(*) FROM tickets t WHERE t.sprint_id IS NOT NULL AND NOT EXISTS (SELECT 1 FROM project_sprints s WHERE s.id=t.sprint_id)",
    "tickets_sprint_other_project": "SELECT count(*) FROM tickets t JOIN project_sprints s ON s.id=t.sprint_id WHERE s.project_id<>t.project_id",
    "tickets_column_orphan": "SELECT count(*) FROM tickets t WHERE t.column_id IS NOT NULL AND NOT EXISTS (SELECT 1 FROM kanban_columns k WHERE k.id=t.column_id)",
    "tickets_column_other_project": "SELECT count(*) FROM tickets t JOIN kanban_columns k ON k.id=t.column_id WHERE k.project_id<>t.project_id",
    "tickets_column_null": "SELECT count(*) FROM tickets WHERE column_id IS NULL",
    "tickets_creator_orphan": "SELECT count(*) FROM tickets t WHERE NOT EXISTS (SELECT 1 FROM users u WHERE u.id=t.created_by_user_id)",
    "tickets_parent_orphan": "SELECT count(*) FROM tickets t WHERE t.parent_ticket_id IS NOT NULL AND NOT EXISTS (SELECT 1 FROM tickets p WHERE p.id=t.parent_ticket_id)",
    "ticket_assignees_orphans": "SELECT sum(CASE WHEN u.id IS NULL THEN 1 ELSE 0 END), sum(CASE WHEN t.id IS NULL THEN 1 ELSE 0 END) FROM ticket_assignees a LEFT JOIN users u ON u.id=a.user_id LEFT JOIN tickets t ON t.id=a.ticket_id",
    "tickets_with_multiple_assignees": "SELECT count(*) FROM (SELECT ticket_id FROM ticket_assignees GROUP BY 1 HAVING count(*)>1) x",
    "sprints_project_orphan": "SELECT count(*) FROM project_sprints s WHERE NOT EXISTS (SELECT 1 FROM projects p WHERE p.id=s.project_id)",
    "kanban_project_orphan": "SELECT count(*) FROM kanban_columns k WHERE NOT EXISTS (SELECT 1 FROM projects p WHERE p.id=k.project_id)",
    "ticket_tags_target_check": "SELECT count(*) AS total, sum(CASE WHEN pt.id IS NULL THEN 1 ELSE 0 END) AS not_in_project_tags FROM ticket_tags tt LEFT JOIN project_tags pt ON pt.id=tt.tag_id",
    "ticket_tags_tag_other_project": "SELECT count(*) FROM ticket_tags tt JOIN project_tags pt ON pt.id=tt.tag_id JOIN tickets t ON t.id=tt.ticket_id WHERE pt.project_id<>t.project_id",
    # ---------------- Approval ----------------
    "approval_status_values": "SELECT status, count(*) FROM approval_requests GROUP BY 1 ORDER BY 2 DESC",
    "approval_by_deleted": "SELECT is_deleted, count(*) FROM approval_requests GROUP BY 1",
    "approval_request_types": "SELECT request_type, count(*) FROM approval_requests GROUP BY 1 ORDER BY 2 DESC",
    "workflow_templates": "SELECT id, code, request_type, is_active, priority FROM approval_workflow_templates ORDER BY request_type, priority",
    "workflow_template_request_type_dupes": "SELECT request_type, count(*) FROM approval_workflow_templates GROUP BY 1 HAVING count(*)>1",
    "workflow_template_active_request_type_dupes": "SELECT request_type, count(*) FROM approval_workflow_templates WHERE is_active GROUP BY 1 HAVING count(*)>1",
    "approval_request_type_without_template": "SELECT count(*) FROM approval_requests r WHERE NOT EXISTS (SELECT 1 FROM approval_workflow_templates w WHERE w.request_type=r.request_type)",
    "approval_creator_orphan": "SELECT count(*) FROM approval_requests r WHERE NOT EXISTS (SELECT 1 FROM users u WHERE u.id=r.created_by_user_id)",
    "approval_participant_roles": "SELECT participant_role, action_status, count(*) FROM approval_participants GROUP BY 1,2 ORDER BY 1,2",
    "approval_participants_orphans": "SELECT sum(CASE WHEN u.id IS NULL THEN 1 ELSE 0 END), sum(CASE WHEN r.id IS NULL THEN 1 ELSE 0 END) FROM approval_participants p LEFT JOIN users u ON u.id=p.user_id LEFT JOIN approval_requests r ON r.id=p.request_id",
    "workflow_steps_assignee_types": "SELECT assignee_type, participant_role, count(*) FROM approval_workflow_steps GROUP BY 1,2 ORDER BY 1,2",
    # ---------------- Schedule ----------------
    "schedule_by_deleted": "SELECT is_deleted, count(*) FROM schedule_events GROUP BY 1",
    "schedule_owner_orphan": "SELECT count(*) FROM schedule_events e WHERE NOT EXISTS (SELECT 1 FROM users u WHERE u.id=e.user_id)",
    "schedule_room_orphan": "SELECT count(*) FROM schedule_events e WHERE e.room_id IS NOT NULL AND NOT EXISTS (SELECT 1 FROM schedule_rooms r WHERE r.id=e.room_id)",
    "schedule_room_set": "SELECT (room_id IS NULL) AS no_room, count(*) FROM schedule_events GROUP BY 1",
    "schedule_visibility": "SELECT visibility, count(*) FROM schedule_events GROUP BY 1 ORDER BY 2 DESC",
    "schedule_participants_orphans": "SELECT sum(CASE WHEN u.id IS NULL THEN 1 ELSE 0 END), sum(CASE WHEN e.id IS NULL THEN 1 ELSE 0 END) FROM schedule_event_participants p LEFT JOIN users u ON u.id=p.user_id LEFT JOIN schedule_events e ON e.id=p.event_id",
    "schedule_participant_status": "SELECT status, count(*) FROM schedule_event_participants GROUP BY 1 ORDER BY 2 DESC",
    # ---------------- Notice / Audience / Talk ----------------
    "notices_flags": "SELECT is_published, is_deleted, count(*) FROM notices GROUP BY 1,2 ORDER BY 1,2",
    "notices_audience_set": "SELECT (audience_id IS NULL) AS no_audience, count(*) FROM notices GROUP BY 1",
    "notices_audience_orphan": "SELECT count(*) FROM notices n WHERE n.audience_id IS NOT NULL AND NOT EXISTS (SELECT 1 FROM audiences a WHERE a.id=n.audience_id)",
    "notices_author_orphan": "SELECT count(*) FROM notices n WHERE NOT EXISTS (SELECT 1 FROM users u WHERE u.id=n.created_by_user_id)",
    "audience_types": "SELECT audience_type, is_system, is_active, count(*) FROM audiences GROUP BY 1,2,3 ORDER BY 1,2,3",
    "audience_reuse_by_notices": "SELECT count(*) AS audiences_used, max(c) AS max_notices_per_audience FROM (SELECT audience_id, count(*) c FROM notices WHERE audience_id IS NOT NULL GROUP BY 1) x",
    "audience_reuse_by_talk": "SELECT count(*) AS audiences_used, max(c) AS max_posts_per_audience FROM (SELECT audience_id, count(*) c FROM talk_posts WHERE audience_id IS NOT NULL GROUP BY 1) x",
    "audience_user_members_orphans": "SELECT sum(CASE WHEN u.id IS NULL THEN 1 ELSE 0 END), sum(CASE WHEN a.id IS NULL THEN 1 ELSE 0 END) FROM audience_user_members m LEFT JOIN users u ON u.id=m.user_id LEFT JOIN audiences a ON a.id=m.audience_id",
    "audience_department_members_orphans": "SELECT sum(CASE WHEN d.id IS NULL THEN 1 ELSE 0 END), sum(CASE WHEN a.id IS NULL THEN 1 ELSE 0 END) FROM audience_department_members m LEFT JOIN departments d ON d.id=m.department_id LEFT JOIN audiences a ON a.id=m.audience_id",
    "talk_posts_flags": "SELECT is_deleted, (audience_id IS NULL) AS no_audience, count(*) FROM talk_posts GROUP BY 1,2 ORDER BY 1,2",
    "talk_posts_author_orphan": "SELECT count(*) FROM talk_posts p WHERE NOT EXISTS (SELECT 1 FROM users u WHERE u.id=p.author_user_id)",
    "talk_post_tags_orphans": "SELECT sum(CASE WHEN p.id IS NULL THEN 1 ELSE 0 END), sum(CASE WHEN t.id IS NULL THEN 1 ELSE 0 END) FROM talk_post_tags x LEFT JOIN talk_posts p ON p.id=x.post_id LEFT JOIN talk_tags t ON t.id=x.tag_id",
    # ---------------- Asset ----------------
    "assets_flags": "SELECT is_deleted, status, count(*) FROM assets GROUP BY 1,2 ORDER BY 1,2",
    "assets_category_orphan": "SELECT count(*) FROM assets a WHERE NOT EXISTS (SELECT 1 FROM asset_categories c WHERE c.id=a.category_id)",
    "assets_department_orphan": "SELECT count(*) FROM assets a WHERE a.department_id IS NOT NULL AND NOT EXISTS (SELECT 1 FROM departments d WHERE d.id=a.department_id)",
    "assets_department_null": "SELECT count(*) FROM assets WHERE department_id IS NULL",
    "assets_assigned_orphan": "SELECT count(*) FROM assets a WHERE a.assigned_user_id IS NOT NULL AND NOT EXISTS (SELECT 1 FROM users u WHERE u.id=a.assigned_user_id)",
    "assets_no_dept_no_user": "SELECT count(*) FROM assets WHERE department_id IS NULL AND assigned_user_id IS NULL",
    "asset_categories_parent_orphan": "SELECT count(*) FROM asset_categories c WHERE c.parent_id IS NOT NULL AND NOT EXISTS (SELECT 1 FROM asset_categories p WHERE p.id=c.parent_id)",
    # ---------------- Files ----------------
    "files_flags": "SELECT storage_provider, is_deleted, count(*) FROM files GROUP BY 1,2 ORDER BY 1,2",
    "files_uploader_null": "SELECT count(*) FROM files WHERE uploaded_by_user_id IS NULL",
    "files_uploader_orphan": "SELECT count(*) FROM files f WHERE f.uploaded_by_user_id IS NOT NULL AND NOT EXISTS (SELECT 1 FROM users u WHERE u.id=f.uploaded_by_user_id)",
    # ---------------- Chat ----------------
    "chat_conversation_types": "SELECT conversation_type, (created_by_user_id IS NULL) AS no_creator, count(*) FROM chat_conversations GROUP BY 1,2 ORDER BY 1,2",
    "chat_members_flags": "SELECT is_deleted, role, count(*) FROM chat_conversation_members GROUP BY 1,2 ORDER BY 1,2",
    "chat_members_orphans": "SELECT sum(CASE WHEN u.id IS NULL THEN 1 ELSE 0 END), sum(CASE WHEN c.id IS NULL THEN 1 ELSE 0 END) FROM chat_conversation_members m LEFT JOIN users u ON u.id=m.user_id LEFT JOIN chat_conversations c ON c.id=m.conversation_id",
    "chat_conversations_without_members": "SELECT count(*) FROM chat_conversations c WHERE NOT EXISTS (SELECT 1 FROM chat_conversation_members m WHERE m.conversation_id=c.id AND m.is_deleted=false)",
    # ---------------- HR ----------------
    "leave_monthly_year_range": "SELECT min(year), max(year), count(DISTINCT user_id) FROM user_leave_monthly_balances",
    "leave_monthly_user_orphan": "SELECT count(*) FROM user_leave_monthly_balances b WHERE NOT EXISTS (SELECT 1 FROM users u WHERE u.id=b.user_id)",
    "leave_year_user_orphan": "SELECT count(*) FROM user_leave_year_balances b WHERE NOT EXISTS (SELECT 1 FROM users u WHERE u.id=b.user_id)",
    "leave_year_range": "SELECT min(year), max(year), count(DISTINCT user_id) FROM user_leave_year_balances",
    "attendance_user_null": "SELECT (user_id IS NULL) AS no_user, count(*) FROM attendance_daily_records GROUP BY 1",
    "attendance_user_orphan": "SELECT count(*) FROM attendance_daily_records a WHERE a.user_id IS NOT NULL AND NOT EXISTS (SELECT 1 FROM users u WHERE u.id=a.user_id)",
    "attendance_dupe_user_date": "SELECT count(*) FROM (SELECT user_id, work_date FROM attendance_daily_records WHERE user_id IS NOT NULL GROUP BY 1,2 HAVING count(*)>1) x",
    "attendance_status_values": "SELECT status, count(*) FROM attendance_daily_records GROUP BY 1 ORDER BY 2 DESC",
    "attendance_date_range": "SELECT min(work_date), max(work_date) FROM attendance_daily_records",
    "attendance_code_matches_profile": "SELECT count(*) AS total, sum(CASE WHEN p.user_id IS NULL THEN 1 ELSE 0 END) AS unmatched_employee_code FROM attendance_daily_records a LEFT JOIN user_profiles p ON p.employee_number=a.employee_code",
    "contracts_flags": "SELECT tenant_id, is_current, count(*) FROM user_contract_histories GROUP BY 1,2 ORDER BY 1,2",
    "contracts_user_orphan": "SELECT count(*) FROM user_contract_histories c WHERE NOT EXISTS (SELECT 1 FROM users u WHERE u.id=c.user_id)",
}


def _jsonable(v):
    if isinstance(v, (datetime.date, datetime.datetime, datetime.time)):
        return v.isoformat()
    if isinstance(v, decimal.Decimal):
        return float(v)
    return v


def main():
    out = {"generated_at": datetime.datetime.now().isoformat(timespec="seconds"),
           "mode": "READ ONLY session on local restored validation copy (inf_nffice @127.0.0.1:5433)",
           "results": {}, "errors": {}}
    with readonly_connection() as conn:
        cur = conn.cursor()
        cur.execute("SHOW transaction_read_only")
        out["transaction_read_only"] = cur.fetchone()[0]
        cur.execute("SELECT version()")
        out["server_version"] = cur.fetchone()[0]
        for k, sql in Q.items():
            try:
                cur.execute(sql)
                out["results"][k] = {"sql": sql, "rows": [[_jsonable(v) for v in r] for r in cur.fetchall()]}
            except Exception as e:  # record, never hide
                out["errors"][k] = {"sql": sql, "error": str(e).strip()}
    os.makedirs(r"artifacts\phase1_2", exist_ok=True)
    with open(r"artifacts\phase1_2\data_profile.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)
    lines = [f"read_only: {out['transaction_read_only']} | queries: {len(out['results'])} | errors: {len(out['errors'])}"]
    for k, v in out["results"].items():
        lines.append(f"{k}: {v['rows']}")
    for k, v in out["errors"].items():
        lines.append(f"ERROR {k}: {v['error']}")
    with open(r"artifacts\phase1_2\data_profile.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(lines[0])


if __name__ == "__main__":
    main()
