"""
Maverick schemas for request/response validation
"""
from pydantic import BaseModel, EmailStr, Field, field_serializer, ConfigDict
from typing import Any, Dict, Optional, List
from datetime import datetime
from uuid import UUID
from ..models.maverick import ProfileStatus, DeploymentStatus


class MaverickCreate(BaseModel):
    """Schema for creating a new maverick"""
    name: str = Field(..., min_length=2, max_length=255)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=20)
    college: Optional[str] = Field(None, max_length=255)
    degree: Optional[str] = Field(None, max_length=255)
    branch: Optional[str] = Field(None, max_length=255)
    graduation_year: Optional[int] = None
    cgpa: Optional[float] = Field(None, ge=0, le=10)
    skills: Optional[List[str]] = []
    resume_url: Optional[str] = None
    github_url: Optional[str] = None
    linkedin_url: Optional[str] = None


class MaverickUpdate(BaseModel):
    """Schema for updating maverick profile"""
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    college: Optional[str] = Field(None, max_length=255)
    degree: Optional[str] = Field(None, max_length=255)
    branch: Optional[str] = Field(None, max_length=255)
    graduation_year: Optional[int] = None
    cgpa: Optional[float] = Field(None, ge=0, le=10)
    skills: Optional[List[str]] = None
    resume_url: Optional[str] = None
    github_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    current_batch_id: Optional[str] = None


class MaverickResponse(BaseModel):
    """Schema for maverick response"""
    id: UUID
    user_id: Optional[UUID]
    name: str
    email: str
    phone: Optional[str]
    college: Optional[str]
    degree: Optional[str]
    branch: Optional[str]
    graduation_year: Optional[int]
    cgpa: Optional[float]
    skills: List[str]
    resume_url: Optional[str]
    github_url: Optional[str]
    linkedin_url: Optional[str]
    profile_status: str
    deployment_status: str
    current_batch_id: Optional[UUID]
    reviewed_by: Optional[UUID]
    review_notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    # AI-parsed resume data
    ai_extracted_skills: Optional[List[str]] = None
    ai_summary: Optional[str] = None
    ai_resume_data: Optional[Dict[str, Any]] = None

    @field_serializer('profile_status', 'deployment_status')
    def serialize_enum(self, value):
        """Convert enum to string value"""
        if hasattr(value, 'value'):
            return value.value
        return value

    model_config = ConfigDict(from_attributes=True)


class MaverickListResponse(BaseModel):
    """Schema for maverick list response"""
    mavericks: List[MaverickResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class MaverickWithResumeCreate(BaseModel):
    """Schema for creating maverick with resume upload"""
    name: str = Field(..., min_length=2, max_length=255)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=20)
    college: Optional[str] = Field(None, max_length=255)
    degree: Optional[str] = Field(None, max_length=255)
    branch: Optional[str] = Field(None, max_length=255)
    graduation_year: Optional[int] = None
    cgpa: Optional[float] = Field(None, ge=0, le=10)
    github_url: Optional[str] = None
    linkedin_url: Optional[str] = None


class ProfileStatusUpdate(BaseModel):
    """Schema for updating profile status"""
    profile_status: str = Field(..., description="pending, approved, rejected")
    review_notes: Optional[str] = None


class DeploymentStatusUpdate(BaseModel):
    """Schema for updating deployment status"""
    deployment_status: str = Field(..., description="available, deployed, on_bench")
