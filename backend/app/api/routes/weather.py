from fastapi import APIRouter, Depends
from app.models.schemas import WeatherDataResponse
from app.api.dependencies import get_weather_service
from app.services.weather_service import WeatherService
from uuid import uuid4
from datetime import date, timedelta

router = APIRouter(prefix="/weather", tags=["Weather"])

@router.get("", response_model=WeatherDataResponse)
async def get_weather_data(
    lat: float,
    lon: float,
    service: WeatherService = Depends(get_weather_service)
):
    field_id = uuid4()
    end_date = date.today()
    start_date = end_date - timedelta(days=1)
    obs = await service.get_historical_weather(field_id, lat, lon, start_date, end_date)
    
    temp = next((o.value for o in obs if o.type == "temperature_2m_mean"), None)
    hum = next((o.value for o in obs if o.type == "relative_humidity_2m_mean"), None)
    rain = next((o.value for o in obs if o.type == "precipitation_sum"), None)
    
    return WeatherDataResponse(latitude=lat, longitude=lon, temperature=temp, humidity=hum, rainfall=rain)
