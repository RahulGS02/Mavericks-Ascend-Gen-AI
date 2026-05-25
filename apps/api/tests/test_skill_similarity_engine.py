"""
Unit tests for SkillSimilarityEngine
Tests all skill matching, adaptability scoring, and learning timeline algorithms
"""
import pytest
from unittest.mock import Mock, MagicMock
from datetime import datetime, timedelta
from uuid import uuid4

from app.services.skill_similarity_engine import SkillSimilarityEngine
from app.models.maverick_skill import MaverickSkill, ProficiencyLevel
from app.models.assessment import AssessmentAttempt
from app.models.maverick import Maverick


@pytest.fixture
def engine():
    """Create SkillSimilarityEngine instance"""
    return SkillSimilarityEngine()


@pytest.fixture
def mock_db():
    """Create mock database session"""
    return MagicMock()


class TestSkillNormalization:
    """Test skill name normalization"""
    
    def test_normalize_skill_name(self, engine):
        """Test skill name normalization"""
        assert engine.normalize_skill_name("Python") == "python"
        assert engine.normalize_skill_name("  .NET  ") == ".net"
        assert engine.normalize_skill_name("C#") == "c#"
        assert engine.normalize_skill_name("JavaScript") == "javascript"


class TestFindSimilarSkills:
    """Test finding similar and transferable skills"""
    
    def test_find_similar_for_dotnet(self, engine):
        """Test finding similar skills for .NET"""
        result = engine.find_similar_skills(".NET")
        
        assert "exact_alternatives" in result
        assert "highly_similar" in result
        assert "transferable" in result
        assert "category" in result
        
        # Check exact alternatives
        assert "ASP.NET" in result["exact_alternatives"]
        assert ".NET Core" in result["exact_alternatives"]
        
        # Check highly similar
        similar_skills = [s["skill"] for s in result["highly_similar"]]
        assert "C#" in similar_skills
        assert "Java" in similar_skills
        
        # Check C# details
        csharp = next(s for s in result["highly_similar"] if s["skill"] == "C#")
        assert csharp["similarity"] == 95
        assert csharp["learning_weeks"] == 1
        assert csharp["difficulty"] == "easy"
    
    def test_find_similar_for_azure(self, engine):
        """Test finding similar skills for Azure"""
        result = engine.find_similar_skills("Azure")
        
        # Check highly similar
        similar_skills = [s["skill"] for s in result["highly_similar"]]
        assert "AWS" in similar_skills
        assert "Google Cloud" in similar_skills
        
        # Check AWS details
        aws = next(s for s in result["highly_similar"] if s["skill"] == "AWS")
        assert aws["similarity"] == 85
        assert aws["learning_weeks"] == 3
        
        assert result["category"] == "cloud_platform"
    
    def test_find_similar_for_unknown_skill(self, engine):
        """Test handling of unknown skill"""
        result = engine.find_similar_skills("UnknownSkill123")
        
        assert result["exact_alternatives"] == []
        assert result["highly_similar"] == []
        assert result["transferable"] == []
    
    def test_expand_required_skills(self, engine):
        """Test expanding required skills to alternatives"""
        required = [".NET", "Azure"]
        expansion = engine.expand_required_skills(required)
        
        assert ".NET" in expansion
        assert "Azure" in expansion
        
        # .NET alternatives should include C#, Java
        assert "C#" in expansion[".NET"]
        assert "Java" in expansion[".NET"]
        
        # Azure alternatives should include AWS
        assert "AWS" in expansion["Azure"]


