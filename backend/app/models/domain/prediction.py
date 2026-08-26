import uuid
from sqlalchemy import Column, String, Float, ForeignKey, DateTime, text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Prediction(Base):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    crop_cycle_id = Column(UUID(as_uuid=True), ForeignKey("crop_cycle.id"), nullable=False)
    agent_run_id = Column(UUID(as_uuid=True), ForeignKey("agent_run.id"), nullable=False)
    target_variable = Column(String, nullable=False)
    value = Column(Float, nullable=False)
    unit = Column(String, nullable=True)
    confidence = Column(Float, nullable=True)
    model_version = Column(String, nullable=True)
    features = Column(JSONB, nullable=True)
    predicted_at = Column(DateTime(timezone=True), server_default=text('now()'))
    target_date = Column(DateTime(timezone=True), nullable=True, index=True)

    crop_cycle = relationship("CropCycle", backref="predictions")
    agent_run = relationship("AgentRun", backref="predictions")
