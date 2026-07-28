import time
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Request, status

from app.api.deps import get_app_settings
from app.core.config import Settings
from app.schemas.base import APIResponse
from app.schemas.health import HealthResponse

router = APIRouter()

# Service start timestamp for uptime calculation
START_TIME = time.time()


@router.get(
    "/health",
    response_model=APIResponse[HealthResponse],
    status_code=status.HTTP_200_OK,
    summary="System Health Check",
    description="Returns the operational status, uptime, and system metadata for Trust-Agent.",
)
async def get_health_status(
    request: Request,
    settings: Settings = Depends(get_app_settings),
) -> APIResponse[HealthResponse]:
    """
    Health check endpoint returning standardized status schema.
    """
    uptime_seconds = round(time.time() - START_TIME, 2)
    health_payload = HealthResponse(
        status="healthy",
        app_name=settings.APP_NAME,
        version="0.1.0",
        environment=settings.ENVIRONMENT,
        timestamp=datetime.now(timezone.utc),
        uptime_seconds=uptime_seconds,
    )
    return APIResponse.ok(data=health_payload)
