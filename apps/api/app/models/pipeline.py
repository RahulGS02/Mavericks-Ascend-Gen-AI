from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, Integer, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum

from ..database import Base


class JobType(str, enum.Enum):
    """Types of jobs in a pipeline"""
    TRAINING = "TRAINING"
    ASSESSMENT = "ASSESSMENT"
    DEPLOYMENT = "DEPLOYMENT"


class PipelineStatus(str, enum.Enum):
    """Status of a pipeline"""
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    ARCHIVED = "ARCHIVED"


class JobStatus(str, enum.Enum):
    """Status of a job"""
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


class Pipeline(Base):
    """Pipeline model - defines the training journey"""
    __tablename__ = "pipelines"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    is_template = Column(Boolean, default=False, nullable=False)
    status = Column(SQLEnum(PipelineStatus, values_callable=lambda x: [e.value for e in x]), default=PipelineStatus.DRAFT, nullable=False)
    
    # Relationships
    creator = relationship("User", back_populates="created_pipelines")
    jobs = relationship("PipelineJob", back_populates="pipeline", cascade="all, delete-orphan", order_by="PipelineJob.sequence_order")
    batches = relationship("Batch", back_populates="pipeline")
    
    def __repr__(self):
        return f"<Pipeline {self.name}>"


class PipelineJob(Base):
    """Individual job/stage within a pipeline"""
    __tablename__ = "pipeline_jobs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pipeline_id = Column(UUID(as_uuid=True), ForeignKey("pipelines.id", ondelete="CASCADE"), nullable=False)

    # Job Details
    name = Column(String(255), nullable=False)  # Changed from job_name to name
    job_type = Column(SQLEnum(JobType, values_callable=lambda x: [e.value for e in x]), nullable=False)
    sequence_order = Column(Integer, nullable=False)
    is_mandatory = Column(Boolean, default=True, nullable=False)
    duration_days = Column(Integer, nullable=True)
    description = Column(Text)
    prerequisites = Column(Text, nullable=True)  # Added prerequisites field
    status = Column(SQLEnum(JobStatus, values_callable=lambda x: [e.value for e in x]), default=JobStatus.PENDING, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Job-specific configuration (e.g., assessment details, training modules)
    job_metadata = Column(JSONB, default=dict)
    
    # Relationships
    pipeline = relationship("Pipeline", back_populates="jobs")
    progress_records = relationship("MaverickJobProgress", back_populates="job")
    batch_schedules = relationship("BatchJobSchedule", back_populates="pipeline_job", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<PipelineJob {self.name} (Order: {self.sequence_order})>"
