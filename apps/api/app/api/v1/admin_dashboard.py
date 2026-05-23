"""
Super Admin Dashboard API
System-wide statistics and monitoring
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, timedelta
from typing import Dict

from app.database import get_db
from app.models.user import User, UserRole
from app.models.maverick import Maverick
from app.models.batch import Batch, BatchStatus
from app.models.deployment import Deployment
from app.models.audit import AuditLog
from app.schemas.admin import SystemStatsResponse, SystemHealthResponse
from app.utils.dependencies import get_super_admin
from app.services.ai_service import ai_service


router = APIRouter(prefix="/admin/dashboard", tags=["Super Admin - Dashboard"])


@router.get("/stats", response_model=SystemStatsResponse)
async def get_system_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_super_admin)
):
    """
    Get comprehensive system-wide statistics
    
    **Required role**: Super Admin ONLY
    
    Returns:
    - Total users and breakdown by role
    - Active/inactive users
    - Total mavericks, batches, deployments
    - AI usage and costs (today and this month)
    - Failed login attempts
    - System uptime and active sessions
    """
    # User statistics
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    inactive_users = total_users - active_users
    
    # Users by role
    users_by_role = {}
    for role in UserRole:
        count = db.query(User).filter(User.role == role).count()
        users_by_role[role.value] = count
    
    # Maverick statistics
    total_mavericks = db.query(Maverick).count()
    
    # Batch statistics
    total_batches = db.query(Batch).count()
    
    # Deployment statistics
    total_deployments = db.query(Deployment).count()
    
    # AI statistics
    ai_stats = ai_service.get_stats()
    ai_detailed_stats = ai_service.get_detailed_stats()
    
    # Get AI costs
    ai_cost_today = 0.0
    ai_cost_this_month = 0.0
    ai_requests_today = 0
    
    if ai_stats.get("total_cost_usd"):
        # For simplicity, use current stats as "this month"
        # In production, you'd track daily costs in database
        ai_cost_this_month = ai_stats["total_cost_usd"]
        ai_requests_today = ai_stats.get("total_requests", 0)
        
        # Estimate today's cost (simplified)
        if ai_stats.get("total_requests", 0) > 0:
            cost_per_request = ai_stats["total_cost_usd"] / ai_stats["total_requests"]
            ai_cost_today = cost_per_request * min(ai_requests_today, 100)  # Rough estimate
    
    # Failed login attempts (from audit logs)
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    failed_logins_today = db.query(AuditLog).filter(
        and_(
            AuditLog.action == "failed_login",
            AuditLog.timestamp >= today_start
        )
    ).count()
    
    # System uptime (placeholder - would need actual uptime tracking)
    # For now, calculate from oldest audit log
    oldest_log = db.query(AuditLog).order_by(AuditLog.timestamp.asc()).first()
    system_uptime_hours = 0.0
    if oldest_log:
        time_diff = datetime.utcnow() - oldest_log.timestamp
        system_uptime_hours = time_diff.total_seconds() / 3600
    
    # Active sessions (users logged in within last 24 hours)
    yesterday = datetime.utcnow() - timedelta(hours=24)
    active_sessions = db.query(User).filter(
        and_(
            User.last_login >= yesterday,
            User.is_active == True
        )
    ).count()
    
    return SystemStatsResponse(
        total_users=total_users,
        users_by_role=users_by_role,
        active_users=active_users,
        inactive_users=inactive_users,
        total_mavericks=total_mavericks,
        total_batches=total_batches,
        total_deployments=total_deployments,
        ai_requests_today=ai_requests_today,
        ai_cost_today=round(ai_cost_today, 2),
        ai_cost_this_month=round(ai_cost_this_month, 2),
        failed_logins_today=failed_logins_today,
        system_uptime_hours=round(system_uptime_hours, 2),
        active_sessions=active_sessions
    )


@router.get("/health", response_model=SystemHealthResponse)
async def get_system_health(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_super_admin)
):
    """
    Get system health metrics
    
    **Required role**: Super Admin ONLY
    
    Returns database status, API performance, error rates, etc.
    """
    try:
        # Test database connection
        db.execute("SELECT 1")
        database_status = "healthy"
    except Exception as e:
        database_status = f"unhealthy: {str(e)}"
    
    # Database connection pool stats (simplified)
    # In production, get from engine.pool
    database_connections = 5  # Placeholder
    
    # API response time (placeholder - would need actual monitoring)
    api_response_time_ms = 50.0  # Placeholder
    
    # Error rate (from AI service stats)
    ai_stats = ai_service.get_detailed_stats()
    error_rate_percentage = ai_stats.get("error_rate_percentage", 0.0)
    
    # Uptime percentage (placeholder)
    uptime_percentage = 99.9
    
    return SystemHealthResponse(
        database_status=database_status,
        database_connections=database_connections,
        api_response_time_ms=api_response_time_ms,
        error_rate_percentage=error_rate_percentage,
        uptime_percentage=uptime_percentage
    )
