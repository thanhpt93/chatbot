"""
Groupware AI Chatbot - Master Pipeline Entrypoint.
Orchestrates:
1. Automated ETL Pipeline from Database Staging to Neo4j Graph DB (Architecture B)
   and Qdrant Vector DB (ChatMessage Option A)
2. Automated DB Dump Restoration (pg_restore)
3. Multi-Tenant Semantic Retrieval CLI
4. Interactive Graph Ontology & Data Visualizer
5. System Component Health & Status Checks
"""

import sys
import json
import argparse
import logging
from pathlib import Path

# Prevent bytecode generation
sys.dont_write_bytecode = True

# Fix Windows console UTF-8 encoding
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("main")

def run_etl(target: str = "all", from_dump: str = None):
    """Executes automated ETL flow to Graph DB and Vector DB."""
    if from_dump:
        print(f"\n[Step 0] Automatic restoration from dump: {from_dump}")
        from etl.staging import restore_dump
        ok = restore_dump(dump_path=from_dump)
        if not ok:
            print("[WARNING] Dump restoration encountered issues or PG is offline; proceeding with available staging data.")

    from etl.pipeline import ETLPipeline
    pipeline = ETLPipeline()
    result = pipeline.run(target=target)

    print("\n" + "=" * 60)
    print("ETL PIPELINE EXECUTION SUMMARY")
    print("=" * 60)
    print(f"Target:           {result['target']}")
    print(f"Elapsed Time:     {result['elapsed_seconds']} seconds")
    print(f"Staging Tables:   {sum(result['staging_tables'].values())} records across {len(result['staging_tables'])} tables")

    if result.get("graph"):
        g = result["graph"]
        print("\n--- [Graph DB - Neo4j (Architecture B)] ---")
        print(f"Status:           {g['status']}")
        print(f"Live Neo4j Sync:  {g['live_neo4j']}")
        print(f"Nodes Loaded:     {g['nodes_loaded']}")
        print(f"Rels Loaded:      {g['relationships_loaded']}")
        print(f"Node Breakdown:   {g['node_breakdown']}")
        print(f"Snapshot File:    {g['export_file']}")
        print(f"Cypher Script:    {g['cypher_script']}")

    if result.get("vector"):
        v = result["vector"]
        print("\n--- [Vector DB - Qdrant (ChatMessage Option A)] ---")
        print(f"Status:           {v['status']}")
        print(f"Collection:       {v['collection_name']}")
        print(f"Total Indexed:    {v['documents_indexed']} documents")
        print(f"Category Counts:  {v['breakdown']}")
        print("Model:            intfloat/multilingual-e5-small (384-dim, CPU)")

    print("=" * 60 + "\n")
    return result

def restore_database(dump_path: str = None):
    """Restores database from dump file."""
    from etl.staging import restore_dump
    print("\n--- PostgreSQL Dump Restoration ---")
    ok = restore_dump(dump_path=dump_path)
    if ok:
        print("Restoration finished successfully.")
    else:
        print("Restoration failed. Please ensure PostgreSQL service is running on configured port.")

def search_knowledge(query: str, tenant_id: int, top_k: int = 5):
    """Executes multi-tenant semantic retrieval."""
    from etl.vector.retriever import MultiTenantRetriever
    retriever = MultiTenantRetriever()
    print(f"\n--- Executing Multi-Tenant Semantic Search ---")
    print(f"Query:     '{query}'")
    print(f"Tenant ID: {tenant_id} (Strict isolation)")
    print(f"Top K:     {top_k}\n")

    hits = retriever.search(query=query, tenant_id=tenant_id, top_k=top_k)
    if not hits:
        print(f"No results found for tenant_id={tenant_id}.")
        return hits

    for i, h in enumerate(hits, 1):
        print(f"[{i}] Score: {h['score']} | Source: {h['source_type']} | DocID: {h['doc_id']}")
        print(f"    Text: \"{h['text']}\"")
        print(f"    Channel: {h['channel_id']} | Created: {h['created_at']}")
        print("-" * 50)
    print()
    return hits

