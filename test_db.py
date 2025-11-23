#!/usr/bin/env python3
import sqlite3
import os

# Test the database path
db_path = '/Users/chrisrabenold/projects/apex/apex.db'

print(f"Testing database at: {db_path}")
print(f"File exists: {os.path.exists(db_path)}")

if os.path.exists(db_path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if contacts table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='contacts'")
        if cursor.fetchone():
            print("✅ Contacts table exists")
            
            # Check columns
            cursor.execute("PRAGMA table_info(contacts)")
            columns = [col[1] for col in cursor.fetchall()]
            print(f"✅ Columns: {', '.join(columns[:5])}...")
            
            # Check required columns for HubSpot import
            required = ['phone', 'firstname', 'lastname', 'lead_status', 'lifecycle_stage', 'enrichment_status']
            missing = [col for col in required if col not in columns]
            if missing:
                print(f"❌ Missing columns: {missing}")
            else:
                print("✅ All required columns present")
                
        else:
            print("❌ Contacts table not found")
        
        conn.close()
    except Exception as e:
        print(f"❌ Database error: {e}")
else:
    print("❌ Database file not found!")
