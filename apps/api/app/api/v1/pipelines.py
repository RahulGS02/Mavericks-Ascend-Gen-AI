"""
Pipeline Management API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
from uuid import UUID

from app.database import get_db
from app.models.user import User
from app.models.pipeline import Pipeline, PipelineJob, PipelineStatus, JobStatus, JobType
from app.schemas.pipeline import (
    PipelineCreate,
    PipelineUpdate,
    PipelineResponse,
    PipelineListResponse,
    PipelineWithStats,
    JobCreate,
    JobUpdate,
    JobResponse,
    AddJobsToPipelineRequest,
    ReorderJobsRequest,
    DeletePipelineResponse
)
from app.services.auth import get_current_user, get_hr_user


router = APIRouter()


# ==================== Template Routes (must come BEFORE /{pipeline_id}) ====================


@router.get("/templates", response_model=PipelineListResponse)
async def list_pipeline_templates(
    page: int = 1,
    page_size: int = 20,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all pipeline templates

    **Required role**: Any authenticated user
    **Query params**:
    - page: Page number (default: 1)
    - page_size: Items per page (default: 20)
    - search: Search by name or description

    Returns only pipelines marked as templates.
    """
    query = db.query(Pipeline).filter(Pipeline.is_template == True)

    # Apply search filter
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (Pipeline.name.ilike(search_filter)) |
            (Pipeline.description.ilike(search_filter))
        )

    # Get total count
    total = query.count()

    # Calculate pagination
    total_pages = (total + page_size - 1) // page_size
    offset = (page - 1) * page_size

    # Get paginated results
    pipelines = query.order_by(Pipeline.created_at.desc()).offset(offset).limit(page_size).all()

    return PipelineListResponse(
        pipelines=pipelines,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.post("/templates/{template_id}/create-from", response_model=PipelineResponse, status_code=status.HTTP_201_CREATED)
async def create_pipeline_from_template(
    template_id: UUID,
    new_name: str,
    description: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_hr_user)
):
    """
    Create a new pipeline from a template

    **Required role**: HR or Super Admin
    **Path params**:
    - template_id: UUID of the template pipeline
    **Query params**:
    - new_name: Name for the new pipeline (required)
    - description: Optional description (inherits from template if not provided)

    Creates a new DRAFT pipeline with all jobs from the template.
    """
    # Get template
    template = db.query(Pipeline).filter(
        Pipeline.id == template_id,
        Pipeline.is_template == True
    ).first()

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found or pipeline is not marked as template"
        )

    # Create new pipeline from template
    new_pipeline = Pipeline(
        name=new_name,
        description=description or template.description,
        status=PipelineStatus.DRAFT,
        created_by=current_user.id,
        is_template=False
    )

    db.add(new_pipeline)
    db.flush()

    # Copy all jobs from template
    template_jobs = db.query(PipelineJob).filter(
        PipelineJob.pipeline_id == template_id
    ).order_by(PipelineJob.sequence_order).all()

    for template_job in template_jobs:
        new_job = PipelineJob(
            pipeline_id=new_pipeline.id,
            name=template_job.name,
            description=template_job.description,
            job_type=template_job.job_type,
            sequence_order=template_job.sequence_order,
            duration_days=template_job.duration_days,
            prerequisites=template_job.prerequisites,
            is_mandatory=template_job.is_mandatory,
            status=JobStatus.PENDING,
            job_metadata=template_job.job_metadata
        )
        db.add(new_job)

    db.commit()
    db.refresh(new_pipeline)

    return new_pipeline


# ==================== Standard Pipeline CRUD ====================


