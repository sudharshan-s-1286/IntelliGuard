import datetime
import json
import logging
import time
from pathlib import Path

from tqdm import tqdm
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
            "new_records": 0,
            "existing_records": 0,
            "embeddings_generated": 0,
            "metadata_updates": 0,
            "vector_inserts": 0,
            "duplicates_skipped": 0,
            "invalid_skipped": 0,
            "failures": 0,
            "total_ingestion_time": 0.0,
            "cache_hits": 0,
            "cache_misses": 0
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
        
        self.stats["duplicates_skipped"] += clean_result["stats"]["duplicates_removed"]
        self.stats["invalid_skipped"] += clean_result["stats"]["invalid_skipped"]
        
        if not valid_records:
            return
            
        # Determine which ones already exist vs new
        ids_to_check = [r.id for r in valid_records]
        existing_ids = await self.repository.check_existing_ids(ids_to_check)
        
        new_records = []
        existing_records = []
        for r in valid_records:
            if r.id in existing_ids:
                existing_records.append(r)
            else:
                new_records.append(r)
                
        self.stats["new_records"] += len(new_records)
        self.stats["existing_records"] += len(existing_records)
        
        # 1. Update Existing Records (Metadata only)
        if existing_records:
            metadata_list = [self._map_to_vector_metadata(r) for r in existing_records]
            try:
                await self.repository.update_attack_metadata(metadata_list)
                self.stats["metadata_updates"] += len(existing_records)
            except Exception as e:
                logger.error(f"Failed to update metadata for {file_path}: {e}")
                self.stats["failures"] += len(existing_records)

        # 2. Insert New Records (Embeddings + Vector insert)
        if new_records:
            texts = [r.text for r in new_records]
            try:
                # We can trace cache hits inside generate_embedding indirectly, but for now we track generated.
                embeddings = await self.embedding_service.generate_embedding(texts)
                if not isinstance(embeddings, list):
                    embeddings = [embeddings]
                if len(embeddings) > 0 and not isinstance(embeddings[0], list):
                    embeddings = [embeddings]
                
                self.stats["embeddings_generated"] += len(new_records)
                
                metadata_list = [self._map_to_vector_metadata(r) for r in new_records]
                
                await self.repository.store_attack_patterns(vectors=embeddings, metadata_list=metadata_list)
                self.stats["vector_inserts"] += len(new_records)
                
            except Exception as e:
                logger.error(f"Failed to embed/store new records for {file_path}: {e}")
                self.stats["failures"] += len(new_records)

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
        files = list(self.data_path.glob("*.json"))
        
        # Add tqdm for dataset progress
        for json_file in tqdm(files, desc="Processing Datasets"):
            dataset_name = json_file.stem.replace("_normalized", "")
            logger.info(f"Processing {json_file}")
            await self._process_file(dataset_name, json_file)
            self.stats["datasets_processed"] += 1
            
        end_time = time.time()
        self.stats["total_ingestion_time"] = round(end_time - start_time, 2)
        
        # Check cache metrics if available
        cache_health = self.embedding_service.cache_service.health()
        keys_count = cache_health.get("keys_count", 0)
        
        # Compute throughput
        throughput = 0.0
        if self.stats["total_ingestion_time"] > 0:
            throughput = self.stats["total_records"] / self.stats["total_ingestion_time"]
            
        print("\n" + "="*50)
        print("INGESTION SUMMARY")
        print("="*50)
        print(f"Datasets Processed   : {self.stats['datasets_processed']}")
        print(f"Total Records        : {self.stats['total_records']}")
        print(f"New Records          : {self.stats['new_records']}")
        print(f"Existing Records     : {self.stats['existing_records']}")
        print(f"Embeddings Generated : {self.stats['embeddings_generated']}")
        print(f"Cache Size           : {keys_count}")
        print(f"Metadata Updates     : {self.stats['metadata_updates']}")
        print(f"Vector Inserts       : {self.stats['vector_inserts']}")
        print(f"Duplicates Skipped   : {self.stats['duplicates_skipped']}")
        print(f"Failures             : {self.stats['failures']}")
        print(f"Elapsed Time         : {self.stats['total_ingestion_time']:.2f}s")
        print(f"Overall Throughput   : {throughput:.2f} records/sec")
        print("="*50 + "\n")
        
        return self.stats
