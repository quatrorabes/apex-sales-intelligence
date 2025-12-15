#!/usr/bin/env python3
"""
APEX FULL ENRICHMENT ENGINE
Uses YOUR EXACT profile builder questions (11-point structure)
Combines Perplexity AI deep research + WHO/WHEN/WHAT kernel + Outreach generation
"""

import os
import json
import requests
import time
import re
from datetime import datetime
from typing import Dict, Optional
import sqlite3

# ============================================================================
# PERPLEXITY API CLIENT - YOUR EXACT PROFILE BUILDER QUESTIONS
# ============================================================================

class PerplexityEnrichment:
    """Deep enrichment using YOUR EXACT 11 profile builder questions"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.perplexity.ai/chat/completions"
    
    def deep_enrich(self, contact: Dict) -> Dict:
        """
        YOUR EXACT PROFILE BUILDER QUESTIONS
        Matches your manual Perplexity enrichment process
        """
        name = f"{contact.get('first_name', '')} {contact.get('last_name', '')}".strip()
        company = contact.get('company', '')
        linkedin = contact.get('linkedin_url', '')
        email = contact.get('email', '')
        title = contact.get('title', '')
        
        if not name or name == "None None":
            name = contact.get('name', 'Unknown')
        
        # YOUR EXACT PROMPT - Word for word from your process
        prompt = f"""You are a professional profile-building assistant. Generate up-to-date profile using both public web sources for the following contact. Use sources such as LinkedIn & Internet.

**CONTACT INFORMATION:**
- Name: {name}
- Email: {email}
- Company: {company}
- LinkedIn: {linkedin}
- Title: {title}

**FOR THE COMPANY ({company}), structure the profile as:**

1. **Overview** – Description, mission, founding details, and HQ
2. **Products & Services** – Key offerings and markets served
3. **Leadership** – Key executives and founders
4. **Market & Competitors** – Industry, position, key competitors
5. **Recent News** – Major announcements, deals, or product launches
6. **Use {name}'s LinkedIn activity and closing data in sales pitches and CRM enrichment** - Analyze recent posts, engagement patterns, deal announcements, and professional updates
7. **Identify top skills highlighted in {name}'s profile** - List all endorsed skills, specializations, and areas of expertise

**FOR THE PERSON ({name}), structure the profile as:**

1. **Overview** – Current title and organization
2. **Background** – Work history, notable achievements
3. **Education** – Degrees and institutions
4. **Recent Mentions** – Any news, public appearances, LinkedIn posts, or online presence
5. **Find Instagram, Facebook, and Twitter user profiles** - Provide exact handles/URLs
6. **Personality Detail** - Perform a Myers-Briggs assessment based on available information
7. **Compose and interpret Myers-Briggs Personality assessment summary** - Provide detailed analysis of:
   - Communication style preferences
   - Decision-making approach
   - Work environment fit
   - Relationship building strategies
   - Stress responses and coping mechanisms
   - Ideal outreach approach based on personality type
8. **Evaluate potential talking points regarding sales opportunities** - Include:
   - Recent achievements or wins
   - Market challenges they're facing
   - Industry trends relevant to their role
   - Pain points specific to their position
   - Value propositions that would resonate
   - Conversation starters based on their interests
9. **Search deals database for any past or current "deal"** - Look for:
   - Recent transactions mentioned on LinkedIn
   - Press releases about deals
   - Company announcements
   - Pipeline activity signals
10. **Update all fields with new or inaccurate information** - Flag any discrepancies between sources
11. **Find any relevant company news or fun facts** - Include:
    - Company awards and recognition
    - Growth metrics and financial performance
    - Expansion plans or new initiatives
    - Personal interests and hobbies
    - Shared connections or affiliations
    - Community involvement
    - Sports teams, alma mater, professional groups

