"""
Batch Job Schedule Management API
Manages the timeline and scheduling of pipeline jobs within batches
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List
from uuid import UUID
from datetime import datetime, timezone

from app.database import get_db
from app.models.user import User
from app.models.batch import Batch
from app.models.pipeline import Pipeline, PipelineJob
from app.models.batch_job_schedule import BatchJobSchedule, JobScheduleStatus
from app.models.assessment import Assessment
from app.schemas.batch_schedule import (
    ScheduleJobRequest,
    UpdateScheduleRequest,
    BatchJobScheduleResponse,
    BatchTimelineResponse,
    MarkAttendanceRequest,
    MarkAttendanceResponse,
    QuickScheduleAllRequest,
    QuickScheduleAllResponse
)
from app.utils.dependencies import get_current_user, get_trainer_or_admin

router = APIRouter()


@router.get("/{batch_id}/timeline", response_model=BatchTimelineResponse)
async def get_batch_timeline(
    batch_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get complete timeline for a batch with all scheduled and unscheduled jobs
    
    **Required role**: Any authenticated user
    **Path params**:
    - batch_id: UUID of the batch
    
    Returns:
    - Batch info
    - Pipeline jobs with their schedules
    - Unscheduled jobs
    - Statistics
    """
    batch = db.query(Batch).options(
        joinedload(Batch.pipeline).joinedload(Pipeline.jobs)
    ).filter(Batch.id == batch_id).first()
    
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Batch not found"
        )
    
    # Get all schedules for this batch
    schedules = db.query(BatchJobSchedule).join(
        PipelineJob, BatchJobSchedule.pipeline_job_id == PipelineJob.id
    ).options(
        joinedload(BatchJobSchedule.pipeline_job)
    ).filter(
        BatchJobSchedule.batch_id == batch_id
    ).order_by(
        PipelineJob.sequence_order
    ).all()
    
    # Build schedule responses
    schedule_responses = []
    scheduled_job_ids = set()
    
    for schedule in schedules:
        scheduled_job_ids.add(schedule.pipeline_job_id)
        
        schedule_responses.append(BatchJobScheduleResponse(
            id=schedule.id,
            batch_id=schedule.batch_id,
            pipeline_job_id=schedule.pipeline_job_id,
            job_name=schedule.pipeline_job.name,
            job_type=schedule.pipeline_job.job_type.value,
            job_sequence_order=schedule.pipeline_job.sequence_order,
            job_is_mandatory=schedule.pipeline_job.is_mandatory,
            job_duration_days=schedule.pipeline_job.duration_days,
            scheduled_start_date=schedule.scheduled_start_date,
            scheduled_end_date=schedule.scheduled_end_date,
            actual_start_date=schedule.actual_start_date,
            actual_end_date=schedule.actual_end_date,
            meeting_link=schedule.meeting_link,
            meeting_password=schedule.meeting_password,
            attendance_required=schedule.attendance_required,
            attendance_count=schedule.attendance_count,
            assessment_id=schedule.assessment_id,
            deployment_project_link=schedule.deployment_project_link,
            status=schedule.status.value,
            completion_percentage=schedule.completion_percentage,
            is_overdue=schedule.is_overdue,
            trainer_notes=schedule.trainer_notes,
            is_published=schedule.is_published,
            created_by=schedule.created_by,
            created_at=schedule.created_at,
            updated_at=schedule.updated_at
        ))
    
    # Find unscheduled jobs
    unscheduled_jobs = []
    for job in batch.pipeline.jobs:
        if job.id not in scheduled_job_ids:
            unscheduled_jobs.append({
                "id": str(job.id),
                "name": job.name,
                "job_type": job.job_type.value,
                "sequence_order": job.sequence_order,
                "is_mandatory": job.is_mandatory,
                "duration_days": job.duration_days,
                "description": job.description
            })
    
    # Calculate statistics
    total_jobs = len(batch.pipeline.jobs)
    scheduled_jobs = len(schedules)
    completed_jobs = sum(1 for s in schedules if s.status == JobScheduleStatus.COMPLETED)
    in_progress_jobs = sum(1 for s in schedules if s.status == JobScheduleStatus.IN_PROGRESS)
    overdue_jobs = sum(1 for s in schedules if s.is_overdue)
    
    return BatchTimelineResponse(
        batch_id=batch.id,
        batch_name=batch.name,
        pipeline_id=batch.pipeline_id,
        pipeline_name=batch.pipeline.name,
        batch_start_date=batch.start_date,
        batch_end_date=batch.end_date,
        total_jobs=total_jobs,
        scheduled_jobs=scheduled_jobs,
        completed_jobs=completed_jobs,
        in_progress_jobs=in_progress_jobs,
        overdue_jobs=overdue_jobs,
        schedules=schedule_responses,
        unscheduled_jobs=unscheduled_jobs
    )


