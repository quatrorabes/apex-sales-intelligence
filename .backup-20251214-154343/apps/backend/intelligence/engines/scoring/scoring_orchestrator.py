"""
APEX Scoring Orchestrator - Coordinates scoring and persona classification
"""

from datetime import datetime
from typing import Dict, List, Optional
import json
import logging

logger = logging.getLogger(__name__)

# Import the scoring engine
try:
    from .apex_intelligence_engine import ApexScoringEngine
    SCORING_ENGINE_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Could not import ApexScoringEngine: {e}")
    SCORING_ENGINE_AVAILABLE = False
    ApexScoringEngine = None


class ScoringOrchestrator:
    """Orchestrates MDCP/RSS scoring, persona classification, and database updates"""
    
    def __init__(self, db_connection):
        """
        Initialize with database connection
        
        Args:
            db_connection: SQLite connection object
        """
        self.db = db_connection
        self._scorer = None
        self._classifier = None
        
        # Ensure scoring history table exists
        self._ensure_tables()
    
    def _ensure_tables(self):
        """Ensure scoring_history table exists"""
        try:
            cursor = self.db.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scoring_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    contact_id INTEGER NOT NULL,
                    trigger TEXT,
                    mdcp_score REAL,
                    rss_score REAL,
                    priority_score REAL,
                    persona_tier TEXT,
                    persona_type TEXT,
                    timestamp TEXT,
                    FOREIGN KEY (contact_id) REFERENCES contacts(id)
                )
            """)
            self.db.commit()
            logger.info("✅ Scoring history table verified")
        except Exception as e:
            logger.error(f"Error ensuring tables: {e}")
    
    @property
    def scorer(self):
        """Lazy load ApexScoringEngine"""
        if not self._scorer:
            if not SCORING_ENGINE_AVAILABLE:
                raise ImportError("ApexScoringEngine not available")
            self._scorer = ApexScoringEngine()
        return self._scorer
    
    @property
    def classifier(self):
        """Lazy load persona classifier"""
        if self._classifier is None:
            try:
                from intelligence.engines.scoring.persona_classifier_cre_sba import UltimatePersonaClassifier
                self._classifier = UltimatePersonaClassifier()
                logger.info("✅ Persona classifier loaded")
            except ImportError as e:
                logger.warning(f"Persona classifier not available: {e}")
                self._classifier = None
        return self._classifier
    
    def score_contact(self, contact_id: int, trigger: str = 'manual') -> Dict:
        """
        Complete scoring pipeline for a contact
        
        Args:
            contact_id: Database ID of contact
            trigger: 'import', 'enrichment', 'manual', or 'batch'
            
        Returns:
            Dictionary with scoring results or error
        """
        try:
            logger.info(f"🎯 Scoring contact {contact_id} (trigger: {trigger})")
            
            # Get contact data first
            cursor = self.db.cursor()
            cursor.execute("SELECT * FROM contacts WHERE id = ?", (contact_id,))
            row = cursor.fetchone()
            
            if not row:
                return {
                    'error': 'Contact not found',
                    'contact_id': contact_id
                }
            
            # Convert row to dict
            columns = [desc[0] for desc in cursor.description]
            contact = dict(zip(columns, row))
            
            # Run ApexScoringEngine
            scoring_result = self.scorer.score_contact(contact_id, save_to_db=True)
            
            if 'error' in scoring_result:
                return scoring_result
            
            # Classify persona if classifier is available
            persona_data = {'tier': None, 'type': None, 'confidence': 0}
            
            if self.classifier:
                try:
                    tier, persona, confidence, criteria = self.classifier.classify_contact({
                        'job_title': contact.get('title', ''),
                        'company': contact.get('company', ''),
                        'industry': contact.get('industry', ''),
                        'skills': contact.get('skills', ''),
                        'annual_revenue': contact.get('annual_revenue', 0),
                        'employee_count': contact.get('employee_count', 0)
                    })
                    
                    persona_data = {
                        'tier': tier,
                        'type': persona,
                        'confidence': round(confidence, 2)
                    }
                    
                    # Update persona in contacts table
                    cursor.execute("""
                        UPDATE contacts SET
                            persona_tier = ?,
                            persona_type = ?,
                            persona_confidence = ?
                        WHERE id = ?
                    """, (tier, persona, confidence, contact_id))
                    self.db.commit()
                    
                    logger.info(f"✅ Persona classified: {tier} - {persona}")
                    
                except Exception as e:
                    logger.warning(f"Persona classification failed: {e}")
            
            # Store in scoring history
            try:
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
                    persona_data['tier'],
                    persona_data['type'],
                    datetime.now().isoformat()
                ))
                self.db.commit()
            except Exception as e:
                logger.warning(f"Could not save to scoring_history: {e}")
            
            # Return combined results
            result = {
                'contact_id': contact_id,
                'name': contact.get('name', ''),
                'mdcp_score': scoring_result.get('mdcp_score', 0),
                'rss_score': scoring_result.get('rss_score', 0),
                'priority_score': scoring_result.get('priority_score', 0),
                'mdcp_tier': scoring_result.get('mdcp_tier', ''),
                'rss_tier': scoring_result.get('rss_tier', ''),
                'urgency_level': scoring_result.get('urgency_level', ''),
                'recommended_action': scoring_result.get('recommended_action', ''),
                'persona': persona_data,
                'trigger': trigger,
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"✅ Contact {contact_id} scored: Priority={result['priority_score']}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error scoring contact {contact_id}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {
                'error': str(e),
                'contact_id': contact_id,
                'timestamp': datetime.now().isoformat()
            }
    
    def bulk_score(self, contact_ids: List[int], trigger: str = 'batch') -> List[Dict]:
        """
        Score multiple contacts efficiently
        
        Args:
            contact_ids: List of contact IDs to score
            trigger: Reason for scoring
            
        Returns:
            List of scoring results
        """
        logger.info(f"🎯 Starting bulk scoring for {len(contact_ids)} contacts")
        
        results = []
        for i, contact_id in enumerate(contact_ids, 1):
            try:
                logger.info(f"Scoring {i}/{len(contact_ids)}: contact {contact_id}")
                result = self.score_contact(contact_id, trigger)
                results.append(result)
            except Exception as e:
                logger.error(f"Error scoring contact {contact_id}: {e}")
                results.append({
                    'contact_id': contact_id,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
        
        logger.info(f"✅ Bulk scoring complete: {len(results)} results")
        return results
    
    def score_after_import(self, contact_ids: List[int]) -> List[Dict]:
        """Score contacts immediately after CSV or HubSpot import"""
        logger.info(f"Scoring {len(contact_ids)} contacts after import")
        return self.bulk_score(contact_ids, trigger='import')
    
    def score_after_enrichment(self, contact_id: int) -> Dict:
        """Re-score contact after Perplexity enrichment completes"""
        logger.info(f"Scoring contact {contact_id} after enrichment")
        return self.score_contact(contact_id, trigger='enrichment')


if __name__ == "__main__":
    print("✅ ScoringOrchestrator class defined successfully")
    print(f"   Class name: {ScoringOrchestrator.__name__}")
    print(f"   Scoring engine available: {SCORING_ENGINE_AVAILABLE}")
