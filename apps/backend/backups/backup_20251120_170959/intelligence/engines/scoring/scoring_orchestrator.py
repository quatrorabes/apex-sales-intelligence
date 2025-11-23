"""
APEX Scoring Orchestrator - CORRECTED CLASS NAMES
Fixed to match your actual apex_intelligence_engine.py class names
"""

from datetime import datetime
from typing import Dict, List
import json


class ScoringOrchestrator:
    """Orchestrates MDCP/RSS scoring, persona classification, and HubSpot sync"""
    
    def __init__(self, db_connection):
        """Initialize with database connection"""
        self.db = db_connection
        # Lazy load to avoid import issues
        self._scorer = None
        self._classifier = None
    
    @property
    def scorer(self):
        """Lazy load scorer - CORRECTED CLASS NAME"""
        if self._scorer is None:
            from intelligence.engines.enrichment.apex_intelligence_engine import ApexScoringEngine
            # ApexScoringEngine expects db path, not connection
            self._scorer = ApexScoringEngine("apex.db")
        return self._scorer
    
    @property
    def classifier(self):
        """Lazy load classifier"""
        if self._classifier is None:
            from intelligence.engines.enrichment.persona_classifier_cre_sba import UltimatePersonaClassifier
            self._classifier = UltimatePersonaClassifier()
        return self._classifier
        
    def score_contact(self, contact_id: int, trigger: str = 'manual') -> Dict:
        """
        Complete scoring pipeline for a contact
        
        Args:
            contact_id: Database ID of contact
            trigger: 'import', 'enrichment', or 'manual'
            
        Returns:
            Dictionary with scoring results
        """
        try:
            # Use the ApexScoringEngine which has its own database connection
            scoring_result = self.scorer.score_contact(contact_id, save_to_db=True)
            
            # Get contact data for persona classification
            cursor = self.db.cursor()
            cursor.execute("SELECT * FROM contacts WHERE id = ?", (contact_id,))
            row = cursor.fetchone()
            
            if not row:
                return {'error': 'Contact not found', 'contact_id': contact_id}
            
            contact = dict(row)
            
            # Classify persona
            tier, persona, confidence, criteria = self.classifier.classify_contact({
                'job_title': contact.get('title', ''),
                'company': contact.get('company', ''),
                'industry': contact.get('industry', ''),
                'skills': contact.get('skills', ''),
                'annual_revenue': contact.get('annual_revenue', 0),
                'employee_count': contact.get('employee_count', 0)
            })
            
            # Update persona in database
            cursor.execute("""
                UPDATE contacts SET
                    persona_tier = ?,
                    persona_type = ?,
                    persona_confidence = ?,
                    last_scored = ?
                WHERE id = ?
            """, (
                tier,
                persona,
                confidence,
                datetime.now().isoformat(),
                contact_id
            ))
            self.db.commit()
            
            # Store in scoring history
            cursor.execute("""
                INSERT INTO scoring_history 
                (contact_id, trigger, mdcp_score, rss_score, priority_score, 
                 persona_tier, persona_type, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                contact_id,
                trigger,
                scoring_result.get('mdcp_score', 0),
                scoring_result.get('rss_score', 0),
                scoring_result.get('priority_score', 0),
                tier,
                persona,
                datetime.now().isoformat()
            ))
            self.db.commit()
            
            # Return combined results
            return {
                'contact_id': contact_id,
                'name': scoring_result.get('contact_name', ''),
                'mdcp_score': scoring_result.get('mdcp_score', 0),
                'rss_score': scoring_result.get('rss_score', 0),
                'priority_score': scoring_result.get('priority_score', 0),
                'mdcp_tier': scoring_result.get('mdcp_tier', ''),
                'rss_tier': scoring_result.get('rss_tier', ''),
                'urgency_level': scoring_result.get('urgency_level', ''),
                'recommended_action': scoring_result.get('recommended_action', ''),
                'persona': {
                    'tier': tier,
                    'type': persona,
                    'confidence': round(confidence, 2)
                },
                'trigger': trigger,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'contact_id': contact_id,
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


if __name__ == "__main__":
    print("✅ ScoringOrchestrator class defined successfully")
    print(f"   Class name: {ScoringOrchestrator.__name__}")
