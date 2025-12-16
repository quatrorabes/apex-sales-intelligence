#!/bin/bash
# scripts/deploy_enrichment_fix.sh
# Deploy enrichment parsing fix

set -e

echo "======================================================================"
echo "APEX ENRICHMENT PARSING FIX — DEPLOYMENT"
echo "======================================================================"

# Step 1: Validate parser
echo ""
echo "Step 1: Running validation tests..."
python3 scripts/validate_enrichment_parsing.py
if [ $? -ne 0 ]; then
    echo "❌ Validation failed. Aborting deployment."
    exit 1
fi

# Step 2: Backup existing parser (optional)
echo ""
echo "Step 2: Creating backup..."
if [ -f apps/backend/services/enrichment_parser.py ]; then
    cp apps/backend/services/enrichment_parser.py \
       apps/backend/services/enrichment_parser.py.backup.$(date +%Y%m%d_%H%M%S)
    echo "✅ Backup created"
else
    echo "⚠️  No existing parser found (clean install)"
fi

# Step 3: Commit changes
echo ""
echo "Step 3: Committing changes..."
git add docs/THREAD-DEC16-ENRICHMENT-PARSING-WIRING.md
git add apps/backend/services/enrichment_parser.py
git add apps/backend/services/enrichment_integration.py
git add scripts/validate_enrichment_parsing.py
git add scripts/deploy_enrichment_fix.sh

git commit -m "fix(enrichment): add markdown_v3 parser support for ## section_key format

- Add multi-format parser (markdown_v3, markdown_v2, legacy, unknown)
- Maintain backwards compatibility with existing formats
- Update integration service for consistency
- Add validation test suite
- Document thread transfer for Dec 16 parsing fix

Closes: enrichment sections not populating in DB/Dashboard_v1"

# Step 4: Push
echo ""
echo "Step 4: Pushing to remote..."
git push origin main

echo ""
echo "======================================================================"
echo "✅ DEPLOYMENT COMPLETE"
echo "======================================================================"
echo ""
echo "Next steps:"
echo "1. Backend will auto-deploy (Railway/Render)"
echo "2. Re-enrich 1 test contact: POST /api/contacts/{id}/enrich"
echo "3. Verify DB: SELECT enrichment_data->'sections' FROM contacts WHERE id = {id};"
echo "4. Verify Dashboard_v1: Check ContactDetail page shows structured sections"
echo ""
