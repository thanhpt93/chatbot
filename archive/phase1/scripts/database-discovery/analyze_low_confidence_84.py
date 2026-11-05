import json

with open("artifacts/database-discovery/relationships.json", "r", encoding="utf-8") as f:
    rels = json.load(f)

with open("artifacts/database-discovery/schema_inventory.json", "r", encoding="utf-8") as f:
    inv = json.load(f)

# Map table rows and schemas
tbl_info = {}
for t in inv["tables"]:
    tbl_info[f"{t['schema_name']}.{t['table_name']}"] = {
        "rows": t["row_count"],
        "schema": t["schema_name"],
        "name": t["table_name"]
    }

inferred = rels["inferred_relationships"]
low_84 = [r for r in inferred if r["source_distinct_count"] == 0]
print(f"Total Low Confidence relationships: {len(low_84)}")

telemetry_or_backup = set()
for r in low_84:
    s_full = f"{r['source_schema']}.{r['source_table']}"
    t_full = f"{r['target_schema']}.{r['target_table']}"
    s_schema = r["source_schema"]
    s_tbl = r["source_table"]
    
    is_telemetry = (
        s_schema in ("_backup_cleanup_20261005", "maintenance_backup", "hangfire") or
        s_tbl in ("system_logs", "error_tracking_outbox", "chat_audit_log", "mail_send_logs", "user_sessions") or
        s_tbl.startswith("attendance_ingest") or s_tbl.startswith("log_") or s_tbl.startswith("audit_") or
        s_tbl.startswith("bot_") or s_tbl.startswith("alert_")
    )
    if is_telemetry:
        telemetry_or_backup.add((s_full, r["source_column"], t_full, r["target_column"]))

print(f"Low confidence from telemetry/backup/alerts: {len(telemetry_or_backup)}")
print(f"Remaining low confidence (empty business tables): {len(low_84) - len(telemetry_or_backup)}")
