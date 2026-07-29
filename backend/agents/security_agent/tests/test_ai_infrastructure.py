import pytest
import asyncio
from backend.agents.security_agent.services.cache_service import CacheService
from backend.agents.security_agent.services.model_loader import ModelLoader
from backend.agents.security_agent.ai.embeddings import EmbeddingService
from backend.agents.security_agent.config import settings

@pytest.fixture
def cache_service():
    return CacheService()

@pytest.fixture
def model_loader():
    return ModelLoader()

@pytest.fixture
def embedding_service(model_loader, cache_service):
    return EmbeddingService(model_loader, cache_service)


@pytest.mark.asyncio
async def test_cache_service_set_get_ttl(cache_service):
    # Test setting and getting
    await cache_service.set("key1", "value1", ttl=10)
    val = await cache_service.get("key1")
    assert val == "value1"
    
    # Test expiration
    await cache_service.set("key2", "value2", ttl=-1) # Immediate expiration
    val2 = await cache_service.get("key2")
    assert val2 is None
    
    # Test invalidation
    await cache_service.set("key3", "value3", ttl=10)
    cache_service.invalidate("key3")
    assert await cache_service.get("key3") is None
    
    # Test capacity eviction
    cache_service.capacity = 2
    await cache_service.set("a", 1)
    await cache_service.set("b", 2)
    await cache_service.set("c", 3)
    
    # "a" should be evicted
    assert await cache_service.get("a") is None
    assert await cache_service.get("b") == 2
    assert await cache_service.get("c") == 3

    assert cache_service.health()["status"] == "healthy"


@pytest.mark.asyncio
async def test_model_loader(model_loader):
    # This will use the MockModel since torch/sentence_transformers aren't installed in the test env
    model = await model_loader.load_model("test-model")
    assert hasattr(model, "encode")
    
    # Test singleton behavior
    model2 = await model_loader.load_model("test-model")
    assert model is model2
    
    assert "test-model" in model_loader.health()["loaded_models"]
    
    # Test unloading
    await model_loader.unload_model("test-model")
    assert "test-model" not in model_loader._models


@pytest.mark.asyncio
async def test_embedding_service(embedding_service):
    # Single string
    emb1 = await embedding_service.generate_embedding("hello world")
    assert isinstance(emb1, list)
    assert len(emb1) == 384
    
    # Batch strings
    emb_batch = await embedding_service.generate_embedding(["hello", "world"])
    assert isinstance(emb_batch, list)
    assert len(emb_batch) == 2
    assert len(emb_batch[0]) == 384
    
    # Test cache hit
    # The cache should now hold the embeddings
    cache_key = embedding_service._get_cache_key("hello world")
    cached = await embedding_service.cache_service.get(cache_key)
    assert cached is not None
    assert cached == emb1

    # Health check
    health = embedding_service.health()
    assert health["status"] == "healthy"
    assert health["cache_service_healthy"] is True
    assert health["model_loader_healthy"] is True


def test_config_settings():
    assert settings.EMBEDDING_MODEL == "BAAI/bge-small-en-v1.5"
    assert isinstance(settings.CACHE_SIZE, int)
    assert isinstance(settings.BATCH_SIZE, int)
    assert isinstance(settings.SIMILARITY_THRESHOLD, float)
    assert isinstance(settings.DEVICE_SELECTION, str)
    assert isinstance(settings.FALLBACK_TO_CPU, bool)