**CRITICAL REQUIREMENTS:**
- BE SPECIFIC: Use exact numbers, dates, dollar amounts, transaction details
- BE CURRENT: Focus on last 12-24 months (2024-2025 activity)
- BE QUANTITATIVE: "1,000+ transactions, $250M+" not "extensive experience"
- BE ACTIONABLE: Every insight should inform sales strategy
- NO GENERIC STATEMENTS: Must be specific to this individual
- VERIFY SOCIAL MEDIA: Confirm handles are correct before listing
- PERSONALITY DEPTH: Go beyond surface MBTI - explain behavioral patterns
- DEAL MOMENTUM: Highlight recent activity that creates urgency
- LINKEDIN ACTIVITY: Quote recent posts if relevant to sales approach

If specific information is not publicly available, state "Not publicly available" rather than making generic statements.

Generate the comprehensive profile now:
"""
        
        print(f"      🔍 Deep enrichment via Perplexity (YOUR profile builder questions)...")
        
        try:
            payload = {
                "model": "sonar-pro",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a professional profile-building assistant specializing in comprehensive B2B contact intelligence. You have access to public web sources including LinkedIn, company websites, press releases, and social media. Your profiles must be specific, quantitative, and actionable for sales teams. Generic statements are unacceptable."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.1,
                "max_tokens": 4000,
                "top_p": 0.9,
                "stream": False
            }
            
            print(f"      📤 Sending profile builder request...")
            
            response = requests.post(
                self.base_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json=payload,
                timeout=120
            )
            
            print(f"      📥 Response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                
                if 'usage' in result:
                    usage = result['usage']
                    print(f"      📊 Tokens used: {usage.get('total_tokens', 'N/A')}")
                    print(f"      💰 Est. cost: ${(usage.get('total_tokens', 0) * 0.001):.4f}")
                
                print(f"      ✅ Generated {len(content)} characters of intelligence")
                
                # Parse the structured response
                return self._parse_profile_builder_response(content, contact)
            else:
                error_detail = response.text
                print(f"      ❌ API Error {response.status_code}: {error_detail}")
                return self._fallback_data(contact)
        
        except requests.exceptions.Timeout:
            print(f"      ⏱️  API Timeout after 120 seconds")
            return self._fallback_data(contact)
        except Exception as e:
            print(f"      ❌ Unexpected error: {e}")
            import traceback
            traceback.print_exc()
            return self._fallback_data(contact)
    
    def _parse_profile_builder_response(self, text: str, contact: Dict) -> Dict:
        """
        Parse response from YOUR profile builder questions
        Matches your 11-point structure
        """
        enriched = {
            "full_profile": text,
            
            # Company Information
            "company_overview": self._extract_section_flexible(text, ["Company.*Overview", "1\\..*Overview", "Overview.*Description"]),
            "company_products": self._extract_section_flexible(text, ["Products.*Services", "2\\..*Products", "Key offerings"]),
            "company_leadership": self._extract_section_flexible(text, ["Leadership", "3\\..*Leadership", "Key executives"]),
            "company_market": self._extract_section_flexible(text, ["Market.*Competitors", "4\\..*Market", "Industry.*position"]),
            "company_news": self._extract_section_flexible(text, ["Recent News", "5\\..*Recent News", "Major announcements"]),
            
            # Person Information
            "overview": self._extract_section_flexible(text, ["Person.*Overview", "Current title", "FOR THE PERSON.*1\\."]),
            "background": self._extract_section_flexible(text, ["Background", "2\\..*Background", "Work history"]),
            "education": self._extract_section_flexible(text, ["Education", "3\\..*Education", "Degrees.*institutions"]),
            "recent_mentions": self._extract_section_flexible(text, ["Recent Mentions", "4\\..*Recent", "LinkedIn posts"]),
            
            # Social Media (Question 5)
            "social_media": self._extract_section_flexible(text, ["social.*profiles", "5\\..*Instagram", "Twitter.*Facebook"]),
            "instagram": self._extract_handle(text, "instagram"),
            "twitter": self._extract_handle(text, "twitter"),
            "facebook": self._extract_handle(text, "facebook"),
            
            # Myers-Briggs (Questions 6 & 7)
            "personality_detail": self._extract_section_flexible(text, ["6\\..*Personality", "Myers.*Briggs", "MBTI", "Personality Detail"]),
            "mbti_assessment": self._extract_section_flexible(text, ["7\\..*Myers-Briggs.*summary", "Personality assessment summary", "MBTI.*interpretation"]),
            "myers_briggs": "",  # Will be populated from above
            "mbti_type": "",
            
            # Talking Points (Question 8)
            "talking_points": self._extract_section_flexible(text, ["8\\..*talking points", "sales opportunities", "Talking points.*sales"]),
            
            # Deals Database (Question 9)
            "deals_database": self._extract_section_flexible(text, ["9\\..*deals database", "past.*current.*deal", "Recent transactions"]),
            "trigger_events": "",  # Will extract from deals
            
            # Field Updates (Question 10)
            "field_updates": self._extract_section_flexible(text, ["10\\..*Update.*fields", "new.*inaccurate.*information", "discrepancies"]),
            
            # Fun Facts & Company News (Question 11)
            "fun_facts": self._extract_section_flexible(text, ["11\\..*company news.*fun facts", "relevant.*news", "company awards"]),
            
            # LinkedIn Activity (Question 6)
            "linkedin_activity": self._extract_section_flexible(text, ["6\\..*LinkedIn activity", "closing data", "recent posts"]),
            
            # Top Skills (Question 7)
            "top_skills": self._extract_section_flexible(text, ["7\\..*top skills", "skills highlighted", "endorsed skills"]),
            
            # Legacy compatibility fields
            "pain_points": "",
            "relationship_tips": "",
            "outreach_approach": "",
            "ai_score_reasoning": "",
            "warm_intros": ""
        }
        
        # Combine Myers-Briggs sections
        enriched["myers_briggs"] = f"{enriched['personality_detail']}\n\n{enriched['mbti_assessment']}"
        
        # Extract MBTI type
        mbti_types = ["ENTJ", "INTJ", "ENTP", "INTP", "ENFJ", "INFJ", "ENFP", "INFP",
                      "ESTJ", "ISTJ", "ESTP", "ISTP", "ESFJ", "ISFJ", "ESFP", "ISFP"]
        for mbti in mbti_types:
            if mbti in enriched["myers_briggs"].upper():
                enriched["mbti_type"] = mbti
                break
        
        # Extract pain points from talking points
        enriched["pain_points"] = self._extract_pain_from_talking_points(enriched["talking_points"])
        
        # Extract relationship tips from MBTI assessment
        enriched["relationship_tips"] = self._extract_relationship_from_mbti(enriched["mbti_assessment"])
        
        # Extract outreach approach from personality + talking points
        enriched["outreach_approach"] = f"{enriched['mbti_assessment'][:500]}\n\n{enriched['talking_points'][:500]}"
        
        # Extract AI score reasoning from background + deals
        enriched["ai_score_reasoning"] = f"{enriched['background'][:300]}\n{enriched['deals_database'][:300]}"
        
        # Trigger events from deals database
        enriched["trigger_events"] = enriched["deals_database"]
        
        # Warm intros from fun facts + education
        enriched["warm_intros"] = f"{enriched['education']}\n{enriched['fun_facts']}"
        
        # Extract quantifiable metrics
        enriched["years_experience"] = self._extract_years(enriched["background"])
        enriched["transaction_count"] = self._extract_transactions(enriched["deals_database"])
        enriched["transaction_value"] = self._extract_value(enriched["deals_database"])
        
        return enriched
    
    def _extract_section_flexible(self, text: str, patterns: list) -> str:
        """
        Extract section using multiple possible patterns
        More flexible than strict section headers
        """
        for pattern in patterns:
            # Try to find section with this pattern
            regex = re.compile(f"{pattern}.*?(?=\n\n\\*\\*|$)", re.IGNORECASE | re.DOTALL)
            match = regex.search(text)
            if match:
                return match.group(0).strip()
        
        return ""
    
    def _extract_handle(self, text: str, platform: str) -> str:
        """Extract social media handle for specific platform"""
        patterns = {
            "instagram": [
                r'instagram\.com/([a-zA-Z0-9._]+)',
                r'@([a-zA-Z0-9._]+).*instagram',
                r'Instagram:.*?@([a-zA-Z0-9._]+)'
            ],
            "twitter": [
                r'twitter\.com/([a-zA-Z0-9_]+)',
                r'x\.com/([a-zA-Z0-9_]+)',
                r'@([a-zA-Z0-9_]+).*twitter',
                r'Twitter:.*?@([a-zA-Z0-9_]+)'
            ],
            "facebook": [
                r'facebook\.com/([a-zA-Z0-9.]+)',
                r'Facebook:.*?facebook\.com/([a-zA-Z0-9.]+)'
            ]
        }
        
        for pattern in patterns.get(platform, []):
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return f"@{match.group(1)}"
        
        return ""
    
    def _extract_pain_from_talking_points(self, talking_points: str) -> str:
        """Extract pain points from talking points section"""
        pain_keywords = ["challenge", "pain", "problem", "struggle", "difficulty", "issue", "concern", "obstacle"]
        lines = talking_points.split('\n')
        pain_lines = []
        
        for line in lines:
            if any(keyword in line.lower() for keyword in pain_keywords):
                pain_lines.append(line.strip())
        
        if pain_lines:
            return '\n'.join(pain_lines[:5])
        
        # Fallback: return first few bullet points from talking points
        bullets = [line.strip() for line in lines if line.strip().startswith(('-', '•', '*'))]
        return '\n'.join(bullets[:5]) if bullets else talking_points[:500]
    
    def _extract_relationship_from_mbti(self, mbti_section: str) -> str:
        """Extract relationship building tips from MBTI assessment"""
        relationship_keywords = ["relationship", "communicate", "approach", "rapport", "trust", "connect"]
        lines = mbti_section.split('\n')
        relationship_lines = []
        
        for line in lines:
            if any(keyword in line.lower() for keyword in relationship_keywords):
                relationship_lines.append(line.strip())
        
        if relationship_lines:
            return '\n'.join(relationship_lines)
        
        # Fallback: return communication style section
        return mbti_section[:500] if mbti_section else "Adapt communication to their personality type"
    
    def _extract_years(self, background: str) -> str:
        """Extract years of experience"""
        patterns = [
            r'(\d+)\+?\s*years',
            r'since\s*(\d{4})',
            r'over\s*(\d+)\s*years'
        ]
        for pattern in patterns:
            match = re.search(pattern, background, re.IGNORECASE)
            if match:
                year_or_count = match.group(1)
                # If it's a year (4 digits), calculate years
                if len(year_or_count) == 4:
                    years = datetime.now().year - int(year_or_count)
                    return str(years)
                return year_or_count
        return ""
    
    def _extract_transactions(self, deals: str) -> str:
        """Extract transaction count from deals database"""
        patterns = [
            r'(\d{1,3}(?:,\d{3})*)\+?\s*(?:transaction|deal|lease|sale)',
        ]
        for pattern in patterns:
            match = re.search(pattern, deals, re.IGNORECASE)
            if match:
                return match.group(1)
        return ""
    
    def _extract_value(self, deals: str) -> str:
        """Extract transaction value"""
        patterns = [
            r'\$(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*(?:M|B|million|billion)',
            r'(\d{1,3}(?:,\d{3})*)\s*(?:million|billion)',
        ]
        for pattern in patterns:
            match = re.search(pattern, deals, re.IGNORECASE)
            if match:
                return f"${match.group(1)}M+"
        return ""
    
    def _fallback_data(self, contact: Dict) -> Dict:
        """Return basic data when API fails"""
        name = contact.get('name', 'Unknown')
        title = contact.get('title', '')
        company = contact.get('company', '')
        
        return {
            "full_profile": f"Basic profile for {name}",
            "overview": f"{name} is {title} at {company}",
            "background": "Professional with experience in their field",
            "education": "Information not available",
            "recent_news": "No recent updates found",
            "myers_briggs": "Unable to assess",
            "mbti_type": "Unknown",
            "pain_points": "Analyze specific role and industry challenges",
            "relationship_tips": "Professional, consultative approach",
            "outreach_approach": "Value-focused messaging",
            "talking_points": "Industry trends and solutions",
            "ai_score_reasoning": "Standard qualification criteria",
            "trigger_events": "Monitor for business developments",
            "warm_intros": "Research mutual connections",
            "decision_style": "Analytical, ROI-focused"
        }


# ============================================================================
# THE KERNEL - WHO, WHEN, WHAT
# ============================================================================

class KernelIntelligence:
    """WHO to call, WHEN to call, WHAT to say"""
    
    def generate_kernel(self, contact: Dict, deep_data: Dict) -> Dict:
        """Generate WHO/WHEN/WHAT intelligence"""
        print(f"      🧠 Kernel: WHO/WHEN/WHAT analysis...")
        
        persona = self._detect_persona(contact)
        timing = self._detect_timing(contact, deep_data)
        approach = self._generate_approach(contact, persona, timing, deep_data)
        
        return {
            'who': {
                'persona_type': persona['type'],
                'decision_role': persona['role'],
                'influence_level': persona['influence']
            },
            'when': {
                'timing_signal': timing['signal'],
                'urgency_level': timing['urgency'],
                'optimal_contact_time': timing['best_time'],
                'follow_up_cadence': timing['cadence']
            },
            'what': {
                'opening_hook': approach['hook'],
                'value_props': approach['value_props'],
                'discovery_questions': approach['questions'],
                'objection_handlers': approach['objections'],
                'call_to_action': approach['cta']
            }
        }
    
    def _detect_persona(self, contact: Dict) -> Dict:
        """Detect WHO this contact is"""
        title = (contact.get('title') or '').lower()
        company = (contact.get('company') or '').lower()
        
        if any(kw in title for kw in ['owner', 'ceo', 'president', 'founder']):
            if 'franchise' in company:
                return {'type': 'franchisee', 'role': 'decision_maker', 'influence': 'high'}
            return {'type': 'owner_operator', 'role': 'decision_maker', 'influence': 'high'}
        elif any(kw in title for kw in ['developer', 'principal', 'partner']):
            return {'type': 'real_estate_developer', 'role': 'decision_maker', 'influence': 'high'}
        elif any(kw in title for kw in ['vp', 'vice president', 'director']):
            return {'type': 'executive', 'role': 'decision_maker', 'influence': 'high'}
        elif any(kw in title for kw in ['manager', 'managing']):
            return {'type': 'manager', 'role': 'influencer', 'influence': 'medium'}
        else:
            return {'type': 'professional', 'role': 'contributor', 'influence': 'medium'}
    
    def _detect_timing(self, contact: Dict, deep_data: Dict) -> Dict:
        """Detect WHEN to contact"""
        trigger_text = (deep_data.get('trigger_events', '') + ' ' + 
                       deep_data.get('recent_mentions', '') + ' ' +
                       deep_data.get('deals_database', '')).lower()
        
        urgent_keywords = ['lease expiring', 'closing soon', 'under contract', 'rate lock', 'just sold', 'just closed']
        if any(kw in trigger_text for kw in urgent_keywords):
            return {'signal': 'URGENT', 'urgency': 'high', 'best_time': 'immediately', 'cadence': 'daily'}
        
        active_keywords = ['looking at properties', 'evaluating options', 'expansion', 'new funding', 'recent deal']
        if any(kw in trigger_text for kw in active_keywords):
            return {'signal': 'ACTIVE', 'urgency': 'medium', 'best_time': 'within_24_hours', 'cadence': 'every_2_days'}
        
        return {'signal': 'WARMING', 'urgency': 'low', 'best_time': 'this_week', 'cadence': 'weekly'}
    
    def _generate_approach(self, contact: Dict, persona: Dict, timing: Dict, deep_data: Dict) -> Dict:
        """Generate WHAT to say based on enriched data"""
        # Extract key talking points from enrichment
        talking_points = deep_data.get('talking_points', '')
        recent_deals = deep_data.get('deals_database', '')
        
        # Generate personalized hook
        if recent_deals and 'sold' in recent_deals.lower():
            hook = f"Congrats on your recent deal! Saw the closing on LinkedIn"
        elif talking_points:
            hook = f"Noticed your expertise in {contact.get('industry', 'the market')}"
        else:
            hook = f"Your track record at {contact.get('company', 'your organization')} caught my attention"
        
        return {
            'hook': hook,
            'value_props': [
                "Competitive financing rates for commercial real estate",
                "SBA 504: 90% LTV with just 10% down",
                "Fast approval process with local decision-making"
            ],
            'questions': [
                "What type of properties are you currently working on?",
                "What's your typical timeline from contract to close?",
                "Have you worked with SBA financing before?"
            ],
            'objections': {
                'just_looking': "No pressure - let's just see what you qualify for",
                'rates_too_high': "SBA rates are fixed and competitive right now"
            },
            'cta': "Worth a quick 15-minute call to explore options?"
        }


# ============================================================================
# FULL ENRICHMENT ORCHESTRATOR
# ============================================================================

class FullEnrichmentEngine:
    """Master orchestrator - combines ALL enrichment modules"""
    
    def __init__(self, perplexity_key: str, db_path: str = './apex.db'):
        self.perplexity = PerplexityEnrichment(perplexity_key)
        self.kernel = KernelIntelligence()
        self.db_path = db_path
    
    def enrich_contact(self, contact_id: int) -> Dict:
        """Full enrichment pipeline"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM contacts WHERE id = ?", (contact_id,))
            contact_row = cursor.fetchone()
            
            if not contact_row:
                return {'success': False, 'error': 'Contact not found'}
            
            contact = dict(contact_row)
            
            print(f"\n   🚀 FULL ENRICHMENT: {contact['name']} ({contact['company']})")
            print(f"   " + "="*70)
            
            cursor.execute("""
                UPDATE contacts 
                SET enrichment_status = 'enriching', updated_at = ?
                WHERE id = ?
            """, (datetime.now().isoformat(), contact_id))
            conn.commit()
            
            # STAGE 1: Deep Perplexity (YOUR 11 QUESTIONS)
            print(f"   📊 Stage 1: Perplexity Deep Research (11-point profile)...")
            deep_data = self.perplexity.deep_enrich(contact)
            time.sleep(2)
            
            # STAGE 2: Kernel
            print(f"   🎯 Stage 2: Kernel Intelligence (WHO/WHEN/WHAT)...")
            kernel_data = self.kernel.generate_kernel(contact, deep_data)
            
            # STAGE 3: Outreach
            print(f"   ✉️  Stage 3: Generating outreach content...")
            outreach_data = self._generate_outreach(contact, deep_data, kernel_data)
            
            # STAGE 4: Scores
            print(f"   📈 Stage 4: Scoring...")
            scores = self._calculate_scores(contact, deep_data, kernel_data)
            
            full_enrichment = {
                **deep_data,
                'kernel': kernel_data,
                'outreach': outreach_data,
                'scores': scores,
                'enriched_at': datetime.now().isoformat()
            }
            
            cursor.execute("""
                UPDATE contacts SET
                    enrichment_status = 'complete',
                    enriched_at = ?,
                    enrichment_data = ?,
                    opportunity_score = ?,
                    lead_tier = ?,
                    persona_name = ?,
                    pain_points = ?,
                    updated_at = ?
                WHERE id = ?
            """, (
                full_enrichment['enriched_at'],
                json.dumps(full_enrichment),
                scores['opportunity_score'],
                scores['tier'],
                kernel_data['who']['persona_type'],
                deep_data.get('pain_points', '')[:5000],
                datetime.now().isoformat(),
                contact_id
            ))
            conn.commit()
            conn.close()
            
            print(f"   ✅ COMPLETE: Score {scores['opportunity_score']}/100, Tier: {scores['tier']}")
            print(f"   " + "="*70 + "\n")
            
            return {
                'success': True,
                'contact_id': contact_id,
                'enrichment': full_enrichment
            }
            
        except Exception as e:
            print(f"   ❌ Enrichment failed: {e}")
            import traceback
            traceback.print_exc()
            
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE contacts 
                    SET enrichment_status = 'failed', updated_at = ?
                    WHERE id = ?
                """, (datetime.now().isoformat(), contact_id))
                conn.commit()
                conn.close()
            except:
                pass
            
            return {'success': False, 'error': str(e)}
    
    def _generate_outreach(self, contact: Dict, deep_data: Dict, kernel_data: Dict) -> Dict:
        """Generate emails and call scripts"""
        name = contact.get('first_name', 'there')
        company = contact.get('company', 'your organization')
        hook = kernel_data['what']['opening_hook']
        value_props = kernel_data['what']['value_props']
        
        return {
            'emails': [
                {
                    'variant': 1,
                    'subject': hook,
                    'body': f"Hi {name},\n\n{hook}\n\n• {value_props[0]}\n• {value_props[1]}\n\n{kernel_data['what']['call_to_action']}\n\nBest"
                },
                {
                    'variant': 2,
                    'subject': f"Quick question about {company}",
                    'body': f"Hi {name},\n\nI specialize in helping companies like {company}.\n\n{value_props[0]}\n\nWorth a conversation?\n\nBest"
                },
                {
                    'variant': 3,
                    'subject': f"Financing options for {company}",
                    'body': f"Hi {name},\n\n{hook}\n\n{kernel_data['what']['call_to_action']}\n\nThanks"
                }
            ],
            'call_scripts': [
                {
                    'variant': 1,
                    'opening': f"Hi {name}, this is [Your Name]. {hook}",
                    'questions': kernel_data['what']['discovery_questions'],
                    'close': kernel_data['what']['call_to_action']
                },
                {
                    'variant': 2,
                    'opening': f"Hi {name}, calling about financing for {company}",
                    'questions': kernel_data['what']['discovery_questions'],
                    'close': "Can we schedule 15 minutes?"
                },
                {
                    'variant': 3,
                    'opening': f"Hey {name}, quick call about your recent activity",
                    'questions': kernel_data['what']['discovery_questions'],
                    'close': "Interested in learning more?"
                }
            ]
        }
    
    def _calculate_scores(self, contact: Dict, deep_data: Dict, kernel_data: Dict) -> Dict:
        """Calculate scores"""
        score = 50
        
        title = (contact.get('title') or '').lower()
        if any(kw in title for kw in ['ceo', 'president', 'owner', 'founder']):
            score += 25
        elif any(kw in title for kw in ['vp', 'director', 'managing']):
            score += 15
        
        if kernel_data['when']['urgency_level'] == 'high':
            score += 25
        elif kernel_data['when']['urgency_level'] == 'medium':
            score += 15
        
        # Boost score for recent deals
        if 'sold' in deep_data.get('deals_database', '').lower() or 'closed' in deep_data.get('deals_database', '').lower():
            score += 10
        
        if score >= 85:
            tier = 'HOT'
        elif score >= 70:
            tier = 'WARM'
        elif score >= 50:
            tier = 'QUALIFIED'
        else:
            tier = 'COLD'
        
        return {
            'opportunity_score': min(score, 100),  # Cap at 100
            'tier': tier,
            'confidence': kernel_data['when']['urgency_level']
        }


# ============================================================================
# SYNC WRAPPER FOR FASTAPI
# ============================================================================

def enrich_contact_full(contact_id: int, perplexity_key: str, db_path: str = './apex.db') -> Dict:
    """Synchronous wrapper for FastAPI endpoint"""
    engine = FullEnrichmentEngine(perplexity_key, db_path)
    return engine.enrich_contact(contact_id)
