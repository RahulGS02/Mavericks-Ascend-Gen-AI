from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum

from ..database import Base


class ProfileStatus(str, enum.Enum):
    """Maverick profile review status"""
    PENDING_REVIEW = "pending_review"
    SHORTLISTED = "shortlisted"
    REJECTED = "rejected"
    ASSIGNED = "assigned"


class DeploymentStatus(str, enum.Enum):
    """Maverick deployment status"""
    IN_TRAINING = "in_training"
    READY_FOR_DEPLOYMENT = "ready_for_deployment"
    DEPLOYED = "deployed"


class Maverick(Base):
    """Maverick (trainee) profile model"""
    __tablename__ = "mavericks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    # Personal Information
    college = Column(String(255))
    degree = Column(String(255))
    graduation_year = Column(Integer)
    phone = Column(String(20))
    
    # Resume & Skills
    resume_url = Column(Text)
    skills = Column(JSONB, default=list)  # Self-declared skills
    ai_extracted_skills = Column(JSONB, default=list)  # AI-parsed skills
    ai_summary = Column(Text)  # AI-generated summary
    
    # Status
    profile_status = Column(SQLEnum(ProfileStatus), default=ProfileStatus.PENDING_REVIEW, nullable=False, index=True)
    deployment_status = Column(SQLEnum(DeploymentStatus), default=DeploymentStatus.IN_TRAINING, nullable=False, index=True)
    
    # Review Information
    submitted_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    reviewed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Current Assignment
    current_batch_id = Column(UUID(as_uuid=True), ForeignKey("batches.id"), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="maverick", foreign_keys=[user_id])
    current_batch = relationship("Batch", foreign_keys=[current_batch_id])
    job_progress = relationship("MaverickJobProgress", back_populates="maverick", cascade="all, delete-orphan")
    assessment_attempts = relationship("AssessmentAttempt", back_populates="maverick", cascade="all, delete-orphan")
    deployments = relationship("Deployment", back_populates="maverick", cascade="all, delete-orphan")
    deployment_requests = relationship("DeploymentRequest", back_populates="maverick")
    
    def __repr__(self):
        return f"<Maverick {self.user.name if self.user else 'Unknown'} - {self.profile_status}>"
