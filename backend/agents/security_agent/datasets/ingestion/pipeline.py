import datetime
import json
import logging
from pathlib import Path

from backend.agents.security_agent.ai.embeddings import EmbeddingService
from backend.agents.security_agent.datasets.ingestion.cleaner import DatasetCleaner
from backend.agents.security_agent.datasets.ingestion.normalizers import (
    BaseNormalizer,
    GarakNormalizer,
    HackAPromptNormalizer,
    OWASPNormalizer,
    ProtectAINormalizer,
)
from backend.agents.security_agent.models.domain import NormalizedDatasetRecord, VectorMetadata
from backend.agents.security_agent.repositories.knowledge_repository import KnowledgeRepository

logger = logging.getLogger(__name__)

class DatasetIngestionPipeline:
    def __init__(self, embedding_service: EmbeddingService, repository: KnowledgeRepository, raw_data_path: str):
        self.embedding_service = embedding_service
        self.repository = repository
        self.raw_data_path = Path(raw_data_path)
        self.cleaner = DatasetCleaner()
        
        self.normalizers: dict[str, BaseNormalizer] = {
            "hackaprompt": HackAPromptNormalizer(),
            "garak": GarakNormalizer(),
            "owasp": OWASPNormalizer(),
            "protect_ai": ProtectAINormalizer()
        }
        
        self.stats = {
            "datasets_processed": 0,
            "records_imported": 0,
            "duplicates_removed": 0,
            "failures": 0,
            "invalid_skipped": 0
        }

    def _map_to_vector_metadata(self, record: NormalizedDatasetRecord) -> VectorMetadata:
        """Map a normalized record to the schema required by the KnowledgeRepository."""
        now = datetime.datetime.utcnow().isoformat()
        return VectorMetadata(
            pattern_id=record.id,
            category=record.category,
            attack_type=record.subcategory,
            severity=record.severity,
            owasp_mapping=record.owasp,
            description=record.text,
            source=record.source,
            dataset_version="1.0",
            created_at=now,
            updated_at=now,
            tags=record.tags
        )

    async def _process_file(self, dataset_name: str, file_path: Path):
        """Parse, normalize, clean, embed, and upload a single file."""
        normalizer = self.normalizers.get(dataset_name)
        if not normalizer:
            logger.warning(f"No normalizer found for dataset: {dataset_name}. Skipping file {file_path}.")
            return
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            if not isinstance(data, list):
                logger.warning(f"File {file_path} is not a JSON list. Skipping.")
                self.stats["failures"] += 1
                return
                
            raw_records = data
        except Exception as e:
            logger.error(f"Failed to read or parse {file_path}: {e}")
            self.stats["failures"] += 1
            return

        normalized_records = []
        for raw in raw_records:
            try:
                norm = normalizer.normalize(raw)
                if norm:
                    normalized_records.append(norm)
                else:
                    self.stats["invalid_skipped"] += 1
            except Exception as e:
                logger.error(f"Failed to normalize record in {file_path}: {e}")
                self.stats["failures"] += 1

        # Clean batch
        clean_result = self.cleaner.clean_batch(normalized_records)
        valid_records: list[NormalizedDatasetRecord] = clean_result["cleaned_records"]
        
        # Update stats
        self.stats["duplicates_removed"] += clean_result["stats"]["duplicates_removed"]
        self.stats["invalid_skipped"] += clean_result["stats"]["invalid_skipped"]
        
        if not valid_records:
            return
            
        # Embed and Upload
        texts = [r.text for r in valid_records]
        try:
            embeddings = await self.embedding_service.generate_embedding(texts)
            if not isinstance(embeddings, list) or len(embeddings) == 0:
                # E.g. single item returns single embedding, we need to wrap it back if needed
                if not isinstance(embeddings[0], list):
                    embeddings = [embeddings]
            
            metadata_list = [self._map_to_vector_metadata(r) for r in valid_records]
            
            await self.repository.store_attack_patterns(vectors=embeddings, metadata_list=metadata_list)
            self.stats["records_imported"] += len(valid_records)
        except Exception as e:
            logger.error(f"Failed to embed/store records for {file_path}: {e}")
            self.stats["failures"] += len(valid_records)

    async def run(self) -> dict:
        """Run the full ingestion pipeline."""
        logger.info(f"Starting ingestion pipeline from {self.raw_data_path}")
        
        if not self.raw_data_path.exists():
            logger.error(f"Raw data path does not exist: {self.raw_data_path}")
            return self.stats

        await self.embedding_service.initialize()
        await self.repository.initialize()
        
        for dataset_dir in self.raw_data_path.iterdir():
            if dataset_dir.is_dir():
                dataset_name = dataset_dir.name
                json_files = list(dataset_dir.glob("*.json"))
                
                if json_files:
                    self.stats["datasets_processed"] += 1
                    
                for json_file in json_files:
                    logger.info(f"Processing {json_file}")
                    await self._process_file(dataset_name, json_file)
                    
        return self.stats
