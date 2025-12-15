#!/usr/bin/env python3
"""
EMAIL GENERATOR - WHY ME? INTEGRATED
Generates 3 personalized email variants using user's products/services
"""

import os
import sys
import json
import sqlite3
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

DB_PATH = '/Users/chrisrabenold/projects/apex/apex.db'


def get_user_preferences():
    """Load Why Me? preferences from database"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    row = conn.execute("""
        SELECT products, services, value_propositions, target_customers
        FROM user_preferences
        WHERE user_id = 'default_user'
    """).fetchone()
    conn.close()

    if not row:
        return {
            'products': [],
            'services': [],
            'value_propositions': [],
            'target_customers': []
        }

    return {
        'products': json.loads(row['products'] or '[]'),
        'services': json.loads(row['services'] or '[]'),
        'value_propositions': json.loads(row['value_propositions'] or '[]'),
        'target_customers': json.loads(row['target_customers'] or '[]')
    }


def generate_email_variants(contact_data, enrichment_data=None, business_profile=None):
    """Generate 3 email variants with Why Me? integration"""

    # Initialize OpenAI
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("ERROR: OPENAI_API_KEY not found")
        return []

    client = OpenAI(api_key=api_key)

    # GET USER PREFERENCES (WHY ME? DATA)
    user_prefs = get_user_preferences()
    if not user_prefs:
        user_prefs = {'products': [], 'services': [], 'value_propositions': [], 'target_customers': []}

    # Build prospect context
    prospect_context = f"""
PROSPECT:
- Name: {contact_data.get('firstname', 'Unknown')} {contact_data.get('lastname', '')}
- Company: {contact_data.get('company', 'Unknown')}
- Title: {contact_data.get('jobtitle', 'Unknown')}
"""

    # Add enrichment if available
    if enrichment_data:
        if enrichment_data.get('linkedin_summary'):
            prospect_context += f"\n- Background: {enrichment_data['linkedin_summary']}"
        if enrichment_data.get('recent_news'):
            prospect_context += f"\n- Recent News: {enrichment_data['recent_news']}"

    # BUILD BUSINESS CONTEXT FROM WHY ME? DATA
    business_context = f"""
YOUR BUSINESS (from Why Me? preferences):
- Products: {', '.join(user_prefs['products'][:3]) if user_prefs['products'] else 'Not specified'}
- Services: {', '.join(user_prefs['services'][:3]) if user_prefs['services'] else 'Not specified'}
- Value Props: {'. '.join(user_prefs['value_propositions'][:3]) if user_prefs['value_propositions'] else 'Not specified'}
- Target Customers: {', '.join(user_prefs['target_customers'][:2]) if user_prefs['target_customers'] else 'Not specified'}
"""

    # Define email approaches
    email_approaches = [
        {
            'style': 'Problem-Agitate-Solve',
            'description': 'Lead with relevant problem, present solution',
            'instructions': f"""
Write a short, highly personalized B2B sales email using Problem-Agitate-Solve.

{prospect_context}

{business_context}

REQUIREMENTS:
- Reference something SPECIFIC about their company/role
- Lead with a problem they likely face
- Show how {user_prefs['products'][0] if user_prefs['products'] else 'your solution'} solves it
- Emphasize: {user_prefs['value_propositions'][0] if user_prefs['value_propositions'] else 'value proposition'}
- Keep under 80 words
- Natural, conversational tone
- End with simple question

FORMAT:
Subject: [compelling subject line]
Body: [email body]
"""
        },
        {
            'style': 'Social Proof',
            'description': 'Reference similar success story',
            'instructions': f"""
Write a short email using social proof.

{prospect_context}

{business_context}

REQUIREMENTS:
- Reference how similar companies use {user_prefs['products'][0] if user_prefs['products'] else 'your product'}
- Connect to their specific situation
- Emphasize: {user_prefs['value_propositions'][0] if user_prefs['value_propositions'] else 'key benefit'}
- Under 80 words
- Natural tone

FORMAT:
Subject: [subject]
Body: [body]
"""
        },
        {
            'style': 'Value-First',
            'description': 'Offer value with no pitch',
            'instructions': f"""
Write a value-first email.

{prospect_context}

{business_context}

REQUIREMENTS:
- Offer something useful (insight, resource) with NO strings
- Show you understand their world
- Reference: {user_prefs['target_customers'][0] if user_prefs['target_customers'] else 'their industry'}
- Under 80 words
- Helpful, not salesy

FORMAT:
Subject: [subject]
Body: [body]
"""
        }
    ]

    variants = []

    for i, approach in enumerate(email_approaches, 1):
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert B2B sales copywriter who writes hyper-personalized emails."},
                    {"role": "user", "content": approach['instructions']}
                ],
                temperature=0.7,
                max_tokens=800
            )

            content = response.choices[0].message.content.strip()

            # Parse subject and body
            subject = ""
            body = ""
            lines = content.split('\n')

            for line in lines:
                if line.startswith('Subject:'):
                    subject = line.replace('Subject:', '').strip()
                elif line.startswith('Body:'):
                    body = line.replace('Body:', '').strip()
                elif body:
                    body += '\n' + line.strip()

            if not subject:
                subject = f"Quick thought about {contact_data.get('company', 'your company')}"
            if not body:
                body = content[:200]

            variant = {
                'subject': subject,
                'body': body.strip(),
                'style': approach['style']
            }

            variants.append(variant)
            print(f"    ✅ Generated {i}/3: {approach['style']}")

        except Exception as e:
            print(f"    ❌ Error generating {approach['style']}: {e}")
            variants.append({
                'subject': f"Thought about {contact_data.get('company')}",
                'body': f"Hi {contact_data.get('firstname')}, I work with companies like yours...",
                'style': f"{approach['style']} (Fallback)"
            })

    return variants


if __name__ == '__main__':
    # Test
    test_contact = {
        'firstname': 'John',
        'lastname': 'Doe',
        'company': 'Acme Corp',
        'jobtitle': 'VP of Operations',
        'email': 'john@acme.com'
    }

    print("Testing Why Me? integrated email generation...")
    variants = generate_email_variants(test_contact)

    for i, v in enumerate(variants, 1):
        print(f"\n--- EMAIL {i}: {v['style']} ---")
        print(f"Subject: {v['subject']}")
        print(f"Body:\n{v['body']}")