@router.post("/{batch_id}/schedule", response_model=BatchJobScheduleResponse, status_code=status.HTTP_201_CREATED)
async def schedule_job(
    batch_id: UUID,
    schedule_data: ScheduleJobRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_trainer_or_admin)
):
    """
    Schedule a pipeline job for a batch

    **Required role**: Trainer, HR, or Super Admin
    **Path params**:
    - batch_id: UUID of the batch
    **Body**: Schedule details including dates, links, notes

    Can optionally create an assessment if job_type is ASSESSMENT
    """
    # Verify batch exists
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Batch not found"
        )

    # Verify pipeline job exists and belongs to batch's pipeline
    pipeline_job = db.query(PipelineJob).filter(
        PipelineJob.id == schedule_data.pipeline_job_id
    ).first()

    if not pipeline_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pipeline job not found"
        )

    if pipeline_job.pipeline_id != batch.pipeline_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Pipeline job does not belong to this batch's pipeline"
        )

    # Check if already scheduled
    existing_schedule = db.query(BatchJobSchedule).filter(
        BatchJobSchedule.batch_id == batch_id,
        BatchJobSchedule.pipeline_job_id == schedule_data.pipeline_job_id
    ).first()

    if existing_schedule:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This job is already scheduled for this batch"
        )

    # Create assessment if job type is ASSESSMENT and assessment_data is provided
    assessment_id = None
    if pipeline_job.job_type.value == "ASSESSMENT" and schedule_data.assessment_data:
        assessment_data = schedule_data.assessment_data

        assessment = Assessment(
            job_id=pipeline_job.id,
            batch_id=batch_id,
            title=assessment_data.title,
            description=assessment_data.description,
            assessment_link=assessment_data.assessment_link,
            max_marks=assessment_data.max_marks,
            passing_marks=assessment_data.passing_marks,
            duration_minutes=assessment_data.duration_minutes,
            scheduled_date=schedule_data.scheduled_start_date,
            created_by=current_user.id
        )
        db.add(assessment)
        db.flush()  # Get assessment ID
        assessment_id = assessment.id

    # Create schedule
    schedule = BatchJobSchedule(
        batch_id=batch_id,
        pipeline_job_id=schedule_data.pipeline_job_id,
        scheduled_start_date=schedule_data.scheduled_start_date,
        scheduled_end_date=schedule_data.scheduled_end_date,
        meeting_link=schedule_data.meeting_link,
        meeting_password=schedule_data.meeting_password,
        attendance_required=schedule_data.attendance_required or False,
        deployment_project_link=schedule_data.deployment_project_link,
        trainer_notes=schedule_data.trainer_notes,
        is_published=schedule_data.is_published or False,
        assessment_id=assessment_id,
        status=JobScheduleStatus.SCHEDULED if schedule_data.scheduled_start_date else JobScheduleStatus.NOT_SCHEDULED,
        created_by=current_user.id
    )

    db.add(schedule)
    db.commit()
    db.refresh(schedule)

    return BatchJobScheduleResponse(
        id=schedule.id,
        batch_id=schedule.batch_id,
        pipeline_job_id=schedule.pipeline_job_id,
        job_name=pipeline_job.name,
        job_type=pipeline_job.job_type.value,
        job_sequence_order=pipeline_job.sequence_order,
        job_is_mandatory=pipeline_job.is_mandatory,
        job_duration_days=pipeline_job.duration_days,
        scheduled_start_date=schedule.scheduled_start_date,
        scheduled_end_date=schedule.scheduled_end_date,
        actual_start_date=schedule.actual_start_date,
        actual_end_date=schedule.actual_end_date,
        meeting_link=schedule.meeting_link,
        meeting_password=schedule.meeting_password,
        attendance_required=schedule.attendance_required,
        attendance_count=schedule.attendance_count,
        assessment_id=schedule.assessment_id,
        deployment_project_link=schedule.deployment_project_link,
        status=schedule.status.value,
        completion_percentage=schedule.completion_percentage,
        is_overdue=schedule.is_overdue,
        trainer_notes=schedule.trainer_notes,
        is_published=schedule.is_published,
        created_by=schedule.created_by,
        created_at=schedule.created_at,
        updated_at=schedule.updated_at
    )


