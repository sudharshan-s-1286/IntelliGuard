import asyncio
import time
from typing import Any, Dict, List, Optional, Union

from shared.logger import get_logger
from shared.interfaces import BaseDetector, DetectorResult

logger = get_logger(__name__)


class AnalysisPipeline:
    """
    Analysis Pipeline abstraction.
    
    Coordinates dynamic detector registration and manages execution policies.
    Executes enabled detectors concurrently using asyncio.gather while preserving
    detector contracts, error resilience, and output result ordering.
    """

    def __init__(self, detectors: Optional[List[BaseDetector]] = None) -> None:
        self._detectors: Dict[str, BaseDetector] = {}
        if detectors:
            for detector in detectors:
                self.register_detector(detector)

    def register_detector(self, detector: BaseDetector) -> None:
        """
        Dynamically registers a detector instance with the pipeline.
        """
        if not isinstance(detector, BaseDetector):
            raise ValueError(f"Detector must inherit from BaseDetector, got {type(detector)}")
        
        self._detectors[detector.name] = detector
        logger.info(f"Registered detector '{detector.name}' (v{detector.version}) in pipeline")

    def unregister_detector(self, detector_name: str) -> None:
        """
        Removes a detector from the pipeline by its unique name.
        """
        if detector_name in self._detectors:
            del self._detectors[detector_name]
            logger.info(f"Unregistered detector '{detector_name}' from pipeline")

    def get_detectors(self) -> List[BaseDetector]:
        """
        Returns all currently registered detectors.
        """
        return list(self._detectors.values())

    async def _run_detector(
        self, detector: BaseDetector, prompt: str, metadata: Optional[Dict[str, Any]]
    ) -> Optional[DetectorResult]:
        """
        Helper coroutine executing a single detector safely with readiness checks,
        latency tracking, and error resilience fallback.
        Returns None if the detector reports itself as not ready.
        """
        start_time = time.perf_counter()
        try:
            is_ready = await detector.is_ready()
            if not is_ready:
                logger.warning(f"Detector '{detector.name}' reported not ready, skipping")
                return None

            result = await detector.analyze(prompt=prompt, metadata=metadata)
            if result.execution_time_ms == 0.0:
                result.execution_time_ms = round((time.perf_counter() - start_time) * 1000, 2)
            return result

        except Exception as exc:
            logger.error(
                f"Error executing detector '{detector.name}': {str(exc)}",
                exc_info=True,
            )
            execution_time = round((time.perf_counter() - start_time) * 1000, 2)
            return DetectorResult(
                detector_name=detector.name,
                is_triggered=False,
                score=100.0,
                findings=[],
                execution_time_ms=execution_time,
                metadata={"error": str(exc)},
            )

    async def execute(
        self, prompt: str, metadata: Optional[Dict[str, Any]] = None
    ) -> List[DetectorResult]:
        """
        Executes all active, enabled detectors concurrently against the target prompt
        using asyncio.gather while preserving original registration ordering and error resilience.
        """
        active_detectors = [d for d in self._detectors.values() if d.is_enabled]

        if not active_detectors:
            logger.debug("No active detectors registered in pipeline execution run")
            return []

        # Launch concurrent task execution for all active detectors
        tasks = [
            self._run_detector(detector, prompt=prompt, metadata=metadata)
            for detector in active_detectors
        ]

        # Gather results concurrently
        raw_results: List[Union[Optional[DetectorResult], BaseException]] = await asyncio.gather(
            *tasks, return_exceptions=True
        )

        results: List[DetectorResult] = []
        for i, res in enumerate(raw_results):
            if isinstance(res, DetectorResult):
                results.append(res)
            elif isinstance(res, Exception):
                detector = active_detectors[i]
                logger.error(f"Unhandled exception in detector '{detector.name}': {str(res)}")
                results.append(
                    DetectorResult(
                        detector_name=detector.name,
                        is_triggered=False,
                        score=100.0,
                        findings=[],
                        execution_time_ms=0.0,
                        metadata={"error": str(res)},
                    )
                )

        return results


from datetime import datetime, timezone
from typing import List, Optional
import uuid

from agents.trust_agent.decision import ComplianceEngine
from agents.trust_agent.remediation import ExplainabilityEngine
from shared.logger import get_logger
from agents.trust_agent.scorer import TrustScoreEngine
from shared.interfaces import BaseDetector, DetectorResult, FindingDetail
from agents.trust_agent.schemas import TrustAnalysisRequest, TrustAnalysisResponse

