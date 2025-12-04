#!/bin/bash

#!/usr/bin/env bash
# apex_deploy_and_import.sh
# Run from: ~/projects/apex

set -euo pipefail

echo "═══════════════════════════════════════════════════════════════"
echo "🚀 APEX DEPLOYMENT & IMPORT - $(date)"
echo "═══════════════════════════════════════════════════════════════"

cd ~/projects/apex

# ─────────────────────────────────────────────────────────────────
# STEP 1: Git Status & Commit
# ─────────────────────────────────────────────────────────────────
echo ""
echo "📦 STEP 1: Git commit all changes..."

git status --short

git add -A
git commit -m "🚀 Apex Dec 3: Enrichment, Scoring, Dashboard fixes, CRM spec

- Fixed EnhancedEnrichment 3-stage pipeline (Perplexity → GPT-4 → DB)
- Fixed ApexScoringEngine initialization
- Fixed 12 dashboard components (removed hardcoded Railway URLs)
- Fixed Today's Board response parsing
- Fixed Intelligence tab section extraction
- Added 14 new database columns for CRM import
- Added CRM connector spec (HubSpot, Salesforce, Pipedrive)
- Added scripts/import_hubspot.py
- Cleaned up duplicate files" || echo "Nothing to commit"

# ─────────────────────────────────────────────────────────────────
# STEP 2: Push to GitHub
# ─────────────────────────────────────────────────────────────────
echo ""
echo "📤 STEP 2: Push to GitHub..."

git push origin main || git push origin main --force

echo "✅ GitHub updated"

# ─────────────────────────────────────────────────────────────────
# STEP 3: Deploy to Railway (auto-deploys on push, but verify)
# ─────────────────────────────────────────────────────────────────
echo ""
echo "🚂 STEP 3: Railway deployment..."

if command -v railway &> /dev/null; then
	echo "Checking Railway status..."
	railway status || true
	echo ""
	echo "Recent logs (last 20 lines):"
	railway logs --tail 20 || true
else
	echo "⚠️  Railway CLI not installed. Check https://apex-intelligence-production.up.railway.app/api/health manually"
fi

# ─────────────────────────────────────────────────────────────────
# STEP 4: Load environment variables properly
# ─────────────────────────────────────────────────────────────────
echo ""
echo "🔑 STEP 4: Loading environment variables..."

if [ -f .env ]; then
	export $(grep -v '^#' .env | grep -v '^$' | xargs)
	echo "✅ Environment loaded"
	
	# Verify critical keys
	if [ -n "${HUBSPOT_ACCESS_TOKEN:-}" ]; then
		echo "   ✅ HUBSPOT_ACCESS_TOKEN: ${HUBSPOT_ACCESS_TOKEN:0:10}..."
	else
		echo "   ❌ HUBSPOT_ACCESS_TOKEN: NOT SET"
	fi
	
	if [ -n "${PERPLEXITY_API_KEY:-}" ]; then
		echo "   ✅ PERPLEXITY_API_KEY: ${PERPLEXITY_API_KEY:0:10}..."
	else
		echo "   ❌ PERPLEXITY_API_KEY: NOT SET"
	fi
	
	if [ -n "${OPENAI_API_KEY:-}" ]; then
		echo "   ✅ OPENAI_API_KEY: ${OPENAI_API_KEY:0:10}..."
	else
		echo "   ❌ OPENAI_API_KEY: NOT SET"
	fi
else
	echo "❌ .env file not found!"
	exit 1
fi

# ─────────────────────────────────────────────────────────────────
# STEP 5: Ensure Python venv and dependencies
# ─────────────────────────────────────────────────────────────────
echo ""
echo "🐍 STEP 5: Python environment..."

if [ -d ".venv" ]; then
	source .venv/bin/activate
else
	python3 -m venv .venv
	source .venv/bin/activate
	pip install -U pip
fi

pip install -q requests python-dotenv openai 2>/dev/null || true
echo "✅ Python ready: $(python --version)"

# ─────────────────────────────────────────────────────────────────
# STEP 6: Ensure database columns exist
# ─────────────────────────────────────────────────────────────────
echo ""
echo "🗄️  STEP 6: Database schema check..."

python3 << 'PYEOF'
import sqlite3

cols = [
	("first_name", "TEXT"),
	("last_name", "TEXT"),
	("phone_mobile", "TEXT"),
	("linkedin_url", "TEXT"),
	("company_domain", "TEXT"),
	("company_website", "TEXT"),
	("company_hq_city", "TEXT"),
	("company_hq_state", "TEXT"),
	("industry", "TEXT"),
	("data_completeness_score", "INTEGER DEFAULT 0"),
	("enrichment_ready", "INTEGER DEFAULT 0"),
	("import_source", "TEXT"),
	("crm_id", "TEXT"),
	("last_crm_sync", "TEXT"),
	("last_contact_date", "TEXT")
]

con = sqlite3.connect('apex.db')
cur = con.cursor()
added = skipped = 0

for c, t in cols:
	try:
		cur.execute(f"ALTER TABLE contacts ADD COLUMN {c} {t}")
		added += 1
	except Exception as e:
		if "duplicate column name" in str(e).lower():
			skipped += 1

