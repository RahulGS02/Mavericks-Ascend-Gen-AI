"""
Integration Tests for AI Talent Search API
Tests the complete API endpoints with database and authentication
"""
import pytest
import os
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
from uuid import uuid4

# Set testing mode
os.environ["TESTING"] = "true"

from app.main import app
from app.database import Base, get_db
from app.models.user import User, UserRole
from app.models.maverick import Maverick, ProfileStatus, DeploymentStatus
from app.models.maverick_skill import MaverickSkill, ProficiencyLevel
from app.models.assessment import Assessment, AssessmentAttempt
from app.models.batch import Batch
from app.models.pipeline import Pipeline, PipelineJob
from app.services.auth import get_password_hash, create_access_token


# Test database setup
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test_talent_search.db"
engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """Create test database"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """Create test client with database override"""
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def hr_user(db):
    """Create HR user for testing"""
    user = User(
        id=uuid4(),
        email="hr@test.com",
        name="HR Test User",
        role=UserRole.HR,
        password_hash=get_password_hash("testpassword"),
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def hr_token(hr_user):
    """Create JWT token for HR user"""
    return create_access_token(data={"user_id": str(hr_user.id)})


@pytest.fixture
def sample_mavericks(db, hr_user):
    """Create sample mavericks with skills for testing"""
    mavericks = []

    # Create a dummy pipeline for assessment/batch foreign keys
    pipeline = Pipeline(
        id=uuid4(),
        name="Test Training Pipeline",
        description="Test pipeline",
        created_by=hr_user.id
    )
    db.add(pipeline)
    db.flush()

    # Create a dummy batch
    batch = Batch(
        id=uuid4(),
        name="Test Batch 2023",
        pipeline_id=pipeline.id,
        created_by=hr_user.id
    )
    db.add(batch)
    db.flush()

    # Create a dummy pipeline job (required for assessment)
    pipeline_job = PipelineJob(
        id=uuid4(),
        pipeline_id=pipeline.id,
        name="Technical Assessment Job",
        job_type="ASSESSMENT",
        sequence_order=1
    )
    db.add(pipeline_job)
    db.flush()

    # Create a dummy assessment
    assessment = Assessment(
        id=uuid4(),
        job_id=pipeline_job.id,
        batch_id=batch.id,
        title="Technical Assessment",
        description="Test assessment",
        max_marks=100.0,
        passing_marks=60.0,
        created_by=hr_user.id
    )
    db.add(assessment)
    db.flush()

    # Maverick 1: Perfect .NET match
    mav1 = Maverick(
        id=uuid4(),
        name="John Doe",
        email="john@test.com",
        cgpa=8.5,
        deployment_status=DeploymentStatus.AVAILABLE,
        profile_status=ProfileStatus.APPROVED,
        college="Test College",
        degree="B.Tech",
        branch="CSE",
        graduation_year=2023
    )
    db.add(mav1)
    db.flush()
    
    # Skills for Maverick 1
    db.add(MaverickSkill(
        maverick_id=mav1.id,
        skill_name=".NET",
        proficiency_score=90.0,
        proficiency_level="PROFICIENT",
        assessment_score=88.0
    ))
    db.add(MaverickSkill(
        maverick_id=mav1.id,
        skill_name="Azure",
        proficiency_score=85.0,
        proficiency_level="INTERMEDIATE",
        assessment_score=82.0
    ))
    
    # Assessments for Maverick 1 (improving trend)
    for i in range(3):
        db.add(AssessmentAttempt(
            maverick_id=mav1.id,
            assessment_id=assessment.id,
            batch_id=batch.id,
            marks_obtained=75 + (i * 5),
            max_marks=100,
            passed=True,
            evaluated_by=hr_user.id,
            evaluated_at=datetime.utcnow() - timedelta(days=30 * (3 - i))
        ))
    
    mavericks.append(mav1)
    
    # Maverick 2: Similar skill match (C# for .NET)
    mav2 = Maverick(
        id=uuid4(),
        name="Jane Smith",
        email="jane@test.com",
        cgpa=8.0,
        deployment_status=DeploymentStatus.AVAILABLE,
        profile_status=ProfileStatus.APPROVED,
        college="Test College",
        degree="B.Tech",
        branch="CSE",
        graduation_year=2023
    )
    db.add(mav2)
    db.flush()
    
    db.add(MaverickSkill(
        maverick_id=mav2.id,
        skill_name="C#",
        proficiency_score=92.0,
        proficiency_level="PROFICIENT",
        assessment_score=90.0
    ))
    db.add(MaverickSkill(
        maverick_id=mav2.id,
        skill_name="Azure",
        proficiency_score=80.0,
        proficiency_level="INTERMEDIATE",
        assessment_score=78.0
    ))
    
    mavericks.append(mav2)
    
    # Maverick 3: Deployed (should be excluded)
    mav3 = Maverick(
        id=uuid4(),
        name="Bob Wilson",
        email="bob@test.com",
        cgpa=9.0,
        deployment_status=DeploymentStatus.DEPLOYED,  # Not available
        profile_status=ProfileStatus.APPROVED,
        college="Test College",
        degree="B.Tech",
        branch="CSE",
        graduation_year=2023
    )
    db.add(mav3)
    db.flush()
    
    db.add(MaverickSkill(
        maverick_id=mav3.id,
        skill_name=".NET",
        proficiency_score=95.0,
        proficiency_level="PROFICIENT",
        assessment_score=92.0
    ))
    
    mavericks.append(mav3)
    
    db.commit()
    return mavericks


class TestTalentSearchAPI:
    """Integration tests for AI Talent Search API"""

    @patch('app.services.ai_service.AIService._call_ai')
    def test_search_endpoint_authentication_required(self, mock_ai, client):
        """Test that authentication is required"""
        response = client.post(
            "/api/v1/talent-search/search",
            json={
                "query": "Need .NET developer",
                "max_results": 10
            }
        )
        assert response.status_code == 403  # FastAPI returns 403 for missing auth

    @patch('app.services.ai_service.AIService._call_ai')
    def test_search_endpoint_with_exact_matches(self, mock_ai, client, hr_token, sample_mavericks):
        """Test search with exact skill matches"""
        # Mock AI response
        mock_ai.return_value = '{"required_skills": [".NET", "Azure"], "preferred_skills": [], "min_cgpa": 8.0, "graduation_year": null, "degree": null, "branch": null}'

        response = client.post(
            "/api/v1/talent-search/search",
            headers={"Authorization": f"Bearer {hr_token}"},
            json={
                "query": "Need .NET developer with Azure, CGPA > 8",
                "max_results": 50,
                "include_similar": False
            }
        )

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "query" in data
        assert "total_found" in data
        assert "results" in data
        assert "summary" in data
        assert "cost_analysis" in data

        # Should find at least 1 exact match (John Doe)
        assert data["total_found"] >= 1

        # Verify first result
        first_result = data["results"][0]
        assert "id" in first_result
        assert "name" in first_result
        assert "final_score" in first_result
        assert "tier" in first_result
        assert "exact_matches" in first_result
        assert "adaptability_score" in first_result
        assert "learning_weeks_required" in first_result
        assert "match_reasoning" in first_result

        # John Doe should be TIER_1_EXACT
        assert first_result["name"] == "John Doe"
        assert first_result["tier"] == "TIER_1_EXACT"

    @patch('app.services.ai_service.AIService._call_ai')
    def test_search_with_similar_skills(self, mock_ai, client, hr_token, sample_mavericks):
        """Test search includes similar skill matches"""
        mock_ai.return_value = '{"required_skills": [".NET"], "preferred_skills": [], "min_cgpa": 7.0, "graduation_year": null, "degree": null, "branch": null}'

        response = client.post(
            "/api/v1/talent-search/search",
            headers={"Authorization": f"Bearer {hr_token}"},
            json={
                "query": "Need .NET developer",
                "max_results": 50,
                "include_similar": True  # Include similar matches
            }
        )

        assert response.status_code == 200
        data = response.json()

        # Should find both exact and similar matches
        # John Doe (exact .NET) and Jane Smith (C# similar to .NET)
        assert data["total_found"] >= 2

        # Check summary
        summary = data["summary"]
        assert summary["exact_matches"] >= 1
        assert "show_similar_button" in summary

    @patch('app.services.ai_service.AIService._call_ai')
    def test_search_filters_deployed_candidates(self, mock_ai, client, hr_token, sample_mavericks):
        """Test that deployed candidates are excluded"""
        mock_ai.return_value = '{"required_skills": [".NET"], "preferred_skills": [], "min_cgpa": null, "graduation_year": null, "degree": null, "branch": null}'

        response = client.post(
            "/api/v1/talent-search/search",
            headers={"Authorization": f"Bearer {hr_token}"},
            json={
                "query": "Need .NET developer",
                "max_results": 50,
                "include_similar": True
            }
        )

        assert response.status_code == 200
        data = response.json()

        # Bob Wilson (deployed) should NOT be in results
        result_names = [r["name"] for r in data["results"]]
        assert "Bob Wilson" not in result_names

    def test_explain_endpoint(self, client, hr_token, sample_mavericks, db):
        """Test candidate match explanation endpoint"""
        maverick = sample_mavericks[0]  # John Doe

        response = client.get(
            f"/api/v1/talent-search/explain/{maverick.id}",
            headers={"Authorization": f"Bearer {hr_token}"},
            params={"required_skills": ".NET,Azure"}
        )

        assert response.status_code == 200
        data = response.json()

        # Verify explanation structure
        assert "candidate_id" in data
        assert "candidate_name" in data
        assert "skill_gap_analysis" in data
        assert "learning_path" in data
        assert "adaptability_breakdown" in data
        assert "timeline_estimate" in data
        assert "match_reasoning" in data
        assert "recommendation" in data

        # Verify skill gap analysis
        skill_gap = data["skill_gap_analysis"]
        assert "exact_matches" in skill_gap
        assert "total_score" in skill_gap
        assert "match_type" in skill_gap

        # Verify adaptability breakdown
        adapt = data["adaptability_breakdown"]
        assert "score" in adapt
        assert "interpretation" in adapt

    def test_cost_estimate_endpoint(self, client, hr_token):
        """Test cost estimate endpoint"""
        response = client.get(
            "/api/v1/talent-search/cost-estimate",
            headers={"Authorization": f"Bearer {hr_token}"}
        )

        assert response.status_code == 200
        data = response.json()

        assert "per_query_cost" in data
        assert "monthly_estimates" in data
        assert "token_usage" in data
        assert "optimization" in data

        # Verify cost structure
        assert data["per_query_cost"]["total"] < 0.01  # Should be less than $0.01

    def test_statistics_endpoint(self, client, hr_token, sample_mavericks):
        """Test talent pool statistics endpoint"""
        response = client.get(
            "/api/v1/talent-search/statistics",
            headers={"Authorization": f"Bearer {hr_token}"}
        )

        assert response.status_code == 200
        data = response.json()

        assert "talent_pool" in data
        assert "top_skills" in data

        # Should show 2 available candidates (excluding deployed Bob)
        assert data["talent_pool"]["total_available"] == 2

    def test_unauthorized_role_access(self, client, db):
        """Test that non-HR/Manager users cannot access"""
        # Create a Maverick user
        maverick_user = User(
            id=uuid4(),
            email="maverick@test.com",
            name="Maverick User",
            role=UserRole.MAVERICK,
            password_hash=get_password_hash("testpassword"),
            is_active=True
        )
        db.add(maverick_user)
        db.commit()

        token = create_access_token(data={"user_id": str(maverick_user.id)})

        response = client.post(
            "/api/v1/talent-search/search",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "query": "Need .NET developer",
                "max_results": 10
            }
        )

        # Should be forbidden (403)
        assert response.status_code == 403

    @patch('app.services.ai_service.AIService._call_ai')
    def test_show_similar_button_logic(self, mock_ai, client, hr_token, sample_mavericks):
        """Test 'Show Similar' button appears when exact matches <= 2"""
        # Only 1 exact match for .NET
        mock_ai.return_value = '{"required_skills": [".NET"], "preferred_skills": [], "min_cgpa": null, "graduation_year": null, "degree": null, "branch": null}'

        response = client.post(
            "/api/v1/talent-search/search",
            headers={"Authorization": f"Bearer {hr_token}"},
            json={
                "query": "Need .NET developer",
                "max_results": 50,
                "include_similar": False  # Don't include similar
            }
        )

        assert response.status_code == 200
        data = response.json()

        summary = data["summary"]
        # Should show button since exact matches <= 2
        assert summary["show_similar_button"] == True
        assert summary["similar_available"] > 0  # Jane Smith with C#
