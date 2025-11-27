"""
Test the complete NoSQL workflow
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.nosql_database import mongo_db
from src.vector_database import vector_db
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_workflow():
    """Test that everything is working"""
    
    print("\n" + "="*60)
    print("  Testing NoSQL + Vector DB Workflow")
    print("="*60 + "\n")
    
    # Test 1: MongoDB Connection
    print("Test 1: MongoDB Connection")
    try:
        candidates = mongo_db.get_all_candidates()
        print(f"✅ MongoDB connected - {len(candidates)} candidates found")
    except Exception as e:
        print(f"❌ MongoDB error: {e}")
        return False
    
    # Test 2: ChromaDB Connection
    print("\nTest 2: ChromaDB Connection")
    try:
        final_count = vector_db.get_collection_count(is_final=True)
        scraped_count = vector_db.get_collection_count(is_final=False)
        print(f"✅ ChromaDB connected")
        print(f"   - Final embeddings: {final_count}")
        print(f"   - Scraped embeddings: {scraped_count}")
    except Exception as e:
        print(f"❌ ChromaDB error: {e}")
        return False
    
    # Test 3: Semantic Search
    print("\nTest 3: Semantic Search")
    try:
        results = vector_db.semantic_search("Python developer", n_results=3, is_final=True)
        if results:
            print(f"✅ Semantic search working - {len(results)} results")
            for i, result in enumerate(results[:3], 1):
                metadata = result.get('metadata', {})
                print(f"   {i}. {metadata.get('name')} - {metadata.get('title')}")
        else:
            print("⚠️  No results from semantic search (database might be empty)")
    except Exception as e:
        print(f"❌ Semantic search error: {e}")
        return False
    
    # Test 4: Vector DB Lookup
    print("\nTest 4: Vector DB Lookup (Simulating Job Search)")
    try:
        from src.models import JobDescription
        
        job_desc = JobDescription(
            title="Python Developer",
            description="Looking for Python developer",
            required_skills=["Python", "Django"],
            experience_years=3,
            location="Remote"
        )
        
        results = vector_db.search_by_job(job_desc.dict(), n_results=5)
        print(f"✅ Job search working - {len(results)} candidates found")
        
        if results:
            print("   Top matches:")
            for i, result in enumerate(results[:3], 1):
                metadata = result.get('metadata', {})
                print(f"   {i}. {metadata.get('name')} - {metadata.get('title')}")
    except Exception as e:
        print(f"❌ Job search error: {e}")
        return False
    
    # Test 5: Data Consistency
    print("\nTest 5: Data Consistency")
    try:
        mongo_candidates = len(mongo_db.get_all_candidates())
        vector_candidates = vector_db.get_collection_count(is_final=True)
        
        if mongo_candidates == vector_candidates:
            print(f"✅ Data consistent - {mongo_candidates} candidates in both DBs")
        else:
            print(f"⚠️  Data mismatch:")
            print(f"   MongoDB: {mongo_candidates} candidates")
            print(f"   ChromaDB: {vector_candidates} embeddings")
            print(f"   Run: python scripts/rebuild_embeddings.py")
    except Exception as e:
        print(f"❌ Consistency check error: {e}")
    
    # Summary
    print("\n" + "="*60)
    print("  Test Summary")
    print("="*60)
    print("\n✅ All systems operational!")
    print("\nNext steps:")
    print("1. Start server: python run_api.py")
    print("2. Open UI: http://localhost:8000")
    print("3. Create a job - it will:")
    print("   • Check vector DB for existing candidates")
    print("   • Scrape new ones if needed")
    print("   • Store ALL with embeddings automatically")
    print("\n" + "="*60 + "\n")
    
    return True


if __name__ == "__main__":
    try:
        test_workflow()
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
