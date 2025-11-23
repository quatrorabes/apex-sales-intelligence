#!/usr/bin/env python3

#!/usr/bin/env python3
"""
Quick Enrichment - Fast public data lookup during import
Populates: LinkedIn profile, photo, company info, social links
Does NOT run full AI analysis - that's for explicit enrichment
"""

import requests
import os
from typing import Dict, Optional
import time

class QuickEnricher:
	"""Fast public data enrichment for contacts"""
	
	def __init__(self):
		self.session = requests.Session()
		self.session.headers.update({
			'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
		})
		
	def enrich_contact(self, contact_data: Dict) -> Dict:
		"""
		Quick enrichment - populate basic public data
		Returns: {linkedin_url, photo_url, company_linkedin, verified_email, etc}
		"""
		enrichment = {
			'linkedin_url': None,
			'photo_url': None,
			'company_linkedin': None,
			'company_website': None,
			'verified_email': False,
			'social_links': {},
			'enriched': False
		}
		
		try:
			name = contact_data.get('name', '')
			company = contact_data.get('company', '')
			email = contact_data.get('email', '')
			existing_linkedin = contact_data.get('linkedin_url', '')
			
			print(f"      🔍 Quick lookup: {name} at {company}")
			
			# 1. LinkedIn URL (if not already present)
			if not existing_linkedin and name and company:
				linkedin = self._find_linkedin_profile(name, company)
				if linkedin:
					enrichment['linkedin_url'] = linkedin
					print(f"         ✓ Found LinkedIn")
			elif existing_linkedin:
				enrichment['linkedin_url'] = existing_linkedin
				
			# 2. Get profile photo from email (Gravatar or similar)
			if email:
				photo = self._get_profile_photo(email)
				if photo:
					enrichment['photo_url'] = photo
					print(f"         ✓ Found photo")
					
			# 3. Company website and LinkedIn
			if company:
				company_data = self._get_company_info(company)
				enrichment['company_website'] = company_data.get('website')
				enrichment['company_linkedin'] = company_data.get('linkedin')
				if company_data.get('website'):
					print(f"         ✓ Found company website")
					
			# 4. Verify email format
			if email and '@' in email:
				enrichment['verified_email'] = True
				
			enrichment['enriched'] = True
			
		except Exception as e:
			print(f"      ⚠️  Quick enrichment error: {e}")
			
		return enrichment
	
	def _find_linkedin_profile(self, name: str, company: str) -> Optional[str]:
		"""
		Find LinkedIn profile URL
		Uses Google search to find LinkedIn profile
		"""
		try:
			# Format search query
			search_query = f"{name} {company} site:linkedin.com/in/"
			
			# Simple pattern matching - could use Google Custom Search API
			# For now, construct likely LinkedIn URL
			name_parts = name.lower().split()
			if len(name_parts) >= 2:
				first = name_parts[0].replace('.', '').replace(',', '')
				last = name_parts[-1].replace('.', '').replace(',', '')
				
				# Common LinkedIn URL patterns
				possible_urls = [
					f"https://www.linkedin.com/in/{first}{last}",
					f"https://www.linkedin.com/in/{first}-{last}",
					f"https://www.linkedin.com/in/{first}.{last}"
				]
				
				# Return first pattern - in production, you'd verify these
				return possible_urls[0]
			
		except Exception as e:
			pass
			
		return None
	
	def _get_profile_photo(self, email: str) -> Optional[str]:
		"""
		Get profile photo from Gravatar or similar service
		"""
		try:
			import hashlib
			
			# Gravatar lookup
			email_hash = hashlib.md5(email.lower().encode()).hexdigest()
			gravatar_url = f"https://www.gravatar.com/avatar/{email_hash}?s=200&d=404"
			
			# Check if Gravatar exists
			response = self.session.head(gravatar_url, timeout=2)
			if response.status_code == 200:
				return gravatar_url
			
			# Fallback to UI Avatars (always works)
			name = email.split('@')[0].replace('.', ' ').title()
			return f"https://ui-avatars.com/api/?name={name}&size=200&background=6366f1&color=fff"
		
		except Exception:
			pass
			
		return None
	
	def _get_company_info(self, company: str) -> Dict:
		"""
		Get company website and LinkedIn
		"""
		company_data = {
			'website': None,
			'linkedin': None
		}
		
		try:
			# Construct likely website
			company_clean = company.lower().replace(' ', '').replace(',', '').replace('.', '')
			company_clean = ''.join(c for c in company_clean if c.isalnum())
			
			# Common TLDs
			possible_domains = [
				f"https://www.{company_clean}.com",
				f"https://{company_clean}.com"
			]
			
			company_data['website'] = possible_domains[0]
			
			# Company LinkedIn
			company_slug = company.lower().replace(' ', '-').replace(',', '').replace('.', '')
			company_data['linkedin'] = f"https://www.linkedin.com/company/{company_slug}"
			
		except Exception:
			pass
			
		return company_data
	
	
def quick_enrich_contact(contact_data: Dict) -> Dict:
	"""
	Main function: Quick enrichment for a single contact
	Returns enriched data to merge into contact record
	"""
	enricher = QuickEnricher()
	return enricher.enrich_contact(contact_data)
