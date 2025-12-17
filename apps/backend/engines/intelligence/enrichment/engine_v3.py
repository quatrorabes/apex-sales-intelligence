"""
APEX Enrichment Engine v3.0
Handles None values and missing fields gracefully
"""

import os
import json
import requests
import logging
from datetime import datetime
from typing import Dict, Optional, Any

logger = logging.getLogger(__name__)

class ApexEnrichmentEngineV3:
    def __init__(self):
        self.perplexity_key = os.getenv('PERPLEXITY_API_KEY')
        self.openai_key = os.getenv('OPENAI_API_KEY')
    
    def enrich_contact(self, contact: Dict) -> Dict[str, Any]:
        """Enrich a single contact with proper None handling"""
        try:
            logger.info(f"🚀 Calling APEX v3.0 engine for {contact.get('name', 'Unknown')}")
            
            # Handle None values safely with (value or "").strip()
            name = (contact.get("name") or "").strip()
            company = (contact.get("company") or "").strip()
            title = (contact.get("title") or "").strip()
            email = (contact.get("email") or "").strip()
            linkedin_url = (contact.get("linkedin_url") or "").strip()
            
            if not name:
                return {'status': 'error', 'error': 'Contact name is required'}
            
            logger.info(f"Enriching: {name} at {company or 'Unknown Company'}")
            
            # Stage 1: Gather raw context
            raw_context = self._gather_raw_context(name, company, title, email, linkedin_url)
            
            # Stage 2: Synthesize with GPT-4
            markdown = self._synthesize_to_markdown(name, company, raw_context)
            
            return {
                'status': 'success',
                'markdown': markdown,
                'raw_context': raw_context,
                'enriched_at': datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"❌ Enrichment failed: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def _gather_raw_context(self, name: str, company: str, title: str, email: str, linkedin_url: str) -> Dict[str, str]:
        """Gather 6 raw searches"""
        raw_context = {}
        
        logger.info(f"1/6 Person research for {name}")
        person_prompt = f"Research {name} comprehensively. Title: {title or 'Unknown'}, Company: {company or 'Unknown'}, Email: {email or 'N/A'}, LinkedIn: {linkedin_url or 'Not provided'}. Provide current role, work history (5 years), education, achievements, and career progression."
        raw_context['person'] = self._call_perplexity(person_prompt, 2000)
        
        logger.info(f"2/6 Company research for {company or 'Unknown'}")
        company_prompt = f"Research {company or 'this company'} thoroughly. Provide description, mission, size, products, leadership, recent news (90 days), market position, and growth trajectory."
        raw_context['company'] = self._call_perplexity(company_prompt, 2000)
        
        logger.info(f"3/6 Social media profiles")
        social_prompt = f"Find all social media profiles for {name}. Search for LinkedIn, Twitter, Instagram, Facebook. Provide exact URLs."
        raw_context['social'] = self._call_perplexity(social_prompt, 1500)
        
        logger.info(f"4/6 Recent activity")
        activity_prompt = f"Find recent activity for {name} at {company or 'their company'} (last 90 days). LinkedIn posts, news, speaking engagements, deals, awards."
        raw_context['activity'] = self._call_perplexity(activity_prompt, 2000)
        
        logger.info(f"5/6 Skills and expertise")
        skills_prompt = f"Identify skills for {name}, {title or 'professional'}. Technical, leadership, industry expertise, certifications."
        raw_context['skills'] = self._call_perplexity(skills_prompt, 1500)
        
        logger.info(f"6/6 Fun facts and icebreakers")
        facts_prompt = f"Find interesting info about {name} and {company or 'their company'}. Culture, background, awards, community involvement, alma mater, sports."
        raw_context['fun_facts'] = self._call_perplexity(facts_prompt, 1200)
        
        return raw_context
    
    def _synthesize_to_markdown(self, name: str, company: str, raw_context: Dict) -> str:
        """Synthesize with GPT-4"""
        logger.info(f"🧠 Synthesizing with GPT-4")
        
        compiled = "\n\n".join([f"## {k.upper()}\n{v}" for k, v in raw_context.items() if v])
        
        synthesis_prompt = f"""Synthesize into sales profile for {name} at {company}.

RAW DATA:
{compiled}

OUTPUT AS MARKDOWN - Only real sections:
## Overview
## Background & Experience  
## Education
## Company Context
## Skills & Expertise
## Social Media & Online Presence
## Recent Activity
## Sales Signals & Triggers
## Talking Points
## Recommended Outreach

Be specific. Include dates, numbers, names."""
        
        markdown = self._call_gpt4(synthesis_prompt, 4000)
        logger.info(f"✅ Synthesis done: {len(markdown)} chars")
        return markdown
    
    def _call_perplexity(self, prompt: str, max_tokens: int = 2000) -> str:
        """Call Perplexity API"""
        if not self.perplexity_key:
            return ""
        
        try:
            response = requests.post(
                'https://api.perplexity.ai/chat/completions',
                headers={
                    'Authorization': f'Bearer {self.perplexity_key}',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': 'sonar-pro',
                    'messages': [{'role': 'user', 'content': prompt}],
                    'temperature': 0.2,
                    'max_tokens': max_tokens
                },
                timeout=120
            )
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content']
        except Exception as e:
            logger.error(f"Perplexity error: {e}")
        return ""
    
    def _call_gpt4(self, prompt: str, max_tokens: int = 4000) -> str:
        """Call GPT-4"""
        if not self.openai_key:
            return ""
        
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.openai_key)
            response = client.chat.completions.create(
                model='gpt-4',
                messages=[
                    {'role': 'system', 'content': 'Professional sales intelligence analyst.'},
                    {'role': 'user', 'content': prompt}
                ],
                temperature=0.3,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"GPT-4 error: {e}")
        return ""
