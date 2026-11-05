# -*- coding: utf-8 -*-
"""Phase 1.2 - Dump verified schema facts for candidate graph tables from the
extracted PostgreSQL catalog snapshot (artifacts/database-discovery/schema_inventory.json).
Read-only. Output: artifacts/phase1_2/schema_facts.json + console summary."""
import json, os, re, sys

INV = r"artifacts\database-discovery\schema_inventory.json"
OUT_DIR = r"artifacts\phase1_2"
os.makedirs(OUT_DIR, exist_ok=True)

inv = json.load(open(INV, encoding="utf-8"))
tables = {(t["schema_name"], t["table_name"]): t for t in inv["tables"]}

CANDIDATES = [
    "users", "user_profiles", "tenants", "tenant_user_memberships",
    "departments", "department_members", "roles", "permissions",
    "user_role_assignments", "role_permissions", "user_permissions",
    "projects", "project_members", "tickets", "ticket_assignees",
    "project_sprints", "kanban_columns", "approval_requests",
    "approval_participants", "approval_workflow_templates",
    "schedule_events", "schedule_event_participants", "schedule_rooms",
    "notices", "audiences", "talk_posts", "assets", "asset_categories",
    "files", "chat_conversations", "chat_conversation_members",
    "user_leave_monthly_balances", "attendance_daily_records",
    "user_contract_histories", "project_tags", "ticket_tags", "tags",
]

facts = {"source": INV, "database_version": inv.get("database_version"), "tables": {}}
missing = []
for name in CANDIDATES:
    t = tables.get(("public", name))
    if not t:
        missing.append(name)
        continue
    uniq = [i["indexdef"] for i in t.get("indexes", []) if "UNIQUE" in i["indexdef"]]
    facts["tables"][name] = {
        "row_count": t["row_count"],
        "primary_key": t["primary_key"],
        "foreign_keys": t["foreign_keys"],
        "unique_indexes": uniq,
        "columns": [{"name": c["column_name"], "type": c["udt_name"], "nullable": c["is_nullable"]} for c in t["columns"]],
    }

# tables with tenant_id
tenant_tables = sorted(f'{t["schema_name"]}.{t["table_name"]}' for t in inv["tables"]
                       if t["table_type"] == "BASE TABLE" and any(c["column_name"] == "tenant_id" for c in t["columns"]))
facts["tables_with_tenant_id"] = tenant_tables
facts["missing_candidates"] = missing
# related approval / audience / tag / chat tables for discovery
facts["related_tables"] = sorted(t["table_name"] for t in inv["tables"] if t["schema_name"] == "public" and
                                 re.match(r"^(approval_workflow|audience|tag|chat_|project_member|asset_|leave|user_leave|attendance_daily|talk_)", t["table_name"]))
json.dump(facts, open(os.path.join(OUT_DIR, "schema_facts.json"), "w", encoding="utf-8"), indent=1)

print("DB version:", facts["database_version"])
print("MISSING candidates:", missing)
print("Tables with tenant_id (%d):" % len(tenant_tables), ", ".join(tenant_tables))
print("Related tables:", ", ".join(facts["related_tables"]))
for n, f in facts["tables"].items():
    cols = ", ".join(f'{c["name"]}:{c["type"]}{"" if c["nullable"] else "!"}' for c in f["columns"])
    print(f"\n## {n} rows={f['row_count']} pk={f['primary_key']}")
    print("  cols:", cols)
    for u in f["unique_indexes"]:
        print("  UQ:", re.sub(r"CREATE UNIQUE INDEX (\S+) ON public\.\S+ USING btree", r"\1", u))
