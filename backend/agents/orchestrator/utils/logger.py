"""Structured Logging Module."""
import logging
import json
from datetime import datetime, UTC
from backend.agents.orchestrator.utils.context import ContextManager

class OrchestratorLogger:
    """Structured JSON Logger that automatically injects trace_id."""
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.context_manager = ContextManager()
        
    def _format(self, level: str, msg: str, **kwargs) -> str:
        ctx = self.context_manager.get_context()
        log_obj = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": level,
            "message": msg,
            "trace_id": ctx.trace_id if ctx else "NO_CONTEXT"
        }
        log_obj.update(kwargs)
        return json.dumps(log_obj)

    def info(self, msg: str, **kwargs):
        self.logger.info(self._format("INFO", msg, **kwargs))
        
    def error(self, msg: str, **kwargs):
        self.logger.error(self._format("ERROR", msg, **kwargs))
