"""
APEX Scoring Orchestrator - Integrates MDCP/RSS scoring + Persona Classification + HubSpot Sync
Place this file at: /apex/apps/backend/intelligence/engines/scoring/scoring_orchestrator.py
"""

import os
import sys
from datetime import datetime
from typing import Dict, List, Optional
import json

# Import your intelligence modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../enrichment'))

from apex_intelligence_engine import ApexIntelligenceScorer
from persona_classifier_cre_sba import CRESBAPersonaClassifier

class ScoringOrchestrator:
    """Orchestrates MDCP/RSS scoring, persona classification, and HubSpot sync"""
    
    def __init__(self, db_connection):
        self.db = db_connection
        self.scorer = ApexIntelligenceScorer(db_connection)
        self.classifier = CRESBAPersonaClassifier()
        
    def score_contact(self, contact_id: int, trigger: str = 'manual') -> Dict:
        """
        Complete scoring pipeline for a contact
        Args:
            contact_id: Database ID of contact
            trigger: 'import', 'enrichment', or 'manual'
        Returns:
            Dictionary with scoring results
        """
        # Get contact data from database
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM contacts WHERE id = ?", (contact_id,))
        row = cursor.fetchone()
        
        if not row:
            return {'error': 'Contact not found', 'contact_id': contact_id}
        
        # Convert SQLite row to dictionary
        contact = dict(row)
        
        # Prepare contact data for scoring
        contact_data = {
            'id': contact['id'],
            'name': contact.get('name', ''),
            'title': contact.get('title', ''),
            'company': contact.get('company', ''),
            'industry': contact.get('industry', ''),
            'email': contact.get('email', ''),
            'phone': contact.get('phone', ''),
            'enrichment_data': contact.get('enrichment_data', '{}')
        }
        
        # Parse enrichment data if available (from Perplexity)
        try:
            if contact_data['enrichment_data']:
                enrichment = json.loads(contact_data['enrichment_data'])
                contact_data.update(enrichment)
        except (json.JSONDecodeError, TypeError):
            pass
        
        # 1. Calculate MDCP and RSS scores using your intelligence engine
        scoring_result = self.scorer.score_contact(contact_data)
        
        # 2. Classify persona using your classifier
        tier, persona, confidence, criteria = self.classifier.classify_contact({
            'job_title': contact_data.get('title', ''),
            'company': contact_data.get('company', ''),
            'industry': contact_data.get('industry', ''),
            'skills': contact_data.get('skills', []),
            'experience': contact_data.get('experience', [])
        })
        
        # 3. Calculate priority score (weighted combination)
        mdcp_score = scoring_result.get('mdcp_score', 0)
        rss_score = scoring_result.get('rss_score', 0)
        priority_score = (mdcp_score * 0.6) + (rss_score * 0.4)
        
        # 4. Update database with all scores and persona
        cursor.execute("""
            UPDATE contacts SET
                mdcp_score = ?,
                rss_score = ?,
                priority_score = ?,
                persona_tier = ?,
                persona_type = ?,
                persona_confidence = ?,
                urgency_level = ?,
                recommended_action = ?,
                last_scored = ?
            WHERE id = ?
        """, (
            mdcp_score,
            rss_score,
            priority_score,
            tier,
            persona,
            confidence,
            scoring_result.get('urgency_level', 'low'),
            scoring_result.get('recommended_action', ''),
            datetime.now().isoformat(),
            contact_id
        ))
        self.db.commit()
        
        # 5. Store scoring history for tracking changes over time
        cursor.execute("""
            INSERT INTO scoring_history 
            (contact_id, trigger, mdcp_score, rss_score, priority_score, 
             persona_tier, persona_type, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            contact_id,
            trigger,
            mdcp_score,
            rss_score,
            priority_score,
            tier,
            persona,
            datetime.now().isoformat()
        ))
        self.db.commit()
        
        # 6. Sync to HubSpot if enabled
        if os.getenv('HUBSPOT_API_KEY') and contact.get('hubspot_id'):
            try:
                from intelligence.hubspot_sync import HubSpotSync
                hubspot = HubSpotSync()
                hubspot.update_contact(contact['hubspot_id'], {
                    'mdcp_score': mdcp_score,
                    'rss_score': rss_score,
                    'priority_score': priority_score,
                    'persona_tier': tier,
                    'persona_type': persona,
                    'apex_urgency': scoring_result.get('urgency_level', 'low')
                })
            except Exception as e:
                print(f"⚠️  HubSpot sync failed: {e}")
        
        # Return complete results
        return {
            'contact_id': contact_id,
            'name': contact_data['name'],
            'mdcp_score': round(mdcp_score, 2),
            'rss_score': round(rss_score, 2),
            'priority_score': round(priority_score, 2),
            'persona': {
                'tier': tier,
                'type': persona,
                'confidence': round(confidence, 2)
            },
            'urgency_level': scoring_result.get('urgency_level'),
            'recommended_action': scoring_result.get('recommended_action'),
            'trigger': trigger,
            'timestamp': datetime.now().isoformat()
        }
    
    def bulk_score(self, contact_ids: List[int], trigger: str = 'bulk') -> List[Dict]:
        """Score multiple contacts efficiently"""
        results = []
        for contact_id in contact_ids:
            try:
                result = self.score_contact(contact_id, trigger)
                results.append(result)
            except Exception as e:
                results.append({
                    'contact_id': contact_id,
                    'error': str(e)
                })
        return results
    
    def score_after_import(self, contact_ids: List[int]) -> List[Dict]:
        """Score contacts immediately after CSV or HubSpot import"""
        return self.bulk_score(contact_ids, trigger='import')
    
    def score_after_enrichment(self, contact_id: int) -> Dict:
        """Re-score contact after Perplexity enrichment completes"""
        return self.score_contact(contact_id, trigger='enrichment')


# Test/Example Usage
if __name__ == "__main__":
    print("🎯 APEX Scoring Orchestrator")
    print("=" * 60)
    print("\nThis module integrates:")
    print("  ✅ MDCP/RSS scoring (apex_intelligence_engine.py)")
    print("  ✅ Persona classification (persona_classifier_cre_sba.py)")
    print("  ✅ HubSpot bi-directional sync")
    print("  ✅ Scoring history tracking")
    print("\nUsage:")
    print("  from intelligence.engines.scoring.scoring_orchestrator import ScoringOrchestrator")
    print("  orchestrator = ScoringOrchestrator(db_connection)")
    print("  result = orchestrator.score_contact(contact_id)")
