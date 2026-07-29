"""Agent Discovery Module."""
import pkgutil
import importlib
import inspect
from typing import List
from backend.shared.interfaces import BaseAgent
from backend.agents.orchestrator.registry.manager import AgentRegistry
from backend.agents.orchestrator.utils.logger import OrchestratorLogger

logger = OrchestratorLogger(__name__)

class AgentDiscovery:
    """Discovers available agents."""
    
    def __init__(self, registry: AgentRegistry):
        self.registry = registry
        
    def discover_agents(self, namespace_package: str = "backend.agents") -> List[str]:
        """Dynamically scans a package for BaseAgent implementations."""
        discovered = []
        try:
            package = importlib.import_module(namespace_package)
        except ImportError:
            logger.error(f"Namespace {namespace_package} not found")
            return []

        prefix = package.__name__ + "."
        for _, modname, ispkg in pkgutil.iter_modules(package.__path__, prefix):
            # Skip orchestrator itself
            if "orchestrator" in modname:
                continue
            
            # Look for agent.py inside the package
            agent_mod_name = f"{modname}.agent"
            try:
                module = importlib.import_module(agent_mod_name)
                for name, obj in inspect.getmembers(module):
                    if inspect.isclass(obj) and issubclass(obj, BaseAgent) and obj is not BaseAgent:
                        # Instantiate the agent
                        agent_instance = obj()
                        agent_id = modname.split('.')[-1]
                        self.registry.register(agent_id, agent_instance)
                        discovered.append(agent_id)
                        logger.info(f"Discovered and registered agent: {agent_id}")
            except Exception as e:
                logger.error(f"Failed to load agent from {modname}: {str(e)}")
                
        return discovered