logger = get_logger(__name__)


class TrustAgent:
    """
    Trust Agent Core Orchestrator.
    
    Coordinates trust analysis requests across registered detection modules via the AnalysisPipeline.
    Aggregates detector findings, calculates overall trust scores, and enforces enterprise compliance policy decisions.
    Designed for zero-touch detector additions following Clean Architecture.
    """

    def __init__(
        self,
        pipeline: Optional[AnalysisPipeline] = None,
        compliance_engine: Optional[ComplianceEngine] = None,
        trust_score_engine: Optional[TrustScoreEngine] = None,
        explainability_engine: Optional[ExplainabilityEngine] = None,
        audit_logger: Optional[Any] = None,
    ) -> None:
        self.pipeline = pipeline or AnalysisPipeline()
        self.compliance_engine = compliance_engine or ComplianceEngine()
        self.trust_score_engine = trust_score_engine or TrustScoreEngine()
        self.explainability_engine = explainability_engine or ExplainabilityEngine()
        self.audit_logger = audit_logger
        logger.info("TrustAgent orchestrator initialized with ComplianceEngine, TrustScoreEngine, and ExplainabilityEngine")

    def register_detector(self, detector: BaseDetector) -> None:
        """
        Registers a new detector with the underlying analysis pipeline.
        """
        self.pipeline.register_detector(detector)

    def unregister_detector(self, detector_name: str) -> None:
        """
        Unregisters a detector from the underlying analysis pipeline.
        """
        self.pipeline.unregister_detector(detector_name)

    async def analyze(
        self, request: TrustAnalysisRequest, request_id: Optional[str] = None
    ) -> TrustAnalysisResponse:
        """
        Orchestrates full trust evaluation pipeline for an incoming request prompt.
        
        1. Invokes AnalysisPipeline execution.
        2. Aggregates findings from active detectors.
        3. Computes Trust Score and Risk Level via TrustScoreEngine.
        4. Evaluates compliance policy rules via ComplianceEngine.
        5. Generates human-readable report via ExplainabilityEngine.
        6. Returns unified TrustAnalysisResponse.
        """
        req_id = request_id or str(uuid.uuid4())
        logger.info(f"Starting trust analysis for request [{req_id}]")
        process_start = time.perf_counter()

        # Execute detector pipeline
        detector_results: List[DetectorResult] = await self.pipeline.execute(
            prompt=request.prompt, metadata=request.metadata
        )

        # Aggregate findings
        all_findings: List[FindingDetail] = []
        for result in detector_results:
            all_findings.extend(result.findings)

        # Determine trust score and risk level
        score_explanation = self.trust_score_engine.calculate(findings=all_findings)
        trust_score_final = score_explanation.base_score - score_explanation.total_deduction

        # Enforce compliance policy decision
        compliance_res = self.compliance_engine.evaluate(
            trust_score=trust_score_final, findings=all_findings
        )

        # Generate Explainability Report
        explainability_report = self.explainability_engine.generate_report(
            findings=all_findings,
            score_explanation=score_explanation,
            compliance_decision=compliance_res["decision"],
            policy_id=compliance_res["policy_id"],
        )

        # Construct response
        response = TrustAnalysisResponse(
            request_id=req_id,
            timestamp=datetime.now(timezone.utc),
            overall_status=score_explanation.risk_level,
            compliance_decision=compliance_res["decision"],
            policy_id=compliance_res["policy_id"],
            trust_score=trust_score_final,
            score_explanation=score_explanation,
            explainability_report=explainability_report,
            findings=all_findings,
        )

        processing_duration_ms = (time.perf_counter() - process_start) * 1000

        if self.audit_logger is not None:
            try:
                await self.audit_logger.record(
                    request_id=req_id,
                    prompt_length=len(request.prompt),
                    trust_score=trust_score_final,
                    overall_status=score_explanation.risk_level.value,
                    compliance_decision=compliance_res["decision"].value,
                    policy_id=compliance_res["policy_id"],
                    total_findings=len(all_findings),
                    detector_results=detector_results,
                    processing_duration_ms=processing_duration_ms,
                    metadata=request.metadata or {},
                )
            except Exception:  # noqa: BLE001
                logger.warning("Audit recording failed", exc_info=True)

        logger.info(
            f"Completed trust analysis for request [{req_id}] -> Status: {response.overall_status.value}, Score: {response.trust_score}, Decision: {response.compliance_decision}"
        )
        return response


