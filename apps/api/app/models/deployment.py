from sqlalchemy import Column, String, Text, Date, DateTime, Integer, ForeignKey, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum

from ..database import Base
from .types import GUID


class DeploymentRequestStatus(str, enum.Enum):
    """Status of deployment requests"""
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class DeploymentStatus(str, enum.Enum):
    """Status of deployments"""
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    TERMINATED = "TERMINATED"


class Deployment(Base):
    """Final deployment record"""
    __tablename__ = "deployments"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    maverick_id = Column(GUID, ForeignKey("mavericks.id", ondelete="CASCADE"), nullable=False)
    batch_id = Column(GUID, ForeignKey("batches.id"), nullable=True)

    # Deployment Details
    project_name = Column(String(255), nullable=False)
    vertical = Column(String(100), nullable=False)  # Banking, Healthcare, etc.
    competency = Column(String(100), nullable=False)  # Backend, Frontend, etc.
    role = Column(String(255), nullable=True)
    manager_name = Column(String(255), nullable=True)
    location = Column(String(255), nullable=True)

    # Dates
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)

    # Status
    status = Column(SQLEnum(DeploymentStatus, values_callable=lambda x: [e.value for e in x]), default=DeploymentStatus.ACTIVE, nullable=False)

    # Metadata
    deployed_by = Column(GUID, ForeignKey("users.id"), nullable=False)
    deployed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    maverick = relationship("Maverick", back_populates="deployments")
    batch = relationship("Batch", back_populates="deployments")

    def __repr__(self):
        return f"<Deployment {self.maverick_id} to {self.project_name}>"


class DeploymentRequest(Base):
    """Deployment requirement cards - post requirements, assign mavericks later"""
    __tablename__ = "deployment_requests"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    maverick_id = Column(GUID, ForeignKey("mavericks.id"), nullable=True)  # Assigned later
    requested_by = Column(GUID, ForeignKey("users.id"), nullable=False)  # Manager or HR

    # Role Requirements (Most Important!)
    role_title = Column(String(255), nullable=False)  # e.g., "Senior Full Stack Developer"
    role_description = Column(Text, nullable=True)  # Detailed requirements
    required_skills = Column(Text, nullable=True)  # JSON array stored as text
    preferred_skills = Column(Text, nullable=True)  # JSON array stored as text

    # Project Details
    project_name = Column(String(255), nullable=True)
    vertical = Column(String(100), nullable=True)
    competency = Column(String(100), nullable=True)
    justification = Column(Text, nullable=True)  # Business justification

    # Review
    status = Column(SQLEnum(DeploymentRequestStatus, values_callable=lambda x: [e.value for e in x]), default=DeploymentRequestStatus.PENDING, nullable=False)
    approved_by = Column(GUID, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    rejection_reason = Column(Text, nullable=True)

    # Workflow fields (new)
    positions_count = Column(Integer, default=1, nullable=False)  # Number of positions
    filled_count = Column(Integer, default=0, nullable=False)  # How many filled
    workflow_stage = Column(String(50), default='PENDING', nullable=True)  # Current workflow stage

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    maverick = relationship("Maverick", back_populates="deployment_requests")
    candidates = relationship("RequirementCandidate", back_populates="requirement", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<DeploymentRequest {self.maverick_id} - {self.status}>"
