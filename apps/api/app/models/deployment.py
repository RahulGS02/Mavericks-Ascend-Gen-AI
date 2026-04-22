from sqlalchemy import Column, String, Text, Date, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum

from ..database import Base


class DeploymentRequestStatus(str, enum.Enum):
    """Status of deployment requests"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class Deployment(Base):
    """Final deployment record"""
    __tablename__ = "deployments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    maverick_id = Column(UUID(as_uuid=True), ForeignKey("mavericks.id", ondelete="CASCADE"), nullable=False)
    batch_id = Column(UUID(as_uuid=True), ForeignKey("batches.id"), nullable=False)
    
    # Deployment Details
    project_name = Column(String(255), nullable=False)
    vertical = Column(String(100), nullable=False)  # Banking, Healthcare, etc.
    competency = Column(String(100), nullable=False)  # Backend, Frontend, etc.
    role_title = Column(String(255), nullable=False)
    deployment_date = Column(Date, nullable=False)
    
    # Metadata
    deployed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    remarks = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    maverick = relationship("Maverick", back_populates="deployments")
    batch = relationship("Batch", back_populates="deployments")
    
    def __repr__(self):
        return f"<Deployment {self.maverick_id} to {self.project_name}>"


class DeploymentRequest(Base):
    """Deployment requests from managers"""
    __tablename__ = "deployment_requests"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    maverick_id = Column(UUID(as_uuid=True), ForeignKey("mavericks.id"), nullable=False)
    requested_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)  # Manager
    
    # Request Details
    project_name = Column(String(255), nullable=False)
    vertical = Column(String(100), nullable=False)
    role_title = Column(String(255), nullable=False)
    required_start_date = Column(Date, nullable=False)
    justification = Column(Text, nullable=False)
    
    # Review
    status = Column(SQLEnum(DeploymentRequestStatus), default=DeploymentRequestStatus.PENDING, nullable=False)
    reviewed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    review_notes = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    maverick = relationship("Maverick", back_populates="deployment_requests")
    
    def __repr__(self):
        return f"<DeploymentRequest {self.maverick_id} - {self.status}>"
