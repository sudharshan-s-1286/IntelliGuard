"""Qdrant Service."""
import logging
from typing import Any

from backend.agents.security_agent.config import settings

logger = logging.getLogger(__name__)

class QdrantService:
    """Manages vector collections, fast nearest-neighbor search, and updates via Qdrant."""

    def __init__(self) -> None:
        self.host = settings.QDRANT_HOST
        self.port = settings.QDRANT_PORT
        self.api_key = settings.QDRANT_API_KEY
        self.https = settings.QDRANT_HTTPS
        self.client = None
        self._is_mock = False

    async def connect(self) -> None:
        """Establish connection to Qdrant async client."""
        try:
            from qdrant_client import AsyncQdrantClient
            self.client = AsyncQdrantClient(
                host=self.host,
                port=self.port,
                api_key=self.api_key,
                https=self.https
            )
            self._is_mock = False
            logger.info("Connected to Qdrant.")
        except ImportError:
            logger.warning("qdrant-client not installed. Mocking QdrantService.")
            self._is_mock = True

    async def disconnect(self) -> None:
        """Close connection."""
        if self.client and not self._is_mock:
            await self.client.close()

    async def collection_exists(self, collection_name: str) -> bool:
        """Check if a collection exists."""
        if self._is_mock:
            return True
        return await self.client.collection_exists(collection_name)

    async def create_collection(self, collection_name: str, vector_size: int, distance: str = "Cosine") -> None:
        """Create a new collection."""
        if self._is_mock:
            return
        from qdrant_client.models import Distance, VectorParams
        dist_enum = getattr(Distance, distance.upper(), Distance.COSINE)
        await self.client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=vector_size, distance=dist_enum)
        )

    async def delete_collection(self, collection_name: str) -> None:
        """Delete an existing collection."""
        if self._is_mock:
            return
        await self.client.delete_collection(collection_name=collection_name)

    async def upsert_vectors(self, collection_name: str, points: list[Any]) -> None:
        """Upsert a list of points (qdrant_client.models.PointStruct)."""
        if self._is_mock:
            return
        await self.client.upsert(
            collection_name=collection_name,
            points=points
        )

    async def delete_vectors(self, collection_name: str, point_ids: list[str]) -> None:
        """Delete specific vectors by ID."""
        if self._is_mock:
            return
        from qdrant_client.models import PointIdsList
        await self.client.delete(
            collection_name=collection_name,
            points_selector=PointIdsList(points=point_ids)
        )

    async def search_nearest_neighbors(
        self, 
        collection_name: str, 
        vector: list[float], 
        limit: int = 5, 
        query_filter: Any | None = None
    ) -> list[Any]:
        """
        Perform a semantic search in Qdrant with optional metadata filtering.
        """
        if self._is_mock:
            return []
        
        return await self.client.search(
            collection_name=collection_name,
            query_vector=vector,
            query_filter=query_filter,
            limit=limit
        )

    def health(self) -> dict[str, Any]:
        """Health check for Qdrant connection."""
        return {
            "status": "healthy" if not self._is_mock else "mocked",
            "host": self.host,
            "port": self.port,
            "is_mock": self._is_mock
        }
