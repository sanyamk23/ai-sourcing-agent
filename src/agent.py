import asyncio
from typing import List
from src.models import JobDescription, Candidate, RankedCandidate, Job, JobStatus
from src.scrapers import PortalScraperManager
from src.matcher import CandidateMatcher
from src.ranker import CandidateRanker
from src.llm_provider import LLMProvider
from src.job_expander import JobExpander
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
        self.job_expander = JobExpander(self.llm_provider)
        logger.info("Agent initialized with Groq/OpenAI support and job expansion")
    

    
    async def source_candidates(self, job_description: JobDescription) -> List[RankedCandidate]:
        """Main entry point for candidate sourcing"""
        logger.info(f"Starting candidate sourcing for: {job_description.title}")
        
        # Step 0: Expand job titles and skills using LLM
        logger.info("🔄 Expanding job titles and skills...")
        expanded_data = self.job_expander.expand_job_data(
            job_title=job_description.title,
            skills=job_description.required_skills
        )
        
        # Create expanded job descriptions for scraping
        expanded_job_descriptions = []
        for job_title in expanded_data["job_titles"]:
            expanded_jd = JobDescription(
                title=job_title,
                description=job_description.description,
                required_skills=expanded_data["skills"],
                experience_years=job_description.experience_years,
                location=job_description.location,
                salary_range=job_description.salary_range
            )
            expanded_job_descriptions.append(expanded_jd)
        
        logger.info(f"✓ Created {len(expanded_job_descriptions)} job title variations:")
        for jd in expanded_job_descriptions:
            logger.info(f"  - {jd.title}")
        logger.info(f"✓ Expanded skills from {len(job_description.required_skills)} to {len(expanded_data['skills'])}")
        
        # Step 1: Scrape candidates from all portals using expanded job descriptions
        all_candidates = []
        seen_ids = set()
        
        for expanded_jd in expanded_job_descriptions:
            logger.info(f"Scraping for: {expanded_jd.title}")
            candidates = await self.scraper_manager.scrape_all(expanded_jd)
            
            # Deduplicate candidates
            for candidate in candidates:
                if candidate.id not in seen_ids:
                    all_candidates.append(candidate)
                    seen_ids.add(candidate.id)
        
        candidates = all_candidates
        logger.info(f"Found {len(candidates)} unique raw candidates across all job title variations")
        
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
        
        # Step 3: Match candidates using NLP (with expanded skills)
        # Use the original job description but with expanded skills for better matching
        enhanced_jd = JobDescription(
            title=job_description.title,
            description=job_description.description,
            required_skills=expanded_data["skills"],
            experience_years=job_description.experience_years,
            location=job_description.location,
            salary_range=job_description.salary_range
        )
        matched = self.matcher.match_candidates(enhanced_jd, candidates)
        logger.info(f"Matched {len(matched)} candidates above threshold")
        
        if not matched:
            logger.warning("No candidates matched the job requirements")
            return []
        
        # Step 4: Rank candidates
        ranked = self.ranker.rank_candidates(job_description, matched)
        logger.info(f"Ranked top {len(ranked)} candidates")
        
        return ranked
