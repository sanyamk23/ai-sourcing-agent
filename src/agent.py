import asyncio
from typing import List
from src.models import JobDescription, Candidate, RankedCandidate, Job, JobStatus
from src.scrapers import PortalScraperManager
from src.matcher import CandidateMatcher
from src.ranker import CandidateRanker
from src.llm_provider import LLMProvider
import logging

logger = logging.getLogger(__name__)

class CandidateSourcingAgent:
    """Agentic AI that orchestrates candidate sourcing workflow"""
    
    def __init__(self, config: dict):
        self.config = config
        self.scraper_manager = PortalScraperManager(config)
        self.matcher = CandidateMatcher(config)
        self.ranker = CandidateRanker(config)
        self.llm_provider = LLMProvider(config)
        logger.info("Agent initialized with Groq/OpenAI support")
    

    
    async def source_candidates(self, job_description: JobDescription) -> List[RankedCandidate]:
        """Main entry point for candidate sourcing"""
        logger.info(f"Starting candidate sourcing for: {job_description.title}")
        
        # Step 1: Scrape candidates from all portals
        candidates = await self.scraper_manager.scrape_all(job_description)
        logger.info(f"Found {len(candidates)} raw candidates")
        
        if not candidates:
            logger.warning("No candidates found from any portal")
            return []
        
        # Step 2: Enrich candidate data (optional)
        try:
            from src.enrichment import CandidateEnricher
            enricher = CandidateEnricher()
            enriched_candidates = []
            for candidate in candidates[:50]:  # Limit enrichment to top 50
                enriched = await enricher.enrich_candidate(candidate)
                enriched_candidates.append(enriched)
            candidates = enriched_candidates
            logger.info(f"Enriched {len(candidates)} candidates")
        except Exception as e:
            logger.warning(f"Enrichment failed: {e}. Continuing without enrichment.")
        
        # Step 3: Match candidates using NLP
        matched = self.matcher.match_candidates(job_description, candidates)
        logger.info(f"Matched {len(matched)} candidates above threshold")
        
        if not matched:
            logger.warning("No candidates matched the job requirements")
            return []
        
        # Step 4: Rank candidates
        ranked = self.ranker.rank_candidates(job_description, matched)
        logger.info(f"Ranked top {len(ranked)} candidates")
        
        return ranked
