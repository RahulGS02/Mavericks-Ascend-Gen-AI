"""
Deployment Management API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from uuid import UUID
from datetime import datetime

from app.database import get_db
from app.models.user import User, UserRole
from app.models.maverick import Maverick, DeploymentStatus as MaverickDeploymentStatus
from app.models.batch import Batch
from app.models.deployment import Deployment, DeploymentRequest, DeploymentRequestStatus, DeploymentStatus
from app.schemas.deployment import (
    DeploymentRequestCreate,
    DeploymentRequestResponse,
    DeploymentRequestListResponse,
    ApproveDeploymentRequest,
    RejectDeploymentRequest,
    DeployMaverickRequest,
    DeploymentResponse,
    DeploymentListResponse,
    DeploymentHistoryResponse
)
from app.services.auth import get_current_user, get_hr_user


router = APIRouter()


# ==================== Manager: Request Deployment ====================


@router.post("/requests", response_model=DeploymentRequestResponse, status_code=status.HTTP_201_CREATED)
async def request_deployment(
    request_data: DeploymentRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Manager/HR: Create deployment requirement card

    **Required role**: Any authenticated user (Manager, HR, or Super Admin)
    **Body** (REQUIRED):
    - role_title: Role/Position title (e.g., "Senior Full Stack Developer")
    - required_skills: List of required skills

    **Body** (Optional):
    - role_description: Detailed requirements description
    - preferred_skills: Nice-to-have skills
    - project_name: Project name
    - vertical: Business vertical
    - competency: Competency area
    - justification: Business justification
    - maverick_id: Can be assigned later by HR

    **Workflow:**
    1. Manager/HR creates requirement card with role details and skills
    2. Card appears in pending requests
    3. HR searches for suitable mavericks
    4. HR assigns maverick to card
    5. Deployment proceeds
    """
    import json

    # Verify maverick if provided
    if request_data.maverick_id:
        maverick = db.query(Maverick).filter(Maverick.id == request_data.maverick_id).first()
        if not maverick:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Maverick not found"
            )

        # Check if maverick is available for deployment
        if maverick.deployment_status == MaverickDeploymentStatus.DEPLOYED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maverick is already deployed"
            )

    # Create deployment requirement card
    deployment_request = DeploymentRequest(
        maverick_id=request_data.maverick_id,  # Can be None
        requested_by=current_user.id,
        role_title=request_data.role_title,
        role_description=request_data.role_description,
        required_skills=json.dumps(request_data.required_skills) if request_data.required_skills else None,
        preferred_skills=json.dumps(request_data.preferred_skills) if request_data.preferred_skills else None,
        project_name=request_data.project_name,
        vertical=request_data.vertical,
        competency=request_data.competency,
        justification=request_data.justification,
        status=DeploymentRequestStatus.PENDING,
        positions_count=request_data.positions_count,
        filled_count=0,
        workflow_stage='PENDING'
    )

    db.add(deployment_request)
    db.commit()
    db.refresh(deployment_request)
    
    # Get requester name and maverick name (if assigned)
    import json
    requester = db.query(User).filter(User.id == current_user.id).first()
    maverick_name = None
    if deployment_request.maverick_id:
        maverick = db.query(Maverick).filter(Maverick.id == deployment_request.maverick_id).first()
        maverick_name = maverick.name if maverick else None

    return DeploymentRequestResponse(
        id=deployment_request.id,
        maverick_id=deployment_request.maverick_id,
        requested_by=deployment_request.requested_by,
        requested_by_name=requester.name if requester else None,
        maverick_name=maverick_name,
        role_title=deployment_request.role_title,
        role_description=deployment_request.role_description,
        required_skills=json.loads(deployment_request.required_skills) if deployment_request.required_skills else [],
        preferred_skills=json.loads(deployment_request.preferred_skills) if deployment_request.preferred_skills else [],
        project_name=deployment_request.project_name,
        vertical=deployment_request.vertical,
        competency=deployment_request.competency,
        justification=deployment_request.justification,
        positions_count=deployment_request.positions_count,
        filled_count=deployment_request.filled_count,
        workflow_stage=deployment_request.workflow_stage,
        status=deployment_request.status.value if hasattr(deployment_request.status, 'value') else deployment_request.status,
        approved_by=deployment_request.approved_by,
        approved_at=deployment_request.approved_at,
        rejection_reason=deployment_request.rejection_reason,
        created_at=deployment_request.created_at,
        updated_at=deployment_request.updated_at
    )


