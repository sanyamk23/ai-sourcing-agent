#!/usr/bin/env python3
"""
Test LinkedIn scraper with improved selectors
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from src.models import JobDescription
from src.scrapers import LinkedInScraper
import yaml

async def test_linkedin():
    """Test LinkedIn scraper"""
    print("\n" + "="*60)
    print("TESTING LINKEDIN SCRAPER")
    print("="*60)
    
    # Load config
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    # Create scraper
    scraper = LinkedInScraper(
        portal_name='linkedin',
        base_url='https://www.linkedin.com',
        config=config
    )
    
    # Create test job
    job = JobDescription(
        title="Python Developer",
        required_skills=["Python", "Django", "REST API"],
        location="India",
        experience_years=3
    )
    
    print(f"\n1. Searching for: {job.title}")
    print(f"   Location: {job.location}")
    print(f"   Skills: {', '.join(job.required_skills)}")
    
    print("\n2. Starting scrape...")
    candidates = await scraper.scrape(job)
    
    print(f"\n3. Results:")
    print(f"   ✅ Found {len(candidates)} candidates")
    
    if candidates:
        print("\n4. Sample candidates:")
        for i, candidate in enumerate(candidates[:5], 1):
            print(f"   {i}. {candidate.name} - {candidate.current_title}")
            print(f"      Location: {candidate.location}")
            print(f"      Profile: {candidate.profile_url[:60]}...")
    else:
        print("\n⚠️  No candidates found")
        print("   Check linkedin_page_debug.html for page source")
    
    print("\n" + "="*60)
    print("TEST COMPLETE")
    print("="*60)
    print("\n💡 Browser window left open for inspection")
    print("   Close it manually when done\n")

if __name__ == "__main__":
    asyncio.run(test_linkedin())
