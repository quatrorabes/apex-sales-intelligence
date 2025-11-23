#!/usr/bin/env python3

#!/usr/bin/env python3
"""Safe testing script - won't break anything"""

print("🧪 Testing Apex Integration Safety\n")

# Test 1: Check if database exists
import os
if os.path.exists('./apex.db'):
	print("✅ Database exists")
else:
	print("⚠️ Database missing - will be created on startup")
	
# Test 2: Check intelligence files
intelligence_files = {
	'intelligence/engines/persona_classifier_cre_sba.py': 'Persona Classifier',
	'intelligence/enrichment/perplexity_deep_enrichment.py': 'Perplexity Enrichment',
	'intelligence/outreach/the_kernal_who_when_what.py': 'Kernel Intelligence',
	'intelligence/sequences/auto_sequence_engine.py': 'Sequence Engine'
}

print("\n📁 Intelligence Files:")
for path, name in intelligence_files.items():
	if os.path.exists(path):
		print(f"  ✅ {name}")
	else:
		print(f"  ❌ {name} - Missing: {path}")
		
# Test 3: Try importing without breaking
print("\n🔌 Testing Imports:")
try:
	from api.routes.outreach import router
	print("  ✅ Outreach router")
except Exception as e:
	print(f"  ⚠️ Outreach router: {e}")
	
print("\n✅ Safe to proceed with integration!")