# ==================== HR: Get Deployment Request Statistics ====================


@router.get("/requests/statistics")
async def get_deployment_request_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get deployment request statistics

    **Required role**: HR, Manager, or Super Admin
    - HR sees ALL requests statistics
    - Manager sees ONLY THEIR OWN requests statistics

    Returns:
    - total_requirements: Total number of deployment requests
    - pending: Number of pending requests
    - approved: Number of approved requests
    - rejected: Number of rejected requests
    """
    # Managers see only their own requests statistics
    if current_user.role == UserRole.MANAGER:
        total = db.query(func.count(DeploymentRequest.id)).filter(
            DeploymentRequest.requested_by == current_user.id
        ).scalar() or 0
        pending = db.query(func.count(DeploymentRequest.id)).filter(
            DeploymentRequest.requested_by == current_user.id,
            DeploymentRequest.status == DeploymentRequestStatus.PENDING
        ).scalar() or 0
        approved = db.query(func.count(DeploymentRequest.id)).filter(
            DeploymentRequest.requested_by == current_user.id,
            DeploymentRequest.status == DeploymentRequestStatus.APPROVED
        ).scalar() or 0
        rejected = db.query(func.count(DeploymentRequest.id)).filter(
            DeploymentRequest.requested_by == current_user.id,
            DeploymentRequest.status == DeploymentRequestStatus.REJECTED
        ).scalar() or 0
    # HR and Super Admin see all requests
    elif current_user.role in [UserRole.HR, UserRole.SUPER_ADMIN]:
        total = db.query(func.count(DeploymentRequest.id)).scalar() or 0
        pending = db.query(func.count(DeploymentRequest.id)).filter(
            DeploymentRequest.status == DeploymentRequestStatus.PENDING
        ).scalar() or 0
        approved = db.query(func.count(DeploymentRequest.id)).filter(
            DeploymentRequest.status == DeploymentRequestStatus.APPROVED
        ).scalar() or 0
        rejected = db.query(func.count(DeploymentRequest.id)).filter(
            DeploymentRequest.status == DeploymentRequestStatus.REJECTED
        ).scalar() or 0
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view deployment request statistics"
        )

    return {
        "total_requirements": total,
        "pending": pending,
        "approved": approved,
        "rejected": rejected
    }


# ==================== HR: List Deployment Requests ====================


@router.get("/requests", response_model=DeploymentRequestListResponse)
async def list_deployment_requests(
    page: int = 1,
    page_size: int = 20,
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List deployment requests

    **Required role**: HR, Manager, or Super Admin
    - HR sees ALL requests
    - Manager sees ONLY THEIR OWN requests

    **Query params**:
    - page: Page number (default: 1)
    - page_size: Items per page (default: 20)
    - status_filter: Filter by status (PENDING, APPROVED, REJECTED)

    Returns deployment requests with filtering.
    """
    query = db.query(DeploymentRequest)

    # Managers see only their own requests
    if current_user.role == UserRole.MANAGER:
        query = query.filter(DeploymentRequest.requested_by == current_user.id)
    # HR and Super Admin see all requests
    elif current_user.role not in [UserRole.HR, UserRole.SUPER_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view deployment requests"
        )

    # Apply status filter
    if status_filter:
        try:
            query = query.filter(DeploymentRequest.status == DeploymentRequestStatus(status_filter))
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
    requests = query.order_by(DeploymentRequest.created_at.desc()).offset(offset).limit(page_size).all()
    
    # Build responses
    request_responses = []
    for req in requests:
        maverick = db.query(Maverick).filter(Maverick.id == req.maverick_id).first()
        requester = db.query(User).filter(User.id == req.requested_by).first()
        
        import json

        request_responses.append(DeploymentRequestResponse(
            id=req.id,
            maverick_id=req.maverick_id,
            requested_by=req.requested_by,
            requested_by_name=requester.name if requester else None,
            maverick_name=maverick.name if maverick else None,
            role_title=req.role_title,
            role_description=req.role_description,
            required_skills=json.loads(req.required_skills) if req.required_skills else [],
            preferred_skills=json.loads(req.preferred_skills) if req.preferred_skills else [],
            project_name=req.project_name,
            vertical=req.vertical,
            competency=req.competency,
            justification=req.justification,
            status=req.status.value if hasattr(req.status, 'value') else req.status,
            approved_by=req.approved_by,
            approved_at=req.approved_at,
            rejection_reason=req.rejection_reason,
            created_at=req.created_at,
            updated_at=req.updated_at
        ))
    
    return DeploymentRequestListResponse(
        requests=request_responses,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


# ==================== HR: Approve Deployment Request ====================


@router.post("/requests/{request_id}/approve", response_model=DeploymentRequestResponse)
async def approve_deployment_request(
    request_id: UUID,
    approval_data: ApproveDeploymentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_hr_user)
):
    """
    HR: Approve a deployment request

    **Required role**: HR or Super Admin
    **Path params**:
    - request_id: UUID of the deployment request
    **Body**:
    - notes: Optional approval notes

    Approves the deployment request.
    """
    # Get request
    deployment_request = db.query(DeploymentRequest).filter(
        DeploymentRequest.id == request_id
    ).first()

    if not deployment_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deployment request not found"
        )

    # Check if already processed
    if deployment_request.status != DeploymentRequestStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Request already {deployment_request.status.value}"
        )

    # Approve request
    deployment_request.status = DeploymentRequestStatus.APPROVED
    deployment_request.approved_by = current_user.id
    deployment_request.approved_at = datetime.utcnow()
    if approval_data.notes:
        deployment_request.rejection_reason = approval_data.notes  # Using rejection_reason field for notes

    db.commit()
    db.refresh(deployment_request)

    # Get details for response
    maverick = db.query(Maverick).filter(Maverick.id == deployment_request.maverick_id).first()
    requester = db.query(User).filter(User.id == deployment_request.requested_by).first()

    return DeploymentRequestResponse(
        id=deployment_request.id,
        maverick_id=deployment_request.maverick_id,
        requested_by=deployment_request.requested_by,
        requested_by_name=requester.name if requester else None,
        maverick_name=maverick.name if maverick else None,
        project_name=deployment_request.project_name,
        vertical=deployment_request.vertical,
        competency=deployment_request.competency,
        justification=deployment_request.justification,
        status=deployment_request.status.value if hasattr(deployment_request.status, 'value') else deployment_request.status,
        approved_by=deployment_request.approved_by,
        approved_at=deployment_request.approved_at,
        rejection_reason=deployment_request.rejection_reason,
        created_at=deployment_request.created_at,
        updated_at=deployment_request.updated_at
    )


