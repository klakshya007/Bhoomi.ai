from fastapi import APIRouter, Depends
from app.models.schemas import SoilDataResponse
from app.api.dependencies import get_soil_service
from app.services.soil_service import SoilService
from uuid import uuid4

router = APIRouter(prefix="/soil", tags=["Soil"])

@router.get("", response_model=SoilDataResponse)
async def get_soil_data(
    lat: float,
    lon: float,
    service: SoilService = Depends(get_soil_service)
):
    field_id = uuid4()
    obs = await service.get_soil_profile_for_field(field_id, lat, lon)
    
    ph = next((o.value for o in obs if "phh2o" in o.type), None)
    n = next((o.value for o in obs if "nitrogen" in o.type), None)
    
    return SoilDataResponse(latitude=lat, longitude=lon, ph=ph, nitrogen=n)
