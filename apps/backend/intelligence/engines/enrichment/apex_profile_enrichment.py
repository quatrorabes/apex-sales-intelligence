#!/usr/bin/env python3
"""
APEX PROFILE ENRICHMENT ENGINE

Pipeline:
- Stage 1: Perplexity raw research (your exact prompt style)
- Stage 2: OpenAI GPT-4 structuring into numbered sections:
    1–7: Person profile
    8:   Company overview
    8.1–8.5: Company sub-sections
    9–11: Sales intelligence
- Stage 3: Parse sections into structured fields

This module is imported by api.py; endpoints call it, not inline code.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any
from datetime import datetime
import os
import re
import requests


@dataclass
class ContactSeed:
    name: str
    linkedin_url: str
    company: str
    email: str
    phone: str


@dataclass
class ParsedProfile:
    # Full GPT text used by the Dossier tab
    full_text: str

    # Person-focused sections
    overview: str = ""
    background: str = ""
    education: str = ""
    recent_mentions: str = ""
    social_profiles: str = ""
    personality_detail: str = ""
    mb_summary: str = ""

    # Company-focused sections (8 + 8.x)
    company_overview: str = ""
    company_products_services: str = ""
    company_leadership: str = ""
    company_market_competitors: str = ""
    company_recent_news: str = ""
    company_fun_facts: str = ""

    # Sales / CRM / deals intelligence
    sales_talking_points: str = ""
    deals_history: str = ""
    fun_facts: str = ""


class ApexProfileEnrichmentEngine:
    def __init__(self, perplexity_key: str, openai_key: str, logger=None):
        if not perplexity_key:
            raise ValueError("PERPLEXITY_API_KEY not set")
        if not openai_key:
            raise ValueError("OPENAI_API_KEY not set")

        self.perplexity_key = perplexity_key
        self.openai_key = openai_key
        self.logger = logger

    # ─────────────────────────────────────────
    # PUBLIC ENTRY POINT
    # ─────────────────────────────────────────
    def enrich(self, seed: ContactSeed) -> ParsedProfile:
        self._log(f"[ENRICH] {seed.name} / {seed.company}")

        raw_research = self._call_perplexity(seed)
        self._log(f"[Perplexity] chars={len(raw_research)}")

        gpt_text = self._call_openai(seed, raw_research)
        self._log(f"[OpenAI] chars={len(gpt_text)}")

        parsed = self._parse_sections(gpt_text)
        return parsed

    # ─────────────────────────────────────────
    # STAGE 1 – PERPLEXITY (YOUR EXACT PROMPT)
    # ─────────────────────────────────────────
    def _build_perplexity_prompt(self, seed: ContactSeed) -> str:
        return f"""
build a professional profile for {seed.name}, {seed.linkedin_url}, {seed.email}, {seed.phone}, using the instructions contained within.

You are a professional profile-building assistant. generate up-to-date profile using sources such as LinkedIn & Internet. Once output is generated, update the contact in Hubspot. Make new note in file noting the updates/new information
For a company, structure the profile as:
1. Overview – Description, mission, founding details, and HQ
2. Products & Services – Key offerings and markets served
3. Leadership – Key executives and founders
4. Market & Competitors – Industry, position, key competitors
5. Recent News – Major announcements, deals, or product launches
6. Use Bryant’s LinkedIn activity and closing data in sales pitches and CRM enrichment. 
7. Identify top skills highlighted in Bryant Smiths profile
For a person, structure the profile as:
1. Overview – Current title and organization
2. Background – Work history, notable achievements
3. Education – Degrees and institutions
4. Recent Mentions – Any news, public appearances, LinkedIn posts, or online presence
5. find instagram, facebook, and twitter user profiles.
6. Personality Detail - perform a Myers briggs assessment.
7. Compose and interpret Myers-Briggs Personality assessment summary. 
8. Evaluate potential talking points regarding sales opportunities.
9. Search deals database for any past or current “deal”
10. Update all fields with new or inaccurate information 
11.  Find any relevant company news or fun facts. Populate results in "talking points" tab and on relevant company page.
""".strip()

    def _call_perplexity(self, seed: ContactSeed) -> str:
        url = "https://api.perplexity.ai/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.perplexity_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "sonar-pro",
            "messages": [{"role": "user", "content": self._build_perplexity_prompt(seed)}],
            "max_tokens": 3000,
            "temperature": 0.6,
        }
        resp = requests.post(url, headers=headers, json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]

    # ─────────────────────────────────────────
    # STAGE 2 – OPENAI (STRUCTURE & NUMBERING)
    # ─────────────────────────────────────────
    def _build_openai_prompt(self, seed: ContactSeed, research: str) -> str:
        return f"""
