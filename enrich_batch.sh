#!/bin/bash

echo "🚀 BATCH ENRICHMENT - First 50 Contacts with LinkedIn"
echo "=========================================================="

# Get DATABASE IDs (not HubSpot IDs)
CONTACTS=$(sqlite3 apex.db "SELECT id FROM contacts WHERE linkedin_url IS NOT NULL AND (enrichment_status IS NULL OR enrichment_status = 'pending') LIMIT 50;")

TOTAL=$(echo "$CONTACTS" | wc -l | tr -d ' ')
COUNT=0

for CONTACT_ID in $CONTACTS; do
    COUNT=$((COUNT + 1))
    
    # Get contact info for logging
    INFO=$(sqlite3 apex.db "SELECT name, company FROM contacts WHERE id = $CONTACT_ID;")
    
    echo ""
    echo "[$COUNT/$TOTAL] Enriching: $INFO"
    echo "              ID: $CONTACT_ID"
    
    RESULT=$(curl -s -X POST http://localhost:8000/api/contacts/$CONTACT_ID/enrich)
    
    if echo "$RESULT" | grep -q '"success":true'; then
        echo "              ✅ Success"
    else
        ERROR=$(echo "$RESULT" | python3 -c "import sys, json; print(json.load(sys.stdin).get('error', 'Unknown error'))" 2>/dev/null || echo "$RESULT")
        echo "              ❌ Failed: $ERROR"
    fi
    
    # Rate limiting (3-5 minutes per enrichment, so wait between)
    sleep 5
done

echo ""
echo "=========================================================="
echo "✅ Batch complete! Check enrichment_status in database."
