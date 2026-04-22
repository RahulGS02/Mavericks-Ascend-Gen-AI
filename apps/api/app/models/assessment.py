from sqlalchemy import Column, Integer, Text, Date, DateTime, ForeignKey, Numeric, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from ..database import Base


class AssessmentAttempt(Base):
    """Track assessment attempts and scores"""
    __tablename__ = "assessment_attempts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey("pipeline_jobs.id"), nullable=False)
    maverick_id = Column(UUID(as_uuid=True), ForeignKey("mavericks.id", ondelete="CASCADE"), nullable=False)
    batch_id = Column(UUID(as_uuid=True), ForeignKey("batches.id", ondelete="CASCADE"), nullable=False)
    
    # Attempt Details
    attempt_number = Column(Integer, default=1, nullable=False)
    marks_obtained = Column(Numeric(5, 2), nullable=False)
    max_marks = Column(Numeric(5, 2), nullable=False)
    passed = Column(Boolean, nullable=False)
    
    # Assessment Info
    assessed_on = Column(Date, nullable=False)
    assessed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    remarks = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    job = relationship("PipelineJob", back_populates="assessment_attempts")
    maverick = relationship("Maverick", back_populates="assessment_attempts")
    batch = relationship("Batch", back_populates="assessment_attempts")
    
    def __repr__(self):
        return f"<AssessmentAttempt {self.maverick_id} - Attempt {self.attempt_number} - {'PASS' if self.passed else 'FAIL'}>"
