"""
Audit Logging Module — Phase 11: Observability

Provides structured, asynchronous JSON audit logging for every trust analysis request.
Stores audit records in-memory (with configurable backend extensibility) and exposes
retrieval with pagination, filtering, and sorting capabilities.

Design Principles:
  - Completely independent of detectors, TrustAgent, and Compliance logic.
  - Thread-safe in-memory store using asyncio.Lock.
  - All fields are serializable to standard Python types for JSON persistence.
  - Pluggable: The AuditStore interface can be swapped for Redis, Postgres, etc.
"""

import asyncio
import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field

from shared.logger import get_logger

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Audit Record Schema
# ---------------------------------------------------------------------------


class DetectorAuditEntry(BaseModel):
    """
    Per-detector execution audit summary recorded alongside each analysis.
    """
    detector_name: str = Field(..., description="Name of the detector")
    execution_time_ms: float = Field(..., description="Detector execution latency in milliseconds")
    findings_count: int = Field(..., description="Number of findings produced by this detector")
    is_triggered: bool = Field(..., description="Whether the detector flagged any risk")


class AuditRecord(BaseModel):
    """
    Structured audit record produced for every trust analysis request.
    Captures full observability metadata for compliance, forensics, and monitoring.
    """
    audit_id: str = Field(default_factory=lambda: str(uuid4()), description="Unique audit entry identifier")
    request_id: str = Field(..., description="Originating trust analysis request ID")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp when the audit record was created",
    )
    prompt_length: int = Field(..., description="Character length of the analyzed prompt")
    trust_score: float = Field(..., description="Final trust score (0.0–100.0)")
    overall_status: str = Field(..., description="Aggregated risk level (e.g. SAFE, CRITICAL_RISK)")
    compliance_decision: str = Field(..., description="Compliance policy decision (ALLOW, BLOCK, etc.)")
    policy_id: str = Field(..., description="Identifier of the enforced compliance policy")
    total_findings: int = Field(..., description="Total number of findings across all detectors")
    detectors: List[DetectorAuditEntry] = Field(
        default_factory=list, description="Per-detector execution audit summaries"
    )
    processing_duration_ms: float = Field(
        ..., description="Total end-to-end analysis processing duration in milliseconds"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Optional contextual metadata from the original request"
    )


# ---------------------------------------------------------------------------
# Audit Store (In-Memory, Thread-Safe)
# ---------------------------------------------------------------------------


class AuditStore:
    """
    Thread-safe, in-memory storage backend for audit records.

    Designed as a pluggable interface — replace `_records` with a database
    cursor or Redis client to transition to a persistent backend without
    changing the AuditLogger public API.
    """

    def __init__(self) -> None:
        self._records: List[AuditRecord] = []
        self._lock = asyncio.Lock()

    async def append(self, record: AuditRecord) -> None:
        """Appends a new audit record to the store."""
        async with self._lock:
            self._records.append(record)
            logger.debug(
                f"[AuditStore] Recorded audit entry {record.audit_id} for request {record.request_id}"
            )

    async def query(
        self,
        *,
        compliance_decision: Optional[str] = None,
        overall_status: Optional[str] = None,
        min_trust_score: Optional[float] = None,
        max_trust_score: Optional[float] = None,
        sort_by: str = "timestamp",
        sort_desc: bool = True,
        page: int = 1,
        page_size: int = 20,
    ) -> Dict[str, Any]:
        """
        Queries audit records with optional filtering, sorting, and pagination.

        Args:
            compliance_decision: Filter by compliance decision string (e.g. "BLOCK").
            overall_status: Filter by overall_status string (e.g. "CRITICAL_RISK").
            min_trust_score: Include only records with trust_score >= this value.
            max_trust_score: Include only records with trust_score <= this value.
            sort_by: Field name to sort by. Supported: "timestamp", "trust_score", "total_findings".
            sort_desc: If True, sort descending (newest/highest first).
            page: 1-indexed page number.
            page_size: Maximum number of records per page.

        Returns:
            Dict with "total", "page", "page_size", "pages", and "records".
        """
        async with self._lock:
            filtered = list(self._records)

        # --- Filtering ---
        if compliance_decision:
            filtered = [r for r in filtered if r.compliance_decision == compliance_decision]
        if overall_status:
            filtered = [r for r in filtered if r.overall_status == overall_status]
        if min_trust_score is not None:
            filtered = [r for r in filtered if r.trust_score >= min_trust_score]
        if max_trust_score is not None:
            filtered = [r for r in filtered if r.trust_score <= max_trust_score]

        # --- Sorting ---
        valid_sort_fields = {"timestamp", "trust_score", "total_findings", "processing_duration_ms"}
        if sort_by not in valid_sort_fields:
            sort_by = "timestamp"

        filtered.sort(key=lambda r: getattr(r, sort_by), reverse=sort_desc)

        # --- Pagination ---
        total = len(filtered)
        page = max(1, page)
        page_size = max(1, min(page_size, 100))  # Cap page size at 100
        total_pages = max(1, (total + page_size - 1) // page_size)
        start = (page - 1) * page_size
        end = start + page_size
        page_records = filtered[start:end]

        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": total_pages,
            "records": page_records,
        }

    async def count(self) -> int:
        """Returns the total number of stored audit records."""
        async with self._lock:
            return len(self._records)

    async def clear(self) -> None:
        """Clears all audit records (for use in testing)."""
        async with self._lock:
            self._records.clear()


