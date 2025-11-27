#!/usr/bin/env python3
"""Quick test using only fast API-based scrapers (GitHub & StackOverflow)"""

import asyncio
import yaml
import os
from dotenv import load_dotenv
from src.models import JobDescription, Candidate
from src.scrapers import GitHubJobsScraper, StackOverflowScraper
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

async def test_quick():
    """Quick test with fast scrapers only"""
    
    # Load config
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)
    
    # Create test job description
    job_desc = JobDescription(
        title="Python Developer",
        description="Looking for a Python developer",
        required_skills=["Python", "Django", "FastAPI"],
        experience_years=3,
        location="Remote"
    )
    
    logger.info("="*80)
    logger.info("QUICK TEST - Fast API-based Scrapers Only")
    logger.info("="*80)
    logger.info(f"\nJob: {job_desc.title}")
    logger.info(f"Skills: {', '.join(job_desc.required_skills)}")
    
    all_candidates = []
    
    # Test GitHub
    logger.info("\n" + "-"*80)
    logger.info("Testing GitHub API...")
    logger.info("-"*80)
    github_scraper = GitHubJobsScraper("github_jobs", "https://github.com", config)
    try:
        github_candidates = await github_scraper.scrape(job_desc)
        logger.info(f"✓ GitHub: Found {len(github_candidates)} candidates")
        all_candidates.extend(github_candidates)
        
        # Show first 3
        for i, candidate in enumerate(github_candidates[:3], 1):
            logger.info(f"\n  {i}. {candidate.name}")
            logger.info(f"     Skills: {', '.join(candidate.skills)}")
            logger.info(f"     Profile: {candidate.profile_url}")
            if candidate.summary:
                logger.info(f"     {candidate.summary}")
    except Exception as e:
        logger.error(f"✗ GitHub failed: {e}")
    
    # Test StackOverflow
    logger.info("\n" + "-"*80)
    logger.info("Testing StackOverflow API...")
    logger.info("-"*80)
    so_scraper = StackOverflowScraper("stackoverflow", "https://stackoverflow.com", config)
    try:
        so_candidates = await so_scraper.scrape(job_desc)
        logger.info(f"✓ StackOverflow: Found {len(so_candidates)} candidates")
        all_candidates.extend(so_candidates)
        
        # Show first 3
        for i, candidate in enumerate(so_candidates[:3], 1):
            logger.info(f"\n  {i}. {candidate.name}")
            logger.info(f"     Skills: {', '.join(candidate.skills)}")
            logger.info(f"     Profile: {candidate.profile_url}")
            if candidate.summary:
                logger.info(f"     {candidate.summary}")
    except Exception as e:
        logger.error(f"✗ StackOverflow failed: {e}")
    
    # Summary
    logger.info("\n" + "="*80)
    logger.info("SUMMARY")
    logger.info("="*80)
    logger.info(f"Total candidates found: {len(all_candidates)}")
    logger.info(f"GitHub: {len([c for c in all_candidates if c.source_portal == 'github'])}")
    logger.info(f"StackOverflow: {len([c for c in all_candidates if c.source_portal == 'stackoverflow'])}")
    
    if all_candidates:
        logger.info("\n✅ Quick test passed! Scrapers are working.")
        logger.info("\nNext steps:")
        logger.info("  1. Run full test: python test_full_pipeline.py")
        logger.info("  2. Start API: python src/api_server.py")
        logger.info("  3. Use example: python example_usage.py")
    else:
        logger.warning("\n⚠ No candidates found. This might be due to rate limiting.")
        logger.info("Try again in a few minutes or check your internet connection.")
    
    logger.info("="*80)

if __name__ == "__main__":
    asyncio.run(test_quick())
