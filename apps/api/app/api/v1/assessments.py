"""
Assessment & Marks Entry API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from uuid import UUID
from datetime import datetime
import io
import pandas as pd
import logging

logger = logging.getLogger(__name__)

from app.database import get_db
from app.models.user import User, UserRole
from app.models.batch import Batch
from app.models.maverick import Maverick
from app.models.pipeline import PipelineJob, JobType
from app.models.assessment import Assessment, AssessmentAttempt
from app.models.progress import MaverickJobProgress, ProgressStatus
from app.schemas.assessment import (
    AssessmentJobCreate,
    AssessmentJobResponse,
    AssessmentListResponse,
    EnterMarksRequest,
    EnterMarksResponse,
    BulkMarksRequest,
    BulkMarksResponse,
    ExcelMarksUploadResponse,
    AssessmentAttemptResponse,
    AssessmentHistoryResponse
)
from app.services.auth import get_current_user, get_hr_user, get_trainer_or_admin
from app.services.skill_proficiency_service import skill_proficiency_service


router = APIRouter()


async def auto_progress_maverick(
    db: Session,
    maverick_id: UUID,
    batch_id: UUID,
    current_job_id: UUID
):
    """
    Auto-progress maverick to next job in pipeline
    
    Returns: (progressed: bool, next_job_name: str)
    """
    # Get current job
    current_job = db.query(PipelineJob).filter(PipelineJob.id == current_job_id).first()
    if not current_job:
        return False, None
    
    # Find next job in sequence
    next_job = db.query(PipelineJob).filter(
        PipelineJob.pipeline_id == current_job.pipeline_id,
        PipelineJob.sequence_order > current_job.sequence_order
    ).order_by(PipelineJob.sequence_order).first()
    
    if not next_job:
        # No more jobs - mark current as completed
        current_progress = db.query(MaverickJobProgress).filter(
            MaverickJobProgress.maverick_id == maverick_id,
            MaverickJobProgress.batch_id == batch_id,
            MaverickJobProgress.job_id == current_job_id
        ).first()
        
        if current_progress:
            current_progress.status = ProgressStatus.COMPLETED
            current_progress.completion_percentage = 100
            db.commit()
        
        return False, "No next job (pipeline complete)"
    
    # Mark current job as completed
    current_progress = db.query(MaverickJobProgress).filter(
        MaverickJobProgress.maverick_id == maverick_id,
        MaverickJobProgress.batch_id == batch_id,
        MaverickJobProgress.job_id == current_job_id
    ).first()
    
    if current_progress:
        current_progress.status = ProgressStatus.COMPLETED
        current_progress.completion_percentage = 100
    
    # Mark next job as in progress
    next_progress = db.query(MaverickJobProgress).filter(
        MaverickJobProgress.maverick_id == maverick_id,
        MaverickJobProgress.batch_id == batch_id,
        MaverickJobProgress.job_id == next_job.id
    ).first()
    
    if next_progress:
        next_progress.status = ProgressStatus.IN_PROGRESS
        next_progress.started_at = datetime.utcnow()
    
    db.commit()
    
    return True, next_job.name


@router.get("/statistics")
async def get_assessment_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get actionable assessment statistics for HR

    Returns metrics HR can actually ACT on:
    - Total assessments (with unused count)
    - Mavericks needing retake (failed their last attempt)
    - Mavericks pending evaluation
    - Overall completion & pass rate
    """
    from sqlalchemy import func, distinct, and_
    from datetime import datetime, timezone

    total_assessments = db.query(func.count(Assessment.id)).scalar() or 0

    # Assessments with no attempts (not being used)
    assessments_with_attempts = db.query(func.count(distinct(AssessmentAttempt.assessment_id))).scalar() or 0
    not_taken = total_assessments - assessments_with_attempts

    # Total attempts
    total_attempts = db.query(func.count(AssessmentAttempt.id)).scalar() or 0
    passed_attempts = db.query(func.count(AssessmentAttempt.id)).filter(
        AssessmentAttempt.passed == True
    ).scalar() or 0

    # Overall pass rate
    pass_rate = round((passed_attempts / total_attempts * 100), 1) if total_attempts > 0 else 0

    # ACTIONABLE: Mavericks who FAILED and need retake/support
    # Get mavericks whose MOST RECENT attempt was a failure
    from sqlalchemy import desc

    # Get the most recent attempt for each maverick
    subquery = db.query(
        AssessmentAttempt.maverick_id,
        func.max(AssessmentAttempt.evaluated_at).label('last_attempt_date')
    ).group_by(AssessmentAttempt.maverick_id).subquery()

    # Find mavericks whose last attempt was a failure
    mavericks_need_retake = db.query(func.count(distinct(AssessmentAttempt.maverick_id))).join(
        subquery,
        and_(
            AssessmentAttempt.maverick_id == subquery.c.maverick_id,
            AssessmentAttempt.evaluated_at == subquery.c.last_attempt_date
        )
    ).filter(AssessmentAttempt.passed == False).scalar() or 0

    # ACTIONABLE: Assessments scheduled but not yet evaluated
    # Get assessments scheduled in the past but have fewer attempts than expected
    scheduled_assessments = db.query(func.count(Assessment.id)).filter(
        and_(
            Assessment.scheduled_date.isnot(None),
            Assessment.scheduled_date <= datetime.now(timezone.utc)
        )
    ).scalar() or 0

    # ACTIONABLE: Average completion rate (what % of scheduled assessments have attempts)
    if scheduled_assessments > 0:
        scheduled_with_attempts = db.query(func.count(distinct(Assessment.id))).filter(
            and_(
                Assessment.scheduled_date.isnot(None),
                Assessment.scheduled_date <= datetime.now(timezone.utc),
                Assessment.id.in_(
                    db.query(distinct(AssessmentAttempt.assessment_id))
                )
            )
        ).scalar() or 0
        completion_rate = round((scheduled_with_attempts / scheduled_assessments * 100), 1)
    else:
        completion_rate = 0

    return {
        "total_assessments": total_assessments,
        "assessments_not_used": not_taken,
        "mavericks_need_retake": mavericks_need_retake,
        "scheduled_assessments": scheduled_assessments,
        "completion_rate": completion_rate,
        "overall_pass_rate": pass_rate,
        "total_attempts": total_attempts,
        "passed_attempts": passed_attempts
    }


