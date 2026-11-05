import json

def analyze():
    with open(r"artifacts\database-discovery\schema_inventory.json", "r", encoding="utf-8") as f:
        inv = json.load(f)
    with open(r"artifacts\database-discovery\data_profiling.json", "r", encoding="utf-8") as f:
        prof = json.load(f)
    with open(r"artifacts\database-discovery\relationships.json", "r", encoding="utf-8") as f:
        rels = json.load(f)

    public_tables = [t for t in inv["tables"] if t["schema_name"] == "public" and t["table_type"] == "BASE TABLE"]
    public_tables.sort(key=lambda x: x["row_count"], reverse=True)

    print(f"Total Base Tables in public: {len(public_tables)}")
    print("\nTop 30 Tables by Row Count:")
    for t in public_tables[:30]:
        print(f"  - {t['table_name']}: {t['row_count']:,} rows")

    # Table names grouped by domain keywords
    domains = {
        "User & Identity": ["user", "tenant", "login", "role", "permission", "menu", "action", "bot"],
        "Organization & HR": ["department", "organization", "job_", "position", "audience", "workforce", "contract"],
        "Attendance & Leave": ["attendance", "leave", "holiday", "work_calendar"],
        "Project & Task Management": ["project", "ticket", "kanban", "sprint"],
        "Approval & Workflow": ["approval", "regulation", "rule"],
        "Communication & Social": ["chat", "talk", "notice", "notification", "mail", "comment"],
        "Asset Management": ["asset"],
        "Schedule & Resource": ["schedule", "room"],
        "System, Logging & Utilities": ["file", "system", "export", "error", "alert", "license", "schema_migrations", "server_resource"]
    }

    categorized = {}
    uncategorized = []

    for t in public_tables:
        name = t["table_name"]
        assigned = False
        for dom, keywords in domains.items():
            if any(k in name for k in keywords):
                categorized.setdefault(dom, []).append(t)
                assigned = True
                break
        if not assigned:
            uncategorized.append(t)

    print("\nDomain Classification Summary:")
    for dom, tbls in categorized.items():
        total_rows = sum(t["row_count"] for t in tbls)
        print(f"\n[{dom}] - {len(tbls)} tables, {total_rows:,} total rows:")
        for t in tbls:
            print(f"    * {t['table_name']} ({t['row_count']:,} rows)")

    if uncategorized:
        print(f"\n[Uncategorized] - {len(uncategorized)} tables:")
        for t in uncategorized:
            print(f"    * {t['table_name']} ({t['row_count']:,} rows)")

if __name__ == "__main__":
    analyze()