# ==================== HR: Reject Deployment Request ====================


@router.post("/requests/{request_id}/reject", response_model=DeploymentRequestResponse)
async def reject_deployment_request(
    request_id: UUID,
    rejection_data: RejectDeploymentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_hr_user)
):
    """
    HR: Reject a deployment request

    **Required role**: HR or Super Admin
    **Path params**:
    - request_id: UUID of the deployment request
    **Body**:
    - rejection_reason: Reason for rejection (required)

    Rejects the deployment request with a reason.
    """
    # Get request
    deployment_request = db.query(DeploymentRequest).filter(
        DeploymentRequest.id == request_id
    ).first()

    if not deployment_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deployment request not found"
        )

    # Check if already processed
    if deployment_request.status != DeploymentRequestStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Request already {deployment_request.status.value}"
        )

    # Reject request
    deployment_request.status = DeploymentRequestStatus.REJECTED
    deployment_request.approved_by = current_user.id
    deployment_request.approved_at = datetime.utcnow()
    deployment_request.rejection_reason = rejection_data.rejection_reason

    db.commit()
    db.refresh(deployment_request)

    # Get details for response
    maverick = db.query(Maverick).filter(Maverick.id == deployment_request.maverick_id).first()
    requester = db.query(User).filter(User.id == deployment_request.requested_by).first()

    return DeploymentRequestResponse(
        id=deployment_request.id,
        maverick_id=deployment_request.maverick_id,
        requested_by=deployment_request.requested_by,
        requested_by_name=requester.name if requester else None,
        maverick_name=maverick.name if maverick else None,
        project_name=deployment_request.project_name,
        vertical=deployment_request.vertical,
        competency=deployment_request.competency,
        justification=deployment_request.justification,
        status=deployment_request.status.value if hasattr(deployment_request.status, 'value') else deployment_request.status,
        approved_by=deployment_request.approved_by,
        approved_at=deployment_request.approved_at,
        rejection_reason=deployment_request.rejection_reason,
        created_at=deployment_request.created_at,
        updated_at=deployment_request.updated_at
    )


