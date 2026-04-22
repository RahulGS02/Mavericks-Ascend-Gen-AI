from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, Integer, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum

from ..database import Base


class JobType(str, enum.Enum):
    """Types of jobs in a pipeline"""
    TRAINING = "training"
    ASSESSMENT = "assessment"
    DEPLOYMENT = "deployment"


class Pipeline(Base):
    """Pipeline model - defines the training journey"""
    __tablename__ = "pipelines"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_template = Column(Boolean, default=False, nullable=False)
    status = Column(String(50), default="active", nullable=False)
    
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
    job_name = Column(String(255), nullable=False)
    job_type = Column(SQLEnum(JobType), nullable=False)
    sequence_order = Column(Integer, nullable=False)
    is_mandatory = Column(Boolean, default=True, nullable=False)
    duration_days = Column(Integer, nullable=True)
    description = Column(Text)

    # Job-specific configuration (e.g., assessment details, training modules)
    job_metadata = Column(JSONB, default=dict)
    
    # Relationships
    pipeline = relationship("Pipeline", back_populates="jobs")
    progress_records = relationship("MaverickJobProgress", back_populates="job")
    assessment_attempts = relationship("AssessmentAttempt", back_populates="job")
    
    def __repr__(self):
        return f"<PipelineJob {self.job_name} (Order: {self.sequence_order})>"
