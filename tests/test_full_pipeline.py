#!/usr/bin/env python3
"""Test the full candidate sourcing pipeline"""

import asyncio
import yaml
import os
from dotenv import load_dotenv
from src.models import JobDescription
from src.agent import CandidateSourcingAgent
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

async def test_full_pipeline():
    """Test the complete pipeline: scrape -> match -> rank"""
    
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
        title="Senior Full Stack Developer",
        description="""We are seeking an experienced Full Stack Developer to join our team.
        The ideal candidate will have strong experience in Python, React, and cloud technologies.
        You will be responsible for building scalable web applications and APIs.""",
        required_skills=["Python", "React", "FastAPI", "PostgreSQL", "Docker", "AWS"],
        experience_years=5,
        location="Remote"
    )
    
    logger.info("="*80)
    logger.info("TESTING FULL CANDIDATE SOURCING PIPELINE")
    logger.info("="*80)
    logger.info(f"\nJob Title: {job_desc.title}")
    logger.info(f"Required Skills: {', '.join(job_desc.required_skills)}")
    logger.info(f"Experience: {job_desc.experience_years} years")
    logger.info(f"Location: {job_desc.location}")
    
    # Initialize agent
    logger.info("\nInitializing AI Agent...")
    agent = CandidateSourcingAgent(config)
    
    # Run full pipeline
    logger.info("\nStarting candidate sourcing...")
    logger.info("This may take several minutes...\n")
    
    try:
        ranked_candidates = await agent.source_candidates(job_desc)
        
        logger.info("\n" + "="*80)
        logger.info("RESULTS")
        logger.info("="*80)
        logger.info(f"\nFound {len(ranked_candidates)} top candidates\n")
        
        # Display top 10 candidates
        for i, ranked_candidate in enumerate(ranked_candidates[:10], 1):
            candidate = ranked_candidate.candidate
            score = ranked_candidate.match_score
            breakdown = ranked_candidate.match_breakdown
            reasoning = ranked_candidate.reasoning
            
            logger.info(f"\n{'─'*80}")
            logger.info(f"#{i} - {candidate.name} (Match Score: {score:.2%})")
            logger.info(f"{'─'*80}")
            logger.info(f"Title: {candidate.current_title}")
            logger.info(f"Skills: {', '.join(candidate.skills)}")
            logger.info(f"Experience: {candidate.experience_years} years")
            logger.info(f"Location: {candidate.location}")
            logger.info(f"Source: {candidate.source_portal}")
            logger.info(f"Profile: {candidate.profile_url}")
            
            if candidate.email:
                logger.info(f"Email: {candidate.email}")
            
            logger.info(f"\nMatch Breakdown:")
            for factor, value in breakdown.items():
                logger.info(f"  {factor}: {value:.2%}")
            
            logger.info(f"\nAI Reasoning:")
            logger.info(f"  {reasoning}")
            
            if candidate.summary:
                logger.info(f"\nSummary:")
                logger.info(f"  {candidate.summary[:200]}...")
        
        logger.info("\n" + "="*80)
        logger.info("PIPELINE TEST COMPLETED SUCCESSFULLY")
        logger.info("="*80)
        
    except Exception as e:
        logger.error(f"\n✗ Pipeline failed: {e}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(test_full_pipeline())
