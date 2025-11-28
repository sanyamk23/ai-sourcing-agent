#!/usr/bin/env python3
"""
Clear database data
"""
import os
import shutil

def clear_jobs():
    """Clear all jobs from NoSQL database"""
    jobs_dir = "./data/jobs"
    if os.path.exists(jobs_dir):
        count = len([f for f in os.listdir(jobs_dir) if f.endswith('.json')])
        for file in os.listdir(jobs_dir):
            if file.endswith('.json'):
                os.remove(os.path.join(jobs_dir, file))
        print(f"✅ Deleted {count} jobs from NoSQL database")
    else:
        print("⚠️  Jobs directory doesn't exist")

def clear_vector_db():
    """Clear all candidates from Vector database"""
    try:
        from src.vector_db import CandidateVectorDB
        vector_db = CandidateVectorDB()
        stats = vector_db.get_stats()
        count = stats['total_candidates']
        vector_db.clear_all()
        print(f"✅ Deleted {count} candidates from Vector database")
    except Exception as e:
        print(f"❌ Error clearing Vector DB: {e}")

def clear_old_sqlite():
    """Clear old SQLite database (if exists)"""
    if os.path.exists("candidates.db"):
        os.remove("candidates.db")
        print("✅ Deleted old SQLite database")
    else:
        print("ℹ️  No SQLite database found (already using NoSQL)")

def main():
    print("\n" + "="*60)
    print("DATABASE CLEANUP TOOL")
    print("="*60)
    
    print("\nWhat would you like to clear?")
    print("1. Jobs only (NoSQL)")
    print("2. Vector DB only (all scraped candidates)")
    print("3. Both (complete reset)")
    print("4. Old SQLite database")
    print("5. Everything (nuclear option)")
    
    choice = input("\nEnter choice (1-5): ").strip()
    
    if choice == "1":
        clear_jobs()
    elif choice == "2":
        clear_vector_db()
    elif choice == "3":
        clear_jobs()
        clear_vector_db()
    elif choice == "4":
        clear_old_sqlite()
    elif choice == "5":
        print("\n⚠️  WARNING: This will delete ALL data!")
        confirm = input("Type 'yes' to confirm: ").strip().lower()
        if confirm == "yes":
            clear_jobs()
            clear_vector_db()
            clear_old_sqlite()
            print("\n🧹 Complete cleanup done!")
        else:
            print("❌ Cancelled")
    else:
        print("❌ Invalid choice")
    
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    main()
