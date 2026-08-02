#!/usr/bin/env python3
"""
Setup Naukri Resdex Persistent Session
Opens a browser, lets you login, keeps it open, and allows scrapers to reuse it
"""

import sys
import os
import time
from dotenv import load_dotenv, set_key

# Add src to path
sys.path.insert(0, '.')

from naukri_persistent_browser import browser_manager
from src.scrapers import NaukriScraper

def setup_persistent_session():
    print("="*80)
    print("NAUKRI RESDEX PERSISTENT SESSION SETUP")
    print("="*80)
    print("\nThis script will:")
    print("1. Open a browser with persistent profile")
    print("2. Let you login manually (login saved for future)")
    print("3. Keep the browser open forever")
    print("4. Allow scrapers to reuse this session")
    print("\n💡 Your login will be saved in: ./chrome_profile_naukri")
    print("   Next time you won't need to login again!")
    print("\n" + "="*80)
    
    # Load existing .env
    load_dotenv()
    
    print("\n🌐 Opening persistent browser...")
    
    # Get the persistent browser
    driver = browser_manager.get_driver()
    
    try:
        # Navigate to Naukri Resdex
        print("📍 Navigating to Naukri Resdex...")
        driver.get("https://resdex.naukri.com/lite")
        time.sleep(3)
        
        # Check if already logged in
        current_url = driver.current_url
        if "login" in current_url.lower() or "signin" in current_url.lower():
            print("\n" + "="*80)
            print("PLEASE LOGIN TO NAUKRI RESDEX")
            print("="*80)
            print("\n📝 Instructions:")
            print("1. Login with your Naukri recruiter account")
            print("2. Complete any CAPTCHA if prompted")
            print("3. If Naukri Launcher opens, login there too")
            print("4. Navigate to a candidate search or requirement")
            print("5. Wait until you see candidate results")
            print("6. Come back here and press Enter")
            print("\n⏳ Waiting for you to login...")
            
            input("\n✅ Press Enter after you've logged in and can see candidate results...")
            current_url = driver.current_url
        else:
            print("\n✅ Already logged in! (Session saved from last time)")
            print("📍 Navigating to requirements page...")
            driver.get("https://resdex.naukri.com/lite/myrequirements")
            time.sleep(3)
            current_url = driver.current_url
        
        # Verify login
        print(f"\n📍 Current URL: {current_url}")
        
        if "login" in current_url.lower() or "signin" in current_url.lower():
            print("⚠️  Warning: Still on login page. Make sure you're logged in.")
            input("Press Enter after logging in...")
            current_url = driver.current_url
        
        # Navigate to requirements page
        print("\n📍 Navigating to My Requirements page...")
        driver.get("https://resdex.naukri.com/lite/myrequirements")
        time.sleep(3)
        
        print("✅ Requirements page loaded")
        print("   You should see a list of your job requirements")
        
        # Get requirement ID
        requirement_id = os.getenv('NAUKRI_REQUIREMENT_ID', '125289')
        
        print(f"\n📋 Current requirement ID: {requirement_id}")
        print("\n📝 Options:")
        print("   1. Press Enter to use this requirement ID")
        print("   2. Or click a requirement in browser and enter the ID from URL")
        
        user_input = input("\n   Enter requirement ID (or press Enter to use current): ").strip()
        
        if user_input:
            requirement_id = user_input
        
        if not requirement_id:
            requirement_id = "125289"
        
        # Save requirement ID to .env
        env_file = ".env"
        if os.path.exists(env_file):
            set_key(env_file, "NAUKRI_REQUIREMENT_ID", requirement_id)
            print(f"✅ Saved NAUKRI_REQUIREMENT_ID: {requirement_id}")
        
        # Mark as logged in
        browser_manager.set_logged_in(True)
        
        # Set the shared driver in NaukriScraper
        NaukriScraper.set_shared_driver(driver)
        
        print("\n" + "="*80)
        print("✅ SESSION READY!")
        print("="*80)
        
        print("\n🌐 Browser session is now active and persistent")
        print("   ✓ Login saved in: ./chrome_profile_naukri")
        print("   ✓ Next time you won't need to login again")
        print("   ✓ The scraper will reuse this browser window")
        print("   ✓ Keep this script running while using the scraper")
        
        print("\n🧪 Test the scraper in another terminal:")
        print("   python3 test_naukri_session.py")
        
        print("\n💡 Tips:")
        print("- Keep this window open while scraping")
        print("- The browser will stay logged in forever")
        print("- Your session is saved, even after restart")
        print("- Press Ctrl+C here when done (browser stays open)")
        
        # Keep the script running
        print("\n⏳ Session active. Press Ctrl+C when done...")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n🛑 Keeping browser open, closing script...")
    
    except KeyboardInterrupt:
        print("\n\n🛑 Script stopped (browser stays open)")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n💡 Browser window is still open and logged in")
        print("   You can close it manually or keep it for next time")
        print("   Your session is saved in: ./chrome_profile_naukri")
        print("\n✅ Done!")

if __name__ == "__main__":
    try:
        setup_persistent_session()
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup cancelled by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
