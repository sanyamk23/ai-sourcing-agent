#!/usr/bin/env python3
"""
Test script to verify persistent browser and cookie fixes
"""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.dirname(__file__))

from naukri_persistent_browser import naukri_browser_manager, linkedin_browser_manager
from src.models import JobDescription

async def test_naukri_persistent():
    """Test Naukri persistent browser"""
    print("\n" + "="*60)
    print("TEST 1: Naukri Persistent Browser")
    print("="*60)
    
    try:
        # Test get_driver method
        print("\n1. Testing get_driver() method...")
        driver = naukri_browser_manager.get_driver()
        print(f"   ✅ Driver created: {driver is not None}")
        
        # Test navigation
        print("\n2. Testing navigation...")
        requirement_id = os.getenv('NAUKRI_REQUIREMENT_ID', '125289')
        url = f"https://resdex.naukri.com/lite/candidatesearchresults?requirementId={requirement_id}"
        driver.get(url)
        await asyncio.sleep(3)
        print(f"   ✅ Navigated to: {driver.current_url[:50]}...")
        
        # Check login status
        print("\n3. Checking login status...")
        current_url = driver.current_url
        if "login" in current_url.lower():
            print("   ⚠️  Not logged in - cookies may be expired")
        else:
            print("   ✅ Appears to be logged in")
        
        print("\n4. Browser window left open for manual inspection")
        print("   Close the browser manually when done")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_linkedin_persistent():
    """Test LinkedIn persistent browser"""
    print("\n" + "="*60)
    print("TEST 2: LinkedIn Persistent Browser")
    print("="*60)
    
    try:
        # Test get_driver method
        print("\n1. Testing get_driver() method...")
        driver = linkedin_browser_manager.get_driver()
        print(f"   ✅ Driver created: {driver is not None}")
        
        # Test navigation
        print("\n2. Testing navigation...")
        driver.get("https://www.linkedin.com/feed")
        await asyncio.sleep(3)
        print(f"   ✅ Navigated to: {driver.current_url[:50]}...")
        
        # Check login status
        print("\n3. Checking login status...")
        current_url = driver.current_url
        if "feed" in current_url or "mynetwork" in current_url:
            print("   ✅ Logged in successfully")
        else:
            print("   ⚠️  Not logged in - may need to login manually")
        
        print("\n4. Browser window left open for manual inspection")
        print("   Close the browser manually when done")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_cookie_parsing():
    """Test cookie parsing from .env"""
    print("\n" + "="*60)
    print("TEST 3: Cookie Parsing")
    print("="*60)
    
    cookie_string = os.getenv('NAUKRI_RESDEX_COOKIES', '')
    
    print(f"\n1. Raw cookie string length: {len(cookie_string)}")
    has_quotes = cookie_string.startswith("'") or cookie_string.startswith('"')
    print(f"   Starts with quote: {has_quotes}")
    
    # Strip quotes
    cleaned = cookie_string.strip().strip("'").strip('"')
    print(f"\n2. After stripping quotes: {len(cleaned)}")
    
    # Parse cookies
    cookie_pairs = cleaned.split(';')
    valid_cookies = 0
    for pair in cookie_pairs:
        if '=' in pair:
            valid_cookies += 1
    
    print(f"\n3. Valid cookie pairs found: {valid_cookies}")
    
    if valid_cookies > 0:
        print("   ✅ Cookies parsed successfully")
        return True
    else:
        print("   ❌ No valid cookies found")
        return False

async def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("PERSISTENT BROWSER & COOKIE FIX TESTS")
    print("="*60)
    
    results = []
    
    # Test cookie parsing first
    results.append(await test_cookie_parsing())
    
    # Test Naukri persistent browser
    results.append(await test_naukri_persistent())
    
    # Test LinkedIn persistent browser
    # results.append(await test_linkedin_persistent())
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    passed = sum(results)
    total = len(results)
    print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        print("✅ All tests passed!")
    else:
        print("⚠️  Some tests failed")
    
    print("\n⚠️  Browser windows left open for inspection")
    print("   Close them manually when done\n")

if __name__ == "__main__":
    asyncio.run(main())
