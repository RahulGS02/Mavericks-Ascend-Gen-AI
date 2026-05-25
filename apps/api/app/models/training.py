from sqlalchemy import Column, String, Integer, Date, DateTime, ForeignKey, Boolean, Text, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum

from ..database import Base
from .types import GUID


class SessionStatus(str, enum.Enum):
    """Status of a training session"""
    SCHEDULED = "SCHEDULED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class TrainingSession(Base):
    """Training session scheduling"""
    __tablename__ = "training_sessions"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    batch_id = Column(GUID, ForeignKey("batches.id", ondelete="CASCADE"), nullable=False)
    job_id = Column(GUID, ForeignKey("pipeline_jobs.id"), nullable=False)

    # Session Details
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    scheduled_date = Column(DateTime(timezone=True), nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    trainer_id = Column(GUID, ForeignKey("users.id"), nullable=True)

    # Location
    location = Column(String(255), nullable=True)
    meeting_link = Column(Text, nullable=True)

    # Status and completion
    status = Column(SQLEnum(SessionStatus, values_callable=lambda x: [e.value for e in x]), default=SessionStatus.SCHEDULED, nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    completion_notes = Column(Text, nullable=True)
    attendance_count = Column(Integer, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    batch = relationship("Batch", back_populates="training_sessions")

    def __repr__(self):
        return f"<TrainingSession {self.title} on {self.scheduled_date}>"
