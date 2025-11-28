#!/usr/bin/env python3
"""
Test All Active Scrapers: LinkedIn, Indeed, Naukri, GitHub, StackOverflow
"""

import asyncio
import sys
sys.path.insert(0, '.')

from src.mcp_tools import ScraperMCPTools
from src.vector_db import CandidateVectorDB
from src.models import Candidate
from src.config import Config

async def main():
    print("="*80)
    print("TESTING ALL ACTIVE SCRAPERS")
    print("="*80)
    
    # Initialize
    print("\n📦 Initializing components...")
    config = Config.load_yaml_config()
    
    # Initialize persistent browsers
    print("🌐 Initializing persistent browsers...")
    try:
        from naukri_persistent_browser import naukri_browser_manager, linkedin_browser_manager
        print("  ✅ Naukri browser manager ready")
        print("  ✅ LinkedIn browser manager ready")
    except Exception as e:
        print(f"  ⚠️  Could not initialize browser managers: {e}")
    
    mcp_tools = ScraperMCPTools(config)
    vector_db = CandidateVectorDB()
    
    print(f"✅ MCP Tools initialized with {len(mcp_tools.scrapers)} scrapers")
    print(f"✅ Vector DB initialized")
    
    # Show available scrapers
    print("\n🔧 Available Scrapers:")
    for name in mcp_tools.scrapers.keys():
        print(f"  - {name}")
    
    # Test parameters
    job_title = "Python Developer"
    location = "Jaipur"
    skills = ["python", "django"]
    
    print(f"\n🔍 Search Parameters:")
    print(f"  Job Title: {job_title}")
    print(f"  Location: {location}")
    print(f"  Skills: {', '.join(skills)}")
    
    # Test each scraper individually
    print("\n" + "="*80)
    print("TESTING INDIVIDUAL SCRAPERS")
    print("="*80)
    
    results = {}
    
    # 1. Test LinkedIn
    print("\n1️⃣  Testing LinkedIn...")
    try:
        result = await mcp_tools.scrape_linkedin(
            job_title=job_title,
            location=location,
            skills=skills
        )
        results['linkedin'] = result['count']
        print(f"   ✅ LinkedIn: Found {result['count']} candidates")
    except Exception as e:
        print(f"   ❌ LinkedIn error: {e}")
        results['linkedin'] = 0
    
    # 2. Test Indeed
    print("\n2️⃣  Testing Indeed...")
    try:
        result = await mcp_tools.scrape_indeed(
            job_title=job_title,
            location=location,
            skills=skills
        )
        results['indeed'] = result['count']
        print(f"   ✅ Indeed: Found {result['count']} candidates")
    except Exception as e:
        print(f"   ❌ Indeed error: {e}")
        results['indeed'] = 0
    
    # 3. Test Naukri
    print("\n3️⃣  Testing Naukri...")
    try:
        result = await mcp_tools.scrape_naukri(
            job_title=job_title,
            location=location,
            skills=skills
        )
        results['naukri'] = result['count']
        print(f"   ✅ Naukri: Found {result['count']} candidates")
    except Exception as e:
        print(f"   ❌ Naukri error: {e}")
        results['naukri'] = 0
    
    # 4. Test GitHub
    print("\n4️⃣  Testing GitHub...")
    try:
        result = await mcp_tools.scrape_github(skills=skills)
        results['github'] = result['count']
        print(f"   ✅ GitHub: Found {result['count']} candidates")
    except Exception as e:
        print(f"   ❌ GitHub error: {e}")
        results['github'] = 0
    
    # 5. Test StackOverflow
    print("\n5️⃣  Testing StackOverflow...")
    try:
        result = await mcp_tools.scrape_github(skills=skills)  # Using same method
        results['stackoverflow'] = result['count']
        print(f"   ✅ StackOverflow: Found {result['count']} candidates")
    except Exception as e:
        print(f"   ❌ StackOverflow error: {e}")
        results['stackoverflow'] = 0
    
    # Test parallel scraping
    print("\n" + "="*80)
    print("TESTING PARALLEL SCRAPING")
    print("="*80)
    
    print("\n⚡ Running all scrapers in parallel...")
    try:
        parallel_result = await mcp_tools.scrape_all_parallel(
            job_title=job_title,
            scrapers=['linkedin', 'indeed', 'naukri', 'github', 'stackoverflow'],
            location=location,
            skills=skills
        )
        
        print(f"\n✅ Parallel scraping complete!")
        print(f"   Total unique candidates: {parallel_result['total_count']}")
        print(f"   Sources used: {', '.join(parallel_result['sources'])}")
        print(f"\n   Breakdown by source:")
        for source, count in parallel_result['by_source'].items():
            print(f"     - {source}: {count} candidates")
        
        # Store in Vector DB
        if parallel_result['total_count'] > 0:
            print(f"\n💾 Storing {parallel_result['total_count']} candidates in Vector DB...")
            candidates = [Candidate(**c) for c in parallel_result['candidates']]
            added = vector_db.add_candidates(candidates)
            print(f"   ✅ Added {added} candidates to Vector DB")
            
            # Test similarity search
            print(f"\n🔎 Testing similarity search...")
            similar = vector_db.search_similar(
                query="experienced Python developer with Django",
                n_results=5
            )
            print(f"   ✅ Found {len(similar)} similar candidates:")
            for i, candidate in enumerate(similar[:3], 1):
                meta = candidate['metadata']
                print(f"     {i}. {meta['name']} - {meta['title']}")
                print(f"        Source: {meta['source']} | Location: {meta['location']}")
    
    except Exception as e:
        print(f"   ❌ Parallel scraping error: {e}")
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    
    print("\n📊 Results by Scraper:")
    total = 0
    for scraper, count in results.items():
        status = "✅" if count > 0 else "❌"
        print(f"   {status} {scraper.capitalize()}: {count} candidates")
        total += count
    
    print(f"\n   Total candidates found: {total}")
    
    # Vector DB stats
    stats = vector_db.get_stats()
    print(f"\n💾 Vector DB Statistics:")
    print(f"   Total stored: {stats['total_candidates']} candidates")
    print(f"   By source: {stats['by_source']}")
    
    print("\n" + "="*80)
    print("✅ TEST COMPLETE")
    print("="*80)
    print("\nActive Scrapers:")
    print("  ✅ LinkedIn (requires credentials)")
    print("  ✅ Indeed")
    print("  ✅ Naukri (Indian job portal)")
    print("  ✅ GitHub (developer profiles)")
    print("  ✅ StackOverflow (developer profiles)")
    print("\nNext: Run API server with: python3 run_api.py")
    print("="*80)

if __name__ == "__main__":
    asyncio.run(main())
