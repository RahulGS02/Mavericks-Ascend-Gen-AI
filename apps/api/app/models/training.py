from sqlalchemy import Column, String, Integer, Date, DateTime, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from ..database import Base


class TrainingSession(Base):
    """Training session scheduling"""
    __tablename__ = "training_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    batch_id = Column(UUID(as_uuid=True), ForeignKey("batches.id", ondelete="CASCADE"), nullable=False)
    
    # Session Details
    session_date = Column(Date, nullable=False)
    topic = Column(String(255), nullable=False)
    duration_hours = Column(Integer, nullable=True)
    trainer_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    has_assessment = Column(Boolean, default=False, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    batch = relationship("Batch", back_populates="training_sessions")
    
    def __repr__(self):
        return f"<TrainingSession {self.topic} on {self.session_date}>"
