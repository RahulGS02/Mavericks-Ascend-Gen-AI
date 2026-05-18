"""
Deployment Service - Handles deployment job logic and readiness checks
"""
from sqlalchemy.orm import Session
from typing import Dict, List, Tuple
from uuid import UUID
import logging

from app.models.pipeline import PipelineJob, JobType
from app.models.batch_job_schedule import BatchJobSchedule, JobScheduleStatus
from app.models.maverick import Maverick, DeploymentStatus as MaverickDeploymentStatus
from app.models.progress import MaverickJobProgress, ProgressStatus
from app.models.assessment import AssessmentAttempt

logger = logging.getLogger(__name__)


def check_maverick_deployment_ready(
    db: Session,
    maverick_id: UUID,
    batch_id: UUID,
    pipeline_id: UUID
) -> Tuple[bool, str]:
    """
    Check if a maverick is ready for deployment.
    
    Criteria:
    1. Attended ALL training jobs (marked PRESENT in attendance)
    2. Passed ALL assessment jobs
    
    Returns: (is_ready: bool, reason: str)
    """
    # Get all non-deployment jobs in the pipeline
    all_jobs = db.query(PipelineJob).filter(
        PipelineJob.pipeline_id == pipeline_id,
        PipelineJob.job_type != JobType.DEPLOYMENT
    ).all()
    
    training_jobs = [j for j in all_jobs if j.job_type == JobType.TRAINING]
    assessment_jobs = [j for j in all_jobs if j.job_type == JobType.ASSESSMENT]
    
    # Check training attendance
    for job in training_jobs:
        progress = db.query(MaverickJobProgress).filter(
            MaverickJobProgress.maverick_id == maverick_id,
            MaverickJobProgress.batch_id == batch_id,
            MaverickJobProgress.job_id == job.id
        ).first()
        
        if not progress or progress.status != ProgressStatus.COMPLETED:
            return False, f"Training '{job.name}' not attended or not completed"
    
    # Check assessment passed
    for job in assessment_jobs:
        # Find assessment attempts for this job
        schedule = db.query(BatchJobSchedule).filter(
            BatchJobSchedule.batch_id == batch_id,
            BatchJobSchedule.pipeline_job_id == job.id
        ).first()
        
        if not schedule or not schedule.assessment_id:
            return False, f"Assessment '{job.name}' not scheduled"
        
        attempt = db.query(AssessmentAttempt).filter(
            AssessmentAttempt.assessment_id == schedule.assessment_id,
            AssessmentAttempt.maverick_id == maverick_id,
            AssessmentAttempt.passed == True
        ).first()
        
        if not attempt:
            return False, f"Assessment '{job.name}' not passed"
    
    return True, "Ready for deployment"


def get_deployment_readiness_stats(
    db: Session,
    batch_id: UUID,
    pipeline_id: UUID
) -> Dict:
    """
    Get deployment readiness statistics for a batch.
    
    Returns:
    {
        "ready_count": X,
        "not_ready_count": Y,
        "deployed_count": Z,
        "total_count": N,
        "mavericks": [
            {
                "maverick_id": "...",
                "maverick_name": "...",
                "is_ready": True/False,
                "reason": "...",
                "deployment_status": "DEPLOYED/NOT_DEPLOYED"
            }
        ]
    }
    """
    mavericks = db.query(Maverick).filter(
        Maverick.current_batch_id == batch_id
    ).all()
    
    ready_count = 0
    not_ready_count = 0
    deployed_count = 0
    
    maverick_details = []
    
    for mav in mavericks:
        is_ready, reason = check_maverick_deployment_ready(
            db, mav.id, batch_id, pipeline_id
        )
        
        # Check if already deployed
        deployment_status = mav.deployment_status if mav.deployment_status else MaverickDeploymentStatus.AVAILABLE

        if deployment_status == MaverickDeploymentStatus.DEPLOYED:
            deployed_count += 1
        elif is_ready:
            ready_count += 1
        else:
            not_ready_count += 1
        
        maverick_details.append({
            "maverick_id": str(mav.id),
            "maverick_name": mav.name,
            "is_ready": is_ready,
            "reason": reason,
            "deployment_status": deployment_status.value if deployment_status else "AVAILABLE"
        })
    
    return {
        "ready_count": ready_count,
        "not_ready_count": not_ready_count,
        "deployed_count": deployed_count,
        "total_count": len(mavericks),
        "mavericks": maverick_details
    }


