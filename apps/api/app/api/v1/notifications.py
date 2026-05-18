"""
Notifications API Endpoints
Handles notification retrieval and management
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from uuid import UUID
from datetime import datetime

from app.database import get_db
from app.models.user import User
from app.models.requirement_workflow import RequirementNotification
from app.schemas.notifications import (
    NotificationResponse,
    NotificationListResponse,
    MarkAsReadRequest,
    NotificationStatsResponse
)
from app.services.auth import get_current_user


router = APIRouter()


@router.get("/", response_model=NotificationListResponse)
async def get_notifications(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    unread_only: bool = Query(False),
    notification_type: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get notifications for current user
    
    **Query params**:
    - page: Page number (default: 1)
    - page_size: Items per page (default: 20)
    - unread_only: Show only unread notifications (default: false)
    - notification_type: Filter by type
    
    Returns paginated list of notifications.
    """
    query = db.query(RequirementNotification).filter(
        RequirementNotification.user_id == current_user.id
    )
    
    # Apply filters
    if unread_only:
        query = query.filter(RequirementNotification.is_read == False)
    
    if notification_type:
        query = query.filter(RequirementNotification.notification_type == notification_type)
    
    # Get total count
    total = query.count()
    
    # Apply pagination and ordering
    notifications = query.order_by(
        RequirementNotification.created_at.desc()
    ).offset((page - 1) * page_size).limit(page_size).all()
    
    # Build response
    notification_list = []
    for notif in notifications:
        notification_list.append(NotificationResponse(
            id=notif.id,
            requirement_id=notif.requirement_id,
            notification_type=notif.notification_type,
            title=notif.title,
            message=notif.message,
            is_read=notif.is_read,
            read_at=notif.read_at,
            metadata=notif.metadata,
            created_at=notif.created_at
        ))
    
    return NotificationListResponse(
        notifications=notification_list,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
        unread_count=db.query(RequirementNotification).filter(
            RequirementNotification.user_id == current_user.id,
            RequirementNotification.is_read == False
        ).count()
    )


@router.post("/{notification_id}/read", response_model=NotificationResponse)
async def mark_notification_as_read(
    notification_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Mark a notification as read
    
    **Path params**:
    - notification_id: UUID of the notification
    """
    notification = db.query(RequirementNotification).filter(
        RequirementNotification.id == notification_id,
        RequirementNotification.user_id == current_user.id
    ).first()
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    notification.is_read = True
    notification.read_at = datetime.utcnow()
    
    db.commit()
    db.refresh(notification)
    
    return NotificationResponse(
        id=notification.id,
        requirement_id=notification.requirement_id,
        notification_type=notification.notification_type,
        title=notification.title,
        message=notification.message,
        is_read=notification.is_read,
        read_at=notification.read_at,
        metadata=notification.metadata,
        created_at=notification.created_at
    )


@router.post("/read-all")
async def mark_all_as_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Mark all notifications as read for current user
    """
    updated_count = db.query(RequirementNotification).filter(
        RequirementNotification.user_id == current_user.id,
        RequirementNotification.is_read == False
    ).update({
        "is_read": True,
        "read_at": datetime.utcnow()
    })
    
    db.commit()
    
    return {
        "message": f"Marked {updated_count} notifications as read",
        "count": updated_count
    }


@router.get("/stats", response_model=NotificationStatsResponse)
async def get_notification_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get notification statistics for current user
    
    Returns counts by type and unread count.
    """
    total = db.query(RequirementNotification).filter(
        RequirementNotification.user_id == current_user.id
    ).count()
    
    unread = db.query(RequirementNotification).filter(
        RequirementNotification.user_id == current_user.id,
        RequirementNotification.is_read == False
    ).count()
    
    return NotificationStatsResponse(
        total=total,
        unread=unread
    )


@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a notification
    
    **Path params**:
    - notification_id: UUID of the notification
    """
    notification = db.query(RequirementNotification).filter(
        RequirementNotification.id == notification_id,
        RequirementNotification.user_id == current_user.id
    ).first()
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    db.delete(notification)
    db.commit()
    
    return {"message": "Notification deleted successfully"}
