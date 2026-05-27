"""
Authentication service for password hashing and verification
"""
# Use bcrypt directly — passlib 1.7.4 is incompatible with bcrypt >= 4.0.
# passlib's detect_wrap_bug() passes a >72-byte password which bcrypt 4.x
# rejects with ValueError, crashing login with HTTP 500.
import bcrypt as _bcrypt
from datetime import datetime, timedelta
from jose import jwt, JWTError
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from ..config import settings
from ..models.user import User, UserRole
from ..database import get_db
from sqlalchemy.orm import Session


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a bcrypt hash.
    Uses bcrypt library directly (bypasses passlib incompatibility).
    """
    try:
        pw_bytes   = plain_password.encode("utf-8")
        hash_bytes = (
            hashed_password.encode("utf-8")
            if isinstance(hashed_password, str)
            else hashed_password
        )
        return _bcrypt.checkpw(pw_bytes, hash_bytes)
    except Exception:
        return False


def get_password_hash(password: str) -> str:
    """
    Hash a plain password with bcrypt (cost factor 12).
    Uses bcrypt library directly (bypasses passlib incompatibility).
    """
    return _bcrypt.hashpw(
        password.encode("utf-8"),
        _bcrypt.gensalt(rounds=12),
    ).decode("utf-8")


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """
    Create a JWT access token
    
    Args:
        data: Dictionary of data to encode in token
        expires_delta: Optional expiration time delta
        
    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """
    Decode and verify a JWT access token

    Args:
        token: JWT token string

    Returns:
        Decoded token payload

    Raises:
        JWTError: If token is invalid or expired
    """
    payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    return payload


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """
    Authenticate a user with email and password

    Args:
        db: Database session
        email: User email
        password: Plain text password

    Returns:
        User object if authentication successful, None otherwise
    """
    # Case-insensitive email lookup
    user = db.query(User).filter(User.email.ilike(email)).first()

    if not user:
        return None

    if not verify_password(password, user.password_hash):
        return None

    return user


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """
    Get user by email address

    Args:
        db: Database session
        email: User email

    Returns:
        User object if found, None otherwise
    """
    # Case-insensitive email lookup
    return db.query(User).filter(User.email.ilike(email)).first()


# Security scheme for JWT bearer token
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT token

    Args:
        credentials: HTTP Authorization credentials with bearer token
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
        # Try both "sub" (standard) and "user_id" (our custom field)
        user_id: str = payload.get("sub") or payload.get("user_id")

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


async def get_hr_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Verify that current user has HR or SUPER_ADMIN role

    Args:
        current_user: Current authenticated user

    Returns:
        Current user if authorized

    Raises:
        HTTPException: If user doesn't have required role
    """
    if current_user.role not in [UserRole.HR, UserRole.SUPER_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only HR or Super Admin can access this resource"
        )

    return current_user


async def get_trainer_or_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    Verify that current user has TRAINER, HR, or SUPER_ADMIN role

    Args:
        current_user: Current authenticated user

    Returns:
        Current user if authorized

    Raises:
        HTTPException: If user doesn't have required role
    """
    if current_user.role not in [UserRole.TRAINER, UserRole.HR, UserRole.SUPER_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Trainer, HR, or Super Admin can access this resource"
        )

    return current_user
