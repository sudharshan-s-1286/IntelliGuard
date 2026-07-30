"""Qdrant Service."""
import logging
from typing import Any

from agents.security_agent.config import settings

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

    async def update_payloads(self, collection_name: str, payload_updates: list[tuple[str, dict]]) -> None:
        """Update payloads for specific points without modifying vectors."""
        if self._is_mock:
            return
            
        try:
            from qdrant_client.models import SetPayloadOperation, SetPayload
            operations = []
            for point_id, payload in payload_updates:
                operations.append(
                    SetPayloadOperation(
                        set_payload=SetPayload(
                            payload=payload,
                            points=[point_id]
                        )
                    )
                )
            
            # Update in chunks
            batch_size = 500
            for i in range(0, len(operations), batch_size):
                await self.client.batch_update_points(
                    collection_name=collection_name,
                    update_operations=operations[i:i + batch_size]
                )
        except Exception as e:
            logger.warning(f"batch_update_points failed or unavailable, falling back to individual updates: {e}")
            for point_id, payload in payload_updates:
                await self.client.overwrite_payload(
                    collection_name=collection_name,
                    payload=payload,
                    points=[point_id]
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
        
        response = await self.client.query_points(
            collection_name=collection_name,
            query=vector,
            query_filter=query_filter,
            limit=limit
        )
        return response.points

    async def retrieve_by_ids(self, collection_name: str, ids: list[str]) -> list[Any]:
        """Retrieve points by ID."""
        if self._is_mock:
            return []
        return await self.client.retrieve(
            collection_name=collection_name,
            ids=ids,
            with_payload=False,
            with_vectors=False
        )

    def health(self) -> dict[str, Any]:
        """Health check for Qdrant connection."""
        return {
            "status": "healthy" if not self._is_mock else "mocked",
            "host": self.host,
            "port": self.port,
            "is_mock": self._is_mock
        }
