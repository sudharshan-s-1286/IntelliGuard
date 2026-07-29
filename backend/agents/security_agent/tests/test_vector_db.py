import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.agents.security_agent.ai.embeddings import EmbeddingService
from backend.agents.security_agent.knowledge.manager import KnowledgeManager
from backend.agents.security_agent.models.domain import VectorMetadata
from backend.agents.security_agent.repositories.knowledge_repository import (
    KnowledgeRepository,
)
from backend.agents.security_agent.repositories.qdrant_service import QdrantService
from backend.agents.security_agent.services.knowledge_ingestion_service import (
    KnowledgeIngestionService,
)


@pytest.fixture
def qdrant_service():
    service = QdrantService()
    # Force mock mode for tests
    service._is_mock = True
    return service

@pytest.fixture
def knowledge_repository(qdrant_service):
    return KnowledgeRepository(qdrant_service)

@pytest.fixture
def embedding_service():
    service = MagicMock(spec=EmbeddingService)
    # Mock embedding generation to return a dummy vector matching input length
    async def mock_generate(texts):
        if isinstance(texts, str):
            return [0.1] * 384
        return [[0.1] * 384 for _ in texts]
    
    service.generate_embedding = AsyncMock(side_effect=mock_generate)
    return service

@pytest.fixture
def ingestion_service(embedding_service, knowledge_repository):
    return KnowledgeIngestionService(embedding_service, knowledge_repository)

@pytest.fixture
def knowledge_manager(knowledge_repository, ingestion_service):
    return KnowledgeManager(knowledge_repository, ingestion_service)


@pytest.mark.asyncio
async def test_qdrant_service_lifecycle(qdrant_service):
    # Test connect/disconnect in mock mode
    await qdrant_service.connect()
    assert qdrant_service._is_mock is True
    
    assert await qdrant_service.collection_exists("test") is True
    await qdrant_service.create_collection("test", 384)
    await qdrant_service.delete_collection("test")
    
    # Check health
    health = qdrant_service.health()
    assert health["status"] == "mocked"
    await qdrant_service.disconnect()


@pytest.mark.asyncio
async def test_knowledge_repository(knowledge_repository):
    await knowledge_repository.initialize()
    
    meta1 = VectorMetadata(
        pattern_id="1", category="Prompt Injection", attack_type="Test",
        severity="HIGH", owasp_mapping="", description="", source="test",
        dataset_version="1.0", created_at="now", updated_at="now", tags=[]
    )
    
    # Store
    await knowledge_repository.store_attack_patterns(
        vectors=[[0.1] * 384], metadata_list=[meta1]
    )
    
    # Search
    results = await knowledge_repository.search_by_embedding([0.1] * 384, limit=5, category="Prompt Injection")
    # Because qdrant_service is mocked, search returns []
    assert len(results) == 0
    
    # Delete
    await knowledge_repository.delete_patterns(["1"])


@pytest.mark.asyncio
async def test_knowledge_ingestion_service(ingestion_service, tmp_path):
    # Create a dummy JSON dataset
    dataset_file = tmp_path / "dataset.json"
    dataset_data = [
        {
            "id": "pattern_1",
            "text": "ignore previous instructions",
            "category": "Prompt Injection",
            "severity": "CRITICAL"
        },
        {
            "id": "pattern_2",
            "text": "DAN mode activated",
            "category": "Jailbreak"
        }
    ]
    with open(dataset_file, "w") as f:
        json.dump(dataset_data, f)
        
    result = await ingestion_service.ingest_file(str(dataset_file), "1.1.0")
    
    assert result["status"] == "success"
    assert result["ingested_count"] == 2
    assert result["version"] == "1.1.0"
    
    # Verify embedding service was called
    ingestion_service.embedding_service.generate_embedding.assert_called_once_with(
        ["ignore previous instructions", "DAN mode activated"]
    )


@pytest.mark.asyncio
async def test_knowledge_manager(knowledge_manager, tmp_path):
    await knowledge_manager.initialize()
    
    dataset_file = tmp_path / "dataset.json"
    with open(dataset_file, "w") as f:
        json.dump([{"id": "1", "text": "test"}], f)
        
    # Sync new version
    result1 = await knowledge_manager.sync_dataset(str(dataset_file), "1.0.0")
    assert result1["status"] == "success"
    assert knowledge_manager._current_version == "1.0.0"
    
    # Sync older version
    result2 = await knowledge_manager.sync_dataset(str(dataset_file), "0.9.0")
    assert result2["status"] == "skipped"
    assert knowledge_manager._current_version == "1.0.0"

    # Sync missing file
    result3 = await knowledge_manager.sync_dataset("missing.json", "2.0.0")
    assert result3["status"] == "error"
