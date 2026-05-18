"""
Batch-Trainer Association Model
Many-to-many relationship between batches and trainers
"""
from sqlalchemy import Column, DateTime, ForeignKey, Table, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from ..database import Base


class BatchTrainer(Base):
    """
    Association table for many-to-many relationship between Batch and Trainer (User)
    Allows multiple trainers to be assigned to a batch
    """
    __tablename__ = "batch_trainers"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    batch_id = Column(UUID(as_uuid=True), ForeignKey("batches.id", ondelete="CASCADE"), nullable=False)
    trainer_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    is_lead_trainer = Column(Boolean, default=False, nullable=False)  # Primary trainer for the batch
    assigned_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    assigned_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)  # HR who assigned
    
    # Relationships
    batch = relationship("Batch", back_populates="batch_trainers")
    trainer = relationship("User", foreign_keys=[trainer_id], back_populates="trainer_assignments")
    assigner = relationship("User", foreign_keys=[assigned_by])
    
    def __repr__(self):
        return f"<BatchTrainer batch={self.batch_id} trainer={self.trainer_id} lead={self.is_lead_trainer}>"
