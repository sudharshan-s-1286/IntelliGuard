"""Audit Analytics Engine.

Provides analytical helper methods that aggregate data from the AuditStorage
for future dashboards, SIEM integrations, and compliance reporting.
"""

from .storage import AuditStorage


class AuditAnalytics:
    """Analyze stored audit events."""

    def __init__(self, storage: AuditStorage):
        """Initialize with storage."""
        self.storage = storage
        
    def get_events(self):
        """Retrieve all events."""
        return self.storage.get_all()

    def total_requests(self) -> int:
        """Return total requests count."""
        return len(self.get_events())
        
    def _count_by_decision(self, decision: str) -> int:
        return sum(1 for e in self.get_events() if e.decision == decision)
        
    def blocked_requests(self) -> int:
        """Return blocked requests count."""
        return self._count_by_decision("BLOCK")
        
    def modified_requests(self) -> int:
        """Return modified requests count."""
        return self._count_by_decision("MODIFY")
        
    def allowed_requests(self) -> int:
        """Return allowed requests count."""
        return self._count_by_decision("ALLOW")
        
    def warning_requests(self) -> int:
        """Return warning requests count."""
        return self._count_by_decision("WARN")
        
    def average_risk_score(self) -> float:
        """Return average risk score."""
        events = self.get_events()
        if not events:
            return 0.0
        return round(sum(e.risk_score for e in events) / len(events), 2)
        
    def average_processing_time(self) -> float:
        """Return average processing time."""
        events = self.get_events()
        if not events:
            return 0.0
        return round(sum(e.processing_time_ms for e in events) / len(events), 2)
        
    def attack_frequency(self) -> dict[str, int]:
        """Return frequency of attacks."""
        freq = {}
        for e in self.get_events():
            for attack in e.detected_attacks:
                freq[attack] = freq.get(attack, 0) + 1
        return dict(sorted(freq.items(), key=lambda item: item[1], reverse=True))
        
    def top_detected_attacks(self) -> list[str]:
        """Return top detected attacks."""
        freq = self.attack_frequency()
        return list(freq.keys())
        
    def decision_distribution(self) -> dict[str, int]:
        """Return decision distribution."""
        return {
            "ALLOW": self.allowed_requests(),
            "WARN": self.warning_requests(),
            "MODIFY": self.modified_requests(),
            "BLOCK": self.blocked_requests()
        }
        
    def get_security_summary(self) -> dict:
        """Provide a security summary for analytical dashboards."""
        top_attacks = self.top_detected_attacks()
        return {
            "total_requests": self.total_requests(),
            "blocked": self.blocked_requests(),
            "modified": self.modified_requests(),
            "warnings": self.warning_requests(),
            "allowed": self.allowed_requests(),
            "average_risk_score": self.average_risk_score(),
            "top_attack": top_attacks[0] if top_attacks else None
        }
