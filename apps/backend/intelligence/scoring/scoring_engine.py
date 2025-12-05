#!/usr/bin/env python3
"""
=============================================================================
APEX SCORING ENGINE - Match-Based Lead Scoring
=============================================================================
Location: apps/backend/intelligence/scoring/scoring_engine.py

Calculates:
- FIT: How well contact matches user's ideal client profile
- RELEVANCE: How well user's solutions match contact's pain points
- TIMING: Urgency signals and trigger events
- MATCH: Combined score (FIT × RELEVANCE × TIMING)

Usage:
    from apps.backend.intelligence.scoring.scoring_engine import ApexScoringEngine
    
    engine = ApexScoringEngine(user_id='default')
    result = engine.score_contact(contact_dict, enrichment_text)
=============================================================================
"""

import json
import os
import re
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Tuple

DATABASE = os.getenv('DATABASE_URL', '/Users/chrisrabenold/projects/apex/apex.db')

# =============================================================================
# DATABASE HELPERS
# =============================================================================

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# =============================================================================
# APEX SCORING ENGINE
# =============================================================================

class ApexScoringEngine:
    """
    Match-based scoring: Does THIS contact match THIS user's ideal client?
    """
    
    VERSION = "3.0.0"
    
    def __init__(self, user_id: str = 'default'):
        self.user_id = user_id
        self.user_profile = self._load_user_profile()
        self.proof_points = self._load_proof_points()
    
    # =========================================================================
    # PROFILE LOADING
    # =========================================================================
    
    def _load_user_profile(self) -> Dict:
        """Load user's profile and preferences."""
        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM user_profile WHERE user_id = ?', (self.user_id,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    'role': row['role'],
                    'company': row['company'],
                    'products_services': json.loads(row['products_services'] or '[]'),
                    'asset_types': json.loads(row['asset_types'] or '[]'),
                    'loan_types': json.loads(row['loan_types'] or '[]'),
                    'sweet_spot_min': row['sweet_spot_min'] or 0,
                    'sweet_spot_max': row['sweet_spot_max'] or 100000000,
                    'geographic_markets': json.loads(row['geographic_markets'] or '[]'),
                    'ideal_titles': json.loads(row['ideal_titles'] or '[]'),
                    'ideal_company_types': json.loads(row['ideal_company_types'] or '[]'),
                    'ideal_deal_triggers': json.loads(row['ideal_deal_triggers'] or '[]'),
                    'avoid_titles': json.loads(row['avoid_titles'] or '[]'),
                    'avoid_company_types': json.loads(row['avoid_company_types'] or '[]'),
                    'differentiators': row['differentiators'],
                    'weight_title_match': row['weight_title_match'] or 30,
                    'weight_company_match': row['weight_company_match'] or 25,
                    'weight_deal_size_match': row['weight_deal_size_match'] or 20,
                    'weight_geography_match': row['weight_geography_match'] or 15,
                    'weight_timing': row['weight_timing'] or 10,
                }
        except Exception as e:
            print(f"Error loading user profile: {e}")
        
        return self._get_default_profile()
    
    def _get_default_profile(self) -> Dict:
        """Default CRE lender profile."""
        return {
            'role': 'commercial_banker',
            'company': '',
            'products_services': ['Bridge Loans', 'Permanent Financing', 'Construction Loans', 'SBA Loans'],
            'asset_types': ['Multifamily', 'Retail', 'Industrial', 'Office', 'Mixed-Use'],
            'loan_types': ['Bridge', 'Perm', 'Construction', 'SBA 7a', 'SBA 504'],
            'sweet_spot_min': 500000,
            'sweet_spot_max': 25000000,
            'geographic_markets': [],
            'ideal_titles': [
                'principal', 'owner', 'partner', 'managing director', 'president',
                'ceo', 'cfo', 'svp', 'senior vice president', 'vice president', 'vp',
                'director', 'head of', 'broker', 'senior broker', 'investment sales'
            ],
            'ideal_company_types': [
                'brokerage', 'developer', 'investor', 'reit', 'family office',
                'private equity', 'syndicator', 'owner operator'
            ],
            'ideal_deal_triggers': [
                'acquisition', 'refinance', 'construction', 'value-add',
                'portfolio growth', 'rate reset', 'maturity'
            ],
            'avoid_titles': ['residential', 'personal', 'consumer', 'retail banking'],
            'avoid_company_types': ['residential', 'single family'],
            'differentiators': '',
            'weight_title_match': 30,
            'weight_company_match': 25,
            'weight_deal_size_match': 20,
            'weight_geography_match': 15,
            'weight_timing': 10,
        }
    
    def _load_proof_points(self) -> Dict:
        """Load user's proof points."""
        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM proof_points WHERE user_id = ?', (self.user_id,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    'deals_closed_12mo': row['deals_closed_12mo'] or 0,
                    'total_volume_12mo': row['total_volume_12mo'] or 0,
                    'avg_close_days': row['avg_close_days'] or 0,
                    'approval_rate': row['approval_rate'] or 0,
                    'notable_deals': json.loads(row['notable_deals'] or '[]'),
                    'lender_relationships': json.loads(row['lender_relationships'] or '[]'),
                }
        except Exception as e:
            print(f"Error loading proof points: {e}")
        
        return {'deals_closed_12mo': 0, 'total_volume_12mo': 0, 'notable_deals': []}
    
    # =========================================================================
    # FIT SCORING
    # =========================================================================
    
    def _calculate_fit_score(self, contact: Dict) -> Tuple[float, Dict]:
        """
        FIT: How well does this contact match my ideal client profile?
        """
        title = (contact.get('title') or '').lower()
        company = (contact.get('company') or '').lower()
        
        breakdown = {
            'title_score': 0,
            'title_match': None,
            'company_type_score': 0,
            'company_match': None,
            'excluded': False,
            'exclude_reason': None,
        }
        
        # CHECK: Exclusions first
        for avoid in self.user_profile['avoid_titles']:
            if avoid.lower() in title:
                breakdown['excluded'] = True
                breakdown['exclude_reason'] = f"Title contains '{avoid}'"
                return 0, breakdown
        
        for avoid in self.user_profile['avoid_company_types']:
            if avoid.lower() in company:
                breakdown['excluded'] = True
                breakdown['exclude_reason'] = f"Company type '{avoid}'"
                return 0, breakdown
        
        # TITLE SCORING
        title_scores = {
            'ceo': 95, 'chief executive': 95, 'owner': 95, 'founder': 95,
            'president': 92, 'principal': 90, 'partner': 90,
            'managing director': 88, 'managing partner': 88,
            'evp': 85, 'executive vice president': 85,
            'svp': 85, 'senior vice president': 85,
            'first vice president': 82,
            'vp': 80, 'vice president': 80,
            'head of': 78, 'director': 75, 'senior director': 77,
            'senior broker': 72, 'investment sales': 72,
            'broker': 68, 'leasing': 65,
            'senior manager': 62, 'manager': 55,
            'senior associate': 50, 'associate': 45,
            'analyst': 35, 'coordinator': 30,
        }
        
        for title_key, score in title_scores.items():
            if title_key in title:
                breakdown['title_score'] = score
                breakdown['title_match'] = title_key
                break
        
        # If no match but title exists, give base score
        if breakdown['title_score'] == 0 and title:
            breakdown['title_score'] = 40
            breakdown['title_match'] = 'other'
        
        # COMPANY TYPE SCORING
        high_value_companies = [
            'cbre', 'jll', 'cushman', 'colliers', 'newmark', 'marcus & millichap',
            'eastdil', 'hff', 'berkadia', 'walker & dunlop', 'meridian',
        ]
        
        company_indicators = {
            'brokerage': 80, 'realty': 75, 'properties': 75, 'capital': 75,
            'partners': 70, 'advisors': 70, 'investments': 72, 'investment': 72,
            'development': 68, 'developer': 68, 'developers': 68,
            'holdings': 65, 'group': 60, 'management': 55,
            'bank': 50, 'credit union': 50, 'lending': 50,
        }
        
        # Check high-value companies first
        for hv in high_value_companies:
            if hv in company:
                breakdown['company_type_score'] = 90
                breakdown['company_match'] = hv
                break
        
        # Then check indicators
        if breakdown['company_type_score'] == 0:
            for indicator, score in company_indicators.items():
                if indicator in company:
                    breakdown['company_type_score'] = score
                    breakdown['company_match'] = indicator
                    break
        
        # If no match but company exists, give base score
        if breakdown['company_type_score'] == 0 and company:
            breakdown['company_type_score'] = 35
            breakdown['company_match'] = 'other'
        
        # WEIGHTED FIT
        title_weight = self.user_profile['weight_title_match'] / 100
        company_weight = self.user_profile['weight_company_match'] / 100
        
        # Normalize weights
        total_weight = title_weight + company_weight
        title_weight = title_weight / total_weight
        company_weight = company_weight / total_weight
        
        fit_score = (
            breakdown['title_score'] * title_weight +
            breakdown['company_type_score'] * company_weight
        )
        
        return round(fit_score, 1), breakdown
    
    # =========================================================================
    # RELEVANCE SCORING
    # =========================================================================
    
    def _calculate_relevance_score(self, contact: Dict, enrichment: str) -> Tuple[float, Dict]:
        """
        RELEVANCE: How well do my solutions match their needs/pain points?
        """
        text = (enrichment or '').lower()
        title = (contact.get('title') or '').lower()
        
        breakdown = {
            'pain_matches': [],
            'solution_matches': [],
            'deal_trigger_matches': [],
        }
        
        score = 0
        
        # PAIN POINT DETECTION
        pain_patterns = {
            'rate pressure': 15,
            'maturity': 15, 'maturing': 15, 'maturities': 15,
            'refinance': 12, 'refi': 12,
            'acquisition': 12, 'acquiring': 10,
            'construction': 12, 'develop': 10,
            'bridge': 10, 'short-term': 8,
            'capital': 8, 'funding': 8, 'financing': 8,
            'growth': 6, 'expansion': 6, 'expanding': 6,
            'portfolio': 6, 'assets under management': 6,
            'challenge': 5, 'difficult': 5, 'struggle': 5,
            'tight timeline': 10, 'fast close': 10, 'quick': 8,
        }
        
        for pattern, points in pain_patterns.items():
            if pattern in text:
                count = min(text.count(pattern), 2)  # Cap at 2 occurrences
                score += points * count
                breakdown['pain_matches'].append(pattern)
        
        # SOLUTION MATCHES (my products match their needs)
        my_products = [p.lower() for p in self.user_profile['products_services']]
        my_assets = [a.lower() for a in self.user_profile['asset_types']]
        
        for product in my_products:
            if product in text:
                score += 10
                breakdown['solution_matches'].append(product)
        
        for asset in my_assets:
            if asset in text:
                score += 8
                breakdown['solution_matches'].append(asset)
        
        # DEAL TRIGGER MATCHES
        triggers = self.user_profile['ideal_deal_triggers']
        for trigger in triggers:
            if trigger.lower() in text:
                score += 12
                breakdown['deal_trigger_matches'].append(trigger)
        
        # Cap and normalize to 0-100
        relevance_score = min(100, score)
        
        return round(relevance_score, 1), breakdown
    
    # =========================================================================
    # TIMING SCORING
    # =========================================================================
    
    def _calculate_timing_score(self, contact: Dict, enrichment: str) -> Tuple[float, Dict]:
        """
        TIMING: Urgency signals - why reach out NOW?
        """
        text = (enrichment or '').lower()
        
        breakdown = {
            'urgency_signals': [],
            'timing_triggers': [],
            'recent_news': [],
        }
        
        score = 0
        
        # URGENCY SIGNALS
        urgency_patterns = {
            'recently': 15, 'just announced': 15, 'this week': 15,
            'this month': 12, 'this quarter': 10,
            'planning': 10, 'looking to': 10, 'seeking': 10,
            'in the market': 15, 'actively': 12,
            'q4': 8, 'q1': 8, 'year-end': 10, 'fiscal year': 8,
            'budget': 8, 'budget cycle': 10,
            'new role': 12, 'just joined': 12, 'recently promoted': 12,
            'announced': 10, 'launching': 10, 'expanding': 10,
            'hiring': 8, 'growing': 8,
        }
        
        for pattern, points in urgency_patterns.items():
            if pattern in text:
                score += points
                breakdown['urgency_signals'].append(pattern)
        
        # TIMING TRIGGERS (from user's preferences)
        for trigger in self.user_profile.get('ideal_deal_triggers', []):
            if trigger.lower() in text:
                score += 10
                breakdown['timing_triggers'].append(trigger)
        
        # NEWS INDICATORS
        news_patterns = ['news', 'announced', 'press release', 'report']
        for pattern in news_patterns:
            if pattern in text:
                score += 5
                breakdown['recent_news'].append(pattern)
        
        timing_score = min(100, score)
        
        return round(timing_score, 1), breakdown
    
    # =========================================================================
    # MAIN SCORING METHOD
    # =========================================================================
    
    def score_contact(self, contact: Dict, enrichment: str = '') -> Dict:
        """
        Calculate comprehensive MATCH score.
        
        MATCH = (FIT × 0.4) + (RELEVANCE × 0.4) + (TIMING × 0.2)
        """
        fit_score, fit_breakdown = self._calculate_fit_score(contact)
        relevance_score, relevance_breakdown = self._calculate_relevance_score(contact, enrichment)
        timing_score, timing_breakdown = self._calculate_timing_score(contact, enrichment)
        
        # Check exclusions
        if fit_breakdown.get('excluded'):
            return {
                'match_score': 0,
                'match_tier': 'EXCLUDED',
                'fit_score': 0,
                'relevance_score': 0,
                'timing_score': 0,
                'excluded': True,
                'exclude_reason': fit_breakdown.get('exclude_reason'),
                'breakdown': {
                    'fit': fit_breakdown,
                    'relevance': relevance_breakdown,
                    'timing': timing_breakdown,
                }
            }
        
        # WEIGHTED MATCH SCORE
        match_score = (
            fit_score * 0.40 +
            relevance_score * 0.40 +
            timing_score * 0.20
        )
        
        # TIER CLASSIFICATION
        if match_score >= 75:
            tier = 'HIGH'
        elif match_score >= 50:
            tier = 'MEDIUM'
        elif match_score >= 25:
            tier = 'LOW'
        else:
            tier = 'MINIMAL'
        
        return {
            'match_score': round(match_score, 1),
            'match_tier': tier,
            'fit_score': fit_score,
            'relevance_score': relevance_score,
            'timing_score': timing_score,
            'excluded': False,
            'breakdown': {
                'fit': fit_breakdown,
                'relevance': relevance_breakdown,
                'timing': timing_breakdown,
            },
            'user_id': self.user_id,
            'scored_at': datetime.now().isoformat(),
        }
    
    def score_contact_by_id(self, contact_id: int) -> Dict:
        """Score a contact from the database by ID."""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM contacts WHERE id = ?', (contact_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return {'error': 'Contact not found'}
        
        contact = dict(row)
        enrichment = contact.get('enrichment_data') or ''
        
        return self.score_contact(contact, enrichment)
    
    # =========================================================================
    # QUICK SCORING (for Cold Call Queue - minimal data)
    # =========================================================================
    
    def quick_score(self, name: str, title: str = '', company: str = '') -> Dict:
        """
        Quick fit score for cold call queue (minimal data).
        Just title + company, no enrichment.
        """
        contact = {'name': name, 'title': title, 'company': company}
        fit_score, fit_breakdown = self._calculate_fit_score(contact)
        
        # Simple tier for quick scoring
        if fit_score >= 70:
            tier = 'HIGH'
            priority = 1
        elif fit_score >= 50:
            tier = 'MEDIUM'
            priority = 2
        else:
            tier = 'LOW'
            priority = 3
        
        return {
            'quick_fit_score': fit_score,
            'quick_fit_tier': tier,
            'priority': priority,
            'title_match': fit_breakdown.get('title_match'),
            'company_match': fit_breakdown.get('company_match'),
            'excluded': fit_breakdown.get('excluded', False),
            'exclude_reason': fit_breakdown.get('exclude_reason'),
        }


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def score_contact(contact: Dict, enrichment: str = '', user_id: str = 'default') -> Dict:
    """Convenience function to score a contact."""
    engine = ApexScoringEngine(user_id)
    return engine.score_contact(contact, enrichment)


