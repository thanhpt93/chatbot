import os
import json

DOC_DIR = r"documentation\phase-1-database-discovery"
os.makedirs(DOC_DIR, exist_ok=True)

with open(r"artifacts\database-discovery\schema_inventory.json", "r", encoding="utf-8") as f:
    inv = json.load(f)

with open(r"artifacts\database-discovery\data_profiling.json", "r", encoding="utf-8") as f:
    prof = json.load(f)

with open(r"artifacts\database-discovery\relationships.json", "r", encoding="utf-8") as f:
    rels = json.load(f)

base_tables = [t for t in inv["tables"] if t["table_type"] == "BASE TABLE"]
total_db_rows = sum(t["row_count"] for t in base_tables)
print(f"Base tables: {len(base_tables)}, Total physical rows: {total_db_rows}")
