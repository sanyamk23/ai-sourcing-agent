"""
Rebuild ChromaDB embeddings from existing MongoDB data
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.nosql_database import mongo_db
from src.vector_database import vector_db
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def rebuild_candidate_embeddings():
    """Rebuild embeddings for all candidates"""
    logger.info("🔄 Rebuilding candidate embeddings...")
    
    candidates = mongo_db.get_all_candidates()
    logger.info(f"Found {len(candidates)} candidates in MongoDB")
    
    if not candidates:
        logger.warning("No candidates found to process")
        return
    
    success_count = 0
    error_count = 0
    
    for candidate in candidates:
        try:
            # Add to vector database
            vector_db.add_candidate(candidate, is_final=True)
            success_count += 1
            logger.info(f"✓ Created embedding for: {candidate.get('name', 'Unknown')}")
        except Exception as e:
            error_count += 1
            logger.error(f"✗ Error creating embedding for {candidate.get('name', 'Unknown')}: {e}")
    
    logger.info(f"\n✅ Successfully created {success_count} embeddings")
    if error_count > 0:
        logger.warning(f"⚠️  Failed to create {error_count} embeddings")
    
    # Verify
    final_count = vector_db.get_collection_count(is_final=True)
    logger.info(f"📊 Total embeddings in ChromaDB: {final_count}")


def rebuild_job_candidate_embeddings():
    """Rebuild embeddings for candidates in jobs"""
    logger.info("\n🔄 Rebuilding embeddings for job candidates...")
    
    jobs = mongo_db.get_all_jobs()
    logger.info(f"Found {len(jobs)} jobs in MongoDB")
    
    all_job_candidates = []
    
    for job in jobs:
        candidates = job.get('candidates', [])
        logger.info(f"Job '{job.get('title')}': {len(candidates)} candidates")
        
        for candidate_data in candidates:
            # Extract candidate from ranked candidate structure
            if isinstance(candidate_data, dict):
                candidate = candidate_data.get('candidate', candidate_data)
                all_job_candidates.append(candidate)
    
    logger.info(f"\nTotal candidates from jobs: {len(all_job_candidates)}")
    
    if not all_job_candidates:
        logger.warning("No job candidates found")
        return
    
    success_count = 0
    error_count = 0
    
    for candidate in all_job_candidates:
        try:
            # Add to scraped collection (these were scraped but may not be final)
            vector_db.add_candidate(candidate, is_final=False)
            success_count += 1
            logger.info(f"✓ Created embedding for: {candidate.get('name', 'Unknown')}")
        except Exception as e:
            error_count += 1
            logger.error(f"✗ Error: {e}")
    
    logger.info(f"\n✅ Successfully created {success_count} embeddings")
    if error_count > 0:
        logger.warning(f"⚠️  Failed to create {error_count} embeddings")
    
    # Verify
    scraped_count = vector_db.get_collection_count(is_final=False)
    logger.info(f"📊 Total scraped embeddings in ChromaDB: {scraped_count}")


def test_embeddings():
    """Test that embeddings work"""
    logger.info("\n🧪 Testing embeddings...")
    
    # Test semantic search
    results = vector_db.semantic_search("Python developer", n_results=3, is_final=True)
    
    if results:
        logger.info(f"✅ Semantic search working! Found {len(results)} results")
        for i, result in enumerate(results, 1):
            metadata = result.get('metadata', {})
            logger.info(f"  {i}. {metadata.get('name')} - {metadata.get('title')}")
    else:
        logger.warning("⚠️  No results from semantic search")


def main():
    logger.info("="*60)
    logger.info("  Rebuilding ChromaDB Embeddings")
    logger.info("="*60)
    
    try:
        # Rebuild final candidate embeddings
        rebuild_candidate_embeddings()
        
        # Rebuild job candidate embeddings (scraped)
        rebuild_job_candidate_embeddings()
        
        # Test
        test_embeddings()
        
        logger.info("\n" + "="*60)
        logger.info("✅ Embedding rebuild complete!")
        logger.info("="*60)
        
        # Show final stats
        final_count = vector_db.get_collection_count(is_final=True)
        scraped_count = vector_db.get_collection_count(is_final=False)
        
        logger.info(f"\nFinal Statistics:")
        logger.info(f"  • Final candidate embeddings: {final_count}")
        logger.info(f"  • Scraped candidate embeddings: {scraped_count}")
        logger.info(f"  • Total embeddings: {final_count + scraped_count}")
        
    except Exception as e:
        logger.error(f"❌ Error during rebuild: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
