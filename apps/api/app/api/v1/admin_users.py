"""
Super Admin User Management API
Allows Super Admin to manage users across all roles
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from typing import Optional
from uuid import UUID
import math

from app.database import get_db
from app.models.user import User, UserRole
from app.models.audit import AuditLog
from app.schemas.admin import (
    UserCreateAdmin,
    UserUpdateAdmin,
    UserResponseAdmin,
    UserListAdminResponse
)
from app.utils.dependencies import get_super_admin
from app.services.auth import get_password_hash, get_user_by_email


router = APIRouter(prefix="/admin/users", tags=["Super Admin - User Management"])


@router.post("/", response_model=UserResponseAdmin, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreateAdmin,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_super_admin)
):
    """
    Create a new user (any role)
    
    **Required role**: Super Admin ONLY
    
    Super Admin can create users with any role including:
    - maverick
    - trainer
    - hr
    - manager
    - super_admin
    """
    # Check if user already exists
    existing_user = get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Validate role
    try:
        user_role = UserRole(user_data.role)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Must be one of: {', '.join([r.value for r in UserRole])}"
        )
    
    # Create new user
    new_user = User(
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        name=user_data.name,
        role=user_role,
        is_active=user_data.is_active
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create audit log
    audit_log = AuditLog(
        user_id=current_user.id,
        action="created",
        entity_type="users",
        entity_id=new_user.id,
        new_value={
            "email": new_user.email,
            "name": new_user.name,
            "role": user_role.value,
            "is_active": new_user.is_active
        }
    )
    db.add(audit_log)
    db.commit()
    
    return new_user


@router.get("/", response_model=UserListAdminResponse)
async def list_all_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    role: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_super_admin)
):
    """
    Get list of all users (all roles)
    
    **Required role**: Super Admin ONLY
    
    **Query params**:
    - page: Page number (default: 1)
    - page_size: Items per page (default: 20, max: 100)
    - search: Search by name or email
    - role: Filter by role
    - is_active: Filter by active status
    """
    # Build query
    query = db.query(User)
    
    # Apply filters
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                User.name.ilike(search_term),
                User.email.ilike(search_term)
            )
        )
    
    if role:
        try:
            role_enum = UserRole(role)
            query = query.filter(User.role == role_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid role. Must be one of: {', '.join([r.value for r in UserRole])}"
            )
    
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    
    # Get total count
    total = query.count()
    
    # Calculate pagination
    total_pages = math.ceil(total / page_size)
    offset = (page - 1) * page_size
    
    # Get paginated results
    users = query.order_by(User.created_at.desc()).offset(offset).limit(page_size).all()
    
    return UserListAdminResponse(
        users=users,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/{user_id}", response_model=UserResponseAdmin)
async def get_user_details(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_super_admin)
):
    """
    Get detailed information about a specific user

    **Required role**: Super Admin ONLY
    """
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user


@router.patch("/{user_id}", response_model=UserResponseAdmin)
async def update_user(
    user_id: UUID,
    user_data: UserUpdateAdmin,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_super_admin)
):
    """
    Update user information (any field)

    **Required role**: Super Admin ONLY

    Can update:
    - Email
    - Name
    - Role (including promote/demote)
    - Active status
    - Password (reset)
    """
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Store old values for audit
    old_values = {
        "email": user.email,
        "name": user.name,
        "role": user.role.value,
        "is_active": user.is_active
    }

    # Update fields
    update_dict = user_data.model_dump(exclude_unset=True)

    if "email" in update_dict:
        # Check if new email is already taken
        existing = get_user_by_email(db, update_dict["email"])
        if existing and existing.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use"
            )
        user.email = update_dict["email"]

    if "name" in update_dict:
        user.name = update_dict["name"]

    if "role" in update_dict:
        try:
            user.role = UserRole(update_dict["role"])
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid role. Must be one of: {', '.join([r.value for r in UserRole])}"
            )

    if "is_active" in update_dict:
        user.is_active = update_dict["is_active"]

    if "password" in update_dict:
        user.password_hash = get_password_hash(update_dict["password"])

    db.commit()
    db.refresh(user)

    # Create audit log
    new_values = {
        "email": user.email,
        "name": user.name,
        "role": user.role.value,
        "is_active": user.is_active
    }

    audit_log = AuditLog(
        user_id=current_user.id,
        action="updated",
        entity_type="users",
        entity_id=user.id,
        old_value=old_values,
        new_value=new_values
    )
    db.add(audit_log)
    db.commit()

    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_super_admin)
):
    """
    Delete a user (soft delete - sets is_active to False)

    **Required role**: Super Admin ONLY

    Note: This is a soft delete. The user is deactivated but not removed from database.
    """
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Prevent self-deletion
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )

    # Soft delete
    user.is_active = False
    db.commit()

    # Create audit log
    audit_log = AuditLog(
        user_id=current_user.id,
        action="deleted",
        entity_type="users",
        entity_id=user.id,
        old_value={
            "email": user.email,
            "name": user.name,
            "role": user.role.value,
            "is_active": True
        },
        new_value={
            "is_active": False
        }
    )
    db.add(audit_log)
    db.commit()

    return None