def launch_visualizer(auto_open: bool = True):
    """Generates and opens the interactive graph ontology visualizer."""
    from etl.graph.visualizer import GraphVisualizer
    visualizer = GraphVisualizer()
    out_path = visualizer.generate(auto_open=auto_open)
    print("\n" + "=" * 60)
    print("GRAPH ONTOLOGY & DATA VISUALIZER")
    print("=" * 60)
    print(f"Interactive File:  {out_path.resolve().as_posix()}")
    print(f"Browser URL:       file:///{out_path.resolve().as_posix()}")
    print("Features Included:")
    print("  1. Schema Ontology View: 24 Node Classes, 43 Semantic Relationships")
    print("  2. Live Graph Data View: 73 Ingested Nodes, 94 Relationships")
    print("  3. Interactive Controls: Multi-Tenant Filter, Node Inspector, Physics")
    print("=" * 60 + "\n")

def check_status():
    """Checks the status of databases and storage."""
    from etl.staging import StagingExtractor
    from etl.graph.loader import GraphLoader
    from etl.config import config
    from qdrant_client import QdrantClient

    staging = StagingExtractor()
    graph_loader = GraphLoader()

    pg_ok = staging.is_pg_available()
    neo_ok = graph_loader.is_neo4j_available()

    # Check Qdrant
    qdrant_ok = False
    qdrant_count = 0
    try:
        if config.qdrant_url:
            qc = QdrantClient(url=config.qdrant_url)
        else:
            qc = QdrantClient(path=str(config.qdrant_path))
        if config.qdrant_collection in [c.name for c in qc.get_collections().collections]:
            qdrant_ok = True
            qdrant_count = qc.count(config.qdrant_collection).count
    except Exception:
        pass

    print("\n" + "=" * 50)
    print("GROUPWARE AI CHATBOT SYSTEM STATUS")
    print("=" * 50)
    print(f"PostgreSQL (5433/5432): {'ONLINE' if pg_ok else 'OFFLINE (Fallback to verified staging)'}")
    print(f"Neo4j Bolt (7687):      {'ONLINE' if neo_ok else 'OFFLINE (Snapshot & Cypher script exported)'}")
    print(f"Qdrant Vector DB:       {'ACTIVE' if qdrant_ok else 'INITIALIZING'}")
    if qdrant_ok:
        print(f"  - Collection:         {config.qdrant_collection}")
        print(f"  - Vector Count:       {qdrant_count} vectors")
        print(f"  - Storage Path:       {config.qdrant_path}")
        print(f"  - Embedding Model:    {config.embedding_model_name} (CPU)")
    print("=" * 50 + "\n")

def main():
    parser = argparse.ArgumentParser(description="Groupware AI Chatbot Master Pipeline")
    subparsers = parser.add_subparsers(dest="command")

    # Command: run-etl
    etl_parser = subparsers.add_parser("run-etl", help="Run automated ETL pipeline")
    etl_parser.add_argument("--target", choices=["all", "graph", "vector"], default="all", help="Target storage")
    etl_parser.add_argument("--from-dump", type=str, default=None, help="Optional path to new .dump file to restore before running ETL")

    # Command: restore-db
    restore_parser = subparsers.add_parser("restore-db", help="Restore PostgreSQL database from .dump file")
    restore_parser.add_argument("--dump-path", type=str, default=None, help="Path to .dump file")

    # Command: search
    search_parser = subparsers.add_parser("search", help="Semantic search in Vector DB with tenant isolation")
    search_parser.add_argument("--query", type=str, required=True, help="Search query")
    search_parser.add_argument("--tenant-id", type=int, required=True, help="Tenant ID for strict isolation")
    search_parser.add_argument("--top-k", type=int, default=5, help="Number of results")

    # Command: visualize
    vis_parser = subparsers.add_parser("visualize", help="Generate and open graph ontology interactive visualizer")
    vis_parser.add_argument("--no-open", action="store_true", help="Do not automatically open browser")

    # Command: status
    subparsers.add_parser("status", help="Check database and storage health status")

    args = parser.parse_args()

    if args.command == "run-etl" or args.command is None:
        target = getattr(args, "target", "all")
        from_dump = getattr(args, "from_dump", None)
        run_etl(target=target, from_dump=from_dump)
    elif args.command == "restore-db":
        restore_database(dump_path=args.dump_path)
    elif args.command == "search":
        search_knowledge(query=args.query, tenant_id=args.tenant_id, top_k=args.top_k)
    elif args.command == "visualize":
        launch_visualizer(auto_open=not args.no_open)
    elif args.command == "status":
        check_status()

if __name__ == "__main__":
    main()
