#!/usr/bin/env python3
"""
Apex Enrichment Engine - Multi-Stage Search Strategy
Does 3 targeted searches then combines for rich profiles
"""
import os
import logging
import requests
from openai import OpenAI
import time

logger = logging.getLogger(__name__)

class EnhancedEnrichment:
    """Multi-stage search for comprehensive enrichment"""
    
    def __init__(self):
        self.perplexity_key = os.getenv('PERPLEXITY_API_KEY')
        self.openai_key = os.getenv('OPENAI_API_KEY')
        
        if not self.perplexity_key:
            raise ValueError("PERPLEXITY_API_KEY not set")
        if not self.openai_key:
            raise ValueError("OPENAI_API_KEY not set")
        
        self.openai_client = OpenAI(api_key=self.openai_key)
        self.perplexity_url = "https://api.perplexity.ai/chat/completions"
        
        logger.info("✅ EnhancedEnrichment initialized (Multi-Stage Search)")
    
    def enrich_contact(self, contact: dict) -> dict:
        """Main enrichment pipeline with 3-stage search"""
        name = contact.get('name', '') or f"{contact.get('firstname', '')} {contact.get('lastname', '')}".strip()
        company = contact.get('company', '')
        title = contact.get('title', '')
        email = contact.get('email', '')
        phone = contact.get('phone', '')
        linkedin = contact.get('linkedin_url', '')
        
        logger.info("=" * 70)
        logger.info(f"🔍 ENRICHING: {name} at {company}")
        logger.info(f"   Title: {title}")
        logger.info(f"   LinkedIn: {linkedin}")
        logger.info("=" * 70)
        
        try:
            # STAGE 1: LinkedIn/Person Search
            logger.info("📡 STAGE 1: Searching LinkedIn for person profile...")
            person_data = self._search_person(name, company, linkedin)
            logger.info(f"   ✅ Got {len(person_data)} chars")
            time.sleep(1)  # Rate limit
            
            # STAGE 2: Company/News Search
            logger.info("📡 STAGE 2: Searching company news and intel...")
            company_data = self._search_company(company)
            logger.info(f"   ✅ Got {len(company_data)} chars")
            time.sleep(1)  # Rate limit
            
            # STAGE 3: Combined Person+Company Context
            logger.info("📡 STAGE 3: Searching person+company relationships...")
            combined_data = self._search_combined(name, company, title)
            logger.info(f"   ✅ Got {len(combined_data)} chars")
            
            # Combine all research
            total_research = f"""# Research Data for {name} at {company}

## Person Profile Data
{person_data}

## Company Intelligence Data
{company_data}

## Combined Context & Relationships
{combined_data}
"""
            
            logger.info(f"📊 Total research: {len(total_research)} chars")
            
            # STAGE 4: Generate Profile from Combined Data
            logger.info("🧠 STAGE 4: Generating structured profile...")
            profile = self._generate_profile(total_research, contact)
            
            if not profile or len(profile) < 500:
                logger.warning(f"⚠️ Short profile: {len(profile) if profile else 0} chars")
                # Use raw research if generation fails
                profile = total_research if len(total_research) > 500 else self._create_minimal_profile(contact)
            
            logger.info(f"✅ COMPLETE: {len(profile)} chars")
            logger.info("=" * 70)
            
            return {
                'success': True,
                'profile_text': profile,
                'character_count': len(profile)
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
            query = f"{name} {company} site:linkedin.com professional profile"
        
        return self._perplexity_search(query, "person profile")
    
    def _search_company(self, company: str) -> str:
        """Stage 2: Company news and intelligence"""
        query = f"{company} news funding leadership products services recent"
        return self._perplexity_search(query, "company intelligence")
    
    def _search_combined(self, name: str, company: str, title: str) -> str:
        """Stage 3: Person+company combined context"""
        query = f"{name} {title} {company} deals announcements achievements"
        return self._perplexity_search(query, "combined context")
    
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
                    "content": "You are a research assistant. Extract all relevant information from search results. Be comprehensive and factual."
                },
                {
                    "role": "user",
                    "content": f"Research and provide all available information about: {query}"
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
    
    def _generate_profile(self, research_data: str, contact: dict) -> str:
        """Generate structured profile from combined research"""
        name = contact.get('name', 'Unknown')
        company = contact.get('company', '')
        
        prompt = f"""Using the research data below, create a comprehensive sales intelligence profile.

**RESEARCH DATA:**
{research_data}

---

**Generate profile with these sections:**

## {name} - Professional Profile

### Overview
- Current role and organization
- Key responsibilities and focus areas

### Background
- Career history and achievements
- Education and credentials
- Notable projects or deals

### Personality & Working Style
- Professional strengths (inferred from public info)
- Communication and decision-making style
- Leadership approach

### Social Presence
- LinkedIn activity and engagement
- Other professional profiles (if available)

## {company} - Company Intelligence

### Company Overview
- Business model and offerings
- Market position and competitors
- Size and locations

### Recent Activity
- News, funding, or major announcements
- Product launches or partnerships
- Leadership changes

## Sales Opportunities

### Why Reach Out NOW
- Trigger events creating urgency
- Pain points based on role and industry
- Budget timing indicators

### Engagement Strategy
- Best approach based on seniority
- Communication preferences
- Key talking points
- Warm introduction paths (if available)

### Success Factors
- Decision-making authority
- KPIs they care about
- How they evaluate vendors

## Strategic Summary
- Top 3 reasons this is a high-value contact
- Recommended opening line for outreach
- Estimated opportunity level (HIGH/MEDIUM/LOW)

---

**IMPORTANT:**
- Use ONLY facts from the research data
- If information is limited, focus on what IS available
- No disclaimers or apologies
- Be specific and actionable
"""

        headers = {
            "Authorization": f"Bearer {self.perplexity_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "sonar-pro",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a sales intelligence analyst. Create actionable profiles from research data. Be concise and specific."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.3,
            "max_tokens": 3000
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
            
            if 'choices' in data and len(data['choices']) > 0:
                return data['choices'][0]['message']['content']
            
            return ""
            
        except Exception as e:
            logger.error(f"❌ Profile generation failed: {e}")
            return ""
    
    def _create_minimal_profile(self, contact: dict) -> str:
        """Fallback minimal profile"""
        name = contact.get('name', 'Unknown')
        title = contact.get('title', 'Position unknown')
        company = contact.get('company', 'Company unknown')
        
        return f"""## {name}
**{title}** at **{company}**

### Sales Opportunities
✅ Contact verified - ready for outreach
🎯 Research {company}'s recent activity before reaching out
💡 Personalize based on their role as {title}

### Next Steps
1. Search for recent {company} news and developments
2. Identify relevant case studies or solutions
3. Craft personalized outreach referencing their specific challenges

*Note: Limited public information available. Direct research recommended.*
"""
