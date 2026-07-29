"""Agent Registry Module."""
from typing import List, Dict, Any, Optional
from backend.shared.interfaces import BaseAgent
from backend.agents.orchestrator.models.domain import AgentMetadata

class AgentRegistry:
    """Single source of truth for registered agents."""
    
    def __init__(self):
        self._agents: Dict[str, BaseAgent] = {}
        self._metadata: Dict[str, AgentMetadata] = {}
        
    def register(self, name: str, agent: BaseAgent) -> None:
        """Registers a BaseAgent compatible agent."""
        self._agents[name] = agent
        # Cache metadata
        version = agent.version() if hasattr(agent, 'version') else "unknown"
        caps = agent.capabilities() if hasattr(agent, 'capabilities') else {}
        self._metadata[name] = AgentMetadata(name=name, version=version, capabilities=caps)
        
    def deregister(self, name: str) -> None:
        """Removes an agent."""
        self._agents.pop(name, None)
        self._metadata.pop(name, None)
        
    def get_agent(self, name: str) -> Optional[BaseAgent]:
        """Retrieves an active agent instance."""
        return self._agents.get(name)
        
    def list_agents(self) -> List[str]:
        """Returns list of registered agent names."""
        return list(self._agents.keys())
        
    def get_metadata(self, name: str) -> Optional[AgentMetadata]:
        return self._metadata.get(name)
