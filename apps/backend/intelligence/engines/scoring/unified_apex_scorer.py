#!/usr/bin/env python3
"""
APEX Unified Scoring - Phase 1 & 2 Integration
Combines ApexScoringEngine + UserSpecificScoringEngine (CRE intelligence)
Supports both SQLite (local) and PostgreSQL (Railway)
Version: 2.1.0 - FIXED
"""

import sys
import os
from typing import Dict, List
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(SCRIPT_DIR))

from apex_scoring_engine import ApexScoringEngine

# Try to import CRE engine, fallback if not available
try:
    from user_scoring_engine import UserSpecificScoringEngine
    CRE_ENGINE_AVAILABLE = True
except ImportError:
    CRE_ENGINE_AVAILABLE = False
    print("⚠️ UserSpecificScoringEngine not available, using foundation scoring only")


class UnifiedApexScorer:
    VERSION = "2.1.0"
    
    def __init__(self, db_path: str = None, user_id: str = None):
        if db_path is None:
            db_path = os.getenv('DATABASE_URL') or '/Users/chrisrabenold/projects/apex/apex.db'
        
        self.db_path = db_path
        self.is_postgres = db_path.startswith('postgres') if db_path else False
        self.user_id = user_id or os.getenv('CURRENT_USER_ID', 'default')
        
        db_type = "PostgreSQL" if self.is_postgres else "SQLite"
        print(f"UnifiedApexScorer v{self.VERSION} initializing ({db_type})...")
        
        self.apex_engine = ApexScoringEngine(db_path=self.db_path)
        
        if CRE_ENGINE_AVAILABLE:
            self.cre_engine = UserSpecificScoringEngine(self.user_id, self.db_path)
        else:
            self.cre_engine = None
        
        print(f"✅ Unified scorer ready")
    
    def score_contact_unified(self, contact_id: int, save_to_db: bool = True) -> Dict:
        print(f"\n{'='*60}")
        print(f"UNIFIED SCORING: Contact {contact_id}")
        print(f"{'='*60}")
        
        # STEP 1: Foundation scoring
        print("\n[1/3] Running foundation MDCP + RSS scoring...")
        foundation_result = self.apex_engine.score_contact(contact_id, save_to_db=False)
        
        print(f"   Foundation MDCP: {foundation_result['mdcp_score']:.2f}")
        print(f"   Foundation RSS:  {foundation_result['rss_score']:.2f}")
        print(f"   Foundation Priority: {foundation_result['priority_score']:.2f}")
        
        # STEP 2: CRE vertical intelligence (if available)
        if self.cre_engine:
            print("\n[2/3] Applying CRE vertical intelligence...")
            contact = self.apex_engine.fetch_contact_data(contact_id)
            if contact:
                cre_rss_result = self.cre_engine.calculate_personalized_rss(contact)
                cre_rss_score = cre_rss_result['total']
                print(f"   CRE RSS Score: {cre_rss_score:.2f}")
                print(f"   Reason: {cre_rss_result['breakdown']['reason']}")
            else:
                cre_rss_score = foundation_result['rss_score']
        else:
            print("\n[2/3] CRE engine not available, using foundation RSS...")
            cre_rss_score = foundation_result['rss_score']
            cre_rss_result = {'breakdown': {'reason': 'Foundation scoring only'}}
        
        # STEP 3: Final priority calculation
        print("\n[3/3] Calculating final priority score...")
        
        final_priority_result = self.apex_engine.calculate_priority_score(
            foundation_result['mdcp_score'],
            cre_rss_score,
            foundation_result['lifecycle_stage'],
            foundation_result['lead_type']
        )
        
        final_result = {
            **foundation_result,
            'rss_score': cre_rss_score,
            'rss_tier': self.apex_engine.classify_rss_tier(cre_rss_score),
            'priority_score': final_priority_result['score'],
            'urgency_level': final_priority_result['urgency'],
            'recommended_action': final_priority_result['action'],
            'cre_vertical_applied': self.cre_engine is not None,
            'cre_vertical_data': cre_rss_result.get('breakdown', {})
        }
        
        print(f"\n   Final MDCP: {final_result['mdcp_score']:.2f} ({final_result['mdcp_tier']})")
        print(f"   Final RSS:  {final_result['rss_score']:.2f} ({final_result['rss_tier']})")
        print(f"   Final Priority: {final_result['priority_score']:.2f} ({final_result['urgency_level']})")
        print(f"   Action: {final_result['recommended_action']}")
        
        if save_to_db:
            print("\n   💾 Saving to database...")
            self.apex_engine.save_scores_to_db(final_result)
        
        print(f"\n{'='*60}")
        print(f"✅ UNIFIED SCORING COMPLETE")
        print(f"{'='*60}\n")
        
        return final_result
    
    def bulk_score_unified(self, contact_ids: List[int]) -> List[Dict]:
        results = []
        print(f"\n🎯 Bulk scoring {len(contact_ids)} contacts\n")
        
        for i, contact_id in enumerate(contact_ids, 1):
            try:
                print(f"[{i}/{len(contact_ids)}] Contact {contact_id}...")
                result = self.score_contact_unified(contact_id)
                results.append(result)
            except Exception as e:
                print(f"❌ Error: {e}")
                results.append({'contact_id': contact_id, 'error': str(e)})
        
        print(f"\n✅ Bulk scoring complete: {len(results)} processed\n")
        return results


def score_contact_unified(contact_id: int, db_path: str = None, user_id: str = None) -> Dict:
    scorer = UnifiedApexScorer(db_path, user_id)
    return scorer.score_contact_unified(contact_id)


def bulk_score_unified(contact_ids: List[int], db_path: str = None, user_id: str = None) -> List[Dict]:
    scorer = UnifiedApexScorer(db_path, user_id)
    return scorer.bulk_score_unified(contact_ids)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python unified_apex_scorer.py tact_id> [<id2> ...]")
        sys.exit(1)
    
    contact_ids = [int(cid) for cid in sys.argv[1:]]
    if len(contact_ids) == 1:
        result = score_contact_unified(contact_ids[0])
        print(f"\n📊 Result: {result['contact_name']} | Priority: {result['priority_score']:.2f}")
    else:
        bulk_score_unified(contact_ids)