@router.get("/", response_model=AssessmentListResponse)
async def list_assessments(
    page: int = 1,
    page_size: int = 20,
    batch_id: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all assessments with pagination and filters

    **Required role**: Any authenticated user
    **Query params**:
    - page: Page number (default: 1)
    - page_size: Items per page (default: 20)
    - batch_id: Filter by batch ID
    - search: Search by title or description

    Returns all assessments with attempt statistics.
    """
    query = db.query(Assessment)

    # Apply filters
    if batch_id:
        try:
            query = query.filter(Assessment.batch_id == UUID(batch_id))
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid batch_id format"
            )

    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (Assessment.title.ilike(search_filter)) |
            (Assessment.description.ilike(search_filter))
        )

    # Get total count
    total = query.count()

    # Calculate pagination
    total_pages = (total + page_size - 1) // page_size
    offset = (page - 1) * page_size

    # Get paginated results
    assessments = query.order_by(Assessment.created_at.desc()).offset(offset).limit(page_size).all()

    # Build response with attempt statistics
    assessment_responses = []
    for assessment in assessments:
        # Get attempt statistics
        attempts = db.query(AssessmentAttempt).filter(
            AssessmentAttempt.assessment_id == assessment.id
        ).all()

        total_attempts = len(attempts)
        passed_count = sum(1 for a in attempts if a.passed)
        failed_count = total_attempts - passed_count

        # Get batch name
        batch = db.query(Batch).filter(Batch.id == assessment.batch_id).first()
        batch_name = batch.name if batch else "Unknown"

        # Get job name
        job = db.query(PipelineJob).filter(PipelineJob.id == assessment.job_id).first()
        job_name = job.name if job else "Unknown"

        # Calculate pending and evaluated counts
        mavericks_in_batch = db.query(Maverick).filter(
            Maverick.current_batch_id == assessment.batch_id
        ).count()

        evaluated_count = len(set(a.maverick_id for a in attempts))
        pending_count = max(0, mavericks_in_batch - evaluated_count)

        assessment_responses.append(AssessmentJobResponse(
            id=assessment.id,
            job_id=assessment.job_id,
            batch_id=assessment.batch_id,
            title=assessment.title,
            description=assessment.description,
            assessment_link=assessment.assessment_link,
            max_marks=assessment.max_marks,
            passing_marks=assessment.passing_marks,
            duration_minutes=assessment.duration_minutes,
            scheduled_date=assessment.scheduled_date,
            created_by=assessment.created_by,
            created_at=assessment.created_at,
            updated_at=assessment.updated_at,
            total_attempts=total_attempts,
            passed_count=passed_count,
            failed_count=failed_count,
            batch_name=batch_name,
            job_name=job_name,
            pending_count=pending_count,
            evaluated_count=evaluated_count
        ))

    return AssessmentListResponse(
        assessments=assessment_responses,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/{assessment_id}", response_model=AssessmentJobResponse)
async def get_assessment(
    assessment_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific assessment by ID

    **Required role**: Any authenticated user
    **Path params**:
    - assessment_id: UUID of the assessment

    Returns assessment details with attempt statistics.
    """
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()

    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found"
        )

    # Get attempt statistics
    attempts = db.query(AssessmentAttempt).filter(
        AssessmentAttempt.assessment_id == assessment.id
    ).all()

    total_attempts = len(attempts)
    passed_count = sum(1 for a in attempts if a.passed)
    failed_count = total_attempts - passed_count

    # Calculate pending and evaluated counts
    # Get all mavericks in this batch
    mavericks_in_batch = db.query(Maverick).filter(
        Maverick.current_batch_id == assessment.batch_id
    ).count()

    # Evaluated = those who have attempts
    evaluated_count = len(set(a.maverick_id for a in attempts))

    # Pending = total mavericks - evaluated
    pending_count = max(0, mavericks_in_batch - evaluated_count)

    # Get batch name
    batch = db.query(Batch).filter(Batch.id == assessment.batch_id).first()
    batch_name = batch.name if batch else None

    # Get job name
    job = db.query(PipelineJob).filter(PipelineJob.id == assessment.job_id).first()
    job_name = job.name if job else None

    return AssessmentJobResponse(
        id=assessment.id,
        job_id=assessment.job_id,
        batch_id=assessment.batch_id,
        title=assessment.title,
        description=assessment.description,
        assessment_link=assessment.assessment_link,
        max_marks=assessment.max_marks,
        passing_marks=assessment.passing_marks,
        duration_minutes=assessment.duration_minutes,
        scheduled_date=assessment.scheduled_date,
        created_by=assessment.created_by,
        created_at=assessment.created_at,
        updated_at=assessment.updated_at,
        total_attempts=total_attempts,
        passed_count=passed_count,
        failed_count=failed_count,
        batch_name=batch_name,
        job_name=job_name,
        pending_count=pending_count,
        evaluated_count=evaluated_count
    )


