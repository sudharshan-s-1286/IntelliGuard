"""Request Routing Module."""
from typing import Any, Dict
from backend.agents.orchestrator.models.domain import RoutingDecision
from backend.agents.orchestrator.registry.manager import AgentRegistry
from backend.agents.orchestrator.config import settings

class RequestRouter:
    """Routes requests to appropriate agents."""
    
    def __init__(self, registry: AgentRegistry):
        self.registry = registry
        
    def determine_route(self, request: Any, metadata: Dict[str, Any] = None) -> RoutingDecision:
        """Determine which agents should execute based on the payload."""
        available = self.registry.list_agents()
        
        # Simple routing rule based on metadata or settings
        # e.g., if metadata has "mode": "security_only", we only route to security_agent
        if metadata and metadata.get("mode") == "security_only":
            selected = [a for a in available if "security" in a]
        else:
            selected = available
            
        return RoutingDecision(
            selected_agents=selected,
            strategy="parallel"
        )