class TestSkillMatchScore:
    """Test skill match scoring algorithm"""
    
    def test_perfect_match(self, engine):
        """Test perfect skill match (100% score)"""
        # Candidate has exact skills required
        candidate_skills = [
            Mock(
                skill_name="Python",
                proficiency_score=90.0,
                proficiency_level=ProficiencyLevel.PROFICIENT,
                assessment_score=85.0
            ),
            Mock(
                skill_name="PostgreSQL",
                proficiency_score=85.0,
                proficiency_level=ProficiencyLevel.INTERMEDIATE,
                assessment_score=80.0
            )
        ]
        
        required_skills = ["Python", "PostgreSQL"]
        
        result = engine.calculate_skill_match_score(candidate_skills, required_skills)
        
        assert result["total_score"] == 100.0
        assert result["match_type"] == "PERFECT_MATCH"
        assert len(result["exact_matches"]) == 2
        assert len(result["missing_skills"]) == 0
        assert result["exact_count"] == 2
    
    def test_similar_skill_match(self, engine):
        """Test matching with similar skills"""
        # Candidate has C# instead of .NET
        candidate_skills = [
            Mock(
                skill_name="C#",
                proficiency_score=90.0,
                proficiency_level=ProficiencyLevel.PROFICIENT,
                assessment_score=88.0
            )
        ]
        
        required_skills = [".NET"]
        
        result = engine.calculate_skill_match_score(candidate_skills, required_skills)
        
        # C# is 95% similar to .NET, proficiency 90
        # Expected: 95 * 0.90 = 85.5 points out of 100
        assert 84.0 <= result["total_score"] <= 86.0
        assert result["match_type"] == "SIMILAR_SKILLS"
        assert len(result["similar_matches"]) == 1
        assert result["similar_matches"][0]["similarity_score"] == 95
        assert result["similar_matches"][0]["candidate_has"] == "C#"

    def test_transferable_skill_match(self, engine):
        """Test matching with transferable skills"""
        # Candidate has Python instead of Java
        candidate_skills = [
            Mock(
                skill_name="Python",
                proficiency_score=85.0,
                proficiency_level=ProficiencyLevel.INTERMEDIATE,
                assessment_score=82.0
            )
        ]

        required_skills = ["Java"]

        result = engine.calculate_skill_match_score(candidate_skills, required_skills)

        # Python is transferable to Java (70% similar)
        # With transferable penalty: 70 * 0.85 * 0.8 = 47.6
        assert result["match_type"] == "TRANSFERABLE_SKILLS"
        assert len(result["transferable_matches"]) == 1
        assert 45.0 <= result["total_score"] <= 50.0

    def test_multiple_skills_mixed_match(self, engine):
        """Test scoring with mix of exact, similar, and missing skills"""
        candidate_skills = [
            Mock(
                skill_name="Python",
                proficiency_score=90.0,
                proficiency_level=ProficiencyLevel.PROFICIENT,
                assessment_score=88.0
            ),
            Mock(
                skill_name="C#",
                proficiency_score=85.0,
                proficiency_level=ProficiencyLevel.INTERMEDIATE,
                assessment_score=80.0
            )
        ]

        required_skills = ["Python", ".NET", "Azure"]

        result = engine.calculate_skill_match_score(candidate_skills, required_skills)

        # Python: 100 points (exact)
        # .NET: ~80 points (has C# which is 95% similar)
        # Azure: 0 points (missing)
        # Total: ~180/300 = 60%
        assert 55.0 <= result["total_score"] <= 65.0
        assert result["match_type"] == "PARTIAL_EXACT"
        assert result["exact_count"] == 1
        assert result["similar_count"] == 1
        assert result["missing_count"] == 1

    def test_no_match(self, engine):
        """Test scoring when no skills match"""
        candidate_skills = [
            Mock(
                skill_name="Graphic Design",
                proficiency_score=90.0,
                proficiency_level=ProficiencyLevel.PROFICIENT,
                assessment_score=85.0
            )
        ]

        required_skills = ["Python", "Java"]

        result = engine.calculate_skill_match_score(candidate_skills, required_skills)

        # Graphic Design has no similarity to Python/Java in our mappings
        assert result["total_score"] == 0.0
        assert result["match_type"] == "NO_MATCH"
        assert len(result["missing_skills"]) == 2

    def test_empty_requirements(self, engine):
        """Test scoring with no requirements"""
        candidate_skills = [Mock(skill_name="Python", proficiency_score=90.0)]
        required_skills = []

        result = engine.calculate_skill_match_score(candidate_skills, required_skills)

        assert result["total_score"] == 100.0
        assert result["match_type"] == "NO_REQUIREMENTS"


