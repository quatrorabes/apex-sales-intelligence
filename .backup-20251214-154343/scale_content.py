#!/usr/bin/env python3

#!/usr/bin/env python3
"""
Scalable Relationship-Aware Content Generation System
Maintains authenticity while handling volume
"""
import os
import sqlite3
import json
from openai import OpenAI
from dotenv import load_dotenv
from enum import Enum
from datetime import datetime
import random

load_dotenv()

class RelationshipLevel(Enum):
	COLD = "never met"
	WARM = "met once or twice"
	FAMILIAR = "see at events, recognize each other"
	CONNECTED = "regular industry contact, mutual respect"
	CLOSE = "actual friends, text regularly"
	
class ContactContext:
	"""Store relationship context efficiently"""
	
	def __init__(self, contact_id):
		self.contact_id = contact_id
		self.load_contact_data()
		self.load_relationship_data()
		
	def load_contact_data(self):
		"""Pull from database"""
		conn = sqlite3.connect(os.path.expanduser("~/projects/apex/apex.db"))
		conn.row_factory = sqlite3.Row
		cursor = conn.cursor()
		
		cursor.execute("SELECT * FROM contacts WHERE id = ?", (self.contact_id,))
		self.contact = dict(cursor.fetchone())
		
		# Parse enrichment for key facts
		if self.contact['enrichment_data']:
			data = json.loads(self.contact['enrichment_data'])
			self.intel = self.extract_key_intel(data)
			
		conn.close()
		
	def load_relationship_data(self):
		"""Get relationship context - this could be from CRM or database"""
		# For now, use defaults - later pull from CRM
		self.relationship = {
			"level": RelationshipLevel.FAMILIAR,
			"years_known": 0,  # 0 if unknown
			"last_interaction": None,
			"common_ground": [],
			"referral_potential": "unknown",
			"notes": ""
		}
		
		# Override for known contacts
		if "Andy Bratt" in self.contact['name']:
			self.relationship = {
				"level": RelationshipLevel.CONNECTED,
				"years_known": 10,
				"last_interaction": "NAIOP event 2 months ago",
				"common_ground": ["NAIOP", "CRE finance", "Newport Beach market"],
				"referral_potential": "high - complementary services",
				"notes": "Does big loans, we do SBA - natural partners"
			}
			
	def extract_key_intel(self, enrichment_data):
		"""Pull out only the most relevant facts"""
		intel = {
			"recent_news": [],
			"company_status": "",
			"pain_points": [],
			"opportunities": []
		}
		
		profile = enrichment_data.get('perplexity_insights', '')[:500]
		
		# Quick extraction logic
		if 'funding' in profile.lower():
			intel['recent_news'].append('recent funding')
		if 'growing' in profile.lower() or 'hiring' in profile.lower():
			intel['company_status'] = 'growth mode'
		if 'lease' in profile.lower():
			intel['pain_points'].append('currently leasing')
			
		return intel
	
