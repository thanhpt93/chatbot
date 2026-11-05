import os
import json
import re
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

def discover_relationships():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    with open(r"artifacts\database-discovery\schema_inventory.json", "r", encoding="utf-8") as f:
        inv = json.load(f)

    # Map tables: schema.table -> table object
    table_map = {}
    table_pks = {}
    for t in inv["tables"]:
        full_name = f"{t['schema_name']}.{t['table_name']}"
        table_map[full_name] = t
        if t["primary_key"]:
            table_pks[t["table_name"]] = (t["schema_name"], t["primary_key"])

    # 1. Explicit Foreign Keys
    print("Extracting explicit foreign keys...")
    cur.execute("""
        SELECT 
            tc.constraint_name,
            tc.table_schema AS source_schema,
            tc.table_name AS source_table,
            kcu.column_name AS source_column,
            ccu.table_schema AS target_schema,
            ccu.table_name AS target_table,
            ccu.column_name AS target_column,
            rc.update_rule,
            rc.delete_rule
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
          ON tc.constraint_name = kcu.constraint_name
          AND tc.table_schema = kcu.table_schema
        JOIN information_schema.referential_constraints rc
          ON tc.constraint_name = rc.constraint_name
          AND tc.table_schema = rc.constraint_schema
        JOIN information_schema.constraint_column_usage ccu
          ON rc.unique_constraint_name = ccu.constraint_name
          AND rc.unique_constraint_schema = ccu.constraint_schema
        WHERE tc.table_schema NOT IN ('pg_catalog', 'information_schema')
        ORDER BY tc.table_schema, tc.table_name, kcu.column_name;
    """)
    raw_explicit_fks = cur.fetchall()

    explicit_relationships = []
    explicit_fk_set = set() # (source_schema, source_table, source_column)

    for fk in raw_explicit_fks:
        s_schema = fk["source_schema"]
        s_table = fk["source_table"]
        s_col = fk["source_column"]
        t_schema = fk["target_schema"]
        t_table = fk["target_table"]
        t_col = fk["target_column"]

        explicit_fk_set.add((s_schema, s_table, s_col))

        # Determine cardinality
        # Check if source_column is PK or has UNIQUE constraint
        src_tbl_obj = table_map.get(f"{s_schema}.{s_table}")
        is_source_unique = False
        if src_tbl_obj:
            if src_tbl_obj["primary_key"] == [s_col]:
                is_source_unique = True
            for c in src_tbl_obj["columns"]:
                if c["column_name"] == s_col and c["is_unique"]:
                    is_source_unique = True

        cardinality = "One-to-One" if is_source_unique else "Many-to-One"
        is_self_ref = (s_schema == t_schema and s_table == t_table)

        explicit_relationships.append({
            "constraint_name": fk["constraint_name"],
            "source_schema": s_schema,
            "source_table": s_table,
            "source_column": s_col,
            "target_schema": t_schema,
            "target_table": t_table,
            "target_column": t_col,
            "cardinality": cardinality,
            "is_self_referencing": is_self_ref,
            "update_rule": fk["update_rule"],
            "delete_rule": fk["delete_rule"],
            "relationship_type": "EXPLICIT_FK",
            "confidence": "Confirmed"
        })

    # 2. Inferred Relationships
    print("Discovering inferred relationships...")
    inferred_relationships = []

    # Common entity table targets in public schema
    # Map common suffix/names to target tables
    target_candidates = {
        "user_id": ("public", "users", "id"),
        "created_by": ("public", "users", "id"),
        "created_by_id": ("public", "users", "id"),
        "updated_by": ("public", "users", "id"),
        "updated_by_id": ("public", "users", "id"),
        "deleted_by": ("public", "users", "id"),
        "deleted_by_id": ("public", "users", "id"),
        "owner_id": ("public", "users", "id"),
        "manager_id": ("public", "users", "id"),
        "leader_id": ("public", "users", "id"),
        "assignee_id": ("public", "users", "id"),
        "assigned_by_user_id": ("public", "users", "id"),
        "author_id": ("public", "users", "id"),
        "sender_id": ("public", "users", "id"),
        "recipient_id": ("public", "users", "id"),
        "department_id": ("public", "departments", "id"),
        "project_id": ("public", "projects", "id"),
        "ticket_id": ("public", "tickets", "id"),
        "tenant_id": ("public", "tenants", "id"),
        "parent_id": None, # Self-ref
        "file_id": ("public", "files", "id"),
        "role_id": ("public", "roles", "id"),
        "permission_id": ("public", "permissions", "id"),
        "approval_request_id": ("public", "approval_requests", "id"),
        "schedule_event_id": ("public", "schedule_events", "id"),
        "conversation_id": ("public", "chat_conversations", "id"),
        "message_id": ("public", "chat_messages", "id"),
        "notice_id": ("public", "notices", "id"),
        "talk_post_id": ("public", "talk_posts", "id"),
        "asset_id": ("public", "assets", "id")
    }

    for t in inv["tables"]:
        s_schema = t["schema_name"]
        s_table = t["table_name"]
        if t["table_type"] != 'BASE TABLE' or s_schema != 'public':
            continue

        for col in t["columns"]:
            c_name = col["column_name"]
            
            # Skip if already explicit FK
            if (s_schema, s_table, c_name) in explicit_fk_set:
                continue

            target = None
            if c_name in target_candidates:
                target = target_candidates[c_name]
                if c_name == "parent_id":
                    target = (s_schema, s_table, t["primary_key"][0] if t["primary_key"] else "id")
            elif c_name.endswith("_id"):
                prefix = c_name[:-3]
                # Check if plural exists (e.g. category_id -> categories, status_id -> statuses)
                plural = prefix + "s"
                if plural in table_pks:
                    target = (table_pks[plural][0], plural, table_pks[plural][1][0])
                elif prefix + "es" in table_pks:
                    target = (table_pks[prefix + "es"][0], prefix + "es", table_pks[prefix + "es"][1][0])
                elif prefix in table_pks:
                    target = (table_pks[prefix][0], prefix, table_pks[prefix][1][0])

            if target and target[1] in table_pks:
                tgt_schema, tgt_table, tgt_col = target
                # Check data match
                try:
                    cur.execute(f'''
                        SELECT 
                            count(DISTINCT "{c_name}") AS src_distinct,
                            count(DISTINCT src."{c_name}") FILTER (WHERE tgt."{tgt_col}" IS NOT NULL) AS matched_distinct
                        FROM "{s_schema}"."{s_table}" src
                        LEFT JOIN "{tgt_schema}"."{tgt_table}" tgt ON tgt."{tgt_col}" = src."{c_name}"
                        WHERE src."{c_name}" IS NOT NULL;
                    ''')
                    res = cur.fetchone()
                    src_dist = res["src_distinct"]
                    matched_dist = res["matched_distinct"]
                    
                    if src_dist == 0:
                        match_rate = 100.0
                        confidence = "Inferred (Empty/Null Column)"
                    else:
                        match_rate = round((matched_dist / src_dist) * 100, 2)
                        if match_rate == 100.0:
                            confidence = "Inferred (High - 100% Match)"
                        elif match_rate >= 90.0:
                            confidence = "Inferred (Partial - Broken Refs)"
                        else:
                            confidence = "Needs Validation (Low Match Rate)"

                    is_self_ref = (s_schema == tgt_schema and s_table == tgt_table)
                    inferred_relationships.append({
                        "source_schema": s_schema,
                        "source_table": s_table,
                        "source_column": c_name,
                        "target_schema": tgt_schema,
                        "target_table": tgt_table,
                        "target_column": tgt_col,
                        "cardinality": "Many-to-One",
                        "is_self_referencing": is_self_ref,
                        "match_rate": match_rate,
                        "source_distinct_count": src_dist,
                        "matched_distinct_count": matched_dist,
                        "relationship_type": "INFERRED",
                        "confidence": confidence
                    })
                except Exception as e:
                    conn.rollback()

    # 3. Junction / Mapping Tables (Many-to-Many)
    print("Identifying Many-to-Many junction tables...")
    junction_tables = []
    for t in inv["tables"]:
        s_schema = t["schema_name"]
        s_table = t["table_name"]
        if t["table_type"] != 'BASE TABLE' or s_schema != 'public':
            continue

        # Look for tables where:
        # a) PK is composite or has multiple FKs
        # b) Table name contains mapping semantics: _members, _assignees, _participants, _tags, _relations, _links, _permissions, _roles
        all_table_fks = [fk for fk in explicit_relationships if fk["source_schema"] == s_schema and fk["source_table"] == s_table]
        inferred_table_fks = [fk for fk in inferred_relationships if fk["source_schema"] == s_schema and fk["source_table"] == s_table and fk["confidence"].startswith("Inferred")]
        
        combined_fks = all_table_fks + inferred_table_fks
        target_tables = list(set([f"{fk['target_schema']}.{fk['target_table']}" for fk in combined_fks if fk['target_table'] != s_table]))
        
        is_junction = False
        reasons = []
        
        if len(target_tables) >= 2:
            reasons.append(f"References {len(target_tables)} distinct entities: {', '.join(target_tables)}")
            # If table has relatively few columns (mostly FKs + timestamps/status)
            if len(t["columns"]) <= 10:
                reasons.append("Compact mapping structure (<= 10 columns)")
                is_junction = True
            elif any(s_table.endswith(suff) for suff in ['_members', '_assignees', '_participants', '_tags', '_relations', '_links', '_assignments', '_recipients', '_scopes']):
                reasons.append("Naming convention matches associative/junction entity")
                is_junction = True

        if is_junction:
            junction_tables.append({
                "schema_name": s_schema,
                "table_name": s_table,
                "row_count": t["row_count"],
                "connected_entities": target_tables,
                "foreign_keys_count": len(combined_fks),
                "reasons": reasons
            })

    conn.close()

    results = {
        "explicit_foreign_keys_count": len(explicit_relationships),
        "inferred_relationships_count": len(inferred_relationships),
        "junction_tables_count": len(junction_tables),
        "explicit_relationships": explicit_relationships,
        "inferred_relationships": inferred_relationships,
        "junction_tables": junction_tables
    }

    out_path = r"artifacts\database-discovery\relationships.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)

    print(f"Relationships discovered and saved to {out_path}")
    print(f"Explicit FKs: {len(explicit_relationships)}")
    print(f"Inferred Relationships: {len(inferred_relationships)}")
    print(f"Junction Tables: {len(junction_tables)}")

if __name__ == "__main__":
    discover_relationships()
