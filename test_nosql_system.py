#!/usr/bin/env python3
"""
Test the new NoSQL + Hard Matching system
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.nosql_db import NoSQLJobDB
from src.hard_matcher import HardMatcher
from src.vector_db import CandidateVectorDB
from src.models import JobDescription, Candidate
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_nosql_db():
    """Test NoSQL database"""
    print("\n" + "="*80)
    print("TEST 1: NoSQL Database")
    print("="*80)
    
    db = NoSQLJobDB()
    stats = db.get_stats()
    
    print(f"✅ NoSQL DB initialized")
    print(f"   Total jobs: {stats['total_jobs']}")
    print(f"   By status: {stats['by_status']}")
    print(f"   Total candidates: {stats['total_candidates']}")

def test_vector_db():
    """Test Vector database"""
    print("\n" + "="*80)
    print("TEST 2: Vector Database")
    print("="*80)
    
    vector_db = CandidateVectorDB()
    stats = vector_db.get_stats()
    
    print(f"✅ Vector DB initialized")
    print(f"   Total candidates: {stats['total_candidates']}")
    print(f"   By source: {stats['by_source']}")

def test_hard_matcher():
    """Test Hard Matcher"""
    print("\n" + "="*80)
    print("TEST 3: Hard Matcher")
    print("="*80)
    
    # Create test job
    job = JobDescription(
        title="Python Developer",
        description="Looking for a Python developer with Django experience",
        required_skills=["Python", "Django", "PostgreSQL", "React"],
        experience_years=5,
        location="Remote"
    )
    
    # Create test candidates
    candidates = [
        Candidate(
            id="1",
            name="John Doe",
            current_title="Senior Python Developer",
            skills=["Python", "Django", "PostgreSQL", "Docker"],
            experience_years=6,
            location="USA",
            profile_url="https://linkedin.com/in/johndoe",
            source_portal="linkedin"
        ),
        Candidate(
            id="2",
            name="Jane Smith",
            current_title="Full Stack Developer",
            skills=["Python", "React", "Node.js", "MongoDB"],
            experience_years=4,
            location="India",
            profile_url="https://naukri.com/profile/janesmith",
            source_portal="naukri"
        ),
        Candidate(
            id="3",
            name="Bob Wilson",
            current_title="Backend Developer",
            skills=["Java", "Spring", "MySQL"],
            experience_years=7,
            location="UK",
            profile_url="https://stackoverflow.com/users/bobwilson",
            source_portal="stackoverflow"
        ),
        Candidate(
            id="4",
            name="Alice Johnson",
            current_title="Python Engineer",
            skills=["Python", "Django", "React", "PostgreSQL", "AWS"],
            experience_years=5,
            location="Canada",
            profile_url="https://github.com/alicejohnson",
            source_portal="github"
        )
    ]
    
    # Test matching
    matcher = HardMatcher()
    matched = matcher.match_candidates(job, candidates)
    
    print(f"\n✅ Matched {len(matched)} candidates:")
    for i, match in enumerate(matched, 1):
        cand = match['candidate']
        print(f"\n   {i}. {cand.name} ({cand.source_portal})")
        print(f"      Combined Score: {match['combined_score']:.2f}")
        print(f"      Skill Match: {match['skill_score']:.2f} ({len(match['matched_skills'])}/{len(job.required_skills)} skills)")
        print(f"      Experience Match: {match['experience_score']:.2f}")
        print(f"      Matched Skills: {', '.join(match['matched_skills'])}")
        if match['missing_skills']:
            print(f"      Missing Skills: {', '.join(match['missing_skills'])}")
    
    # Test balancing
    print(f"\n   Testing balancing...")
    balanced = matcher.balance_by_source(matched, max_results=10)
    
    print(f"\n✅ Balanced to {len(balanced)} candidates:")
    for i, match in enumerate(balanced, 1):
        cand = match['candidate']
        print(f"   {i}. {cand.name} ({cand.source_portal}) - Score: {match['combined_score']:.2f}")

def main():
    print("\n" + "="*80)
    print("TESTING NEW NOSQL + HARD MATCHING SYSTEM")
    print("="*80)
    
    try:
        test_nosql_db()
        test_vector_db()
        test_hard_matcher()
        
        print("\n" + "="*80)
        print("✅ ALL TESTS PASSED!")
        print("="*80)
        print("\nYou can now start the API server:")
        print("  python3 run_api.py")
        print("\n")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
