#!/usr/bin/env python3
"""
Perplexity Deep Enrichment Module
Comprehensive person and company intelligence gathering
"""

import os
import json
import requests
from datetime import datetime
from typing import Dict, Optional

def enrich_contact(contact_id: int, contact: Dict, db_connection=None):
    """
    Main enrichment function that can be called from main.py

    Args:
        contact_id: Database ID of the contact
        contact: Dictionary with contact data
        db_connection: Optional database connection to use

    Returns:
        Dictionary with enrichment results
    """
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key:
        return {"status": "error", "message": "PERPLEXITY_API_KEY not set"}

    # Build contact details
    firstname = contact.get('firstname', '').strip()
    lastname = contact.get('lastname', '').strip()

    if firstname or lastname:
        name = f"{firstname} {lastname}".strip()
    elif contact.get('name'):
        name = contact.get('name').strip()
    else:
        name = ""

    company = contact.get('company', '').strip()
    title = contact.get('job_title', '') or contact.get('title', '')
    email = contact.get('email', '')
    linkedin = contact.get('linkedin_url', '') or contact.get('linkedin', '')

    print(f"🔍 Deep enriching:")
    print(f"   Name: {name if name else '[No name provided]'}")
    print(f"   Company: {company if company else '[No company]'}")
    print(f"   Title: {title if title else '[No title]'}")

    # Build the comprehensive prompt
    prompt = build_enrichment_prompt(name, company, title, email, linkedin)

    # Call Perplexity API
    enrichment_data = call_perplexity_api(prompt, api_key)

    if enrichment_data:
        # Extract key fields
        result = {
            "status": "success",
            "enrichment_data": enrichment_data,
            "pain_points": enrichment_data.get('pain_points', []),
            "talking_points": enrichment_data.get('talking_points', []),
            "myers_briggs": enrichment_data.get('myers_briggs', ''),
            "person_name": enrichment_data.get('person_name', name),
            "current_title": enrichment_data.get('current_title', title),
            "current_company": enrichment_data.get('current_company', company)
        }

        print(f"✅ Deep enrichment complete!")
        print(f"   Person: {result['person_name']}")
        print(f"   MBTI: {result['myers_briggs']}")

        return result
    else:
        return {"status": "error", "message": "Failed to get enrichment data"}

def build_enrichment_prompt(name: str, company: str, title: str, email: str, linkedin: str) -> str:
    """Build the comprehensive enrichment prompt"""

    if name and company:
        search_focus = f"{name} who works at {company}"
        if title:
            search_focus += f" as {title}"
    elif name:
        search_focus = f"professional named {name}"
    elif company:
        search_focus = f"contacts at {company}"
        if email:
            search_focus += f" particularly someone with email {email}"
    else:
        search_focus = "available information"

    prompt = f"""You are a B2B sales intelligence researcher. Your PRIMARY GOAL is to find detailed information about the PERSON, not just the company.

SEARCH TARGET: {search_focus}

Known Information:
- Name: {name if name else 'FIND THE PERSONS NAME'}
- Company: {company}
- Title: {title if title else 'FIND THEIR TITLE'}
- Email: {email}
- LinkedIn: {linkedin}

CRITICAL REQUIREMENTS:

1. PERSON PROFILE (MOST IMPORTANT):
   - Full name, current title, and responsibilities
   - Professional background and career history
   - Education and certifications
   - Recent activities and social media profiles
   - Professional interests and expertise

2. PERSONALITY & INTELLIGENCE:
   - Myers-Briggs personality assessment
   - Communication and decision-making style
   - Pain points specific to their role
   - Topics of interest and trigger events
   - Best approach methods

3. COMPANY INFORMATION:
   - Overview and products/services
   - Recent news and market position

Return findings as valid JSON with these fields:
{{
    "person_name": "Full name",
    "current_title": "Job title",
    "current_company": "Company",
    "overview": "Professional summary of the PERSON",
    "background": "Work history",
    "education": "Educational background",
    "recent_activities": "Recent posts or activities",
    "social_profiles": {{"linkedin": "", "twitter": "", "instagram": "", "facebook": ""}},
    "myers_briggs": "MBTI type",
    "personality_assessment": "Personality analysis",
    "communication_style": "How they communicate",
    "decision_style": "How they make decisions",
    "pain_points": ["Pain 1", "Pain 2", "Pain 3"],
    "talking_points": ["Topic 1", "Topic 2", "Topic 3"],
    "trigger_events": ["Event 1", "Event 2"],
    "budget_authority": "Purchasing power level",
    "best_contact_method": "Email/phone/LinkedIn",
    "best_contact_time": "When to reach them",
    "company_overview": "Company description",
    "products_services": "What company offers",
    "recent_company_news": "Latest developments",
    "market_position": "Industry standing",
    "ai_score_reasoning": "Why this is a high-value contact",
    "outreach_approach": "Personalized strategy"
}}"""

    return prompt

def call_perplexity_api(prompt: str, api_key: str) -> Optional[Dict]:
    """Call Perplexity API and parse response"""

    try:
        response = requests.post(
            "https://api.perplexity.ai/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.1-sonar-large-128k-online",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an expert B2B sales researcher. Prioritize finding information about the PERSON over the company. Return valid JSON only."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.1,
                "max_tokens": 4000,
                "return_citations": True,
                "search_recency_filter": "month"
            },
            timeout=60
        )

        if response.status_code == 200:
            content = response.json()['choices'][0]['message']['content']

            # Clean response
            content = content.replace("```json", "").replace("```", "").strip()
            if content.startswith('"') or content.startswith("'"):
                content = content[1:-1]

            try:
                return json.loads(content)
            except json.JSONDecodeError as e:
                print(f"⚠️ JSON parsing failed: {e}")
                return {
                    "overview": content[:500] if content else "Parse error",
                    "raw_response": content,
                    "parse_error": True
                }
        else:
            print(f"❌ Perplexity API error: {response.status_code}")
            return None

    except Exception as e:
        print(f"❌ API call failed: {e}")
        return None
