"""
HubSpot → PostgreSQL Sync (WITH PROGRESS & BATCH COMMITS)
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import ssl
ssl._create_default_https_context = ssl._create_unverified_context

import psycopg2
from psycopg2.extras import RealDictCursor
from hubspot import HubSpot
from datetime import datetime
import uuid

HUBSPOT_ACCESS_TOKEN = os.getenv('HUBSPOT_ACCESS_TOKEN')
DATABASE_URL = os.getenv('DATABASE_URL')

if not HUBSPOT_ACCESS_TOKEN or not DATABASE_URL:
    print("❌ Set HUBSPOT_ACCESS_TOKEN and DATABASE_URL")
    sys.exit(1)

hubspot_client = HubSpot(access_token=HUBSPOT_ACCESS_TOKEN)

def is_qualified_contact(props):
    if not all([props.get('firstname'), props.get('lastname'), 
                props.get('email'), props.get('company')]):
        return False, "Missing required fields"
    
    lifecycle = (props.get('lifecyclestage') or '').lower()
    if lifecycle == 'unqualified':
        return False, f"Lifecycle: {lifecycle}"
    
    lead_status = (props.get('hs_lead_status') or '').lower()
    excluded = ['unqualified', 'unsubscribe', 'do not contact']
    if any(s in lead_status for s in excluded):
        return False, f"Lead status: {lead_status}"
    
    return True, "Qualified"

def sync_batch(contacts_batch, conn):
    """Save a batch of contacts with transaction"""
    cur = conn.cursor()
    saved = 0
    updated = 0
    skipped = 0
    
    for contact in contacts_batch:
        props = contact.properties
        hubspot_id = contact.id
        
        is_qual, reason = is_qualified_contact(props)
        if not is_qual:
            skipped += 1
            continue
        
        try:
            cur.execute(
                "SELECT id FROM contacts WHERE hubspot_id = %s",
                (hubspot_id,)
            )
            existing = cur.fetchone()
            
            if existing:
                cur.execute("""
                    UPDATE contacts SET
                        first_name=%s, last_name=%s, email=%s, phone=%s,
                        company=%s, title=%s, industry=%s, linkedin_url=%s,
                        updated_at=%s
                    WHERE hubspot_id=%s
                """, (
                    props.get("firstname"), props.get("lastname"),
                    props.get("email"), props.get("phone"),
                    props.get("company"), props.get("jobtitle"),
                    props.get("industry"), props.get("linkedin_url"),
                    datetime.now().isoformat(), hubspot_id
                ))
                updated += 1
            else:
                cur.execute("""
                    INSERT INTO contacts (
                        id, hubspot_id, first_name, last_name, email, phone,
                        company, title, industry, linkedin_url,
                        created_at, updated_at, enrichment_status
                    ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """, (
                    str(uuid.uuid4()), hubspot_id,
                    props.get("firstname"), props.get("lastname"),
                    props.get("email"), props.get("phone"),
                    props.get("company"), props.get("jobtitle"),
                    props.get("industry"), props.get("linkedin_url"),
                    datetime.now().isoformat(),
                    datetime.now().isoformat(),
                    "pending"
                ))
                saved += 1
        except Exception as e:
            print(f"\n❌ Error: {e}")
            skipped += 1
    
    conn.commit()
    return saved, updated, skipped

def sync_contacts():
    print("🚀 Starting HubSpot → PostgreSQL sync (BATCH MODE)\n")
    
    properties = [
        "firstname", "lastname", "email", "phone", "company",
        "jobtitle", "industry", "linkedin_url", "hs_object_id",
        "lifecyclestage", "hs_lead_status"
    ]
    
    conn = psycopg2.connect(DATABASE_URL)
    
    total_saved = 0
    total_updated = 0
    total_skipped = 0
    batch_num = 0
    after = None
    
    while batch_num < 10:  # Max 1000 contacts (10 batches)
        try:
            response = hubspot_client.crm.contacts.basic_api.get_page(
                limit=100, after=after, properties=properties, archived=False
            )
            
            batch_num += 1
            contacts_batch = response.results
            
            # Process this batch
            saved, updated, skipped = sync_batch(contacts_batch, conn)
            total_saved += saved
            total_updated += updated
            total_skipped += skipped
            
            print(f"Batch {batch_num}: +{saved} new, ~{updated} updated, x{skipped} skipped (Total: {total_saved+total_updated})")
            
            if not response.paging:
                print("\n✅ Reached end of contacts")
                break
            after = response.paging.next.after
            
        except Exception as e:
            print(f"\n❌ Batch error: {e}")
            break
    
    conn.close()
    
    print(f"\n📊 FINAL RESULTS:")
    print(f"  ✅ Saved: {total_saved}")
    print(f"  ✅ Updated: {total_updated}")
    print(f"  ⚠️  Skipped: {total_skipped}")
    print(f"  🎉 Total qualified: {total_saved + total_updated}")

if __name__ == "__main__":
    sync_contacts()
