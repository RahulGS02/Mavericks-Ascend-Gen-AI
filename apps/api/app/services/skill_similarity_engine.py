"""
Skill Similarity Engine
Calculates skill similarity scores and learning potential for talent matching
"""
import logging
from typing import List, Dict, Any, Tuple, Optional, Set
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.skill_mappings import (
    SKILL_SIMILARITY_MAP,
    LEARNING_DIFFICULTY,
    SOFT_SKILLS,
    get_skill_mapping,
    is_soft_skill
)
from app.models.maverick_skill import MaverickSkill, ProficiencyLevel
from app.models.assessment import AssessmentAttempt
from app.models.maverick import Maverick

logger = logging.getLogger(__name__)


class SkillSimilarityEngine:
    """Engine for calculating skill similarity and learning potential"""
    
    def __init__(self):
        self.skill_map = SKILL_SIMILARITY_MAP
        self.learning_difficulty = LEARNING_DIFFICULTY
    
    def normalize_skill_name(self, skill: str) -> str:
        """Normalize skill name for comparison"""
        return skill.lower().strip()
    
    def find_similar_skills(self, required_skill: str) -> Dict[str, List[Dict]]:
        """
        Find similar and transferable skills for a required skill
        
        Returns:
        {
            "exact_alternatives": ["alt1", "alt2"],
            "highly_similar": [{"skill": "skill1", "similarity": 90, ...}],
            "transferable": [{"skill": "skill2", "similarity": 70, ...}]
        }
        """
        mapping = get_skill_mapping(required_skill)
        
        if not mapping:
            logger.warning(f"No similarity mapping found for skill: {required_skill}")
            return {
                "exact_alternatives": [],
                "highly_similar": [],
                "transferable": []
            }
        
        # Format highly similar skills
        highly_similar = []
        for skill_name, details in mapping.get("highly_similar", {}).items():
            highly_similar.append({
                "skill": skill_name,
                "similarity": details["similarity"],
                "learning_weeks": details["learning_weeks"],
                "difficulty": details["difficulty"]
            })
        
        # Format transferable skills
        transferable = []
        for skill_name, details in mapping.get("transferable", {}).items():
            transferable.append({
                "skill": skill_name,
                "similarity": details["similarity"],
                "learning_weeks": details["learning_weeks"],
                "difficulty": details["difficulty"]
            })
        
        return {
            "exact_alternatives": mapping.get("exact_alternatives", []),
            "highly_similar": highly_similar,
            "transferable": transferable,
            "category": mapping.get("category", "unknown"),
            "core_concepts": mapping.get("core_concepts", []),
            "prerequisites": mapping.get("prerequisites", [])
        }
    
    def expand_required_skills(self, required_skills: List[str]) -> Dict[str, List[str]]:
        """
        Expand required skills to include similar alternatives
        
        Returns: {
            "skill1": ["similar1", "similar2", ...],
            "skill2": ["similar3", "similar4", ...]
        }
        """
        expansion = {}
        
        for skill in required_skills:
            similar_data = self.find_similar_skills(skill)
            all_alternatives = []
            
            # Add exact alternatives
            all_alternatives.extend(similar_data["exact_alternatives"])
            
            # Add highly similar skills
            all_alternatives.extend([s["skill"] for s in similar_data["highly_similar"]])
            
            # Add transferable skills
            all_alternatives.extend([s["skill"] for s in similar_data["transferable"]])
            
            expansion[skill] = all_alternatives
        
        return expansion
    
    def calculate_skill_match_score(
        self,
        candidate_skills: List[MaverickSkill],
        required_skills: List[str]
    ) -> Dict[str, Any]:
        """
        Calculate how well candidate's skills match requirements
        
        Returns detailed breakdown with scores
        """
        if not required_skills:
            return {
                "total_score": 100,
                "exact_matches": [],
                "similar_matches": [],
                "transferable_matches": [],
                "missing_skills": [],
                "match_type": "NO_REQUIREMENTS"
            }
        
        # Normalize candidate skills into a lookup dict
        candidate_skill_dict = {
            self.normalize_skill_name(skill.skill_name): skill
            for skill in candidate_skills
        }
        
        exact_matches = []
        similar_matches = []
        transferable_matches = []
        missing_skills = []
        
        for required in required_skills:
            required_norm = self.normalize_skill_name(required)
            matched = False
            
            # Check for exact match
            if required_norm in candidate_skill_dict:
                skill = candidate_skill_dict[required_norm]
                exact_matches.append({
                    "skill": required,
                    "proficiency_score": skill.proficiency_score,
                    "proficiency_level": skill.proficiency_level,
                    "assessment_validated": skill.assessment_score is not None,
                    "points": 100
                })
                matched = True
                continue

            # Check for similar skills
            similar_data = self.find_similar_skills(required)

            # Check exact alternatives first
            for alt in similar_data["exact_alternatives"]:
                alt_norm = self.normalize_skill_name(alt)
                if alt_norm in candidate_skill_dict:
                    skill = candidate_skill_dict[alt_norm]
                    exact_matches.append({
                        "skill": required,
                        "candidate_has": skill.skill_name,
                        "proficiency_score": skill.proficiency_score,
                        "proficiency_level": skill.proficiency_level,
                        "assessment_validated": skill.assessment_score is not None,
                        "points": 100
                    })
                    matched = True
                    break

            if matched:
                continue

            # Check highly similar skills
            for similar_skill in similar_data["highly_similar"]:
                similar_norm = self.normalize_skill_name(similar_skill["skill"])
                if similar_norm in candidate_skill_dict:
                    skill = candidate_skill_dict[similar_norm]
                    # Score = similarity * proficiency
                    points = similar_skill["similarity"] * (skill.proficiency_score / 100)

                    similar_matches.append({
                        "required_skill": required,
                        "candidate_has": skill.skill_name,
                        "similarity_score": similar_skill["similarity"],
                        "proficiency_score": skill.proficiency_score,
                        "proficiency_level": skill.proficiency_level,
                        "learning_weeks": similar_skill["learning_weeks"],
                        "difficulty": similar_skill["difficulty"],
                        "assessment_validated": skill.assessment_score is not None,
                        "points": points
                    })
                    matched = True
                    break

            if matched:
                continue

            # Check transferable skills
            for transferable_skill in similar_data["transferable"]:
                trans_norm = self.normalize_skill_name(transferable_skill["skill"])
                if trans_norm in candidate_skill_dict:
                    skill = candidate_skill_dict[trans_norm]
                    # Score = similarity * proficiency * 0.8 (transferable penalty)
                    points = transferable_skill["similarity"] * (skill.proficiency_score / 100) * 0.8

                    transferable_matches.append({
                        "required_skill": required,
                        "candidate_has": skill.skill_name,
                        "transferability_score": transferable_skill["similarity"],
                        "proficiency_score": skill.proficiency_score,
                        "proficiency_level": skill.proficiency_level,
                        "learning_weeks": transferable_skill["learning_weeks"],
                        "difficulty": transferable_skill["difficulty"],
                        "assessment_validated": skill.assessment_score is not None,
                        "points": points
                    })
                    matched = True
                    break

            # If still not matched, it's a missing skill
            if not matched:
                missing_skills.append(required)

        # Calculate total score
        total_points = 0
        max_points = len(required_skills) * 100

        for match in exact_matches:
            total_points += match["points"]

        for match in similar_matches:
            total_points += match["points"]

        for match in transferable_matches:
            total_points += match["points"]

        total_score = (total_points / max_points) * 100 if max_points > 0 else 0

        # Determine match type
        if len(exact_matches) == len(required_skills):
            match_type = "PERFECT_MATCH"
        elif len(exact_matches) > 0:
            match_type = "PARTIAL_EXACT"
        elif len(similar_matches) > 0:
            match_type = "SIMILAR_SKILLS"
        elif len(transferable_matches) > 0:
            match_type = "TRANSFERABLE_SKILLS"
        else:
            match_type = "NO_MATCH"

        return {
            "total_score": round(total_score, 2),
            "exact_matches": exact_matches,
            "similar_matches": similar_matches,
            "transferable_matches": transferable_matches,
            "missing_skills": missing_skills,
            "match_type": match_type,
            "exact_count": len(exact_matches),
            "similar_count": len(similar_matches),
            "transferable_count": len(transferable_matches),
            "missing_count": len(missing_skills)
        }

    def calculate_adaptability_score(
        self,
        maverick: Maverick,
        db: Session
    ) -> Dict[str, Any]:
        """
        Calculate candidate's adaptability/learning potential score (0-100)

        Based on:
        - Assessment trend (40%) - improving scores = high adaptability
        - Skill diversity (30%) - more skills = faster learner
        - Recent learning (20%) - active in last 3 months
        - Pass rate (10%) - overall success rate
        """
        factors = {
            "assessment_trend": 0,
            "skill_diversity": 0,
            "recent_learning": 0,
            "pass_rate": 0
        }
        weights = {
            "assessment_trend": 0.40,
            "skill_diversity": 0.30,
            "recent_learning": 0.20,
            "pass_rate": 0.10
        }

        # 1. Assessment Trend (40%)
        recent_assessments = db.query(AssessmentAttempt).filter(
            AssessmentAttempt.maverick_id == maverick.id
        ).order_by(AssessmentAttempt.evaluated_at.desc()).limit(5).all()

        if recent_assessments and len(recent_assessments) >= 2:
            scores = [(a.marks_obtained / a.max_marks) * 100 for a in reversed(recent_assessments) if a.max_marks > 0]
            if scores and len(scores) >= 2:
                # Calculate trend (improving, stable, declining)
                avg_first_half = sum(scores[:len(scores)//2]) / (len(scores)//2)
                avg_second_half = sum(scores[len(scores)//2:]) / (len(scores) - len(scores)//2)
                improvement = avg_second_half - avg_first_half

                avg_score = sum(scores) / len(scores)

                if improvement > 5:  # Improving significantly
                    factors["assessment_trend"] = 100
                elif improvement > 0 and avg_score >= 80:  # Slight improvement + high scores
                    factors["assessment_trend"] = 95
                elif avg_score >= 85:  # Stable but excellent
                    factors["assessment_trend"] = 90
                elif avg_score >= 75:  # Stable and good
                    factors["assessment_trend"] = 80
                else:
                    factors["assessment_trend"] = 60
            else:
                factors["assessment_trend"] = 70  # Default
        else:
            factors["assessment_trend"] = 50  # Not enough data

        # 2. Skill Diversity (30%)
        skill_count = len(maverick.skills) if maverick.skills else 0
        # More skills = better learner (normalize to 0-100, cap at 10 skills)
        factors["skill_diversity"] = min((skill_count / 10) * 100, 100)

        # 3. Recent Learning Activity (20%)
        from datetime import datetime, timedelta
        three_months_ago = datetime.utcnow() - timedelta(days=90)

        recent_activity = db.query(AssessmentAttempt).filter(
            AssessmentAttempt.maverick_id == maverick.id,
            AssessmentAttempt.evaluated_at >= three_months_ago
        ).count()

        if recent_activity >= 3:
            factors["recent_learning"] = 100
        elif recent_activity >= 1:
            factors["recent_learning"] = 75
        else:
            factors["recent_learning"] = 50

        # 4. Overall Pass Rate (10%)
        all_assessments = db.query(AssessmentAttempt).filter(
            AssessmentAttempt.maverick_id == maverick.id
        ).all()

        if all_assessments:
            passed = sum(1 for a in all_assessments if a.passed)
            pass_rate = (passed / len(all_assessments)) * 100
            factors["pass_rate"] = pass_rate
        else:
            factors["pass_rate"] = 50  # Default

        # Calculate weighted score
        adaptability_score = (
            factors["assessment_trend"] * weights["assessment_trend"] +
            factors["skill_diversity"] * weights["skill_diversity"] +
            factors["recent_learning"] * weights["recent_learning"] +
            factors["pass_rate"] * weights["pass_rate"]
        )

        return {
            "adaptability_score": round(adaptability_score, 2),
            "factors": factors,
            "assessment_count": len(all_assessments) if all_assessments else 0,
            "recent_activity_count": recent_activity,
            "interpretation": self._interpret_adaptability(adaptability_score)
        }

    def _interpret_adaptability(self, score: float) -> str:
        """Interpret adaptability score"""
        if score >= 90:
            return "Exceptional learner - Quick to adapt to new technologies"
        elif score >= 80:
            return "Strong learner - Can master new skills efficiently"
        elif score >= 70:
            return "Good learner - Adapts well with proper training"
        elif score >= 60:
            return "Average learner - Needs structured learning path"
        else:
            return "Developing learner - Requires extended training period"

    def estimate_learning_timeline(
        self,
        candidate_skills: List[MaverickSkill],
        missing_skills: List[str],
        adaptability_score: float,
        skill_match_details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Estimate how long it will take candidate to learn missing skills

        Considers:
        - Base learning curve from skill mappings
        - Similar skills already possessed
        - Candidate's adaptability score
        - Skill category difficulty
        """
        if not missing_skills:
            return {
                "total_weeks": 0,
                "deployment_readiness": "immediate",
                "skill_timelines": [],
                "message": "✅ Ready for immediate deployment"
            }

        # Check if we have similar/transferable matches that reduce learning time
        similar_matches = skill_match_details.get("similar_matches", [])
        transferable_matches = skill_match_details.get("transferable_matches", [])

        # If we have similar/transferable matches, use those timelines
        if similar_matches or transferable_matches:
            skill_timelines = []
            total_weeks = 0

            for match in similar_matches:
                weeks = match["learning_weeks"]
                # Adjust for adaptability
                adjusted_weeks = self._adjust_for_adaptability(weeks, adaptability_score)
                skill_timelines.append({
                    "skill": match["required_skill"],
                    "candidate_has": match["candidate_has"],
                    "base_weeks": weeks,
                    "adjusted_weeks": adjusted_weeks,
                    "difficulty": match["difficulty"],
                    "similarity": match["similarity_score"],
                    "type": "similar"
                })
                total_weeks += adjusted_weeks

            for match in transferable_matches:
                weeks = match["learning_weeks"]
                adjusted_weeks = self._adjust_for_adaptability(weeks, adaptability_score)
                skill_timelines.append({
                    "skill": match["required_skill"],
                    "candidate_has": match["candidate_has"],
                    "base_weeks": weeks,
                    "adjusted_weeks": adjusted_weeks,
                    "difficulty": match["difficulty"],
                    "transferability": match["transferability_score"],
                    "type": "transferable"
                })
                total_weeks += adjusted_weeks

        else:
            # No similar skills - estimate from scratch
            skill_timelines = []
            total_weeks = 0

            for skill in missing_skills:
                mapping = get_skill_mapping(skill)
                if mapping:
                    category = mapping.get("category", "unknown")
                    difficulty = self.learning_difficulty.get(category, {})
                    base_weeks = difficulty.get("base_weeks", 4)
                    multiplier = difficulty.get("multiplier", 1.0)

                    weeks = base_weeks * multiplier
                    adjusted_weeks = self._adjust_for_adaptability(weeks, adaptability_score)

                    skill_timelines.append({
                        "skill": skill,
                        "candidate_has": None,
                        "base_weeks": weeks,
                        "adjusted_weeks": adjusted_weeks,
                        "difficulty": "medium",
                        "type": "from_scratch",
                        "prerequisites": difficulty.get("prerequisites", [])
                    })
                    total_weeks += adjusted_weeks
                else:
                    # Unknown skill - use default
                    adjusted_weeks = self._adjust_for_adaptability(4, adaptability_score)
                    skill_timelines.append({
                        "skill": skill,
                        "candidate_has": None,
                        "base_weeks": 4,
                        "adjusted_weeks": adjusted_weeks,
                        "difficulty": "medium",
                        "type": "unknown"
                    })
                    total_weeks += adjusted_weeks

        # Determine deployment readiness
        if total_weeks <= 2:
            deployment_readiness = "immediate"
            message = f"✅ Ready in {int(total_weeks)}-{int(total_weeks)+1} weeks with focused training"
        elif total_weeks <= 4:
            deployment_readiness = "short_term"
            message = f"⭐ Ready in {int(total_weeks)}-{int(total_weeks)+1} weeks with structured training"
        elif total_weeks <= 8:
            deployment_readiness = "medium_term"
            message = f"💡 Ready in {int(total_weeks)} weeks with comprehensive training program"
        else:
            deployment_readiness = "long_term"
            message = f"📚 Ready in {int(total_weeks)} weeks with extended training and mentorship"

        return {
            "total_weeks": round(total_weeks, 1),
            "deployment_readiness": deployment_readiness,
            "skill_timelines": skill_timelines,
            "message": message,
            "adaptability_adjusted": True
        }

    def _adjust_for_adaptability(self, base_weeks: float, adaptability_score: float) -> float:
        """
        Adjust learning timeline based on adaptability score

        High adaptability (90+) = 70% of base time
        Good adaptability (80-89) = 80% of base time
        Average adaptability (70-79) = 90% of base time
        Below average (60-69) = 100% of base time
        Low (<60) = 120% of base time
        """
        if adaptability_score >= 90:
            return base_weeks * 0.7
        elif adaptability_score >= 80:
            return base_weeks * 0.8
        elif adaptability_score >= 70:
            return base_weeks * 0.9
        elif adaptability_score >= 60:
            return base_weeks * 1.0
        else:
            return base_weeks * 1.2

    def generate_training_plan(
        self,
        skill_timelines: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Generate a structured training plan for missing skills
        """
        training_plan = []

        for timeline in skill_timelines:
            skill_mapping = get_skill_mapping(timeline["skill"])

            plan_item = {
                "skill": timeline["skill"],
                "duration_weeks": timeline["adjusted_weeks"],
                "difficulty": timeline.get("difficulty", "medium"),
                "learning_path": []
            }

            if skill_mapping:
                # Add core concepts to learn
                plan_item["core_concepts"] = skill_mapping.get("core_concepts", [])
                plan_item["prerequisites"] = skill_mapping.get("prerequisites", [])

                # Create learning path
                weeks = int(timeline["adjusted_weeks"])
                if weeks >= 4:
                    plan_item["learning_path"] = [
                        {"phase": "Fundamentals", "weeks": 1, "focus": "Core concepts and syntax"},
                        {"phase": "Practice", "weeks": weeks - 2, "focus": "Hands-on projects and exercises"},
                        {"phase": "Assessment", "weeks": 1, "focus": "Skill validation and certification"}
                    ]
                elif weeks >= 2:
                    plan_item["learning_path"] = [
                        {"phase": "Quick Start", "weeks": 1, "focus": "Essential concepts"},
                        {"phase": "Application", "weeks": weeks - 1, "focus": "Practical implementation"}
                    ]
                else:
                    plan_item["learning_path"] = [
                        {"phase": "Intensive Training", "weeks": weeks, "focus": "Rapid skill acquisition"}
                    ]

            training_plan.append(plan_item)

        return training_plan
