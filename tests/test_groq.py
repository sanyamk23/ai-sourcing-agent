#!/usr/bin/env python3
"""Quick test to verify Groq API is working"""

import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

def test_groq():
    """Test Groq API connection"""
    
    groq_key = os.getenv('GROQ_API_KEY')
    
    if not groq_key:
        print("❌ GROQ_API_KEY not found in .env file")
        print("\nTo fix:")
        print("1. Go to https://console.groq.com")
        print("2. Sign up (free, no credit card)")
        print("3. Create API key")
        print("4. Add to .env file: GROQ_API_KEY=gsk_...")
        return False
    
    print(f"✓ Found GROQ_API_KEY: {groq_key[:20]}...")
    
    try:
        print("\nTesting Groq API connection...")
        client = Groq(api_key=groq_key)
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "user", "content": "Say 'Hello from Groq!' in one sentence"}
            ],
            max_tokens=50
        )
        
        result = response.choices[0].message.content
        print(f"✓ Groq API working!")
        print(f"Response: {result}")
        
        print("\n✅ All tests passed! You're ready to use Groq.")
        return True
        
    except Exception as e:
        print(f"❌ Groq API error: {e}")
        return False

if __name__ == "__main__":
    test_groq()
