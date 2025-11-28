#!/usr/bin/env python3
"""
Quick script to check if vector DB has candidates
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.dirname(__file__))

try:
    from src.vector_db import CandidateVectorDB
    
    print("\n" + "="*60)
    print("VECTOR DB STATUS CHECK")
    print("="*60)
    
    # Initialize vector DB
    print("\n1. Initializing Vector DB...")
    vector_db = CandidateVectorDB()
    print("   ✅ Vector DB initialized")
    
    # Check collection
    print("\n2. Checking collection...")
    try:
        collection = vector_db.collection
        count = collection.count()
        print(f"   ✅ Collection exists")
        print(f"   📊 Total candidates: {count}")
        
        if count > 0:
            # Get a sample
            print("\n3. Sample candidates:")
            results = collection.get(limit=5)
            for i, (doc_id, metadata) in enumerate(zip(results['ids'], results['metadatas']), 1):
                name = metadata.get('name', 'Unknown')
                title = metadata.get('current_title', 'Unknown')
                source = metadata.get('source_portal', 'Unknown')
                print(f"   {i}. {name} - {title} (from {source})")
        else:
            print("\n⚠️  No candidates in vector DB yet")
            print("   Run the scraper to add candidates")
    
    except Exception as e:
        print(f"   ❌ Error checking collection: {e}")
    
    print("\n" + "="*60)
    print("✅ Vector DB is working!")
    print("="*60 + "\n")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
