"""
Super Admin schemas for request/response validation
"""
from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_serializer
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


class UserCreateAdmin(BaseModel):
    """Schema for creating users (Super Admin only)"""
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)
    name: str = Field(..., min_length=2, max_length=255)
    role: str = Field(..., description="User role: maverick, trainer, hr, manager, super_admin")
    is_active: bool = True


class UserUpdateAdmin(BaseModel):
    """Schema for updating users (Super Admin only)"""
    email: Optional[EmailStr] = None
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    role: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = Field(None, min_length=6, max_length=100)


class UserResponseAdmin(BaseModel):
    """Extended user response for admin (includes more details)"""
    id: UUID
    email: str
    name: str
    role: str
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    
    @field_serializer('id')
    def serialize_uuid(self, value):
        return str(value)
    
    @field_serializer('role')
    def serialize_role(self, value):
        if hasattr(value, 'value'):
            return value.value
        return value
    
    model_config = ConfigDict(from_attributes=True)


class UserListAdminResponse(BaseModel):
    """Response for admin user list"""
    users: List[UserResponseAdmin]
    total: int
    page: int
    page_size: int
    total_pages: int


class AuditLogResponse(BaseModel):
    """Audit log entry response"""
    id: UUID
    user_id: Optional[UUID]
    user_name: Optional[str]
    action: str
    entity_type: Optional[str]
    entity_id: Optional[UUID]
    old_value: Optional[Dict[str, Any]]
    new_value: Optional[Dict[str, Any]]
    ip_address: Optional[str]
    timestamp: datetime
    
    @field_serializer('id', 'user_id', 'entity_id')
    def serialize_uuid(self, value):
        if value is None:
            return None
        return str(value)
    
    model_config = ConfigDict(from_attributes=True)


class AuditLogListResponse(BaseModel):
    """Response for audit log list"""
    logs: List[AuditLogResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class SystemStatsResponse(BaseModel):
    """System-wide statistics for Super Admin dashboard"""
    total_users: int
    users_by_role: Dict[str, int]
    active_users: int
    inactive_users: int
    total_mavericks: int
    total_batches: int
    total_deployments: int
    ai_requests_today: int
    ai_cost_today: float
    ai_cost_this_month: float
    failed_logins_today: int
    system_uptime_hours: float
    active_sessions: int
    

class SystemHealthResponse(BaseModel):
    """System health metrics"""
    database_status: str
    database_connections: int
    api_response_time_ms: float
    error_rate_percentage: float
    uptime_percentage: float
    

class EmergencyActionRequest(BaseModel):
    """Request for emergency actions"""
    action: str = Field(..., description="Action: disable_ai, force_logout_all, maintenance_mode")
    reason: str = Field(..., min_length=10)
    

class EmergencyActionResponse(BaseModel):
    """Response for emergency action"""
    success: bool
    action: str
    message: str
    timestamp: datetime


class SystemSettingsResponse(BaseModel):
    """System settings (masked sensitive data)"""
    ai_enabled: bool
    ai_model: str
    ai_max_tokens: int
    ai_daily_limit: int
    ai_rate_limit_per_minute: int
    ai_resume_parsing_enabled: bool
    ai_skill_extraction_enabled: bool
    ai_performance_insights_enabled: bool
    environment: str
