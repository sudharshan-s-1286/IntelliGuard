"""Response Aggregation Module."""
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
