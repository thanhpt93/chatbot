import os
import json

DOC_DIR = r"documentation\phase-1-database-discovery"
os.makedirs(DOC_DIR, exist_ok=True)

# 1. Load Data
with open(r"artifacts\database-discovery\schema_inventory.json", "r", encoding="utf-8") as f:
    inv = json.load(f)

with open(r"artifacts\database-discovery\data_profiling.json", "r", encoding="utf-8") as f:
    prof = json.load(f)

with open(r"artifacts\database-discovery\relationships.json", "r", encoding="utf-8") as f:
    rels = json.load(f)

explicit_rels = rels["explicit_relationships"]
inferred_rels = rels["inferred_relationships"]
base_tables = [t for t in inv["tables"] if t["table_type"] == "BASE TABLE"]

# Map table columns
table_col_types = {}
table_row_counts = {}
for t in inv["tables"]:
    full_name = f"{t['schema_name']}.{t['table_name']}"
    table_col_types[full_name] = {c["column_name"]: c["data_type"] for c in t["columns"]}
    table_row_counts[full_name] = t["row_count"]

print(f"Base tables: {len(base_tables)}, Explicit rels: {len(explicit_rels)}, Inferred rels: {len(inferred_rels)}")

def get_null_count(schema, table, column):
    full_name = f"{schema}.{table}"
    if full_name in prof and column in prof[full_name]["columns"]:
        return prof[full_name]["columns"][column]["null_count"]
    return 0

def get_col_type(schema, table, column):
    full_name = f"{schema}.{table}"
    if full_name in table_col_types and column in table_col_types[full_name]:
        return table_col_types[full_name][column]
    return "unknown"

print("Setup complete.")
