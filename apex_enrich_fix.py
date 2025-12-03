#!/usr/bin/env python3

# FILE: apex_enrich_fix.py
# PURPOSE: Diagnose and fix OpenAI enrichment pipeline
# RUN: python apex_enrich_fix.py <contact_id>

import os
import sqlite3
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def diagnose_contact(contact_id):
		"""Stage-by-stage diagnostic"""
		conn = sqlite3.connect('./apex.db')
		conn.row_factory = sqlite3.Row
		cursor = conn.cursor()
	
		# 1. Fetch contact
		contact = cursor.execute(
				"SELECT * FROM contacts WHERE id = ?", (contact_id,)
		).fetchone()
	
		if not contact:
				print(f"❌ Contact {contact_id} not found")
				return
	
		print(f"✅ STAGE 0: Contact loaded - {contact['name']} ({contact['email']})")
	
		# 2. Check Stage1 data (profile_content or enrichment_data)
		if contact['profile_content']:
				print(f"✅ STAGE 1: Raw profile exists ({len(contact['profile_content'])} chars)")
				stage1_data = contact['profile_content']
		elif contact['enrichment_data']:
				print(f"✅ STAGE 1: Enrichment data exists ({len(contact['enrichment_data'])} chars)")
				stage1_data = contact['enrichment_data']
		else:
				print("⚠️  STAGE 1: No enrichment data - run enhanced_enrichment.py first")
				stage1_data = f"""
				Contact: {contact['name']}
				Company: {contact['company']}
				Title: {contact['job_title']}
				LinkedIn: {contact['linkedin_url']}
				Email: {contact['email']}
				"""
			
		# 3. Build GPT-4 prompt (Stage2)
		prompt = f"""
You are a B2B sales intelligence analyst. Analyze this contact and produce a comprehensive JSON profile.

CONTACT DATA:
{stage1_data}

OUTPUT REQUIREMENTS (strict JSON):
{{
	"overview": "2-3 sentence executive summary",
	"background": "Professional background and career trajectory",
	"personality_detail": "Communication style and decision-making approach",
	"pain_points": "Top 3 business challenges (bullet list)",
	"talking_points": "5 conversation starters for sales outreach",
	"fun_facts": "2-3 personal interests or unique facts",
	"company_overview": "Company description and market position",
	"company_products_services": "Main offerings",
	"sales_talking_points": "How our solution addresses their needs"
}}

Respond with ONLY valid JSON. No markdown, no code blocks.
"""

		print(f"\n📤 STAGE 2: Sending to GPT-4 ({len(prompt)} chars)...")
		
		try:
				# 4. Call OpenAI
				response = client.chat.completions.create(
						model="gpt-4o",
						messages=[
								{"role": "system", "content": "You are a sales intelligence analyst. Always respond with valid JSON only."},
								{"role": "user", "content": prompt}
						],
						temperature=0.7,
						max_tokens=2000
				)
			
				raw_response = response.choices[0].message.content
				print(f"✅ STAGE 2: GPT-4 response received ({len(raw_response)} chars)")
			
				# 5. Parse JSON (Stage3)
				# Strip markdown if present
				cleaned = raw_response.strip()
				if cleaned.startswith("```
						cleaned = cleaned.split("```json").split("```
				elif cleaned.startswith("```"):
						cleaned = cleaned.split("``````")[0].strip()
							
				enrichment = json.loads(cleaned)
				print("✅ STAGE 3: JSON parsed successfully")
							
				# 6. Update database
				update_fields = {
						'overview': enrichment.get('overview', ''),
						'background': enrichment.get('background', ''),
						'personality_detail': enrichment.get('personality_detail', ''),
						'pain_points': enrichment.get('pain_points', ''),
						'talking_points': enrichment.get('talking_points', ''),
						'fun_facts': enrichment.get('fun_facts', ''),
						'company_overview': enrichment.get('company_overview', ''),
						'company_products_services': enrichment.get('company_products_services', ''),
						'sales_talking_points': enrichment.get('sales_talking_points', ''),
						'enrichment_status': 'completed',
						'last_enriched': 'datetime("now")'
				}
							
				set_clause = ', '.join([f"{k} = ?" for k in update_fields.keys() if k != 'last_enriched'])
				set_clause += ', last_enriched = datetime("now")'
				values = [v for k, v in update_fields.items() if k != 'last_enriched']
							
				cursor.execute(
						f"UPDATE contacts SET {set_clause} WHERE id = ?",
						values + [contact_id]
				)
				conn.commit()
							
				print(f"✅ STAGE 4: Database updated - {cursor.rowcount} row(s)")
				print("\n🎉 SUCCESS - Full pipeline completed!")
							
				# Show sample
				print("\n📊 SAMPLE OUTPUT:")
				print(f"Overview: {enrichment.get('overview', '')[:200]}...")
				print(f"Pain Points: {enrichment.get('pain_points', '')[:150]}...")
							
		except json.JSONDecodeError as e:
				print(f"❌ STAGE 3 FAILED: JSON parsing error")
				print(f"Error: {e}")
				print(f"\nRaw response:\n{raw_response[:500]}...")
							
		except Exception as e:
				print(f"❌ STAGE 2/3 FAILED: {type(e).__name__}")
				print(f"Error: {e}")
							
		finally:
				conn.close()
							
if __name__ == "__main__":
		import sys
		if len(sys.argv) < 2:
				print("Usage: python apex_enrich_fix.py <contact_id>")
				print("\nExample: python apex_enrich_fix.py 1")
				sys.exit(1)
							
		contact_id = int(sys.argv[1])
		diagnose_contact(contact_id)
							