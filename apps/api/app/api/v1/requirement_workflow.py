"""
Requirement Workflow API Endpoints
Handles candidate suggestions, shortlisting, interviews, and workflow management
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID
from datetime import datetime
import json

from app.database import get_db
from app.models.user import User, UserRole
from app.models.maverick import Maverick
from app.models.deployment import DeploymentRequest, DeploymentRequestStatus
from app.models.requirement_workflow import (
    RequirementCandidate, CandidateStatus,
    RequirementInterview, InterviewStatus, InterviewType, InterviewMode,
    RequirementWorkflowHistory, WorkflowStage
)
from app.schemas.requirement_workflow import (
    SuggestCandidateRequest, SuggestCandidatesRequest,
    ShortlistCandidateRequest, RejectCandidateRequest,
    CandidateResponse, CandidateListResponse,
    ScheduleInterviewRequest, UpdateInterviewStatusRequest,
    SubmitInterviewFeedbackRequest, InterviewResponse, InterviewListResponse,
    UpdateWorkflowStageRequest, WorkflowHistoryResponse, WorkflowHistoryListResponse
)
from app.services.auth import get_current_user, get_hr_user
from app.services.notification_service import NotificationService


router = APIRouter()


# ==================== Helper Functions ====================

def _get_requirement_or_404(db: Session, requirement_id: UUID) -> DeploymentRequest:
    """Get requirement or raise 404"""
    requirement = db.query(DeploymentRequest).filter(
        DeploymentRequest.id == requirement_id
    ).first()
    
    if not requirement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Requirement not found"
        )
    
    return requirement


def _get_candidate_or_404(db: Session, candidate_id: UUID) -> RequirementCandidate:
    """Get candidate or raise 404"""
    candidate = db.query(RequirementCandidate).filter(
        RequirementCandidate.id == candidate_id
    ).first()
    
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )
    
    return candidate


def _add_workflow_history(
    db: Session, 
    requirement_id: UUID, 
    from_stage: Optional[str], 
    to_stage: str, 
    changed_by: UUID, 
    reason: Optional[str] = None
):
    """Add entry to workflow history"""
    history = RequirementWorkflowHistory(
        requirement_id=requirement_id,
        from_stage=from_stage,
        to_stage=to_stage,
        changed_by=changed_by,
        change_reason=reason
    )
    db.add(history)


# ==================== HR: Suggest Candidates ====================

@router.post("/requirements/{requirement_id}/candidates", response_model=CandidateResponse, status_code=status.HTTP_201_CREATED)
async def suggest_candidate(
    requirement_id: UUID,
    candidate_data: SuggestCandidateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_hr_user)
):
    """
    HR: Suggest a candidate for a requirement
    
    **Required role**: HR or Super Admin
    **Path params**:
    - requirement_id: UUID of the requirement
    **Body**:
    - maverick_id: UUID of the maverick to suggest
    - match_score: Optional match score (0-100)
    - hr_notes: Optional notes about this candidate
    
    Suggests a candidate for the requirement.
    """
    # Verify requirement exists
    requirement = _get_requirement_or_404(db, requirement_id)
    
    # Verify maverick exists
    maverick = db.query(Maverick).filter(Maverick.id == candidate_data.maverick_id).first()
    if not maverick:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Maverick not found"
        )
    
    # Check if already suggested
    existing = db.query(RequirementCandidate).filter(
        RequirementCandidate.requirement_id == requirement_id,
        RequirementCandidate.maverick_id == candidate_data.maverick_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Candidate already suggested for this requirement"
        )
    
    # Create candidate suggestion
    candidate = RequirementCandidate(
        requirement_id=requirement_id,
        maverick_id=candidate_data.maverick_id,
        suggested_by=current_user.id,
        match_score=candidate_data.match_score,
        hr_notes=candidate_data.hr_notes,
        status=CandidateStatus.SUGGESTED
    )
    
    db.add(candidate)
    
    # Update requirement workflow stage if this is the first candidate
    if requirement.workflow_stage == WorkflowStage.PENDING.value or requirement.workflow_stage == WorkflowStage.UNDER_REVIEW.value:
        old_stage = requirement.workflow_stage
        requirement.workflow_stage = WorkflowStage.CANDIDATES_SUGGESTED.value
        _add_workflow_history(db, requirement_id, old_stage, WorkflowStage.CANDIDATES_SUGGESTED.value, current_user.id, "First candidate suggested")

    db.commit()
    db.refresh(candidate)

    # Send notification to manager
    NotificationService.notify_candidate_suggested(
        db=db,
        requirement=requirement,
        manager_id=requirement.requested_by,
        candidate_name=f"{maverick.first_name} {maverick.last_name}",
        suggested_by_name=f"{current_user.first_name} {current_user.last_name}",
        match_score=candidate_data.match_score
    )
    
    # Get maverick details for response
    response_data = CandidateResponse(
        id=candidate.id,
        requirement_id=candidate.requirement_id,
        maverick_id=candidate.maverick_id,
        maverick_name=f"{maverick.first_name} {maverick.last_name}",
        maverick_email=maverick.email,
        suggested_by=candidate.suggested_by,
        suggested_by_name=f"{current_user.first_name} {current_user.last_name}",
        suggestion_date=candidate.suggestion_date,
        match_score=candidate.match_score,
        status=candidate.status.value,
        shortlist_notes=candidate.shortlist_notes,
        rejection_reason=candidate.rejection_reason,
        manager_notes=candidate.manager_notes,
        hr_notes=candidate.hr_notes,
        created_at=candidate.created_at,
        updated_at=candidate.updated_at,
        maverick_skills=json.loads(maverick.skills) if maverick.skills else [],
        maverick_cgpa=maverick.cgpa,
        maverick_degree=maverick.degree,
        maverick_branch=maverick.branch,
        maverick_graduation_year=maverick.graduation_year
    )

    return response_data


@router.post("/requirements/{requirement_id}/candidates/bulk", response_model=CandidateListResponse, status_code=status.HTTP_201_CREATED)
async def suggest_candidates_bulk(
    requirement_id: UUID,
    bulk_data: SuggestCandidatesRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_hr_user)
):
    """
    HR: Suggest multiple candidates at once

    **Required role**: HR or Super Admin
    **Path params**:
    - requirement_id: UUID of the requirement
    **Body**:
    - candidates: List of candidates to suggest

    Suggests multiple candidates for the requirement in bulk.
    """
    # Verify requirement exists
    requirement = _get_requirement_or_404(db, requirement_id)

    created_candidates = []

    for candidate_data in bulk_data.candidates:
        # Verify maverick exists
        maverick = db.query(Maverick).filter(Maverick.id == candidate_data.maverick_id).first()
        if not maverick:
            continue  # Skip if maverick not found

        # Check if already suggested
        existing = db.query(RequirementCandidate).filter(
            RequirementCandidate.requirement_id == requirement_id,
            RequirementCandidate.maverick_id == candidate_data.maverick_id
        ).first()

        if existing:
            continue  # Skip if already suggested

        # Create candidate suggestion
        candidate = RequirementCandidate(
            requirement_id=requirement_id,
            maverick_id=candidate_data.maverick_id,
            suggested_by=current_user.id,
            match_score=candidate_data.match_score,
            hr_notes=candidate_data.hr_notes,
            status=CandidateStatus.SUGGESTED
        )

        db.add(candidate)
        created_candidates.append(candidate)

    # Update requirement workflow stage if this is the first batch of candidates
    if created_candidates and (requirement.workflow_stage == WorkflowStage.PENDING.value or requirement.workflow_stage == WorkflowStage.UNDER_REVIEW.value):
        old_stage = requirement.workflow_stage
        requirement.workflow_stage = WorkflowStage.CANDIDATES_SUGGESTED.value
        _add_workflow_history(db, requirement_id, old_stage, WorkflowStage.CANDIDATES_SUGGESTED.value, current_user.id, f"Suggested {len(created_candidates)} candidates")

    db.commit()

    # Build response
    response_list = []
    for candidate in created_candidates:
        db.refresh(candidate)
        maverick = db.query(Maverick).filter(Maverick.id == candidate.maverick_id).first()

        response_list.append(CandidateResponse(
            id=candidate.id,
            requirement_id=candidate.requirement_id,
            maverick_id=candidate.maverick_id,
            maverick_name=f"{maverick.first_name} {maverick.last_name}" if maverick else None,
            maverick_email=maverick.email if maverick else None,
            suggested_by=candidate.suggested_by,
            suggested_by_name=f"{current_user.first_name} {current_user.last_name}",
            suggestion_date=candidate.suggestion_date,
            match_score=candidate.match_score,
            status=candidate.status.value,
            shortlist_notes=candidate.shortlist_notes,
            rejection_reason=candidate.rejection_reason,
            manager_notes=candidate.manager_notes,
            hr_notes=candidate.hr_notes,
            created_at=candidate.created_at,
            updated_at=candidate.updated_at,
            maverick_skills=json.loads(maverick.skills) if maverick and maverick.skills else [],
            maverick_cgpa=maverick.cgpa if maverick else None,
            maverick_degree=maverick.degree if maverick else None,
            maverick_branch=maverick.branch if maverick else None,
            maverick_graduation_year=maverick.graduation_year if maverick else None
        ))

    return CandidateListResponse(
        candidates=response_list,
        total=len(response_list)
    )


# ==================== Manager: Shortlist Candidates ====================

@router.post("/requirements/{requirement_id}/candidates/{candidate_id}/shortlist", response_model=CandidateResponse)
async def shortlist_candidate(
    requirement_id: UUID,
    candidate_id: UUID,
    shortlist_data: ShortlistCandidateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Manager: Shortlist a suggested candidate

    **Required role**: Manager or HR
    **Path params**:
    - requirement_id: UUID of the requirement
    - candidate_id: UUID of the candidate
    **Body**:
    - manager_notes: Optional notes about why shortlisting

    Shortlists a suggested candidate for further evaluation.
    """
    # Verify requirement exists
    requirement = _get_requirement_or_404(db, requirement_id)

    # Check authorization: Only HR or the manager who created the requirement
    if current_user.role not in [UserRole.HR, UserRole.SUPER_ADMIN]:
        if requirement.requested_by != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the requirement creator or HR can shortlist candidates"
            )

    # Get candidate
    candidate = _get_candidate_or_404(db, candidate_id)

    # Verify candidate belongs to this requirement
    if candidate.requirement_id != requirement_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Candidate does not belong to this requirement"
        )

    # Check current status
    if candidate.status not in [CandidateStatus.SUGGESTED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Candidate is already {candidate.status.value}. Can only shortlist SUGGESTED candidates."
        )

    # Update candidate status
    candidate.status = CandidateStatus.SHORTLISTED
    candidate.manager_notes = shortlist_data.manager_notes
    candidate.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(candidate)

    # Send notification to HR
    hr_users = db.query(User).filter(User.role.in_(['HR', 'SUPER_ADMIN'])).all()
    NotificationService.notify_candidate_shortlisted(
        db=db,
        requirement=requirement,
        hr_users=hr_users,
        candidate_name=f"{maverick.first_name} {maverick.last_name}" if maverick else "Unknown",
        manager_name=f"{current_user.first_name} {current_user.last_name}"
    )

    # Get maverick and user details for response
    maverick = db.query(Maverick).filter(Maverick.id == candidate.maverick_id).first()
    suggested_by_user = db.query(User).filter(User.id == candidate.suggested_by).first() if candidate.suggested_by else None

    return CandidateResponse(
        id=candidate.id,
        requirement_id=candidate.requirement_id,
        maverick_id=candidate.maverick_id,
        maverick_name=f"{maverick.first_name} {maverick.last_name}" if maverick else None,
        maverick_email=maverick.email if maverick else None,
        suggested_by=candidate.suggested_by,
        suggested_by_name=f"{suggested_by_user.first_name} {suggested_by_user.last_name}" if suggested_by_user else None,
        suggestion_date=candidate.suggestion_date,
        match_score=candidate.match_score,
        status=candidate.status.value,
        shortlist_notes=candidate.shortlist_notes,
        rejection_reason=candidate.rejection_reason,
        manager_notes=candidate.manager_notes,
        hr_notes=candidate.hr_notes,
        created_at=candidate.created_at,
        updated_at=candidate.updated_at,
        maverick_skills=json.loads(maverick.skills) if maverick and maverick.skills else [],
        maverick_cgpa=maverick.cgpa if maverick else None,
        maverick_degree=maverick.degree if maverick else None,
        maverick_branch=maverick.branch if maverick else None,
        maverick_graduation_year=maverick.graduation_year if maverick else None
    )


