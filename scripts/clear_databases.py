"""
Clear all databases - MongoDB and ChromaDB
WARNING: This will delete ALL data!
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.nosql_database import mongo_db
from src.vector_database import vector_db
import shutil
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def clear_mongodb():
    """Clear all MongoDB collections"""
    logger.info("🗑️  Clearing MongoDB...")
    
    try:
        # Drop all collections
        mongo_db.candidates.drop()
        logger.info("✓ Dropped candidates collection")
        
        mongo_db.jobs.drop()
        logger.info("✓ Dropped jobs collection")
        
        mongo_db.scraped_candidates.drop()
        logger.info("✓ Dropped scraped_candidates collection")
        
        logger.info("✅ MongoDB cleared successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Error clearing MongoDB: {e}")
        return False


def clear_chromadb():
    """Clear ChromaDB by deleting the directory"""
    logger.info("🗑️  Clearing ChromaDB...")
    
    try:
        chroma_dir = "./chroma_db"
        
        if os.path.exists(chroma_dir):
            shutil.rmtree(chroma_dir)
            logger.info(f"✓ Deleted {chroma_dir}")
            logger.info("✅ ChromaDB cleared successfully")
        else:
            logger.info("ℹ️  ChromaDB directory doesn't exist")
        
        return True
    except Exception as e:
        logger.error(f"❌ Error clearing ChromaDB: {e}")
        return False


def clear_sqlite():
    """Clear SQLite database (if you want to clear old data too)"""
    logger.info("🗑️  Clearing SQLite...")
    
    try:
        sqlite_file = "./candidates.db"
        
        if os.path.exists(sqlite_file):
            os.remove(sqlite_file)
            logger.info(f"✓ Deleted {sqlite_file}")
            logger.info("✅ SQLite cleared successfully")
        else:
            logger.info("ℹ️  SQLite database doesn't exist")
        
        return True
    except Exception as e:
        logger.error(f"❌ Error clearing SQLite: {e}")
        return False


def main():
    print("\n" + "="*60)
    print("  ⚠️  DATABASE CLEANUP TOOL")
    print("="*60)
    print("\nThis will DELETE ALL data from:")
    print("  • MongoDB (candidates, jobs, scraped_candidates)")
    print("  • ChromaDB (all vector embeddings)")
    print("  • SQLite (old database)")
    print("\n⚠️  THIS CANNOT BE UNDONE!")
    print("="*60)
    
    confirm = input("\nType 'DELETE ALL' to confirm: ").strip()
    
    if confirm != "DELETE ALL":
        print("\n❌ Cancelled. No data was deleted.")
        return
    
    print("\n" + "="*60)
    print("  Starting cleanup...")
    print("="*60 + "\n")
    
    # Clear MongoDB
    mongo_success = clear_mongodb()
    print()
    
    # Clear ChromaDB
    chroma_success = clear_chromadb()
    print()
    
    # Ask about SQLite
    clear_old = input("Also clear old SQLite database? (y/n): ").strip().lower()
    if clear_old == 'y':
        sqlite_success = clear_sqlite()
    else:
        sqlite_success = True
        logger.info("ℹ️  Skipped SQLite cleanup")
    
    print("\n" + "="*60)
    print("  Cleanup Summary")
    print("="*60)
    print(f"MongoDB:  {'✅ Cleared' if mongo_success else '❌ Failed'}")
    print(f"ChromaDB: {'✅ Cleared' if chroma_success else '❌ Failed'}")
    print(f"SQLite:   {'✅ Cleared' if clear_old == 'y' and sqlite_success else '⏭️  Skipped'}")
    print("="*60)
    
    if mongo_success and chroma_success:
        print("\n✅ All databases cleared successfully!")
        print("\nNext steps:")
        print("1. Restart your server: python run_api.py")
        print("2. Create new jobs - fresh start!")
    else:
        print("\n⚠️  Some operations failed. Check logs above.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
