"""
Master ETL Pipeline Orchestrator.
Coordinates:
1. Staging Data Extraction
2. Graph Transformation & Loading (Neo4j Architecture B)
3. Vector Embedding & Indexing (Qdrant ChatMessage Option A)
"""

import time
import logging
from typing import Dict, Any
from etl.staging import StagingExtractor
from etl.graph.transformer import GraphTransformer
from etl.graph.loader import GraphLoader
from etl.vector.loader import VectorLoader

logger = logging.getLogger("etl.pipeline")

class ETLPipeline:
    def __init__(self):
        self.staging = StagingExtractor()
        self.graph_transformer = GraphTransformer()
        self.graph_loader = GraphLoader()
        self.vector_loader = VectorLoader()

    def run(self, target: str = "all") -> Dict[str, Any]:
        """
        Runs the ETL pipeline.
        target: 'all' | 'graph' | 'vector'
        """
        start_time = time.time()
        logger.info(f"=== Starting Groupware ETL Pipeline (target={target}) ===")

        # 1. Staging Extraction
        logger.info("[Step 1/3] Extracting staging data...")
        staging_data = self.staging.extract_all()
        table_counts = {k: len(v) for k, v in staging_data.items()}
        logger.info(f"Staging tables extracted: {table_counts}")

        graph_result = None
        vector_result = None

        # 2. Graph Pipeline
        if target in ("all", "graph"):
            logger.info("[Step 2/3] Processing Graph Pipeline (Architecture B)...")
            graph_data = self.graph_transformer.transform(staging_data)
            graph_result = self.graph_loader.load(graph_data)
            logger.info(f"Graph Pipeline completed: {graph_result['nodes_loaded']} nodes, {graph_result['relationships_loaded']} rels")

        # 3. Vector Pipeline
        if target in ("all", "vector"):
            logger.info("[Step 3/3] Processing Vector Pipeline (ChatMessage Option A)...")
            vector_result = self.vector_loader.load_texts(staging_data)
            logger.info(f"Vector Pipeline completed: {vector_result['documents_indexed']} docs indexed")

        elapsed = round(time.time() - start_time, 2)
        logger.info(f"=== ETL Pipeline finished in {elapsed}s ===")

        return {
            "target": target,
            "elapsed_seconds": elapsed,
            "staging_tables": table_counts,
            "graph": graph_result,
            "vector": vector_result
        }
