"""
NoSQL Database using MongoDB for candidate and job storage
"""
from pymongo import MongoClient
from datetime import datetime
from typing import List, Dict, Optional
import os
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)


class MongoDBManager:
    """MongoDB manager for candidates and jobs"""
    
    def __init__(self):
        # Use MongoDB connection string from env or default to local
        mongo_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
        self.client = MongoClient(mongo_uri)
        self.db = self.client['candidate_sourcing']
        
        # Collections
        self.candidates = self.db['candidates']
        self.jobs = self.db['jobs']
        self.scraped_candidates = self.db['scraped_candidates']  # All scraped data
        
        # Create indexes
        self._create_indexes()
        
        logger.info("MongoDB connection established")
    
    def _create_indexes(self):
        """Create indexes for better query performance"""
        # Candidates indexes
        self.candidates.create_index("id", unique=True)
        self.candidates.create_index("email")
        self.candidates.create_index("source_portal")
        self.candidates.create_index("created_at")
        
        # Jobs indexes
        self.jobs.create_index("id", unique=True)
        self.jobs.create_index("status")
        self.jobs.create_index("created_at")
        
        # Scraped candidates indexes
        self.scraped_candidates.create_index("profile_url", unique=True)
        self.scraped_candidates.create_index("source_portal")
        self.scraped_candidates.create_index("scraped_at")
    
    # Candidate operations
    def insert_candidate(self, candidate_data: Dict) -> str:
        """Insert a new candidate"""
        candidate_data['created_at'] = datetime.now()
        candidate_data['updated_at'] = datetime.now()
        
        result = self.candidates.update_one(
            {'id': candidate_data['id']},
            {'$set': candidate_data},
            upsert=True
        )
        
        return candidate_data['id']
    
    def get_candidate(self, candidate_id: str) -> Optional[Dict]:
        """Get candidate by ID"""
        return self.candidates.find_one({'id': candidate_id}, {'_id': 0})
    
    def get_all_candidates(self) -> List[Dict]:
        """Get all candidates"""
        return list(self.candidates.find({}, {'_id': 0}).sort('created_at', -1))
    
    def update_candidate(self, candidate_id: str, update_data: Dict) -> bool:
        """Update candidate"""
        update_data['updated_at'] = datetime.now()
        result = self.candidates.update_one(
            {'id': candidate_id},
            {'$set': update_data}
        )
        return result.modified_count > 0
    
    # Job operations
    def insert_job(self, job_data: Dict) -> str:
        """Insert a new job"""
        job_data['created_at'] = datetime.now()
        job_data['updated_at'] = datetime.now()
        
        result = self.jobs.update_one(
            {'id': job_data['id']},
            {'$set': job_data},
            upsert=True
        )
        
        return job_data['id']
    
    def get_job(self, job_id: str) -> Optional[Dict]:
        """Get job by ID"""
        return self.jobs.find_one({'id': job_id}, {'_id': 0})
    
    def get_all_jobs(self) -> List[Dict]:
        """Get all jobs"""
        return list(self.jobs.find({}, {'_id': 0}).sort('created_at', -1))
    
    def update_job(self, job_id: str, update_data: Dict) -> bool:
        """Update job"""
        update_data['updated_at'] = datetime.now()
        result = self.jobs.update_one(
            {'id': job_id},
            {'$set': update_data}
        )
        return result.modified_count > 0
    
    # Scraped candidates (all data before filtering)
    def insert_scraped_candidate(self, candidate_data: Dict) -> str:
        """Insert scraped candidate (before filtering)"""
        candidate_data['scraped_at'] = datetime.now()
        
        result = self.scraped_candidates.update_one(
            {'profile_url': candidate_data.get('profile_url')},
            {'$set': candidate_data},
            upsert=True
        )
        
        return str(result.upserted_id) if result.upserted_id else candidate_data.get('profile_url')
    
    def get_scraped_candidates(self, source_portal: Optional[str] = None) -> List[Dict]:
        """Get all scraped candidates"""
        query = {'source_portal': source_portal} if source_portal else {}
        return list(self.scraped_candidates.find(query, {'_id': 0}).sort('scraped_at', -1))
    
    def search_candidates(self, query: Dict) -> List[Dict]:
        """Search candidates with filters"""
        return list(self.candidates.find(query, {'_id': 0}))
    
    def close(self):
        """Close MongoDB connection"""
        self.client.close()


# Global instance
mongo_db = MongoDBManager()
