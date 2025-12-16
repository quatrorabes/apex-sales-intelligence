#!/usr/bin/env python3
"""
APEX Custom Enrichment Route - 4-Stage Pipeline

Architecture:
  Stage 1-3: Perplexity research (person, company, sales context)
  Stage 4:   GPT-4 structured parsing (clean, dash-ready sections)

Route: POST /api/contacts/{contact_id}/apex-enrich
"""

import os
import re
import time
import json
import logging
from typing import Dict, Any, Optional
from uuid import UUID

import requests
from openai import OpenAI
from fastapi import APIRouter, HTTPException, Depends
import psycopg2
from psycopg2.extras import RealDictCursor

logger = logging.getLogger("APEX_CUSTOM_ENRICHMENT")

router = APIRouter(prefix="/api/contacts", tags=["Enrichment"])

DATABASE_URL = os.getenv("DATABASE_URL")


def get_db():
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    try:
        yield conn
    finally:
        conn.close()


class ApexEnrichmentEngine:
    """
    4-Stage Enrichment: Perplexity research → GPT-4 parsing.
    Returns structured markdown with ## headers and - bullets.
    """

    SECTION_HEADERS = [
        "overview",
        "background_and_experience",
        "company_overview",
        "market_position",
        "leadership_and_culture",
        "recent_activity_and_news",
        "pain_points_and_challenges",
        "budget_and_authority",
        "personality_and_communication",
    ]

    def __init__(self) -> None:
        self.perplexity_key = os.getenv("PERPLEXITY_API_KEY")
        self.openai_key = os.getenv("OPENAI_API_KEY")

        if not self.perplexity_key:
            raise ValueError("PERPLEXITY_API_KEY not set")
        if not self.openai_key:
            raise ValueError("OPENAI_API_KEY not set")

        self.openai_client = OpenAI(api_key=self.openai_key)
        self.perplexity_url = "https://api.perplexity.ai/chat/completions"

        logger.info("✅ ApexEnrichmentEngine initialized (4-stage pipeline)")

    def enrich_contact(self, contact: Dict[str, Any]) -> Dict[str, Any]:
        """Main enrichment pipeline."""
        name = self._get_name(contact)
        company = contact.get("company", "") or ""
        title = contact.get("title", "") or ""
        linkedin = contact.get("linkedinurl") or contact.get("linkedin_url", "") or ""

        logger.info("=" * 70)
        logger.info("🔍 ENRICHING: %s at %s", name, company)
        logger.info("   Title: %s | LinkedIn: %s", title, linkedin[:50] if linkedin else "N/A")
        logger.info("=" * 70)

        try:
            # STAGE 1: Person profile
            logger.info("📡 STAGE 1: Person profile search...")
            person_data = self._search_person(name, company, linkedin)
            logger.info("   ✅ %d chars", len(person_data))
            time.sleep(1)

            # STAGE 2: Company intel
            logger.info("📡 STAGE 2: Company intelligence search...")
            company_data = self._search_company(company)
            logger.info("   ✅ %d chars", len(company_data))
            time.sleep(1)

            # STAGE 3: Sales context
            logger.info("📡 STAGE 3: Sales context search...")
            sales_data = self._search_sales_context(name, company, title)
            logger.info("   ✅ %d chars", len(sales_data))

            # Combine research
            combined = self._combine_research(name, company, person_data, company_data, sales_data)
            logger.info("📊 Combined research: %d chars", len(combined))

            # STAGE 4: GPT-4 structured parsing
            logger.info("🧠 STAGE 4: GPT-4 structured parsing...")
            structured = self._parse_with_gpt4(combined, contact)

            if not structured or len(structured) < 400:
                logger.warning("⚠️ GPT-4 output too short, using fallback")
                structured = combined if len(combined) > 400 else self._minimal_profile(contact)

            # Normalize and extract
            structured = self._normalize(structured)
            sections = self._extract_sections(structured)

            logger.info("✅ ENRICHMENT COMPLETE: %d chars, %d sections", len(structured), len(sections))
            logger.info("=" * 70)

            return {
                "success": True,
                "profile_text": structured,
                "character_count": len(structured),
                "profile_format": "v1",
                "sections": sections,
                "raw_research": combined,
            }

        except Exception as e:
            logger.error("❌ Enrichment failed: %s", e, exc_info=True)
            fallback = self._minimal_profile(contact)
            return {
                "success": False,
                "profile_text": fallback,
                "character_count": len(fallback),
                "profile_format": "v1",
                "sections": self._extract_sections(fallback),
                "raw_research": "",
            }

    # -------------------------------------------------------------------------
    # PERPLEXITY STAGES
    # -------------------------------------------------------------------------
    def _search_person(self, name: str, company: str, linkedin: str) -> str:
        if linkedin:
            query = f"{name} {company} site:linkedin.com OR {linkedin}"
        else:
            query = f"{name} {company} site:linkedin.com professional profile background education career"
        return self._perplexity(query, "person")

    def _search_company(self, company: str) -> str:
        query = f"{company} company news funding leadership products services market competitors recent announcements"
        return self._perplexity(query, "company")

    def _search_sales_context(self, name: str, company: str, title: str) -> str:
        query = f"{name} {title} {company} deals announcements achievements projects press challenges pain points"
        return self._perplexity(query, "sales")

    def _perplexity(self, query: str, label: str) -> str:
        headers = {
            "Authorization": f"Bearer {self.perplexity_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "sonar-pro",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a research assistant. Extract ALL relevant facts and details.",
                },
                {
                    "role": "user",
                    "content": f"Provide comprehensive information about: {query}",
                },
            ],
            "temperature": 0.1,
            "max_tokens": 2000,
            "return_citations": True,
            "search_recency_filter": "month",
        }
        try:
            resp = requests.post(self.perplexity_url, headers=headers, json=payload, timeout=60)
            resp.raise_for_status()
            data = resp.json()
            if "choices" not in data or not data["choices"]:
                return ""
            content = data["choices"][0]["message"]["content"]
            return content
        except Exception as e:
            logger.error("Perplexity %s search failed: %s", label, e)
            return ""

    # -------------------------------------------------------------------------
    # GPT-4 PARSING
    # -------------------------------------------------------------------------
    def _parse_with_gpt4(self, research: str, contact: Dict[str, Any]) -> str:
        name = self._get_name(contact)
        research = research[:12000]

        prompt = f"""
Using the research below, create a structured sales profile for {name}.

**RESEARCH:**
{research}

---

**Use EXACTLY these section headers with ## markdown:**

## overview
[2-3 sentences: current role, responsibilities, company context]

## background_and_experience
[Career history, achievements - bullet points with "-"]

## company_overview
[Company description, size, industry - bullet points]

## market_position
[Industry, competitors, advantages - bullet points]

## leadership_and_culture
[CEO/leadership, culture, values - bullet points]

## recent_activity_and_news
[Recent news, funding, launches - bullet points]

## pain_points_and_challenges
[Role-specific challenges - bullet points]

## budget_and_authority
[Decision-making power, budget - bullet points]

## personality_and_communication
[Communication style, traits - bullet points]

---

**RULES:**
- Use ONLY facts from research
- 3-5 bullet points per section max
- Use "-" for bullets (not * or numbers)
- If no data: "- Limited information available"
- No disclaimers or meta-commentary
"""

        try:
            resp = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a sales intelligence analyst. Be concise and factual."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.2,
                max_tokens=3000,
            )
            return resp.choices[0].message.content
        except Exception as e:
            logger.error("GPT-4 parsing failed: %s", e)
            return ""

    # -------------------------------------------------------------------------
    # HELPERS
    # -------------------------------------------------------------------------
    def _get_name(self, contact: Dict[str, Any]) -> str:
        name = contact.get("name") or ""
        if not name:
            first = contact.get("firstname") or contact.get("first_name") or ""
            last = contact.get("lastname") or contact.get("last_name") or ""
            name = f"{first} {last}".strip()
        return name or "Unknown"

    def _combine_research(self, name: str, company: str, person: str, company_data: str, sales: str) -> str:
        return (
            f"# Research: {name} at {company}\n\n"
            f"## Person Profile\n{person}\n\n"
            f"## Company Intel\n{company_data}\n\n"
            f"## Sales Context\n{sales}\n"
        )

    def _normalize(self, text: str) -> str:
        if not text:
            return text
        lines = []
        for line in text.splitlines():
            s = line.rstrip()
            if s.startswith("##") and not s.startswith("## ") and s != "##":
                s = "## " + s[2:].lstrip()
            if s.startswith("* "):
                s = "- " + s[2:]
            if s.startswith("• "):
                s = "- " + s[2:]
            s = re.sub(r"\[\d+\]", "", s)
            lines.append(s)
        return "\n".join(lines).strip()

    def _extract_sections(self, text: str) -> Dict[str, str]:
        sections = {}
        current = None
        buffer = []
        for line in text.splitlines():
            if line.startswith("## "):
                if current:
                    sections[current] = "\n".join(buffer).strip()
                current = line[3:].strip().lower().replace(" ", "_")
                buffer = []
            else:
                buffer.append(line)
        if current:
            sections[current] = "\n".join(buffer).strip()
        return sections

    def _minimal_profile(self, contact: Dict[str, Any]) -> str:
        name = self._get_name(contact)
        title = contact.get("title") or "Position unknown"
        company = contact.get("company") or "Company unknown"
        return f"""## overview
{name} - {title} at {company}

## background_and_experience
- Limited public information available

## company_overview
- {company}

## market_position
- Limited information available

## leadership_and_culture
- Limited information available

## recent_activity_and_news
- Limited information available

## pain_points_and_challenges
- Industry-standard challenges likely apply

## budget_and_authority
- {title} level suggests relevant authority

## personality_and_communication
- Limited information available
"""


