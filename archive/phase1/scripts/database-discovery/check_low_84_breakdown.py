import json

with open("artifacts/database-discovery/relationships.json", "r", encoding="utf-8") as f:
    rels = json.load(f)

with open("artifacts/database-discovery/schema_inventory.json", "r", encoding="utf-8") as f:
    inv = json.load(f)

tbl_meta = {f"{t['schema_name']}.{t['table_name']}": t for t in inv["tables"]}

# Tables classified as Operational/Telemetry/Infrastructure/Backup
telemetry_or_excluded = {
    # Hangfire
    "hangfire.job", "hangfire.jobparameter", "hangfire.jobqueue", "hangfire.list",
    "hangfire.lock", "hangfire.schema", "hangfire.server", "hangfire.set",
    "hangfire.state", "hangfire.aggregatedcounter", "hangfire.counter", "hangfire.hash",
    # Telemetry
    "public.system_logs", "public.error_tracking_outbox", "public.attendance_ingest_events",
    "public.attendance_ingest_event_backups", "public.mail_send_logs", "public.chat_audit_log",
    "public.attendance_face_events", "public.user_sessions", "public.bot_messages",
    "public.bot_requests", "public.bot_threads", "public.push_notification_logs",
    "public.device_tokens", "public.performance_metrics", "public.health_checks",
    "public.sync_logs", "public.system_events", "public.notifications",
    "public.notification_recipients", "public.project_activity_logs", "public.approval_activity_logs",
    "public.schema_migrations", "public.license_audit_events", "public.license_runtime_states",
    "public.login_qr_challenges", "public.server_resource_nodes", "public.notification_device_registrations",
    # Alert telemetry
    "public.alert_acknowledgements", "public.alert_action_outbox", "public.alert_events",
    "public.alert_routes", "public.alert_sources", "public.alert_webhook_receipts"
}

low_84 = [r for r in rels["inferred_relationships"] if r["source_distinct_count"] == 0]

defer_count = 0
exclude_count = 0

for r in low_84:
    s_full = f"{r['source_schema']}.{r['source_table']}"
    t_full = f"{r['target_schema']}.{r['target_table']}"
    
    is_excl = (
        r["source_schema"] in ("_backup_cleanup_20261005", "maintenance_backup") or
        r["target_schema"] in ("_backup_cleanup_20261005", "maintenance_backup") or
        s_full in telemetry_or_excluded or t_full in telemetry_or_excluded
    )
    if is_excl:
        exclude_count += 1
    else:
        defer_count += 1

print(f"Total Low Confidence: {len(low_84)}")
print(f"  - DEFER (Business Schema-Only Candidate): {defer_count}")
print(f"  - EXCLUDE (Telemetry/Backup Schema-Only Candidate): {exclude_count}")
print(f"Sum: {defer_count + exclude_count}")
