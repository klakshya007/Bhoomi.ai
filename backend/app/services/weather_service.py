from uuid import UUID
from datetime import date
from typing import List
from app.providers.weather import OpenMeteoProvider
from app.models.schemas import NormalizedObservationDTO
from app.core.exceptions import IntegrationError

class WeatherService:
    """
    Orchestrates the Weather Providers and acts as the optional persistence boundary.
    """
    def __init__(self, provider=None, db=None):
        self.provider = provider or OpenMeteoProvider()
        self.db = db

    async def get_historical_weather(self, field_id: UUID, lat: float, lon: float, start_date: date, end_date: date) -> List[NormalizedObservationDTO]:
        """
        Retrieves historical weather data normalized as observations.
        If persistence were running, this boundary would optionally cache/store them.
        """
        try:
            # 1. Fetch from external provider via the boundary layer
            observations = await self.provider.fetch_historical_weather(
                lat=lat, 
                lon=lon, 
                start_date=start_date, 
                end_date=end_date, 
                field_id=field_id
            )
            
            # 2. Persistence Boundary
            if self.db and observations:
                from sqlalchemy.dialects.postgresql import insert
                from app.models.domain.observation import Observation
                
                values = []
                for dto in observations:
                    values.append({
                        "field_id": dto.field_id,
                        "crop_cycle_id": dto.crop_cycle_id,
                        "source": dto.source,
                        "type": dto.type,
                        "depth_interval": getattr(dto, "depth_interval", None),
                        "value": dto.value,
                        "unit": dto.unit,
                        "observed_at": dto.observed_at,
                        "provenance_id": getattr(dto, "provenance_id", None),
                        "metadata": getattr(dto, "metadata", None)
                    })
                
                stmt = insert(Observation).values(values)
                stmt = stmt.on_conflict_do_nothing(
                    index_elements=['field_id', 'source', 'type', 'observed_at', 'depth_interval']
                )
                self.db.execute(stmt)
                self.db.commit()
            
            return observations
            
        except IntegrationError as e:
            # Log error and raise safely
            print(f"Weather Service failed: {e.message}")
            raise