# ---------------------------------------------------------------------------
# Audit Logger (Facade)
# ---------------------------------------------------------------------------


class AuditLogger:
    """
    High-level facade for creating and persisting structured audit records.

    Called by TrustAgent after each analysis run. Decoupled from all
    detector, compliance, and scoring logic.
    """

    def __init__(self, store: Optional[AuditStore] = None) -> None:
        self.store = store or AuditStore()

    async def record(
        self,
        *,
        request_id: str,
        prompt_length: int,
        trust_score: float,
        overall_status: str,
        compliance_decision: str,
        policy_id: str,
        total_findings: int,
        detector_results: List[Any],
        processing_duration_ms: float,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AuditRecord:
        """
        Constructs and persists an AuditRecord from a completed analysis run.

        Args:
            request_id: The originating request ID from TrustAgent.
            prompt_length: Character length of the analyzed prompt.
            trust_score: Final trust score.
            overall_status: Risk level string from TrustRiskLevel enum.
            compliance_decision: Decision string from ComplianceDecision enum.
            policy_id: Policy identifier string.
            total_findings: Total findings count across all detectors.
            detector_results: List of DetectorResult objects from pipeline.
            processing_duration_ms: Total end-to-end latency in ms.
            metadata: Optional request metadata dict.

        Returns:
            The persisted AuditRecord instance.
        """
        detector_entries = [
            DetectorAuditEntry(
                detector_name=r.detector_name,
                execution_time_ms=r.execution_time_ms,
                findings_count=len(r.findings),
                is_triggered=r.is_triggered,
            )
            for r in detector_results
        ]

        record = AuditRecord(
            request_id=request_id,
            prompt_length=prompt_length,
            trust_score=trust_score,
            overall_status=overall_status,
            compliance_decision=compliance_decision,
            policy_id=policy_id,
            total_findings=total_findings,
            detectors=detector_entries,
            processing_duration_ms=processing_duration_ms,
            metadata=metadata or {},
        )

        await self.store.append(record)

        logger.info(
            json.dumps({
                "event": "audit_recorded",
                "audit_id": record.audit_id,
                "request_id": request_id,
                "trust_score": trust_score,
                "overall_status": overall_status,
                "compliance_decision": compliance_decision,
                "total_findings": total_findings,
                "processing_duration_ms": round(processing_duration_ms, 3),
            })
        )

        return record

    async def query(self, **kwargs: Any) -> Dict[str, Any]:
        """Delegates to AuditStore.query() with all supported filter/sort/page args."""
        return await self.store.query(**kwargs)

    async def count(self) -> int:
        """Returns total stored audit records count."""
        return await self.store.count()

"""
Dashboard Analytics Service — Phase 12

Computes all dashboard metrics from AuditStore data.
Completely stateless — reads from the store on each call.
Follows the Single Responsibility Principle: this service
only performs aggregation; it never writes audit records.

All heavy lifting happens in pure Python over the in-memory
list snapshot, keeping the code offline and dependency-free.
"""

from collections import defaultdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from agents.trust_agent.utils import AuditLogger, AuditRecord
from shared.logger import get_logger
from agents.trust_agent.schemas import (
    DecisionDistribution,
    DetectorStats,
    DetectorsResponse,
    FindingsMetrics,
    LatencyMetrics,
    MetricsResponse,
    OverviewResponse,
    RiskDistribution,
    TrendBucket,
    TrendsResponse,
    TrustScoreMetrics,
)

logger = get_logger(__name__)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _percentile(sorted_vals: List[float], p: float) -> float:
    """
    Calculates the p-th percentile of a pre-sorted list of floats.
    Returns 0.0 for empty lists. p should be in [0, 100].
    """
    if not sorted_vals:
        return 0.0
    idx = (p / 100) * (len(sorted_vals) - 1)
    lo = int(idx)
    hi = lo + 1
    if hi >= len(sorted_vals):
        return sorted_vals[-1]
    frac = idx - lo
    return round(sorted_vals[lo] + frac * (sorted_vals[hi] - sorted_vals[lo]), 3)


def _filter_by_date(
    records: List[AuditRecord],
    since: Optional[datetime],
    until: Optional[datetime],
) -> List[AuditRecord]:
    """Applies optional date-range filter to a record list."""
    if since:
        records = [r for r in records if r.timestamp >= since]
    if until:
        records = [r for r in records if r.timestamp <= until]
    return records


class DashboardService:
    """
    Stateless analytics service that aggregates AuditStore records
    into structured dashboard payloads.

    Injected with an AuditLogger so it can read from the shared store.
    Never writes records — read-only contract.
    """

    def __init__(self, audit_logger: AuditLogger) -> None:
        self._audit_logger = audit_logger

    async def _fetch_all(
        self,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
    ) -> List[AuditRecord]:
        """
        Fetches all records from the store, bypassing pagination,
        then applies optional date-range filtering.
        """
        # Retrieve a very large page to get all records.
        # AuditStore caps page_size at 100, so we grab total first.
        total = await self._audit_logger.count()
        if total == 0:
            return []

        result = await self._audit_logger.query(
            sort_by="timestamp",
            sort_desc=False,
            page=1,
            page_size=min(total, 100),
        )
        records: List[AuditRecord] = result["records"]

        # If the store has more than 100 records, paginate through remainder
        pages = result["pages"]
        for page_num in range(2, pages + 1):
            extra = await self._audit_logger.query(
                sort_by="timestamp",
                sort_desc=False,
                page=page_num,
                page_size=100,
            )
            records.extend(extra["records"])

        return _filter_by_date(records, since, until)

    async def get_overview(
        self,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
    ) -> OverviewResponse:
        """Computes the platform KPI overview snapshot."""
        records = await self._fetch_all(since, until)
        total = len(records)

        if total == 0:
            return OverviewResponse(
                total_requests=0,
                total_findings=0,
                average_trust_score=0.0,
                blocked_requests=0,
                flagged_requests=0,
                safe_requests=0,
                risk_distribution=RiskDistribution(),
                decision_distribution=DecisionDistribution(),
                average_processing_ms=0.0,
                generated_at=_now_iso(),
            )

        total_findings = sum(r.total_findings for r in records)
        avg_score = round(sum(r.trust_score for r in records) / total, 2)
        avg_ms = round(sum(r.processing_duration_ms for r in records) / total, 3)
        blocked = sum(1 for r in records if r.compliance_decision == "BLOCK")
        flagged = sum(1 for r in records if r.total_findings > 0)
        safe = sum(1 for r in records if r.overall_status == "SAFE")

        risk_dist = RiskDistribution(
            SAFE=sum(1 for r in records if r.overall_status == "SAFE"),
            LOW_RISK=sum(1 for r in records if r.overall_status == "LOW_RISK"),
            MEDIUM_RISK=sum(1 for r in records if r.overall_status == "MEDIUM_RISK"),
            HIGH_RISK=sum(1 for r in records if r.overall_status == "HIGH_RISK"),
            CRITICAL_RISK=sum(1 for r in records if r.overall_status == "CRITICAL_RISK"),
        )
        decision_dist = DecisionDistribution(
            ALLOW=sum(1 for r in records if r.compliance_decision == "ALLOW"),
            ALLOW_WITH_WARNING=sum(1 for r in records if r.compliance_decision == "ALLOW_WITH_WARNING"),
            REVIEW=sum(1 for r in records if r.compliance_decision == "REVIEW"),
            BLOCK=blocked,
        )

        return OverviewResponse(
            total_requests=total,
            total_findings=total_findings,
            average_trust_score=avg_score,
            blocked_requests=blocked,
            flagged_requests=flagged,
            safe_requests=safe,
            risk_distribution=risk_dist,
            decision_distribution=decision_dist,
            average_processing_ms=avg_ms,
            generated_at=_now_iso(),
        )

    async def get_metrics(
        self,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
    ) -> MetricsResponse:
        """Computes detailed statistical metrics over the dataset."""
        records = await self._fetch_all(since, until)
        total = len(records)
        now = _now_iso()

        if total == 0:
            return MetricsResponse(
                total_requests=0,
                trust_score=TrustScoreMetrics(min=0.0, max=0.0, mean=0.0, median=0.0, p10=0.0, p90=0.0),
                latency=LatencyMetrics(min_ms=0.0, max_ms=0.0, mean_ms=0.0, median_ms=0.0, p95_ms=0.0),
                findings=FindingsMetrics(total=0),
                generated_at=now,
            )

        # Trust score stats
        scores = sorted(r.trust_score for r in records)
        score_stats = TrustScoreMetrics(
            min=round(scores[0], 2),
            max=round(scores[-1], 2),
            mean=round(sum(scores) / total, 2),
            median=_percentile(scores, 50),
            p10=_percentile(scores, 10),
            p90=_percentile(scores, 90),
        )

        # Latency stats
        durations = sorted(r.processing_duration_ms for r in records)
        latency_stats = LatencyMetrics(
            min_ms=round(durations[0], 3),
            max_ms=round(durations[-1], 3),
            mean_ms=round(sum(durations) / total, 3),
            median_ms=_percentile(durations, 50),
            p95_ms=_percentile(durations, 95),
        )

        # Findings breakdown — we need to read per-detector data from AuditRecord.detectors
        total_findings = sum(r.total_findings for r in records)
        by_category: Dict[str, int] = defaultdict(int)
        by_severity: Dict[str, int] = defaultdict(int)

        # Since AuditRecord doesn't store per-finding severity (only counts per detector),
        # we build category prefix counts from detector names acting as proxies.
        # For severity: we don't store per-finding severity in AuditRecord by design (avoids
        # duplication with the main response). We instead report findings_count per detector.
        for r in records:
            for det in r.detectors:
                # Map detector names to category prefixes
                prefix = det.detector_name.replace("_detector", "").replace("_", ".")
                by_category[prefix] += det.findings_count

        findings_stats = FindingsMetrics(
            total=total_findings,
            by_category_prefix=dict(by_category),
            by_severity={},  # Severity detail not stored at audit level; available in live response
        )

        return MetricsResponse(
            total_requests=total,
            trust_score=score_stats,
            latency=latency_stats,
            findings=findings_stats,
            generated_at=now,
        )

    async def get_detector_stats(
        self,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
    ) -> DetectorsResponse:
        """Aggregates per-detector performance statistics."""
        records = await self._fetch_all(since, until)
        now = _now_iso()

        # Aggregate by detector name
        agg: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            "executions": 0,
            "triggers": 0,
            "findings": 0,
            "latencies": [],
        })

        for record in records:
            for det in record.detectors:
                entry = agg[det.detector_name]
                entry["executions"] += 1
                entry["triggers"] += int(det.is_triggered)
                entry["findings"] += det.findings_count
                entry["latencies"].append(det.execution_time_ms)

        detector_stats = []
        for det_name, data in sorted(agg.items()):
            lats = data["latencies"]
            execs = data["executions"]
            avg_ms = round(sum(lats) / len(lats), 3) if lats else 0.0
            max_ms = round(max(lats), 3) if lats else 0.0
            trigger_rate = round(data["triggers"] / execs, 4) if execs else 0.0

            detector_stats.append(DetectorStats(
                detector_name=det_name,
                total_executions=execs,
                total_triggers=data["triggers"],
                trigger_rate=trigger_rate,
                total_findings=data["findings"],
                avg_execution_ms=avg_ms,
                max_execution_ms=max_ms,
            ))

        return DetectorsResponse(detectors=detector_stats, generated_at=now)

    async def get_trends(
        self,
        granularity: str = "hour",
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
    ) -> TrendsResponse:
        """
        Produces time-series trend data bucketed by hour or day.

        Args:
            granularity: 'hour' or 'day'. Defaults to 'hour'.
            since: Optional start of date range.
            until: Optional end of date range.
        """
        records = await self._fetch_all(since, until)
        now = _now_iso()
        gran = granularity if granularity in ("hour", "day") else "hour"

        # Build buckets
        bucket_data: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            "total_requests": 0,
            "scores": [],
            "blocked_count": 0,
            "findings_count": 0,
        })

        for r in records:
            if gran == "hour":
                key = r.timestamp.strftime("%Y-%m-%dT%H")
            else:
                key = r.timestamp.strftime("%Y-%m-%d")

            bucket_data[key]["total_requests"] += 1
            bucket_data[key]["scores"].append(r.trust_score)
            bucket_data[key]["findings_count"] += r.total_findings
            if r.compliance_decision == "BLOCK":
                bucket_data[key]["blocked_count"] += 1

        buckets = []
        for bucket_key in sorted(bucket_data.keys()):
            entry = bucket_data[bucket_key]
            scores = entry["scores"]
            avg_score = round(sum(scores) / len(scores), 2) if scores else 0.0
            buckets.append(TrendBucket(
                bucket=bucket_key,
                total_requests=entry["total_requests"],
                avg_trust_score=avg_score,
                blocked_count=entry["blocked_count"],
                findings_count=entry["findings_count"],
            ))

        return TrendsResponse(granularity=gran, buckets=buckets, generated_at=now)

