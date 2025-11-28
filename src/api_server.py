from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import List
import yaml
import uuid
from datetime import datetime
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models import JobDescription, Job, JobStatus, RankedCandidate, Candidate
from src.agent import CandidateSourcingAgent
from src.nosql_db import NoSQLJobDB
from src.hard_matcher import HardMatcher
import asyncio
import logging
import os
import json
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Candidate Sourcing API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load config
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

# Replace env variables in config
config['llm']['groq_api_key'] = os.getenv('GROQ_API_KEY')
config['llm']['openai_api_key'] = os.getenv('OPENAI_API_KEY')
config['linkedin']['username'] = os.getenv('LINKEDIN_USERNAME')
config['linkedin']['password'] = os.getenv('LINKEDIN_PASSWORD')

# Initialize agent and databases
agent = CandidateSourcingAgent(config)
nosql_db = NoSQLJobDB()
hard_matcher = HardMatcher()

# In-memory storage for job status (for real-time updates)
jobs_db = {}

# Track polling count per job to prevent excessive calls
job_poll_count = {}

# API Routes - specific routes MUST come before parameterized routes
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/api/candidates")
async def get_all_candidates():
    """Get all candidates from vector database"""
    try:
        from src.vector_db import CandidateVectorDB
        vector_db = CandidateVectorDB()
        stats = vector_db.get_stats()
        return {
            "total": stats['total_candidates'],
            "by_source": stats['by_source'],
            "message": "Use /jobs/{job_id} to see matched candidates for a specific job"
        }
    except Exception as e:
        logger.error(f"Error fetching candidates: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/database/stats")
async def get_database_stats():
    """Get comprehensive database statistics"""
    try:
        from src.vector_db import CandidateVectorDB
        from collections import Counter
        
        # Vector DB stats
        vector_db = CandidateVectorDB()
        vector_stats = vector_db.get_stats()
        
        # Get detailed vector DB info
        results = vector_db.collection.get()
        all_skills = []
        titles = []
        
        for metadata in results['metadatas']:
            skills_str = metadata.get('skills', '[]')
            try:
                if isinstance(skills_str, str):
                    skills = json.loads(skills_str)
                else:
                    skills = skills_str
                all_skills.extend(skills)
            except:
                pass
            
            title = metadata.get('title', 'N/A')
            if title != 'N/A':
                titles.append(title)
        
        skill_counts = Counter(all_skills)
        title_counts = Counter(titles)
        
        # NoSQL DB stats
        jobs = nosql_db.get_all_jobs()
        total_matched = sum(len(job.candidates) for job in jobs)
        
        return {
            "vector_db": {
                "total_candidates": vector_stats['total_candidates'],
                "by_source": vector_stats['by_source'],
                "top_skills": dict(skill_counts.most_common(20)),
                "top_titles": dict(title_counts.most_common(10))
            },
            "nosql_db": {
                "total_jobs": len(jobs),
                "total_matched_candidates": total_matched,
                "average_matches_per_job": total_matched / len(jobs) if jobs else 0
            },
            "health": {
                "vector_db_populated": vector_stats['total_candidates'] > 0,
                "nosql_db_populated": len(jobs) > 0,
                "match_rate": (total_matched / vector_stats['total_candidates'] * 100) if vector_stats['total_candidates'] > 0 else 0
            }
        }
    except Exception as e:
        logger.error(f"Error fetching database stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/jobs/all")
async def get_all_jobs():
    """Get all jobs from NoSQL database"""
    try:
        jobs = nosql_db.get_all_jobs()
        return [
            {
                "id": j.id,
                "title": j.description.title,
                "description": j.description.description,
                "required_skills": j.description.required_skills,
                "experience_years": j.description.experience_years,
                "location": j.description.location,
                "status": j.status.value if hasattr(j.status, 'value') else str(j.status),
                "candidates": [c.dict() if hasattr(c, 'dict') else c for c in (j.candidates if j.candidates else [])],
                "created_at": j.created_at.isoformat() if hasattr(j.created_at, 'isoformat') else str(j.created_at)
            }
            for j in jobs
        ]
    except Exception as e:
        logger.error(f"Error fetching jobs: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/candidate/{candidate_id}/profile")