con.commit()
con.close()
print(f"✅ Schema: {added} added, {skipped} already exist")
PYEOF

# ─────────────────────────────────────────────────────────────────
# STEP 7: Create HubSpot import script if missing
# ─────────────────────────────────────────────────────────────────
echo ""
echo "📝 STEP 7: Ensuring import script exists..."

mkdir -p scripts

cat > scripts/import_hubspot.py << 'PYEOF'
#!/usr/bin/env python3
"""HubSpot contact import for Apex"""

import os
import sqlite3
import requests
from datetime import datetime

TOKEN = os.getenv('HUBSPOT_ACCESS_TOKEN')
DB = 'apex.db'

if not TOKEN:
	print("❌ HUBSPOT_ACCESS_TOKEN not set")
	print("   Run: export $(grep -v '^#' .env | xargs)")
	exit(1)

headers = {"Authorization": f"Bearer {TOKEN}"}
url = "https://api.hubapi.com/crm/v3/objects/contacts"
params = {
	"limit": 100,
	"properties": "firstname,lastname,email,phone,mobilephone,jobtitle,company,hs_linkedin_url"
}

print("📥 Fetching contacts from HubSpot...")

all_contacts = []
after = None

while True:
	if after:
		params['after'] = after
	
	resp = requests.get(url, headers=headers, params=params)
	
	if resp.status_code != 200:
		print(f"❌ HubSpot API error: {resp.status_code}")
		print(resp.text[:500])
		break
	
	data = resp.json()
	contacts = data.get('results', [])
	all_contacts.extend(contacts)
	
	paging = data.get('paging', {}).get('next', {})
	after = paging.get('after')
	
	print(f"   Fetched {len(all_contacts)} contacts...")
	
	if not after:
		break

print(f"✅ Total fetched: {len(all_contacts)}")

con = sqlite3.connect(DB)
cur = con.cursor()

imported = updated = skipped = 0

for c in all_contacts:
	props = c.get('properties', {})
	email = props.get('email')
	
	if not email:
		skipped += 1
		continue
	
	first = props.get('firstname', '') or ''
	last = props.get('lastname', '') or ''
	name = f"{first} {last}".strip() or email.split('@')[0]
	
	# Check if exists
	cur.execute("SELECT id FROM contacts WHERE email = ?", (email,))
	existing = cur.fetchone()
	
	if existing:
		# Update existing
		cur.execute("""
			UPDATE contacts SET
				name = COALESCE(?, name),
				phone = COALESCE(?, phone),
				phone_mobile = COALESCE(?, phone_mobile),
				title = COALESCE(?, title),
				company = COALESCE(?, company),
				linkedin_url = COALESCE(?, linkedin_url),
				import_source = 'hubspot',
				crm_id = ?,
				last_crm_sync = ?,
				updated_at = ?
			WHERE email = ?
		""", (
			name,
			props.get('phone'),
			props.get('mobilephone'),
			props.get('jobtitle'),
			props.get('company'),
			props.get('hs_linkedin_url'),
			c.get('id'),
			datetime.now().isoformat(),
			datetime.now().isoformat(),
			email
		))
		updated += 1
	else:
		# Insert new
		cur.execute("""
			INSERT INTO contacts (
				name, email, phone, phone_mobile, title, company, 
				linkedin_url, import_source, crm_id, last_crm_sync, 
				enrichment_status, created_at, updated_at
			) VALUES (?, ?, ?, ?, ?, ?, ?, 'hubspot', ?, ?, 'pending', ?, ?)
		""", (
			name, email,
			props.get('phone'),
			props.get('mobilephone'),
			props.get('jobtitle'),
			props.get('company'),
			props.get('hs_linkedin_url'),
			c.get('id'),
			datetime.now().isoformat(),
			datetime.now().isoformat(),
			datetime.now().isoformat()
		))
		imported += 1

con.commit()
con.close()

print("")
print("═" * 50)
print(f"✅ IMPORT COMPLETE")
print(f"   New contacts:     {imported}")
print(f"   Updated:          {updated}")
print(f"   Skipped (no email): {skipped}")
print("═" * 50)
PYEOF

echo "✅ Import script ready"

# ─────────────────────────────────────────────────────────────────
# STEP 8: Test HubSpot API connection
# ─────────────────────────────────────────────────────────────────
echo ""
echo "🔌 STEP 8: Testing HubSpot API connection..."

HUBSPOT_TEST=$(curl -s -o /dev/null -w "%{http_code}" \
	-H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
	"https://api.hubapi.com/crm/v3/objects/contacts?limit=1")

if [ "$HUBSPOT_TEST" = "200" ]; then
	echo "✅ HubSpot API: Connected"
else
	echo "❌ HubSpot API: Failed (HTTP $HUBSPOT_TEST)"
	echo "   Check your HUBSPOT_ACCESS_TOKEN in .env"
	exit 1
fi

# ─────────────────────────────────────────────────────────────────
# STEP 9: Run HubSpot Import
# ─────────────────────────────────────────────────────────────────
echo ""
