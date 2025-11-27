"""
Enhanced Agent with NoSQL and Vector DB integration
Automatically stores all scraped candidates and creates embeddings
"""
import asyncio
from typing import List
from src.models import JobDescription, Candidate, RankedCandidate
from src.scrapers import PortalScraperManager
from src.matcher import CandidateMatcher
from src.ranker import CandidateRanker
from src.llm_provider import LLMProvider
from src.nosql_database import mongo_db
from src.vector_database import vector_db
import logging

logger = logging.getLogger(__name__)


class CandidateSourcingAgentNoSQL:
    """Enhanced agent with automatic NoSQL and Vector DB storage"""
    
    def __init__(self, config: dict):
        self.config = config
        self.scraper_manager = PortalScraperManager(config)
        self.matcher = CandidateMatcher(config)
        self.ranker = CandidateRanker(config)
        self.llm_provider = LLMProvider(config)
        logger.info("Agent initialized with NoSQL + Vector DB support")
    
    async def check_existing_candidates(self, job_description: JobDescription, min_results: int = 10) -> List[Candidate]:
        """Check vector DB for existing similar candidates"""
        logger.info("🔍 Checking vector DB for existing candidates...")
        
        try:
            # Search in scraped candidates collection (larger pool)
            results = vector_db.search_by_job(job_description.dict(), n_results=min_results * 2)
            
            if results:
                logger.info(f"✅ Found {len(results)} existing candidates in vector DB")
                
                # Convert vector results to Candidate objects
                candidates = []
                for result in results:
                    metadata = result.get('metadata', {})
                    
                    # Get full candidate data from MongoDB
                    candidate_data = mongo_db.get_candidate(result['id'])
                    if not candidate_data:
                        # Try scraped collection
                        scraped_candidates = mongo_db.get_scraped_candidates()
                        candidate_data = next((c for c in scraped_candidates if c.get('id') == result['id']), None)
                    
                    if candidate_data:
                        try:
                            candidate = Candidate(**candidate_data)
                            candidates.append(candidate)
                        except:
                            logger.warning(f"Could not convert candidate {result['id']}")
                
                logger.info(f"✅ Retrieved {len(candidates)} full candidate profiles")
                return candidates
            else:
                logger.info("No existing candidates found, will scrape fresh")
                return []
                
        except Exception as e:
            logger.error(f"Error checking existing candidates: {e}")
            return []
    
    async def source_candidates(self, job_description: JobDescription) -> List[RankedCandidate]:
        """Main entry point with vector DB lookup and automatic storage"""
        logger.info(f"🚀 Starting candidate sourcing for: {job_description.title}")
        
        # Step 1: Check existing candidates in vector DB
        existing_candidates = await self.check_existing_candidates(job_description, min_results=10)
        
        # Step 2: Scrape new candidates if needed
        if len(existing_candidates) < 10:
            logger.info(f"📡 Scraping new candidates (have {len(existing_candidates)}, need 10+)")
            scraped_candidates = await self.scraper_manager.scrape_all(job_description)
            logger.info(f"Found {len(scraped_candidates)} new candidates")
            
            # Store ALL scraped candidates in MongoDB and Vector DB
            if scraped_candidates:
                await self.store_scraped_candidates(scraped_candidates)
            
            # Combine with existing
            all_candidates = existing_candidates + scraped_candidates
        else:
            logger.info(f"✅ Using {len(existing_candidates)} existing candidates from vector DB")
            all_candidates = existing_candidates
        
        if not all_candidates:
            logger.warning("No candidates found")
            return []
        
        # Step 3: Enrich candidate data (optional)
        try:
            from src.enrichment import CandidateEnricher
            enricher = CandidateEnricher()
            enriched_candidates = []
            for candidate in all_candidates[:50]:
                enriched = await enricher.enrich_candidate(candidate)
                enriched_candidates.append(enriched)
            all_candidates = enriched_candidates
            logger.info(f"Enriched {len(all_candidates)} candidates")
        except Exception as e:
            logger.warning(f"Enrichment failed: {e}. Continuing without enrichment.")
        
        # Step 4: Match candidates using NLP (correct order: job, candidates)
        matched_candidates = self.matcher.match_candidates(job_description, all_candidates)
        logger.info(f"Matched {len(matched_candidates)} candidates")
        
        # Step 5: Rank candidates (correct order: job, candidates)
        ranked_candidates = self.ranker.rank_candidates(job_description, matched_candidates)
        logger.info(f"Ranked {len(ranked_candidates)} candidates")
        
        # Step 6: Get top candidates and add reasoning
        top_candidates = ranked_candidates[:20]
        
        # Add LLM reasoning for top candidates
        for ranked_candidate in top_candidates[:10]:
            try:
                reasoning = await self.llm_provider.generate_candidate_reasoning(
                    ranked_candidate.candidate,
                    job_description
                )
                ranked_candidate.reasoning = reasoning
            except Exception as e:
                logger.warning(f"Failed to generate reasoning: {e}")
                ranked_candidate.reasoning = "AI reasoning unavailable"
        
        # Step 7: Store final candidates in MongoDB and Vector DB
        await self.store_final_candidates(top_candidates)
        
        logger.info(f"✅ Completed sourcing: {len(top_candidates)} final candidates")
        return top_candidates
    
    async def store_scraped_candidates(self, candidates: List[Candidate]):
        """Store ALL scraped candidates in MongoDB and Vector DB"""
        logger.info(f"💾 Storing {len(candidates)} scraped candidates...")
        
        stored_count = 0
        embedding_count = 0
        
        for candidate in candidates:
            try:
                # Prepare candidate data
                candidate_data = {
                    'id': candidate.id,
                    'name': candidate.name,
                    'email': candidate.email,
                    'phone': candidate.phone,
                    'current_title': candidate.current_title,
                    'skills': candidate.skills,
                    'experience_years': candidate.experience_years,
                    'education': candidate.education,
                    'location': candidate.location,
                    'profile_url': candidate.profile_url,
                    'source_portal': candidate.source_portal,
                    'summary': candidate.summary
                }
                
                # Store in MongoDB (scraped collection)
                mongo_db.insert_scraped_candidate(candidate_data)
                stored_count += 1
                
                # Create embedding and store in ChromaDB (scraped collection)
                vector_db.add_candidate(candidate_data, is_final=False)
                embedding_count += 1
                
            except Exception as e:
                logger.error(f"Error storing scraped candidate {candidate.name}: {e}")
        
        logger.info(f"✅ Stored {stored_count} candidates in MongoDB")
        logger.info(f"✅ Created {embedding_count} embeddings in ChromaDB")
    
    async def store_final_candidates(self, ranked_candidates: List[RankedCandidate]):
        """Store final selected candidates in MongoDB and Vector DB"""
        logger.info(f"💾 Storing {len(ranked_candidates)} final candidates...")
        
        stored_count = 0
        embedding_count = 0
        
        for ranked_candidate in ranked_candidates:
            try:
                candidate = ranked_candidate.candidate
                
                # Prepare candidate data
                candidate_data = {
                    'id': candidate.id,
                    'name': candidate.name,
                    'email': candidate.email,
                    'phone': candidate.phone,
                    'current_title': candidate.current_title,
                    'skills': candidate.skills,
                    'experience_years': candidate.experience_years,
                    'education': candidate.education,
                    'location': candidate.location,
                    'profile_url': candidate.profile_url,
                    'source_portal': candidate.source_portal,
                    'summary': candidate.summary
                }
                
                # Store in MongoDB (final candidates collection)
                mongo_db.insert_candidate(candidate_data)
                stored_count += 1
                
                # Create embedding and store in ChromaDB (final collection)
                vector_db.add_candidate(candidate_data, is_final=True)
                embedding_count += 1
                
            except Exception as e:
                logger.error(f"Error storing final candidate {candidate.name}: {e}")
        
        logger.info(f"✅ Stored {stored_count} final candidates in MongoDB")
        logger.info(f"✅ Created {embedding_count} final embeddings in ChromaDB")
