import asyncio
import logging
import sys
from pathlib import Path

from agents.security_agent.ai.embeddings import EmbeddingService
from agents.security_agent.datasets.ingestion.pipeline import DatasetIngestionPipeline
from agents.security_agent.repositories.knowledge_repository import KnowledgeRepository
from agents.security_agent.repositories.qdrant_service import QdrantService
from agents.security_agent.services.cache_service import CacheService
from agents.security_agent.services.model_loader import ModelLoader

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
    processed_data_path = base_dir / "datasets" / "processed"
    
    # Run pipeline
    pipeline = DatasetIngestionPipeline(
        embedding_service=embedding_service,
        repository=knowledge_repository,
        data_path=str(processed_data_path)
    )
    
    try:
        stats = await pipeline.run()
        
        print("\n" + "="*50)
        print("INGESTION SUMMARY")
        print("="*50)
        print(f"Total records processed: {stats.get('total_records', 0)}")
        print(f"Embeddings generated:    {stats.get('embeddings_generated', 0)}")
        print(f"Duplicates skipped:      {stats.get('duplicates_skipped', 0)}")
        print(f"Vectors inserted:        {stats.get('vectors_inserted', 0)}")
        print(f"Vectors updated:         {stats.get('vectors_updated', 0)}")
        print(f"Failed records:          {stats.get('failures', 0)}")
        print(f"Total ingestion time:    {stats.get('total_ingestion_time', 0.0)} seconds")
        print("="*50 + "\n")
        
    except Exception as e:
        logger.error(f"Ingestion pipeline failed: {e}", exc_info=True)
        sys.exit(1)
        
    finally:
        await qdrant_service.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
