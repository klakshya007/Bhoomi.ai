import uuid
from sqlalchemy import Column, String, ForeignKey, DateTime, text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Simulation(Base):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    crop_cycle_id = Column(UUID(as_uuid=True), ForeignKey("crop_cycle.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    scenario_type = Column(String, nullable=False)
    parameters = Column(JSONB, nullable=False)
    results = Column(JSONB, nullable=True)
    status = Column(String, default="PENDING")
    created_at = Column(DateTime(timezone=True), server_default=text('now()'))

    crop_cycle = relationship("CropCycle", backref="simulations")
    user = relationship("User", backref="simulations")
