#!/usr/bin/env python3
"""HubSpot filtered contact import for Apex"""

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

# ═══════════════════════════════════════════════════════════════
# FILTER CONFIGURATION
# ═══════════════════════════════════════════════════════════════
EXCLUDED_LEAD_STATUSES = ['unqualified', 'do not contact', 'unsubscribe']
EXCLUDED_LIFECYCLE_STAGES = ['unqualified']
REQUIRE_EMAIL = True
REQUIRE_COMPANY = True
REQUIRE_PHONE = True
EXCLUDE_PERSONAL_CONTACTS = True
MAX_IMPORTS = None  # Set to number to limit, None for all

# ═══════════════════════════════════════════════════════════════

headers = {"Authorization": f"Bearer {TOKEN}"}
url = "https://api.hubapi.com/crm/v3/objects/contacts"
params = {
    "limit": 100,
    "properties": ",".join([
        "firstname", "lastname", "email", "phone", "mobilephone",
        "jobtitle", "company", "hs_linkedin_url",
        "hs_lead_status", "lifecyclestage", "personal_contact",
        "industry", "city", "state", "website"
    ])
}

print("═" * 60)
print("📥 HUBSPOT FILTERED IMPORT")
print("═" * 60)
print(f"Excluding lead statuses: {EXCLUDED_LEAD_STATUSES}")
print(f"Excluding lifecycle stages: {EXCLUDED_LIFECYCLE_STAGES}")
print(f"Require email: {REQUIRE_EMAIL}")
print(f"Require company: {REQUIRE_COMPANY}")
print(f"Require phone: {REQUIRE_PHONE}")
print(f"Exclude personal contacts: {EXCLUDE_PERSONAL_CONTACTS}")
print("═" * 60)

all_contacts = []
after = None
page = 1

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
    
    print(f"   Page {page}: fetched {len(contacts)}, total {len(all_contacts)}")
    
    paging = data.get('paging', {}).get('next', {})
    after = paging.get('after')
    page += 1
    
    if not after:
        break

print(f"\n✅ Total fetched from HubSpot: {len(all_contacts)}")

# ═══════════════════════════════════════════════════════════════
# FILTER AND IMPORT
# ═══════════════════════════════════════════════════════════════

con = sqlite3.connect(DB)
cur = con.cursor()

imported = 0
updated = 0
filtered_reasons = {
    'no_email': 0,
    'no_company': 0,
    'no_phone': 0,
    'excluded_lead_status': 0,
    'excluded_lifecycle': 0,
    'personal_contact': 0,
    'already_exists': 0
}

for c in all_contacts:
    if MAX_IMPORTS and imported >= MAX_IMPORTS:
        print(f"\n🛑 Hit import limit of {MAX_IMPORTS}")
        break
    
    props = c.get('properties', {})
    hubspot_id = c.get('id')
    
    # Safe getter
    def safe_get(key):
        val = props.get(key)
        return str(val).strip().lower() if val else ''
    
    def safe_get_raw(key):
        val = props.get(key)
        return str(val).strip() if val else ''
    
    email = safe_get_raw('email')
    company = safe_get_raw('company')
    phone = safe_get_raw('phone') or safe_get_raw('mobilephone')
    lead_status = safe_get('hs_lead_status')
    lifecycle_stage = safe_get('lifecyclestage')
    personal_contact = safe_get('personal_contact')
    
    first = safe_get_raw('firstname')
    last = safe_get_raw('lastname')
    name = f"{first} {last}".strip()
    if not name and email:
        name = email.split('@')[0]
    if not name:
        name = f"HubSpot-{hubspot_id}"
    
    # ─────────────────────────────────────────────────────────
    # APPLY FILTERS
    # ─────────────────────────────────────────────────────────
    
    if REQUIRE_EMAIL and not email:
        filtered_reasons['no_email'] += 1
        continue
    
    if REQUIRE_COMPANY and not company:
        filtered_reasons['no_company'] += 1
        continue
    
    if REQUIRE_PHONE and not phone:
        filtered_reasons['no_phone'] += 1
        continue
    
    if lead_status in EXCLUDED_LEAD_STATUSES:
        filtered_reasons['excluded_lead_status'] += 1
        continue
    
    if lifecycle_stage in EXCLUDED_LIFECYCLE_STAGES:
        filtered_reasons['excluded_lifecycle'] += 1
        continue
    
    if EXCLUDE_PERSONAL_CONTACTS and personal_contact == 'true':
        filtered_reasons['personal_contact'] += 1
        continue
    
    # ─────────────────────────────────────────────────────────
    # CHECK FOR EXISTING
    # ─────────────────────────────────────────────────────────
    
    cur.execute("SELECT id FROM contacts WHERE email = ? OR crm_id = ?", (email, hubspot_id))
    existing = cur.fetchone()
    
    if existing:
        # Update existing
        cur.execute("""
            UPDATE contacts SET
                name = COALESCE(NULLIF(?, ''), name),
                phone = COALESCE(NULLIF(?, ''), phone),
                phone_mobile = COALESCE(NULLIF(?, ''), phone_mobile),
                title = COALESCE(NULLIF(?, ''), title),
                company = COALESCE(NULLIF(?, ''), company),
                linkedin_url = COALESCE(NULLIF(?, ''), linkedin_url),
                import_source = 'hubspot',
                crm_id = ?,
                last_crm_sync = ?,
                updated_at = ?
            WHERE email = ? OR crm_id = ?
        """, (
            name,
            safe_get_raw('phone'),
            safe_get_raw('mobilephone'),
            safe_get_raw('jobtitle'),
            company,
            safe_get_raw('hs_linkedin_url'),
            hubspot_id,
            datetime.now().isoformat(),
            datetime.now().isoformat(),
            email,
            hubspot_id
        ))
        updated += 1
    else:
        # Insert new
        cur.execute("""
            INSERT INTO contacts (
                name, first_name, last_name, email, phone, phone_mobile,
                title, company, linkedin_url, industry,
                company_hq_city, company_hq_state, company_website,
                import_source, crm_id, last_crm_sync,
                enrichment_status, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'hubspot', ?, ?, 'pending', ?, ?)
        """, (
            name,
            first,
            last,
            email,
            safe_get_raw('phone'),
            safe_get_raw('mobilephone'),
            safe_get_raw('jobtitle'),
            company,
            safe_get_raw('hs_linkedin_url'),
            safe_get_raw('industry'),
            safe_get_raw('city'),
            safe_get_raw('state'),
            safe_get_raw('website'),
            hubspot_id,
            datetime.now().isoformat(),
            datetime.now().isoformat(),
            datetime.now().isoformat()
        ))
        imported += 1

con.commit()
con.close()

# ═══════════════════════════════════════════════════════════════
# SUMMARY
# ═══════════════════════════════════════════════════════════════

total_filtered = sum(filtered_reasons.values()) - filtered_reasons['already_exists']

print("")
print("═" * 60)
print("✅ IMPORT COMPLETE")
print("═" * 60)
print(f"   New contacts imported:  {imported}")
print(f"   Existing updated:       {updated}")
print(f"   Total filtered out:     {total_filtered}")
print("")
print("   Filter breakdown:")
print(f"      No email:            {filtered_reasons['no_email']}")
print(f"      No company:          {filtered_reasons['no_company']}")
print(f"      No phone:            {filtered_reasons['no_phone']}")
print(f"      Excluded lead status:{filtered_reasons['excluded_lead_status']}")
print(f"      Excluded lifecycle:  {filtered_reasons['excluded_lifecycle']}")
print(f"      Personal contact:    {filtered_reasons['personal_contact']}")
print("═" * 60)
