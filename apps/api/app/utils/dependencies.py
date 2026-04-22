"""
FastAPI dependencies for authentication and authorization
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models.user import User, UserRole
from ..services.auth import decode_access_token

# Bearer token security
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT token
    
    Args:
        credentials: Bearer token credentials
        db: Database session
        
    Returns:
        Current user object
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        payload = decode_access_token(token)
        
        user_id: str = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    return user


def require_role(allowed_roles: List[UserRole]):
    """
    Dependency to check if user has required role
    
    Args:
        allowed_roles: List of allowed user roles
        
    Returns:
        Dependency function that checks user role
    """
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {[role.value for role in allowed_roles]}"
            )
        return current_user
    
    return role_checker


# Role-specific dependencies
async def get_super_admin(current_user: User = Depends(require_role([UserRole.SUPER_ADMIN]))) -> User:
    """Require super admin role"""
    return current_user


async def get_hr_user(current_user: User = Depends(require_role([UserRole.HR, UserRole.SUPER_ADMIN]))) -> User:
    """Require HR or super admin role"""
    return current_user


async def get_trainer_user(current_user: User = Depends(require_role([UserRole.TRAINER, UserRole.SUPER_ADMIN]))) -> User:
    """Require trainer or super admin role"""
    return current_user


async def get_manager_user(current_user: User = Depends(require_role([UserRole.MANAGER, UserRole.SUPER_ADMIN]))) -> User:
    """Require manager or super admin role"""
    return current_user


async def get_maverick_user(current_user: User = Depends(require_role([UserRole.MAVERICK]))) -> User:
    """Require maverick role"""
    return current_user
