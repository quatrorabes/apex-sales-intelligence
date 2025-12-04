#!/usr/bin/env python3
"""
Apex Enrichment Engine - YOUR PROMPT + SONAR-PRO
Uses your proven 17-point prompt with sonar-pro model
"""
import os
import logging
import requests
from openai import OpenAI

logger = logging.getLogger(__name__)

class EnhancedEnrichment:
    """Your proven prompt + sonar-pro model"""
    
    def __init__(self):
        self.perplexity_key = os.getenv('PERPLEXITY_API_KEY')
        self.openai_key = os.getenv('OPENAI_API_KEY')
        
        if not self.perplexity_key:
            raise ValueError("PERPLEXITY_API_KEY not set")
        if not self.openai_key:
            raise ValueError("OPENAI_API_KEY not set")
        
        self.openai_client = OpenAI(api_key=self.openai_key)
        self.perplexity_url = "https://api.perplexity.ai/chat/completions"
        
        logger.info("✅ EnhancedEnrichment initialized (YOUR PROMPT + sonar-pro)")
    
    def enrich_contact(self, contact: dict) -> dict:
        """Main enrichment pipeline"""
        name = contact.get('name', 'Unknown')
        company = contact.get('company', '')
        linkedin = contact.get('linkedin_url', '')
        
        logger.info("=" * 70)
        logger.info(f"🔍 ENRICHING: {name} at {company}")
        logger.info("=" * 70)
        
        # STAGE 1: Perplexity with YOUR PROMPT + sonar-pro
        logger.info("📡 STAGE 1: Perplexity sonar-pro (YOUR 17-point prompt)...")
        
        try:
            raw_research = self._call_perplexity(name, company, linkedin)
            
            if not raw_research or len(raw_research) < 500:
                logger.error(f"❌ Insufficient: {len(raw_research) if raw_research else 0} chars")
                return {'success': False, 'error': 'Insufficient research'}
            
            logger.info(f"✅ STAGE 1: {len(raw_research)} chars")
            
            # STAGE 2: Optional GPT-4o light enhancement
            logger.info("🧠 STAGE 2: GPT-4o light enhancement (optional)...")
            polished = self._gpt4o_light_enhance(raw_research, contact)
            
            if not polished or len(polished) < len(raw_research):
                logger.warning("⚠️  Stage 2 skipped, using Perplexity only")
                polished = raw_research
            else:
                logger.info(f"✅ STAGE 2: Enhanced")
            
            logger.info("=" * 70)
            logger.info(f"✅ COMPLETE: {len(polished)} chars")
            logger.info("=" * 70)
            
            return {
                'success': True,
                'profile_text': polished,
                'raw_research': raw_research,
                'character_count': len(polished)
            }
            
        except Exception as e:
            logger.error(f"❌ Failed: {e}")
            import traceback
            traceback.print_exc()
            return {'success': False, 'error': str(e)}
    
    def _call_perplexity(self, name: str, company: str, linkedin: str) -> str:
        """YOUR PROVEN 17-POINT PROMPT with sonar-pro model"""
        
        prompt = f"""You are a professional profile-building assistant. Generate up-to-date profile using both public web sources for {name} at {company}.

Use sources such as LinkedIn ({linkedin}) & Internet.

For a company ({company}), structure the profile as:
1. Overview – Description, mission, founding details, and HQ
2. Products & Services – Key offerings and markets served
3. Leadership – Key executives and founders
4. Market & Competitors – Industry, position, key competitors
5. Recent News – Major announcements, deals, or product launches

For a person ({name}), structure the profile as:
1. Overview – Current title and organization
2. Background – Work history, notable achievements
3. Education – Degrees and institutions
4. Recent Mentions – Any news, public appearances, LinkedIn posts, or online presence
5. Find instagram, facebook, and twitter user profiles.
6. Personality Detail - perform a Myers briggs assessment.
7. Compose and interpret Myers-Briggs Personality assessment summary.
8. Evaluate potential talking points regarding sales opportunities.
9. Search deals database for any past or current "deal"
10. Update all fields with new or inaccurate information
11. Find any relevant company news or fun facts.
12. Trigger Events - Identify any recent events that create sales opportunities (new funding, expansion, leadership changes)
13. Competitive Intelligence - What solutions are they currently using that we could replace?
14. Warm Introduction Paths - Find mutual connections or shared affiliations
15. Engagement Preferences - Best time to reach, preferred communication channels
16. Decision Making Style - How they evaluate vendors and make purchasing decisions
17. Budget Authority - Signs of budget availability or fiscal year timing
18. Success Metrics - What KPIs they care about based on their role

Additionally, provide:
- AI Score Reasoning: Why this is a high-value contact (100 words)
- Relationship Tips: Based on their personality type
- Pain Points: Specific to their role and industry
- Outreach Approach: Multi-paragraph personalized approach"""

        headers = {
            "Authorization": f"Bearer {self.perplexity_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "sonar-pro",  # FIXED: Using sonar-pro instead of llama
            "messages": [
                {
                    "role": "system",
                    "content": "You are a professional profile-building assistant. Generate comprehensive, actionable intelligence from publicly available sources."
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
        
        try:
            response = requests.post(
                self.perplexity_url,
                headers=headers,
                json=payload,
                timeout=120
            )
            
            response.raise_for_status()
            data = response.json()
            
            if 'choices' in data and len(data['choices']) > 0:
                profile = data['choices'][0]['message']['content']
                
                # Add citations
                if 'citations' in data and data['citations']:
                    profile += "\n\n### Sources\n"
                    for i, citation in enumerate(data['citations'], 1):
                        profile += f"[{i}] {citation}\n"
                
                return profile
            
            return ""
                
        except Exception as e:
            logger.error(f"❌ Perplexity error: {e}")
            raise
    
    def _gpt4o_light_enhance(self, raw_research: str, contact: dict) -> str:
        """GPT-4o: ONLY add 1-2 sentence strategic summary at end"""
        name = contact.get('name', 'Unknown')
        
        prompt = f"""Add ONLY a brief strategic summary at the very end.

**PROFILE:**
{raw_research}

---

**ADD:** One "Strategic Summary" paragraph (2-3 sentences) synthesizing key sales takeaways.

Keep 100% of original content. Just add brief summary at end."""

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "Add brief summary only. Keep all content."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=4500,
                timeout=45
            )
            
            result = response.choices[0].message.content
            
            # Reject if disclaimers
            if any(p in result for p in ["I cannot", "ethical", "I appreciate", "I need to"]):
                return None
            
            return result
            
        except Exception as e:
            logger.error(f"❌ GPT-4o error: {e}")
            return None
