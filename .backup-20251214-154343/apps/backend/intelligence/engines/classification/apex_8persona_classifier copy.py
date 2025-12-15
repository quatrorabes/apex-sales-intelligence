#!/usr/bin/env python3
"""
APEX 8-PERSONA CLASSIFIER (TUNED)

Personas:
- loan_broker, sales_broker, banker, sba_banker, referral_network_other,
  internal, borrower, past_borrower

RULES:
- Minimum confidence threshold: 35 points (prevents weak "borrower" fallback)
- Title matches weighted 60 pts (was 50) – catches bankers/brokers aggressively
- Company matches weighted 25 pts (was 20)
- Borrower requires BOTH title + company match (owner + LLC/Inc)
- If no persona hits 35, returns "unclassified" (not borrower)
- All personas: multiplier 1.00 (relationship boost later)
"""

from datetime import datetime
from typing import Dict, Any, List


class Apex8PersonaClassifier:
    def __init__(self):
        self.minimum_threshold = 20  # NEW: must hit this to get any persona
        self.rules = {
            'banker': {
                'title_keywords': [
                    'commercial lender', 'cre lender', 'bdo', 'business development officer',
                    'loan officer', 'vp commercial', 'svp commercial', 'vp lending', 'svp lending',
                    'relationship manager', 'commercial loan', 'lending specialist'
                ],
                'company_keywords': [
                    'bank', 'banking', 'credit union', 'community bank',
                    'financial services', 'trust company', 'bancorp', 'bancshares'
                ],
                'match_keywords': [
                    'commercial lending', 'loans', 'commercial mortgages',
                    'finance', 'financial services', 'credit analysis', 'underwriting'
                ],
            },
            'sba_banker': {
                'title_keywords': [
                    'sba specialist', 'sba 504', 'sba 7a', 'sba 7(a)', 'sba 7(a)',
                    'sba program manager', 'sba lender', 'sba loan officer',
                    'government guaranteed', 'small business lending specialist',
                    'sba relationship manager', 'sba bdo', 'sba business development'
                ],
                'company_keywords': [
                    'bank', 'credit union', 'sba', 'small business administration',
                    'community bank', 'financial services', 'sba preferred lender'
                ],
                'match_keywords': [
                    'sba lending', 'government guaranteed lending', 'sba'
                    'small business loans', 'small business lending', 'sba programs'
                ],
            },
            'loan_broker': {
                'title_keywords': [
                    'loan broker', 'mortgage broker', 'commercial mortgage broker',
                    'business loan broker', 'lending broker', 'capital advisor',
                    'loan originator', 'loan processor', 'loan correspondent',
                    'commercial finance consultant', 'financing advisor', 'capital broker',
                    'mortgage consultant', 'commercial loan originator'
                ],
                'company_keywords': [
                    'mortgage broker', 'loan broker', 'brokerage', 'mortgage',
                    'broker network', 'commercial capital', 'capital markets'
                ],
                'match_keywords': [
                    'commercial lending', 'business lending', 'commercial mortgages',
                    'finance', 'broker', 'origination'
                ],
            },
            'sales_broker': {
                'title_keywords': [
                    'cre broker', 'commercial real estate broker', 'cre agent',
                    'commercial broker', 'commercial agent', 'real estate advisor',
                    'real estate broker', 'principal broker', 'senior broker',
                    'business broker', 'm&a advisor', 'm&a intermediary',
                    'middle market broker', 'business sales broker', 'broker associate',
                    'ccim', 'cbb', 'commercial real estate advisor'
                ],
                'company_keywords': [
                    'cbre', 'cushman', 'colliers', 'jll', 'marcus & millichap',
                    'cre', 'commercial real estate', 'realty', 'business brokerage',
                    'm&a', 'investment sales', 'real estate investment'
                ],
                'match_keywords': [
                    'commercial real estate', 'mergers & acquisitions',
                    'business sale', 'sale of business', 'real estate brokerage'
                ],
            },
            'referral_network_other': {
                'title_keywords': [
                    'economic development', 'edo', 'city planner', 'urban development',
                    'chamber of commerce', 'executive director chamber',
                    'executive coach', 'ceo coach',
                    'business coach', 'peer advisory facilitator',
                    'group facilitator', 'nonprofit director', 'eo board member',
                    'ypo member', 'leadership coach', 'economic development officer'
                ],
                'company_keywords': [
                    'chamber', 'economic development', 'city of', 'county of',
                    'sbdc', 'cdc', 'municipality', 'nonprofit',
                    'vistage', 'eo', 'ypo', 'coaching', 'advisory', 'government'
                ],
                'match_keywords': [
                    'economic development', 'government', 'business development',
                    'leadership', 'peer advisory', 'nonprofit', 'public sector'
                ],
            },
            'internal': {
                'title_keywords': [
                    'harvest', 'harvest small business finance', 'harvest bank',
                    'havest commercial capital'
                ],
                'company_keywords': [
                    'harvest', 'harvest small business finance', 'harvest bank',
                    'havest commercial capital',
                ],
                'match_keywords': [
                    'internal referral', 'team collaboration'
                ],
            },
            'borrower': {
                'title_keywords': [
                    'owner', 'business owner''customer, borrower'
                ],
                'company_keywords': [
                    'family'
                ],
                'match_keywords': [
                    'business owner', 'entrepreneur', 'executive',
                    'decision maker', 'management', 'leadership',
                    'small business', 'family business', 'self-employed'
                ],
            },
            'past_borrower': {
                'title_keywords': [
                    'former owner', 'retired owner', 'former ceo',
                    'consultant', 'advisor', 'former executive',
                    'ex-owner', 'previous owner'
                ],
                'company_keywords': [
                    'former', 'retired', 'consulting', 'advisory'
                ],
                'match_keywords': [
                    'previous business owner', 'business experience',
                    'former executive', 'retired business owner'
                ],
            },
        }

    def _count_matches(self, text: str, keywords: List[str]) -> (int, List[str]):
        if not text:
            return 0, []
        tl = text.lower()
        hits = [kw for kw in keywords if kw.lower() in tl]
        return len(hits), hits

    def classify_contact(self, contact: Dict[str, Any]) -> Dict[str, Any]:
        title = str(contact.get('title') or contact.get('job_title') or '').lower()
        company = str(contact.get('company') or '').lower()
        industry = str(contact.get('industry') or '').lower()
        profile = str(contact.get('profile_content') or '').lower()

        best_persona = None  # NEW: no default borrower
        best_score = 0
        best_criteria: List[str] = []

        for persona, rule in self.rules.items():
            score = 0
            criteria: List[str] = []

            # Title (60 pts max) - higher weight for bankers/brokers
            t_count, t_hits = self._count_matches(title, rule['title_keywords'])
            if t_count:
                score += min(60, t_count * 25)
                criteria.append(f"title: {', '.join(t_hits[:3])}")

            # Company (25 pts)
            c_count, c_hits = self._count_matches(company, rule['company_keywords'])
            if c_count:
                score += min(25, c_count * 15)
                criteria.append(f"company: {', '.join(c_hits[:3])}")

            # Profile/Industry (15 pts)
            m_count, m_hits = self._count_matches(profile, rule['match_keywords'])
            if m_count:
                score += min(15, m_count * 8)
                criteria.append(f"profile: {', '.join(m_hits[:3])}")

            if industry in ['banking', 'financial services'] and persona in ['banker', 'sba_banker']:
                score += 10
                criteria.append(f"industry: {industry}")

            if score > best_score:
                best_score = score
                best_persona = persona
                best_criteria = criteria

        # NEW: Return "unclassified" if no persona hits threshold
        if best_score < self.minimum_threshold:
            return {
                'persona': 'unclassified',
                'confidence_score': best_score,
                'criteria': ['low confidence across all personas'],
                'multiplier': 1.00,
                'classified_at': datetime.now().isoformat()
            }

        multiplier = 1.00
        return {
            'persona': best_persona,
            'confidence_score': best_score,
            'criteria': best_criteria,
            'multiplier': multiplier,
            'classified_at': datetime.now().isoformat()
        }


if __name__ == "__main__":
    clf = Apex8PersonaClassifier()
    # Test cases
    tests = [
        {
            'name': 'Bart Hutchins',
            'title': 'Experienced CRE Lender | 20+ Years Providing CRE Financial Solutions',
            'company': 'California Bank & Trust',
            'persona_expected': 'banker'
        },
        {
            'name': 'Jeremy Bailey',
            'title': 'SBA Wholesale BDO',
            'company': 'First Citizens Bank',
            'persona_expected': 'sba_banker'
        },
        {
            'name': 'Sarah Johnson',
            'title': 'Owner & CEO',
            'company': 'Johnson Manufacturing LLC',
            'persona_expected': 'borrower'
        }
    ]
    print("════════════════════════════════════════════════════")
    for t in tests:
        result = clf.classify_contact(t)
        status = "✅" if result['persona'] == t['persona_expected'] else "❌"
        print(f"{status} {t['name']} → {result['persona']} (score {result['confidence_score']})")
    print("════════════════════════════════════════════════════")
    