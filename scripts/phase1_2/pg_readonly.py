# -*- coding: utf-8 -*-
"""Phase 1.2 - Local PostgreSQL lifecycle helper (validation copy of the restored dump).

Starts the local restored cluster (.pgdata, port 5433) on demand using postgres.exe,
yields a READ-ONLY psycopg2 connection, and stops the cluster afterwards. Never writes to the database.
"""
import contextlib, os, subprocess, time
import psycopg2

PG_BIN = r"C:\Users\admin\miniconda3\envs\chat\Library\bin"
PGDATA = os.path.abspath(".pgdata")
LOG = os.path.abspath(r"artifacts\phase1_2\pg_runtime.log")
DSN = dict(host="127.0.0.1", port=5433, dbname="inf_nffice", user="postgres", connect_timeout=5)


def _try_connect():
    try:
        c = psycopg2.connect(**DSN)
        return c
    except Exception:
        return None


@contextlib.contextmanager
def readonly_connection(manage_server=True):
    proc = None
    conn = _try_connect()
    if conn is None and manage_server:
        pid = os.path.join(PGDATA, "postmaster.pid")
        if os.path.exists(pid):  # stale pid from a killed process
            try:
                os.remove(pid)
            except OSError:
                pass
        os.makedirs(os.path.dirname(LOG), exist_ok=True)
        proc = subprocess.Popen(
            [os.path.join(PG_BIN, "postgres.exe"), "-D", PGDATA, "-p", "5433"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        for _ in range(30):
            conn = _try_connect()
            if conn:
                break
            time.sleep(1)
    if conn is None:
        if proc:
            proc.terminate()
        raise RuntimeError("PostgreSQL validation copy is not reachable on 127.0.0.1:5433")
    conn.set_session(readonly=True, autocommit=True)
    try:
        yield conn
    finally:
        conn.close()
        if proc:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except Exception:
                proc.kill()
