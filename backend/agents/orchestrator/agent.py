"""Orchestrator Agent Entry Point."""
from typing import Any, Dict
import logging

from backend.agents.orchestrator.models.domain import AggregatedResponse
from backend.agents.orchestrator.registry.manager import AgentRegistry
from backend.agents.orchestrator.discovery.manager import AgentDiscovery
from backend.agents.orchestrator.router.manager import RequestRouter
from backend.agents.orchestrator.scheduler.manager import TaskScheduler
from backend.agents.orchestrator.aggregator.manager import ResponseAggregator
from backend.agents.orchestrator.health.manager import HealthMonitor
from backend.agents.orchestrator.utils.context import ContextManager
from backend.agents.orchestrator.utils.logger import OrchestratorLogger

class OrchestratorAgent:
    """
    Enterprise Orchestrator.
    Manages discovery, routing, execution, and aggregation of all sub-agents.
    """
    
    def __init__(self):
        self.registry = AgentRegistry()
        self.discovery = AgentDiscovery(self.registry)
        self.router = RequestRouter(self.registry)
        self.scheduler = TaskScheduler()
        self.aggregator = ResponseAggregator()
        self.health_monitor = HealthMonitor(self.registry)
        self.context_manager = ContextManager()
        self.logger = OrchestratorLogger(__name__)
        
    async def initialize(self) -> None:
        """Initialize orchestrator and discover agents."""
        self.logger.info("Initializing Orchestrator...")
        discovered = self.discovery.discover_agents()
        self.logger.info(f"Discovered agents: {discovered}")
        
    async def process(self, request: Any, metadata: Dict[str, Any] = None) -> AggregatedResponse:
        """Process incoming request, route to agents, and aggregate."""
        # 1. Establish Shared Context
        self.context_manager.create_context(metadata)
        self.logger.info("Received request for orchestration")
        
        # 2. Route
        route = self.router.determine_route(request, metadata)
        self.logger.info(f"Routing to: {route.selected_agents}")
        
        # 3. Resolve agents
        agent_map = {}
        for name in route.selected_agents:
            agent = self.registry.get_agent(name)
            if agent:
                agent_map[name] = agent
                
        # 4. Schedule concurrent execution
        results = await self.scheduler.schedule(agent_map, request)
        
        # 5. Aggregate
        aggregated = self.aggregator.aggregate(results)
        self.logger.info("Aggregation complete", risk_score=aggregated.global_risk_score)
        
        return aggregated
        
    def health(self) -> dict:
        """Return overall health of orchestrator and registered agents."""
        sub_health = self.health_monitor.check_health()
        is_healthy = all(h.status in ["OK", "healthy", "mock_healthy"] for h in sub_health.values())
        return {
            "status": "healthy" if is_healthy or not sub_health else "degraded",
            "agents": {k: v.model_dump() for k, v in sub_health.items()}
        }
