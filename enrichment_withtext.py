#!/usr/bin/env python3

#!/usr/bin/env python3
"""
Full Output Perplexity Enrichment
Saves complete profile to file and displays everything
"""
import os
import requests
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class FullOutputEnrichment:
	"""Get and save COMPLETE Perplexity output"""
	
	def __init__(self, api_key=None):
		self.api_key = api_key or os.getenv('PERPLEXITY_API_KEY')
		if not self.api_key:
			raise ValueError("PERPLEXITY_API_KEY required")
			
		# Create output directory
		self.output_dir = "enrichment_profiles"
		os.makedirs(self.output_dir, exist_ok=True)
		
	def enrich_contact(self, contact):
		"""Enrich and save EVERYTHING"""
		
		name = contact.get('name', '')
		company = contact.get('company', '')
		contact_id = contact.get('id', 'unknown')
		
		print(f"\n{'='*80}")
		print(f"🔍 ENRICHING: {name} at {company}")
		print(f"{'='*80}\n")
		
		# Build query like you do manually
		query = self.build_query(contact)
		
		print("📤 SENDING TO PERPLEXITY:")
		print("-" * 40)
		print(query)
		print("-" * 40)
		
		# Call Perplexity
		result = self.call_perplexity(query)
		
		if result:
			# Generate filename with timestamp
			timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
			filename = f"{self.output_dir}/profile_{contact_id}_{name.replace(' ', '_')}_{timestamp}.txt"
			
			# Save COMPLETE output to file
			with open(filename, 'w', encoding='utf-8') as f:
				f.write("=" * 80 + "\n")
				f.write(f"ENRICHMENT PROFILE\n")
				f.write(f"Generated: {datetime.now().isoformat()}\n")
				f.write("=" * 80 + "\n\n")
				
				f.write("CONTACT DETAILS:\n")
				f.write(f"Name: {contact.get('name')}\n")
				f.write(f"Title: {contact.get('title')}\n")
				f.write(f"Company: {contact.get('company')}\n")
				f.write(f"Email: {contact.get('email')}\n")
				f.write(f"Phone: {contact.get('phone')}\n")
				f.write("\n" + "=" * 80 + "\n\n")
				
				f.write("PERPLEXITY AI RESEARCH:\n")
				f.write("-" * 80 + "\n")
				f.write(result)
				f.write("\n" + "=" * 80 + "\n")
				
			print(f"\n✅ SAVED TO FILE: {filename}")
			print(f"📊 Profile size: {len(result):,} characters\n")
			
			# Display the ENTIRE output
			print("📄 COMPLETE PERPLEXITY OUTPUT:")
			print("=" * 80)
			print(result)
			print("=" * 80)
			
			# Also save a JSON version for database
			json_filename = filename.replace('.txt', '.json')
			with open(json_filename, 'w', encoding='utf-8') as f:
				json.dump({
					'contact': contact,
					'perplexity_output': result,
					'generated_at': datetime.now().isoformat(),
					'character_count': len(result),
					'filename': filename
				}, f, indent=2)
				
			print(f"\n✅ Also saved JSON: {json_filename}")
			
			# Check which Gantry we found
			self.verify_correct_company(result)
			
			return {
				'success': True,
				'profile_text': result,
				'filename': filename,
				'character_count': len(result)
			}
		else:
			print("\n❌ No result from Perplexity")
			return None
		
	def build_query(self, contact):
		"""Build query exactly like you do it manually"""
		
		name = contact.get('name', '')
		title = contact.get('title', '')
		company = contact.get('company', '')
		email = contact.get('email', '')
		phone = contact.get('phone', '')
		
		# Your exact query format
		query = f"""{name}, {title} at {company}
Email: {email}
Phone: {phone}

You are a professional profile-building assistant. Generate up-to-date profile using public web sources and LinkedIn.

For the person ({name}), structure the profile as:
1. Overview – Current title and organization
2. Background – Work history, notable achievements
3. Education – Degrees and institutions
4. Recent Mentions – Any news, public appearances, LinkedIn posts, or online presence
5. Find LinkedIn, Instagram, Facebook, and Twitter profiles
6. Personality Detail - perform a Myers Briggs assessment
7. Compose and interpret Myers-Briggs Personality assessment summary
8. Evaluate potential talking points regarding sales opportunities

For the company ({company}), structure the profile as:
1. Overview – Description, mission, founding details, and HQ
2. Products & Services – Key offerings and markets served
3. Leadership – Key executives and founders
4. Market & Competitors – Industry, position, key competitors
5. Recent News – Major announcements, deals, or product launches
6. Find any relevant company news or fun facts

IMPORTANT: Make sure to find the correct {company} where {name} works as {title}, not a different company with the same name."""
		
		return query
	
	def call_perplexity(self, query):
		"""Call Perplexity API"""
		
		url = "https://api.perplexity.ai/chat/completions"
		
		headers = {
			"Authorization": f"Bearer {self.api_key}",
			"Content-Type": "application/json"
		}
		
		payload = {
			"model": "sonar-pro",
			"messages": [
				{
					"role": "user",
					"content": query
				}
			]
		}
		
		try:
			print("\n⏳ Calling Perplexity API...")
			response = requests.post(url, json=payload, headers=headers)
			
			if response.status_code == 200:
				data = response.json()
				return data['choices'][0]['message']['content']
			else:
				print(f"❌ API Error {response.status_code}")
				print(f"Response: {response.text}")
				return None
			
		except Exception as e:
			print(f"❌ Request error: {e}")
			return None
		
	def verify_correct_company(self, profile_text):
		"""Check if we got the right company"""
		
		print("\n🔍 VERIFYING COMPANY IDENTIFICATION:")
		print("-" * 40)
		
		text_lower = profile_text.lower()
		
		indicators = {
			'Correct Gantry (CRE)': [
				'mortgage', 'commercial real estate', 'real estate finance',
				'lending', 'debt financing', 'ccim', 'billion in loans'
			],
			'Wrong Gantry (AI)': [
				'artificial intelligence', 'machine learning', 'josh tobin',
				'vicki cheung', 'ai infrastructure', 'mlops'
			]
		}
		
		correct_count = sum(1 for term in indicators['Correct Gantry (CRE)'] if term in text_lower)
		wrong_count = sum(1 for term in indicators['Wrong Gantry (AI)'] if term in text_lower)
		
		if correct_count > wrong_count:
			print("✅ CORRECT: Found Gantry mortgage banking firm!")
			print(f"   Evidence: {correct_count} CRE indicators found")
		elif wrong_count > correct_count:
			print("❌ WRONG: Found Gantry AI company instead!")
			print(f"   Evidence: {wrong_count} AI indicators found")
		else:
			print("🤔 UNCLEAR: Could not determine which Gantry")
			
		print("-" * 40)
		
def test_andy_full():
	"""Test with Andy and show EVERYTHING"""
	
	contact = {
		'id': 48,
		'name': 'Andy Bratt',
		'title': 'Principal',
		'company': 'Gantry',
		'email': 'abratt@gantryinc.com',
		'phone': '+1 949-356-6678'
	}
	
	enricher = FullOutputEnrichment()
	result = enricher.enrich_contact(contact)
	
	if result:
		print(f"\n{'='*80}")
		print("✅ ENRICHMENT COMPLETE!")
		print(f"{'='*80}")
		print(f"📁 Full profile saved to: {result['filename']}")
		print(f"📊 Total size: {result['character_count']:,} characters")
		
		# Open the file automatically (macOS)
		import subprocess
		try:
			subprocess.run(['open', result['filename']])
			print("📖 Opening file in default text editor...")
		except:
			print("💡 Open the file manually to see full output")
			
if __name__ == "__main__":
	test_andy_full()
	