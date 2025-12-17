#!/usr/bin/env bash
set -euo pipefail

echo "======================================================================"
echo "ROLLBACK: enrichment_parser + enrichment_integration to prior versions"
echo "======================================================================"

# From repo root
# (If you run this elsewhere, cd into the repo first)
if [ ! -d "apps/backend/services" ]; then
  echo "❌ Expected apps/backend/services not found. Run from repo root."
  exit 1
fi

TS="$(date +%Y%m%d_%H%M%S)"

echo ""
echo "Step 1: Backup current files (timestamp: $TS)"
cp -v apps/backend/services/enrichment_parser.py "apps/backend/services/enrichment_parser.py.rollback_backup_${TS}" || true
cp -v apps/backend/services/enrichment_integration.py "apps/backend/services/enrichment_integration.py.rollback_backup_${TS}" || true

echo ""
echo "Step 2: Restore PRIOR parser (class-based v2.1)"
cat > apps/backend/services/enrichment_parser.py << 'PARSEREOF'
#!/usr/bin/env python3
"""
APEX Enrichment Parser v2.1 - Production
Parses raw enrichment profiles into structured sections
Handles BOTH old and NEW formats from apex_custom_enrichment.py
"""

import re
from typing import Dict, Optional, Any

class EnrichmentParser:
    """Parse raw enrichment profiles into structured sections"""

    def parse(self, raw_profile: str) -> Dict[str, Any]:
        """
        Main parsing function - auto-detects format

        Returns:
        {
            "sections": {
                "overview": "text...",
                "company_overview": "text...",
                "pain_points_and_challenges": "text...",
                "budget_and_authority": "text...",
                ...
            },
            "metadata": {
                "total_sections": 12,
                "character_count": 8500,
                "format_detected": "markdown_structured"
            }
        }
        """
        if not raw_profile or not isinstance(raw_profile, str):
            return self._empty_result()

        # Detect format
        if ("---" in raw_profile and "Professional Profile" in raw_profile):
            format_type = "markdown_structured"
            sections = self._parse_markdown_structured(raw_profile)
        elif "===" in raw_profile and "PERSON RESEARCH" in raw_profile:
            format_type = "triple_equals"
            sections = self._parse_triple_equals(raw_profile)
        else:
            format_type = "unknown"
            sections = {"raw_text": raw_profile}

        return {
            "sections": sections,
            "metadata": {
                "total_sections": len(sections),
                "character_count": len(raw_profile),
                "format_detected": format_type
            }
        }

    def _parse_markdown_structured(self, text: str) -> Dict[str, str]:
        """Parse NEW format from apex_custom_enrichment.py Stage 2"""
        sections = {}

        # Split by main section headers (###)
        main_pattern = r'###\s+(.+?)\n(.*?)(?=###|$)'
        main_matches = re.findall(main_pattern, text, re.DOTALL)

        for header, content in main_matches:
            header_clean = header.strip()

            # Map sections to frontend keys
            if "PERSON PROFILE" in header_clean or "Professional Profile" in header_clean:
                # Parse person subsections
                subsections = self._parse_subsections(content)

                # Map to frontend keys
                if "Overview" in subsections:
                    sections["overview"] = subsections["Overview"]
                if "Background" in subsections:
                    sections["person_background"] = subsections["Background"]
                if "Education" in subsections:
                    sections["person_education"] = subsections["Education"]
                if "Recent Activity" in subsections or "Recent Activity Mentions" in subsections:
                    sections["recent_activity"] = subsections.get("Recent Activity", subsections.get("Recent Activity Mentions", ""))
                if "LinkedIn Activity" in subsections:
                    sections["linkedin_activity"] = subsections["LinkedIn Activity"]
                if "Top Skills" in subsections:
                    sections["skills_expertise"] = subsections["Top Skills"]

            elif "COMPANY PROFILE" in header_clean or "Company Intelligence" in header_clean:
                # Parse company subsections
                subsections = self._parse_subsections(content)

                if "Overview" in subsections:
                    sections["company_overview"] = subsections["Overview"]
                if "Products" in subsections or "Products Services" in subsections:
                    sections["company_products"] = subsections.get("Products", subsections.get("Products Services", ""))
                if "Leadership" in subsections:
                    sections["company_leadership"] = subsections["Leadership"]
                if "Market" in subsections or "Market Competitors" in subsections:
                    sections["company_market"] = subsections.get("Market", subsections.get("Market Competitors", ""))
                if "Recent News" in subsections:
                    sections["company_news"] = subsections["Recent News"]
                if "Strategic Context" in subsections:
                    sections["company_strategy"] = subsections["Strategic Context"]

            elif "PERSONALITY ASSESSMENT" in header_clean:
                subsections = self._parse_subsections(content)

                # Store full personality section
                sections["personality_analysis"] = content.strip()

                # Extract specific personality fields
                if "Myers-Briggs" in subsections or "MBTI" in subsections:
                    sections["personality_mbti"] = subsections.get("Myers-Briggs", subsections.get("MBTI", ""))
                if "DISC" in subsections:
                    sections["personality_disc"] = subsections["DISC"]
                if "StrengthsFinder" in subsections:
                    sections["personality_strengths"] = subsections["StrengthsFinder"]
                if "Communication Style" in subsections or "Professional Communication Style" in subsections:
                    sections["communication_style"] = subsections.get("Communication Style", subsections.get("Professional Communication Style", ""))

            elif "SALES INTELLIGENCE" in header_clean or "SALES OPPORTUNITIES" in header_clean:
                subsections = self._parse_subsections(content)

                # Store full sales intelligence
                sections["sales_intelligence"] = content.strip()

                # Extract specific sales fields
                if "Top" in subsections and "Talking Points" in subsections:
                    sections["talking_points"] = subsections.get("Top 5 Talking Points", "")
                if "Sales Opportunities" in subsections:
                    sections["sales_opportunities"] = subsections["Sales Opportunities"]

                    # Parse pain points from sales opportunities
                    if "Pain Points" in subsections["Sales Opportunities"]:
                        pain_match = re.search(r'Pain Points?:(.+?)(?=\n\w+:|$)', subsections["Sales Opportunities"], re.DOTALL)
                        if pain_match:
                            sections["pain_points_and_challenges"] = pain_match.group(1).strip()

                    # Parse budget/authority
                    if "Budget" in subsections["Sales Opportunities"] or "Authority" in subsections["Sales Opportunities"]:
                        budget_match = re.search(r'(Budget|Authority).+', subsections["Sales Opportunities"], re.DOTALL)
                        if budget_match:
                            sections["budget_and_authority"] = budget_match.group(0).strip()

                if "Value Proposition" in subsections:
                    sections["value_propositions"] = subsections.get("Value Proposition Angles", "")
                if "Objection" in subsections:
                    sections["objection_handling"] = subsections.get("Objection Handling", "")
                if "Relationship Building" in subsections:
                    sections["relationship_building"] = subsections["Relationship Building"]
                if "Outreach Strategy" in subsections:
                    sections["outreach_strategy"] = subsections["Outreach Strategy"]

            elif "SOCIAL MEDIA PROFILES" in header_clean:
                sections["social_profiles"] = content.strip()

            elif "NEWS" in header_clean or "FUN FACTS" in header_clean:
                subsections = self._parse_subsections(content)

                if "Fun Facts" in subsections:
                    sections["fun_facts"] = subsections["Fun Facts"]
                if "Icebreaker" in subsections:
                    sections["icebreaker"] = subsections["Icebreaker"]
                if "Recent Company News" in subsections or "Company News" in subsections:
                    sections["company_news"] = subsections.get("Recent Company News", subsections.get("Company News", ""))

            elif "ENRICHMENT NOTES" in header_clean:
                sections["enrichment_notes"] = content.strip()
            else:
                # Generic catch-all
                key = header_clean.lower().replace(" ", "_").replace(",", "").replace("-", "_")
                sections[key] = content.strip()

        return sections

    def _parse_subsections(self, content: str) -> Dict[str, str]:
        """Parse subsections within a section (#### headers)"""
        subsections = {}

        pattern = r'####\s+(.+?)\n(.*?)(?=####|$)'
        matches = re.findall(pattern, content, re.DOTALL)

        for header, text in matches:
            key = header.strip()
            subsections[key] = text.strip()

        return subsections

    def _parse_triple_equals(self, text: str) -> Dict[str, str]:
        """Parse OLD format (===SECTION===)"""
        sections = {}

        pattern = r'={3,}\s*([A-Z\s]+)\s*={3,}(.*?)(?===|$)'
        matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)

        for header, content in matches:
            header_clean = header.strip().upper()

            if "PERSON RESEARCH" in header_clean:
                sections["person_research"] = content.strip()
            elif "COMPANY RESEARCH" in header_clean:
                sections["company_research"] = content.strip()
            elif "SALES INTELLIGENCE" in header_clean:
                sections["sales_intelligence"] = content.strip()
            elif "PERSONALITY" in header_clean:
                sections["personality_analysis"] = content.strip()

        return sections

    def _empty_result(self) -> Dict:
        """Return empty result structure"""
        return {
            "sections": {},
            "metadata": {
                "total_sections": 0,
                "character_count": 0,
                "format_detected": "none"
            }
        }


