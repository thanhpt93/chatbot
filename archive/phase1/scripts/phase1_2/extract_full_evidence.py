# -*- coding: utf-8 -*-
"""Phase 1.2 - Extract complete profiling metrics from artifacts/database-discovery/
and run any supplementary read-only SQL checks if PostgreSQL is reachable.
"""
import json, os, subprocess, time
import psycopg2

INV_PATH = r"artifacts\database-discovery\schema_inventory.json"
PROF_PATH = r"artifacts\database-discovery\data_profiling.json"
REL_PATH = r"artifacts\database-discovery\relationships.json"
INV_RES_PATH = r"artifacts\database-discovery\investigation_results.json"

inv = json.load(open(INV_PATH, encoding="utf-8"))
prof = json.load(open(PROF_PATH, encoding="utf-8"))
rels = json.load(open(REL_PATH, encoding="utf-8"))
inv_res = json.load(open(INV_RES_PATH, encoding="utf-8"))

tables = {(t["schema_name"], t["table_name"]): t for t in inv["tables"]}
inferred = {(r["source_schema"], r["source_table"], r["source_column"], r["target_table"]): r for r in rels["inferred_relationships"]}

summary = {
    "database_version": inv.get("database_version"),
    "tables_summary": {},
    "relationships_summary": {},
    "live_sql_queries": {}
}

# Try quick read-only Postgres connection if possible
PG_EXE = r"C:\Users\admin\miniconda3\envs\chat\Library\bin\postgres.exe"
PGDATA = os.path.abspath(".pgdata")
proc = None
conn = None
try:
    conn = psycopg2.connect(host="127.0.0.1", port=5433, dbname="inf_nffice", user="postgres", connect_timeout=2)
except Exception:
    pid = os.path.join(PGDATA, "postmaster.pid")
    if os.path.exists(pid):
        try:
            os.remove(pid)
        except OSError:
            pass
    try:
        proc = subprocess.Popen([PG_EXE, "-D", PGDATA, "-p", "5433"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for _ in range(15):
            time.sleep(0.5)
            try:
                conn = psycopg2.connect(host="127.0.0.1", port=5433, dbname="inf_nffice", user="postgres", connect_timeout=2)
                break
            except Exception:
                pass
    except Exception as e:
        summary["pg_start_error"] = str(e)

if conn:
    conn.set_session(readonly=True, autocommit=True)
    cur = conn.cursor()
    from profile_graph_sources import Q, _jsonable
    cur.execute("SHOW transaction_read_only")
    summary["transaction_read_only"] = cur.fetchone()[0]
    for k, sql in Q.items():
        try:
            cur.execute(sql)
            summary["live_sql_queries"][k] = [[_jsonable(v) for v in r] for r in cur.fetchall()]
        except Exception as e:
            summary["live_sql_queries"][k] = f"ERROR: {e}"
    conn.close()

if proc:
    proc.terminate()
    try:
        proc.wait(timeout=3)
    except Exception:
        proc.kill()

os.makedirs(r"artifacts\phase1_2", exist_ok=True)
with open(r"artifacts\phase1_2\data_profile.json", "w", encoding="utf-8") as f:
    json.dump(summary, f, indent=2, ensure_ascii=False)

lines = [f"Database Version: {summary['database_version']}",
         f"Read-Only Mode: {summary.get('transaction_read_only', 'N/A')}",
         f"Live SQL Queries Executed: {len(summary['live_sql_queries'])}"]
for k, v in summary["live_sql_queries"].items():
    lines.append(f"{k}: {v}")
with open(r"artifacts\phase1_2\data_profile.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")
