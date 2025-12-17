"""
apps/backend/services/enrichment_parser.py

Enrichment Parser — Multi-Format Support
Parses enrichment markdown into structured JSON sections.

Supported formats:
1. "markdown_v3" (## section_key) — Current EnhancedEnrichment output
2. "markdown_v2" (### SECTION NAME) — Legacy format
3. "legacy" (=== SECTION) — Original format
4. "unknown" — Fallback to raw_text

Author: Apex Sales Intelligence Team
Date: 2025-12-16
"""

import re
from typing import Dict, Any


def parse_enrichment(raw_profile: str) -> Dict[str, Any]:
    """
    Parse enrichment markdown into structured sections.
    
    Auto-detects format and returns:
    {
        "sections": {...},
        "metadata": {
            "format_detected": str,
            "total_sections": int,
            "character_count": int
        }
    }
    
    Args:
        raw_profile: Raw markdown string from enrichment engine
        
    Returns:
        Dict with sections and metadata
    """
    if not raw_profile or not isinstance(raw_profile, str):
        return {
            "sections": {"raw_text": ""},
            "metadata": {
                "format_detected": "empty",
                "total_sections": 0,
                "character_count": 0
            }
        }
    
    raw_profile = raw_profile.strip()
    char_count = len(raw_profile)
    
    # Try format detection in priority order
    # 1. markdown_v3 (## section_key) - Current EnhancedEnrichment output
    if re.search(r'^## [a-z_]+', raw_profile, re.MULTILINE):
        sections = _parse_markdown_v3(raw_profile)
        if len(sections) > 1:  # More than just raw_text
            return {
                "sections": sections,
                "metadata": {
                    "format_detected": "markdown_v3",
                    "total_sections": len(sections),
                    "character_count": char_count
                }
            }
    
    # 2. markdown_v2 (### SECTION NAME) - Legacy format
    if re.search(r'^### [A-Z]', raw_profile, re.MULTILINE):
        sections = _parse_markdown_v2(raw_profile)
        if len(sections) > 1:
            return {
                "sections": sections,
                "metadata": {
                    "format_detected": "markdown_v2",
                    "total_sections": len(sections),
                    "character_count": char_count
                }
            }
    
    # 3. Legacy (=== SECTION) - Original format
    if re.search(r'^===', raw_profile, re.MULTILINE):
        sections = _parse_legacy(raw_profile)
        if len(sections) > 1:
            return {
                "sections": sections,
                "metadata": {
                    "format_detected": "legacy",
                    "total_sections": len(sections),
                    "character_count": char_count
                }
            }
    
    # 4. Fallback to raw_text
    return {
        "sections": {"raw_text": raw_profile},
        "metadata": {
            "format_detected": "unknown",
            "total_sections": 1,
            "character_count": char_count
        }
    }


def _parse_markdown_v3(raw_profile: str) -> Dict[str, str]:
    """
    Parse markdown_v3 format: ## section_key
    
    Expected format:
        ## overview
        Content here...
        
        ## background_and_experience
        More content...
        
        ## company_overview
        Company details...
    
    Returns:
        Dict mapping section_key -> content
    """
    sections = {}
    
    # Split on ## headers
    parts = re.split(r'^## ', raw_profile, flags=re.MULTILINE)
    
    # First part is preamble (if any)
    if parts[0].strip():
        sections["preamble"] = parts[0].strip()
    
    # Process remaining sections
    for part in parts[1:]:
        if not part.strip():
            continue
            
        lines = part.split('\n', 1)
        if len(lines) < 2:
            # Header only, no content
            section_key = lines[0].strip().lower()
            sections[section_key] = ""
        else:
            section_key = lines[0].strip().lower()
            content = lines[1].strip()
            sections[section_key] = content
    
    return sections if sections else {"raw_text": raw_profile}


def _parse_markdown_v2(raw_profile: str) -> Dict[str, str]:
    """
    Parse markdown_v2 format: ### SECTION NAME
    
    Expected format:
        ### PERSON PROFILE
        Content here...
        
        ### COMPANY PROFILE
        More content...
    
    Returns:
        Dict mapping normalized_section_key -> content
    """
    sections = {}
    
    # Split on ### headers
    parts = re.split(r'^### ', raw_profile, flags=re.MULTILINE)
    
    # First part is preamble (if any)
    if parts[0].strip():
        sections["preamble"] = parts[0].strip()
    
    # Process remaining sections
    for part in parts[1:]:
        if not part.strip():
            continue
            
        lines = part.split('\n', 1)
        if len(lines) < 2:
            section_name = lines[0].strip()
            section_key = _normalize_section_key(section_name)
            sections[section_key] = ""
        else:
            section_name = lines[0].strip()
            section_key = _normalize_section_key(section_name)
            content = lines[1].strip()
            sections[section_key] = content
    
    return sections if sections else {"raw_text": raw_profile}


