#!/bin/bash

BASE_URL="https://apex-backend-i7b0.onrender.com"
CONTACT_ID=3308  # Neal Raburn - known enriched contact

echo "=========================================="
echo "🧪 APEX BACKEND - COMPLETE TEST SUITE"
echo "Testing: $BASE_URL"
echo "=========================================="
echo ""

# HEALTH & STATUS
echo "1️⃣ HEALTH CHECK"
curl -s "$BASE_URL/health" | jq '.'
echo ""

echo "2️⃣ ROOT ENDPOINT"
curl -s "$BASE_URL/" | jq '.'
echo ""

# CONTACT CRUD
echo "3️⃣ LIST CONTACTS (limit 5)"
curl -s "$BASE_URL/api/contacts?limit=5" | jq '.success, .total, .contacts[0].name'
echo ""

echo "4️⃣ GET SINGLE CONTACT (ID: $CONTACT_ID)"
curl -s "$BASE_URL/api/contacts/$CONTACT_ID" | jq '.success, .contact.name, .contact.company, .contact.enrichment_status'
echo ""

echo "5️⃣ SEARCH CONTACTS (search=neal)"
curl -s "$BASE_URL/api/contacts?search=neal&limit=3" | jq '.success, .total, .contacts[].name'
echo ""

# ENRICHMENT
echo "6️⃣ GET ENRICHMENT DATA"
curl -s "$BASE_URL/api/contacts/$CONTACT_ID" | jq '.contact.enrichment_data' | head -20
echo "... (truncated)"
echo ""

# DASHBOARD & ANALYTICS
echo "7️⃣ TODAY'S BOARD ⚠️"
curl -s "$BASE_URL/api/todays-board" | jq '.'
echo ""

echo "8️⃣ ANALYTICS"
curl -s "$BASE_URL/api/analytics" | jq '.'
echo ""

echo "9️⃣ SMART LISTS"
curl -s "$BASE_URL/api/smart-lists" | jq '.lists[].name'
echo ""

echo "🔟 COLD CALL QUEUE"
curl -s "$BASE_URL/api/cold-call/queue" | jq '.success, .count'
echo ""

# ICP & PERSONA
echo "1️⃣1️⃣ ICP MATCH"
curl -s "$BASE_URL/api/contacts/$CONTACT_ID/icp-match" | jq '.'
echo ""

echo "1️⃣2️⃣ ENROLLMENTS"
curl -s "$BASE_URL/api/contacts/$CONTACT_ID/enrollments" | jq '.'
echo ""

# SCORES
echo "1️⃣3️⃣ APEX SCORES (top 5)"
curl -s "$BASE_URL/api/apex/scores?limit=5" | jq '.success, .count'
echo ""

echo "1️⃣4️⃣ CONTACT DASHBOARD"
curl -s "$BASE_URL/api/dashboard/$CONTACT_ID" | jq 'keys'
echo ""

# CONTENT GENERATION
echo "1️⃣5️⃣ GENERATE CALL SCRIPT"
curl -s -X POST "$BASE_URL/api/contacts/$CONTACT_ID/generate-call-script" | jq '.success'
echo ""

echo "1️⃣6️⃣ GENERATE EMAIL"
curl -s -X POST "$BASE_URL/api/contacts/$CONTACT_ID/generate-email" | jq '.success'
echo ""

echo "1️⃣7️⃣ GENERATE LINKEDIN MESSAGE"
curl -s -X POST "$BASE_URL/api/contacts/$CONTACT_ID/generate-linkedin" | jq '.success'
echo ""

echo "=========================================="
echo "✅ TEST SUITE COMPLETE"
echo "=========================================="
