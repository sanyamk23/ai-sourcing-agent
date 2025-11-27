#!/usr/bin/env python3
"""
Setup LinkedIn Cookies - Login once and save session
Run this script to setup your LinkedIn profile for scraping
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.browser_profile_manager import setup_linkedin_profile

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║          LinkedIn Cookie Setup                               ║
║          Save your LinkedIn session for scraping             ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    setup_linkedin_profile()