@router.post("/", response_model=AssessmentJobResponse, status_code=status.HTTP_201_CREATED)
async def create_assessment_job(
    assessment_data: AssessmentJobCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_trainer_or_admin)
):
    """
    Schedule an assessment for a maverick

    **Required role**: Trainer, HR, or Super Admin
    **Body**:
    - job_id: Pipeline job UUID (must be ASSESSMENT type)
    - batch_id: Batch UUID
    - title: Assessment title
    - max_marks: Maximum marks
    - passing_marks: Passing threshold
    - description, duration_minutes, scheduled_date: Optional
    """
    # Verify job exists and is ASSESSMENT type
    job = db.query(PipelineJob).filter(PipelineJob.id == assessment_data.job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pipeline job not found"
        )

    if job.job_type != JobType.ASSESSMENT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Job must be ASSESSMENT type, got {job.job_type}"
        )
    
    # Verify batch exists
    batch = db.query(Batch).filter(Batch.id == assessment_data.batch_id).first()
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Batch not found"
        )
    
    # Verify job belongs to batch's pipeline
    if job.pipeline_id != batch.pipeline_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job does not belong to batch's pipeline"
        )
    
    # Check if assessment already exists
    existing = db.query(Assessment).filter(
        Assessment.job_id == assessment_data.job_id,
        Assessment.batch_id == assessment_data.batch_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Assessment already exists for this job and batch"
        )
    
    # Create assessment (copy metadata from job for skill proficiency tracking)
    assessment = Assessment(
        job_id=assessment_data.job_id,
        batch_id=assessment_data.batch_id,
        title=assessment_data.title,
        description=assessment_data.description,
        max_marks=assessment_data.max_marks,
        passing_marks=assessment_data.passing_marks,
        duration_minutes=assessment_data.duration_minutes,
        scheduled_date=assessment_data.scheduled_date,
        config_metadata=job.job_metadata,  # Copy job metadata (contains skills_tested)
        created_by=current_user.id
    )
    
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    
    return AssessmentJobResponse(
        id=assessment.id,
        job_id=assessment.job_id,
        batch_id=assessment.batch_id,
        title=assessment.title,
        description=assessment.description,
        max_marks=assessment.max_marks,
        passing_marks=assessment.passing_marks,
        duration_minutes=assessment.duration_minutes,
        scheduled_date=assessment.scheduled_date,
        created_by=assessment.created_by,
        created_at=assessment.created_at,
        updated_at=assessment.updated_at,
        total_attempts=0,
        passed_count=0,
        failed_count=0
    )


