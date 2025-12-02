#!/usr/bin/env python3
"""
FIXED Generator - Actually understands relationships
"""
import os
import sqlite3
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class SmartContextGenerator:
    """Generate content that actually makes sense"""
    
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    def generate_for_andy(self):
        """Generate PROPER content for Andy"""
        
        # CRITICAL CONTEXT THAT MUST BE UNDERSTOOD
        context = """
CRITICAL RELATIONSHIP CONTEXT - READ THIS FIRST:

ANDY BRATT IS NOT A PROSPECT. HE IS A PEER IN THE INDUSTRY.

- Andy works at Gantry - they do $1M-$200M commercial real estate loans
- Chris (me) works at Harvest - we do SBA loans under $5M
- We are COMPLEMENTARY not competitive
- Known each other 10 years through industry events
- Andy could REFER his too-small deals to Chris
- Chris could REFER his too-big deals to Andy

DO NOT try to sell Andy SBA loans. He doesn't need them.
DO NOT treat him like a prospect. He's a potential referral partner.

Andy's Full Profile:
Principal at Gantry, Inc. - largest independent commercial mortgage banking firm in Western U.S.
Does $1M-$200M loans for institutional lenders
CCIM designation, 20+ years experience
Arranges debt/equity for major CRE deals

Chris's Profile:
SVP at Harvest Small Business Finance
Does SBA 504/7(a) loans for small businesses
Focus on owner-occupied CRE under $5M
20+ years experience
"""

        prompts = {
            "referral_partnership": """
Write a casual email from Chris to Andy about potential referral partnership.

Context: Andy gets deals too small for Gantry ($1-5M range). Chris gets deals too big for SBA (over $5M).
Tone: Professional peers who respect each other
Length: Under 75 words
Focus: Mutual benefit, not selling

Example of what it should sound like:
"Andy - quick thought. You probably get smaller owner-user deals that don't pencil for Gantry. 
I occasionally see $10M+ that are outside SBA limits. Want to set up a referral arrangement? 
Could be win-win. Coffee next week?"
""",
            
            "market_observation": """
Write a brief message from Chris to Andy sharing a market observation.

Context: Both are in CRE finance, see different parts of the market
Tone: Sharing intelligence between peers
Length: Under 60 words

Example feel:
"Interesting trend - seeing a lot of companies looking to buy vs lease post-COVID.
Your guys seeing the same on larger deals? Might be good pipeline for both of us."
""",
            
            "deal_referral": """
Write a message from Chris to Andy referring a specific opportunity.

Context: Chris has a $15M hotel deal that's too big for SBA, perfect for Gantry
Tone: Doing Andy a favor by sending good business
Length: Under 50 words

Example:
"Andy - have a strong borrower looking at $15M hotel acquisition in Newport. 
Too big for SBA but right in your wheelhouse. Want the intro?"
"""
        }
        
        results = {}
        
        for content_type, prompt in prompts.items():
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Write authentic business communication between long-time industry peers. No corporate speak. Get to the point."},
                    {"role": "user", "content": context + "\n\n" + prompt}
                ],
                temperature=0.8,
                max_tokens=100
            )
            
            results[content_type] = response.choices[0].message.content
        
        return results
    
    def generate_for_actual_prospect(self, contact_id):
        """Generate for someone who actually needs SBA loans"""
        
        conn = sqlite3.connect(os.path.expanduser("~/projects/apex/apex.db"))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM contacts WHERE id = ?", (contact_id,))
        contact = dict(cursor.fetchone())
        conn.close()
        
        # Check if they're actually a prospect
        title_lower = (contact.get('title', '') or '').lower()
        
        # These are BROKERS/COMPETITORS - treat as referral partners
        if any(x in title_lower for x in ['broker', 'ccim', 'mortgage', 'lender', 'banker']):
            prompt_type = "referral_partner"
            context = f"""
{contact['name']} is a BROKER/LENDER, not a prospect.
They could REFER deals to us, not buy from us.
Write as peer-to-peer, exploring partnership.
"""
        
        # These are actual PROSPECTS - business owners who might need loans
        elif any(x in title_lower for x in ['ceo', 'owner', 'president', 'cfo', 'founder']):
            prompt_type = "actual_prospect"
            context = f"""
{contact['name']} runs {contact['company']} and might need SBA financing.
They could be LEASING and should consider BUYING.
Write about building wealth through ownership vs paying rent.
"""
        
        else:
            prompt_type = "general"
            context = f"Standard outreach to {contact['name']} at {contact['company']}"
        
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Write appropriate business outreach based on recipient's role."},
                {"role": "user", "content": context + "\n\nWrite a brief, natural email. Under 100 words."}
            ],
            temperature=0.7
        )
        
        return response.choices[0].message.content

if __name__ == "__main__":
    generator = SmartContextGenerator()
    
    print("\n🎯 PROPER CONTENT FOR ANDY (PEER, NOT PROSPECT)")
    print("="*60)
    
    results = generator.generate_for_andy()
    
    for content_type, content in results.items():
        print(f"\n📧 {content_type.upper().replace('_', ' ')}:")
        print("-"*40)
        print(content)
    
    print("\n" + "="*60)
    
    # Test with an actual prospect
    print("\n🎯 CONTENT FOR ACTUAL PROSPECT")
    print("="*60)
    
    # Find a CEO/Owner to test with
    conn = sqlite3.connect(os.path.expanduser("~/projects/apex/apex.db"))
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, name, title, company 
        FROM contacts 
        WHERE (title LIKE '%CEO%' OR title LIKE '%Owner%' OR title LIKE '%President%')
        AND id != 48
        LIMIT 1
    """)
    prospect = cursor.fetchone()
    conn.close()
    
    if prospect:
        print(f"\nGenerating for {prospect[1]} ({prospect[2]}) at {prospect[3]}...")
        content = generator.generate_for_actual_prospect(prospect[0])
        print("-"*40)
        print(content)
