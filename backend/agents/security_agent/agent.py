"""Security Agent Module.

Orchestrates the security analysis pipeline and implements the BaseAgent interface
for integration into the IntelliGuard multi-agent system.
"""
import logging
import os
import sys
import time
from datetime import UTC, datetime
from typing import Any

# Ensure we can import from shared
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from shared.enums import AgentStatus
from shared.interfaces import BaseAgent
from shared.response_models import AgentResponse

from .audit.logger import AuditLogger
from .config import REWRITE_TEMPLATES
from .decision import make_decision
from .detector import run_all_detectors
from .patterns import PATTERNS
from .prompt_parser import parse_prompt
from .remediation import remediate
from .schemas import SecurityAgentResponse
from .scorer import calculate_risk_score

logger = logging.getLogger(__name__)

class SecurityAgent(BaseAgent):
    """Main orchestrator class for the Security Agent."""
    
    def __init__(self):
        """Initialize the Security Agent."""
        self.audit_logger = AuditLogger()
        self._start_time = time.time()
        
        self._metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_processing_time_ms": 0.0,
            "last_request_time": None
        }
        
    def version(self) -> str:
        """Return the version of the agent."""
        return "1.0.0"
        
    def _metadata(self) -> dict[str, Any]:
        return {
            "agent": "SecurityAgent",
            "display_name": "AI Security Analysis Agent",
            "description": "Enterprise-grade prompt security and remediation engine.",
            "version": self.version(),
            "author": "IntelliGuard",
            "capabilities": [
                "Prompt Injection Detection",
                "Jailbreak Detection",
                "Risk Scoring",
                "Prompt Remediation",
                "Audit Logging"
            ]
        }
        
    def capabilities(self) -> dict[str, Any]:
        """Return the capabilities of the agent."""
        return {
            "detections": [
                "Prompt Injection",
                "Jailbreak",
                "System Prompt Extraction",
                "Role Escalation",
                "Instruction Override",
                "Tool Abuse",
                "Data Exfiltration",
                "Prompt Leakage",
                "Obfuscated Prompt Detection",
                "Encoding-based Attacks",
                "Multi-step Attack Chains",
                "Suspicious Command Patterns"
            ],
            "features": [
                "Risk Assessment",
                "Prompt Remediation",
                "Audit Logging",
                "Analytics"
            ]
        }
        
    def health(self) -> dict[str, Any]:
        """Return the health status of the agent."""
        uptime_s = time.time() - self._start_time
        return {
            "status": "healthy",
            "uptime": f"{uptime_s:.2f}s",
            "version": self.version(),
            "checks": {
                "detector": True,
                "scorer": True,
                "audit": True,
                "remediation": True
            }
        }
        
    def ready(self) -> dict[str, Any]:
        """Return readiness status and missing components."""
        missing = []
        if not PATTERNS:
            missing.append("PATTERNS")
        if not REWRITE_TEMPLATES:
            missing.append("REWRITE_TEMPLATES")
        if not self.audit_logger or not self.audit_logger.storage:
            missing.append("Audit Storage")
            
        return {
            "ready": len(missing) == 0,
            "missing_components": missing
        }
        
    def metrics(self) -> dict[str, Any]:
        """Return usage metrics for the agent."""
        total = self._metrics["total_requests"]
        avg_time = 0.0
        if total > 0:
            avg_time = self._metrics["total_processing_time_ms"] / total
            
        uptime_s = time.time() - self._start_time
        return {
            "total_requests": total,
            "successful_requests": self._metrics["successful_requests"],
            "failed_requests": self._metrics["failed_requests"],
            "average_processing_time_ms": round(avg_time, 2),
            "uptime_seconds": round(uptime_s, 2),
            "last_request_time": self._metrics["last_request_time"]
        }
        
    def process(self, request: Any) -> AgentResponse:
        """Public entry point for the Orchestrator."""
        self._metrics["total_requests"] += 1
        self._metrics["last_request_time"] = datetime.now(UTC).isoformat().replace('+00:00', 'Z')
        process_start = time.time()
        
        try:
            prompt = request.prompt if hasattr(request, "prompt") else str(request)
            
            # Step 1-6: Analyze
            result = self.analyze(prompt)
            
            process_time_ms = (time.time() - process_start) * 1000
            self._metrics["successful_requests"] += 1
            self._metrics["total_processing_time_ms"] += process_time_ms
            
            return AgentResponse(
                agent="SecurityAgent",
                status=AgentStatus.SUCCESS,
                version=self.version(),
                processing_time_ms=process_time_ms,
                result=result,
                metadata=self._metadata()
            )
        except Exception as e:
            logger.exception("[SecurityAgent] Process failed:")
            self._metrics["failed_requests"] += 1
            process_time_ms = (time.time() - process_start) * 1000
            return AgentResponse(
                agent="SecurityAgent",
                status=AgentStatus.ERROR,
                version=self.version(),
                processing_time_ms=process_time_ms,
                error_code="SECURITY_ANALYSIS_FAILED",
                message=str(e)
            )

    def analyze(self, prompt: str) -> dict:
        """Execute the full security analysis pipeline on a given prompt."""
        start_time = time.time()
        logger.info("[SecurityAgent] Analysis started.")
        
        # Step 1: Parse & Normalize
        parsed = parse_prompt(prompt)
        normalized_prompt = parsed["normalized"]
        was_encoded = parsed.get("was_encoded", False)
        
        # Step 2: Detect Attacks
        findings_dict = run_all_detectors(normalized_prompt, was_encoded=was_encoded)
        
        # Step 3: Calculate Risk Assessment
        assessment = calculate_risk_score(findings_dict)
        
        # Step 4: Make Explainable Decision
        decision_data = make_decision(assessment)
        
        # Step 5: Remediation Engine
        remediation_data = remediate(prompt, findings_dict, decision_data["decision"])
        
        # Format findings for the response
        formatted_findings = []
        detected_attacks = []
        matched_signatures = []
        for data in findings_dict.values():
            if data["detected"]:
                formatted_findings.append({
                    "detector": data["attack"],
                    "confidence": data["confidence"],
                    "severity": data["severity"],
                    "reason": data["reason"],
                    "matched_patterns": data.get("matched_patterns", [])
                })
                detected_attacks.append(data["attack"])
                matched_signatures.extend(data.get("matched_patterns", []))
                
        # Metrics and Logging
        duration_s = time.time() - start_time
        duration_ms = duration_s * 1000
        top_attacks = list(assessment["attack_summary"].keys())[:3]
        highest_priority_attack = top_attacks[0] if top_attacks else None
        
        logger.info(
            f"[SecurityAgent] Analysis finished in {duration_ms:.2f}ms. "
            f"Decision: {decision_data['decision']}, "
            f"Risk Score: {assessment['risk_score']}, "
            f"Detected Attacks: {len(detected_attacks)}, "
            f"Highest-priority attack: {highest_priority_attack}"
        )
                
        # Step 6: Audit Logging
        audit_event_data = {
            "processing_time_ms": duration_ms,
            "original_prompt": prompt,
            "normalized_prompt": normalized_prompt,
            "detected_attacks": detected_attacks,
            "matched_signatures": matched_signatures,
            "risk_score": assessment["risk_score"],
            "confidence": assessment["confidence"],
            "severity": assessment["severity"],
            "risk_category": assessment["risk_category"],
            "decision": decision_data["decision"],
            "remediation_applied": remediation_data["applied"],
            "safe_prompt": remediation_data["safe_prompt"],
            "explanation": decision_data["explanation"],
            "justification": decision_data["justification"],
            "recommended_action": decision_data["recommended_action"],
            "agent_version": self.version()
        }
        self.audit_logger.log_event(audit_event_data)
        
        # Step 7: Construct XAI Response
        response = SecurityAgentResponse(
            agent="SecurityAgent",
            risk_score=assessment["risk_score"],
            confidence=assessment["confidence"],
            severity=assessment["severity"],
            risk_category=assessment["risk_category"],
            decision=decision_data["decision"],
            findings=formatted_findings,
            attack_summary=assessment["attack_summary"],
            explanation=decision_data["explanation"],
            justification=decision_data["justification"],
            recommended_action=decision_data["recommended_action"],
            safe_prompt=remediation_data["safe_prompt"],
            remediation={
                "applied": remediation_data["applied"],
                "changes": remediation_data["changes"],
                "confidence": remediation_data["confidence"],
                "reason": remediation_data["reason"],
                "safe_prompt": remediation_data["safe_prompt"]
            }
        )
        
        return response.model_dump() if hasattr(response, "model_dump") else response.dict()
