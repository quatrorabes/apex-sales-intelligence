#!/usr/bin/env python3
"""
Apex Intelligence - Main Scoring Engine
Adaptive MDCP + RSS scoring with lifecycle tracking
Supports both SQLite (local) and PostgreSQL (Railway)
Version: 2.1.0 - FIXED
"""

import os
from datetime import datetime
from typing import Dict, List, Optional


class DatabaseAdapter:
    """Database adapter that supports both SQLite and PostgreSQL"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = os.getenv('DATABASE_URL') or '/Users/chrisrabenold/projects/apex/apex.db'
        
        self.db_path = db_path
        self.is_postgres = db_path.startswith('postgres') if db_path else False
        self.conn = None
        self._connect()
    
    def _connect(self):
        if self.is_postgres:
            import psycopg2
            from psycopg2.extras import RealDictCursor
            self.conn = psycopg2.connect(self.db_path)
            self._cursor = self.conn.cursor(cursor_factory=RealDictCursor)
        else:
            import sqlite3
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            self._cursor = self.conn.cursor()
    
    def execute(self, query: str, params: tuple = None):
        if self.is_postgres:
            query = query.replace('?', '%s')
        if params:
            self._cursor.execute(query, params)
        else:
            self._cursor.execute(query)
    
    def fetchone(self) -> Optional[Dict]:
        row = self._cursor.fetchone()
        return dict(row) if row else None
    
    def fetchall(self) -> List[Dict]:
        return [dict(row) for row in self._cursor.fetchall()]
    
    def commit(self):
        self.conn.commit()
    
    def rollback(self):
        self.conn.rollback()
    
    def close(self):
        if self.conn:
            self.conn.close()


class LeadTypeProfile:
    PROFILES = {
        'BANKER': {'mdcp_weights': {'Money': 0.30, 'Decision': 0.25, 'Credibility': 0.30, 'Pain': 0.15}},
        'CDC': {'mdcp_weights': {'Money': 0.35, 'Decision': 0.20, 'Credibility': 0.30, 'Pain': 0.15}},
        'BROKER': {'mdcp_weights': {'Money': 0.40, 'Decision': 0.20, 'Credibility': 0.20, 'Pain': 0.20}},
        'PRIVATE_LENDER': {'mdcp_weights': {'Money': 0.35, 'Decision': 0.25, 'Credibility': 0.25, 'Pain': 0.15}},
        'BORROWER': {'mdcp_weights': {'Money': 0.35, 'Decision': 0.25, 'Credibility': 0.25, 'Pain': 0.15}}
    }
    
    @classmethod
    def get_profile(cls, lead_type: str) -> Dict:
        if not lead_type:
            lead_type = 'BORROWER'
        return cls.PROFILES.get(lead_type.upper(), cls.PROFILES['BORROWER'])


class ApexScoringEngine:
    VERSION = "2.1.0"
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = os.getenv('DATABASE_URL') or '/Users/chrisrabenold/projects/apex/apex.db'
        self.db_path = db_path
        self.is_postgres = db_path.startswith('postgres') if db_path else False
        db_type = "PostgreSQL" if self.is_postgres else "SQLite"
        print(f"ApexScoringEngine v{self.VERSION} initialized ({db_type})")
    
    def _get_db(self) -> DatabaseAdapter:
        return DatabaseAdapter(self.db_path)
    
    def fetch_contact_data(self, contact_id: int) -> Optional[Dict]:
        db = self._get_db()
        try:
            db.execute("SELECT * FROM contacts WHERE id = ?", (contact_id,))
            return db.fetchone()
        finally:
            db.close()
    
    def score_contact(self, contact_id: int, save_to_db: bool = True) -> Dict:
        contact = self.fetch_contact_data(contact_id)
        if not contact:
            raise ValueError(f"Contact {contact_id} not found")
        
        lifecycle_stage = self.determine_lifecycle_stage(contact)
        lead_type = contact.get('lead_type') or 'BORROWER'
        
        mdcp_result = self.calculate_mdcp_score(contact, lead_type, lifecycle_stage)
        rss_result = self.calculate_rss_score(contact, lifecycle_stage)
        priority_result = self.calculate_priority_score(
            mdcp_result['total'], rss_result['total'], lifecycle_stage, lead_type
        )
        
        result = {
            'contact_id': contact_id,
            'contact_name': contact.get('name') or f"{contact.get('firstname', '')} {contact.get('lastname', '')}".strip(),
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
        profile = LeadTypeProfile.get_profile(lead_type)
        weights = profile['mdcp_weights']
        
        money = self._score_money(contact)
        decision = self._score_decision(contact)
        credibility = self._score_credibility(lifecycle_stage)
        pain = 50.0
        
        total = money * weights['Money'] + decision * weights['Decision'] + credibility * weights['Credibility'] + pain * weights['Pain']
        tier = 'HOT' if total >= 85 else 'WARM' if total >= 70 else 'QUALIFIED' if total >= 55 else 'COLD'
        
        return {'total': round(total, 2), 'Money': round(money, 2), 'Decision': round(decision, 2),
                'Credibility': round(credibility, 2), 'Pain': round(pain, 2), 'weights': weights,
                'tier': tier, 'lead_type': lead_type}
    
    def _score_money(self, contact: Dict) -> float:
        equity = contact.get('equity_percent', 0) or 0
        if equity >= 35: return 95.0
        if equity >= 30: return 90.0
        if equity >= 25: return 80.0
        if equity >= 20: return 70.0
        if equity >= 15: return 55.0
        if equity >= 10: return 40.0
        return 25.0
    
    def _score_decision(self, contact: Dict) -> float:
        title = (contact.get('title') or '').lower()
        if any(w in title for w in ['ceo', 'president', 'owner', 'founder']): return 95.0
        if any(w in title for w in ['cfo', 'chief', 'partner']): return 90.0
        if any(w in title for w in ['vp', 'vice president', 'director']): return 75.0
        if any(w in title for w in ['manager', 'head of']): return 60.0
        return 50.0
    
    def _score_credibility(self, lifecycle_stage: str) -> float:
        if lifecycle_stage == 'ESTABLISHED': return 80.0
        if lifecycle_stage == 'ACTIVE': return 65.0
        if lifecycle_stage == 'WARMING': return 50.0
        return 50.0
    
    def calculate_rss_score(self, contact: Dict, lifecycle_stage: str) -> Dict:
        title = (contact.get('title') or '').lower()
        
        seniority = 40 if any(w in title for w in ['ceo', 'cfo', 'coo', 'chief', 'president', 'founder', 'owner', 'partner']) else \
                   35 if any(w in title for w in ['vp', 'vice president', 'evp', 'svp']) else \
                   30 if 'director' in title and ('senior' in title or 'sr.' in title) else \
                   25 if 'director' in title else \
                   20 if 'manager' in title and ('senior' in title or 'sr.' in title) else \
                   15 if 'manager' in title else \
                   10 if any(w in title for w in ['specialist', 'analyst', 'coordinator', 'associate']) else 5
        
        scope = (15 if any(w in title for w in ['national', 'regional', 'global', 'international']) else 0) + \
                (10 if any(w in title for w in ['head', 'lead', 'principal']) else 0) + \
                (5 if any(w in title for w in ['senior', 'sr.']) else 0)
        
        authority = 30 if any(w in title for w in ['director', 'vp', 'president', 'chief', 'head']) else \
                   20 if any(w in title for w in ['manager', 'supervisor', 'lead']) else \
                   15 if any(w in title for w in ['senior', 'principal']) else 10
        
        total = seniority + scope + authority
        if lifecycle_stage == 'ESTABLISHED': total = min(100, total * 1.2)
        elif lifecycle_stage == 'ACTIVE': total = min(100, total * 1.1)
        elif lifecycle_stage == 'WARMING': total = min(100, total * 1.05)
        
        tier = 'PLATINUM' if total >= 80 else 'GOLD' if total >= 65 else 'SILVER' if total >= 50 else 'BRONZE'
        return {'total': round(total, 2), 'seniority': seniority, 'scope': scope, 'authority': authority, 'tier': tier}
    
    def classify_rss_tier(self, score: float) -> str:
        if score >= 80: return 'PLATINUM'
        if score >= 65: return 'GOLD'
        if score >= 50: return 'SILVER'
        return 'BRONZE'
    
    def calculate_priority_score(self, mdcp: float, rss: float, lifecycle: str, lead_type: str) -> Dict:
        if lifecycle in ['NEW', 'COLD']:
            priority = mdcp
        elif lifecycle == 'WARMING':
            priority = mdcp * 0.80 + rss * 0.20
        else:
            priority = mdcp * 0.60 + rss * 0.40
        
        urgency = 'IMMEDIATE' if priority >= 80 else 'HIGH' if priority >= 65 else 'MEDIUM' if priority >= 50 else 'LOW'
        
        if priority >= 85: action = "🔥 HOT LEAD - Immediate outreach within 1 hour"
        elif priority >= 70: action = "✅ GOOD OPPORTUNITY - Respond same day"
        elif priority >= 55: action = "📧 QUALIFIED - Standard outreach within 24 hours"
        else: action = "👀 MONITOR - Long-term nurture campaign"
        
        return {'score': round(priority, 2), 'urgency': urgency, 'action': action}
    
    def determine_lifecycle_stage(self, contact: Dict) -> str:
        created_date = contact.get('created_at')
        if not created_date:
            return 'NEW'
        try:
            if isinstance(created_date, str):
                for fmt in ['%Y-%m-%dT%H:%M:%S.%f', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d']:
                    try:
                        created_date = datetime.strptime(created_date.split('+')[0].split('Z')[0], fmt)
                        break
                    except ValueError:
                        continue
                else:
                    return 'NEW'
            days = (datetime.now() - created_date).days
        except:
            return 'NEW'
        
        if days < 30: return 'NEW'
        if days < 90: return 'WARMING'
        if days < 365: return 'ACTIVE'
        return 'ESTABLISHED'
    
    def save_scores_to_db(self, result: Dict):
        db = self._get_db()
        try:
            db.execute("""
                UPDATE contacts SET
                    mdcp_score = ?, mdcp_tier = ?, rss_score = ?, rss_tier = ?,
                    priority_score = ?, urgency_level = ?, recommended_action = ?,
                    last_scored = ?, calculation_version = ?
                WHERE id = ?
            """, (
                result['mdcp_score'], result.get('mdcp_tier'), result.get('rss_score', 0),
                result.get('rss_tier'), result['priority_score'], result.get('urgency_level'),
                result.get('recommended_action'), datetime.now().isoformat(),
                result.get('calculation_version', self.VERSION), result['contact_id']
            ))
            db.commit()
            print(f"✅ Saved scores for contact {result['contact_id']}")
        except Exception as e:
            print(f"❌ Error saving scores: {e}")
            db.rollback()
        finally:
            db.close()


if __name__ == "__main__":
    engine = ApexScoringEngine()
    print(f"Database: {'PostgreSQL' if engine.is_postgres else 'SQLite'}")