# ==================== HR: Get Single Deployment Request ====================


@router.get("/requests/{request_id}", response_model=DeploymentRequestResponse)
async def get_deployment_request(
    request_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get details of a single deployment request

    **Required role**: HR, Manager, or Super Admin
    - HR can view ANY request
    - Manager can view ONLY THEIR OWN requests

    **Path params**:
    - request_id: UUID of the deployment request

    Returns full deployment request details.
    """
    deployment_request = db.query(DeploymentRequest).filter(
        DeploymentRequest.id == request_id
    ).first()

    if not deployment_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deployment request not found"
        )

    # Managers can only view their own requests
    if current_user.role == UserRole.MANAGER:
        if deployment_request.requested_by != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view your own deployment requests"
            )
    # Only HR and Super Admin can view all requests
    elif current_user.role not in [UserRole.HR, UserRole.SUPER_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view deployment requests"
        )

    # Get related data
    import json

    maverick = db.query(Maverick).filter(Maverick.id == deployment_request.maverick_id).first()
    requester = db.query(User).filter(User.id == deployment_request.requested_by).first()
    approver = db.query(User).filter(User.id == deployment_request.approved_by).first() if deployment_request.approved_by else None

    return DeploymentRequestResponse(
        id=deployment_request.id,
        maverick_id=deployment_request.maverick_id,
        requested_by=deployment_request.requested_by,
        requested_by_name=requester.name if requester else None,
        maverick_name=maverick.name if maverick else None,
        role_title=deployment_request.role_title,
        role_description=deployment_request.role_description,
        required_skills=json.loads(deployment_request.required_skills) if deployment_request.required_skills else [],
        preferred_skills=json.loads(deployment_request.preferred_skills) if deployment_request.preferred_skills else [],
        project_name=deployment_request.project_name,
        vertical=deployment_request.vertical,
        competency=deployment_request.competency,
        justification=deployment_request.justification,
        status=deployment_request.status.value if hasattr(deployment_request.status, 'value') else deployment_request.status,
        approved_by=deployment_request.approved_by,
        approved_at=deployment_request.approved_at,
        rejection_reason=deployment_request.rejection_reason,
        created_at=deployment_request.created_at,
        updated_at=deployment_request.updated_at
    )


# ==================== HR: Delete Deployment Request ====================


@router.delete("/requests/{request_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_deployment_request(
    request_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_hr_user)
):
    """
    HR: Delete a deployment request

    **Required role**: HR or Super Admin
    **Path params**:
    - request_id: UUID of the deployment request

    Permanently deletes the deployment request.
    """
    deployment_request = db.query(DeploymentRequest).filter(
        DeploymentRequest.id == request_id
    ).first()

    if not deployment_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deployment request not found"
        )

    db.delete(deployment_request)
    db.commit()

    return None


# ==================== HR: Deploy Maverick ====================


@router.post("/", response_model=DeploymentResponse, status_code=status.HTTP_201_CREATED)
async def deploy_maverick(
    deployment_data: DeployMaverickRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_hr_user)
):
    """
    HR: Deploy a maverick to a project

    **Required role**: HR or Super Admin
    **Body**:
    - maverick_id: UUID of the maverick
    - project_name: Project name (required)
    - vertical: Business vertical (required)
    - competency: Competency area (required)
    - start_date: Deployment start date (required)
    - end_date: Expected end date (optional)
    - role: Role/designation (optional)
    - manager_name: Project manager (optional)
    - location: Deployment location (optional)
    - notes: Deployment notes (optional)

    Creates a deployment record and updates maverick status to DEPLOYED.
    """
    # Verify maverick exists
    maverick = db.query(Maverick).filter(Maverick.id == deployment_data.maverick_id).first()
    if not maverick:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Maverick not found"
        )

    # Check if already deployed
    if maverick.deployment_status == MaverickDeploymentStatus.DEPLOYED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maverick is already deployed"
        )

    # Create deployment
    deployment = Deployment(
        maverick_id=deployment_data.maverick_id,
        batch_id=maverick.current_batch_id,
        project_name=deployment_data.project_name,
        vertical=deployment_data.vertical,
        competency=deployment_data.competency,
        role=deployment_data.role,
        manager_name=deployment_data.manager_name,
        location=deployment_data.location,
        start_date=deployment_data.start_date,
        end_date=deployment_data.end_date,
        status=DeploymentStatus.ACTIVE,
        deployed_by=current_user.id,
        deployed_at=datetime.utcnow(),
        notes=deployment_data.notes
    )

    db.add(deployment)

    # Update maverick status
    maverick.deployment_status = MaverickDeploymentStatus.DEPLOYED

    db.commit()
    db.refresh(deployment)

    # Get batch name
    batch = None
    batch_name = None
    if deployment.batch_id:
        batch = db.query(Batch).filter(Batch.id == deployment.batch_id).first()
        batch_name = batch.name if batch else None

    return DeploymentResponse(
        id=deployment.id,
        maverick_id=deployment.maverick_id,
        maverick_name=maverick.name,
        batch_id=deployment.batch_id,
        batch_name=batch_name,
        project_name=deployment.project_name,
        vertical=deployment.vertical,
        competency=deployment.competency,
        start_date=deployment.start_date,
        end_date=deployment.end_date,
        role=deployment.role,
        manager_name=deployment.manager_name,
        location=deployment.location,
        status=deployment.status.value if hasattr(deployment.status, 'value') else deployment.status,
        deployed_by=deployment.deployed_by,
        deployed_at=deployment.deployed_at,
        notes=deployment.notes,
        created_at=deployment.created_at,
        updated_at=deployment.updated_at
    )


# ==================== Get Deployment History ====================


@router.get("/maverick/{maverick_id}/history", response_model=DeploymentHistoryResponse)
async def get_deployment_history(
    maverick_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get deployment history for a maverick

    **Required role**: Any authenticated user
    **Path params**:
    - maverick_id: UUID of the maverick

    Returns all deployments for the maverick.
    """
    # Verify maverick exists
    maverick = db.query(Maverick).filter(Maverick.id == maverick_id).first()
    if not maverick:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Maverick not found"
        )

    # Get all deployments
    deployments = db.query(Deployment).filter(
        Deployment.maverick_id == maverick_id
    ).order_by(Deployment.start_date.desc()).all()

    # Calculate statistics
    total_deployments = len(deployments)
    active_deployments = sum(1 for d in deployments if d.status == DeploymentStatus.ACTIVE)
    completed_deployments = sum(1 for d in deployments if d.status == DeploymentStatus.COMPLETED)

    # Build deployment responses
    deployment_responses = []
    for deployment in deployments:
        batch_name = None
        if deployment.batch_id:
            batch = db.query(Batch).filter(Batch.id == deployment.batch_id).first()
            batch_name = batch.name if batch else None

        deployment_responses.append(DeploymentResponse(
            id=deployment.id,
            maverick_id=deployment.maverick_id,
            maverick_name=maverick.name,
            batch_id=deployment.batch_id,
            batch_name=batch_name,
            project_name=deployment.project_name,
            vertical=deployment.vertical,
            competency=deployment.competency,
            start_date=deployment.start_date,
            end_date=deployment.end_date,
            role=deployment.role,
            manager_name=deployment.manager_name,
            location=deployment.location,
            status=deployment.status.value if hasattr(deployment.status, 'value') else deployment.status,
            deployed_by=deployment.deployed_by,
            deployed_at=deployment.deployed_at,
            notes=deployment.notes,
            created_at=deployment.created_at,
            updated_at=deployment.updated_at
        ))

    return DeploymentHistoryResponse(
        maverick_id=maverick_id,
        maverick_name=maverick.name,
        total_deployments=total_deployments,
        active_deployments=active_deployments,
        completed_deployments=completed_deployments,
        deployments=deployment_responses
    )


