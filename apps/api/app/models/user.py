from sqlalchemy import Column, String, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum

from ..database import Base


class UserRole(str, enum.Enum):
    """User roles in the system"""
    MAVERICK = "maverick"
    TRAINER = "trainer"
    HR = "hr"
    MANAGER = "manager"
    SUPER_ADMIN = "super_admin"


class User(Base):
    """User model for authentication and authorization"""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    maverick = relationship("Maverick", back_populates="user", uselist=False, foreign_keys="Maverick.user_id")
    created_pipelines = relationship("Pipeline", back_populates="creator", foreign_keys="Pipeline.created_by")
    trained_batches = relationship("Batch", back_populates="trainer", foreign_keys="Batch.trainer_id")  # Legacy single trainer
    trainer_assignments = relationship("BatchTrainer", foreign_keys="BatchTrainer.trainer_id", back_populates="trainer")  # New: Multiple batch assignments
    
    def __repr__(self):
        return f"<User {self.email} ({self.role})>"
