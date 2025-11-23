# apps/backend/intelligence/lead_types.py
"""
Apex Intelligence - Lead Type Profiles
"""

from typing import Dict, Optional


class LeadTypeProfile:
    """Lead type definitions with MDCP scoring weights"""
    
    TYPES = {
        'BANKER': {
            'description': 'Conservative, compliance-focused, relationship-driven',
            'typical_role': 'Bank VP, Loan Officer, Credit Manager',
            'mdcp_weights': {'Money': 0.25, 'Decision': 0.20, 'Credibility': 0.35, 'Pain': 0.20}
        },
        'CDC': {
            'description': 'Volume-focused, SBA expertise, process-oriented',
            'typical_role': 'CDC Loan Officer, SBA Specialist',
            'mdcp_weights': {'Money': 0.25, 'Decision': 0.30, 'Credibility': 0.25, 'Pain': 0.20}
        },
        'BROKER': {
            'description': 'Deal-hungry, commission-driven, speed-focused',
            'typical_role': 'Commercial Mortgage Broker, Loan Broker',
            'mdcp_weights': {'Money': 0.30, 'Decision': 0.15, 'Credibility': 0.20, 'Pain': 0.35}
        },
        'PRIVATE_LENDER': {
            'description': 'Flexible, ROI-obsessed, creative deal structures',
            'typical_role': 'Private Equity, Family Office, Hard Money Lender',
            'mdcp_weights': {'Money': 0.20, 'Decision': 0.25, 'Credibility': 0.15, 'Pain': 0.40}
        },
        'BORROWER': {
            'description': 'Direct borrower seeking financing, no intermediary',
            'typical_role': 'Property Owner, Developer, Business Owner',
            'mdcp_weights': {'Money': 0.35, 'Decision': 0.30, 'Credibility': 0.20, 'Pain': 0.15}
        }
    }
    
    @staticmethod
    def get_profile(lead_type: str) -> Optional[Dict]:
        return LeadTypeProfile.TYPES.get(lead_type.upper())
    
    @staticmethod
    def get_all_types() -> list:
        return list(LeadTypeProfile.TYPES.keys())
    
    @staticmethod
    def get_mdcp_weights(lead_type: str) -> Dict[str, float]:
        profile = LeadTypeProfile.get_profile(lead_type)
        if profile:
            return profile['mdcp_weights']
        return LeadTypeProfile.TYPES['BORROWER']['mdcp_weights']


class LeadLifecycleStage:
    """Lead lifecycle stage definitions"""
    
    STAGES = {
        'NEW': {
            'description': 'Brand new lead, no history',
            'duration_days_range': (0, 30),
            'rss_approach': 'PREDICTIVE',
            'mdcp_approach': 'STATIC'
        },
        'COLD': {
            'description': 'No engagement after initial contact',
            'duration_days_range': (30, None),
            'rss_approach': 'MINIMAL',
            'mdcp_approach': 'STATIC'
        },
        'WARMING': {
            'description': 'Some engagement, building relationship',
            'duration_days_range': (30, 180),
            'rss_approach': 'EMERGING',
            'mdcp_approach': 'ADAPTIVE'
        },
        'ACTIVE': {
            'description': 'Regular engagement, deals in progress',
            'duration_days_range': (90, 365),
            'rss_approach': 'BUILDING',
            'mdcp_approach': 'DYNAMIC'
        },
        'ESTABLISHED': {
            'description': 'Proven track record, closed deals',
            'duration_days_range': (365, None),
            'rss_approach': 'FULL',
            'mdcp_approach': 'DYNAMIC'
        }
    }
    
    @staticmethod
    def get_stage_info(stage: str) -> Optional[Dict]:
        return LeadLifecycleStage.STAGES.get(stage.upper())
    
    @staticmethod
    def get_all_stages() -> list:
        return list(LeadLifecycleStage.STAGES.keys())
