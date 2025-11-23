#!/usr/bin/env python3
"""
Perplexity Deep Enrichment Module - Fixed for API 400 errors
"""

import os
import json
import requests
from datetime import datetime
from typing import Dict, Optional

class PerplexityEnrichment:
    """Handle all Perplexity enrichment operations"""

    def __init__(self, api_key: str = None):
        """Initialize with API key"""
        self.api_key = api_key or os.getenv("PERPLEXITY_API_KEY")
        if not self.api_key:
            raise ValueError("PERPLEXITY_API_KEY not set")

    def enrich_contact(self, contact: Dict) -> Dict:
        """Main enrichment function"""
        # Extract contact information
        person_info = self._extract_person_info(contact)

        # Build prompt
        prompt = self._build_prompt(person_info)

        # Call API
        raw_response = self._call_api(prompt)

        if not raw_response:
            return {
                "status": "error",
                "message": "Failed to get response from Perplexity"
            }

        # Parse response
        enrichment_data = self._parse_response(raw_response)

        # Structure results
        return {
            "status": "success",
            "enrichment_data": enrichment_data,
            "person_name": enrichment_data.get("person_name", person_info["name"]),
            "company_name": enrichment_data.get("current_company", person_info["company"]),
            "pain_points": enrichment_data.get("pain_points", []),
            "talking_points": enrichment_data.get("talking_points", []),
            "myers_briggs": enrichment_data.get("myers_briggs", ""),
            "overview": enrichment_data.get("overview", ""),
            "background": enrichment_data.get("background", ""),
            "trigger_events": enrichment_data.get("trigger_events", [])
        }

    def _extract_person_info(self, contact: Dict) -> Dict:
        """Extract person information from contact"""
        firstname = contact.get("firstname", "").strip() if contact.get("firstname") else ""
        lastname = contact.get("lastname", "").strip() if contact.get("lastname") else ""

        if firstname or lastname:
            name = f"{firstname} {lastname}".strip()
        elif contact.get("name"):
            name = contact.get("name").strip()
        else:
            name = ""

        return {
            "name": name,
            "firstname": firstname,
            "lastname": lastname,
            "company": contact.get("company", "").strip() if contact.get("company") else "",
            "title": contact.get("job_title", "") or contact.get("title", ""),
            "email": contact.get("email", ""),
            "linkedin": contact.get("linkedin_url", "") or contact.get("linkedin", ""),
            "phone": contact.get("phone", "")
        }

    def _build_prompt(self, person_info: Dict) -> str:
        """Build enrichment prompt - FIXED to avoid f-string JSON issues"""
        name = person_info["name"]
        company = person_info["company"]
        title = person_info["title"]
        email = person_info["email"]
        linkedin = person_info["linkedin"]

        # Determine search focus
        if name and company:
            search_focus = f"{name} who works at {company}"
            if title:
                search_focus += f" as {title}"
        elif name:
            search_focus = f"professional named {name}"
        elif company and email:
            search_focus = f"person at {company} with email {email}"
        elif company:
            search_focus = f"company {company} and their team"
        else:
            search_focus = "available information"

        # Build prompt without JSON in f-string
        prompt_text = f"""You are a B2B sales intelligence researcher. Find comprehensive information about BOTH the person AND company.

SEARCH TARGET: {search_focus}

AVAILABLE DATA:
- Name: {name if name else 'MUST FIND'}
- Company: {company if company else 'MUST FIND'}
- Title: {title if title else 'MUST FIND'}
- Email: {email}
- LinkedIn: {linkedin}

REQUIREMENTS:

PERSON PROFILE:
- Full name, current title, responsibilities
- Career history with dates
- Education and certifications
- Recent activities (posts, articles, speaking)
- Social media profiles
- Professional interests
- Awards and achievements

PERSONALITY ANALYSIS:
- Myers-Briggs type based on online presence
- Communication style
- Decision-making patterns
- Values and motivations

SALES INTELLIGENCE:
- Pain points specific to their role
- Challenges they face
- Talking points that resonate
- Trigger events for outreach
- Budget authority
- Best contact approach

COMPANY INTELLIGENCE:
- Overview (size, revenue, employees)
- Products and services
- Recent news and developments
- Technology stack
- Competitors
- Growth trajectory"""

        # Add JSON format separately to avoid f-string issues
        json_template = """

Return ONLY valid JSON with these fields:
{
    "person_name": "Full name of the person",
    "current_title": "Current job title",
    "current_company": "Company name",
    "email": "Email address",
    "phone": "Phone number",
    "location": "City, State/Country",
    "linkedin_url": "LinkedIn profile URL",
    "overview": "Professional summary of the person",
    "background": "Career history",
    "education": "Degrees and universities",
    "skills": ["Skill 1", "Skill 2"],
    "recent_activities": "Recent posts, articles, speaking",
    "achievements": "Awards and recognition",
    "social_profiles": {"linkedin": "", "twitter": "", "instagram": "", "facebook": ""},
    "professional_interests": ["Interest 1", "Interest 2"],
    "myers_briggs": "MBTI type (e.g., ENTJ)",
    "personality_assessment": "Personality analysis",
    "communication_style": "How they communicate",
    "decision_style": "How they make decisions",
    "pain_points": ["Pain point 1", "Pain point 2", "Pain point 3"],
    "talking_points": ["Topic 1", "Topic 2", "Topic 3"],
    "trigger_events": ["Event 1", "Event 2"],
    "budget_authority": "Purchasing influence level",
    "best_contact_method": "Email, phone, or LinkedIn",
    "best_contact_time": "When to reach them",
    "company_overview": "Company description",
    "products_services": "What company offers",
    "recent_company_news": "Latest developments",
    "technology_stack": ["Tech 1", "Tech 2"],
    "competitors": ["Competitor 1", "Competitor 2"],
    "ai_score": 85,
    "ai_score_reasoning": "Why this is a valuable contact",
    "outreach_approach": "Personalized outreach strategy"
}"""

        return prompt_text + json_template

    def _call_api(self, prompt: str) -> Optional[str]:
        """Call Perplexity API with better error handling"""
        try:
            # Log the request for debugging
            print(f"🔍 Calling Perplexity API...")
            print(f"   API Key: {'✅ Set' if self.api_key else '❌ Missing'}")
            print(f"   Prompt length: {len(prompt)} characters")

            response = requests.post(
                "https://api.perplexity.ai/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "sonar-pro",
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are an expert B2B sales researcher. Search the web for current information. Return ONLY valid JSON, no markdown formatting."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": 0.1,
                    "max_tokens": 4000
                },
                timeout=60
            )

            if response.status_code == 200:
                content = response.json()["choices"][0]["message"]["content"]
                print(f"✅ Perplexity API call successful")
                return content
            else:
                print(f"❌ Perplexity API error: {response.status_code}")
                print(f"   Response: {response.text[:500] if response.text else 'No response text'}")
                return None

        except Exception as e:
            print(f"❌ API call exception: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

    def _parse_response(self, response: str) -> Dict:
        """Parse and clean API response"""
        # Remove markdown formatting
        cleaned = response.replace("```json", "").replace("```", "").strip()

        # Remove quotes if wrapped
        if cleaned.startswith('"') or cleaned.startswith("'"):
            cleaned = cleaned[1:]
        if cleaned.endswith('"') or cleaned.endswith("'"):
            cleaned = cleaned[:-1]

        try:
            data = json.loads(cleaned)
            return data
        except json.JSONDecodeError as e:
            print(f"⚠️ Failed to parse JSON: {e}")
            print(f"   Response preview: {cleaned[:200]}...")

            # Return structured fallback
            return {
                "overview": cleaned[:500] if cleaned else "Parse error occurred",
                "raw_response": cleaned,
                "parse_error": True
            }


def enrich_contact(contact_id: int, contact: Dict) -> Dict:
    """Simple function interface for enrichment"""
    try:
        print(f"🚀 Starting enrichment for contact ID {contact_id}")

        # Log what data we have
        print(f"   Name: {contact.get('name', '[Missing]')}")
        print(f"   Company: {contact.get('company', '[Missing]')}")
        print(f"   Email: {contact.get('email', '[Missing]')}")

        enricher = PerplexityEnrichment()
        result = enricher.enrich_contact(contact)

        if result["status"] == "success":
            print(f"✅ Enrichment successful for ID {contact_id}")
        else:
            print(f"❌ Enrichment failed for ID {contact_id}: {result.get('message')}")

        return result

    except Exception as e:
        print(f"❌ Enrichment error for ID {contact_id}: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "status": "error",
            "message": str(e)
        }
