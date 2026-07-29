"""Knowledge Ingestion Service."""
import json
import logging
from datetime import datetime
from typing import Any, List, Dict

from backend.agents.security_agent.ai.embeddings import EmbeddingService
from backend.agents.security_agent.repositories.knowledge_repository import KnowledgeRepository
from backend.agents.security_agent.models.domain import VectorMetadata

logger = logging.getLogger(__name__)

class KnowledgeIngestionService:
    """Parses, normalizes, embeds, and stores external datasets into Qdrant."""

    def __init__(self, embedding_service: EmbeddingService, repository: KnowledgeRepository) -> None:
        self.embedding_service = embedding_service
        self.repository = repository

    def _parse_json(self, filepath: str) -> List[Dict[str, Any]]:
        """Parse JSON dataset."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
                elif "patterns" in data and isinstance(data["patterns"], list):
                    return data["patterns"]
                else:
                    raise ValueError("JSON dataset must be a list or contain a 'patterns' list.")
        except Exception as e:
            logger.error(f"Failed to parse JSON file {filepath}: {e}")
            raise

    def _normalize_metadata(self, item: Dict[str, Any], dataset_version: str) -> VectorMetadata:
        """Map raw dictionary to VectorMetadata schema."""
        return VectorMetadata(
            pattern_id=str(item.get("id") or item.get("pattern_id")),
            category=item.get("category", "General"),
            attack_type=item.get("attack_type", "Unknown"),
            severity=item.get("severity", "MEDIUM"),
            owasp_mapping=item.get("owasp_mapping", ""),
            description=item.get("description", ""),
            source=item.get("source", "internal_dataset"),
            dataset_version=dataset_version,
            created_at=item.get("created_at", datetime.utcnow().isoformat()),
            updated_at=datetime.utcnow().isoformat(),
            tags=item.get("tags", [])
        )

    async def ingest_file(self, filepath: str, dataset_version: str = "1.0.0") -> Any:
        """Read a dataset file, embed its text, and store structured threats in Qdrant."""
        logger.info(f"Starting ingestion of {filepath} (version: {dataset_version})")
        
        # 1. Parse based on extension
        if filepath.endswith(".json"):
            raw_data = self._parse_json(filepath)
        elif filepath.endswith(".csv"):
            raise NotImplementedError("CSV ingestion is planned for a future release.")
        else:
            raise ValueError("Unsupported dataset file format. Only JSON is currently supported.")

        # 2. Extract texts and normalize metadata
        texts_to_embed = []
        metadata_list = []
        
        for item in raw_data:
            text = item.get("text") or item.get("pattern")
            if not text:
                logger.warning(f"Skipping entry missing 'text' or 'pattern': {item}")
                continue
                
            try:
                meta = self._normalize_metadata(item, dataset_version)
                texts_to_embed.append(text)
                metadata_list.append(meta)
            except Exception as e:
                logger.warning(f"Failed to normalize metadata for item {item}: {e}")
                continue

        if not texts_to_embed:
            logger.info("No valid patterns found in dataset.")
            return {"status": "success", "ingested_count": 0}

        # 3. Embedding Generation (Batch)
        logger.info(f"Generating embeddings for {len(texts_to_embed)} patterns...")
        embeddings = await self.embedding_service.generate_embedding(texts_to_embed)

        # 4. Storage in Qdrant via Repository
        logger.info("Storing patterns in Knowledge Repository...")
        await self.repository.store_attack_patterns(vectors=embeddings, metadata_list=metadata_list)
        
        logger.info(f"Successfully ingested {len(texts_to_embed)} patterns.")
        return {
            "status": "success",
            "ingested_count": len(texts_to_embed),
            "version": dataset_version
        }
