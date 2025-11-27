#!/usr/bin/env python3

#!/usr/bin/env python3
"""
Working content generator for APEX
"""
import os
import sys
import sqlite3
import asyncio
import json

# Add the generator directory to path
sys.path.insert(0, '/Users/chrisrabenold/projects/apex/apps/backend/intelligence/engines/outreach/generators')

# Set the database path
os.environ['APEX_DB'] = os.path.expanduser("~/projects/apex/apex.db")

async def generate_for_contact(contact_id):
	from generate_content import ContentGenerator
	
	print(f"\n🚀 Generating content for contact ID {contact_id}...")
	
	try:
		generator = ContentGenerator()
		
		# Generate all content
		emails = await generator.generate_email_sequence(contact_id)
		calls = await generator.generate_call_scripts(contact_id) 
		linkedin = await generator.generate_linkedin_outreach(contact_id)
		
		# Get connection
		conn = sqlite3.connect(os.path.expanduser("~/projects/apex/apex.db"))
		cursor = conn.cursor()
		
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
			linkedin.get('connection_request'),
			linkedin.get('follow_up'),
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
			
		if linkedin.get('connection_request'):
			print(f"\n💼 LINKEDIN REQUEST:")
			print(f"   {linkedin['connection_request'][:150]}...")
			
		return True
	
	except Exception as e:
		print(f"\n❌ Error: {e}")
		import traceback
		traceback.print_exc()
		return False
	
# Run it
if __name__ == "__main__":
	contact_id = 48  # Andy
	asyncio.run(generate_for_contact(contact_id))
	