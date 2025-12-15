#!/usr/bin/env python3

#!/usr/bin/env python3
"""
CRE-Specific Content Generator
"""
import os
import sys
import sqlite3
import asyncio
import json
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

# Your company context
COMPANY_CONTEXT = """
You are writing outreach for a commercial real estate company.
We help companies optimize their office space, reduce costs, and plan expansions.
We are NOT selling tech/AI services - we sell REAL ESTATE services.
Focus on their OFFICE SPACE needs, not their tech products.
"""

async def generate_cre_email(contact, profile):
	client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
	
	name = contact['name'].split()[0]  # First name
	company = contact['company']
	title = contact['title']
	
	prompt = f"""
	{COMPANY_CONTEXT}
	
	Write a cold email to {name}, {title} at {company}.
	
	Company info: {profile[:500]}
	
	Focus on:
	- Their potential office space needs
	- Growth requiring more space
	- Cost optimization opportunities
	- NOT their products/services
	
	Keep it under 150 words. Be specific about CRE value.
	"""
	
	response = await client.chat.completions.create(
		model="gpt-4o-mini",
		messages=[
			{"role": "system", "content": "You write B2B sales emails for commercial real estate."},
			{"role": "user", "content": prompt}
		]
	)
	
	return response.choices[0].message.content

# Test with Andy
async def test_andy():
	conn = sqlite3.connect(os.path.expanduser("~/projects/apex/apex.db"))
	conn.row_factory = sqlite3.Row
	cursor = conn.cursor()
	
	cursor.execute("SELECT * FROM contacts WHERE id = 48")
	contact = dict(cursor.fetchone())
	
	data = json.loads(contact['enrichment_data'])
	profile = data.get('perplexity_insights', '')[:1000]
	
	print("Generating CRE-focused email for Andy...\n")
	email = await generate_cre_email(contact, profile)
	print("📧 CRE EMAIL:\n")
	print(email)
	
	conn.close()
	
if __name__ == "__main__":
	asyncio.run(test_andy())
	