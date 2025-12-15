#!/usr/bin/env python3
"""
LINKEDIN GENERATOR - WORLD CLASS EDITION
Combines Sales Navigator insights, LinkMatch Pro warmup, and AI personalization
"""

import os
import sys
import json
import sqlite3
from datetime import datetime, timezone
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

DB_PATH = '/Users/chrisrabenold/projects/apex/apex.db'


class LinkedInContentGenerator:
    """Generate hyper-personalized LinkedIn content using Sales Nav + AI"""

    def __init__(self, db_path=None):
        self.db_path = db_path or DB_PATH
        self.client = None
        self._init_openai()

    def _init_openai(self):
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            self.client = OpenAI(api_key=api_key)

    def _get_contact(self, contact_id):
        """Fetch contact with enrichment data"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        contact = conn.execute("""
            SELECT * FROM contacts WHERE id = ?
        """, (contact_id,)).fetchone()
        conn.close()
        return dict(contact) if contact else None

    def _get_sales_nav_insights(self, contact_id):
        """Get Sales Navigator insights if available"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row

        # Check if sales_nav tables exist
        tables = conn.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name LIKE 'sales_nav%'
        """).fetchall()

        if not tables:
            conn.close()
            return None

        try:
            lead = conn.execute("""
                SELECT snl.*, GROUP_CONCAT(sni.insight_type || ':' || sni.insight_data, '|||') as insights
                FROM sales_nav_leads snl
                LEFT JOIN sales_nav_insights sni ON snl.id = sni.lead_id
                WHERE snl.contact_id = ?
                GROUP BY snl.id
            """, (contact_id,)).fetchone()
            conn.close()

            if lead:
                insights = []
                if lead['insights']:
                    for item in lead['insights'].split('|||'):
                        if ':' in item:
                            itype, idata = item.split(':', 1)
                            try:
                                insights.append({'type': itype, 'data': json.loads(idata)})
                            except:
                                pass
                return {
                    'lead_data': json.loads(lead['lead_data']) if lead['lead_data'] else {},
                    'insights': insights
                }
        except Exception as e:
            conn.close()
            print(f"    ⚠️ Sales Nav lookup: {e}")

        return None

    def _get_user_preferences(self):
        """Load Why Me? preferences"""
        conn = sqlite3.connect(self.db_path)
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

    def _extract_personality(self, profile_content):
        """Extract personality type from enrichment"""
        if not profile_content:
            return 'Unknown'

        for ptype in ['D-Type', 'I-Type', 'S-Type', 'C-Type', 'ENTJ', 'INTJ', 'ENFP', 'INFP']:
            if ptype in profile_content:
                return ptype
        return 'Unknown'

    def _build_context(self, contact, sales_nav_data, user_prefs):
        """Build rich context for AI generation"""

        # Basic contact info
        context = f"""
PROSPECT PROFILE:
- Name: {contact.get('firstname', '')} {contact.get('lastname', '')}
- Title: {contact.get('jobtitle', 'Unknown')}
- Company: {contact.get('company', 'Unknown')}
- Email: {contact.get('email', '')}
- LinkedIn: {contact.get('linkedin_url', '')}
"""

        # Add personality if available
        personality = self._extract_personality(contact.get('profile_content', ''))
        if personality != 'Unknown':
            context += f"- Personality Type: {personality}\n"

        # Add enrichment highlights
        if contact.get('profile_content'):
            profile = contact['profile_content'][:2000]  # First 2000 chars
            context += f"""
ENRICHMENT HIGHLIGHTS:
{profile}
"""

        # Add Sales Navigator insights
        if sales_nav_data and sales_nav_data.get('insights'):
            context += "\nSALES NAVIGATOR INSIGHTS:\n"
            for insight in sales_nav_data['insights'][:5]:
                if insight.get('data', {}).get('message'):
                    context += f"- {insight['data']['message']}\n"
                if insight.get('data', {}).get('action'):
                    context += f"  → Action: {insight['data']['action']}\n"

        # Add user's business context
        context += f"""
YOUR BUSINESS (Why Me?):
- Products: {', '.join(user_prefs['products'][:3]) if user_prefs['products'] else 'Sales intelligence platform'}
- Services: {', '.join(user_prefs['services'][:3]) if user_prefs['services'] else 'AI-powered contact enrichment'}
- Value Props: {'. '.join(user_prefs['value_propositions'][:2]) if user_prefs['value_propositions'] else 'Help sales teams close more deals faster'}
"""

        return context

    def generate_connection_request(self, contact, context, personality):
        """Generate <300 char connection request"""

        # Personality-based approach
        approaches = {
            'D-Type': 'Direct, results-focused, skip pleasantries',
            'I-Type': 'Warm, enthusiastic, mention shared interests',
            'S-Type': 'Friendly, low-pressure, build rapport first',
            'C-Type': 'Professional, data-driven, mention specific value',
            'Unknown': 'Professional and personalized'
        }

        approach = approaches.get(personality, approaches['Unknown'])

        prompt = f"""Write a LinkedIn connection request (MUST be under 280 characters).

