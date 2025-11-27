"""
FastAPI server using MongoDB + ChromaDB (NoSQL + Vector DB)
"""
from fastapi import FastAPI, HTTPException
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

from src.models import JobDescription, Job, JobStatus, RankedCandidate
from src.agent_nosql import CandidateSourcingAgentNoSQL
from src.nosql_database import mongo_db
from src.vector_database import vector_db
import asyncio
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Candidate Sourcing API (NoSQL)", version="2.0.0")

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

config['llm']['groq_api_key'] = os.getenv('GROQ_API_KEY')
config['llm']['openai_api_key'] = os.getenv('OPENAI_API_KEY')
config['linkedin']['username'] = os.getenv('LINKEDIN_USERNAME')
config['linkedin']['password'] = os.getenv('LINKEDIN_PASSWORD')

# Initialize enhanced agent with NoSQL support
agent = CandidateSourcingAgentNoSQL(config)

# In-memory storage for job status
jobs_db = {}

# API Routes
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "database": "MongoDB + ChromaDB",
        "candidates_count": len(mongo_db.get_all_candidates()),
        "jobs_count": len(mongo_db.get_all_jobs()),
        "vector_db_count": vector_db.get_collection_count(is_final=True)
    }

@app.get("/api/candidates")
async def get_all_candidates():
    """Get all candidates from MongoDB"""
    try:
        candidates = mongo_db.get_all_candidates()
        return candidates
    except Exception as e:
        logger.error(f"Error fetching candidates: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/jobs/all")
async def get_all_jobs():
    """Get all jobs with their candidates from MongoDB"""
    try:
        jobs = mongo_db.get_all_jobs()
        return jobs
    except Exception as e:
        logger.error(f"Error fetching jobs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

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
    """Background task to process job with vector search"""
    try:
        job = jobs_db[job_id]
        job.status = JobStatus.PROCESSING
        
        logger.info(f"Starting candidate sourcing for job {job_id}")
        
        # Source candidates (agent handles everything automatically)
        # - Checks vector DB for existing candidates
        # - Scrapes new ones if needed
        # - Stores ALL scraped candidates with embeddings
        # - Stores final candidates with embeddings
        candidates = await agent.source_candidates(job.description)
        
        job.candidates = candidates
        job.status = JobStatus.COMPLETED
        logger.info(f"Job {job_id} completed with {len(candidates)} candidates")
        
        # Save job to MongoDB
        job_data = {
            "id": job_id,
            "title": job.description.title,
            "description": job.description.description,
            "required_skills": job.description.required_skills,
            "experience_years": job.description.experience_years,
            "location": job.description.location,
            "status": job.status.value,
            "candidates": [c.dict() for c in candidates]
        }
        mongo_db.insert_job(job_data)
        
        logger.info(f"✅ Job {job_id} saved to MongoDB")
        logger.info(f"✅ All candidates stored with embeddings in ChromaDB")
        
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

@app.get("/api/candidate/{candidate_id}/profile")
async def get_candidate_profile(candidate_id: str):
    """Get detailed candidate profile"""
    try:
        candidate = mongo_db.get_candidate(candidate_id)
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")
        
        # Get experience from summary
        experience_data = parse_experience_from_summary(candidate.get('summary', ''))
        candidate['experience'] = experience_data
        
        return candidate
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching candidate profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/candidate/{candidate_id}/scrape-linkedin")
async def scrape_linkedin_profile(candidate_id: str):
    """Scrape LinkedIn profile and update candidate data"""
    try:
        candidate = mongo_db.get_candidate(candidate_id)
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")
        
        if not candidate.get('profile_url') or 'linkedin.com' not in candidate['profile_url']:
            raise HTTPException(status_code=400, detail="No valid LinkedIn URL")
        
        from src.linkedin_profile_scraper import LinkedInProfileScraper
        
        scraper = LinkedInProfileScraper(config)
        profile_data = scraper.scrape_profile(candidate['profile_url'])
        scraper.close()
        
        if "error" in profile_data:
            raise HTTPException(status_code=500, detail=profile_data["error"])
        
        # Update candidate in MongoDB
        update_data = {}
        if profile_data.get("name"):
            update_data["name"] = profile_data["name"]
        if profile_data.get("headline"):
            update_data["current_title"] = profile_data["headline"]
        if profile_data.get("location"):
            update_data["location"] = profile_data["location"]
        if profile_data.get("about"):
            update_data["summary"] = profile_data["about"]
        if profile_data.get("total_experience_years"):
            update_data["experience_years"] = int(profile_data["total_experience_years"])
        if profile_data.get("skills"):
            update_data["skills"] = profile_data["skills"]
        if profile_data.get("education") and len(profile_data["education"]) > 0:
            edu = profile_data["education"][0]
            update_data["education"] = f"{edu.get('degree', '')} - {edu.get('school', '')}".strip(' -')
        
        mongo_db.update_candidate(candidate_id, update_data)
        
        # Update vector DB
        updated_candidate = mongo_db.get_candidate(candidate_id)
        vector_db.add_candidate(updated_candidate, is_final=True)
        
        logger.info(f"Successfully scraped and updated profile for {updated_candidate['name']}")
        
        return {
            "success": True,
            "message": "Profile scraped and updated successfully",
            "profile_data": profile_data,
            "candidate": updated_candidate
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error scraping LinkedIn profile: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/search/semantic")
async def semantic_search(query: str, n_results: int = 10):
    """Semantic search using vector database"""
    try:
        results = vector_db.semantic_search(query, n_results=n_results, is_final=True)
        return {
            "query": query,
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        logger.error(f"Error in semantic search: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def parse_experience_from_summary(summary: str) -> list:
    """Parse experience from summary"""
    experiences = []
    if not summary:
        return []
    
    lines = summary.split('\n')
    for line in lines:
        line = line.strip()
        if any(keyword in line.lower() for keyword in ['worked at', 'experience at', 'engineer at', 'developer at']):
            experiences.append({
                "title": "Position extracted from summary",
                "company": line,
                "duration": "Duration not specified",
                "description": line
            })
    
    if not experiences:
        experiences = [{
            "title": "Experience details",
            "company": "See full profile for details",
            "duration": "Various",
            "description": summary[:200] + "..." if len(summary) > 200 else summary
        }]
    
    return experiences

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def serve_ui():
    """Serve the UI"""
    return FileResponse("static/index.html")
