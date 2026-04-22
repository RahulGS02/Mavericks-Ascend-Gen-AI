from sqlalchemy import Column, String, Date, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum

from ..database import Base


class BatchStatus(str, enum.Enum):
    """Batch status"""
    ACTIVE = "active"
    COMPLETED = "completed"
    ON_HOLD = "on_hold"
    ARCHIVED = "archived"


class Batch(Base):
    """Batch model - group of mavericks following a pipeline"""
    __tablename__ = "batches"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, unique=True)
    pipeline_id = Column(UUID(as_uuid=True), ForeignKey("pipelines.id"), nullable=False)
    
    # Schedule
    start_date = Column(Date, nullable=True)
    expected_end_date = Column(Date, nullable=True)
    
    # Assignment
    trainer_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    # Status
    status = Column(SQLEnum(BatchStatus), default=BatchStatus.ACTIVE, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    pipeline = relationship("Pipeline", back_populates="batches")
    trainer = relationship("User", back_populates="trained_batches")
    job_progress = relationship("MaverickJobProgress", back_populates="batch")
    training_sessions = relationship("TrainingSession", back_populates="batch", cascade="all, delete-orphan")
    assessment_attempts = relationship("AssessmentAttempt", back_populates="batch")
    deployments = relationship("Deployment", back_populates="batch")
    
    def __repr__(self):
        return f"<Batch {self.name}>"
