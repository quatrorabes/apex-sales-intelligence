#!/usr/bin/env python3
"""
Test Perplexity API connection
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('PERPLEXITY_API_KEY')

if not api_key:
    print("❌ PERPLEXITY_API_KEY not found in .env")
    exit(1)

print(f"✓ API Key found: {api_key[:20]}...")

# Test simple request
url = "https://api.perplexity.ai/chat/completions"

payload = {
    "model": "sonar-pro",  # CORRECT MODEL NAME
    "messages": [
        {
            "role": "system",
            "content": "You are a helpful assistant."
        },
        {
            "role": "user",
            "content": "Say hello in exactly 5 words."
        }
    ],
    "max_tokens": 50
}

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

print("\n🔍 Testing Perplexity API with sonar-pro model...")

try:
    response = requests.post(url, json=payload, headers=headers, timeout=30)
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        message = result['choices'][0]['message']['content']
        print(f"\n✅ API Working!")
        print(f"Response: {message}")
    else:
        print(f"\n❌ API Error")
        print(f"Status: {response.status_code}")
        print(f"Body: {response.text}")
        
except requests.exceptions.Timeout:
    print("❌ Request timed out")
except Exception as e:
    print(f"❌ Error: {e}")
