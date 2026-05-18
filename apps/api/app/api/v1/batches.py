"""
Batch Management API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, case, desc
from typing import Optional, List
from uuid import UUID
from datetime import date
import io
import pandas as pd

from app.database import get_db
from app.models.user import User, UserRole
from app.models.batch import Batch, BatchStatus
from app.models.batch_trainer import BatchTrainer
from app.models.maverick import Maverick, DeploymentStatus
from app.models.pipeline import Pipeline
from app.models.assessment import AssessmentAttempt
from app.schemas.batch import (
    BatchCreate,
    BatchUpdate,
    BatchResponse,
    BatchListResponse,
    BatchWithMavericks,
    AssignMaverickRequest,
    BulkAssignRequest,
    AssignmentResponse,
    BulkAssignmentResponse,
    ExcelUploadResponse,
    AssignTrainerRequest,
    AssignMultipleTrainersRequest,
    RemoveTrainerRequest,
    TrainerAssignmentResponse,
    TrainerInfo,
    BatchWithTrainers
)
from app.services.auth import get_current_user, get_hr_user


router = APIRouter()


@router.post("/", response_model=BatchResponse, status_code=status.HTTP_201_CREATED)
async def create_batch(
    batch_data: BatchCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_hr_user)
):
    """
    Create a new training batch

    **Required role**: HR or Super Admin
    **Body**:
    - name: Batch name (required)
    - description: Batch description (optional)
    - pipeline_id: Pipeline UUID (required)
    - start_date: Start date (required)
    - end_date: End date (optional)
    - max_capacity: Maximum enrollments (optional)
    """
    # Verify pipeline exists
    pipeline = db.query(Pipeline).filter(Pipeline.id == batch_data.pipeline_id).first()
    if not pipeline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pipeline not found"
        )

    # Verify trainer exists if provided
    if batch_data.trainer_id:
        from app.models.user import UserRole
        trainer = db.query(User).filter(
            User.id == batch_data.trainer_id,
            User.role == UserRole.TRAINER
        ).first()
        if not trainer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Trainer not found"
            )

        # Check if trainer is already assigned to other active batches
        existing_assignments = db.query(Batch).filter(
            Batch.trainer_id == batch_data.trainer_id,
            Batch.status.in_([BatchStatus.ACTIVE, BatchStatus.PLANNED])
        ).all()

        if existing_assignments:
            batch_names = [b.name for b in existing_assignments]
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Trainer {trainer.name} is already assigned to active batch(es): {', '.join(batch_names)}. Please complete or close those batches first."
            )

    # Create batch
    batch = Batch(
        name=batch_data.name,
        description=batch_data.description,
        pipeline_id=batch_data.pipeline_id,
        trainer_id=batch_data.trainer_id,
        start_date=batch_data.start_date,
        end_date=batch_data.end_date,
        max_capacity=batch_data.max_capacity,
        category=batch_data.category,  # AI matching category
        focus_areas=batch_data.focus_areas,  # Batch focus areas
        required_skills=batch_data.required_skills,  # Required skills
        preferred_skills=batch_data.preferred_skills,  # Preferred skills
        target_role=batch_data.target_role,  # Target job role
        status=BatchStatus.PLANNED,
        current_enrollment=0,
        created_by=current_user.id
    )

    db.add(batch)
    db.commit()
    db.refresh(batch)

    return batch


@router.get("/", response_model=BatchListResponse)
async def list_batches(
    page: int = 1,
    page_size: int = 20,
    status_filter: Optional[str] = None,
    pipeline_id: Optional[UUID] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get list of all batches with filters

    **Required role**: Any authenticated user
    **Query params**:
    - page: Page number (default: 1)
    - page_size: Items per page (default: 20)
    - status_filter: Filter by status (PLANNED, ACTIVE, COMPLETED, CANCELLED)
    - pipeline_id: Filter by pipeline UUID
    - search: Search by name or description
    """
    query = db.query(Batch)

    # Apply filters
    if status_filter:
        try:
            query = query.filter(Batch.status == BatchStatus(status_filter))
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {status_filter}"
            )

    if pipeline_id:
        query = query.filter(Batch.pipeline_id == pipeline_id)

    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (Batch.name.ilike(search_filter)) |
            (Batch.description.ilike(search_filter))
        )

    # Get total count
    total = query.count()

    # Calculate pagination
    total_pages = (total + page_size - 1) // page_size
    offset = (page - 1) * page_size

    # Get paginated results
    batches = query.order_by(Batch.start_date.desc()).offset(offset).limit(page_size).all()

    return BatchListResponse(
        batches=batches,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/top-performers")
async def get_top_performers_by_batch(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_hr_user)
):
    """
    Get top performers by batch

    **Required role**: HR or Super Admin

    Returns the top performer from each of the most recent batches.
    For each batch, shows the maverick with the best assessment performance.

    **Query params**:
    - limit: Number of batches to include (default: 10)

    **Returns**:
    - List of batches with their top performer
    - Performance metrics (pass rate, average score)
    """

    # Get recent active/completed batches
    recent_batches = db.query(Batch).filter(
        Batch.status.in_([BatchStatus.ACTIVE, BatchStatus.COMPLETED])
    ).order_by(Batch.created_at.desc()).limit(limit).all()

    result = []

    for batch in recent_batches:
        # Get all mavericks in this batch with their assessment performance
        maverick_performance = db.query(
            Maverick.id,
            Maverick.name,
            Maverick.email,
            func.count(AssessmentAttempt.id).label('total_attempts'),
            func.sum(case((AssessmentAttempt.passed == True, 1), else_=0)).label('passed_attempts'),
            func.avg(
                (AssessmentAttempt.marks_obtained / AssessmentAttempt.max_marks) * 100
            ).label('avg_percentage')
        ).join(
            AssessmentAttempt, Maverick.id == AssessmentAttempt.maverick_id
        ).filter(
            Maverick.current_batch_id == batch.id
        ).group_by(
            Maverick.id, Maverick.name, Maverick.email
        ).all()

        if not maverick_performance:
            # No assessment data for this batch
            continue

        # Calculate pass rate and score for each maverick
        performers = []
        for mav_id, name, email, total, passed, avg_percentage in maverick_performance:
            pass_rate = (passed / total * 100) if total > 0 else 0
            avg_pct = float(avg_percentage) if avg_percentage else 0

            performers.append({
                "maverick_id": str(mav_id),
                "name": name,
                "email": email,
                "total_attempts": total,
                "passed_attempts": passed,
                "pass_rate": round(pass_rate, 1),
                "avg_score": round(avg_pct, 1),
                # Combined score: 70% pass rate + 30% avg percentage score
                "combined_score": round((pass_rate * 0.7) + (avg_pct * 0.3), 1)
            })

        # Sort by combined score and get top performer
        performers.sort(key=lambda x: x['combined_score'], reverse=True)
        top_performer = performers[0] if performers else None

        if top_performer:
            result.append({
                "batch_id": str(batch.id),
                "batch_name": batch.name,
                "batch_status": batch.status.value,
                "pipeline_id": str(batch.pipeline_id) if batch.pipeline_id else None,
                "start_date": batch.start_date.isoformat() if batch.start_date else None,
                "end_date": batch.end_date.isoformat() if batch.end_date else None,
                "total_enrolled": batch.current_enrollment,
                "top_performer": top_performer
            })

    return {
        "total_batches": len(result),
        "batches": result
    }


