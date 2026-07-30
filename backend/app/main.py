from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import security

@asynccontextmanager
async def lifespan(app: FastAPI):
    await security.agent.initialize()
    yield
    await security.agent.cleanup()

app = FastAPI(title="IntelliGuard Backend", lifespan=lifespan)

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

app.include_router(security.router)

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "IntelliGuard Backend"
    }
