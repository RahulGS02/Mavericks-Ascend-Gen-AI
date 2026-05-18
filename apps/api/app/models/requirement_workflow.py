"""
Requirement Workflow Models
Models for candidate suggestions, interviews, and workflow tracking
"""

from sqlalchemy import Column, String, Text, Date, Time, DateTime, Integer, ForeignKey, Enum as SQLEnum, Numeric, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum

from ..database import Base


class WorkflowStage(str, enum.Enum):
    """Workflow stages for deployment requests"""
    PENDING = "PENDING"
    UNDER_REVIEW = "UNDER_REVIEW"
    CANDIDATES_SUGGESTED = "CANDIDATES_SUGGESTED"
    INTERVIEW_SCHEDULING = "INTERVIEW_SCHEDULING"
    INTERVIEWS_IN_PROGRESS = "INTERVIEWS_IN_PROGRESS"
    SELECTION_IN_PROGRESS = "SELECTION_IN_PROGRESS"
    AWAITING_APPROVAL = "AWAITING_APPROVAL"
    APPROVED = "APPROVED"
    COMPLETED = "COMPLETED"
    CLOSED = "CLOSED"


class CandidateStatus(str, enum.Enum):
    """Status of candidate in requirement workflow"""
    SUGGESTED = "SUGGESTED"
    SHORTLISTED = "SHORTLISTED"
    REJECTED = "REJECTED"
    INTERVIEW_SCHEDULED = "INTERVIEW_SCHEDULED"
    INTERVIEWED = "INTERVIEWED"
    SELECTED = "SELECTED"
    APPROVED = "APPROVED"
    DEPLOYED = "DEPLOYED"
    ON_HOLD = "ON_HOLD"


class InterviewType(str, enum.Enum):
    """Interview type"""
    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"


class InterviewMode(str, enum.Enum):
    """Interview mode/format"""
    VIDEO_CALL = "VIDEO_CALL"
    PHONE_CALL = "PHONE_CALL"
    IN_PERSON = "IN_PERSON"
    PANEL_INTERVIEW = "PANEL_INTERVIEW"
    TECHNICAL_ROUND = "TECHNICAL_ROUND"
    HR_ROUND = "HR_ROUND"
    MANAGERIAL_ROUND = "MANAGERIAL_ROUND"


class InterviewStatus(str, enum.Enum):
    """Interview status"""
    SCHEDULED = "SCHEDULED"
    CONFIRMED = "CONFIRMED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    RESCHEDULED = "RESCHEDULED"
    NO_SHOW = "NO_SHOW"


class RequirementCandidate(Base):
    """Candidates suggested for a requirement"""
    __tablename__ = "requirement_candidates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    requirement_id = Column(UUID(as_uuid=True), ForeignKey("deployment_requests.id", ondelete="CASCADE"), nullable=False)
    maverick_id = Column(UUID(as_uuid=True), ForeignKey("mavericks.id", ondelete="CASCADE"), nullable=False)
    suggested_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    suggestion_date = Column(DateTime(timezone=True), server_default=func.now())
    match_score = Column(Numeric(5, 2), nullable=True)  # 0-100
    
    status = Column(
        SQLEnum(CandidateStatus, values_callable=lambda x: [e.value for e in x]),
        default=CandidateStatus.SUGGESTED,
        nullable=False
    )
    
    # Notes
    shortlist_notes = Column(Text, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    manager_notes = Column(Text, nullable=True)
    hr_notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    requirement = relationship("DeploymentRequest", back_populates="candidates")
    maverick = relationship("Maverick")
    suggested_by_user = relationship("User", foreign_keys=[suggested_by])
    interviews = relationship("RequirementInterview", back_populates="candidate", cascade="all, delete-orphan")


class RequirementInterview(Base):
    """Interview scheduling and feedback"""
    __tablename__ = "requirement_interviews"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    requirement_id = Column(UUID(as_uuid=True), ForeignKey("deployment_requests.id", ondelete="CASCADE"), nullable=False)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("requirement_candidates.id", ondelete="CASCADE"), nullable=False)
    maverick_id = Column(UUID(as_uuid=True), ForeignKey("mavericks.id", ondelete="CASCADE"), nullable=False)
    
    # Interview Details
    interview_type = Column(
        SQLEnum(InterviewType, values_callable=lambda x: [e.value for e in x]),
        default=InterviewType.ONLINE
    )
    interview_mode = Column(
        SQLEnum(InterviewMode, values_callable=lambda x: [e.value for e in x]),
        default=InterviewMode.VIDEO_CALL
    )
    interview_date = Column(Date, nullable=False)
    interview_time = Column(Time, nullable=False)
    duration_minutes = Column(Integer, default=60)
    
    # Location/Link
    location = Column(Text, nullable=True)  # For offline interviews
    video_link = Column(Text, nullable=True)  # For online interviews
    interviewer_panel = Column(JSONB, default=list)  # List of interviewer names/emails
    
    # Status
    status = Column(
        SQLEnum(InterviewStatus, values_callable=lambda x: [e.value for e in x]),
        default=InterviewStatus.SCHEDULED
    )
    
    # Feedback
    feedback = Column(Text, nullable=True)
    rating = Column(Numeric(2, 1), nullable=True)  # 1.0-5.0
    technical_rating = Column(Numeric(2, 1), nullable=True)
    communication_rating = Column(Numeric(2, 1), nullable=True)
    cultural_fit_rating = Column(Numeric(2, 1), nullable=True)
    
    # Metadata
    scheduled_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    completed_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    requirement = relationship("DeploymentRequest")
    candidate = relationship("RequirementCandidate", back_populates="interviews")
    maverick = relationship("Maverick")


class RequirementWorkflowHistory(Base):
    """Audit trail for workflow stage changes"""
    __tablename__ = "requirement_workflow_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    requirement_id = Column(UUID(as_uuid=True), ForeignKey("deployment_requests.id", ondelete="CASCADE"), nullable=False)

    from_stage = Column(String(50), nullable=True)
    to_stage = Column(String(50), nullable=False)
    changed_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    change_reason = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    requirement = relationship("DeploymentRequest")
    changed_by_user = relationship("User")


class RequirementNotification(Base):
    """Notifications for requirement workflow"""
    __tablename__ = "requirement_notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    requirement_id = Column(UUID(as_uuid=True), ForeignKey("deployment_requests.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    notification_type = Column(String(50), nullable=False)  # CANDIDATE_SUGGESTED, INTERVIEW_SCHEDULED, etc.
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)

    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime(timezone=True), nullable=True)

    notification_metadata = Column(JSONB, default=dict)  # Additional data (renamed from 'metadata' to avoid SQLAlchemy conflict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    requirement = relationship("DeploymentRequest")
    user = relationship("User")
