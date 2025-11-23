"""
Apex Intelligence - Main Scoring Engine
Adaptive MDCP + RSS scoring with lifecycle tracking for commercial real estate lending
Version: 1.0.0
"""

import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import statistics
import json

# ============================================================================
# INLINE UTILITIES (replacing relative imports)
# ============================================================================

def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safely divide two numbers"""
    try:
        return numerator / denominator if denominator != 0 else default
    except:
        return default

def normalize_score(value: float, min_val: float, max_val: float) -> float:
    """Normalize a value to 0-100 scale"""
    if max_val == min_val:
        return 50.0
    return max(0, min(100, ((value - min_val) / (max_val - min_val)) * 100))

def calculate_days_between(date1, date2=None) -> int:
    """Calculate days between two dates"""
    if date2 is None:
        date2 = datetime.now()
    try:
        if isinstance(date1, str):
            date1 = datetime.fromisoformat(date1.replace('Z', '+00:00'))
        if isinstance(date2, str):
            date2 = datetime.fromisoformat(date2.replace('Z', '+00:00'))
        return abs((date2 - date1).days)
    except:
        return 0

# ============================================================================
# LEAD TYPE PROFILES
# ============================================================================

class LeadTypeProfile:
    """Lead type configuration and MDCP weights"""
    
    PROFILES = {
        'BANKER': {
            'mdcp_weights': {'Money': 0.30, 'Decision': 0.25, 'Credibility': 0.30, 'Pain': 0.15}
        },
        'CDC': {
            'mdcp_weights': {'Money': 0.35, 'Decision': 0.20, 'Credibility': 0.30, 'Pain': 0.15}
        },
        'BROKER': {
            'mdcp_weights': {'Money': 0.40, 'Decision': 0.20, 'Credibility': 0.20, 'Pain': 0.20}
        },
        'PRIVATE_LENDER': {
            'mdcp_weights': {'Money': 0.35, 'Decision': 0.25, 'Credibility': 0.25, 'Pain': 0.15}
        },
        'BORROWER': {
            'mdcp_weights': {'Money': 0.35, 'Decision': 0.25, 'Credibility': 0.25, 'Pain': 0.15}
        }
    }
    
    @classmethod
    def get_profile(cls, lead_type: str) -> Dict:
        """Get profile for lead type"""
        return cls.PROFILES.get(lead_type.upper(), cls.PROFILES['BORROWER'])

# ============================================================================
# MAIN SCORING ENGINE
# ============================================================================

class ApexScoringEngine:
    """Main scoring engine for Apex Intelligence"""
    
    VERSION = "1.0.0"
    
    def __init__(self, db_path: str = "./apex.db"):
        """Initialize scoring engine"""
        self.db_path = db_path
        self.db = sqlite3.connect(db_path)
        self.db.row_factory = sqlite3.Row
        self.cursor = self.db.cursor()
    
    def __del__(self):
        """Clean up database connection"""
        if hasattr(self, 'db'):
            self.db.close()
    
    def score_contact(self, contact_id: int, save_to_db: bool = True) -> Dict:
        """Complete scoring for a single contact"""
        
        contact = self.fetch_contact_data(contact_id)
        if not contact:
            raise ValueError(f"Contact {contact_id} not found")
        
        contact = dict(contact)
        
        # Determine lifecycle stage
        lifecycle_stage = self.determine_lifecycle_stage(contact)
        lead_type = contact.get('lead_type', 'BORROWER')
        
        # Calculate scores
        mdcp_result = self.calculate_mdcp_score(contact, lead_type, lifecycle_stage)
        rss_result = self.calculate_rss_score(contact, lifecycle_stage)
        priority_result = self.calculate_priority_score(
            mdcp_result['total'],
            rss_result['total'] if rss_result['total'] else 0,
            lifecycle_stage,
            lead_type
        )
        
        result = {
            'contact_id': contact_id,
            'contact_name': f"{contact.get('first_name', '')} {contact.get('last_name', '')}".strip(),
            'company': contact.get('company', ''),
            'lead_type': lead_type,
            'lifecycle_stage': lifecycle_stage,
            'mdcp_score': mdcp_result['total'],
            'mdcp_tier': mdcp_result['tier'],
            'mdcp_breakdown': mdcp_result,
            'rss_score': rss_result['total'],
            'rss_tier': rss_result['tier'],
            'rss_breakdown': rss_result,
            'priority_score': priority_result['score'],
            'urgency_level': priority_result['urgency'],
            'recommended_action': priority_result['action'],
            'calculated_at': datetime.now().isoformat(),
            'calculation_version': self.VERSION
        }
        
        if save_to_db:
            self.save_scores_to_db(result)
        
        return result
    
    def calculate_mdcp_score(self, contact: Dict, lead_type: str, lifecycle_stage: str) -> Dict:
        """Calculate MDCP score"""
        
        profile = LeadTypeProfile.get_profile(lead_type)
        weights = profile['mdcp_weights']
        
        # Calculate components
        money_score = self.score_money(contact, lead_type)
        decision_score = self.score_decision(contact, lead_type)
        credibility_score = self.score_credibility(contact, lead_type, lifecycle_stage)
        pain_score = self.score_pain(contact, lead_type)
        
        # Apply weights
        total = (
            money_score * weights['Money'] +
            decision_score * weights['Decision'] +
            credibility_score * weights['Credibility'] +
            pain_score * weights['Pain']
        )
        
        tier = self.classify_mdcp_tier(total)
        
        return {
            'total': round(total, 2),
            'Money': round(money_score, 2),
            'Decision': round(decision_score, 2),
            'Credibility': round(credibility_score, 2),
            'Pain': round(pain_score, 2),
            'weights': weights,
            'tier': tier,
            'lead_type': lead_type
        }
    
    def score_money(self, contact: Dict, lead_type: str) -> float:
        """Score Money component"""
        # Simplified - customize based on your data
        equity_percent = contact.get('equity_percent', 0) or 0
        
        if equity_percent >= 35:
            return 95.0
        elif equity_percent >= 30:
            return 90.0
        elif equity_percent >= 25:
            return 80.0
        elif equity_percent >= 20:
            return 70.0
        elif equity_percent >= 15:
            return 55.0
        elif equity_percent >= 10:
            return 40.0
        else:
            return 25.0
    
    def score_decision(self, contact: Dict, lead_type: str) -> float:
        """Score Decision authority"""
        job_title = (contact.get('title') or '').lower()
        
        if any(word in job_title for word in ['ceo', 'president', 'owner', 'founder']):
            return 95.0
        elif any(word in job_title for word in ['cfo', 'chief', 'partner']):
            return 90.0
        elif any(word in job_title for word in ['vp', 'vice president', 'director']):
            return 75.0
        elif any(word in job_title for word in ['manager', 'head of']):
            return 60.0
        else:
            return 50.0
    
    def score_credibility(self, contact: Dict, lead_type: str, lifecycle_stage: str) -> float:
        """Score Credibility"""
        base_score = 50.0
        
        # Adjust based on lifecycle
        if lifecycle_stage == 'ESTABLISHED':
            base_score = 80.0
        elif lifecycle_stage == 'ACTIVE':
            base_score = 65.0
        elif lifecycle_stage == 'WARMING':
            base_score = 50.0
        
        return base_score
    
    def score_pain(self, contact: Dict, lead_type: str) -> float:
        """Score Pain/Urgency"""
        # Default medium urgency
        return 50.0
    
    def classify_mdcp_tier(self, score: float) -> str:
        """Classify MDCP score into tier"""
        if score >= 85:
            return 'HOT'
        elif score >= 70:
            return 'WARM'
        elif score >= 55:
            return 'QUALIFIED'
        else:
            return 'COLD'
    
    def calculate_rss_score(self, contact: Dict, lifecycle_stage: str) -> Dict:
        """Calculate RSS score"""
        
        if lifecycle_stage == 'NEW':
            return {
                'total': 0,
                'familiarity': 0,
                'engagement': 0,
                'productivity': 0,
                'tier': 'N/A'
            }
        
        # Simplified RSS
        base_score = 50.0
        
        if lifecycle_stage == 'ESTABLISHED':
            base_score = 75.0
        elif lifecycle_stage == 'ACTIVE':
            base_score = 60.0
        
        return {
            'total': round(base_score, 2),
            'familiarity': round(base_score * 0.4, 2),
            'engagement': round(base_score * 0.3, 2),
            'productivity': round(base_score * 0.3, 2),
            'tier': self.classify_rss_tier(base_score)
        }
    
    def classify_rss_tier(self, score: float) -> str:
        """Classify RSS score"""
        if score >= 80:
            return 'PLATINUM'
        elif score >= 65:
            return 'GOLD'
        elif score >= 50:
            return 'SILVER'
        else:
            return 'BRONZE'
    
    def calculate_priority_score(self, mdcp: float, rss: float, lifecycle: str, lead_type: str) -> Dict:
        """Calculate priority score"""
        
        if lifecycle in ['NEW', 'COLD']:
            priority = mdcp
        elif lifecycle == 'WARMING':
            priority = mdcp * 0.80 + rss * 0.20
        else:
            priority = mdcp * 0.60 + rss * 0.40
        
        if priority >= 80:
            urgency = 'IMMEDIATE'
        elif priority >= 65:
            urgency = 'HIGH'
        elif priority >= 50:
            urgency = 'MEDIUM'
        else:
            urgency = 'LOW'
        
        action = self.get_recommended_action(priority, mdcp, rss, lifecycle, lead_type, urgency)
        
        return {
            'score': round(priority, 2),
            'urgency': urgency,
            'action': action
        }
    
    def get_recommended_action(self, priority: float, mdcp: float, rss: float, lifecycle: str, lead_type: str, urgency: str) -> str:
        """Generate actionable recommendation"""
        if priority >= 85:
            return "🔥 HOT LEAD - Immediate outreach within 1 hour"
        elif priority >= 70:
            return "✅ GOOD OPPORTUNITY - Respond same day"
        elif priority >= 55:
            return "📧 QUALIFIED - Standard outreach within 24 hours"
        else:
            return "👀 MONITOR - Long-term nurture campaign"
    
    def determine_lifecycle_stage(self, contact: Dict) -> str:
        """Determine lifecycle stage"""
        created_date = contact.get('created_at')
        
        if not created_date:
            return 'NEW'
        
        try:
            if isinstance(created_date, str):
                created_date = datetime.fromisoformat(created_date.replace('Z', '+00:00'))
            days_since_created = (datetime.now(created_date.tzinfo) - created_date).days
        except:
            return 'NEW'
        
        if days_since_created < 30:
            return 'NEW'
        elif days_since_created < 90:
            return 'WARMING'
        elif days_since_created < 365:
            return 'ACTIVE'
        else:
            return 'ESTABLISHED'
    
    def fetch_contact_data(self, contact_id: int) -> Optional[Dict]:
        """Fetch contact data"""
        self.cursor.execute("SELECT * FROM contacts WHERE id = ?", (contact_id,))
        return self.cursor.fetchone()
    
    def save_scores_to_db(self, result: Dict):
        """Save scores to database"""
        contact_id = result['contact_id']
        
        try:
            # Update contact table with scores
            self.cursor.execute('''
                UPDATE contacts SET
                    opportunity_score = ?,
                    lead_tier = ?,
                    enrichment_data = ?,
                    enriched_at = ?,
                    enrichment_status = 'complete'
                WHERE id = ?
            ''', (
                result['mdcp_score'],
                result['mdcp_tier'],
                json.dumps(result),
                datetime.now().isoformat(),
                contact_id
            ))
            
            self.db.commit()
            print(f"✅ Saved scores for contact {contact_id}")
            
        except Exception as e:
            print(f"❌ Error saving scores: {e}")
            self.db.rollback()

# Quick score function
def score_contact(contact_id: int, db_path: str = "./apex.db") -> Dict:
    """Quick function to score a single contact"""
    engine = ApexScoringEngine(db_path)
    return engine.score_contact(contact_id)

if __name__ == "__main__":
    import sys
    db_path = sys.argv[1] if len(sys.argv) > 1 else "./apex.db"
    engine = ApexScoringEngine(db_path)
    print("APEX Intelligence - Scoring Engine Ready")
