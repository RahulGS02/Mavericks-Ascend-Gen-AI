"""
HR Workflow schemas for review process
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID


class ReviewAction(BaseModel):
    """Schema for review action (shortlist/reject)"""
    maverick_id: UUID
    notes: Optional[str] = Field(None, description="Review notes or rejection reason")


class BulkShortlistRequest(BaseModel):
    """Schema for bulk shortlist request"""
    maverick_ids: List[UUID] = Field(..., description="List of maverick IDs to shortlist")
    notes: Optional[str] = Field(None, description="Common review notes for all")


class BulkRejectRequest(BaseModel):
    """Schema for bulk reject request"""
    maverick_ids: List[UUID] = Field(..., description="List of maverick IDs to reject")
    reason: str = Field(..., description="Common rejection reason")


class ReviewResponse(BaseModel):
    """Schema for review action response"""
    success: bool
    maverick_id: UUID
    new_status: str
    message: str


class BulkReviewResponse(BaseModel):
    """Schema for bulk review response"""
    success_count: int
    failed_count: int
    results: List[ReviewResponse]


class NotificationRequest(BaseModel):
    """Schema for sending notification emails"""
    maverick_ids: Optional[List[UUID]] = Field(
        None, 
        description="Specific maverick IDs to notify (if None, notifies all approved/rejected)"
    )
    status_filter: Optional[str] = Field(
        None,
        description="Filter by status: 'approved' or 'rejected'"
    )


class NotificationResponse(BaseModel):
    """Schema for notification response"""
    sent_count: int
    failed_count: int
    message: str