def parse_enrichment(raw_profile: str) -> Dict:
    """Convenience function"""
    parser = EnrichmentParser()
    return parser.parse(raw_profile)
PARSEREOF

echo "✅ Restored apps/backend/services/enrichment_parser.py"

echo ""
echo "Step 3: Restore PRIOR integration wrapper (v2.0 object shape)"
cat > apps/backend/services/enrichment_integration.py << 'INTEGEOF'
"""
Enrichment Integration Service
Orchestrates apex_custom_enrichment.py + enrichment_parser.py
"""

import sys
from pathlib import Path
import json

# Add intelligence path
BACKEND_DIR = Path(__file__).parent.parent
INTELLIGENCE_PATH = BACKEND_DIR / 'intelligence'
sys.path.insert(0, str(INTELLIGENCE_PATH))

from services.enrichment_parser import parse_enrichment


def integrate_enrichment_result(raw_enrichment_output: str) -> dict:
    """
    Takes raw output from apex_custom_enrichment.py Stage 2 (GPT-4 synthesis)
    Parses it into structured sections
    Returns enrichment object ready for Postgres storage
    """

    parsed = parse_enrichment(raw_enrichment_output)

    enrichment_object = {
        "version": "2.0",
        "raw_profile": raw_enrichment_output,
        "sections": parsed["sections"],
        "metadata": parsed["metadata"]
    }

    return enrichment_object


