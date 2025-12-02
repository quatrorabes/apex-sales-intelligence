"""
APEX Unified Scoring - Phase 1 & 2 Integration
Combines ApexScoringEngine (foundation) + UserSpecificScoringEngine (CRE intelligence)

Auto-generated: 2025-12-01T15:29:09.168220
"""

import sys
import os
from typing import Dict, Optional
from pathlib import Path

# Ensure we can import sibling modules
SCRIPT_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(SCRIPT_DIR))

from apex_scoring_engine import ApexScoringEngine
from user_scoring_engine import UserSpecificScoringEngine

# HARDCODED DATABASE PATH
DEFAULT_DB_PATH = "/Users/chrisrabenold/projects/apex/apex.db"


class UnifiedApexScorer:
    """Unified scorer combining foundation MDCP/RSS + CRE vertical intelligence"""
    
    def __init__(self, db_path: str = None, user_id: str = None):
        """Initialize both scoring engines"""
        # Always use absolute path
        if db_path is None:
            db_path = DEFAULT_DB_PATH
        
        # Verify database exists
        if not os.path.exists(db_path):
            raise FileNotFoundError(f"❌ Database not found: {db_path}")
        
        self.db_path = db_path
        self.user_id = user_id or os.getenv('CURRENT_USER_ID', 'default')
        
        print(f"Initializing scoring engines...")
        print(f"  Database: {self.db_path}")
        print(f"  User: {self.user_id}")
        
        # Initialize engines with explicit path
        self.apex_engine = ApexScoringEngine(db_path=self.db_path)
        self.cre_engine = UserSpecificScoringEngine(self.user_id, self.db_path)
        
        print(f"✅ Unified scorer initialized")
    
    def score_contact_unified(self, contact_id: int, save_to_db: bool = True) -> Dict:
        """
        Complete unified scoring pipeline
        
        1. Run foundation MDCP + RSS scoring
        2. Apply CRE vertical intelligence boost/penalty
        3. Generate final priority score
        4. Save to database
        """
        
        print(f"\n{'='*60}")
        print(f"UNIFIED SCORING: Contact {contact_id}")
        print(f"{'='*60}")
        
        # STEP 1: Foundation scoring (MDCP + generic RSS)
        print("\n[1/3] Running foundation MDCP + RSS scoring...")
        foundation_result = self.apex_engine.score_contact(contact_id, save_to_db=False)
        
        print(f"   Foundation MDCP: {foundation_result['mdcp_score']:.2f}")
        print(f"   Foundation RSS:  {foundation_result['rss_score']:.2f}")
        print(f"   Foundation Priority: {foundation_result['priority_score']:.2f}")
        
        # STEP 2: CRE vertical intelligence boost
        print("\n[2/3] Applying CRE vertical intelligence...")
        
        # Fetch contact for CRE analysis
        contact = dict(self.apex_engine.fetch_contact_data(contact_id))
        
        # Get CRE-specific RSS score
        cre_rss_result = self.cre_engine.calculate_personalized_rss(contact)
        cre_rss_score = cre_rss_result['total']
        
        print(f"   CRE RSS Score: {cre_rss_score:.2f}")
        print(f"   Reason: {cre_rss_result['breakdown']['reason']}")
        
        # Determine if CRE boost or penalty applies
        rss_delta = cre_rss_score - foundation_result['rss_score']
        
        if rss_delta > 0:
            print(f"   ✅ CRE BOOST: +{rss_delta:.2f} points")
        elif rss_delta < 0:
            print(f"   ⚠️  CRE PENALTY: {rss_delta:.2f} points")
        else:
            print(f"   → No CRE adjustment needed")
        
        # STEP 3: Recalculate priority with CRE-enhanced RSS
        print("\n[3/3] Calculating final priority score...")
        
        lifecycle_stage = foundation_result['lifecycle_stage']
        mdcp_score = foundation_result['mdcp_score']
        
        # Use CRE RSS instead of foundation RSS
        final_priority_result = self.apex_engine.calculate_priority_score(
            mdcp_score,
            cre_rss_score,  # CRE-enhanced RSS
            lifecycle_stage,
            foundation_result['lead_type']
        )
        
        # Assemble final result
        final_result = {
            **foundation_result,
            'rss_score': cre_rss_score,  # Override with CRE RSS
            'rss_tier': self.apex_engine.classify_rss_tier(cre_rss_score),
            'priority_score': final_priority_result['score'],
            'urgency_level': final_priority_result['urgency'],
            'recommended_action': final_priority_result['action'],
            'cre_vertical_applied': True,
            'cre_vertical_data': cre_rss_result['breakdown']
        }
        
        print(f"\n   Final MDCP: {final_result['mdcp_score']:.2f} ({final_result['mdcp_tier']})")
        print(f"   Final RSS:  {final_result['rss_score']:.2f} ({final_result['rss_tier']})")
        print(f"   Final Priority: {final_result['priority_score']:.2f} ({final_result['urgency_level']})")
        print(f"   Action: {final_result['recommended_action']}")
        
        # STEP 4: Save to database
        if save_to_db:
            print("\n   💾 Saving to database...")
            self.apex_engine.save_scores_to_db(final_result)
        
        print(f"\n{'='*60}")
        print(f"✅ UNIFIED SCORING COMPLETE")
        print(f"{'='*60}\n")
        
        return final_result
    
    def bulk_score_unified(self, contact_ids: list) -> list:
        """Score multiple contacts with unified pipeline"""
        results = []
        
        print(f"\n🎯 Starting bulk unified scoring for {len(contact_ids)} contacts\n")
        
        for i, contact_id in enumerate(contact_ids, 1):
            try:
                print(f"[{i}/{len(contact_ids)}] Scoring contact {contact_id}...")
                result = self.score_contact_unified(contact_id)
                results.append(result)
            except Exception as e:
                print(f"❌ Error scoring contact {contact_id}: {e}")
                results.append({'contact_id': contact_id, 'error': str(e)})
        
        print(f"\n✅ Bulk unified scoring complete: {len(results)} contacts processed\n")
        return results


