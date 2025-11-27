#!/usr/bin/env python3

# cold_outreach_scorer.py
class ColdOutreachScorer:
	"""Specialized scorer for minimal-info prospects"""
	
	def calculate_cold_score(self, contact: Dict, icp_profile: Dict) -> Dict:
		"""
		Score based on limited info:
		- Company match to target industries
		- Title keywords matching ICP
		- LinkedIn presence
		- Phone availability for cold calling
		"""
		score = 0
		confidence = 'low'
		
		# Company Industry Match (40 points)
		if contact.get('company'):
			company_lower = contact['company'].lower()
			if any(ind in company_lower for ind in icp_profile['target_industries']):
				score += 40
				confidence = 'medium'
				
		# Title Match (30 points)
		if contact.get('title'):
			title_lower = contact['title'].lower()
			if any(role in title_lower for role in icp_profile['ideal_roles']):
				score += 30
				confidence = 'medium'
				
		# Contact Method Availability (30 points)
		if contact.get('phone'):
			score += 15  # Can cold call
		if contact.get('linkedin_url'):
			score += 15  # Can social sell
			
		# Boost for exact ICP match
		if score >= 70 and confidence == 'medium':
			confidence = 'high'
			
		return {
			'cold_score': score,
			'confidence': confidence,
			'recommended_approach': self._get_approach(score, contact)
		}
	
	def _get_approach(self, score: int, contact: Dict) -> str:
		if score >= 70:
			return "🔥 HOT - Call immediately"
		elif score >= 50:
			return "🌡️ WARM - Research then call"
		elif score >= 30:
			return "❄️ COOL - LinkedIn first, then call"
		else:
			return "🧊 COLD - Needs more research"
		