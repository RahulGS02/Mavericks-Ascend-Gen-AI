"""
Maverick management API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional, List
from uuid import UUID
import logging

logger = logging.getLogger(__name__)

from ...database import get_db
from ...models.maverick import Maverick, ProfileStatus, DeploymentStatus
from ...models.user import User, UserRole
from ...schemas.maverick import (
    MaverickCreate, MaverickUpdate, MaverickResponse,
    MaverickListResponse, ProfileStatusUpdate, DeploymentStatusUpdate
)
from ...schemas.file import FileUploadResponse
from ...utils.dependencies import get_current_user, get_hr_user
from ...services import storage
from ...services.ai_service import ai_service
from ...services.document_parser import document_parser
from ...config import settings

router = APIRouter()


@router.post("/", response_model=MaverickResponse, status_code=status.HTTP_201_CREATED)
async def create_maverick(
    maverick_data: MaverickCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_hr_user)
):
    """
    Create a new maverick profile
    
    **Required role**: HR or Super Admin
    """
    # Check if email already exists
    existing = db.query(Maverick).filter(Maverick.email == maverick_data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maverick with this email already exists"
        )
    
    # Create maverick
    new_maverick = Maverick(
        name=maverick_data.name,
        email=maverick_data.email,
        phone=maverick_data.phone,
        college=maverick_data.college,
        degree=maverick_data.degree,
        branch=maverick_data.branch,
        graduation_year=maverick_data.graduation_year,
        cgpa=maverick_data.cgpa,
        skills=maverick_data.skills or [],
        resume_url=maverick_data.resume_url,
        github_url=maverick_data.github_url,
        linkedin_url=maverick_data.linkedin_url,
        profile_status=ProfileStatus.PENDING,
        deployment_status=DeploymentStatus.AVAILABLE
    )
    
    db.add(new_maverick)
    db.commit()
    db.refresh(new_maverick)
    
    return new_maverick


@router.post("/with-resume", response_model=MaverickResponse, status_code=status.HTTP_201_CREATED)
async def create_maverick_with_resume(
    name: str = Form(...),
    email: str = Form(...),
    phone: Optional[str] = Form(None),
    college: Optional[str] = Form(None),
    degree: Optional[str] = Form(None),
    branch: Optional[str] = Form(None),
    graduation_year: Optional[int] = Form(None),
    cgpa: Optional[float] = Form(None),
    github_url: Optional[str] = Form(None),
    linkedin_url: Optional[str] = Form(None),
    resume: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_hr_user)
):
    """
    Create maverick with resume upload
    
    **Required role**: HR or Super Admin
    **File types**: PDF, DOC, DOCX
    **Max size**: 5MB
    """
    # Check if email already exists
    existing = db.query(Maverick).filter(Maverick.email == email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maverick with this email already exists"
        )
    
    # Validate and upload resume
    if resume.content_type not in settings.allowed_resume_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid resume file type. Allowed: PDF, DOC, DOCX"
        )
    
    # Read and validate file size
    file_content = await resume.read()
    if len(file_content) > settings.MAX_RESUME_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Resume size exceeds 5MB limit"
        )
    
    # Upload resume
    try:
        upload_result = storage.upload_resume(
            file_content,
            resume.filename,
            resume.content_type
        )
        resume_url = upload_result["public_url"]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload resume: {str(e)}"
        )
    
    # Create maverick
    new_maverick = Maverick(
        name=name,
        email=email,
        phone=phone,
        college=college,
        degree=degree,
        branch=branch,
        graduation_year=graduation_year,
        cgpa=cgpa,
        resume_url=resume_url,
        github_url=github_url,
        linkedin_url=linkedin_url,
        profile_status=ProfileStatus.PENDING,
        deployment_status=DeploymentStatus.AVAILABLE,
        skills=[]
    )
    
    db.add(new_maverick)
    db.commit()
    db.refresh(new_maverick)
    
    return new_maverick


# ==================== MAVERICK SELF-SERVICE ENDPOINTS ====================


@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
async def register_maverick_with_profile(
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    phone: str = Form(...),
    college: str = Form(...),
    degree: str = Form(...),
    branch: str = Form(...),
    graduation_year: int = Form(...),
    cgpa: float = Form(...),
    skills: str = Form(...),
    github_url: Optional[str] = Form(None),
    linkedin_url: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Public maverick registration - Create user account + profile in one step

    This endpoint is for public self-registration. It:
    1. Creates a user account with role=MAVERICK
    2. Creates maverick profile with DRAFT status
    3. Returns access token for immediate login

    No authentication required for this endpoint.
    """
    try:
        from ...services.auth import get_password_hash, create_access_token, get_user_by_email

        # Normalize email to lowercase
        email = email.lower().strip()

        logger.info(f"Registration attempt for email: {email}")

        # Check if email already exists
        existing_user = get_user_by_email(db, email)
        if existing_user:
            logger.warning(f"Email already registered: {email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Create user account
        hashed_password = get_password_hash(password)
        new_user = User(
            email=email,
            name=name,
            password_hash=hashed_password,
            role=UserRole.MAVERICK,
            is_active=True
        )
        db.add(new_user)
        db.flush()  # Get user ID without committing

        logger.info(f"Created user account for: {email}")

        # Parse skills
        skills_list = [s.strip() for s in skills.split(",") if s.strip()]

        # Create maverick profile
        new_maverick = Maverick(
            user_id=new_user.id,
            name=name,
            email=email,
            phone=phone,
            college=college,
            degree=degree,
            branch=branch,
            graduation_year=graduation_year,
            cgpa=cgpa,
            skills=skills_list,
            github_url=github_url if github_url else None,
            linkedin_url=linkedin_url if linkedin_url else None,
            profile_status=ProfileStatus.PENDING,
            deployment_status=DeploymentStatus.AVAILABLE
        )
        db.add(new_maverick)
        db.commit()
        db.refresh(new_user)
        db.refresh(new_maverick)

        logger.info(f"Created maverick profile for: {email}")

        # Create access token with user_id (required by get_current_user dependency)
        access_token = create_access_token(data={"user_id": str(new_user.id)})

        logger.info(f"Registration successful for: {email}")

        return {
            "message": "Registration successful! Please upload your resume to complete your profile.",
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": str(new_user.id),
                "email": new_user.email,
                "name": new_user.name,
                "role": new_user.role.value
            },
            "maverick_id": str(new_maverick.id),
            "profile_status": new_maverick.profile_status.value
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error for {email}: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/my-profile", response_model=MaverickResponse, status_code=status.HTTP_201_CREATED)
async def create_my_profile(
    name: str = Form(..., description="Full name"),
    email: str = Form(..., description="Email address"),
    phone: str = Form(..., description="Phone number"),
    college: str = Form(..., description="College name"),
    degree: str = Form(..., description="Degree (e.g., B.Tech, B.E.)"),
    branch: str = Form(..., description="Branch (e.g., CSE, IT, ECE)"),
    graduation_year: int = Form(..., description="Graduation year"),
    cgpa: float = Form(..., description="CGPA (0-10)"),
    skills: str = Form(..., description="Comma-separated skills"),
    github_url: Optional[str] = Form(None, description="GitHub profile URL"),
    linkedin_url: Optional[str] = Form(None, description="LinkedIn profile URL"),
    resume: UploadFile = File(..., description="Resume PDF/DOC"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Maverick: Create own profile with all details and resume

    **Required role**: Maverick (logged in user)

    **ALL fields are required** except github_url and linkedin_url.
    Profile will be in PENDING status until HR reviews and approves.

    After approval, HR will add maverick to a batch.
    """
    # Verify user is a maverick
    if current_user.role != UserRole.MAVERICK:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only mavericks can create their own profile"
        )

    # Check if maverick profile already exists for this user
    existing = db.query(Maverick).filter(Maverick.user_id == current_user.id).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Profile already exists. Use PATCH /my-profile to update."
        )

    # Check if email already used by another maverick
    email_exists = db.query(Maverick).filter(Maverick.email == email).first()
    if email_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Validate resume file
    if not resume.content_type in settings.allowed_resume_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed: {', '.join(settings.allowed_resume_types)}"
        )

    # Read resume file
    file_content = await resume.read()

    if len(file_content) > settings.MAX_RESUME_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Resume size exceeds limit of {settings.MAX_RESUME_SIZE / 1048576}MB"
        )

    # Upload resume to storage
    try:
        upload_result = storage.upload_resume(
            file_content,
            resume.filename,
            resume.content_type
        )
        resume_url = upload_result["public_url"]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload resume: {str(e)}"
        )

    # Parse skills
    skills_list = [s.strip() for s in skills.split(",") if s.strip()]

    # AI Enhancement: Parse resume and extract information
    ai_extracted_skills = []
    ai_summary = None
    ai_resume_data = None  # Complete parsed resume data

    if await ai_service.is_available():
        try:
            # Extract text from resume
            resume_text = document_parser.extract_text(file_content, resume.content_type)

            if resume_text:
                # Parse resume comprehensively
                parsed_resume = await ai_service.parse_resume_comprehensive(resume_text)

                if parsed_resume:
                    # Store complete AI parsed data for future use
                    ai_resume_data = parsed_resume

                    # Extract all skills (flattened for easy access)
                    if parsed_resume.get("skills"):
                        skills_data = parsed_resume["skills"]
                        all_skills = []
                        all_skills.extend(skills_data.get("technical", []))
                        all_skills.extend(skills_data.get("languages", []))
                        all_skills.extend(skills_data.get("frameworks", []))
                        all_skills.extend(skills_data.get("tools", []))
                        all_skills.extend(skills_data.get("databases", []))
                        ai_extracted_skills = list(set(all_skills))  # Remove duplicates

                    # Use AI-generated summary
                    ai_summary = parsed_resume.get("summary")

                    logger.info(f"AI parsed resume: {len(ai_extracted_skills)} skills extracted, complete data stored")
        except Exception as e:
            # AI is optional - continue even if it fails
            logger.warning(f"AI resume parsing failed: {e}")

    # Create maverick profile
    new_maverick = Maverick(
        user_id=current_user.id,
        name=name,
        email=email,
        phone=phone,
        college=college,
        degree=degree,
        branch=branch,
        graduation_year=graduation_year,
        cgpa=cgpa,
        skills=skills_list,
        resume_url=resume_url,
        github_url=github_url,
        linkedin_url=linkedin_url,
        ai_extracted_skills=ai_extracted_skills,
        ai_summary=ai_summary,
        ai_resume_data=ai_resume_data,  # Store complete parsed resume
        profile_status=ProfileStatus.PENDING,
        deployment_status=DeploymentStatus.AVAILABLE
    )

    db.add(new_maverick)
    db.commit()
    db.refresh(new_maverick)

    return new_maverick


@router.get("/my-profile", response_model=MaverickResponse)
async def get_my_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Maverick: Get own profile

    **Required role**: Maverick (logged in user)
    """
    if current_user.role != UserRole.MAVERICK:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only mavericks can access their profile via this endpoint"
        )

    maverick = db.query(Maverick).filter(Maverick.user_id == current_user.id).first()

    if not maverick:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found. Please create your profile first."
        )

    return maverick


@router.patch("/my-profile", response_model=MaverickResponse)
async def update_my_profile(
    phone: Optional[str] = Form(None),
    skills: Optional[str] = Form(None, description="Comma-separated skills"),
    github_url: Optional[str] = Form(None),
    linkedin_url: Optional[str] = Form(None),
    resume: Optional[UploadFile] = File(None, description="Updated resume"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Maverick: Update own profile

    **Required role**: Maverick (logged in user)

    Can update: phone, skills, github_url, linkedin_url, resume
    Cannot update: name, email, college, degree, branch, graduation_year, cgpa
    (Contact HR to update those fields)
    """
    if current_user.role != UserRole.MAVERICK:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only mavericks can update their profile"
        )

    maverick = db.query(Maverick).filter(Maverick.user_id == current_user.id).first()

    if not maverick:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found. Please create your profile first."
        )

    # Update fields
    if phone is not None:
        maverick.phone = phone

    if skills is not None:
        maverick.skills = [s.strip() for s in skills.split(",") if s.strip()]

    if github_url is not None:
        maverick.github_url = github_url

    if linkedin_url is not None:
        maverick.linkedin_url = linkedin_url

    # Update resume if provided
    if resume:
        # Validate file type
        if not resume.content_type in settings.allowed_resume_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file type. Allowed: {', '.join(settings.allowed_resume_types)}"
            )

        file_content = await resume.read()

        if len(file_content) > settings.MAX_RESUME_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Resume size exceeds limit of {settings.MAX_RESUME_SIZE / 1048576}MB"
            )

        # Upload new resume
        try:
            upload_result = storage.upload_resume(
                file_content,
                resume.filename,
                resume.content_type
            )
            maverick.resume_url = upload_result["public_url"]

            # Re-parse resume with AI if enabled
            if await ai_service.is_available():
                try:
                    logger.info(f"Extracting text from resume: {resume.filename}, type: {resume.content_type}, size: {len(file_content)} bytes")

                    # Check if it's a valid PDF
                    if file_content[:4] == b'%PDF':
                        logger.info("✅ File is a valid PDF (starts with %PDF)")
                    else:
                        logger.warning(f"⚠️ File doesn't start with PDF header. First 20 bytes: {file_content[:20]}")

                    resume_text = document_parser.extract_text(file_content, resume.content_type)

                    if not resume_text:
                        logger.error("❌ Failed to extract text from PDF - resume_text is empty")
                        logger.error(f"File details: {len(file_content)} bytes, Content-Type: {resume.content_type}")
                        logger.error("Possible reasons: 1) Image-based PDF (needs OCR), 2) Encrypted PDF, 3) Corrupted file")
                    else:
                        logger.info(f"✅ Successfully extracted {len(resume_text)} characters from resume")

                    if resume_text:
                        logger.info(f"Extracted {len(resume_text)} characters from resume")
                        parsed_resume = await ai_service.parse_resume_comprehensive(resume_text)
                        if parsed_resume:
                            # Store complete parsed data
                            maverick.ai_resume_data = parsed_resume

                            # Extract skills (flattened)
                            if parsed_resume.get("skills"):
                                skills_data = parsed_resume["skills"]
                                all_skills = []
                                all_skills.extend(skills_data.get("technical", []))
                                all_skills.extend(skills_data.get("languages", []))
                                all_skills.extend(skills_data.get("frameworks", []))
                                all_skills.extend(skills_data.get("tools", []))
                                all_skills.extend(skills_data.get("databases", []))
                                maverick.ai_extracted_skills = list(set(all_skills))

                            # Update summary if available
                            if parsed_resume.get("summary"):
                                maverick.ai_summary = parsed_resume["summary"]

                            logger.info(f"AI re-parsed resume: {len(maverick.ai_extracted_skills)} skills, complete data updated")
                except Exception as e:
                    logger.warning(f"AI resume re-parsing failed: {e}")

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload resume: {str(e)}"
            )

    db.commit()
    db.refresh(maverick)

    return maverick


@router.get("/", response_model=MaverickListResponse)
async def get_mavericks(
    page: int = 1,
    page_size: int = 20,
    search: Optional[str] = None,
    profile_status: Optional[str] = None,
    deployment_status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get list of mavericks with pagination and filters
    
    **Query params**:
    - page: Page number (default 1)
    - page_size: Items per page (default 20)
    - search: Search by name, email, college
    - profile_status: Filter by status (pending, approved, rejected)
    - deployment_status: Filter by status (available, deployed, on_bench)
    """
    query = db.query(Maverick)
    
    # Apply filters
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (Maverick.name.ilike(search_filter)) |
            (Maverick.email.ilike(search_filter)) |
            (Maverick.college.ilike(search_filter))
        )
    
    if profile_status:
        try:
            status_enum = ProfileStatus(profile_status)
            query = query.filter(Maverick.profile_status == status_enum)
        except ValueError:
            pass
    
    if deployment_status:
        try:
            status_enum = DeploymentStatus(deployment_status)
            query = query.filter(Maverick.deployment_status == status_enum)
        except ValueError:
            pass
    
    # Get total count
    total = query.count()
    
    # Calculate pagination
    total_pages = (total + page_size - 1) // page_size
    offset = (page - 1) * page_size
    
    # Get mavericks
    mavericks = query.offset(offset).limit(page_size).all()
    
    return MaverickListResponse(
        mavericks=mavericks,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/{maverick_id}", response_model=MaverickResponse)
async def get_maverick_by_id(
    maverick_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get maverick by ID

    **Path params**:
    - maverick_id: UUID of the maverick
    """
    maverick = db.query(Maverick).filter(Maverick.id == maverick_id).first()

    if not maverick:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Maverick not found"
        )

    return maverick


@router.put("/{maverick_id}", response_model=MaverickResponse)
async def update_maverick(
    maverick_id: str,
    maverick_data: MaverickUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_hr_user)
):
    """
    Update maverick profile

    **Required role**: HR or Super Admin
    """
    from ...models.batch import Batch

    maverick = db.query(Maverick).filter(Maverick.id == maverick_id).first()

    if not maverick:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Maverick not found"
        )

    # Handle batch assignment changes
    update_data = maverick_data.model_dump(exclude_unset=True)
    if 'current_batch_id' in update_data:
        old_batch_id = maverick.current_batch_id
        new_batch_id = update_data['current_batch_id']

        # If batch changed
        if old_batch_id != new_batch_id:
            # Decrement old batch enrollment
            if old_batch_id:
                old_batch = db.query(Batch).filter(Batch.id == old_batch_id).first()
                if old_batch and old_batch.current_enrollment > 0:
                    old_batch.current_enrollment -= 1

            # Increment new batch enrollment
            if new_batch_id:
                new_batch = db.query(Batch).filter(Batch.id == new_batch_id).first()
                if new_batch:
                    # Check capacity
                    if new_batch.max_capacity and new_batch.current_enrollment >= new_batch.max_capacity:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Batch is at full capacity ({new_batch.max_capacity})"
                        )
                    new_batch.current_enrollment += 1
                else:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="New batch not found"
                    )

    # Update other fields
    for field, value in update_data.items():
        setattr(maverick, field, value)

    db.commit()
    db.refresh(maverick)

    return maverick


@router.patch("/{maverick_id}", response_model=MaverickResponse)
async def patch_maverick(
    maverick_id: str,
    maverick_data: MaverickUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Partially update maverick profile (same as PUT but allows any authenticated user for batch updates)

    **Required role**: Any authenticated user
    """
    from ...models.batch import Batch

    maverick = db.query(Maverick).filter(Maverick.id == maverick_id).first()

    if not maverick:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Maverick not found"
        )

    # Handle batch assignment changes
    update_data = maverick_data.model_dump(exclude_unset=True)
    if 'current_batch_id' in update_data:
        old_batch_id = maverick.current_batch_id
        new_batch_id = update_data['current_batch_id']

        # If batch changed
        if old_batch_id != new_batch_id:
            # Decrement old batch enrollment
            if old_batch_id:
                old_batch = db.query(Batch).filter(Batch.id == old_batch_id).first()
                if old_batch and old_batch.current_enrollment > 0:
                    old_batch.current_enrollment -= 1

            # Increment new batch enrollment (if not None - None means removing from batch)
            if new_batch_id:
                new_batch = db.query(Batch).filter(Batch.id == new_batch_id).first()
                if new_batch:
                    # Check capacity
                    if new_batch.max_capacity and new_batch.current_enrollment >= new_batch.max_capacity:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Batch is at full capacity ({new_batch.max_capacity})"
                        )
                    new_batch.current_enrollment += 1
                else:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="New batch not found"
                    )

    # Update fields
    for field, value in update_data.items():
        setattr(maverick, field, value)

    db.commit()
    db.refresh(maverick)

    return maverick


@router.patch("/{maverick_id}/profile-status", response_model=MaverickResponse)
async def update_profile_status(
    maverick_id: str,
    status_data: ProfileStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_hr_user)
):
    """
    Update maverick profile status (approve/reject)

    **Required role**: HR or Super Admin
    **Allowed statuses**: pending, approved, rejected
    """
    maverick = db.query(Maverick).filter(Maverick.id == maverick_id).first()

    if not maverick:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Maverick not found"
        )

    # Validate status
    try:
        profile_status = ProfileStatus(status_data.profile_status)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid profile status. Must be: pending, approved, rejected"
        )

    # Update status
    maverick.profile_status = profile_status
    maverick.reviewed_by = str(current_user.id)
    if status_data.review_notes:
        maverick.review_notes = status_data.review_notes

    db.commit()
    db.refresh(maverick)

    return maverick