# ============================================================================
# QUICK SCORING FUNCTIONS
# ============================================================================

def score_contact_unified(contact_id: int, db_path: str = None, user_id: str = None) -> Dict:
    """Quick function to score a single contact with unified pipeline"""
    scorer = UnifiedApexScorer(db_path, user_id)
    return scorer.score_contact_unified(contact_id)


def bulk_score_unified(contact_ids: list, db_path: str = None, user_id: str = None) -> list:
    """Quick function to score multiple contacts with unified pipeline"""
    scorer = UnifiedApexScorer(db_path, user_id)
    return scorer.bulk_score_unified(contact_ids)


# ============================================================================
# CLI INTERFACE
# ============================================================================

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python unified_apex_scorer.py tact_id>          # Score single contact")
        print("  python unified_apex_scorer.py <id1> <id2> <id3>...  # Score multiple contacts")
        sys.exit(1)
    
    contact_ids = [int(cid) for cid in sys.argv[1:]]
    
    if len(contact_ids) == 1:
        result = score_contact_unified(contact_ids[0])
        print(f"\n📊 FINAL RESULT:")
        print(f"   Contact: {result['contact_name']}")
        print(f"   Priority: {result['priority_score']:.2f}")
        print(f"   Urgency: {result['urgency_level']}")
        print(f"   Action: {result['recommended_action']}")
    else:
        results = bulk_score_unified(contact_ids)
        print(f"\n📊 BULK RESULTS:")
        for r in results:
            if 'error' not in r:
                print(f"   {r['contact_id']:3d} | {r['contact_name']:30s} | Priority: {r['priority_score']:5.2f} | {r['urgency_level']}")
