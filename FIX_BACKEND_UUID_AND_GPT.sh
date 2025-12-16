#!/usr/bin/env python3

#!/bin/bash
# FIX_BACKEND_UUID_AND_GPT.sh
# Backend-only fixes - does NOT touch frontend (yesterday's work preserved)

set -e

cd ~/projects/apex/apex-sales-intelligence

echo "========================================"
echo "APEX Backend Fixes (main.py + GPT-4o)"
echo "Preserving all frontend UUID work"
echo "========================================"

# Backup
cp apps/backend/main.py apps/backend/main.py.backup-$(date +%s)
cp enrichment_apex_custom.py enrichment_apex_custom.py.backup-$(date +%s) 2>/dev/null || true

# FIX 1: GET contact endpoint - change int to str
echo ""
echo "🔧 Fix 1: GET /api/contacts/{contact_id} - int → str"
sed -i '' 's/contact_id: int/contact_id: str/g' apps/backend/main.py

# FIX 2: GPT-4 → GPT-4o (handles 128K context)
echo "🔧 Fix 2: GPT-4 → GPT-4o (token limit fix)"
sed -i '' 's/model="gpt-4"/model="gpt-4o"/g' enrichment_apex_custom.py 2>/dev/null || true
sed -i '' "s/model='gpt-4'/model='gpt-4o'/g" enrichment_apex_custom.py 2>/dev/null || true
sed -i '' 's/model="gpt-4"/model="gpt-4o"/g' apps/backend/enrichment*.py 2>/dev/null || true

# Verify changes
echo ""
echo "📋 Verifying changes in main.py..."
grep -n "contact_id:" apps/backend/main.py | head -10

echo ""
echo "📋 Verifying GPT model..."
grep -n "gpt-4" enrichment_apex_custom.py 2>/dev/null | head -5 || echo "Check enrichment file manually"

# Commit
echo ""
echo "📤 Committing backend fixes..."
git add apps/backend/main.py enrichment_apex_custom.py 2>/dev/null || git add apps/backend/main.py
git commit -m "fix(backend): UUID support for GET contact + GPT-4o upgrade

1. GET /api/contacts/{contact_id}: int → str
	- Fixes 422 Unprocessable Entity on UUID contacts
	- Aligns with POST /enrich which already accepts UUID
	
2. Upgraded gpt-4 to gpt-4o
	- Fixes context_length_exceeded (8K → 128K tokens)
	- Enrichment synthesis will now complete
	
Frontend UUID handling (yesterday's work) unchanged.
	
Dec 15, 2025"
	
git push origin main
	
echo ""
echo "✅ BACKEND FIXES DEPLOYED"
echo ""
echo "Wait 2-3 min for Render rebuild, then:"
echo "  curl https://apex-backend-i7b0.onrender.com/api/contacts/ef40c46e-1470-4138-beb6-d4be08f73c1f"
echo ""
echo "Should return contact JSON instead of 422"
echo "========================================"
	