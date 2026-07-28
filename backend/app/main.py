import logging
import os
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api import trust
from app.api.trust import get_trust_agent

logger = logging.getLogger(__name__)

app = FastAPI(title="IntelliGuard Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info("Incoming request: %s %s", request.method, request.url.path)
    response = await call_next(request)
    logger.info("Response: %s %s status=%d", request.method, request.url.path, response.status_code)
    return response


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    logger.error("Validation error: %s", exc.errors())
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": {"code": "VALIDATION_ERROR", "message": "Validation error", "details": exc.errors()},
        },
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled exception")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": {"code": "INTERNAL_ERROR", "message": str(exc)},
        },
    )


app.include_router(trust.router)


@app.get("/health")
async def health_check():
    logger.info("Health check requested")
    return {
        "status": "online",
        "service": "Trust Agent",
        "agent": "TrustAgent",
    }


@app.get("/api/trust/health")
async def trust_health_alt():
    logger.info("Trust health check requested at /api/trust/health")
    return {
        "status": "online",
        "service": "Trust Agent",
        "agent": "TrustAgent",
    }


@app.get("/api/v1/dashboard/overview")
async def dashboard_overview(since: Optional[str] = None, until: Optional[str] = None):
    agent = get_trust_agent()
    try:
        overview = await agent.dashboard_service.get_overview(
            since=datetime.fromisoformat(since) if since else None,
            until=datetime.fromisoformat(until) if until else None,
        )
        return {
            "success": True,
            "data": overview.model_dump(),
            "meta": {"since": since, "until": until},
        }
    except Exception as exc:
        logger.exception("Dashboard overview failed")
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/api/v1/dashboard/metrics")
async def dashboard_metrics(since: Optional[str] = None, until: Optional[str] = None):
    agent = get_trust_agent()
    try:
        metrics = await agent.dashboard_service.get_metrics(
            since=datetime.fromisoformat(since) if since else None,
            until=datetime.fromisoformat(until) if until else None,
        )
        return {
            "success": True,
            "data": metrics.model_dump(),
            "meta": {"since": since, "until": until},
        }
    except Exception as exc:
        logger.exception("Dashboard metrics failed")
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/api/v1/dashboard/detectors")
async def dashboard_detectors(since: Optional[str] = None, until: Optional[str] = None):
    agent = get_trust_agent()
    try:
        stats = await agent.dashboard_service.get_detector_stats(
            since=datetime.fromisoformat(since) if since else None,
            until=datetime.fromisoformat(until) if until else None,
        )
        return {
            "success": True,
            "data": stats.model_dump(),
            "meta": {"since": since, "until": until},
        }
    except Exception as exc:
        logger.exception("Dashboard detectors failed")
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/api/v1/dashboard/trends")
async def dashboard_trends(granularity: str = "hour", since: Optional[str] = None, until: Optional[str] = None):
    agent = get_trust_agent()
    try:
        trends = await agent.dashboard_service.get_trends(
            granularity=granularity,
            since=datetime.fromisoformat(since) if since else None,
            until=datetime.fromisoformat(until) if until else None,
        )
        return {
            "success": True,
            "data": trends.model_dump(),
            "meta": {"since": since, "until": until},
        }
    except Exception as exc:
        logger.exception("Dashboard trends failed")
        raise HTTPException(status_code=500, detail=str(exc))
