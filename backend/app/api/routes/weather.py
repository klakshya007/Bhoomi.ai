from fastapi import APIRouter, Depends
from app.models.schemas import WeatherDataResponse
from app.api.dependencies import get_weather_service
from app.services.weather_service import WeatherService

router = APIRouter(prefix="/weather", tags=["Weather"])

@router.get("", response_model=WeatherDataResponse)
async def get_weather_data(
    lat: float,
    lon: float,
    service: WeatherService = Depends(get_weather_service)
):
    data = await service.get_weather_data(lat, lon)
    return WeatherDataResponse(**data)
