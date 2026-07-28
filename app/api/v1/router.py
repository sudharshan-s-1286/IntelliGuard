from fastapi import APIRouter

from app.api.v1.endpoints import health, trust

api_v1_router = APIRouter()

# Register endpoint routers
api_v1_router.include_router(health.router, tags=["Health Check"])
api_v1_router.include_router(trust.router, prefix="/trust", tags=["Trust Analysis"])
