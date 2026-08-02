#!/usr/bin/env python3
"""
View all candidates from all sources with detailed breakdown
"""
import sqlite3
from collections import Counter, defaultdict
import chromadb
from chromadb.config import Settings

print("\n" + "="*100)
print(" "*35 + "CANDIDATE DATABASE REPORT")
print("="*100)

# 1. Check Vector DB (this has ALL scraped candidates)
print("\n📦 VECTOR DATABASE (All Scraped Candidates)")
print("-" * 100)

try:
    client = chromadb.PersistentClient(
        path="./chroma_db",
        settings=Settings(anonymized_telemetry=False)
    )
    
    collections = client.list_collections()
    
    all_vector_candidates = []
    for collection in collections:
        results = collection.get()
        total = len(results['ids'])
        
        if total > 0:
            print(f"\n  Collection: '{collection.name}' - {total} candidates")
            
            # Group by source
            by_source = defaultdict(list)
            for i, metadata in enumerate(results['metadatas']):
                source = metadata.get('source_portal', 'unknown')
                name = metadata.get('name', 'Unknown')
                title = metadata.get('current_title', 'N/A')
                by_source[source].append((name, title))
                all_vector_candidates.append((name, title, source))
            
            # Show breakdown
            for source in sorted(by_source.keys()):
                candidates = by_source[source]
                print(f"    ├─ {source}: {len(candidates)} candidates")
                
                # Show first 3 examples
                for i, (name, title) in enumerate(candidates[:3], 1):
                    print(f"    │  {i}. {name} - {title}")
                
                if len(candidates) > 3:
                    print(f"    │  ... and {len(candidates) - 3} more")
    
    if not collections or all(len(c.get()['ids']) == 0 for c in collections):
        print("\n  ⚠️  Vector DB is EMPTY!")
        print("  This means scraped data was not persisted to the vector database.")
        
except Exception as e:
    print(f"  ❌ Error: {e}")

# 2. Check SQLite (this has only RANKED candidates from completed jobs)
print("\n\n💾 SQLITE DATABASE (Ranked Candidates from Completed Jobs)")
print("-" * 100)

try:
    conn = sqlite3.connect('candidates.db')
    cursor = conn.cursor()
    
    # Get candidates by source
    cursor.execute("""
        SELECT source_portal, COUNT(*) as count
        FROM candidates
        GROUP BY source_portal
        ORDER BY count DESC
    """)
    
    results = cursor.fetchall()
    
    if results:
        print(f"\n  Total candidates in SQLite: {sum(r[1] for r in results)}")
        print(f"\n  Breakdown by source:")
        
        for source, count in results:
            print(f"    ├─ {source}: {count} candidates")
            
            # Show examples
            cursor.execute("""
                SELECT name, current_title
                FROM candidates
                WHERE source_portal = ?
                LIMIT 3
            """, (source,))
            
            examples = cursor.fetchall()
            for i, (name, title) in enumerate(examples, 1):
                print(f"    │  {i}. {name} - {title}")
            
            if count > 3:
                print(f"    │  ... and {count - 3} more")
    else:
        print("\n  ⚠️  No candidates in SQLite database!")
    
    # Check jobs
    print(f"\n\n  Jobs in database:")
    cursor.execute("""
        SELECT id, title, status, created_at
        FROM jobs
        ORDER BY created_at DESC
        LIMIT 5
    """)
    
    jobs = cursor.fetchall()
    for job_id, title, status, created in jobs:
        # Count candidates for this job
        cursor.execute("""
            SELECT COUNT(*)
            FROM candidates
            WHERE id IN (
                SELECT json_extract(value, '$.candidate.id')
                FROM jobs, json_each(jobs.candidates)
                WHERE jobs.id = ?
            )
        """, (job_id,))
        
        # Simpler approach - just count from the candidates JSON
        cursor.execute("SELECT candidates FROM jobs WHERE id = ?", (job_id,))
        result = cursor.fetchone()
        if result and result[0]:
            import json
            try:
                candidates_list = json.loads(result[0])
                candidate_count = len(candidates_list)
            except:
                candidate_count = 0
        else:
            candidate_count = 0
        
        print(f"    • {title} ({status}) - {candidate_count} candidates [{created}]")
    
    conn.close()
    
except Exception as e:
    print(f"  ❌ Error: {e}")
    import traceback
    traceback.print_exc()

# 3. Summary
print("\n\n" + "="*100)
print(" "*40 + "SUMMARY")
print("="*100)

print("""
📊 How the system works:

1. SCRAPING PHASE:
   - Candidates are scraped from portals (Naukri, LinkedIn, GitHub, StackOverflow)
   - ALL scraped candidates are saved to Vector DB for semantic search
   
2. MATCHING & RANKING PHASE:
   - Vector DB is queried to find relevant candidates
   - Candidates are matched and ranked
   - Only TOP 50 ranked candidates are saved to SQLite
   
3. STORAGE:
   - Vector DB = ALL scraped candidates (for future searches)
   - SQLite DB = Only ranked candidates from completed jobs

⚠️  If Vector DB is empty, it means:
   - Data was scraped but not persisted (check vector_db.py)
   - Or the database was cleared/reset
""")

print("="*100 + "\n")
