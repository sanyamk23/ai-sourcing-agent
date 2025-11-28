#!/usr/bin/env python3
"""
Comprehensive database check
"""
import sqlite3
from collections import Counter

print("\n" + "="*80)
print("CHECKING ALL DATA SOURCES")
print("="*80)

# Check SQLite
print("\n1️⃣  SQLITE DATABASE (candidates.db)")
print("-" * 80)
try:
    conn = sqlite3.connect('candidates.db')
    cursor = conn.cursor()
    
    # List all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print(f"Tables: {[t[0] for t in tables]}")
    
    # Check candidates table
    cursor.execute("SELECT source_portal, COUNT(*) FROM candidates GROUP BY source_portal")
    results = cursor.fetchall()
    print(f"\nCandidates by source:")
    for source, count in results:
        print(f"  {source}: {count}")
    
    cursor.execute("SELECT COUNT(*) FROM candidates")
    total = cursor.fetchone()[0]
    print(f"\nTotal in SQLite: {total}")
    
    conn.close()
except Exception as e:
    print(f"Error: {e}")

# Check Vector DB
print("\n2️⃣  VECTOR DATABASE (ChromaDB)")
print("-" * 80)
try:
    import chromadb
    from chromadb.config import Settings
    
    client = chromadb.PersistentClient(
        path="./chroma_db",
        settings=Settings(anonymized_telemetry=False)
    )
    
    # List all collections
    collections = client.list_collections()
    print(f"Collections: {[c.name for c in collections]}")
    
    if collections:
        for collection in collections:
            print(f"\nCollection: {collection.name}")
            results = collection.get()
            total = len(results['ids'])
            print(f"  Total documents: {total}")
            
            if total > 0:
                # Count by source
                sources = [m.get('source_portal', 'unknown') for m in results['metadatas']]
                source_counts = Counter(sources)
                print(f"  By source:")
                for source, count in source_counts.most_common():
                    print(f"    {source}: {count}")
    else:
        print("No collections found!")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

# Check if there's a separate jobs database
print("\n3️⃣  CHECKING FOR RECENT DATA")
print("-" * 80)
try:
    conn = sqlite3.connect('candidates.db')
    cursor = conn.cursor()
    
    # Check most recent candidates
    cursor.execute("""
        SELECT name, current_title, source_portal, created_at 
        FROM candidates 
        ORDER BY created_at DESC 
        LIMIT 10
    """)
    recent = cursor.fetchall()
    
    print("Most recent 10 candidates:")
    for name, title, source, created in recent:
        print(f"  {name} - {title} (from {source}) [{created}]")
    
    conn.close()
except Exception as e:
    print(f"Error: {e}")

print("\n" + "="*80)
