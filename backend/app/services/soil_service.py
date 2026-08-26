from typing import List
from uuid import UUID
from datetime import datetime, timezone
import uuid

from app.models.schemas import NormalizedObservationDTO
from app.providers.soil import BaseSoilProvider

class SoilService:
    """
    Orchestrates soil data retrieval from a provider and normalizes it.
    """
    def __init__(self, provider: BaseSoilProvider, db=None):
        self.provider = provider
        self.db = db
        
    async def get_soil_profile_for_field(
        self, 
        field_id: UUID, 
        latitude: float, 
        longitude: float
    ) -> List[NormalizedObservationDTO]:
        """
        Fetches multi-depth soil properties using the field's centroid.
        (Centroid extraction from Field geometry is a Phase 0 simplification).
        """
        
        # 1. Fetch from provider
        properties = await self.provider.get_soil_properties(latitude, longitude)
        
        # 2. Normalize to DTOs
        now = datetime.now(timezone.utc)
        provenance = str(uuid.uuid4()) # In real world, we would extract from provider response
        
        dtos = []
        for prop in properties:
            metadata = None
            if prop.uncertainty is not None:
                metadata = {"uncertainty": prop.uncertainty}
                
            dto = NormalizedObservationDTO(
                field_id=field_id,
                source="ISRIC_SoilGrids",
                type=f"soil_{prop.property_name}",
                depth_interval=prop.depth_interval,
                value=prop.mean_value,
                unit=prop.unit,
                observed_at=now,
                provenance_id=provenance,
                metadata=metadata
            )
        
            dtos.append(dto)
            
        # 3. Persistence Boundary
        if self.db and dtos:
            from sqlalchemy.dialects.postgresql import insert
            from app.models.domain.observation import Observation
            
            values = []
            for dto in dtos:
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
            
        return dtos
