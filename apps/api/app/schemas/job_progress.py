"""
Job Progress schemas for tracking maverick progress through pipeline jobs
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class JobProgressBase(BaseModel):
    """Base schema for job progress"""
    notes: Optional[str] = Field(None, description="Progress notes")
    completion_percentage: Optional[int] = Field(None, ge=0, le=100, description="Completion percentage")


class InitializeJobProgressRequest(BaseModel):
    """Schema for initializing job progress for a maverick"""
    maverick_id: UUID = Field(..., description="Maverick ID")
    batch_id: UUID = Field(..., description="Batch ID")


class UpdateJobProgressRequest(BaseModel):
    """Schema for updating job progress"""
    status: Optional[str] = Field(None, description="Job status: PENDING, IN_PROGRESS, COMPLETED, FAILED, SKIPPED")
    completion_percentage: Optional[int] = Field(None, ge=0, le=100)
    notes: Optional[str] = None
    score: Optional[float] = Field(None, ge=0, le=100, description="Score for assessments")


class JobProgressResponse(BaseModel):
    """Schema for job progress response"""
    id: UUID
    maverick_id: UUID
    batch_id: UUID
    job_id: UUID
    job_name: str  # Included for convenience
    job_type: str
    status: str
    completion_percentage: Optional[int] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    score: Optional[float] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class MaverickProgressResponse(BaseModel):
    """Schema for maverick's overall progress"""
    maverick_id: UUID
    maverick_name: str
    batch_id: UUID
    batch_name: str
    pipeline_id: UUID
    pipeline_name: str
    total_jobs: int
    completed_jobs: int
    in_progress_jobs: int
    pending_jobs: int
    failed_jobs: int
    skipped_jobs: int
    overall_completion: float  # Percentage
    job_progress: List[JobProgressResponse] = []


class BatchProgressResponse(BaseModel):
    """Schema for batch progress summary"""
    batch_id: UUID
    batch_name: str
    pipeline_id: UUID
    pipeline_name: str
    total_mavericks: int
    total_jobs: int
    overall_completion: float  # Average completion across all mavericks
    maverick_progress: List[dict] = []  # Summary of each maverick's progress


class SkipJobRequest(BaseModel):
    """Schema for skipping an optional job"""
    reason: str = Field(..., description="Reason for skipping the job")


class SkipJobResponse(BaseModel):
    """Schema for skip job response"""
    success: bool
    maverick_id: UUID
    job_id: UUID
    message: str


class BulkInitializeResponse(BaseModel):
    """Schema for bulk initialization response"""
    success_count: int
    failed_count: int
    total_jobs_created: int
    message: str
