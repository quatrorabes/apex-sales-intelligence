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
    
    Args:
        raw_enrichment_output: The synthesized intelligence text from GPT-4
        
    Returns:
        {
            "version": "2.0",
            "raw_profile": "original GPT-4 output",
            "sections": {
                "overview": "...",
                "company_overview": "...",
                ...
            },
            "metadata": {
                "total_sections": 12,
                "character_count": 8500,
                "format_detected": "markdown_structured"
            }
        }
    """
    
    # Parse the raw enrichment
    parsed = parse_enrichment(raw_enrichment_output)
    
    # Build final enrichment object
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
    
    Args:
        contact_enrichment: The enrichment dict from Postgres
        
    Returns:
        Updated enrichment with parsed sections
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
