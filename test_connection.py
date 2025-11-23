#!/usr/bin/env python3
import sqlite3
import os
import sys
sys.path.insert(0, '/Users/chrisrabenold/projects/apex/apps/backend')
from dotenv import load_dotenv

# Load environment
ENV_PATH = '/Users/chrisrabenold/projects/apex/apps/backend/.env'
load_dotenv(ENV_PATH)

# Test database
db_path = '/Users/chrisrabenold/projects/apex/apex.db'
print(f"Testing database at: {db_path}")
print(f"Database exists: {os.path.exists(db_path)}")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='contacts'")
schema = cursor.fetchone()
if schema:
    print("✅ Contacts table exists")
    print("Schema:", schema[0])
else:
    print("❌ Contacts table not found")
conn.close()

# Test environment variables
print("\n🔑 Environment Variables:")
print(f"HUBSPOT_ACCESS_TOKEN: {os.getenv('HUBSPOT_ACCESS_TOKEN', 'NOT SET')[:20]}...")
print(f"PERPLEXITY_API_KEY: {os.getenv('PERPLEXITY_API_KEY', 'NOT SET')[:20]}...")
