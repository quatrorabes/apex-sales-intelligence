#!/usr/bin/env python3
"""
Apex Enrichment Engine - Production Version v2
Optimized prompting for Perplexity Sonar-Pro
"""
import os
import logging
import requests
from datetime import datetime

logger = logging.getLogger(__name__)

class EnhancedEnrichment:
    """Two-Stage Enrichment: Perplexity Research -> Database Save"""
    
    def __init__(self):
        self.perplexity_key = os.getenv('PERPLEXITY_API_KEY')
        
        if not self.perplexity_key:
            raise ValueError("PERPLEXITY_API_KEY not set in .env")
        
        self.perplexity_url = "https://api.perplexity.ai/chat/completions"
        logger.info("✅ EnhancedEnrichment initialized (Perplexity Sonar-Pro)")
    
    def enrich_contact(self, contact: dict) -> dict:
        """Main enrichment pipeline"""
        name = contact.get('name', 'Unknown')
        company = contact.get('company', '')
        email = contact.get('email', '')
        linkedin = contact.get('linkedin_url', '')
        title = contact.get('title', '')
        
        logger.info("=" * 80)
        logger.info(f"🔍 ENRICHMENT: {name} ({title}) at {company}")
        logger.info("=" * 80)
        
        # Build optimized prompt
        prompt = self._build_research_prompt(name, company, email, linkedin, title)
        
        # Call Perplexity
        logger.info("📡 Calling Perplexity Sonar-Pro...")
        try:
            profile_text = self._call_perplexity(prompt)
            
            if not profile_text or len(profile_text) < 200:
                logger.error(f"❌ Insufficient data returned: {len(profile_text)} chars")
                return {
                    'success': False,
                    'error': 'Insufficient enrichment data'
                }
            
            logger.info(f"✅ SUCCESS: {len(profile_text)} characters received")
            logger.info("=" * 80)
            
            return {
                'success': True,
                'profile_text': profile_text,
                'character_count': len(profile_text)
            }
            
        except Exception as e:
            logger.error(f"❌ Enrichment failed: {e}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'error': str(e)
            }
    
    def _build_research_prompt(self, name: str, company: str, email: str, linkedin: str, title: str) -> str:
        """Build optimized research prompt"""
        
        # More direct, action-oriented prompt
        prompt = f"""Research and compile a comprehensive business intelligence profile for the following contact:

Name: {name}
Title: {title}
Company: {company}
Email: {email}
LinkedIn: {linkedin}

Search all available public sources and provide detailed narrative information under these exact headings:

### Overview
Provide current role, responsibilities, and organization summary.

### Background
Detail career trajectory, work history, notable achievements with specific years and companies.

### Education
List degrees, institutions, years attended, honors or distinctions.

### Recent Mentions
Find news articles, public appearances, LinkedIn activity, online presence with dates.

### Social Profiles
Locate and provide Instagram, Facebook, Twitter/X handles and profile URLs if publicly available.

### Personality Assessment
Based on professional behavior, leadership style, and communication patterns visible in public sources, assess personality traits and work style.

### Assessment Summary
Interpret personality type and how it relates to their professional approach and strengths.

### Sales Talking Points
Identify key discussion points relevant for business development conversations.

### Deal History
Find information about major deals, projects, or business initiatives they've led or participated in.

### Profile Updates
Recent career moves, company changes, or significant professional developments.

### Fun Facts & News
Interesting background details, awards, community involvement, or recent company news.

### Misc Notes
Additional context, caveats, or supplemental details.

Provide comprehensive, interpretive raw information under each heading. Use freeform prose. If information is not available for a section, state that directly."""

        return prompt
    
    def _call_perplexity(self, prompt: str) -> str:
        """Call Perplexity Sonar-Pro API"""
        headers = {
            "Authorization": f"Bearer {self.perplexity_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "sonar-pro",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a professional business intelligence researcher conducting company and executive research. Provide detailed findings from publicly available sources including company websites, news articles, press releases, and professional profiles. Focus on factual, verifiable information."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.3,
            "max_tokens": 4000,
            "return_citations": True,
            "search_recency_filter": "month"
        }
        
        try:
            response = requests.post(
                self.perplexity_url,
                headers=headers,
                json=payload,
                timeout=90
            )
            
            response.raise_for_status()
            data = response.json()
            
            if 'choices' in data and len(data['choices']) > 0:
                profile_text = data['choices'][0]['message']['content']
                
                # Add citations
                if 'citations' in data and data['citations']:
                    citations = "\n\n### Sources\n"
                    for i, citation in enumerate(data['citations'], 1):
                        citations += f"[{i}] {citation}\n"
                    profile_text += citations
                
                return profile_text
            else:
                logger.error(f"Unexpected API response: {data}")
                return ""
                
        except Exception as e:
            logger.error(f"❌ Perplexity API error: {e}")
            raise
