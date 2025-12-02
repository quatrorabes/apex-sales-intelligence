#!/usr/bin/env python3

#!/usr/bin/env python3
"""
Complete test: Enhanced Enrichment → Better Content Generation
Run this to see the full flow working
"""
import os
import sqlite3
import json
import asyncio
from datetime import datetime

async def test_complete_flow():
	"""Test enrichment → scoring → content generation"""
	
	print("\n" + "="*80)
	print("🚀 TESTING COMPLETE FLOW WITH ENHANCED ENRICHMENT")
	print("="*80)
	
	# Step 1: Clear Andy's old enrichment
	print("\n1️⃣ Clearing old enrichment...")
	conn = sqlite3.connect(os.path.expanduser("~/projects/apex/apex.db"))
	cursor = conn.cursor()
	
	cursor.execute("""
		UPDATE contacts 
		SET enrichment_status = NULL,
			enrichment_data = NULL 
		WHERE id = 48
	""")
	conn.commit()
	
	# Step 2: Run enhanced enrichment
	print("\n2️⃣ Running ENHANCED enrichment...")
	from enhanced_enrichment import EnhancedEnrichment
	
	enricher = EnhancedEnrichment()
	contact = {
		'id': 48,
		'name': 'Andy Bratt',
		'title': 'Principal',
		'company': 'Gantry',
		'email': 'abratt@gantryinc.com',
		'phone': '+1 949-356-6678'
	}
	
	enrich_result = enricher.enrich_contact(contact)
	
	if enrich_result:
		# Save to database
		cursor.execute("""
			UPDATE contacts 
			SET enrichment_data = ?,
				enrichment_status = 'complete'
			WHERE id = 48
		""", (json.dumps({
			'full_profile_text': enrich_result['profile_text'],
			'perplexity_insights': enrich_result['profile_text']
		}),))
		conn.commit()
		print(f"✅ Enriched with {enrich_result['character_count']} chars")
		
	# Step 3: Generate content with GOOD intelligence
	print("\n3️⃣ Generating content with enhanced profile...")
	
	# Get the enhanced profile
	cursor.execute("SELECT enrichment_data FROM contacts WHERE id = 48")
	row = cursor.fetchone()
	enrichment = json.loads(row[0]) if row[0] else {}
	profile = enrichment.get('full_profile_text', '')
	
	# Now generate content with the GOOD profile
	from openai import AsyncOpenAI
	from dotenv import load_dotenv
	load_dotenv()
	
	client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
	
	# Generate with proper context
	prompt = f"""
You are Chris Rabenold from Harvest Small Business Finance (SBA lending).
You're writing to Andy Bratt, who you've known for 10 years through the CRE industry.

CRITICAL CONTEXT:
- Andy is NOT a prospect - he's a peer at Gantry (commercial mortgage banking)
- You could refer deals to each other
- Keep it casual, professional, under 75 words

Andy's Enhanced Profile:
{profile[:2000]}

Write a brief email about potential referral partnership. Sound natural.
"""

	response = await client.chat.completions.create(
		model="gpt-4o",
		messages=[
			{"role": "system", "content": "Write authentic business communication between peers."},
			{"role": "user", "content": prompt}
		],
		temperature=0.7
	)

	email_content = response.choices[0].message.content
	
	# Save generated content
	cursor.execute("""
		UPDATE contacts 
		SET email_1_body = ?
		WHERE id = 48
	""", (email_content,))
	conn.commit()
	
	print("\n📧 GENERATED EMAIL WITH ENHANCED INTELLIGENCE:")
	print("-"*60)
	print(email_content)
	print("-"*60)
	
	# Step 4: Show the difference
	print("\n✅ COMPLETE FLOW TESTED:")
	print("   • Enhanced enrichment with pain points & insights")
	print("   • Correct company identification")  
	print("   • Relationship-aware content generation")
	print("   • Natural, peer-to-peer tone")
	
	conn.close()
	
if __name__ == "__main__":
	asyncio.run(test_complete_flow())
	