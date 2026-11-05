import subprocess
import time
import psycopg2
from psycopg2.extras import RealDictCursor

def main():
    p = subprocess.Popen([
        r"C:\Users\admin\miniconda3\envs\chat\Library\bin\postgres.exe",
        "-D", r"C:\Project\chatbot\.pgdata",
        "-p", "5433"
    ])
    time.sleep(1.5)
    
    conn = psycopg2.connect("host=127.0.0.1 port=5433 user=postgres dbname=inf_nffice sslmode=disable gssencmode=disable")
    cur = conn.cursor(cursor_factory=RealDictCursor)

    # 1. Check data types of users.id, user_profiles.id, user_profiles.user_id
    cur.execute("""
        SELECT table_name, column_name, data_type, udt_name, numeric_precision, numeric_scale
        FROM information_schema.columns
        WHERE table_schema = 'public' 
          AND (
            (table_name = 'users' AND column_name = 'id')
            OR (table_name = 'user_profiles' AND column_name IN ('id', 'user_id'))
          )
        ORDER BY table_name, column_name;
    """)
    print("=== 1. USER ID TYPES ===")
    for r in cur.fetchall():
        print(f"Table: {r['table_name']}, Col: {r['column_name']}, Type: {r['data_type']}, UDT: {r['udt_name']}, Precision: {r['numeric_precision']}")

    # 2. Check all user-referencing columns in public
    cur.execute("""
        SELECT table_name, column_name, data_type, udt_name
        FROM information_schema.columns
        WHERE table_schema = 'public'
          AND (
            column_name IN ('user_id', 'created_by_user_id', 'updated_by_user_id', 'deleted_by_id', 'manager_user_id', 'author_user_id', 'author_id', 'sender_user_id', 'sender_id', 'current_holder_id', 'requester_id')
            OR column_name LIKE '%user_id%'
          )
        ORDER BY table_name, column_name;
    """)
    print("\n=== 2. ALL USER REFERENCING COLS ===")
    user_cols = cur.fetchall()
    print(f"Total user referencing columns found: {len(user_cols)}")
    type_counts = {}
    for r in user_cols:
        t = r['data_type']
        type_counts[t] = type_counts.get(t, 0) + 1
    print(f"Type breakdown: {type_counts}")
    for r in user_cols[:30]:
        print(f"  {r['table_name']}.{r['column_name']}: {r['data_type']} ({r['udt_name']})")

    # 3. Check projects columns
    cur.execute("""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = 'projects'
        ORDER BY ordinal_position;
    """)
    print("\n=== 3. PROJECTS COLUMNS ===")
    for r in cur.fetchall():
        print(f"  {r['column_name']}: {r['data_type']} (nullable: {r['is_nullable']})")

    # Check project_members roles
    cur.execute("""
        SELECT role, count(*) 
        FROM project_members 
        GROUP BY role;
    """)
    print("Project Members Role Distribution:")
    for r in cur.fetchall():
        print(f"  {r['role']}: {r['count']}")

    # Check if created_by_user_id exists in projects
    cur.execute("""
        SELECT count(*), count(created_by_user_id) 
        FROM projects;
    """)
    print("Projects created_by_user_id count:", cur.fetchone())

    # 4. Check chat_messages columns
    cur.execute("""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = 'chat_messages'
        ORDER BY ordinal_position;
    """)
    print("\n=== 4. CHAT_MESSAGES COLUMNS ===")
    for r in cur.fetchall():
        print(f"  {r['column_name']}: {r['data_type']} (nullable: {r['is_nullable']})")

    # 5. Check schedule_events columns
    cur.execute("""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = 'schedule_events'
        ORDER BY ordinal_position;
    """)
    print("\n=== 5. SCHEDULE_EVENTS COLUMNS ===")
    for r in cur.fetchall():
        print(f"  {r['column_name']}: {r['data_type']} (nullable: {r['is_nullable']})")

    # 6. Check tenant_user_memberships schema and records
    cur.execute("""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = 'tenant_user_memberships'
        ORDER BY ordinal_position;
    """)
    print("\n=== 6. TENANT_USER_MEMBERSHIPS SCHEMA ===")
    for r in cur.fetchall():
        print(f"  {r['column_name']}: {r['data_type']}")

    cur.execute("SELECT * FROM tenant_user_memberships;")
    print("TENANT_USER_MEMBERSHIPS ALL ROWS:")
    rows = cur.fetchall()
    print(f"Total rows in tenant_user_memberships: {len(rows)}")
    for r in rows:
        print(r)

    # Check unique constraints on tenant_user_memberships
    cur.execute("""
        SELECT tc.constraint_name, tc.constraint_type, kcu.column_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu 
          ON tc.constraint_name = kcu.constraint_name AND tc.table_schema = kcu.table_schema
        WHERE tc.table_schema = 'public' AND tc.table_name = 'tenant_user_memberships';
    """)
    print("TENANT_USER_MEMBERSHIPS CONSTRAINTS:")
    for r in cur.fetchall():
        print(r)

    conn.close()
    p.terminate()
    p.wait()

if __name__ == "__main__":
    main()