@router.get("/{batch_id}", response_model=BatchWithMavericks)
async def get_batch_details(
    batch_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get detailed information about a batch including enrolled mavericks

    **Required role**: Any authenticated user
    **Path params**:
    - batch_id: UUID of the batch
    """
    batch = db.query(Batch).filter(Batch.id == batch_id).first()

    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Batch not found"
        )

    # Get enrolled mavericks
    mavericks = db.query(Maverick).filter(Maverick.current_batch_id == batch_id).all()

    # Convert to dict and add mavericks
    batch_dict = {
        "id": batch.id,
        "name": batch.name,
        "description": batch.description,
        "pipeline_id": batch.pipeline_id,
        "trainer_id": batch.trainer_id,
        "start_date": batch.start_date,
        "end_date": batch.end_date,
        "max_capacity": batch.max_capacity,
        "status": batch.status.value if hasattr(batch.status, 'value') else batch.status,
        "current_enrollment": batch.current_enrollment,
        "created_by": batch.created_by,
        "created_at": batch.created_at,
        "updated_at": batch.updated_at,
        "mavericks": [
            {
                "id": str(m.id),
                "name": m.name,
                "email": m.email,
                "college": m.college,
                "skills": m.skills
            }
            for m in mavericks
        ]
    }

    return batch_dict


@router.patch("/{batch_id}", response_model=BatchResponse)
async def update_batch(
    batch_id: UUID,
    batch_data: BatchUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_hr_user)
):
    """
    Update batch details

    **Required role**: HR or Super Admin
    **Path params**:
    - batch_id: UUID of the batch
    **Body**: Fields to update (all optional)
    """
    batch = db.query(Batch).filter(Batch.id == batch_id).first()

    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Batch not found"
        )

    # Update fields
    if batch_data.name is not None:
        batch.name = batch_data.name
    if batch_data.description is not None:
        batch.description = batch_data.description
    if batch_data.start_date is not None:
        batch.start_date = batch_data.start_date
    if batch_data.end_date is not None:
        batch.end_date = batch_data.end_date
    if batch_data.max_capacity is not None:
        batch.max_capacity = batch_data.max_capacity
    if batch_data.trainer_id is not None:
        # Verify trainer exists
        from app.models.user import UserRole
        trainer = db.query(User).filter(
            User.id == batch_data.trainer_id,
            User.role == UserRole.TRAINER
        ).first()
        if not trainer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Trainer not found"
            )

        # Check if trainer is already assigned to other active batches
        existing_assignments = db.query(Batch).filter(
            Batch.trainer_id == batch_data.trainer_id,
            Batch.id != batch_id,  # Exclude current batch
            Batch.status.in_([BatchStatus.ACTIVE, BatchStatus.PLANNED])
        ).all()

        if existing_assignments:
            batch_names = [b.name for b in existing_assignments]
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Trainer {trainer.name} is already assigned to active batch(es): {', '.join(batch_names)}. Please complete or close those batches first."
            )

        batch.trainer_id = batch_data.trainer_id
    if batch_data.status is not None:
        try:
            batch.status = BatchStatus(batch_data.status)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {batch_data.status}"
            )

    # Update AI matching fields
    if batch_data.category is not None:
        batch.category = batch_data.category
    if batch_data.focus_areas is not None:
        batch.focus_areas = batch_data.focus_areas
    if batch_data.required_skills is not None:
        batch.required_skills = batch_data.required_skills
    if batch_data.preferred_skills is not None:
        batch.preferred_skills = batch_data.preferred_skills
    if batch_data.target_role is not None:
        batch.target_role = batch_data.target_role

    db.commit()
    db.refresh(batch)

    return batch


# ==================== Maverick Assignment Endpoints ====================


@router.post("/{batch_id}/assign", response_model=AssignmentResponse)
async def assign_maverick_to_batch(
    batch_id: UUID,
    request: AssignMaverickRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_hr_user)
):
    """
    Assign a single maverick to a batch

    **Required role**: HR or Super Admin
    **Path params**:
    - batch_id: UUID of the batch
    **Body**:
    - maverick_id: UUID of the maverick
    - notes: Optional assignment notes
    """
    # Get batch
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Batch not found"
        )

    # Check capacity
    if batch.max_capacity and batch.current_enrollment >= batch.max_capacity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Batch is at full capacity ({batch.max_capacity})"
        )

    # Get maverick
    maverick = db.query(Maverick).filter(Maverick.id == request.maverick_id).first()
    if not maverick:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Maverick not found"
        )

    # Check if already assigned
    if maverick.current_batch_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Maverick is already assigned to batch {maverick.current_batch_id}"
        )

    # Assign maverick
    maverick.current_batch_id = batch_id
    maverick.deployment_status = DeploymentStatus.AVAILABLE

    # Update batch enrollment
    batch.current_enrollment += 1

    db.commit()

    return AssignmentResponse(
        success=True,
        maverick_id=request.maverick_id,
        batch_id=batch_id,
        message=f"Maverick {maverick.name} assigned to batch {batch.name}"
    )


@router.post("/{batch_id}/bulk-assign", response_model=BulkAssignmentResponse)
async def bulk_assign_mavericks(
    batch_id: UUID,
    request: BulkAssignRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_hr_user)
):
    """
    Assign multiple mavericks to a batch at once

    **Required role**: HR or Super Admin
    **Path params**:
    - batch_id: UUID of the batch
    **Body**:
    - maverick_ids: List of maverick UUIDs
    - notes: Optional common notes
    """
    # Get batch
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Batch not found"
        )

    results = []
    success_count = 0
    failed_count = 0

    for maverick_id in request.maverick_ids:
        try:
            # Check capacity
            if batch.max_capacity and batch.current_enrollment >= batch.max_capacity:
                results.append(AssignmentResponse(
                    success=False,
                    maverick_id=maverick_id,
                    batch_id=batch_id,
                    message="Batch at full capacity"
                ))
                failed_count += 1
                continue

            # Get maverick
            maverick = db.query(Maverick).filter(Maverick.id == maverick_id).first()
            if not maverick:
                results.append(AssignmentResponse(
                    success=False,
                    maverick_id=maverick_id,
                    batch_id=batch_id,
                    message="Maverick not found"
                ))
                failed_count += 1
                continue

            # Check if already assigned
            if maverick.current_batch_id:
                results.append(AssignmentResponse(
                    success=False,
                    maverick_id=maverick_id,
                    batch_id=batch_id,
                    message="Already assigned to another batch"
                ))
                failed_count += 1
                continue

            # Assign
            maverick.current_batch_id = batch_id
            maverick.deployment_status = DeploymentStatus.AVAILABLE
            batch.current_enrollment += 1

            results.append(AssignmentResponse(
                success=True,
                maverick_id=maverick_id,
                batch_id=batch_id,
                message=f"{maverick.name} assigned successfully"
            ))
            success_count += 1

        except Exception as e:
            results.append(AssignmentResponse(
                success=False,
                maverick_id=maverick_id,
                batch_id=batch_id,
                message=str(e)
            ))
            failed_count += 1

    db.commit()

    return BulkAssignmentResponse(
        success_count=success_count,
        failed_count=failed_count,
        results=results
    )


# ==================== Excel Upload/Download Endpoints ====================


@router.get("/{batch_id}/template/excel")
async def download_excel_template(
    batch_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_hr_user)
):
    """
    Generate and download Excel template for bulk maverick assignment

    **Required role**: HR or Super Admin
    **Path params**:
    - batch_id: UUID of the batch

    Returns an Excel file with:
    - Instructions sheet
    - Template sheet with maverick data
    """
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Batch not found"
        )

    # Get available mavericks (approved and not assigned)
    mavericks = db.query(Maverick).filter(
        Maverick.profile_status == "approved",
        Maverick.current_batch_id == None
    ).all()

    # Create Excel file
    output = io.BytesIO()

    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Instructions sheet
        instructions_df = pd.DataFrame({
            'Instructions': [
                f'Bulk Assignment Template for Batch: {batch.name}',
                '',
                'HOW TO USE:',
                '1. Go to the "Mavericks" sheet',
                '2. Mark "Yes" in the "Assign" column for mavericks you want to assign',
                '3. Save the file',
                '4. Upload it using the bulk upload API',
                '',
                'NOTES:',
                '- Only mavericks with "Yes" in Assign column will be assigned',
                '- Do not modify the Maverick_ID column',
                f'- Batch capacity: {batch.max_capacity or "Unlimited"}',
                f'- Current enrollment: {batch.current_enrollment}',
            ]
        })
        instructions_df.to_excel(writer, sheet_name='Instructions', index=False)

        # Mavericks sheet
        mavericks_data = []
        for m in mavericks:
            mavericks_data.append({
                'Maverick_ID': str(m.id),
                'Name': m.name,
                'Email': m.email,
                'College': m.college or '',
                'Skills': ', '.join(m.skills) if m.skills else '',
                'CGPA': m.cgpa or '',
                'Assign': 'No'  # Default value
            })

        mavericks_df = pd.DataFrame(mavericks_data)
        mavericks_df.to_excel(writer, sheet_name='Mavericks', index=False)

    output.seek(0)

    filename = f"batch_assignment_template_{batch.name.replace(' ', '_')}.xlsx"

    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.post("/{batch_id}/upload/excel", response_model=ExcelUploadResponse)
async def upload_excel_assignments(
    batch_id: UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_hr_user)
):
    """
    Bulk assign mavericks using Excel upload

    **Required role**: HR or Super Admin
    **Path params**:
    - batch_id: UUID of the batch
    **Body**:
    - file: Excel file (use template from /template/excel endpoint)

    Expected Excel format:
    - Sheet named "Mavericks"
    - Columns: Maverick_ID, Name, Email, College, Skills, CGPA, Assign
    - Only rows with Assign="Yes" will be processed
    """
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Batch not found"
        )

    # Read Excel file
    try:
        contents = await file.read()
        df = pd.read_excel(io.BytesIO(contents), sheet_name='Mavericks')
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error reading Excel file: {str(e)}"
        )

    # Validate required columns
    required_columns = ['Maverick_ID', 'Assign']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Missing required columns: {', '.join(missing_columns)}"
        )

    # Filter rows where Assign = "Yes"
    to_assign = df[df['Assign'].str.upper() == 'YES']

    total_rows = len(to_assign)
    success_count = 0
    failed_count = 0
    errors = []

    for idx, row in to_assign.iterrows():
        try:
            maverick_id = row['Maverick_ID']

            # Check capacity
            if batch.max_capacity and batch.current_enrollment >= batch.max_capacity:
                errors.append({
                    "row": int(idx) + 2,  # Excel row number (1-indexed + header)
                    "maverick_id": maverick_id,
                    "error": "Batch at full capacity"
                })
                failed_count += 1
                continue

            # Get maverick
            maverick = db.query(Maverick).filter(Maverick.id == maverick_id).first()
            if not maverick:
                errors.append({
                    "row": int(idx) + 2,
                    "maverick_id": maverick_id,
                    "error": "Maverick not found"
                })
                failed_count += 1
                continue

            # Check if already assigned
            if maverick.current_batch_id:
                errors.append({
                    "row": int(idx) + 2,
                    "maverick_id": maverick_id,
                    "error": "Already assigned to another batch"
                })
                failed_count += 1
                continue

            # Assign
            maverick.current_batch_id = batch_id
            maverick.deployment_status = DeploymentStatus.AVAILABLE
            batch.current_enrollment += 1
            success_count += 1

        except Exception as e:
            errors.append({
                "row": int(idx) + 2,
                "maverick_id": str(maverick_id) if 'maverick_id' in locals() else "Unknown",
                "error": str(e)
            })
            failed_count += 1

    db.commit()

    return ExcelUploadResponse(
        success_count=success_count,
        failed_count=failed_count,
        total_rows=total_rows,
        errors=errors,
        message=f"Processed {total_rows} rows: {success_count} successful, {failed_count} failed"
    )



# ===== MULTIPLE TRAINER MANAGEMENT ENDPOINTS =====

@router.get("/{batch_id}/trainers", response_model=List[TrainerInfo])
async def get_batch_trainers(
    batch_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all trainers assigned to a batch

    **Required role**: Any authenticated user
    """
    # Verify batch exists
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Batch not found"
        )

    # Get all trainer assignments
    assignments = db.query(BatchTrainer).filter(
        BatchTrainer.batch_id == batch_id
    ).all()

    trainers = []
    for assignment in assignments:
        trainer = db.query(User).filter(User.id == assignment.trainer_id).first()
        if trainer:
            trainers.append(TrainerInfo(
                user_id=trainer.id,
                name=trainer.name,
                email=trainer.email,
                is_lead=assignment.is_lead_trainer,
                assigned_at=assignment.assigned_at
            ))

    return trainers


