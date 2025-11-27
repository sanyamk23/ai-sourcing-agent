"""Pytest configuration and fixtures"""
import pytest
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

@pytest.fixture
def sample_job_description():
    """Sample job description for testing"""
    from src.models import JobDescription
    return JobDescription(
        title="Python Developer",
        description="Looking for experienced Python developer",
        required_skills=["Python", "Django", "FastAPI"],
        experience_years=3,
        location="San Francisco"
    )

@pytest.fixture
def sample_candidate():
    """Sample candidate for testing"""
    from src.models import Candidate
    return Candidate(
        id="test-123",
        name="John Doe",
        current_title="Senior Python Developer",
        skills=["Python", "Django", "PostgreSQL"],
        experience_years=5,
        location="San Francisco",
        profile_url="https://example.com/profile",
        source_portal="test",
        summary="Experienced developer"
    )
