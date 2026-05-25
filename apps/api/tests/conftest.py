"""
Pytest configuration and fixtures for tests
"""
import os
import sys
from pathlib import Path

# Set test environment variables FIRST before any imports
os.environ["TESTING"] = "true"
os.environ["DATABASE_URL"] = "postgresql://test:test@localhost:5432/test_db"
os.environ["SUPABASE_URL"] = "http://localhost:54321"
os.environ["SUPABASE_SERVICE_KEY"] = "test_key_for_testing"
os.environ["JWT_SECRET"] = "test_secret_key_for_testing_only"
os.environ["ENVIRONMENT"] = "test"

# Add the parent directory to the path so we can import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session

# Fixtures for all tests

@pytest.fixture
def mock_db():
    """Create a mock database session"""
    return MagicMock(spec=Session)


@pytest.fixture
def sample_maverick():
    """Create a sample maverick for testing"""
    from uuid import uuid4
    from unittest.mock import Mock
    
    maverick = Mock()
    maverick.id = uuid4()
    maverick.name = "Test Maverick"
    maverick.email = "test@example.com"
    maverick.deployment_status = "AVAILABLE"
    maverick.profile_status = "APPROVED"
    maverick.cgpa = 8.5
    maverick.skills = []
    
    return maverick


@pytest.fixture
def sample_skills():
    """Create sample skills for testing"""
    from unittest.mock import Mock
    from app.models.maverick_skill import ProficiencyLevel
    
    return [
        Mock(
            skill_name="Python",
            proficiency_score=90.0,
            proficiency_level=ProficiencyLevel.ADVANCED,
            assessment_score=88.0
        ),
        Mock(
            skill_name="PostgreSQL",
            proficiency_score=85.0,
            proficiency_level=ProficiencyLevel.INTERMEDIATE,
            assessment_score=82.0
        )
    ]
