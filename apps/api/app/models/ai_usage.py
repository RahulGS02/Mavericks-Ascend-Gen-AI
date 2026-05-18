"""
AI Usage Tracking Models
"""
from sqlalchemy import Column, String, Integer, DateTime, Numeric, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from ..database import Base


class AIUsageLog(Base):
    """Log of AI API usage for cost tracking"""
    __tablename__ = "ai_usage_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Request Details
    feature = Column(String(100), nullable=False)  # skill_extraction, resume_parsing, etc.
    model = Column(String(100), nullable=False)
    
    # Token Usage
    input_tokens = Column(Integer, nullable=False)
    output_tokens = Column(Integer, nullable=False)
    total_tokens = Column(Integer, nullable=False)
    
    # Cost
    cost_usd = Column(Numeric(10, 6), nullable=False)
    
    # Request Info
    request_duration_ms = Column(Integer, nullable=True)
    success = Column(String(20), nullable=False)  # SUCCESS, ERROR, TIMEOUT
    error_message = Column(Text, nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<AIUsageLog {self.feature} - {self.total_tokens} tokens - ${self.cost_usd}>"
