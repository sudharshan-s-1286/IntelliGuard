import asyncio
import time
from typing import Any, Dict, List, Optional, Union

from app.core.logging import get_logger
from app.detectors.base import BaseDetector, DetectorResult

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

