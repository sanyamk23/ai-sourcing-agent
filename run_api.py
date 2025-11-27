#!/usr/bin/env python3
"""Run the API server from project root"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Now import and run - USING NOSQL VERSION
from src.api_server_nosql import app
import uvicorn

if __name__ == "__main__":
    print("="*80)
    print("AI CANDIDATE SOURCING API SERVER (NoSQL + Vector DB)")
    print("="*80)
    print("\n🚀 Using MongoDB + ChromaDB")
    print("📊 Automatic embedding creation enabled")
    print("🔍 Vector search for existing candidates enabled")
    print("\nStarting server on http://localhost:8000")
    print("API Documentation: http://localhost:8000/docs")
    print("Alternative docs: http://localhost:8000/redoc")
    print("\nPress CTRL+C to stop")
    print("="*80 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
