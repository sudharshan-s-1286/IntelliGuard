from datetime import datetime, timezone
from typing import List, Optional
import uuid

from app.agents.pipeline import AnalysisPipeline
from app.core.logging import get_logger
from app.detectors.base import BaseDetector, DetectorResult, FindingDetail
from app.schemas.trust import TrustAnalysisRequest, TrustAnalysisResponse

logger = get_logger(__name__)


class TrustAgent:
    """
    Trust Agent Core Orchestrator.
    
    Coordinates trust analysis requests across registered detection modules via the AnalysisPipeline.
    Aggregates detector findings, calculates overall trust scores, and generates unified response models.
    Designed for zero-touch detector additions following Clean Architecture.
    """

    def __init__(self, pipeline: Optional[AnalysisPipeline] = None) -> None:
        self.pipeline = pipeline or AnalysisPipeline()
        logger.info("TrustAgent orchestrator initialized")

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
        3. Determines overall trust status and score.
        4. Returns unified TrustAnalysisResponse.
        """
        req_id = request_id or str(uuid.uuid4())
        logger.info(f"Starting trust analysis for request [{req_id}]")

        # Execute detector pipeline
        detector_results: List[DetectorResult] = await self.pipeline.execute(
            prompt=request.prompt, metadata=request.metadata
        )

        # Aggregate findings and calculate scores
        all_findings: List[FindingDetail] = []
        is_any_triggered = False
        min_score = 100.0

        for result in detector_results:
            if result.is_triggered:
                is_any_triggered = True
            
            if result.score < min_score:
                min_score = result.score

            all_findings.extend(result.findings)

        # Determine overall status classification
        if is_any_triggered:
            overall_status = "RISK_DETECTED"
        else:
            overall_status = "SAFE"

        # Construct response
        response = TrustAnalysisResponse(
            request_id=req_id,
            timestamp=datetime.now(timezone.utc),
            overall_status=overall_status,
            trust_score=round(min_score, 2),
            findings=all_findings,
        )

        logger.info(
            f"Completed trust analysis for request [{req_id}] -> Status: {overall_status}, Score: {response.trust_score}"
        )
        return response
