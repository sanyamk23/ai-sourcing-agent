from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import yaml
import uuid
from datetime import datetime
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models import JobDescription, Job, JobStatus, RankedCandidate
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
    """Background task to process job"""
    try:
        job = jobs_db[job_id]
        job.status = JobStatus.PROCESSING
        
        logger.info(f"Starting candidate sourcing for job {job_id}")
        
        # Source candidates
        candidates = await agent.source_candidates(job.description)
        
        job.candidates = candidates
        job.status = JobStatus.COMPLETED
        logger.info(f"Job {job_id} completed with {len(candidates)} candidates")
        
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
                candidates=[c.dict() for c in candidates]
            )
            db.merge(job_db)
            
            # Save candidates
            for ranked_candidate in candidates:
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

@app.get("/health")
async def health_check():
    return {"status": "healthy"}