You are an expert sales intelligence analyst.

Below is raw research about a contact, generated from LinkedIn and the open web.

CONTACT CONTEXT:
- Name: {seed.name}
- Company: {seed.company}
- Email: {seed.email}
- Phone: {seed.phone}
- LinkedIn: {seed.linkedin_url or "Not provided"}

RAW RESEARCH:
{research}

STRUCTURE THIS INTO CLEAR, NUMBERED SECTIONS EXACTLY AS FOLLOWS:

1. Overview
2. Background
3. Education
4. Recent Mentions & Online Presence
5. Social profiles
6. Personality Detail (Myers-Briggs – inferred)
7. Myers-Briggs summary & interpretation

8. Company Overview
8.1 Products & Services
8.2 Leadership
8.3 Market & Competitors
8.4 Recent News
8.5 Company Fun Facts

9. Sales opportunity talking points
10. Deals history & CRM enrichment notes
11. Fun facts & company-related talking points

RULES:
- Use plain text only (no JSON, no markdown code fences).
- Start each section with its number and title exactly (e.g., "1. Overview", "8.1 Products & Services").
- Do not invent data; if something is not found, state that clearly.
- Do not add extra sections beyond 1–11.
""".strip()

    def _call_openai(self, seed: ContactSeed, research: str) -> str:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.openai_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "gpt-4",
            "messages": [{"role": "user", "content": self._build_openai_prompt(seed, research)}],
            "temperature": 0.5,
            "max_tokens": 3500,
        }
        resp = requests.post(url, headers=headers, json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]

    # ─────────────────────────────────────────
    # STAGE 3 – PARSE NUMBERED SECTIONS
    # ─────────────────────────────────────────
    def _parse_sections(self, text: str) -> ParsedProfile:
        # Pattern captures 1., 8., 8.1, 8.2, etc.
        pattern = re.compile(r"(?m)^\s*(\d+(?:\.\d+)?)\.\s+([^\n]+)\n")
        matches = list(pattern.finditer(text))
        blocks: Dict[str, str] = {}

        if not matches:
            return ParsedProfile(full_text=text, overview=text)

        for i, m in enumerate(matches):
            key = m.group(1)           # e.g., "1", "8.1"
            start = m.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            body = text[start:end].strip()
            blocks[key] = body

        def g(k: str) -> str:
            return blocks.get(k, "").strip()

        return ParsedProfile(
            full_text=text,
            overview=g("1"),
            background=g("2"),
            education=g("3"),
            recent_mentions=g("4"),
            social_profiles=g("5"),
            personality_detail=g("6"),
            mb_summary=g("7"),
            company_overview=g("8"),
            company_products_services=g("8.1"),
            company_leadership=g("8.2"),
            company_market_competitors=g("8.3"),
            company_recent_news=g("8.4"),
            company_fun_facts=g("8.5"),
            sales_talking_points=g("9"),
            deals_history=g("10"),
            fun_facts=g("11"),
        )

    # ─────────────────────────────────────────
    # LOGGING
    # ─────────────────────────────────────────
    def _log(self, msg: str):
        if self.logger:
            self.logger.info(msg)
        else:
            print(msg)
