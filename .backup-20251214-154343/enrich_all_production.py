#!/usr/bin/env python3
"""Bulk enrich all Railway contacts with AI profiles"""
import requests
import time
from datetime import datetime

API_URL = 'https://apex-intelligence-production.up.railway.app'

def get_contacts(limit=2000):
    """Fetch all contacts from Railway"""
    response = requests.get(f"{API_URL}/api/contacts?limit={limit}")
    if response.status_code == 200:
        return response.json()
    print(f"❌ Failed to fetch contacts: {response.status_code}")
    return []

def enrich_contact(contact_id):
    """Trigger enrichment for single contact"""
    try:
        response = requests.post(
            f"{API_URL}/api/contacts/{contact_id}/enrich",
            timeout=60
        )
        return response.status_code == 200
    except Exception as e:
        return False

def main():
    print("=" * 70)
    print("🚀 APEX BULK ENRICHMENT — PRODUCTION")
    print("=" * 70)
    
    # Get all contacts
    print("\n📥 Fetching contacts from Railway...")
    contacts = get_contacts()
    total = len(contacts)
    print(f"✅ Found {total} contacts to enrich")
    
    # Enrich in batches
    enriched = 0
    failed = 0
    batch_size = 10
    
    print(f"\n🔄 Starting enrichment (batches of {batch_size})...\n")
    
    for i, contact in enumerate(contacts, 1):
        contact_id = contact['id']
        name = contact.get('name', 'Unknown')
        
        # Skip if already enriched
        if contact.get('enrichment_status') == 'completed':
            print(f"[{i:4}/{total}] {name:30} ⏭️  Already enriched")
            enriched += 1
            continue
        
        # Trigger enrichment
        success = enrich_contact(contact_id)
        
        if success:
            print(f"[{i:4}/{total}] {name:30} ✅ Enrichment triggered")
            enriched += 1
        else:
            print(f"[{i:4}/{total}] {name:30} ❌ Failed")
            failed += 1
        
        # Rate limiting: pause every batch
        if i % batch_size == 0:
            print(f"   ⏸️  Pausing {batch_size} sec (batch limit)...\n")
            time.sleep(batch_size)
    
    # Summary
    print("\n" + "=" * 70)
    print(f"✅ ENRICHMENT SUMMARY")
    print("=" * 70)
    print(f"Total contacts:    {total}")
    print(f"Triggered:         {enriched}")
    print(f"Failed:            {failed}")
    print(f"Success rate:      {(enriched/total*100):.1f}%")
    print(f"Estimated time:    {(total / 2):.0f} minutes (assuming 2 enrichments/min)")
    print(f"Timestamp:         {datetime.now().isoformat()}")
    print("=" * 70)

if __name__ == '__main__':
    main()