@router.post("/", response_model=PipelineResponse, status_code=status.HTTP_201_CREATED)
async def create_pipeline(
    pipeline_data: PipelineCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_hr_user)
):
    """
    Create a new pipeline with optional initial jobs

    **Required role**: HR or Super Admin
    **Body**:
    - name: Pipeline name (required)
    - description: Pipeline description (optional)
    - status: Pipeline status (default: DRAFT)
    - jobs: List of initial jobs (optional)
    """
    # Create pipeline
    pipeline = Pipeline(
        name=pipeline_data.name,
        description=pipeline_data.description,
        status=PipelineStatus(pipeline_data.status) if pipeline_data.status else PipelineStatus.DRAFT,
        created_by=current_user.id
    )
    
    db.add(pipeline)
    db.flush()  # Get pipeline ID
    
    # Add initial jobs if provided
    if pipeline_data.jobs:
        for job_data in pipeline_data.jobs:
            job = PipelineJob(
                pipeline_id=pipeline.id,
                name=job_data.name,
                description=job_data.description,
                job_type=JobType(job_data.job_type),
                sequence_order=job_data.sequence_order,
                duration_days=job_data.duration_days,
                prerequisites=job_data.prerequisites,
                status=JobStatus.PENDING
            )
            db.add(job)
    
    db.commit()
    db.refresh(pipeline)
    
    return pipeline


@router.get("/", response_model=PipelineListResponse)
async def list_pipelines(
    page: int = 1,
    page_size: int = 20,
    status_filter: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get list of all pipelines with pagination
    
    **Required role**: Any authenticated user
    **Query params**:
    - page: Page number (default: 1)
    - page_size: Items per page (default: 20)
    - status_filter: Filter by status (DRAFT, ACTIVE, COMPLETED, ARCHIVED)
    - search: Search by name or description
    """
    query = db.query(Pipeline)
    
    # Apply status filter
    if status_filter:
        try:
            query = query.filter(Pipeline.status == PipelineStatus(status_filter))
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {status_filter}"
            )
    
    # Apply search filter
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (Pipeline.name.ilike(search_filter)) |
            (Pipeline.description.ilike(search_filter))
        )
    
    # Get total count
    total = query.count()
    
    # Calculate pagination
    total_pages = (total + page_size - 1) // page_size
    offset = (page - 1) * page_size
    
    # Get paginated results
    pipelines = query.order_by(Pipeline.created_at.desc()).offset(offset).limit(page_size).all()
    
    return PipelineListResponse(
        pipelines=pipelines,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/{pipeline_id}", response_model=PipelineResponse)
async def get_pipeline(
    pipeline_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific pipeline by ID with all its jobs
    
    **Required role**: Any authenticated user
    **Path params**:
    - pipeline_id: UUID of the pipeline
    """
    pipeline = db.query(Pipeline).filter(Pipeline.id == pipeline_id).first()
    
    if not pipeline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pipeline not found"
        )
    
    return pipeline


@router.patch("/{pipeline_id}", response_model=PipelineResponse)
async def update_pipeline(
    pipeline_id: UUID,
    pipeline_data: PipelineUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a pipeline's details

    **Required role**: Any authenticated user
    **Path params**:
    - pipeline_id: UUID of the pipeline
    **Body**: Fields to update (all optional)
    - name: New pipeline name
    - description: New description
    - status: New status (DRAFT, ACTIVE, COMPLETED, ARCHIVED)
    """
    pipeline = db.query(Pipeline).filter(Pipeline.id == pipeline_id).first()

    if not pipeline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pipeline not found"
        )

    # Update fields
    if pipeline_data.name is not None:
        pipeline.name = pipeline_data.name
    if pipeline_data.description is not None:
        pipeline.description = pipeline_data.description
    if pipeline_data.status is not None:
        try:
            pipeline.status = PipelineStatus(pipeline_data.status)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {pipeline_data.status}"
            )

    db.commit()
    db.refresh(pipeline)

    return pipeline


@router.delete("/{pipeline_id}", response_model=DeletePipelineResponse)
async def delete_pipeline(
    pipeline_id: UUID,
    force: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a pipeline (with constraints)

    **Required role**: Any authenticated user
    **Path params**:
    - pipeline_id: UUID of the pipeline
    **Query params**:
    - force: Force delete even if pipeline has active jobs (default: False)

    **Constraints**:
    - Cannot delete ACTIVE pipelines unless force=True
    - Deletes all associated jobs
    """
    pipeline = db.query(Pipeline).filter(Pipeline.id == pipeline_id).first()

    if not pipeline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pipeline not found"
        )

    # Check constraints
    if pipeline.status == PipelineStatus.ACTIVE and not force:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete ACTIVE pipeline. Set status to ARCHIVED first or use force=True"
        )

    # Count jobs before deletion
    jobs_count = db.query(PipelineJob).filter(PipelineJob.pipeline_id == pipeline_id).count()

    # Delete all associated jobs first
    db.query(PipelineJob).filter(PipelineJob.pipeline_id == pipeline_id).delete()

    # Delete pipeline
    db.delete(pipeline)
    db.commit()

    return DeletePipelineResponse(
        success=True,
        message=f"Pipeline '{pipeline.name}' deleted successfully",
        deleted_pipeline_id=pipeline_id,
        deleted_jobs_count=jobs_count
    )


