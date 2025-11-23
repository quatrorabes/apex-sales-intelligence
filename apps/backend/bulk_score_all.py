#!/usr/bin/env python3
"""
Bulk Score All Contacts - Populate Dashboard with Data
This will score all 104 contacts in your database
"""

import sqlite3
import sys
import os

# Add intelligence path
sys.path.insert(0, os.path.dirname(__file__))

from intelligence.engines.scoring.scoring_orchestrator import ScoringOrchestrator

DATABASE = "apex.db"

def bulk_score_all_contacts():
    """Score all contacts in the database"""
    
    print("🎯 APEX Bulk Scoring - Processing All Contacts")
    print("=" * 70)
    
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get all contact IDs
    cursor.execute("SELECT id, name FROM contacts ORDER BY id")
    contacts = cursor.fetchall()
    
    total = len(contacts)
    print(f"\n📊 Found {total} contacts to score\n")
    
    if total == 0:
        print("❌ No contacts found in database")
        return
    
    # Initialize orchestrator
    orchestrator = ScoringOrchestrator(conn)
    
    # Score each contact
    success_count = 0
    error_count = 0
    
    for idx, contact in enumerate(contacts, 1):
        contact_id = contact['id']
        name = contact['name'] or f"Contact {contact_id}"
        
        try:
            print(f"[{idx}/{total}] Scoring: {name} (ID: {contact_id})...", end=" ")
            result = orchestrator.score_contact(contact_id, trigger='bulk')
            
            if 'error' in result:
                print(f"❌ {result['error']}")
                error_count += 1
            else:
                print(f"✅ Priority: {result.get('priority_score', 0):.1f}")
                success_count += 1
        except Exception as e:
            print(f"❌ Error: {e}")
            error_count += 1
    
    conn.close()
    
    print("\n" + "=" * 70)
    print(f"✅ Scoring Complete!")
    print(f"   - Successfully scored: {success_count}")
    print(f"   - Errors: {error_count}")
    print(f"   - Total processed: {total}")
    print("=" * 70)
    print("\n💡 Refresh your dashboard to see the results!")

if __name__ == "__main__":
    bulk_score_all_contacts()
