from fastapi import FastAPI
from app.config.settings import settings
from app.api.routes import satellite, soil, weather

app = FastAPI(
    title="Bhoomi.ai Backend",
    description="Minimal FastAPI foundation for Bhoomi.ai",
    version="0.1.0"
)

app.include_router(satellite.router, prefix="/api/v1")
app.include_router(soil.router, prefix="/api/v1")
app.include_router(weather.router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    """Basic health check endpoint."""
    return {
        "status": "ok",
        "service": "bhoomi-ai",
        "environment": settings.ENVIRONMENT
    }