@router.get("/{assessment_id}/attempts")
async def get_assessment_attempts(
    assessment_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all attempts for an assessment

    **Required role**: Any authenticated user
    **Path params**:
    - assessment_id: UUID of the assessment

    Returns all attempts with student details.
    """
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found"
        )

    # Get all attempts for this assessment
    attempts = db.query(AssessmentAttempt).filter(
        AssessmentAttempt.assessment_id == assessment_id
    ).all()

    # Build response with maverick details
    attempt_responses = []
    for attempt in attempts:
        maverick = db.query(Maverick).filter(Maverick.id == attempt.maverick_id).first()
        if not maverick:
            continue

        percentage = (float(attempt.marks_obtained) / float(attempt.max_marks)) * 100 if attempt.max_marks > 0 else 0

        attempt_responses.append(AssessmentAttemptResponse(
            id=attempt.id,
            assessment_id=attempt.assessment_id,
            maverick_id=attempt.maverick_id,
            maverick_name=maverick.name,
            maverick_email=maverick.email,
            batch_id=attempt.batch_id,
            marks_obtained=attempt.marks_obtained,
            max_marks=attempt.max_marks,
            percentage=round(percentage, 2),
            passed=attempt.passed,
            feedback=attempt.feedback,
            evaluated_by=attempt.evaluated_by,
            evaluated_at=attempt.evaluated_at,
            created_at=attempt.created_at
        ))

    return {
        "assessment_id": str(assessment_id),
        "assessment_title": assessment.title,
        "total_attempts": len(attempt_responses),
        "attempts": attempt_responses
    }


@router.post("/{assessment_id}/enter-marks", response_model=EnterMarksResponse)
async def enter_marks_manually(
    assessment_id: UUID,
    marks_data: EnterMarksRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Enter marks for a maverick manually

    **Required role**: Trainer or Admin
    **Path params**:
    - assessment_id: UUID of the assessment
    **Body**:
    - maverick_id: Student UUID
    - marks_obtained: Marks scored
    - feedback: Optional feedback
    - auto_progress: Auto-progress if passed (default: True)

    **Auto-progression logic**:
    - If marks >= passing_marks: Progress to next job
    - If marks < passing_marks: Stay on current job
    """
    # Verify user has permission (trainer or admin)
    if current_user.role not in [UserRole.TRAINER, UserRole.SUPER_ADMIN, UserRole.HR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only trainers and admins can enter marks"
        )

    # Get assessment
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found"
        )

    # Verify maverick exists
    maverick = db.query(Maverick).filter(Maverick.id == marks_data.maverick_id).first()
    if not maverick:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Maverick not found"
        )

    # Validate marks
    if marks_data.marks_obtained > assessment.max_marks:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Marks cannot exceed maximum marks ({assessment.max_marks})"
        )

    # Check if passed
    passed = marks_data.marks_obtained >= float(assessment.passing_marks)
    percentage = (marks_data.marks_obtained / float(assessment.max_marks)) * 100

    # Create assessment attempt
    attempt = AssessmentAttempt(
        assessment_id=assessment_id,
        maverick_id=marks_data.maverick_id,
        batch_id=assessment.batch_id,
        marks_obtained=marks_data.marks_obtained,
        max_marks=assessment.max_marks,
        passed=passed,
        feedback=marks_data.feedback,
        evaluated_by=current_user.id,
        evaluated_at=datetime.utcnow()
    )

    db.add(attempt)

    # Update job progress with score
    progress = db.query(MaverickJobProgress).filter(
        MaverickJobProgress.maverick_id == marks_data.maverick_id,
        MaverickJobProgress.batch_id == assessment.batch_id,
        MaverickJobProgress.job_id == assessment.job_id
    ).first()

    if progress:
        progress.score = float(marks_data.marks_obtained)
        progress.completion_percentage = int(percentage)
        if passed:
            progress.status = ProgressStatus.COMPLETED
        else:
            progress.status = ProgressStatus.FAILED

    db.commit()
    db.refresh(attempt)

    # === AUTO-UPDATE SKILL PROFICIENCY (Day 19) ===
    # Extract skills from assessment config_metadata and update proficiency
    try:
        logger.info(f"Checking assessment config_metadata for skill proficiency update...")
        logger.info(f"Assessment config_metadata: {assessment.config_metadata}")

        if assessment.config_metadata and isinstance(assessment.config_metadata, dict):
            skills_tested = assessment.config_metadata.get("skills_tested", {})
            logger.info(f"Skills tested: {skills_tested}")

            if skills_tested:
                # Convert marks to skill scores (proportional to skill weight in assessment)
                skill_scores = {}
                for skill_name, weight in skills_tested.items():
                    # Calculate skill score based on overall marks and weight
                    # Convert Decimal to float for calculation
                    skill_score = (marks_data.marks_obtained / float(assessment.max_marks)) * 100
                    skill_scores[skill_name] = skill_score

                logger.info(f"Calculated skill scores: {skill_scores}")

                # Update skill proficiency
                await skill_proficiency_service.analyze_assessment_for_skills(
                    maverick_id=str(marks_data.maverick_id),
                    assessment_id=str(assessment_id),
                    assessment_data={"skill_scores": skill_scores},
                    db=db
                )

                logger.info(f"✅ Updated skill proficiency for maverick {marks_data.maverick_id}")
            else:
                logger.warning(f"No skills_tested found in assessment config_metadata")
        else:
            logger.warning(f"Assessment config_metadata is None or not a dict: {assessment.config_metadata}")
    except Exception as e:
        logger.error(f"❌ Failed to update skill proficiency: {e}", exc_info=True)
        # Don't fail marks entry if skill proficiency update fails

    # Auto-progress if passed and enabled
    progressed = False
    next_job_name = None

    if passed and marks_data.auto_progress:
        progressed, next_job_name = await auto_progress_maverick(
            db, marks_data.maverick_id, assessment.batch_id, assessment.job_id
        )

    message = f"Marks entered successfully. "
    if passed:
        message += f"PASSED with {percentage:.1f}%. "
        if progressed:
            message += f"Progressed to next job: {next_job_name}"
        else:
            message += "Pipeline complete or progression disabled."
    else:
        message += f"FAILED with {percentage:.1f}%. Needs to retry."

    return EnterMarksResponse(
        success=True,
        assessment_attempt_id=attempt.id,
        maverick_id=marks_data.maverick_id,
        marks_obtained=marks_data.marks_obtained,
        max_marks=assessment.max_marks,
        passed=passed,
        progressed=progressed,
        message=message
    )


