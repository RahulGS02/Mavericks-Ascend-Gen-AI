"""
Test Runner Script - Sets up environment and runs tests
"""
import os
import sys
import subprocess

# Set test environment variables
os.environ["TESTING"] = "true"
os.environ["DATABASE_URL"] = "postgresql://test:test@localhost:5432/test_db"
os.environ["SUPABASE_URL"] = "http://localhost:54321"
os.environ["SUPABASE_SERVICE_KEY"] = "test_key_for_testing"
os.environ["JWT_SECRET"] = "test_secret_key_for_testing_only"
os.environ["ENVIRONMENT"] = "test"

print("=" * 60)
print("Running Skill Similarity Engine Unit Tests")
print("=" * 60)
print()
print("Environment: TEST MODE")
print()

# Run pytest
result = subprocess.run(
    [sys.executable, "-m", "pytest", "tests/test_skill_similarity_engine.py", "-v", "--tb=short"],
    cwd=os.path.dirname(__file__)
)

print()
print("=" * 60)
print(f"Test execution complete! Exit code: {result.returncode}")
print("=" * 60)

sys.exit(result.returncode)