class TestAdaptabilityScore:
    """Test adaptability scoring algorithm"""

    def test_exceptional_learner(self, engine, mock_db):
        """Test scoring for exceptional learner"""
        maverick = Mock(id=uuid4())
        maverick.skills = [
            Mock(skill_name=f"Skill{i}") for i in range(8)
        ]

        # Create improving assessment trend
        three_months_ago = datetime.utcnow() - timedelta(days=90)
        assessments = [
            Mock(
                maverick_id=maverick.id,
                marks_obtained=75.0,
                max_marks=100.0,
                passed=True,
                evaluated_at=three_months_ago + timedelta(days=10)
            ),
            Mock(
                maverick_id=maverick.id,
                marks_obtained=82.0,
                max_marks=100.0,
                passed=True,
                evaluated_at=three_months_ago + timedelta(days=30)
            ),
            Mock(
                maverick_id=maverick.id,
                marks_obtained=88.0,
                max_marks=100.0,
                passed=True,
                evaluated_at=three_months_ago + timedelta(days=60)
            ),
            Mock(
                maverick_id=maverick.id,
                marks_obtained=92.0,
                max_marks=100.0,
                passed=True,
                evaluated_at=datetime.utcnow() - timedelta(days=10)
            )
        ]

        # Mock database queries
        mock_db.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = assessments[-5:]
        mock_db.query.return_value.filter.return_value.count.return_value = 4
        mock_db.query.return_value.filter.return_value.all.return_value = assessments

        result = engine.calculate_adaptability_score(maverick, mock_db)

        # Should score high (90+) for:
        # - Improving trend (75 → 92)
        # - 8 skills (80 points for diversity)
        # - Recent activity (4 assessments)
        # - 100% pass rate
        assert result["adaptability_score"] >= 85.0
        assert "Exceptional" in result["interpretation"] or "Strong" in result["interpretation"]
        assert result["assessment_count"] == 4
        assert result["recent_activity_count"] == 4

    def test_average_learner(self, engine, mock_db):
        """Test scoring for average learner"""
        maverick = Mock(id=uuid4())
        maverick.skills = [Mock(skill_name=f"Skill{i}") for i in range(3)]

        # Stable but not improving
        assessments = [
            Mock(
                maverick_id=maverick.id,
                marks_obtained=70.0,
                max_marks=100.0,
                passed=True,
                evaluated_at=datetime.utcnow() - timedelta(days=200)
            ),
            Mock(
                maverick_id=maverick.id,
                marks_obtained=72.0,
                max_marks=100.0,
                passed=True,
                evaluated_at=datetime.utcnow() - timedelta(days=150)
            )
        ]

        mock_db.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = assessments
        mock_db.query.return_value.filter.return_value.count.return_value = 0  # No recent activity
        mock_db.query.return_value.filter.return_value.all.return_value = assessments

        result = engine.calculate_adaptability_score(maverick, mock_db)

        # Should score average (50-75) for:
        # - Stable scores (not improving)
        # - Only 3 skills
        # - No recent activity
        assert 50.0 <= result["adaptability_score"] <= 75.0
        assert result["recent_activity_count"] == 0

    def test_no_assessment_history(self, engine, mock_db):
        """Test scoring with no assessment history"""
        maverick = Mock(id=uuid4())
        maverick.skills = [Mock(skill_name="Python")]

        mock_db.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = []
        mock_db.query.return_value.filter.return_value.count.return_value = 0
        mock_db.query.return_value.filter.return_value.all.return_value = []

        result = engine.calculate_adaptability_score(maverick, mock_db)

        # Should use defaults
        assert result["adaptability_score"] >= 0
        assert result["assessment_count"] == 0


