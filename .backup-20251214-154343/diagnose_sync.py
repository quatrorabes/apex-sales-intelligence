#!/usr/bin/env python3
"""
Diagnose why contacts aren't inserting
"""

import os
import sqlite3
from dotenv import load_dotenv

load_dotenv()

db = sqlite3.connect('./apex.db')
db.row_factory = sqlite3.Row
cursor = db.cursor()

print("=" * 80)
print("🔍 DATABASE DIAGNOSTICS")
print("=" * 80)

# Check if table exists
try:
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='contacts';")
    table_exists = cursor.fetchone()
    
    if table_exists:
        print("✅ Table 'contacts' exists")
    else:
        print("❌ Table 'contacts' does NOT exist!")
        print("\nYou need to create the table first!")
        db.close()
        exit(1)
except Exception as e:
    print(f"❌ Error checking table: {e}")
    db.close()
    exit(1)

# Get table schema
print("\n📋 TABLE SCHEMA:")
cursor.execute("PRAGMA table_info(contacts);")
columns = cursor.fetchall()
for col in columns:
    print(f"   {col['name']:20s} {col['type']:10s} {'NOT NULL' if col['notnull'] else ''} {'PK' if col['pk'] else ''}")

# Check current count
cursor.execute("SELECT COUNT(*) as count FROM contacts;")
count = cursor.fetchone()['count']
print(f"\n📊 Current contacts in DB: {count}")

# Check if we can insert a test record
print("\n🧪 TEST INSERT:")
test_id = "TEST_12345"

try:
    # Try to insert
    cursor.execute("""
        INSERT INTO contacts (id, name, email, company, job_title, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, datetime('now'), datetime('now'))
    """, (test_id, "Test Person", "test@example.com", "Test Corp", "CEO"))
    
    db.commit()
    print("✅ Test insert SUCCESS")
    
    # Clean up
    cursor.execute("DELETE FROM contacts WHERE id = ?", (test_id,))
    db.commit()
    print("✅ Test delete SUCCESS")
    
except Exception as e:
    print(f"❌ Test insert FAILED: {e}")
    db.rollback()

# Check for any existing HubSpot contacts
print("\n🔍 Checking for HubSpot contacts:")
cursor.execute("SELECT COUNT(*) as count FROM contacts WHERE id LIKE '%hubspot%' OR id LIKE '%hs_%';")
hs_count = cursor.fetchone()['count']
print(f"   Found: {hs_count} contacts with HubSpot-like IDs")

# Show sample if any exist
if hs_count > 0:
    cursor.execute("SELECT id, name, email, company, linkedin_url FROM contacts LIMIT 5;")
    print("\n📋 Sample contacts:")
    for row in cursor.fetchall():
        li = "✓" if row['linkedin_url'] else "✗"
        print(f"   [{li}] {row['name']} @ {row['company']} (ID: {row['id']})")

db.close()

print("\n" + "=" * 80)
print("💡 DIAGNOSIS:")
print("   If test insert worked but sync didn't, the issue is likely:")
print("   1. ID conflict (HubSpot IDs might be integers but schema expects TEXT)")
print("   2. Field name mismatch")
print("   3. Silent exception being caught")
print("=" * 80)
