"""Health Monitoring Module."""
from typing import Dict, Any
import time
from backend.agents.orchestrator.models.domain import AgentHealth
from backend.agents.orchestrator.registry.manager import AgentRegistry

class HealthMonitor:
    """Monitors health of registered agents."""
    
    def __init__(self, registry: AgentRegistry):
        self.registry = registry
        
    def check_health(self) -> Dict[str, AgentHealth]:
        """Queries health from all registered agents."""
        health_status = {}
        for name in self.registry.list_agents():
            agent = self.registry.get_agent(name)
            start = time.time()
            try:
                res = agent.health() if hasattr(agent, 'health') else {"status": "unknown"}
                latency = (time.time() - start) * 1000
                health_status[name] = AgentHealth(
                    status=res.get("status", "unknown"),
                    latency_ms=latency,
                    last_check=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    details=res
                )
            except Exception as e:
                health_status[name] = AgentHealth(
                    status="ERROR",
                    latency_ms=0.0,
                    last_check=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    details={"error": str(e)}
                )
        return health_status
