"""Audit Storage.

Abstracts the persistence layer for Audit Events. Initially supports in-memory
and JSON file storage. Can be extended to databases like PostgreSQL or Elasticsearch.
"""
import json
import os

from .models import AuditEvent


class AuditStorage:
    """Provide storage for audit events."""

    def __init__(self, file_path: str = "audit_log.json"):
        """Initialize the storage."""
        self.events: list[AuditEvent] = []
        self.file_path = file_path
        
        # Load existing logs if available
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.events = [AuditEvent(**e) for e in data]
            except (FileNotFoundError, json.JSONDecodeError):
                pass

    def save(self, event: AuditEvent):
        """Save an event to storage."""
        self.events.append(event)
        # Flush to JSON (in production, this would be async or batched)
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump([e.model_dump() if hasattr(e, "model_dump") else e.dict() for e in self.events], f, indent=4)
        except OSError:
            pass # Fail silently so the agent doesn't crash
            
    def get_all(self) -> list[AuditEvent]:
        """Retrieve all stored events."""
        return self.events
