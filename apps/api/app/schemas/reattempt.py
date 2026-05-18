"""
Reattempt management schemas
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class ScheduleReattemptRequest(BaseModel):
    """Schema for scheduling a reattempt"""
    maverick_id: UUID = Field(..., description="Maverick ID")
    scheduled_date: Optional[datetime] = Field(None, description="Scheduled reattempt date")
    notes: Optional[str] = Field(None, description="Notes for scheduling reattempt")


class ScheduleReattemptResponse(BaseModel):
    """Schema for reattempt scheduling response"""
    success: bool
    maverick_id: UUID
    assessment_id: UUID
    attempt_number: int
    scheduled_date: Optional[datetime] = None
    message: str


class FailedMaverickInfo(BaseModel):
    """Schema for failed maverick information"""
    maverick_id: UUID
    maverick_name: str
    email: str
    last_attempt_id: UUID
    marks_obtained: float
    max_marks: float
    percentage: float
    total_attempts: int
    last_attempt_date: datetime
    feedback: Optional[str] = None
    can_reattempt: bool
    next_reattempt_available: Optional[datetime] = None


class FailedMavericksListResponse(BaseModel):
    """Schema for failed mavericks list"""
    assessment_id: UUID
    assessment_title: str
    batch_id: UUID
    total_failed: int
    failed_mavericks: List[FailedMaverickInfo] = []


class AttemptInfo(BaseModel):
    """Schema for attempt information"""
    attempt_id: UUID
    attempt_number: int
    marks_obtained: float
    max_marks: float
    percentage: float
    passed: bool
    evaluated_at: datetime
    feedback: Optional[str] = None


class MaverickAttemptHistory(BaseModel):
    """Schema for maverick's attempt history"""
    maverick_id: UUID
    maverick_name: str
    assessment_id: UUID
    assessment_title: str
    total_attempts: int
    passed: bool
    best_score: float
    latest_score: float
    attempts: List[AttemptInfo] = []


class UpdateAttemptStatusRequest(BaseModel):
    """Schema for updating attempt status"""
    status: str = Field(..., description="Status: PENDING, IN_PROGRESS, COMPLETED")
    notes: Optional[str] = Field(None, description="Status update notes")


class UpdateAttemptStatusResponse(BaseModel):
    """Schema for attempt status update response"""
    success: bool
    attempt_id: UUID
    new_status: str
    message: str


class ReattemptStatistics(BaseModel):
    """Schema for reattempt statistics"""
    assessment_id: UUID
    total_attempts: int
    first_attempt_count: int
    reattempt_count: int
    first_attempt_pass_rate: float
    reattempt_pass_rate: float
    average_attempts_to_pass: float
    max_attempts_by_maverick: int