def quick_score(name: str, title: str = '', company: str = '', user_id: str = 'default') -> Dict:
    """Convenience function for quick scoring."""
    engine = ApexScoringEngine(user_id)
    return engine.quick_score(name, title, company)


# =============================================================================
# CLI
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("APEX SCORING ENGINE v3.0")
    print("=" * 60)
    
    engine = ApexScoringEngine()
    
    # Test contact
    test_contact = {
        'name': 'Greg Richter',
        'title': 'CEO',
        'company': 'Medalist Partners',
    }
    
    test_enrichment = """
    Greg Richter is CEO of Medalist Partners, a $2B alternative credit fund.
    They focus on bridge lending and value-add multifamily acquisitions.
    Recently announced expansion into senior housing sector.
    Looking to deploy capital in Q4. Budget cycle ends December.
    Pain points include finding quality deal flow and quick execution.
    """
    
    result = engine.score_contact(test_contact, test_enrichment)
    
    print(f"\nContact: {test_contact['name']}")
    print(f"Title: {test_contact['title']}")
    print(f"Company: {test_contact['company']}")
    print("-" * 40)
    print(f"MATCH Score: {result['match_score']}")
    print(f"MATCH Tier: {result['match_tier']}")
    print(f"  FIT: {result['fit_score']}")
    print(f"  RELEVANCE: {result['relevance_score']}")
    print(f"  TIMING: {result['timing_score']}")
    print("-" * 40)
    print(f"Breakdown: {json.dumps(result['breakdown'], indent=2)}")
