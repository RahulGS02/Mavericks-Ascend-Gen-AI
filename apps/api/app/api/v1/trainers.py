"""
Trainer Management API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from uuid import UUID
import secrets
import string

from app.database import get_db
from app.models.user import User, UserRole
from app.models.batch import Batch
from app.models.progress import MaverickJobProgress, ProgressStatus
from app.models.maverick import Maverick
from app.schemas.trainer import (
    TrainerCreate,
    TrainerResponse,
    TrainerListItem,
    TrainerListResponse,
    TrainerUpdate
)
from app.services.auth import get_password_hash, get_current_user
from app.utils.dependencies import get_hr_user


router = APIRouter()


def generate_temp_password(length: int = 12) -> str:
    """Generate a secure temporary password"""
    characters = string.ascii_letters + string.digits + "!@#$%&"
    return ''.join(secrets.choice(characters) for _ in range(length))


@router.post("/", response_model=TrainerResponse, status_code=status.HTTP_201_CREATED)
async def create_trainer(
    trainer_data: TrainerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_hr_user)
):
    """
    Create a new trainer account
    
    **Required role**: HR or Super Admin
    **Body**:
    - name: Full name (required)
    - email: Email address (required, will be used for login)
    - phone: Phone number (optional)
    - specialization: List of expertise areas (optional)
    - bio: Short bio (optional)
    
    **Returns**: Trainer details with generated temporary password (shown only once!)
    """
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == trainer_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Generate temporary password
    temp_password = generate_temp_password()
    
    # Create user account with TRAINER role
    new_user = User(
        email=trainer_data.email,
        name=trainer_data.name,
        password_hash=get_password_hash(temp_password),
        role=UserRole.TRAINER,
        is_active=True
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Return trainer details with temp password
    return TrainerResponse(
        user_id=new_user.id,
        name=new_user.name,
        email=new_user.email,
        phone=trainer_data.phone,
        specialization=trainer_data.specialization,
        bio=trainer_data.bio,
        role=new_user.role.value,
        is_active=new_user.is_active,
        created_at=new_user.created_at,
        temp_password=temp_password  # Only shown during creation!
    )


@router.get("/", response_model=TrainerListResponse)
async def list_trainers(
    page: int = 1,
    page_size: int = 20,
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get list of all trainers
    
    **Required role**: Any authenticated user
    **Query params**:
    - page: Page number (default: 1)
    - page_size: Items per page (default: 20, max: 100)
    - search: Search by name or email
    - is_active: Filter by active status
    """
    # Validate pagination
    page_size = min(page_size, 100)
    
    # Build query
    query = db.query(User).filter(User.role == UserRole.TRAINER)
    
    # Apply filters
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (User.name.ilike(search_term)) | (User.email.ilike(search_term))
        )
    
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    trainers = query.order_by(User.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    # Get batch counts for each trainer
    trainer_list = []
    for trainer in trainers:
        # Get all batches assigned to this trainer
        assigned_batches = db.query(Batch).filter(Batch.trainer_id == trainer.id).all()
        batch_count = len(assigned_batches)

        # Check if trainer is idle (all batches have 100% completion)
        # Trainer is idle if they have no batches OR all batches are 100% complete
        is_idle = True
        if batch_count > 0:
            for batch in assigned_batches:
                # Get all mavericks in this batch
                mavericks = db.query(Maverick).filter(
                    Maverick.current_batch_id == batch.id
                ).all()

                if not mavericks:
                    # Batch has no mavericks enrolled = idle for this batch
                    continue

                # Calculate batch completion by averaging all maverick progress
                total_completion = 0.0
                for maverick in mavericks:
                    progress_records = db.query(MaverickJobProgress).filter(
                        MaverickJobProgress.maverick_id == maverick.id,
                        MaverickJobProgress.batch_id == batch.id
                    ).all()

                    if progress_records:
                        # Calculate completion percentage for this maverick
                        maverick_completion = sum(float(p.completion_percentage or 0) for p in progress_records)
                        maverick_avg = maverick_completion / len(progress_records)
                        total_completion += maverick_avg
                    else:
                        # No progress records = batch not started = not idle
                        is_idle = False
                        break

                if not is_idle:
                    break

                # Calculate batch overall completion
                batch_completion = total_completion / len(mavericks) if mavericks else 0

                # If batch completion is less than 100%, trainer is not idle
                if batch_completion < 100:
                    is_idle = False
                    break

        trainer_list.append(TrainerListItem(
            user_id=trainer.id,
            name=trainer.name,
            email=trainer.email,
            phone=None,  # Not stored in User model
            specialization=None,  # Not stored in User model
            is_active=trainer.is_active,
            created_at=trainer.created_at,
            assigned_batches_count=batch_count,
            is_idle=is_idle
        ))
    
    return TrainerListResponse(
        trainers=trainer_list,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


@router.get("/{trainer_id}")
async def get_trainer(
    trainer_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get trainer details by ID

    **Required role**: Any authenticated user
    **Path params**:
    - trainer_id: UUID of the trainer
    """
    trainer = db.query(User).filter(
        User.id == trainer_id,
        User.role == UserRole.TRAINER
    ).first()

    if not trainer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trainer not found"
        )

    # Get assigned batches
    batches = db.query(Batch).filter(Batch.trainer_id == trainer_id).all()

    return {
        "user_id": str(trainer.id),
        "name": trainer.name,
        "email": trainer.email,
        "role": trainer.role.value,
        "is_active": trainer.is_active,
        "created_at": trainer.created_at,
        "last_login": trainer.last_login,
        "assigned_batches": [
            {
                "id": str(b.id),
                "name": b.name,
                "status": b.status.value,
                "current_enrollment": b.current_enrollment
            }
            for b in batches
        ]
    }


@router.patch("/{trainer_id}")
async def update_trainer(
    trainer_id: UUID,
    update_data: TrainerUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_hr_user)
):
    """
    Update trainer information

    **Required role**: HR or Super Admin
    **Path params**:
    - trainer_id: UUID of the trainer
    **Body**: Fields to update (all optional)
    """
    trainer = db.query(User).filter(
        User.id == trainer_id,
        User.role == UserRole.TRAINER
    ).first()

    if not trainer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trainer not found"
        )

    # Update fields
    update_dict = update_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        if hasattr(trainer, field):
            setattr(trainer, field, value)

    db.commit()
    db.refresh(trainer)

    return {
        "user_id": str(trainer.id),
        "name": trainer.name,
        "email": trainer.email,
        "is_active": trainer.is_active,
        "message": "Trainer updated successfully"
    }


@router.delete("/{trainer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_trainer(
    trainer_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_hr_user)
):
    """
    Deactivate a trainer account (soft delete)

    **Required role**: HR or Super Admin
    **Path params**:
    - trainer_id: UUID of the trainer
    """
    trainer = db.query(User).filter(
        User.id == trainer_id,
        User.role == UserRole.TRAINER
    ).first()

    if not trainer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trainer not found"
        )

    # Soft delete: set is_active to False
    trainer.is_active = False
    db.commit()

    return None
