"""
Assessment and marks entry schemas
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class AssessmentJobBase(BaseModel):
    """Base schema for assessment job"""
    job_id: UUID = Field(..., description="Pipeline job ID (must be ASSESSMENT type)")
    batch_id: UUID = Field(..., description="Batch ID")
    title: str = Field(..., description="Assessment title", max_length=255)
    description: Optional[str] = Field(None, description="Assessment description")
    assessment_link: Optional[str] = Field(None, description="Link to assessment (Google Form, etc.)", max_length=500)
    max_marks: float = Field(..., gt=0, description="Maximum marks")
    passing_marks: float = Field(..., gt=0, description="Passing marks threshold")
    duration_minutes: Optional[int] = Field(None, gt=0, description="Assessment duration")
    scheduled_date: Optional[datetime] = Field(None, description="Scheduled date")


class AssessmentJobCreate(AssessmentJobBase):
    """Schema for creating assessment job"""
    pass


class AssessmentJobResponse(AssessmentJobBase):
    """Schema for assessment job response"""
    id: UUID
    created_by: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    total_attempts: int = 0
    passed_count: int = 0
    failed_count: int = 0

    # Optional fields for frontend convenience
    batch_name: Optional[str] = None
    job_name: Optional[str] = None
    pending_count: int = 0
    evaluated_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class AssessmentAttemptBase(BaseModel):
    """Base schema for assessment attempt"""
    marks_obtained: float = Field(..., ge=0, description="Marks obtained")
    feedback: Optional[str] = Field(None, description="Feedback from evaluator")


class EnterMarksRequest(BaseModel):
    """Schema for entering marks manually"""
    maverick_id: UUID = Field(..., description="Maverick ID")
    marks_obtained: float = Field(..., ge=0, description="Marks obtained")
    feedback: Optional[str] = Field(None, description="Evaluator feedback")
    auto_progress: bool = Field(True, description="Auto-progress if passed")


class EnterMarksResponse(BaseModel):
    """Schema for marks entry response"""
    success: bool
    assessment_attempt_id: UUID
    maverick_id: UUID
    marks_obtained: float
    max_marks: float
    passed: bool
    progressed: bool
    message: str


class BulkMarksEntry(BaseModel):
    """Schema for bulk marks entry"""
    maverick_id: UUID
    marks_obtained: float
    feedback: Optional[str] = None


class BulkMarksRequest(BaseModel):
    """Schema for bulk marks upload"""
    entries: List[BulkMarksEntry] = Field(..., description="List of marks entries")
    auto_progress: bool = Field(True, description="Auto-progress passed students")


class BulkMarksResponse(BaseModel):
    """Schema for bulk marks response"""
    success_count: int
    failed_count: int
    passed_count: int
    progressed_count: int
    errors: List[dict] = []
    message: str


class ExcelMarksUploadResponse(BaseModel):
    """Schema for Excel marks upload response"""
    success_count: int
    failed_count: int
    total_rows: int
    passed_count: int
    progressed_count: int
    errors: List[dict] = []
    message: str


class AssessmentAttemptResponse(BaseModel):
    """Schema for assessment attempt response"""
    id: UUID
    assessment_id: UUID
    maverick_id: UUID
    maverick_name: str
    maverick_email: str
    batch_id: UUID
    marks_obtained: float
    max_marks: float
    percentage: float
    passed: bool
    feedback: Optional[str] = None
    evaluated_by: Optional[UUID] = None
    evaluated_at: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AssessmentHistoryResponse(BaseModel):
    """Schema for assessment history"""
    assessment_id: UUID
    assessment_title: str
    assessment_description: Optional[str] = None
    duration_minutes: Optional[int] = None
    batch_id: UUID
    batch_name: str
    trainer_id: Optional[UUID] = None
    trainer_name: Optional[str] = None
    max_marks: float
    passing_marks: float
    total_attempts: int
    attempts: List[AssessmentAttemptResponse] = []


class AssessmentListResponse(BaseModel):
    """Schema for paginated assessment list"""
    assessments: List[AssessmentJobResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class AssessmentStatistics(BaseModel):
    """Schema for assessment statistics"""
    total_assessments: int
    total_attempts: int
    pass_rate: float
    average_marks: float
    highest_marks: float
    lowest_marks: float
