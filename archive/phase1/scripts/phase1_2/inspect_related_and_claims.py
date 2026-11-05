# -*- coding: utf-8 -*-
"""Phase 1.2 - Read-only inspection of related tables and verification of earlier
Phase 1.1 claims against the extracted catalog snapshot."""
import json, re

inv = json.load(open(r"artifacts\database-discovery\schema_inventory.json", encoding="utf-8"))
T = {t["table_name"]: t for t in inv["tables"] if t["schema_name"] == "public"}
ALL = {(t["schema_name"], t["table_name"]): t for t in inv["tables"]}

def show(n):
    t = T.get(n)
    if not t:
        print("MISSING", n); return
    print(f"## {n} rows={t['row_count']} pk={t['primary_key']}")
    print("  cols:", ", ".join(c["column_name"] + ":" + c["udt_name"] + ("" if c["is_nullable"] else "!") for c in t["columns"]))
    for i in t["indexes"]:
        if "UNIQUE" in i["indexdef"]:
            print("  UQ:", re.sub(r"CREATE UNIQUE INDEX (\S+) ON public\.\S+ USING btree", r"\1", i["indexdef"]))

for n in ["approval_workflow_steps", "audience_user_members", "audience_department_members", "talk_post_tags",
          "talk_tags", "asset_assignments", "tenant_domains", "user_department_data_scopes",
          "user_leave_year_balances", "leave_catalogs", "chat_messages", "chat_threads", "chat_thread_participants"]:
    show(n)

print("\n=== CLAIM CHECKS ===")
print("telemetry_events exists:", ("public", "telemetry_events") in ALL)
for n in ["system_logs", "error_tracking_outbox", "attendance_face_events", "chat_audit_log"]:
    t = T.get(n); print(f"{n}: rows={t['row_count'] if t else 'MISSING'}")
sal = [f"{s}.{tn}.{c['column_name']}" for (s, tn), t in ALL.items() for c in t["columns"]
       if re.search(r"salary|bonus|allowance|bank_account|compensation", c["column_name"])]
print("compensation-like columns anywhere:", sal or "NONE")
no_pk = sorted(f"{s}.{tn}" for (s, tn), t in ALL.items() if t["table_type"] == "BASE TABLE" and not t["primary_key"])
print(f"base tables without PK ({len(no_pk)}):", no_pk)
fks = [(f"{s}.{tn}", t["foreign_keys"]) for (s, tn), t in ALL.items() if t["foreign_keys"]]
print("explicit FKs:", fks)
print("DB version:", inv.get("database_version"))
print("triggers:", len(inv.get("triggers", [])), "routines:", len(inv.get("routines", [])))
for r in inv.get("routines", [])[:60]:
    print("  routine:", r.get("routine_name") if isinstance(r, dict) else r)
pii = [f"{tn}.{c['column_name']}" for tn, t in T.items() for c in t["columns"]
       if re.search(r"password|token|secret|tax_code|birth_date|mobile_phone|address|face|biometric|national_id|passport", c["column_name"])]
print("PII/secret-like columns in public:", pii)
