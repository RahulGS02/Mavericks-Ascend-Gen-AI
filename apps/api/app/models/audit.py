from sqlalchemy import Column, String, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid

from ..database import Base


class AuditLog(Base):
    """Audit trail for all system actions"""
    __tablename__ = "audit_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    # Action details
    action = Column(String(100), nullable=False)  # created, updated, deleted, login, etc.
    entity_type = Column(String(50), nullable=True)  # users, mavericks, batches, etc.
    entity_id = Column(UUID(as_uuid=True), nullable=True)
    
    # Change tracking
    old_value = Column(JSONB, nullable=True)
    new_value = Column(JSONB, nullable=True)
    
    # Request metadata
    ip_address = Column(String(45), nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    # Indexes for efficient querying
    __table_args__ = (
        Index('idx_audit_user_timestamp', 'user_id', 'timestamp'),
        Index('idx_audit_entity', 'entity_type', 'entity_id'),
    )
    
    def __repr__(self):
        return f"<AuditLog {self.action} on {self.entity_type} by {self.user_id}>"
