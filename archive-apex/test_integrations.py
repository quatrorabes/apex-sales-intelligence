#!/usr/bin/env python3

#!/usr/bin/env python3
"""
Quick integration test for APEX intelligence
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from services.intelligence_service import IntelligenceService

def test_integration():
	print("🧪 Testing APEX Intelligence Integration\n")
	print("="*60)
	
	# Initialize service
	intel = IntelligenceService('./apex.db')
	
	# Test 1: Dashboard summary
	print("\n📊 Test 1: Dashboard Summary")
	summary = intel.get_dashboard_summary()
	print(f"✅ Summary: {summary}")
	
	# Test 2: Active sequences
	print("\n🔄 Test 2: Active Sequences")
	sequences = intel.get_active_sequences()
	print(f"✅ Active sequences: {len(sequences)}")
	
	print("\n" + "="*60)
	print("✅ Integration test complete!")
	
if __name__ == "__main__":
	test_integration()
	