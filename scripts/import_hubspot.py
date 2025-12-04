#!/usr/bin/env python3
"""HubSpot contact import for Apex"""

import os
import sqlite3
import requests
from datetime import datetime

TOKEN = os.getenv('HUBSPOT_ACCESS_TOKEN')
DB = 'apex.db'

if not TOKEN:
	print("❌ HUBSPOT_ACCESS_TOKEN not set")
	print("   Run: export $(grep -v '^#' .env | xargs)")
	exit(1)

headers = {"Authorization": f"Bearer {TOKEN}"}
url = "https://api.hubapi.com/crm/v3/objects/contacts"
params = {
	"limit": 100,
	"properties": "firstname,lastname,email,phone,mobilephone,jobtitle,company,hs_linkedin_url"
}

print("📥 Fetching contacts from HubSpot...")

all_contacts = []
after = None

while True:
	if after:
		params['after'] = after
	
	resp = requests.get(url, headers=headers, params=params)
	
	if resp.status_code != 200:
		print(f"❌ HubSpot API error: {resp.status_code}")
		print(resp.text[:500])
		break
	
	data = resp.json()
	contacts = data.get('results', [])
	all_contacts.extend(contacts)
	
	paging = data.get('paging', {}).get('next', {})
	after = paging.get('after')
	
	print(f"   Fetched {len(all_contacts)} contacts...")
	
	if not after:
		break

print(f"✅ Total fetched: {len(all_contacts)}")

con = sqlite3.connect(DB)
cur = con.cursor()

imported = updated = skipped = 0

for c in all_contacts:
	props = c.get('properties', {})
	email = props.get('email')
	
	if not email:
		skipped += 1
		continue
	
	first = props.get('firstname', '') or ''
	last = props.get('lastname', '') or ''
	name = f"{first} {last}".strip() or email.split('@')[0]
	
	# Check if exists
	cur.execute("SELECT id FROM contacts WHERE email = ?", (email,))
	existing = cur.fetchone()
	
	if existing:
		# Update existing
		cur.execute("""
			UPDATE contacts SET
				name = COALESCE(?, name),
				phone = COALESCE(?, phone),
				phone_mobile = COALESCE(?, phone_mobile),
				title = COALESCE(?, title),
				company = COALESCE(?, company),
				linkedin_url = COALESCE(?, linkedin_url),
				import_source = 'hubspot',
				crm_id = ?,
				last_crm_sync = ?,
				updated_at = ?
			WHERE email = ?
		""", (
			name,
			props.get('phone'),
			props.get('mobilephone'),
			props.get('jobtitle'),
			props.get('company'),
			props.get('hs_linkedin_url'),
			c.get('id'),
			datetime.now().isoformat(),
			datetime.now().isoformat(),
			email
		))
		updated += 1
	else:
		# Insert new
		cur.execute("""
			INSERT INTO contacts (
				name, email, phone, phone_mobile, title, company, 
				linkedin_url, import_source, crm_id, last_crm_sync, 
				enrichment_status, created_at, updated_at
			) VALUES (?, ?, ?, ?, ?, ?, ?, 'hubspot', ?, ?, 'pending', ?, ?)
		""", (
			name, email,
			props.get('phone'),
			props.get('mobilephone'),
			props.get('jobtitle'),
			props.get('company'),
			props.get('hs_linkedin_url'),
			c.get('id'),
			datetime.now().isoformat(),
			datetime.now().isoformat(),
			datetime.now().isoformat()
		))
		imported += 1

con.commit()
con.close()

print("")
print("═" * 50)
print(f"✅ IMPORT COMPLETE")
print(f"   New contacts:     {imported}")
print(f"   Updated:          {updated}")
print(f"   Skipped (no email): {skipped}")
print("═" * 50)