@router.put("/{batch_id}/schedule/{schedule_id}", response_model=BatchJobScheduleResponse)
async def update_schedule(
    batch_id: UUID,
    schedule_id: UUID,
    update_data: UpdateScheduleRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_trainer_or_admin)
):
    """
    Update an existing job schedule

    **Required role**: Trainer, HR, or Super Admin
    **Path params**:
    - batch_id: UUID of the batch
    - schedule_id: UUID of the schedule to update
    **Body**: Fields to update
    """
    schedule = db.query(BatchJobSchedule).filter(
        BatchJobSchedule.id == schedule_id,
        BatchJobSchedule.batch_id == batch_id
    ).first()

    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found"
        )

    # Update fields
    if update_data.scheduled_start_date is not None:
        schedule.scheduled_start_date = update_data.scheduled_start_date
    if update_data.scheduled_end_date is not None:
        schedule.scheduled_end_date = update_data.scheduled_end_date
    if update_data.actual_start_date is not None:
        schedule.actual_start_date = update_data.actual_start_date
    if update_data.actual_end_date is not None:
        schedule.actual_end_date = update_data.actual_end_date
    if update_data.meeting_link is not None:
        schedule.meeting_link = update_data.meeting_link
    if update_data.meeting_password is not None:
        schedule.meeting_password = update_data.meeting_password
    if update_data.attendance_required is not None:
        schedule.attendance_required = update_data.attendance_required
    if update_data.attendance_count is not None:
        schedule.attendance_count = update_data.attendance_count
    if update_data.deployment_project_link is not None:
        schedule.deployment_project_link = update_data.deployment_project_link
    if update_data.trainer_notes is not None:
        schedule.trainer_notes = update_data.trainer_notes
    if update_data.is_published is not None:
        schedule.is_published = update_data.is_published
    if update_data.status is not None:
        schedule.status = JobScheduleStatus(update_data.status)
    if update_data.completion_percentage is not None:
        schedule.completion_percentage = update_data.completion_percentage

    # 🔥 FIX: Sync with maverick_job_progress when marking as complete
    # Note: If attendance was already marked, this will update those who attended
    # If attendance was NOT marked, this will update ALL students in the batch
    if update_data.status == "COMPLETED" and update_data.completion_percentage == 100:
        from app.models.progress import MaverickJobProgress, ProgressStatus
        from app.models.maverick import Maverick
        from datetime import datetime
        import logging

        logger = logging.getLogger(__name__)
        logger.info(f"🔥 Syncing job completion for batch {batch_id}, job {schedule.pipeline_job_id}")

        # Check if attendance was required and tracked
        # If yes, only update students who have progress records (who attended)
        # If no, update all students
        if schedule.attendance_required and schedule.attendance_count > 0:
            # Only update students who already have progress (attended)
            logger.info(f"📋 Attendance-based: Updating only students who attended ({schedule.attendance_count})")
            progress_records = db.query(MaverickJobProgress).filter(
                MaverickJobProgress.job_id == schedule.pipeline_job_id,
                MaverickJobProgress.batch_id == batch_id
            ).all()

            updated_count = 0
            for progress in progress_records:
                if progress.status != ProgressStatus.COMPLETED:
                    progress.status = ProgressStatus.COMPLETED
                    progress.completion_percentage = 100
                    progress.completed_at = datetime.utcnow()
                    updated_count += 1
                    logger.info(f"✅ Marked COMPLETED for student who attended")

            logger.info(f"✨ Updated {updated_count} students who attended")
        else:
            # No attendance tracking - mark complete for ALL students
            logger.info(f"📊 No attendance tracking: Marking complete for ALL students")
            mavericks = db.query(Maverick).filter(Maverick.current_batch_id == batch_id).all()
            logger.info(f"📊 Found {len(mavericks)} mavericks in batch")

            updated_count = 0
            created_count = 0
            for maverick in mavericks:
                progress = db.query(MaverickJobProgress).filter(
                    MaverickJobProgress.maverick_id == maverick.id,
                    MaverickJobProgress.job_id == schedule.pipeline_job_id,
                    MaverickJobProgress.batch_id == batch_id
                ).first()

                if progress:
                    # Update existing progress
                    progress.status = ProgressStatus.COMPLETED
                    progress.completion_percentage = 100
                    progress.completed_at = datetime.utcnow()
                    updated_count += 1
                    logger.info(f"✅ Updated progress for maverick {maverick.name}")
                else:
                    # Create new progress record if it doesn't exist
                    new_progress = MaverickJobProgress(
                        maverick_id=maverick.id,
                        batch_id=batch_id,
                        job_id=schedule.pipeline_job_id,
                        status=ProgressStatus.COMPLETED,
                        completion_percentage=100,
                        started_at=schedule.actual_start_date or datetime.utcnow(),
                        completed_at=datetime.utcnow()
                    )
                    db.add(new_progress)
                    created_count += 1
                    logger.info(f"➕ Created progress for maverick {maverick.name}")

            logger.info(f"✨ Sync complete: {updated_count} updated, {created_count} created")

    # 🚀 Auto-activate deployment job if all jobs are now complete
    # This should run after ANY schedule update, not just completion
    if update_data.status == "COMPLETED":
        from app.services.deployment_service import auto_activate_deployment_job

        batch = db.query(Batch).filter(Batch.id == batch_id).first()
        if batch:
            logger.info(f"🔍 Checking if deployment job should auto-activate for batch {batch_id}...")
            deployment_activated = auto_activate_deployment_job(db, batch_id, batch.pipeline_id)
            if deployment_activated:
                logger.info(f"🚀 Deployment job auto-activated for batch {batch_id}")
            else:
                logger.info(f"⏳ Deployment job not yet ready - other jobs still pending")

    db.commit()
    db.refresh(schedule)

    # Load pipeline job for response
    pipeline_job = db.query(PipelineJob).filter(PipelineJob.id == schedule.pipeline_job_id).first()

    return BatchJobScheduleResponse(
        id=schedule.id,
        batch_id=schedule.batch_id,
        pipeline_job_id=schedule.pipeline_job_id,
        job_name=pipeline_job.name,
        job_type=pipeline_job.job_type.value,
        job_sequence_order=pipeline_job.sequence_order,
        job_is_mandatory=pipeline_job.is_mandatory,
        job_duration_days=pipeline_job.duration_days,
        scheduled_start_date=schedule.scheduled_start_date,
        scheduled_end_date=schedule.scheduled_end_date,
        actual_start_date=schedule.actual_start_date,
        actual_end_date=schedule.actual_end_date,
        meeting_link=schedule.meeting_link,
        meeting_password=schedule.meeting_password,
        attendance_required=schedule.attendance_required,
        attendance_count=schedule.attendance_count,
        assessment_id=schedule.assessment_id,
        deployment_project_link=schedule.deployment_project_link,
        status=schedule.status.value,
        completion_percentage=schedule.completion_percentage,
        is_overdue=schedule.is_overdue,
        trainer_notes=schedule.trainer_notes,
        is_published=schedule.is_published,
        created_by=schedule.created_by,
        created_at=schedule.created_at,
        updated_at=schedule.updated_at
    )


