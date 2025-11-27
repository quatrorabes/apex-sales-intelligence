#!/usr/bin/env python3

#!/usr/bin/env python3
"""
Enhanced Perplexity Enrichment Module
Save this as: ~/projects/apex/apps/backend/intelligence/engines/enrichment/enhanced_perplexity.py
"""
import os
import requests
import json
from datetime import datetime
from typing import Dict, Optional

class EnhancedPerplexityEnrichment:
	"""Enhanced enrichment with strategic intelligence questions"""
	
	def __init__(self, api_key: Optional[str] = None):
		self.api_key = api_key or os.getenv('PERPLEXITY_API_KEY')
		if not self.api_key:
			raise ValueError("PERPLEXITY_API_KEY required in environment")
			
		# Create output directory for full profiles
		self.output_dir = os.path.expanduser("~/projects/apex/enrichment_profiles")
		os.makedirs(self.output_dir, exist_ok=True)
		
	def enrich_contact(self, contact: Dict) -> Dict:
		"""Enhanced enrichment with pain points, SBA interest, and insights"""
		
		name = contact.get('name', '')
		company = contact.get('company', '')
		title = contact.get('title', '')
		email = contact.get('email', '')
		phone = contact.get('phone', '')
		contact_id = contact.get('id', 'unknown')
		
		print(f"🔍 Enhanced enrichment for {name} at {company}...")
		
		# Build the comprehensive query
		query = self._build_enhanced_query(contact)
		
		# Call Perplexity
		result = self._call_perplexity_api(query)
		
		if result:
			# Save full profile to file
			timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
			filename = f"{self.output_dir}/profile_{contact_id}_{name.replace(' ', '_')}_{timestamp}.txt"
			
			with open(filename, 'w', encoding='utf-8') as f:
				f.write(f"={'='*80}\n")
				f.write(f"ENHANCED ENRICHMENT PROFILE\n")
				f.write(f"Generated: {datetime.now().isoformat()}\n")
				f.write(f"Contact: {name} ({title}) at {company}\n")
				f.write(f"={'='*80}\n\n")
				f.write(result)
				
			print(f"✅ Saved profile: {filename} ({len(result)} chars)")
			
			# Return structured data for database
			return {
				'success': True,
				'enrichment_data': {
					'full_profile_text': result,
					'perplexity_insights': result,
					'enriched_at': datetime.now().isoformat(),
					'source': 'perplexity_enhanced',
					'model': 'sonar-pro',
					'profile_length': len(result),
					'profile_file': filename
				}
			}
		
		return {'success': False, 'error': 'Enrichment failed'}
	
	def _build_enhanced_query(self, contact: Dict) -> str:
		"""Build comprehensive query with strategic questions"""
		
		name = contact.get('name', '')
		title = contact.get('title', '')
		company = contact.get('company', '')
		email = contact.get('email', '')
		phone = contact.get('phone', '')
		
		query = f"""{name}, {title} at {company}
Email: {email}
Phone: {phone}

You are a professional profile-building assistant. Generate comprehensive profile using public web sources and LinkedIn.

PERSON PROFILE ({name}):
1. Overview – Current title and organization
2. Background – Work history, notable achievements
3. Education – Degrees and institutions
4. Recent Mentions – News, LinkedIn posts, online presence
5. Social profiles – LinkedIn, Instagram, Facebook, Twitter
6. Personality assessment – Myers-Briggs based on available information
7. Professional network – Industry associations, speaking engagements

COMPANY PROFILE ({company}):
1. Overview – Description, mission, founding, HQ location
2. Products & Services – Key offerings and markets
3. Leadership – Key executives and founders
4. Market & Competitors – Industry position, competitors
5. Recent News – Major announcements, deals, launches
6. Financial info – Revenue, funding if available

STRATEGIC INTELLIGENCE:

PAIN POINTS: Provide 5 specific pain points someone in {name}'s role ({title}) and seniority would likely experience. Consider industry challenges, role frustrations, and market conditions.

SBA INTEREST POINTS: Provide 5 points {name} might find valuable about SBA loans and owner-occupied commercial real estate:
- Benefits vs conventional financing
- Building equity vs paying rent
- 10% down vs 30% conventional
- Tax and cash flow advantages
- Long-term wealth building

KEY INSIGHTS: Provide 3 critical things to know about this person/company for business conversations:
- Non-obvious insights showing deep understanding
- Conversation starters
- Strategic business intelligence

IMPORTANT: Find the correct {company} where {name} works as {title}. If multiple companies share this name, identify by email domain or {name}'s actual role."""
		
		return query
	
	def _call_perplexity_api(self, query: str) -> Optional[str]:
		"""Call Perplexity API with sonar-pro model"""
		
		url = "https://api.perplexity.ai/chat/completions"
		
		headers = {
			"Authorization": f"Bearer {self.api_key}",
			"Content-Type": "application/json"
		}
		
		payload = {
			"model": "sonar-pro",  # Using correct model
			"messages": [
				{
					"role": "user",
					"content": query
				}
			]
		}
		
		try:
			response = requests.post(url, json=payload, headers=headers)
			
			if response.status_code == 200:
				data = response.json()
				return data['choices'][0]['message']['content']
			else:
				# Fallback to sonar if pro fails
				if response.status_code == 400:
					print("Trying fallback model...")
					payload["model"] = "sonar"
					response = requests.post(url, json=payload, headers=headers)
					if response.status_code == 200:
						return response.json()['choices'][0]['message']['content']
					
				print(f"API Error: {response.status_code} - {response.text}")
				return None
			
		except Exception as e:
			print(f"Request error: {e}")
			return None
		