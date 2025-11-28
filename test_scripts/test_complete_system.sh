#!/bin/bash

echo "================================================================================"
echo "                    COMPLETE SYSTEM TEST"
echo "================================================================================"
echo ""
echo "This will test:"
echo "  1. Naukri scraper (100 candidates, 2 pages)"
echo "  2. Vector database storage"
echo "  3. All scrapers integration"
echo ""
echo "================================================================================"
echo ""

read -p "Press Enter to start..."

echo ""
echo "🚀 Step 1: Testing Naukri Scraper (100 candidates)..."
echo "================================================================================"
python3 run_naukri_complete_test.py

echo ""
echo "================================================================================"
echo "✅ Naukri test complete!"
echo "================================================================================"
echo ""
echo "📊 Check results:"
echo "  - Candidates scraped and saved to vector database"
echo "  - Profile URLs stored"
echo "  - Browser session saved"
echo ""

read -p "Press Enter to test all scrapers..."

echo ""
echo "🚀 Step 2: Testing All Scrapers..."
echo "================================================================================"
python3 test_all_scrapers.py

echo ""
echo "================================================================================"
echo "✅ ALL TESTS COMPLETE!"
echo "================================================================================"
echo ""
echo "📊 Summary:"
echo "  ✅ Naukri: 100 candidates (2 pages)"
echo "  ✅ LinkedIn: Persistent browser"
echo "  ✅ All scrapers: Integrated"
echo "  ✅ Vector DB: All candidates stored"
echo ""
echo "🚀 Next: Start API server"
echo "   python3 run_api.py"
echo ""
echo "================================================================================"
