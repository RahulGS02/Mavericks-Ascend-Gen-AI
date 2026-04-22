from sqlalchemy import Column, Text, DateTime, ForeignKey, Numeric, Enum as SQLEnum, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum

from ..database import Base


class JobProgressStatus(str, enum.Enum):
    """Status of a maverick's progress on a job"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"
    FAILED_ASSESSMENT = "failed_assessment"


class MaverickJobProgress(Base):
    """Track maverick progress through pipeline jobs"""
    __tablename__ = "maverick_job_progress"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    maverick_id = Column(UUID(as_uuid=True), ForeignKey("mavericks.id", ondelete="CASCADE"), nullable=False)
    batch_id = Column(UUID(as_uuid=True), ForeignKey("batches.id", ondelete="CASCADE"), nullable=False)
    job_id = Column(UUID(as_uuid=True), ForeignKey("pipeline_jobs.id"), nullable=False)
    
    # Progress Details
    status = Column(SQLEnum(JobProgressStatus), default=JobProgressStatus.NOT_STARTED, nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    completion_percentage = Column(Numeric(5, 2), default=0, nullable=False)
    notes = Column(Text)
    
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
