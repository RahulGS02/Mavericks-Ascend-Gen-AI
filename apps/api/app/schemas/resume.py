"""
Resume parsing schemas
"""
from pydantic import BaseModel
from typing import Optional, List


class PersonalInfo(BaseModel):
    """Personal information from resume"""
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    portfolio: Optional[str] = None


class Education(BaseModel):
    """Education details"""
    degree: str
    branch: Optional[str] = None
    college: str
    university: Optional[str] = None
    year: Optional[int] = None
    cgpa: Optional[float] = None
    percentage: Optional[float] = None


class Experience(BaseModel):
    """Work experience details"""
    company: str
    role: str
    duration: str
    years: Optional[float] = None
    location: Optional[str] = None
    description: Optional[str] = None
    technologies: List[str] = []


class Skills(BaseModel):
    """Categorized skills"""
    technical: List[str] = []
    soft_skills: List[str] = []
    languages: List[str] = []
    frameworks: List[str] = []
    tools: List[str] = []
    databases: List[str] = []


class Project(BaseModel):
    """Project details"""
    name: str
    description: Optional[str] = None
    technologies: List[str] = []
    role: Optional[str] = None
    duration: Optional[str] = None
    url: Optional[str] = None


class Certification(BaseModel):
    """Certification details"""
    name: str
    issuer: Optional[str] = None
    year: Optional[int] = None


class ParsedResumeData(BaseModel):
    """Complete parsed resume data"""
    personal_info: PersonalInfo
    education: List[Education] = []
    experience: List[Experience] = []
    skills: Skills
    projects: List[Project] = []
    certifications: List[Certification] = []
    total_experience_years: float = 0.0
    summary: Optional[str] = None


class ResumeParseResponse(BaseModel):
    """Response for resume parsing"""
    success: bool
    parsed_data: Optional[ParsedResumeData] = None
    extracted_text_length: int
    ai_skills: List[str] = []
    ai_summary: Optional[str] = None
    message: str
