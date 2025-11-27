#!/usr/bin/env python3
import os
import sqlite3
import json
from datetime import datetime

# Check Andy's data
db_path = os.path.expanduser("~/projects/apex/apex.db")
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row  # This makes it return dict-like rows
cursor = conn.cursor()

# Get Andy's info
cursor.execute("SELECT * FROM contacts WHERE id = 48")
contact = cursor.fetchone()

if contact:
    print("✅ Found Andy Bratt")
    print(f"  Name: {contact['name']}")
    print(f"  Email: {contact['email']}")
    print(f"  Phone: {contact['phone']}")
    print(f"  Company: {contact['company']}")
    print(f"  Title: {contact['title']}")
    print(f"  Enrichment Status: {contact['enrichment_status']}")
    
    # Check enrichment data
    if contact['enrichment_data']:
        data = json.loads(contact['enrichment_data'])
        print(f"  Enrichment Data Size: {len(contact['enrichment_data'])} chars")
        print(f"  Has Perplexity insights: {'perplexity_insights' in data}")
        if 'perplexity_insights' in data:
            print(f"  Insights preview: {data['perplexity_insights'][:100]}...")
    else:
        print("  ⚠️ No enrichment data!")
else:
    print("❌ Contact not found")

conn.close()

# Now check OpenAI API key
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if api_key:
    print(f"\n✅ OpenAI API Key found: {api_key[:8]}...{api_key[-4:]}")
else:
    print("\n❌ No OpenAI API Key found - this is required for content generation!")
    print("   Add to .env file: OPENAI_API_KEY=sk-...")
