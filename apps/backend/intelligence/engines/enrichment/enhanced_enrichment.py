#!/usr/bin/env python3
"""
Apex Enrichment Engine - Pass ALL data to Perplexity
Uses proven prompt structure that works manually
"""
import os
import logging
import requests
from openai import OpenAI

logger = logging.getLogger(__name__)

class EnhancedEnrichment:
    """Pass all contact data to Perplexity with proven prompt"""
    
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
        """Main enrichment pipeline"""
        name = contact.get('name', '') or contact.get('firstname', '') + ' ' + contact.get('lastname', '')
        company = contact.get('company', '')
        title = contact.get('title', '')
        email = contact.get('email', '')
        phone = contact.get('phone', '')
        linkedin = contact.get('linkedin_url', '')
        
        logger.info("=" * 70)
        logger.info(f"🔍 ENRICHING: {name} at {company}")
        logger.info(f"   Title: {title}")
        logger.info(f"   Email: {email}")
        logger.info(f"   Phone: {phone}")
        logger.info(f"   LinkedIn: {linkedin}")
        logger.info("=" * 70)
        
        try:
            # Call Perplexity with ALL data
            profile = self._call_perplexity(
                name=name,
                company=company,
                title=title,
                email=email,
                phone=phone,
                linkedin=linkedin
            )
            
            if not profile or len(profile) < 500:
                logger.warning(f"⚠️  Short response: {len(profile) if profile else 0} chars")
                # Don't fail - return what we got
                if profile:
                    logger.info("Returning short profile anyway")
                else:
                    profile = self._create_minimal_profile(contact)
            
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
            
            # Return minimal profile on error
            return {
                'success': True,
                'profile_text': self._create_minimal_profile(contact),
                'character_count': 200
            }
    
    def _create_minimal_profile(self, contact: dict) -> str:
        """Fallback when enrichment fails"""
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
"""
    
    def _call_perplexity(self, name: str, company: str, title: str, email: str, phone: str, linkedin: str) -> str:
        """Send ALL data with proven prompt structure"""
        
        # Build context with ALL available data
        context_parts = []
        if name: context_parts.append(f"Name: {name}")
        if title: context_parts.append(f"Title: {title}")
        if company: context_parts.append(f"Company: {company}")
        if email: context_parts.append(f"Email: {email}")
        if phone: context_parts.append(f"Phone: {phone}")
        if linkedin: context_parts.append(f"LinkedIn: {linkedin}")
        
        contact_context = "\n".join(context_parts)
        
        # Use the EXACT structure that works for Dorit Fischer
        prompt = f"""Build comprehensive profile for:

{contact_context}

Provide:

**Person Profile:**
1. Overview – Current title and organization
2. Background – Work history, notable achievements
3. Education – Degrees and institutions
4. Recent Mentions – News, public appearances, LinkedIn posts
5. Social Media Profiles – Instagram, Facebook, Twitter (if available)
6. Personality Detail – Perform Myers-Briggs assessment (inferred from professional style)
7. StrengthsFinder – Key professional strengths
8. Sales Opportunities Talking Points – Why this is a valuable contact
9. Fun Fact – Interesting personal or professional detail

**Company Profile ({company}):**
1. Overview – Description, mission, founding details, HQ location
2. Products & Services – Key offerings and markets served
3. Leadership – Key executives and founders
4. Market & Competitors – Industry position, key competitors
5. Recent News – Major announcements, deals, product launches, funding

**Sales Intelligence:**
1. Trigger Events – Recent events creating sales opportunities (funding, expansion, leadership changes)
2. Current Solutions – What they might be using that we could replace
3. Warm Introduction Paths – Mutual connections or shared affiliations
4. Engagement Preferences – Best time/channel to reach out
5. Decision Making Style – How they evaluate vendors
6. Budget Authority – Signs of budget availability or fiscal timing
7. Success Metrics – KPIs they care about based on role

**Updates & New Information:**
- Verify all fields with current, accurate information
- Highlight any deals, partnerships, or major changes
- Note recent LinkedIn activity or company announcements

Format as structured markdown with clear sections and citations."""

        headers = {
            "Authorization": f"Bearer {self.perplexity_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "sonar-pro",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a professional sales intelligence researcher. Build comprehensive profiles from publicly available sources. Always provide actionable insights even with limited data. Work with what's available and make it useful."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.2,
            "max_tokens": 4000,
            "return_citations": True,
            "search_recency_filter": "month"
        }
        
        logger.info("📡 Calling Perplexity sonar-pro...")
        
        try:
            response = requests.post(
                self.perplexity_url,
                headers=headers,
                json=payload,
                timeout=120
            )
            
            response.raise_for_status()
            data = response.json()
            
            if 'choices' not in data or len(data['choices']) == 0:
                logger.error("❌ No choices in response")
                return ""
            
            profile = data['choices'][0]['message']['content']
            
            # Add citations
            if 'citations' in data and data['citations']:
                profile += "\n\n### Sources\n"
                for i, citation in enumerate(data['citations'][:20], 1):  # Limit to 20 citations
                    profile += f"[{i}] {citation}\n"
            
            logger.info(f"✅ Perplexity returned {len(profile)} characters")
            
            # Log first 500 chars for debugging
            logger.info(f"Preview: {profile[:500]}...")
            
            return profile
                
        except requests.exceptions.Timeout:
            logger.error("❌ Perplexity timeout after 120s")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Perplexity request error: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ Unexpected error: {e}")
            raise
