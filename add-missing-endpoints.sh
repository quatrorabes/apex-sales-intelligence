#!/bin/bash
cd ~/projects/apex/apex-sales-intelligence

echo "🚀 DEPLOYING RENAMED ENDPOINTS"
echo "==========================================="

git add api.py
git commit -m "fix: rename old endpoints to /api/v1/ to avoid conflicts with new frontend-compatible endpoints"
git push origin main

echo ""
echo "⏳ Waiting 90 seconds for Railway deployment..."
for i in {90..1}; do
    printf "\r   ⏱️  %02d:%02d remaining   " $((i/60)) $((i%60))
    sleep 1
done
echo ""

echo ""
echo "🧪 TESTING NEW ENDPOINTS"
echo "==========================================="

BASE="https://apex-backend-production-production.up.railway.app"

echo ""
echo "--- Health Check ---"
curl -s "$BASE/api/health" | python3 -m json.tool

echo ""
echo "--- ICP Match (Should show nested format now!) ---"
curl -s "$BASE/api/contacts/2066/icp-match" | python3 -m json.tool

echo ""
echo "--- Activities ---"
curl -s "$BASE/api/contacts/2066/activities" | python3 -m json.tool

echo ""
echo "==========================================="
echo "✅ DEPLOYMENT COMPLETE!"
echo "==========================================="
echo ""
echo "🎯 CHECK THE OUTPUT ABOVE:"
echo "ICP Match should show:"
echo "  - 'contactid': 2066  (NOT 'contact_id')"
echo "  - 'icpmatch': { nested object }"
echo "  - 'whyusfit': { nested object }"
echo ""
echo "If YES → Frontend will work!"
echo "If NO → Old endpoint still being called"
echo ""
echo "🌐 Test frontend: https://apex-sales-intelligence.vercel.app/contacts/2066"
echo "💡 Open in INCOGNITO mode and hard refresh!"
