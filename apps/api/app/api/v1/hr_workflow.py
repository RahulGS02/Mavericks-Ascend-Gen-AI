"""
HR Workflow API endpoints for reviewing mavericks
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

from app.database import get_db
from app.models.user import User
from app.models.maverick import Maverick, ProfileStatus
from app.schemas.hr_workflow import (
    ReviewAction,
    BulkShortlistRequest,
    BulkRejectRequest,
    ReviewResponse,
    BulkReviewResponse,
    NotificationRequest,
    NotificationResponse
)
from app.schemas.maverick import MaverickResponse, MaverickListResponse
from app.services.auth import get_current_user, get_hr_user
from app.services.email_service import email_service


router = APIRouter()


@router.get("/pending-profiles", response_model=MaverickListResponse)
async def get_pending_profiles(
    page: int = 1,
    page_size: int = 20,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_hr_user)
):
    """
    Get all pending maverick profiles for review
    
    **Required role**: HR or Super Admin
    **Query params**:
    - page: Page number (default: 1)
    - page_size: Items per page (default: 20)
    - search: Search by name, email, or college
    """
    query = db.query(Maverick).filter(Maverick.profile_status == ProfileStatus.PENDING)
    
    # Apply search filter
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (Maverick.name.ilike(search_filter)) |
            (Maverick.email.ilike(search_filter)) |
            (Maverick.college.ilike(search_filter))
        )
    
    # Get total count
    total = query.count()
    
    # Calculate pagination
    total_pages = (total + page_size - 1) // page_size
    offset = (page - 1) * page_size
    
    # Get paginated results
    mavericks = query.order_by(Maverick.created_at.desc()).offset(offset).limit(page_size).all()
    
    return MaverickListResponse(
        mavericks=mavericks,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


class ShortlistRequest(BaseModel):
    """Schema for shortlist request"""
    review_notes: Optional[str] = Field(None, description="Review notes")
    batch_id: Optional[str] = Field(None, description="Batch ID to assign (optional)")


@router.post("/shortlist/{maverick_id}", response_model=ReviewResponse)
async def shortlist_maverick(
    maverick_id: str,
    request: Optional[ShortlistRequest] = None,
    notes: Optional[str] = None,  # Kept for backwards compatibility
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_hr_user)
):
    """
    Shortlist (approve) a maverick profile and optionally assign to batch

    **Required role**: HR or Super Admin
    **Path params**:
    - maverick_id: UUID of the maverick
    **Body** (optional):
    - review_notes: Review notes
    - batch_id: Batch ID to assign (optional)
    """
    maverick = db.query(Maverick).filter(Maverick.id == maverick_id).first()

    if not maverick:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Maverick not found"
        )

    # Get review notes from request body or query param
    review_notes = None
    batch_id = None
    if request:
        review_notes = request.review_notes
        batch_id = request.batch_id
    elif notes:
        review_notes = notes

    # Update status
    maverick.profile_status = ProfileStatus.APPROVED
    maverick.reviewed_by = current_user.id
    if review_notes:
        maverick.review_notes = review_notes

    # Assign to batch if provided
    if batch_id:
        from app.models.batch import Batch
        batch = db.query(Batch).filter(Batch.id == batch_id).first()
        if batch:
            # Check if not already assigned
            if not maverick.current_batch_id:
                # Check capacity
                if not batch.max_capacity or batch.current_enrollment < batch.max_capacity:
                    maverick.current_batch_id = batch_id
                    batch.current_enrollment += 1
                else:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Batch is at full capacity ({batch.max_capacity})"
                    )
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Batch not found"
            )

    db.commit()
    db.refresh(maverick)

    # Send notification email in background
    if background_tasks:
        background_tasks.add_task(
            email_service.send_approval_email,
            maverick.email,
            maverick.name
        )

    return ReviewResponse(
        success=True,
        maverick_id=maverick.id,
        new_status="approved",
        message=f"Maverick {maverick.name} has been shortlisted successfully"
    )


@router.post("/reject/{maverick_id}", response_model=ReviewResponse)
async def reject_maverick(
    maverick_id: str,
    reason: str,
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_hr_user)
):
    """
    Reject a maverick profile
    
    **Required role**: HR or Super Admin
    **Path params**:
    - maverick_id: UUID of the maverick
    **Body**:
    - reason: Rejection reason (required)
    """
    maverick = db.query(Maverick).filter(Maverick.id == maverick_id).first()
    
    if not maverick:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Maverick not found"
        )
    
    # Update status
    maverick.profile_status = ProfileStatus.REJECTED
    maverick.reviewed_by = current_user.id
    maverick.review_notes = reason
    
    db.commit()
    db.refresh(maverick)
    
    # Send notification email in background
    if background_tasks:
        background_tasks.add_task(
            email_service.send_rejection_email,
            maverick.email,
            maverick.name,
            reason
        )
    
    return ReviewResponse(
        success=True,
        maverick_id=maverick.id,
        new_status="rejected",
        message=f"Maverick {maverick.name} has been rejected"
    )


@router.post("/bulk-shortlist", response_model=BulkReviewResponse)
async def bulk_shortlist_mavericks(
    request: BulkShortlistRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_hr_user)
):
    """
    Shortlist multiple mavericks at once

    **Required role**: HR or Super Admin
    **Body**:
    - maverick_ids: List of maverick UUIDs
    - notes: Optional common notes for all
    """
    results = []
    success_count = 0
    failed_count = 0

    for maverick_id in request.maverick_ids:
        try:
            maverick = db.query(Maverick).filter(Maverick.id == maverick_id).first()

            if not maverick:
                results.append(ReviewResponse(
                    success=False,
                    maverick_id=maverick_id,
                    new_status="",
                    message="Maverick not found"
                ))
                failed_count += 1
                continue

            # Update status
            maverick.profile_status = ProfileStatus.APPROVED
            maverick.reviewed_by = current_user.id
            if request.notes:
                maverick.review_notes = request.notes

            # Send email in background
            background_tasks.add_task(
                email_service.send_approval_email,
                maverick.email,
                maverick.name
            )

            results.append(ReviewResponse(
                success=True,
                maverick_id=maverick.id,
                new_status="approved",
                message=f"{maverick.name} shortlisted"
            ))
            success_count += 1

        except Exception as e:
            results.append(ReviewResponse(
                success=False,
                maverick_id=maverick_id,
                new_status="",
                message=str(e)
            ))
            failed_count += 1

    db.commit()

    return BulkReviewResponse(
        success_count=success_count,
        failed_count=failed_count,
        results=results
    )


@router.post("/bulk-reject", response_model=BulkReviewResponse)
async def bulk_reject_mavericks(
    request: BulkRejectRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_hr_user)
):
    """
    Reject multiple mavericks at once

    **Required role**: HR or Super Admin
    **Body**:
    - maverick_ids: List of maverick UUIDs
    - reason: Common rejection reason (required)
    """
    results = []
    success_count = 0
    failed_count = 0

    for maverick_id in request.maverick_ids:
        try:
            maverick = db.query(Maverick).filter(Maverick.id == maverick_id).first()

            if not maverick:
                results.append(ReviewResponse(
                    success=False,
                    maverick_id=maverick_id,
                    new_status="",
                    message="Maverick not found"
                ))
                failed_count += 1
                continue

            # Update status
            maverick.profile_status = ProfileStatus.REJECTED
            maverick.reviewed_by = current_user.id
            maverick.review_notes = request.reason

            # Send email in background
            background_tasks.add_task(
                email_service.send_rejection_email,
                maverick.email,
                maverick.name,
                request.reason
            )

            results.append(ReviewResponse(
                success=True,
                maverick_id=maverick.id,
                new_status="rejected",
                message=f"{maverick.name} rejected"
            ))
            success_count += 1

        except Exception as e:
            results.append(ReviewResponse(
                success=False,
                maverick_id=maverick_id,
                new_status="",
                message=str(e)
            ))
            failed_count += 1

    db.commit()

    return BulkReviewResponse(
        success_count=success_count,
        failed_count=failed_count,
        results=results
    )


@router.post("/send-notifications", response_model=NotificationResponse)
async def send_notification_emails(
    request: NotificationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_hr_user)
):
    """
    Send notification emails to mavericks

    **Required role**: HR or Super Admin
    **Body**:
    - maverick_ids: Optional list of specific maverick IDs
    - status_filter: Optional filter by status ('approved' or 'rejected')

    If no filters provided, sends to all approved and rejected mavericks
    """
    query = db.query(Maverick)

    # Apply filters
    if request.maverick_ids:
        query = query.filter(Maverick.id.in_(request.maverick_ids))

    if request.status_filter:
        if request.status_filter == "approved":
            query = query.filter(Maverick.profile_status == ProfileStatus.APPROVED)
        elif request.status_filter == "rejected":
            query = query.filter(Maverick.profile_status == ProfileStatus.REJECTED)
    else:
        # Default: send to both approved and rejected
        query = query.filter(
            Maverick.profile_status.in_([ProfileStatus.APPROVED, ProfileStatus.REJECTED])
        )

    mavericks = query.all()

    sent_count = 0
    failed_count = 0

    for maverick in mavericks:
        try:
            if maverick.profile_status == ProfileStatus.APPROVED:
                background_tasks.add_task(
                    email_service.send_approval_email,
                    maverick.email,
                    maverick.name
                )
            elif maverick.profile_status == ProfileStatus.REJECTED:
                background_tasks.add_task(
                    email_service.send_rejection_email,
                    maverick.email,
                    maverick.name,
                    maverick.review_notes
                )
            sent_count += 1
        except Exception:
            failed_count += 1

    return NotificationResponse(
        sent_count=sent_count,
        failed_count=failed_count,
        message=f"Notification emails queued for {sent_count} mavericks"
    )