@router.patch("/{maverick_id}/deployment-status", response_model=MaverickResponse)
async def update_deployment_status(
    maverick_id: str,
    status_data: DeploymentStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_hr_user)
):
    """
    Update maverick deployment status

    **Required role**: HR or Super Admin
    **Allowed statuses**: available, deployed, on_bench
    """
    maverick = db.query(Maverick).filter(Maverick.id == maverick_id).first()

    if not maverick:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Maverick not found"
        )

    # Validate status
    try:
        deployment_status = DeploymentStatus(status_data.deployment_status)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid deployment status. Must be: available, deployed, on_bench"
        )

    # Update status
    maverick.deployment_status = deployment_status

    db.commit()
    db.refresh(maverick)

    return maverick


@router.delete("/{maverick_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_maverick(
    maverick_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_hr_user)
):
    """
    Delete maverick profile

    **Required role**: HR or Super Admin
    **Warning**: This will permanently delete the maverick and all related data
    """
    maverick = db.query(Maverick).filter(Maverick.id == maverick_id).first()

    if not maverick:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Maverick not found"
        )

    # Delete resume from storage if exists
    if maverick.resume_url:
        try:
            file_path = maverick.resume_url.split("/")[-1]
            storage.delete_file(file_path, "resumes")
        except Exception as e:
            print(f"Error deleting resume: {e}")

    db.delete(maverick)
    db.commit()

    return None
