#!/usr/bin/env python3
"""
APEX LINKEDIN MESSAGE GENERATOR
"""

import json
import os
from datetime import datetime
from typing import Dict
from openai import OpenAI

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None


class LinkedInGenerator:
    """Generate LinkedIn connection requests and InMails."""
    
    TEMPLATES = {
        'connection': {
            'name': 'Connection Request',
            'max_chars': 300,
            'description': 'Brief note with connection request',
        },
        'inmail_intro': {
            'name': 'InMail Introduction',
            'max_chars': 1900,
            'description': 'Longer form InMail for cold outreach',
        },
        'inmail_followup': {
            'name': 'InMail Follow-up',
            'max_chars': 1900,
            'description': 'Follow up to previous outreach',
        },
        'mutual_connection': {
            'name': 'Mutual Connection',
            'max_chars': 300,
            'description': 'Leverage shared connections',
        },
        'content_engagement': {
            'name': 'Content Engagement',
            'max_chars': 300,
            'description': 'Reference their post or content',
        },
    }
    
    def __init__(self, user_id: str = 'default'):
        self.user_id = user_id
    
    def generate(self, contact: Dict, enrichment: str = '', why_me_data: Dict = None,
                 template: str = 'connection', custom_context: str = '') -> Dict:
        """Generate LinkedIn message."""
        
        if not client:
            return self._fallback(contact, template)
        
        template_info = self.TEMPLATES.get(template, self.TEMPLATES['connection'])
        max_chars = template_info['max_chars']
        
        name = contact.get('name') or f"{contact.get('first_name', '')} {contact.get('last_name', '')}".strip()
        first_name = name.split()[0] if name else 'there'
        
        hook = why_me_data.get('hook', '') if why_me_data else ''
        
        prompt = f"""Generate a LinkedIn {template_info['name']} message.

RECIPIENT:
- Name: {name} (use first name: {first_name})
- Title: {contact.get('title', '')}
- Company: {contact.get('company', '')}

CONTEXT FROM RESEARCH:
{enrichment[:2000] if enrichment else 'No additional context.'}

PERSONALIZATION HOOK: {hook}
ADDITIONAL CONTEXT: {custom_context}

REQUIREMENTS:
- Maximum {max_chars} characters (STRICT - LinkedIn enforces this)
- Sound human and personal, not templated
- Reference something specific about them
- Clear but soft call-to-action
- No generic phrases like "I came across your profile"
- Professional but warm tone

Return JSON with: message, character_count, cta_type"""

        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": f"LinkedIn messaging expert. Keep under {max_chars} chars. Return JSON only."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.7,
                max_tokens=500
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Enforce character limit
            if len(result.get('message', '')) > max_chars:
                result['message'] = result['message'][:max_chars-3] + '...'
            
            result['template'] = template
            result['character_count'] = len(result.get('message', ''))
            result['max_chars'] = max_chars
            result['generated_at'] = datetime.now().isoformat()
            
            return result
            
        except Exception as e:
            print(f"LinkedIn generation error: {e}")
            return self._fallback(contact, template)
    
    def _fallback(self, contact: Dict, template: str) -> Dict:
        name = contact.get('name', '').split()[0] or 'there'
        company = contact.get('company', 'your company')
        
        msg = f"Hi {name}, I noticed your work at {company} and would love to connect. Always great to meet others in the industry."
        
        return {
            'message': msg,
            'character_count': len(msg),
            'max_chars': 300,
            'template': template,
            'fallback': True,
            'generated_at': datetime.now().isoformat()
        }


def generate_linkedin(contact: Dict, enrichment: str = '', template: str = 'connection') -> Dict:
    gen = LinkedInGenerator()
    return gen.generate(contact, enrichment, template=template)
