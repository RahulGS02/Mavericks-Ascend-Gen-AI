"""
Training session schemas for request/response validation
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime, date
from uuid import UUID


class TrainingSessionBase(BaseModel):
    """Base schema for training session"""
    title: str = Field(..., description="Training session title", max_length=255)
    description: Optional[str] = Field(None, description="Session description")
    job_id: UUID = Field(..., description="Pipeline job ID this session is for")
    trainer_id: Optional[UUID] = Field(None, description="Assigned trainer")
    scheduled_date: datetime = Field(..., description="Scheduled date and time")
    duration_minutes: int = Field(..., gt=0, description="Duration in minutes")
    location: Optional[str] = Field(None, description="Training location (online/offline)")
    meeting_link: Optional[str] = Field(None, description="Online meeting link")


class TrainingSessionCreate(TrainingSessionBase):
    """Schema for creating a training session"""
    batch_id: UUID = Field(..., description="Batch ID")


class TrainingSessionUpdate(BaseModel):
    """Schema for updating a training session"""
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    trainer_id: Optional[UUID] = None
    scheduled_date: Optional[datetime] = None
    duration_minutes: Optional[int] = Field(None, gt=0)
    location: Optional[str] = None
    meeting_link: Optional[str] = None
    status: Optional[str] = None


class TrainingSessionResponse(TrainingSessionBase):
    """Schema for training session response"""
    id: UUID
    batch_id: UUID
    batch_name: str  # For convenience
    status: str
    completed_at: Optional[datetime] = None
    completion_notes: Optional[str] = None
    attendance_count: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class TrainingSessionListResponse(BaseModel):
    """Schema for paginated training session list"""
    sessions: List[TrainingSessionResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class MarkCompleteRequest(BaseModel):
    """Schema for marking training as complete"""
    completion_notes: Optional[str] = Field(None, description="Notes about the session")
    attendance_count: Optional[int] = Field(None, ge=0, description="Number of attendees")
    actual_duration_minutes: Optional[int] = Field(None, gt=0, description="Actual duration")


class MarkCompleteResponse(BaseModel):
    """Schema for mark complete response"""
    success: bool
    session_id: UUID
    message: str
    completed_at: datetime


class TrainingCalendarDay(BaseModel):
    """Schema for a day in the training calendar"""
    date: date
    sessions: List[dict] = []  # Simplified session info


class TrainingCalendarResponse(BaseModel):
    """Schema for training calendar"""
    month: int
    year: int
    batch_id: Optional[UUID] = None
    batch_name: Optional[str] = None
    days: List[TrainingCalendarDay]
    total_sessions: int


class TrainingStatistics(BaseModel):
    """Schema for training statistics"""
    total_sessions: int
    scheduled_sessions: int
    completed_sessions: int
    cancelled_sessions: int
    upcoming_sessions: int
    total_training_hours: float
    average_attendance: float