@router.get("/{assessment_id}/template/excel")
async def download_marks_template(
    assessment_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Download Excel template for marks entry

    **Required role**: Any authenticated user
    **Path params**:
    - assessment_id: UUID of the assessment

    Returns Excel file with maverick list for marks entry.
    """
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found"
        )

    # Get all mavericks in the batch
    mavericks = db.query(Maverick).filter(
        Maverick.current_batch_id == assessment.batch_id
    ).all()

    # Create Excel file
    output = io.BytesIO()

    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Instructions sheet
        instructions_df = pd.DataFrame({
            'Instructions': [
                f'Marks Entry Template for: {assessment.title}',
                '',
                f'Maximum Marks: {assessment.max_marks}',
                f'Passing Marks: {assessment.passing_marks}',
                '',
                'HOW TO USE:',
                '1. Go to the "Marks" sheet',
                '2. Enter marks in the "Marks_Obtained" column',
                '3. Optionally add feedback in the "Feedback" column',
                '4. Save and upload the file',
                '',
                'NOTES:',
                f'- Marks must be between 0 and {assessment.max_marks}',
                '- Do not modify Maverick_ID or Name columns',
                f'- Students scoring >= {assessment.passing_marks} will be marked as PASSED',
            ]
        })
        instructions_df.to_excel(writer, sheet_name='Instructions', index=False)

        # Marks entry sheet
        marks_data = []
        for m in mavericks:
            marks_data.append({
                'Maverick_ID': str(m.id),
                'Name': m.name,
                'Email': m.email,
                'Marks_Obtained': '',
                'Feedback': ''
            })

        marks_df = pd.DataFrame(marks_data)
        marks_df.to_excel(writer, sheet_name='Marks', index=False)

    output.seek(0)

    filename = f"marks_template_{assessment.title.replace(' ', '_')}.xlsx"

    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.post("/{assessment_id}/upload/excel", response_model=ExcelMarksUploadResponse)
async def upload_marks_via_excel(
    assessment_id: UUID,
    file: UploadFile = File(...),
    auto_progress: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload marks via Excel file

    **Required role**: Trainer or Admin
    **Path params**:
    - assessment_id: UUID of the assessment
    **Query params**:
    - auto_progress: Auto-progress passed students (default: True)
    **Body**:
    - file: Excel file (use template from /template/excel)
    """
    # Verify permission
    if current_user.role not in [UserRole.TRAINER, UserRole.SUPER_ADMIN, UserRole.HR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only trainers and admins can upload marks"
        )

    # Get assessment
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found"
        )

    # Read Excel file
    try:
        contents = await file.read()
        df = pd.read_excel(io.BytesIO(contents), sheet_name='Marks')
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error reading Excel file: {str(e)}"
        )

    # Validate required columns
    required_columns = ['Maverick_ID', 'Marks_Obtained']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Missing required columns: {', '.join(missing_columns)}"
        )

    # Filter rows with marks entered
    df = df[df['Marks_Obtained'].notna() & (df['Marks_Obtained'] != '')]

    total_rows = len(df)
    success_count = 0
    failed_count = 0
    passed_count = 0
    progressed_count = 0
    errors = []

    for idx, row in df.iterrows():
        try:
            maverick_id = row['Maverick_ID']
            marks_obtained = float(row['Marks_Obtained'])
            feedback = row.get('Feedback', '')

            # Validate marks
            if marks_obtained > float(assessment.max_marks) or marks_obtained < 0:
                errors.append({
                    "row": int(idx) + 2,
                    "maverick_id": maverick_id,
                    "error": f"Invalid marks: {marks_obtained} (must be 0-{assessment.max_marks})"
                })
                failed_count += 1
                continue

            # Check if passed
            passed = marks_obtained >= float(assessment.passing_marks)
            percentage = (marks_obtained / float(assessment.max_marks)) * 100

            # Create attempt
            attempt = AssessmentAttempt(
                assessment_id=assessment_id,
                maverick_id=maverick_id,
                batch_id=assessment.batch_id,
                marks_obtained=marks_obtained,
                max_marks=assessment.max_marks,
                passed=passed,
                feedback=feedback if feedback else None,
                evaluated_by=current_user.id,
                evaluated_at=datetime.utcnow()
            )
            db.add(attempt)

            # Update progress
            progress = db.query(MaverickJobProgress).filter(
                MaverickJobProgress.maverick_id == maverick_id,
                MaverickJobProgress.batch_id == assessment.batch_id,
                MaverickJobProgress.job_id == assessment.job_id
            ).first()

            if progress:
                progress.score = float(marks_obtained)
                progress.completion_percentage = int(percentage)
                if passed:
                    progress.status = ProgressStatus.COMPLETED
                else:
                    progress.status = ProgressStatus.FAILED

            success_count += 1
            if passed:
                passed_count += 1

                # Auto-progress
                if auto_progress:
                    progressed, _ = await auto_progress_maverick(
                        db, maverick_id, assessment.batch_id, assessment.job_id
                    )
                    if progressed:
                        progressed_count += 1

        except Exception as e:
            errors.append({
                "row": int(idx) + 2,
                "maverick_id": str(maverick_id) if 'maverick_id' in locals() else "Unknown",
                "error": str(e)
            })
            failed_count += 1

    db.commit()

    return ExcelMarksUploadResponse(
        success_count=success_count,
        failed_count=failed_count,
        total_rows=total_rows,
        passed_count=passed_count,
        progressed_count=progressed_count,
        errors=errors,
        message=f"Processed {total_rows} rows: {success_count} successful, {failed_count} failed. {passed_count} passed, {progressed_count} progressed."
    )


