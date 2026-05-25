from sqlalchemy import Column, Integer, Text, Date, DateTime, ForeignKey, Numeric, Boolean, String
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from ..database import Base
from .types import GUID, JSON


class Assessment(Base):
    """Assessment job configuration"""
    __tablename__ = "assessments"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    job_id = Column(GUID, ForeignKey("pipeline_jobs.id"), nullable=False)
    batch_id = Column(GUID, ForeignKey("batches.id", ondelete="CASCADE"), nullable=False)

    # Assessment Details
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    assessment_link = Column(String(500), nullable=True)  # Link to Google Form, Typeform, etc.
    max_marks = Column(Numeric(5, 2), nullable=False)
    passing_marks = Column(Numeric(5, 2), nullable=False)
    duration_minutes = Column(Integer, nullable=True)
    scheduled_date = Column(DateTime(timezone=True), nullable=True)

    # Store job metadata (skills_tested, etc.) - renamed to avoid SQLAlchemy conflict
    config_metadata = Column(JSON, nullable=True)

    # Timestamps
    created_by = Column(GUID, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    attempts = relationship("AssessmentAttempt", back_populates="assessment", cascade="all, delete-orphan")
    job_schedule = relationship("BatchJobSchedule", back_populates="assessment", uselist=False)

    def __repr__(self):
        return f"<Assessment {self.title} - Max:{self.max_marks} Pass:{self.passing_marks}>"


class AssessmentAttempt(Base):
    """Track assessment attempts and scores"""
    __tablename__ = "assessment_attempts"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    assessment_id = Column(GUID, ForeignKey("assessments.id", ondelete="CASCADE"), nullable=False)
    maverick_id = Column(GUID, ForeignKey("mavericks.id", ondelete="CASCADE"), nullable=False)
    batch_id = Column(GUID, ForeignKey("batches.id", ondelete="CASCADE"), nullable=False)

    # Attempt Details
    marks_obtained = Column(Numeric(5, 2), nullable=False)
    max_marks = Column(Numeric(5, 2), nullable=False)
    passed = Column(Boolean, nullable=False)
    feedback = Column(Text, nullable=True)

    # Evaluation Info
    evaluated_by = Column(GUID, ForeignKey("users.id"), nullable=False)
    evaluated_at = Column(DateTime(timezone=True), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    assessment = relationship("Assessment", back_populates="attempts")
    maverick = relationship("Maverick", back_populates="assessment_attempts")
    batch = relationship("Batch", back_populates="assessment_attempts")

    def __repr__(self):
        return f"<AssessmentAttempt {self.maverick_id} - {'PASS' if self.passed else 'FAIL'} - {self.marks_obtained}/{self.max_marks}>"
