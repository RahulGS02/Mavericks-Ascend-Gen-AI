"""
Skill Proficiency Service
Analyzes assessments and generates AI-powered skill proficiency scores
"""
import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
import math

from app.models.maverick import Maverick
from app.models.maverick_skill import MaverickSkill, ProficiencyLevel
from app.models.assessment import Assessment
from app.services.ai_service import ai_service

logger = logging.getLogger(__name__)

# Force reload marker - v2


class SkillProficiencyService:
    """AI-powered skill proficiency analysis and scoring"""
    
    def _determine_proficiency_level(self, score: float) -> str:
        """Determine proficiency level from score - 3 levels only"""
        if score >= 80:
            return ProficiencyLevel.PROFICIENT.value
        elif score >= 60:
            return ProficiencyLevel.INTERMEDIATE.value
        else:
            return ProficiencyLevel.BEGINNER.value
    
    def _calculate_weighted_score(
        self,
        assessment_score: Optional[float] = None,
        training_completion: Optional[float] = None,
        self_declared: Optional[float] = None,
        ai_analyzed: Optional[float] = None
    ) -> float:
        """
        Calculate weighted proficiency score from multiple sources
        
        Weights:
        - Assessment: 50%
        - Training: 20%
        - AI Analysis: 20%
        - Self-declared: 10%
        """
        total_score = 0.0
        total_weight = 0.0
        
        if assessment_score is not None:
            total_score += assessment_score * 0.5
            total_weight += 0.5
        
        if training_completion is not None:
            total_score += training_completion * 0.2
            total_weight += 0.2
        
        if ai_analyzed is not None:
            total_score += ai_analyzed * 0.2
            total_weight += 0.2
        
        if self_declared is not None:
            total_score += self_declared * 0.1
            total_weight += 0.1
        
        if total_weight == 0:
            return 0.0

        # Calculate weighted average (already in 0-100 range)
        # total_score is already the sum of (score * weight), so dividing by total_weight gives the average
        return min(max(total_score / total_weight, 0), 100)
    
    def _generate_radar_data(self, skills: List[MaverickSkill]) -> Dict[str, Any]:
        """
        Generate radar chart data for visualization

        Returns:
            {
                "labels": ["Python", "JavaScript", "React", ...],
                "data": [85, 70, 90, ...],
                "categories": ["TECHNICAL", "FRAMEWORK", ...],
                "colors": ["#10B981", "#3B82F6", ...]
            }
        """
        if not skills:
            return {"labels": [], "data": [], "categories": [], "colors": []}
        
        # Sort by proficiency score (top skills)
        sorted_skills = sorted(skills, key=lambda x: x.proficiency_score, reverse=True)
        
        # Take top 8 skills for radar chart
        top_skills = sorted_skills[:8]
        
        return {
            "labels": [skill.skill_name for skill in top_skills],
            "data": [round(skill.proficiency_score, 1) for skill in top_skills],
            "categories": [skill.category for skill in top_skills],
            "colors": self._get_skill_colors(top_skills)
        }
    
    def _get_skill_colors(self, skills: List[MaverickSkill]) -> List[str]:
        """Get color codes based on proficiency level - 3 levels"""
        color_map = {
            ProficiencyLevel.PROFICIENT.value: "#10B981",      # Green (80-100)
            ProficiencyLevel.INTERMEDIATE.value: "#F59E0B",    # Orange (60-79)
            ProficiencyLevel.BEGINNER.value: "#EF4444"         # Red (0-59)
        }

        return [color_map.get(skill.proficiency_level, "#6B7280") for skill in skills]
    
    async def analyze_assessment_for_skills(
        self,
        maverick_id: str,
        assessment_id: str,
        assessment_data: Dict[str, Any],
        db: Session
    ) -> List[MaverickSkill]:
        """
        Analyze assessment results and extract skill proficiency
        
        Args:
            maverick_id: Maverick UUID
            assessment_id: Assessment UUID
            assessment_data: Assessment result data (scores, questions, etc.)
            db: Database session
        
        Returns:
            List of updated/created MaverickSkill objects
        """
        
        # Extract skills from assessment
        # Assume assessment_data has structure: {"skills": {"Python": 85, "JavaScript": 70, ...}}
        skill_scores = assessment_data.get("skill_scores", {})
        
        if not skill_scores:
            logger.warning(f"No skill scores found in assessment {assessment_id}")
            return []
        
        updated_skills = []
        
        for skill_name, score in skill_scores.items():
            # Get or create skill record
            skill = db.query(MaverickSkill).filter(
                MaverickSkill.maverick_id == maverick_id,
                MaverickSkill.skill_name == skill_name
            ).first()
            
            if not skill:
                skill = MaverickSkill(
                    maverick_id=maverick_id,
                    skill_name=skill_name,
                    category="TECHNICAL"  # Default, can be improved with AI
                )
                db.add(skill)
            
            # Store previous score for trend analysis
            previous_score = skill.assessment_score

            # Update assessment score
            skill.assessment_score = score
            skill.assessment_count = (skill.assessment_count or 0) + 1
            skill.last_assessed_at = datetime.utcnow()

            # Recalculate proficiency
            skill.proficiency_score = self._calculate_weighted_score(
                assessment_score=skill.assessment_score,
                training_completion=skill.training_completion,
                self_declared=skill.self_declared,
                ai_analyzed=skill.ai_analyzed
            )

            skill.proficiency_level = self._determine_proficiency_level(skill.proficiency_score)

            # Generate AI feedback if available
            if await ai_service.is_available():
                feedback = await self._generate_ai_feedback(
                    skill_name=skill_name,
                    score=score,
                    assessment_count=skill.assessment_count,
                    previous_score=previous_score
                )
                skill.ai_feedback = feedback

            updated_skills.append(skill)
        
        db.commit()
        
        # Regenerate radar data for all skills
        await self.update_radar_data(maverick_id, db)

        return updated_skills

    def _calculate_skill_analytics(
        self,
        skill_name: str,
        score: float,
        assessment_count: int = 1,
        previous_score: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Calculate all skill analytics using Python (no AI tokens wasted)

        Returns dictionary with all calculated metrics
        """
        # Performance thresholds - 3 levels only
        PROFICIENT_THRESHOLD = 80
        INTERMEDIATE_THRESHOLD = 60

        # Basic calculations
        percentage = score
        gap_to_proficient = max(0, PROFICIENT_THRESHOLD - score)

        # Determine performance band - 3 levels
        if score >= PROFICIENT_THRESHOLD:
            band = "Proficient"
            band_range = "80-100%"
        elif score >= INTERMEDIATE_THRESHOLD:
            band = "Intermediate"
            band_range = "60-79%"
        else:
            band = "Beginner"
            band_range = "0-59%"

        # Trend analysis
        trend_analysis = None
        if previous_score is not None:
            change = score - previous_score
            change_pct = (change / previous_score) * 100 if previous_score > 0 else 0

            if change > 5:
                trend_analysis = {
                    "direction": "improved",
                    "change_points": round(change, 1),
                    "change_percent": round(change_pct, 1),
                    "from_score": round(previous_score, 1),
                    "to_score": round(score, 1)
                }
            elif change < -5:
                trend_analysis = {
                    "direction": "declined",
                    "change_points": round(change, 1),
                    "change_percent": round(change_pct, 1),
                    "from_score": round(previous_score, 1),
                    "to_score": round(score, 1)
                }
            else:
                trend_analysis = {
                    "direction": "stable",
                    "change_points": round(change, 1),
                    "change_percent": round(change_pct, 1)
                }

        return {
            "skill_name": skill_name,
            "score": round(score, 1),
            "percentage": round(percentage, 1),
            "performance_band": band,
            "band_range": band_range,
            "gap_to_proficient": round(gap_to_proficient, 1),
            "trend": trend_analysis
        }

    async def _generate_ai_feedback(
        self,
        skill_name: str,
        score: float,
        assessment_count: int = 1,
        previous_score: Optional[float] = None
    ) -> str:
        """
        Generate AI feedback - AI only analyzes WHAT to improve, Python handles all calculations
        """
        try:
            # Python calculates ALL metrics (no AI tokens wasted)
            analytics = self._calculate_skill_analytics(
                skill_name, score, assessment_count, previous_score
            )

            # Build concise data context for AI
            data_summary = f"""Skill: {analytics['skill_name']}
Score: {analytics['score']}/100 ({analytics['performance_band']})"""

            if analytics['trend']:
                trend = analytics['trend']
                if trend['direction'] == 'improved':
                    data_summary += f"\nProgress: +{trend['change_points']} points"
                elif trend['direction'] == 'declined':
                    data_summary += f"\nRegression: {trend['change_points']} points"

            # AI focuses ONLY on technical insights (compact format)
            prompt = f"""{data_summary}

Provide concise technical analysis (3-4 sentences):

**What's working**: Name 1-2 specific {skill_name} concepts this score indicates.
**What's missing**: Identify 1 precise technical gap.
**Next step**: Recommend 1 concrete action (project/exercise with specific features).

Be technical. Skip pleasantries."""

            result = await ai_service._call_ai(
                prompt=prompt,
                max_tokens=200,  # More compact
                temperature=0.3,
                system_prompt=f"You are a {skill_name} expert. Be specific, technical, and concise. No fluff.",
                feature="skill_feedback"
            )

            # Format final feedback - Clean and eye-catching
            feedback_parts = [
                f"📊 **{analytics['score']}/100** ({analytics['performance_band']})"
            ]

            # Only show trend if significant change
            if analytics['trend'] and analytics['trend']['direction'] != 'stable':
                trend = analytics['trend']
                emoji = "📈" if trend['direction'] == 'improved' else "📉"
                feedback_parts.append(
                    f"{emoji} {trend['direction'].title()}: {abs(trend['change_points'])} pts ({trend['change_percent']:+.1f}%)"
                )

            # Add AI insights
            if result and result.strip():
                feedback_parts.append(f"\n{result.strip()}")
            else:
                feedback_parts.append("\nContinue focused practice.")

            return "\n".join(feedback_parts)

        except Exception as e:
            logger.error(f"AI feedback generation failed: {e}")
            analytics = self._calculate_skill_analytics(skill_name, score, assessment_count, previous_score)
            return f"**Score**: {analytics['score']}/100 ({analytics['performance_band']}). **Gap to Expert**: {analytics['gap_to_expert']} points. Focus on advancing {skill_name} proficiency."

    async def update_radar_data(self, maverick_id: str, db: Session):
        """Update radar chart data for maverick"""
        skills = db.query(MaverickSkill).filter(
            MaverickSkill.maverick_id == maverick_id
        ).all()

        if skills:
            radar_data = self._generate_radar_data(skills)

            # Store radar data in each skill (for caching)
            for skill in skills:
                skill.radar_data = radar_data

            db.commit()

    async def initialize_skills_from_resume(
        self,
        maverick_id: str,
        ai_extracted_skills: List[str],
        db: Session
    ):
        """
        Initialize skill records from AI-parsed resume

        Sets initial proficiency based on AI analysis
        """
        for skill_name in ai_extracted_skills:
            # Check if skill already exists
            existing = db.query(MaverickSkill).filter(
                MaverickSkill.maverick_id == maverick_id,
                MaverickSkill.skill_name == skill_name
            ).first()

            if not existing:
                # Create new skill with AI-analyzed score (default 50 - intermediate)
                skill = MaverickSkill(
                    maverick_id=maverick_id,
                    skill_name=skill_name,
                    category="TECHNICAL",
                    ai_analyzed=50.0,  # Default initial score
                    proficiency_score=50.0,
                    proficiency_level=ProficiencyLevel.INTERMEDIATE.value
                )
                db.add(skill)

        db.commit()

    def get_skill_proficiency_summary(
        self,
        maverick_id: str,
        db: Session
    ) -> Dict[str, Any]:
        """
        Get complete skill proficiency summary for maverick

        Returns:
            {
                "total_skills": 10,
                "proficient_skills": 3,
                "intermediate_skills": 5,
                "beginner_skills": 2,
                "average_proficiency": 72.5,
                "radar_chart": {...},
                "top_skills": [...],
                "skills_needing_improvement": [...]
            }
        """
        skills = db.query(MaverickSkill).filter(
            MaverickSkill.maverick_id == maverick_id
        ).all()

        if not skills:
            return {
                "total_skills": 0,
                "proficient_skills": 0,
                "intermediate_skills": 0,
                "beginner_skills": 0,
                "average_proficiency": 0.0,
                "radar_chart": {"labels": [], "data": [], "categories": []},
                "top_skills": [],
                "skills_needing_improvement": []
            }

        # Calculate statistics
        level_counts = {level.value: 0 for level in ProficiencyLevel}
        for skill in skills:
            if skill.proficiency_level:
                level_counts[skill.proficiency_level] = level_counts.get(skill.proficiency_level, 0) + 1

        avg_proficiency = sum(s.proficiency_score for s in skills) / len(skills)

        # Get top skills (>= 70)
        top_skills = [
            {"name": s.skill_name, "score": s.proficiency_score, "level": s.proficiency_level}
            for s in sorted(skills, key=lambda x: x.proficiency_score, reverse=True)
            if s.proficiency_score >= 70
        ][:5]

        # Get skills needing improvement (< 50)
        needs_improvement = [
            {"name": s.skill_name, "score": s.proficiency_score, "level": s.proficiency_level}
            for s in sorted(skills, key=lambda x: x.proficiency_score)
            if s.proficiency_score < 50
        ][:5]

        radar_data = self._generate_radar_data(skills)

        return {
            "total_skills": len(skills),
            "proficient_skills": level_counts.get(ProficiencyLevel.PROFICIENT.value, 0),
            "intermediate_skills": level_counts.get(ProficiencyLevel.INTERMEDIATE.value, 0),
            "beginner_skills": level_counts.get(ProficiencyLevel.BEGINNER.value, 0),
            "average_proficiency": round(avg_proficiency, 1),
            "radar_chart": radar_data,
            "top_skills": top_skills,
            "skills_needing_improvement": needs_improvement
        }


# Global instance
skill_proficiency_service = SkillProficiencyService()
