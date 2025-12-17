#!/bin/bash
# Commit and deploy enrichment updates

set -e

echo "========================================================================"
echo "DEPLOYING ENRICHMENT UPDATES"
echo "========================================================================"
echo ""

# Backend changes
git add apps/backend/api/routes/enrichment.py

# Frontend instructions
git add dashboard_v1/ENRICH_BUTTON_INSTRUCTIONS.md

# Commit
git commit -m "fix(enrichment): PostgreSQL compat + debug files + single contact UI

BACKEND:
- Fixed PostgreSQL query syntax
- Limited batch enrich to 1 contact
- Added debug file output:
  - 01_engine_raw_result.txt
  - 02_after_perplexity_and_openai.txt (THE KEY FILE)
  - 03_after_parsing.txt
- Added POST /api/contacts/{id}/enrich endpoint

FRONTEND:
- Added instructions for single contact enrich button
- See dashboard_v1/ENRICH_BUTTON_INSTRUCTIONS.md

Debug files saved to: /tmp/apex_debug/contact_{id}_*"

git push origin main

echo ""
echo "✅ Backend deployed to Render (~2 min)"
echo ""
echo "Next: Update frontend ContactsView.tsx"
echo "See: dashboard_v1/ENRICH_BUTTON_INSTRUCTIONS.md"
echo ""