# ==================== Reject Candidate ====================

@router.post("/requirements/{requirement_id}/candidates/{candidate_id}/reject", response_model=CandidateResponse)
async def reject_candidate(
    requirement_id: UUID,
    candidate_id: UUID,
    reject_data: RejectCandidateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Manager/HR: Reject a candidate

    **Required role**: Manager or HR
    **Path params**:
    - requirement_id: UUID of the requirement
    - candidate_id: UUID of the candidate
    **Body**:
    - rejection_reason: Reason for rejection

    Rejects a candidate for this requirement.
    """
    # Verify requirement exists
    requirement = _get_requirement_or_404(db, requirement_id)

    # Check authorization
    if current_user.role not in [UserRole.HR, UserRole.SUPER_ADMIN]:
        if requirement.requested_by != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the requirement creator or HR can reject candidates"
            )

    # Get candidate
    candidate = _get_candidate_or_404(db, candidate_id)

    # Verify candidate belongs to this requirement
    if candidate.requirement_id != requirement_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Candidate does not belong to this requirement"
        )

    # Update candidate status
    candidate.status = CandidateStatus.REJECTED
    candidate.rejection_reason = reject_data.rejection_reason
    candidate.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(candidate)

    # Get details for response
    maverick = db.query(Maverick).filter(Maverick.id == candidate.maverick_id).first()
    suggested_by_user = db.query(User).filter(User.id == candidate.suggested_by).first() if candidate.suggested_by else None

    return CandidateResponse(
        id=candidate.id,
        requirement_id=candidate.requirement_id,
        maverick_id=candidate.maverick_id,
        maverick_name=f"{maverick.first_name} {maverick.last_name}" if maverick else None,
        maverick_email=maverick.email if maverick else None,
        suggested_by=candidate.suggested_by,
        suggested_by_name=f"{suggested_by_user.first_name} {suggested_by_user.last_name}" if suggested_by_user else None,
        suggestion_date=candidate.suggestion_date,
        match_score=candidate.match_score,
        status=candidate.status.value,
        shortlist_notes=candidate.shortlist_notes,
        rejection_reason=candidate.rejection_reason,
        manager_notes=candidate.manager_notes,
        hr_notes=candidate.hr_notes,
        created_at=candidate.created_at,
        updated_at=candidate.updated_at,
        maverick_skills=json.loads(maverick.skills) if maverick and maverick.skills else [],
        maverick_cgpa=maverick.cgpa if maverick else None,
        maverick_degree=maverick.degree if maverick else None,
        maverick_branch=maverick.branch if maverick else None,
        maverick_graduation_year=maverick.graduation_year if maverick else None
    )


# ==================== List Candidates ====================

@router.get("/requirements/{requirement_id}/candidates", response_model=CandidateListResponse)
async def list_candidates(
    requirement_id: UUID,
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all candidates for a requirement

    **Required role**: Any authenticated user
    **Path params**:
    - requirement_id: UUID of the requirement
    **Query params**:
    - status_filter: Optional filter by status (SUGGESTED, SHORTLISTED, REJECTED, etc.)

    Returns all candidates suggested for this requirement.
    """
    # Verify requirement exists
    requirement = _get_requirement_or_404(db, requirement_id)

    # Check authorization for managers
    if current_user.role not in [UserRole.HR, UserRole.SUPER_ADMIN]:
        if requirement.requested_by != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the requirement creator or HR can view candidates"
            )

    # Build query
    query = db.query(RequirementCandidate).filter(
        RequirementCandidate.requirement_id == requirement_id
    )

    # Apply status filter
    if status_filter:
        query = query.filter(RequirementCandidate.status == status_filter)

    # Order by suggestion date
    query = query.order_by(RequirementCandidate.suggestion_date.desc())

    candidates = query.all()

    # Build response
    response_list = []
    for candidate in candidates:
        maverick = db.query(Maverick).filter(Maverick.id == candidate.maverick_id).first()
        suggested_by_user = db.query(User).filter(User.id == candidate.suggested_by).first() if candidate.suggested_by else None

        response_list.append(CandidateResponse(
            id=candidate.id,
            requirement_id=candidate.requirement_id,
            maverick_id=candidate.maverick_id,
            maverick_name=f"{maverick.first_name} {maverick.last_name}" if maverick else None,
            maverick_email=maverick.email if maverick else None,
            suggested_by=candidate.suggested_by,
            suggested_by_name=f"{suggested_by_user.first_name} {suggested_by_user.last_name}" if suggested_by_user else None,
            suggestion_date=candidate.suggestion_date,
            match_score=candidate.match_score,
            status=candidate.status.value,
            shortlist_notes=candidate.shortlist_notes,
            rejection_reason=candidate.rejection_reason,
            manager_notes=candidate.manager_notes,
            hr_notes=candidate.hr_notes,
            created_at=candidate.created_at,
            updated_at=candidate.updated_at,
            maverick_skills=json.loads(maverick.skills) if maverick and maverick.skills else [],
            maverick_cgpa=maverick.cgpa if maverick else None,
            maverick_degree=maverick.degree if maverick else None,
            maverick_branch=maverick.branch if maverick else None,
            maverick_graduation_year=maverick.graduation_year if maverick else None
        ))

    return CandidateListResponse(
        candidates=response_list,
        total=len(response_list)
    )


