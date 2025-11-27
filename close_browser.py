#!/usr/bin/env python3
"""
Utility script to manually close the persistent LinkedIn browser session.
Run this when you want to close the browser window.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.scrapers import LinkedInScraper

if __name__ == "__main__":
    print("Closing LinkedIn browser session...")
    LinkedInScraper.close_browser()
    print("Done!")