# ==================== Job Management Endpoints ====================


@router.post("/{pipeline_id}/jobs", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def add_job_to_pipeline(
    pipeline_id: UUID,
    job_data: JobCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Add a new job to a pipeline

    **Required role**: Any authenticated user
    **Path params**:
    - pipeline_id: UUID of the pipeline
    **Body**:
    - name: Job name (required)
    - job_type: Job type - TRAINING, ASSESSMENT, or DEPLOYMENT (required)
    - sequence_order: Order in pipeline (required)
    - duration_days: Estimated duration (optional)
    - description: Job description (optional)
    - prerequisites: Prerequisites (optional)
    """
    # Verify pipeline exists
    pipeline = db.query(Pipeline).filter(Pipeline.id == pipeline_id).first()
    if not pipeline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pipeline not found"
        )

    # Create job
    try:
        job = PipelineJob(
            pipeline_id=pipeline_id,
            name=job_data.name,
            description=job_data.description,
            job_type=JobType(job_data.job_type),
            sequence_order=job_data.sequence_order,
            duration_days=job_data.duration_days,
            prerequisites=job_data.prerequisites,
            job_metadata=job_data.metadata,  # Store metadata (e.g., skills_tested)
            status=JobStatus.PENDING
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid job_type: {job_data.job_type}. Must be TRAINING, ASSESSMENT, or DEPLOYMENT"
        )

    db.add(job)
    db.commit()
    db.refresh(job)

    return job


@router.post("/{pipeline_id}/jobs/bulk", response_model=List[JobResponse])
async def add_multiple_jobs(
    pipeline_id: UUID,
    request: AddJobsToPipelineRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Add multiple jobs to a pipeline at once

    **Required role**: Any authenticated user
    **Path params**:
    - pipeline_id: UUID of the pipeline
    **Body**:
    - jobs: List of job data
    """
    # Verify pipeline exists
    pipeline = db.query(Pipeline).filter(Pipeline.id == pipeline_id).first()
    if not pipeline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pipeline not found"
        )

    created_jobs = []

    for job_data in request.jobs:
        try:
            job = PipelineJob(
                pipeline_id=pipeline_id,
                name=job_data.name,
                description=job_data.description,
                job_type=JobType(job_data.job_type),
                sequence_order=job_data.sequence_order,
                duration_days=job_data.duration_days,
                prerequisites=job_data.prerequisites,
                status=JobStatus.PENDING
            )
            db.add(job)
            created_jobs.append(job)
        except ValueError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid job data: {str(e)}"
            )

    db.commit()

    for job in created_jobs:
        db.refresh(job)

    return created_jobs


