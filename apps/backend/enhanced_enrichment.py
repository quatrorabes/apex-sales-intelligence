#!/usr/bin/env python3
"""
APEX Enrichment Engine - Multi-Stage Strategy (Apex-compatible)

Dec 16, 2025

Architecture:
- Stage 1-3: Perplexity research (raw data collection)
- Stage 4: GPT-4 structured parsing (clean sections, dash-ready)

This version is aligned with the existing apps/backend/main.py wiring:
- Class name: EnhancedEnrichment
- Public method: enrich_contact(contact: dict) -> dict
- Returns a dict suitable to persist into contacts.enrichmentdata/profile_context
"""

import os
import time
import logging
from typing import Dict, Any

import requests
from openai import OpenAI

logger = logging.getLogger(__name__)


class EnhancedEnrichment:
    """Multi-stage enrichment: Perplexity research → GPT-4 structured parsing."""

    def __init__(self) -> None:
        self.perplexity_key = os.getenv("PERPLEXITY_API_KEY")
        self.openai_key = os.getenv("OPENAI_API_KEY")

        if not self.perplexity_key:
            raise ValueError("PERPLEXITY_API_KEY not set")

        if not self.openai_key:
            raise ValueError("OPENAI_API_KEY not set")

        self.openai_client = OpenAI(api_key=self.openai_key)
        self.perplexity_url = "https://api.perplexity.ai/chat/completions"

        logger.info("✅ EnhancedEnrichment initialized")

    # --------------------------------------------------------------------- #
    # PUBLIC ENTRYPOINT
    # --------------------------------------------------------------------- #
    def enrich_contact(self, contact: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main enrichment pipeline with 4-stage search.

        Expected usage (from apps/backend/main.py or routes):
            engine = EnhancedEnrichment()
            result = engine.enrich_contact(contact_dict)

        Returns:
            {
              "success": True/False,
              "profile_text": "<markdown with ## sections and - bullets>",
              "character_count": int,
              "profile_format": "v1",
              "raw_research": "<optional combined research blob>"
            }
        """
        name = contact.get("name") or f"{contact.get('firstname', '')} {contact.get('lastname', '')}".strip()
        company = contact.get("company", "")
        title = contact.get("title", "")
        linkedin = contact.get("linkedinurl") or contact.get("linkedin_url", "")

        logger.info("=" * 70)
        logger.info("🔍 ENRICHING CONTACT")
        logger.info(" Name: %s", name)
        logger.info(" Company: %s", company)
        logger.info(" Title: %s", title)
        logger.info(" LinkedIn: %s", linkedin)
        logger.info("=" * 70)

        try:
            # STAGE 1: Person Research (Perplexity)
            logger.info("📡 STAGE 1: Person profile search...")
            person_data = self._search_person(name, company, linkedin)
            logger.info(" ✅ Person data length: %d chars", len(person_data))
            time.sleep(1)

            # STAGE 2: Company Research (Perplexity)
            logger.info("📡 STAGE 2: Company intelligence search...")
            company_data = self._search_company(company)
            logger.info(" ✅ Company data length: %d chars", len(company_data))
            time.sleep(1)

            # STAGE 3: Sales Context (Perplexity)
            logger.info("📡 STAGE 3: Sales context search...")
            sales_data = self._search_sales_context(name, company, title)
            logger.info(" ✅ Sales context length: %d chars", len(sales_data))

            # Combine all research
            combined_research = (
                f"# Research Data for {name} at {company}\n\n"
                "## Person Profile Data\n\n"
                f"{person_data}\n\n"
                "## Company Intelligence Data\n\n"
                f"{company_data}\n\n"
                "## Sales & Relationship Context\n\n"
                f"{sales_data}\n"
            )
            logger.info("📊 Total combined research: %d chars", len(combined_research))

            # STAGE 4: Parse with GPT-4 into structured, dash-ready profile
            logger.info("🧠 STAGE 4: Parsing with GPT-4 into structured profile...")
            structured_profile = self._parse_with_gpt4(combined_research, contact)

            # Guardrails: if parsing fails or is too short, fall back
            if not structured_profile or len(structured_profile) < 500:
                logger.warning(
                    "⚠️ Short or empty structured profile (%d chars). Falling back to minimal profile.",
                    len(structured_profile) if structured_profile else 0,
                )
                structured_profile = (
                    combined_research
                    if len(combined_research) > 500
                    else self._create_minimal_profile(contact)
                )

            # Optional: normalize headers and bullets (light touch)
            structured_profile = self._normalize_profile(structured_profile)

            logger.info("✅ ENRICHMENT COMPLETE: %d chars", len(structured_profile))
            logger.info("=" * 70)

            return {
                "success": True,
                "profile_text": structured_profile,
                "character_count": len(structured_profile),
                "profile_format": "v1",
                "raw_research": combined_research,
            }

        except Exception as e:
            logger.error("❌ Enrichment failed: %s", e, exc_info=True)
            fallback = self._create_minimal_profile(contact)
            return {
                "success": False,
                "profile_text": fallback,
                "character_count": len(fallback),
                "profile_format": "v1",
                "raw_research": "",
            }

    # --------------------------------------------------------------------- #
    # PERPLEXITY STAGES
    # --------------------------------------------------------------------- #
    def _search_person(self, name: str, company: str, linkedin: str) -> str:
        """Stage 1: LinkedIn-focused person search."""
        if linkedin:
            query = f"{name} {company} site:linkedin.com OR {linkedin}"
        else:
            query = (
                f"{name} {company} site:linkedin.com professional profile "
                f"background education career"
            )
        return self._perplexity_search(query, "person profile")

    def _search_company(self, company: str) -> str:
        """Stage 2: Company news and intelligence."""
        query = (
            f"{company} company news funding leadership team products services "
            f"market competitors recent announcements"
        )
        return self._perplexity_search(query, "company intelligence")

    def _search_sales_context(self, name: str, company: str, title: str) -> str:
        """Stage 3: Person+company combined context."""
        query = (
            f"{name} {title} {company} deals announcements achievements projects "
            f"press mentions challenges pain points"
        )
        return self._perplexity_search(query, "sales context")

    def _perplexity_search(self, query: str, search_type: str) -> str:
        """Execute a Perplexity search and return raw results."""
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
                        "You are a comprehensive research assistant. Extract ALL "
                        "relevant information from search results. Be thorough and "
                        "detailed. Include facts, context, and specific details."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Provide comprehensive, detailed information about: {query}\n\n"
                        "Include all available facts, context, background, and specific "
                        "details."
                    ),
                },
            ],
            "temperature": 0.1,
            "max_tokens": 2000,
            "return_citations": True,
            "search_recency_filter": "month",
        }

        try:
            response = requests.post(
                self.perplexity_url,
                headers=headers,
                json=payload,
                timeout=60,
            )
            response.raise_for_status()
            data = response.json()

            if "choices" not in data or not data["choices"]:
                logger.warning("⚠️ No results for %s", search_type)
                return ""

            content = data["choices"][0]["message"]["content"]

            # Append citations as simple sources list (optional)
            if "citations" in data and data["citations"]:
                content += "\n\nSources:\n"
                for i, citation in enumerate(data["citations"][:10], start=1):
                    content += f"[{i}] {citation}\n"

            return content

        except Exception as e:
            logger.error("❌ Perplexity search failed for %s: %s", search_type, e)
            return ""

    # --------------------------------------------------------------------- #
    # GPT-4 PARSING STAGE
    # --------------------------------------------------------------------- #
    def _parse_with_gpt4(self, research_data: str, contact: Dict[str, Any]) -> str:
        """
        Stage 4: Use GPT-4 to parse raw research into structured sections.

        Output is markdown with EXACT section headers and '-' bullets only.
        This is designed to be rendered directly in Dashboard_v1 or split
        by headers in ContactDetail.
        """
        name = contact.get("name", "Unknown")
        company = contact.get("company", "Unknown Company")
        title = contact.get("title", "Unknown Title")

        # Truncate research to fit within GPT-4's context window
        # Leave room for prompt (~1500 tokens) + response (up to ~3000 tokens).
        max_research_chars = 12000  # ~3000 tokens
        truncated_research = research_data[:max_research_chars]

        prompt = f"""
Using the research data below, create a structured sales intelligence profile for {name}.

**RESEARCH DATA:**

{truncated_research}

---

**Generate a profile with EXACTLY these section headers (include the ## markdown):**

## overview
[2-3 sentences summarizing current role, key responsibilities, and company context]

## background_and_experience
[Career history, achievements, expertise - use bullet points with "-"]

## company_overview
[Company description, size, industry, business model - bullet points]

## market_position
[Industry category, competitors, market advantages - bullet points]

## leadership_and_culture
[CEO/leadership team, company culture, values - bullet points]

## recent_activity_and_news
[Recent company news, funding, launches, press - bullet points]

## pain_points_and_challenges
[Role-specific and industry challenges they face - bullet points]

## budget_and_authority
[Decision-making power, budget ownership, procurement influence - bullet points]

## personality_and_communication
[Inferred communication style, professional traits, preferences - bullet points]

---

**CRITICAL RULES:**
- Use ONLY verifiable facts from the research data.
- Keep each section concise (3-5 bullet points maximum).
- Use the EXACT section headers shown above with ##.
- Use "-" for bullet points, not "*" or numbers.
- If a section lacks data, write "- Limited information available".
- No disclaimers, apologies, or meta-commentary.
- Be specific with names, dates, numbers, and companies.
"""

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an expert sales intelligence analyst. "
                            "Parse research into structured, actionable sections "
                            "using the exact headers provided. Be concise and factual."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.2,
                max_tokens=3000,
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error("❌ GPT-4 parsing failed: %s", e, exc_info=True)
            return ""

    # --------------------------------------------------------------------- #
    # NORMALIZATION + FALLBACK
    # --------------------------------------------------------------------- #
    def _normalize_profile(self, text: str) -> str:
        """
        Light normalization pass so ContactDetail gets clean markdown.

        - Ensures headers start with '## '.
        - Ensures bullets start with '- '.
        - Strips leading/trailing whitespace.
        """
        if not text:
            return text

        lines = text.splitlines()
        normalized = []

        for line in lines:
            stripped = line.rstrip()

            # Normalize headers that look like '##header' -> '## header'
            if stripped.startswith("##") and not stripped.startswith("###"):
                if stripped.startswith("## ") or stripped == "##":
                    normalized.append(stripped)
                else:
                    normalized.append("## " + stripped[2:].lstrip())
                continue

            # Normalize bullets: '* ' or '• ' -> '- '
            if stripped.startswith("* "):
                normalized.append("- " + stripped[2:])
                continue
            if stripped.startswith("• "):
                normalized.append("- " + stripped[2:])
                continue

            normalized.append(stripped)

        return "\n".join(normalized).strip()

    def _create_minimal_profile(self, contact: Dict[str, Any]) -> str:
        """Fallback minimal profile if everything else fails."""
        name = contact.get("name", "Unknown")
        title = contact.get("title", "Position unknown")
        company = contact.get("company", "Company unknown")

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
