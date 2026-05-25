"""
Batch-Trainer Association Model
Many-to-many relationship between batches and trainers
"""
from sqlalchemy import Column, DateTime, ForeignKey, Table, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from ..database import Base
from .types import GUID


class BatchTrainer(Base):
    """
    Association table for many-to-many relationship between Batch and Trainer (User)
    Allows multiple trainers to be assigned to a batch
    """
    __tablename__ = "batch_trainers"
    
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    batch_id = Column(GUID, ForeignKey("batches.id", ondelete="CASCADE"), nullable=False)
    trainer_id = Column(GUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    is_lead_trainer = Column(Boolean, default=False, nullable=False)  # Primary trainer for the batch
    assigned_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    assigned_by = Column(GUID, ForeignKey("users.id"), nullable=True)  # HR who assigned
    
    # Relationships
    batch = relationship("Batch", back_populates="batch_trainers")
    trainer = relationship("User", foreign_keys=[trainer_id], back_populates="trainer_assignments")
    assigner = relationship("User", foreign_keys=[assigned_by])
    
    def __repr__(self):
        return f"<BatchTrainer batch={self.batch_id} trainer={self.trainer_id} lead={self.is_lead_trainer}>"
