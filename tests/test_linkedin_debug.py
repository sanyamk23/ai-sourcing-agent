#!/usr/bin/env python3
"""Debug LinkedIn scraper - shows what's happening"""

import asyncio
import yaml
import os
from dotenv import load_dotenv
from src.models import JobDescription
from src.scrapers import LinkedInScraper
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

load_dotenv()

async def test_linkedin_debug():
    """Test LinkedIn with detailed debugging"""
    
    # Load config
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)
    
    # Force non-headless and longer waits
    config['scraping']['headless'] = False
    config['scraping']['rate_limit_delay'] = 5
    
    job_desc = JobDescription(
        title="Software Engineer",
        description="Looking for software engineers",
        required_skills=["Python", "JavaScript"],
        experience_years=3,
        location="United States"
    )
    
    logger.info("="*80)
    logger.info("LINKEDIN DEBUG TEST")
    logger.info("="*80)
    logger.info("\nBrowser will open - WATCH WHAT HAPPENS")
    logger.info("If CAPTCHA appears, solve it manually")
    logger.info("Browser will stay open for 30 seconds after search")
    logger.info("="*80 + "\n")
    
    linkedin_scraper = LinkedInScraper("linkedin", "https://www.linkedin.com", config)
    
    try:
        candidates = await linkedin_scraper.scrape(job_desc)
        
        logger.info("\n" + "="*80)
        logger.info(f"RESULT: Found {len(candidates)} candidates")
        logger.info("="*80)
        
        if candidates:
            for i, c in enumerate(candidates[:5], 1):
                logger.info(f"{i}. {c.name} - {c.current_title}")
        else:
            logger.warning("\n⚠️  NO CANDIDATES FOUND")
            logger.warning("\nPossible reasons:")
            logger.warning("1. LinkedIn detected automation")
            logger.warning("2. CAPTCHA not solved")
            logger.warning("3. Search page didn't load")
            logger.warning("4. CSS selectors changed")
            logger.warning("\nCheck the browser window to see what happened!")
    
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(test_linkedin_debug())
