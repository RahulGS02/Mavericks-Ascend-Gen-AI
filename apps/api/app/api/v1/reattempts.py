"""
Reattempt Management API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import Optional
from uuid import UUID
from datetime import datetime, timedelta

from app.database import get_db
from app.models.user import User, UserRole
from app.models.maverick import Maverick
from app.models.assessment import Assessment, AssessmentAttempt
from app.models.progress import MaverickJobProgress, ProgressStatus
from app.schemas.reattempt import (
    ScheduleReattemptRequest,
    ScheduleReattemptResponse,
    FailedMavericksListResponse,
    FailedMaverickInfo,
    MaverickAttemptHistory,
    AttemptInfo,
    ReattemptStatistics
)
from app.services.auth import get_current_user, get_hr_user


router = APIRouter()


@router.post("/{assessment_id}/schedule", response_model=ScheduleReattemptResponse)
async def schedule_reattempt(
    assessment_id: UUID,
    request: ScheduleReattemptRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Schedule a reattempt for a failed maverick
    
    **Required role**: Any authenticated user (Trainer/HR for others, Maverick for self)
    **Path params**:
    - assessment_id: UUID of the assessment
    **Body**:
    - maverick_id: Student UUID
    - scheduled_date: Optional reattempt date
    - notes: Optional notes
    
    Checks if maverick failed and allows scheduling reattempt.
    """
    # Verify assessment exists
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found"
        )
    
    # Verify maverick exists
    maverick = db.query(Maverick).filter(Maverick.id == request.maverick_id).first()
    if not maverick:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Maverick not found"
        )
    
    # Check permission: HR/Trainer can schedule for anyone, maverick can schedule for self
    if current_user.role not in [UserRole.HR, UserRole.TRAINER, UserRole.SUPER_ADMIN]:
        # Check if current user is the maverick
        if str(current_user.id) != str(request.maverick_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only schedule reattempts for yourself"
            )
    
    # Get latest attempt
    latest_attempt = db.query(AssessmentAttempt).filter(
        AssessmentAttempt.assessment_id == assessment_id,
        AssessmentAttempt.maverick_id == request.maverick_id
    ).order_by(desc(AssessmentAttempt.evaluated_at)).first()
    
    if not latest_attempt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No previous attempt found. Take the assessment first."
        )
    
    if latest_attempt.passed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot schedule reattempt - already passed the assessment"
        )
    
    # Count total attempts
    total_attempts = db.query(AssessmentAttempt).filter(
        AssessmentAttempt.assessment_id == assessment_id,
        AssessmentAttempt.maverick_id == request.maverick_id
    ).count()
    
    # Update job progress to allow reattempt
    progress = db.query(MaverickJobProgress).filter(
        MaverickJobProgress.maverick_id == request.maverick_id,
        MaverickJobProgress.batch_id == assessment.batch_id,
        MaverickJobProgress.job_id == assessment.job_id
    ).first()
    
    if progress:
        progress.status = ProgressStatus.PENDING  # Reset to pending for reattempt
        progress.notes = f"Reattempt scheduled (Attempt #{total_attempts + 1}). {request.notes or ''}"
    
    db.commit()
    
    next_attempt_number = total_attempts + 1
    
    return ScheduleReattemptResponse(
        success=True,
        maverick_id=request.maverick_id,
        assessment_id=assessment_id,
        attempt_number=next_attempt_number,
        scheduled_date=request.scheduled_date,
        message=f"Reattempt #{next_attempt_number} scheduled successfully for {maverick.name}"
    )


