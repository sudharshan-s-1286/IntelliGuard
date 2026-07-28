from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class ComplianceCheckRequest(BaseModel):
    text: str = Field(..., min_length=1, description="The content to check for compliance violations.")
    policies: Optional[List[str]] = Field(
        default=None, 
        description="Optional list of specific policy rules or standards to evaluate against (e.g., GDPR, HIPAA)."
    )

class ComplianceCheckResponse(BaseModel):
    status: str = Field(..., description="The final compliance status (e.g., Compliant, Non-Compliant).")
    score: int = Field(..., description="Overall computed risk score.")
    risk_level: str = Field(..., description="The risk level based on score (e.g., NONE, LOW, MEDIUM, HIGH, CRITICAL).")
    decision: str = Field(..., description="Actionable decision (e.g., ALLOW, WARNING, REVIEW, BLOCK).")
    violations: List[Dict[str, Any]] = Field(default_factory=list, description="A list of specific compliance findings and violations.")
    recommendations: List[str] = Field(default_factory=list, description="Actionable recommendations based on violations.")
    execution_time_ms: float = Field(..., description="Processing time of the compliance evaluation in milliseconds.")
