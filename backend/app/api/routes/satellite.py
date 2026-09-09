from fastapi import APIRouter, Depends
from app.models.schemas import SatelliteDataResponse
from app.api.dependencies import get_satellite_service
from app.services.satellite_service import SatelliteService
from uuid import uuid4
from datetime import date, timedelta

router = APIRouter(prefix="/satellite", tags=["Satellite"])

@router.get("", response_model=SatelliteDataResponse)
async def get_satellite_data(
    lat: float,
    lon: float,
    service: SatelliteService = Depends(get_satellite_service)
):
    field_id = uuid4()
    end_date = date.today()
    start_date = end_date - timedelta(days=30)
    # Simple polygon around lat/lon
    polygon = {
        "type": "Polygon",
        "coordinates": [[[lon-0.01, lat-0.01], [lon+0.01, lat-0.01], [lon+0.01, lat+0.01], [lon-0.01, lat+0.01], [lon-0.01, lat-0.01]]]
    }
    obs = await service.get_historical_indices(field_id, polygon, start_date, end_date)
    
    ndvi = next((o.value for o in obs if o.type == "NDVI_Mean"), None)
    evi = next((o.value for o in obs if o.type == "EVI_Mean"), None)
    
    return SatelliteDataResponse(latitude=lat, longitude=lon, ndvi=ndvi, evi=evi)
