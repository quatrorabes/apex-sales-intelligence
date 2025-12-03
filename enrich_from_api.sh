#!/bin/bash

echo "🚀 ENRICHMENT - Using API Contact IDs"
echo "=========================================================="

# Get contacts from API
CONTACTS=$(curl -s "http://localhost:8000/api/contacts?limit=1000" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for contact in data.get('contacts', []):
	if contact.get('linkedin_url'):
		print(f\"{contact['id']}|{contact.get('name', 'Unknown')}|{contact.get('company', 'Unknown')}\")
" | head -50)

if [ -z "$CONTACTS" ]; then
	echo "❌ No contacts with LinkedIn URL found in API"
	exit 1
fi

TOTAL=$(echo "$CONTACTS" | wc -l | tr -d ' ')
COUNT=0

echo "Found $TOTAL contacts with LinkedIn URLs"
echo ""

for LINE in $CONTACTS; do
	IFS='|' read -r CONTACT_ID NAME COMPANY <<< "$LINE"
	COUNT=$((COUNT + 1))
	
	echo "[$COUNT/$TOTAL] Enriching: $NAME @ $COMPANY"
	echo "            ID: $CONTACT_ID"
	
	RESULT=$(curl -s -X POST http://localhost:8000/api/contacts/$CONTACT_ID/enrich)
	
	if echo "$RESULT" | grep -q '"success":true'; then
		echo "            ✅ Success"
	else
		ERROR=$(echo "$RESULT" | python3 -c "import sys, json; print(json.load(sys.stdin).get('error', 'Unknown'))" 2>/dev/null || echo "Parse error")
		echo "            ❌ Failed: $ERROR"
	fi
	
	sleep 5
done

echo ""
echo "=========================================================="
echo "✅ Batch complete!"
