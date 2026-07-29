"""Context Management Module."""
import contextvars
import uuid
from datetime import datetime, UTC
from typing import Dict, Any, Optional

from backend.agents.orchestrator.models.domain import ExecutionContext

# The thread-safe context variable
_execution_context: contextvars.ContextVar[Optional[ExecutionContext]] = contextvars.ContextVar(
    "execution_context", default=None
)

class ContextManager:
    """Manages shared execution context across agents."""
    
    def create_context(self, request_metadata: Dict[str, Any] = None) -> ExecutionContext:
        """Create and set a new execution context."""
        ctx = ExecutionContext(
            trace_id=str(uuid.uuid4()),
            request_id=str(uuid.uuid4()),
            metadata=request_metadata or {}
        )
        _execution_context.set(ctx)
        return ctx
        
    def get_context(self) -> Optional[ExecutionContext]:
        """Retrieve the current context."""
        return _execution_context.get()
