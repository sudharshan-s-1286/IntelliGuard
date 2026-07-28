import asyncio
import logging
import time
from typing import Dict, Any

from shared.logger import setup_logging
from shared.utils import mask_sensitive_value
from shared.response_models import ComplianceCheckRequest, ComplianceCheckResponse

from agents.compliance_agent.detector import (
    PIIDetector,
    ConfidentialDetector,
    ToxicityDetector,
    RegulationChecker,
    CopyrightDetector
)
from agents.compliance_agent.decision import PolicyEngine
from agents.compliance_agent.scorer import RiskScoringEngine
from agents.compliance_agent.remediation import RecommendationEngine

logger = logging.getLogger(__name__)

class ComplianceAgent:
    """
    Agent responsible for orchestrating compliance scans over input documents.
    This class utilizes all detectors and core engines to evaluate compliance.
    """
    def __init__(self) -> None:
        logger.info("Initializing ComplianceAgent and all underlying detectors/engines.")
        
        # Detectors
        self.pii_detector = PIIDetector()
        self.confidential_detector = ConfidentialDetector()
        self.toxicity_detector = ToxicityDetector()
        self.regulation_checker = RegulationChecker()
        self.copyright_detector = CopyrightDetector()
        
        # Core Engines
        self.policy_engine = PolicyEngine()
        self.risk_scorer = RiskScoringEngine()
        self.recommendation_engine = RecommendationEngine()

    def health(self) -> Dict[str, Any]:
        return {"status": "ok"}

    def is_ready(self) -> bool:
        return True

    async def analyze(self, request: ComplianceCheckRequest, context: Dict[str, Any] = None) -> ComplianceCheckResponse:
        """
        Orchestrates the entire compliance evaluation pipeline.
        
        Args:
            request: The API request containing text and optional policies.
            context: Optional contextual data for the policy engine.
            
        Returns:
            The final compliance report mapped to the API schema.
        """
        start_time = time.perf_counter()
        
        if context is None:
            context = {}
        if request.policies:
            context["policies"] = request.policies
            
        logger.info("Starting compliance analysis.")
        
        # 1. Run detectors concurrently in thread pool since they are CPU bound (regex)
        tasks = [
            asyncio.to_thread(self.pii_detector.detect, request.text),
            asyncio.to_thread(self.confidential_detector.detect, request.text),
            asyncio.to_thread(self.toxicity_detector.detect, request.text),
            asyncio.to_thread(self.regulation_checker.detect, request.text),
            asyncio.to_thread(self.copyright_detector.detect, request.text),
        ]
        
        results = await asyncio.gather(*tasks)
        
        # 2. Aggregate all findings
        aggregated_findings = []
        for result in results:
            aggregated_findings.extend(result)
            
        # 3. Policy Engine Evaluation
        finding_texts = [request.text]
        finding_texts.extend([f.get("text", "") or f.get("matched", "") for f in aggregated_findings])
        finding_texts.extend([f.get("type", "") or f.get("details", "") or f.get("category", "") for f in aggregated_findings])
        
        policy_violations = self.policy_engine.evaluate(context, finding_texts)
        
        for pv in policy_violations:
            aggregated_findings.append({
                "type": "POLICY_VIOLATION",
                "details": f"Rule {pv.get('id')} violated",
                "severity": pv.get("severity", "MEDIUM")
            })

        # 4. Risk Scorer Evaluation
        risk_result = self.risk_scorer.evaluate(aggregated_findings)
        decision = risk_result["decision"]
        
        # 5. Recommendation Engine
        recommendations = self.recommendation_engine.generate_recommendations(aggregated_findings, risk_decision=decision)
        
        # Mask sensitive data before returning
        for v in aggregated_findings:
            if "text" in v:
                v["text"] = mask_sensitive_value(v["text"], v.get("type", ""))
            elif "matched" in v:
                v_type = v.get("type") or v.get("category") or v.get("regulation") or ""
                v["matched"] = mask_sensitive_value(v["matched"], v_type)
        
        # 6. Final Compliance Report
        status = "Non-Compliant" if decision in ["BLOCK", "REVIEW"] else "Compliant"
        execution_time_ms = (time.perf_counter() - start_time) * 1000.0
        
        response = ComplianceCheckResponse(
            status=status,
            score=risk_result["compliance_score"],
            risk_level=risk_result["risk_level"],
            decision=decision,
            violations=aggregated_findings,
            recommendations=recommendations,
            execution_time_ms=execution_time_ms
        )
        
        logger.info(f"Compliance analysis completed in {execution_time_ms:.2f}ms. Status: {status}, Score: {risk_result['compliance_score']}")
        return response
