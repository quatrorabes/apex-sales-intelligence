#!/bin/bash
# Quick test: Check if enrichment_data is returned by API

echo "Testing API response for enriched contact..."
echo ""

BACKEND_URL="https://your-backend.onrender.com"  # Replace with actual URL
CONTACT_ID="f6e4e0f2-0597-47a2-b4f5-869fa94b6a12"

echo "GET $BACKEND_URL/api/contacts/$CONTACT_ID"
echo ""

curl -s "$BACKEND_URL/api/contacts/$CONTACT_ID" | python3 -m json.tool | grep -A 20 enrichment

echo ""
echo "Look for:"
echo '  "enrichment_status": "completed"'
echo '  "enrichment_data": { ... }'
echo ""
echo "If enrichment_data is null or missing, the backend isn't returning it."
