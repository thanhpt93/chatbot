import json

def analyze_quality():
    with open(r"artifacts\database-discovery\schema_inventory.json", "r", encoding="utf-8") as f:
        inv = json.load(f)
    with open(r"artifacts\database-discovery\data_profiling.json", "r", encoding="utf-8") as f:
        prof = json.load(f)
    with open(r"artifacts\database-discovery\relationships.json", "r", encoding="utf-8") as f:
        rels = json.load(f)

    print("Analyzing Data Quality & Profiling Details...")

    # 1. Primary Identifier types
    pk_types = {}
    missing_pk_tables = []
    composite_pk_tables = []

    for t in inv["tables"]:
        if t["schema_name"] != "public":
            continue
        t_name = t["table_name"]
        pks = t["primary_key"]
        if not pks:
            missing_pk_tables.append(t_name)
        elif len(pks) > 1:
            composite_pk_tables.append((t_name, pks))
        else:
            pk_col = pks[0]
            col_def = next((c for c in t["columns"] if c["column_name"] == pk_col), None)
            if col_def:
                pk_types[col_def["data_type"]] = pk_types.get(col_def["data_type"], 0) + 1

    print(f"\nPrimary Key Types in public: {pk_types}")
    print(f"Tables missing Primary Key ({len(missing_pk_tables)}): {missing_pk_tables}")
    print(f"Tables with Composite Primary Key ({len(composite_pk_tables)}): {composite_pk_tables}")

    # 2. Inferred Relationships Match Rates & Broken References
    broken_inferred = []
    for r in rels["inferred_relationships"]:
        if r["source_distinct_count"] > 0 and r["match_rate"] < 100.0:
            broken_inferred.append(r)

    print(f"\nInferred Relationships with Broken/Orphan References ({len(broken_inferred)}):")
    for r in broken_inferred:
        src = f"{r['source_table']}.{r['source_column']}"
        tgt = f"{r['target_table']}.{r['target_column']}"
        missing_cnt = r['source_distinct_count'] - r['matched_distinct_count']
        print(f"  - {src} -> {tgt}: {r['match_rate']}% match ({missing_cnt} unmatched distinct values out of {r['source_distinct_count']})")

    # 3. Soft deletion analysis
    soft_delete_patterns = {
        "deleted_at": [],
        "is_deleted": [],
        "status_deleted": []
    }
    for t in inv["tables"]:
        if t["schema_name"] != "public":
            continue
        cols = [c["column_name"] for c in t["columns"]]
        if "deleted_at" in cols:
            soft_delete_patterns["deleted_at"].append(t["table_name"])
        if "is_deleted" in cols:
            soft_delete_patterns["is_deleted"].append(t["table_name"])

    print(f"\nSoft Deletion Adoption:")
    print(f"  - Tables with deleted_at ({len(soft_delete_patterns['deleted_at'])} tables)")
    print(f"  - Tables with is_deleted ({len(soft_delete_patterns['is_deleted'])} tables)")

    # 4. Status Distributions across major entities
    major_entities = ["public.users", "public.departments", "public.projects", "public.tickets", "public.approval_requests", "public.assets", "public.schedule_events"]
    print("\nStatus & Lifecycle Values in Major Entities:")
    for ent in major_entities:
        if ent in prof:
            dist = prof[ent].get("status_distributions", {})
            print(f"  [{ent}] (Rows: {prof[ent]['row_count']}):")
            for field, vals in dist.items():
                print(f"    * {field}: {vals}")

if __name__ == "__main__":
    analyze_quality()