@router.patch("/{pipeline_id}/jobs/{job_id}", response_model=JobResponse)
async def update_job(
    pipeline_id: UUID,
    job_id: UUID,
    job_data: JobUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a job in a pipeline

    **Required role**: Any authenticated user
    **Path params**:
    - pipeline_id: UUID of the pipeline
    - job_id: UUID of the job
    **Body**: Fields to update (all optional)
    """
    job = db.query(PipelineJob).filter(
        PipelineJob.id == job_id,
        PipelineJob.pipeline_id == pipeline_id
    ).first()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found in this pipeline"
        )

    # Update fields
    if job_data.name is not None:
        job.name = job_data.name
    if job_data.description is not None:
        job.description = job_data.description
    if job_data.job_type is not None:
        try:
            job.job_type = JobType(job_data.job_type)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid job_type: {job_data.job_type}"
            )
    if job_data.sequence_order is not None:
        job.sequence_order = job_data.sequence_order
    if job_data.duration_days is not None:
        job.duration_days = job_data.duration_days
    if job_data.prerequisites is not None:
        job.prerequisites = job_data.prerequisites

    db.commit()
    db.refresh(job)

    return job


@router.delete("/{pipeline_id}/jobs/{job_id}")
async def delete_job(
    pipeline_id: UUID,
    job_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a job from a pipeline

    **Required role**: Any authenticated user
    **Path params**:
    - pipeline_id: UUID of the pipeline
    - job_id: UUID of the job
    """
    job = db.query(PipelineJob).filter(
        PipelineJob.id == job_id,
        PipelineJob.pipeline_id == pipeline_id
    ).first()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found in this pipeline"
        )

    job_name = job.name
    db.delete(job)
    db.commit()

    return {
        "success": True,
        "message": f"Job '{job_name}' deleted successfully",
        "deleted_job_id": str(job_id)
    }