def parse_existing_enrichment(contact_enrichment: dict) -> dict:
    """
    Parse existing enrichment data that might be in old format
    Useful for migrating existing enriched contacts
    """

    # Check if already in v2 format
    if isinstance(contact_enrichment, dict) and "sections" in contact_enrichment:
        return contact_enrichment

    # If it's a string or old format, parse it
    if isinstance(contact_enrichment, str):
        raw_text = contact_enrichment
    elif isinstance(contact_enrichment, dict) and "raw_profile" in contact_enrichment:
        raw_text = contact_enrichment["raw_profile"]
    else:
        # Unknown format, return as-is
        return contact_enrichment

    # Parse it
    return integrate_enrichment_result(raw_text)
INTEGEOF

echo "✅ Restored apps/backend/services/enrichment_integration.py"

echo ""
echo "Step 4: Remove optional helper artifacts to avoid orphan code (safe rm -f)"
rm -f scripts/validate_enrichment_parsing.py || true
rm -f scripts/deploy_enrichment_fix.sh || true
rm -f scripts/verify_enrichment_db.sql || true
rm -f scripts/deploy_enrichment_fix.sh.bak || true
rm -f docs/THREAD-DEC16-ENRICHMENT-PARSING-WIRING.md || true
rm -f docs/THREAD-DEC16-ENRICHMENT-PARSING-WIRING.md.* || true

echo ""
echo "Step 5: Show git status (review before committing)"
git status

echo ""
echo "NOTE: This rollback returns parsing behavior to PRIOR state."
echo "If your engine outputs '## overview' style sections, the prior parser may classify it as 'unknown' and store only raw_text."
