"""
Pipeline schemas for request/response validation
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


class JobBase(BaseModel):
    """Base schema for pipeline job"""
    name: str = Field(..., description="Job name")
    description: Optional[str] = Field(None, description="Job description")
    job_type: str = Field(..., description="Job type: TRAINING, ASSESSMENT, DEPLOYMENT")
    sequence_order: int = Field(..., description="Order in pipeline")
    duration_days: Optional[int] = Field(None, description="Estimated duration in days")
    prerequisites: Optional[str] = Field(None, description="Prerequisites for this job")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Job-specific configuration (e.g., skills_tested for assessments)")


class JobCreate(JobBase):
    """Schema for creating a pipeline job"""
    pass


class JobUpdate(BaseModel):
    """Schema for updating a pipeline job"""
    name: Optional[str] = None
    description: Optional[str] = None
    job_type: Optional[str] = None
    sequence_order: Optional[int] = None
    duration_days: Optional[int] = None
    prerequisites: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class JobResponse(BaseModel):
    """Schema for pipeline job response"""
    id: UUID
    pipeline_id: UUID
    name: str
    description: Optional[str] = None
    job_type: str
    sequence_order: int
    duration_days: Optional[int] = None
    prerequisites: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    # Use job_metadata from the model (not metadata which conflicts with SQLAlchemy)
    job_metadata: Optional[Dict[str, Any]] = Field(None, alias="job_metadata")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class PipelineBase(BaseModel):
    """Base schema for pipeline"""
    name: str = Field(..., description="Pipeline name", max_length=255)
    description: Optional[str] = Field(None, description="Pipeline description")
    status: Optional[str] = Field("DRAFT", description="Pipeline status")


class PipelineCreate(PipelineBase):
    """Schema for creating a pipeline"""
    jobs: Optional[List[JobCreate]] = Field(default=[], description="Initial jobs in pipeline")


class PipelineUpdate(BaseModel):
    """Schema for updating a pipeline"""
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    status: Optional[str] = None


class PipelineResponse(PipelineBase):
    """Schema for pipeline response"""
    id: UUID
    created_by: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    jobs: List[JobResponse] = []

    model_config = ConfigDict(from_attributes=True)


class PipelineListResponse(BaseModel):
    """Schema for paginated pipeline list"""
    pipelines: List[PipelineResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class PipelineWithStats(PipelineResponse):
    """Pipeline with additional statistics"""
    total_jobs: int
    completed_jobs: int
    active_jobs: int
    total_mavericks: int = 0


class AddJobsToPipelineRequest(BaseModel):
    """Schema for adding multiple jobs to pipeline"""
    jobs: List[JobCreate] = Field(..., description="List of jobs to add")


class ReorderJobsRequest(BaseModel):
    """Schema for reordering jobs in pipeline"""
    job_orders: List[dict] = Field(
        ..., 
        description="List of {job_id, sequence_order} to reorder jobs",
        example=[
            {"job_id": "uuid-1", "sequence_order": 1},
            {"job_id": "uuid-2", "sequence_order": 2}
        ]
    )


class DeletePipelineResponse(BaseModel):
    """Schema for pipeline deletion response"""
    success: bool
    message: str
    deleted_pipeline_id: UUID
    deleted_jobs_count: int
