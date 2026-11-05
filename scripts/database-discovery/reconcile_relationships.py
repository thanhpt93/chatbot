import json

with open("artifacts/database-discovery/relationships.json", "r", encoding="utf-8") as f:
    rels = json.load(f)

inferred = rels["inferred_relationships"]
print(f"Total inferred relationships: {len(inferred)}")

categories = {
    "100% Match with Data": [],
    "Partial Match (Broken/Orphan Data)": [],
    "0% Match (Data present, 0 matched)": [],
    "Empty Table / All NULL Column": []
}

for r in inferred:
    src_dist = r["source_distinct_count"]
    match_rate = r["match_rate"]
    if src_dist == 0:
        categories["Empty Table / All NULL Column"].append(r)
    elif match_rate == 100.0:
        categories["100% Match with Data"].append(r)
    elif match_rate == 0.0:
        categories["0% Match (Data present, 0 matched)"].append(r)
    else:
        categories["Partial Match (Broken/Orphan Data)"].append(r)

print("\nReconciliation Breakdown:")
for cat, lst in categories.items():
    print(f"  - {cat}: {len(lst)}")

print(f"Total: {sum(len(lst) for lst in categories.values())}")
