"""
Batch schemas for request/response validation
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime, date
from uuid import UUID
from enum import Enum


class BatchCategoryEnum(str, Enum):
    """Batch category enumeration"""
    TECH_DEVELOPMENT = "TECH_DEVELOPMENT"
    TECH_DEVOPS = "TECH_DEVOPS"
    TECH_TESTING = "TECH_TESTING"
    TECH_DATA_SCIENCE = "TECH_DATA_SCIENCE"
    TECH_CYBER_SECURITY = "TECH_CYBER_SECURITY"
    SOFT_SKILLS = "SOFT_SKILLS"


class BatchBase(BaseModel):
    """Base schema for batch"""
    name: str = Field(..., description="Batch name", max_length=255)
    description: Optional[str] = Field(None, description="Batch description")
    pipeline_id: UUID = Field(..., description="Pipeline to use for this batch")
    start_date: date = Field(..., description="Batch start date")
    end_date: Optional[date] = Field(None, description="Batch end date")
    max_capacity: Optional[int] = Field(None, description="Maximum number of mavericks")

    # AI Batch Matching Fields
    category: Optional[BatchCategoryEnum] = Field(None, description="Batch category for AI matching")
    focus_areas: Optional[List[str]] = Field(None, description="Batch focus areas (e.g., ['React', 'Node.js'])")
    required_skills: Optional[List[str]] = Field(None, description="Must-have skills")
    preferred_skills: Optional[List[str]] = Field(None, description="Nice-to-have skills")
    target_role: Optional[str] = Field(None, description="Target job role (e.g., 'Full Stack Developer')")


class BatchCreate(BatchBase):
    """Schema for creating a batch"""
    trainer_id: Optional[UUID] = Field(None, description="Assigned trainer ID")


class BatchUpdate(BaseModel):
    """Schema for updating a batch"""
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    max_capacity: Optional[int] = None
    status: Optional[str] = None
    trainer_id: Optional[UUID] = Field(None, description="Assigned trainer ID")
    category: Optional[BatchCategoryEnum] = None
    focus_areas: Optional[List[str]] = None
    required_skills: Optional[List[str]] = None
    preferred_skills: Optional[List[str]] = None
    target_role: Optional[str] = None


class BatchResponse(BatchBase):
    """Schema for batch response"""
    id: UUID
    status: str
    current_enrollment: int = 0
    trainer_id: Optional[UUID] = None
    created_by: Optional[UUID] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class BatchListResponse(BaseModel):
    """Schema for paginated batch list"""
    batches: List[BatchResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class BatchWithMavericks(BatchResponse):
    """Batch with enrolled mavericks"""
    mavericks: List[dict] = []  # Will contain maverick details


class AssignMaverickRequest(BaseModel):
    """Schema for assigning a maverick to batch"""
    maverick_id: UUID = Field(..., description="Maverick ID to assign")
    notes: Optional[str] = Field(None, description="Assignment notes")


class BulkAssignRequest(BaseModel):
    """Schema for bulk assigning mavericks"""
    maverick_ids: List[UUID] = Field(..., description="List of maverick IDs")
    notes: Optional[str] = Field(None, description="Common notes for all")


class AssignmentResponse(BaseModel):
    """Schema for assignment response"""
    success: bool
    maverick_id: UUID
    batch_id: UUID
    message: str


class BulkAssignmentResponse(BaseModel):
    """Schema for bulk assignment response"""
    success_count: int
    failed_count: int
    results: List[AssignmentResponse]


class ExcelUploadResponse(BaseModel):
    """Schema for Excel upload response"""
    success_count: int
    failed_count: int
    total_rows: int
    errors: List[dict] = []
    message: str


class BatchStatistics(BaseModel):
    """Schema for batch statistics"""
    total_batches: int
    active_batches: int
    completed_batches: int
    total_enrolled: int
    average_enrollment: float



# === Multiple Trainer Management Schemas ===

class TrainerInfo(BaseModel):
    """Schema for trainer basic info"""
    user_id: UUID
    name: str
    email: str
    is_lead: bool = False
    assigned_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AssignTrainerRequest(BaseModel):
    """Schema for assigning a trainer to batch"""
    trainer_id: UUID = Field(..., description="Trainer user ID")
    is_lead_trainer: bool = Field(False, description="Mark as lead/primary trainer")


class AssignMultipleTrainersRequest(BaseModel):
    """Schema for assigning multiple trainers to batch"""
    trainer_ids: List[UUID] = Field(..., description="List of trainer user IDs")
    lead_trainer_id: Optional[UUID] = Field(None, description="Which trainer should be the lead")


class RemoveTrainerRequest(BaseModel):
    """Schema for removing a trainer from batch"""
    trainer_id: UUID = Field(..., description="Trainer user ID to remove")


class TrainerAssignmentResponse(BaseModel):
    """Schema for trainer assignment response"""
    success: bool
    batch_id: UUID
    trainer_id: UUID
    is_lead: bool
    message: str


class BatchWithTrainers(BatchResponse):
    """Batch response with assigned trainers list"""
    trainers: List[TrainerInfo] = []
