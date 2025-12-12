#!/usr/bin/env python3
"""
One-time migration: add personaconfidence column to contacts in PostgreSQL.

Relies on DATABASE_URL (same as Apex).
"""

import os
import psycopg2

db_url = os.getenv("DATABASE_URL")
if not db_url:
    raise SystemExit("DATABASE_URL is not set")

conn = psycopg2.connect(db_url)
cur = conn.cursor()

for col in ("personaconfidence",):
    try:
        cur.execute(f"ALTER TABLE contacts ADD COLUMN {col} REAL;")
        print(f"✅ Added column: {col}")
    except Exception as e:
        # Likely: column already exists
        print(f"⚠️ Skipping {col}: {e}")

conn.commit()
conn.close()
print("✅ Migration complete")
