#!/usr/bin/env python3
"""
Debug LinkedIn candidate skills
"""
from src.vector_db import CandidateVectorDB

vector_db = CandidateVectorDB()

# Get all candidates
results = vector_db.collection.get()

print("\n" + "="*80)
print("LINKEDIN CANDIDATES IN VECTOR DB")
print("="*80)

linkedin_count = 0
for i, metadata in enumerate(results['metadatas']):
    source = metadata.get('source_portal') or metadata.get('source', '')
    
    if 'linkedin' in source.lower():
        linkedin_count += 1
        name = metadata.get('name', 'Unknown')
        title = metadata.get('title', 'N/A')
        skills = metadata.get('skills', '[]')
        
        print(f"\n{linkedin_count}. {name}")
        print(f"   Title: {title}")
        print(f"   Source: {source}")
        print(f"   Skills: {skills}")

print(f"\n" + "="*80)
print(f"Total LinkedIn candidates: {linkedin_count}")
print("="*80 + "\n")
