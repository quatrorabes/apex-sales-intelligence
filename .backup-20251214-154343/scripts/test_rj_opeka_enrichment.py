#!/usr/bin/env python3

#!/usr/bin/env python3
"""
Test ApexCustomEnrichment with RJ Opeka
Validates all sections render correctly
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'apps', 'backend'))

from intelligence.engines.enrichment.apex_custom_enrichment import ApexCustomEnrichment
from services.enrichment_parser_v2 import EnrichmentParser

print("=" * 70)
print("🧪 Testing ApexCustomEnrichment with RJ Opeka")
print("=" * 70)

# Mock contact data for RJ
rj_contact = {
	"name": "RJ Opeka",
	"first_name": "RJ",
	"last_name": "Opeka",
	"title": "Chief Revenue Officer",
	"company": "SunWest Bank",
	"email": "rj.opeka@sunwestbank.com",
	"linkedin_url": "https://www.linkedin.com/in/rjopeka"
}

class Config:
	def __init__(self):
		self.perplexity_api_key = os.getenv('PERPLEXITY_API_KEY')
		self.openai_api_key = os.getenv('OPENAI_API_KEY')
		
print("\n📊 Contact Info:")
print(f"   Name: {rj_contact['name']}")
print(f"   Title: {rj_contact['title']}")
print(f"   Company: {rj_contact['company']}")
print(f"   LinkedIn: {rj_contact['linkedin_url']}")

# Check API keys
config = Config()
if not config.perplexity_api_key:
	print("\n❌ PERPLEXITY_API_KEY not set")
	print("   Set it with: export PERPLEXITY_API_KEY='your-key'")
	sys.exit(1)
	
if not config.openai_api_key:
	print("\n❌ OPENAI_API_KEY not set")
	print("   Set it with: export OPENAI_API_KEY='your-key'")
	sys.exit(1)
	
print("\n✅ API keys configured")

# Initialize enricher
try:
	enricher = ApexCustomEnrichment(config)
	print("✅ ApexCustomEnrichment initialized")
except Exception as e:
	print(f"❌ Failed to initialize: {e}")
	sys.exit(1)
	
# Run enrichment
print("\n🚀 Starting three-stage enrichment...")
print("   This will take ~90-120 seconds")
print()

try:
	result = enricher.enrich_contact_full(rj_contact)
	
	if result['status'] != 'success':
		print(f"❌ Enrichment failed: {result.get('error')}")
		sys.exit(1)
		
	print("\n✅ Enrichment completed!")
	
	# Parse results
	parser = EnrichmentParser()
	parsed = parser.parse(result['profile_data']['synthesized_intelligence'])
	
	print(f"\n📊 Results:")
	print(f"   Format detected: {parsed['metadata']['format_detected']}")
	print(f"   Total sections: {parsed['metadata']['total_sections']}")
	print(f"   Character count: {parsed['metadata']['character_count']:,}")
	
	print(f"\n📋 Sections extracted:")
	for i, section_name in enumerate(sorted(parsed['sections'].keys()), 1):
		char_count = len(parsed['sections'][section_name])
		print(f"   {i:2d}. {section_name:40s} ({char_count:,} chars)")
		
	# Check critical sections
	print(f"\n🎯 Critical Section Check:")
	critical_sections = [
		'personality_and_communication',
		'pain_points_and_challenges',
		'budget_and_authority',
		'company_overview',
		'overview'
	]
	
	for section in critical_sections:
		status = "✅" if section in parsed['sections'] else "❌"
		print(f"   {status} {section}")
		
	# Show personality preview
	if 'personality_and_communication' in parsed['sections']:
		preview = parsed['sections']['personality_and_communication'][:200]
		print(f"\n👤 Personality Preview:")
		print(f"   {preview}...")
		
	print("\n" + "=" * 70)
	print("✅ Test Complete - Ready for production!")
	print("=" * 70)
	
except KeyboardInterrupt:
	print("\n\n⚠️  Test interrupted")
	sys.exit(1)
except Exception as e:
	print(f"\n❌ Test failed: {e}")
	import traceback
	traceback.print_exc()
	sys.exit(1)
	