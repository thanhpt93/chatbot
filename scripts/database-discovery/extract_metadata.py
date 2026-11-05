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

def extract_metadata():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    print("Extracting database version and overview...")
    cur.execute("SELECT version();")
    db_version = cur.fetchone()["version"]
    
    # 1. Schemas
    cur.execute("""
        SELECT nspname AS schema_name,
               pg_catalog.pg_get_userbyid(nspowner) AS schema_owner,
               obj_description(oid, 'pg_namespace') AS description
        FROM pg_catalog.pg_namespace
        WHERE nspname NOT IN ('pg_catalog', 'information_schema')
        ORDER BY nspname;
    """)
    schemas = cur.fetchall()
    
    # 2. Tables and Views
    print("Extracting tables and views...")
    cur.execute("""
        SELECT table_schema, table_name, table_type
        FROM information_schema.tables
        WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
        ORDER BY table_schema, table_name;
    """)
    raw_tables = cur.fetchall()
    
    tables_meta = []
    
    for t in raw_tables:
        s_name = t["table_schema"]
        t_name = t["table_name"]
        t_type = t["table_type"]
        
        # Get comment
        cur.execute("""
            SELECT obj_description(c.oid, 'pg_class') AS description
            FROM pg_class c
            JOIN pg_namespace n ON n.oid = c.relnamespace
            WHERE n.nspname = %s AND c.relname = %s;
        """, (s_name, t_name))
        res_desc = cur.fetchone()
        t_desc = res_desc["description"] if res_desc else None
        
        # Row count and size
        row_count = 0
        total_size_bytes = 0
        if t_type == 'BASE TABLE':
            try:
                cur.execute(f'SELECT count(*) AS cnt FROM "{s_name}"."{t_name}";')
                row_count = cur.fetchone()["cnt"]
            except Exception as e:
                conn.rollback()
                row_count = -1
                
            try:
                cur.execute(f'SELECT pg_total_relation_size(\'"{s_name}"."{t_name}"\') AS sz;')
                total_size_bytes = cur.fetchone()["sz"]
            except Exception:
                conn.rollback()
                total_size_bytes = 0
        
        # Columns
        cur.execute("""
            SELECT 
                column_name,
                ordinal_position,
                column_default,
                is_nullable,
                data_type,
                character_maximum_length,
                numeric_precision,
                numeric_scale,
                udt_name
            FROM information_schema.columns
            WHERE table_schema = %s AND table_name = %s
            ORDER BY ordinal_position;
        """, (s_name, t_name))
        cols = cur.fetchall()
        
        # Column comments
        cur.execute("""
            SELECT 
                a.attname AS column_name,
                col_description(a.attrelid, a.attnum) AS description
            FROM pg_attribute a
            JOIN pg_class c ON c.oid = a.attrelid
            JOIN pg_namespace n ON n.oid = c.relnamespace
            WHERE n.nspname = %s AND c.relname = %s AND a.attnum > 0 AND NOT a.attisdropped;
        """, (s_name, t_name))
        col_comments = {row["column_name"]: row["description"] for row in cur.fetchall()}
        
        # PK columns
        cur.execute("""
            SELECT kcu.column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
              ON tc.constraint_name = kcu.constraint_name
              AND tc.table_schema = kcu.table_schema
            WHERE tc.constraint_type = 'PRIMARY KEY'
              AND tc.table_schema = %s AND tc.table_name = %s;
        """, (s_name, t_name))
        pk_cols = [r["column_name"] for r in cur.fetchall()]
        
        # FK columns
        cur.execute("""
            SELECT 
                kcu.column_name,
                ccu.table_schema AS foreign_table_schema,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name,
                tc.constraint_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
              ON tc.constraint_name = kcu.constraint_name
              AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage ccu
              ON ccu.constraint_name = tc.constraint_name
              AND ccu.table_schema = tc.table_schema
            WHERE tc.constraint_type = 'FOREIGN KEY'
              AND tc.table_schema = %s AND tc.table_name = %s;
        """, (s_name, t_name))
        fk_list = cur.fetchall()
        fk_cols = {r["column_name"]: r for r in fk_list}
        
        # Unique constraints
        cur.execute("""
            SELECT kcu.column_name, tc.constraint_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
              ON tc.constraint_name = kcu.constraint_name
              AND tc.table_schema = kcu.table_schema
            WHERE tc.constraint_type = 'UNIQUE'
              AND tc.table_schema = %s AND tc.table_name = %s;
        """, (s_name, t_name))
        unique_cols = {r["column_name"]: r["constraint_name"] for r in cur.fetchall()}
        
        # Indexes
        cur.execute("""
            SELECT 
                indexname,
                indexdef
            FROM pg_indexes
            WHERE schemaname = %s AND tablename = %s;
        """, (s_name, t_name))
        indexes = cur.fetchall()
        
        formatted_cols = []
        for c in cols:
            c_name = c["column_name"]
            is_pk = c_name in pk_cols
            is_fk = c_name in fk_cols
            is_unique = c_name in unique_cols
            fk_info = fk_cols.get(c_name)
            
            formatted_cols.append({
                "column_name": c_name,
                "ordinal_position": c["ordinal_position"],
                "data_type": c["data_type"],
                "udt_name": c["udt_name"],
                "length": c["character_maximum_length"],
                "precision": c["numeric_precision"],
                "scale": c["numeric_scale"],
                "is_nullable": c["is_nullable"] == 'YES',
                "default_value": c["column_default"],
                "is_primary_key": is_pk,
                "is_foreign_key": is_fk,
                "foreign_key_target": f"{fk_info['foreign_table_schema']}.{fk_info['foreign_table_name']}({fk_info['foreign_column_name']})" if fk_info else None,
                "foreign_key_constraint": fk_info['constraint_name'] if fk_info else None,
                "is_unique": is_unique,
                "description": col_comments.get(c_name)
            })
            
        tables_meta.append({
            "schema_name": s_name,
            "table_name": t_name,
            "table_type": t_type,
            "description": t_desc,
            "row_count": row_count,
            "total_size_bytes": total_size_bytes,
            "primary_key": pk_cols,
            "columns": formatted_cols,
            "foreign_keys": fk_list,
            "indexes": indexes
        })
        
    # 3. Views definition
    print("Extracting view definitions...")
    cur.execute("""
        SELECT table_schema, table_name, view_definition
        FROM information_schema.views
        WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
        ORDER BY table_schema, table_name;
    """)
    views = cur.fetchall()
    
    # 4. Functions
    print("Extracting functions and procedures...")
    cur.execute("""
        SELECT 
            n.nspname AS schema_name,
            p.proname AS routine_name,
            pg_catalog.pg_get_function_result(p.oid) AS result_data_type,
            pg_catalog.pg_get_function_arguments(p.oid) AS argument_data_types,
            CASE p.prokind
                WHEN 'f' THEN 'FUNCTION'
                WHEN 'p' THEN 'PROCEDURE'
                WHEN 'a' THEN 'AGGREGATE'
                WHEN 'w' THEN 'WINDOW'
            END AS routine_type,
            p.prosrc AS source_code,
            obj_description(p.oid, 'pg_proc') AS description
        FROM pg_catalog.pg_proc p
        JOIN pg_catalog.pg_namespace n ON n.oid = p.pronamespace
        WHERE n.nspname NOT IN ('pg_catalog', 'information_schema')
        ORDER BY n.nspname, p.proname;
    """)
    routines = cur.fetchall()
    
    # 5. Triggers
    print("Extracting triggers...")
    cur.execute("""
        SELECT 
            event_object_schema AS schema_name,
            event_object_table AS table_name,
            trigger_name,
            event_manipulation,
            action_timing,
            action_statement
        FROM information_schema.triggers
        WHERE trigger_schema NOT IN ('pg_catalog', 'information_schema')
        ORDER BY event_object_schema, event_object_table, trigger_name;
    """)
    triggers = cur.fetchall()
    
    # 6. Sequences
    print("Extracting sequences...")
    cur.execute("""
        SELECT 
            sequence_schema,
            sequence_name,
            data_type,
            start_value,
            minimum_value,
            maximum_value,
            increment
        FROM information_schema.sequences
        WHERE sequence_schema NOT IN ('pg_catalog', 'information_schema')
        ORDER BY sequence_schema, sequence_name;
    """)
    sequences = cur.fetchall()

    conn.close()

    result = {
        "database_name": DB_CONFIG["dbname"],
        "database_engine": "PostgreSQL",
        "database_version": db_version,
        "schemas": schemas,
        "tables": tables_meta,
        "views": views,
        "routines": routines,
        "triggers": triggers,
        "sequences": sequences
    }
    
    out_path = r"artifacts\database-discovery\schema_inventory.json"
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False, default=str)
        
    print(f"Extracted metadata saved to {out_path}")
    print(f"Total tables/views processed: {len(tables_meta)}")
    print(f"Total routines processed: {len(routines)}")
    print(f"Total triggers processed: {len(triggers)}")
    print(f"Total sequences processed: {len(sequences)}")

if __name__ == "__main__":
    extract_metadata()
