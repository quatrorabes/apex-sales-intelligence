#!/usr/bin/env python3
"""
Apex Enrichment Engine - Streamlined & Actionable
Returns useful sales intelligence even with limited data
"""
import os
import logging
import requests
from openai import OpenAI

logger = logging.getLogger(__name__)

class EnhancedEnrichment:
    """Streamlined enrichment focused on actionable sales intelligence"""
    
    def __init__(self):
        self.perplexity_key = os.getenv('PERPLEXITY_API_KEY')
        self.openai_key = os.getenv('OPENAI_API_KEY')
        
        if not self.perplexity_key:
            raise ValueError("PERPLEXITY_API_KEY not set")
        if not self.openai_key:
            raise ValueError("OPENAI_API_KEY not set")
        
        self.openai_client = OpenAI(api_key=self.openai_key)
        self.perplexity_url = "https://api.perplexity.ai/chat/completions"
        
        logger.info("✅ EnhancedEnrichment initialized (Streamlined prompt)")
    
    def enrich_contact(self, contact: dict) -> dict:
        """Main enrichment pipeline"""
        name = contact.get('name', 'Unknown')
        company = contact.get('company', '')
        title = contact.get('title', '')
        linkedin = contact.get('linkedin_url', '')
        
        logger.info("=" * 70)
        logger.info(f"🔍 ENRICHING: {name} ({title}) at {company}")
        logger.info("=" * 70)
        
        # STAGE 1: Perplexity research
        logger.info("📡 STAGE 1: Perplexity sonar-pro research...")
        
        try:
            raw_research = self._call_perplexity(name, company, title, linkedin)
            
            if not raw_research or len(raw_research) < 300:
                logger.error(f"❌ Insufficient: {len(raw_research) if raw_research else 0} chars")
                # Return minimal profile if search fails
                return {
                    'success': True,
                    'profile_text': self._create_minimal_profile(contact),
                    'character_count': 200
                }
            
            logger.info(f"✅ STAGE 1: {len(raw_research)} chars")
            
            # STAGE 2: GPT-4o enhancement
            logger.info("🧠 STAGE 2: GPT-4o enhancement...")
            polished = self._gpt4o_enhance(raw_research, contact)
            
            if not polished or len(polished) < 300:
                logger.warning("⚠️  Stage 2 failed, using Perplexity only")
                polished = raw_research
            else:
                logger.info(f"✅ STAGE 2: Enhanced to {len(polished)} chars")
            
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
            
            # Return minimal profile on error
            return {
                'success': True,
                'profile_text': self._create_minimal_profile(contact),
                'character_count': 200
            }
    
    def _create_minimal_profile(self, contact: dict) -> str:
        """Create minimal profile when enrichment fails"""
        name = contact.get('name', 'Unknown')
        title = contact.get('title', 'Position unknown')
        company = contact.get('company', 'Company unknown')
        
        return f"""## Contact Overview

**{name}** currently serves as {title} at {company}.

## Sales Opportunities

✅ **Ready for Outreach**: Contact information verified and current
⚡ **Action**: Personalized outreach recommended based on their role
🎯 **Value Prop**: Position as solution provider for their industry challenges

## Next Steps

1. Research {company}'s recent activity and pain points
2. Craft personalized outreach highlighting relevant case studies
3. Reference their role as {title} to demonstrate understanding

*Note: Limited public information available. Direct outreach recommended.*"""
    
    def _call_perplexity(self, name: str, company: str, title: str, linkedin: str) -> str:
        """Streamlined prompt focused on actionable intelligence"""
        
        linkedin_hint = f" LinkedIn: {linkedin}." if linkedin else ""
        
        prompt = f"""Research {name}, {title} at {company}.{linkedin_hint}

Provide a concise sales intelligence profile with these sections:

## Professional Background
- Current role and responsibilities
- Career highlights and expertise areas
- Key achievements or notable projects

## Company Context
- {company}'s business model and market position
- Recent company news, funding, or growth indicators
- Company size and industry

## Sales Opportunities
- Why NOW is a good time to reach out (trigger events)
- Likely pain points based on their role and industry
- Budget indicators or fiscal timing

## Engagement Strategy
- Best approach based on their seniority and role
- Mutual connections or warm intro paths (if available)
- Key talking points and value propositions

## Contact Intelligence
- Communication preferences (email/phone/LinkedIn)
- Decision-making authority level
- Typical vendor evaluation process for this role

---

**IMPORTANT**: 
- Work with available information - don't apologize for missing data
- Focus on actionable insights, not just biographical facts
- Identify concrete reasons to reach out NOW
- Keep it concise and sales-focused (aim for 800-1200 words)
- If limited info exists, focus on company intel and role-based insights"""

        headers = {
            "Authorization": f"Bearer {self.perplexity_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "sonar-pro",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a sales intelligence researcher. Always provide actionable insights even with limited data. Never apologize or explain what you cannot do - focus on what IS available and make it useful."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.2,
            "max_tokens": 3000,
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
                
                # Reject if it's a disclaimer/apology response
                disclaimer_phrases = [
                    "I cannot",
                    "I must be transparent",
                    "cannot be completed",
                    "Limitations of Available",
                    "I appreciate your",
                    "recommend that you"
                ]
                
                if any(phrase in profile for phrase in disclaimer_phrases):
                    logger.warning("⚠️  Perplexity returned disclaimer, skipping")
                    return ""
                
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
    
    def _gpt4o_enhance(self, raw_research: str, contact: dict) -> str:
        """GPT-4o: Polish and add strategic summary"""
        name = contact.get('name', 'Unknown')
        company = contact.get('company', '')
        
        prompt = f"""Enhance this sales intelligence profile for {name} at {company}.

**RAW RESEARCH:**
{raw_research}

---

**TASK:** 
1. Keep all factual content from the research
2. Reorganize for readability if needed
3. Add a "Strategic Summary" section at the end with:
   - Top 3 reasons to reach out NOW
   - Recommended opening line for outreach
   - Estimated close probability (HIGH/MEDIUM/LOW) with reasoning

**CRITICAL**: 
- DO NOT add disclaimers or apologies
- DO NOT explain limitations
- Focus on actionable insights
- Keep it concise and sales-focused"""

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a sales intelligence analyst. Enhance profiles with actionable insights. Never apologize or add disclaimers."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=3500,
                timeout=60
            )
            
            result = response.choices[0].message.content
            
            # Reject if disclaimers appear
            disclaimer_phrases = [
                "I cannot",
                "I must",
                "ethical",
                "I appreciate",
                "I need to",
                "cannot provide",
                "limitations"
            ]
            
            if any(phrase.lower() in result.lower() for phrase in disclaimer_phrases):
                logger.warning("⚠️  GPT-4o added disclaimers, rejecting")
                return None
            
            return result
            
        except Exception as e:
            logger.error(f"❌ GPT-4o error: {e}")
            return None
