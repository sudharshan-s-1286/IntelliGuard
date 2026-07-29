"""Task Scheduler Module."""
import asyncio
import time
import inspect
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
                if inspect.iscoroutinefunction(agent.process):
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
