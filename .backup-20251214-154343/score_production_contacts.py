#!/usr/bin/env python3
"""Bulk score all Railway contacts"""
import requests
import time

API_URL = 'https://apex-intelligence-production.up.railway.app'

# Get all contacts
response = requests.get(f"{API_URL}/api/contacts?limit=2000")
contacts = response.json()

print(f"📊 Found {len(contacts)} contacts to score")

scored = 0
failed = 0

for i, contact in enumerate(contacts, 1):
    contact_id = contact['id']
    print(f"[{i}/{len(contacts)}] Scoring {contact.get('name', 'Unknown')}...", end=" ")
    
    try:
        resp = requests.post(f"{API_URL}/api/contacts/{contact_id}/score", timeout=30)
        if resp.status_code == 200:
            result = resp.json()
            print(f"✅ {result.get('scores', {}).get('urgency', 'SCORED')}")
            scored += 1
        else:
            print(f"❌ HTTP {resp.status_code}")
            failed += 1
    except Exception as e:
        print(f"❌ {e}")
        failed += 1
    
    # Rate limiting
    if i % 50 == 0:
        time.sleep(2)

print(f"\n{'='*60}")
print(f"✅ Scored: {scored} | ❌ Failed: {failed}")
