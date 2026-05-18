"""
Deployment management schemas
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime, date
from uuid import UUID


class DeploymentRequestBase(BaseModel):
    """Base schema for deployment request - requirement card first, maverick assigned later"""
    maverick_id: Optional[UUID] = Field(None, description="Maverick ID (assigned later)")
    role_title: str = Field(..., description="Role/Position title (e.g., Senior Full Stack Developer)", max_length=255)
    project_name: Optional[str] = Field(None, description="Project name", max_length=255)
    vertical: Optional[str] = Field(None, description="Business vertical", max_length=100)
    competency: Optional[str] = Field(None, description="Competency area", max_length=100)
    required_skills: List[str] = Field(default_factory=list, description="Required skills for the role")
    preferred_skills: List[str] = Field(default_factory=list, description="Preferred/nice-to-have skills")
    role_description: Optional[str] = Field(None, description="Detailed role requirements and description")
    justification: Optional[str] = Field(None, description="Business justification for this requirement")
    positions_count: int = Field(1, ge=1, description="Number of positions to fill")


class DeploymentRequestCreate(DeploymentRequestBase):
    """Schema for creating deployment request"""
    pass


class DeploymentRequestResponse(DeploymentRequestBase):
    """Schema for deployment request response"""
    id: UUID
    requested_by: UUID
    requested_by_name: Optional[str] = None
    maverick_name: Optional[str] = None
    status: str  # PENDING, APPROVED, REJECTED
    approved_by: Optional[UUID] = None
    approved_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    filled_count: int = 0
    workflow_stage: Optional[str] = "PENDING"
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class DeploymentRequestListResponse(BaseModel):
    """Schema for paginated deployment request list"""
    requests: List[DeploymentRequestResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class ApproveDeploymentRequest(BaseModel):
    """Schema for approving deployment request"""
    notes: Optional[str] = Field(None, description="Approval notes")


class RejectDeploymentRequest(BaseModel):
    """Schema for rejecting deployment request"""
    rejection_reason: str = Field(..., description="Reason for rejection")


class DeployMaverickRequest(BaseModel):
    """Schema for deploying a maverick"""
    maverick_id: UUID = Field(..., description="Maverick ID")
    project_name: str = Field(..., description="Project name", max_length=255)
    vertical: str = Field(..., description="Business vertical", max_length=100)
    competency: str = Field(..., description="Competency area", max_length=100)
    start_date: date = Field(..., description="Deployment start date")
    end_date: Optional[date] = Field(None, description="Expected end date")
    role: Optional[str] = Field(None, description="Role/designation")
    manager_name: Optional[str] = Field(None, description="Project manager name")
    location: Optional[str] = Field(None, description="Deployment location")
    notes: Optional[str] = Field(None, description="Deployment notes")


class DeploymentResponse(BaseModel):
    """Schema for deployment response"""
    id: UUID
    maverick_id: UUID
    maverick_name: str
    batch_id: Optional[UUID] = None
    batch_name: Optional[str] = None
    project_name: str
    vertical: str
    competency: str
    start_date: date
    end_date: Optional[date] = None
    role: Optional[str] = None
    manager_name: Optional[str] = None
    location: Optional[str] = None
    status: str  # ACTIVE, COMPLETED, TERMINATED
    deployed_by: UUID
    deployed_at: datetime
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class DeploymentListResponse(BaseModel):
    """Schema for paginated deployment list"""
    deployments: List[DeploymentResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class DeploymentHistoryResponse(BaseModel):
    """Schema for deployment history"""
    maverick_id: UUID
    maverick_name: str
    total_deployments: int
    active_deployments: int
    completed_deployments: int
    deployments: List[DeploymentResponse] = []


class DeploymentStatistics(BaseModel):
    """Schema for deployment statistics"""
    total_deployments: int
    active_deployments: int
    completed_deployments: int
    deployments_by_vertical: dict
    deployments_by_competency: dict
    average_deployment_duration_days: float
    total_mavericks_deployed: int
