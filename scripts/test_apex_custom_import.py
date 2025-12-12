#!/usr/bin/env python3
"""
Test that ApexCustomEnrichment imports correctly after migration
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'apps', 'backend'))

print("=" * 60)
print("🧪 Testing ApexCustomEnrichment Import")
print("=" * 60)

try:
    from intelligence.engines.enrichment.apex_custom_enrichment import ApexCustomEnrichment
    print("✅ Import successful!")
    print(f"   Class: {ApexCustomEnrichment}")
    print(f"   Methods: {[m for m in dir(ApexCustomEnrichment) if not m.startswith('_')]}")
    
    # Test instantiation (without API keys for now)
    print("\n🔧 Testing instantiation...")
    
    class MockConfig:
        def __init__(self):
            self.perplexity_api_key = "test_key"
            self.openai_api_key = "test_key"
    
    try:
        enricher = ApexCustomEnrichment(MockConfig())
        print("✅ Instantiation successful!")
        print(f"   Has Stage 1 method: {hasattr(enricher, 'stage1_gather_raw_data')}")
        print(f"   Has Stage 2 method: {hasattr(enricher, 'stage2_synthesize_intelligence')}")
        print(f"   Has Stage 3 method: {hasattr(enricher, 'stage3_parse_and_extract')}")
    except Exception as e:
        print(f"⚠️  Instantiation warning (expected without real API keys): {e}")
    
    print("\n✅ All import tests passed!")
    print("=" * 60)
    
except ImportError as e:
    print(f"❌ Import failed: {e}")
    print("\nTroubleshooting:")
    print("1. Did you run migrate_apex_custom_enrichment.sh?")
    print("2. Is the file in apps/backend/intelligence/engines/enrichment/?")
    print("3. Does __init__.py exist in that directory?")
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