def auto_activate_deployment_job(
    db: Session,
    batch_id: UUID,
    pipeline_id: UUID
) -> bool:
    """
    Auto-activate deployment job if all other jobs are completed.

    Returns True if deployment job was activated, False otherwise.
    """
    logger.info(f"🔍 AUTO-ACTIVATION CHECK: Batch {batch_id}, Pipeline {pipeline_id}")

    # Get the deployment job
    deployment_job = db.query(PipelineJob).filter(
        PipelineJob.pipeline_id == pipeline_id,
        PipelineJob.job_type == JobType.DEPLOYMENT
    ).first()

    if not deployment_job:
        logger.info(f"❌ No deployment job found in pipeline {pipeline_id}")
        return False

    logger.info(f"✅ Found deployment job: '{deployment_job.name}' (ID: {deployment_job.id})")

    # Check if deployment job already has a schedule
    existing_schedule = db.query(BatchJobSchedule).filter(
        BatchJobSchedule.batch_id == batch_id,
        BatchJobSchedule.pipeline_job_id == deployment_job.id
    ).first()

    if existing_schedule:
        logger.info(f"📅 Deployment job already scheduled - Status: {existing_schedule.status}")
        # Already scheduled, just check if we should mark it as in-progress
        if existing_schedule.status == JobScheduleStatus.PENDING:
            # Check if all other jobs are completed
            other_schedules = db.query(BatchJobSchedule).filter(
                BatchJobSchedule.batch_id == batch_id,
                BatchJobSchedule.pipeline_job_id != deployment_job.id
            ).all()

            all_complete = all(s.status == JobScheduleStatus.COMPLETED for s in other_schedules)

            if all_complete and other_schedules:
                existing_schedule.status = JobScheduleStatus.IN_PROGRESS
                db.commit()
                logger.info(f"✅ Deployment job auto-activated for batch {batch_id}")
                return True
        return False

    # No schedule exists - create one if all other jobs are completed
    other_jobs = db.query(PipelineJob).filter(
        PipelineJob.pipeline_id == pipeline_id,
        PipelineJob.job_type != JobType.DEPLOYMENT
    ).all()

    if not other_jobs:
        return False  # No other jobs to check

    # Check if all other jobs have completed schedules
    logger.info(f"📋 Checking {len(other_jobs)} non-deployment jobs for completion...")
    for job in other_jobs:
        schedule = db.query(BatchJobSchedule).filter(
            BatchJobSchedule.batch_id == batch_id,
            BatchJobSchedule.pipeline_job_id == job.id
        ).first()

        if not schedule:
            logger.info(f"❌ Job '{job.name}' (type: {job.job_type}) - NOT SCHEDULED")
            return False

        if schedule.status != JobScheduleStatus.COMPLETED:
            logger.info(f"⏳ Job '{job.name}' (type: {job.job_type}) - Status: {schedule.status} (not completed)")
            return False

        logger.info(f"✅ Job '{job.name}' (type: {job.job_type}) - COMPLETED")

    # All jobs completed - auto-create deployment schedule
    from datetime import datetime, timedelta

    new_schedule = BatchJobSchedule(
        batch_id=batch_id,
        pipeline_job_id=deployment_job.id,
        scheduled_start_date=datetime.utcnow(),
        scheduled_end_date=datetime.utcnow() + timedelta(days=30),
        status=JobScheduleStatus.IN_PROGRESS,
        is_published=True,
        trainer_notes="Auto-activated when all jobs completed"
    )
    db.add(new_schedule)
    db.commit()

    logger.info(f"🚀 Deployment job auto-created and activated for batch {batch_id}")
    return True
