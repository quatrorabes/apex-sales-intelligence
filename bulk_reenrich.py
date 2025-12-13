#!/usr/bin/env python3
"""
Bulk Re-Enrichment Script for Apex
Finds contacts with old enrichment format and re-enriches them
"""

import os
import psycopg2
import requests
import time
from urllib.parse import urlparse

# Database connection
DATABASE_URL = os.environ.get('DATABASE_PUBLIC_URL') or os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    print("❌ DATABASE_URL not found in environment")
    exit(1)

# Parse connection
result = urlparse(DATABASE_URL)
conn = psycopg2.connect(
    database=result.path[1:],
    user=result.username,
    password=result.password,
    host=result.hostname,
    port=result.port
)
cur = conn.cursor()

# Find contacts needing re-enrichment
print("🔍 Scanning for contacts with old enrichment format...")
cur.execute("""
    SELECT id, firstname, lastname, company, jobtitle, enrichment_status, 
           CASE 
               WHEN profile_text LIKE '%=== SALES INTELLIGENCE ===%' THEN 'new'
               WHEN profile_text LIKE '%## %' THEN 'old_markdown'
               WHEN profile_text IS NOT NULL THEN 'old_other'
               ELSE 'not_enriched'
           END as format_type
    FROM contacts
    WHERE enrichment_status = 'completed'
    AND (profile_text NOT LIKE '%=== SALES INTELLIGENCE ===%' OR profile_text IS NULL)
    LIMIT 50
""")

candidates = cur.fetchall()
print(f"📊 Found {len(candidates)} contacts with old/missing enrichment data\n")

# Show sample
for row in candidates[:10]:
    print(f"  - ID {row[0]}: {row[1]} {row[2]} @ {row[3]} ({row[6]})")

if not candidates:
    print("✅ All contacts are up to date!")
    exit(0)

# Confirm
choice = input(f"\n⚠️  Re-enrich these {len(candidates)} contacts? (yes/no): ")
if choice.lower() != 'yes':
    print("Aborted.")
    exit(0)

# Re-enrich each
API_BASE = "https://apex-backend-production-production.up.railway.app"
success_count = 0
error_count = 0

for idx, row in enumerate(candidates, 1):
    contact_id = row[0]
    name = f"{row[1]} {row[2]}"
    
    print(f"\n[{idx}/{len(candidates)}] Enriching {name} (ID {contact_id})...")
    
    try:
        resp = requests.post(f"{API_BASE}/api/contacts/{contact_id}/enrich", timeout=120)
        resp.raise_for_status()
        result = resp.json()
        
        if result.get('profile_text'):
            print(f"  ✅ Success ({len(result['profile_text'])} chars)")
            success_count += 1
        else:
            print(f"  ⚠️  No profile_text returned")
            error_count += 1
            
    except Exception as e:
        print(f"  ❌ Error: {e}")
        error_count += 1
    
    # Rate limit (Perplexity free tier: 5 req/min)
    if idx < len(candidates):
        print("  ⏳ Waiting 15s...")
        time.sleep(15)

print(f"\n{'='*60}")
print(f"✅ Re-enriched: {success_count}")
print(f"❌ Errors: {error_count}")
print(f"{'='*60}")

conn.close()
