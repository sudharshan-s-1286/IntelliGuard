import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class RecommendationEngine:
    """
    Engine to generate actionable recommendations based on detected compliance violations.
    """

    # Mapping of finding types/details to specific recommendation actions.
    # Note: keys here should map somewhat flexibly to what the detectors output.
    RECOMMENDATION_MAPPINGS = {
        "EMAIL": "Mask Email",
        "PHONE": "Mask Phone Number",
        "AADHAAR": "Redact Aadhaar Number",
        "SSN": "Redact SSN",
        "PASSPORT": "Redact Passport Number",
        "CREDIT_CARD": "Mask Credit Card",
        "BANK_ACCOUNT": "Mask Bank Account",
        
        "AWS_ACCESS_KEY": "Remove API Keys",
        "JWT_TOKEN": "Remove Bearer Tokens",
        "BEARER_TOKEN": "Remove Bearer Tokens",
        "API_KEY": "Remove API Keys",
        "SSH_KEY": "Remove SSH Keys",
        "PASSWORD": "Remove Passwords",
        "SECRET": "Remove Secrets",
        "DB_CONNECTION_STRING": "Remove Database Connection Strings",
        
        "MEDICAL_INFORMATION": "Redact Medical Information",
        "DIAGNOSIS": "Redact Medical Information",
        "TREATMENT": "Redact Medical Information",
        "PATIENT_IDENTIFIERS": "Redact Medical Information",
        
        "HARASSMENT": "Remove Toxic Content",
        "HATE_SPEECH": "Remove Toxic Content",
        "VIOLENCE": "Remove Toxic Content",
        "THREATS": "Remove Toxic Content",
        
        "LICENSE-SENSITIVE CODE": "Review License Compatibility",
        "COPYRIGHT WARNINGS": "Review Copyright Notices",
        "LARGE COPIED PASSAGES": "Remove Copied Passages",
        "EXCESSIVE QUOTATIONS": "Reduce Quotations"
    }

    def generate_recommendations(self, findings: List[Dict[str, Any]], risk_decision: str = None) -> List[str]:
        """
        Generates a deduplicated list of recommendations based on findings.
        
        Args:
            findings: List of dictionary findings from detectors.
            risk_decision: Optional string representing the overall risk decision (e.g. 'BLOCK', 'REVIEW').
            
        Returns:
            A list of unique recommendation strings.
        """
        recommendations = set()
        
        for finding in findings:
            # Findings can have 'type' or 'details' or 'category' depending on the detector
            finding_type = finding.get("type") or finding.get("details") or finding.get("category") or ""
            finding_type = str(finding_type).upper().strip()
            
            # Check for direct mapping
            matched = False
            for key, rec in self.RECOMMENDATION_MAPPINGS.items():
                if key in finding_type or finding_type in key:
                    recommendations.add(rec)
                    matched = True
                    break
            
            # Fallback for critical/high issues without specific mapping
            if not matched:
                severity = str(finding.get("severity", "")).upper()
                if severity in ["CRITICAL", "HIGH"]:
                    recommendations.add("Remove Confidential Text")

        # Include "Request Human Review" if decision is REVIEW or BLOCK, or if there are critical/high items
        # that warranted a review regardless.
        if risk_decision in ["REVIEW", "BLOCK"]:
            recommendations.add("Request Human Review")
        elif any(str(f.get("severity", "")).upper() in ["CRITICAL", "HIGH"] for f in findings):
            recommendations.add("Request Human Review")
            
        final_list = list(recommendations)
        # Sort to ensure deterministic output for tests
        final_list.sort()
        
        logger.info(f"Generated {len(final_list)} recommendations.")
        return final_list
