"""
AI-Powered Maverick Suggestion Service
Suggests best-fit mavericks for a batch based on skills and AI analysis
"""
import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.models.maverick import Maverick, ProfileStatus
from app.models.batch import Batch, BatchCategory, BatchStatus
from app.services.batch_matcher import batch_matcher
from app.config import settings

logger = logging.getLogger(__name__)


class MaverickSuggester:
    """Suggests mavericks for batch assignment"""
    
    def get_unassigned_mavericks(self, db: Session) -> List[Maverick]:
        """
        Get all mavericks who are NOT assigned to any ACTIVE/PLANNED batch
        and have APPROVED profile status
        """
        # Get mavericks where:
        # 1. current_batch_id is NULL OR
        # 2. current_batch is not ACTIVE/PLANNED
        # 3. profile_status is APPROVED

        unassigned = db.query(Maverick).outerjoin(
            Batch, Maverick.current_batch_id == Batch.id
        ).filter(
            and_(
                Maverick.profile_status == ProfileStatus.APPROVED,
                or_(
                    Maverick.current_batch_id.is_(None),
                    Batch.status.notin_([BatchStatus.ACTIVE, BatchStatus.PLANNED])
                )
            )
        ).all()

        return unassigned
    
    async def suggest_mavericks_for_batch(
        self,
        batch: Batch,
        db: Session,
        top_n: int = 10,
        use_ai: bool = True,
        min_score: float = 40.0
    ) -> List[Dict[str, Any]]:
        """
        Suggest best-fit mavericks for a batch
        
        Args:
            batch: Batch to suggest mavericks for
            db: Database session
            top_n: Maximum number of suggestions
            use_ai: Whether to use AI for scoring
            min_score: Minimum match score threshold
        
        Returns:
            List of maverick suggestions with scores and reasoning
        """
        
        # For SOFT_SKILLS batches, return all unassigned mavericks
        if batch.category == BatchCategory.SOFT_SKILLS:
            unassigned = self.get_unassigned_mavericks(db)
            
            suggestions = []
            for mav in unassigned[:top_n]:
                suggestions.append({
                    "maverick_id": str(mav.id),
                    "maverick_name": mav.name,
                    "email": mav.email,
                    "college": mav.college,
                    "cgpa": mav.cgpa,
                    "skills": (mav.skills or []) + (mav.ai_extracted_skills or []),
                    "match_score": 100.0,  # No skill matching for soft skills
                    "recommendation": "RECOMMENDED",
                    "reasoning": "Soft skills training - no specific technical requirements",
                    "details": {
                        "total_skills": len((mav.skills or []) + (mav.ai_extracted_skills or [])),
                        "profile_status": mav.profile_status.value if mav.profile_status else "N/A"
                    }
                })
            
            return suggestions
        
        # For TECH batches, use AI matching
        unassigned = self.get_unassigned_mavericks(db)
        
        if not unassigned:
            logger.info("No unassigned mavericks found")
            return []
        
        suggestions = []
        
        for maverick in unassigned:
            # Calculate match score using batch_matcher logic
            exact_score, details = batch_matcher._calculate_exact_match_score(maverick, batch)
            
            # Calculate AI score if enabled
            ai_score = 0.0
            ai_reasoning = ""
            
            if use_ai:
                ai_score, ai_reasoning = await batch_matcher._calculate_ai_similarity_score(
                    maverick, batch
                )
            
            # Combined score
            if use_ai and ai_score > 0:
                final_score = (exact_score * 0.6) + (ai_score * 0.4)
            else:
                final_score = exact_score
            
            # Skip if below minimum score
            if final_score < min_score:
                continue
            
            # Build reasoning
            reasoning_parts = []
            
            if batch.required_skills:
                matched = details["required_skills_match"]
                total = len(batch.required_skills)
                if matched == total:
                    reasoning_parts.append(f"✅ All {total} required skills")
                elif matched > 0:
                    reasoning_parts.append(f"⚠️ {matched}/{total} required skills")
                else:
                    reasoning_parts.append(f"❌ Missing required skills")
            
            if details["matched_skills"]:
                reasoning_parts.append(f"Matches: {', '.join(details['matched_skills'][:3])}")
            
            if ai_reasoning:
                reasoning_parts.append(f"AI: {ai_reasoning[:100]}")
            
            suggestion = {
                "maverick_id": str(maverick.id),
                "maverick_name": maverick.name,
                "email": maverick.email,
                "college": maverick.college,
                "degree": maverick.degree,
                "branch": maverick.branch,
                "cgpa": maverick.cgpa,
                "graduation_year": maverick.graduation_year,
                "skills": (maverick.skills or []) + (maverick.ai_extracted_skills or []),
                "ai_summary": maverick.ai_summary,
                "match_score": round(final_score, 2),
                "exact_match_score": round(exact_score, 2),
                "ai_similarity_score": round(ai_score, 2) if ai_score > 0 else None,
                "recommendation": batch_matcher._get_recommendation(final_score, details),
                "reasoning": " | ".join(reasoning_parts),
                "details": {
                    "required_skills_matched": details["required_skills_match"],
                    "required_skills_total": len(batch.required_skills) if batch.required_skills else 0,
                    "required_skills_missing": details["required_skills_missing"],
                    "preferred_skills_matched": details["preferred_skills_match"],
                    "matched_skills": details["matched_skills"],
                    "total_maverick_skills": details["total_maverick_skills"]
                }
            }
            
            suggestions.append(suggestion)
        
        # Sort by score (descending)
        suggestions.sort(key=lambda x: x["match_score"], reverse=True)
        
        # Return top N
        return suggestions[:top_n]


# Global instance
maverick_suggester = MaverickSuggester()
