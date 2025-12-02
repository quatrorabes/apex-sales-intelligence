#!/usr/bin/env python3
"""Quick HubSpot import to populate local DB"""

import os
import sqlite3
import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('HUBSPOT_ACCESS_TOKEN')
DB = 'apex.db'

if not TOKEN:
    print("❌ HUBSPOT_ACCESS_TOKEN not set")
    exit(1)

headers = {"Authorization": f"Bearer {TOKEN}"}
url = "https://api.hubapi.com/crm/v3/objects/contacts"
params = {
    "limit": 100,
    "properties": "firstname,lastname,email,phone,mobilephone,jobtitle,company,linkedin_url"
}

print("📥 Fetching contacts from HubSpot...")
resp = requests.get(url, headers=headers, params=params)
resp.raise_for_status()
data = resp.json()

contacts = data.get('results', [])
print(f"   Found {len(contacts)} contacts")

con = sqlite3.connect(DB)
cur = con.cursor()

imported = 0
skipped = 0

for c in contacts:
    props = c.get('properties', {})
    email = props.get('email')
    
    # Skip if no email or already exists
    if not email:
        skipped += 1
        continue
    
    cur.execute("SELECT id FROM contacts WHERE email = ?", (email,))
    if cur.fetchone():
        skipped += 1
        continue
    
    # Build full name
    first = props.get('firstname', '') or ''
    last = props.get('lastname', '') or ''
    name = f"{first} {last}".strip() or email.split('@')[0]
    
    cur.execute("""
        INSERT INTO contacts (name, email, phone, phone_mobile, title, company, linkedin_url, import_source, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'hubspot', datetime('now'))
    """, (
        name,
        email,
        props.get('phone'),
        props.get('mobilephone'),
        props.get('jobtitle'),
        props.get('company'),
        props.get('linkedin_url')
    ))
    imported += 1

con.commit()
con.close()

print(f"✅ Imported: {imported}, Skipped: {skipped}")
print(f"   Run: sqlite3 apex.db 'SELECT COUNT(*) FROM contacts;'")
