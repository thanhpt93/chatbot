import json

with open("artifacts/database-discovery/relationships.json", "r", encoding="utf-8") as f:
    rels = json.load(f)

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

chat_child_tables = {
    "chat_message_attachments", "chat_message_mentions", "chat_message_reactions",
    "chat_message_links", "chat_message_polls", "chat_message_poll_options",
    "chat_message_poll_votes", "chat_message_hidden_for_users", "chat_shared_links"
}

non_low = [r for r in rels["inferred_relationships"] if r["source_distinct_count"] > 0]
print(f"Total non-low: {len(non_low)}")

decisions = {}
for r in non_low:
    s_full = f"{r['source_schema']}.{r['source_table']}"
    t_full = f"{r['target_schema']}.{r['target_table']}"
    src_t = r["source_table"]
    tgt_t = r["target_table"]
    rate = r["match_rate"]
    
    if rate == 0.0:
        dec = "DO NOT MODEL"
        reason = "0% match rate; invalid or legacy identifier."
    elif s_full in telemetry_or_excluded or t_full in telemetry_or_excluded or r["source_schema"] in ("_backup_cleanup_20261005", "maintenance_backup"):
        dec = "EXCLUDE"
        reason = f"Excluded because {s_full if s_full in telemetry_or_excluded else t_full} is excluded from Graph."
    elif src_t in chat_child_tables and tgt_t == "chat_messages":
        dec = "EXCLUDE (VECTOR RAG METADATA / OPTION A)"
        reason = "Option A selected: no ChatMessage nodes in Neo4j. Message metadata and attachments handled in Vector DB."
    elif src_t == "chat_messages":
        dec = "EXCLUDE (VECTOR RAG METADATA / OPTION A)"
        reason = "Option A selected: no ChatMessage nodes in Neo4j. User/channel IDs stored as vector chunk metadata."
    elif rate < 100.0:
        dec = "INCLUDE (OPTIONAL MATCH)"
        reason = f"Valid business semantics ({rate:.1f}% match); unmapped target IDs exist in _backup_cleanup_20261005."
    else:
        dec = "INCLUDE"
        reason = "Both source and target tables are included in Graph; 100% active data match."
        
    decisions[f"{s_full}.{r['source_column']} -> {t_full}.{r['target_column']}"] = (dec, reason)

from collections import Counter
counts = Counter(d[0] for d in decisions.values())
print("\nNon-low decisions breakdown:")
for k, v in counts.items():
    print(f"  {k}: {v}")
print(f"Total non-low classified: {sum(counts.values())}")