# ==================== Interview Management ====================

@router.post("/requirements/{requirement_id}/candidates/{candidate_id}/interviews", response_model=InterviewResponse, status_code=status.HTTP_201_CREATED)
async def schedule_interview(
    requirement_id: UUID,
    candidate_id: UUID,
    interview_data: ScheduleInterviewRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Schedule an interview for a candidate

    **Required role**: Manager or HR
    **Path params**:
    - requirement_id: UUID of the requirement
    - candidate_id: UUID of the candidate
    **Body**: Interview details

    Schedules an interview for a shortlisted candidate.
    """
    # Verify requirement and authorization
    requirement = _get_requirement_or_404(db, requirement_id)

    if current_user.role not in [UserRole.HR, UserRole.SUPER_ADMIN]:
        if requirement.requested_by != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the requirement creator or HR can schedule interviews"
            )

    # Get candidate
    candidate = _get_candidate_or_404(db, candidate_id)

    if candidate.requirement_id != requirement_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Candidate does not belong to this requirement"
        )

    # Create interview
    interview = RequirementInterview(
        requirement_id=requirement_id,
        candidate_id=candidate_id,
        maverick_id=candidate.maverick_id,
        interview_type=InterviewType(interview_data.interview_type),
        interview_mode=InterviewMode(interview_data.interview_mode),
        interview_date=interview_data.interview_date,
        interview_time=interview_data.interview_time,
        duration_minutes=interview_data.duration_minutes,
        location=interview_data.location,
        video_link=interview_data.video_link,
        interviewer_panel=interview_data.interviewer_panel,
        scheduled_by=current_user.id,
        status=InterviewStatus.SCHEDULED
    )

    db.add(interview)

    # Update candidate status
    candidate.status = CandidateStatus.INTERVIEW_SCHEDULED
    candidate.updated_at = datetime.utcnow()

    # Update requirement workflow stage
    if requirement.workflow_stage not in [WorkflowStage.INTERVIEWS_IN_PROGRESS.value]:
        old_stage = requirement.workflow_stage
        requirement.workflow_stage = WorkflowStage.INTERVIEW_SCHEDULING.value
        _add_workflow_history(db, requirement_id, old_stage, WorkflowStage.INTERVIEW_SCHEDULING.value, current_user.id, "Interview scheduled")

    db.commit()
    db.refresh(interview)

    # Send notifications
    maverick = db.query(Maverick).filter(Maverick.id == interview.maverick_id).first()
    recipient_ids = [requirement.requested_by]  # Manager
    hr_users = db.query(User).filter(User.role.in_(['HR', 'SUPER_ADMIN'])).all()
    recipient_ids.extend([hr.id for hr in hr_users])

    NotificationService.notify_interview_scheduled(
        db=db,
        requirement=requirement,
        candidate_name=f"{maverick.first_name} {maverick.last_name}" if maverick else "Unknown",
        interview_date=str(interview_data.interview_date),
        interview_time=str(interview_data.interview_time),
        recipient_ids=list(set(recipient_ids))  # Remove duplicates
    )

    # Get maverick details
    maverick = db.query(Maverick).filter(Maverick.id == interview.maverick_id).first()

    return InterviewResponse(
        id=interview.id,
        requirement_id=interview.requirement_id,
        candidate_id=interview.candidate_id,
        maverick_id=interview.maverick_id,
        maverick_name=f"{maverick.first_name} {maverick.last_name}" if maverick else None,
        interview_type=interview.interview_type.value,
        interview_mode=interview.interview_mode.value,
        interview_date=interview.interview_date,
        interview_time=interview.interview_time,
        duration_minutes=interview.duration_minutes,
        location=interview.location,
        video_link=interview.video_link,
        interviewer_panel=interview.interviewer_panel if interview.interviewer_panel else [],
        status=interview.status.value,
        feedback=interview.feedback,
        rating=interview.rating,
        technical_rating=interview.technical_rating,
        communication_rating=interview.communication_rating,
        cultural_fit_rating=interview.cultural_fit_rating,
        scheduled_by=interview.scheduled_by,
        completed_by=interview.completed_by,
        completed_at=interview.completed_at,
        created_at=interview.created_at,
        updated_at=interview.updated_at
    )


@router.post("/requirements/{requirement_id}/interviews/{interview_id}/feedback", response_model=InterviewResponse)
async def submit_interview_feedback(
    requirement_id: UUID,
    interview_id: UUID,
    feedback_data: SubmitInterviewFeedbackRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Submit feedback for an interview

    **Required role**: Manager or HR
    **Path params**:
    - requirement_id: UUID of the requirement
    - interview_id: UUID of the interview
    **Body**: Feedback and ratings

    Submits feedback and ratings for a completed interview.
    """
    # Verify requirement
    requirement = _get_requirement_or_404(db, requirement_id)

    if current_user.role not in [UserRole.HR, UserRole.SUPER_ADMIN]:
        if requirement.requested_by != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the requirement creator or HR can submit feedback"
            )

    # Get interview
    interview = db.query(RequirementInterview).filter(
        RequirementInterview.id == interview_id,
        RequirementInterview.requirement_id == requirement_id
    ).first()

    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview not found"
        )

    # Update interview with feedback
    interview.feedback = feedback_data.feedback
    interview.rating = feedback_data.rating
    interview.technical_rating = feedback_data.technical_rating
    interview.communication_rating = feedback_data.communication_rating
    interview.cultural_fit_rating = feedback_data.cultural_fit_rating
    interview.status = InterviewStatus.COMPLETED
    interview.completed_by = current_user.id
    interview.completed_at = datetime.utcnow()
    interview.updated_at = datetime.utcnow()

    # Update candidate status
    candidate = db.query(RequirementCandidate).filter(
        RequirementCandidate.id == interview.candidate_id
    ).first()

    if candidate:
        candidate.status = CandidateStatus.INTERVIEWED
        candidate.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(interview)

    # Get maverick details
    maverick = db.query(Maverick).filter(Maverick.id == interview.maverick_id).first()

    return InterviewResponse(
        id=interview.id,
        requirement_id=interview.requirement_id,
        candidate_id=interview.candidate_id,
        maverick_id=interview.maverick_id,
        maverick_name=f"{maverick.first_name} {maverick.last_name}" if maverick else None,
        interview_type=interview.interview_type.value,
        interview_mode=interview.interview_mode.value,
        interview_date=interview.interview_date,
        interview_time=interview.interview_time,
        duration_minutes=interview.duration_minutes,
        location=interview.location,
        video_link=interview.video_link,
        interviewer_panel=interview.interviewer_panel if interview.interviewer_panel else [],
        status=interview.status.value,
        feedback=interview.feedback,
        rating=interview.rating,
        technical_rating=interview.technical_rating,
        communication_rating=interview.communication_rating,
        cultural_fit_rating=interview.cultural_fit_rating,
        scheduled_by=interview.scheduled_by,
        completed_by=interview.completed_by,
        completed_at=interview.completed_at,
        created_at=interview.created_at,
        updated_at=interview.updated_at
    )


