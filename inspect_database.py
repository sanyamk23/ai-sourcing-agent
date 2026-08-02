#!/usr/bin/env python3
"""
Script to inspect the candidate database and show breakdown by source portal
"""
import sqlite3
from collections import Counter
import json

def inspect_sqlite_db():
    """Inspect the SQLite candidates database"""
    print("\n" + "="*80)
    print("SQLITE DATABASE (candidates.db)")
    print("="*80)
    
    try:
        conn = sqlite3.connect('candidates.db')
        cursor = conn.cursor()
        
        # Get all candidates
        cursor.execute("SELECT * FROM candidates")
        candidates = cursor.fetchall()
        
        # Get column names
        cursor.execute("PRAGMA table_info(candidates)")
        columns = [col[1] for col in cursor.fetchall()]
        
        print(f"\n📊 Total candidates in SQLite: {len(candidates)}")
        
        if candidates:
            # Find source_portal column index
            source_idx = columns.index('source_portal') if 'source_portal' in columns else None
            
            if source_idx:
                sources = [c[source_idx] for c in candidates]
                source_counts = Counter(sources)
                
                print("\n📍 Breakdown by source portal:")
                for source, count in source_counts.most_common():
                    print(f"   {source}: {count} candidates")
            
            # Show sample candidates
            print(f"\n📋 Sample candidates (first 5):")
            name_idx = columns.index('name') if 'name' in columns else 0
            title_idx = columns.index('current_title') if 'current_title' in columns else 1
            
            for i, candidate in enumerate(candidates[:5], 1):
                name = candidate[name_idx] if name_idx < len(candidate) else "N/A"
                title = candidate[title_idx] if title_idx < len(candidate) else "N/A"
                source = candidate[source_idx] if source_idx and source_idx < len(candidate) else "N/A"
                print(f"   {i}. {name} - {title} (from {source})")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error reading SQLite database: {e}")

def inspect_vector_db():
    """Inspect the ChromaDB vector database"""
    print("\n" + "="*80)
    print("VECTOR DATABASE (chroma_db)")
    print("="*80)
    
    try:
        from src.vector_db import CandidateVectorDB
        
        vector_db = CandidateVectorDB()
        
        # Get all candidates
        results = vector_db.collection.get()
        
        total = len(results['ids'])
        print(f"\n📊 Total candidates in Vector DB: {total}")
        
        if total > 0:
            # Extract source portals from metadata
            metadatas = results['metadatas']
            sources = [m.get('source_portal', 'unknown') for m in metadatas]
            source_counts = Counter(sources)
            
            print("\n📍 Breakdown by source portal:")
            for source, count in source_counts.most_common():
                print(f"   {source}: {count} candidates")
            
            # Show sample candidates
            print(f"\n📋 Sample candidates (first 5):")
            for i in range(min(5, total)):
                name = metadatas[i].get('name', 'N/A')
                title = metadatas[i].get('current_title', 'N/A')
                source = metadatas[i].get('source_portal', 'N/A')
                print(f"   {i+1}. {name} - {title} (from {source})")
        
    except Exception as e:
        print(f"❌ Error reading Vector database: {e}")
        import traceback
        traceback.print_exc()

def inspect_jobs():
    """Inspect the jobs in the database"""
    print("\n" + "="*80)
    print("JOBS DATABASE")
    print("="*80)
    
    try:
        conn = sqlite3.connect('candidates.db')
        cursor = conn.cursor()
        
        # Check if jobs table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='jobs'")
        if not cursor.fetchone():
            print("\n⚠️  No jobs table found")
            conn.close()
            return
        
        # Get all jobs
        cursor.execute("SELECT * FROM jobs")
        jobs = cursor.fetchall()
        
        # Get column names
        cursor.execute("PRAGMA table_info(jobs)")
        columns = [col[1] for col in cursor.fetchall()]
        
        print(f"\n📊 Total jobs: {len(jobs)}")
        
        if jobs:
            print(f"\n📋 Jobs:")
            id_idx = columns.index('id') if 'id' in columns else 0
            title_idx = columns.index('title') if 'title' in columns else 1
            status_idx = columns.index('status') if 'status' in columns else 2
            
            for i, job in enumerate(jobs, 1):
                job_id = job[id_idx] if id_idx < len(job) else "N/A"
                title = job[title_idx] if title_idx < len(job) else "N/A"
                status = job[status_idx] if status_idx < len(job) else "N/A"
                print(f"   {i}. {title} (ID: {job_id[:8]}..., Status: {status})")
                
                # Get candidates for this job
                cursor.execute("SELECT COUNT(*) FROM job_candidates WHERE job_id = ?", (job_id,))
                count = cursor.fetchone()[0]
                print(f"      → {count} candidates matched")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error reading jobs: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("\n🔍 INSPECTING AI SOURCING AGENT DATABASES")
    print("="*80)
    
    inspect_sqlite_db()
    inspect_vector_db()
    inspect_jobs()
    
    print("\n" + "="*80)
    print("✅ Inspection complete!")
    print("="*80 + "\n")
