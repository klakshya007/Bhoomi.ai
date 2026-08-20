from fastapi import APIRouter, Depends
from app.models.schemas import SoilDataResponse
from app.api.dependencies import get_soil_service
from app.services.soil_service import SoilService

router = APIRouter(prefix="/soil", tags=["Soil"])

@router.get("", response_model=SoilDataResponse)
async def get_soil_data(
    lat: float,
    lon: float,
    service: SoilService = Depends(get_soil_service)
):
    data = await service.get_soil_data(lat, lon)
    return SoilDataResponse(**data)
