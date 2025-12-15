"""
APEX Structured Enrichment Engine v1.0
Outputs validated JSON matching EnrichmentSchema
"""
import json
import os
from datetime import datetime
from typing import Optional
import httpx

# Import schema
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from schemas.enrichment_schema import EnrichmentData, Contact

PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
PERPLEXITY_URL = "https://api.perplexity.ai/chat/completions"

# =============================================================================
# STRUCTURED PROMPT - Forces JSON output matching our schema
# =============================================================================
ENRICHMENT_PROMPT = '''You are an AI sales intelligence analyst. Research the following contact and return ONLY valid JSON matching this exact structure. No markdown, no explanation, just JSON.

CONTACT:
Name: {first_name} {last_name}
Title: {title}
Company: {company}
Email: {email}

REQUIRED JSON STRUCTURE:
{{
  "version": "1.0",
  "generated_at": "{timestamp}",
  "professional": {{
    "executive_summary": "2-3 sentence overview of this person's professional background",
    "current_role": {{
      "title": "{title}",
      "company": "{company}",
      "tenure": "estimated tenure or null",
      "responsibilities": ["responsibility 1", "responsibility 2", "responsibility 3"]
    }},
    "career_trajectory": {{
      "previous_roles": ["Previous Role 1 at Company", "Previous Role 2 at Company"],
      "industry_experience": ["Industry 1", "Industry 2"],
      "expertise_areas": ["Expertise 1", "Expertise 2", "Expertise 3"]
    }},
    "education": ["Degree, University"],
    "achievements": ["Notable achievement 1", "Notable achievement 2"],
    "community_involvement": ["Community involvement if any"]
  }},
  "company": {{
    "overview": {{
      "name": "{company}",
      "industry": "Industry category",
      "business_model": "Brief description of what the company does",
      "founded": "Year or null",
      "headquarters": "City, State",
      "employee_count": "Approximate count or range"
    }},
    "financials": {{
      "revenue": "Revenue if public/known or null",
      "growth_rate": "Growth info if available",
      "funding": "Funding info if available",
      "key_metrics": ["Key metric 1", "Key metric 2"]
    }},
    "market_position": {{
      "target_market": "Who they serve",
      "competitive_advantages": ["Advantage 1", "Advantage 2"],
      "competitors": ["Competitor 1", "Competitor 2"]
    }},
    "recent_news": ["Recent news item 1", "Recent news item 2"],
    "strategic_priorities": ["Priority 1", "Priority 2"]
  }},
  "sales": {{
    "match_score": 75,
    "match_reasoning": "Why this contact is a good fit for commercial lending services",
    "pain_points": [
      {{"title": "Pain Point Title", "description": "Description of the pain", "priority": "high"}}
    ],
    "opportunities": [
      {{"title": "Opportunity Title", "description": "The opportunity", "alignment": "How we can help"}}
    ],
    "buying_triggers": ["Trigger 1", "Trigger 2"],
    "decision_factors": ["Factor 1", "Factor 2"],
    "objections": [
      {{"objection": "Likely objection", "response": "How to handle it"}}
    ],
    "why_now": "Why this is a good time to reach out",
    "why_us": "Why they should choose us over alternatives"
  }},
  "personality": {{
    "mbti": {{
      "type": "XXXX",
      "dimensions": [
        {{"dimension": "Energy", "preference": "E/I - Label", "evidence": "Why you think this"}}
      ]
    }},
    "disc": {{
      "primary": "X - Label",
      "secondary": "X - Label"
    }},
    "communication_style": {{
      "preferences": ["Preference 1", "Preference 2"],
      "dos": ["Do this", "Do that"],
      "donts": ["Don't do this", "Don't do that"]
    }},
    "best_opening_approach": "Suggested opening line or approach"
  }},
  "outreach": {{
    "talking_points": ["Talking point 1", "Talking point 2", "Talking point 3"],
    "call_scripts": [
      {{"level": 1, "script": "Initial cold call script"}},
      {{"level": 2, "script": "Follow-up call script"}},
      {{"level": 3, "script": "Closing call script"}}
    ],
    "email_templates": [
      {{"type": "initial", "subject": "Subject line", "body": "Email body"}},
      {{"type": "followup", "subject": "Follow-up subject", "body": "Follow-up body"}}
    ],
    "linkedin_message": "LinkedIn connection message",
    "voicemail_script": "Voicemail script"
  }}
}}

Research this contact thoroughly and return ONLY the JSON. Fill in all fields with real researched data. For fields you cannot find information for, use reasonable inferences based on role/industry or null.'''


async def enrich_contact(
    first_name: str,
    last_name: str,
    title: str = "",
    company: str = "",
    email: str = ""
) -> Optional[EnrichmentData]:
    """
    Enrich a contact using Perplexity AI and return structured JSON.
    """
    if not PERPLEXITY_API_KEY:
        raise ValueError("PERPLEXITY_API_KEY not set")
    
    prompt = ENRICHMENT_PROMPT.format(
        first_name=first_name,
        last_name=last_name,
        title=title or "Unknown",
        company=company or "Unknown",
        email=email or "Unknown",
        timestamp=datetime.utcnow().isoformat() + "Z"
    )
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            PERPLEXITY_URL,
            headers={
                "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.1-sonar-large-128k-online",
                "messages": [
                    {"role": "system", "content": "You are a JSON-only response bot. Return only valid JSON, no markdown, no explanation."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.1,
                "max_tokens": 4000
            }
        )
        
        if response.status_code != 200:
            print(f"❌ Perplexity API error: {response.status_code}")
            print(response.text)
            return None
        
        result = response.json()
        content = result["choices"][0]["message"]["content"]
        
        # Clean up response - remove markdown if present
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()
        
        try:
            data = json.loads(content)
            # Validate against schema
            enrichment = EnrichmentData(**data)
            return enrichment
        except json.JSONDecodeError as e:
            print(f"❌ JSON parse error: {e}")
            print(f"Raw content: {content[:500]}...")
            return None
        except Exception as e:
            print(f"❌ Schema validation error: {e}")
            return None


def enrich_contact_sync(
    first_name: str,
    last_name: str,
    title: str = "",
    company: str = "",
    email: str = ""
) -> Optional[EnrichmentData]:
    """Synchronous wrapper for enrich_contact"""
    import asyncio
    return asyncio.run(enrich_contact(first_name, last_name, title, company, email))


# =============================================================================
# TEST
# =============================================================================
if __name__ == "__main__":
    import asyncio
    
    async def test():
        result = await enrich_contact(
            first_name="Ed",
            last_name="Colunga",
            title="VP Relationship Manager",
            company="SunWest Bank",
            email="ecolunga@sunwestbank.com"
        )
        if result:
            print("✅ Enrichment successful!")
            print(json.dumps(result.model_dump(), indent=2)[:2000])
        else:
            print("❌ Enrichment failed")
    
    asyncio.run(test())
