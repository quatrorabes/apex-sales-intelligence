#!/usr/bin/env python3

#!/usr/bin/env python3
"""
Working content generator for APEX - Fixed function names
"""
import os
import sys
import sqlite3
import asyncio
import json

# Add the generator directory to path
sys.path.insert(0, '/Users/chrisrabenold/projects/apex/apps/backend/intelligence/engines/outreach/generators')

async def generate_for_contact(contact_id):
	from generate_content import ContentGenerator
	
	print(f"\n🚀 Generating content for contact ID {contact_id}...")
	
	try:
		# Get contact data first
		conn = sqlite3.connect(os.path.expanduser("~/projects/apex/apex.db"))
		conn.row_factory = sqlite3.Row
		cursor = conn.cursor()
		
		cursor.execute("SELECT * FROM contacts WHERE id = ?", (contact_id,))
		row = cursor.fetchone()
		
		if not row:
			print(f"❌ Contact {contact_id} not found")
			return False
		
		# Convert to dict
		contact = dict(row)
		
		# Get the profile/enrichment data
		profile = ""
		if contact['enrichment_data']:
			data = json.loads(contact['enrichment_data'])
			profile = data.get('perplexity_insights', '') or data.get('full_profile_text', '')
			
		print(f"✓ Found {contact['name']} with {len(profile)} chars of profile data")
		
		# Create generator
		generator = ContentGenerator()
		
		# Generate all content with CORRECT function names
		emails = await generator.generate_email_sequence(contact, profile)
		calls = await generator.generate_call_scripts(contact, profile)
		linkedin = await generator.generate_linkedin_request(contact, profile)  # Fixed name
		
		# Save to database
		cursor.execute("""
			UPDATE contacts SET
				email_1_subject = ?,
				email_1_body = ?,
				email_2_subject = ?,
				email_2_body = ?,
				email_3_subject = ?,
				email_3_body = ?,
				call_script_1 = ?,
				call_script_2 = ?,
				call_script_3 = ?,
				linkedin_request = ?,
				linkedin_followup = ?,
				content_generated_at = CURRENT_TIMESTAMP
			WHERE id = ?
		""", (
			emails.get('email_1', {}).get('subject'),
			emails.get('email_1', {}).get('body'),
			emails.get('email_2', {}).get('subject'),
			emails.get('email_2', {}).get('body'),
			emails.get('email_3', {}).get('subject'),
			emails.get('email_3', {}).get('body'),
			calls.get('call_1'),
			calls.get('call_2'),
			calls.get('call_3'),
			linkedin.get('request'),  # Changed key
			linkedin.get('followup'),  # Changed key
			contact_id
		))
		
		conn.commit()
		conn.close()
		
		print("\n✅ Content generated successfully!")
		
		# Display results
		if emails.get('email_1'):
			print(f"\n📧 EMAIL 1 SUBJECT: {emails['email_1']['subject']}")
			print(f"   Preview: {emails['email_1']['body'][:100]}...")
			
		if calls.get('call_1'):
			print(f"\n📞 CALL SCRIPT 1:")
			print(f"   {calls['call_1'][:150]}...")
			
		if linkedin.get('request'):
			print(f"\n💼 LINKEDIN REQUEST:")
			print(f"   {linkedin['request'][:150]}...")
			
		return True
	
	except Exception as e:
		print(f"\n❌ Error: {e}")
		import traceback
		traceback.print_exc()
		if 'conn' in locals():
			conn.close()
		return False
	
# Run it
if __name__ == "__main__":
	contact_id = 48  # Andy
	asyncio.run(generate_for_contact(contact_id))
	