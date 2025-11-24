"""
Vertical/Department Verification System
Verifies if someone is actually in CRE by checking multiple sources
"""
import json
import re
from typing import Dict, List, Tuple, Optional

class VerticalVerifier:
    """Verify professional vertical from multiple data sources"""
    
    def __init__(self):
        self.cre_signals = self._load_cre_signals()
    
    def _load_cre_signals(self) -> Dict:
        """Define signals that indicate CRE involvement"""
        return {
            'strong_signals': {
                # Definitive CRE indicators
                'title_keywords': [
                    'commercial real estate', 'cre broker', 'investment sales',
                    'commercial leasing', 'tenant representation', 'landlord representation',
                    'capital markets', 'debt placement', 'mortgage broker',
                    'commercial mortgage', 'commercial lending', 'cre finance'
                ],
                'company_keywords': [
                    'cbre', 'jll', 'cushman wakefield', 'colliers', 'newmark',
                    'marcus millichap', 'eastdil', 'berkadia', 'walker dunlop',
                    'commercial real estate', 'cre advisors', 'capital markets'
                ],
                'linkedin_keywords': [
                    'commercial real estate', 'investment sales', 'net lease',
                    'cap rate', 'noi', 'cmbs', 'bridge lending', 'acquisition',
                    'disposition', 'underwriting', 'argus', 'costar'
                ],
                'certifications': [
                    'ccim', 'sior', 'cpm', 'mba.org', 'uli', 'icsc',
                    'mortgage broker license', 'nmls'
                ]
            },
            'medium_signals': {
                # Probable CRE involvement
                'title_keywords': [
                    'real estate', 'property', 'asset management', 'portfolio',
                    'development', 'construction', 'facilities'
                ],
                'company_keywords': [
                    'properties', 'realty', 'development', 'capital',
                    'partners', 'advisors', 'commercial'
                ]
            },
            'negative_signals': {
                # Definitely NOT CRE
                'title_keywords': [
                    'residential', 'single family', 'homeowner', 'personal',
                    'hr', 'human resources', 'marketing', 'it support',
                    'legal counsel', 'compliance', 'audit', 'tax'
                ],
                'company_keywords': [
                    'residential', 'homes', 'apartments', 'homebuilders'
                ]
            }
        }
    
    def verify_from_enrichment(self, contact: Dict, enrichment_data: Dict) -> Dict:
        """
        Verify vertical from enriched data (LinkedIn, web search, etc.)
        """
        verification = {
            'is_cre': False,
            'confidence': 0,
            'vertical': None,
            'signals_found': [],
            'data_sources': []
        }
        
        # Extract data from different sources
        title = (contact.get('title') or '').lower()
        company = (contact.get('company') or '').lower()
        
        # Check enrichment data
        if enrichment_data:
            # LinkedIn data
            linkedin_data = enrichment_data.get('linkedin', {})
            if linkedin_data:
                verification['data_sources'].append('linkedin')
                
                # Check LinkedIn headline
                headline = (linkedin_data.get('headline') or '').lower()
                if headline:
                    cre_score = self._check_text_for_cre(headline)
                    if cre_score > 0:
                        verification['signals_found'].append(f'LinkedIn headline: {headline[:50]}')
                        verification['confidence'] += cre_score * 20
                
                # Check LinkedIn summary/about
                summary = (linkedin_data.get('summary') or '').lower()
                if summary:
                    cre_score = self._check_text_for_cre(summary)
                    if cre_score > 0:
                        verification['signals_found'].append('CRE keywords in LinkedIn summary')
                        verification['confidence'] += cre_score * 15
                
                # Check skills
                skills = linkedin_data.get('skills', [])
                cre_skills = [s for s in skills if self._is_cre_skill(s)]
                if cre_skills:
                    verification['signals_found'].append(f'CRE skills: {", ".join(cre_skills[:3])}')
                    verification['confidence'] += len(cre_skills) * 10
            
            # Company website data
            company_data = enrichment_data.get('company_profile', {})
            if company_data:
                verification['data_sources'].append('company_website')
                
                # Check company description
                company_desc = (company_data.get('description') or '').lower()
                if 'commercial real estate' in company_desc or 'cre' in company_desc:
                    verification['signals_found'].append('Company in CRE industry')
                    verification['confidence'] += 30
                
                # Check company specialties
                specialties = company_data.get('specialties', [])
                cre_specialties = [s for s in specialties if 'commercial' in s.lower() or 'cre' in s.lower()]
                if cre_specialties:
                    verification['signals_found'].append(f'Company specialties: {", ".join(cre_specialties[:2])}')
                    verification['confidence'] += 25
            
            # Perplexity/Web search data
            web_data = enrichment_data.get('web_search', {})
            if web_data:
                verification['data_sources'].append('web_search')
                
                # Check if person appears in CRE-related articles
                search_results = web_data.get('results', [])
                cre_mentions = 0
                for result in search_results:
                    if self._check_text_for_cre(result.get('snippet', '')) > 0:
                        cre_mentions += 1
                
                if cre_mentions > 0:
                    verification['signals_found'].append(f'Found in {cre_mentions} CRE-related web results')
                    verification['confidence'] += cre_mentions * 5
        
        # Basic verification from title/company
        title_score = self._check_text_for_cre(title)
        company_score = self._check_text_for_cre(company)
        
        if title_score > 0:
            verification['signals_found'].append(f'CRE title: {title[:50]}')
            verification['confidence'] += title_score * 25
        
        if company_score > 0:
            verification['signals_found'].append(f'CRE company: {company[:50]}')
            verification['confidence'] += company_score * 20
        
        # Determine vertical based on signals
        if verification['confidence'] >= 50:
            verification['is_cre'] = True
            verification['vertical'] = self._determine_specific_vertical(
                title, company, verification['signals_found']
            )
        
        # Cap confidence at 100
        verification['confidence'] = min(100, verification['confidence'])
        
        return verification
    
    def _check_text_for_cre(self, text: str) -> float:
        """Check if text contains CRE indicators (returns 0-1 score)"""
        if not text:
            return 0
        
        text = text.lower()
        signals = self.cre_signals
        
        # Check negative signals first
        for neg_signal in signals['negative_signals']['title_keywords']:
            if neg_signal in text:
                return -0.5  # Negative score for excluded departments
        
        # Check strong signals
        strong_count = sum(1 for s in signals['strong_signals']['title_keywords'] if s in text)
        if strong_count > 0:
            return 1.0
        
        # Check medium signals
        medium_count = sum(1 for s in signals['medium_signals']['title_keywords'] if s in text)
        if medium_count > 0:
            return 0.5
        
        return 0
    
    def _is_cre_skill(self, skill: str) -> bool:
        """Check if a skill indicates CRE expertise"""
        skill = skill.lower()
        cre_skills = [
            'commercial real estate', 'investment sales', 'lease negotiation',
            'argus', 'costar', 'crexi', 'loopnet', 'property valuation',
            'underwriting', 'acquisition', 'disposition', 'asset management',
            'capital markets', 'cmbs', 'debt placement', 'bridge lending'
        ]
        return any(cre_skill in skill for cre_skill in cre_skills)
    
    def _determine_specific_vertical(self, title: str, company: str, signals: List[str]) -> str:
        """Determine specific CRE vertical"""
        combined = f"{title} {company} {' '.join(signals)}".lower()
        
        if 'investment sales' in combined or 'investment broker' in combined:
            return 'cre_investment_sales'
        elif 'leasing' in combined or 'tenant rep' in combined:
            return 'cre_leasing'
        elif 'mortgage' in combined or 'lending' in combined:
            return 'cre_lending'
        elif 'development' in combined or 'developer' in combined:
            return 'cre_development'
        elif 'property management' in combined or 'asset management' in combined:
            return 'cre_management'
        else:
            return 'cre_general'
    
    def verify_batch(self, contacts: List[Dict]) -> List[Dict]:
        """Verify multiple contacts"""
        results = []
        for contact in contacts:
            # Get enrichment data if available
            enrichment = contact.get('enrichment_data', {})
            verification = self.verify_from_enrichment(contact, enrichment)
            
            results.append({
                'contact_id': contact['id'],
                'name': contact['name'],
                'verification': verification
            })
        
        return results
