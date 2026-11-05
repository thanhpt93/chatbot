import json

with open("artifacts/database-discovery/schema_inventory.json", "r", encoding="utf-8") as f:
    inv = json.load(f)

with open("artifacts/database-discovery/relationships.json", "r", encoding="utf-8") as f:
    rels = json.load(f)

inferred_set = set()
for r in rels["inferred_relationships"]:
    inferred_set.add((r["source_schema"], r["source_table"], r["source_column"]))

explicit_set = set()
for r in rels["explicit_relationships"]:
    explicit_set.add((r["source_schema"], r["source_table"], r["source_column"]))

all_known = inferred_set | explicit_set

missing_candidates = []
for t in inv["tables"]:
    s = t["schema_name"]
    tbl = t["table_name"]
    for c in t["columns"]:
        col = c["column_name"]
        if (s, tbl, col) not in all_known:
            if col.endswith("_user_id") or col.endswith("_id") or col in ("created_by", "updated_by", "deleted_by", "manager_id", "author_id", "sender_id"):
                if not col.startswith("is_") and col != "id":
                    missing_candidates.append((s, tbl, col, c["data_type"], t["row_count"]))

print(f"Total potential relationship columns not in relationships.json: {len(missing_candidates)}")
print("\nSample missing candidates in public schema:")
for s, tbl, col, dt, rows in missing_candidates:
    if s == "public" and rows > 0:
        print(f"  {tbl}.{col} ({dt}, rows={rows})")
