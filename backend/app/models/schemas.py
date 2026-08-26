from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from uuid import UUID

class NormalizedObservationDTO(BaseModel):
    """
    Standardized payload for external data entering the application boundary.
    Services map this DTO into the SQLAlchemy Observation ORM model.
    """
    field_id: UUID
    crop_cycle_id: Optional[UUID] = None
    source: str = Field(..., description="E.g., 'OpenMeteo', 'GEE_Sentinel2'")
    type: str = Field(..., description="E.g., 'Rainfall_mm', 'NDVI_Mean'")
    depth_interval: Optional[str] = Field(None, description="E.g., '0-5cm', '5-15cm' for soil data")
    value: Union[float, Dict[str, Any]]
    unit: Optional[str] = None
    observed_at: datetime
    provenance_id: Optional[str] = Field(None, description="Provider's request ID or source image ID")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Optional metadata, e.g. prediction uncertainty")

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
