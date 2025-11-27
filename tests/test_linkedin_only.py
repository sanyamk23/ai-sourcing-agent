#!/usr/bin/env python3
"""Test LinkedIn scraper specifically"""

import asyncio
import yaml
import os
from dotenv import load_dotenv
from src.models import JobDescription
from src.scrapers import LinkedInScraper
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

async def test_linkedin():
    """Test LinkedIn scraper"""
    
    # Load config
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)
    
    # Check credentials
    username = os.getenv('LINKEDIN_USERNAME')
    password = os.getenv('LINKEDIN_PASSWORD')
    
    if not username or not password:
        logger.error("❌ LinkedIn credentials not found in .env file")
        logger.info("\nPlease add to .env:")
        logger.info("LINKEDIN_USERNAME=your_email@example.com")
        logger.info("LINKEDIN_PASSWORD=your_password")
        return
    
    logger.info("="*80)
    logger.info("TESTING LINKEDIN SCRAPER")
    logger.info("="*80)
    logger.info(f"\nLinkedIn Username: {username}")
    logger.info("LinkedIn Password: ********")
    
    # Create test job description
    job_desc = JobDescription(
        title="Python Developer",
        description="Looking for a Python developer with web development experience",
        required_skills=["Python", "Django", "FastAPI", "PostgreSQL"],
        experience_years=3,
        location="San Francisco Bay Area"
    )
    
    logger.info(f"\nSearching for: {job_desc.title}")
    logger.info(f"Location: {job_desc.location}")
    logger.info(f"Skills: {', '.join(job_desc.required_skills)}")
    
    # Initialize LinkedIn scraper
    linkedin_scraper = LinkedInScraper("linkedin", "https://www.linkedin.com", config)
    
    logger.info("\n" + "-"*80)
    logger.info("Starting LinkedIn scrape...")
    logger.info("NOTE: Browser will open (non-headless mode for better success)")
    logger.info("If CAPTCHA appears, please solve it manually")
    logger.info("-"*80 + "\n")
    
    try:
        candidates = await linkedin_scraper.scrape(job_desc)
        
        logger.info("\n" + "="*80)
        logger.info("RESULTS")
        logger.info("="*80)
        logger.info(f"\n✓ Found {len(candidates)} candidates from LinkedIn\n")
        
        # Show all candidates
        for i, candidate in enumerate(candidates, 1):
            logger.info(f"{i}. {candidate.name}")
            logger.info(f"   Title: {candidate.current_title}")
            logger.info(f"   Location: {candidate.location}")
            logger.info(f"   Profile: {candidate.profile_url}")
            logger.info(f"   Skills: {', '.join(candidate.skills[:5])}")
            logger.info("")
        
        if candidates:
            logger.info("="*80)
            logger.info("✅ SUCCESS! LinkedIn scraper is working!")
            logger.info("="*80)
        else:
            logger.warning("="*80)
            logger.warning("⚠ No candidates found. Possible issues:")
            logger.warning("  1. Login failed (check credentials)")
            logger.warning("  2. CAPTCHA required (solve manually)")
            logger.warning("  3. Rate limiting (try again later)")
            logger.warning("  4. Search returned no results")
            logger.warning("="*80)
    
    except Exception as e:
        logger.error(f"\n❌ Error: {e}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(test_linkedin())
