#!/usr/bin/env python3

#!/usr/bin/env python3
"""
Advanced CRE Content Generator with Deep Context
"""
import os
import sqlite3
import asyncio
import json
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

# CRE-SPECIFIC INTELLIGENCE
CRE_CONTEXT = {
	"company": "Harvest Small Business Finance",
	"seller": "Chris Rabenold",
	"value_props": {
		"primary": "SBA 504 loans for owner-occupied commercial real estate - up to 90% financing",
		"secondary": "Help businesses build wealth through real estate ownership vs leasing",
		"tertiary": "Lower down payments (10%) compared to conventional loans (20-30%)"
	},
	"triggers": [
		"Currently leasing and paying rent (money down the drain)",
		"Growing company needing more space",
		"Lease renewal coming up",
		"Looking to control occupancy costs",
		"Want to build equity instead of enriching landlord"
	],
	"case_studies": {
		"tech": "Helped a 50-person SaaS company buy their building with just 10% down, saving $40K/month vs leasing",
		"manufacturing": "Financed a 30,000 sq ft facility purchase, client now owns a $5M asset",
		"professional": "Law firm bought their office building, fixed costs for 20 years"
	}
}

async def generate_intelligent_cre_content(contact, profile):
	client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
	
	# Extract key data
	name = contact['name'].split()[0]
	company = contact['company']
	title = contact['title']
	
	# Parse enrichment for insights
	insights = analyze_company_for_cre(profile)
	
	prompt = f"""
	You are {CRE_CONTEXT['seller']} from {CRE_CONTEXT['company']}.
	
	RECIPIENT: {name}, {title} at {company}
	
	CRITICAL INTEL FROM RESEARCH:
	- Company size/growth: {insights.get('size_growth')}
	- Current location: {insights.get('location')}
	- Funding/financial health: {insights.get('funding')}
	- Recent news: {insights.get('recent_news')}
	
	YOUR MISSION: Write a SPECIFIC, COMPELLING email about:
	{CRE_CONTEXT['value_props']['primary']}
	
	ANGLE TO USE (pick most relevant):
	1. If they're growing → "Your growth trajectory suggests you'll outgrow your space. Let's talk about OWNING instead of leasing your next facility."
	2. If they raised funding → "Congrats on the funding! Smart companies use SBA 504 to buy their building with just 10% down, preserving capital."
	3. If established company → "You're likely tired of rent increases. We can help you fix your occupancy costs forever by owning."
	
	SPECIFIC HOOKS TO INCLUDE:
	- Mention a SPECIFIC detail about their company from the research
	- Include ONE relevant case study number
	- Create urgency with rates/market conditions
	- Keep under 125 words
	- End with specific CTA: "Can we discuss your real estate strategy next Tuesday or Thursday?"
	
	DO NOT:
	- Be generic
	- Talk about their products/services except as context
	- Use buzzwords
	- Sound like every other cold email
	
	The email should feel like it was written by someone who actually researched them.
	"""
	
	response = await client.chat.completions.create(
		model="gpt-4o",  # Use better model for quality
		messages=[
			{"role": "system", "content": "You are a commercial real estate finance expert writing highly personalized outreach."},
			{"role": "user", "content": prompt}
		],
		temperature=0.7  # More creative but not wild
	)
	
	return response.choices[0].message.content

def analyze_company_for_cre(profile_text):
	"""Extract CRE-relevant insights from profile"""
	insights = {}
	
	# Look for growth indicators
	if "funding" in profile_text.lower() or "series" in profile_text.lower():
		insights['funding'] = "Recently raised funding"
		
	if "employee" in profile_text.lower() or "team" in profile_text.lower():
		# Try to extract employee count
		insights['size_growth'] = "Growing team"
		
	# Location info
	if "headquarter" in profile_text.lower() or "office" in profile_text.lower():
		insights['location'] = "Has established presence"
		
	# Recent developments
	if "expand" in profile_text.lower():
		insights['recent_news'] = "Expansion mentioned"
		
	return insights

async def generate_complete_sequence(contact_id):
	"""Generate full outreach sequence with rich context"""
	conn = sqlite3.connect(os.path.expanduser("~/projects/apex/apex.db"))
	conn.row_factory = sqlite3.Row
	cursor = conn.cursor()
	
	cursor.execute("SELECT * FROM contacts WHERE id = ?", (contact_id,))
	contact = dict(cursor.fetchone())
	
	# Get enrichment data
	data = json.loads(contact['enrichment_data'])
	profile = data.get('perplexity_insights', '')
	
	print(f"\n🎯 Generating INTELLIGENT CRE content for {contact['name']}...\n")
	
	# Generate email
	email = await generate_intelligent_cre_content(contact, profile)
	
	print("📧 PERSONALIZED CRE EMAIL:\n")
	print("="*60)
	print(email)
	print("="*60)
	
	# Also generate a call script
	call_prompt = f"""
	Create a 30-second call script for {contact['name']} at {contact['company']}.
	
	Key points:
	- I'm Chris from Harvest Small Business Finance
	- We do SBA 504 loans - help companies buy their buildings with 10% down
	- Reference something specific about their company: {profile[:200]}
	- Ask: "Are you currently leasing or do you own your facility?"
	- If leasing: "Let's talk about building equity instead of paying rent"
	
	Keep it conversational, not scripted.
	"""
	
	client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
	call_response = await client.chat.completions.create(
		model="gpt-4o-mini",
		messages=[
			{"role": "system", "content": "You write natural phone scripts."},
			{"role": "user", "content": call_prompt}
		]
	)
	
	print("\n📞 CALL SCRIPT:\n")
	print("="*60)
	print(call_response.choices[0].message.content)
	print("="*60)
	
	# Save to database
	cursor.execute("""
		UPDATE contacts 
		SET email_1_body = ?,
			call_script_1 = ?,
			content_generated_at = CURRENT_TIMESTAMP
		WHERE id = ?
	""", (email, call_response.choices[0].message.content, contact_id))
	
	conn.commit()
	conn.close()
	
	return email

if __name__ == "__main__":
	# Generate for Andy with MUCH better context
	asyncio.run(generate_complete_sequence(48))
	