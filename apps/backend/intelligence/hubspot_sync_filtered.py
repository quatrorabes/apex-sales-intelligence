"""
HubSpot → PostgreSQL Contact Sync (FILTERED)
Only imports qualified leads with complete data
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import psycopg2
from psycopg2.extras import RealDictCursor
from hubspot import HubSpot
from datetime import datetime
import uuid

# Initialize HubSpot client
HUBSPOT_ACCESS_TOKEN = os.getenv('HUBSPOT_ACCESS_TOKEN')
if not HUBSPOT_ACCESS_TOKEN:
    print("❌ Set HUBSPOT_ACCESS_TOKEN environment variable")
    sys.exit(1)

hubspot_client = HubSpot(access_token=HUBSPOT_ACCESS_TOKEN)

def get_db_connection():
    """Connect to PostgreSQL on Railway"""
    DATABASE_URL = os.getenv('DATABASE_URL')
    if not DATABASE_URL:
        print("❌ Set DATABASE_URL environment variable")
        sys.exit(1)
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

def is_qualified_contact(props):
    """Check if contact meets import criteria"""
    # Must have required fields
    if not all([
        props.get('firstname'),
        props.get('lastname'),
        props.get('email'),
        props.get('company')
    ]):
        return False, "Missing required fields"
    
    # Check lifecycle stage
    lifecycle = (props.get('lifecyclestage') or '').lower()
    if lifecycle == 'unqualified':
        return False, f"Lifecycle: {lifecycle}"
    
    # Check lead status
    lead_status = (props.get('hs_lead_status') or '').lower()
    excluded_statuses = ['unqualified', 'unsubscribe', 'do not contact']
    if any(status in lead_status for status in excluded_statuses):
        return False, f"Lead status: {lead_status}"
    
    return True, "Qualified"

def sync_contacts():
    """Pull filtered contacts from HubSpot and sync to PostgreSQL"""
    print("🔄 Starting FILTERED HubSpot → PostgreSQL sync...")
    print("📋 Filters:")
    print("  ✅ Must have: company, first_name, last_name, email")
    print("  ❌ Exclude: lifecycle=unqualified")
    print("  ❌ Exclude: lead_status=unqualified/unsubscribe/do not contact")
    print()
    
    # Fetch all contacts from HubSpot
    properties = [
        "firstname", "lastname", "email", "phone", "company",
        "jobtitle", "industry", "linkedin_url", "hs_object_id",
        "lifecyclestage", "hs_lead_status"
    ]
    
    all_contacts = []
    after = None
    
    while True:
        try:
            response = hubspot_client.crm.contacts.basic_api.get_page(
                limit=200,
                after=after,
                properties=properties,
                archived=False
            )
            
            all_contacts.extend(response.results)
            print(f"  Fetched {len(response.results)} contacts (total: {len(all_contacts)})")
            
            if not response.paging:
                break
            after = response.paging.next.after
            
        except Exception as e:
            print(f"❌ Error fetching contacts: {e}")
            break
    
    print(f"✅ Retrieved {len(all_contacts)} contacts from HubSpot\n")
    
    # Filter and save to PostgreSQL
    conn = get_db_connection()
    cur = conn.cursor()
    
    saved_count = 0
    updated_count = 0
    skipped_count = 0
    skip_reasons = {}
    
    for contact in all_contacts:
        props = contact.properties
        hubspot_id = contact.id
        
        # Check if qualified
        is_qualified, reason = is_qualified_contact(props)
        if not is_qualified:
            skipped_count += 1
            skip_reasons[reason] = skip_reasons.get(reason, 0) + 1
            continue
        
        try:
            # Check if contact exists
            cur.execute(
                "SELECT id FROM contacts WHERE hubspot_id = %s",
                (hubspot_id,)
            )
            existing = cur.fetchone()
            
            if existing:
                # Update existing
                cur.execute("""
                    UPDATE contacts SET
                        first_name = %s,
                        last_name = %s,
                        email = %s,
                        phone = %s,
                        company = %s,
                        title = %s,
                        industry = %s,
                        linkedin_url = %s,
                        updated_at = %s
                    WHERE hubspot_id = %s
                """, (
                    props.get("firstname"),
                    props.get("lastname"),
                    props.get("email"),
                    props.get("phone"),
                    props.get("company"),
                    props.get("jobtitle"),
                    props.get("industry"),
                    props.get("linkedin_url"),
                    datetime.now().isoformat(),
                    hubspot_id
                ))
                updated_count += 1
            else:
                # Insert new
                contact_id = str(uuid.uuid4())
                
                cur.execute("""
                    INSERT INTO contacts (
                        id, hubspot_id, first_name, last_name, email, phone,
                        company, title, industry, linkedin_url,
                        created_at, updated_at, enrichment_status
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    contact_id,
                    hubspot_id,
                    props.get("firstname"),
                    props.get("lastname"),
                    props.get("email"),
                    props.get("phone"),
                    props.get("company"),
                    props.get("jobtitle"),
                    props.get("industry"),
                    props.get("linkedin_url"),
                    datetime.now().isoformat(),
                    datetime.now().isoformat(),
                    "pending"
                ))
                saved_count += 1
        
        except Exception as e:
            print(f"❌ Error saving contact {props.get('email')}: {e}")
            continue
    
    conn.commit()
    conn.close()
    
    print(f"\n📊 SYNC RESULTS:")
    print(f"  ✅ Saved {saved_count} new contacts")
    print(f"  ✅ Updated {updated_count} existing contacts")
    print(f"  ⚠️  Skipped {skipped_count} contacts")
    
    if skip_reasons:
        print(f"\n📋 Skip Breakdown:")
        for reason, count in skip_reasons.items():
            print(f"  - {reason}: {count}")
    
    return saved_count + updated_count

if __name__ == "__main__":
    total = sync_contacts()
    print(f"\n🎉 Sync complete: {total} qualified contacts in PostgreSQL")
