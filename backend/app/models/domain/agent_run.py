import uuid
from sqlalchemy import Column, String, ForeignKey, DateTime, text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class AgentRun(Base):
    __tablename__ = "agent_run"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    parent_run_id = Column(UUID(as_uuid=True), ForeignKey("agent_run.id"), nullable=True)
    agent_type = Column(String, nullable=False)
    status = Column(String, default="PENDING")
    input_payload = Column(JSONB, nullable=True)
    output_payload = Column(JSONB, nullable=True)
    error_details = Column(String, nullable=True)
    started_at = Column(DateTime(timezone=True), server_default=text('now()'))
    completed_at = Column(DateTime(timezone=True), nullable=True)

    parent_run = relationship("AgentRun", remote_side=[id], backref="child_runs")
