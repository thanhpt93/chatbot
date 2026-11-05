# -*- coding: utf-8 -*-
"""Phase 1.2 - Extract complete profiling metrics from artifacts/database-discovery/
and run any supplementary read-only SQL checks if PostgreSQL is reachable.
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))

INV_PATH = r"artifacts\database-discovery\schema_inventory.json"
PROF_PATH = r"artifacts\database-discovery\data_profiling.json"
REL_PATH = r"artifacts\database-discovery\relationships.json"
INV_RES_PATH = r"artifacts\database-discovery\investigation_results.json"

inv = json.load(open(INV_PATH, encoding="utf-8"))
prof = json.load(open(PROF_PATH, encoding="utf-8"))
rels = json.load(open(REL_PATH, encoding="utf-8"))
inv_res = json.load(open(INV_RES_PATH, encoding="utf-8"))

tables = {(t["schema_name"], t["table_name"]): t for t in inv["tables"]}

TARGET_TABLES = [
    "tenants", "users", "user_profiles", "tenant_user_memberships",
    "departments", "department_members", "roles", "permissions",
    "user_role_assignments", "role_permissions", "user_permissions",
    "projects", "project_members", "tickets", "ticket_assignees",
    "project_sprints", "kanban_columns", "approval_requests",
    "approval_participants", "approval_workflow_templates", "approval_workflow_steps",
    "schedule_events", "schedule_event_participants", "schedule_rooms",
    "notices", "audiences", "audience_user_members", "audience_department_members",
    "talk_posts", "talk_tags", "talk_post_tags", "assets", "asset_categories",
    "asset_assignments", "files", "chat_conversations", "chat_conversation_members",
    "chat_messages", "user_leave_monthly_balances", "user_leave_year_balances",
    "leave_catalogs", "attendance_daily_records", "user_contract_histories",
    "project_tags", "ticket_tags", "project_common_documents", "user_department_data_scopes"
]

profile_summary = {
    "generated_at": "2026-11-05T09:15:00+07:00",
    "database_version": inv.get("database_version"),
    "source_artifacts": [INV_PATH, PROF_PATH, REL_PATH, INV_RES_PATH],
    "tables": {},
    "relationships": [],
    "investigation_highlights": inv_res
}

for tname in TARGET_TABLES:
    key = f"public.{tname}"
    tmeta = tables.get(("public", tname), {})
    pmeta = prof.get(key, {})
    profile_summary["tables"][tname] = {
        "row_count": tmeta.get("row_count", pmeta.get("row_count")),
        "primary_key": tmeta.get("primary_key", []),
        "unique_indexes": [i["indexdef"] for i in tmeta.get("indexes", []) if "UNIQUE" in i["indexdef"]],
        "columns": {
            c["column_name"]: {
                "udt_name": c["udt_name"],
                "data_type": c["data_type"],
                "is_nullable": c["is_nullable"],
                "null_count": pmeta.get("columns", {}).get(c["column_name"], {}).get("null_count"),
                "distinct_count": pmeta.get("columns", {}).get(c["column_name"], {}).get("distinct_count"),
                "distribution": pmeta.get("columns", {}).get(c["column_name"], {}).get("distribution"),
                "min_value": pmeta.get("columns", {}).get(c["column_name"], {}).get("min_value"),
                "max_value": pmeta.get("columns", {}).get(c["column_name"], {}).get("max_value"),
            }
            for c in tmeta.get("columns", [])
        },
        "status_distributions": pmeta.get("status_distributions", {}),
        "duplicate_primary_keys": pmeta.get("duplicate_primary_keys", 0),
    }

for r in rels["inferred_relationships"]:
    if r["source_table"] in TARGET_TABLES or r["target_table"] in TARGET_TABLES:
        profile_summary["relationships"].append(r)

os.makedirs(r"artifacts\phase1_2", exist_ok=True)
with open(r"artifacts\phase1_2\data_profile.json", "w", encoding="utf-8") as f:
    json.dump(profile_summary, f, indent=2, ensure_ascii=False)

lines = [f"Database Version: {profile_summary['database_version']}", f"Tables Profiled: {len(profile_summary['tables'])}"]
for tname, tdata in profile_summary["tables"].items():
    lines.append(f"\n=== public.{tname} (rows={tdata['row_count']}, pk={tdata['primary_key']}) ===")
    for cname, cdata in tdata["columns"].items():
        dist_str = f" dist={cdata['distribution']}" if cdata.get("distribution") else ""
        range_str = f" range=[{cdata['min_value']}..{cdata['max_value']}]" if cdata.get("min_value") else ""
        lines.append(f"  - {cname}: {cdata['udt_name']} (nullable={cdata['is_nullable']}, nulls={cdata['null_count']}, distinct={cdata['distinct_count']}){dist_str}{range_str}")
    if tdata["status_distributions"]:
        lines.append(f"  status_distributions: {tdata['status_distributions']}")

lines.append("\n=== Key Relationships Match Rates ===")
for r in profile_summary["relationships"]:
    lines.append(f"  {r['source_table']}.{r['source_column']} -> {r['target_table']}.{r['target_column']}: src_dist={r['source_distinct_count']}, match_dist={r['matched_distinct_count']}, rate={r['match_rate']}%, conf={r['confidence']}")

with open(r"artifacts\phase1_2\data_profile.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")
print("Saved artifacts/phase1_2/data_profile.json and data_profile.txt")
