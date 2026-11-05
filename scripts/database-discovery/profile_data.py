import os
import json
import psycopg2
from psycopg2.extras import RealDictCursor

DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 5433,
    "user": "postgres",
    "dbname": "inf_nffice",
    "sslmode": "disable",
    "gssencmode": "disable"
}

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

def profile_tables():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # Load schema inventory
    with open(r"artifacts\database-discovery\schema_inventory.json", "r", encoding="utf-8") as f:
        inv = json.load(f)
        
    profiling_results = {}
    
    print("Starting data profiling on tables...")
    
    for table in inv["tables"]:
        s_name = table["schema_name"]
        t_name = table["table_name"]
        t_type = table["table_type"]
        
        if t_type != 'BASE TABLE':
            continue
            
        full_table_name = f"{s_name}.{t_name}"
        row_count = table["row_count"]
        
        table_profile = {
            "schema_name": s_name,
            "table_name": t_name,
            "row_count": row_count,
            "columns": {},
            "status_distributions": {},
            "date_ranges": {},
            "duplicate_primary_keys": 0,
            "foreign_key_orphans": {}
        }
        
        if row_count == 0:
            profiling_results[full_table_name] = table_profile
            continue
            
        # 1. Column profiling: NULL counts, distinct counts
        for col in table["columns"]:
            c_name = col["column_name"]
            c_type = col["data_type"]
            udt_name = col["udt_name"]
            
            try:
                cur.execute(f'''
                    SELECT 
                        count(*) - count("{c_name}") AS null_count,
                        count(DISTINCT "{c_name}") AS distinct_count
                    FROM "{s_name}"."{t_name}";
                ''')
                res = cur.fetchone()
                null_cnt = res["null_count"]
                null_pct = round((null_cnt / row_count) * 100, 2) if row_count > 0 else 0
                dist_cnt = res["distinct_count"]
                
                col_stat = {
                    "null_count": null_cnt,
                    "null_percentage": null_pct,
                    "distinct_count": dist_cnt
                }
                
                # If date/timestamp, get min and max
                if "timestamp" in c_type or "date" in c_type or "time" in c_type:
                    cur.execute(f'''
                        SELECT min("{c_name}")::text AS min_val, max("{c_name}")::text AS max_val
                        FROM "{s_name}"."{t_name}";
                    ''')
                    min_max = cur.fetchone()
                    col_stat["min_value"] = min_max["min_val"]
                    col_stat["max_value"] = min_max["max_val"]
                    table_profile["date_ranges"][c_name] = {
                        "min": min_max["min_val"],
                        "max": min_max["max_val"]
                    }
                    
                # If potential status, type, priority, role, flag, or low cardinality text
                if dist_cnt > 0 and dist_cnt <= 20 and (c_type in ['character varying', 'text', 'character', 'integer', 'smallint', 'boolean'] or 'status' in c_name.lower() or 'type' in c_name.lower() or 'role' in c_name.lower()):
                    cur.execute(f'''
                        SELECT "{c_name}"::text AS val, count(*) AS cnt
                        FROM "{s_name}"."{t_name}"
                        GROUP BY "{c_name}"
                        ORDER BY cnt DESC;
                    ''')
                    distrib = {str(r["val"]): r["cnt"] for r in cur.fetchall()}
                    col_stat["distribution"] = distrib
                    if any(k in c_name.lower() for k in ['status', 'state', 'phase', 'type', 'priority', 'role', 'visibility']):
                        table_profile["status_distributions"][c_name] = distrib

                table_profile["columns"][c_name] = col_stat
            except Exception as e:
                conn.rollback()
                table_profile["columns"][c_name] = {"error": str(e)}

        # 2. Duplicate primary keys check
        if table["primary_key"]:
            pk_cols_str = ', '.join([f'"{k}"' for k in table["primary_key"]])
            try:
                cur.execute(f'''
                    SELECT count(*) AS dup_cnt
                    FROM (
                        SELECT {pk_cols_str}
                        FROM "{s_name}"."{t_name}"
                        GROUP BY {pk_cols_str}
                        HAVING count(*) > 1
                    ) sub;
                ''')
                table_profile["duplicate_primary_keys"] = cur.fetchone()["dup_cnt"]
            except Exception:
                conn.rollback()
                
        # 3. Check explicit FK orphan counts
        for fk in table["foreign_keys"]:
            c_name = fk["column_name"]
            tgt_schema = fk["foreign_table_schema"]
            tgt_table = fk["foreign_table_name"]
            tgt_col = fk["foreign_column_name"]
            
            try:
                cur.execute(f'''
                    SELECT count(*) AS orphan_cnt
                    FROM "{s_name}"."{t_name}" src
                    WHERE src."{c_name}" IS NOT NULL
                      AND NOT EXISTS (
                          SELECT 1 FROM "{tgt_schema}"."{tgt_table}" tgt
                          WHERE tgt."{tgt_col}" = src."{c_name}"
                      );
                ''')
                orphan_cnt = cur.fetchone()["orphan_cnt"]
                table_profile["foreign_key_orphans"][c_name] = {
                    "target": f"{tgt_schema}.{tgt_table}({tgt_col})",
                    "orphan_count": orphan_cnt
                }
            except Exception:
                conn.rollback()
                
        profiling_results[full_table_name] = table_profile

    conn.close()
    
    out_path = r"artifacts\database-discovery\data_profiling.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(profiling_results, f, indent=2, ensure_ascii=False, default=str)
        
    print(f"Data profiling completed and saved to {out_path}")
    print(f"Total tables profiled: {len(profiling_results)}")

if __name__ == "__main__":
    profile_tables()
