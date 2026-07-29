import pytest
from unittest.mock import AsyncMock, MagicMock
import asyncio

from backend.agents.security_agent.detectors.semantic_detector import SemanticDetector
from backend.agents.security_agent.ai.embeddings import EmbeddingService
from backend.agents.security_agent.repositories.knowledge_repository import KnowledgeRepository
from backend.agents.security_agent.models.domain import PatternMatch
from backend.agents.security_agent.config import settings

@pytest.fixture
def embedding_service():
    service = MagicMock(spec=EmbeddingService)
    service.generate_embedding = AsyncMock(return_value=[0.1] * 384)
    service.health = MagicMock(return_value={"status": "healthy"})
    return service

@pytest.fixture
def repository():
    repo = MagicMock(spec=KnowledgeRepository)
    repo.health = MagicMock(return_value={"status": "healthy"})
    return repo

@pytest.fixture
def semantic_detector(embedding_service, repository):
    detector = SemanticDetector(embedding_service, repository)
    # Ensure test environment overrides for predictable testing
    detector.threshold = 0.85
    return detector

@pytest.mark.asyncio
async def test_semantic_detector_no_matches(semantic_detector, repository):
    repository.search_by_embedding = AsyncMock(return_value=[])
    findings = await semantic_detector.evaluate("hello world")
    assert len(findings) == 0

@pytest.mark.asyncio
async def test_semantic_detector_below_threshold(semantic_detector, repository):
    match = PatternMatch(
        pattern_id="1",
        similarity_score=0.80, # Below 0.85 default
        metadata={"category": "Prompt Injection"}
    )
    repository.search_by_embedding = AsyncMock(return_value=[match])
    findings = await semantic_detector.evaluate("ignore instructions")
    assert len(findings) == 0

@pytest.mark.asyncio
async def test_semantic_detector_high_confidence(semantic_detector, repository):
    match = PatternMatch(
        pattern_id="2",
        similarity_score=0.98,
        metadata={"category": "Jailbreak", "severity": "CRITICAL"}
    )
    repository.search_by_embedding = AsyncMock(return_value=[match])
    
    findings = await semantic_detector.evaluate("DAN mode")
    assert len(findings) == 1
    f = findings[0]
    
    assert f.threat.category == "Jailbreak"
    assert "Confidence: High" in f.threat.description
    assert f.severity == 1.0  # CRITICAL mapped to 1.0

@pytest.mark.asyncio
async def test_semantic_detector_duplicate_reduction(semantic_detector, repository):
    # Two matches with same category
    match1 = PatternMatch(
        pattern_id="3",
        similarity_score=0.96,
        metadata={"category": "Data Exfiltration"}
    )
    match2 = PatternMatch(
        pattern_id="4",
        similarity_score=0.90,
        metadata={"category": "Data Exfiltration"}
    )
    # The repository returns them in order of highest score first
    repository.search_by_embedding = AsyncMock(return_value=[match1, match2])
    
    findings = await semantic_detector.evaluate("send data")
    # Should only keep the highest scoring match for the category
    assert len(findings) == 1
    assert findings[0].threat.category == "Data Exfiltration"
    assert "Confidence: High" in findings[0].threat.description

@pytest.mark.asyncio
async def test_semantic_detector_timeout(semantic_detector, repository):
    # Simulate a slow repository response
    async def slow_search(*args, **kwargs):
        await asyncio.sleep(2.0)
        return []
        
    repository.search_by_embedding = AsyncMock(side_effect=slow_search)
    semantic_detector.timeout = 0.1 # aggressive timeout
    
    findings = await semantic_detector.evaluate("timeout test")
    assert len(findings) == 0 # Returns empty list gracefully on timeout

def test_semantic_detector_health(semantic_detector):
    health = semantic_detector.health()
    assert health["status"] == "healthy"
    assert health["embedding_service"]["status"] == "healthy"
    assert health["repository"]["status"] == "healthy"
