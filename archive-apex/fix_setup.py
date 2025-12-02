#!/usr/bin/env python3
"""
APEX Setup Fixer - Fixes database path, creates schema, and updates configuration
"""

import os
import sys
import sqlite3
import shutil
from pathlib import Path

# Define paths
PROJECT_ROOT = Path(__file__).parent.absolute()
API_FILE = PROJECT_ROOT / "apex-api" / "api.py"
DATABASE_PATH = PROJECT_ROOT / "apex.db"
ENV_PATH = PROJECT_ROOT / "apps" / "backend" / ".env"

print("=" * 70)
print("🔧 APEX SETUP FIXER")
print("=" * 70)

# Step 1: Backup existing database if it exists
if DATABASE_PATH.exists():
    backup_path = PROJECT_ROOT / f"apex.db.backup_{DATABASE_PATH.stat().st_mtime:.0f}"
    print(f"📦 Backing up existing database to {backup_path.name}")
    shutil.copy2(DATABASE_PATH, backup_path)
    DATABASE_PATH.unlink()  # Remove old database

# Step 2: Create new database with proper schema
print("📊 Creating fresh database with complete schema...")
conn = sqlite3.connect(str(DATABASE_PATH))
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS contacts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        firstname TEXT,
        lastname TEXT,
        email TEXT,
        phone TEXT,
        company TEXT,
        title TEXT,
        hubspot_id TEXT UNIQUE,
        linkedin_url TEXT,
        lead_status TEXT,
        lifecycle_stage TEXT,
        enrichment_status TEXT DEFAULT 'pending',
        enrichment_data TEXT DEFAULT '{}',
        enrichment_date TEXT,
        opportunity_score REAL,
        priority_score REAL,
        mdcp_score REAL,
        rss_score REAL,
        persona_tier TEXT,
        persona_type TEXT,
        urgency_level TEXT DEFAULT 'LOW',
        recommended_action TEXT,
        enriched INTEGER DEFAULT 0,
        last_scored TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')
conn.commit()
conn.close()
print("✅ Database created successfully!")

# Step 3: Update api.py with correct database path
print("📝 Updating api.py with correct database path...")
if API_FILE.exists():
    with open(API_FILE, 'r') as f:
        content = f.read()
    
    # Replace various possible database paths
    replacements = [
        ("DATABASE = 'apex.db'", f"DATABASE = '{DATABASE_PATH}'"),
        ('DATABASE = "apex.db"', f'DATABASE = "{DATABASE_PATH}"'),
        ("DATABASE = '/Users/chrisrabenold/projects/apex/apps/backend/apex.db'", f"DATABASE = '{DATABASE_PATH}'"),
        ('DATABASE = "/Users/chrisrabenold/projects/apex/apps/backend/apex.db"', f'DATABASE = "{DATABASE_PATH}"'),
        ("DATABASE = os.path.join(BACKEND_PATH, 'apex.db')", f"DATABASE = '{DATABASE_PATH}'"),
    ]
    
    for old, new in replacements:
        if old in content:
            content = content.replace(old, new)
            print(f"   ✅ Updated: {old[:30]}... → {new[:30]}...")
    
    # Save updated file
    with open(API_FILE, 'w') as f:
        f.write(content)
    print("✅ api.py updated!")
else:
    print("⚠️  api.py not found at expected location")

# Step 4: Update .env path loading in api.py
print("📝 Updating .env loading path...")
if API_FILE.exists():
    with open(API_FILE, 'r') as f:
        lines = f.readlines()
    
    # Find load_dotenv line and update it
    updated = False
    for i, line in enumerate(lines):
        if 'load_dotenv()' in line and 'load_dotenv(ENV_PATH)' not in line:
            # Add ENV_PATH definition before load_dotenv
            lines[i] = f"ENV_PATH = '{ENV_PATH}'\nload_dotenv(ENV_PATH)\n"
            updated = True
            print("   ✅ Updated load_dotenv to use specific path")
            break
    
    if updated:
        with open(API_FILE, 'w') as f:
            f.writelines(lines)

# Step 5: Verify .env file exists and has required keys
print("🔑 Checking environment variables...")
if ENV_PATH.exists():
    with open(ENV_PATH, 'r') as f:
        env_content = f.read()
    
    required_keys = ['HUBSPOT_ACCESS_TOKEN', 'PERPLEXITY_API_KEY', 'OPENAI_API_KEY']
    for key in required_keys:
        if key in env_content:
            # Get first few chars of the value for display
            line = [l for l in env_content.split('\n') if l.startswith(key)][0]
            value = line.split('=')[1].strip()[:20] if '=' in line else 'NOT SET'
            print(f"   ✅ {key}: {value}...")
        else:
            print(f"   ⚠️  {key}: NOT FOUND")
else:
    print(f"   ❌ .env file not found at {ENV_PATH}")

# Step 6: Create a test script
print("\n📝 Creating test script...")
test_script = PROJECT_ROOT / "test_connection.py"
test_content = f'''#!/usr/bin/env python3
import sqlite3
import os
import sys
sys.path.insert(0, '{PROJECT_ROOT / "apps" / "backend"}')
from dotenv import load_dotenv

# Load environment
ENV_PATH = '{ENV_PATH}'
load_dotenv(ENV_PATH)

# Test database
db_path = '{DATABASE_PATH}'
print(f"Testing database at: {{db_path}}")
print(f"Database exists: {{os.path.exists(db_path)}}")

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
print("\\n🔑 Environment Variables:")
print(f"HUBSPOT_ACCESS_TOKEN: {{os.getenv('HUBSPOT_ACCESS_TOKEN', 'NOT SET')[:20]}}...")
print(f"PERPLEXITY_API_KEY: {{os.getenv('PERPLEXITY_API_KEY', 'NOT SET')[:20]}}...")
'''

with open(test_script, 'w') as f:
    f.write(test_content)
test_script.chmod(0o755)
print(f"✅ Created test script: {test_script}")

# Final summary
print("\n" + "=" * 70)
print("✅ SETUP COMPLETE!")
print("=" * 70)
print(f"Database: {DATABASE_PATH}")
print(f"Environment: {ENV_PATH}")
print(f"API File: {API_FILE}")
print("\n🚀 Next steps:")
print("1. Run the test script: python test_connection.py")
print("2. Start the API server: cd apex-api && python api.py")
print("3. Try importing from HubSpot")
print("=" * 70)
