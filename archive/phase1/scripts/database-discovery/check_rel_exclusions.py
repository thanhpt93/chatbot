import json

with open("artifacts/database-discovery/relationships.json", "r", encoding="utf-8") as f:
    rels = json.load(f)

with open("artifacts/database-discovery/schema_inventory.json", "r", encoding="utf-8") as f:
    inv = json.load(f)

# Build a lookup of table decision from 14_data_classification_and_graph_scope
# Let's inspect all tables
telemetry_tables = {
    "system_logs", "error_tracking_outbox", "attendance_ingest_events", "attendance_ingest_event_backups",
    "mail_send_logs", "chat_audit_log", "attendance_face_events", "user_sessions",
    "bot_messages", "bot_requests", "bot_threads", "push_notification_logs",
    "device_tokens", "performance_metrics", "health_checks", "sync_logs",
    "system_events", "notifications", "notification_recipients", "project_activity_logs",
    "approval_activity_logs"
}

table_decisions = {}
for t in inv["tables"]:
    s = t["schema_name"]
    name = t["table_name"]
    rows = t["row_count"]
    
    if s in ("_backup_cleanup_20261005", "maintenance_backup"):
        table_decisions[f"{s}.{name}"] = "EXCLUDE (Backup/Archive)"
    elif s == "hangfire":
        table_decisions[f"{s}.{name}"] = "EXCLUDE (Hangfire Infrastructure)"
    elif name in telemetry_tables or name.startswith("log_") or name.startswith("audit_") or name.startswith("attendance_ingest"):
        table_decisions[f"{s}.{name}"] = "EXCLUDE (Operational Telemetry)"
    elif rows == 0:
        table_decisions[f"{s}.{name}"] = "DEFER (Empty Table)"
    elif name == "chat_messages":
        table_decisions[f"{s}.{name}"] = "VECTOR RAG ONLY"
    else:
        table_decisions[f"{s}.{name}"] = "INCLUDE"

print(f"Total tables mapped: {len(table_decisions)}")

# Check each inferred relationship
rel_graph_decisions = {}
for r in rels["inferred_relationships"]:
    s_full = f"{r['source_schema']}.{r['source_table']}"
    t_full = f"{r['target_schema']}.{r['target_table']}"
    src_dec = table_decisions.get(s_full, "UNKNOWN")
    tgt_dec = table_decisions.get(t_full, "UNKNOWN")
    
    # Determine Graph Decision
    if "EXCLUDE" in src_dec or "EXCLUDE" in tgt_dec:
        reason = f"Excluded because {s_full if 'EXCLUDE' in src_dec else t_full} is excluded from Graph ({src_dec if 'EXCLUDE' in src_dec else tgt_dec})."
        decision = "EXCLUDE"
    elif "DEFER" in src_dec or "DEFER" in tgt_dec:
        reason = f"Deferred because {s_full if 'DEFER' in src_dec else t_full} currently contains 0 records."
        decision = "DEFER"
    elif r["match_rate"] == 0.0:
        decision = "DO NOT MODEL"
        reason = "0% match rate; invalid or legacy identifier."
    elif r["source_table"] == "chat_messages":
        decision = "VECTOR RAG METADATA"
        reason = "Message text is stored in Vector DB; user/channel IDs serve as vector metadata filtering payload."
    elif r["match_rate"] < 100.0:
        decision = "INCLUDE (OPTIONAL MATCH)"
        reason = f"Valid business semantics ({r['match_rate']:.1f}% match); unmapped target IDs exist in _backup_cleanup_20261005."
    else:
        decision = "INCLUDE"
        reason = "Both source and target tables are included in Graph; 100% active data match."
        
    rel_graph_decisions[f"{s_full}.{r['source_column']} -> {t_full}.{r['target_column']}"] = (decision, reason)

from collections import Counter
counts = Counter(d[0] for d in rel_graph_decisions.values())
print("\nRelationship Graph Decision Breakdown across all 276 inferred rels:")
for dec, cnt in counts.items():
    print(f"  - {dec}: {cnt}")
