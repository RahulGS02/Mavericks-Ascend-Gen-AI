"""
Batch Job Schedule Schemas for API Request/Response validation
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class BatchJobScheduleBase(BaseModel):
    """Base schema for batch job schedule"""
    scheduled_start_date: Optional[datetime] = Field(None, description="Scheduled start date/time")
    scheduled_end_date: Optional[datetime] = Field(None, description="Scheduled end date/time (deadline)")
    meeting_link: Optional[str] = Field(None, description="Meeting link for training sessions", max_length=500)
    meeting_password: Optional[str] = Field(None, description="Meeting password", max_length=100)
    attendance_required: Optional[bool] = Field(False, description="Is attendance tracking required")
    deployment_project_link: Optional[str] = Field(None, description="Link to deployment project/repo", max_length=500)
    trainer_notes: Optional[str] = Field(None, description="Notes from trainer")
    is_published: Optional[bool] = Field(False, description="Whether mavericks can see this schedule")


class AssessmentData(BaseModel):
    """Nested assessment data for scheduling"""
    title: str = Field(..., description="Assessment title")
    description: Optional[str] = Field(None, description="Assessment description")
    assessment_link: str = Field(..., description="Link to assessment (Google Form, etc.)")
    max_marks: float = Field(..., gt=0, description="Maximum marks")
    passing_marks: float = Field(..., gt=0, description="Passing marks threshold")
    duration_minutes: int = Field(..., gt=0, description="Assessment duration in minutes")


class ScheduleJobRequest(BatchJobScheduleBase):
    """Request to schedule a pipeline job in a batch"""
    pipeline_job_id: UUID = Field(..., description="Pipeline job ID to schedule")

    # For ASSESSMENT type jobs - create assessment inline
    assessment_data: Optional[AssessmentData] = Field(None, description="Assessment data if job type is ASSESSMENT")


class UpdateScheduleRequest(BatchJobScheduleBase):
    """Request to update an existing schedule"""
    status: Optional[str] = Field(None, description="Job status")
    actual_start_date: Optional[datetime] = Field(None, description="Actual start date")
    actual_end_date: Optional[datetime] = Field(None, description="Actual completion date")
    completion_percentage: Optional[int] = Field(None, description="Completion percentage (0-100)", ge=0, le=100)
    attendance_count: Optional[int] = Field(None, description="Number of mavericks who attended", ge=0)


class BatchJobScheduleResponse(BaseModel):
    """Response schema for batch job schedule"""
    id: UUID
    batch_id: UUID
    pipeline_job_id: UUID
    
    # Pipeline job details (denormalized for convenience)
    job_name: str
    job_type: str
    job_sequence_order: int
    job_is_mandatory: bool
    job_duration_days: Optional[int] = None
    
    # Scheduling
    scheduled_start_date: Optional[datetime] = None
    scheduled_end_date: Optional[datetime] = None
    actual_start_date: Optional[datetime] = None
    actual_end_date: Optional[datetime] = None
    
    # Training details
    meeting_link: Optional[str] = None
    meeting_password: Optional[str] = None
    attendance_required: bool = False
    attendance_count: int = 0
    
    # Assessment link
    assessment_id: Optional[UUID] = None
    
    # Deployment link
    deployment_project_link: Optional[str] = None
    
    # Status
    status: str
    completion_percentage: int = 0
    is_overdue: bool = False
    
    # Notes
    trainer_notes: Optional[str] = None
    is_published: bool = False
    
    # Metadata
    created_by: Optional[UUID] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class BatchTimelineResponse(BaseModel):
    """Complete timeline for a batch with all scheduled jobs"""
    batch_id: UUID
    batch_name: str
    pipeline_id: UUID
    pipeline_name: str
    batch_start_date: Optional[datetime] = None
    batch_end_date: Optional[datetime] = None
    
    # Statistics
    total_jobs: int
    scheduled_jobs: int
    completed_jobs: int
    in_progress_jobs: int
    overdue_jobs: int
    
    # Timeline
    schedules: List[BatchJobScheduleResponse] = []
    
    # Unscheduled pipeline jobs
    unscheduled_jobs: List[dict] = []


class MarkAttendanceRequest(BaseModel):
    """Request to mark attendance for a training session"""
    maverick_ids: List[UUID] = Field(..., description="List of maverick IDs who attended")
    notes: Optional[str] = Field(None, description="Attendance notes")


class MarkAttendanceResponse(BaseModel):
    """Response for attendance marking"""
    success: bool
    attendance_count: int
    message: str


class QuickScheduleAllRequest(BaseModel):
    """Request to quickly schedule all unscheduled jobs"""
    start_date: datetime = Field(..., description="Start date for first job")
    auto_calculate_dates: bool = Field(True, description="Auto-calculate dates based on duration_days")
    buffer_days: int = Field(1, description="Buffer days between jobs", ge=0, le=7)


class QuickScheduleAllResponse(BaseModel):
    """Response for quick schedule all"""
    success: bool
    scheduled_count: int
    failed_count: int
    message: str
    schedules: List[BatchJobScheduleResponse] = []
