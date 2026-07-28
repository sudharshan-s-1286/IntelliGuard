from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI, Depends, Request, status
from fastapi.responses import RedirectResponse
import uvicorn

from app.api.deps import get_app_settings
from app.api.v1.endpoints.health import get_health_status
from app.api.v1.router import api_v1_router
from app.core.config import Settings, settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import get_logger, setup_logging
from app.core.middleware import register_middlewares
from app.schemas.base import APIResponse
from app.schemas.health import HealthResponse

logger = get_logger("app.main")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    FastAPI Lifespan Context Manager.
    Handles startup and shutdown infrastructure initialization & teardown.
    """
    # Startup Initialization
    setup_logging()
    logger.info(
        f"Starting {settings.APP_NAME} [Environment: {settings.ENVIRONMENT}] [Debug: {settings.DEBUG}]"
    )

    yield

    # Graceful Shutdown Teardown
    logger.info(f"Shutting down {settings.APP_NAME} service gracefully...")


def create_application() -> FastAPI:
    """
    Factory function to initialize and configure the FastAPI application instance.
    Follows Clean Architecture & SOLID separation.
    """
    app = FastAPI(
        title=settings.APP_NAME,
        description="Trust Agent backend foundation for IntelliGuard platform",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # Register Global Exception Handlers
    register_exception_handlers(app)

    # Register Middlewares (CORS, Context, Tracing)
    register_middlewares(app)

    # Register API Routers
    app.include_router(api_v1_router, prefix=settings.API_V1_STR)

    # Top-Level Health Check Endpoint Shortcut (GET /health)
    @app.get(
        "/health",
        response_model=APIResponse[HealthResponse],
        status_code=status.HTTP_200_OK,
        tags=["Health Check"],
        summary="Root Health Check Shortcut",
        description="Direct endpoint shortcut for GET /health alias to GET /api/v1/health.",
    )
    async def root_health_check(
        request: Request,
        app_settings: Settings = Depends(get_app_settings),
    ) -> APIResponse[HealthResponse]:
        return await get_health_status(request=request, settings=app_settings)

    # Root redirect to API Documentation
    @app.get("/", include_in_schema=False)
    async def root_redirect():
        return RedirectResponse(url="/docs")

    return app


app = create_application()

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
