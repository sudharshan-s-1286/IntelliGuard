from typing import Any, Dict, Optional
import pytest
from fastapi import status
from httpx import AsyncClient
from starlette.testclient import TestClient

from app.agents.pipeline import AnalysisPipeline
from app.agents.trust_agent import TrustAgent
from app.detectors.base import BaseDetector, DetectorResult, DetectorSeverity, FindingDetail
from app.schemas.trust import TrustAnalysisRequest


class MockTestDetector(BaseDetector):
    """
    Mock detector used to verify dynamic pipeline registration and findings aggregation.
    """

    @property
    def name(self) -> str:
        return "mock_test_detector"

    @property
    def version(self) -> str:
        return "1.0.0"

    async def analyze(
        self, prompt: str, metadata: Optional[Dict[str, Any]] = None
    ) -> DetectorResult:
        if "risk" in prompt.lower():
            return DetectorResult(
                detector_name=self.name,
                is_triggered=True,
                score=45.0,
                findings=[
                    FindingDetail(
                        detector_name=self.name,
                        category="mock_risk",
                        severity=DetectorSeverity.HIGH,
                        description="Test risk detected in prompt",
                        confidence_score=0.95,
                    )
                ],
                execution_time_ms=1.5,
            )
        return DetectorResult(
            detector_name=self.name,
            is_triggered=False,
            score=100.0,
            findings=[],
            execution_time_ms=1.0,
        )


def test_post_trust_analyze_endpoint_sync(sync_client: TestClient) -> None:
    """
    Tests POST /api/v1/trust/analyze endpoint with valid payload.
    """
    payload = {"prompt": "Hello Trust Agent"}
    response = sync_client.post("/api/v1/trust/analyze", json=payload)
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["success"] is True
    assert data["data"]["overall_status"] == "SAFE"
    assert data["data"]["trust_score"] == 100.0
    assert data["data"]["findings"] == []
    assert "request_id" in data["data"]
    assert "timestamp" in data["data"]


@pytest.mark.asyncio
async def test_post_trust_analyze_endpoint_async(async_client: AsyncClient) -> None:
    """
    Tests POST /api/v1/trust/analyze endpoint asynchronously.
    """
    payload = {"prompt": "Analyze this safe prompt", "metadata": {"user_id": "usr_123"}}
    response = await async_client.post("/api/v1/trust/analyze", json=payload)
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["success"] is True
    assert data["data"]["overall_status"] == "SAFE"
    assert data["data"]["trust_score"] == 100.0
    assert isinstance(data["data"]["findings"], list)


@pytest.mark.asyncio
async def test_post_trust_analyze_validation_failure(async_client: AsyncClient) -> None:
    """
    Tests POST /api/v1/trust/analyze with invalid empty prompt payload.
    """
    payload = {"prompt": ""}
    response = await async_client.post("/api/v1/trust/analyze", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "VALIDATION_ERROR"


@pytest.mark.asyncio
async def test_trust_agent_pipeline_with_mock_detector() -> None:
    """
    Unit test verifying TrustAgent orchestrator and AnalysisPipeline aggregation logic with a mock detector.
    """
    pipeline = AnalysisPipeline()
    detector = MockTestDetector()
    pipeline.register_detector(detector)

    agent = TrustAgent(pipeline=pipeline)

    # 1. Test clean prompt
    clean_req = TrustAnalysisRequest(prompt="This is a safe input prompt")
    res_clean = await agent.analyze(clean_req)
    assert res_clean.overall_status == "SAFE"
    assert res_clean.trust_score == 100.0
    assert len(res_clean.findings) == 0

    # 2. Test prompt triggering mock detector risk
    risk_req = TrustAnalysisRequest(prompt="This contains a risk keyword")
    res_risk = await agent.analyze(risk_req)
    assert res_risk.overall_status == "RISK_DETECTED"
    assert res_risk.trust_score == 45.0
    assert len(res_risk.findings) == 1
    assert res_risk.findings[0].detector_name == "mock_test_detector"
    assert res_risk.findings[0].severity == DetectorSeverity.HIGH


class SlowDetector(BaseDetector):
    def __init__(self, detector_name: str, delay: float = 0.1) -> None:
        self._name = detector_name
        self.delay = delay

    @property
    def name(self) -> str:
        return self._name

    @property
    def version(self) -> str:
        return "1.0.0"

    async def analyze(
        self, prompt: str, metadata: Optional[Dict[str, Any]] = None
    ) -> DetectorResult:
        import asyncio
        await asyncio.sleep(self.delay)
        return DetectorResult(
            detector_name=self.name,
            is_triggered=False,
            score=100.0,
            findings=[],
        )


class FailingDetector(BaseDetector):
    @property
    def name(self) -> str:
        return "failing_detector"

    @property
    def version(self) -> str:
        return "1.0.0"

    async def analyze(
        self, prompt: str, metadata: Optional[Dict[str, Any]] = None
    ) -> DetectorResult:
        raise RuntimeError("Simulated detector runtime exception")


class UnreadyDetector(BaseDetector):
    @property
    def name(self) -> str:
        return "unready_detector"

    @property
    def version(self) -> str:
        return "1.0.0"

    async def is_ready(self) -> bool:
        return False

    async def analyze(
        self, prompt: str, metadata: Optional[Dict[str, Any]] = None
    ) -> DetectorResult:
        return DetectorResult(
            detector_name=self.name,
            is_triggered=False,
            score=100.0,
        )


@pytest.mark.asyncio
async def test_concurrent_detector_execution_speed() -> None:
    """
    Verifies that multiple detectors run concurrently via asyncio.gather().
    Two detectors with 0.1s delays should complete in ~0.1s total (well under 0.2s).
    """
    import time
    pipeline = AnalysisPipeline()
    pipeline.register_detector(SlowDetector("slow_1", delay=0.1))
    pipeline.register_detector(SlowDetector("slow_2", delay=0.1))

    start = time.perf_counter()
    results = await pipeline.execute("Safe test prompt")
    elapsed = time.perf_counter() - start

    assert len(results) == 2
    # Concurrent execution total elapsed time should be close to 0.1s (and strictly under 0.18s)
    assert elapsed < 0.18, f"Pipeline executed sequentially! Took {elapsed:.2f}s instead of ~0.1s"


@pytest.mark.asyncio
async def test_failing_detector_does_not_stop_pipeline() -> None:
    """
    Verifies pipeline resilience: a failing detector logs error and returns fallback result,
    allowing healthy detectors to return their results cleanly.
    """
    pipeline = AnalysisPipeline()
    pipeline.register_detector(MockTestDetector())
    pipeline.register_detector(FailingDetector())

    results = await pipeline.execute("This contains a risk keyword")
    assert len(results) == 2

    # Verify first detector completed cleanly
    healthy_res = next(r for r in results if r.detector_name == "mock_test_detector")
    assert healthy_res.is_triggered is True

    # Verify failing detector returned fallback error result
    failing_res = next(r for r in results if r.detector_name == "failing_detector")
    assert failing_res.is_triggered is False
    assert "error" in failing_res.metadata
    assert "Simulated detector runtime exception" in failing_res.metadata["error"]


@pytest.mark.asyncio
async def test_unready_detector_skipped() -> None:
    """
    Verifies unready detectors (is_ready() == False) are skipped cleanly during concurrent execution.
    """
    pipeline = AnalysisPipeline()
    pipeline.register_detector(MockTestDetector())
    pipeline.register_detector(UnreadyDetector())

    results = await pipeline.execute("Safe test prompt")
    assert len(results) == 1
    assert results[0].detector_name == "mock_test_detector"

