import httpx
from datetime import datetime, date, timezone
from uuid import UUID
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, field_validator, model_validator
from app.core.exceptions import IntegrationError, ProviderDataFormatError
from app.models.schemas import NormalizedObservationDTO

class OpenMeteoHistoricalRequest(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    start_date: date
    end_date: date

    @model_validator(mode='after')
    def check_date_range(self):
        if self.start_date > self.end_date:
            raise ValueError("start_date must be less than or equal to end_date")
        return self

class OpenMeteoProvider:
    """
    Concrete implementation for the Open-Meteo Historical Weather Provider.
    """
    def __init__(self, client: Optional[httpx.AsyncClient] = None):
        self.base_url = "https://archive-api.open-meteo.com/v1/archive"
        self._client = client
        self.requested_variables = [
            "temperature_2m_mean",
            "relative_humidity_2m_mean",
            "precipitation_sum",
            "wind_speed_10m_max",
            "et0_fao_evapotranspiration"
        ]

    async def fetch_historical_weather(self, lat: float, lon: float, start_date: date, end_date: date, field_id: UUID) -> List[NormalizedObservationDTO]:
        try:
            req = OpenMeteoHistoricalRequest(
                latitude=lat, 
                longitude=lon, 
                start_date=start_date, 
                end_date=end_date
            )
        except ValueError as e:
            raise IntegrationError(f"Invalid parameters: {e}", provider="OpenMeteo")

        params = {
            "latitude": req.latitude,
            "longitude": req.longitude,
            "start_date": req.start_date.isoformat(),
            "end_date": req.end_date.isoformat(),
            "daily": ",".join(self.requested_variables),
            "timezone": "UTC"
        }
        
        # Dependency inject or create short-lived client
        client_to_use = self._client or httpx.AsyncClient()
        
        try:
            response = await client_to_use.get(self.base_url, params=params, timeout=10.0)
            response.raise_for_status()
            data = response.json()
        except httpx.TimeoutException:
            raise IntegrationError("Request to provider timed out.", provider="OpenMeteo")
        except httpx.HTTPError as e:
            raise IntegrationError(f"HTTP Error: {e}", provider="OpenMeteo")
        finally:
            if not self._client:
                await client_to_use.aclose()
        
        return self._normalize_response(data, field_id, req)

    def _normalize_response(self, data: Dict[str, Any], field_id: UUID, req: OpenMeteoHistoricalRequest) -> List[NormalizedObservationDTO]:
        if "daily" not in data or "time" not in data["daily"]:
            raise ProviderDataFormatError("Response missing 'daily' or 'time' arrays", provider="OpenMeteo")

        daily = data["daily"]
        times = daily["time"]
        n_times = len(times)
        
        # Check that all requested variables exist and array lengths match the time array
        for var in self.requested_variables:
            if var not in daily:
                raise ProviderDataFormatError(f"Missing requested variable '{var}' in response", provider="OpenMeteo")
            if len(daily[var]) != n_times:
                raise ProviderDataFormatError(f"Array length mismatch for '{var}': expected {n_times}, got {len(daily[var])}", provider="OpenMeteo")
        
        units = data.get("daily_units", {})
        
        observations = []
        provenance = f"openmeteo_archive_v1_{req.latitude}_{req.longitude}_{req.start_date}_{req.end_date}"

        for i, t_str in enumerate(times):
            dt = datetime.fromisoformat(t_str).replace(tzinfo=timezone.utc)
            
            for var in self.requested_variables:
                val = daily[var][i]
                if val is None:
                    continue # Skip missing values cleanly
                
                obs = NormalizedObservationDTO(
                    field_id=field_id,
                    source="OpenMeteo",
                    type=var,
                    value=float(val),
                    unit=units.get(var),
                    observed_at=dt,
                    provenance_id=provenance
                )
                observations.append(obs)
                
        return observations
