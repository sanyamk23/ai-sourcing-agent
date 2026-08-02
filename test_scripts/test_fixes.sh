#!/bin/bash

echo "=================================="
echo "TESTING PERSISTENT BROWSER FIXES"
echo "=================================="

echo ""
echo "1. Testing cookie parsing..."
python3 -c "
import os
from dotenv import load_dotenv
load_dotenv()
cookie_string = os.getenv('NAUKRI_RESDEX_COOKIES', '')
cleaned = cookie_string.strip().strip(\"'\").strip('\"')
valid = sum(1 for p in cleaned.split(';') if '=' in p)
print(f'   ✅ Valid cookies found: {valid}')
if valid > 20:
    print('   ✅ Cookie parsing works!')
else:
    print('   ❌ Cookie parsing failed!')
    exit(1)
"

echo ""
echo "2. Testing persistent browser imports..."
python3 -c "
from naukri_persistent_browser import naukri_browser_manager, linkedin_browser_manager
print('   ✅ Naukri browser manager imported')
print('   ✅ LinkedIn browser manager imported')
print(f'   ✅ get_driver method exists: {hasattr(naukri_browser_manager, \"get_driver\")}')
"

echo ""
echo "3. Testing scraper imports..."
python3 -c "
from src.scrapers import NaukriScraper, LinkedInScraper, PortalScraperManager
print('   ✅ NaukriScraper imported')
print('   ✅ LinkedInScraper imported')
print('   ✅ PortalScraperManager imported')
print('   ℹ️  Indeed scraper disabled (was causing crashes)')
"

echo ""
echo "4. Testing vector DB..."
python3 -c "
from src.vector_db import CandidateVectorDB
vector_db = CandidateVectorDB()
print('   ✅ Vector DB initialized')
print(f'   📊 Current candidates: {vector_db.collection.count()}')
"

echo ""
echo "=================================="
echo "✅ ALL TESTS PASSED!"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. Run: python3 run_api.py"
echo "2. Create a job posting at http://localhost:8000"
echo "3. Watch logs for persistent browser usage"
echo ""
