#!/usr/bin/env python3
"""
Apex Enrichment Engine - Multi-Stage Search Strategy
Does 3 targeted searches then combines for rich profiles
Target: 8000+ character profiles
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
            query = f"{name} {company} site:linkedin.com professional profile background education"
        
        return self._perplexity_search(query, "person profile")
    
    def _search_company(self, company: str) -> str:
        """Stage 2: Company news and intelligence"""
        query = f"{company} company news funding leadership team products services market competitors recent announcements"
        return self._perplexity_search(query, "company intelligence")
    
    def _search_combined(self, name: str, company: str, title: str) -> str:
        """Stage 3: Person+company combined context"""
        query = f"{name} {title} {company} deals announcements achievements projects press mentions"
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
                    "content": "You are a comprehensive research assistant. Extract ALL relevant information from search results. Be thorough and detailed. Include facts, context, and specific details."
                },
                {
                    "role": "user",
                    "content": f"Provide comprehensive, detailed information about: {query}\n\nInclude all available facts, context, background, and specific details."
                }
            ],
            "temperature": 0.1,
            "max_tokens": 3000,  # Increased from 2000
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
            
            if 'choices' not in data or len(data['choices']) == 0:
                logger.warning(f"⚠️ No results for {search_type}")
                return ""
            
            content = data['choices'][0]['message']['content']
            
            # Add citations
            if 'citations' in data and data['citations']:
                content += "\n\nSources:\n"
                for i, citation in enumerate(data['citations'][:15], 1):  # Increased from 10
                    content += f"[{i}] {citation}\n"
            
            return content
            
        except Exception as e:
            logger.error(f"❌ Search failed for {search_type}: {e}")
            return ""
    
    def _generate_profile(self, research_data: str, contact: dict) -> str:
        """Generate comprehensive structured profile from combined research"""
        name = contact.get('name', 'Unknown')
        company = contact.get('company', '')
        
        prompt = f"""Using the research data below, create a COMPREHENSIVE sales intelligence profile (target 8000+ characters).

**RESEARCH DATA:**
{research_data}

---

**Generate a DETAILED profile with these sections:**

## {name} - Professional Profile

### Overview
- Current role, organization, and tenure
- Key responsibilities and areas of focus
- Reporting structure and team size (if available)

### Background & Experience
- Complete career history with dates and companies
- Major achievements and notable projects
- Industry expertise and specializations
- Awards and recognition

### Education & Credentials
- Degrees, institutions, and graduation years
- Certifications and professional development
- Academic achievements

### Personality & Working Style
- Professional strengths and leadership approach (inferred)
- Communication style and preferences
- Decision-making patterns
- Core values and motivations (based on public statements)

### Social Presence & Engagement
- LinkedIn activity, posts, and engagement topics
- Twitter/X presence and thought leadership
- Speaking engagements and conference appearances
- Published articles or media mentions

## {company} - Company Intelligence

### Company Overview
- Business model, mission, and value proposition
- Founded date, headquarters, and locations
- Company size (employees, revenue if public)
- Ownership structure (public/private/PE-backed)

### Products & Services
- Core offerings and product lines
- Target markets and customer segments
- Pricing models and go-to-market strategy

### Market Position
- Industry category and market size
- Top 3-5 competitors
- Competitive advantages and differentiators
- Market share and growth trajectory

### Leadership & Culture
- CEO and executive team background
- Board members and advisors
- Company culture and values
- Employee sentiment (if available)

### Recent Activity & News
- Funding rounds, M&A, or IPO activity
- Product launches and major announcements
- Partnerships and strategic initiatives
- Leadership changes or organizational shifts
- Press coverage and media mentions

## Sales Opportunities

### Trigger Events - Why Reach Out NOW
- Recent company events creating urgency
- Budget cycle timing and fiscal indicators
- Expansion signals or hiring patterns
- Technology changes or migrations
- Competitive pressures or market shifts

### Pain Points & Challenges
- Industry-specific challenges they're facing
- Role-specific pain points based on title
- Problems our solution could address
- Current gap analysis

### Budget & Authority
- Decision-making level and influence
- Budget ownership and approval process
- Typical vendor evaluation criteria
- Procurement cycle and timeline

### Engagement Strategy
- Best communication channels (email/phone/LinkedIn)
- Optimal timing for outreach
- Referral and warm introduction paths
- Mutual connections or shared affiliations
- Content preferences and interests

### Value Proposition Alignment
- Key talking points specific to their role
- Case studies or testimonials from similar companies
- ROI metrics they care about
- Success metrics and KPIs for their position

### Competitive Intelligence
- Current solutions they're likely using
- Vendor relationships and contracts
- Technology stack (if known)
- Integration requirements

## Strategic Summary

### Opportunity Assessment
- **Opportunity Level:** HIGH / MEDIUM / LOW (with specific reasoning)
- **Close Probability:** Percentage estimate with justification
- **Deal Size Potential:** Estimated value and time to close

### Top 5 Reasons to Engage
1. [Specific trigger or pain point]
2. [Budget/timing indicator]
3. [Strategic fit factor]
4. [Competitive advantage]
5. [Relationship leverage point]

### Recommended Opening Line
[Specific, personalized opening that references recent activity, shared connection, or relevant pain point]

### 30/60/90 Day Engagement Plan
- **Days 1-30:** [Initial outreach strategy]
- **Days 31-60:** [Follow-up and value demonstration]
- **Days 61-90:** [Proposal and closing activities]

---

**CRITICAL INSTRUCTIONS:**
- Use ONLY verifiable facts from the research data
- Be COMPREHENSIVE - aim for 8000+ characters
- Include specific names, dates, numbers, and details
- No disclaimers, apologies, or explanations of limitations
- If a section lacks data, briefly note it and move on
- Focus on actionable, sales-relevant insights
- Be specific and detailed in every section
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
                    "content": "You are an expert sales intelligence analyst. Create comprehensive, detailed, actionable profiles. Be thorough and specific. Target 8000+ characters."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.3,
            "max_tokens": 4500  # Increased from 3000 to allow longer outputs
        }
        
        try:
            response = requests.post(
                self.perplexity_url,
                headers=headers,
                json=payload,
                timeout=120  # Increased timeout for longer generation
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
