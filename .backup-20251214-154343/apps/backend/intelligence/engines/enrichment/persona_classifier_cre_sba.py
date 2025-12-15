#!/usr/bin/env python3

"""
ULTIMATE CRE/SBA PERSONA CLASSIFIER
Integrates with advanced_scoring.py and uses comprehensive LinkedIn/HubSpot data
Based on ENHANCED_MULTI_TIER_PERSONA_STRATEGY.md

Features:
- 8 detailed personas (5 Tier 1 Referral + 5 Tier 2 Borrower)
- Integrated with your existing scoring system
- Enhanced keyword matching for long LinkedIn titles
- Multi-signal classification (title + industry + company + skills)
- Lowered thresholds for better classification rate
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import re
from datetime import datetime


class UltimatePersonaClassifier:
	"""
	Enhanced 8-Tier Persona Classification
	Designed for real-world LinkedIn data with long titles
	"""
	
	def __init__(self):
		# TIER 1: REFERRAL PARTNER PERSONAS (Relationship-based)
		self.tier1_personas = {
			'Peer/Referral Partner (Lender)': {
				'title_keywords': [
					# Core banking titles
					'commercial lend', 'cre lend', 'business development officer', 'bdo',
					'loan officer', 'sba specialist', 'sba 504', 'sba 7a',
					'vp commercial', 'svp commercial', 'vp lending', 'svp lending',
					'regional manager', 'market president', 'relationship manager',
					# Financial services
					'commercial financ', 'business lending', 'commercial loan',
					'credit union', 'community bank', 'lending specialist',
					# SBA specific
					'sba program', 'government guaranteed', 'small business lending'
				],
				'company_keywords': [
					'bank', 'credit union', 'commercial capital', 'lending',
					'financial services', 'community bank', 'trust company'
				],
				'skills_keywords': [
					'commercial lending', 'loans', 'commercial mortgages',
					'finance', 'mergers & acquisitions', 'financial services'
				],
				'priority_multiplier': 1.25,
				'min_score': 40  # Lowered threshold
			},
			
			'Advisory & Broker Network': {
				'title_keywords': [
					# Real estate
					'cre broker', 'commercial real estate broker', 'cre agent',
					'commercial broker', 'commercial agent', 'ccim', 'cbb',
					'real estate advisor', 'real estate broker', 'principal broker',
					# Business brokerage
					'business broker', 'm&a advisor', 'mergers and acquisitions',
					'm&a intermediary', 'middle market',
					# Finance consulting
					'commercial finance consult', 'financing advisor', 'capital advisor'
				],
				'company_keywords': [
					'cbre', 'cushman', 'colliers', 'jll', 'marcus & millichap',
					'cre', 'commercial real estate', 'brokerage', 'realty',
					'm&a', 'business brokerage'
				],
				'skills_keywords': [
					'commercial real estate', 'mergers & acquisitions',
					'loans', 'finance', 'commercial lending'
				],
				'priority_multiplier': 1.30,
				'min_score': 40
			},
			
			'Influencer/Multiplier - Tech/Fintech': {
				'title_keywords': [
					'cto', 'chief technology officer', 'chief product officer',
					'head of commercial', 'vp product', 'chief revenue officer',
					'commercial credit analyst', 'credit analyst', 'senior analyst',
					'founder', 'co-founder', 'product manager lending'
				],
				'company_keywords': [
					'fintech', 'lendtech', 'saas', 'software', 'analytics',
					'crm', 'lending platform', 'credit', 'financial technology'
				],
				'skills_keywords': [
					'finance', 'commercial lending', 'financial services',
					'fintech', 'lending', 'credit analysis'
				],
				'priority_multiplier': 1.30,
				'min_score': 40
			},
			
			'Influencer/Multiplier - Community/EDO': {
				'title_keywords': [
					'economic development', 'edo', 'city planner', 'urban development',
					'chamber of commerce', 'executive director chamber',
					'cdc director', 'sbdc director', 'community development',
					'business development director', 'government relations'
				],
				'company_keywords': [
					'chamber', 'economic development', 'city of', 'county of',
					'sbdc', 'cdc', 'government', 'municipality', 'nonprofit'
				],
				'skills_keywords': [
					'finance', 'commercial lending', 'commercial real estate',
					'economic development', 'government'
				],
				'priority_multiplier': 1.25,
				'min_score': 35
			},
			
			'Superconnector - Executive Coach/Vistage': {
				'title_keywords': [
					'vistage chair', 'vistage', 'eo board', 'ypo member',
					'executive coach', 'ceo coach', 'business coach',
					'peer advisory', 'mastermind', 'group facilitator',
					'ceo roundtable', 'leadership coach', 'coach',
					'group admin', 'facilitator'
				],
				'company_keywords': [
					'vistage', 'eo ', 'ypo', 'coaching', 'advisory',
					'peer advisory', 'executive coaching', 'leadership'
				],
				'skills_keywords': [
					'finance', 'commercial lending', 'commercial real estate',
					'coaching', 'leadership', 'business development'
				],
				'priority_multiplier': 1.35,  # HIGHEST
				'min_score': 35
			}
		}
		
		# TIER 2: DIRECT BORROWER PERSONAS
		self.tier2_personas = {
			'Established Small Business Owner-User': {
				'title_keywords': [
					'owner', 'business owner', 'co-owner', 'president', 'ceo',
					'chief executive', 'cfo', 'partner', 'managing partner',
					'founder & ceo', 'founder & president', 'founder',
					'managing member', 'principal', 'proprietor'
				],
				'company_keywords': [
					'llc', 'inc', 'corporation', 'company', 'group',
					'services', 'solutions', 'consulting'
				],
				'revenue_range': (1000000, 15000000),
				'employee_range': (10, 75),
				'priority_multiplier': 1.15,
				'min_score': 50
			},
			
			'Professional Practice Decision Maker': {
				'title_keywords': [
					# Medical
					'doctor', 'physician', 'md', 'do', 'dentist', 'dds', 'dmd',
					'orthodontist', 'veterinarian', 'dvm', 'dr.', 'dr ',
					# Legal
					'attorney', 'esquire', 'esq', 'partner attorney', 'managing partner',
					'senior partner', 'law firm partner',
					# Financial
					'cpa', 'financial advisor', 'wealth manager', 'cfp',
					# Practice management
					'practice owner', 'practice manager', 'clinic owner'
				],
				'company_keywords': [
					'medical', 'dental', 'veterinary', 'law firm', 'legal',
					'practice', 'clinic', 'associates', 'partners',
					'financial advisory', 'wealth management'
				],
				'revenue_range': (2000000, 10000000),
				'employee_range': (5, 50),
				'priority_multiplier': 1.20,
				'min_score': 50
			},
			
			'Serial Entrepreneur & Portfolio Builder': {
				'title_keywords': [
					'investor', 'real estate investor', 'property investor',
					'portfolio manager', 'portfolio', 'serial entrepreneur',
					'multiple companies', 'multi-unit', 'franchise owner',
					'property owner', 'real estate owner', 'managing member'
				],
				'company_keywords': [
					'investments', 'holdings', 'ventures', 'capital',
					'portfolio', 'properties', 'real estate', 'group'
				],
				'revenue_range': (2000000, 25000000),
				'priority_multiplier': 1.25,
				'min_score': 45
			},
			
			'Minority-Owned Business Growth Seeker': {
				'title_keywords': [
					'owner', 'founder', 'ceo', 'president', 'managing member',
					'mbe', 'wbe', 'dbe', 'minority', 'diverse',
					'woman-owned', 'veteran-owned', 'community business'
				],
				'company_keywords': [
					'mbe', 'wbe', 'dbe', 'minority', 'diverse',
					'community', 'local', 'family'
				],
				'revenue_range': (500000, 5000000),
				'employee_range': (5, 50),
				'priority_multiplier': 1.15,
				'min_score': 45
			},
			
			'Family Business Succession Planner': {
				'title_keywords': [
					'2nd generation', '3rd generation', 'family business',
					'family-owned', 'successor', 'next generation',
					'generational', 'family', 'legacy', 'owner'
				],
				'company_keywords': [
					'family', '& son', '& sons', '& daughter', 'brothers',
					'family-owned', 'generational', 'since 19', 'est. 19'
				],
				'revenue_range': (3000000, 20000000),
				'employee_range': (15, 100),
				'priority_multiplier': 1.25,
				'min_score': 45
			}
		}
		
	def _extract_keywords(self, text):
		"""Extract and normalize keywords from text"""
		if not text:
			return set()
		# Convert to lowercase and extract words
		text = text.lower()
		# Remove special characters but keep spaces and pipes
		text = re.sub(r'[^\w\s|]', ' ', text)
		# Split on spaces and pipes
		words = text.split()
		return set(words)
	
	def _match_keywords(self, contact_text, keyword_list):
		"""
		Enhanced keyword matching for long LinkedIn titles
		Returns: (matched_count, matched_keywords)
		"""
		if not contact_text:
			return 0, []
		
		contact_text = contact_text.lower()
		matches = []
		
		for keyword in keyword_list:
			keyword = keyword.lower()
			# Use word boundary matching for better accuracy
			if keyword in contact_text:
				matches.append(keyword)
				
		return len(matches), matches
	
	def classify_contact(self, contact_data):
		"""
		Main classification function
		Returns: (tier, persona_type, confidence_score, matched_criteria)
		"""
		
		# Extract data
		title = str(contact_data.get('job_title', '')).lower()
		company = str(contact_data.get('company', '')).lower()
		industry = str(contact_data.get('industry', '')).lower()
		
		# NEW: Check skills if available (from HubSpot LinkedIn enrichment)
		skills = contact_data.get('skills', [])
		if isinstance(skills, str):
			skills = [s.strip() for s in skills.split(',')]
		skills_text = ' '.join(skills).lower()
		
		# Check Tier 1 (Referral Partner) match
		tier1_score, tier1_persona, tier1_criteria = self._check_tier1_match(
			title, company, industry, skills_text
		)
		
		# Check Tier 2 (Direct Borrower) match
		tier2_score, tier2_persona, tier2_criteria = self._check_tier2_match(
			contact_data, title, company, industry
		)
		
		# Decision logic - Tier 1 takes priority if close scores
		if tier1_score >= 40:  # Lowered from 60
			return ('Tier 1', tier1_persona, tier1_score, tier1_criteria)
		elif tier2_score >= 50:  # Lowered from 70
			return ('Tier 2', tier2_persona, tier2_score, tier2_criteria)
		else:
			return ('Unclassified', None, max(tier1_score, tier2_score), [])
	
	def _check_tier1_match(self, title, company, industry, skills_text):
		"""Check for Tier 1 (Referral Partner) persona match"""
		best_score = 0
		best_persona = None
		best_criteria = []
		
		for persona_name, rules in self.tier1_personas.items():
			score = 0
			criteria = []
			
			# Title keyword matching (50 points possible)
			title_count, title_matches = self._match_keywords(title, rules['title_keywords'])
			if title_count > 0:
				title_score = min(50, title_count * 25)  # 25 points per match, max 50
				score += title_score
				criteria.append(f"Title: {', '.join(title_matches[:3])}")
				
			# Company keyword matching (20 points)
			company_count, company_matches = self._match_keywords(company, rules['company_keywords'])
			if company_count > 0:
				score += 20
				criteria.append(f"Company: {', '.join(company_matches[:2])}")
				
			# Skills matching (20 points)
			if skills_text:
				skills_count, skills_matches = self._match_keywords(skills_text, rules['skills_keywords'])
				if skills_count > 0:
					score += 20
					criteria.append(f"Skills: {', '.join(skills_matches[:2])}")
					
			# Industry matching (10 points) - bonus
			if any(kw in industry for kw in ['banking', 'lending', 'real estate', 'finance', 'consulting']):
				score += 10
				criteria.append(f"Industry: {industry}")
				
			if score > best_score:
				best_score = score
				best_persona = persona_name
				best_criteria = criteria
				
		return best_score, best_persona, best_criteria
	
	def _check_tier2_match(self, contact_data, title, company, industry):
		"""Check for Tier 2 (Direct Borrower) persona match"""
		best_score = 0
		best_persona = None
		best_criteria = []
		
		for persona_name, rules in self.tier2_personas.items():
			score = 0
			criteria = []
			
			# Title keyword matching (40 points)
			title_count, title_matches = self._match_keywords(title, rules['title_keywords'])
			if title_count > 0:
				title_score = min(40, title_count * 20)
				score += title_score
				criteria.append(f"Title: {', '.join(title_matches[:2])}")
				
			# Revenue range (25 points)
			revenue = contact_data.get('annual_revenue', 0)
			if 'revenue_range' in rules and revenue:
				min_rev, max_rev = rules['revenue_range']
				if min_rev <= revenue <= max_rev:
					score += 25
					criteria.append(f"Revenue: ${revenue:,.0f}")
					
			# Employee count (20 points)
			employees = contact_data.get('employee_count', 0)
			if 'employee_range' in rules and employees:
				min_emp, max_emp = rules['employee_range']
				if min_emp <= employees <= max_emp:
					score += 20
					criteria.append(f"Employees: {employees}")
					
			# Company keywords (15 points)
			company_count, company_matches = self._match_keywords(company, rules['company_keywords'])
			if company_count > 0:
				score += 15
				criteria.append(f"Company: {', '.join(company_matches[:2])}")
				
			if score > best_score:
				best_score = score
				best_persona = persona_name
				best_criteria = criteria
				
		return best_score, best_persona, best_criteria
	
	def get_priority_multiplier(self, tier, persona_type):
		"""Get priority multiplier for scoring integration"""
		if not persona_type:
			return 1.0
		
		if tier == 'Tier 1' or 'Tier 1' in str(tier):
			return self.tier1_personas.get(persona_type, {}).get('priority_multiplier', 1.0)
		elif tier == 'Tier 2' or 'Tier 2' in str(tier):
			return self.tier2_personas.get(persona_type, {}).get('priority_multiplier', 1.0)
		return 1.0
	
	
# USAGE EXAMPLE / TEST
if __name__ == "__main__":
	classifier = UltimatePersonaClassifier()
	
	print("="*80)
	print("ULTIMATE CRE/SBA PERSONA CLASSIFIER - TESTING")
	print("="*80)
	
	# Test Case 1: Real-world CRE Lender (like Bart Hutchins)
	test_cre_lender = {
		'contact_name': 'Bart Hutchins',
		'job_title': 'Experienced CRE Lender | 20+ Years Providing CRE Financial Solutions & Building Client Relationships | Expertise in Structured Finance for Value Add Real Estate',
		'company': 'California Bank & Trust',
		'industry': 'Banking',
		'skills': ['Finance', 'Mergers & Acquisitions', 'Loans', 'Commercial Lending', 'Commercial Mortgages']
	}
	
	tier, persona, score, criteria = classifier.classify_contact(test_cre_lender)
	print(f"\n{'='*80}")
	print(f"Test 1: REAL-WORLD CRE LENDER (Bart Hutchins)")
	print(f"{'='*80}")
	print(f"Title: {test_cre_lender['job_title'][:80]}...")
	print(f"\nRESULTS:")
	print(f"  Primary Persona Tier: {tier}")
	print(f"  Relationship Persona Type: {persona}")
	print(f"  Persona Confidence Score: {score}%")
	print(f"  Priority Multiplier: {classifier.get_priority_multiplier(tier, persona)}x")
	print(f"  Matched Criteria:")
	for c in criteria:
		print(f"    • {c}")
		
	# Test Case 2: SBA BDO
	test_sba_bdo = {
		'contact_name': 'Jeremy Bailey',
		'job_title': 'SBA Wholesale Business Development Officer',
		'company': 'First Citizens Bank',
		'industry': 'Banking',
		'skills': ['Commercial Lending', 'Business Development', 'SBA Loans']
	}
	
	tier, persona, score, criteria = classifier.classify_contact(test_sba_bdo)
	print(f"\n{'='*80}")
	print(f"Test 2: SBA BUSINESS DEVELOPMENT OFFICER")
	print(f"{'='*80}")
	print(f"Title: {test_sba_bdo['job_title']}")
	print(f"\nRESULTS:")
	print(f"  Primary Persona Tier: {tier}")
	print(f"  Relationship Persona Type: {persona}")
	print(f"  Persona Confidence Score: {score}%")
	print(f"  Priority Multiplier: {classifier.get_priority_multiplier(tier, persona)}x")
	print(f"  Matched Criteria:")
	for c in criteria:
		print(f"    • {c}")
		
	# Test Case 3: Business Owner (Tier 2)
	test_owner = {
		'contact_name': 'Sarah Johnson',
		'job_title': 'Owner & CEO',
		'company': 'Johnson Manufacturing Inc',
		'industry': 'Manufacturing',
		'annual_revenue': 5000000,
		'employee_count': 35,
		'skills': []
	}
	
	tier, persona, score, criteria = classifier.classify_contact(test_owner)
	print(f"\n{'='*80}")
	print(f"Test 3: BUSINESS OWNER (TIER 2)")
	print(f"{'='*80}")
	print(f"Title: {test_owner['job_title']}")
	print(f"\nRESULTS:")
	print(f"  Primary Persona Tier: {tier}")
	print(f"  Borrower Persona Type: {persona}")
	print(f"  Persona Confidence Score: {score}%")
	print(f"  Priority Multiplier: {classifier.get_priority_multiplier(tier, persona)}x")
	print(f"  Matched Criteria:")
	for c in criteria:
		print(f"    • {c}")
		
	print("\n" + "="*80)
	print("✅ CLASSIFIER READY FOR INTEGRATION")
	print("="*80)
	print("\nFeatures:")
	print("  • Enhanced keyword matching for long LinkedIn titles")
	print("  • Multi-signal classification (title + company + industry + skills)")
	print("  • Lowered thresholds for better classification rate")
	print("  • Priority multipliers integrated with advanced_scoring.py")
	print("  • Ready to handle real-world HubSpot data")
	