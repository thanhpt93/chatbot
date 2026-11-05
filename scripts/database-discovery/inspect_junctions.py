import json

with open("artifacts/database-discovery/relationships.json", "r", encoding="utf-8") as f:
    rels = json.load(f)

for i, j in enumerate(rels['junction_tables']):
    print(f"{i+1:2d}. {j['table_name']:<35} (rows: {j['row_count']:<6}) -> {j['connected_entities']}")
