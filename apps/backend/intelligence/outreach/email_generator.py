#!/usr/bin/env python3
"""
=============================================================================
APEX EMAIL GENERATOR - AI-Powered Email Drafts
=============================================================================
Location: apps/backend/intelligence/outreach/email_generator.py

Generates personalized email drafts using:
- Contact enrichment data
- Why Me content
- User profile & proof points

Usage:
    from apps.backend.intelligence.outreach.email_generator import EmailGenerator
    
    generator = EmailGenerator(user_id='default')
    result = generator.generate_email(contact, enrichment, why_me_data, template='intro')
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


class EmailGenerator:
    """Generate personalized email drafts."""
    
    TEMPLATES = {
        'intro': {
            'name': 'Introduction',
            'description': 'First outreach to a new contact',
            'tone': 'professional, warm, concise',
            'goal': 'Get a meeting or call scheduled',
        },
        'follow_up': {
            'name': 'Follow Up',
            'description': 'Following up after no response',
            'tone': 'friendly, persistent but not pushy',
            'goal': 'Re-engage and get a response',
        },
        'value_add': {
            'name': 'Value Add',
            'description': 'Share something valuable without asking',
            'tone': 'helpful, knowledgeable, generous',
            'goal': 'Build relationship by providing value',
        },
        'meeting_request': {
            'name': 'Meeting Request',
            'description': 'Direct ask for a meeting',
            'tone': 'confident, specific, respectful of time',
            'goal': 'Get a specific meeting time confirmed',
        },
        'referral': {
            'name': 'Referral Introduction',
            'description': 'Reaching out via mutual connection',
            'tone': 'warm, credible, personal',
            'goal': 'Leverage relationship for warm intro',
        },
    }
    
    def __init__(self, user_id: str = 'default'):
        self.user_id = user_id
        self.user_profile = self._load_user_profile()
        self.proof_points = self._load_proof_points()
    
    def _load_user_profile(self) -> Dict:
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
        return {'full_name': '', 'role': '', 'company': '', 'differentiators': ''}
    
    def _load_proof_points(self) -> Dict:
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
        return {}
    
    def generate_email(
        self, 
        contact: Dict, 
        enrichment: str = '', 
        why_me_data: Dict = None,
        template: str = 'intro',
        custom_context: str = ''
    ) -> Dict:
        """Generate a personalized email draft."""
        
        if not client:
            return self._generate_fallback(contact, template)
        
        template_info = self.TEMPLATES.get(template, self.TEMPLATES['intro'])
        
        name = contact.get('name') or f"{contact.get('first_name', '')} {contact.get('last_name', '')}".strip()
        first_name = name.split()[0] if name else 'there'
        
        # Build context from why_me if available
        hook = why_me_data.get('hook', '') if why_me_data else ''
        proof_points = why_me_data.get('proof_points', []) if why_me_data else []
        why_now = why_me_data.get('why_now', '') if why_me_data else ''
        
        prompt = f"""You are an expert sales copywriter crafting a personalized email.

SENDER PROFILE:
- Name: {self.user_profile.get('full_name', 'Sales Professional')}
- Role: {self.user_profile.get('role', '')}
- Company: {self.user_profile.get('company', '')}
- Differentiators: {self.user_profile.get('differentiators', '')}

RECIPIENT:
- Name: {name}
- Title: {contact.get('title', '')}
- Company: {contact.get('company', '')}

ENRICHMENT DATA (about recipient):
{enrichment[:3000] if enrichment else 'No enrichment data available.'}

PERSONALIZATION HOOKS:
- Hook: {hook}
- Proof Points: {json.dumps(proof_points[:3])}
- Why Now: {why_now}

EMAIL TEMPLATE: {template_info['name']}
- Description: {template_info['description']}
- Tone: {template_info['tone']}
- Goal: {template_info['goal']}

{f'ADDITIONAL CONTEXT: {custom_context}' if custom_context else ''}

Generate a personalized email with:
1. Subject line (compelling, specific, under 50 characters)
2. Email body (3-5 short paragraphs max)
3. Clear call-to-action

Rules:
- Use first name only in greeting
- Reference something specific about them or their company
- Keep it under 150 words
- Sound human, not templated
- No generic phrases like "I hope this email finds you well"
- Include a specific, easy ask

Return JSON with keys: subject, body, cta_type (meeting/reply/call)"""

        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Expert sales email copywriter. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.7,
                max_tokens=1000
            )
            
            result = json.loads(response.choices[0].message.content)
            result['template'] = template
            result['generated_at'] = datetime.now().isoformat()
            result['contact_id'] = contact.get('id')
            
            return result
            
        except Exception as e:
            print(f"Email generation error: {e}")
            return self._generate_fallback(contact, template)
    
    def _generate_fallback(self, contact: Dict, template: str) -> Dict:
        name = contact.get('name') or f"{contact.get('first_name', '')} {contact.get('last_name', '')}".strip()
        first_name = name.split()[0] if name else 'there'
        company = contact.get('company', 'your company')
        
        return {
            'subject': f"Quick question about {company}",
            'body': f"""Hi {first_name},

I came across {company} and wanted to reach out directly.

I work with companies like yours on [specific solution]. Would love to learn more about your current approach and see if there might be a fit.

Do you have 15 minutes this week for a quick call?

Best,
{self.user_profile.get('full_name', 'Your Name')}""",
            'cta_type': 'meeting',
            'template': template,
            'fallback': True,
            'generated_at': datetime.now().isoformat()
        }
    
    def generate_sequence(self, contact: Dict, enrichment: str = '', why_me_data: Dict = None) -> List[Dict]:
        """Generate a 3-email sequence."""
        sequence = []
        
        # Email 1: Introduction
        email1 = self.generate_email(contact, enrichment, why_me_data, 'intro')
        email1['sequence_position'] = 1
        email1['send_delay_days'] = 0
        sequence.append(email1)
        
        # Email 2: Follow up (day 3)
        email2 = self.generate_email(contact, enrichment, why_me_data, 'follow_up')
        email2['sequence_position'] = 2
        email2['send_delay_days'] = 3
        sequence.append(email2)
        
        # Email 3: Value add (day 7)
        email3 = self.generate_email(contact, enrichment, why_me_data, 'value_add')
        email3['sequence_position'] = 3
        email3['send_delay_days'] = 7
        sequence.append(email3)
        
        return sequence


# Convenience function
def generate_email(contact: Dict, enrichment: str = '', why_me_data: Dict = None, 
                   template: str = 'intro', user_id: str = 'default') -> Dict:
    generator = EmailGenerator(user_id)
    return generator.generate_email(contact, enrichment, why_me_data, template)


if __name__ == "__main__":
    gen = EmailGenerator()
    test_contact = {
        'name': 'Greg Richter',
        'title': 'CEO',
        'company': 'Medalist Partners'
    }
    result = gen.generate_email(test_contact, template='intro')
    print(json.dumps(result, indent=2))
