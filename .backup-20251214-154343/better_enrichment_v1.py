#!/usr/bin/env python3

#!/usr/bin/env python3
"""
Simple Perplexity Enrichment - Let it do its thing
No forcing structure in the API call
"""
import os
import requests
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class SimplePerplexityEnrichment:
	"""Just ask Perplexity the right questions and let it work"""
	
	def __init__(self, api_key=None):
		self.api_key = api_key or os.getenv('PERPLEXITY_API_KEY')
		if not self.api_key:
			raise ValueError("PERPLEXITY_API_KEY required")
			
	def enrich_contact(self, contact):
		"""Simple enrichment - just ask good questions"""
		
		name = contact.get('name', '')
		company = contact.get('company', '')
		title = contact.get('title', '')
		email = contact.get('email', '')
		phone = contact.get('phone', '')
		
		print(f"🔍 Enriching {name}...")
		
		# Simple, natural query - let Perplexity figure it out
		query = f"""{name}, {title} at {company}
Email: {email}
Phone: {phone}

Find comprehensive profile including:
- Professional background and current role
- Work history and achievements
- Education and certifications
- Company information - what {company} actually does
- Recent news or activities
- LinkedIn profile information
- Industry associations or involvement
- Any relevant business intelligence

Make sure to find the right {company} that matches {name} as {title}."""
		
		# Call Perplexity with simple format
		result = self.call_perplexity_simple(query)
		
		if result:
			# Save to file like your system does
			profile_file = f"profile_{contact.get('id', 'unknown')}.txt"
			with open(profile_file, 'w', encoding='utf-8') as f:
				f.write(result)
			print(f"✅ Saved {len(result)} chars to {profile_file}")
			
			return {
				'enrichment_data': {
					'full_profile_text': result,
					'perplexity_insights': result,
					'enriched_at': datetime.now().isoformat(),
					'source': 'perplexity_ai',
					'profile_length': len(result)
				}
			}
		
		return None
	
	def call_perplexity_simple(self, query):
		"""Simple API call - let Perplexity do its thing"""
		
		url = "https://api.perplexity.ai/chat/completions"
		
		headers = {
			"Authorization": f"Bearer {self.api_key}",
			"Content-Type": "application/json"
		}
		
		# SIMPLE payload - no complex instructions
		payload = {
			"model": "sonar-pro",
			"messages": [
				{
					"role": "user",
					"content": query  # Just the query, no forcing structure
				}
			]
		}
		
		try:
			response = requests.post(url, json=payload, headers=headers)
			
			if response.status_code == 200:
				data = response.json()
				return data['choices'][0]['message']['content']
			else:
				print(f"API Error {response.status_code}: {response.text}")
				return None
			
		except Exception as e:
			print(f"Request error: {e}")
			return None
		
# Even simpler - just like you do it manually
class ManualStyleEnrichment:
	"""Exactly how you do it manually in Perplexity"""
	
	def __init__(self, api_key=None):
		self.api_key = api_key or os.getenv('PERPLEXITY_API_KEY')
		
	def enrich_like_human(self, contact):
		"""Ask Perplexity like a human would"""
		
		# Exactly what you'd type into Perplexity chat
		human_query = f"""Andy Bratt, Gantry, Principal, abratt@gantryinc.com, 949-356-6678

Create a professional profile with:
1. Overview – Current title and organization
2. Background – Work history, notable achievements  
3. Education – Degrees and institutions
4. Recent Mentions – Any news, public appearances, LinkedIn posts
5. Social media profiles
6. Myers-Briggs personality assessment
7. Company overview for Gantry
8. Recent company news
9. Industry position and competitors
10. Potential talking points for sales

Use LinkedIn and web sources. Find the Gantry that Andy Bratt works at as Principal."""
		
		# Just send it
		url = "https://api.perplexity.ai/chat/completions"
		
		response = requests.post(
			url,
			headers={
				"Authorization": f"Bearer {self.api_key}",
				"Content-Type": "application/json"
			},
			json={
				"model": "sonar-pro",
				"messages": [{"role": "user", "content": human_query}]
			}
		)
		
		if response.status_code == 200:
			return response.json()['choices'][0]['message']['content']
		else:
			print(f"Error: {response.text}")
			return None
		
def test_simple():
	"""Test the simple approach"""
	
	contact = {
		'id': 48,
		'name': 'Andy Bratt',
		'title': 'Principal',
		'company': 'Gantry',
		'email': 'abratt@gantryinc.com',
		'phone': '+1 949-356-6678'
	}
	
	print("Testing SIMPLE approach (no structure forcing)...")
	print("=" * 60)
	
	# Method 1: Simple enrichment
	enricher = SimplePerplexityEnrichment()
	result = enricher.enrich_contact(contact)
	
	if result:
		profile = result['enrichment_data']['full_profile_text']
		print("\n✅ Got profile!")
		print("\nFirst 800 chars:")
		print(profile[:800])
		
		# Check which Gantry we got
		if 'mortgage' in profile.lower() or 'commercial real estate' in profile.lower():
			print("\n✅ Found CORRECT Gantry (mortgage)!")
		elif 'artificial intelligence' in profile.lower():
			print("\n❌ Found WRONG Gantry (AI)!")
			
	print("\n" + "=" * 60)
	
	# Method 2: Human-style
	print("\nTesting HUMAN-STYLE approach...")
	manual = ManualStyleEnrichment()
	result2 = manual.enrich_like_human(contact)
	
	if result2:
		print("\n✅ Got profile!")
		print("\nFirst 500 chars:")
		print(result2[:500])
		
if __name__ == "__main__":
	test_simple()
	