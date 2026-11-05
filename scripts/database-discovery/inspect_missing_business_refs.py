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

    cur.execute('''
        SELECT 
            COUNT(*) AS total_rows,
            COUNT(assigned_user_id) AS non_null_count,
            COUNT(DISTINCT assigned_user_id) AS distinct_count
        FROM assets;
    ''')
    stats = cur.fetchone()
    cur.execute('''
        SELECT 
            COUNT(DISTINCT s.assigned_user_id) AS matched_distinct_count
        FROM assets s
        JOIN users t ON s.assigned_user_id = t.id
        WHERE s.assigned_user_id IS NOT NULL;
    ''')
    m_stats = cur.fetchone()
    print("assets.assigned_user_id:", stats, m_stats)

    # Also check created_by_user_id in assets
    cur.execute('''
        SELECT 
            COUNT(*) AS total_rows,
            COUNT(created_by_user_id) AS non_null_count,
            COUNT(DISTINCT created_by_user_id) AS distinct_count
        FROM assets;
    ''')
    stats_c = cur.fetchone()
    cur.execute('''
        SELECT 
            COUNT(DISTINCT s.created_by_user_id) AS matched_distinct_count
        FROM assets s
        JOIN users t ON s.created_by_user_id = t.id
        WHERE s.created_by_user_id IS NOT NULL;
    ''')
    m_stats_c = cur.fetchone()
    print("assets.created_by_user_id:", stats_c, m_stats_c)

    conn.close()
    p.terminate()
    p.wait()

if __name__ == "__main__":
    main()