@router.get("/requirements/{requirement_id}/interviews", response_model=InterviewListResponse)
async def list_interviews(
    requirement_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all interviews for a requirement

    **Required role**: Manager or HR
    **Path params**:
    - requirement_id: UUID of the requirement

    Returns all scheduled interviews for this requirement.
    """
    # Verify requirement
    requirement = _get_requirement_or_404(db, requirement_id)

    if current_user.role not in [UserRole.HR, UserRole.SUPER_ADMIN]:
        if requirement.requested_by != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the requirement creator or HR can view interviews"
            )

    # Get interviews
    interviews = db.query(RequirementInterview).filter(
        RequirementInterview.requirement_id == requirement_id
    ).order_by(RequirementInterview.interview_date.desc()).all()

    # Build response
    response_list = []
    for interview in interviews:
        maverick = db.query(Maverick).filter(Maverick.id == interview.maverick_id).first()

        response_list.append(InterviewResponse(
            id=interview.id,
            requirement_id=interview.requirement_id,
            candidate_id=interview.candidate_id,
            maverick_id=interview.maverick_id,
            maverick_name=f"{maverick.first_name} {maverick.last_name}" if maverick else None,
            interview_type=interview.interview_type.value,
            interview_mode=interview.interview_mode.value,
            interview_date=interview.interview_date,
            interview_time=interview.interview_time,
            duration_minutes=interview.duration_minutes,
            location=interview.location,
            video_link=interview.video_link,
            interviewer_panel=interview.interviewer_panel if interview.interviewer_panel else [],
            status=interview.status.value,
            feedback=interview.feedback,
            rating=interview.rating,
            technical_rating=interview.technical_rating,
            communication_rating=interview.communication_rating,
            cultural_fit_rating=interview.cultural_fit_rating,
            scheduled_by=interview.scheduled_by,
            completed_by=interview.completed_by,
            completed_at=interview.completed_at,
            created_at=interview.created_at,
            updated_at=interview.updated_at
        ))

    return InterviewListResponse(
        interviews=response_list,
        total=len(response_list)
    )
