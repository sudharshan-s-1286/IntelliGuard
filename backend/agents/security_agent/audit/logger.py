"""Audit Logger.

Handles structured logging of security analysis events. Protects the main Agent
thread from logging failures.
"""
import logging

from .models import AuditEvent
from .storage import AuditStorage
from .utils import truncate_string

structured_logger = logging.getLogger("SecurityAudit")
structured_logger.setLevel(logging.INFO)

class AuditLogger:
    """Provide structured logging for audit events."""

    def __init__(self):
        """Initialize the audit logger."""
        self.storage = AuditStorage()
        
    def log_event(self, event_data: dict) -> None:
        """Create and store an AuditEvent. Fail silently to prevent agent crashes."""
        try:
            # Truncate potentially huge prompts for safety
            if "original_prompt" in event_data:
                event_data["original_prompt"] = truncate_string(event_data["original_prompt"])
            if "normalized_prompt" in event_data:
                event_data["normalized_prompt"] = truncate_string(event_data["normalized_prompt"])
                
            event = AuditEvent(**event_data)
            self.storage.save(event)
            
            # Emit structured JSON log
            event_json = event.model_dump_json() if hasattr(event, "model_dump_json") else event.json()
            structured_logger.info(f"AUDIT_EVENT: {event_json}")
        except Exception as e:  # noqa: BLE001
            # Fallback safe logging
            structured_logger.error(f"Audit logging failed: {e!s}")
