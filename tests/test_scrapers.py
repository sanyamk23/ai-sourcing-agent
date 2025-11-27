#!/usr/bin/env python3
"""Test script to verify scrapers are working with real data"""

import asyncio
import yaml
import os
from dotenv import load_dotenv
from src.models import JobDescription
from src.scrapers import PortalScraperManager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

async def test_scrapers():
    """Test all scrapers with a sample job description"""
    
    # Load config
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)
    
    # Replace env variables
    config['llm']['groq_api_key'] = os.getenv('GROQ_API_KEY')
    config['llm']['openai_api_key'] = os.getenv('OPENAI_API_KEY')
    config['linkedin']['username'] = os.getenv('LINKEDIN_USERNAME')
    config['linkedin']['password'] = os.getenv('LINKEDIN_PASSWORD')
    
    # Create test job description
    job_desc = JobDescription(
        title="Python Developer",
        description="Looking for a Python developer with web development experience",
        required_skills=["Python", "Django", "FastAPI", "PostgreSQL"],
        experience_years=3,
        location="San Francisco, CA"
    )
    
    logger.info(f"Testing scrapers for job: {job_desc.title}")
    logger.info(f"Required skills: {', '.join(job_desc.required_skills)}")
    
    # Initialize scraper manager
    scraper_manager = PortalScraperManager(config)
    
    logger.info(f"Initialized {len(scraper_manager.scrapers)} scrapers")
    
    # Test each scraper individually
    for scraper in scraper_manager.scrapers:
        logger.info(f"\n{'='*60}")
        logger.info(f"Testing {scraper.portal_name}...")
        logger.info(f"{'='*60}")
        
        try:
            candidates = await scraper.scrape(job_desc)
            logger.info(f"✓ {scraper.portal_name}: Found {len(candidates)} candidates")
            
            # Show first 3 candidates
            for i, candidate in enumerate(candidates[:3], 1):
                logger.info(f"\n  Candidate {i}:")
                logger.info(f"    Name: {candidate.name}")
                logger.info(f"    Title: {candidate.current_title}")
                logger.info(f"    Skills: {', '.join(candidate.skills[:5])}")
                logger.info(f"    Location: {candidate.location}")
                logger.info(f"    Profile: {candidate.profile_url}")
                if candidate.summary:
                    logger.info(f"    Summary: {candidate.summary[:100]}...")
        
        except Exception as e:
            logger.error(f"✗ {scraper.portal_name}: Failed - {e}")
    
    # Test all scrapers together
    logger.info(f"\n{'='*60}")
    logger.info("Testing all scrapers together...")
    logger.info(f"{'='*60}")
    
    try:
        all_candidates = await scraper_manager.scrape_all(job_desc)
        logger.info(f"\n✓ Total unique candidates: {len(all_candidates)}")
        
        # Show breakdown by portal
        portal_counts = {}
        for candidate in all_candidates:
            portal_counts[candidate.source_portal] = portal_counts.get(candidate.source_portal, 0) + 1
        
        logger.info("\nBreakdown by portal:")
        for portal, count in portal_counts.items():
            logger.info(f"  {portal}: {count} candidates")
    
    except Exception as e:
        logger.error(f"✗ Combined scraping failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_scrapers())
