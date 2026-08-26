import uuid
from sqlalchemy import Column, String, Date, ForeignKey, DateTime, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class CropCycle(Base):
    __tablename__ = "crop_cycle"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    field_id = Column(UUID(as_uuid=True), ForeignKey("field.id"), nullable=False)
    crop_type = Column(String, nullable=False)
    planting_date = Column(Date, nullable=False)
    expected_harvest_date = Column(Date, nullable=True)
    status = Column(String, default="PLANNED")
    created_at = Column(DateTime(timezone=True), server_default=text('now()'))
    updated_at = Column(DateTime(timezone=True), onupdate=text('now()'))

    field = relationship("Field", backref="crop_cycles")