def _parse_legacy(raw_profile: str) -> Dict[str, str]:
    """
    Parse legacy format: === SECTION
    
    Expected format:
        === OVERVIEW
        Content here...
        
        === BACKGROUND
        More content...
    
    Returns:
        Dict mapping normalized_section_key -> content
    """
    sections = {}
    
    # Split on === headers
    parts = re.split(r'^=== ', raw_profile, flags=re.MULTILINE)
    
    # First part is preamble (if any)
    if parts[0].strip():
        sections["preamble"] = parts[0].strip()
    
    # Process remaining sections
    for part in parts[1:]:
        if not part.strip():
            continue
            
        lines = part.split('\n', 1)
        if len(lines) < 2:
            section_name = lines[0].strip()
            section_key = _normalize_section_key(section_name)
            sections[section_key] = ""
        else:
            section_name = lines[0].strip()
            section_key = _normalize_section_key(section_name)
            content = lines[1].strip()
            sections[section_key] = content
    
    return sections if sections else {"raw_text": raw_profile}


def _normalize_section_key(section_name: str) -> str:
    """
    Normalize section names to lowercase snake_case keys.
    
    Examples:
        "PERSON PROFILE" -> "person_profile"
        "Company Overview" -> "company_overview"
        "Background & Experience" -> "background_experience"
    
    Args:
        section_name: Original section header text
        
    Returns:
        Normalized snake_case key
    """
    # Remove special chars, convert to lowercase, replace spaces with underscores
    normalized = re.sub(r'[^a-zA-Z0-9\s]', '', section_name)
    normalized = normalized.strip().lower()
    normalized = re.sub(r'\s+', '_', normalized)
    return normalized or "section"


# Backwards compatibility alias
def integrate_enrichment_result(raw_profile: str) -> Dict[str, Any]:
    """
    Alias for parse_enrichment() for backwards compatibility.
    Some callers may use this name.
    """
    return parse_enrichment(raw_profile)


if __name__ == "__main__":
    # Test cases
    print("="*70)
    print("ENRICHMENT PARSER TEST SUITE")
    print("="*70)
    
    # Test 1: markdown_v3 (current format)
    test_v3 = """
## overview
John Doe is a Senior VP of Engineering at TechCorp, responsible for a team of 150 engineers.

## background_and_experience
15+ years in software engineering. Previously at Google and Amazon.

## company_overview
TechCorp is a B2B SaaS company with $50M ARR, 200 employees.

## pain_points_and_challenges
Struggling with cloud infrastructure costs and developer productivity.

## budget_and_authority
Reports to CTO, has budget authority for $2M annually.
"""
    
    result = parse_enrichment(test_v3)
    print(f"\n✅ Test 1 (markdown_v3):")
    print(f"   Format: {result['metadata']['format_detected']}")
    print(f"   Sections: {result['metadata']['total_sections']}")
    print(f"   Keys: {list(result['sections'].keys())}")
    
    # Test 2: markdown_v2 (legacy)
    test_v2 = """
### PERSON PROFILE
Jane Smith, Director of Sales at SalesCo.

### COMPANY PROFILE
SalesCo is a mid-market sales enablement platform.
"""
    
    result = parse_enrichment(test_v2)
    print(f"\n✅ Test 2 (markdown_v2):")
    print(f"   Format: {result['metadata']['format_detected']}")
    print(f"   Sections: {result['metadata']['total_sections']}")
    print(f"   Keys: {list(result['sections'].keys())}")
    
    # Test 3: Unknown format (fallback)
    test_unknown = "Just some plain text without any headers."
    
    result = parse_enrichment(test_unknown)
    print(f"\n✅ Test 3 (unknown):")
    print(f"   Format: {result['metadata']['format_detected']}")
    print(f"   Sections: {result['metadata']['total_sections']}")
    print(f"   Keys: {list(result['sections'].keys())}")
    
    print("\n" + "="*70)
    print("ALL TESTS COMPLETE")
    print("="*70)
