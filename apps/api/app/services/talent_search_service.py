"""
TalentSearchService - AI-Powered Intelligent Talent Search
Orchestrates the complete talent search workflow with intelligent skill matching
"""
import logging
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from datetime import datetime, timedelta
from uuid import UUID

from ..models.maverick import Maverick, ProfileStatus, DeploymentStatus
from ..models.maverick_skill import MaverickSkill, ProficiencyLevel
from ..models.assessment import AssessmentAttempt
from ..schemas.talent_search import (
    TalentSearchRequest,
    TalentSearchResponse,
    CandidateMatch,
    SkillMatch,
    SimilarSkillMatch,
    TransferableSkillMatch,
    AssessmentSummary,
    TrainingItem,
    TrainingPhase,
    SearchSummary,
    CostBreakdown
)
from .skill_similarity_engine import SkillSimilarityEngine
from .ai_service import ai_service
from ..logging_config import get_talent_search_logger

# Use dedicated talent search logger
logger = get_talent_search_logger()


class TalentSearchService:
    """
    Main orchestrator for AI-powered talent search
    
    Workflow:
    1. Parse natural language query using AI → extract skills, CGPA, etc.
    2. SQL pre-filter: deployment_status=AVAILABLE & profile_status=APPROVED
    3. For each candidate:
       a. Calculate skill match score (exact/similar/transferable)
       b. Calculate adaptability score (learning potential)
       c. Estimate learning timeline
       d. Generate training plan
    4. Tier candidates: TIER_1_EXACT, TIER_2_SIMILAR, TIER_3_TRANSFERABLE
    5. Return top N matches with "Show Similar" button if exact ≤ 2
    """
    
    def __init__(self):
        self.skill_engine = SkillSimilarityEngine()
        self.ai_service = ai_service
    
    async def search(
        self,
        request: TalentSearchRequest,
        db: Session
    ) -> TalentSearchResponse:
        """
        Main search endpoint - returns top talent matches
        
        Args:
            request: TalentSearchRequest with natural language query
            db: Database session
            
        Returns:
            TalentSearchResponse with ranked candidates
        """
        logger.info(f"Starting AI talent search: {request.query}")
        
        # Track AI usage
        ai_tokens_used = 0
        ai_cost = 0.0
        
        # Step 1: Parse natural language query using AI
        parsed_requirements = await self._parse_query_with_ai(request.query)
        ai_tokens_used += parsed_requirements.get("tokens_used", 0)
        
        # Step 2: SQL Pre-filter - Get AVAILABLE and APPROVED candidates
        candidate_pool = self._get_available_candidates(
            db=db,
            min_cgpa=parsed_requirements.get("min_cgpa"),
            graduation_year=parsed_requirements.get("graduation_year"),
            degree=parsed_requirements.get("degree"),
            branch=parsed_requirements.get("branch")
        )
        
        logger.info(f"Candidate pool after SQL filter: {len(candidate_pool)}")
        
        # Step 3: Score each candidate using SkillSimilarityEngine
        required_skills = parsed_requirements.get("required_skills", [])
        preferred_skills = parsed_requirements.get("preferred_skills", [])
        all_skills = required_skills + preferred_skills
        
        scored_candidates = []
        for candidate in candidate_pool:
            candidate_result = await self._score_candidate(
                maverick=candidate,
                required_skills=all_skills,
                db=db
            )
            if candidate_result:
                scored_candidates.append(candidate_result)
        
        # Step 4: Determine strategy and filter results
        exact_matches = [c for c in scored_candidates if c["tier"] == "TIER_1_EXACT"]
        similar_matches = [c for c in scored_candidates if c["tier"] in ["TIER_2_SIMILAR", "TIER_3_TRANSFERABLE"]]
        
        # Decision: Show similar if exact ≤ 2 OR user explicitly requested
        show_similar = len(exact_matches) <= 2 or request.include_similar
        
        if show_similar:
            final_results = exact_matches + similar_matches
            search_strategy = "with_similar"
            message = f"Found {len(exact_matches)} exact matches. Showing {len(similar_matches)} candidates with similar skills."
        else:
            final_results = exact_matches
            search_strategy = "exact_only"
            message = f"Found {len(exact_matches)} exact matches."
        
        # Step 5: Sort by final_score and limit
        final_results.sort(key=lambda x: x["final_score"], reverse=True)
        final_results = final_results[:request.max_results]
        
        # Step 6: Convert to response schema
        candidate_matches = [self._to_candidate_match(r) for r in final_results]
        
        # Step 7: Build summary
        summary = self._build_summary(
            scored_candidates=scored_candidates,
            exact_matches=exact_matches,
            similar_matches=similar_matches,
            show_similar=show_similar
        )
        
        # Step 8: Cost analysis
        cost_breakdown = CostBreakdown(
            query_parsing_tokens=parsed_requirements.get("tokens_used", 0),
            query_parsing_cost=parsed_requirements.get("cost", 0.0),
            ranking_tokens=0,  # We use rules-based scoring
            ranking_cost=0.0,
            total_tokens=parsed_requirements.get("tokens_used", 0),
            total_cost=parsed_requirements.get("cost", 0.0)
        )
        
        return TalentSearchResponse(
            query=request.query,
            search_strategy=search_strategy,
            parsed_requirements=parsed_requirements,
            total_found=len(final_results),
            results=candidate_matches,
            summary=summary,
            cost_analysis=cost_breakdown,
            message=message
        )

    async def _parse_query_with_ai(self, query: str) -> Dict[str, Any]:
        """
        Use AI to parse natural language query into structured requirements

        Example: "Need .NET developer with Azure, CGPA > 8"
        Returns: {
            "required_skills": [".NET", "Azure"],
            "preferred_skills": [],
            "min_cgpa": 8.0,
            "graduation_year": None,
            "degree": None,
            "branch": None,
            "tokens_used": 150,
            "cost": 0.0015
        }
        """
        if not await self.ai_service.is_available():
            logger.warning("AI not available, using basic parsing")
            # Fallback: basic keyword extraction
            return {
                "required_skills": [],
                "preferred_skills": [],
                "min_cgpa": None,
                "tokens_used": 0,
                "cost": 0.0
            }

        system_prompt = """You are an expert at parsing job requirements from natural language.
Extract structured information and return ONLY valid JSON with this exact format:
{
    "required_skills": ["skill1", "skill2"],
    "preferred_skills": ["skill3"],
    "min_cgpa": 8.0,
    "graduation_year": 2024,
    "degree": "B.Tech",
    "branch": "Computer Science"
}

Rules:
- Extract technical skills mentioned (programming languages, frameworks, tools, platforms)
- Identify CGPA requirements (look for phrases like "CGPA > 8", "minimum CGPA 7.5")
- Identify education filters (graduation year, degree, branch)
- Use null for missing fields
- Return valid JSON only, no markdown or extra text"""

        prompt = f"Extract requirements from this search query:\n\n{query}"

        try:
            response = await self.ai_service._call_ai(
                prompt=prompt,
                system_prompt=system_prompt,
                feature="talent_search_query_parsing",
                max_tokens=500,
                temperature=0.1
            )

            if response:
                import json
                logger.info(f"AI response received: {response[:200]}...")  # Log first 200 chars

                # Clean response - remove markdown code blocks if present
                cleaned_response = response.strip()
                if cleaned_response.startswith("```json"):
                    cleaned_response = cleaned_response[7:]
                if cleaned_response.startswith("```"):
                    cleaned_response = cleaned_response[3:]
                if cleaned_response.endswith("```"):
                    cleaned_response = cleaned_response[:-3]
                cleaned_response = cleaned_response.strip()

                parsed = json.loads(cleaned_response)
                parsed["tokens_used"] = 500  # Approximate
                parsed["cost"] = 0.0015  # Approximate $0.003 per 1K tokens
                logger.info(f"Successfully parsed query, found {len(parsed.get('required_skills', []))} required skills")
                return parsed
            else:
                logger.warning("AI service returned None/empty response")

        except json.JSONDecodeError as e:
            logger.error(f"AI query parsing failed - JSON decode error: {e}")
            logger.error(f"Response was: {response[:500] if response else 'None'}")
        except Exception as e:
            logger.error(f"AI query parsing failed: {e}")

        # Fallback
        return {
            "required_skills": [],
            "preferred_skills": [],
            "min_cgpa": None,
            "tokens_used": 0,
            "cost": 0.0
        }

    def _get_available_candidates(
        self,
        db: Session,
        min_cgpa: Optional[float] = None,
        graduation_year: Optional[int] = None,
        degree: Optional[str] = None,
        branch: Optional[str] = None
    ) -> List[Maverick]:
        """
        SQL pre-filter: Get AVAILABLE and APPROVED candidates

        This drastically reduces AI token costs by filtering out:
        - Deployed candidates
        - Pending/rejected profiles
        - Candidates not meeting basic criteria
        """
        query = db.query(Maverick).filter(
            and_(
                Maverick.deployment_status == DeploymentStatus.AVAILABLE,
                Maverick.profile_status == ProfileStatus.APPROVED
            )
        )

        # Apply additional filters
        if min_cgpa is not None:
            query = query.filter(Maverick.cgpa >= min_cgpa)

        if graduation_year is not None:
            query = query.filter(Maverick.graduation_year == graduation_year)

        if degree:
            query = query.filter(Maverick.degree.ilike(f"%{degree}%"))

        if branch:
            query = query.filter(Maverick.branch.ilike(f"%{branch}%"))

        return query.all()

    async def _score_candidate(
        self,
        maverick: Maverick,
        required_skills: List[str],
        db: Session
    ) -> Optional[Dict[str, Any]]:
        """
        Score a single candidate using SkillSimilarityEngine

        Returns:
            {
                "maverick": Maverick object,
                "final_score": 85.5,
                "tier": "TIER_1_EXACT",
                "skill_match_result": {...},
                "adaptability_result": {...},
                "timeline_result": {...},
                "assessment_summary": {...}
            }
        """
        # Get candidate's skills from maverick_skills table
        candidate_skills = db.query(MaverickSkill).filter(
            MaverickSkill.maverick_id == maverick.id
        ).all()

        if not candidate_skills:
            logger.warning(f"⚠️ Candidate {maverick.name} (ID: {maverick.id}) has NO SKILLS in maverick_skills table - SKIPPING")
            logger.warning(f"   Self-declared skills: {maverick.skills}")
            logger.warning(f"   AI extracted skills: {maverick.ai_extracted_skills}")
            return None

        # Calculate skill match score
        skill_match_result = self.skill_engine.calculate_skill_match_score(
            candidate_skills=candidate_skills,
            required_skills=required_skills
        )

        # Skip if no match at all
        if skill_match_result["match_type"] == "NO_MATCH":
            return None

        # Calculate adaptability score
        adaptability_result = self.skill_engine.calculate_adaptability_score(
            maverick=maverick,
            db=db
        )

        # Estimate learning timeline
        timeline_result = self.skill_engine.estimate_learning_timeline(
            candidate_skills=candidate_skills,
            missing_skills=skill_match_result["missing_skills"],
            adaptability_score=adaptability_result["adaptability_score"],
            skill_match_details=skill_match_result
        )

        # Get assessment summary
        assessment_summary = self._get_assessment_summary(maverick, db)

        # Determine tier
        tier = self._determine_tier(skill_match_result)

        # Calculate final score (0-100)
        final_score = self._calculate_final_score(
            skill_match_score=skill_match_result["total_score"],
            adaptability_score=adaptability_result["adaptability_score"],
            assessment_avg=assessment_summary["average_score"],
            cgpa=maverick.cgpa or 0,
            tier=tier
        )

        return {
            "maverick": maverick,
            "final_score": final_score,
            "tier": tier,
            "skill_match_result": skill_match_result,
            "adaptability_result": adaptability_result,
            "timeline_result": timeline_result,
            "assessment_summary": assessment_summary
        }

    def _determine_tier(self, skill_match_result: Dict[str, Any]) -> str:
        """
        Determine candidate tier based on match type

        TIER_1_EXACT: Has all or most required skills
        TIER_2_SIMILAR: Has similar skills (70-95% similarity)
        TIER_3_TRANSFERABLE: Has transferable skills (50-70% similarity)
        """
        match_type = skill_match_result["match_type"]

        if match_type == "PERFECT_MATCH":
            return "TIER_1_EXACT"
        elif match_type == "EXACT_MATCH":
            return "TIER_1_EXACT"
        elif match_type == "SIMILAR_MATCH":
            return "TIER_2_SIMILAR"
        elif match_type == "TRANSFERABLE_MATCH":
            return "TIER_3_TRANSFERABLE"
        elif match_type == "PARTIAL_MATCH":
            # Check if has any exact matches
            if skill_match_result.get("exact_matches"):
                return "TIER_1_EXACT"
            elif skill_match_result.get("similar_matches"):
                return "TIER_2_SIMILAR"
            else:
                return "TIER_3_TRANSFERABLE"
        else:
            return "TIER_3_TRANSFERABLE"

    def _calculate_final_score(
        self,
        skill_match_score: float,
        adaptability_score: float,
        assessment_avg: float,
        cgpa: float,
        tier: str
    ) -> float:
        """
        Calculate composite final score (0-100)

        Weights:
        - Skill Match: 50%
        - Adaptability: 25%
        - Assessment Avg: 15%
        - CGPA: 10%

        Tier bonus:
        - TIER_1: +0 points (baseline)
        - TIER_2: -5 points (similar skills)
        - TIER_3: -10 points (transferable skills)
        """
        weights = {
            "skill_match": 0.50,
            "adaptability": 0.25,
            "assessment": 0.15,
            "cgpa": 0.10
        }

        # Normalize CGPA to 0-100 scale (assuming 10 is max)
        cgpa_normalized = (cgpa / 10.0) * 100 if cgpa else 0

        # Convert Decimal to float to avoid type errors
        assessment_avg_float = float(assessment_avg) if assessment_avg else 0.0

        # Calculate weighted score
        score = (
            skill_match_score * weights["skill_match"] +
            adaptability_score * weights["adaptability"] +
            assessment_avg_float * weights["assessment"] +
            cgpa_normalized * weights["cgpa"]
        )

        # Apply tier penalty
        tier_penalty = {
            "TIER_1_EXACT": 0,
            "TIER_2_SIMILAR": 5,
            "TIER_3_TRANSFERABLE": 10
        }

        score -= tier_penalty.get(tier, 0)

        # Clamp to 0-100
        return max(0.0, min(100.0, score))

    def _get_assessment_summary(self, maverick: Maverick, db: Session) -> Dict[str, Any]:
        """Get assessment performance summary for a candidate"""
        assessments = db.query(AssessmentAttempt).filter(
            AssessmentAttempt.maverick_id == maverick.id
        ).order_by(AssessmentAttempt.evaluated_at).all()

        if not assessments:
            return {
                "average_score": 0.0,
                "total_assessments": 0,
                "passed_assessments": 0,
                "pass_rate": 0.0,
                "trend": "no_data",
                "recent_activity": 0
            }

        # Calculate average score
        total_score = sum(
            (a.marks_obtained / a.max_marks * 100) if a.max_marks > 0 else 0
            for a in assessments
        )
        average_score = total_score / len(assessments) if assessments else 0.0

        # Calculate pass rate
        passed = sum(1 for a in assessments if a.passed)
        pass_rate = (passed / len(assessments) * 100) if assessments else 0.0

        # Determine trend
        trend = "stable"
        if len(assessments) >= 3:
            recent_scores = [
                (a.marks_obtained / a.max_marks * 100) if a.max_marks > 0 else 0
                for a in assessments[-3:]
            ]
            if recent_scores[-1] > recent_scores[0] + 5:
                trend = "improving"
            elif recent_scores[-1] < recent_scores[0] - 5:
                trend = "declining"

        # Recent activity (last 3 months)
        # Make timezone-aware to match database datetime
        from datetime import timezone
        three_months_ago = datetime.now(timezone.utc) - timedelta(days=90)
        recent_activity = sum(
            1 for a in assessments
            if a.evaluated_at and a.evaluated_at >= three_months_ago
        )

        return {
            "average_score": round(average_score, 2),
            "total_assessments": len(assessments),
            "passed_assessments": passed,
            "pass_rate": round(pass_rate, 2),
            "trend": trend,
            "recent_activity": recent_activity
        }

    def _to_candidate_match(self, result: Dict[str, Any]) -> CandidateMatch:
        """Convert internal result to CandidateMatch schema"""
        maverick = result["maverick"]
        skill_match = result["skill_match_result"]
        adaptability = result["adaptability_result"]
        timeline = result["timeline_result"]
        assessment = result["assessment_summary"]

        # Build exact matches
        exact_matches = [
            SkillMatch(
                skill=m["skill"],
                candidate_has=m.get("candidate_has"),
                proficiency_score=m["proficiency_score"],
                proficiency_level=m["proficiency_level"],
                assessment_validated=m.get("assessment_validated", False),
                points=m.get("points", 0.0)
            )
            for m in skill_match.get("exact_matches", [])
        ]

        # Build similar matches
        similar_matches = [
            SimilarSkillMatch(
                required_skill=m["required_skill"],
                candidate_has=m["candidate_has"],
                similarity_score=m["similarity_score"],
                proficiency_score=m.get("proficiency_score", 0.0),
                proficiency_level=m.get("proficiency_level", "BEGINNER"),
                learning_weeks=m["learning_weeks"],
                difficulty=m["difficulty"],
                assessment_validated=m.get("assessment_validated", False),
                points=m.get("points", 0.0)
            )
            for m in skill_match.get("similar_matches", [])
        ]

        # Build transferable matches
        transferable_matches = [
            TransferableSkillMatch(
                required_skill=m["required_skill"],
                candidate_has=m["candidate_has"],
                transferability_score=m.get("transferability_score", m.get("similarity_score", 50)),
                proficiency_score=m.get("proficiency_score", 0.0),
                proficiency_level=m.get("proficiency_level", "BEGINNER"),
                learning_weeks=m["learning_weeks"],
                difficulty=m["difficulty"],
                assessment_validated=m.get("assessment_validated", False),
                points=m.get("points", 0.0)
            )
            for m in skill_match.get("transferable_matches", [])
        ]

        # Build training plan
        training_plan = self._build_training_plan(timeline)

        # Generate match reasoning
        match_reasoning = self._generate_match_reasoning(
            tier=result["tier"],
            exact_count=len(exact_matches),
            similar_count=len(similar_matches),
            transferable_count=len(transferable_matches),
            adaptability_score=adaptability["adaptability_score"],
            learning_weeks=timeline["total_weeks"]
        )

        return CandidateMatch(
            id=maverick.id,
            name=maverick.name,
            email=maverick.email,
            cgpa=maverick.cgpa,
            deployment_status=maverick.deployment_status.value,
            profile_status=maverick.profile_status.value,
            final_score=round(result["final_score"], 2),
            tier=result["tier"],
            exact_matches=exact_matches,
            similar_matches=similar_matches,
            transferable_matches=transferable_matches,
            missing_skills=skill_match.get("missing_skills", []),
            assessment_performance=AssessmentSummary(**assessment) if assessment["total_assessments"] > 0 else None,
            adaptability_score=round(adaptability["adaptability_score"], 2),
            adaptability_interpretation=adaptability.get("interpretation", "average"),
            deployment_readiness=timeline["deployment_readiness"],
            learning_weeks_required=timeline["total_weeks"],
            training_plan=training_plan,
            match_reasoning=match_reasoning
        )

    def _build_training_plan(self, timeline_result: Dict[str, Any]) -> List[TrainingItem]:
        """Build structured training plan from timeline result"""
        training_items = []

        for skill_timeline in timeline_result.get("skill_timelines", []):
            # Build learning phases
            phases = []
            skill_type = skill_timeline.get("type", "missing")

            if skill_type == "similar":
                phases = [
                    TrainingPhase(
                        phase="Quick Adaptation",
                        weeks=skill_timeline["adjusted_weeks"] * 0.5,
                        focus=f"Leverage existing {skill_timeline['candidate_has']} knowledge"
                    ),
                    TrainingPhase(
                        phase="Skill Migration",
                        weeks=skill_timeline["adjusted_weeks"] * 0.5,
                        focus=f"Learn {skill_timeline['skill']}-specific features"
                    )
                ]
            elif skill_type == "transferable":
                phases = [
                    TrainingPhase(
                        phase="Foundation Transfer",
                        weeks=skill_timeline["adjusted_weeks"] * 0.3,
                        focus=f"Apply {skill_timeline['candidate_has']} concepts"
                    ),
                    TrainingPhase(
                        phase="Core Learning",
                        weeks=skill_timeline["adjusted_weeks"] * 0.5,
                        focus=f"Master {skill_timeline['skill']} fundamentals"
                    ),
                    TrainingPhase(
                        phase="Practice",
                        weeks=skill_timeline["adjusted_weeks"] * 0.2,
                        focus="Hands-on projects and exercises"
                    )
                ]
            else:
                # Learning from scratch
                phases = [
                    TrainingPhase(
                        phase="Fundamentals",
                        weeks=skill_timeline.get("adjusted_weeks", 4) * 0.4,
                        focus=f"Learn {skill_timeline.get('skill', 'skill')} basics"
                    ),
                    TrainingPhase(
                        phase="Intermediate",
                        weeks=skill_timeline.get("adjusted_weeks", 4) * 0.4,
                        focus="Advanced concepts and patterns"
                    ),
                    TrainingPhase(
                        phase="Project Work",
                        weeks=skill_timeline.get("adjusted_weeks", 4) * 0.2,
                        focus="Build real-world applications"
                    )
                ]

            training_items.append(TrainingItem(
                skill=skill_timeline.get("skill", "Unknown"),
                duration_weeks=skill_timeline.get("adjusted_weeks", 4),
                difficulty=skill_timeline.get("difficulty", "medium"),
                core_concepts=[],
                prerequisites=[skill_timeline.get("candidate_has")] if skill_timeline.get("candidate_has") else [],
                learning_path=phases
            ))

        return training_items

    def _generate_match_reasoning(
        self,
        tier: str,
        exact_count: int,
        similar_count: int,
        transferable_count: int,
        adaptability_score: float,
        learning_weeks: float
    ) -> str:
        """Generate human-readable explanation of why candidate was matched"""
        if tier == "TIER_1_EXACT":
            if exact_count >= 3:
                reasoning = f"✅ Excellent match! Has {exact_count} exact skill matches. "
            else:
                reasoning = f"✅ Good match! Has {exact_count} exact skill(s). "

            if adaptability_score >= 80:
                reasoning += "Strong learning ability (top 20%). "

            if learning_weeks == 0:
                reasoning += "Ready for immediate deployment."
            else:
                reasoning += f"Minimal training needed ({learning_weeks:.1f} weeks)."

        elif tier == "TIER_2_SIMILAR":
            reasoning = f"🔄 Similar skills match! Has {similar_count} transferable skill(s). "
            if adaptability_score >= 75:
                reasoning += "Fast learner - can adapt quickly. "
            reasoning += f"Estimated {learning_weeks:.1f} weeks to full proficiency."

        else:  # TIER_3_TRANSFERABLE
            reasoning = f"🎯 Transferable skills! Has {transferable_count} related skill(s). "
            if adaptability_score >= 70:
                reasoning += "Good adaptability score. "
            reasoning += f"Training required: ~{learning_weeks:.1f} weeks."

        return reasoning

    def _build_summary(
        self,
        scored_candidates: List[Dict[str, Any]],
        exact_matches: List[Dict[str, Any]],
        similar_matches: List[Dict[str, Any]],
        show_similar: bool
    ) -> SearchSummary:
        """Build search summary statistics"""
        immediate_deployment = sum(
            1 for c in scored_candidates
            if c["timeline_result"]["deployment_readiness"] == "immediate"
        )

        short_training = sum(
            1 for c in scored_candidates
            if c["timeline_result"]["deployment_readiness"] in ["immediate", "short_term"]
        ) - immediate_deployment

        longer_training = len(scored_candidates) - immediate_deployment - short_training

        return SearchSummary(
            total_found=len(scored_candidates),
            exact_matches=len(exact_matches),
            similar_skill_candidates=len(similar_matches),
            transferable_skill_candidates=sum(
                1 for c in similar_matches
                if c["tier"] == "TIER_3_TRANSFERABLE"
            ),
            immediate_deployment=immediate_deployment,
            short_training_needed=short_training,
            longer_training_needed=max(0, longer_training),
            show_similar_button=len(exact_matches) <= 2,
            similar_available=len(similar_matches)
        )


# Singleton instance
talent_search_service = TalentSearchService()
