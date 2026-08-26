from fastapi import FastAPI
from app.config.settings import settings

app = FastAPI(
    title="Bhoomi.ai Backend",
    description="Minimal FastAPI foundation for Bhoomi.ai",
    version="0.1.0"
)

@app.get("/health")
async def health_check():
    """Basic health check endpoint."""
    return {
        "status": "ok",
        "service": "bhoomi-ai",
        "environment": settings.ENVIRONMENT
    }
