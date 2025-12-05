#!/usr/bin/env python3
"""
=============================================================================
APEX WHY ME ENGINE - Personalized Value Proposition Generator
=============================================================================
Location: apps/backend/intelligence/why_me/why_me_engine.py

Generates personalized outreach content:
- Hook: One compelling sentence connecting MY expertise to THEIR situation
- Proof Points: Relevant credentials for this specific contact
- Why Now: Timing justification
- Suggested Opening: Ready-to-use first message
- Talking Points: Conversation starters
- Objection Handlers: Pre-loaded responses

Usage:
    from apps.backend.intelligence.why_me.why_me_engine import WhyMeEngine
    
    engine = WhyMeEngine(user_id='default')
    result = engine.generate(contact, enrichment_text)
=============================================================================
"""

import json
import os
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional
from openai import OpenAI

DATABASE = os.getenv('DATABASE_URL', '/Users/chrisrabenold/projects/apex/apex.db')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


class WhyMeEngine:
    """
    Generate personalized "Why Me" content for each contact.
    """
    
    def __init__(self, user_id: str = 'default'):
        self.user_id = user_id
        self.user_profile = self._load_user_profile()
        self.proof_points = self._load_proof_points()
    
    def _load_user_profile(self) -> Dict:
        """Load user profile from database."""
        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM user_profile WHERE user_id = ?', (self.user_id,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return dict(row)
        except:
            pass
        
        return {
            'role': 'Commercial Lender',
            'company': '',
            'products_services': '["Bridge Loans", "Permanent Financing", "SBA Loans"]',
            'differentiators': 'Fast execution, direct lender relationships',
            'specialization': 'CRE financing',
        }
    
    def _load_proof_points(self) -> Dict:
        """Load proof points from database."""
        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM proof_points WHERE user_id = ?', (self.user_id,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return dict(row)
        except:
            pass
        
        return {
            'deals_closed_12mo': 0,
            'total_volume_12mo': 0,
            'avg_close_days': 0,
            'notable_deals': '[]',
        }
    
    def generate(self, contact: Dict, enrichment: str = '') -> Dict:
        """
        Generate "Why Me" content for a contact.
        """
        if not client:
            return self._generate_fallback(contact, enrichment)
        
        name = contact.get('name') or f"{contact.get('first_name', '')} {contact.get('last_name', '')}".strip()
        title = contact.get('title', '')
        company = contact.get('company', '')
        
        # Build user context
        products = self.user_profile.get('products_services', '[]')
        if isinstance(products, str):
            products = json.loads(products)
        
        notable = self.proof_points.get('notable_deals', '[]')
        if isinstance(notable, str):
            notable = json.loads(notable)
        
        prompt = f"""You are a sales intelligence AI helping craft personalized outreach.

USER PROFILE (the person reaching out):
- Role: {self.user_profile.get('role', 'Commercial Lender')}
- Company: {self.user_profile.get('company', '')}
- Products/Services: {', '.join(products) if products else 'Commercial Real Estate Financing'}
- Differentiators: {self.user_profile.get('differentiators', 'Fast execution, strong lender relationships')}
- Specialization: {self.user_profile.get('specialization', 'CRE Financing')}

USER'S PROOF POINTS:
- Deals closed (12 months): {self.proof_points.get('deals_closed_12mo', 'N/A')}
- Total volume: ${self.proof_points.get('total_volume_12mo', 0)}M
- Average close time: {self.proof_points.get('avg_close_days', 'N/A')} days
- Notable deals: {json.dumps(notable[:3]) if notable else 'N/A'}

TARGET CONTACT:
- Name: {name}
- Title: {title}
- Company: {company}

ENRICHMENT DATA ABOUT TARGET:
{enrichment[:6000] if enrichment else 'No enrichment data available.'}

Generate personalized outreach content. Return JSON with these keys:

1. "hook" - One compelling sentence (under 30 words) connecting the user's expertise to this contact's specific situation. Reference something specific about them.

2. "proof_points" - Array of 2-3 proof points from the user's track record that are RELEVANT to this contact's likely needs.

3. "why_now" - 2-3 sentences explaining why NOW is the right time to reach out (reference timing signals, news, budget cycles, market conditions).

4. "suggested_opening" - A complete first message (under 60 words) ready to send via email or LinkedIn. Personal, specific, with a clear ask.

5. "talking_points" - Array of 3-4 conversation topics that would resonate based on their role and company.

6. "objection_handlers" - Array of 2-3 common objections this person might have and how to address them.

7. "rapport_builders" - Array of 2-3 personal connection opportunities (alma mater, background, interests) if any are mentioned.

8. "best_channel" - Recommended outreach channel ("email", "linkedin", "phone", "referral") with brief reasoning.

Return ONLY valid JSON, no markdown formatting."""

        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are an expert sales strategist. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.4,
                max_tokens=2000
            )
            
            result = json.loads(response.choices[0].message.content)
            result['generated_at'] = datetime.now().isoformat()
            result['contact_id'] = contact.get('id')
            result['user_id'] = self.user_id
            
            return result
            
        except Exception as e:
            print(f"Why Me generation error: {e}")
            return self._generate_fallback(contact, enrichment)
    
    def _generate_fallback(self, contact: Dict, enrichment: str) -> Dict:
        """Fallback when GPT is unavailable."""
        name = contact.get('name', 'there')
        title = contact.get('title', '')
        company = contact.get('company', '')
        
        return {
            'hook': f"I specialize in helping {title}s like yourself navigate complex financing needs.",
            'proof_points': [
                "Extensive experience in commercial real estate financing",
                "Strong relationships with multiple lending sources",
                "Track record of fast closings"
            ],
            'why_now': "Market conditions are creating unique opportunities for well-positioned borrowers.",
            'suggested_opening': f"Hi {name.split()[0] if name else 'there'}, I noticed your work at {company}. Would love to share how we've helped similar firms—worth a quick call?",
            'talking_points': [
                f"Current market conditions affecting {company}",
                "Recent trends in their sector",
                "Financing strategies for growth"
            ],
            'objection_handlers': [
                {"objection": "We have existing banking relationships", "response": "Great—we often complement existing relationships for specialized needs."},
                {"objection": "Not looking right now", "response": "Understood. When deals do come up, what's typically your timeline?"}
            ],
            'rapport_builders': [],
            'best_channel': 'email',
            'generated_at': datetime.now().isoformat(),
            'fallback': True
        }
    
    def save_to_db(self, contact_id: int, why_me_data: Dict) -> bool:
        """Save Why Me data to contact_match table."""
        try:
            conn = get_db()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO contact_match 
                (contact_id, user_id, hook, proof_points_matched, why_now, 
                 suggested_opening, talking_points, objection_handlers, generated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                contact_id,
                self.user_id,
                why_me_data.get('hook', ''),
                json.dumps(why_me_data.get('proof_points', [])),
                why_me_data.get('why_now', ''),
                why_me_data.get('suggested_opening', ''),
                json.dumps(why_me_data.get('talking_points', [])),
                json.dumps(why_me_data.get('objection_handlers', [])),
                datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error saving Why Me data: {e}")
            return False


# =============================================================================
# CONVENIENCE FUNCTION
# =============================================================================

def generate_why_me(contact: Dict, enrichment: str = '', user_id: str = 'default') -> Dict:
    """Convenience function to generate Why Me content."""
    engine = WhyMeEngine(user_id)
    return engine.generate(contact, enrichment)


# =============================================================================
# CLI TEST
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("APEX WHY ME ENGINE")
    print("=" * 60)
    
    engine = WhyMeEngine()
    
    test_contact = {
        'id': 1,
        'name': 'Greg Richter',
        'title': 'CEO',
        'company': 'Medalist Partners',
    }
    
    test_enrichment = """
    Greg Richter is CEO of Medalist Partners, a $2B alternative credit fund.
    They focus on bridge lending and value-add multifamily acquisitions.
    Recently announced expansion into senior housing sector.
    Greg previously worked at Prudential and Credit Suisse.
    Stanford MBA graduate.
    """
    
    result = engine.generate(test_contact, test_enrichment)
    print(json.dumps(result, indent=2))