@router.post("/{batch_id}/trainers/assign", response_model=TrainerAssignmentResponse)
async def assign_trainer_to_batch(
    batch_id: UUID,
    request: AssignTrainerRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_hr_user)
):
    """
    Assign a trainer to a batch

    **Required role**: HR or Super Admin
    **Body**:
    - trainer_id: UUID of the trainer
    - is_lead_trainer: Mark as lead trainer (default: false)
    """
    # Verify batch exists
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Batch not found"
        )

    # Verify trainer exists and is a trainer
    trainer = db.query(User).filter(
        User.id == request.trainer_id,
        User.role == UserRole.TRAINER
    ).first()
    if not trainer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trainer not found or user is not a trainer"
        )

    # Check if already assigned
    existing = db.query(BatchTrainer).filter(
        BatchTrainer.batch_id == batch_id,
        BatchTrainer.trainer_id == request.trainer_id
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Trainer {trainer.name} is already assigned to this batch"
        )

    # If marking as lead, remove lead status from others
    if request.is_lead_trainer:
        db.query(BatchTrainer).filter(
            BatchTrainer.batch_id == batch_id,
            BatchTrainer.is_lead_trainer == True
        ).update({"is_lead_trainer": False})

    # Create assignment
    assignment = BatchTrainer(
        batch_id=batch_id,
        trainer_id=request.trainer_id,
        is_lead_trainer=request.is_lead_trainer,
        assigned_by=current_user.id
    )
    db.add(assignment)

    # Also update the legacy trainer_id field if this is the lead
    if request.is_lead_trainer:
        batch.trainer_id = request.trainer_id

    db.commit()

    return TrainerAssignmentResponse(
        success=True,
        batch_id=batch_id,
        trainer_id=request.trainer_id,
        is_lead=request.is_lead_trainer,
        message=f"Trainer {trainer.name} assigned successfully"
    )


