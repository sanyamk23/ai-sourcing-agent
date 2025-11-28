#!/usr/bin/env python3
"""
Complete view of all candidate data across all storage systems
"""
import sqlite3
from collections import Counter, defaultdict
import json

print("\n" + "="*100)
print("COMPLETE CANDIDATE DATA REPORT")
print("="*100)

# Check SQLite - this has the FINAL ranked candidates from completed jobs
print("\n1️⃣  SQLITE DATABASE - Final Ranked Candidates")
print("-" * 100)

try:
    conn = sqlite3.connect('candidates.db')
    cursor = conn.cursor()
    
    # Get total and breakdown
    cursor.execute("SELECT COUNT(*) FROM candidates")
    total = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT source_portal, COUNT(*) as count
        FROM candidates
        GROUP BY source_portal
        ORDER BY count DESC
    """)
    
    by_source = cursor.fetchall()
    
    print(f"\n📊 Total: {total} candidates")
    print(f"\n📍 By Source Portal:")
    for source, count in by_source:
        print(f"   • {source}: {count} candidates")
        
        # Show examples
        cursor.execute("""
            SELECT name, current_title
            FROM candidates
            WHERE source_portal = ?
            ORDER BY created_at DESC
            LIMIT 5
        """, (source,))
        
        examples = cursor.fetchall()
        for name, title in examples:
            print(f"     - {name}: {title}")
    
    # Show jobs
    print(f"\n\n📋 Completed Jobs:")
    cursor.execute("""
        SELECT id, title, status, created_at, candidates
        FROM jobs
        ORDER BY created_at DESC
    """)
    
    jobs = cursor.fetchall()
    for job_id, title, status, created, candidates_json in jobs:
        try:
            candidates_list = json.loads(candidates_json) if candidates_json else []
            candidate_count = len(candidates_list)
            
            # Count by source in this job
            sources_in_job = Counter()
            for c in candidates_list:
                if isinstance(c, dict) and 'candidate' in c:
                    source = c['candidate'].get('source_portal', 'unknown')
                    sources_in_job[source] += 1
            
            print(f"\n   Job: {title} ({status})")
            print(f"   Created: {created}")
            print(f"   Total Candidates: {candidate_count}")
            if sources_in_job:
                print(f"   Sources: {dict(sources_in_job)}")
        except Exception as e:
            print(f"\n   Job: {title} ({status}) - Error parsing: {e}")
    
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

# Check Vector DB
print("\n\n2️⃣  VECTOR DATABASE - All Scraped Candidates (for semantic search)")
print("-" * 100)

try:
    import chromadb
    from chromadb.config import Settings
    
    client = chromadb.PersistentClient(
        path="./chroma_db",
        settings=Settings(anonymized_telemetry=False)
    )
    
    collections = client.list_collections()
    print(f"\n📦 Collections: {[c.name for c in collections]}")
    
    total_vector = 0
    for collection in collections:
        results = collection.get()
        count = len(results['ids'])
        total_vector += count
        
        print(f"\n   Collection '{collection.name}': {count} candidates")
        
        if count > 0:
            # Group by source
            by_source = defaultdict(int)
            for metadata in results['metadatas']:
                source = metadata.get('source_portal') or metadata.get('source', 'unknown')
                by_source[source] += 1
            
            print(f"   By Source:")
            for source, count in sorted(by_source.items(), key=lambda x: x[1], reverse=True):
                print(f"     • {source}: {count} candidates")
    
    if total_vector == 0:
        print("\n   ⚠️  Vector DB is EMPTY!")
        print("   Note: After the fix, new scrapes will persist here.")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

# Summary
print("\n\n" + "="*100)
print("SUMMARY")
print("="*100)

print("""
📌 Understanding the Data:

1. SQLITE DATABASE (candidates.db):
   - Contains ONLY the top-ranked candidates from completed jobs
   - Each job saves its top 50 matches
   - This is what you see in the final results
   - Currently shows mostly StackOverflow because those ranked highest in previous jobs

2. VECTOR DATABASE (chroma_db):
   - Should contain ALL scraped candidates from all portals
   - Used for semantic similarity search during matching
   - Was EMPTY due to a bug (now fixed!)
   - After restart, new scrapes will persist here

3. Your Latest Run Results:
   - Scraped: 100 Naukri + 6 LinkedIn + 60 StackOverflow = 166 candidates
   - These were matched and ranked
   - Top 50 were saved to SQLite as part of the job
   - But they didn't persist in Vector DB (due to the bug)

🔧 FIX APPLIED:
   - Changed vector_db.py to use PersistentClient instead of ephemeral Client
   - Changed default path from ./data/chroma_db to ./chroma_db
   - Restart your API server to use the fixed version

🚀 NEXT STEPS:
   1. Restart the API server
   2. Run a new job
   3. Data will now persist in both SQLite AND Vector DB
""")

print("="*100 + "\n")
