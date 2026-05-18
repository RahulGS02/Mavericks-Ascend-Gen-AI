"""
AI-Powered Batch Matching Service
Matches mavericks to best-fit batches using AI embeddings and skill analysis
"""
import logging
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
import asyncio

from app.models.maverick import Maverick
from app.models.batch import Batch, BatchStatus
from app.services.ai_service import ai_service
from app.config import settings

logger = logging.getLogger(__name__)


class BatchMatcher:
    """AI-powered batch matching service"""
    
    def __init__(self):
        pass
    
    def _normalize_skills(self, skills: List[str]) -> List[str]:
        """Normalize skills for comparison"""
        if not skills:
            return []
        
        # Convert to lowercase, strip whitespace, remove duplicates
        normalized = list(set([
            skill.lower().strip() 
            for skill in skills 
            if skill and skill.strip()
        ]))
        
        return normalized
    
    def _calculate_skill_overlap(
        self, 
        maverick_skills: List[str], 
        batch_skills: List[str]
    ) -> Tuple[int, List[str]]:
        """
        Calculate skill overlap
        Returns: (overlap_count, matched_skills)
        """
        mav_set = set(self._normalize_skills(maverick_skills))
        batch_set = set(self._normalize_skills(batch_skills))
        
        overlap = mav_set.intersection(batch_set)
        return len(overlap), list(overlap)
    
    def _calculate_exact_match_score(
        self,
        maverick: Maverick,
        batch: Batch
    ) -> Tuple[float, Dict[str, Any]]:
        """
        Calculate match score based on exact skill matching
        Returns: (score_0_to_100, details)
        """
        details = {
            "required_skills_match": 0,
            "required_skills_missing": [],
            "preferred_skills_match": 0,
            "focus_areas_match": 0,
            "matched_skills": [],
            "total_maverick_skills": 0,
            "total_batch_skills": 0
        }
        
        # Get all maverick skills (manual + AI extracted)
        mav_skills = (maverick.skills or []) + (maverick.ai_extracted_skills or [])
        mav_skills = self._normalize_skills(mav_skills)
        details["total_maverick_skills"] = len(set(mav_skills))
        
        total_score = 0
        max_score = 0
        
        # 1. Required Skills (40% weight) - MUST HAVE
        if batch.required_skills:
            req_count, req_matched = self._calculate_skill_overlap(mav_skills, batch.required_skills)
            details["required_skills_match"] = req_count
            details["total_batch_skills"] += len(batch.required_skills)
            
            required_normalized = self._normalize_skills(batch.required_skills)
            mav_normalized = set(mav_skills)
            missing = [skill for skill in required_normalized if skill not in mav_normalized]
            details["required_skills_missing"] = missing
            
            # Required skills scoring: percentage of required skills matched
            req_percentage = (req_count / len(batch.required_skills)) * 100 if batch.required_skills else 0
            total_score += req_percentage * 0.4
            max_score += 40
        
        # 2. Preferred Skills (30% weight) - NICE TO HAVE
        if batch.preferred_skills:
            pref_count, pref_matched = self._calculate_skill_overlap(mav_skills, batch.preferred_skills)
            details["preferred_skills_match"] = pref_count
            details["total_batch_skills"] += len(batch.preferred_skills)
            
            pref_percentage = (pref_count / len(batch.preferred_skills)) * 100 if batch.preferred_skills else 0
            total_score += pref_percentage * 0.3
            max_score += 30
        
        # 3. Focus Areas (30% weight) - OVERALL FIT
        if batch.focus_areas:
            focus_count, focus_matched = self._calculate_skill_overlap(mav_skills, batch.focus_areas)
            details["focus_areas_match"] = focus_count
            details["matched_skills"] = focus_matched
            details["total_batch_skills"] += len(batch.focus_areas)
            
            focus_percentage = (focus_count / len(batch.focus_areas)) * 100 if batch.focus_areas else 0
            total_score += focus_percentage * 0.3
            max_score += 30
        
        # Calculate final score
        final_score = (total_score / max_score * 100) if max_score > 0 else 0
        
        return min(final_score, 100), details
    
    async def _calculate_ai_similarity_score(
        self,
        maverick: Maverick,
        batch: Batch
    ) -> Tuple[float, str]:
        """
        Use AI to calculate semantic similarity between maverick and batch
        Returns: (similarity_score_0_to_100, reasoning)
        """
        if not await ai_service.is_available():
            logger.info("AI not available for similarity calculation")
            return 0.0, "AI similarity analysis unavailable"
        
        # Prepare maverick profile using AI resume data if available
        skills_list = (maverick.skills or []) + (maverick.ai_extracted_skills or [])

        # Use complete AI resume data if available
        experience_info = "N/A"
        education_info = f"{maverick.degree} in {maverick.branch}"
        projects_info = ""

        if maverick.ai_resume_data:
            ai_data = maverick.ai_resume_data

            # Experience
            if ai_data.get("experience"):
                exp_list = ai_data["experience"]
                if exp_list:
                    exp_summary = []
                    for exp in exp_list[:2]:  # Top 2 experiences
                        exp_summary.append(f"{exp.get('role', 'N/A')} at {exp.get('company', 'N/A')} ({exp.get('years', 0)} years)")
                    experience_info = "; ".join(exp_summary)
                    experience_info += f" | Total: {ai_data.get('total_experience_years', 0)} years"

            # Education
            if ai_data.get("education"):
                edu_list = ai_data["education"]
                if edu_list:
                    edu = edu_list[0]  # Primary education
                    education_info = f"{edu.get('degree', maverick.degree)} in {edu.get('branch', maverick.branch)} from {edu.get('college', maverick.college)}"
                    if edu.get("cgpa"):
                        education_info += f" (CGPA: {edu['cgpa']})"

            # Projects
            if ai_data.get("projects"):
                proj_count = len(ai_data["projects"])
                projects_info = f"Projects: {proj_count} total"

        mav_profile = f"""
Candidate Profile:
- Skills: {', '.join(skills_list)}
- Education: {education_info}
- Experience: {experience_info}
{projects_info if projects_info else ''}
- Summary: {maverick.ai_summary or 'N/A'}
"""
        
        # Prepare batch requirements
        batch_requirements = f"""
Batch: {batch.name}
- Description: {batch.description or 'N/A'}
- Target Role: {batch.target_role or 'N/A'}
- Required Skills: {', '.join(batch.required_skills or [])}
- Preferred Skills: {', '.join(batch.preferred_skills or [])}
- Focus Areas: {', '.join(batch.focus_areas or [])}
"""
        
        prompt = f"""
Analyze the fit between this candidate and the batch program.

{mav_profile}

{batch_requirements}

Provide:
1. Match Score (0-100)
2. Brief reasoning (2-3 sentences)

Format your response as JSON:
{{"score": <number>, "reasoning": "<text>"}}
"""
        
        try:
            result = await ai_service._call_ai(
                prompt=prompt,
                max_tokens=300,
                temperature=0.3,
                system_prompt="You are an expert recruiter analyzing candidate-batch fit. Return only valid JSON.",
                feature="batch_matching"
            )
            
            if result:
                # Parse JSON response
                import json
                cleaned = result.strip()
                if cleaned.startswith("```json"):
                    cleaned = cleaned[7:]
                if cleaned.startswith("```"):
                    cleaned = cleaned[3:]
                if cleaned.endswith("```"):
                    cleaned = cleaned[:-3]
                
                data = json.loads(cleaned.strip())
                score = float(data.get("score", 0))
                reasoning = data.get("reasoning", "No reasoning provided")
                
                return min(max(score, 0), 100), reasoning
        
        except Exception as e:
            logger.error(f"AI similarity calculation failed: {e}")

        return 0.0, "AI analysis failed"

    async def suggest_best_batches(
        self,
        maverick: Maverick,
        db: Session,
        top_n: int = 3,
        use_ai: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Suggest best-fit batches for a maverick

        Args:
            maverick: Maverick to match
            db: Database session
            top_n: Number of top suggestions to return
            use_ai: Whether to use AI for similarity scoring

        Returns:
            List of batch suggestions with scores and reasoning
        """

        # Get all active batches
        active_batches = db.query(Batch).filter(
            Batch.status == BatchStatus.ACTIVE
        ).all()

        if not active_batches:
            logger.warning("No active batches found for matching")
            return []

        suggestions = []

        for batch in active_batches:
            # Calculate exact match score
            exact_score, details = self._calculate_exact_match_score(maverick, batch)

            # Calculate AI similarity score if enabled
            ai_score = 0.0
            ai_reasoning = ""

            if use_ai and await ai_service.is_available():
                ai_score, ai_reasoning = await self._calculate_ai_similarity_score(maverick, batch)

            # Combined score: 60% exact match + 40% AI similarity
            if use_ai and ai_score > 0:
                final_score = (exact_score * 0.6) + (ai_score * 0.4)
            else:
                final_score = exact_score

            # Build reasoning
            reasoning_parts = []

            # Required skills
            if batch.required_skills:
                matched_req = details["required_skills_match"]
                total_req = len(batch.required_skills)
                if matched_req == total_req:
                    reasoning_parts.append(f"✅ Meets all {total_req} required skills")
                elif matched_req > 0:
                    reasoning_parts.append(f"⚠️ Meets {matched_req}/{total_req} required skills")
                else:
                    reasoning_parts.append(f"❌ Missing all {total_req} required skills")

            # Preferred skills
            if batch.preferred_skills and details["preferred_skills_match"] > 0:
                reasoning_parts.append(f"Has {details['preferred_skills_match']} preferred skills")

            # Focus areas
            if batch.focus_areas and details["matched_skills"]:
                reasoning_parts.append(f"Strong match in: {', '.join(details['matched_skills'][:3])}")

            # AI reasoning
            if ai_reasoning:
                reasoning_parts.append(f"AI Analysis: {ai_reasoning}")

            suggestion = {
                "batch_id": str(batch.id),
                "batch_name": batch.name,
                "batch_description": batch.description,
                "target_role": batch.target_role,
                "match_score": round(final_score, 2),
                "exact_match_score": round(exact_score, 2),
                "ai_similarity_score": round(ai_score, 2) if ai_score > 0 else None,
                "reasoning": " | ".join(reasoning_parts),
                "details": {
                    "required_skills_matched": details["required_skills_match"],
                    "required_skills_total": len(batch.required_skills) if batch.required_skills else 0,
                    "required_skills_missing": details["required_skills_missing"],
                    "preferred_skills_matched": details["preferred_skills_match"],
                    "focus_areas_matched": details["focus_areas_match"],
                    "matched_skills": details["matched_skills"],
                    "total_maverick_skills": details["total_maverick_skills"],
                    "total_batch_requirements": details["total_batch_skills"]
                },
                "recommendation": self._get_recommendation(final_score, details)
            }

            suggestions.append(suggestion)

        # Sort by match score (descending)
        suggestions.sort(key=lambda x: x["match_score"], reverse=True)

        # Return top N
        return suggestions[:top_n]

    def _get_recommendation(self, score: float, details: Dict[str, Any]) -> str:
        """Get recommendation based on score"""

        # Check if all required skills are met
        if details.get("required_skills_missing"):
            return "NOT_RECOMMENDED"

        if score >= 80:
            return "HIGHLY_RECOMMENDED"
        elif score >= 60:
            return "RECOMMENDED"
        elif score >= 40:
            return "CONSIDER"
        else:
            return "NOT_RECOMMENDED"


# Global instance
batch_matcher = BatchMatcher()
