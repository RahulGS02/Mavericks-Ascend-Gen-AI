"""
Training Management API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from typing import Optional
from uuid import UUID
from datetime import datetime, date
from calendar import monthrange

from app.database import get_db
from app.models.user import User, UserRole
from app.models.batch import Batch
from app.models.pipeline import PipelineJob
from app.models.training import TrainingSession, SessionStatus
from app.schemas.training import (
    TrainingSessionCreate,
    TrainingSessionUpdate,
    TrainingSessionResponse,
    TrainingSessionListResponse,
    MarkCompleteRequest,
    MarkCompleteResponse,
    TrainingCalendarResponse,
    TrainingCalendarDay
)
from app.services.auth import get_current_user, get_hr_user


router = APIRouter()


@router.post("/", response_model=TrainingSessionResponse, status_code=status.HTTP_201_CREATED)
async def schedule_training_session(
    session_data: TrainingSessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_hr_user)
):
    """
    Schedule a new training session
    
    **Required role**: HR or Super Admin
    **Body**:
    - title: Session title (required)
    - description: Session description (optional)
    - batch_id: Batch UUID (required)
    - job_id: Pipeline job UUID (required)
    - trainer_id: Trainer UUID (optional)
    - scheduled_date: Date and time (required)
    - duration_minutes: Duration in minutes (required)
    - location: Location (optional)
    - meeting_link: Online meeting link (optional)
    """
    # Verify batch exists
    batch = db.query(Batch).filter(Batch.id == session_data.batch_id).first()
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Batch not found"
        )
    
    # Verify job exists and belongs to batch's pipeline
    job = db.query(PipelineJob).filter(PipelineJob.id == session_data.job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pipeline job not found"
        )
    
    if job.pipeline_id != batch.pipeline_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job does not belong to batch's pipeline"
        )
    
    # Verify trainer exists if provided
    if session_data.trainer_id:
        trainer = db.query(User).filter(
            User.id == session_data.trainer_id,
            User.role.in_([UserRole.TRAINER, UserRole.SUPER_ADMIN])
        ).first()
        if not trainer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Trainer not found or user is not a trainer"
            )
    
    # Create training session
    training_session = TrainingSession(
        batch_id=session_data.batch_id,
        job_id=session_data.job_id,
        title=session_data.title,
        description=session_data.description,
        trainer_id=session_data.trainer_id,
        scheduled_date=session_data.scheduled_date,
        duration_minutes=session_data.duration_minutes,
        location=session_data.location,
        meeting_link=session_data.meeting_link,
        status=SessionStatus.SCHEDULED
    )
    
    db.add(training_session)
    db.commit()
    db.refresh(training_session)
    
    return TrainingSessionResponse(
        id=training_session.id,
        batch_id=training_session.batch_id,
        batch_name=batch.name,
        job_id=training_session.job_id,
        title=training_session.title,
        description=training_session.description,
        trainer_id=training_session.trainer_id,
        scheduled_date=training_session.scheduled_date,
        duration_minutes=training_session.duration_minutes,
        location=training_session.location,
        meeting_link=training_session.meeting_link,
        status=training_session.status.value if hasattr(training_session.status, 'value') else training_session.status,
        completed_at=training_session.completed_at,
        completion_notes=training_session.completion_notes,
        attendance_count=training_session.attendance_count,
        created_at=training_session.created_at,
        updated_at=training_session.updated_at
    )


@router.get("/batch/{batch_id}", response_model=TrainingSessionListResponse)
async def list_training_sessions_by_batch(
    batch_id: UUID,
    page: int = 1,
    page_size: int = 20,
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all training sessions for a batch
    
    **Required role**: Any authenticated user
    **Path params**:
    - batch_id: UUID of the batch
    **Query params**:
    - page: Page number (default: 1)
    - page_size: Items per page (default: 20)
    - status_filter: Filter by status (SCHEDULED, COMPLETED, CANCELLED)
    """
    query = db.query(TrainingSession).filter(TrainingSession.batch_id == batch_id)
    
    # Apply status filter
    if status_filter:
        try:
            query = query.filter(TrainingSession.status == SessionStatus(status_filter))
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {status_filter}"
            )
    
    # Get total count
    total = query.count()
    
    # Calculate pagination
    total_pages = (total + page_size - 1) // page_size
    offset = (page - 1) * page_size
    
    # Get paginated results
    sessions = query.order_by(TrainingSession.scheduled_date).offset(offset).limit(page_size).all()
    
    # Build response with batch names
    session_responses = []
    for session in sessions:
        batch = db.query(Batch).filter(Batch.id == session.batch_id).first()
        session_responses.append(TrainingSessionResponse(
            id=session.id,
            batch_id=session.batch_id,
            batch_name=batch.name if batch else "Unknown",
            job_id=session.job_id,
            title=session.title,
            description=session.description,
            trainer_id=session.trainer_id,
            scheduled_date=session.scheduled_date,
            duration_minutes=session.duration_minutes,
            location=session.location,
            meeting_link=session.meeting_link,
            status=session.status.value if hasattr(session.status, 'value') else session.status,
            completed_at=session.completed_at,
            completion_notes=session.completion_notes,
            attendance_count=session.attendance_count,
            created_at=session.created_at,
            updated_at=session.updated_at
        ))
    
    return TrainingSessionListResponse(
        sessions=session_responses,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.post("/{session_id}/complete", response_model=MarkCompleteResponse)
async def mark_training_complete(
    session_id: UUID,
    request: MarkCompleteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Mark a training session as complete (Trainer only)

    **Required role**: Trainer or Super Admin
    **Path params**:
    - session_id: UUID of the training session
    **Body**:
    - completion_notes: Notes about the session (optional)
    - attendance_count: Number of attendees (optional)
    - actual_duration_minutes: Actual duration (optional)
    """
    # Verify user is trainer or admin
    if current_user.role not in [UserRole.TRAINER, UserRole.SUPER_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only trainers can mark sessions as complete"
        )

    # Get session
    session = db.query(TrainingSession).filter(TrainingSession.id == session_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Training session not found"
        )

    # Check if trainer is assigned to this session (unless admin)
    if current_user.role == UserRole.TRAINER:
        if session.trainer_id and session.trainer_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not assigned to this training session"
            )

    # Check if already completed
    if session.status == SessionStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session is already marked as complete"
        )

    # Mark as complete
    session.status = SessionStatus.COMPLETED
    session.completed_at = datetime.utcnow()

    if request.completion_notes:
        session.completion_notes = request.completion_notes
    if request.attendance_count is not None:
        session.attendance_count = request.attendance_count
    if request.actual_duration_minutes is not None:
        session.duration_minutes = request.actual_duration_minutes

    db.commit()
    db.refresh(session)

    return MarkCompleteResponse(
        success=True,
        session_id=session.id,
        message=f"Training session '{session.title}' marked as complete",
        completed_at=session.completed_at
    )


@router.get("/calendar", response_model=TrainingCalendarResponse)
async def get_training_calendar(
    year: int,
    month: int,
    batch_id: Optional[UUID] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get training calendar for a specific month

    **Required role**: Any authenticated user
    **Query params**:
    - year: Calendar year (required)
    - month: Calendar month 1-12 (required)
    - batch_id: Filter by batch (optional)

    Returns all training sessions organized by day.
    """
    # Validate month
    if month < 1 or month > 12:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Month must be between 1 and 12"
        )

    # Get first and last day of month
    _, last_day = monthrange(year, month)
    start_date = datetime(year, month, 1)
    end_date = datetime(year, month, last_day, 23, 59, 59)

    # Build query
    query = db.query(TrainingSession).filter(
        TrainingSession.scheduled_date >= start_date,
        TrainingSession.scheduled_date <= end_date
    )

    if batch_id:
        query = query.filter(TrainingSession.batch_id == batch_id)

    sessions = query.order_by(TrainingSession.scheduled_date).all()

    # Group sessions by day
    days_dict = {}
    for session in sessions:
        session_date = session.scheduled_date.date()

        if session_date not in days_dict:
            days_dict[session_date] = []

        batch = db.query(Batch).filter(Batch.id == session.batch_id).first()

        days_dict[session_date].append({
            "id": str(session.id),
            "title": session.title,
            "time": session.scheduled_date.strftime("%H:%M"),
            "duration_minutes": session.duration_minutes,
            "batch_name": batch.name if batch else "Unknown",
            "status": session.status.value if hasattr(session.status, 'value') else session.status,
            "location": session.location
        })

    # Create list of all days with sessions
    calendar_days = []
    for day_date, day_sessions in sorted(days_dict.items()):
        calendar_days.append(TrainingCalendarDay(
            date=day_date,
            sessions=day_sessions
        ))

    # Get batch info if filtered
    batch_name = None
    if batch_id:
        batch = db.query(Batch).filter(Batch.id == batch_id).first()
        batch_name = batch.name if batch else None

    return TrainingCalendarResponse(
        month=month,
        year=year,
        batch_id=batch_id,
        batch_name=batch_name,
        days=calendar_days,
        total_sessions=len(sessions)
    )


@router.patch("/{session_id}", response_model=TrainingSessionResponse)
async def update_training_session(
    session_id: UUID,
    update_data: TrainingSessionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_hr_user)
):
    """
    Update a training session

    **Required role**: HR or Super Admin
    **Path params**:
    - session_id: UUID of the training session
    **Body**: Fields to update (all optional)
    """
    session = db.query(TrainingSession).filter(TrainingSession.id == session_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Training session not found"
        )

    # Update fields
    if update_data.title is not None:
        session.title = update_data.title
    if update_data.description is not None:
        session.description = update_data.description
    if update_data.trainer_id is not None:
        # Verify trainer exists
        trainer = db.query(User).filter(
            User.id == update_data.trainer_id,
            User.role.in_([UserRole.TRAINER, UserRole.SUPER_ADMIN])
        ).first()
        if not trainer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Trainer not found"
            )
        session.trainer_id = update_data.trainer_id
    if update_data.scheduled_date is not None:
        session.scheduled_date = update_data.scheduled_date
    if update_data.duration_minutes is not None:
        session.duration_minutes = update_data.duration_minutes
    if update_data.location is not None:
        session.location = update_data.location
    if update_data.meeting_link is not None:
        session.meeting_link = update_data.meeting_link
    if update_data.status is not None:
        try:
            session.status = SessionStatus(update_data.status)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {update_data.status}"
            )

    db.commit()
    db.refresh(session)

    batch = db.query(Batch).filter(Batch.id == session.batch_id).first()

    return TrainingSessionResponse(
        id=session.id,
        batch_id=session.batch_id,
        batch_name=batch.name if batch else "Unknown",
        job_id=session.job_id,
        title=session.title,
        description=session.description,
        trainer_id=session.trainer_id,
        scheduled_date=session.scheduled_date,
        duration_minutes=session.duration_minutes,
        location=session.location,
        meeting_link=session.meeting_link,
        status=session.status.value if hasattr(session.status, 'value') else session.status,
        completed_at=session.completed_at,
        completion_notes=session.completion_notes,
        attendance_count=session.attendance_count,
        created_at=session.created_at,
        updated_at=session.updated_at
    )
