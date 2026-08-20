from fastapi import APIRouter
from app.models.schemas import HealthResponse
from app.config.settings import settings

router = APIRouter(prefix="/health", tags=["Health"])

@router.get("", response_model=HealthResponse)
async def health_check():
    return HealthResponse(status="ok", version=settings.VERSION)
