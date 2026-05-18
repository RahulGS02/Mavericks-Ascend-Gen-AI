from sqlalchemy import Column, String, Date, DateTime, ForeignKey, Enum as SQLEnum, Integer, Text
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum

from ..database import Base


class BatchStatus(str, enum.Enum):
    """Batch status"""
    PLANNED = "PLANNED"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    ON_HOLD = "ON_HOLD"
    ARCHIVED = "ARCHIVED"


class BatchCategory(str, enum.Enum):
    """Batch training category for AI matching"""
    TECH_DEVELOPMENT = "TECH_DEVELOPMENT"  # Web Dev, Mobile Dev, Backend, Frontend
    TECH_DEVOPS = "TECH_DEVOPS"  # DevOps, Cloud, Infrastructure
    TECH_TESTING = "TECH_TESTING"  # QA, Automation Testing
    TECH_DATA_SCIENCE = "TECH_DATA_SCIENCE"  # ML, AI, Data Analysis
    TECH_CYBER_SECURITY = "TECH_CYBER_SECURITY"  # Security, Penetration Testing
    SOFT_SKILLS = "SOFT_SKILLS"  # Communication, Leadership, etc.


class Batch(Base):
    """Batch model - group of mavericks following a pipeline"""
    __tablename__ = "batches"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    pipeline_id = Column(UUID(as_uuid=True), ForeignKey("pipelines.id"), nullable=False)

    # AI Batch Suggestion Fields
    category = Column(SQLEnum(BatchCategory), nullable=True)  # Batch category (required for AI matching)
    focus_areas = Column(ARRAY(String), nullable=True)  # e.g., ["React", "Node.js", "AWS"]
    required_skills = Column(ARRAY(String), nullable=True)  # Must-have skills
    preferred_skills = Column(ARRAY(String), nullable=True)  # Nice-to-have skills
    target_role = Column(String(255), nullable=True)  # e.g., "Full Stack Developer"

    # Schedule
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)  # Changed from expected_end_date

    # Capacity management
    max_capacity = Column(Integer, nullable=True)
    current_enrollment = Column(Integer, default=0, nullable=False)

    # Assignment
    trainer_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Status
    status = Column(SQLEnum(BatchStatus, values_callable=lambda x: [e.value for e in x]), default=BatchStatus.PLANNED, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    pipeline = relationship("Pipeline", back_populates="batches")
    trainer = relationship("User", foreign_keys=[trainer_id], back_populates="trained_batches")  # Legacy single trainer (kept for backwards compatibility)
    batch_trainers = relationship("BatchTrainer", back_populates="batch", cascade="all, delete-orphan")  # New: Multiple trainers support
    creator = relationship("User", foreign_keys=[created_by])
    job_progress = relationship("MaverickJobProgress", back_populates="batch")
    job_schedules = relationship("BatchJobSchedule", back_populates="batch", cascade="all, delete-orphan")
    training_sessions = relationship("TrainingSession", back_populates="batch", cascade="all, delete-orphan")
    assessment_attempts = relationship("AssessmentAttempt", back_populates="batch")
    deployments = relationship("Deployment", back_populates="batch")
    
    def __repr__(self):
        return f"<Batch {self.name}>"
