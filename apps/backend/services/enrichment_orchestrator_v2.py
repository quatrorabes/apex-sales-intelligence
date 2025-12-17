"""
APEX Enrichment Orchestrator v2
Open-ended Perplexity + GPT-4 Semi-Structured Output
For Dashboard_v1 frontend parsing
"""

import os
import json
import requests
import time
import re
import logging
from datetime import datetime
from typing import Dict, Optional, Any

logger = logging.getLogger(__name__)

class ApexEnrichmentOrchestrator:
    """Three-stage enrichment: Perplexity raw → GPT-4 markdown → Frontend parse"""
    
    def __init__(self):
        self.perplexity_key = os.getenv('PERPLEXITY_API_KEY')
        self.openai_key = os.getenv('OPENAI_API_KEY')
        
        if not self.perplexity_key:
            logger.warning("PERPLEXITY_API_KEY not set")
        if not self.openai_key:
            logger.warning("OPENAI_API_KEY not set")
    
    # ============================================================
    # STAGE 1: OPEN-ENDED PERPLEXITY DATA GATHERING
    # ============================================================
    
    def gather_raw_context(self, contact: Dict) -> Dict[str, str]:
        """
        Gather raw context from 6 parallel Perplexity searches
        NO structure - just raw intelligence
        """
        logger.info("🔍 STAGE 1: Gathering raw context from Perplexity...")
        
        name = contact.get('name', 'Unknown')
        company = contact.get('company', 'Unknown')
        linkedin = contact.get('linkedin_url', '')
        title = contact.get('title', '')
        email = contact.get('email', '')
        
        raw_context = {}
        
        # Search 1: Person Profile
        logger.info(f"1/6 Researching person: {name}")
        raw_context['person'] = self._search_person(name, title, company, linkedin)
        time.sleep(1)
        
        # Search 2: Company Intelligence
        logger.info(f"2/6 Researching company: {company}")
        raw_context['company'] = self._search_company(company)
        time.sleep(1)
        
        # Search 3: Social Media
        logger.info(f"3/6 Finding social media profiles")
        raw_context['social'] = self._search_social_media(name)
        time.sleep(1)
        
        # Search 4: Recent Activity
        logger.info(f"4/6 Finding recent activity and news")
        raw_context['activity'] = self._search_activity(name, company)
        time.sleep(1)
        
        # Search 5: Skills & Expertise
        logger.info(f"5/6 Researching skills and expertise")
        raw_context['skills'] = self._search_skills(name, title)
        time.sleep(1)
        
        # Search 6: Fun Facts & Icebreakers
        logger.info(f"6/6 Finding fun facts and icebreakers")
        raw_context['fun_facts'] = self._search_fun_facts(name, company)
        
        logger.info(f"✅ STAGE 1 COMPLETE: Gathered {len(raw_context)} context sections")
        return raw_context
    
    def _search_person(self, name: str, title: str, company: str, linkedin: str) -> str:
        """Open-ended person profile search"""
        prompt = f"""Research {name} comprehensively.
        
Title: {title}
Company: {company}
LinkedIn: {linkedin if linkedin else 'Not provided'}

Provide:
- Current role, scope, responsibilities
- Complete work history (last 5 roles)
- Education and certifications
- Notable achievements
- Tenure at current company
- Career progression

Be specific with dates and details. Use sources like LinkedIn, company website, news."""
        
        return self._call_perplexity(prompt, max_tokens=2000)
    
    def _search_company(self, company: str) -> str:
        """Open-ended company intelligence search"""
        prompt = f"""Research {company} thoroughly.

Provide:
- Company description, mission, founding date
- Headquarters and size (employees, revenue)
- Key products/services and markets
- Leadership team (CEO, key executives)
- Recent news, funding, acquisitions (last 90 days)
- Market position and top competitors
- Growth trajectory and strategic direction

Focus on current, factual information with dates and numbers."""
        
        return self._call_perplexity(prompt, max_tokens=2000)
    
    def _search_social_media(self, name: str) -> str:
        """Open-ended social media discovery"""
        prompt = f"""Find all social media profiles for {name}.

Search for:
- LinkedIn profile URL
- Twitter/X handle and bio
- Instagram username
- Facebook profile
- Any other public profiles (TikTok, YouTube, Medium, GitHub, blog)

For each found, provide:
- Exact URL or handle
- Activity level (active/inactive)
- Follower count if available
- Bio/description

Format clearly with exact URLs."""
        
        return self._call_perplexity(prompt, max_tokens=1500)
    
    def _search_activity(self, name: str, company: str) -> str:
        """Open-ended recent activity search"""
        prompt = f"""Find recent activity for {name} at {company} (last 90 days).

Search for:
- LinkedIn posts, comments, engagement
- News mentions or press releases
- Speaking engagements or presentations
- Company announcements
- Deal closings or transactions
- Job postings indicating growth
- Awards or recognition

Include dates, sources, and specifics. Focus on sales signals."""
        
        return self._call_perplexity(prompt, max_tokens=2000)
    
    def _search_skills(self, name: str, title: str) -> str:
        """Open-ended skills and expertise search"""
        prompt = f"""Identify skills and expertise for {name}, {title}.

Research:
- Technical skills (tools, technologies, languages)
- Professional/leadership skills
- Industry expertise and specializations
- LinkedIn endorsed skills
- Certifications and credentials
- Demonstrated expertise from projects/publications
- Thought leadership topics

Be specific with context on how these are demonstrated."""
        
        return self._call_perplexity(prompt, max_tokens=1500)
    
    def _search_fun_facts(self, name: str, company: str) -> str:
        """Open-ended fun facts and icebreakers"""
        prompt = f"""Find interesting information about {name} and {company}.

Search for:
- Company fun facts, culture, history
- Unusual company background or story
- Awards or recognition
- Community involvement or charity
- Industry humor or trivia
- Shared interests or hobbies
- Alma mater connections
- Sports team affiliations

Make it relevant for sales conversations. Keep professional."""
        
        return self._call_perplexity(prompt, max_tokens=1200)
    
    # ============================================================
    # STAGE 2: GPT-4 SEMI-STRUCTURED SYNTHESIS
    # ============================================================
    
    def synthesize_to_markdown(self, contact: Dict, raw_context: Dict) -> str:
        """
        Use GPT-4 to synthesize 6 raw chunks into markdown
        NOT fully parsed - that's frontend's job
        Output: Clean markdown with ## headers for each section
        """
        logger.info("🧠 STAGE 2: Synthesizing with GPT-4...")
        
        compiled = self._compile_raw_data(raw_context)
        
        synthesis_prompt = f"""You are a sales intelligence analyst. Synthesize this raw research into a comprehensive profile.

CONTACT: {contact.get('name')} at {contact.get('company')}

RAW RESEARCH:
{compiled}

OUTPUT AS MARKDOWN WITH THESE SECTIONS (only include sections with real data):

## Overview
- Current role, title, company
- Tenure and scope
- Key facts about the person

## Background & Experience
- Work history (last 5 positions)
- Career progression
- Notable achievements

## Education
- Degrees and institutions
- Certifications or training

## Current Role & Responsibilities
- Day-to-day focus
- Key objectives
- Team scope if applicable

## Company Context
- Company description
- Mission and markets
- Recent news or updates
- Market position

## Leadership & Culture
- Company leadership team
- Cultural attributes
- Growth stage

## Skills & Expertise
- Top 5-7 professional skills
- Technical competencies
- Industry expertise
- Endorsed skills from LinkedIn

## Social Media & Online Presence
- LinkedIn profile (if found)
- Twitter/X presence
- Instagram or other platforms
- Posting frequency/engagement level

## Recent Activity (Last 90 Days)
- LinkedIn posts or activity
- Company announcements
- Deal activity
- Speaking engagements
- Press mentions

## Sales Signals & Trigger Events
- Signs of growth or expansion
- Recent budget decisions
- Technology adoptions
- Hiring activity
- Deal closing signals

## Talking Points & Hooks
- 3-5 specific conversation starters
- Based on their background, interests, recent activity
- Industry-relevant observations
- Mutual connection opportunities

## Recommended Outreach Approach
- Best contact method (email, LinkedIn, phone)
- Timing (ASAP, this week, etc.)
- Tone and style based on personality
- Key objection handlers

CRITICAL:
- Be specific. Use exact numbers, dates, names.
- Only include sections where you found real data.
- No generic statements like "Limited information available".
- Format with ## headers so it's easy to parse.
- Keep professional but conversational.
"""
        
        markdown = self._call_gpt4(synthesis_prompt, max_tokens=4000)
        logger.info(f"✅ STAGE 2 COMPLETE: Generated {len(markdown)} character markdown")
        return markdown
    
    def _compile_raw_data(self, raw_context: Dict) -> str:
        """Compile 6 raw sections into a single text for GPT"""
        sections = []
        
        if raw_context.get('person'):
            sections.append(f"## PERSON RESEARCH\n{raw_context['person']}")
        if raw_context.get('company'):
            sections.append(f"## COMPANY RESEARCH\n{raw_context['company']}")
        if raw_context.get('social'):
            sections.append(f"## SOCIAL MEDIA\n{raw_context['social']}")
        if raw_context.get('activity'):
            sections.append(f"## RECENT ACTIVITY\n{raw_context['activity']}")
        if raw_context.get('skills'):
            sections.append(f"## SKILLS & EXPERTISE\n{raw_context['skills']}")
        if raw_context.get('fun_facts'):
            sections.append(f"## FUN FACTS\n{raw_context['fun_facts']}")
        
        return "\n\n".join(sections)
    
    # ============================================================
    # API CALLS
    # ============================================================
    
    def _call_perplexity(self, prompt: str, max_tokens: int = 2000) -> str:
        """Call Perplexity with open-ended query"""
        if not self.perplexity_key:
            logger.warning("Perplexity key not available")
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
            else:
                logger.error(f"Perplexity error: {response.status_code}")
                return ""
        except Exception as e:
            logger.error(f"Perplexity API error: {e}")
            return ""
    
    def _call_gpt4(self, prompt: str, max_tokens: int = 4000) -> str:
        """Call GPT-4 for synthesis"""
        if not self.openai_key:
            logger.warning("OpenAI key not available")
            return ""
        
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.openai_key)
            
            response = client.chat.completions.create(
                model='gpt-4',
                messages=[
                    {
                        'role': 'system',
                        'content': 'You are a professional sales intelligence analyst. Synthesize research into actionable profiles.'
                    },
                    {'role': 'user', 'content': prompt}
                ],
                temperature=0.3,
                max_tokens=max_tokens
            )
            
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"GPT-4 API error: {e}")
            return ""
    
    # ============================================================
    # PUBLIC INTERFACE
    # ============================================================
    
    def enrich_contact(self, contact: Dict) -> Dict[str, Any]:
        """
        Full enrichment pipeline
        Returns: {
            'status': 'success',
            'raw_context': {...},  # For debugging
            'markdown': '## Section\nContent...',  # For frontend parsing
            'metadata': {...}
        }
        """
        try:
            logger.info(f"🚀 STARTING ENRICHMENT: {contact.get('name')} at {contact.get('company')}")
            
            # Stage 1
            raw_context = self.gather_raw_context(contact)
            
            # Stage 2
            markdown = self.synthesize_to_markdown(contact, raw_context)
            
            logger.info("✅ ENRICHMENT COMPLETE")
            
            return {
                'status': 'success',
                'raw_context': raw_context,
                'markdown': markdown,
                'metadata': {
                    'enriched_at': datetime.now().isoformat(),
                    'contact_id': contact.get('id'),
                    'name': contact.get('name'),
                    'company': contact.get('company')
                }
            }
        
        except Exception as e:
            logger.error(f"Enrichment failed: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'metadata': {'enriched_at': datetime.now().isoformat()}
            }
