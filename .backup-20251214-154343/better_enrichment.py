#!/usr/bin/env python3
"""
Fixed Better Perplexity Enrichment - Correct API format
"""
import os
import requests
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class BetterPerplexityEnrichment:
    """Enrichment that gets the RIGHT information"""
    
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv('PERPLEXITY_API_KEY')
        if not self.api_key:
            raise ValueError("PERPLEXITY_API_KEY required")
    
    def enrich_contact(self, contact):
        """Enrich using structured questions approach"""
        
        print(f"🔍 Enriching {contact.get('name')} with STRUCTURED approach...")
        
        # Build the research query
        prompt = self.build_structured_prompt(contact)
        
        # Call Perplexity
        result = self.call_perplexity_api(prompt)
        
        # Save profile to file
        if result:
            profile_file = f"profile_{contact.get('id', 'unknown')}.txt"
            with open(profile_file, 'w', encoding='utf-8') as f:
                f.write(result)
            print(f"✅ Saved profile to {profile_file} ({len(result)} chars)")
        
        return {
            'enrichment_data': {
                'full_profile_text': result,
                'perplexity_insights': result,
                'enriched_at': datetime.now().isoformat(),
                'source': 'perplexity_structured',
                'profile_length': len(result) if result else 0
            }
        }
    
    def build_structured_prompt(self, contact):
        """Build a focused research prompt"""
        
        name = contact.get('name', '')
        company = contact.get('company', '')
        title = contact.get('title', '')
        email = contact.get('email', '')
        
        # Shorter, more focused prompt for Perplexity
        prompt = f"""Research {name}, {title} at {company}.

Important: If multiple companies named "{company}" exist, find the one where {name} works as {title}.
Email domain: {email.split('@')[1] if email and '@' in email else 'unknown'}

Provide:
1. Person Profile:
   - Current role and responsibilities
   - Professional background and experience
   - Education and certifications
   - Industry involvement (associations, events)
   - Recent activities or mentions

2. Company Profile:
   - What the company actually does
   - Industry and market position
   - Size and locations
   - Recent news or developments

3. Business Context:
   - How their role relates to commercial real estate
   - Potential business needs or opportunities
   - Key relationships or partnerships

Focus on verified, current information from LinkedIn and business sources."""
        
        return prompt
    
    def call_perplexity_api(self, prompt):
        """Make the actual API call to Perplexity - FIXED FORMAT"""
        
        url = "https://api.perplexity.ai/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # CORRECTED payload format
        payload = {
            "model": "sonar-pro",  # Use a valid model
            "model": "sonar-pro",  # Use a valid model
            "messages": [
                {
                    "role": "user",  # Just user, no system message
                    "content": prompt
                }
            ],
            "temperature": 0.2,
            "top_p": 0.9
            # Removed invalid parameters
        }
        
        try:
            print("📡 Calling Perplexity API...")
            response = requests.post(url, json=payload, headers=headers)
            
            # Debug the response
            print(f"Status Code: {response.status_code}")
            
            if response.status_code != 200:
                print(f"Error Response: {response.text}")
                
                # Try a simpler request
                simple_payload = {
                    "model": "llama-3.1-sonar-small-128k-online",
                    "messages": [{"role": "user", "content": prompt[:1000]}]  # Shorter prompt
                }
                
                print("Trying simpler request...")
                response = requests.post(url, json=simple_payload, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                content = data['choices'][0]['message']['content']
                print(f"✅ Got response: {len(content)} characters")
                return content
            else:
                print(f"❌ API Error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Request error: {e}")
            return None

# Simpler test function
def test_perplexity_connection():
    """Test if Perplexity API is working at all"""
    
    api_key = os.getenv('PERPLEXITY_API_KEY')
    if not api_key:
        print("❌ No PERPLEXITY_API_KEY in environment")
        return
    
    print(f"✅ Found API key: {api_key[:20]}...")
    
    # Super simple test
    url = "https://api.perplexity.ai/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Minimal payload
    payload = {
        "model": "sonar-pro",
        "messages": [
            {
                "role": "user",
                "content": "What is 2+2?"
            }
        ]
    }
    
    print("Testing basic API call...")
    response = requests.post(url, json=payload, headers=headers)
    
    print(f"Response Status: {response.status_code}")
    if response.status_code == 200:
        print("✅ API is working!")
        data = response.json()
        print(f"Response: {data['choices'][0]['message']['content']}")
    else:
        print(f"❌ API error: {response.text}")

# Test function for Andy
def test_andy():
    """Test with Andy"""
    
    # First test basic connectivity
    print("=" * 60)
    print("Testing Perplexity API Connection...")
    print("=" * 60)
    test_perplexity_connection()
    
    print("\n" + "=" * 60)
    print("Testing Andy Enrichment...")
    print("=" * 60)
    
    contact = {
        'id': 48,
        'name': 'Andy Bratt',
        'title': 'Principal',
        'company': 'Gantry',
        'email': 'abratt@gantryinc.com',
        'phone': '+1 949-356-6678'
    }
    
    try:
        enricher = BetterPerplexityEnrichment()
        result = enricher.enrich_contact(contact)
        
        if result and result['enrichment_data']['full_profile_text']:
            profile = result['enrichment_data']['full_profile_text']
            
            # Check if we got the RIGHT Gantry
            if 'mortgage' in profile.lower() or 'real estate' in profile.lower():
                print("✅ SUCCESS! Found the CORRECT Gantry (mortgage banking)")
            elif 'artificial intelligence' in profile.lower() or 'AI' in profile:
                print("❌ FAILED! Got the wrong Gantry (AI company)")
            else:
                print("🤔 UNCLEAR - Check the profile")
            
            print(f"\nFirst 500 chars of profile:")
            print(profile[:500])
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_andy()
