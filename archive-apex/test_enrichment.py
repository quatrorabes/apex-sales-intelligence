#!/usr/bin/env python3

import sys
import sqlite3
from enhanced_enrichment import EnhancedEnrichment

# Get contact from database
contact_id = int(sys.argv[1]) if len(sys.argv) > 1 else 48  # Default to Andy (48)

conn = sqlite3.connect('apex.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute("SELECT * FROM contacts WHERE id = ?", (contact_id,))
row = cursor.fetchone()
conn.close()

if not row:
    print(f"❌ Contact {contact_id} not found")
    sys.exit(1)

contact = dict(row)

print(f"\n🔍 Testing Enhanced Enrichment")
print(f"Contact: {contact['name']} at {contact['company']}")
print(f"ID: {contact_id}\n")

# Run enrichment
enricher = EnhancedEnrichment()
result = enricher.enrich_contact(contact)

if result:
    print(f"\n✅ SUCCESS!")
    print(f"📄 Saved to: {result['filename']}")
    print(f"📊 Size: {result['character_count']:,} chars")
else:
    print("\n❌ Enrichment failed")
