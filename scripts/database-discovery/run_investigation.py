import subprocess
import time
import json
import psycopg2
from psycopg2.extras import RealDictCursor

def run_investigation():
    # Start postgres process
    p = subprocess.Popen([
        r"C:\Users\admin\miniconda3\envs\chat\Library\bin\postgres.exe",
        "-D", r"C:\Project\chatbot\.pgdata",
        "-p", "5433"
    ])
    time.sleep(1.5)
    
    conn = psycopg2.connect("host=127.0.0.1 port=5433 user=postgres dbname=inf_nffice sslmode=disable gssencmode=disable")
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    results = {}
    
    print("1. Investigating Tenant & Multi-tenancy...")
    cur.execute("SELECT * FROM tenants;")
    results["tenants"] = cur.fetchall()
    
    # Check tenant_id across tables
    cur.execute("""
        SELECT table_name 
        FROM information_schema.columns 
        WHERE table_schema = 'public' AND column_name = 'tenant_id'
        ORDER BY table_name;
    """)
    results["tables_with_tenant_id"] = [r["table_name"] for r in cur.fetchall()]
    
    # Check distinct tenant_id values in tables with tenant_id
    tenant_id_dist = {}
    for tbl in results["tables_with_tenant_id"][:20]:
        cur.execute(f'SELECT tenant_id, count(*) AS cnt FROM "{tbl}" GROUP BY tenant_id;')
        tenant_id_dist[tbl] = {str(r["tenant_id"]): r["cnt"] for r in cur.fetchall()}
    results["tenant_id_distributions"] = tenant_id_dist
    
    # Does users table have tenant_id?
    cur.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_schema = 'public' AND table_name = 'users' AND column_name = 'tenant_id';
    """)
    results["users_has_tenant_id"] = len(cur.fetchall()) > 0

    # Check tenant_user_memberships
    cur.execute("SELECT count(*), count(DISTINCT user_id), count(DISTINCT tenant_id) FROM tenant_user_memberships;")
    results["tenant_user_memberships_stats"] = cur.fetchone()

    print("2. Investigating Authorization Architecture (RBAC vs Direct)...")
    cur.execute("SELECT count(*) FROM roles;")
    results["roles_count"] = cur.fetchone()["count"]
    cur.execute("SELECT count(*) FROM permissions;")
    results["permissions_count"] = cur.fetchone()["count"]
    cur.execute("SELECT count(*) FROM role_permissions;")
    results["role_permissions_count"] = cur.fetchone()["count"]
    cur.execute("SELECT count(*) FROM user_role_assignments;")
    results["user_role_assignments_count"] = cur.fetchone()["count"]
    cur.execute("SELECT count(*) FROM user_permissions;")
    results["user_permissions_count"] = cur.fetchone()["count"]
    cur.execute("SELECT is_granted, count(*) FROM user_permissions GROUP BY is_granted;")
    results["user_permissions_breakdown"] = cur.fetchall()
    cur.execute("SELECT * FROM user_department_data_scopes;")
    results["user_department_data_scopes"] = cur.fetchall()

    print("3. Investigating Self-Referencing Hierarchies...")
    # Departments
    cur.execute("""
        SELECT 
            count(*) AS total_depts,
            count(*) FILTER (WHERE parent_id IS NULL) AS root_depts,
            count(*) FILTER (WHERE parent_id IS NOT NULL) AS child_depts,
            max(depth) AS max_depth
        FROM departments;
    """)
    results["department_hierarchy"] = cur.fetchone()
    
    # Tickets
    cur.execute("""
        SELECT 
            count(*) AS total_tickets,
            count(*) FILTER (WHERE parent_ticket_id IS NULL) AS root_tickets,
            count(*) FILTER (WHERE parent_ticket_id IS NOT NULL) AS child_tickets
        FROM tickets;
    """)
    results["ticket_hierarchy"] = cur.fetchone()

    # Ticket Comments
    cur.execute("""
        SELECT 
            count(*) AS total_comments,
            count(*) FILTER (WHERE parent_id IS NULL) AS root_comments,
            count(*) FILTER (WHERE parent_id IS NOT NULL) AS reply_comments
        FROM ticket_comments;
    """)
    results["ticket_comments_hierarchy"] = cur.fetchone()

    # Menus
    cur.execute("""
        SELECT 
            count(*) AS total_menus,
            count(*) FILTER (WHERE parent_id IS NULL) AS root_menus,
            count(*) FILTER (WHERE parent_id IS NOT NULL) AS sub_menus
        FROM menus;
    """)
    results["menu_hierarchy"] = cur.fetchone()

    # Talk Post Comments
    cur.execute("""
        SELECT 
            count(*) AS total_talk_comments,
            count(*) FILTER (WHERE parent_comment_id IS NULL) AS root_comments,
            count(*) FILTER (WHERE parent_comment_id IS NOT NULL) AS reply_comments
        FROM talk_post_comments;
    """)
    results["talk_post_comments_hierarchy"] = cur.fetchone()

    print("4. Investigating Ticket Workflow & Kanban Columns...")
    cur.execute("SELECT status, count(*) FROM tickets GROUP BY status;")
    results["ticket_status_dist"] = cur.fetchall()
    
    cur.execute("""
        SELECT 
            kc.id, kc.project_id, kc.title, kc.status_group, kc.position, kc.is_default, count(t.id) AS ticket_count
        FROM kanban_columns kc
        LEFT JOIN tickets t ON t.column_id = kc.id
        GROUP BY kc.id, kc.project_id, kc.title, kc.status_group, kc.position, kc.is_default
        ORDER BY kc.project_id, kc.position
        LIMIT 25;
    """)
    results["kanban_sample"] = cur.fetchall()

    cur.execute("""
        SELECT 
            status_group, count(*) AS column_count
        FROM kanban_columns
        GROUP BY status_group;
    """)
    results["kanban_status_groups"] = cur.fetchall()

    # Completed tickets check
    cur.execute("""
        SELECT 
            count(*) AS total_tickets,
            count(*) FILTER (WHERE completed_at IS NOT NULL) AS completed_at_not_null,
            count(*) FILTER (WHERE completed_at IS NULL) AS completed_at_null
        FROM tickets;
    """)
    results["tickets_completion_stats"] = cur.fetchone()

    print("5. Investigating Attendance Ingestion vs Aggregation...")
    cur.execute("SELECT count(*) FROM attendance_ingest_events;")
    results["ingest_events_cnt"] = cur.fetchone()["count"]
    cur.execute("SELECT count(*) FROM attendance_ingest_event_backups;")
    results["ingest_backups_cnt"] = cur.fetchone()["count"]
    cur.execute("SELECT count(*) FROM attendance_daily_records;")
    results["daily_records_cnt"] = cur.fetchone()["count"]
    cur.execute("SELECT count(*) FROM attendance_face_events;")
    results["face_events_cnt"] = cur.fetchone()["count"]
    cur.execute("SELECT count(*) FROM attendance_logs;")
    results["attendance_logs_cnt"] = cur.fetchone()["count"]

    # Sample daily records
    cur.execute("""
        SELECT user_id, work_date, first_check_in, last_check_out, actual_minutes, status, is_late, is_early_leave
        FROM attendance_daily_records
        LIMIT 5;
    """)
    results["daily_records_sample"] = cur.fetchall()

    print("6. Investigating Sensitive Data & PII Columns...")
    pii_cols = {}
    for tbl in ["users", "user_profiles", "attendance_face_events", "user_contract_histories"]:
        cur.execute(f"""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_schema = 'public' AND table_name = '{tbl}';
        """)
        pii_cols[tbl] = [f"{r['column_name']} ({r['data_type']})" for r in cur.fetchall()]
    results["pii_columns"] = pii_cols

    conn.close()
    p.terminate()
    p.wait()
    
    with open(r"artifacts\database-discovery\investigation_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)
    print("Investigation results saved to artifacts/database-discovery/investigation_results.json")

if __name__ == "__main__":
    run_investigation()
