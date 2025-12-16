#!/usr/bin/env python3

#!/usr/bin/env python3
"""
APEX SALES INTELLIGENCE - Content Generation Engine
Generates personalized outreach (emails, call scripts, LinkedIn) via OpenAI GPT-4o
PostgreSQL + Supabase production version
"""

import os
import logging
from datetime import datetime
from typing import Dict, Optional
import psycopg2
from psycopg2.extras import RealDictCursor
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

class ContentGenerator:
	"""
	Generates hyper-personalized outreach content using enriched intelligence
	- 3 Email Sequence (intro, value-add, breakup)
	- 3 Call Scripts (cold, follow-up, executive)
	- LinkedIn Connection Request + Follow-up
	"""
	
	def __init__(self):
		if not OPENAI_API_KEY:
			raise ValueError("OPENAI_API_KEY required in environment")
		if not DATABASE_URL:
			raise ValueError("DATABASE_URL required in environment")
			
		self.client = AsyncOpenAI(api_key=OPENAI_API_KEY)
		self.model = "gpt-4o"  # Latest model
		
	def _get_db_connection(self):
		"""Get PostgreSQL connection"""
		return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
	
	def _parse_name(self, full_name: str) -> tuple:
		"""Split full name into first/last"""
		parts = full_name.strip().split(maxsplit=1)
		firstname = parts[0] if parts else ""
		lastname = parts[1] if len(parts) > 1 else ""
		return firstname, lastname
	
	async def generate_email_sequence(self, contact: Dict, profile_sections: Dict) -> Dict:
		"""Generate 3-email outreach sequence"""
		
		firstname, lastname = self._parse_name(contact.get('name', ''))
		company = contact.get('company', 'your company')
		title = contact.get('title', 'your role')
		
		# Build intelligence summary from enrichment sections
		intelligence = []
		if profile_sections:
			if '1._overview' in profile_sections:
				intelligence.append(f"OVERVIEW:\n{profile_sections['1._overview'][:500]}")
			if 'person_profile' in profile_sections:
				intelligence.append(f"PROFILE:\n{profile_sections['person_profile'][:500]}")
			if '6._strategic_context' in profile_sections:
				intelligence.append(f"CONTEXT:\n{profile_sections['6._strategic_context'][:500]}")
				
		intel_text = "\n\n".join(intelligence[:3]) if intelligence else "Limited intelligence available"
		
		prompt = f"""
You are a world-class B2B sales copywriter. Generate a 3-email outreach sequence.

**TARGET CONTACT:**
Name: {firstname} {lastname}
Title: {title}
Company: {company}

**INTELLIGENCE PROFILE:**
{intel_text}

**REQUIREMENTS:**
1. Hyper-personalized using intelligence (reference specific details)
2. Professional but conversational tone
3. Short and scannable (150-200 words each)
4. Strong value propositions
5. Clear call-to-action
6. Reference their recent work, achievements, or company initiatives

**Generate exactly 3 emails:**

EMAIL 1: INTRODUCTION (Day 1)
- Hook with specific detail from their profile
- Establish credibility quickly
- One clear value proposition
- Soft ask for 15-min call

EMAIL 2: VALUE ADD (Day 4 - if no response)
- Share relevant insight or resource
- Reference industry challenge they face
- Reinforce value
- Another CTA

EMAIL 3: BREAKUP (Day 7 - if no response)
- Acknowledge they're busy
- Final value statement
- Leave door open
- Different CTA (resources, connection, etc.)

Format as:
---EMAIL 1---
Subject: [subject line]
[body]

---EMAIL 2---
Subject: [subject line]
[body]

---EMAIL 3---
Subject: [subject line]
[body]
"""

		response = await self.client.chat.completions.create(
			model=self.model,
			messages=[
				{"role": "system", "content": "You are an expert B2B sales copywriter who writes hyper-personalized, conversion-optimized emails."},
				{"role": "user", "content": prompt}
			],
			temperature=0.7,
			max_tokens=2000
		)

		content = response.choices[0].message.content
		emails = self._parse_emails(content)
		
		return emails
		
	async def generate_call_scripts(self, contact: Dict, profile_sections: Dict) -> Dict:
		"""Generate 3 call script variants"""
		
		firstname, lastname = self._parse_name(contact.get('name', ''))
		company = contact.get('company', 'the company')
		title = contact.get('title', 'their role')
		
		# Build intelligence for call context
		intelligence = []
		if profile_sections:
			if 'company_intelligence' in profile_sections:
				intelligence.append(profile_sections['company_intelligence'][:400])
			if 'skills_expertise' in profile_sections:
				intelligence.append(profile_sections['skills_expertise'][:300])
				
		intel_text = "\n".join(intelligence) if intelligence else "Limited intelligence"
		
		prompt = f"""
You are a world-class sales trainer. Generate 3 phone call scripts.

**TARGET CONTACT:**
Name: {firstname} {lastname}
Title: {title}
Company: {company}

**INTELLIGENCE PROFILE:**
{intel_text}

**Generate 3 scripts:**

SCRIPT 1: COLD CALL (First contact)
- Permission-based opening
- Reason for call (reference specific detail)
- Value hypothesis
- Ask for meeting
- Handle objections

SCRIPT 2: FOLLOW-UP CALL (After email/voicemail)
- Reference previous touchpoint
- New insight or value
- Discovery questions
- Next steps

SCRIPT 3: EXECUTIVE BRIEFING (If you get through)
- Executive summary opener
- 3 key discovery questions based on their role
- Value alignment
- Clear next steps

Format each script with:
- Opening
- Body/Value Prop
- Discovery Questions (3-5)
- Objection Handling
- Close/Next Steps

Make them conversational, not robotic!
"""

		response = await self.client.chat.completions.create(
			model=self.model,
			messages=[
				{"role": "system", "content": "You are an expert sales trainer who creates effective, natural call scripts."},
				{"role": "user", "content": prompt}
			],
			temperature=0.7,
			max_tokens=2500
		)

		content = response.choices[0].message.content
		
		# Parse scripts
		scripts = {
			'script_1': content.split('SCRIPT 2')[0] if 'SCRIPT 2' in content else content,
			'script_2': content.split('SCRIPT 2')[1].split('SCRIPT 3')[0] if 'SCRIPT 2' in content and 'SCRIPT 3' in content else '',
			'script_3': content.split('SCRIPT 3')[1] if 'SCRIPT 3' in content else ''
		}

		return scripts
		
	async def generate_linkedin_request(self, contact: Dict, profile_sections: Dict) -> Dict:
		"""Generate LinkedIn connection request + follow-up"""
		
		firstname, _ = self._parse_name(contact.get('name', ''))
		company = contact.get('company', 'your company')
		
		# Use social profiles or recent activity
		context = ""
		if profile_sections:
			if 'social_profiles' in profile_sections:
				context = profile_sections['social_profiles'][:300]
			elif '2._icebreaker_topics' in profile_sections:
				context = profile_sections['2._icebreaker_topics'][:300]
				
		prompt = f"""
Generate a LinkedIn connection request for:
Name: {firstname}
Company: {company}

**INTELLIGENCE:**
{context or 'Limited profile data'}

Create:
1. Connection note (300 chars max - LinkedIn limit)
2. Follow-up message (if they accept)

Be warm, professional, reference something specific from their profile.
No sales pitch in connection request!
"""

		response = await self.client.chat.completions.create(
			model=self.model,
			messages=[
				{"role": "system", "content": "You write engaging LinkedIn connection requests that get accepted."},
				{"role": "user", "content": prompt}
			],
			temperature=0.7,
			max_tokens=500
		)

		content = response.choices[0].message.content
		parts = content.split('Follow-up')
		
		return {
			'connection_note': parts[0].strip()[:300],  # LinkedIn limit
			'followup_message': parts[1].strip() if len(parts) > 1 else ''
		}

	async def generate_all_content(self, contact_id: str) -> Dict:
		"""Generate complete outreach package for a contact"""
		
		conn = self._get_db_connection()
		try:
			cursor = conn.cursor()
			
			# Fetch contact with enrichment
			cursor.execute("""
				SELECT id, name, email, company, title, phone, linkedin_url,
						enrichment, apex_score, rss_score
				FROM contacts
				WHERE id = %s
			""", (contact_id,))
			
			row = cursor.fetchone()
			if not row:
				return {'error': 'Contact not found', 'contact_id': contact_id}
			
			contact = dict(row)
			
			# Check if enriched
			enrichment = contact.get('enrichment') or {}
			sections = enrichment.get('sections', {})
			
			if not sections:
				return {
					'error': 'Contact not enriched - run enrichment first',
					'contact_id': contact_id,
					'name': contact.get('name')
				}
			
			logger.info(f"Generating content for: {contact.get('name')} at {contact.get('company')}")
			
			# Generate all content in parallel
			emails = await self.generate_email_sequence(contact, sections)
			scripts = await self.generate_call_scripts(contact, sections)
			linkedin = await self.generate_linkedin_request(contact, sections)
			
			# Save to database
			cursor.execute("""
				INSERT INTO outreach_content (
					contact_id,
					email_1_subject, email_1_body,
					email_2_subject, email_2_body,
					email_3_subject, email_3_body,
					call_script_1, call_script_2, call_script_3,
					linkedin_connection_note, linkedin_followup_message,
					generated_at
				) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
				ON CONFLICT (contact_id) 
				DO UPDATE SET
					email_1_subject = EXCLUDED.email_1_subject,
					email_1_body = EXCLUDED.email_1_body,
					email_2_subject = EXCLUDED.email_2_subject,
					email_2_body = EXCLUDED.email_2_body,
					email_3_subject = EXCLUDED.email_3_subject,
					email_3_body = EXCLUDED.email_3_body,
					call_script_1 = EXCLUDED.call_script_1,
					call_script_2 = EXCLUDED.call_script_2,
					call_script_3 = EXCLUDED.call_script_3,
					linkedin_connection_note = EXCLUDED.linkedin_connection_note,
					linkedin_followup_message = EXCLUDED.linkedin_followup_message,
					updated_at = NOW()
			""", (
				contact_id,
				emails.get('email_1', {}).get('subject', ''),
				emails.get('email_1', {}).get('body', ''),
				emails.get('email_2', {}).get('subject', ''),
				emails.get('email_2', {}).get('body', ''),
				emails.get('email_3', {}).get('subject', ''),
				emails.get('email_3', {}).get('body', ''),
				scripts['script_1'],
				scripts['script_2'],
				scripts['script_3'],
				linkedin['connection_note'],
				linkedin['followup_message'],
				datetime.now()
			))
			
			conn.commit()
			
			logger.info(f"✅ Content saved for contact {contact_id}")
			
			return {
				'success': True,
				'contact_id': contact_id,
				'name': contact.get('name'),
				'emails': emails,
				'scripts': scripts,
				'linkedin': linkedin,
				'generated_at': datetime.now().isoformat()
			}
		
		except Exception as e:
			logger.error(f"Error generating content: {str(e)}")
			conn.rollback()
			return {'error': str(e), 'contact_id': contact_id}
		finally:
			conn.close()
			
	def _parse_emails(self, content: str) -> Dict:
		"""Parse email content into structured format"""
		emails = {}
		parts = content.split('---EMAIL ')
		
		for i, part in enumerate(parts[1:], 1):  # Skip first empty part
			if f'{i}---' in part:
				email_content = part.split('---')[1].strip()
				lines = email_content.split('\n')
				subject = ''
				body = ''
				
				for line in lines:
					if line.startswith('Subject:'):
						subject = line.replace('Subject:', '').strip()
					else:
						body += line + '\n'
						
				emails[f'email_{i}'] = {
					'subject': subject,
					'body': body.strip()
				}
				
		return emails