@router.post("/{batch_id}/trainers/assign-multiple", response_model=dict)
async def assign_multiple_trainers(
    batch_id: UUID,
    request: AssignMultipleTrainersRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_hr_user)
):
    """
    Assign multiple trainers to a batch at once

    **Required role**: HR or Super Admin
    **Body**:
    - trainer_ids: List of trainer UUIDs
    - lead_trainer_id: Optional UUID of the lead trainer
    """
    # Verify batch exists
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Batch not found"
        )

    success_count = 0
    failed_count = 0
    messages = []

    for trainer_id in request.trainer_ids:
        try:
            # Verify trainer
            trainer = db.query(User).filter(
                User.id == trainer_id,
                User.role == UserRole.TRAINER
            ).first()

            if not trainer:
                messages.append(f"Trainer {trainer_id} not found")
                failed_count += 1
                continue

            # Check if already assigned
            existing = db.query(BatchTrainer).filter(
                BatchTrainer.batch_id == batch_id,
                BatchTrainer.trainer_id == trainer_id
            ).first()

            if existing:
                messages.append(f"{trainer.name} already assigned")
                failed_count += 1
                continue

            # Determine if this is the lead
            is_lead = (request.lead_trainer_id == trainer_id)

            # If marking as lead, remove lead status from others
            if is_lead:
                db.query(BatchTrainer).filter(
                    BatchTrainer.batch_id == batch_id,
                    BatchTrainer.is_lead_trainer == True
                ).update({"is_lead_trainer": False})

            # Create assignment
            assignment = BatchTrainer(
                batch_id=batch_id,
                trainer_id=trainer_id,
                is_lead_trainer=is_lead,
                assigned_by=current_user.id
            )
            db.add(assignment)

            # Update legacy field if lead
            if is_lead:
                batch.trainer_id = trainer_id

            messages.append(f"{trainer.name} assigned successfully")
            success_count += 1

        except Exception as e:
            messages.append(f"Error assigning {trainer_id}: {str(e)}")
            failed_count += 1

    db.commit()

    return {
        "success_count": success_count,
        "failed_count": failed_count,
        "total": len(request.trainer_ids),
        "messages": messages
    }


