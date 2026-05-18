"""
Trainer schemas for request/response validation
"""
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class TrainerCreate(BaseModel):
    """Schema for creating a new trainer"""
    name: str = Field(..., min_length=2, max_length=255, description="Full name")
    email: EmailStr = Field(..., description="Email address (will be used for login)")
    phone: Optional[str] = Field(None, max_length=20, description="Phone number")
    specialization: Optional[List[str]] = Field(None, description="Areas of expertise (e.g., ['React', 'Python', 'Data Science'])")
    bio: Optional[str] = Field(None, description="Short bio or description")


class TrainerResponse(BaseModel):
    """Schema for trainer response with generated credentials"""
    user_id: UUID
    name: str
    email: str
    phone: Optional[str]
    specialization: Optional[List[str]]
    bio: Optional[str]
    role: str
    is_active: bool
    created_at: datetime
    
    # Generated credentials (only returned once during creation)
    temp_password: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class TrainerListItem(BaseModel):
    """Schema for trainer in list view"""
    user_id: UUID
    name: str
    email: str
    phone: Optional[str]
    specialization: Optional[List[str]]
    is_active: bool
    created_at: datetime
    assigned_batches_count: int = 0
    is_idle: bool = False  # True if all assigned batches are 100% complete

    model_config = ConfigDict(from_attributes=True)


class TrainerListResponse(BaseModel):
    """Schema for paginated trainer list"""
    trainers: List[TrainerListItem]
    total: int
    page: int
    page_size: int
    total_pages: int


class TrainerUpdate(BaseModel):
    """Schema for updating trainer information"""
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    specialization: Optional[List[str]] = None
    bio: Optional[str] = None
    is_active: Optional[bool] = None
