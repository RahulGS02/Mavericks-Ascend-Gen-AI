"""
Super Admin Audit Logs API
Allows Super Admin to view system audit trail
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, and_
from typing import Optional
from uuid import UUID
from datetime import datetime, timedelta
import math

from app.database import get_db
from app.models.user import User
from app.models.audit import AuditLog
from app.schemas.admin import AuditLogResponse, AuditLogListResponse
from app.utils.dependencies import get_super_admin


router = APIRouter(prefix="/admin/audit-logs", tags=["Super Admin - Audit Logs"])


@router.get("/", response_model=AuditLogListResponse)
async def get_audit_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    user_id: Optional[UUID] = None,
    action: Optional[str] = None,
    entity_type: Optional[str] = None,
    days: int = Query(30, ge=1, le=365, description="Number of days to look back"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_super_admin)
):
    """
    Get audit logs with filters
    
    **Required role**: Super Admin ONLY
    
    **Query params**:
    - page: Page number (default: 1)
    - page_size: Items per page (default: 50, max: 200)
    - user_id: Filter by user who performed action
    - action: Filter by action type (created, updated, deleted, login, etc.)
    - entity_type: Filter by entity type (users, mavericks, batches, etc.)
    - days: Number of days to look back (default: 30, max: 365)
    """
    # Build query
    query = db.query(AuditLog)
    
    # Filter by date range
    start_date = datetime.utcnow() - timedelta(days=days)
    query = query.filter(AuditLog.timestamp >= start_date)
    
    # Apply filters
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    
    if action:
        query = query.filter(AuditLog.action == action)
    
    if entity_type:
        query = query.filter(AuditLog.entity_type == entity_type)
    
    # Get total count
    total = query.count()
    
    # Calculate pagination
    total_pages = math.ceil(total / page_size)
    offset = (page - 1) * page_size
    
    # Get paginated results with user information
    logs = query.order_by(AuditLog.timestamp.desc()).offset(offset).limit(page_size).all()
    
    # Enrich with user names
    log_responses = []
    for log in logs:
        log_dict = {
            "id": log.id,
            "user_id": log.user_id,
            "user_name": None,
            "action": log.action,
            "entity_type": log.entity_type,
            "entity_id": log.entity_id,
            "old_value": log.old_value,
            "new_value": log.new_value,
            "ip_address": log.ip_address,
            "timestamp": log.timestamp
        }
        
        # Get user name if available
        if log.user_id:
            user = db.query(User).filter(User.id == log.user_id).first()
            if user:
                log_dict["user_name"] = user.name
        
        log_responses.append(AuditLogResponse(**log_dict))
    
    return AuditLogListResponse(
        logs=log_responses,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/actions", response_model=list[str])
async def get_audit_actions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_super_admin)
):
    """
    Get list of all unique action types in audit logs
    
    **Required role**: Super Admin ONLY
    
    Useful for populating filter dropdowns
    """
    actions = db.query(AuditLog.action).distinct().all()
    return [action[0] for action in actions if action[0]]


@router.get("/entity-types", response_model=list[str])
async def get_audit_entity_types(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_super_admin)
):
    """
    Get list of all unique entity types in audit logs
    
    **Required role**: Super Admin ONLY
    
    Useful for populating filter dropdowns
    """
    entity_types = db.query(AuditLog.entity_type).distinct().all()
    return [et[0] for et in entity_types if et[0]]


@router.get("/user/{user_id}", response_model=AuditLogListResponse)
async def get_user_audit_history(
    user_id: UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    days: int = Query(90, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_super_admin)
):
    """
    Get complete audit history for a specific user
    
    **Required role**: Super Admin ONLY
    
    Shows all actions performed by this user
    """
    # Check if user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Reuse main endpoint logic
    return await get_audit_logs(
        page=page,
        page_size=page_size,
        user_id=user_id,
        action=None,
        entity_type=None,
        days=days,
        db=db,
        current_user=current_user
    )
