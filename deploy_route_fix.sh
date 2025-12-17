#!/bin/bash
# Deploy enrichment route fix

git add apps/backend/api/routes/enrichment.py
git commit -m "fix: add /api/v2 routes for Dashboard enrichment button

ADDED ROUTES:
- POST /api/v2/contacts/{id}/enrich (Dashboard calls this)
- GET /api/v2/contacts/{id}/enrichment-status (Dashboard polling)

KEPT ROUTES (backwards compatibility):
- POST /api/contacts/{id}/enrich
- GET /api/contacts/{id}/enrichment-status
- POST /api/batch/enrich

NO FRONTEND CHANGES - Dashboard already has the button

Result: Dashboard 'Generate AI Outreach Content' button now works"

git push origin main

echo ""
echo "✅ Deployed - Render will restart in ~2 min"
echo ""
echo "Test: Click any contact → Outreach tab → Generate AI Outreach Content"
