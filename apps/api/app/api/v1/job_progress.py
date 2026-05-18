"""
Job Progress Tracking API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from uuid import UUID
from datetime import datetime

from app.database import get_db
from app.models.user import User
from app.models.maverick import Maverick
from app.models.batch import Batch
from app.models.batch_job_schedule import BatchJobSchedule
from app.models.pipeline import PipelineJob, JobStatus
from app.models.progress import MaverickJobProgress, ProgressStatus
from app.schemas.job_progress import (
    InitializeJobProgressRequest,
    UpdateJobProgressRequest,
    JobProgressResponse,
    MaverickProgressResponse,
    BatchProgressResponse,
    SkipJobRequest,
    SkipJobResponse,
    BulkInitializeResponse
)
from app.services.auth import get_current_user, get_hr_user


router = APIRouter()


@router.post("/initialize", response_model=BulkInitializeResponse)
async def initialize_job_progress(
    request: InitializeJobProgressRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_hr_user)
):
    """
    Initialize job progress tracking for a maverick in a batch
    
    **Required role**: HR or Super Admin
    **Body**:
    - maverick_id: UUID of the maverick
    - batch_id: UUID of the batch
    
    Creates progress records for all jobs in the batch's pipeline.
    """
    # Verify maverick exists
    maverick = db.query(Maverick).filter(Maverick.id == request.maverick_id).first()
    if not maverick:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Maverick not found"
        )
    
    # Verify batch exists
    batch = db.query(Batch).filter(Batch.id == request.batch_id).first()
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Batch not found"
        )
    
    # Get all jobs in the pipeline
    jobs = db.query(PipelineJob).filter(
        PipelineJob.pipeline_id == batch.pipeline_id
    ).order_by(PipelineJob.sequence_order).all()
    
    if not jobs:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No jobs found in pipeline"
        )
    
    # Check if progress already exists
    existing_count = db.query(MaverickJobProgress).filter(
        MaverickJobProgress.maverick_id == request.maverick_id,
        MaverickJobProgress.batch_id == request.batch_id
    ).count()
    
    if existing_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Progress already initialized ({existing_count} jobs tracked)"
        )
    
    # Create progress records for each job
    created_count = 0
    for job in jobs:
        progress = MaverickJobProgress(
            maverick_id=request.maverick_id,
            batch_id=request.batch_id,
            job_id=job.id,
            status=ProgressStatus.PENDING,
            completion_percentage=0
        )
        db.add(progress)
        created_count += 1
    
    db.commit()
    
    return BulkInitializeResponse(
        success_count=1,
        failed_count=0,
        total_jobs_created=created_count,
        message=f"Initialized progress tracking for {created_count} jobs"
    )


@router.patch("/{progress_id}", response_model=JobProgressResponse)
async def update_job_progress(
    progress_id: UUID,
    update_data: UpdateJobProgressRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update job progress for a maverick
    
    **Required role**: Any authenticated user
    **Path params**:
    - progress_id: UUID of the job progress record
    **Body**:
    - status: New status (PENDING, IN_PROGRESS, COMPLETED, FAILED, SKIPPED)
    - completion_percentage: Progress percentage (0-100)
    - notes: Progress notes
    - score: Score for assessment jobs (0-100)
    """
    progress = db.query(MaverickJobProgress).filter(
        MaverickJobProgress.id == progress_id
    ).first()
    
    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job progress record not found"
        )
    
    # Update fields
    if update_data.status is not None:
        try:
            new_status = ProgressStatus(update_data.status)
            progress.status = new_status
            
            # Auto-set timestamps based on status
            if new_status == ProgressStatus.IN_PROGRESS and not progress.started_at:
                progress.started_at = datetime.utcnow()
            elif new_status == ProgressStatus.COMPLETED:
                progress.completed_at = datetime.utcnow()
                if update_data.completion_percentage is None:
                    progress.completion_percentage = 100
                    
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {update_data.status}"
            )
    
    if update_data.completion_percentage is not None:
        progress.completion_percentage = update_data.completion_percentage
    
    if update_data.notes is not None:
        progress.notes = update_data.notes
    
    if update_data.score is not None:
        progress.score = update_data.score
    
    db.commit()
    db.refresh(progress)
    
    # Get job details for response
    job = db.query(PipelineJob).filter(PipelineJob.id == progress.job_id).first()
    
    return JobProgressResponse(
        id=progress.id,
        maverick_id=progress.maverick_id,
        batch_id=progress.batch_id,
        job_id=progress.job_id,
        job_name=job.name if job else "Unknown",
        job_type=job.job_type.value if job and hasattr(job.job_type, 'value') else "Unknown",
        status=progress.status.value if hasattr(progress.status, 'value') else progress.status,
        completion_percentage=progress.completion_percentage,
        started_at=progress.started_at,
        completed_at=progress.completed_at,
        score=progress.score,
        notes=progress.notes,
        created_at=progress.created_at,
        updated_at=progress.updated_at
    )