# ==================== List All Deployments ====================


@router.get("/", response_model=DeploymentListResponse)
async def list_deployments(
    page: int = 1,
    page_size: int = 20,
    status_filter: Optional[str] = None,
    vertical_filter: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all deployments

    **Required role**: Any authenticated user
    **Query params**:
    - page: Page number (default: 1)
    - page_size: Items per page (default: 20)
    - status_filter: Filter by status (ACTIVE, COMPLETED, TERMINATED)
    - vertical_filter: Filter by vertical

    Returns all deployments with filtering.
    """
    query = db.query(Deployment)

    # Apply filters
    if status_filter:
        try:
            query = query.filter(Deployment.status == DeploymentStatus(status_filter))
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {status_filter}"
            )

    if vertical_filter:
        query = query.filter(Deployment.vertical == vertical_filter)

    # Get total count
    total = query.count()

    # Calculate pagination
    total_pages = (total + page_size - 1) // page_size
    offset = (page - 1) * page_size

    # Get paginated results
    deployments = query.order_by(Deployment.start_date.desc()).offset(offset).limit(page_size).all()

    # Build responses
    deployment_responses = []
    for deployment in deployments:
        maverick = db.query(Maverick).filter(Maverick.id == deployment.maverick_id).first()
        batch_name = None
        if deployment.batch_id:
            batch = db.query(Batch).filter(Batch.id == deployment.batch_id).first()
            batch_name = batch.name if batch else None

        deployment_responses.append(DeploymentResponse(
            id=deployment.id,
            maverick_id=deployment.maverick_id,
            maverick_name=maverick.name if maverick else "Unknown",
            batch_id=deployment.batch_id,
            batch_name=batch_name,
            project_name=deployment.project_name,
            vertical=deployment.vertical,
            competency=deployment.competency,
            start_date=deployment.start_date,
            end_date=deployment.end_date,
            role=deployment.role,
            manager_name=deployment.manager_name,
            location=deployment.location,
            status=deployment.status.value if hasattr(deployment.status, 'value') else deployment.status,
            deployed_by=deployment.deployed_by,
            deployed_at=deployment.deployed_at,
            notes=deployment.notes,
            created_at=deployment.created_at,
            updated_at=deployment.updated_at
        ))

    return DeploymentListResponse(
        deployments=deployment_responses,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


# ==================== Deployment Readiness ====================


@router.get("/batch/{batch_id}/readiness")
async def get_deployment_readiness(
    batch_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get deployment readiness statistics for a batch.

    Shows:
    - How many mavericks are ready for deployment
    - How many are not ready (with reasons)
    - How many are already deployed

    Readiness criteria:
    - Attended ALL training jobs (marked PRESENT)
    - Passed ALL assessments

    **Required role**: Any authenticated user
    **Path params**:
    - batch_id: UUID of the batch
    """
    from app.services.deployment_service import get_deployment_readiness_stats

    # Verify batch exists
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Batch not found"
        )

    stats = get_deployment_readiness_stats(db, batch_id, batch.pipeline_id)

    return {
        "batch_id": str(batch_id),
        "batch_name": batch.name,
        "deployment_ready_count": stats["ready_count"],
        "not_ready_count": stats["not_ready_count"],
        "deployed_count": stats["deployed_count"],
        "total_students": stats["total_count"],
        "students": stats["mavericks"]
    }


@router.post("/batch/{batch_id}/auto-activate")
async def trigger_deployment_auto_activation(
    batch_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Manually trigger deployment job auto-activation check.

    This is normally done automatically when jobs are completed,
    but can be triggered manually if needed.

    **Required role**: Any authenticated user
    **Path params**:
    - batch_id: UUID of the batch
    """
    from app.services.deployment_service import auto_activate_deployment_job

    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Batch not found"
        )

    activated = auto_activate_deployment_job(db, batch_id, batch.pipeline_id)

    return {
        "success": True,
        "activated": activated,
        "message": "Deployment job activated" if activated else "Deployment job not ready to activate"
    }
