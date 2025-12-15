#!/usr/bin/env python3

#!/usr/bin/env python3
"""
DEBUG VERSION - Shows exactly what we send to OpenAI
"""
import os
import sqlite3
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class DebugGenerator:
	"""Shows exactly what we're sending to OpenAI"""
	
	def __init__(self):
		self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
		
	def show_what_we_send(self, contact_id=48):
		"""Show the exact prompt being sent"""
		
		# Get contact data
		conn = sqlite3.connect(os.path.expanduser("~/projects/apex/apex.db"))
		conn.row_factory = sqlite3.Row
		cursor = conn.cursor()
		
		cursor.execute("SELECT * FROM contacts WHERE id = ?", (contact_id,))
		contact = dict(cursor.fetchone())
		
		# Get enrichment
		enrichment = ""
		if contact['enrichment_data']:
			data = json.loads(contact['enrichment_data'])
			enrichment = data.get('perplexity_insights', '')[:2000]  # First 2000 chars
			
		conn.close()
		
		# Build the EXACT prompts we're sending
		
		print("="*80)
		print("🔍 WHAT WE'RE SENDING TO OPENAI - VERSION 1 (BAD)")
		print("="*80)
		
		bad_system_prompt = "You are writing as Chris Rabenold, an experienced SBA lender with 20+ years in commercial real estate finance."
		
		bad_user_prompt = f"""
MY COMPLETE PROFILE (Chris Rabenold):
Senior Vice President at Harvest Small Business Finance
20+ years in SBA lending
Does SBA 504 and 7(a) loans

CONTACT'S COMPLETE PROFILE:
Name: {contact['name']}
Title: {contact['title']}
Company: {contact['company']}

INTELLIGENCE:
{enrichment[:500]}

TASK:
Write a cold outreach email explaining how SBA financing can help them.
"""

		print("\n📝 SYSTEM PROMPT:")
		print("-"*40)
		print(bad_system_prompt)
		
		print("\n📝 USER PROMPT:")
		print("-"*40)
		print(bad_user_prompt)
		
		print("\n❌ PROBLEM: No context about the RELATIONSHIP or Andy's actual role!")
		
		print("\n" + "="*80)
		print("🔍 WHAT WE SHOULD SEND - VERSION 2 (GOOD)")
		print("="*80)
		
		good_system_prompt = "Write authentic business communication between industry peers who have known each other for years. No templates or corporate speak."
		
		good_user_prompt = f"""
CRITICAL CONTEXT - READ THIS FIRST:

{contact['name']} is NOT a prospect. He is a peer/competitor in the same industry.

RELATIONSHIP FACTS:
- Chris (sender) does SBA loans at Harvest ($500k-$5M deals)
- {contact['name']} does large commercial loans at {contact['company']} ($1M-$200M deals)
- Known each other 10 years
- See each other at NAIOP/ULI events
- Could refer deals to each other (complementary, not competitive)

{contact['name']}'s ACTUAL ROLE:
{contact['title']} at {contact['company']}
{enrichment[:500]}

DO NOT:
- Try to sell him SBA loans (he doesn't need them)
- Treat him like a prospect
- Use any corporate language

DO:
- Write like texting a business acquaintance
- Focus on mutual benefit/referrals
- Keep it under 50 words
- Sound natural

Write a brief message about setting up a referral partnership.
"""

		print("\n📝 SYSTEM PROMPT:")
		print("-"*40)
		print(good_system_prompt)
		
		print("\n📝 USER PROMPT:")
		print("-"*40)
		print(good_user_prompt)
		
		print("\n✅ This version understands the RELATIONSHIP!")
		
		# Actually send both and show results
		print("\n" + "="*80)
		print("🤖 ACTUAL OPENAI RESPONSES")
		print("="*80)
		
		# Bad version
		print("\n❌ BAD VERSION OUTPUT:")
		print("-"*40)
		bad_response = self.client.chat.completions.create(
			model="gpt-4o-mini",
			messages=[
				{"role": "system", "content": bad_system_prompt},
				{"role": "user", "content": bad_user_prompt}
			],
			temperature=0.7,
			max_tokens=150
		)
		print(bad_response.choices[0].message.content)
		
		# Good version
		print("\n✅ GOOD VERSION OUTPUT:")
		print("-"*40)
		good_response = self.client.chat.completions.create(
			model="gpt-4o-mini",
			messages=[
				{"role": "system", "content": good_system_prompt},
				{"role": "user", "content": good_user_prompt}
			],
			temperature=0.7,
			max_tokens=150
		)
		print(good_response.choices[0].message.content)
		
		print("\n" + "="*80)
		
		# Show token usage
		print("\n📊 TOKEN USAGE:")
		print(f"Bad version: ~{len(bad_system_prompt + bad_user_prompt)//4} tokens")
		print(f"Good version: ~{len(good_system_prompt + good_user_prompt)//4} tokens")
		print("(Rough estimate - actual tokens vary)")
		
		return {
			"bad_prompt": bad_system_prompt + "\n\n" + bad_user_prompt,
			"good_prompt": good_system_prompt + "\n\n" + good_user_prompt,
			"bad_response": bad_response.choices[0].message.content,
			"good_response": good_response.choices[0].message.content
		}

if __name__ == "__main__":
	debug = DebugGenerator()
	debug.show_what_we_send(contact_id=48)  # Andy
	