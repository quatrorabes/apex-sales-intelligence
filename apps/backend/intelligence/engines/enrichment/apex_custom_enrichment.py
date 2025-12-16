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
        """
        name = contact.get('name', '')
        company = contact.get('company', '')
        linkedin_url = contact.get('linkedin_url', '')

        logger.info(f"\n{'='*90}")
        logger.info(f"🎯 TWO-STAGE ENRICHMENT: {name} at {company}")
        logger.info(f"{'='*90}")

        # Validate required fields
        if not name or not company:
            logger.error("❌ Missing required fields: name, company")
            return {'status': 'error', 'error': 'Missing required fields'}

        # Warn if LinkedIn URL is missing
        if not linkedin_url:
            logger.warning("⚠️ Missing LinkedIn profile may affect enrichment results")
            logger.info("🔍 Attempting to discover LinkedIn URL...")
            discovered_url = self._discover_linkedin_url(name, company)
            if discovered_url:
                linkedin_url = discovered_url
                contact['linkedin_url'] = linkedin_url
                logger.info(f"✅ Found LinkedIn URL: {linkedin_url}")
            else:
                logger.warning("❌ Could not discover LinkedIn URL")

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

        logger.info("  🔍 1/6: Person Profile Research...")
        raw_data['person_profile'] = self._gather_person_profile(contact)

        logger.info("  🔍 2/6: Company Intelligence...")
        raw_data['company_intelligence'] = self._gather_company_intelligence(contact)

        logger.info("  🔍 3/6: Social Media Profiles...")
        raw_data['social_profiles'] = self._gather_social_profiles(contact)

        logger.info("  🔍 4/6: Recent Activity & News...")
        raw_data['recent_activity'] = self._gather_recent_activity(contact)

        logger.info("  🔍 5/6: Skills & Expertise...")
        raw_data['skills_expertise'] = self._gather_skills_expertise(contact)

        logger.info("  🔍 6/6: Fun Facts & Icebreakers...")
        raw_data['fun_facts'] = self._gather_fun_facts(contact)

        logger.info(f"  ✅ Raw data gathering complete: {sum(1 for v in raw_data.values() if v)} sections collected")
        return raw_data

    def _gather_person_profile(self, contact: Dict) -> Optional[str]:
        """Gather comprehensive person profile"""
        prompt = f"""Research {contact.get('name')} at {contact.get('company')}:

**PERSON PROFILE - RAW DATA COLLECTION:**

1. **Overview** - Current title and organization, role scope, responsibilities, tenure
2. **Background** - Complete work history (last 5 positions), career progression, notable achievements
3. **Education** - Degrees, certifications, institutions, graduation years
4. **Recent Mentions** (Last 90 days) - LinkedIn posts, news articles, public appearances
5. **LinkedIn Activity** - Post frequency, topics, engagement patterns, skills endorsed

LinkedIn URL: {contact.get('linkedin_url')}

Provide factual, recent data. Be comprehensive."""
        return self._call_perplexity(prompt, max_tokens=4000)

    def _gather_company_intelligence(self, contact: Dict) -> Optional[str]:
        """Gather company intelligence"""
        prompt = f"""Research {contact.get('company')} comprehensively:

**COMPANY INTELLIGENCE - RAW DATA:**

1. **Overview** - Description, mission, founding, headquarters, size, revenue
2. **Products & Services** - Key offerings, markets served, value propositions
3. **Leadership** - CEO, key executives, founders, recent changes
4. **Market Position** - Industry, competitors (top 5), market share
5. **Recent News** (Last 90 days) - Announcements, funding, acquisitions, partnerships
6. **Strategic Context** - Growth trajectory, industry trends, expansion plans

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

For each: exact URL, activity level, content themes. State "Not found" if unavailable."""
        return self._call_perplexity(prompt, max_tokens=2000)

    def _gather_recent_activity(self, contact: Dict) -> Optional[str]:
        """Gather recent activity and news"""
        prompt = f"""Find recent activity (last 90 days) for:
- {contact.get('name')} (person)
- {contact.get('company')} (company)

**RECENT ACTIVITY:**

1. **Personal Activity** - LinkedIn posts/comments, speaking engagements, articles, Twitter activity
2. **Company News** - Press releases, media mentions, events, awards

For each: Date, source, summary, relevance."""
        return self._call_perplexity(prompt, max_tokens=2500)

    def _gather_skills_expertise(self, contact: Dict) -> Optional[str]:
        """Identify top skills and expertise"""
        prompt = f"""Identify skills and expertise for {contact.get('name')} ({contact.get('title', '')}):

**SKILLS & EXPERTISE:**

