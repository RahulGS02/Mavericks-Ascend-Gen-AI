"""
Trainer Feedback Model
Stores feedback from mavericks about trainers after completing training
"""
import uuid
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from ..database import Base
from .types import GUID


class FeedbackRating(str, enum.Enum):
    """Feedback rating scale"""
    EXCELLENT = "excellent"  # 5 stars
    GOOD = "good"  # 4 stars
    AVERAGE = "average"  # 3 stars
    POOR = "poor"  # 2 stars
    VERY_POOR = "very_poor"  # 1 star


class TrainerFeedback(Base):
    """
    Trainer Feedback from Mavericks
    
    After completing training in a batch, mavericks provide feedback about the trainer.
    This helps HR evaluate trainer performance and identify areas for improvement.
    """
    __tablename__ = "trainer_feedback"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)

    # Foreign Keys
    maverick_id = Column(GUID, ForeignKey("mavericks.id", ondelete="CASCADE"), nullable=False)
    trainer_id = Column(GUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    batch_id = Column(GUID, ForeignKey("batches.id", ondelete="CASCADE"), nullable=False)
    
    # Rating (1-5 stars)
    rating = Column(SQLEnum(FeedbackRating, name='feedbackrating', create_constraint=True, native_enum=True), nullable=False)
    
    # Detailed feedback
    subject_knowledge = Column(Integer, nullable=False)  # 1-5 scale
    communication_skills = Column(Integer, nullable=False)  # 1-5 scale
    session_quality = Column(Integer, nullable=False)  # 1-5 scale
    doubt_resolution = Column(Integer, nullable=False)  # 1-5 scale
    
    # Text feedback
    positive_feedback = Column(Text, nullable=True)  # What went well
    areas_for_improvement = Column(Text, nullable=True)  # What can be improved
    additional_comments = Column(Text, nullable=True)  # Any other comments
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    maverick = relationship("Maverick", backref="trainer_feedbacks")
    trainer = relationship("User", backref="received_feedbacks", foreign_keys=[trainer_id])
    batch = relationship("Batch", backref="trainer_feedbacks")

    def __repr__(self):
        return f"<TrainerFeedback {self.maverick_id} -> {self.trainer_id} (Rating: {self.rating})>"
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": str(self.id),
            "maverick_id": str(self.maverick_id),
            "trainer_id": str(self.trainer_id),
            "batch_id": str(self.batch_id),
            "rating": self.rating.value,
            "subject_knowledge": self.subject_knowledge,
            "communication_skills": self.communication_skills,
            "session_quality": self.session_quality,
            "doubt_resolution": self.doubt_resolution,
            "positive_feedback": self.positive_feedback,
            "areas_for_improvement": self.areas_for_improvement,
            "additional_comments": self.additional_comments,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
