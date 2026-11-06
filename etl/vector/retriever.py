"""
Multi-Tenant Semantic Retriever Module.
Retrieves semantic knowledge and chat messages from Qdrant with STRICT Tenant Isolation.
"""

import logging
from typing import List, Dict, Any
from etl.config import config
from etl.vector.embedder import TextEmbedder

logger = logging.getLogger("etl.vector.retriever")

class MultiTenantRetriever:
    def __init__(self):
        from qdrant_client import QdrantClient
        from qdrant_client.http import models

        self.models = models
        if config.qdrant_url:
            self.client = QdrantClient(url=config.qdrant_url, timeout=60)
        else:
            self.client = QdrantClient(path=str(config.qdrant_path), timeout=60)

        self.collection_name = config.qdrant_collection
        self.embedder = TextEmbedder()

    def search(self, query: str, tenant_id: int, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Executes semantic search strictly filtered by tenant_id.
        Multi-Tenant Security invariant: No results from other tenants may ever be returned.
        """
        query_vector = self.embedder.embed_query(query)

        # Build strict tenant filter
        tenant_filter = self.models.Filter(
            must=[
                self.models.FieldCondition(
                    key="tenant_id",
                    match=self.models.MatchValue(value=int(tenant_id))
                )
            ]
        )

        # Support both qdrant-client >= 1.20 (query_points) and earlier versions (search)
        if hasattr(self.client, "query_points"):
            response = self.client.query_points(
                collection_name=self.collection_name,
                query=query_vector,
                query_filter=tenant_filter,
                limit=top_k
            )
            hits = response.points
        else:
            hits = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                query_filter=tenant_filter,
                limit=top_k
            )

        results = []
        for hit in hits:
            results.append({
                "score": round(hit.score, 4),
                "doc_id": hit.payload.get("doc_id"),
                "tenant_id": hit.payload.get("tenant_id"),
                "channel_id": hit.payload.get("channel_id"),
                "source_type": hit.payload.get("source_type"),
                "text": hit.payload.get("text"),
                "created_at": hit.payload.get("created_at")
            })

        return results
