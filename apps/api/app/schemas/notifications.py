"""
Pydantic schemas for notifications
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from uuid import UUID
from datetime import datetime


class NotificationResponse(BaseModel):
    """Response for notification details"""
    id: UUID
    requirement_id: UUID
    notification_type: str
    title: str
    message: str
    is_read: bool
    read_at: Optional[datetime] = None
    metadata: dict = {}
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class NotificationListResponse(BaseModel):
    """List of notifications with pagination"""
    notifications: List[NotificationResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
    unread_count: int


class MarkAsReadRequest(BaseModel):
    """Request to mark notifications as read"""
    notification_ids: List[UUID] = Field(..., description="List of notification IDs to mark as read")


class NotificationStatsResponse(BaseModel):
    """Notification statistics"""
    total: int
    unread: int
