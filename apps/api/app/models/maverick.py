from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum

from ..database import Base


class ProfileStatus(str, enum.Enum):
    """Maverick profile review status"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class DeploymentStatus(str, enum.Enum):
    """Maverick deployment status"""
    AVAILABLE = "AVAILABLE"
    DEPLOYED = "DEPLOYED"
    ON_LEAVE = "ON_LEAVE"
    TERMINATED = "TERMINATED"


class Maverick(Base):
    """Maverick (trainee) profile model"""
    __tablename__ = "mavericks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=True)

    # Personal Information (direct fields - no need for user lookup)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    college = Column(String(255))
    degree = Column(String(255))
    branch = Column(String(255))
    graduation_year = Column(Integer)
    cgpa = Column(Integer)
    phone = Column(String(20))

    # URLs
    github_url = Column(Text)
    linkedin_url = Column(Text)

    # Resume & Skills
    resume_url = Column(Text)
    skills = Column(JSONB, default=list)  # Self-declared skills
    ai_extracted_skills = Column(JSONB, default=list)  # AI-parsed skills (flattened list)
    ai_summary = Column(Text)  # AI-generated summary
    ai_resume_data = Column(JSONB)  # Complete AI-parsed resume data (education, experience, projects, etc.)

    # Status
    profile_status = Column(SQLEnum(ProfileStatus, values_callable=lambda x: [e.value for e in x]), default=ProfileStatus.PENDING, nullable=False, index=True)
    deployment_status = Column(SQLEnum(DeploymentStatus, values_callable=lambda x: [e.value for e in x]), default=DeploymentStatus.AVAILABLE, nullable=False, index=True)

    # Review Information
    review_notes = Column(Text)
    reviewed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Current Assignment
    current_batch_id = Column(UUID(as_uuid=True), ForeignKey("batches.id"), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="maverick", foreign_keys=[user_id])
    current_batch = relationship("Batch", foreign_keys=[current_batch_id])
    skill_proficiencies = relationship("MaverickSkill", back_populates="maverick", cascade="all, delete-orphan")
    job_progress = relationship("MaverickJobProgress", back_populates="maverick", cascade="all, delete-orphan")
    assessment_attempts = relationship("AssessmentAttempt", back_populates="maverick", cascade="all, delete-orphan")
    deployments = relationship("Deployment", back_populates="maverick", cascade="all, delete-orphan")
    deployment_requests = relationship("DeploymentRequest", back_populates="maverick")
    
    def __repr__(self):
        return f"<Maverick {self.user.name if self.user else 'Unknown'} - {self.profile_status}>"
