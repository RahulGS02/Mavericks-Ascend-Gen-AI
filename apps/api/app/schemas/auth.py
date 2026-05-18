"""
Authentication schemas for request/response validation
"""
from pydantic import BaseModel, EmailStr, Field, field_serializer
from typing import Optional
from datetime import datetime
from uuid import UUID


class UserRegister(BaseModel):
    """User registration request schema"""
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)
    name: str = Field(..., min_length=2, max_length=255)
    role: str = Field(..., description="User role: maverick, trainer, hr, manager, super_admin")


class UserLogin(BaseModel):
    """User login request schema"""
    email: EmailStr
    password: str


class Token(BaseModel):
    """JWT token response schema"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """JWT token payload data"""
    user_id: str
    email: str
    role: str


class UserResponse(BaseModel):
    """User response schema"""
    id: UUID
    email: str
    name: str
    role: str
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None

    @field_serializer('id')
    def serialize_uuid(self, value):
        """Convert UUID to string"""
        return str(value)

    @field_serializer('role')
    def serialize_role(self, value):
        """Convert enum to string"""
        if hasattr(value, 'value'):
            return value.value
        return value

    class Config:
        from_attributes = True


class PasswordChange(BaseModel):
    """Password change request schema"""
    current_password: str
    new_password: str = Field(..., min_length=6, max_length=100)
