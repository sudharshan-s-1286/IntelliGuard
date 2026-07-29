import os
from pathlib import Path

BASE_DIR = Path("/home/pranav/Desktop/IntelliGaurd/backend/agents/orchestrator")

def implement():
    # ---------------------------------------------------------
    # 1. Models
    # ---------------------------------------------------------
    models_content = '''"""Orchestrator domain models."""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class AgentMetadata(BaseModel):
    name: str
    version: str
    description: Optional[str] = None
    capabilities: Dict[str, Any] = {}

class AgentCapability(BaseModel):
    id: str
    description: str

class AgentHealth(BaseModel):
    status: str
    latency_ms: float
    last_check: str
    details: Dict[str, Any] = {}

class ExecutionContext(BaseModel):
    trace_id: str
    request_id: str
    metadata: Dict[str, Any] = {}

class RoutingDecision(BaseModel):
    selected_agents: List[str]
    strategy: str

class ExecutionResult(BaseModel):
    agent_name: str
    status: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    processing_time_ms: float = 0.0

class AggregatedResponse(BaseModel):
    trace_id: str
    global_risk_score: float
    global_decision: str
    security_findings: List[Any] = []
    privacy_findings: List[Any] = []
    trust_findings: List[Any] = []
    compliance_findings: List[Any] = []
    execution_summary: Dict[str, Any] = {}
    explainability: List[str] = []

class AgentStatus(BaseModel):
    state: str
    is_active: bool
'''
    (BASE_DIR / "models" / "domain.py").write_text(models_content)
    
    # ---------------------------------------------------------
    # 2. Config
    # ---------------------------------------------------------
    settings_content = '''"""Configuration settings for Orchestrator."""
import os

AGENT_TIMEOUT = int(os.getenv("AGENT_TIMEOUT", 10))
CONCURRENCY_LIMIT = int(os.getenv("CONCURRENCY_LIMIT", 5))
RETRY_COUNT = int(os.getenv("RETRY_COUNT", 3))
DISCOVERY_INTERVAL = int(os.getenv("DISCOVERY_INTERVAL", 60))
HEALTH_INTERVAL = int(os.getenv("HEALTH_INTERVAL", 30))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
METRICS_ENABLED = os.getenv("METRICS_ENABLED", "True").lower() == "true"
ROUTING_RULES = os.getenv("ROUTING_RULES", "default")
'''
    (BASE_DIR / "config" / "settings.py").write_text(settings_content)

    # ---------------------------------------------------------
    # 3. Context
    # ---------------------------------------------------------
    context_content = '''"""Context Management Module."""
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
'''
    (BASE_DIR / "utils" / "context.py").write_text(context_content)
    
    # ---------------------------------------------------------
    # 4. Logger
    # ---------------------------------------------------------
    logger_content = '''"""Structured Logging Module."""
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
'''
    (BASE_DIR / "utils" / "logger.py").write_text(logger_content)

    # ---------------------------------------------------------
    # 5. Registry
    # ---------------------------------------------------------
    registry_content = '''"""Agent Registry Module."""
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
'''
    (BASE_DIR / "registry" / "manager.py").write_text(registry_content)

    # ---------------------------------------------------------
    # 6. Discovery
    # ---------------------------------------------------------
    discovery_content = '''"""Agent Discovery Module."""
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
'''
    (BASE_DIR / "discovery" / "manager.py").write_text(discovery_content)
    
    # ---------------------------------------------------------
    # 7. Router
    # ---------------------------------------------------------
    router_content = '''"""Request Routing Module."""
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
'''
    (BASE_DIR / "router" / "manager.py").write_text(router_content)

    # ---------------------------------------------------------
    # 8. Scheduler
    # ---------------------------------------------------------
    scheduler_content = '''"""Task Scheduler Module."""
import asyncio
import time
from typing import Any, List
from backend.shared.interfaces import BaseAgent
from backend.shared.response_models import AgentResponse, AgentStatus as SharedAgentStatus
from backend.agents.orchestrator.models.domain import ExecutionResult
from backend.agents.orchestrator.utils.logger import OrchestratorLogger
from backend.agents.orchestrator.config import settings

logger = OrchestratorLogger(__name__)

class TaskScheduler:
    """Schedules concurrent agent execution with fault tolerance."""
    
    def __init__(self):
        self.timeout = settings.AGENT_TIMEOUT
        
    async def _execute_agent(self, name: str, agent: BaseAgent, request: Any) -> ExecutionResult:
        """Executes a single agent safely with timeout and retries."""
        start_time = time.time()
        for attempt in range(settings.RETRY_COUNT):
            try:
                # BaseAgent process is synchronous in its definition, 
                # but might be implemented asynchronously in child classes.
                # We check if it is a coroutine function.
                if asyncio.iscoroutinefunction(agent.process):
                    result = await asyncio.wait_for(agent.process(request), timeout=self.timeout)
                else:
                    # Run sync function in thread pool
                    result = await asyncio.wait_for(
                        asyncio.to_thread(agent.process, request), 
                        timeout=self.timeout
                    )
                
                duration = (time.time() - start_time) * 1000
                logger.info(f"Agent {name} succeeded", latency_ms=duration)
                
                # Normalize result
                if isinstance(result, AgentResponse):
                    data = result.model_dump()
                else:
                    data = {"raw": result}
                    
                return ExecutionResult(agent_name=name, status="SUCCESS", data=data, processing_time_ms=duration)
                
            except asyncio.TimeoutError:
                logger.error(f"Agent {name} timed out on attempt {attempt+1}")
            except Exception as e:
                logger.error(f"Agent {name} failed on attempt {attempt+1}: {str(e)}")
                
        # If we exit the loop, all attempts failed
        duration = (time.time() - start_time) * 1000
        return ExecutionResult(agent_name=name, status="ERROR", error="Max retries exceeded", processing_time_ms=duration)

    async def schedule(self, agent_map: dict[str, BaseAgent], request: Any) -> List[ExecutionResult]:
        """Concurrent execution of all requested agents."""
        tasks = [
            self._execute_agent(name, agent, request)
            for name, agent in agent_map.items()
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Safely extract results (though _execute_agent already catches exceptions)
        final_results = []
        for r in results:
            if isinstance(r, Exception):
                final_results.append(ExecutionResult(agent_name="unknown", status="CRITICAL_ERROR", error=str(r)))
            else:
                final_results.append(r)
        return final_results
'''
    (BASE_DIR / "scheduler" / "manager.py").write_text(scheduler_content)
    
    # ---------------------------------------------------------
    # 9. Aggregator
    # ---------------------------------------------------------
    aggregator_content = '''"""Response Aggregation Module."""
from typing import List
from backend.agents.orchestrator.models.domain import ExecutionResult, AggregatedResponse
from backend.agents.orchestrator.utils.context import ContextManager

class ResponseAggregator:
    """Aggregates results from multiple agents."""
    
    def __init__(self):
        self.context_manager = ContextManager()
        
    def aggregate(self, results: List[ExecutionResult]) -> AggregatedResponse:
        """Fuses multiple agent responses into one global response."""
        ctx = self.context_manager.get_context()
        trace_id = ctx.trace_id if ctx else "unknown"
        
        global_risk_score = 0.0
        decisions = []
        security_findings = []
        execution_summary = {}
        explainability = []
        
        for res in results:
            execution_summary[res.agent_name] = {
                "status": res.status,
                "processing_time_ms": res.processing_time_ms,
                "error": res.error
            }
            
            if res.status == "SUCCESS" and res.data:
                # Extract embedded SecurityAgentResponse fields
                agent_res = res.data.get("result", {}) or res.data
                
                if "risk_score" in agent_res:
                    score = float(agent_res["risk_score"])
                    global_risk_score = max(global_risk_score, score)
                    
                if "decision" in agent_res:
                    decisions.append(agent_res["decision"])
                    
                if "findings" in agent_res:
                    security_findings.extend(agent_res["findings"])
                    
                if "explanation" in agent_res:
                    explainability.append(f"[{res.agent_name}] {agent_res['explanation']}")
                    
        # Determine global decision
        global_decision = "ALLOW"
        if "BLOCK" in decisions:
            global_decision = "BLOCK"
        elif "FLAG" in decisions:
            global_decision = "FLAG"
            
        return AggregatedResponse(
            trace_id=trace_id,
            global_risk_score=global_risk_score,
            global_decision=global_decision,
            security_findings=security_findings,
            execution_summary=execution_summary,
            explainability=explainability
        )
'''
    (BASE_DIR / "aggregator" / "manager.py").write_text(aggregator_content)

    # ---------------------------------------------------------
    # 10. Health
    # ---------------------------------------------------------
    health_content = '''"""Health Monitoring Module."""
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
'''
    (BASE_DIR / "health" / "manager.py").write_text(health_content)

    # ---------------------------------------------------------
    # 11. Agent Entry Point (agent.py)
    # ---------------------------------------------------------
    agent_content = '''"""Orchestrator Agent Entry Point."""
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
'''
    (BASE_DIR / "agent.py").write_text(agent_content)
    
if __name__ == "__main__":
    implement()
    print("Implementation updated.")
