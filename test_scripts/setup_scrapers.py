#!/usr/bin/env python3
"""
Master Setup Script for All Scrapers
Sets up credentials and cookies for LinkedIn, Naukri, and other scrapers
"""

import os
import sys

def print_menu():
    print("\n" + "="*80)
    print("SCRAPER SETUP - CHOOSE WHAT TO CONFIGURE")
    print("="*80)
    print("\n📋 Available Options:")
    print("\n1. 🔵 LinkedIn Setup")
    print("   - Opens browser for LinkedIn login")
    print("   - Saves username/password to .env")
    print("   - Extracts and saves cookies")
    print("\n2. 🟠 Naukri Resdex Setup")
    print("   - Opens browser for Naukri Resdex login")
    print("   - Saves cookies to .env")
    print("   - Extracts requirement ID")
    print("\n3. ✅ Setup Both (LinkedIn + Naukri)")
    print("   - Runs both setups sequentially")
    print("\n4. 📊 Check Current Configuration")
    print("   - Shows what's already configured")
    print("\n5. ❌ Exit")
    print("\n" + "="*80)

def check_configuration():
    """Check and display current configuration"""
    from dotenv import load_dotenv
    load_dotenv()
    
    print("\n" + "="*80)
    print("CURRENT CONFIGURATION")
    print("="*80)
    
    # LinkedIn
    print("\n🔵 LinkedIn:")
    linkedin_user = os.getenv('LINKEDIN_USERNAME', '')
    linkedin_pass = os.getenv('LINKEDIN_PASSWORD', '')
    
    if linkedin_user and linkedin_user != 'your_email@example.com':
        print(f"   ✅ Username: {linkedin_user}")
        print(f"   ✅ Password: {'*' * len(linkedin_pass) if linkedin_pass else 'Not set'}")
    else:
        print("   ❌ Not configured")
    
    # Naukri
    print("\n🟠 Naukri Resdex:")
    naukri_cookies = os.getenv('NAUKRI_RESDEX_COOKIES', '')
    naukri_req_id = os.getenv('NAUKRI_REQUIREMENT_ID', '')
    naukri_user = os.getenv('NAUKRI_USERNAME', '')
    
    if naukri_cookies and naukri_cookies != 'your_cookies_here':
        print(f"   ✅ Cookies: {len(naukri_cookies)} characters")
        if naukri_req_id:
            print(f"   ✅ Requirement ID: {naukri_req_id}")
        if naukri_user:
            print(f"   ✅ Username: {naukri_user}")
    else:
        print("   ❌ Not configured")
    
    # Other scrapers
    print("\n🌐 Other Scrapers:")
    print("   ✅ Indeed: No credentials needed")
    print("   ✅ GitHub: No credentials needed")
    print("   ✅ StackOverflow: No credentials needed")
    
    print("\n" + "="*80)

def run_linkedin_setup():
    """Run LinkedIn setup script"""
    print("\n🔵 Starting LinkedIn setup...")
    try:
        import setup_linkedin_cookies
        setup_linkedin_cookies.setup_linkedin_cookies()
    except Exception as e:
        print(f"❌ Error running LinkedIn setup: {e}")

def run_naukri_setup():
    """Run Naukri setup script"""
    print("\n🟠 Starting Naukri setup...")
    try:
        import setup_naukri_cookies
        setup_naukri_cookies.setup_naukri_cookies()
    except Exception as e:
        print(f"❌ Error running Naukri setup: {e}")

def main():
    print("="*80)
    print("🚀 AI SOURCING AGENT - SCRAPER SETUP")
    print("="*80)
    print("\nWelcome! This script will help you configure scrapers for:")
    print("  • LinkedIn (requires login credentials)")
    print("  • Naukri Resdex (requires login and cookies)")
    print("  • Other scrapers work without configuration")
    
    while True:
        print_menu()
        
        try:
            choice = input("\nEnter your choice (1-5): ").strip()
            
            if choice == '1':
                run_linkedin_setup()
                input("\nPress Enter to continue...")
            
            elif choice == '2':
                run_naukri_setup()
                input("\nPress Enter to continue...")
            
            elif choice == '3':
                print("\n📋 Setting up both LinkedIn and Naukri...")
                print("\n" + "="*80)
                print("STEP 1/2: LINKEDIN SETUP")
                print("="*80)
                run_linkedin_setup()
                
                input("\n✅ LinkedIn setup complete. Press Enter to continue to Naukri setup...")
                
                print("\n" + "="*80)
                print("STEP 2/2: NAUKRI SETUP")
                print("="*80)
                run_naukri_setup()
                
                print("\n" + "="*80)
                print("✅ ALL SETUPS COMPLETE!")
                print("="*80)
                input("\nPress Enter to continue...")
            
            elif choice == '4':
                check_configuration()
                input("\nPress Enter to continue...")
            
            elif choice == '5':
                print("\n👋 Goodbye!")
                break
            
            else:
                print("\n❌ Invalid choice. Please enter 1-5.")
        
        except KeyboardInterrupt:
            print("\n\n⚠️  Setup cancelled by user")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*80)
    print("NEXT STEPS")
    print("="*80)
    print("\n🧪 Test your scrapers:")
    print("   python3 test_all_scrapers.py")
    print("\n🚀 Start the API server:")
    print("   python3 run_api.py")
    print("\n📚 Read documentation:")
    print("   - SCRAPERS_UPDATED.md")
    print("   - NAUKRI_RESDEX_SETUP.md")
    print("   - MCP_ARCHITECTURE.md")
    print("\n" + "="*80)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup cancelled by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