@router.post("/{batch_id}/schedule/{schedule_id}/attendance", response_model=MarkAttendanceResponse)
async def mark_attendance(
    batch_id: UUID,
    schedule_id: UUID,
    attendance_data: MarkAttendanceRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_trainer_or_admin)
):
    """
    Mark attendance for a scheduled job (training or assessment)

    **Required role**: Trainer, HR, or Super Admin
    **Path params**:
    - batch_id: UUID of the batch
    - schedule_id: UUID of the schedule
    **Body**:
    - maverick_ids: List of maverick IDs who attended
    - notes: Optional attendance notes
    """
    # Verify schedule exists
    schedule = db.query(BatchJobSchedule).filter(
        BatchJobSchedule.id == schedule_id,
        BatchJobSchedule.batch_id == batch_id
    ).first()

    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found"
        )

    # Update attendance count
    schedule.attendance_count = len(attendance_data.maverick_ids)

    # If notes provided, update trainer notes
    if attendance_data.notes:
        schedule.trainer_notes = attendance_data.notes if not schedule.trainer_notes else f"{schedule.trainer_notes}\n\nAttendance: {attendance_data.notes}"

    # 🔥 NEW: Update maverick progress for students who attended
    from app.models.progress import MaverickJobProgress, ProgressStatus
    from datetime import datetime
    import logging

    logger = logging.getLogger(__name__)
    logger.info(f"🎯 Marking attendance for {len(attendance_data.maverick_ids)} mavericks")

    # Mark job as IN_PROGRESS or COMPLETED for students who attended
    for maverick_id in attendance_data.maverick_ids:
        progress = db.query(MaverickJobProgress).filter(
            MaverickJobProgress.maverick_id == maverick_id,
            MaverickJobProgress.job_id == schedule.pipeline_job_id,
            MaverickJobProgress.batch_id == batch_id
        ).first()

        if progress:
            # If schedule is completed, mark progress as completed
            if schedule.status == JobScheduleStatus.COMPLETED:
                progress.status = ProgressStatus.COMPLETED
                progress.completion_percentage = 100
                progress.completed_at = datetime.utcnow()
                logger.info(f"✅ Marked COMPLETED for maverick {maverick_id}")
            elif progress.status == ProgressStatus.PENDING:
                # Start the job if it's still pending
                progress.status = ProgressStatus.IN_PROGRESS
                progress.started_at = datetime.utcnow()
                logger.info(f"▶️ Marked IN_PROGRESS for maverick {maverick_id}")
        else:
            # Create new progress record for this maverick
            status = ProgressStatus.COMPLETED if schedule.status == JobScheduleStatus.COMPLETED else ProgressStatus.IN_PROGRESS
            new_progress = MaverickJobProgress(
                maverick_id=maverick_id,
                batch_id=batch_id,
                job_id=schedule.pipeline_job_id,
                status=status,
                completion_percentage=100 if status == ProgressStatus.COMPLETED else 50,
                started_at=datetime.utcnow(),
                completed_at=datetime.utcnow() if status == ProgressStatus.COMPLETED else None
            )
            db.add(new_progress)
            logger.info(f"➕ Created {status.value} progress for maverick {maverick_id}")

    db.commit()
    db.refresh(schedule)

    return MarkAttendanceResponse(
        success=True,
        attendance_count=schedule.attendance_count,
        message=f"Attendance marked for {schedule.attendance_count} mavericks. Progress updated!"
    )


