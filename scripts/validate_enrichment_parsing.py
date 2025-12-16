#!/usr/bin/env python3
"""
scripts/validate_enrichment_parsing.py

Validation script for enrichment parsing patch.
Run this after deploying parser changes.

Usage:
    python scripts/validate_enrichment_parsing.py
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'apps', 'backend'))

from services.enrichment_parser import parse_enrichment


def test_markdown_v3():
    """Test current EnhancedEnrichment format"""
    input_text = """
## overview
John Doe is VP of Engineering at TechCorp.

## background_and_experience
15 years in tech, previously at FAANG companies.

## company_overview
TechCorp: $50M ARR B2B SaaS platform.

## pain_points_and_challenges
Cloud costs and developer velocity are key concerns.

## budget_and_authority
$2M budget authority, reports to CTO.
"""
    
    result = parse_enrichment(input_text)
    
    assert result['metadata']['format_detected'] == 'markdown_v3', \
        f"Expected markdown_v3, got {result['metadata']['format_detected']}"
    assert result['metadata']['total_sections'] >= 5, \
        f"Expected >= 5 sections, got {result['metadata']['total_sections']}"
    assert 'overview' in result['sections'], \
        "Missing 'overview' section"
    assert 'company_overview' in result['sections'], \
        "Missing 'company_overview' section"
    
    print("✅ Test 1 PASSED: markdown_v3 format")


def test_markdown_v2():
    """Test legacy format"""
    input_text = """
### PERSON PROFILE
Jane Smith at SalesCo.

### COMPANY PROFILE
SalesCo is a sales enablement platform.
"""
    
    result = parse_enrichment(input_text)
    
    assert result['metadata']['format_detected'] == 'markdown_v2', \
        f"Expected markdown_v2, got {result['metadata']['format_detected']}"
    assert 'person_profile' in result['sections'], \
        "Missing normalized 'person_profile' section"
    
    print("✅ Test 2 PASSED: markdown_v2 format")


def test_unknown_fallback():
    """Test fallback to raw_text"""
    input_text = "Just plain text with no headers."
    
    result = parse_enrichment(input_text)
    
    assert result['metadata']['format_detected'] == 'unknown', \
        f"Expected unknown, got {result['metadata']['format_detected']}"
    assert 'raw_text' in result['sections'], \
        "Missing 'raw_text' fallback"
    
    print("✅ Test 3 PASSED: unknown format fallback")


def test_empty_input():
    """Test empty/null input"""
    result = parse_enrichment("")
    
    assert result['metadata']['format_detected'] == 'empty', \
        f"Expected empty, got {result['metadata']['format_detected']}"
    
    print("✅ Test 4 PASSED: empty input handling")


if __name__ == "__main__":
    print("="*70)
    print("ENRICHMENT PARSER VALIDATION SUITE")
    print("="*70)
    
    try:
        test_markdown_v3()
        test_markdown_v2()
        test_unknown_fallback()
        test_empty_input()
        
        print("\n" + "="*70)
        print("ALL VALIDATION TESTS PASSED ✅")
        print("="*70)
        print("\nParser is ready for production deployment.")
        sys.exit(0)
        
    except AssertionError as e:
        print(f"\n❌ VALIDATION FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        sys.exit(1)
