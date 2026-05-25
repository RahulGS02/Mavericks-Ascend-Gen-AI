"""
Talent Search Request/Response Schemas
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime


class TalentSearchRequest(BaseModel):
    """Request schema for AI-powered talent search"""
    query: str = Field(..., description="Natural language search query")
    max_results: int = Field(50, ge=1, le=100, description="Maximum results to return")
    include_similar: bool = Field(False, description="Include candidates with similar/transferable skills")
    urgency: Optional[str] = Field("flexible", description="immediate | flexible")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "Need .NET developer with Azure experience and CGPA > 8",
                "max_results": 50,
                "include_similar": False,
                "urgency": "immediate"
            }
        }


class SkillMatch(BaseModel):
    """Exact skill match details"""
    skill: str
    candidate_has: Optional[str] = None
    proficiency_score: float
    proficiency_level: str
    assessment_validated: bool
    points: float


class SimilarSkillMatch(BaseModel):
    """Similar skill match details"""
    required_skill: str
    candidate_has: str
    similarity_score: int  # 70-95
    proficiency_score: float
    proficiency_level: str
    learning_weeks: float
    difficulty: str
    assessment_validated: bool
    points: float


class TransferableSkillMatch(BaseModel):
    """Transferable skill match details"""
    required_skill: str
    candidate_has: str
    transferability_score: int  # 50-70
    proficiency_score: float
    proficiency_level: str
    learning_weeks: float
    difficulty: str
    assessment_validated: bool
    points: float


class AssessmentSummary(BaseModel):
    """Candidate's assessment performance summary"""
    average_score: float
    total_assessments: int
    passed_assessments: int
    pass_rate: float
    trend: str  # "improving" | "stable" | "declining"
    recent_activity: int  # assessments in last 3 months


class TrainingPhase(BaseModel):
    """Training phase details"""
    phase: str
    weeks: float
    focus: str


class TrainingItem(BaseModel):
    """Training plan item"""
    skill: str
    duration_weeks: float
    difficulty: str
    core_concepts: List[str] = []
    prerequisites: List[str] = []
    learning_path: List[TrainingPhase] = []


class CandidateMatch(BaseModel):
    """Individual candidate match result"""
    # Candidate info
    id: UUID
    name: str
    email: str
    cgpa: Optional[float]
    deployment_status: str
    profile_status: str
    
    # Scoring
    final_score: float  # 0-100
    tier: str  # TIER_1_EXACT | TIER_2_SIMILAR | TIER_3_TRANSFERABLE
    
    # Skill analysis
    exact_matches: List[SkillMatch]
    similar_matches: List[SimilarSkillMatch] = []
    transferable_matches: List[TransferableSkillMatch] = []
    missing_skills: List[str] = []
    
    # Performance metrics
    assessment_performance: Optional[AssessmentSummary]
    adaptability_score: float
    adaptability_interpretation: str
    
    # Recommendations
    deployment_readiness: str  # immediate | short_term | medium_term | long_term
    learning_weeks_required: float
    training_plan: List[TrainingItem] = []
    match_reasoning: str


class SearchSummary(BaseModel):
    """Search results summary"""
    total_found: int
    exact_matches: int
    similar_skill_candidates: int
    transferable_skill_candidates: int
    immediate_deployment: int  # Ready now
    short_training_needed: int  # 1-4 weeks
    longer_training_needed: int  # 4+ weeks
    show_similar_button: bool  # True if exact_matches <= 2
    similar_available: int  # How many similar candidates are available


class CostBreakdown(BaseModel):
    """AI cost analysis"""
    query_parsing_tokens: int
    query_parsing_cost: float
    ranking_tokens: int
    ranking_cost: float
    total_tokens: int
    total_cost: float


class TalentSearchResponse(BaseModel):
    """Response schema for talent search"""
    query: str
    search_strategy: str  # "exact_only" | "with_similar"
    parsed_requirements: Dict[str, Any]
    
    total_found: int
    results: List[CandidateMatch]
    
    summary: SearchSummary
    cost_analysis: CostBreakdown
    
    # Message to display
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ExplainRequest(BaseModel):
    """Request to explain why a candidate was suggested"""
    candidate_id: UUID
    required_skills: List[str]


class ExplanationResponse(BaseModel):
    """Detailed explanation of candidate match"""
    candidate_id: UUID
    candidate_name: str
    
    skill_gap_analysis: Dict[str, Any]
    learning_path: List[TrainingItem]
    adaptability_breakdown: Dict[str, Any]
    
    timeline_estimate: Dict[str, Any]
    match_reasoning: str
    recommendation: str
