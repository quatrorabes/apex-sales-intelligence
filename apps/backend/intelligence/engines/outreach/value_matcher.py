#!/usr/bin/env python3
"""
Value Matcher - AI-Powered Product-to-Pain Matching
Analyzes enrichment data to match user's products/services to contact needs
"""

import json
import sqlite3
import os
import sys
from openai import OpenAI
from datetime import datetime

# Add generators to path for whyme_helper
GENERATORS_PATH = os.path.join(os.path.dirname(__file__), 'generators')
sys.path.insert(0, GENERATORS_PATH)

from whyme_helper import get_user_preferences

class ValueMatcher:
    """Matches user's Why Me? offerings to contact pain points"""
    
    def __init__(self, db_path=None):
        self.db_path = db_path or '/Users/chrisrabenold/projects/apex/apex.db'
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    def match(self, contact):
        """Match best product to contact's needs using AI"""
        
        # Get user preferences
        prefs = get_user_preferences()
        if not prefs or not prefs['products']:
            return {
                'success': False,
                'error': 'No products defined in Why Me? tab'
            }
        
        # Extract profile sections
        profile = contact.get('profile_content', '')
        
        if not profile:
            return {
                'success': False,
                'error': 'Contact not enriched yet'
            }
        
        # Extract relevant sections
        pain_points = self._extract_section(profile, '9. Pain Points')
        product_fit = self._extract_section(profile, '10. Product Fit')
        
        # Build matching prompt
        prompt = f"""
You are an AI sales intelligence analyst. Analyze this contact and match them to the best offering.

YOUR OFFERINGS:
Products: {', '.join(prefs['products'])}
Services: {', '.join(prefs['services'])}
Value Propositions: {'. '.join(prefs['value_propositions'])}

CONTACT PROFILE:
Name: {contact.get('name')}
Title: {contact.get('title')}
Company: {contact.get('company')}

THEIR PAIN POINTS:
{pain_points[:1000] if pain_points else 'Not available'}

EXISTING PRODUCT FIT ANALYSIS:
{product_fit[:1000] if product_fit else 'Not available'}

TASK:
1. Select the #1 BEST product/service that fits this contact's needs
2. Explain WHY in 2-3 sentences (reference their specific pain points)
3. Suggest the best outreach angle (what to emphasize)

Return ONLY valid JSON:
{{
  "best_product": "exact product name from YOUR OFFERINGS list",
  "reasoning": "2-3 sentence explanation referencing their pain points",
  "suggested_angle": "what to emphasize in outreach",
  "confidence": "HIGH/MEDIUM/LOW"
}}
"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a sales intelligence analyst. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Save to database
            conn = sqlite3.connect(self.db_path)
            conn.execute("""
                UPDATE contacts 
                SET product_match = ?,
                    match_reasoning = ?,
                    suggested_angle = ?,
                    match_confidence = ?,
                    matched_at = ?
                WHERE id = ?
            """, (
                result.get('best_product', ''),
                result.get('reasoning', ''),
                result.get('suggested_angle', ''),
                result.get('confidence', 'MEDIUM'),
                datetime.now().isoformat(),
                contact['id']
            ))
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'match': result
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': f'Matching failed: {str(e)}'
            }
    
    def _extract_section(self, profile, section_title):
        """Extract specific section from enrichment profile"""
        if section_title not in profile:
            return None
        
        # Find section
        start = profile.find(section_title)
        if start == -1:
            return None
        
        # Find next section (starts with number followed by period)
        next_section = start + len(section_title)
        for i in range(next_section, len(profile) - 3):
            if profile[i].isdigit() and profile[i+1] == '.' and profile[i+2] == ' ':
                return profile[start:i].strip()
        
        # If no next section found, return to end
        return profile[start:].strip()

if __name__ == '__main__':
    # Test
    if len(sys.argv) < 2:
        print("Usage: python value_matcher.py <contact_id>")
        sys.exit(1)
    
    contact_id = int(sys.argv[1])
    
    conn = sqlite3.connect('/Users/chrisrabenold/projects/apex/apex.db')
    conn.row_factory = sqlite3.Row
    contact = dict(conn.execute("SELECT * FROM contacts WHERE id = ?", (contact_id,)).fetchone())
    conn.close()
    
    matcher = ValueMatcher()
    result = matcher.match(contact)
    
    if result['success']:
        print("✅ Match Found!")
        print(f"Best Product: {result['match']['best_product']}")
        print(f"Reasoning: {result['match']['reasoning']}")
        print(f"Angle: {result['match']['suggested_angle']}")
    else:
        print(f"❌ Error: {result['error']}")
