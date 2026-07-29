"""Knowledge Manager."""
import logging
import os
from typing import Any, Dict

from backend.agents.security_agent.services.knowledge_ingestion_service import KnowledgeIngestionService
from backend.agents.security_agent.repositories.knowledge_repository import KnowledgeRepository

logger = logging.getLogger(__name__)

class KnowledgeManager:
    """Orchestrates dataset loading, version tracking, and synchronization."""

    def __init__(self, repository: KnowledgeRepository, ingestion_service: KnowledgeIngestionService) -> None:
        self.repository = repository
        self.ingestion_service = ingestion_service
        # In a real system, this would be persisted to a DB or local file
        self._current_version = "0.0.0"

    async def initialize(self) -> None:
        """Initialize the manager and ensure the repository is ready."""
        await self.repository.initialize()

    async def sync_dataset(self, filepath: str, version: str) -> Dict[str, Any]:
        """
        Synchronize a dataset into the knowledge base if the version is newer.
        """
        if not os.path.exists(filepath):
            logger.error(f"Dataset file not found: {filepath}")
            return {"status": "error", "message": "File not found"}

        if self._is_newer_version(version, self._current_version):
            logger.info(f"New dataset version detected: {version}. Triggering ingestion.")
            try:
                result = await self.ingestion_service.ingest_file(filepath, dataset_version=version)
                if result.get("status") == "success":
                    self._current_version = version
                return result
            except Exception as e:
                logger.error(f"Failed to sync dataset {filepath}: {e}")
                return {"status": "error", "message": str(e)}
        else:
            logger.info(f"Dataset version {version} is not newer than current {self._current_version}. Skipping.")
            return {"status": "skipped", "message": "Already up to date"}

    def _is_newer_version(self, new_version: str, current_version: str) -> bool:
        """Basic semantic version comparison (e.g., '1.0.1' > '1.0.0')."""
        def parse_version(v: str) -> tuple:
            try:
                return tuple(map(int, v.split('.')))
            except ValueError:
                return (0, 0, 0)
        return parse_version(new_version) > parse_version(current_version)

    def health(self) -> dict[str, Any]:
        """Health check for the knowledge manager."""
        return {
            "status": "healthy",
            "current_dataset_version": self._current_version,
            "repository": self.repository.health()
        }
