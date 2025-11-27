"""
Migration script: SQLite -> MongoDB + ChromaDB
Migrates existing candidates and jobs to NoSQL databases
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database import SessionLocal, CandidateDB, JobDB
from src.nosql_database import mongo_db
from src.vector_database import vector_db
import json
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def migrate_candidates():
    """Migrate candidates from SQLite to MongoDB and ChromaDB"""
    db = SessionLocal()
    
    try:
        candidates = db.query(CandidateDB).all()
        logger.info(f"Found {len(candidates)} candidates to migrate")
        
        migrated_count = 0
        vector_count = 0
        
        for candidate in candidates:
            # Prepare candidate data
            candidate_data = {
                'id': candidate.id,
                'name': candidate.name,
                'email': candidate.email,
                'phone': candidate.phone,
                'current_title': candidate.current_title,
                'skills': candidate.skills if isinstance(candidate.skills, list) else 
                         (json.loads(candidate.skills) if candidate.skills else []),
                'experience_years': candidate.experience_years,
                'education': candidate.education,
                'location': candidate.location,
                'profile_url': candidate.profile_url,
                'source_portal': candidate.source_portal,
                'summary': candidate.summary,
                'created_at': candidate.created_at or datetime.now(),
                'updated_at': candidate.updated_at or datetime.now()
            }
            
            # Insert to MongoDB
            mongo_db.insert_candidate(candidate_data)
            migrated_count += 1
            
            # Add to vector database (as final candidates)
            try:
                vector_db.add_candidate(candidate_data, is_final=True)
                vector_count += 1
                logger.info(f"Migrated: {candidate.name} (with embedding)")
            except Exception as e:
                logger.error(f"Error creating embedding for {candidate.name}: {e}")
                logger.info(f"Migrated: {candidate.name} (MongoDB only)")
        
        logger.info(f"✅ Successfully migrated {migrated_count} candidates to MongoDB")
        logger.info(f"✅ Successfully added {vector_count} candidates to ChromaDB")
        
    except Exception as e:
        logger.error(f"Error migrating candidates: {e}", exc_info=True)
    finally:
        db.close()


def migrate_jobs():
    """Migrate jobs from SQLite to MongoDB"""
    db = SessionLocal()
    
    try:
        jobs = db.query(JobDB).all()
        logger.info(f"Found {len(jobs)} jobs to migrate")
        
        migrated_count = 0
        
        for job in jobs:
            # Prepare job data
            job_data = {
                'id': job.id,
                'title': job.title,
                'description': job.description,
                'required_skills': job.required_skills if isinstance(job.required_skills, list) else
                                 (json.loads(job.required_skills) if job.required_skills else []),
                'experience_years': job.experience_years,
                'location': job.location,
                'status': job.status,
                'candidates': job.candidates if isinstance(job.candidates, list) else
                            (json.loads(job.candidates) if job.candidates else []),
                'created_at': job.created_at or datetime.now(),
                'updated_at': job.updated_at or datetime.now()
            }
            
            # Insert to MongoDB
            mongo_db.insert_job(job_data)
            migrated_count += 1
            
            logger.info(f"Migrated job: {job.title}")
        
        logger.info(f"✅ Successfully migrated {migrated_count} jobs to MongoDB")
        
    except Exception as e:
        logger.error(f"Error migrating jobs: {e}", exc_info=True)
    finally:
        db.close()


def verify_migration():
    """Verify migration was successful"""
    logger.info("\n=== Verification ===")
    
    # Check MongoDB
    candidates = mongo_db.get_all_candidates()
    jobs = mongo_db.get_all_jobs()
    
    logger.info(f"MongoDB - Candidates: {len(candidates)}")
    logger.info(f"MongoDB - Jobs: {len(jobs)}")
    
    # Check ChromaDB
    final_count = vector_db.get_collection_count(is_final=True)
    scraped_count = vector_db.get_collection_count(is_final=False)
    
    logger.info(f"ChromaDB - Final candidates: {final_count}")
    logger.info(f"ChromaDB - Scraped candidates: {scraped_count}")
    
    # Test semantic search
    if final_count > 0:
        logger.info("\nTesting semantic search...")
        results = vector_db.semantic_search("Python developer", n_results=3)
        logger.info(f"Found {len(results)} results for 'Python developer'")
        for i, result in enumerate(results[:3], 1):
            logger.info(f"  {i}. {result['metadata'].get('name')} - {result['metadata'].get('title')}")


if __name__ == "__main__":
    logger.info("🚀 Starting migration from SQLite to MongoDB + ChromaDB")
    logger.info("=" * 60)
    
    # Migrate candidates
    logger.info("\n📋 Migrating candidates...")
    migrate_candidates()
    
    # Migrate jobs
    logger.info("\n💼 Migrating jobs...")
    migrate_jobs()
    
    # Verify
    logger.info("\n🔍 Verifying migration...")
    verify_migration()
    
    logger.info("\n✅ Migration complete!")
    logger.info("\nNext steps:")
    logger.info("1. Update your .env file with MONGODB_URI if using remote MongoDB")
    logger.info("2. Restart your API server")
    logger.info("3. The system will now use MongoDB + ChromaDB for all operations")
