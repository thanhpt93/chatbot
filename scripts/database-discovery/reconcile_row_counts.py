import json

with open("artifacts/database-discovery/schema_inventory.json", "r", encoding="utf-8") as f:
    inv = json.load(f)

base_tables = [t for t in inv["tables"] if t["table_type"] == "BASE TABLE"]

# We define 4 major categories as requested by user:
# 1. Core Business Modules (Users, Departments, Projects, Tickets, Approvals, Attendance Daily Records, Calendar, Chat Metadata, Assets, Notices, Posts, File Metadata, Roles/Permissions)
# 2. Operational & Telemetry Data (system_logs, error_tracking_outbox, attendance_ingest_*, mail_send_logs, chat_audit_log, bot_*, etc.)
# 3. Hangfire Scheduler Schema (hangfire.*)
# 4. Maintenance & Backup Schemas (_backup_cleanup_20261005.*, maintenance_backup.*)

categories = {
    "Core Business Modules": [],
    "Operational & Telemetry Data": [],
    "Hangfire Scheduler": [],
    "Maintenance & Backup Schemas": []
}

telemetry_tables = {
    "system_logs", "error_tracking_outbox", "attendance_ingest_events", "attendance_ingest_event_backups",
    "mail_send_logs", "chat_audit_log", "attendance_face_events", "user_sessions",
    "bot_messages", "bot_requests", "bot_threads", "push_notification_logs",
    "device_tokens", "performance_metrics", "health_checks", "sync_logs",
    "system_events", "notifications", "notification_recipients", "project_activity_logs",
    "approval_activity_logs"
}

for t in base_tables:
    s = t["schema_name"]
    name = t["table_name"]
    rows = t["row_count"]
    
    if s == "hangfire":
        categories["Hangfire Scheduler"].append((s, name, rows))
    elif s in ("_backup_cleanup_20261005", "maintenance_backup"):
        categories["Maintenance & Backup Schemas"].append((s, name, rows))
    elif name in telemetry_tables or name.startswith("log_") or name.startswith("audit_") or name.startswith("attendance_ingest"):
        categories["Operational & Telemetry Data"].append((s, name, rows))
    else:
        categories["Core Business Modules"].append((s, name, rows))

total_db_rows = sum(t["row_count"] for t in base_tables)
print(f"Total Base Tables: {len(base_tables)}")
print(f"Total Database Physical Rows: {total_db_rows:,}")
print("\n--- Category Breakdown ---")
cat_sums = {}
for cat_name, tbls in categories.items():
    cat_rows = sum(r for _, _, r in tbls)
    cat_sums[cat_name] = cat_rows
    pct = (cat_rows / total_db_rows) * 100
    print(f"{cat_name}: {cat_rows:,} rows ({pct:.2f}%) across {len(tbls)} tables")

print(f"\nSum of categories: {sum(cat_sums.values()):,}")
assert sum(cat_sums.values()) == total_db_rows, "Category sum does not match total!"
print("Assertion passed: Category sum matches Total Database Physical Rows exactly!")

print("\n--- Schema Breakdown ---")
schemas = {}
for t in base_tables:
    s = t["schema_name"]
    schemas[s] = schemas.get(s, 0) + t["row_count"]
for s, r in schemas.items():
    print(f"Schema `{s}`: {r:,} rows ({(r/total_db_rows)*100:.2f}%)")
print(f"Sum of schemas: {sum(schemas.values()):,}")
assert sum(schemas.values()) == total_db_rows, "Schema sum does not match total!"
print("Assertion passed: Schema sum matches Total Database Physical Rows exactly!")
