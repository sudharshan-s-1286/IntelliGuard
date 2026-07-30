"""Agent Entry Point."""
import logging
import time
from typing import Any

from agents.security_agent.detectors.decision_engine import DecisionEngine
from agents.security_agent.detectors.risk_scorer import calculate_risk_score
from agents.security_agent.detectors.semantic_detector import SemanticDetector
from agents.security_agent.llm.classifier import LLMClassifier
from agents.security_agent.models.domain import RiskScore
from agents.security_agent.reporting.generator import ReportGenerator
from agents.security_agent.utils.telemetry import AuditLogger, MetricsRegistry
from agents.security_agent.validators.request_validator import parse_prompt

logger = logging.getLogger(__name__)

class AgentStatus:
    SUCCESS = "SUCCESS"
    ERROR = "ERROR"

from pydantic import BaseModel


class AgentResponse(BaseModel):
    agent: str
    status: str
    version: str
    processing_time_ms: float
    result: dict | None = None
    metadata: dict | None = None
    error_code: str | None = None
    message: str | None = None

class SecurityAgent:
    """
    Security Agent implementation.
    Acts as the facade for the security API, orchestrating the Enterprise Pipeline:
    DecisionEngine -> LLM Fallback -> RiskScorer -> ReportGenerator
    """
    def __init__(self):
        self._start_time = time.time()
        
        # Telemetry
        self.audit_logger = AuditLogger()
        self.metrics = MetricsRegistry()
        
        # Subsystems
        self.semantic_detector = None
        self.decision_engine = None
        self.llm_classifier = None
        self.report_generator = ReportGenerator(agent_version=self.version())

    @property
    def name(self) -> str:
        return "security_agent"

    def version(self) -> str:
        return "1.0.0"


    def _metadata(self) -> dict:
        return {"architecture": "hybrid_async"}

    async def initialize(self) -> None:
        """Initialize external connections (Qdrant, LLM clients)."""
        logger.info("Initializing Enterprise Security Agent...")
        
        from agents.security_agent.ai.embeddings import EmbeddingService
        from agents.security_agent.repositories.knowledge_repository import (
            KnowledgeRepository,
        )
        from agents.security_agent.repositories.qdrant_service import (
            QdrantService,
        )
        from agents.security_agent.services.cache_service import CacheService
        from agents.security_agent.services.model_loader import ModelLoader

        model_loader = ModelLoader()
        cache_service = CacheService()
        embedding_service = EmbeddingService(model_loader=model_loader, cache_service=cache_service)
        await embedding_service.initialize()
        
        qdrant_service = QdrantService()
        repository = KnowledgeRepository(qdrant_service=qdrant_service)
        await repository.initialize()
        
        self.semantic_detector = SemanticDetector(
            embedding_service=embedding_service,
            repository=repository
        )
        
        if hasattr(self.semantic_detector, "initialize"):
            await self.semantic_detector.initialize()
            
        self.decision_engine = DecisionEngine(self.semantic_detector)
        self.llm_classifier = LLMClassifier()
        logger.info("Security Agent successfully initialized.")

    async def validate(self, request: Any) -> None:
        pass

    async def process(self, request: Any) -> Any:
        self.metrics.increment("total_requests")
        process_start = time.time()

        try:
            prompt = request.prompt if hasattr(request, "prompt") else str(request)
            result_dict = await self.analyze(prompt)
            
            process_time_ms = (time.time() - process_start) * 1000
            self.metrics.increment("successful_requests")
            self.metrics.record_time(process_time_ms)
            
            return AgentResponse(
                agent="SecurityAgent",
                status=AgentStatus.SUCCESS,
                version=self.version(),
                processing_time_ms=process_time_ms,
                result=result_dict,
                metadata=self._metadata()
            )
        except Exception as e:
            logger.exception("[SecurityAgent] Process failed:")
            self.metrics.increment("failed_requests")
            process_time_ms = (time.time() - process_start) * 1000
            
            self.audit_logger.log_event("AGENT_ERROR", {"error": str(e), "latency_ms": process_time_ms})
            
            return AgentResponse(
                agent="SecurityAgent",
                status=AgentStatus.ERROR,
                version=self.version(),
                processing_time_ms=process_time_ms,
                error_code="SECURITY_ANALYSIS_FAILED",
                message=str(e)
            )

    async def analyze(self, prompt: str) -> dict:
        start_time = time.time()

        parsed = parse_prompt(prompt)
        normalized_prompt = parsed["normalized"]
        was_encoded = parsed.get("was_encoded", False)

        # 1. Orchestrate Standard Detectors
        detection_result = await self.decision_engine.analyze(normalized_prompt)
        logger.warning(f"DEBUG(4): detection result before risk scoring: {len(detection_result.findings)} findings.")

        # 2. LLM Fallback (if ambiguity or conflict exists)
        if detection_result.routing.needs_llm:
            self.metrics.increment("llm_invocations")
            try:
                llm_result = await self.llm_classifier.classify(normalized_prompt, detection_result.findings)
                # Append LLM findings, replace severity based on LLM output
                detection_result.findings.extend(llm_result.findings)
                detection_result.explainability.extend(llm_result.explainability)
            except Exception as e:
                self.metrics.increment("llm_failures")
                logger.error(f"LLM Classification failed, proceeding with baseline findings: {e}")

        # 3. Final Risk Scoring
        risk_assessment = calculate_risk_score(detection_result.findings, was_encoded=was_encoded)
        logger.warning(f"DEBUG(5): final risk score calculation output: {risk_assessment}")
        
        # Inject the final risk score back into the DetectionResult so the ReportGenerator has it
        detection_result.risk_score = RiskScore(
            score=risk_assessment["risk_score"], 
            factors=[
                f"Confidence: {risk_assessment['confidence']}",
                f"Severity: {risk_assessment['severity']}"
            ]
        )

        # 4. Generate Standardized Report
        report = self.report_generator.generate(detection_result, prompt, was_encoded)
        
        # Override the legacy loosely typed fields with our robust calculations
        report.risk_category = risk_assessment["risk_category"]
        report.severity = risk_assessment["severity"]
        report.confidence = risk_assessment["confidence"]
        
        # Presentation logic: For safe prompts, hide intermediate findings from the attack summary
        if report.decision == "ALLOW" or report.risk_category == "Safe":
            report.attack_summary = {"Safe": {"confidence": 1.0, "detector": "DecisionEngine", "severity": 0.0}}
        else:
            report.attack_summary = risk_assessment["attack_summary"]

        duration_ms = (time.time() - start_time) * 1000

        # Extract semantic timing info if available
        emb_time = 0.0
        qdrant_time = 0.0
        retrieved_results = 0
        for finding in detection_result.findings:
            if finding.metadata:
                emb_time = max(emb_time, finding.metadata.get("embedding_time_ms", 0.0))
                qdrant_time = max(qdrant_time, finding.metadata.get("qdrant_time_ms", 0.0))
                if finding.detector in ("SemanticDetector", "Merged"):
                    retrieved_results += 1

        # 5. Audit Logging
        self.audit_logger.log_event("PROMPT_ANALYSIS", {
            "processing_time_ms": duration_ms,
            "embedding_time_ms": emb_time,
            "qdrant_time_ms": qdrant_time,
            "semantic_results_count": retrieved_results,
            "original_prompt": prompt,
            "detected_attacks": [f.threat.category for f in detection_result.findings],
            "risk_score": report.risk_score,
            "decision": report.decision,
            "used_llm": detection_result.routing.needs_llm,
            "agent_version": self.version()
        })

        return report.model_dump()

    async def cleanup(self) -> None:
        """Close external connections."""
        if self.semantic_detector and hasattr(self.semantic_detector, "cleanup"):
            await self.semantic_detector.cleanup()

    async def health_check(self) -> Any:
        return self.health()

    def health(self) -> dict[str, Any]:
        """Return the health status of the agent."""
        uptime_s = time.time() - self._start_time
        return {
            "status": "healthy",
            "uptime": f"{uptime_s:.2f}s",
            "version": self.version(),
            "metrics": self.metrics.get_metrics(),
            "checks": {
                "llm_classifier": self.llm_classifier.health() if self.llm_classifier else None
            }
        }
