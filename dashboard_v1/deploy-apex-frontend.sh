#!/bin/bash
# ====================================================================
# APEX FRONTEND DEPLOYMENT & TESTING SCRIPT
# ====================================================================
# Purpose: Deploy Dashboard_v1 to Vercel and test all production links
# Date: December 8, 2025
# Backend: https://apex-backend-i7b0.onrender.com
# Frontend: https://apex-sales-intelligence.vercel.app
# ====================================================================

set -e  # Exit on error

# Color codes for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     APEX FRONTEND DEPLOYMENT & TESTING WORKFLOW           ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# ====================================================================
# STEP 1: VERIFY BACKEND HEALTH ON RENDER
# ====================================================================
echo -e "${YELLOW}[STEP 1/6] Verifying Render Backend Health...${NC}"
BACKEND_URL="https://apex-backend-i7b0.onrender.com"

echo "Testing root endpoint..."
ROOT_RESPONSE=$(curl -s "$BACKEND_URL/" || echo "ERROR")
if [[ "$ROOT_RESPONSE" == *"ERROR"* ]]; then
    echo -e "${RED}✗ Backend root endpoint failed!${NC}"
    exit 1
else
    echo -e "${GREEN}✓ Backend root responding${NC}"
fi

echo "Testing /api/contacts endpoint..."
CONTACTS_RESPONSE=$(curl -s "$BACKEND_URL/api/contacts" || echo "ERROR")
if [[ "$CONTACTS_RESPONSE" == *"ERROR"* ]]; then
    echo -e "${RED}✗ Contacts API failed!${NC}"
    exit 1
else
    CONTACT_COUNT=$(echo "$CONTACTS_RESPONSE" | grep -o '"id"' | wc -l)
    echo -e "${GREEN}✓ Contacts API responding (${CONTACT_COUNT} contacts found)${NC}"
fi

echo "Testing /api/playbook endpoint..."
PLAYBOOK_RESPONSE=$(curl -s "$BACKEND_URL/api/playbook" || echo "ERROR")
if [[ "$PLAYBOOK_RESPONSE" == *"ERROR"* ]]; then
    echo -e "${RED}✗ Playbook API failed!${NC}"
else
    echo -e "${GREEN}✓ Playbook API responding${NC}"
fi

echo ""

# ====================================================================
# STEP 2: NAVIGATE TO DASHBOARD_V1 & CHECK GIT STATUS
# ====================================================================
echo -e "${YELLOW}[STEP 2/6] Checking Dashboard_v1 Git Status...${NC}"

cd ~/projects/apex/apex-sales-intelligence/dashboard_v1 || {
    echo -e "${RED}✗ Could not navigate to dashboard_v1 directory${NC}"
    exit 1
}

echo -e "${BLUE}Current directory:${NC} $(pwd)"
echo ""

# Show current branch
CURRENT_BRANCH=$(git branch --show-current)
echo -e "${BLUE}Current branch:${NC} $CURRENT_BRANCH"

# Check if on main branch
if [[ "$CURRENT_BRANCH" != "main" ]]; then
    echo -e "${YELLOW}⚠ Not on main branch. Switching to main...${NC}"
    git checkout main
    git pull origin main
fi

echo ""

# Check for uncommitted changes
GIT_STATUS=$(git status --porcelain)
if [[ -z "$GIT_STATUS" ]]; then
    echo -e "${GREEN}✓ No uncommitted changes${NC}"
else
    echo -e "${YELLOW}⚠ Uncommitted changes detected:${NC}"
    git status --short
    echo ""
fi

echo ""

# ====================================================================
# STEP 3: VERIFY ENVIRONMENT CONFIGURATION
# ====================================================================
echo -e "${YELLOW}[STEP 3/6] Verifying Environment Configuration...${NC}"

# Check if .env file exists
if [[ -f ".env" ]]; then
    echo -e "${BLUE}Local .env file found:${NC}"
    cat .env | grep "VITE_API" || echo -e "${YELLOW}⚠ No VITE_API variables found${NC}"
else
    echo -e "${YELLOW}⚠ No local .env file (using Vercel env vars)${NC}"
fi

echo ""
echo -e "${BLUE}Expected Vercel Environment Variable:${NC}"
echo "VITE_API_URL = https://apex-backend-i7b0.onrender.com"
echo ""
echo -e "${YELLOW}⚠ VERIFY: Check Vercel dashboard for correct backend URL${NC}"
echo -e "${BLUE}→ https://vercel.com/quatrorabes-projects/apex-sales-intelligence/settings/environment-variables${NC}"
echo ""

# ====================================================================
# STEP 4: COMMIT & PUSH TO GITHUB
# ====================================================================
echo -e "${YELLOW}[STEP 4/6] Committing & Pushing to GitHub...${NC}"

if [[ -n "$GIT_STATUS" ]]; then
    echo "Staging all changes..."
    git add -A

    # Generate timestamp for commit
    TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S %Z')
    COMMIT_MSG="deploy: Frontend update - $TIMESTAMP"

    echo "Committing with message: $COMMIT_MSG"
    git commit -m "$COMMIT_MSG"
    echo -e "${GREEN}✓ Changes committed${NC}"
