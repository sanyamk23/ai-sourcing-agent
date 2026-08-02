#!/usr/bin/env python3
"""
Complete Naukri Resdex Test - Setup and Verify
This script will guide you through setup and test until we get candidate data
"""

import sys
import os
import time
import asyncio
from dotenv import load_dotenv, set_key

# Add src to path
sys.path.insert(0, '.')

from naukri_persistent_browser import browser_manager
from src.scrapers import NaukriScraper
from src.models import JobDescription
from src.config import Config

def print_header(text):
    print("\n" + "="*80)
    print(text.center(80))
    print("="*80 + "\n")

def print_step(number, text):
    print(f"\n{'='*80}")
    print(f"STEP {number}: {text}")
    print(f"{'='*80}\n")

async def test_scraper(scraper, job):
    """Test the scraper and return candidates"""
    print("🔍 Starting scrape...")
    candidates = await scraper.scrape(job)
    return candidates

def main():
    print_header("NAUKRI RESDEX COMPLETE SETUP & TEST")
    
    print("This script will:")
    print("1. Open a persistent browser with saved profile")
    print("2. Guide you through login (if needed)")
    print("3. Test the scraper")
    print("4. Show candidate data")
    print("5. Keep browser open for future use")
    
    print("\n⏳ Starting in 2 seconds...")
    time.sleep(2)
    
    # Load environment
    load_dotenv()
    
    # STEP 1: Open persistent browser
    print_step(1, "OPENING PERSISTENT BROWSER")
    
    print("🌐 Opening Chrome with persistent profile...")
    print("   Profile location: ./chrome_profile_naukri")
    print("   Your login will be saved permanently!")
    
    driver = browser_manager.get_driver()
    print("✅ Browser opened")
    
    # STEP 2: Navigate and login
    print_step(2, "LOGIN TO NAUKRI RESDEX")
    
    print("📍 Navigating to Naukri Resdex...")
    driver.get("https://resdex.naukri.com/lite")
    time.sleep(3)
    
    current_url = driver.current_url
    print(f"   Current URL: {current_url}")
    
    if "login" in current_url.lower() or "signin" in current_url.lower():
        print("\n⚠️  You need to login")
        print("\n📝 Instructions:")
        print("   1. Look at the Chrome window that just opened")
        print("   2. Login with your Naukri recruiter credentials")
        print("   3. If Naukri Launcher app opens, login there too")
        print("   4. Complete any CAPTCHA if shown")
        print("   5. Wait for the dashboard to load")
        print("   6. Come back here and press Enter")
        
        input("\n✅ Press Enter after you've logged in...")
        
        # Verify login
        time.sleep(2)
        current_url = driver.current_url
        
        if "login" in current_url.lower():
            print("❌ Still on login page. Please complete login.")
            input("   Press Enter after logging in...")
            current_url = driver.current_url
    else:
        print("✅ Already logged in! (Session saved from before)")
    
    # Mark as logged in
    browser_manager.set_logged_in(True)
    print("✅ Login successful - session saved!")
    
    # STEP 3: Navigate to requirements page first
    print_step(3, "NAVIGATE TO REQUIREMENTS")
    
    print("📍 Opening My Requirements page...")
    driver.get("https://resdex.naukri.com/lite/myrequirements")
    time.sleep(3)
    
    print("✅ Requirements page loaded")
    print("\n💡 You should see a list of your job requirements")
    
    # Get requirement ID
    requirement_id = os.getenv('NAUKRI_REQUIREMENT_ID', '125289')
    
    print(f"\n📋 Using requirement ID: {requirement_id}")
    print("   (You can change this in .env file)")
    time.sleep(1)
    
    # STEP 4: Navigate to requirement
    print_step(4, "OPENING REQUIREMENT")
    
    print(f"📍 Looking for requirement {requirement_id} on the page...")
    
    # Try to find and click the requirement link
    try:
        # Look for the requirement link with this ID
        requirement_link = driver.find_element(By.CSS_SELECTOR, f"a[href*='requirementId={requirement_id}']")
        
        # Get requirement details
        try:
            req_name = requirement_link.find_element(By.CSS_SELECTOR, ".tuple_reqName__xYnHU, [class*='reqName']").text
            candidate_count = requirement_link.find_element(By.CSS_SELECTOR, ".tuple_count__mvMaE, [class*='count']").text
            print(f"   Found: {req_name} ({candidate_count} candidates)")
        except:
            print(f"   Found requirement link")
        
        print(f"\n🖱️  Clicking on requirement...")
        requirement_link.click()
        time.sleep(5)
        
    except:
        # Fallback: navigate directly
        print(f"   Requirement not found on page, navigating directly...")
        url = f"https://resdex.naukri.com/lite/candidatesearchresults?requirementId={requirement_id}&requirementGroupId={requirement_id}&resPerPage=50&pageNo=1&activeTab=potential"
        driver.get(url)
        time.sleep(5)
    
    current_url = driver.current_url
    print(f"\n📍 Current URL: {current_url}")
    
    if "login" in current_url.lower():
        print("❌ Session expired. Please login again.")
        return
    
    print("✅ Requirement page loaded")
    
    # Check if we can see candidates
    print("\n📋 Checking page content...")
    page_title = driver.title
    print(f"   Page title: {page_title}")
    
    # Check for candidate count on page
    try:
        # Look for candidate count indicator
        page_text = driver.find_element(By.TAG_NAME, "body").text
        if "candidates" in page_text.lower() or "resumes" in page_text.lower():
            print("   ✅ Candidate data detected on page")
    except:
        pass
    
    print("\n⏳ Waiting for page to fully load...")
    time.sleep(3)
    
    # STEP 5: Test scraper
    print_step(5, "TESTING SCRAPER")
    
    print("🔧 Initializing scraper...")
    config = Config.load_yaml_config()
    scraper = NaukriScraper('naukri', 'https://www.naukri.com', config)
    
    # Create test job
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
    
    print("\n🚀 Running scraper...")
    print("   (This will extract data from the current page)")
    
    try:
        candidates = asyncio.run(test_scraper(scraper, job))
        
        # STEP 6: Show results
        print_step(6, "RESULTS")
        
        if candidates:
            print(f"✅ SUCCESS! Found {len(candidates)} candidates\n")
            
            print("📊 Sample Candidates (showing first 20):\n")
            for i, candidate in enumerate(candidates[:20], 1):
                print(f"{i}. {candidate.name}")
                print(f"   Title: {candidate.current_title}")
                print(f"   Location: {candidate.location}")
                print(f"   Skills: {', '.join(candidate.skills[:5])}")
                if candidate.summary:
                    print(f"   Summary: {candidate.summary}")
                print(f"   Source: {candidate.source_portal}")
                print()
            
            if len(candidates) > 20:
                print(f"... and {len(candidates) - 20} more candidates\n")
            
            # Statistics
            print("="*80)
            print("STATISTICS")
            print("="*80 + "\n")
            
            # Skills distribution
            all_skills = {}
            for c in candidates:
                for skill in c.skills:
                    all_skills[skill] = all_skills.get(skill, 0) + 1
            
            print("🛠️  Top Skills:")
            top_skills = sorted(all_skills.items(), key=lambda x: x[1], reverse=True)[:10]
            for skill, count in top_skills:
                print(f"   - {skill}: {count} candidates")
            
            # Locations
            locations = {}
            for c in candidates:
                if c.location:
                    locations[c.location] = locations.get(c.location, 0) + 1
            
            print(f"\n📍 Top Locations:")
            top_locations = sorted(locations.items(), key=lambda x: x[1], reverse=True)[:5]
            for location, count in top_locations:
                print(f"   - {location}: {count} candidates")
            
            print("\n" + "="*80)
            print("✅ TEST SUCCESSFUL!")
            print("="*80)
            
        else:
            print("⚠️  No candidates found\n")
            print("Possible reasons:")
            print("1. Wrong requirement ID")
            print("2. No candidates in this requirement")
            print("3. Page structure changed")
            print("\nDebug info saved to: resdex_page_debug.html")
            
            # Save debug HTML
            with open("resdex_page_debug.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            print("✅ Debug HTML saved")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    # STEP 7: Keep browser open
    print_step(7, "SESSION SAVED")
    
    print("💡 What happens now:")
    print("   ✓ Browser stays open with your login")
    print("   ✓ Session saved in: ./chrome_profile_naukri")
    print("   ✓ Next time you run this, you won't need to login")
    print("   ✓ You can run test_naukri_session.py anytime")
    print("   ✓ All scrapers will use this browser")
    
    print("\n🌐 Browser window:")
    print("   - You can close it manually")
    print("   - Or keep it open for faster scraping")
    print("   - Your login is saved either way")
    
    print("\n🧪 Next steps:")
    print("   1. Run: python3 test_naukri_session.py")
    print("   2. Run: python3 test_all_scrapers.py")
    print("   3. Start API: python3 run_api.py")
    
    print("\n" + "="*80)
    print("✅ SETUP COMPLETE!")
    print("="*80)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test cancelled by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