class AuthenticContentGenerator:
	"""Generate content based on relationship depth"""
	
	def __init__(self):
		self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
		
	def generate(self, context: ContactContext, channel="email", angle=None):
		"""Generate content with appropriate tone for relationship"""
		
		# Select angle based on relationship
		if not angle:
			angle = self.select_angle(context)
			
		# Build prompt based on relationship level
		prompt = self.build_prompt(context, channel, angle)
		
		response = self.client.chat.completions.create(
			model="gpt-4o-mini",  # Cheaper for scale
			messages=[
				{"role": "system", "content": self.get_system_prompt(context)},
				{"role": "user", "content": prompt}
			],
			temperature=0.7
		)
		
		return response.choices[0].message.content
	
	def select_angle(self, context):
		"""Smart angle selection based on context"""
		if context.relationship['level'] == RelationshipLevel.COLD:
			return "introduction with specific value prop"
		elif context.relationship['level'] == RelationshipLevel.CONNECTED:
			angles = [
				"market observation worth discussing",
				"potential referral opportunity",
				"recent deal congrats",
				"upcoming event touchpoint"
			]
			return random.choice(angles)
		else:
			return "reconnect with business reason"
		
	def get_system_prompt(self, context):
		"""Adjust tone based on relationship"""
		if context.relationship['level'] in [RelationshipLevel.CONNECTED, RelationshipLevel.CLOSE]:
			return "Write like texting a business friend. No corporate speak. Casual but professional."
		elif context.relationship['level'] == RelationshipLevel.FAMILIAR:
			return "Write friendly but professional. You know each other but aren't close."
		else:
			return "Write a warm but professional introduction. Be specific about value."
		
	def build_prompt(self, context, channel, angle):
		"""Create the full prompt"""
		name = context.contact['name'].split()[0]
		company = context.contact['company']
		
		# Base context
		prompt = f"""
Write a {channel} to {name} at {company}.

RELATIONSHIP: {context.relationship['level'].value}
"""

		# Add relationship details if we have them
		if context.relationship['years_known'] > 0:
			prompt += f"\nKnown for: {context.relationship['years_known']} years"
			
		if context.relationship['last_interaction']:
			prompt += f"\nLast saw: {context.relationship['last_interaction']}"
			
		if context.relationship['common_ground']:
			prompt += f"\nCommon ground: {', '.join(context.relationship['common_ground'])}"
			
		# Add the angle
		prompt += f"\n\nANGLE: {angle}"
		
		# Add intelligence if relevant
		if context.intel.get('recent_news'):
			prompt += f"\nRecent news to reference (subtly): {context.intel['recent_news'][0]}"
			
		# Channel-specific instructions
		if channel == "text":
			prompt += "\n\nKeep under 40 words. Very casual."
		elif channel == "email":
			prompt += "\n\nKeep under 75 words. No subject line needed."
		elif channel == "linkedin":
			prompt += "\n\nKeep under 60 words. Professional but not stiff."
			
		prompt += "\n\nSound authentic. No fake enthusiasm. Write like you're busy but this matters."
		
		return prompt
		
# BATCH PROCESSING FUNCTION
def generate_batch_content(contact_ids, channel="email"):
	"""Generate for multiple contacts efficiently"""
	generator = AuthenticContentGenerator()
	results = {}
	
	for contact_id in contact_ids:
		try:
			context = ContactContext(contact_id)
			content = generator.generate(context, channel)
			
			# Save to database
			save_generated_content(contact_id, channel, content)
			
			results[contact_id] = {
				"name": context.contact['name'],
				"content": content,
				"relationship": context.relationship['level'].value
			}
			
			print(f"✓ Generated for {context.contact['name']} ({context.relationship['level'].value})")
			
		except Exception as e:
			print(f"✗ Failed for contact {contact_id}: {e}")
			results[contact_id] = {"error": str(e)}
			
	return results

def save_generated_content(contact_id, channel, content):
	"""Save to database"""
	conn = sqlite3.connect(os.path.expanduser("~/projects/apex/apex.db"))
	cursor = conn.cursor()
	
	# Map channel to column
	column_map = {
		"email": "email_1_body",
		"text": "sms_message",
		"linkedin": "linkedin_request"
	}
	
	if channel in column_map:
		cursor.execute(f"""
			UPDATE contacts 
			SET {column_map[channel]} = ?,
				content_generated_at = ?
			WHERE id = ?
		""", (content, datetime.now().isoformat(), contact_id))
		
		conn.commit()
		
	conn.close()
	
# TEST THE SYSTEM
if __name__ == "__main__":
	print("\n🚀 SCALABLE AUTHENTIC CONTENT GENERATION TEST\n")
	print("="*60)
	
	# Test single contact with known relationship (Andy)
	print("\n1️⃣ TESTING ANDY (Known relationship):")
	print("-"*40)
	context = ContactContext(48)  # Andy
	generator = AuthenticContentGenerator()
	
	email = generator.generate(context, "email")
	print(f"Email:\n{email}")
	
	# Test batch generation
	print("\n2️⃣ TESTING BATCH GENERATION:")
	print("-"*40)
	
	# Get 5 random contacts
	conn = sqlite3.connect(os.path.expanduser("~/projects/apex/apex.db"))
	cursor = conn.cursor()
	cursor.execute("SELECT id FROM contacts WHERE enrichment_status = 'complete' LIMIT 5")
	contact_ids = [row[0] for row in cursor.fetchall()]
	conn.close()
	
	if contact_ids:
		results = generate_batch_content(contact_ids, "email")
		
		print(f"\n✅ Generated content for {len(results)} contacts")
		
		# Show samples
		for cid, result in list(results.items())[:2]:
			if 'content' in result:
				print(f"\n📧 {result['name']} ({result['relationship']}):")
				print(result['content'][:150] + "...")
				
	print("\n" + "="*60)
	print("✨ System ready for scale!")
	