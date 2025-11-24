"""
Enhanced scoring engine for CRE professionals (brokers, leasing, mortgage)
"""
import json
import sqlite3
from typing import Dict, Optional, List, Tuple
import os

class UserSpecificScoringEngine:
    """Scoring that targets CRE professionals who need financing"""
    
    def __init__(self, user_id: str = None, db_path: str = None):
        self.user_id = user_id or os.getenv('CURRENT_USER_ID', 'default')
        self.db_path = db_path or '/Users/chrisrabenold/projects/apex/apex.db'
        self.preferences = self._load_user_preferences()
        
    def _load_user_preferences(self) -> Dict:
        """Load user's scoring preferences from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM user_preferences WHERE user_id = ?
            ''', (self.user_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    'scoring_profile': row['scoring_profile'],
                    'custom_ideal_titles': json.loads(row['custom_ideal_titles'] or '[]'),
                    'custom_avoid_titles': json.loads(row['custom_avoid_titles'] or '[]'),
                    'ideal_company_size_min': row['ideal_company_size_min'],
                    'ideal_company_size_max': row['ideal_company_size_max'],
                    'target_seniority_levels': json.loads(row['target_seniority_levels'] or '[]'),
                    'exclude_c_suite': row['exclude_c_suite']
                }
        except Exception as e:
            print(f"Error loading preferences: {e}")
            
        return self._get_default_preferences()
    
    def _get_default_preferences(self) -> Dict:
        """CRE-specific preferences"""
        return {
            'scoring_profile': 'CRE_MORTGAGE',
            'custom_ideal_titles': [
                'broker', 'commercial', 'real estate', 'leasing', 'investment',
                'loan officer', 'mortgage banker', 'relationship manager'
            ],
            'custom_avoid_titles': ['residential', 'personal'],
            'ideal_company_size_min': 10,
            'ideal_company_size_max': 5000,
            'target_seniority_levels': ['VP', 'SVP', 'Director', 'Manager', 'Associate'],
            'exclude_c_suite': False  # CRE owners/principals might be good
        }
    
    def _get_vertical_profiles(self) -> Dict:
        """Define target verticals for CRE mortgage business"""
        return {
            'CRE_MORTGAGE': {
                'target_departments': [
                    # PRIMARY TARGETS - Your customers
                    'commercial real estate', 'cre', 'commercial broker',
                    'investment sales', 'investment broker',
                    'leasing', 'tenant rep', 'tenant representation',
                    'landlord rep', 'landlord representation',
                    'property management', 'asset management',
                    'capital markets', 'debt placement',
                    'mortgage broker', 'mortgage banking',
                    
                    # SECONDARY TARGETS - Referral sources
                    'commercial banking', 'commercial lending',
                    'real estate finance', 'structured finance',
                    'private equity', 'real estate investment',
                    'development', 'real estate development',
                    
                    # KEY WORDS that indicate CRE
                    'commercial', 'industrial', 'retail', 'office',
                    'multifamily', 'mixed-use', 'hospitality'
                ],
                'exclude_departments': [
                    # Definitely not targets
                    'residential', 'personal banking', 'consumer',
                    'hr', 'human resources', 'marketing', 'it', 
                    'legal', 'compliance', 'operations', 'administration',
                    'audit', 'accounting', 'tax', 'insurance',
                    'wealth management', 'private banking'
                ],
                'high_value_companies': [
                    # Company names/types that indicate CRE
                    'cbre', 'jll', 'cushman', 'colliers', 'newmark',
                    'marcus & millichap', 'eastdil', 'hff',
                    'berkadia', 'walker & dunlop',
                    'realty', 'properties', 'capital', 'partners',
                    'advisors', 'brokerage', 'commercial'
                ],
                'title_scores': {
                    # CRE-specific title scoring
                    # Principals/Owners (decision makers)
                    'principal': 85,
                    'owner': 85,
                    'partner': 85,
                    'managing director': 90,
                    'managing partner': 90,
                    
                    # Senior brokers/bankers
                    'senior vice president': 90,
                    'svp': 90,
                    'executive vice president': 88,
                    'evp': 88,
                    'first vice president': 87,
                    'vice president': 85,
                    'vp': 85,
                    
                    # Mid-level (very active in deals)
                    'director': 80,
                    'senior director': 82,
                    'senior associate': 75,
                    'associate director': 78,
                    
                    # Active brokers/originators
                    'broker': 70,
                    'senior broker': 75,
                    'investment sales': 75,
                    'leasing broker': 70,
                    'loan officer': 70,
                    'mortgage banker': 72,
                    
                    # Junior but still valuable
                    'associate': 60,
                    'analyst': 50,
                    'coordinator': 40
                }
            }
        }
    
    def calculate_personalized_rss(self, contact: Dict) -> Dict:
        """Score CRE professionals"""
        title = (contact.get('title') or '').lower()
        company = (contact.get('company') or '').lower()
        
        print(f"\n=== CRE SCORING: {contact.get('name', 'Unknown')} ===")
        print(f"Title: '{title}'")
        print(f"Company: '{company}'")
        
        profile = self._get_vertical_profiles()['CRE_MORTGAGE']
        
        # CHECK 1: Excluded departments (immediate disqualification)
        for exclude_dept in profile['exclude_departments']:
            if exclude_dept in title:
                print(f"  ❌ EXCLUDED: '{exclude_dept}' - Score: 10")
                return self._create_score_result(10, f'Excluded: {exclude_dept}', None, None)
        
        # CHECK 2: High-value company match (automatic qualification)
        company_match = False
        for hv_company in profile['high_value_companies']:
            if hv_company in company:
                company_match = True
                print(f"  ⭐ HIGH-VALUE COMPANY: '{hv_company}'")
                break
        
        # CHECK 3: Target department/vertical match
        vertical_match = False
        matched_vertical = None
        
        # Look for CRE indicators in title
        cre_indicators = [
            'commercial', 'cre', 'broker', 'leasing', 'investment',
            'capital markets', 'debt', 'mortgage', 'real estate',
            'tenant rep', 'landlord rep', 'multifamily', 'office', 'retail'
        ]
        
        for indicator in cre_indicators:
            if indicator in title:
                vertical_match = True
                matched_vertical = indicator
                print(f"  ✅ CRE INDICATOR: '{indicator}'")
                break
        
        # If no title match but company match, partial credit
        if not vertical_match and company_match:
            vertical_match = True
            matched_vertical = 'cre_company'
            print(f"  ✅ CRE company employee")
        
        # No CRE connection = low score
        if not vertical_match:
            print(f"  ❌ NOT IN CRE - Score: 20")
            return self._create_score_result(20, 'Not in CRE', None, None)
        
        # CHECK 4: Title level scoring (for CRE professionals)
        base_score = 50  # Base for being in CRE
        title_score = base_score
        matched_title = None
        
        # Check specific titles
        for title_pattern, score_value in profile['title_scores'].items():
            if title_pattern in title:
                title_score = score_value
                matched_title = title_pattern
                print(f"  ✅ TITLE: '{title_pattern}' = {score_value}")
                break
        
        # Boost for high-value company + good title
        if company_match and title_score >= 70:
            title_score = min(100, title_score + 10)
            print(f"  🎯 PREMIUM COMBO: +10 bonus")
        
        # Special handling for ambiguous "manager" titles
        if 'manager' in title and not matched_title:
            if any(word in title for word in ['portfolio', 'property', 'asset', 'relationship']):
                title_score = 65
                matched_title = 'manager (cre)'
            else:
                title_score = 45
                matched_title = 'manager (generic)'
        
        print(f"  FINAL SCORE: {title_score}")
        
        return self._create_score_result(
            title_score, 
            'CRE Professional',
            matched_vertical,
            matched_title
        )
    
    def _create_score_result(self, score: float, reason: str, 
                            vertical: Optional[str], title: Optional[str]) -> Dict:
        """Create standardized score result"""
        return {
            'total': round(min(100, max(0, score)), 2),
            'breakdown': {
                'score': score,
                'reason': reason,
                'matched_vertical': vertical,
                'matched_title': title
            },
            'preferences_applied': True,
            'user_id': self.user_id
        }
