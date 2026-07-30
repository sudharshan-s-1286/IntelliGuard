import asyncio
from agents.security_agent.repositories.qdrant_service import QdrantService
from agents.security_agent.ai.embeddings import EmbeddingService
from agents.security_agent.services.model_loader import ModelLoader
from agents.security_agent.services.cache_service import CacheService

async def run():
    q = QdrantService()
    await q.connect()
    res = await q.client.scroll(
        collection_name="security_patterns",
        limit=1,
        with_payload=True
    )
    print("One prompt from DB:", res[0][0].payload.get("description"))

asyncio.run(run())
