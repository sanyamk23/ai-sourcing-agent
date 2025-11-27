"""
Test the fixed LinkedIn scraper
"""
import asyncio
import sys
import os
import yaml
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.scrapers import LinkedInScraper
from src.models import JobDescription
from dotenv import load_dotenv

load_dotenv()

async def test_linkedin():
    print("="*60)
    print("TESTING FIXED LINKEDIN SCRAPER")
    print("="*60)
    
    # Load config
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)
    
    scraper = LinkedInScraper(
        portal_name="linkedin",
        base_url="https://www.linkedin.com",
        config=config
    )
    
    job = JobDescription(
        title="Python Developer",
        description="Looking for Python developers",
        required_skills=["Python", "Django", "FastAPI"],
        experience_years=3,
        location="United States"
    )
    
    print(f"\nSearching for: {job.title}")
    print(f"Location: {job.location}")
    print(f"Max candidates: 5\n")
    
    candidates = await scraper.scrape(job)
    
    print("\n" + "="*60)
    print(f"RESULTS: Found {len(candidates)} candidates")
    print("="*60)
    
    for i, candidate in enumerate(candidates, 1):
        print(f"\n{i}. {candidate.name}")
        print(f"   Title: {candidate.current_title}")
        print(f"   Location: {candidate.location}")
        print(f"   URL: {candidate.profile_url}")

if __name__ == "__main__":
    asyncio.run(test_linkedin())
