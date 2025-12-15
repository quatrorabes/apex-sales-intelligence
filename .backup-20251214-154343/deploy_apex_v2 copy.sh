#!/bin/bash

#!/bin/bash

echo "╔════════════════════════════════════════════════════════════╗"
echo "║   APEX SALES INTELLIGENCE v2.0 - AUTONOMOUS DEPLOYMENT    ║"
echo "║   Frameworks: APEX + BANT + SPICE                          ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Navigate to project
cd ~/projects/apex/apex-sales-intelligence || exit

# Step 1: Database Migration
echo "📋 Step 1: Database Migration"
echo "Please run the SQL migration script in Railway:"
echo "1. Go to https://railway.app"
echo "2. Select your PostgreSQL database"
echo "3. Open Query tab"
echo "4. Paste apex_migration_v2.sql content"
echo "5. Execute"
echo ""
read -p "Press ENTER after migration complete..."

# Step 2: Backup current main.py
echo ""
echo "💾 Step 2: Backing up current main.py..."
cp apps/backend/main.py apps/backend/main.py.backup.$(date +%Y%m%d_%H%M%S)
echo "✅ Backup created"

# Step 3: Deploy new main.py
echo ""
echo "🚀 Step 3: Deploying new main.py..."
echo "The new main.py file should already be in apps/backend/"
read -p "Press ENTER to continue..."

# Step 4: Git commit and push
echo ""
echo "📤 Step 4: Pushing to GitHub..."
git add apps/backend/main.py
git commit -m "feat: APEX v2.0 - Multi-framework qualification (APEX + BANT + SPICE) with unified scoring"
git push origin main

echo ""
echo "⏳ Step 5: Waiting for Render auto-deploy (60 seconds)..."
sleep 60

# Step 6: Test endpoints
echo ""
echo "🧪 Step 6: Testing endpoints..."
BASE_URL="https://apex-backend-i7b0.onrender.com"

echo ""
echo "Testing /health..."
curl -s "$BASE_URL/health" | jq '.status, .apex_scored, .bant_qualified, .spice_qualified'

echo ""
echo "Testing /api/todays-board..."
curl -s "$BASE_URL/api/todays-board" | jq '.success, .stats.total_contacts'

echo ""
echo "Testing /api/analytics..."
curl -s "$BASE_URL/api/analytics" | jq '.success, .qualification'

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║   ✅ APEX v2.0 DEPLOYMENT COMPLETE                         ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "🎯 Next Steps:"
echo "1. Visit: https://apex-sales-intelligence.vercel.app"
echo "2. Test Today's Board"
echo "3. Test Contact Detail with qualification"
echo "4. Run test contact through BANT/SPICE qualification"
echo ""
echo "📊 New Endpoints Available:"
echo "- POST /api/contacts/{id}/qualify/bant"
echo "- POST /api/contacts/{id}/qualify/spice"
echo "- GET /api/contacts/{id}/qualification-report"
echo ""
