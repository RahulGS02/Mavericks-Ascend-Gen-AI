"""
Pydantic schemas for requirement workflow
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from uuid import UUID
from datetime import datetime, date, time
from decimal import Decimal


# ==================== Candidate Schemas ====================

class SuggestCandidateRequest(BaseModel):
    """HR: Suggest a candidate for a requirement"""
    maverick_id: UUID = Field(..., description="Maverick ID to suggest")
    match_score: Optional[Decimal] = Field(None, ge=0, le=100, description="Match score (0-100)")
    hr_notes: Optional[str] = Field(None, description="HR notes about this candidate")


class SuggestCandidatesRequest(BaseModel):
    """HR: Suggest multiple candidates at once"""
    candidates: List[SuggestCandidateRequest] = Field(..., description="List of candidates to suggest")


class ShortlistCandidateRequest(BaseModel):
    """Manager: Shortlist a suggested candidate"""
    manager_notes: Optional[str] = Field(None, description="Manager's notes about why shortlisting")


class RejectCandidateRequest(BaseModel):
    """Reject a candidate"""
    rejection_reason: str = Field(..., description="Reason for rejection")


class CandidateResponse(BaseModel):
    """Response for candidate details"""
    id: UUID
    requirement_id: UUID
    maverick_id: UUID
    maverick_name: Optional[str] = None
    maverick_email: Optional[str] = None
    suggested_by: Optional[UUID] = None
    suggested_by_name: Optional[str] = None
    suggestion_date: datetime
    match_score: Optional[Decimal] = None
    status: str
    shortlist_notes: Optional[str] = None
    rejection_reason: Optional[str] = None
    manager_notes: Optional[str] = None
    hr_notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Maverick details (populated from join)
    maverick_skills: Optional[List[str]] = None
    maverick_cgpa: Optional[Decimal] = None
    maverick_degree: Optional[str] = None
    maverick_branch: Optional[str] = None
    maverick_graduation_year: Optional[int] = None
    
    model_config = ConfigDict(from_attributes=True)


class CandidateListResponse(BaseModel):
    """List of candidates"""
    candidates: List[CandidateResponse]
    total: int


# ==================== Interview Schemas ====================

class ScheduleInterviewRequest(BaseModel):
    """Schedule an interview for a candidate"""
    interview_type: str = Field("ONLINE", description="ONLINE or OFFLINE")
    interview_mode: str = Field("VIDEO_CALL", description="VIDEO_CALL, PHONE_CALL, IN_PERSON, etc.")
    interview_date: date = Field(..., description="Interview date")
    interview_time: time = Field(..., description="Interview time")
    duration_minutes: int = Field(60, description="Duration in minutes")
    location: Optional[str] = Field(None, description="Location for offline interviews")
    video_link: Optional[str] = Field(None, description="Video call link for online interviews")
    interviewer_panel: List[str] = Field(default_factory=list, description="List of interviewer names/emails")


class UpdateInterviewStatusRequest(BaseModel):
    """Update interview status"""
    status: str = Field(..., description="CONFIRMED, IN_PROGRESS, COMPLETED, CANCELLED, etc.")
    notes: Optional[str] = Field(None, description="Optional notes")


class SubmitInterviewFeedbackRequest(BaseModel):
    """Submit interview feedback"""
    feedback: str = Field(..., description="Interview feedback text")
    rating: Decimal = Field(..., ge=1.0, le=5.0, description="Overall rating (1-5)")
    technical_rating: Optional[Decimal] = Field(None, ge=1.0, le=5.0, description="Technical rating")
    communication_rating: Optional[Decimal] = Field(None, ge=1.0, le=5.0, description="Communication rating")
    cultural_fit_rating: Optional[Decimal] = Field(None, ge=1.0, le=5.0, description="Cultural fit rating")


class InterviewResponse(BaseModel):
    """Response for interview details"""
    id: UUID
    requirement_id: UUID
    candidate_id: UUID
    maverick_id: UUID
    maverick_name: Optional[str] = None
    interview_type: str
    interview_mode: str
    interview_date: date
    interview_time: time
    duration_minutes: int
    location: Optional[str] = None
    video_link: Optional[str] = None
    interviewer_panel: List[str] = []
    status: str
    feedback: Optional[str] = None
    rating: Optional[Decimal] = None
    technical_rating: Optional[Decimal] = None
    communication_rating: Optional[Decimal] = None
    cultural_fit_rating: Optional[Decimal] = None
    scheduled_by: Optional[UUID] = None
    completed_by: Optional[UUID] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class InterviewListResponse(BaseModel):
    """List of interviews"""
    interviews: List[InterviewResponse]
    total: int


# ==================== Workflow Schemas ====================

class UpdateWorkflowStageRequest(BaseModel):
    """Update workflow stage"""
    to_stage: str = Field(..., description="Target workflow stage")
    reason: Optional[str] = Field(None, description="Reason for change")


class WorkflowHistoryResponse(BaseModel):
    """Workflow history entry"""
    id: UUID
    requirement_id: UUID
    from_stage: Optional[str] = None
    to_stage: str
    changed_by: Optional[UUID] = None
    changed_by_name: Optional[str] = None
    change_reason: Optional[str] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class WorkflowHistoryListResponse(BaseModel):
    """List of workflow history"""
    history: List[WorkflowHistoryResponse]
    total: int