@router.get("/maverick/{maverick_id}/batch/{batch_id}", response_model=MaverickProgressResponse)
async def get_maverick_progress(
    maverick_id: UUID,
    batch_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get complete progress for a maverick in a batch

    **Required role**: Any authenticated user
    **Path params**:
    - maverick_id: UUID of the maverick
    - batch_id: UUID of the batch

    Returns all job progress for the maverick with statistics.
    """
    # Verify maverick exists
    maverick = db.query(Maverick).filter(Maverick.id == maverick_id).first()
    if not maverick:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Maverick not found"
        )

    # Verify batch exists
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Batch not found"
        )

    # Get all progress records
    progress_records = db.query(MaverickJobProgress).filter(
        MaverickJobProgress.maverick_id == maverick_id,
        MaverickJobProgress.batch_id == batch_id
    ).all()

    if not progress_records:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No progress records found. Initialize progress first."
        )

    # Calculate statistics
    total_jobs = len(progress_records)
    completed = sum(1 for p in progress_records if p.status == ProgressStatus.COMPLETED)
    in_progress = sum(1 for p in progress_records if p.status == ProgressStatus.IN_PROGRESS)
    pending = sum(1 for p in progress_records if p.status == ProgressStatus.PENDING)
    failed = sum(1 for p in progress_records if p.status == ProgressStatus.FAILED)
    skipped = sum(1 for p in progress_records if p.status == ProgressStatus.SKIPPED)

    # Calculate overall completion
    total_percentage = sum(p.completion_percentage or 0 for p in progress_records)
    overall_completion = (total_percentage / total_jobs) if total_jobs > 0 else 0

    # Build response with job details
    job_progress_list = []
    for progress in progress_records:
        job = db.query(PipelineJob).filter(PipelineJob.id == progress.job_id).first()
        job_progress_list.append(JobProgressResponse(
            id=progress.id,
            maverick_id=progress.maverick_id,
            batch_id=progress.batch_id,
            job_id=progress.job_id,
            job_name=job.name if job else "Unknown",
            job_type=job.job_type.value if job and hasattr(job.job_type, 'value') else "Unknown",
            status=progress.status.value if hasattr(progress.status, 'value') else progress.status,
            completion_percentage=progress.completion_percentage,
            started_at=progress.started_at,
            completed_at=progress.completed_at,
            score=progress.score,
            notes=progress.notes,
            created_at=progress.created_at,
            updated_at=progress.updated_at
        ))

    # Get pipeline info
    from app.models.pipeline import Pipeline
    pipeline = db.query(Pipeline).filter(Pipeline.id == batch.pipeline_id).first()

    return MaverickProgressResponse(
        maverick_id=maverick_id,
        maverick_name=maverick.name,
        batch_id=batch_id,
        batch_name=batch.name,
        pipeline_id=batch.pipeline_id,
        pipeline_name=pipeline.name if pipeline else "Unknown",
        total_jobs=total_jobs,
        completed_jobs=completed,
        in_progress_jobs=in_progress,
        pending_jobs=pending,
        failed_jobs=failed,
        skipped_jobs=skipped,
        overall_completion=round(overall_completion, 2),
        job_progress=job_progress_list
    )


@router.get("/batch/{batch_id}", response_model=BatchProgressResponse)
async def get_batch_progress(
    batch_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get progress summary for all mavericks in a batch

    **Required role**: Any authenticated user
    **Path params**:
    - batch_id: UUID of the batch

    Returns aggregated progress statistics for the entire batch.
    """
    # Verify batch exists
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Batch not found"
        )

    # Get all mavericks in batch
    mavericks = db.query(Maverick).filter(Maverick.current_batch_id == batch_id).all()

    if not mavericks:
        return BatchProgressResponse(
            batch_id=batch_id,
            batch_name=batch.name,
            pipeline_id=batch.pipeline_id,
            pipeline_name="Unknown",
            total_mavericks=0,
            total_jobs=0,
            overall_completion=0.0,
            maverick_progress=[]
        )

    # Get pipeline info
    from app.models.pipeline import Pipeline
    pipeline = db.query(Pipeline).filter(Pipeline.id == batch.pipeline_id).first()

    # Count total jobs in pipeline
    total_jobs = db.query(PipelineJob).filter(
        PipelineJob.pipeline_id == batch.pipeline_id
    ).count()

    # Calculate progress for each maverick
    maverick_summaries = []
    total_completion = 0.0

    for maverick in mavericks:
        progress_records = db.query(MaverickJobProgress).filter(
            MaverickJobProgress.maverick_id == maverick.id,
            MaverickJobProgress.batch_id == batch_id
        ).all()

        # Check if jobs are scheduled for this batch
        scheduled_jobs = db.query(BatchJobSchedule).filter(
            BatchJobSchedule.batch_id == batch_id
        ).count()

        has_scheduled_jobs = scheduled_jobs > 0
        has_initialized = len(progress_records) > 0

        if progress_records:
            completed = sum(1 for p in progress_records if p.status == ProgressStatus.COMPLETED)
            # Calculate completion based on actual pipeline total jobs
            completion = (completed / total_jobs * 100) if total_jobs > 0 else 0.0
        else:
            completed = 0
            completion = 0.0

        maverick_summaries.append({
            "maverick_id": str(maverick.id),
            "maverick_name": maverick.name,
            "completed_jobs": completed,
            "total_jobs": total_jobs,  # Use pipeline total_jobs, not progress_records count
            "completion_percentage": round(completion, 2),
            "has_scheduled_jobs": has_scheduled_jobs,
            "has_initialized": has_initialized
        })

        total_completion += float(completion)

    overall_completion = (total_completion / len(mavericks)) if mavericks else 0.0

    return BatchProgressResponse(
        batch_id=batch_id,
        batch_name=batch.name,
        pipeline_id=batch.pipeline_id,
        pipeline_name=pipeline.name if pipeline else "Unknown",
        total_mavericks=len(mavericks),
        total_jobs=total_jobs,
        overall_completion=round(overall_completion, 2),
        maverick_progress=maverick_summaries
    )


@router.post("/{progress_id}/skip", response_model=SkipJobResponse)
async def skip_optional_job(
    progress_id: UUID,
    request: SkipJobRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Skip an optional job for a maverick

    **Required role**: Any authenticated user
    **Path params**:
    - progress_id: UUID of the job progress record
    **Body**:
    - reason: Reason for skipping the job (required)

    Only optional jobs (is_mandatory=False) can be skipped.
    """
    progress = db.query(MaverickJobProgress).filter(
        MaverickJobProgress.id == progress_id
    ).first()

    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job progress record not found"
        )

    # Get job to check if it's optional
    job = db.query(PipelineJob).filter(PipelineJob.id == progress.job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )

    if job.is_mandatory:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot skip mandatory job"
        )

    # Update progress to SKIPPED
    progress.status = ProgressStatus.SKIPPED
    progress.notes = f"Skipped: {request.reason}"
    progress.completion_percentage = 0

    db.commit()

    return SkipJobResponse(
        success=True,
        maverick_id=progress.maverick_id,
        job_id=progress.job_id,
        message=f"Job '{job.name}' skipped successfully"
    )
