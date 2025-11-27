#!/usr/bin/env python3
"""Verify that everything is set up correctly"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

def check_env_var(name, required=True):
    """Check if environment variable is set"""
    value = os.getenv(name)
    if value and value != f"your_{name.lower()}":
        print(f"✓ {name}: {value[:20]}..." if len(value) > 20 else f"✓ {name}: {value}")
        return True
    elif required:
        print(f"✗ {name}: NOT SET (required)")
        return False
    else:
        print(f"⚠ {name}: NOT SET (optional)")
        return True

def check_file(path, description):
    """Check if file exists"""
    if Path(path).exists():
        size = Path(path).stat().st_size
        print(f"✓ {description}: {path} ({size} bytes)")
        return True
    else:
        print(f"✗ {description}: {path} NOT FOUND")
        return False

def check_database():
    """Check database connection"""
    try:
        from src.database import SessionLocal, CandidateDB, JobDB
        db = SessionLocal()
        # Try a simple query
        count = db.query(CandidateDB).count()
        db.close()
        print(f"✓ Database connection: Working ({count} candidates)")
        return True
    except Exception as e:
        print(f"✗ Database connection: Failed - {e}")
        return False

def check_groq():
    """Check Groq API connection"""
    try:
        from groq import Groq
        groq_key = os.getenv('GROQ_API_KEY')
        if not groq_key:
            print("✗ Groq API: No API key found")
            return False
        
        client = Groq(api_key=groq_key)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": "Say 'OK'"}],
            max_tokens=10
        )
        print(f"✓ Groq API: Working (response: {response.choices[0].message.content})")
        return True
    except Exception as e:
        print(f"✗ Groq API: Failed - {e}")
        return False

def main():
    print("="*60)
    print("VERIFYING SETUP")
    print("="*60)
    
    all_good = True
    
    print("\n1. Environment Variables:")
    print("-" * 60)
    all_good &= check_env_var("GROQ_API_KEY", required=True)
    all_good &= check_env_var("DATABASE_URL", required=True)
    all_good &= check_env_var("LINKEDIN_USERNAME", required=False)
    all_good &= check_env_var("LINKEDIN_PASSWORD", required=False)
    
    print("\n2. Files:")
    print("-" * 60)
    all_good &= check_file(".env", ".env file")
    all_good &= check_file("config.yaml", "Config file")
    all_good &= check_file("candidates.db", "SQLite database")
    all_good &= check_file("src/agent.py", "Agent module")
    all_good &= check_file("src/scrapers.py", "Scrapers module")
    
    print("\n3. Database:")
    print("-" * 60)
    all_good &= check_database()
    
    print("\n4. Groq API:")
    print("-" * 60)
    all_good &= check_groq()
    
    print("\n" + "="*60)
    if all_good:
        print("✅ ALL CHECKS PASSED! You're ready to go!")
        print("\nNext steps:")
        print("  python test_scrapers.py      # Test scrapers")
        print("  python test_full_pipeline.py # Test full pipeline")
        print("  python src/api_server.py     # Start API server")
    else:
        print("❌ SOME CHECKS FAILED")
        print("\nPlease fix the issues above and run again.")
        print("See SETUP_INSTRUCTIONS.md for help.")
        sys.exit(1)
    print("="*60)

if __name__ == "__main__":
    main()
