"""Semantic Detector."""
import logging
from typing import List, Any
import asyncio

from backend.agents.security_agent.ai.embeddings import EmbeddingService
from backend.agents.security_agent.repositories.knowledge_repository import KnowledgeRepository
from backend.agents.security_agent.models.domain import Finding, Threat
from backend.agents.security_agent.config import settings

logger = logging.getLogger(__name__)

class SemanticDetector:
    """Utilizes embeddings to perform similarity searches against known attacks."""

    def __init__(self, embedding_service: EmbeddingService, repository: KnowledgeRepository) -> None:
        self.embedding_service = embedding_service
        self.repository = repository
        self.threshold = settings.SEMANTIC_SIMILARITY_THRESHOLD
        self.limit = settings.SEMANTIC_MAX_RESULTS
        self.timeout = settings.SEMANTIC_SEARCH_TIMEOUT

    def _determine_confidence(self, score: float) -> str:
        """Classify confidence based on similarity score."""
        if score >= settings.SEMANTIC_CONFIDENCE_HIGH:
            return "High"
        elif score >= settings.SEMANTIC_CONFIDENCE_MEDIUM:
            return "Medium"
        return "Low"

    async def evaluate(self, prompt: str) -> List[Finding]:
        """
        Evaluate the prompt semantically against the vector database.
        :param prompt: The input prompt.
        :return: A list of Findings.
        """
        findings = []
        
        try:
            # 1. Generate embedding
            logger.info("Generating embedding for semantic detection.")
            # Use asyncio.wait_for to apply a timeout to the overall process
            vector = await asyncio.wait_for(
                self.embedding_service.generate_embedding(prompt),
                timeout=self.timeout
            )

            # 2. Search Qdrant via Repository
            logger.info("Searching vector DB for semantic matches.")
            matches = await asyncio.wait_for(
                self.repository.search_by_embedding(vector, limit=self.limit),
                timeout=self.timeout
            )

            # 3. Similarity Evaluation & False Positive Reduction
            seen_categories = set()
            for match in matches:
                score = match.similarity_score
                
                # Minimum confidence threshold (False Positive Reduction)
                if score < self.threshold:
                    continue
                    
                meta = match.metadata
                category = meta.get("category", "Semantic Match")
                
                # Duplicate removal (only keep the highest score per category)
                if category in seen_categories:
                    continue
                seen_categories.add(category)

                confidence = self._determine_confidence(score)
                severity = meta.get("severity", "MEDIUM")
                # Map string severity to float for the Finding schema
                # e.g., CRITICAL: 1.0, HIGH: 0.8, MEDIUM: 0.5, LOW: 0.2
                severity_map = {"CRITICAL": 1.0, "HIGH": 0.8, "MEDIUM": 0.5, "LOW": 0.2}
                mapped_severity = severity_map.get(str(severity).upper(), 0.5)

                description = meta.get("description", "Semantic similarity to known attack.")
                
                finding = Finding(
                    threat=Threat(
                        category=category,
                        description=f"{description} (Similarity: {score:.2f}, Confidence: {confidence})"
                    ),
                    severity=mapped_severity,
                    evidence=f"Matched Pattern ID: {match.pattern_id}",
                    detector="SemanticDetector",
                    confidence=score
                )
                findings.append(finding)

            logger.info(f"Semantic detector identified {len(findings)} findings.")

        except asyncio.TimeoutError:
            logger.error(f"Semantic search timed out after {self.timeout}s.")
        except Exception as e:
            logger.error(f"Error during semantic evaluation: {e}")

        return findings

    def health(self) -> dict[str, Any]:
        """Health check for the semantic detector."""
        return {
            "status": "healthy",
            "threshold": self.threshold,
            "embedding_service": self.embedding_service.health(),
            "repository": self.repository.health()
        }
