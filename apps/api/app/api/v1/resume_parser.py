"""
Resume Parser API
Extract structured data from resumes using AI
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models.user import User
from app.services.auth import get_current_user
from app.services.ai_service import ai_service
from app.services.document_parser import document_parser
from app.schemas.resume import ResumeParseResponse, ParsedResumeData
from app.config import settings


router = APIRouter()


@router.post("/parse", response_model=ResumeParseResponse)
async def parse_resume(
    resume: UploadFile = File(..., description="Resume file (PDF or DOCX)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Parse resume and extract structured information using AI
    
    **Required role**: Any authenticated user
    
    **Accepts**: PDF, DOCX files
    
    **Extracts**:
    - Personal information (name, email, phone, links)
    - Education history (degree, college, CGPA, year)
    - Work experience (company, role, duration, technologies)
    - Skills (technical, soft skills, languages, frameworks, tools, databases)
    - Projects (name, description, technologies)
    - Certifications
    - Total experience years
    - Professional summary
    
    **AI Features**:
    - Comprehensive resume parsing
    - Skill extraction and categorization
    - Experience calculation
    - Professional summary generation
    """
    
    # Validate file type
    if resume.content_type not in settings.allowed_resume_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed: PDF, DOC, DOCX"
        )
    
    # Read file
    file_content = await resume.read()
    
    if len(file_content) > settings.MAX_RESUME_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds limit of {settings.MAX_RESUME_SIZE / 1048576}MB"
        )
    
    # Extract text from document
    extracted_text = document_parser.extract_text(file_content, resume.content_type)
    
    if not extracted_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to extract text from resume. Please ensure the file is not corrupted."
        )
    
    # Check if AI is available
    if not await ai_service.is_available():
        return ResumeParseResponse(
            success=False,
            parsed_data=None,
            extracted_text_length=len(extracted_text),
            ai_skills=[],
            ai_summary=None,
            message="AI service not available. Text extracted but not parsed."
        )
    
    # Parse resume using AI
    parsed_data_dict = await ai_service.parse_resume_comprehensive(extracted_text)
    
    if not parsed_data_dict:
        return ResumeParseResponse(
            success=False,
            parsed_data=None,
            extracted_text_length=len(extracted_text),
            ai_skills=[],
            ai_summary=None,
            message="AI parsing failed. Text extracted successfully."
        )
    
    # Convert to Pydantic model
    try:
        parsed_data = ParsedResumeData(**parsed_data_dict)
        
        # Extract all technical skills for ai_skills field
        all_skills = []
        if parsed_data.skills:
            all_skills.extend(parsed_data.skills.technical)
            all_skills.extend(parsed_data.skills.languages)
            all_skills.extend(parsed_data.skills.frameworks)
            all_skills.extend(parsed_data.skills.tools)
            all_skills.extend(parsed_data.skills.databases)
        
        # Remove duplicates
        ai_skills = list(set(all_skills))
        
        return ResumeParseResponse(
            success=True,
            parsed_data=parsed_data,
            extracted_text_length=len(extracted_text),
            ai_skills=ai_skills,
            ai_summary=parsed_data.summary,
            message=f"Resume parsed successfully. Extracted {len(ai_skills)} skills, "
                   f"{len(parsed_data.experience)} experiences, "
                   f"{len(parsed_data.projects)} projects."
        )
    
    except Exception as e:
        # Return raw data if Pydantic validation fails
        return ResumeParseResponse(
            success=False,
            parsed_data=None,
            extracted_text_length=len(extracted_text),
            ai_skills=[],
            ai_summary=None,
            message=f"Parsing validation failed: {str(e)}"
        )
