#!/usr/bin/env python3
"""
APEX Enrichment Engine - Production (4-Stage Pipeline)

Architecture:
  Stage 1-3: Perplexity research (raw data collection)
  Stage 4:   GPT-4 structured parsing (clean, dash-ready sections)

Module: enrichment_engine.py
Class:  EnhancedEnrichment
Method: enrich_contact(contact: dict) -> dict

Wiring: main.py imports via `from enrichment_engine import EnhancedEnrichment`
"""

import os
import re
import time
import logging
from typing import Dict, Any, Optional

import requests
from openai import OpenAI

logger = logging.getLogger(__name__)


class EnhancedEnrichment:
    """
    Production enrichment engine: Perplexity research → GPT-4 parsing.

    Returns structured markdown with ## headers and - bullets, ready for
    Dashboard_v1 ContactDetail rendering.
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

        logger.info("✅ EnhancedEnrichment initialized (4-stage pipeline)")

    # -------------------------------------------------------------------------
    # PUBLIC API
    # -------------------------------------------------------------------------
    def enrich_contact(self, contact: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main enrichment pipeline.

        Args:
            contact: dict with keys like name, company, title, linkedin_url

        Returns:
            {
                "success": True/False,
                "profile_text": "<structured markdown>",
                "character_count": int,
                "profile_format": "v1",
                "sections": { "overview": "...", ... },
                "raw_research": "<combined perplexity output>"
            }
        """
        name = self._get_name(contact)
        company = contact.get("company", "") or ""
        title = contact.get("title", "") or ""
        linkedin = contact.get("linkedinurl") or contact.get("linkedin_url", "") or ""

        logger.info("=" * 70)
        logger.info("🔍 ENRICHING: %s at %s", name, company)
        logger.info("   Title: %s | LinkedIn: %s", title, linkedin[:50] if linkedin else "N/A")
        logger.info("=" * 70)

        try:
            # STAGE 1: Person profile (Perplexity)
            logger.info("📡 STAGE 1: Person profile search...")
            person_data = self._search_person(name, company, linkedin)
            logger.info("   ✅ %d chars", len(person_data))
            time.sleep(1)

            # STAGE 2: Company intel (Perplexity)
            logger.info("📡 STAGE 2: Company intelligence search...")
            company_data = self._search_company(company)
            logger.info("   ✅ %d chars", len(company_data))
            time.sleep(1)

            # STAGE 3: Sales context (Perplexity)
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
                logger.warning("⚠️ GPT-4 output too short (%d chars), using fallback", len(structured or ""))
                structured = combined if len(combined) > 400 else self._minimal_profile(contact)

            # Normalize
            structured = self._normalize(structured)

            # Parse into sections dict for frontend
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
                    "content": (
                        "You are a research assistant. Extract ALL relevant facts, "
                        "context, and specific details from search results. Be thorough."
                    ),
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
            # Append citations
            if data.get("citations"):
                content += "\n\nSources:\n"
                for i, c in enumerate(data["citations"][:10], 1):
                    content += f"[{i}] {c}\n"
            return content
        except Exception as e:
            logger.error("Perplexity %s search failed: %s", label, e)
            return ""

    # -------------------------------------------------------------------------
    # GPT-4 PARSING
    # -------------------------------------------------------------------------
    def _parse_with_gpt4(self, research: str, contact: Dict[str, Any]) -> str:
        name = self._get_name(contact)
        company = contact.get("company", "Unknown")
        title = contact.get("title", "Unknown")

        # Truncate to fit context
        research = research[:12000]

        prompt = f"""
Using the research data below, create a structured sales intelligence profile for {name}.

**RESEARCH DATA:**
{research}

---

**Generate a profile with EXACTLY these section headers (use ## markdown):**

## overview
[2-3 sentences: current role, responsibilities, company context]

## background_and_experience
[Career history, achievements, expertise - bullet points with "-"]

## company_overview
[Company description, size, industry, business model - bullet points]

## market_position
[Industry, competitors, market advantages - bullet points]

## leadership_and_culture
[CEO/leadership, culture, values - bullet points]

## recent_activity_and_news
[Recent news, funding, launches, press - bullet points]

## pain_points_and_challenges
[Role-specific and industry challenges - bullet points]

## budget_and_authority
[Decision-making power, budget ownership - bullet points]

## personality_and_communication
[Communication style, professional traits - bullet points]

---

**RULES:**
- Use ONLY verifiable facts from research data
- 3-5 bullet points per section max
- Use "-" for bullets (not * or numbers)
- If no data, write "- Limited information available"
- No disclaimers or meta-commentary
- Be specific with names, dates, numbers
"""

        try:
            resp = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert sales intelligence analyst. Parse research into structured, actionable sections. Be concise and factual.",
                    },
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
            f"# Research Data for {name} at {company}\n\n"
            f"## Person Profile Data\n\n{person}\n\n"
            f"## Company Intelligence Data\n\n{company_data}\n\n"
            f"## Sales & Relationship Context\n\n{sales}\n"
        )

    def _normalize(self, text: str) -> str:
        """Normalize markdown: fix headers and bullets."""
        if not text:
            return text
        lines = []
        for line in text.splitlines():
            s = line.rstrip()
            # Fix header spacing
            if s.startswith("##") and not s.startswith("## ") and s != "##":
                s = "## " + s[2:].lstrip()
            # Normalize bullets
            if s.startswith("* "):
                s = "- " + s[2:]
            if s.startswith("• "):
                s = "- " + s[2:]
            # Remove citation brackets like [1][2]
            s = re.sub(r"\[\d+\]", "", s)
            lines.append(s)
        return "\n".join(lines).strip()

    def _extract_sections(self, text: str) -> Dict[str, str]:
        """Split profile_text into dict keyed by section header."""
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
- Direct research recommended

## company_overview
- {company}
- Further research needed

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
