"""
Batch Job Schedule Model
Links pipeline jobs to actual batch execution timeline
"""
from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, Integer, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum

from ..database import Base


class JobScheduleStatus(str, enum.Enum):
    """Status of a scheduled job in a batch"""
    NOT_SCHEDULED = "NOT_SCHEDULED"
    SCHEDULED = "SCHEDULED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    OVERDUE = "OVERDUE"


class BatchJobSchedule(Base):
    """
    Timeline scheduling for pipeline jobs within a specific batch.
    
    This model connects:
    - Pipeline Job (what to do)
    - Batch (which group of mavericks)
    - Timeline (when and how)
    
    Example:
    - Pipeline Job: "React Fundamentals Training"
    - Batch: "Q1 2024 Full Stack Batch"
    - Schedule: Jan 1-7, Zoom link, Completed on Jan 8
    """
    __tablename__ = "batch_job_schedules"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Links
    batch_id = Column(UUID(as_uuid=True), ForeignKey("batches.id", ondelete="CASCADE"), nullable=False, index=True)
    pipeline_job_id = Column(UUID(as_uuid=True), ForeignKey("pipeline_jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Scheduling Information
    scheduled_start_date = Column(DateTime(timezone=True), nullable=True)
    scheduled_end_date = Column(DateTime(timezone=True), nullable=True)  # Deadline
    actual_start_date = Column(DateTime(timezone=True), nullable=True)
    actual_end_date = Column(DateTime(timezone=True), nullable=True)
    
    # Training Session Details (for TRAINING type jobs)
    meeting_link = Column(String(500), nullable=True)  # Zoom/Teams/Meet link
    meeting_password = Column(String(100), nullable=True)
    attendance_required = Column(Boolean, default=False)
    attendance_count = Column(Integer, default=0)  # How many attended
    
    # Assessment Link (for ASSESSMENT type jobs)
    assessment_id = Column(UUID(as_uuid=True), ForeignKey("assessments.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # Deployment Link (for DEPLOYMENT type jobs)
    deployment_project_link = Column(String(500), nullable=True)  # GitHub repo, etc.
    
    # Status Tracking
    status = Column(
        SQLEnum(JobScheduleStatus, values_callable=lambda x: [e.value for e in x]),
        default=JobScheduleStatus.NOT_SCHEDULED,
        nullable=False
    )
    completion_percentage = Column(Integer, default=0)  # 0-100
    
    # Notes and Configuration
    trainer_notes = Column(Text, nullable=True)
    is_published = Column(Boolean, default=False)  # Whether mavericks can see this yet
    
    # Metadata
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    batch = relationship("Batch", back_populates="job_schedules")
    pipeline_job = relationship("PipelineJob", back_populates="batch_schedules")
    assessment = relationship("Assessment", back_populates="job_schedule")
    creator = relationship("User", foreign_keys=[created_by])
    
    def __repr__(self):
        return f"<BatchJobSchedule batch={self.batch_id} job={self.pipeline_job_id} status={self.status}>"
    
    @property
    def is_overdue(self) -> bool:
        """Check if the job is overdue"""
        if not self.scheduled_end_date:
            return False
        if self.status in [JobScheduleStatus.COMPLETED, JobScheduleStatus.CANCELLED]:
            return False
        from datetime import datetime, timezone
        return datetime.now(timezone.utc) > self.scheduled_end_date
    
    @property
    def duration_days(self) -> int:
        """Calculate scheduled duration in days"""
        if not self.scheduled_start_date or not self.scheduled_end_date:
            return 0
        delta = self.scheduled_end_date - self.scheduled_start_date
        return delta.days