@router.delete("/{batch_id}/trainers/{trainer_id}", response_model=dict)
async def remove_trainer_from_batch(
    batch_id: UUID,
    trainer_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_hr_user)
):
    """
    Remove a trainer from a batch

    **Required role**: HR or Super Admin
    """
    # Verify batch exists
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Batch not found"
        )

    # Find assignment
    assignment = db.query(BatchTrainer).filter(
        BatchTrainer.batch_id == batch_id,
        BatchTrainer.trainer_id == trainer_id
    ).first()

    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trainer is not assigned to this batch"
        )

    was_lead = assignment.is_lead_trainer

    # Remove assignment
    db.delete(assignment)

    # If this was the lead, clear the legacy field
    if was_lead and batch.trainer_id == trainer_id:
        # Assign another trainer as lead if any exist
        other_assignment = db.query(BatchTrainer).filter(
            BatchTrainer.batch_id == batch_id
        ).first()

        if other_assignment:
            other_assignment.is_lead_trainer = True
            batch.trainer_id = other_assignment.trainer_id
        else:
            batch.trainer_id = None

    db.commit()

    return {
        "success": True,
        "message": "Trainer removed successfully",
        "was_lead": was_lead
    }


@router.patch("/{batch_id}/trainers/{trainer_id}/make-lead", response_model=TrainerAssignmentResponse)
async def make_trainer_lead(
    batch_id: UUID,
    trainer_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_hr_user)
):
    """
    Make a trainer the lead trainer for a batch

    **Required role**: HR or Super Admin
    """
    # Verify batch exists
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Batch not found"
        )

    # Find assignment
    assignment = db.query(BatchTrainer).filter(
        BatchTrainer.batch_id == batch_id,
        BatchTrainer.trainer_id == trainer_id
    ).first()

    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trainer is not assigned to this batch"
        )

    # Remove lead status from all others
    db.query(BatchTrainer).filter(
        BatchTrainer.batch_id == batch_id,
        BatchTrainer.is_lead_trainer == True
    ).update({"is_lead_trainer": False})

    # Make this one lead
    assignment.is_lead_trainer = True
    batch.trainer_id = trainer_id

    db.commit()

    trainer = db.query(User).filter(User.id == trainer_id).first()

    return TrainerAssignmentResponse(
        success=True,
        batch_id=batch_id,
        trainer_id=trainer_id,
        is_lead=True,
        message=f"{trainer.name if trainer else 'Trainer'} is now the lead trainer"
    )


