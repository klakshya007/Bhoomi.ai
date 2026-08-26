from typing import Protocol
from uuid import UUID
from app.models.schemas import NormalizedObservationDTO

class WeatherProvider(Protocol):
    """
    Protocol defining the expected interface for any weather provider.
    This avoids heavy abstract base classes while enforcing a clean contract.
    """
    async def fetch_current_weather(self, lat: float, lon: float, field_id: UUID) -> NormalizedObservationDTO:
        ...
