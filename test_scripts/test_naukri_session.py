#!/usr/bin/env python3
"""
Test Naukri Resdex with Persistent Session
This script tests the scraper using the persistent browser session
"""

import asyncio
import sys
sys.path.insert(0, '.')

from src.scrapers import NaukriScraper
from src.models import JobDescription
from src.config import Config

async def main():
    print("="*80)
    print("TESTING NAUKRI RESDEX WITH PERSISTENT SESSION")
    print("="*80)
    
    # Try to import persistent browser manager
    try:
        from naukri_persistent_browser import browser_manager
        
        # Get or create persistent browser
        print("\n🌐 Getting persistent browser...")
        driver = browser_manager.get_driver()
        
        # Check if logged in
        if not browser_manager.check_login_status():
            print("\n⚠️  Not logged in. Navigating to Resdex...")
            driver.get("https://resdex.naukri.com/lite")
            import time
            time.sleep(3)
            
            if "login" in driver.current_url.lower():
                print("\n❌ Please login first!")
                print("   1. Login in the browser window")
                print("   2. Run this script again")
                input("\nPress Enter after logging in...")
                browser_manager.set_logged_in(True)
        
        print("✅ Browser session ready")
        
    except Exception as e:
        print(f"\n❌ Error with persistent browser: {e}")
        print("\n📝 Please run setup first:")
        print("   python3 run_naukri_complete_test.py")
        return
    
    # Initialize scraper
    print("\n🔧 Initializing Naukri Scraper...")
    config = Config.load_yaml_config()
    scraper = NaukriScraper('naukri', 'https://www.naukri.com', config)
    
    # Create test job description
    job = JobDescription(
        title="Python Developer",
        description="Looking for experienced Python developers",
        required_skills=["python", "django", "flask"],
        experience_years=2,
        location="Jaipur"
    )
    
    print(f"\n🔍 Search Parameters:")
    print(f"   Title: {job.title}")
    print(f"   Location: {job.location}")
    print(f"   Skills: {', '.join(job.required_skills)}")
    print(f"   Experience: {job.experience_years}+ years")
    
    # Run scraper
    print("\n" + "="*80)
    print("SCRAPING CANDIDATES")
    print("="*80 + "\n")
    
    try:
        candidates = await scraper.scrape(job)
        
        print("\n" + "="*80)
        print("RESULTS")
        print("="*80)
        
        print(f"\n✅ Found {len(candidates)} candidates")
        
        if candidates:
            print(f"\n📊 Sample Candidates (showing first 5):\n")
            
            for i, candidate in enumerate(candidates[:5], 1):
                print(f"{i}. {candidate.name}")
                print(f"   Title: {candidate.current_title}")
                print(f"   Location: {candidate.location}")
                print(f"   Skills: {', '.join(candidate.skills[:5])}")
                if candidate.summary:
                    print(f"   Summary: {candidate.summary}")
                print(f"   Source: {candidate.source_portal}")
                print()
            
            if len(candidates) > 5:
                print(f"... and {len(candidates) - 5} more candidates\n")
        else:
            print("\n⚠️  No candidates found")
            print("\nPossible reasons:")
            print("1. No candidates match the criteria")
            print("2. Wrong requirement ID")
            print("3. Session expired - restart setup_naukri_session.py")
    
    except Exception as e:
        print(f"\n❌ Error during scraping: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80)
    
    print("\n💡 The browser session is still active")
    print("   You can run this test again without re-logging in")

if __name__ == "__main__":
    asyncio.run(main())
