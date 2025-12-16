"""
apps/backend/services/enrichment_integration.py

Enrichment Integration Service
Orchestrates parsing and normalization of enrichment data.

Author: Apex Sales Intelligence Team
Date: 2025-12-16
"""

from typing import Dict, Any
from .enrichment_parser import parse_enrichment


def integrate_enrichment_result(raw_enrichment_output: str) -> Dict[str, Any]:
    """
    Integrate raw enrichment output into structured format.
    
    This is the main orchestration point called by main.py after
    the enrichment engine completes.
    
    Flow:
        1. Parse raw markdown into sections
        2. Return structured dict ready for JSON serialization
        3. DB persistence happens in caller (main.py)
    
    Args:
        raw_enrichment_output: Raw markdown from enrichment engine
        
    Returns:
        Structured dict with sections and metadata
    """
    return parse_enrichment(raw_enrichment_output)


if __name__ == "__main__":
    # Quick smoke test
    test_input = """
## overview
Test contact at Test Company.

## background_and_experience
5 years experience in the field.
"""
    
    result = integrate_enrichment_result(test_input)
    print("Integration Test:")
    print(f"  Format: {result['metadata']['format_detected']}")
    print(f"  Sections: {result['metadata']['total_sections']}")
    print(f"  Keys: {list(result['sections'].keys())}")
    print("✅ Integration service operational")