class TestLearningTimeline:
    """Test learning timeline estimation"""

    def test_immediate_deployment_no_gaps(self, engine):
        """Test timeline when no skills are missing"""
        candidate_skills = [Mock(skill_name="Python")]
        missing_skills = []
        adaptability_score = 85.0
        skill_match_details = {
            "similar_matches": [],
            "transferable_matches": []
        }

        result = engine.estimate_learning_timeline(
            candidate_skills,
            missing_skills,
            adaptability_score,
            skill_match_details
        )

        assert result["total_weeks"] == 0
        assert result["deployment_readiness"] == "immediate"
        assert "Ready for immediate deployment" in result["message"]

    def test_timeline_with_similar_skill(self, engine):
        """Test timeline when candidate has similar skill"""
        candidate_skills = [Mock(skill_name="C#")]
        missing_skills = [".NET"]  # Actually missing .NET, but has similar C#
        adaptability_score = 88.0  # Strong learner = 80% of base time

        skill_match_details = {
            "similar_matches": [
                {
                    "required_skill": ".NET",
                    "candidate_has": "C#",
                    "similarity_score": 95,
                    "learning_weeks": 1,
                    "difficulty": "easy"
                }
            ],
            "transferable_matches": []
        }

        result = engine.estimate_learning_timeline(
            candidate_skills,
            missing_skills,
            adaptability_score,
            skill_match_details
        )

        # Base: 1 week, Adjusted for adaptability (88): 1 * 0.8 = 0.8 weeks
        assert result["total_weeks"] <= 1.0
        assert result["deployment_readiness"] == "immediate"
        assert len(result["skill_timelines"]) == 1
        assert result["skill_timelines"][0]["type"] == "similar"

    def test_timeline_with_transferable_skill(self, engine):
        """Test timeline with transferable skill"""
        candidate_skills = [Mock(skill_name="AWS")]
        missing_skills = ["Azure"]  # Actually missing Azure, but has transferable AWS
        adaptability_score = 75.0  # Average learner = 90% of base time

        skill_match_details = {
            "similar_matches": [],
            "transferable_matches": [
                {
                    "required_skill": "Azure",
                    "candidate_has": "AWS",
                    "transferability_score": 85,
                    "learning_weeks": 3,
                    "difficulty": "medium"
                }
            ]
        }

        result = engine.estimate_learning_timeline(
            candidate_skills,
            missing_skills,
            adaptability_score,
            skill_match_details
        )

        # Base: 3 weeks, Adjusted: 3 * 0.9 = 2.7 weeks
        assert 2.5 <= result["total_weeks"] <= 3.0
        assert result["deployment_readiness"] == "short_term"
        assert result["skill_timelines"][0]["type"] == "transferable"

    def test_timeline_from_scratch(self, engine):
        """Test timeline for learning from scratch"""
        candidate_skills = []
        missing_skills = [".NET", "Azure"]
        adaptability_score = 90.0  # Exceptional learner = 70% of base time

        skill_match_details = {
            "similar_matches": [],
            "transferable_matches": []
        }

        result = engine.estimate_learning_timeline(
            candidate_skills,
            missing_skills,
            adaptability_score,
            skill_match_details
        )

        # .NET (framework): base ~3 weeks
        # Azure (cloud): base ~4 weeks
        # Total: ~7 weeks, adjusted for high adaptability: ~5 weeks
        assert result["total_weeks"] > 0
        assert len(result["skill_timelines"]) == 2
        assert all(t["type"] == "from_scratch" for t in result["skill_timelines"])

    def test_adaptability_adjustment_high(self, engine):
        """Test learning time adjustment for high adaptability"""
        base_weeks = 10.0

        # High adaptability (90+) = 70% of time
        adjusted = engine._adjust_for_adaptability(base_weeks, 92.0)
        assert adjusted == 7.0

        # Good adaptability (80-89) = 80% of time
        adjusted = engine._adjust_for_adaptability(base_weeks, 85.0)
        assert adjusted == 8.0

        # Average (70-79) = 90% of time
        adjusted = engine._adjust_for_adaptability(base_weeks, 75.0)
        assert adjusted == 9.0

        # Below average (60-69) = 100% of time
        adjusted = engine._adjust_for_adaptability(base_weeks, 65.0)
        assert adjusted == 10.0

        # Low (<60) = 120% of time
        adjusted = engine._adjust_for_adaptability(base_weeks, 55.0)
        assert adjusted == 12.0


class TestTrainingPlanGeneration:
    """Test training plan generation"""

    def test_generate_training_plan_short(self, engine):
        """Test generating training plan for short duration"""
        skill_timelines = [
            {
                "skill": ".NET",
                "adjusted_weeks": 1.5,
                "difficulty": "easy"
            }
        ]

        result = engine.generate_training_plan(skill_timelines)

        assert len(result) == 1
        assert result[0]["skill"] == ".NET"
        assert result[0]["duration_weeks"] == 1.5
        assert len(result[0]["learning_path"]) >= 1

    def test_generate_training_plan_long(self, engine):
        """Test generating training plan for longer duration"""
        skill_timelines = [
            {
                "skill": "Machine Learning",
                "adjusted_weeks": 6.0,
                "difficulty": "hard"
            }
        ]

        result = engine.generate_training_plan(skill_timelines)

        assert len(result) == 1
        assert result[0]["skill"] == "Machine Learning"
        # Should have multi-phase plan for 6+ weeks
        assert len(result[0]["learning_path"]) >= 2
        assert "core_concepts" in result[0]

    def test_generate_training_plan_multiple_skills(self, engine):
        """Test generating plan for multiple skills"""
        skill_timelines = [
            {"skill": "Python", "adjusted_weeks": 2.0, "difficulty": "easy"},
            {"skill": "Django", "adjusted_weeks": 3.0, "difficulty": "medium"}
        ]

        result = engine.generate_training_plan(skill_timelines)

        assert len(result) == 2
        assert result[0]["skill"] == "Python"
        assert result[1]["skill"] == "Django"


