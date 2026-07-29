"""Knowledge Repository."""
import logging
from typing import List, Dict, Any, Optional

from backend.agents.security_agent.repositories.qdrant_service import QdrantService
from backend.agents.security_agent.models.domain import VectorMetadata, PatternMatch
from backend.agents.security_agent.config import settings

logger = logging.getLogger(__name__)


class KnowledgeRepository:
    """Isolates Qdrant Service from core business logic."""

    def __init__(self, qdrant_service: QdrantService) -> None:
        self.db = qdrant_service
        self.collection_name = settings.QDRANT_COLLECTION_NAME

    async def initialize(self) -> None:
        """Ensure collection exists and is ready."""
        await self.db.connect()
        exists = await self.db.collection_exists(self.collection_name)
        if not exists:
            logger.info(f"Creating collection {self.collection_name}...")
            await self.db.create_collection(
                collection_name=self.collection_name,
                vector_size=settings.VECTOR_SIZE,
                distance=settings.DISTANCE_METRIC
            )

    async def store_attack_patterns(self, vectors: List[List[float]], metadata_list: List[VectorMetadata]) -> None:
        """Store new attack patterns into the vector database."""
        if not vectors or len(vectors) != len(metadata_list):
            raise ValueError("Vectors and metadata lists must be of the same non-zero length.")

        try:
            from qdrant_client.models import PointStruct
            points = []
            for vec, meta in zip(vectors, metadata_list):
                payload = {
                    "pattern_id": meta.pattern_id,
                    "category": meta.category,
                    "attack_type": meta.attack_type,
                    "severity": meta.severity,
                    "owasp_mapping": meta.owasp_mapping,
                    "description": meta.description,
                    "source": meta.source,
                    "dataset_version": meta.dataset_version,
                    "created_at": meta.created_at,
                    "updated_at": meta.updated_at,
                    "tags": meta.tags
                }
                points.append(
                    PointStruct(
                        id=meta.pattern_id,
                        vector=vec,
                        payload=payload
                    )
                )

            # Batch upsert
            batch_size = settings.VECTOR_BATCH_SIZE
            for i in range(0, len(points), batch_size):
                batch = points[i:i + batch_size]
                await self.db.upsert_vectors(self.collection_name, batch)
                
            logger.info(f"Successfully stored {len(points)} patterns.")
        except ImportError:
            logger.warning("qdrant-client not installed. Skipping store operation.")

    async def search_by_embedding(self, vector: List[float], limit: int = 5, category: Optional[str] = None) -> List[PatternMatch]:
        """Search the database by vector similarity, optionally filtering by category."""
        query_filter = None
        
        try:
            from qdrant_client.models import Filter, FieldCondition, MatchValue
            if category:
                query_filter = Filter(
                    must=[
                        FieldCondition(
                            key="category",
                            match=MatchValue(value=category)
                        )
                    ]
                )
        except ImportError:
            pass

        results = await self.db.search_nearest_neighbors(
            collection_name=self.collection_name,
            vector=vector,
            limit=limit,
            query_filter=query_filter
        )

        matches = []
        for res in results:
            matches.append(
                PatternMatch(
                    pattern_id=res.id,
                    similarity_score=res.score,
                    metadata=res.payload
                )
            )
        return matches

    async def delete_patterns(self, pattern_ids: List[str]) -> None:
        """Remove patterns from the knowledge base."""
        await self.db.delete_vectors(self.collection_name, pattern_ids)

    def health(self) -> dict[str, Any]:
        """Health check."""
        return {
            "status": "healthy",
            "qdrant_service": self.db.health()
        }