@router.get("/{batch_id}/schedule/{schedule_id}/attendance")
async def get_attendance(
    batch_id: UUID,
    schedule_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get attendance records for a scheduled job

    **Required role**: Any authenticated user
    **Path params**:
    - batch_id: UUID of the batch
    - schedule_id: UUID of the schedule
    """
    # Verify schedule exists
    schedule = db.query(BatchJobSchedule).filter(
        BatchJobSchedule.id == schedule_id,
        BatchJobSchedule.batch_id == batch_id
    ).first()

    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found"
        )

    return {
        "schedule_id": schedule_id,
        "attendance_count": schedule.attendance_count,
        "attendance_required": schedule.attendance_required,
        "notes": schedule.trainer_notes
    }


@router.delete("/{batch_id}/schedule/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_schedule(
    batch_id: UUID,
    schedule_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_trainer_or_admin)
):
    """
    Delete a job schedule (unschedule a job)

    **Required role**: Trainer, HR, or Super Admin
    **Path params**:
    - batch_id: UUID of the batch
    - schedule_id: UUID of the schedule to delete
    """
    schedule = db.query(BatchJobSchedule).filter(
        BatchJobSchedule.id == schedule_id,
        BatchJobSchedule.batch_id == batch_id
    ).first()

    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found"
        )

    db.delete(schedule)
    db.commit()

    return None