class TestIntegrationScenarios:
    """Integration tests for realistic scenarios"""

    def test_dotnet_developer_search_has_csharp(self, engine):
        """Scenario: Search for .NET dev, candidate has C#"""
        # Candidate profile
        candidate_skills = [
            Mock(
                skill_name="C#",
                proficiency_score=90.0,
                proficiency_level=ProficiencyLevel.PROFICIENT,
                assessment_score=88.0
            ),
            Mock(
                skill_name="SQL Server",
                proficiency_score=85.0,
                proficiency_level=ProficiencyLevel.INTERMEDIATE,
                assessment_score=82.0
            )
        ]

        required_skills = [".NET", "Azure"]

        # Calculate match
        match_result = engine.calculate_skill_match_score(candidate_skills, required_skills)

        # Should have C# as similar to .NET
        assert match_result["similar_count"] >= 1
        assert match_result["total_score"] > 40  # Partial match

        # Estimate timeline
        timeline = engine.estimate_learning_timeline(
            candidate_skills,
            [],
            85.0,  # Good adaptability
            match_result
        )

        # Should show quick learning path (C# → .NET is easy)
        # Missing Azure will add weeks
        assert timeline["total_weeks"] <= 5  # Should be reasonable

    def test_cloud_platform_switching(self, engine):
        """Scenario: Search for Azure, candidate has AWS"""
        candidate_skills = [
            Mock(
                skill_name="AWS",
                proficiency_score=92.0,
                proficiency_level=ProficiencyLevel.PROFICIENT,
                assessment_score=90.0
            ),
            Mock(
                skill_name="Docker",
                proficiency_score=80.0,
                proficiency_level=ProficiencyLevel.INTERMEDIATE,
                assessment_score=78.0
            )
        ]

        required_skills = ["Azure"]

        match_result = engine.calculate_skill_match_score(candidate_skills, required_skills)

        # AWS is highly similar to Azure
        assert match_result["similar_count"] == 1
        assert match_result["total_score"] >= 75  # High similarity

        # Timeline should be reasonable (3-4 weeks for cloud switching)
        timeline = engine.estimate_learning_timeline(
            candidate_skills,
            [],
            88.0,
            match_result
        )

        assert timeline["deployment_readiness"] in ["immediate", "short_term"]

    def test_zero_matches_scenario(self, engine):
        """Scenario: No matching skills at all"""
        candidate_skills = [
            Mock(
                skill_name="Graphic Design",
                proficiency_score=90.0,
                proficiency_level=ProficiencyLevel.PROFICIENT,
                assessment_score=85.0
            )
        ]

        required_skills = ["Python", "Machine Learning"]

        match_result = engine.calculate_skill_match_score(candidate_skills, required_skills)

        assert match_result["match_type"] == "NO_MATCH"
        assert match_result["total_score"] == 0
        assert len(match_result["missing_skills"]) == 2

    def test_multiple_skills_complex_scenario(self, engine):
        """Scenario: Complex requirement with mixed matches"""
        candidate_skills = [
            Mock(skill_name="Java", proficiency_score=92.0,
                 proficiency_level=ProficiencyLevel.PROFICIENT, assessment_score=90.0),
            Mock(skill_name="Spring", proficiency_score=88.0,
                 proficiency_level=ProficiencyLevel.PROFICIENT, assessment_score=85.0),
            Mock(skill_name="PostgreSQL", proficiency_score=85.0,
                 proficiency_level=ProficiencyLevel.INTERMEDIATE, assessment_score=82.0),
            Mock(skill_name="AWS", proficiency_score=80.0,
                 proficiency_level=ProficiencyLevel.INTERMEDIATE, assessment_score=78.0)
        ]

        required_skills = [".NET", "C#", "Azure", "SQL Server"]

        match_result = engine.calculate_skill_match_score(candidate_skills, required_skills)

        # Java is similar to C# and .NET
        # PostgreSQL is similar to SQL Server
        # AWS is similar to Azure
        assert match_result["similar_count"] >= 2
        assert match_result["total_score"] > 50  # Should have decent score

        # With high adaptability, should be ready in reasonable time
        timeline = engine.estimate_learning_timeline(
            candidate_skills,
            [],
            90.0,  # Exceptional learner
            match_result
        )

        # Multiple similar skills = shorter total time due to adaptability
        assert timeline["total_weeks"] <= 6


# Run tests with: pytest tests/test_skill_similarity_engine.py -v
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