{context}

APPROACH: {approach}

REQUIREMENTS:
- Reference something SPECIFIC about them (company, role, recent activity)
- Clear reason for connecting
- No generic "I'd love to connect" without context
- Professional but human
- UNDER 280 CHARACTERS (this is critical - LinkedIn limit is 300)

Return ONLY the message, nothing else."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You write hyper-personalized LinkedIn connection requests. Always under 280 characters."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=150
            )
            message = response.choices[0].message.content.strip()
            # Remove quotes if present
            message = message.strip('"').strip("'")
            # Truncate if over 300
            if len(message) > 300:
                message = message[:297] + "..."
            return message
        except Exception as e:
            print(f"    ❌ Connection request error: {e}")
            firstname = contact.get('firstname', 'there')
            company = contact.get('company', 'your company')
            return f"Hi {firstname}, I work with companies like {company} helping them grow faster. Would love to connect and share some ideas."

    def generate_follow_up(self, contact, context, personality):
        """Generate follow-up message after connection"""

        prompt = f"""Write a LinkedIn follow-up message sent AFTER they accepted your connection.

{context}

REQUIREMENTS:
- Thank them for connecting (briefly)
- Provide genuine value or insight relevant to their role
- Soft ask for conversation (not hard pitch)
- Personality-aware: {personality}
- 50-100 words
- Natural, conversational tone

Return ONLY the message."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You write personalized LinkedIn follow-up messages that provide value before asking."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=300
            )
            return response.choices[0].message.content.strip().strip('"').strip("'")
        except Exception as e:
            print(f"    ❌ Follow-up error: {e}")
            return f"Thanks for connecting! I noticed you're doing interesting work at {contact.get('company', 'your company')}. I work with similar companies on sales intelligence - would love to hear about your current priorities and see if there's any way I can help."

    def generate_inmail(self, contact, context, personality):
        """Generate InMail (for non-connections or premium outreach)"""

        prompt = f"""Write a LinkedIn InMail for cold outreach.

{context}

REQUIREMENTS:
- Compelling subject line (5-8 words)
- Hook in first sentence (reference their work/company/news)
- Clear value proposition
- Specific call-to-action
- Personality-aware: {personality}
- 75-150 words total body
- Format:
  SUBJECT: [subject line]
  BODY: [message body]

