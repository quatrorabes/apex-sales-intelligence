
import sys
sys.path.insert(0, '/Users/chrisrabenold/projects/apex/apps/backend/intelligence/engines/scoring')

try:
	from intelligence.engines.scoring import ApexScoringEngine, ScoringOrchestrator
	from intelligence.engines.scoring.scoring_wrapper import score_contact_from_db
	print("✅ All imports successful!")
except ImportError as e:
	print(f"❌ Import failed: {e}")

