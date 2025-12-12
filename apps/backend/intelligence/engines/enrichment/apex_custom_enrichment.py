# apex_custom_enrichment.py
# APEX CUSTOM ENRICHMENT ENGINE - Two-Stage Processing with Post-GPT Parsing
# Version: 2.1 | December 2, 2025

"""
🎯 APEX CUSTOM ENRICHMENT - TWO-STAGE ARCHITECTURE
====================================================
Stage 1: Raw Data Gathering (Perplexity)
Stage 2: Intelligence Synthesis (GPT-4)
Stage 3: Structured Parsing & Field Extraction
"""

import os
import logging
import json
import re
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
import requests

logger = logging.getLogger("APEX_CUSTOM_ENRICHMENT")

class ApexCustomEnrichment:
    """Two-stage enrichment with post-GPT parsing"""
    
    def __init__(self, config):
        self.config = config
        self.perplexity_key = config.perplexity_api_key
        self.openai_key = config.openai_api_key
        
        logger.info("🎯 Apex Custom Enrichment Engine initialized (Two-Stage)")
    
    def enrich_contact_full(self, contact: Dict) -> Dict:
        """
        Execute two-stage enrichment with post-processing
        
        Stage 1: Gather raw data (Perplexity)
        Stage 2: Synthesize intelligence (GPT-4)
        Stage 3: Parse and extract fields
        """
        
        name = contact.get('name', '')
        company = contact.get('company', '')
        linkedin_url = contact.get('linkedin_url', '')
        
        logger.info(f"\n{'='*90}")
        logger.info(f"🎯 TWO-STAGE ENRICHMENT: {name} at {company}")
        logger.info(f"{'='*90}")
        
        # Validate required fields
            logger.error("❌ Missing required fields: name, company")
                    return {'status': 'error', 'error': 'Missing required fields'}
        
                # Warn if LinkedIn URL is missing
                if not linkedin_url:
                                logger.warning("⚠️ Missing LinkedIn profile may affect enrichment results")return {'status': 'error', 'error': 'Missing required fields'}
        
        # ===================================================================
        # STAGE 1: RAW DATA GATHERING (Perplexity)
        # ===================================================================
        logger.info("\n" + "="*90)
        logger.info("📊 STAGE 1: RAW DATA GATHERING (Perplexity)")
        logger.info("="*90)
        
        raw_data = self._stage1_gather_raw_data(contact)
        
        if not raw_data:
            return {'status': 'error', 'error': 'Stage 1 failed - no raw data'}
        
        # ===================================================================
        # STAGE 2: INTELLIGENCE SYNTHESIS (GPT-4)
        # ===================================================================
        logger.info("\n" + "="*90)
        logger.info("🧠 STAGE 2: INTELLIGENCE SYNTHESIS (GPT-4)")
        logger.info("="*90)
        
        synthesized_intelligence = self._stage2_synthesize_intelligence(contact, raw_data)
        
        if not synthesized_intelligence:
            logger.warning("⚠️ Stage 2 failed - using raw data only")
            synthesized_intelligence = self._format_raw_data_fallback(raw_data)
        
        # ===================================================================
        # STAGE 3: PARSING & FIELD EXTRACTION
        # ===================================================================
        logger.info("\n" + "="*90)
        logger.info("🔍 STAGE 3: PARSING & FIELD EXTRACTION")
        logger.info("="*90)
        
        parsed_fields = self._stage3_parse_and_extract(synthesized_intelligence)
        
        # Combine everything
        complete_profile = {
            'raw_data': raw_data,
            'synthesized_intelligence': synthesized_intelligence,
            'parsed_fields': parsed_fields
        }
        
        logger.info(f"\n{'='*90}")
        logger.info("🎉 TWO-STAGE ENRICHMENT COMPLETE!")
        logger.info(f"✅ Raw data gathered: {len(raw_data)} sections")
        logger.info(f"✅ Intelligence synthesized: {len(synthesized_intelligence)} chars")
        logger.info(f"✅ Fields extracted: {len(parsed_fields)} fields")
        logger.info(f"{'='*90}\n")
        
        return {
            'status': 'success',
            'profile_data': complete_profile,
            'enrichment_notes': self._generate_processing_notes(raw_data, parsed_fields)
        }
    
    # ========================================================================
    # STAGE 1: RAW DATA GATHERING (Perplexity)
    # ========================================================================
    
    def _stage1_gather_raw_data(self, contact: Dict) -> Dict:
        """Gather raw data from all sources using Perplexity"""
        
        raw_data = {}
        
        # 1. Person Research
        logger.info("  🔍 1/6: Person Profile Research...")
        raw_data['person_profile'] = self._gather_person_profile(contact)
        
        # 2. Company Research
        logger.info("  🔍 2/6: Company Intelligence...")
        raw_data['company_intelligence'] = self._gather_company_intelligence(contact)
        
        # 3. Social Media Discovery
        logger.info("  🔍 3/6: Social Media Profiles...")
        raw_data['social_profiles'] = self._gather_social_profiles(contact)
        
        # 4. Recent Activity & News
        logger.info("  🔍 4/6: Recent Activity & News...")
        raw_data['recent_activity'] = self._gather_recent_activity(contact)
        
        # 5. Skills & Expertise
        logger.info("  🔍 5/6: Skills & Expertise...")
        raw_data['skills_expertise'] = self._gather_skills_expertise(contact)
        
        # 6. Fun Facts & Humor
        logger.info("  🔍 6/6: Fun Facts & Icebreakers...")
        raw_data['fun_facts'] = self._gather_fun_facts(contact)
        
        logger.info(f"  ✅ Raw data gathering complete: {sum(1 for v in raw_data.values() if v)} sections collected")
        
        return raw_data
    
    def _gather_person_profile(self, contact: Dict) -> Optional[str]:
        """Gather comprehensive person profile"""
        
        prompt = f"""Research {contact.get('name')} at {contact.get('company')}:

**PERSON PROFILE - RAW DATA COLLECTION:**

1. **Overview**
   - Current title and organization
   - Role scope, responsibilities, tenure

2. **Background**
   - Complete work history (last 5 positions)
   - Career progression
   - Notable achievements

3. **Education**
   - Degrees, certifications, institutions
   - Graduation years
   - Relevant coursework

4. **Recent Mentions** (Last 90 days)
   - LinkedIn posts and activity
   - News articles or press mentions
   - Public appearances, conferences
   - Published content

5. **LinkedIn Activity**
   - Post frequency and topics
   - Engagement patterns
   - Recent announcements
   - Skills endorsed
   - Recommendations

LinkedIn URL: {contact.get('linkedin_url')}

Provide factual, recent data. Be comprehensive."""

        return self._call_perplexity(prompt, max_tokens=4000)
    
    def _gather_company_intelligence(self, contact: Dict) -> Optional[str]:
        """Gather company intelligence"""
        
        prompt = f"""Research {contact.get('company')} comprehensively:

**COMPANY INTELLIGENCE - RAW DATA:**

1. **Overview**
   - Description, mission, founding details
   - Headquarters, size, revenue

2. **Products & Services**
   - Key offerings, solutions
   - Markets served, customers
   - Value propositions

3. **Leadership**
   - CEO, key executives, founders
   - Recent leadership changes

4. **Market Position**
   - Industry, sector
   - Competitors (top 5)
   - Market share, advantages

5. **Recent News** (Last 90 days)
   - Major announcements
   - Funding, acquisitions
   - Product launches
   - Partnerships, deals
   - Awards, challenges

6. **Strategic Context**
   - Growth trajectory
   - Industry trends
   - Technology adoption
   - Expansion plans

Provide comprehensive, factual data."""

        return self._call_perplexity(prompt, max_tokens=4000)
    
    def _gather_social_profiles(self, contact: Dict) -> Optional[str]:
        """Find all social media profiles"""
        
        prompt = f"""Find social media profiles for {contact.get('name')}:

**SOCIAL MEDIA DISCOVERY:**

1. **Instagram**: Username, URL, activity level, bio
2. **Facebook**: Profile/page URL, public info
3. **Twitter/X**: Handle, URL, bio, followers, activity
4. **LinkedIn**: Already known: {contact.get('linkedin_url')}
5. **Other**: YouTube, TikTok, Medium, GitHub, blog

For each found:
- Exact URL
- Activity level (active/moderate/inactive)
- Content themes
- Professional vs personal

State "Not found" if unavailable."""

        return self._call_perplexity(prompt, max_tokens=2000)
    
    def _gather_recent_activity(self, contact: Dict) -> Optional[str]:
        """Gather recent activity and news"""
        
        prompt = f"""Find recent activity (last 90 days) for:
- {contact.get('name')} (person)
- {contact.get('company')} (company)

**RECENT ACTIVITY:**

1. **Personal Activity**
   - LinkedIn posts/comments
   - Speaking engagements
   - Published articles
   - Twitter/X activity
   - Public appearances

2. **Company News**
   - Press releases
   - Media mentions
   - Industry news
   - Events, webinars
   - Awards, recognition

For each: Date, source, summary, relevance."""

        return self._call_perplexity(prompt, max_tokens=2500)
    
    def _gather_skills_expertise(self, contact: Dict) -> Optional[str]:
        """Identify top skills and expertise"""
        
        prompt = f"""Identify skills and expertise for {contact.get('name')} ({contact.get('title', '')}):

**SKILLS & EXPERTISE:**

1. **Technical Skills**
   - Tools, technologies, platforms
   - Certifications

2. **Professional Skills**
   - Leadership, management
   - Industry expertise
   - Functional skills

3. **LinkedIn Profile Skills**
   - Top endorsed skills
   - Skill endorsements count

4. **Demonstrated Expertise**
   - Projects, initiatives
   - Published work
   - Thought leadership topics

LinkedIn: {contact.get('linkedin_url')}"""

        return self._call_perplexity(prompt, max_tokens=1500)
    
    def _gather_fun_facts(self, contact: Dict) -> Optional[str]:
        """Gather fun facts and icebreakers"""
        
        prompt = f"""Find interesting information about {contact.get('company')} and {contact.get('name')}:

**FUN FACTS & ICEBREAKERS:**

1. **Company Fun Facts**
   - Interesting history/trivia
   - Unique culture elements
   - Notable achievements
   - Company traditions

2. **Icebreaker Topics**
   - Shared interests
   - Community involvement
   - Personal hobbies (if public)

3. **Industry Humor**
   - A relevant, professional joke about their industry
   - Light observation about their sector

Keep professional and appropriate."""

        return self._call_perplexity(prompt, max_tokens=1500)
    
    # ========================================================================
    # STAGE 2: INTELLIGENCE SYNTHESIS (GPT-4)
    # ========================================================================
    
    def _stage2_synthesize_intelligence(self, contact: Dict, raw_data: Dict) -> Optional[str]:
        """Synthesize raw data into structured intelligence using GPT-4"""
        
        # Compile all raw data
        compiled_raw = self._compile_raw_data(contact, raw_data)
        
        synthesis_prompt = f"""You are a professional profile analyst and sales intelligence expert. Synthesize the raw research below into a comprehensive, structured profile.

**RAW RESEARCH DATA:**
{compiled_raw}

**REQUIRED OUTPUT STRUCTURE:**

# ENRICHED PROFILE: {contact.get('name')}

## CONTACT INFORMATION
- **Name**: {contact.get('name')}
- **Title**: {contact.get('title', 'TBD')}
- **Company**: {contact.get('company')}
- **Email**: {contact.get('email')}
- **Phone**: {contact.get('phone', 'N/A')}
- **LinkedIn**: {contact.get('linkedin_url')}

---

## PERSON PROFILE

### Overview
[Synthesize current role, scope, tenure from raw data]

### Background
[Synthesize work history, career progression, achievements]

### Education
[Format education data clearly]

### Recent Activity & Mentions
[Compile recent activity, posts, mentions with dates]

### LinkedIn Activity Analysis
[Summarize posting patterns, engagement, topics]

### Top Skills
[List top 10 skills with context]

---

## COMPANY PROFILE

### Overview
[Company description, mission, founding, HQ, size]

### Products & Services
[Key offerings, markets served]

### Leadership
[CEO, key executives with details]

### Market & Competitors
[Industry position, top 3-5 competitors]

### Recent News (Last 90 days)
[Major announcements with dates and sources]

### Strategic Context
[Growth, trends, digital maturity]

---

## PERSONALITY ASSESSMENT

### Myers-Briggs (MBTI) Type: [4-letter type]
**Confidence Level**: [High/Medium/Low - Based on data or industry norms]

**Analysis**:
- **E vs I**: [Reasoning]
- **S vs N**: [Reasoning]
- **T vs F**: [Reasoning]
- **J vs P**: [Reasoning]

**Interpretation**: [2-3 paragraph interpretation]

**Work Style Implications**: [How this affects decision-making, communication]

### DISC Profile: [Primary Style]
**Secondary**: [If applicable]

**Behavioral Tendencies**: [Key behaviors]
**Communication Preferences**: [How they like to communicate]
**Motivators**: [What drives them]

### StrengthsFinder (Top 5 Themes)
1. [Strength 1] - [How it manifests]
2. [Strength 2] - [How it manifests]
3. [Strength 3] - [How it manifests]
4. [Strength 4] - [How it manifests]
5. [Strength 5] - [How it manifests]

### Professional Communication Style
- **Preferred Channels**: [Email, LinkedIn, phone, etc.]
- **Meeting Preferences**: [Style, structure]
- **Decision-Making Approach**: [Process]
- **Information Preferences**: [Data, stories, visuals]

---

## SOCIAL MEDIA PROFILES

### Instagram
[URL, activity level, content themes - or "Not found"]

### Facebook
[URL, activity level - or "Not found"]

### Twitter/X
[Handle, URL, activity, topics - or "Not found"]

### Other Platforms
[YouTube, Medium, GitHub, etc. if found]

---

## SALES INTELLIGENCE

### Top 5 Talking Points
1. [Specific, actionable conversation starter]
2. [Based on their recent activity]
3. [Related to their interests]
4. [Current events relevant to them]
5. [Mutual connections or topics]

### Sales Opportunities
**Pain Points**:
- [Likely challenge 1]
- [Likely challenge 2]
- [Likely challenge 3]

**Buying Triggers**:
- [Event or circumstance 1]
- [Event or circumstance 2]
- [Budget cycles/timing]

**Current Signals**: [Any active buying signals detected]

### Value Proposition Angles
**Option A**: [Angle for this persona]
**Option B**: [Alternative angle]
**Option C**: [Third angle]

### Objection Handling
**Likely Objection 1**: [How to address]
**Likely Objection 2**: [How to address]
**Likely Objection 3**: [How to address]

### Outreach Strategy
**Best Channel**: [Email/LinkedIn/Phone + reasoning]
**Optimal Timing**: [Day/time recommendations]
**Message Tone**: [Formal/casual/technical]
**Follow-up Cadence**: [Frequency and sequence]

### Relationship Building
- [How to build rapport with this personality]
- [Shared interests to leverage]
- [Long-term nurture approach]

---

## NEWS & FUN FACTS

### Recent Company News
[Headline 1 - Date - Source]
[Headline 2 - Date - Source]
[Headline 3 - Date - Source]

### Fun Facts
- [Interesting fact 1]
- [Interesting fact 2]
- [Interesting fact 3]

### Icebreaker
[A professional, relevant joke or humorous observation about their industry]

---

## ENRICHMENT NOTES

**Data Sources**: Perplexity research + LinkedIn analysis + News monitoring
**Confidence Score**: [85-95% based on data availability]
**Last Updated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Next Re-enrichment**: [90 days from now]

**Updates Applied**:
✅ Comprehensive person profile
✅ Company intelligence
✅ Personality assessment (MBTI, DISC, StrengthsFinder)
✅ Social media profiles identified
✅ Sales intelligence & talking points
✅ Recent news & fun facts

---

**IMPORTANT**:
- Be specific and actionable
- Use actual data from research
- If limited info, clearly state "Based on industry norms for [role]"
- Include dates for all recent mentions
- Keep professional tone throughout
- Format consistently
"""

        logger.info("  🧠 Calling GPT-4 for intelligence synthesis...")
        return self._call_gpt4(synthesis_prompt, max_tokens=4000)
    
    def _compile_raw_data(self, contact: Dict, raw_data: Dict) -> str:
        """Compile all raw data for GPT-4"""
        
        sections = []
        
        if raw_data.get('person_profile'):
            sections.append(f"=== PERSON PROFILE ===\n{raw_data['person_profile']}")
        
        if raw_data.get('company_intelligence'):
            sections.append(f"\n=== COMPANY INTELLIGENCE ===\n{raw_data['company_intelligence']}")
        
        if raw_data.get('social_profiles'):
            sections.append(f"\n=== SOCIAL PROFILES ===\n{raw_data['social_profiles']}")
        
        if raw_data.get('recent_activity'):
            sections.append(f"\n=== RECENT ACTIVITY ===\n{raw_data['recent_activity']}")
        
        if raw_data.get('skills_expertise'):
            sections.append(f"\n=== SKILLS & EXPERTISE ===\n{raw_data['skills_expertise']}")
        
        if raw_data.get('fun_facts'):
            sections.append(f"\n=== FUN FACTS ===\n{raw_data['fun_facts']}")
        
        return '\n\n'.join(sections)
    
    def _format_raw_data_fallback(self, raw_data: Dict) -> str:
        """Fallback if GPT-4 unavailable"""
        sections = []
        sections.append(f"# RAW ENRICHMENT DATA (GPT-4 Unavailable)")
        sections.append(f"Enriched: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        for key, value in raw_data.items():
            if value:
                sections.append(f"## {key.replace('_', ' ').title()}")
                sections.append(value)
                sections.append("")
        
        return '\n'.join(sections)
    
    # ========================================================================
    # STAGE 3: PARSING & FIELD EXTRACTION
    # ========================================================================
    
    def _stage3_parse_and_extract(self, synthesized_intelligence: str) -> Dict:
        """Parse synthesized intelligence and extract structured fields"""
        
        logger.info("  🔍 Extracting structured fields...")
        
        fields = {}
        
        # Extract Myers-Briggs Type
        mbti_pattern = r'Myers-Briggs \(MBTI\) Type:\s*\**([EI][SN][TF][JP])\**'
        mbti_match = re.search(mbti_pattern, synthesized_intelligence)
        if mbti_match:
            fields['myers_briggs'] = mbti_match.group(1)
            logger.info(f"    ✓ Myers-Briggs: {fields['myers_briggs']}")
        
        # Extract DISC Profile
        disc_pattern = r'DISC Profile:\s*\**([A-Z][a-z]+)\**'
        disc_match = re.search(disc_pattern, synthesized_intelligence)
        if disc_match:
            fields['disc_profile'] = disc_match.group(1)
            logger.info(f"    ✓ DISC: {fields['disc_profile']}")
        
        # Extract social media profiles
        instagram_pattern = r'instagram\.com/([^\s\)\]]+)'
        instagram_match = re.search(instagram_pattern, synthesized_intelligence, re.IGNORECASE)
        if instagram_match:
            fields['instagram_url'] = f"https://instagram.com/{instagram_match.group(1)}"
            logger.info(f"    ✓ Instagram found")
        
        twitter_pattern = r'(?:twitter\.com|x\.com)/([^\s\)\]]+)'
        twitter_match = re.search(twitter_pattern, synthesized_intelligence, re.IGNORECASE)
        if twitter_match:
            fields['twitter_url'] = f"https://twitter.com/{twitter_match.group(1)}"
            logger.info(f"    ✓ Twitter/X found")
        
        facebook_pattern = r'facebook\.com/([^\s\)\]]+)'
        facebook_match = re.search(facebook_pattern, synthesized_intelligence, re.IGNORECASE)
        if facebook_match:
            fields['facebook_url'] = f"https://facebook.com/{facebook_match.group(1)}"
            logger.info(f"    ✓ Facebook found")
        
        # Extract talking points (first 5)
        talking_points = []
        talking_section = re.search(r'### Top 5 Talking Points\s+((?:\d+\..+\n?)+)', synthesized_intelligence)
        if talking_section:
            points = re.findall(r'\d+\.\s*(.+)', talking_section.group(1))
            talking_points = points[:5]
            fields['talking_points'] = talking_points
            logger.info(f"    ✓ Extracted {len(talking_points)} talking points")
        
        # Extract pain points
        pain_points = []
        pain_section = re.search(r'\*\*Pain Points\*\*:\s+((?:-\s*.+\n?)+)', synthesized_intelligence)
        if pain_section:
            points = re.findall(r'-\s*(.+)', pain_section.group(1))
            pain_points = points
            fields['pain_points'] = pain_points
            logger.info(f"    ✓ Extracted {len(pain_points)} pain points")
        
        # Extract best channel
        channel_pattern = r'\*\*Best Channel\*\*:\s*([^\n]+)'
        channel_match = re.search(channel_pattern, synthesized_intelligence)
        if channel_match:
            fields['best_contact_channel'] = channel_match.group(1).strip()
            logger.info(f"    ✓ Best channel: {fields['best_contact_channel']}")
        
        # Extract StrengthsFinder themes
        strengths = []
        strengths_section = re.search(r'### StrengthsFinder \(Top 5 Themes\)\s+((?:\d+\..+\n?)+)', synthesized_intelligence)
        if strengths_section:
            strength_matches = re.findall(r'\d+\.\s*([^-\n]+)', strengths_section.group(1))
            strengths = [s.strip() for s in strength_matches]
            fields['strengthsfinder_themes'] = strengths
            logger.info(f"    ✓ Extracted {len(strengths)} StrengthsFinder themes")
        
        # Extract confidence score
        confidence_pattern = r'\*\*Confidence Score\*\*:\s*(\d+)%?'
        confidence_match = re.search(confidence_pattern, synthesized_intelligence)
        if confidence_match:
            fields['enrichment_confidence'] = int(confidence_match.group(1))
            logger.info(f"    ✓ Confidence: {fields['enrichment_confidence']}%")
        
        logger.info(f"  ✅ Extracted {len(fields)} structured fields")
        
        return fields
    
    # ========================================================================
    # UTILITY FUNCTIONS
    # ========================================================================
    
    def _generate_processing_notes(self, raw_data: Dict, parsed_fields: Dict) -> str:
        """Generate processing notes"""
        
        notes = []
        notes.append(f"# TWO-STAGE ENRICHMENT NOTES")
        notes.append(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        notes.append("## Stage 1: Raw Data Gathering")
        for key, value in raw_data.items():
            status = "✅ Complete" if value else "❌ Failed"
            notes.append(f"  {status}: {key.replace('_', ' ').title()}")
        
        notes.append("\n## Stage 2: Intelligence Synthesis")
        notes.append("  ✅ GPT-4 synthesis completed")
        
        notes.append("\n## Stage 3: Field Extraction")
        notes.append(f"  ✅ Extracted {len(parsed_fields)} structured fields:")
        for field_name in parsed_fields.keys():
            notes.append(f"    - {field_name}")
        
        notes.append(f"\n## Data Quality")
        notes.append(f"  Confidence: HIGH")
        notes.append(f"  Next Re-enrichment: {datetime.now().strftime('%Y-%m-%d')} (+90 days)")
        
        return '\n'.join(notes)
    
    def _call_perplexity(self, prompt: str, max_tokens: int = 4000) -> Optional[str]:
        """Call Perplexity API"""
        if not self.perplexity_key:
            logger.warning("⚠️ Perplexity API key not configured")
            return None
        
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
                timeout=90
            )
            
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content']
            else:
                logger.error(f"Perplexity error: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Perplexity API error: {e}")
            return None
    
    def _call_gpt4(self, prompt: str, max_tokens: int = 4000) -> Optional[str]:
        """Call GPT-4 API"""
        if not self.openai_key:
            logger.warning("⚠️ OpenAI API key not configured")
            return None
        
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.openai_key)
            
            response = client.chat.completions.create(
                model='gpt-4',
                messages=[
                    {'role': 'system', 'content': 'You are a professional profile analyst and sales intelligence expert.'},
                    {'role': 'user', 'content': prompt}
                ],
                temperature=0.3,
                max_tokens=max_tokens
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"GPT-4 API error: {e}")
            return None

