from fastapi import APIRouter, Depends
from app.models.schemas import SatelliteDataResponse
from app.api.dependencies import get_satellite_service
from app.services.satellite_service import SatelliteService

router = APIRouter(prefix="/satellite", tags=["Satellite"])

@router.get("", response_model=SatelliteDataResponse)
async def get_satellite_data(
    lat: float,
    lon: float,
    service: SatelliteService = Depends(get_satellite_service)
):
    data = await service.get_satellite_data(lat, lon)
    return SatelliteDataResponse(**data)
