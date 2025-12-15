#!/usr/bin/env python3

#!/usr/bin/env python3
"""
Contact Scorer - Initial scoring based on public data
Scores contacts 0-100 before expensive AI enrichment
"""

from typing import Dict

class ContactScorer:
	"""Score contacts based on title, company, lifecycle, and available data"""
	
	def __init__(self):
		# Title scoring weights
		self.title_scores = {
			'c-level': 30,      # CEO, CFO, CTO, COO, CIO, CMO
			'president': 30,
			'owner': 30,
			'founder': 28,
			'partner': 28,
			'evp': 25,          # Executive VP
			'svp': 22,          # Senior VP
			'vp': 18,           # Vice President
			'director': 15,
			'manager': 10,
			'coordinator': 5,
			'assistant': 3
		}
		
		# Lifecycle stage scoring
		self.lifecycle_scores = {
			'salesqualifiedlead': 25,
			'marketingqualifiedlead': 20,
			'lead': 15,
			'subscriber': 10,
			'other': 5
		}
		
		# Company size indicators (from domain or industry)
		self.company_indicators = {
			'bank': 15,
			'capital': 12,
			'investment': 12,
			'financial': 10,
			'enterprise': 10,
			'inc': 8,
			'llc': 5
		}
		
	def score_contact(self, contact_data: Dict) -> Dict:
		"""
		Calculate initial contact score (0-100)
		Returns: {
			'total_score': 85,
			'tier': 'HOT',
			'breakdown': {...},
			'priority': 'high'
		}
		"""
		score_breakdown = {
			'title_score': 0,
			'lifecycle_score': 0,
			'data_completeness_score': 0,
			'company_score': 0
		}
		
		# 1. Title Score (max 30 points)
		title = (contact_data.get('title') or '').lower()
		title_score = self._score_title(title)
		score_breakdown['title_score'] = title_score
		
		# 2. Lifecycle Score (max 25 points)
		lifecycle = (contact_data.get('lifecycle_stage') or '').lower()
		lifecycle_score = self.lifecycle_scores.get(lifecycle, 5)
		score_breakdown['lifecycle_score'] = lifecycle_score
		
		# 3. Data Completeness Score (max 25 points)
		completeness_score = self._score_completeness(contact_data)
		score_breakdown['data_completeness_score'] = completeness_score
		
		# 4. Company Score (max 20 points)
		company = (contact_data.get('company') or '').lower()
		company_score = self._score_company(company)
		score_breakdown['company_score'] = company_score
		
		# Calculate total
		total_score = sum(score_breakdown.values())
		
		# Determine tier
		tier = self._determine_tier(total_score)
		
		# Determine priority for enrichment
		priority = self._determine_priority(total_score, title_score)
		
		return {
			'total_score': total_score,
			'tier': tier,
			'priority': priority,
			'breakdown': score_breakdown,
			'recommendation': self._get_recommendation(tier, priority)
		}
	
	def _score_title(self, title: str) -> int:
		"""Score based on job title"""
		if not title:
			return 0
		
		# Check for C-level
		c_level_titles = ['ceo', 'cfo', 'cto', 'coo', 'cio', 'cmo', 'chief']
		if any(c in title for c in c_level_titles):
			return 30
		
		# Check other title patterns
		for keyword, score in self.title_scores.items():
			if keyword in title:
				return score
			
		return 5  # Default for any title
	
	def _score_completeness(self, contact: Dict) -> int:
		"""Score based on data completeness"""
		score = 0
		
		# Email (required, already validated)
		score += 5
		
		# Phone
		if contact.get('phone') or contact.get('mobile_phone'):
			score += 5
			
		# LinkedIn
		if contact.get('linkedin_url'):
			score += 5
			
		# Title
		if contact.get('title'):
			score += 5
			
		# Industry
		if contact.get('industry'):
			score += 5
			
		return score
	
	def _score_company(self, company: str) -> int:
		"""Score based on company name indicators"""
		if not company:
			return 0
		
		score = 5  # Base score for having a company
		
		# Check for industry indicators
		for keyword, points in self.company_indicators.items():
			if keyword in company:
				score += points
				break  # Only count highest match
			
		return min(score, 20)  # Cap at 20
	
	def _determine_tier(self, score: float) -> str:
		"""Determine lead tier from score"""
		if score >= 75:
			return 'HOT'
		elif score >= 60:
			return 'WARM'
		elif score >= 45:
			return 'QUALIFIED'
		else:
			return 'COLD'
		
	def _determine_priority(self, score: float, title_score: int) -> str:
		"""Determine enrichment priority"""
		# High priority: High score OR high title authority
		if score >= 70 or title_score >= 25:
			return 'high'
		elif score >= 55 or title_score >= 18:
			return 'medium'
		else:
			return 'low'
		
	def _get_recommendation(self, tier: str, priority: str) -> str:
		"""Get action recommendation"""
		if tier in ['HOT', 'WARM'] and priority == 'high':
			return 'Enrich immediately - High value target'
		elif tier == 'WARM' and priority == 'medium':
			return 'Enrich soon - Good potential'
		elif tier == 'QUALIFIED':
			return 'Review and enrich selectively'
		else:
			return 'Monitor - Enrich only if needed'
		
		
def score_contact(contact_data: Dict) -> Dict:
	"""Main scoring function"""
	scorer = ContactScorer()
	return scorer.score_contact(contact_data)
