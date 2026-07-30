"""Decision Engine."""
import asyncio
import logging
from typing import Any

from agents.security_agent.config import settings
from agents.security_agent.detectors.rule_engine import run_all_detectors
from agents.security_agent.detectors.semantic_detector import SemanticDetector
from agents.security_agent.models.domain import (
    DetectionResult,
    Finding,
    Metadata,
    RiskScore,
    RoutingDecision,
    Threat,
    Recommendation
)

logger = logging.getLogger(__name__)

class DecisionEngine:
    """Orchestrates independent detectors, aggregates findings, and makes LLM routing decisions."""

    def __init__(self, semantic_detector: SemanticDetector) -> None:
        self.semantic_detector = semantic_detector
        self.llm_routing_threshold = settings.DECISION_LLM_ROUTING_THRESHOLD
        self.fusion_strategy = settings.DECISION_FUSION_STRATEGY
        self.route_on_conflict = settings.DECISION_LLM_ON_CONFLICT

    async def analyze(self, prompt: str) -> DetectionResult:
        """
        Orchestrate detectors and aggregate results.
        :param prompt: The input prompt.
        :return: A unified DetectionResult.
        """
        explainability = []
        logger.info("Decision Engine: Starting orchestration.")

        # 1. Execute detectors concurrently
        async def _run_rule_engine() -> list[Finding]:
            results_dict = run_all_detectors(prompt)
            return self._normalize_rule_output(results_dict)

        rule_findings, semantic_findings = await asyncio.gather(
            _run_rule_engine(),
            self.semantic_detector.evaluate(prompt)
        )
        
        logger.warning(f"DEBUG(1): rule engine findings count: {len(rule_findings)}")
        logger.warning(f"DEBUG(2): semantic retrieval results count: {len(semantic_findings)}")

        all_findings = rule_findings + semantic_findings

        if not all_findings:
            logger.info("No threats detected by any engine.")
            return DetectionResult(
                risk_score=RiskScore(score=0.0, factors=["No threats detected"]),
                findings=[],
                recommendations=[],
                metadata=Metadata(execution_time_ms=0.0, model_versions={}),
                routing=RoutingDecision(needs_llm=False, reason="No findings to investigate"),
                explainability=["No threats detected by Rule Engine or Semantic Detector."]
            )

        # 2. Result Aggregation & Duplicate Resolution
        recommendations = []
        merged_findings = self._resolve_duplicates(all_findings, explainability, recommendations)

        # 3. LLM Routing & Conflict Resolution
        needs_llm, reason = self._determine_routing(rule_findings, semantic_findings, merged_findings, explainability)

        # 4. Final Aggregation
        max_severity = max([f.severity for f in merged_findings], default=0.0)
        max_confidence = max([f.confidence for f in merged_findings], default=0.0)
        
        risk_placeholder = RiskScore(
            score=max_severity * max_confidence, # Simplified placeholder
            factors=["Risk scoring logic deferred", f"Max severity: {max_severity}"]
        )

        logger.info(f"Decision Engine: Outputting {len(merged_findings)} merged findings. Needs LLM: {needs_llm}")

        return DetectionResult(
            risk_score=risk_placeholder,
            findings=merged_findings,
            recommendations=recommendations,
            metadata=Metadata(execution_time_ms=0.0, model_versions={}),
            routing=RoutingDecision(needs_llm=needs_llm, reason=reason),
            explainability=explainability
        )

    def _normalize_rule_output(self, raw_results: dict[str, Any]) -> list[Finding]:
        """Convert Rule Engine dictionary output into Finding objects."""
        findings = []
        severity_map = {"CRITICAL": 1.0, "HIGH": 0.8, "MEDIUM": 0.5, "LOW": 0.2, "NONE": 0.0}
        
        for key, res in raw_results.items():
            if res.get("detected"):
                category = res.get("attack", "Unknown")
                raw_severity = str(res.get("severity", "LOW")).upper()
                mapped_severity = severity_map.get(raw_severity, 0.2)
                confidence = res.get("confidence", 0.5)
                
                findings.append(Finding(
                    threat=Threat(
                        category=category,
                        description="Known rule-based attack."
                    ),
                    severity=mapped_severity,
                    evidence=", ".join(res.get("matched_patterns", [])),
                    detector="RuleEngine",
                    confidence=confidence,
                    metadata=None
                ))
        return findings

    def _resolve_duplicates(self, findings: list[Finding], explainability: list[str], recommendations: list[Recommendation]) -> list[Finding]:
        """Merge findings with the same category across detectors."""
        grouped: dict[str, list[Finding]] = {}
        for f in findings:
            grouped.setdefault(f.threat.category, []).append(f)

        merged = []
        for category, group in grouped.items():
            if len(group) == 1:
                f = group[0]
                merged.append(f)
                explainability.append(f"[{category}] Detected exclusively by {f.detector} (Confidence: {f.confidence:.2f}).")
                if f.detector == "SemanticDetector" and f.metadata:
                    recommendations.append(Recommendation(
                        action=f"Review semantic match from {f.metadata.get('source_dataset')}",
                        priority="High" if f.severity >= 0.8 else "Medium"
                    ))
                continue

            detectors = [f.detector for f in group]
            has_rule = "RuleEngine" in detectors
            has_semantic = "SemanticDetector" in detectors

            if self.fusion_strategy == "weighted":
                # Combine independent confidences: P(A or B) = 1 - (1 - P(A)) * (1 - P(B))
                complement = 1.0
                for f in group:
                    complement *= (1.0 - f.confidence)
                fused_confidence = 1.0 - complement
            else:
                fused_confidence = max(f.confidence for f in group)

            # Increase confidence if both match
            if has_rule and has_semantic:
                fused_confidence = min(1.0, fused_confidence + 0.10)
                
            max_severity = max(f.severity for f in group)
            
            combined_evidence = " | ".join([f"[{f.detector}] {f.evidence}" for f in group if f.evidence])
            
            # Use metadata from semantic detector if present
            semantic_finding = next((f for f in group if f.detector == "SemanticDetector"), None)
            meta = semantic_finding.metadata if semantic_finding else None
            
            if has_rule and has_semantic:
                combined_desc = "Known rule-based attack corroborated by semantic similarity."
                if meta:
                    recommendations.append(Recommendation(
                        action=f"Review semantic match from {meta.get('source_dataset')} for corroborated rule-based attack",
                        priority="High"
                    ))
            else:
                combined_desc = " | ".join([f.threat.description for f in group])

            merged.append(Finding(
                threat=Threat(category=category, description=combined_desc),
                severity=max_severity,
                evidence=combined_evidence,
                detector="Merged",
                confidence=fused_confidence,
                metadata=meta
            ))
            
            explainability.append(
                f"[{category}] Duplicate resolved. Merged findings from {detectors}. "
                f"Fused Confidence: {fused_confidence:.2f}, Severity: {max_severity}."
            )
            
        return merged

    def _determine_routing(self, rule_findings: list[Finding], semantic_findings: list[Finding], merged_findings: list[Finding], explainability: list[str]) -> tuple[bool, str]:
        """Decide if the prompt needs to be routed to the LLM."""
        
        # 1. Check for low confidence / ambiguous results
        max_confidence = max([f.confidence for f in merged_findings], default=0.0)
        if 0.0 < max_confidence < self.llm_routing_threshold:
            reason = f"Maximum confidence ({max_confidence:.2f}) is below routing threshold ({self.llm_routing_threshold})."
            explainability.append(f"Routing Decision: Route to LLM. {reason}")
            return True, reason

        # 2. Check for conflicts if enabled
        if self.route_on_conflict:
            rule_cats = {f.threat.category for f in rule_findings}
            sem_cats = {f.threat.category for f in semantic_findings}
            
            # If there's a complete disagreement on high severity threats, trigger LLM
            # Define high severity as severity >= 0.8
            high_sev_sem = {f.threat.category for f in semantic_findings if f.severity >= 0.8}
            high_sev_rule = {f.threat.category for f in rule_findings if f.severity >= 0.8}
            
            for cat in high_sev_sem:
                if cat not in rule_cats:
                    reason = f"Conflict: SemanticDetector found high-severity {cat} but RuleEngine missed it."
                    explainability.append(f"Routing Decision: Route to LLM. {reason}")
                    return True, reason
                    
            for cat in high_sev_rule:
                if cat not in sem_cats and semantic_findings: # Only if semantic ran but found nothing matching
                    reason = f"Conflict: RuleEngine found high-severity {cat} but SemanticDetector missed it."
                    explainability.append(f"Routing Decision: Route to LLM. {reason}")
                    return True, reason

        explainability.append("Routing Decision: LLM not required. High confidence consensus reached.")
        return False, "High confidence consensus reached."
