"""
Super Admin System Settings API
Configuration management and emergency actions
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Dict
import os

from app.database import get_db
from app.models.user import User
from app.models.audit import AuditLog
from app.schemas.admin import (
    SystemSettingsResponse,
    EmergencyActionRequest,
    EmergencyActionResponse
)
from app.utils.dependencies import get_super_admin
from app.config import settings
from app.services.ai_service import ai_service


router = APIRouter(prefix="/admin/settings", tags=["Super Admin - Settings"])


@router.get("/", response_model=SystemSettingsResponse)
async def get_system_settings(
    current_user: User = Depends(get_super_admin)
):
    """
    Get current system settings
    
    **Required role**: Super Admin ONLY
    
    Note: Sensitive data (API keys) are not exposed
    """
    return SystemSettingsResponse(
        ai_enabled=settings.AI_ENABLED,
        ai_model=settings.AI_MODEL,
        ai_max_tokens=settings.AI_MAX_TOKENS,
        ai_daily_limit=settings.AI_DAILY_REQUEST_LIMIT,
        ai_rate_limit_per_minute=settings.AI_RATE_LIMIT_PER_MINUTE,
        ai_resume_parsing_enabled=settings.AI_RESUME_PARSING_ENABLED,
        ai_skill_extraction_enabled=settings.AI_SKILL_EXTRACTION_ENABLED,
        ai_performance_insights_enabled=settings.AI_PERFORMANCE_INSIGHTS_ENABLED,
        environment=os.getenv("ENVIRONMENT", "production")
    )


@router.post("/ai/toggle", response_model=Dict[str, bool])
async def toggle_ai_features(
    feature: str,
    enabled: bool,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_super_admin)
):
    """
    Toggle AI features on/off
    
    **Required role**: Super Admin ONLY
    
    **Parameters**:
    - feature: One of: "resume_parsing", "skill_extraction", "performance_insights", "all"
    - enabled: True to enable, False to disable
    
    Note: This updates the settings object but doesn't persist to env file.
    Restart required for permanent changes.
    """
    old_values = {}
    new_values = {}
    
    if feature == "resume_parsing":
        old_values["ai_resume_parsing_enabled"] = settings.AI_RESUME_PARSING_ENABLED
        settings.AI_RESUME_PARSING_ENABLED = enabled
        new_values["ai_resume_parsing_enabled"] = enabled
    elif feature == "skill_extraction":
        old_values["ai_skill_extraction_enabled"] = settings.AI_SKILL_EXTRACTION_ENABLED
        settings.AI_SKILL_EXTRACTION_ENABLED = enabled
        new_values["ai_skill_extraction_enabled"] = enabled
    elif feature == "performance_insights":
        old_values["ai_performance_insights_enabled"] = settings.AI_PERFORMANCE_INSIGHTS_ENABLED
        settings.AI_PERFORMANCE_INSIGHTS_ENABLED = enabled
        new_values["ai_performance_insights_enabled"] = enabled
    elif feature == "all":
        old_values = {
            "ai_resume_parsing_enabled": settings.AI_RESUME_PARSING_ENABLED,
            "ai_skill_extraction_enabled": settings.AI_SKILL_EXTRACTION_ENABLED,
            "ai_performance_insights_enabled": settings.AI_PERFORMANCE_INSIGHTS_ENABLED,
        }
        settings.AI_RESUME_PARSING_ENABLED = enabled
        settings.AI_SKILL_EXTRACTION_ENABLED = enabled
        settings.AI_PERFORMANCE_INSIGHTS_ENABLED = enabled
        new_values = {
            "ai_resume_parsing_enabled": enabled,
            "ai_skill_extraction_enabled": enabled,
            "ai_performance_insights_enabled": enabled,
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid feature. Must be one of: resume_parsing, skill_extraction, performance_insights, all"
        )
    
    # Create audit log
    audit_log = AuditLog(
        user_id=current_user.id,
        action="updated",
        entity_type="system_settings",
        entity_id=None,
        old_value=old_values,
        new_value=new_values
    )
    db.add(audit_log)
    db.commit()
    
    return {
        "success": True,
        "feature": feature,
        "enabled": enabled
    }


@router.post("/emergency", response_model=EmergencyActionResponse)
async def execute_emergency_action(
    action_request: EmergencyActionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_super_admin)
):
    """
    Execute emergency actions
    
    **Required role**: Super Admin ONLY
    
    **Available actions**:
    - disable_ai: Immediately disable all AI features
    - force_logout_all: Force logout all users (not implemented - requires session management)
    - maintenance_mode: Enable maintenance mode (not implemented - requires middleware)
    
    **Parameters**:
    - action: Action to perform
    - reason: Reason for emergency action (required, min 10 characters)
    """
    timestamp = datetime.utcnow()
    message = ""
    success = False
    
    if action_request.action == "disable_ai":
        # Disable all AI features
        settings.AI_ENABLED = False
        settings.AI_RESUME_PARSING_ENABLED = False
        settings.AI_SKILL_EXTRACTION_ENABLED = False
        settings.AI_PERFORMANCE_INSIGHTS_ENABLED = False
        
        message = "All AI features have been disabled. Resume, skill extraction, and performance insights are now inactive."
        success = True
        
    elif action_request.action == "force_logout_all":
        # This would require session management or JWT blacklist
        message = "Force logout feature requires session management implementation"
        success = False
        
    elif action_request.action == "maintenance_mode":
        # This would require middleware implementation
        message = "Maintenance mode requires middleware implementation"
        success = False
        
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid action. Must be one of: disable_ai, force_logout_all, maintenance_mode"
        )
    
    # Create audit log
    audit_log = AuditLog(
        user_id=current_user.id,
        action="emergency_action",
        entity_type="system",
        entity_id=None,
        new_value={
            "action": action_request.action,
            "reason": action_request.reason,
            "success": success
        }
    )
    db.add(audit_log)
    db.commit()
    
    return EmergencyActionResponse(
        success=success,
        action=action_request.action,
        message=message,
        timestamp=timestamp
    )
