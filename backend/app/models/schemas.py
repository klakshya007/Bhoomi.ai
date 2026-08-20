from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class HealthResponse(BaseModel):
    status: str
    version: str

class LocationQuery(BaseModel):
    latitude: float
    longitude: float

class SatelliteDataResponse(BaseModel):
    latitude: float
    longitude: float
    ndvi: Optional[float] = None
    evi: Optional[float] = None
    raw_data: Optional[Dict[str, Any]] = None

class WeatherDataResponse(BaseModel):
    latitude: float
    longitude: float
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    rainfall: Optional[float] = None

class SoilDataResponse(BaseModel):
    latitude: float
    longitude: float
    ph: Optional[float] = None
    nitrogen: Optional[float] = None
    phosphorus: Optional[float] = None
    potassium: Optional[float] = None
    moisture: Optional[float] = None

class PredictionRequest(BaseModel):
    latitude: float
    longitude: float
    crop_type: Optional[str] = None

class PredictionResponse(BaseModel):
    crop_stress_index: float
    risk_level: str
    details: Optional[Dict[str, Any]] = None

class AdvisoryRequest(BaseModel):
    latitude: float
    longitude: float
    crop_type: Optional[str] = None
    issue_description: Optional[str] = None

class AdvisoryResponse(BaseModel):
    recommendations: List[str]
    summary: str
