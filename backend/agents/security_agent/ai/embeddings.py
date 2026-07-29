"""Embedding Service."""
import hashlib
import logging
from typing import Any

from backend.agents.security_agent.config.settings import BATCH_SIZE, EMBEDDING_MODEL

logger = logging.getLogger(__name__)

class EmbeddingService:
    """Generates embeddings and manages caching logic via CacheService and ModelLoader."""

    def __init__(self, model_loader: Any, cache_service: Any) -> None:
        self.model_loader = model_loader
        self.cache_service = cache_service
        self.model_name = EMBEDDING_MODEL
        self.batch_size = BATCH_SIZE

    async def initialize(self) -> None:
        """Initialize the model via the model loader."""
        await self.model_loader.load_model(self.model_name)

    def _get_cache_key(self, text: str) -> str:
        """Generate a deterministic cache key for a string."""
        hash_obj = hashlib.sha256(text.encode("utf-8"))
        return f"emb_{self.model_name}_{hash_obj.hexdigest()}"

    async def generate_embedding(self, text: str | list[str]) -> list[float] | list[list[float]]:
        """
        Generate a vector embedding for a given string or list of strings.
        Checks cache first.
        """
        is_single = isinstance(text, str)
        inputs = [text] if is_single else text
        
        results = [None] * len(inputs)
        missing_indices = []
        missing_texts = []

        # 1. Check Cache
        for i, t in enumerate(inputs):
            cache_key = self._get_cache_key(t)
            cached_val = await self.cache_service.get(cache_key)
            if cached_val is not None:
                results[i] = cached_val
            else:
                missing_indices.append(i)
                missing_texts.append(t)

        # 2. Compute missing
        if missing_texts:
            model = await self.model_loader.load_model(self.model_name)
            
            # Process in batches if batch size is exceeded
            computed_embeddings = []
            for i in range(0, len(missing_texts), self.batch_size):
                batch = missing_texts[i:i + self.batch_size]
                try:
                    # model.encode may be synchronous, but we can call it here.
                    # In a high-throughput env, this should run in a threadpool
                    # but for this infrastructure phase, we wrap it directly.
                    batch_embs = model.encode(batch, convert_to_numpy=False)
                    computed_embeddings.extend(batch_embs)
                except Exception as e:
                    logger.error(f"Error generating embeddings: {e}")
                    raise RuntimeError("Failed to generate embedding.") from e

            # 3. Store in cache and populate results
            for idx, text_val, emb in zip(missing_indices, missing_texts, computed_embeddings):
                results[idx] = emb
                # cache for 24 hours
                await self.cache_service.set(self._get_cache_key(text_val), emb, ttl=86400)

        return results[0] if is_single else results

    def health(self) -> dict[str, Any]:
        """Check health of the embedding service."""
        return {
            "status": "healthy",
            "model_configured": self.model_name,
            "batch_size": self.batch_size,
            "cache_service_healthy": self.cache_service.health().get("status") == "healthy",
            "model_loader_healthy": self.model_loader.health().get("status") == "healthy"
        }