@router.get("/{assessment_id}/history", response_model=AssessmentHistoryResponse)
async def get_assessment_history(
    assessment_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get assessment history with all attempts

    **Required role**: Any authenticated user
    **Path params**:
    - assessment_id: UUID of the assessment

    Returns all attempts for this assessment.
    """
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found"
        )

    # Get all attempts
    attempts = db.query(AssessmentAttempt).filter(
        AssessmentAttempt.assessment_id == assessment_id
    ).order_by(AssessmentAttempt.evaluated_at.desc()).all()

    # Build response
    attempt_responses = []
    for attempt in attempts:
        maverick = db.query(Maverick).filter(Maverick.id == attempt.maverick_id).first()
        percentage = (float(attempt.marks_obtained) / float(attempt.max_marks)) * 100

        attempt_responses.append(AssessmentAttemptResponse(
            id=attempt.id,
            assessment_id=attempt.assessment_id,
            maverick_id=attempt.maverick_id,
            maverick_name=maverick.name if maverick else "Unknown",
            maverick_email=maverick.email if maverick else "N/A",
            batch_id=attempt.batch_id,
            marks_obtained=attempt.marks_obtained,
            max_marks=attempt.max_marks,
            percentage=round(percentage, 2),
            passed=attempt.passed,
            feedback=attempt.feedback,
            evaluated_by=attempt.evaluated_by,
            evaluated_at=attempt.evaluated_at,
            created_at=attempt.created_at
        ))

    batch = db.query(Batch).filter(Batch.id == assessment.batch_id).first()
    trainer = None
    if batch and batch.trainer_id:
        trainer = db.query(User).filter(User.id == batch.trainer_id).first()

    return AssessmentHistoryResponse(
        assessment_id=assessment.id,
        assessment_title=assessment.title,
        assessment_description=assessment.description,
        duration_minutes=assessment.duration_minutes,
        batch_id=assessment.batch_id,
        batch_name=batch.name if batch else "Unknown",
        trainer_id=trainer.id if trainer else None,
        trainer_name=trainer.name if trainer else None,
        max_marks=assessment.max_marks,
        passing_marks=assessment.passing_marks,
        total_attempts=len(attempts),
        attempts=attempt_responses
    )
