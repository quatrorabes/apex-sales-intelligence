#!/usr/bin/env python3
"""
Migrate apex.db (SQLite) to Railway PostgreSQL
Preserves all contacts and enrichment data
"""
import sqlite3
import psycopg2
import os
import json
from datetime import datetime

# Railway PostgreSQL connection
DATABASE_URL = os.getenv('DATABASE_URL')  # Get from Railway dashboard
if not DATABASE_URL:
    print("❌ Set DATABASE_URL environment variable")
    exit(1)

# Connect to both databases
sqlite_conn = sqlite3.connect('apex.db')
sqlite_conn.row_factory = sqlite3.Row
pg_conn = psycopg2.connect(DATABASE_URL)

sqlite_cur = sqlite_conn.cursor()
pg_cur = pg_conn.cursor()

# Create contacts table in PostgreSQL (matches schema)
pg_cur.execute("""
    DROP TABLE IF EXISTS contacts CASCADE;
    CREATE TABLE contacts (
        id TEXT PRIMARY KEY,
        hubspot_id TEXT UNIQUE,
        salesforce_id TEXT UNIQUE,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        email TEXT,
        phone TEXT,
        title TEXT,
        company TEXT,
        industry TEXT,
        linkedin_url TEXT,
        enrichment JSONB,
        enrichment_status TEXT DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT NOW(),
        updated_at TIMESTAMP DEFAULT NOW(),
        enriched_at TIMESTAMP
    );
    
    CREATE INDEX idx_contacts_hubspot ON contacts(hubspot_id);
    CREATE INDEX idx_contacts_email ON contacts(email);
    CREATE INDEX idx_contacts_enrichment_status ON contacts(enrichment_status);
""")

# Copy all contacts
sqlite_cur.execute("SELECT * FROM contacts")
columns = [desc[0] for desc in sqlite_cur.description]
migrated = 0

for row in sqlite_cur.fetchall():
    row_dict = dict(zip(columns, row))
    
    # Convert enrichment to JSON if string
    enrichment = row_dict.get('enrichment')
    if isinstance(enrichment, str):
        try:
            enrichment = json.loads(enrichment)
        except:
            enrichment = None
    
    pg_cur.execute("""
        INSERT INTO contacts (
            id, hubspot_id, first_name, last_name, email, phone,
            title, company, industry, linkedin_url, enrichment,
            enrichment_status, created_at, updated_at, enriched_at
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO UPDATE SET
            updated_at = EXCLUDED.updated_at
    """, (
        row_dict.get('id'),
        row_dict.get('hubspot_id'),
        row_dict.get('first_name') or row_dict.get('firstname'),
        row_dict.get('last_name') or row_dict.get('lastname'),
        row_dict.get('email'),
        row_dict.get('phone'),
        row_dict.get('title'),
        row_dict.get('company'),
        row_dict.get('industry'),
        row_dict.get('linkedin_url'),
        json.dumps(enrichment) if enrichment else None,
        row_dict.get('enrichment_status', 'pending'),
        row_dict.get('created_at'),
        row_dict.get('updated_at'),
        row_dict.get('enriched_at')
    ))
    migrated += 1

pg_conn.commit()
print(f"✅ Migrated {migrated} contacts to PostgreSQL")

# Verify
pg_cur.execute("SELECT COUNT(*) FROM contacts")
total = pg_cur.fetchone()[0]
print(f"✅ Total contacts in PostgreSQL: {total}")

pg_cur.execute("SELECT COUNT(*) FROM contacts WHERE enrichment IS NOT NULL")
enriched = pg_cur.fetchone()[0]
print(f"✅ Enriched contacts: {enriched}")

sqlite_conn.close()
pg_conn.close()