# ==================== Batch Leaderboard ====================


@router.get("/{batch_id}/leaderboard")
async def get_batch_leaderboard(
    batch_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get leaderboard for a batch showing maverick rankings

    **Required role**: Any authenticated user (HR, Trainer, Student)
    **Path params**:
    - batch_id: UUID of the batch

    Returns rankings based purely on assessment performance:
    - Average assessment scores
    - Pass rate
    - Total assessments completed
    """

    # Verify batch exists
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Batch not found"
        )

    # Get pipeline and trainer info
    pipeline = db.query(Pipeline).filter(Pipeline.id == batch.pipeline_id).first() if batch.pipeline_id else None
    trainer = db.query(User).filter(User.id == batch.trainer_id).first() if batch.trainer_id else None

    # Get all mavericks in this batch
    batch_mavericks = db.query(Maverick).filter(
        Maverick.current_batch_id == batch_id
    ).all()

    # Calculate performance metrics for each maverick
    performance_data = []

    for maverick in batch_mavericks:
        # Calculate average assessment score
        assessments = db.query(AssessmentAttempt).filter(
            AssessmentAttempt.maverick_id == maverick.id,
            AssessmentAttempt.batch_id == batch_id
        ).all()

        if assessments:
            total_score = sum(
                (float(a.marks_obtained) / float(a.max_marks) * 100)
                for a in assessments if a.max_marks > 0
            )
            avg_score = total_score / len(assessments)
            passed_count = sum(1 for a in assessments if a.passed)
            total_assessments = len(assessments)
        else:
            avg_score = 0
            passed_count = 0
            total_assessments = 0

        # Calculate pass rate
        pass_rate = (passed_count / total_assessments * 100) if total_assessments > 0 else 0

        # Calculate combined score for ranking based purely on assessments
        # 60% average score + 40% pass rate
        combined_score = (avg_score * 0.6) + (pass_rate * 0.4)

        performance_data.append({
            "id": str(maverick.id),
            "name": maverick.name,
            "email": maverick.email,
            "average_score": round(avg_score, 2),
            "total_assessments": total_assessments,
            "passed_count": passed_count,
            "combined_score": combined_score
        })

    # Sort by combined score (descending) and assign ranks
    performance_data.sort(key=lambda x: x["combined_score"], reverse=True)

    for rank, data in enumerate(performance_data, 1):
        data["rank"] = rank
        # Remove combined_score from response (internal use only)
        del data["combined_score"]

    return {
        "batch_id": str(batch.id),
        "batch_name": batch.name,
        "pipeline_name": pipeline.name if pipeline else "Unknown Pipeline",
        "trainer_name": trainer.name if trainer else "No Trainer Assigned",
        "start_date": batch.start_date.isoformat() if batch.start_date else None,
        "total_students": len(batch_mavericks),
        "batch_mates": performance_data
    }
