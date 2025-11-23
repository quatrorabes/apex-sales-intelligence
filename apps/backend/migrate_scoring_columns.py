#!/usr/bin/env python3
"""
Database Migration Script - Add Scoring Columns
Run this to add all MDCP/RSS scoring columns to your database
"""

import sqlite3
import os
from datetime import datetime

DATABASE = "apex.db"

def run_migration():
    """Add scoring columns to contacts table"""
    
    print("🔧 APEX Database Migration - Adding Scoring Columns")
    print("=" * 70)
    
    if not os.path.exists(DATABASE):
        print(f"❌ Database not found: {DATABASE}")
        print(f"   Current directory: {os.getcwd()}")
        return
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # List of columns to add
    columns_to_add = [
        ("mdcp_score", "REAL"),
        ("rss_score", "REAL"),
        ("priority_score", "REAL"),
        ("persona_tier", "TEXT"),
        ("persona_type", "TEXT"),
        ("persona_confidence", "REAL"),
        ("urgency_level", "TEXT"),
        ("recommended_action", "TEXT"),
        ("last_scored", "TEXT"),
        ("enrichment_status", "TEXT"),
        ("enrichment_started_at", "TEXT"),
        ("enrichment_data", "TEXT")
    ]
    
    print("\n📊 Checking existing columns...")
    cursor.execute("PRAGMA table_info(contacts)")
    existing_columns = {row[1] for row in cursor.fetchall()}
    print(f"   Found {len(existing_columns)} existing columns")
    
    print("\n➕ Adding new columns...")
    added_count = 0
    
    for column_name, column_type in columns_to_add:
        if column_name not in existing_columns:
            try:
                cursor.execute(f"ALTER TABLE contacts ADD COLUMN {column_name} {column_type}")
                print(f"   ✅ Added: {column_name} ({column_type})")
                added_count += 1
            except sqlite3.OperationalError as e:
                print(f"   ⚠️  Skipped {column_name}: {e}")
        else:
            print(f"   ⏭️  Already exists: {column_name}")
    
    conn.commit()
    
    # Create scoring_history table if it doesn't exist
    print("\n📜 Creating scoring_history table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scoring_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contact_id INTEGER NOT NULL,
            trigger TEXT,
            mdcp_score REAL,
            rss_score REAL,
            priority_score REAL,
            persona_tier TEXT,
            persona_type TEXT,
            timestamp TEXT,
            FOREIGN KEY (contact_id) REFERENCES contacts (id)
        )
    """)
    print("   ✅ scoring_history table ready")
    
    conn.commit()
    
    # Show current contact count
    cursor.execute("SELECT COUNT(*) FROM contacts")
    contact_count = cursor.fetchone()[0]
    
    print("\n" + "=" * 70)
    print(f"✅ Migration complete!")
    print(f"   - Added {added_count} new columns")
    print(f"   - Current contacts in database: {contact_count}")
    print(f"   - scoring_history table: ready")
    print("=" * 70)
    
    if contact_count > 0:
        print("\n💡 Next steps:")
        print("   1. Restart your server if it's running")
        print("   2. Score existing contacts:")
        print("      curl -X POST http://localhost:8000/api/contacts/1/score")
        print("   3. Or bulk score all contacts via API")
    else:
        print("\n💡 Your database is ready but empty.")
        print("   Import contacts via:")
        print("   - POST /api/contacts (create manually)")
        print("   - POST /api/hubspot/import (import from HubSpot)")
    
    conn.close()

if __name__ == "__main__":
    run_migration()
