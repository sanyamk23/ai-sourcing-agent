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
from src.database import get_db, JobDB, CandidateDB
from sqlalchemy.orm import Session
import asyncio
import logging
import os
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

# Initialize agent
agent = CandidateSourcingAgent(config)

# In-memory storage for job status (use database for persistence)
jobs_db = {}

# API Routes - specific routes MUST come before parameterized routes
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/api/candidates")
async def get_all_candidates(db: Session = Depends(get_db)):
    """Get all candidates from database"""
    try:
        candidates = db.query(CandidateDB).all()
        return [
            {
                "id": c.id,
                "name": c.name,
                "email": c.email,
                "phone": c.phone,
                "current_title": c.current_title,
                "skills": c.skills,
                "experience_years": c.experience_years,
                "education": c.education,
                "location": c.location,
                "profile_url": c.profile_url,
                "source_portal": c.source_portal,
                "summary": c.summary,
                "created_at": c.created_at,
                "updated_at": c.updated_at
            }
            for c in candidates
        ]
    except Exception as e:
        logger.error(f"Error fetching candidates: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/jobs/all")
async def get_all_jobs(db: Session = Depends(get_db)):
    """Get all jobs with their candidates from database"""
    try:
        jobs = db.query(JobDB).order_by(JobDB.created_at.desc()).all()
        return [
            {
                "id": j.id,
                "title": j.title,
                "description": j.description,
                "required_skills": j.required_skills,
                "experience_years": j.experience_years,
                "location": j.location,
                "status": j.status,
                "candidates": j.candidates if j.candidates else [],
                "created_at": j.created_at,
                "updated_at": j.updated_at
            }
            for j in jobs
        ]
    except Exception as e:
        logger.error(f"Error fetching jobs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/candidate/{candidate_id}/profile")
async def get_candidate_profile(candidate_id: str, db: Session = Depends(get_db)):
    """Get detailed candidate profile with experience"""
    try:
        candidate = db.query(CandidateDB).filter(CandidateDB.id == candidate_id).first()
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")
        
        # Parse experience from summary or create mock data
        experience_data = parse_experience_from_summary(candidate.summary or "")
        
        return {
            "id": candidate.id,
            "name": candidate.name,
            "email": candidate.email,
            "phone": candidate.phone,
            "current_title": candidate.current_title,
            "skills": candidate.skills,
            "experience_years": candidate.experience_years,
            "education": candidate.education,
            "location": candidate.location,
            "profile_url": candidate.profile_url,
            "source_portal": candidate.source_portal,
            "summary": candidate.summary,
            "experience": experience_data,
            "created_at": candidate.created_at
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
    """Background task to process job - Two phase approach"""
    try:
        job = jobs_db[job_id]
        job.status = JobStatus.PROCESSING
        
        logger.info(f"Starting candidate sourcing for job {job_id}")
        
        # PHASE 1: Scrape candidates from all portals
        logger.info(f"Phase 1: Scraping candidates...")
        raw_candidates = await agent.scraper_manager.scrape_all(job.description)
        logger.info(f"Found {len(raw_candidates)} raw candidates")
        
        if not raw_candidates:
            logger.warning("No candidates found from any portal")
            job.status = JobStatus.FAILED
            return
        
        # Skip enrichment for speed (can be enabled later if needed)
        # Enrichment adds 10-20 seconds but provides minimal value
        logger.info(f"Skipping enrichment for faster processing")
        
        # Convert to RankedCandidate with basic info (for display)
        from src.models import RankedCandidate
        initial_candidates = []
        for candidate in raw_candidates:
            initial_candidates.append(RankedCandidate(
                candidate=candidate,
                match_score=0.5,  # Placeholder
                match_breakdown={},
                reasoning="Candidate found, matching in progress..."
            ))
        
        # Update job with initial candidates (so frontend can show them)
        job.candidates = initial_candidates
        logger.info(f"Phase 1 complete: {len(initial_candidates)} candidates ready for matching")
        
        # Small delay to let frontend detect the candidates
        await asyncio.sleep(1)  # Reduced from 2s to 1s
        
        # PHASE 2: Match and rank candidates
        logger.info(f"Phase 2: Matching and ranking candidates...")
        matched = agent.matcher.match_candidates(job.description, raw_candidates)
        logger.info(f"Matched {len(matched)} candidates above threshold")
        
        if not matched:
            logger.warning("No candidates matched the job requirements")
            # Keep the raw candidates but mark as completed
            job.status = JobStatus.COMPLETED
            return
        
        # Rank candidates
        ranked = agent.ranker.rank_candidates(job.description, matched)
        logger.info(f"Ranked top {len(ranked)} candidates")
        
        # Update with final ranked candidates
        job.candidates = ranked
        job.status = JobStatus.COMPLETED
        logger.info(f"Job {job_id} completed with {len(ranked)} candidates")
        
        # Save to database
        from src.database import SessionLocal
        db = SessionLocal()
        try:
            job_db = JobDB(
                id=job_id,
                title=job.description.title,
                description=job.description.description,
                required_skills=job.description.required_skills,
                experience_years=job.description.experience_years,
                location=job.description.location,
                status=job.status.value,
                candidates=[c.dict() for c in ranked]
            )
            db.merge(job_db)
            
            # Save candidates
            for ranked_candidate in ranked:
                candidate = ranked_candidate.candidate
                candidate_db = CandidateDB(
                    id=candidate.id,
                    name=candidate.name,
                    email=candidate.email,
                    phone=candidate.phone,
                    current_title=candidate.current_title,
                    skills=candidate.skills,
                    experience_years=candidate.experience_years,
                    education=candidate.education,
                    location=candidate.location,
                    profile_url=candidate.profile_url,
                    source_portal=candidate.source_portal,
                    summary=candidate.summary
                )
                db.merge(candidate_db)
            
            db.commit()
            logger.info(f"Saved job {job_id} to database")
        finally:
            db.close()
        
    except Exception as e:
        logger.error(f"Error processing job {job_id}: {e}", exc_info=True)
        jobs_db[job_id].status = JobStatus.FAILED

@app.get("/jobs/{job_id}", response_model=Job)
async def get_job(job_id: str):
    """Get job status and results"""
    if job_id not in jobs_db:
        raise HTTPException(status_code=404, detail="Job not found")
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


