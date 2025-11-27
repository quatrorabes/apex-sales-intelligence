#!/usr/bin/env python3
"""
Value Matching Engine
Matches user's products/services to contact's needs
"""
import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()  # ✅ Add this line

class ValueMatcher:
    def __init__(self):
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment")
        self.client = OpenAI(api_key=api_key)
    
    def match(self, user_prefs, contact_profile):
        """Match user's products to contact's needs"""
        
        # Extract user's offerings
        products = json.loads(user_prefs.get('products', '[]'))
        services = json.loads(user_prefs.get('services', '[]'))
        values = json.loads(user_prefs.get('value_propositions', '[]'))
        targets = json.loads(user_prefs.get('target_customers', '[]'))
        personal = json.loads(user_prefs.get('personal_differentiators', '[]'))
        company = json.loads(user_prefs.get('company_differentiators', '[]'))
        
        # Extract contact's needs
        pain_points = contact_profile.get('pain_points', [])
        profile_text = contact_profile.get('profile_content', '')[:2000]
        
        prompt = f"""You are a sales intelligence AI. Match the seller's offerings to the buyer's needs.

SELLER (User):
Products: {', '.join(products)}
Services: {', '.join(services)}
Value Props: {', '.join(values)}
Target Customers: {', '.join(targets)}
Personal Edge: {', '.join(personal)}
Company Edge: {', '.join(company)}

BUYER (Contact):
Name: {contact_profile.get('firstname')} {contact_profile.get('lastname')}
Title: {contact_profile.get('jobtitle')}
Company: {contact_profile.get('company')}
Pain Points: {', '.join(pain_points) if pain_points else 'Unknown'}
Profile: {profile_text}

OUTPUT (JSON only):
{{
  "best_product": "exact product name from list",
  "best_service": "exact service name from list", 
  "fit_score": 85,
  "reasoning": "2-sentence explanation of why this fits",
  "talking_points": ["point 1", "point 2", "point 3"]
}}
"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a sales matching AI. Return ONLY valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            result = json.loads(response.choices[0].message.content)
            return {
                'success': True,
                'match': result
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

if __name__ == "__main__":
    # Test
    matcher = ValueMatcher()
    print("✅ ValueMatcher initialized")
