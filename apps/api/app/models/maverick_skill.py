"""
Maverick Skill Model
Tracks individual skill proficiency levels for each maverick
"""
from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum

from ..database import Base
from .types import GUID, JSON


class SkillCategory(str, enum.Enum):
    """Skill category enumeration"""
    TECHNICAL = "TECHNICAL"
    PROGRAMMING_LANGUAGE = "PROGRAMMING_LANGUAGE"
    FRAMEWORK = "FRAMEWORK"
    TOOL = "TOOL"
    DATABASE = "DATABASE"
    SOFT_SKILL = "SOFT_SKILL"
    OTHER = "OTHER"


class ProficiencyLevel(str, enum.Enum):
    """Proficiency level based on score - Simplified to 3 levels"""
    BEGINNER = "BEGINNER"          # 0-59
    INTERMEDIATE = "INTERMEDIATE"  # 60-79
    PROFICIENT = "PROFICIENT"      # 80-100


class MaverickSkill(Base):
    """
    Tracks skill proficiency for each maverick
    
    Proficiency is calculated from:
    - Assessment scores
    - Training completion
    - AI analysis
    - Self-declared skills
    """
    __tablename__ = "maverick_skills"
    
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    
    # Relationships
    maverick_id = Column(GUID, ForeignKey("mavericks.id", ondelete="CASCADE"), nullable=False)
    
    # Skill details
    skill_name = Column(String(255), nullable=False)  # e.g., "Python", "React", "Communication"
    category = Column(String(50), nullable=True)  # TECHNICAL, SOFT_SKILL, etc.
    
    # Proficiency scoring (0-100)
    proficiency_score = Column(Float, nullable=False, default=0.0)  # 0-100
    proficiency_level = Column(String(50), nullable=True)  # BEGINNER, INTERMEDIATE, ADVANCED, EXPERT
    
    # Sources of proficiency data
    assessment_score = Column(Float, nullable=True)  # Score from assessments (0-100)
    training_completion = Column(Float, nullable=True)  # Training completion % (0-100)
    self_declared = Column(Float, nullable=True)  # Self-assessment (0-100)
    ai_analyzed = Column(Float, nullable=True)  # AI-analyzed from resume/projects (0-100)
    
    # Metadata
    assessment_count = Column(Integer, default=0)  # Number of assessments taken
    training_count = Column(Integer, default=0)  # Number of trainings completed
    last_assessed_at = Column(DateTime(timezone=True), nullable=True)  # Last assessment date
    last_trained_at = Column(DateTime(timezone=True), nullable=True)  # Last training date
    
    # AI insights
    ai_feedback = Column(Text, nullable=True)  # AI-generated feedback on skill
    improvement_suggestions = Column(JSON, nullable=True)  # AI suggestions for improvement

    # Radar chart data
    radar_data = Column(JSON, nullable=True)  # Pre-computed radar chart coordinates
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    maverick = relationship("Maverick", back_populates="skill_proficiencies")
    
    def __repr__(self):
        return f"<MaverickSkill(maverick_id={self.maverick_id}, skill={self.skill_name}, score={self.proficiency_score})>"
