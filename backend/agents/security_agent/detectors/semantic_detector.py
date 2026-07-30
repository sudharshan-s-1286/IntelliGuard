"""Semantic Detector."""
import asyncio
import logging
import time
from typing import Any

from agents.security_agent.ai.embeddings import EmbeddingService
from agents.security_agent.config import settings
from agents.security_agent.models.domain import Finding, Threat
from agents.security_agent.repositories.knowledge_repository import (
    KnowledgeRepository,
)

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
        if score >= settings.SEMANTIC_CONFIDENCE_CRITICAL:
            return "Critical"
        elif score >= settings.SEMANTIC_CONFIDENCE_HIGH:
            return "High"
        elif score >= settings.SEMANTIC_CONFIDENCE_MEDIUM:
            return "Medium"
        return "Low"

    async def evaluate(self, prompt: str) -> list[Finding]:
        """
        Evaluate the prompt semantically against the vector database.
        :param prompt: The input prompt.
        :return: A list of Findings.
        """
        if not settings.SEMANTIC_RETRIEVAL_ENABLED:
            logger.info("Semantic retrieval is disabled via configuration.")
            return []

        findings = []
        
        try:
            # 1. Generate embedding
            logger.info("Generating embedding for semantic detection.")
            emb_start = time.time()
            vector = await asyncio.wait_for(
                self.embedding_service.generate_embedding(prompt),
                timeout=self.timeout
            )
            emb_time_ms = (time.time() - emb_start) * 1000
            logger.info(f"Embedding generation completed in {emb_time_ms:.2f}ms")
            logger.warning(f"DEBUG(1): query embedding dimensions: {len(vector)}")
            logger.warning(f"DEBUG(1.5): collection name: {self.repository.collection_name}")

            # 2. Search Qdrant via Repository
            logger.info("Searching vector DB for semantic matches.")
            qdrant_start = time.time()
            matches = await asyncio.wait_for(
                self.repository.search_by_embedding(vector, limit=self.limit),
                timeout=self.timeout
            )
            qdrant_time_ms = (time.time() - qdrant_start) * 1000
            
            logger.warning(f"DEBUG(2): number of retrieved vectors: {len(matches)}")
            scores = [match.similarity_score for match in matches]
            logger.warning(f"DEBUG(3): retrieved similarity scores from Qdrant (top-5): {scores[:5]}")
            
            pattern_ids = [match.pattern_id for match in matches]
            logger.warning(f"DEBUG(3.1): matched pattern IDs: {pattern_ids}")
            
            categories = [match.metadata.get('category') for match in matches]
            logger.warning(f"DEBUG(3.2): matched attack categories: {categories}")

            logger.info(f"Qdrant query completed in {qdrant_time_ms:.2f}ms. Retrieved {len(matches)} results.")

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

                confidence_tier = self._determine_confidence(score)
                severity = meta.get("severity", "MEDIUM")
                
                # Scale severity down for medium-confidence matches
                severity_map = {"CRITICAL": 1.0, "HIGH": 0.8, "MEDIUM": 0.5, "LOW": 0.2}
                mapped_severity = severity_map.get(str(severity).upper(), 0.5)
                if confidence_tier == "Medium":
                    mapped_severity *= 0.5 # Lower confidence reduces severity impact
                    
                logger.info(
                    f"Semantic Match: similarity_score={score:.4f}, tier={confidence_tier}, "
                    f"category='{category}'"
                )

                finding_metadata = {
                    "similarity_score": score,
                    "confidence_tier": confidence_tier,
                    "attack_type": meta.get("attack_type", "Unknown"),
                    "category": category,
                    "owasp_mapping": meta.get("owasp_mapping", "Unknown"),
                    "severity": severity,
                    "source_dataset": meta.get("source", "Unknown"),
                    "original_attack_prompt": meta.get("description", ""),
                    "embedding_time_ms": emb_time_ms,
                    "qdrant_time_ms": qdrant_time_ms
                }
                
                finding = Finding(
                    threat=Threat(
                        category=category,
                        description="Potential novel attack detected through semantic similarity."
                    ),
                    severity=mapped_severity,
                    evidence=f"Matched Pattern ID: {match.pattern_id}",
                    detector="SemanticDetector",
                    confidence=score,
                    metadata=finding_metadata
                )
                findings.append(finding)

            logger.warning(f"DEBUG(3.3): semantic findings count: {len(findings)}")
            logger.info(f"Semantic detector identified {len(findings)} findings.")

        except asyncio.TimeoutError:
            logger.error(f"Semantic search timed out after {self.timeout}s.")
        except Exception as e:
            logger.error(f"Error during semantic evaluation: {e}")

        return findings

    def health(self) -> dict[str, Any]:
        """Health check for the semantic detector."""
        return {
            "status": "healthy" if settings.SEMANTIC_RETRIEVAL_ENABLED else "disabled",
            "threshold": self.threshold,
            "embedding_service": self.embedding_service.health(),
            "repository": self.repository.health()
        }
