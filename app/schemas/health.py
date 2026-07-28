from datetime import datetime
from pydantic import BaseModel, Field


class SystemComponentStatus(BaseModel):
    """
    Subsystem health component status model.
    """

    status: str = Field(..., description="Component status: ok, degraded, or down")
    details: str = Field(default="", description="Additional health diagnostic message")


class HealthResponse(BaseModel):
    """
    Schema for system health check endpoint response payload.
    """

    status: str = Field(..., description="Overall system health status")
    app_name: str = Field(..., description="Name of the microservice")
    version: str = Field(..., description="Application semantic version")
    environment: str = Field(..., description="Runtime environment name")
    timestamp: datetime = Field(..., description="Server UTC ISO-8601 timestamp")
    uptime_seconds: float = Field(..., description="Seconds since application startup")
