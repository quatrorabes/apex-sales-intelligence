#!/usr/bin/env python3
"""
APEX Enrichment Engine - Multi-Stage Strategy
Dec 11, 2025 - Fixed version matching Dec 5 architecture

Architecture:
- Stage 1-3: Perplexity research (raw data collection)
- Stage 4: GPT-4 structured parsing (clean sections)
"""

import os
import logging
import requests
from openai import OpenAI
import time

logger = logging.getLogger(__name__)

class EnhancedEnrichment:
    """Multi-stage enrichment: Perplexity research → GPT-4 structured parsing"""
    
    def __init__(self):
        self.perplexity_key = os.getenv('PERPLEXITY_API_KEY')
        self.openai_key = os.getenv('OPENAI_API_KEY')
        
        if not self.perplexity_key:
            raise ValueError("PERPLEXITY_API_KEY not set")
        if not self.openai_key:
            raise ValueError("OPENAI_API_KEY not set")
        
        self.openai_client = OpenAI(api_key=self.openai_key)
        self.perplexity_url = "https://api.perplexity.ai/chat/completions"
        logger.info("✅ EnhancedEnrichment initialized")
    
    def enrich_contact(self, contact: dict) -> dict:
        """Main enrichment pipeline with 4-stage search"""
        name = contact.get('name', '') or f"{contact.get('firstname', '')} {contact.get('lastname', '')}".strip()
        company = contact.get('company', '')
        title = contact.get('title', '')
        linkedin = contact.get('linkedin_url', '')
        
        logger.info("=" * 70)
        logger.info(f"🔍 ENRICHING: {name} at {company}")
        logger.info(f"   Title: {title}")
        logger.info(f"   LinkedIn: {linkedin}")
        logger.info("=" * 70)
        
        try:
            # STAGE 1: Person Research (Perplexity)
            logger.info("📡 STAGE 1: Searching LinkedIn for person profile...")
            person_data = self._search_person(name, company, linkedin)
            logger.info(f"   ✅ Got {len(person_data)} chars")
            time.sleep(1)  # Rate limit
            
            # STAGE 2: Company Research (Perplexity)
            logger.info("📡 STAGE 2: Searching company news and intel...")
            company_data = self._search_company(company)
            logger.info(f"   ✅ Got {len(company_data)} chars")
            time.sleep(1)  # Rate limit
            
            # STAGE 3: Sales Context (Perplexity)
            logger.info("📡 STAGE 3: Searching person+company relationships...")
            sales_data = self._search_sales_context(name, company, title)
            logger.info(f"   ✅ Got {len(sales_data)} chars")
            
            # Combine all research
            combined_research = f"""# Research Data for {name} at {company}

## Person Profile Data
{person_data}

## Company Intelligence Data
{company_data}

## Sales & Relationship Context
{sales_data}
"""
            
            logger.info(f"📊 Total research: {len(combined_research)} chars")
            
            # STAGE 4: Parse with GPT-4
            logger.info("🧠 STAGE 4: Generating structured profile with GPT-4...")
            structured_profile = self._parse_with_gpt4(combined_research, contact)
            
            if not structured_profile or len(structured_profile) < 500:
                logger.warning(f"⚠️ Short profile: {len(structured_profile) if structured_profile else 0} chars")
                # Use raw research if parsing fails
                structured_profile = combined_research if len(combined_research) > 500 else self._create_minimal_profile(contact)
            
            logger.info(f"✅ COMPLETE: {len(structured_profile)} chars")
            logger.info("=" * 70)
            
            return {
                'success': True,
                'profile_text': structured_profile,
                'character_count': len(structured_profile),
                'raw_research': combined_research  # Include for compiler
            }
        
        except Exception as e:
            logger.error(f"❌ Enrichment failed: {e}")
            import traceback
            traceback.print_exc()
            return {
                'success': True,
                'profile_text': self._create_minimal_profile(contact),
                'character_count': 200
            }
    
    def _search_person(self, name: str, company: str, linkedin: str) -> str:
        """Stage 1: LinkedIn-focused person search"""
        if linkedin:
            query = f"{name} {company} site:linkedin.com OR {linkedin}"
        else:
            query = f"{name} {company} site:linkedin.com professional profile background education career"
        return self._perplexity_search(query, "person profile")
    
    def _search_company(self, company: str) -> str:
        """Stage 2: Company news and intelligence"""
        query = f"{company} company news funding leadership team products services market competitors recent announcements"
        return self._perplexity_search(query, "company intelligence")
    
    def _search_sales_context(self, name: str, company: str, title: str) -> str:
        """Stage 3: Person+company combined context"""
        query = f"{name} {title} {company} deals announcements achievements projects press mentions challenges pain points"
        return self._perplexity_search(query, "sales context")
    
    def _perplexity_search(self, query: str, search_type: str) -> str:
        """Execute a Perplexity search and return raw results"""
        headers = {
            "Authorization": f"Bearer {self.perplexity_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "sonar-pro",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a comprehensive research assistant. Extract ALL relevant information from search results. Be thorough and detailed. Include facts, context, and specific details."
                },
                {
                    "role": "user",
                    "content": f"Provide comprehensive, detailed information about: {query}\n\nInclude all available facts, context, background, and specific details."
                }
            ],
            "temperature": 0.1,
            "max_tokens": 2000,
            "return_citations": True,
            "search_recency_filter": "month"
        }
        
        try:
            response = requests.post(
                self.perplexity_url,
                headers=headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            data = response.json()
            
            if 'choices' not in data or len(data['choices']) == 0:
                logger.warning(f"⚠️ No results for {search_type}")
                return ""
            
            content = data['choices'][0]['message']['content']
            
            # Add citations
            if 'citations' in data and data['citations']:
                content += "\n\nSources:\n"
                for i, citation in enumerate(data['citations'][:10], 1):
                    content += f"[{i}] {citation}\n"
            
            return content
        
        except Exception as e:
            logger.error(f"❌ Search failed for {search_type}: {e}")
            return ""
    
    def _parse_with_gpt4(self, research_data: str, contact: dict) -> str:
        """
        Stage 4: Use GPT-4 to parse raw research into structured sections
        """
        name = contact.get('name', 'Unknown')
        company = contact.get('company', 'Unknown Company')
        title = contact.get('title', 'Unknown Title')
        
        # Truncate research to fit within GPT-4's context window
        max_research_chars = 12000  # ~3000 tokens
        truncated_research = research_data[:max_research_chars]
        
        prompt = f"""Using the research data below, create a structured sales intelligence profile for {name}.

**RESEARCH DATA:**
{truncated_research}

---

**Generate a profile with EXACTLY these section headers (include the ## markdown):**

## overview
[2-3 sentences summarizing current role, key responsibilities, and company context]

## background_and_experience
[Career history, achievements, expertise - use bullet points with "-"]

## company_overview
[Company description, size, industry, business model - bullet points]

## pain_points_and_challenges
[Role-specific and industry challenges they face - bullet points]

## budget_and_authority
[Decision-making power, budget ownership, procurement influence - bullet points]

---

**CRITICAL RULES:**
- Use ONLY verifiable facts from the research data
- Keep each section concise (3-5 bullet points maximum)
- Use the EXACT section headers shown above with ##
- Use "-" for bullet points, not "*" or numbers
- If a section lacks data, write "- Limited information available"
- No disclaimers, apologies, or meta-commentary
- Be specific with names, dates, numbers, companies
"""
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert sales intelligence analyst. Parse research into structured, actionable sections using exact headers provided. Be concise and factual."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.2,
                max_tokens=3000
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            logger.error(f"❌ GPT-4 parsing failed: {e}")
            import traceback
            traceback.print_exc()
            return ""
    
    def _create_minimal_profile(self, contact: dict) -> str:
        """Fallback minimal profile"""
        name = contact.get('name', 'Unknown')
        title = contact.get('title', 'Position unknown')
        company = contact.get('company', 'Company unknown')
        
        return f"""## overview
{name} - {title} at {company}

## background_and_experience
- Limited public information available
- Direct research recommended

## company_overview
- {company}
- Further research needed

## pain_points_and_challenges
- Industry-standard challenges likely apply

## budget_and_authority
- {title} level suggests relevant authority
"""