async def get_candidate_profile(candidate_id: str):
    """Get detailed candidate profile from vector database"""
    try:
        from src.vector_db import CandidateVectorDB
        vector_db = CandidateVectorDB()
        
        candidate_data = vector_db.get_by_id(candidate_id)
        if not candidate_data:
            raise HTTPException(status_code=404, detail="Candidate not found")
        
        metadata = candidate_data['metadata']
        
        # Parse experience from summary if available
        experience_data = []
        if metadata.get('summary'):
            experience_data = parse_experience_from_summary(metadata['summary'])
        
        return {
            "id": candidate_id,
            "name": metadata.get('name', 'N/A'),
            "email": metadata.get('email', ''),
            "phone": metadata.get('phone', ''),
            "current_title": metadata.get('title', ''),
            "skills": metadata.get('skills', '[]'),
            "experience_years": metadata.get('experience_years', 0),
            "education": metadata.get('education', ''),
            "location": metadata.get('location', ''),
            "profile_url": metadata.get('profile_url', ''),
            "source_portal": metadata.get('source', ''),
            "summary": metadata.get('summary', ''),
            "experience": experience_data
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching candidate profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def parse_experience_from_summary(summary: str) -> list:
    """Parse experience information from candidate summary"""
    # This is a simple parser - in production, you'd scrape LinkedIn directly
    experiences = []
    
    # Look for common patterns in summaries
    if not summary:
        return []
    
    # Try to extract company names and roles
    lines = summary.split('\n')
    for line in lines:
        line = line.strip()
        if any(keyword in line.lower() for keyword in ['worked at', 'experience at', 'engineer at', 'developer at', 'manager at']):
            experiences.append({
                "title": "Position extracted from summary",
                "company": line,
                "duration": "Duration not specified",
                "description": line
            })
    
    # If no experience found, return a placeholder
    if not experiences:
        experiences = [{
            "title": "Experience details",
            "company": "See full profile for details",
            "duration": "Various",
            "description": summary[:200] + "..." if len(summary) > 200 else summary
        }]
    
    return experiences

@app.post("/jobs", response_model=Job)
async def create_job(job_description: JobDescription):
    """Submit a new job description for candidate sourcing"""
    job_id = str(uuid.uuid4())
    job = Job(
        id=job_id,
        description=job_description,
        status=JobStatus.PENDING,
        created_at=datetime.now()
    )
    jobs_db[job_id] = job
    
    # Start sourcing in background
    asyncio.create_task(process_job(job_id))
    
    return job

async def process_job(job_id: str):
    """Background task to process job - Hard matching with balanced results"""
    try:
        job = jobs_db[job_id]
        job.status = JobStatus.PROCESSING
        
        logger.info(f"Starting candidate sourcing for job {job_id}")
        
        # PHASE 1: Scrape candidates from all portals
        logger.info(f"Phase 1: Scraping candidates...")
        raw_candidates = await agent.scraper_manager.scrape_all_sequential(job.description)
        logger.info(f"Found {len(raw_candidates)} raw candidates")
        
        if not raw_candidates:
            logger.warning("No candidates found from any portal")
            job.status = JobStatus.FAILED
            job.candidates = []
            nosql_db.save_job(job)
            return
        
        # PHASE 2: Semantic search in Vector DB for additional relevant candidates
        logger.info(f"Phase 2: Searching Vector DB for relevant candidates...")
        from src.vector_db import CandidateVectorDB
        vector_db = CandidateVectorDB()
        
        # Create search query from job description
        search_query = f"{job.description.title} {' '.join(job.description.required_skills)} {job.description.description}"
        
        # Search for similar candidates (get more than needed)
        similar_candidates_data = vector_db.search_similar(search_query, n_results=50)
        
        # Convert vector DB results to Candidate objects
        from src.models import Candidate
        vector_candidates = []
        for result in similar_candidates_data:
            metadata = result['metadata']
            try:
                # Parse skills
                skills_str = metadata.get('skills', '[]')
                if isinstance(skills_str, str):
                    skills = json.loads(skills_str) if skills_str else []
                else:
                    skills = skills_str
                
                candidate = Candidate(
                    id=result['id'],
                    name=metadata.get('name', 'Unknown'),
                    current_title=metadata.get('title', ''),
                    skills=skills,
                    experience_years=metadata.get('experience_years', 0),
                    location=metadata.get('location', ''),
                    profile_url=metadata.get('profile_url', ''),
                    source_portal=metadata.get('source', 'unknown'),
                    email=metadata.get('email'),
                    phone=metadata.get('phone'),
                    summary=metadata.get('summary')
                )
                vector_candidates.append(candidate)
            except Exception as e:
                logger.warning(f"Error converting vector DB result: {e}")
                continue
        
        logger.info(f"Found {len(vector_candidates)} candidates from Vector DB search")
        
        # Combine scraped candidates with vector DB candidates (remove duplicates)
        all_candidates = raw_candidates.copy()
        existing_ids = {c.id for c in raw_candidates}
        for vc in vector_candidates:
            if vc.id not in existing_ids:
                all_candidates.append(vc)
                existing_ids.add(vc.id)
        
        logger.info(f"Total candidates for matching: {len(all_candidates)} (scraped + vector DB)")
        
        # PHASE 3: Hard match on skills and experience (VERY LENIENT)
        logger.info(f"Phase 3: Hard matching on skills and experience...")
        matched = hard_matcher.match_candidates(
            job.description, 
            all_candidates,
            min_skill_match=0.1,  # At least 10% skills must match (very lenient)
            min_experience_match=0.1  # At least 10% experience requirement (very lenient)
        )
        logger.info(f"Matched {len(matched)} candidates")
        
        if not matched:
            logger.warning("No candidates matched the requirements")
            job.candidates = []
            job.status = JobStatus.COMPLETED
            nosql_db.save_job(job)
            return
        
        # PHASE 4: Balance results across sources (show ALL matched candidates)
        logger.info(f"Phase 4: Balancing results across sources...")
        balanced = hard_matcher.balance_by_source(
            matched,
            max_results=len(matched),  # Show ALL candidates who passed
            sources=['naukri', 'linkedin', 'stackoverflow', 'github']
        )
        logger.info(f"Selected {len(balanced)} balanced candidates (showing all who passed criteria)")
        
        # Convert to RankedCandidate format and mark top 3
        ranked_candidates = []
        for i, match in enumerate(balanced):
            candidate = match['candidate']
            is_top_3 = i < 3  # Mark top 3 candidates
            
            ranked_candidates.append(RankedCandidate(
                candidate=candidate,
                match_score=match['combined_score'],
                match_breakdown={
                    'skill_match': match['skill_score'],
                    'experience_match': match['experience_score'],
                    'matched_skills': match['matched_skills'],
                    'missing_skills': match['missing_skills'],
                    'experience_gap': match['experience_gap'],
                    'is_top_3': is_top_3,  # Flag for UI highlighting
                    'rank': i + 1  # Add rank number
                },
                reasoning=f"{'🏆 TOP MATCH - ' if is_top_3 else ''}Skills: {len(match['matched_skills'])}/{len(job.description.required_skills)} matched, Experience: {match['experience_score']*100:.0f}% match"
            ))
        
        # Update job with final results
        job.candidates = ranked_candidates
        job.status = JobStatus.COMPLETED
        logger.info(f"Job {job_id} completed with {len(ranked_candidates)} candidates")
        
        # Save to NoSQL database
        nosql_db.save_job(job)
        logger.info(f"💾 Saved job {job_id} to NoSQL database")
        
    except Exception as e:
        logger.error(f"Error processing job {job_id}: {e}", exc_info=True)
        jobs_db[job_id].status = JobStatus.FAILED
        nosql_db.save_job(jobs_db[job_id])

@app.get("/jobs/{job_id}", response_model=Job)
async def get_job(job_id: str):
    """Get job status and results (polled by frontend)"""
    if job_id not in jobs_db:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Track polling count
    if job_id not in job_poll_count:
        job_poll_count[job_id] = 0
    job_poll_count[job_id] += 1
    
    # Log only every 10th poll to reduce noise
    if job_poll_count[job_id] % 10 == 0:
        logger.info(f"📊 Job {job_id[:8]}... polled {job_poll_count[job_id]} times (status: {jobs_db[job_id].status})")
    
    return jobs_db[job_id]

@app.get("/jobs/{job_id}/candidates", response_model=List[RankedCandidate])
async def get_candidates(job_id: str):
    """Get ranked candidates for a job"""
    if job_id not in jobs_db:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs_db[job_id]
    if job.status != JobStatus.COMPLETED:
        raise HTTPException(status_code=400, detail=f"Job status: {job.status}")
    
    return job.candidates

# Mount static files and serve index.html
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def serve_ui():
    """Serve the UI"""
    return FileResponse("static/index.html")


