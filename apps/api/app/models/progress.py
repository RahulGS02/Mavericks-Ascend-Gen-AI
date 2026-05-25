from sqlalchemy import Column, Text, DateTime, ForeignKey, Numeric, Enum as SQLEnum, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum

from ..database import Base
from .types import GUID


class ProgressStatus(str, enum.Enum):
    """Status of a maverick's progress on a job"""
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


# Alias for backwards compatibility
JobProgressStatus = ProgressStatus


class MaverickJobProgress(Base):
    """Track maverick progress through pipeline jobs"""
    __tablename__ = "maverick_job_progress"
    
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    maverick_id = Column(GUID, ForeignKey("mavericks.id", ondelete="CASCADE"), nullable=False)
    batch_id = Column(GUID, ForeignKey("batches.id", ondelete="CASCADE"), nullable=False)
    job_id = Column(GUID, ForeignKey("pipeline_jobs.id"), nullable=False)
    
    # Progress Details
    status = Column(SQLEnum(ProgressStatus, values_callable=lambda x: [e.value for e in x]), default=ProgressStatus.PENDING, nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    completion_percentage = Column(Numeric(5, 2), default=0, nullable=False)
    score = Column(Numeric(5, 2), nullable=True)  # For assessment jobs
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    maverick = relationship("Maverick", back_populates="job_progress")
    batch = relationship("Batch", back_populates="job_progress")
    job = relationship("PipelineJob", back_populates="progress_records")
    
    # Unique constraint - one progress record per maverick per job
    __table_args__ = (
        UniqueConstraint('maverick_id', 'job_id', name='unique_maverick_job'),
    )
    
    def __repr__(self):
        return f"<MaverickJobProgress {self.maverick_id} - Job {self.job_id} - {self.status}>"
