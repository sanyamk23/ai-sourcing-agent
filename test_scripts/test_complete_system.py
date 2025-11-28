#!/usr/bin/env python3
"""
Complete System Test: MCP Tools + Vector DB + Parallel Scraping
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
    print("COMPLETE SYSTEM TEST: MCP + Vector DB + Parallel Scraping")
    print("="*80)
    
    # 1. Initialize components
    print("\n📦 Step 1: Initializing components...")
    config = Config.load_yaml_config()
    mcp_tools = ScraperMCPTools(config)
    vector_db = CandidateVectorDB()
    
    print(f"✅ MCP Tools initialized")
    print(f"✅ Vector DB initialized")
    
    # 2. Show available tools
    print("\n🔧 Step 2: Available MCP Tools:")
    schemas = mcp_tools.get_tools_schema()
    for tool in schemas:
        print(f"  - {tool['name']}")
        print(f"    {tool['description'][:70]}...")
    
    # 3. Test Naukri scraper (should work without credits)
    print("\n🔍 Step 3: Testing Naukri scraper...")
    try:
        result = await mcp_tools.scrape_naukri(
            job_title="Python Developer",
            location="Jaipur",
            skills=["python", "django"],
            experience_years=3
        )
        print(f"✅ Naukri: Found {result['count']} candidates")
        
        if result['count'] > 0:
            # 4. Store in Vector DB
            print("\n💾 Step 4: Storing candidates in Vector DB...")
            candidates = [Candidate(**c) for c in result['candidates']]
            added = vector_db.add_candidates(candidates)
            print(f"✅ Added {added} candidates to Vector DB")
            
            # 5. Test similarity search
            print("\n🔎 Step 5: Testing similarity search...")
            similar = vector_db.search_similar(
                query="Python Django developer with experience",
                n_results=5
            )
            print(f"✅ Found {len(similar)} similar candidates:")
            for i, candidate in enumerate(similar[:3], 1):
                meta = candidate['metadata']
                print(f"  {i}. {meta['name']} - {meta['title']}")
                print(f"     Location: {meta['location']}")
                print(f"     Source: {meta['source']}")
        else:
            print("⚠️  No candidates found (might need to adjust search criteria)")
    
    except Exception as e:
        print(f"❌ Error testing Naukri: {e}")
        print("   (This is expected if browser automation fails)")
    
    # 6. Test parallel scraping (with available scrapers)
    print("\n⚡ Step 6: Testing parallel scraping...")
    try:
        # Only use Naukri for now (Coresignal needs credits)
        result = await mcp_tools.scrape_all_parallel(
            job_title="Python Developer",
            scrapers=["naukri"],  # Add "coresignal" when you have credits
            location="Jaipur",
            skills=["python"]
        )
        print(f"✅ Parallel scraping complete:")
        print(f"   Total candidates: {result['total_count']}")
        print(f"   Sources used: {result['sources']}")
        print(f"   By source: {result['by_source']}")
    except Exception as e:
        print(f"❌ Error in parallel scraping: {e}")
    
    # 7. Show Vector DB stats
    print("\n📊 Step 7: Vector DB Statistics:")
    stats = vector_db.get_stats()
    print(f"   Total candidates: {stats['total_candidates']}")
    print(f"   By source: {stats['by_source']}")
    
    print("\n" + "="*80)
    print("✅ SYSTEM TEST COMPLETE")
    print("="*80)
    print("\nNext steps:")
    print("1. Get Coresignal API credits to enable API scraping")
    print("2. Add more scrapers (Indeed, GitHub, etc.)")
    print("3. Integrate with LLM for intelligent orchestration")
    print("4. Run full API server: python3 run_api.py")
    print("="*80)

if __name__ == "__main__":
    asyncio.run(main())