Return ONLY in that format."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You write compelling LinkedIn InMails that get responses. Focus on relevance and value."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=400
            )

            content = response.choices[0].message.content.strip()

            # Parse subject and body
            subject = ""
            body = ""

            if "SUBJECT:" in content and "BODY:" in content:
                parts = content.split("BODY:")
                subject = parts[0].replace("SUBJECT:", "").strip()
                body = parts[1].strip() if len(parts) > 1 else ""
            else:
                body = content
                subject = f"Quick idea for {contact.get('company', 'your team')}"

            return {
                'subject': subject.strip('"').strip("'"),
                'body': body.strip('"').strip("'")
            }
        except Exception as e:
            print(f"    ❌ InMail error: {e}")
            return {
                'subject': f"Quick idea for {contact.get('company', 'your team')}",
                'body': f"Hi {contact.get('firstname', 'there')},\n\nI work with companies like {contact.get('company', 'yours')} helping them accelerate sales through better intelligence.\n\nWould you be open to a 15-minute call to explore if we could help?\n\nBest regards"
            }

    def generate_warmup_sequence(self, contact):
        """Generate LinkMatch Pro style warmup sequence"""
        return {
            'day_1_3': [
                f"View {contact.get('firstname', 'their')}'s profile",
                "Like 1-2 of their recent posts",
                "View their company page"
            ],
            'day_4_7': [
                "Like another post or article they shared",
                "View profile again",
                "Comment thoughtfully on a post (optional)"
            ],
            'day_8': [
                "Send personalized connection request",
                "Reference something from their recent content"
            ],
            'post_connect': [
                "Wait 24-48 hours after acceptance",
                "Send value-first follow-up message",
                "Continue engaging with their content"
            ]
        }

    def generate_all_content(self, contact_id):
        """Generate all LinkedIn content for a contact"""
        print(f"\n🔵 LinkedIn Generator: Contact {contact_id}")

        # Get contact
        contact = self._get_contact(contact_id)
        if not contact:
            print("    ❌ Contact not found")
            return None

        print(f"    📋 {contact.get('firstname', '')} {contact.get('lastname', '')} @ {contact.get('company', '')}")

        # Get Sales Nav insights
        sales_nav_data = self._get_sales_nav_insights(contact_id)
        if sales_nav_data:
            print(f"    📊 Found {len(sales_nav_data.get('insights', []))} Sales Nav insights")

        # Get user preferences
        user_prefs = self._get_user_preferences()

        # Build context
        context = self._build_context(contact, sales_nav_data, user_prefs)

        # Extract personality
        personality = self._extract_personality(contact.get('profile_content', ''))
        print(f"    🧠 Personality: {personality}")

        # Generate content
        print("    ✍️ Generating connection request...")
        connection_request = self.generate_connection_request(contact, context, personality)
        print(f"       ✅ ({len(connection_request)} chars)")

        print("    ✍️ Generating follow-up message...")
        follow_up = self.generate_follow_up(contact, context, personality)
        print(f"       ✅ Generated")

        print("    ✍️ Generating InMail...")
        inmail = self.generate_inmail(contact, context, personality)
        print(f"       ✅ Subject: {inmail['subject'][:40]}...")

        # Generate warmup sequence
        warmup = self.generate_warmup_sequence(contact)

        # Build result
        result = {
            'linkedin_connect': connection_request,
            'linkedin_followup': follow_up,
            'linkedin_inmail': f"Subject: {inmail['subject']}\n\n{inmail['body']}",
            'linkedin_warmup': json.dumps(warmup),
            'personality_detected': personality
        }

        # Save to database
        self._save_content(contact_id, result)

        return result

    def _save_content(self, contact_id, content):
        """Save generated content to contacts table"""
        conn = sqlite3.connect(self.db_path)

        # Check if columns exist, add if not
        cursor = conn.cursor()
        existing_cols = [col[1] for col in cursor.execute("PRAGMA table_info(contacts)").fetchall()]

        new_cols = ['linkedin_connect', 'linkedin_followup', 'linkedin_inmail', 'linkedin_warmup']
        for col in new_cols:
            if col not in existing_cols:
                cursor.execute(f"ALTER TABLE contacts ADD COLUMN {col} TEXT")

        # Update contact
        cursor.execute("""
            UPDATE contacts 
            SET linkedin_connect = ?,
                linkedin_followup = ?,
                linkedin_inmail = ?,
                linkedin_warmup = ?
            WHERE id = ?
        """, (
            content['linkedin_connect'],
            content['linkedin_followup'],
            content['linkedin_inmail'],
            content.get('linkedin_warmup', ''),
            contact_id
        ))

        conn.commit()
        conn.close()
        print("    💾 Saved to database")


# Main function for API integration
def generate_linkedin_content(contact_id, contact_data=None):
    """Main entry point for API calls"""
    generator = LinkedInContentGenerator()
    return generator.generate_all_content(contact_id)


# CLI
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("""
╔══════════════════════════════════════════════════════════════╗
║     LINKEDIN CONTENT GENERATOR - WORLD CLASS EDITION         ║
║  Sales Nav + LinkMatch Pro + AI Personalization              ║
╚══════════════════════════════════════════════════════════════╝

Usage:
    python linkedin_generator.py <contact_id>
    python linkedin_generator.py 7
        """)
        sys.exit(1)

    contact_id = int(sys.argv[1])
    generator = LinkedInContentGenerator()
    result = generator.generate_all_content(contact_id)

    if result:
        print("\n" + "="*60)
        print("📝 GENERATED CONTENT")
        print("="*60)

        print(f"\n🔗 CONNECTION REQUEST ({len(result['linkedin_connect'])} chars):")
        print("-" * 40)
        print(result['linkedin_connect'])

        print(f"\n💬 FOLLOW-UP MESSAGE:")
        print("-" * 40)
        print(result['linkedin_followup'])

        print(f"\n📧 INMAIL:")
        print("-" * 40)
        print(result['linkedin_inmail'])

        print(f"\n🔥 WARMUP SEQUENCE:")
        print("-" * 40)
        warmup = json.loads(result['linkedin_warmup'])
        for phase, actions in warmup.items():
            print(f"  {phase.replace('_', ' ').title()}:")
            for action in actions:
                print(f"    • {action}")
        print()