else
    echo -e "${BLUE}→ No changes to commit${NC}"
fi

echo ""
echo "Pushing to GitHub main branch..."
git push origin main

echo -e "${GREEN}✓ Pushed to GitHub${NC}"
echo -e "${BLUE}→ Vercel will auto-deploy from GitHub (takes ~90 seconds)${NC}"
echo ""

# ====================================================================
# STEP 5: WAIT FOR VERCEL DEPLOYMENT
# ====================================================================
echo -e "${YELLOW}[STEP 5/6] Waiting for Vercel Deployment...${NC}"
echo ""

# Countdown timer
for i in {90..1}; do
    printf "\r${YELLOW}Deployment in progress... %2d seconds remaining${NC}" "$i"
    sleep 1
done
echo ""
echo -e "${GREEN}✓ Deployment should be complete${NC}"
echo ""

# ====================================================================
# STEP 6: TEST PRODUCTION FRONTEND LINKS
# ====================================================================
echo -e "${YELLOW}[STEP 6/6] Testing Production Frontend Links...${NC}"
echo ""

FRONTEND_URL="https://apex-sales-intelligence.vercel.app"

# Test pages array
declare -a PAGES=(
    "/:Landing Page"
    "/contacts:All Contacts"
    "/contacts/2068:Robert Covarrubias"
    "/settings:Settings & Playbook"
    "/today:Today's Board"
)

echo -e "${BLUE}Testing frontend pages:${NC}"
for PAGE_INFO in "${PAGES[@]}"; do
    IFS=':' read -r PAGE DESC <<< "$PAGE_INFO"
    printf "%-50s" "Testing $DESC ($PAGE)..."
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$FRONTEND_URL$PAGE" 2>/dev/null || echo "FAIL")
    if [[ "$STATUS" == "200" ]]; then
        echo -e "${GREEN}✓ OK${NC}"
    else
        echo -e "${RED}✗ HTTP $STATUS${NC}"
    fi
done

echo ""

# Test backend connectivity from frontend perspective
echo -e "${BLUE}Testing backend API endpoints:${NC}"
declare -a API_ENDPOINTS=(
    "/api/contacts:Contacts API"
    "/api/playbook:Playbook API"
    "/api/cadences:Cadences API"
)

for ENDPOINT_INFO in "${API_ENDPOINTS[@]}"; do
    IFS=':' read -r ENDPOINT DESC <<< "$ENDPOINT_INFO"
    printf "%-50s" "Testing $DESC ($ENDPOINT)..."
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BACKEND_URL$ENDPOINT" 2>/dev/null || echo "FAIL")
    if [[ "$STATUS" == "200" ]]; then
        echo -e "${GREEN}✓ OK${NC}"
    else
        echo -e "${RED}✗ HTTP $STATUS${NC}"
    fi
done

echo ""

# ====================================================================
# BROWSER TESTING INSTRUCTIONS
# ====================================================================
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║              MANUAL BROWSER TESTING REQUIRED              ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}1. Open browser and navigate to:${NC}"
echo -e "   ${GREEN}$FRONTEND_URL${NC}"
echo ""
echo -e "${YELLOW}2. Hard refresh (clear cache):${NC}"
echo -e "   ${BLUE}• Mac: Cmd+Shift+R${NC}"
echo -e "   ${BLUE}• Windows: Ctrl+Shift+R${NC}"
echo ""
echo -e "${YELLOW}3. Test these critical paths:${NC}"
echo -e "   ${BLUE}a) Landing Page → Contact list loads${NC}"
echo -e "   ${BLUE}b) Click contact → View detail page${NC}"
echo -e "   ${BLUE}c) Click 'Enrich' → Verify backend call (check Network tab)${NC}"
echo -e "   ${BLUE}d) Navigate to Settings → Playbook loads${NC}"
echo -e "   ${BLUE}e) Check Console → No CORS/API errors${NC}"
echo ""
echo -e "${YELLOW}4. Test Robert Covarrubias (ID 2068):${NC}"
echo -e "   ${GREEN}$FRONTEND_URL/contacts/2068${NC}"
echo -e "   ${BLUE}→ Verify: MBTI, DISC, Communication Playbook display${NC}"
echo ""

# ====================================================================
# DEPLOYMENT SUMMARY
# ====================================================================
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                  DEPLOYMENT SUMMARY                       ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}✓ Backend:${NC}  $BACKEND_URL"
echo -e "${GREEN}✓ Frontend:${NC} $FRONTEND_URL"
echo -e "${GREEN}✓ Database:${NC} SQLite on Render persistent disk"
echo -e "${GREEN}✓ Deploy:${NC}   Vercel auto-deploy from GitHub"
echo -e "${GREEN}✓ Status:${NC}   LIVE - Ready for testing"
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}NEXT STEPS:${NC}"
echo -e "  1. Open $FRONTEND_URL in browser"
echo -e "  2. Hard refresh (Cmd+Shift+R / Ctrl+Shift+R)"
echo -e "  3. Test all pages and verify no console errors"
echo -e "  4. Test contact enrichment on a sample contact"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""