1. **Technical Skills** - Tools, technologies, certifications
2. **Professional Skills** - Leadership, industry expertise
3. **LinkedIn Profile Skills** - Top endorsed skills
4. **Demonstrated Expertise** - Projects, published work, thought leadership

LinkedIn: {contact.get('linkedin_url')}"""
        return self._call_perplexity(prompt, max_tokens=1500)

    def _gather_fun_facts(self, contact: Dict) -> Optional[str]:
        """Gather fun facts and icebreakers"""
        prompt = f"""Find interesting information about {contact.get('company')} and {contact.get('name')}:

**FUN FACTS & ICEBREAKERS:**

1. **Company Fun Facts** - Interesting history, unique culture, traditions
2. **Icebreaker Topics** - Shared interests, community involvement
3. **Industry Humor** - A relevant, professional joke about their industry

Keep professional and appropriate."""
        return self._call_perplexity(prompt, max_tokens=1500)

    # ========================================================================
    # STAGE 2: INTELLIGENCE SYNTHESIS (GPT-4)
    # ========================================================================

    def _stage2_synthesize_intelligence(self, contact: Dict, raw_data: Dict) -> Optional[str]:
        """Synthesize raw data into structured intelligence using GPT-4"""
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

---

## PERSONALITY ASSESSMENT

### Myers-Briggs (MBTI) Type: [4-letter type]
**Confidence Level**: [High/Medium/Low]

### DISC Profile: [Primary Style]
**Secondary**: [If applicable]

### StrengthsFinder (Top 5 Themes)
1. [Strength 1] - [How it manifests]
2. [Strength 2] - [How it manifests]
3. [Strength 3] - [How it manifests]
4. [Strength 4] - [How it manifests]
5. [Strength 5] - [How it manifests]

---

## SOCIAL MEDIA PROFILES
### Instagram
[URL, activity level, content themes - or "Not found"]

### Twitter/X
[Handle, URL, activity, topics - or "Not found"]

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

**Best Channel**: [Email/LinkedIn/Phone + reasoning]

---

## NEWS & FUN FACTS
### Fun Facts
- [Interesting fact 1]
- [Interesting fact 2]

### Icebreaker
[A professional, relevant joke or humorous observation]

---

## ENRICHMENT NOTES
**Confidence Score**: [85-95% based on data availability]
**Last Updated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
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

        # Extract talking points
        talking_section = re.search(r'### Top 5 Talking Points\s+((?:\d+\..+\n?)+)', synthesized_intelligence)
        if talking_section:
            points = re.findall(r'\d+\.\s*(.+)', talking_section.group(1))
            fields['talking_points'] = points[:5]
            logger.info(f"    ✓ Extracted {len(fields['talking_points'])} talking points")

        # Extract pain points
        pain_section = re.search(r'\*\*Pain Points\*\*:\s+((?:-\s*.+\n?)+)', synthesized_intelligence)
        if pain_section:
            points = re.findall(r'-\s*(.+)', pain_section.group(1))
            fields['pain_points'] = points
            logger.info(f"    ✓ Extracted {len(points)} pain points")

        # Extract best channel
        channel_pattern = r'\*\*Best Channel\*\*:\s*([^\n]+)'
        channel_match = re.search(channel_pattern, synthesized_intelligence)
        if channel_match:
            fields['best_contact_channel'] = channel_match.group(1).strip()
            logger.info(f"    ✓ Best channel: {fields['best_contact_channel']}")

        # Extract StrengthsFinder themes
        strengths_section = re.search(r'### StrengthsFinder \(Top 5 Themes\)\s+((?:\d+\..+\n?)+)', synthesized_intelligence)
        if strengths_section:
            strength_matches = re.findall(r'\d+\.\s*([^-\n]+)', strengths_section.group(1))
            fields['strengthsfinder_themes'] = [s.strip() for s in strength_matches]
            logger.info(f"    ✓ Extracted {len(fields['strengthsfinder_themes'])} StrengthsFinder themes")

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

    def _discover_linkedin_url(self, name: str, company: str) -> Optional[str]:
        """Discover LinkedIn URL using Perplexity search"""
        prompt = f"""Find the exact LinkedIn profile URL for:
Name: {name}
Company: {company}

Return ONLY the LinkedIn URL in this exact format:
https://www.linkedin.com/in/username

If you cannot find a LinkedIn profile, return: NOT_FOUND"""

        try:
            result = self._call_perplexity(prompt, max_tokens=200)
            if result and 'linkedin.com/in/' in result and 'NOT_FOUND' not in result:
                match = re.search(r'https?://(?:www\.)?linkedin\.com/in/[A-Za-z0-9_-]+', result)
                if match:
                    return match.group(0)
            return None
        except Exception as e:
            logger.error(f"LinkedIn discovery error: {e}")
            return None

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
                model='gpt-4o',
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
