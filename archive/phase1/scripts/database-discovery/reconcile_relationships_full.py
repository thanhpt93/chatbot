import json

with open("artifacts/database-discovery/relationships.json", "r", encoding="utf-8") as f:
    rels = json.load(f)

with open("artifacts/database-discovery/schema_inventory.json", "r", encoding="utf-8") as f:
    inv = json.load(f)

with open("artifacts/database-discovery/data_profiling.json", "r", encoding="utf-8") as f:
    prof = json.load(f)

explicit = rels["explicit_relationships"]
inferred = rels["inferred_relationships"]

print(f"Explicit FKs: {len(explicit)}")
print(f"Inferred candidates in JSON: {len(inferred)}")

# Table classifications
# Telemetry tables:
telemetry_tables = {
    "system_logs", "error_tracking_outbox", "attendance_ingest_events", "attendance_ingest_event_backups",
    "mail_send_logs", "chat_audit_log", "attendance_face_events", "user_sessions",
    "bot_messages", "bot_requests", "bot_threads", "push_notification_logs",
    "device_tokens", "performance_metrics", "health_checks", "sync_logs",
    "system_events", "notifications", "notification_recipients", "project_activity_logs",
    "approval_activity_logs", "schema_migrations", "license_audit_events", "license_runtime_states",
    "login_qr_challenges", "server_resource_nodes", "notification_device_registrations"
}

# Low confidence: src_dist == 0
low_rels = [r for r in inferred if r["source_distinct_count"] == 0]
print(f"Low confidence (src_dist == 0): {len(low_rels)}")

# Let's inspect each of the 84 low rels
low_telemetry = []
low_business = []
for r in low_rels:
    s_schema = r["source_schema"]
    s_tbl = r["source_table"]
    t_schema = r["target_schema"]
    t_tbl = r["target_table"]
    
    is_telemetry = (
        s_schema in ("_backup_cleanup_20261005", "maintenance_backup", "hangfire") or
        t_schema in ("_backup_cleanup_20261005", "maintenance_backup", "hangfire") or
        s_tbl in telemetry_tables or t_tbl in telemetry_tables or
        s_tbl.startswith("log_") or s_tbl.startswith("audit_") or s_tbl.startswith("attendance_ingest")
    )
    if is_telemetry:
        low_telemetry.append(r)
    else:
        low_business.append(r)

print(f"Low confidence - Telemetry/Backup: {len(low_telemetry)}")
print(f"Low confidence - Business (Empty tables): {len(low_business)}")

# Non-low rels
non_low = [r for r in inferred if r["source_distinct_count"] > 0]
print(f"Non-low rels: {len(non_low)}")

match_100 = [r for r in non_low if r["match_rate"] == 100.0]
partial_match = [r for r in non_low if 0.0 < r["match_rate"] < 100.0]
zero_match = [r for r in non_low if r["match_rate"] == 0.0]

print(f"100% Match: {len(match_100)}")
print(f"Partial Match (16.95% - 99.19%): {len(partial_match)}")
print(f"0% Match: {len(zero_match)}")

# Check chat child tables in non_low
chat_child_tables = {
    "chat_message_attachments", "chat_message_mentions", "chat_message_reactions",
    "chat_message_links", "chat_message_polls", "chat_message_poll_options",
    "chat_message_poll_votes", "chat_message_hidden_for_users", "chat_shared_links"
}
chat_child_rels = [r for r in non_low if r["source_table"] in chat_child_tables or r["target_table"] in chat_child_tables]
print(f"Chat child rels in non_low: {len(chat_child_rels)}")
for r in chat_child_rels:
    print(f"  {r['source_table']}.{r['source_column']} -> {r['target_table']}.{r['target_column']} (match={r['match_rate']}%, src_dist={r['source_distinct_count']})")
