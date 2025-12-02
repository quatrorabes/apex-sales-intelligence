#!/usr/bin/env python3
"""
CRE-Specific Scoring Engine for Commercial Real Estate Professionals
Supports both SQLite (local) and PostgreSQL (Railway)
Version: 2.1.0 - FIXED
"""

import json
import os
from typing import Dict, Optional, List


class DatabaseAdapter:
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
    
    def close(self):
        if self.conn:
            self.conn.close()


class UserSpecificScoringEngine:
    VERSION = "2.1.0"
    
    def __init__(self, user_id: str = None, db_path: str = None):
        self.user_id = user_id or os.getenv('CURRENT_USER_ID', 'default')
        self.db_path = db_path or os.getenv('DATABASE_URL') or '/Users/chrisrabenold/projects/apex/apex.db'
        self.is_postgres = self.db_path.startswith('postgres') if self.db_path else False
        self.preferences = self._get_default_preferences()
    
    def _get_default_preferences(self) -> Dict:
        return {
            'scoring_profile': 'CRE_MORTGAGE',
            'custom_ideal_titles': ['broker', 'commercial', 'real estate', 'leasing', 'investment', 'loan officer', 'mortgage banker'],
            'custom_avoid_titles': ['residential', 'personal'],
            'ideal_company_size_min': 10,
            'ideal_company_size_max': 5000,
            'target_seniority_levels': ['VP', 'SVP', 'Director', 'Manager', 'Associate'],
            'exclude_c_suite': False
        }
    
    def _get_cre_profile(self) -> Dict:
        return {
            'exclude_departments': ['residential', 'personal banking', 'consumer', 'hr', 'human resources', 'marketing', 'it', 'legal', 'compliance', 'operations', 'administration', 'audit', 'accounting', 'tax', 'insurance', 'wealth management', 'private banking'],
            'high_value_companies': ['cbre', 'jll', 'cushman', 'colliers', 'newmark', 'marcus & millichap', 'eastdil', 'hff', 'berkadia', 'walker & dunlop', 'realty', 'properties', 'capital', 'partners', 'advisors', 'brokerage', 'commercial'],
            'cre_indicators': ['commercial', 'cre', 'broker', 'leasing', 'investment', 'capital markets', 'debt', 'mortgage', 'real estate', 'tenant rep', 'landlord rep', 'multifamily', 'office', 'retail'],
            'title_scores': {
                'principal': 85, 'owner': 85, 'partner': 85, 'managing director': 90, 'managing partner': 90,
                'senior vice president': 90, 'svp': 90, 'executive vice president': 88, 'evp': 88,
                'first vice president': 87, 'vice president': 85, 'vp': 85, 'director': 80, 'senior director': 82,
                'senior associate': 75, 'associate director': 78, 'broker': 70, 'senior broker': 75,
                'investment sales': 75, 'leasing broker': 70, 'loan officer': 70, 'mortgage banker': 72,
                'associate': 60, 'analyst': 50, 'coordinator': 40
            }
        }
    
    def calculate_personalized_rss(self, contact: Dict) -> Dict:
        title = (contact.get('title') or '').lower()
        company = (contact.get('company') or '').lower()
        
        print(f"\n=== CRE SCORING: {contact.get('name', 'Unknown')} ===")
        print(f"Title: '{title}'")
        print(f"Company: '{company}'")
        
        profile = self._get_cre_profile()
        
        # CHECK 1: Excluded departments
        for exclude in profile['exclude_departments']:
            if exclude in title:
                print(f"  ❌ EXCLUDED: '{exclude}' - Score: 10")
                return self._create_result(10, f'Excluded: {exclude}', None, None)
        
        # CHECK 2: High-value company
        company_match = any(hv in company for hv in profile['high_value_companies'])
        if company_match:
            print(f"  ⭐ HIGH-VALUE COMPANY MATCH")
        
        # CHECK 3: CRE indicators
        vertical_match = False
        matched_vertical = None
        for indicator in profile['cre_indicators']:
            if indicator in title:
                vertical_match = True
                matched_vertical = indicator
                print(f"  ✅ CRE INDICATOR: '{indicator}'")
                break
        
        if not vertical_match and company_match:
            vertical_match = True
            matched_vertical = 'cre_company'
            print(f"  ✅ CRE company employee")
        
        if not vertical_match:
            print(f"  ❌ NOT IN CRE - Score: 20")
            return self._create_result(20, 'Not in CRE', None, None)
        
        # CHECK 4: Title scoring
        title_score = 50
        matched_title = None
        for title_pattern, score_value in profile['title_scores'].items():
            if title_pattern in title:
                title_score = score_value
                matched_title = title_pattern
                print(f"  ✅ TITLE: '{title_pattern}' = {score_value}")
                break
        
        if company_match and title_score >= 70:
            title_score = min(100, title_score + 10)
            print(f"  🎯 PREMIUM COMBO: +10 bonus")
        
        if 'manager' in title and not matched_title:
            if any(w in title for w in ['portfolio', 'property', 'asset', 'relationship']):
                title_score = 65
                matched_title = 'manager (cre)'
            else:
                title_score = 45
                matched_title = 'manager (generic)'
        
        print(f"  FINAL SCORE: {title_score}")
        return self._create_result(title_score, 'CRE Professional', matched_vertical, matched_title)
    
    def _create_result(self, score: float, reason: str, vertical: Optional[str], title: Optional[str]) -> Dict:
        return {
            'total': round(min(100, max(0, score)), 2),
            'breakdown': {'score': score, 'reason': reason, 'matched_vertical': vertical, 'matched_title': title},
            'preferences_applied': True,
            'user_id': self.user_id
        }


if __name__ == "__main__":
    engine = UserSpecificScoringEngine()
    print(f"UserSpecificScoringEngine v{engine.VERSION}")
    print(f"Database: {'PostgreSQL' if engine.is_postgres else 'SQLite'}")
