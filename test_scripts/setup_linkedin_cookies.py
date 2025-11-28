#!/usr/bin/env python3
"""
Setup LinkedIn Cookies
Opens a browser, lets you login, then extracts and saves cookies/credentials to .env
"""

import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
from dotenv import load_dotenv, set_key

def setup_linkedin_cookies():
    print("="*80)
    print("LINKEDIN COOKIE & CREDENTIAL SETUP")
    print("="*80)
    print("\nThis script will:")
    print("1. Open a browser to LinkedIn")
    print("2. Let you login manually")
    print("3. Extract cookies automatically")
    print("4. Save credentials to .env file")
    print("\n" + "="*80)
    
    # Load existing .env
    load_dotenv()
    
    # Check if already configured
    existing_username = os.getenv('LINKEDIN_USERNAME', '')
    if existing_username and existing_username != 'your_email@example.com':
        print(f"\n⚠️  LinkedIn credentials already configured: {existing_username}")
        response = input("Do you want to update them? (y/n): ")
        if response.lower() != 'y':
            print("Cancelled.")
            return
    
    print("\n🌐 Opening browser...")
    
    # Create browser with visible window
    options = uc.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')
    
    driver = uc.Chrome(options=options)
    
    try:
        # Navigate to LinkedIn login
        print("📍 Navigating to LinkedIn...")
        driver.get("https://www.linkedin.com/login")
        
        print("\n" + "="*80)
        print("PLEASE LOGIN TO LINKEDIN")
        print("="*80)
        print("\n📝 Instructions:")
        print("1. Login with your LinkedIn account")
        print("2. Complete any CAPTCHA or verification if prompted")
        print("3. Wait until you see your LinkedIn feed")
        print("4. Come back here and press Enter")
        print("\n⏳ Waiting for you to login...")
        
        input("\n✅ Press Enter after you've logged in successfully...")
        
        # Check if logged in
        current_url = driver.current_url
        print(f"\n📍 Current URL: {current_url}")
        
        if "linkedin.com" not in current_url:
            print("❌ Error: Not on LinkedIn domain.")
            return
        
        if "login" in current_url.lower() or "checkpoint" in current_url.lower():
            print("⚠️  Warning: Still on login/verification page.")
            input("Press Enter after completing login/verification...")
            current_url = driver.current_url
        
        # Extract cookies
        print("\n🍪 Extracting cookies...")
        cookies = driver.get_cookies()
        
        if not cookies:
            print("❌ Error: No cookies found. Make sure you're logged in.")
            return
        
        # Format cookies for .env
        cookie_string = "; ".join([f"{cookie['name']}={cookie['value']}" for cookie in cookies])
        
        print(f"✅ Found {len(cookies)} cookies")
        print(f"   Cookie string length: {len(cookie_string)} characters")
        
        # Get credentials
        print("\n📝 Please provide your LinkedIn credentials:")
        print("   (These will be used for automatic login in the scraper)")
        
        username = input("   LinkedIn email: ").strip()
        password = input("   LinkedIn password: ").strip()
        
        if not username or not password:
            print("❌ Error: Username and password are required")
            return
        
        # Save to .env
        print("\n💾 Saving to .env file...")
        
        env_file = ".env"
        if not os.path.exists(env_file):
            print(f"⚠️  {env_file} not found, creating new file...")
            with open(env_file, 'w') as f:
                f.write("# LinkedIn Configuration\n")
        
        # Update .env file
        set_key(env_file, "LINKEDIN_USERNAME", username)
        set_key(env_file, "LINKEDIN_PASSWORD", password)
        print("✅ Saved LinkedIn credentials")
        
        # Optionally save cookies too
        save_cookies = input("\n💾 Also save cookies? (y/n): ").lower()
        if save_cookies == 'y':
            set_key(env_file, "LINKEDIN_COOKIES", cookie_string)
            print("✅ Saved LinkedIn cookies")
        
        print("\n" + "="*80)
        print("✅ SETUP COMPLETE!")
        print("="*80)
        
        print("\n📋 Configuration saved to .env:")
        print(f"   - LINKEDIN_USERNAME: {username}")
        print(f"   - LINKEDIN_PASSWORD: {'*' * len(password)}")
        if save_cookies == 'y':
            print(f"   - LINKEDIN_COOKIES: {len(cookie_string)} characters")
        
        print("\n🧪 Next Steps:")
        print("1. Test the scraper: python3 test_all_scrapers.py")
        print("2. Start API server: python3 run_api.py")
        
        print("\n💡 Tips:")
        print("- LinkedIn may require CAPTCHA on first automated login")
        print("- The scraper will keep browser open for manual CAPTCHA solving")
        print("- Session is reused across multiple searches")
        
        print("\n🌐 Browser will stay open for testing...")
        print("   Close it manually when done, or press Ctrl+C here")
        
        try:
            input("\nPress Enter to close browser and exit...")
        except KeyboardInterrupt:
            print("\n\nClosing...")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        print("\n🔒 Closing browser...")
        try:
            driver.quit()
        except:
            pass
        print("✅ Done!")

if __name__ == "__main__":
    try:
        setup_linkedin_cookies()
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup cancelled by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
