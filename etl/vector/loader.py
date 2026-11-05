"""
Qdrant Vector DB Loader Module.
Stores text embeddings and Multi-Tenant metadata in Qdrant collection.
Features:
- Implements ChatMessage Option A (ChatMessage content stored in Vector DB, not Neo4j)
- Multi-Tenant isolation payload schema
- Automatic payload indexing on tenant_id and channel_id
- Local on-disk or remote server connectivity
"""

import uuid
import logging
from typing import Dict, List, Any
from etl.config import config
from etl.vector.embedder import TextEmbedder

logger = logging.getLogger("etl.vector.loader")

class VectorLoader:
    def __init__(self):
        from qdrant_client import QdrantClient
        from qdrant_client.http import models

        self.models = models
        if config.qdrant_url:
            logger.info(f"Connecting to remote Qdrant at {config.qdrant_url}")
            self.client = QdrantClient(url=config.qdrant_url)
        else:
            logger.info(f"Using local on-disk Qdrant storage at {config.qdrant_path}")
            config.qdrant_path.mkdir(parents=True, exist_ok=True)
            self.client = QdrantClient(path=str(config.qdrant_path))

        self.collection_name = config.qdrant_collection
        self.embedder = TextEmbedder()
        self._ensure_collection()

    def _ensure_collection(self):
        collections = [c.name for c in self.client.get_collections().collections]
        if self.collection_name not in collections:
            logger.info(f"Creating Qdrant collection '{self.collection_name}' (dim={config.vector_dimension})...")
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=self.models.VectorParams(
                    size=config.vector_dimension,
                    distance=self.models.Distance.COSINE
                )
            )
            # Create payload index on tenant_id for high-performance multi-tenant filtering
            self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name="tenant_id",
                field_schema=self.models.PayloadSchemaType.INTEGER
            )
            self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name="source_type",
                field_schema=self.models.PayloadSchemaType.KEYWORD
            )
            logger.info("Qdrant collection and payload indexes created successfully.")

    def load_texts(self, staging_data: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """
        Extracts textual entities (chat messages, notices, approvals, assets),
        computes embeddings, and upserts into Qdrant.
        """
        documents = []

        # 1. Chat Messages (ChatMessage Option A: Primary retrieval source outside Neo4j)
        for msg in staging_data.get("chat_messages", []):
            if msg.get("is_deleted", False):
                continue
            text = msg.get("message", "").strip()
            if not text:
                continue
            documents.append({
                "doc_id": f"msg_{msg['id']}",
                "tenant_id": int(msg["tenant_id"]),
                "channel_id": str(msg.get("conversation_id", "")),
                "author_id": int(msg.get("user_id", 0)),
                "text": text,
                "created_at": msg.get("created_at", ""),
                "source_type": "chat_message"
            })

        # 2. Notices (Announcements)
        for n in staging_data.get("notices", []):
            if n.get("is_deleted", False):
                continue
            title = n.get("title", "").strip()
            if not title:
                continue
            documents.append({
                "doc_id": f"notice_{n['id']}",
                "tenant_id": int(n.get("tenant_id", 1)),
                "channel_id": f"audience_{n.get('audience_id', 0)}",
                "author_id": int(n.get("created_by_user_id", 0)),
                "text": f"Thông báo: {title} (Phân loại: {n.get('notice_type', 'general')})",
                "created_at": n.get("published_at", ""),
                "source_type": "notice"
            })

        # 3. Approval Requests
        for app in staging_data.get("approval_requests", []):
            if app.get("is_deleted", False):
                continue
            title = app.get("title", "").strip()
            if not title:
                continue
            documents.append({
                "doc_id": f"approval_{app['id']}",
                "tenant_id": int(app.get("tenant_id", 1)),
                "channel_id": "approval_workflow",
                "author_id": int(app.get("requester_id", 0)),
                "text": f"Đơn đề xuất: {title} (Trạng thái: {app.get('status', 'PENDING')})",
                "created_at": "",
                "source_type": "approval_request"
            })

        # 4. Assets (IT equipment, servers, laptops)
        for ast in staging_data.get("assets", []):
            if ast.get("is_deleted", False):
                continue
            name = ast.get("name", "").strip()
            code = ast.get("asset_code", "").strip()
            if not name:
                continue
            documents.append({
                "doc_id": f"asset_{ast['id']}",
                "tenant_id": int(ast.get("tenant_id", 1)),
                "channel_id": f"dept_{ast.get('department_id', 0)}",
                "author_id": int(ast.get("assigned_user_id", 0)),
                "text": f"Tài sản: {name} | Mã: {code} | Số Serial: {ast.get('serial_number', 'N/A')} | Trạng thái: {ast.get('status', 'IN_USE')}",
                "created_at": "",
                "source_type": "asset"
            })

        if not documents:
            return {"status": "SUCCESS", "documents_indexed": 0}

        logger.info(f"Computing embeddings for {len(documents)} documents on CPU...")
        raw_texts = [d["text"] for d in documents]
        vectors = self.embedder.embed_documents(raw_texts)

        # Prepare Qdrant points
        points = []
        for doc, vec in zip(documents, vectors):
            point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, doc["doc_id"]))
            points.append(
                self.models.PointStruct(
                    id=point_id,
                    vector=vec,
                    payload=doc
                )
            )

        logger.info(f"Upserting {len(points)} points into Qdrant collection '{self.collection_name}'...")
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )

        return {
            "status": "SUCCESS",
            "collection_name": self.collection_name,
            "documents_indexed": len(documents),
            "breakdown": {
                "chat_messages": sum(1 for d in documents if d["source_type"] == "chat_message"),
                "notices": sum(1 for d in documents if d["source_type"] == "notice"),
                "approval_requests": sum(1 for d in documents if d["source_type"] == "approval_request"),
                "assets": sum(1 for d in documents if d["source_type"] == "asset")
            }
        }