# -----------------------------------------------------------------------------
# ROUTE
# -----------------------------------------------------------------------------
@router.post("/{contact_id}/apex-enrich")
async def apex_enrich_contact(contact_id: UUID):
    """4-stage Apex enrichment: Perplexity → GPT-4 parsing."""
    try:
        engine = ApexEnrichmentEngine()
    except Exception as e:
        logger.error("Failed to init engine: %s", e)
        raise HTTPException(status_code=503, detail="Enrichment engine unavailable")

    try:
        with next(get_db()) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM contacts WHERE id = %s", (str(contact_id),))
            contact = cursor.fetchone()
            if not contact:
                raise HTTPException(status_code=404, detail="Contact not found")

            cursor.execute("UPDATE contacts SET enrichment_status = 'enriching' WHERE id = %s", (str(contact_id),))
            conn.commit()

            contact_dict = dict(contact)
            result = engine.enrich_contact(contact_dict)

            # Save to DB
            enrichment_json = json.dumps({
                "profile_text": result["profile_text"],
                "sections": result["sections"],
                "profile_format": result["profile_format"],
            })

            cursor.execute("""
                UPDATE contacts SET
                    enrichment_status = 'completed',
                    enriched_at = NOW(),
                    enrichment_data = %s,
                    profile_context = %s
                WHERE id = %s
            """, (enrichment_json, result["profile_text"], str(contact_id)))
            conn.commit()
            cursor.close()

            return {
                "success": True,
                "contact_id": str(contact_id),
                "status": "completed",
                "sections_count": len(result["sections"]),
                "character_count": result["character_count"],
                "format": "v1",
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Enrichment failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
