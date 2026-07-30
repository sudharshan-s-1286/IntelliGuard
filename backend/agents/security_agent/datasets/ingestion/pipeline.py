import datetime
import hashlib
import json
import logging
import time
from pathlib import Path

from agents.security_agent.ai.embeddings import EmbeddingService
from agents.security_agent.datasets.ingestion.cleaner import DatasetCleaner
from agents.security_agent.models.domain import NormalizedDatasetRecord, VectorMetadata
from agents.security_agent.repositories.knowledge_repository import KnowledgeRepository

logger = logging.getLogger(__name__)

class DatasetIngestionPipeline:
    def __init__(self, embedding_service: EmbeddingService, repository: KnowledgeRepository, data_path: str):
        self.embedding_service = embedding_service
        self.repository = repository
        self.data_path = Path(data_path)
        self.cleaner = DatasetCleaner()
        
        self.stats = {
            "datasets_processed": 0,
            "total_records": 0,
            "embeddings_generated": 0,
            "duplicates_skipped": 0,
            "vectors_inserted": 0,
            "vectors_updated": 0,
            "failures": 0,
            "invalid_skipped": 0,
            "total_ingestion_time": 0.0
        }

    def _generate_deterministic_id(self, source: str, text: str) -> str:
        """Generate a deterministic ID based on the source and the text content."""
        import uuid
        content = f"{source}::{text}"
        return str(uuid.uuid5(uuid.NAMESPACE_DNS, content))

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
        """Parse, clean, embed, and upload a single file."""
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
                # Generate deterministic ID
                text = raw.get("text", "")
                source = raw.get("source", dataset_name)
                det_id = self._generate_deterministic_id(source, text)
                
                norm = NormalizedDatasetRecord(
                    id=det_id,
                    category=raw.get("category", "Unknown"),
                    subcategory=raw.get("subcategory", "Unknown"),
                    severity=raw.get("severity", "MEDIUM"),
                    owasp=raw.get("owasp", "Unknown"),
                    text=text,
                    source=source,
                    tags=raw.get("tags", [])
                )
                normalized_records.append(norm)
                self.stats["total_records"] += 1
            except Exception as e:
                logger.error(f"Failed to parse record in {file_path}: {e}")
                self.stats["failures"] += 1

        if not normalized_records:
            return

        # Clean batch
        clean_result = self.cleaner.clean_batch(normalized_records)
        valid_records: list[NormalizedDatasetRecord] = clean_result["cleaned_records"]
        
        # Update stats
        # We treat cleaner's duplicates as duplicate skipping
        self.stats["duplicates_skipped"] += clean_result["stats"]["duplicates_removed"]
        self.stats["invalid_skipped"] += clean_result["stats"]["invalid_skipped"]
        
        if not valid_records:
            return
            
        # Determine which ones already exist vs new
        ids_to_check = [r.id for r in valid_records]
        existing_ids = await self.repository.check_existing_ids(ids_to_check)
        
        new_records = []
        updated_records = []
        for r in valid_records:
            if r.id in existing_ids:
                updated_records.append(r)
            else:
                new_records.append(r)
                
        texts = [r.text for r in valid_records]
        try:
            # Batch embedding generation
            embeddings = await self.embedding_service.generate_embedding(texts)
            if not isinstance(embeddings, list) or len(embeddings) == 0:
                if not isinstance(embeddings[0], list):
                    embeddings = [embeddings]
            
            self.stats["embeddings_generated"] += len(valid_records)
            
            metadata_list = [self._map_to_vector_metadata(r) for r in valid_records]
            
            # Batch upload vectors (Qdrant's upsert will insert new and update existing automatically)
            await self.repository.store_attack_patterns(vectors=embeddings, metadata_list=metadata_list)
            
            self.stats["vectors_inserted"] += len(new_records)
            self.stats["vectors_updated"] += len(updated_records)
            
        except Exception as e:
            logger.error(f"Failed to embed/store records for {file_path}: {e}")
            self.stats["failures"] += len(valid_records)

    async def run(self) -> dict:
        """Run the full ingestion pipeline."""
        logger.info(f"Starting ingestion pipeline from {self.data_path}")
        start_time = time.time()
        
        if not self.data_path.exists():
            logger.error(f"Data path does not exist: {self.data_path}")
            return self.stats

        await self.embedding_service.initialize()
        await self.repository.initialize()
        
        # We look for json files in processed directory
        for json_file in self.data_path.glob("*.json"):
            dataset_name = json_file.stem.replace("_normalized", "")
            logger.info(f"Processing {json_file}")
            await self._process_file(dataset_name, json_file)
            self.stats["datasets_processed"] += 1
            
        self.stats["total_ingestion_time"] = round(time.time() - start_time, 2)
        return self.stats
