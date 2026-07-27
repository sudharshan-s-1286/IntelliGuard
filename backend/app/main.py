from fastapi import FastAPI
from app.api import security

app = FastAPI(title="IntelliGuard Backend")

app.include_router(security.router)

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "IntelliGuard Backend"
    }
