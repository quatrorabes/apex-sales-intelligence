"""
One-time migration: Re-parse existing enrichments
Run this AFTER deploying new code to add sections to existing contacts
"""
import sqlite3
import json
from services.enrichment_parser import parse_enrichment

def migrate_enrichments():
    """Re-parse all existing enrichments and add sections"""
    conn = sqlite3.connect('apex.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Find all enriched contacts
    cursor.execute("""
        SELECT id, first_name, last_name, enrichment 
        FROM contacts 
        WHERE enrichment IS NOT NULL
    """)
    
    contacts = cursor.fetchall()
    print(f"\n{'='*80}")
    print(f"Found {len(contacts)} enriched contacts")
    print(f"{'='*80}\n")
    
    updated = 0
    skipped = 0
    
    for contact in contacts:
        contact_id = contact["id"]
        name = f"{contact['first_name']} {contact['last_name']}"
        enrichment = json.loads(contact["enrichment"])
        
        # Skip if already has sections (version 2.0)
        if enrichment.get("version") == "2.0" and enrichment.get("sections"):
            print(f"  ✓ {name} - already v2.0")
            skipped += 1
            continue
        
        # Parse raw_profile
        raw_profile = enrichment.get("raw_profile", "")
        if not raw_profile:
            print(f"  ✗ {name} - no raw_profile")
            skipped += 1
            continue
        
        parsed = parse_enrichment(raw_profile)
        
        # Update enrichment with sections
        enrichment["version"] = "2.0"
        enrichment["sections"] = parsed["sections"]
        enrichment["metadata"] = parsed["metadata"]
        
        cursor.execute("""
            UPDATE contacts 
            SET enrichment = ? 
            WHERE id = ?
        """, (json.dumps(enrichment), contact_id))
        
        updated += 1
        print(f"  ✓ {name} - parsed {parsed['metadata']['total_sections']} sections ({parsed['metadata']['format_detected']})")
    
    conn.commit()
    conn.close()
    
    print(f"\n{'='*80}")
    print(f"✅ Migration complete:")
    print(f"   Updated: {updated}")
    print(f"   Skipped: {skipped}")
    print(f"   Total:   {len(contacts)}")
    print(f"{'='*80}\n")

if __name__ == "__main__":
    migrate_enrichments()
