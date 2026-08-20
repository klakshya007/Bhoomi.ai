from app.services.satellite_service import SatelliteService
from app.services.weather_service import WeatherService
from app.services.soil_service import SoilService
from app.services.advisory_service import AdvisoryService

def get_satellite_service() -> SatelliteService:
    return SatelliteService()

def get_weather_service() -> WeatherService:
    return WeatherService()

def get_soil_service() -> SoilService:
    return SoilService()

def get_advisory_service() -> AdvisoryService:
    return AdvisoryService()