@router.post("/{pipeline_id}/jobs/reorder")
async def reorder_jobs(
    pipeline_id: UUID,
    request: ReorderJobsRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Reorder jobs in a pipeline

    **Required role**: Any authenticated user
    **Path params**:
    - pipeline_id: UUID of the pipeline
    **Body**:
    - job_orders: List of {job_id, sequence_order} mappings
    """
    # Verify pipeline exists
    pipeline = db.query(Pipeline).filter(Pipeline.id == pipeline_id).first()
    if not pipeline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pipeline not found"
        )

    # Update sequence orders
    for item in request.job_orders:
        job_id = item.get("job_id")
        sequence_order = item.get("sequence_order")

        if not job_id or sequence_order is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Each item must have job_id and sequence_order"
            )

        job = db.query(PipelineJob).filter(
            PipelineJob.id == job_id,
            PipelineJob.pipeline_id == pipeline_id
        ).first()

        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job {job_id} not found in pipeline"
            )

        job.sequence_order = sequence_order

    db.commit()

    # Return updated jobs
    jobs = db.query(PipelineJob).filter(
        PipelineJob.pipeline_id == pipeline_id
    ).order_by(PipelineJob.sequence_order).all()

    return {
        "success": True,
        "message": "Jobs reordered successfully",
        "jobs": jobs
    }


# ==================== Pipeline Cloning & Template Endpoints ====================


@router.post("/{pipeline_id}/clone", response_model=PipelineResponse, status_code=status.HTTP_201_CREATED)
async def clone_pipeline(
    pipeline_id: UUID,
    new_name: Optional[str] = None,
    include_jobs: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_hr_user)
):
    """
    Clone an existing pipeline

    **Required role**: HR or Super Admin
    **Path params**:
    - pipeline_id: UUID of the pipeline to clone
    **Query params**:
    - new_name: Optional new name for cloned pipeline (defaults to "Copy of [original name]")
    - include_jobs: Whether to clone all jobs (default: True)

    Creates a new pipeline with DRAFT status and copies all jobs if specified.
    """
    # Get source pipeline
    source_pipeline = db.query(Pipeline).filter(Pipeline.id == pipeline_id).first()

    if not source_pipeline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Source pipeline not found"
        )

    # Create cloned pipeline name
    cloned_name = new_name or f"Copy of {source_pipeline.name}"

    # Create new pipeline
    cloned_pipeline = Pipeline(
        name=cloned_name,
        description=source_pipeline.description,
        status=PipelineStatus.DRAFT,
        created_by=current_user.id,
        is_template=False  # Clones are not templates by default
    )

    db.add(cloned_pipeline)
    db.flush()  # Get the new pipeline ID

    # Clone jobs if requested
    if include_jobs:
        source_jobs = db.query(PipelineJob).filter(
            PipelineJob.pipeline_id == pipeline_id
        ).order_by(PipelineJob.sequence_order).all()

        for source_job in source_jobs:
            cloned_job = PipelineJob(
                pipeline_id=cloned_pipeline.id,
                name=source_job.name,
                description=source_job.description,
                job_type=source_job.job_type,
                sequence_order=source_job.sequence_order,
                duration_days=source_job.duration_days,
                prerequisites=source_job.prerequisites,
                is_mandatory=source_job.is_mandatory,
                status=JobStatus.PENDING,
                job_metadata=source_job.job_metadata
            )
            db.add(cloned_job)

    db.commit()
    db.refresh(cloned_pipeline)

    return cloned_pipeline


@router.patch("/{pipeline_id}/mark-template", response_model=PipelineResponse)
async def mark_as_template(
    pipeline_id: UUID,
    is_template: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_hr_user)
):
    """
    Mark or unmark a pipeline as a template

    **Required role**: HR or Super Admin
    **Path params**:
    - pipeline_id: UUID of the pipeline
    **Query params**:
    - is_template: True to mark as template, False to unmark (default: True)

    Templates can be used to quickly create new pipelines with standard job structures.
    """
    pipeline = db.query(Pipeline).filter(Pipeline.id == pipeline_id).first()

    if not pipeline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pipeline not found"
        )

    # Update template status
    pipeline.is_template = is_template

    # If marking as template, suggest archiving if active
    if is_template and pipeline.status == PipelineStatus.ACTIVE:
        # Just log a warning, don't force change
        print(f"⚠️  Warning: Pipeline {pipeline.name} is ACTIVE and being marked as template")

    db.commit()
    db.refresh(pipeline)

    return pipeline





@router.patch("/{pipeline_id}/modify-active")
async def modify_active_pipeline(
    pipeline_id: UUID,
    force: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_hr_user)
):
    """
    Check if an ACTIVE pipeline can be modified (with warnings)

    **Required role**: HR or Super Admin
    **Path params**:
    - pipeline_id: UUID of the pipeline
    **Query params**:
    - force: Force modification even with warnings (default: False)

    **Returns warnings about:**
    - Active batches using this pipeline
    - Number of mavericks enrolled
    - Ongoing jobs

    This is a safety check endpoint - actual modifications happen via PATCH /pipelines/{id}
    """
    pipeline = db.query(Pipeline).filter(Pipeline.id == pipeline_id).first()

    if not pipeline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pipeline not found"
        )

    if pipeline.status != PipelineStatus.ACTIVE:
        return {
            "can_modify": True,
            "warnings": [],
            "message": "Pipeline is not ACTIVE, safe to modify"
        }

    # Check for active batches (simplified - you'd query batches table in production)
    warnings = []

    # Count jobs in progress
    in_progress_jobs = db.query(PipelineJob).filter(
        PipelineJob.pipeline_id == pipeline_id,
        PipelineJob.status == JobStatus.IN_PROGRESS
    ).count()

    if in_progress_jobs > 0:
        warnings.append(f"{in_progress_jobs} jobs are currently in progress")

    # Check total jobs
    total_jobs = db.query(PipelineJob).filter(
        PipelineJob.pipeline_id == pipeline_id
    ).count()

    warnings.append(f"Pipeline has {total_jobs} jobs that may be affected")

    # Warning about active status
    warnings.append("Pipeline is ACTIVE - modifications may affect ongoing training")

    if warnings and not force:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "can_modify": False,
                "warnings": warnings,
                "message": "Pipeline has active dependencies. Use force=True to override.",
                "recommendation": "Consider cloning this pipeline instead or setting status to DRAFT first"
            }
        )

    return {
        "can_modify": True,
        "warnings": warnings,
        "message": "Modification allowed (force=True)" if force else "Safe to modify",
        "recommendation": "Clone pipeline to preserve original if changes are significant"
    }
