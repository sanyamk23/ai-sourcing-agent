"""
NoSQL Database for Job Storage
Uses JSON files for simple, portable storage
"""
import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from src.models import Job, JobStatus, RankedCandidate
import logging

logger = logging.getLogger(__name__)

class NoSQLJobDB:
    """Simple JSON-based NoSQL database for jobs"""
    
    def __init__(self, data_dir: str = "./data/jobs"):
        """Initialize NoSQL database"""
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        logger.info(f"✅ NoSQL Job DB initialized at {data_dir}")
    
    def _get_job_path(self, job_id: str) -> str:
        """Get file path for a job"""
        return os.path.join(self.data_dir, f"{job_id}.json")
    
    def save_job(self, job: Job) -> bool:
        """Save job to JSON file"""
        try:
            job_data = job.dict()
            # Convert datetime to string
            if isinstance(job_data.get('created_at'), datetime):
                job_data['created_at'] = job_data['created_at'].isoformat()
            if isinstance(job_data.get('updated_at'), datetime):
                job_data['updated_at'] = job_data['updated_at'].isoformat()
            
            with open(self._get_job_path(job.id), 'w') as f:
                json.dump(job_data, f, indent=2)
            
            logger.info(f"💾 Saved job {job.id} to NoSQL DB")
            return True
        except Exception as e:
            logger.error(f"Error saving job {job.id}: {e}")
            return False
    
    def get_job(self, job_id: str) -> Optional[Job]:
        """Get job by ID"""
        try:
            job_path = self._get_job_path(job_id)
            if not os.path.exists(job_path):
                return None
            
            with open(job_path, 'r') as f:
                job_data = json.load(f)
            
            return Job(**job_data)
        except Exception as e:
            logger.error(f"Error loading job {job_id}: {e}")
            return None
    
    def get_all_jobs(self) -> List[Job]:
        """Get all jobs"""
        jobs = []
        try:
            for filename in os.listdir(self.data_dir):
                if filename.endswith('.json'):
                    job_id = filename[:-5]  # Remove .json
                    job = self.get_job(job_id)
                    if job:
                        jobs.append(job)
            
            # Sort by created_at descending
            jobs.sort(key=lambda x: x.created_at, reverse=True)
        except Exception as e:
            logger.error(f"Error loading jobs: {e}")
        
        return jobs
    
    def delete_job(self, job_id: str) -> bool:
        """Delete job"""
        try:
            job_path = self._get_job_path(job_id)
            if os.path.exists(job_path):
                os.remove(job_path)
                logger.info(f"🗑️  Deleted job {job_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting job {job_id}: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            jobs = self.get_all_jobs()
            
            stats = {
                "total_jobs": len(jobs),
                "by_status": {},
                "total_candidates": 0
            }
            
            for job in jobs:
                status = job.status.value if hasattr(job.status, 'value') else str(job.status)
                stats["by_status"][status] = stats["by_status"].get(status, 0) + 1
                stats["total_candidates"] += len(job.candidates)
            
            return stats
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {"total_jobs": 0, "by_status": {}, "total_candidates": 0}
