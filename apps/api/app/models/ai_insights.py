from sqlalchemy import Column, String, DateTime, Numeric
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid

from ..database import Base


class AIInsight(Base):
    """Store AI-generated insights"""
    __tablename__ = "ai_insights"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # What this insight is about
    entity_type = Column(String(50), nullable=False)  # maverick, batch, assessment, pipeline
    entity_id = Column(UUID(as_uuid=True), nullable=False)
    
    # Insight details
    insight_type = Column(String(100), nullable=False)  # role_match, gap_analysis, prediction, performance
    content = Column(JSONB, nullable=False)  # Actual insight data
    relevance_score = Column(Numeric(3, 2), nullable=True)
    
    generated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<AIInsight {self.insight_type} for {self.entity_type}:{self.entity_id}>"
