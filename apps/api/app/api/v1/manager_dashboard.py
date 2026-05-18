"""
Manager Dashboard API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import Optional, List
from uuid import UUID
from datetime import datetime, timedelta

from app.database import get_db
from app.models.user import User, UserRole
from app.models.maverick import Maverick, DeploymentStatus as MaverickDeploymentStatus
from app.models.deployment import Deployment, DeploymentRequest, DeploymentRequestStatus, DeploymentStatus
from app.utils.dependencies import get_manager_user

router = APIRouter()


@router.get("/manager/dashboard/overview")
async def get_manager_dashboard_overview(
    current_user: User = Depends(get_manager_user),
    db: Session = Depends(get_db)
):
    """
    Manager Dashboard Overview
    
    Returns:
    - Statistics cards (deployment requests, team size, utilization)
    - Recent activity
    - Quick action items
    - Team summary
    """
    
    manager_id = current_user.id
    
    # ===== STATISTICS CARDS =====
    
    # Total deployment requests by this manager
    total_requests = db.query(func.count(DeploymentRequest.id)).filter(
        DeploymentRequest.requested_by == manager_id
    ).scalar() or 0
    
    pending_requests = db.query(func.count(DeploymentRequest.id)).filter(
        DeploymentRequest.requested_by == manager_id,
        DeploymentRequest.status == DeploymentRequestStatus.PENDING
    ).scalar() or 0
    
    approved_requests = db.query(func.count(DeploymentRequest.id)).filter(
        DeploymentRequest.requested_by == manager_id,
        DeploymentRequest.status == DeploymentRequestStatus.APPROVED
    ).scalar() or 0
    
    # Current team size (active deployments)
    # Note: In the Deployment model, we don't have manager_id directly
    # We need to check which deployments were from approved requests by this manager
    active_team_count = db.query(func.count(Deployment.id)).join(
        DeploymentRequest,
        DeploymentRequest.maverick_id == Deployment.maverick_id
    ).filter(
        DeploymentRequest.requested_by == manager_id,
        DeploymentRequest.status == DeploymentRequestStatus.APPROVED,
        Deployment.status == DeploymentStatus.ACTIVE
    ).scalar() or 0
    
    # Available mavericks (for quick info)
    available_mavericks = db.query(func.count(Maverick.id)).filter(
        Maverick.deployment_status == MaverickDeploymentStatus.AVAILABLE
    ).scalar() or 0
    
    stats = {
        "total_requests": total_requests,
        "pending_requests": pending_requests,
        "approved_requests": approved_requests,
        "rejected_requests": total_requests - pending_requests - approved_requests,
        "active_team_size": active_team_count,
        "available_talent_count": available_mavericks
    }
    
    # ===== RECENT DEPLOYMENT REQUESTS =====
    recent_requests = db.query(DeploymentRequest).filter(
        DeploymentRequest.requested_by == manager_id
    ).order_by(DeploymentRequest.created_at.desc()).limit(5).all()
    
    import json
    recent_requests_list = []
    for req in recent_requests:
        maverick = db.query(Maverick).filter(Maverick.id == req.maverick_id).first() if req.maverick_id else None
        recent_requests_list.append({
            "id": str(req.id),
            "role_title": req.role_title,
            "project_name": req.project_name,
            "status": req.status.value,
            "maverick_name": maverick.name if maverick else "Not Assigned",
            "created_at": req.created_at.isoformat(),
            "required_skills": json.loads(req.required_skills) if req.required_skills else []
        })
    
    # ===== ACTIVE TEAM MEMBERS =====
    # Get deployments from approved requests by this manager
    active_deployments = db.query(Deployment).join(
        DeploymentRequest,
        DeploymentRequest.maverick_id == Deployment.maverick_id
    ).filter(
        DeploymentRequest.requested_by == manager_id,
        DeploymentRequest.status == DeploymentRequestStatus.APPROVED,
        Deployment.status == DeploymentStatus.ACTIVE
    ).order_by(Deployment.deployed_at.desc()).limit(10).all()
    
    team_list = []
    for deployment in active_deployments:
        maverick = db.query(Maverick).filter(Maverick.id == deployment.maverick_id).first()
        if maverick:
            team_list.append({
                "id": str(deployment.id),
                "maverick_id": str(maverick.id),
                "maverick_name": maverick.name,
                "project_name": deployment.project_name,
                "role": deployment.role,
                "start_date": deployment.start_date.isoformat() if deployment.start_date else None,
                "vertical": deployment.vertical,
                "competency": deployment.competency
            })
    
    return {
        "stats": stats,
        "recent_requests": recent_requests_list,
        "active_team": team_list,
        "welcome_message": f"Welcome back, {current_user.name}!"
    }
