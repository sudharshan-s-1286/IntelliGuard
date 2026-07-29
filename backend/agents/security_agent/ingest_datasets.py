import asyncio
import logging
import sys
from pathlib import Path

from backend.agents.security_agent.ai.embeddings import EmbeddingService
from backend.agents.security_agent.datasets.ingestion.pipeline import DatasetIngestionPipeline
from backend.agents.security_agent.repositories.knowledge_repository import KnowledgeRepository
from backend.agents.security_agent.repositories.qdrant_service import QdrantService
from backend.agents.security_agent.services.cache_service import CacheService
from backend.agents.security_agent.services.model_loader import ModelLoader

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def main():
    logger.info("Initializing dataset ingestion process...")
    
    # Initialize dependencies
    cache_service = CacheService()
    model_loader = ModelLoader()
    embedding_service = EmbeddingService(model_loader=model_loader, cache_service=cache_service)
    
    qdrant_service = QdrantService()
    knowledge_repository = KnowledgeRepository(qdrant_service=qdrant_service)
    
    # Set paths
    base_dir = Path(__file__).parent
    raw_data_path = base_dir / "datasets" / "raw"
    
    # Run pipeline
    pipeline = DatasetIngestionPipeline(
        embedding_service=embedding_service,
        repository=knowledge_repository,
        raw_data_path=str(raw_data_path)
    )
    
    try:
        stats = await pipeline.run()
        
        print("\n" + "="*50)
        print("INGESTION SUMMARY")
        print("="*50)
        print(f"Datasets processed:   {stats.get('datasets_processed', 0)}")
        print(f"Records imported:     {stats.get('records_imported', 0)}")
        print(f"Duplicates removed:   {stats.get('duplicates_removed', 0)}")
        print(f"Invalid skipped:      {stats.get('invalid_skipped', 0)}")
        print(f"Failures:             {stats.get('failures', 0)}")
        print("="*50 + "\n")
        
    except Exception as e:
        logger.error(f"Ingestion pipeline failed: {e}", exc_info=True)
        sys.exit(1)
        
    finally:
        await qdrant_service.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
