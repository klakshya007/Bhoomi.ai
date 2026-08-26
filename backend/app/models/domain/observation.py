import uuid
from sqlalchemy import Column, String, ForeignKey, DateTime, text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Observation(Base):
    __tablename__ = 'observation'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    field_id = Column(UUID(as_uuid=True), ForeignKey("field.id"), nullable=False)
    crop_cycle_id = Column(UUID(as_uuid=True), ForeignKey("crop_cycle.id"), nullable=True)
    source = Column(String, nullable=False)
    type = Column(String, nullable=False)
    depth_interval = Column(String, nullable=True)
    value = Column(JSONB, nullable=False)
    unit = Column(String, nullable=True)
    provenance_id = Column(String, nullable=True)
    metadata_ = Column("metadata", JSONB, nullable=True)
    observed_at = Column(DateTime(timezone=True), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=text('now()'))

    field = relationship("Field", backref="observations")
    crop_cycle = relationship("CropCycle", backref="observations")

    __table_args__ = (
        UniqueConstraint('field_id', 'source', 'type', 'observed_at', 'depth_interval', name='uq_observation_idempotency'),
    )