@router.get("/{assessment_id}/failed-mavericks", response_model=FailedMavericksListResponse)
async def get_failed_mavericks(
    assessment_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get list of mavericks who failed the assessment
    
    **Required role**: Any authenticated user
    **Path params**:
    - assessment_id: UUID of the assessment
    
    Returns all mavericks who failed with their latest attempt details.
    """
    # Verify assessment exists
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found"
        )
    
    # Get all attempts for this assessment
    all_attempts = db.query(AssessmentAttempt).filter(
        AssessmentAttempt.assessment_id == assessment_id
    ).all()
    
    # Group by maverick and find who failed
    maverick_attempts = {}
    for attempt in all_attempts:
        maverick_id = str(attempt.maverick_id)
        if maverick_id not in maverick_attempts:
            maverick_attempts[maverick_id] = []
        maverick_attempts[maverick_id].append(attempt)
    
    failed_mavericks_list = []
    
    for maverick_id, attempts in maverick_attempts.items():
        # Sort attempts by date (latest first)
        attempts.sort(key=lambda x: x.evaluated_at, reverse=True)
        latest_attempt = attempts[0]
        
        # Check if latest attempt failed
        if not latest_attempt.passed:
            maverick = db.query(Maverick).filter(Maverick.id == maverick_id).first()
            if maverick:
                percentage = (float(latest_attempt.marks_obtained) / float(latest_attempt.max_marks)) * 100
                
                # Check if can reattempt (e.g., max 3 attempts)
                can_reattempt = len(attempts) < 3
                next_available = None
                if can_reattempt and len(attempts) > 0:
                    # Cooldown period of 1 day between attempts
                    next_available = latest_attempt.evaluated_at + timedelta(days=1)
                
                failed_mavericks_list.append(FailedMaverickInfo(
                    maverick_id=UUID(maverick_id),
                    maverick_name=maverick.name,
                    email=maverick.email,
                    last_attempt_id=latest_attempt.id,
                    marks_obtained=float(latest_attempt.marks_obtained),
                    max_marks=float(latest_attempt.max_marks),
                    percentage=round(percentage, 2),
                    total_attempts=len(attempts),
                    last_attempt_date=latest_attempt.evaluated_at,
                    feedback=latest_attempt.feedback,
                    can_reattempt=can_reattempt,
                    next_reattempt_available=next_available if datetime.utcnow() < next_available else None
                ))
    
    return FailedMavericksListResponse(
        assessment_id=assessment_id,
        assessment_title=assessment.title,
        batch_id=assessment.batch_id,
        total_failed=len(failed_mavericks_list),
        failed_mavericks=failed_mavericks_list
    )


@router.get("/maverick/{maverick_id}/assessment/{assessment_id}/history", response_model=MaverickAttemptHistory)
async def get_maverick_attempt_history(
    maverick_id: UUID,
    assessment_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get attempt history for a specific maverick and assessment

    **Required role**: Any authenticated user (can view own history)
    **Path params**:
    - maverick_id: UUID of the maverick
    - assessment_id: UUID of the assessment

    Returns all attempts with attempt numbers tracked.
    """
    # Check permission
    if current_user.role not in [UserRole.HR, UserRole.TRAINER, UserRole.SUPER_ADMIN]:
        if str(current_user.id) != str(maverick_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view your own attempt history"
            )

    # Verify maverick exists
    maverick = db.query(Maverick).filter(Maverick.id == maverick_id).first()
    if not maverick:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Maverick not found"
        )

    # Verify assessment exists
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found"
        )

    # Get all attempts
    attempts = db.query(AssessmentAttempt).filter(
        AssessmentAttempt.assessment_id == assessment_id,
        AssessmentAttempt.maverick_id == maverick_id
    ).order_by(AssessmentAttempt.evaluated_at).all()

    if not attempts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No attempts found"
        )

    # Build attempt info list
    attempt_infos = []
    for idx, attempt in enumerate(attempts, start=1):
        percentage = (float(attempt.marks_obtained) / float(attempt.max_marks)) * 100
        attempt_infos.append(AttemptInfo(
            attempt_id=attempt.id,
            attempt_number=idx,
            marks_obtained=float(attempt.marks_obtained),
            max_marks=float(attempt.max_marks),
            percentage=round(percentage, 2),
            passed=attempt.passed,
            evaluated_at=attempt.evaluated_at,
            feedback=attempt.feedback
        ))

    # Calculate statistics
    passed = any(a.passed for a in attempts)
    best_score = max(float(a.marks_obtained) for a in attempts)
    latest_score = float(attempts[-1].marks_obtained)

    return MaverickAttemptHistory(
        maverick_id=maverick_id,
        maverick_name=maverick.name,
        assessment_id=assessment_id,
        assessment_title=assessment.title,
        total_attempts=len(attempts),
        passed=passed,
        best_score=best_score,
        latest_score=latest_score,
        attempts=attempt_infos
    )


@router.get("/{assessment_id}/statistics", response_model=ReattemptStatistics)
async def get_reattempt_statistics(
    assessment_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get reattempt statistics for an assessment

    **Required role**: Any authenticated user
    **Path params**:
    - assessment_id: UUID of the assessment

    Returns statistics about attempts, pass rates, etc.
    """
    # Verify assessment exists
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found"
        )

    # Get all attempts
    all_attempts = db.query(AssessmentAttempt).filter(
        AssessmentAttempt.assessment_id == assessment_id
    ).all()

    if not all_attempts:
        return ReattemptStatistics(
            assessment_id=assessment_id,
            total_attempts=0,
            first_attempt_count=0,
            reattempt_count=0,
            first_attempt_pass_rate=0.0,
            reattempt_pass_rate=0.0,
            average_attempts_to_pass=0.0,
            max_attempts_by_maverick=0
        )

    # Group by maverick
    maverick_attempts = {}
    for attempt in all_attempts:
        maverick_id = str(attempt.maverick_id)
        if maverick_id not in maverick_attempts:
            maverick_attempts[maverick_id] = []
        maverick_attempts[maverick_id].append(attempt)

    # Calculate statistics
    total_attempts = len(all_attempts)
    first_attempt_count = len(maverick_attempts)
    reattempt_count = total_attempts - first_attempt_count

    first_attempt_passes = 0
    reattempt_passes = 0
    total_attempts_to_pass = 0
    passed_mavericks = 0
    max_attempts = 0

    for maverick_id, attempts in maverick_attempts.items():
        attempts.sort(key=lambda x: x.evaluated_at)
        max_attempts = max(max_attempts, len(attempts))

        # Check first attempt
        if attempts[0].passed:
            first_attempt_passes += 1
            total_attempts_to_pass += 1
            passed_mavericks += 1
        else:
            # Check if passed in reattempts
            for idx, attempt in enumerate(attempts[1:], start=2):
                if attempt.passed:
                    reattempt_passes += 1
                    total_attempts_to_pass += idx
                    passed_mavericks += 1
                    break

    first_attempt_pass_rate = (first_attempt_passes / first_attempt_count * 100) if first_attempt_count > 0 else 0
    reattempt_pass_rate = (reattempt_passes / reattempt_count * 100) if reattempt_count > 0 else 0
    average_attempts_to_pass = (total_attempts_to_pass / passed_mavericks) if passed_mavericks > 0 else 0

    return ReattemptStatistics(
        assessment_id=assessment_id,
        total_attempts=total_attempts,
        first_attempt_count=first_attempt_count,
        reattempt_count=reattempt_count,
        first_attempt_pass_rate=round(first_attempt_pass_rate, 2),
        reattempt_pass_rate=round(reattempt_pass_rate, 2),
        average_attempts_to_pass=round(average_attempts_to_pass, 2),
        max_attempts_by_maverick=max_attempts
    )
