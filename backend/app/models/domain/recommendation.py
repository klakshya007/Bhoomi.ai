import uuid
from sqlalchemy import Column, String, ForeignKey, DateTime, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Recommendation(Base):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    crop_cycle_id = Column(UUID(as_uuid=True), ForeignKey("crop_cycle.id"), nullable=False)
    prediction_id = Column(UUID(as_uuid=True), ForeignKey("prediction.id"), nullable=True)
    agent_run_id = Column(UUID(as_uuid=True), ForeignKey("agent_run.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    status = Column(String, default="ACTIVE")
    created_at = Column(DateTime(timezone=True), server_default=text('now()'))
    updated_at = Column(DateTime(timezone=True), onupdate=text('now()'))

    crop_cycle = relationship("CropCycle", backref="recommendations")
    prediction = relationship("Prediction", backref="recommendations")
    agent_run = relationship("AgentRun", backref="recommendations")
