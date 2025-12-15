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
echo -e "${YELLOW}[STEP 1/5] Verifying Render Backend Health...${NC}"
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

echo ""

# ====================================================================
# STEP 2: NAVIGATE TO DASHBOARD_V1 & CHECK GIT STATUS
# ====================================================================
echo -e "${YELLOW}[STEP 2/5] Checking Dashboard_v1 Git Status...${NC}"

cd ~/projects/apex/apex-sales-intelligence/dashboard_v1 || {
    echo -e "${RED}✗ Could not navigate to dashboard_v1 directory${NC}"
    exit 1
}

echo -e "${BLUE}Current directory:${NC} $(pwd)"
echo ""

# Check if there are uncommitted changes
GIT_STATUS=$(git status --porcelain)
if [[ -z "$GIT_STATUS" ]]; then
    echo -e "${GREEN}✓ No uncommitted changes${NC}"
else
    echo -e "${YELLOW}⚠ Uncommitted changes detected:${NC}"
    git status --short
    echo ""
    echo -e "${YELLOW}Do you want to commit these changes? (y/n)${NC}"
    read -r COMMIT_CHOICE
    if [[ "$COMMIT_CHOICE" == "y" ]]; then
        echo "Enter commit message:"
        read -r COMMIT_MSG
        git add -A
        git commit -m "$COMMIT_MSG"
        echo -e "${GREEN}✓ Changes committed${NC}"
    else
        echo -e "${YELLOW}⚠ Proceeding without committing${NC}"
    fi
fi

echo ""

# ====================================================================
# STEP 3: VERIFY ENVIRONMENT CONFIGURATION
# ====================================================================
echo -e "${YELLOW}[STEP 3/5] Verifying Environment Configuration...${NC}"

# Check if .env file exists
if [[ -f ".env" ]]; then
    echo -e "${BLUE}Local .env file found:${NC}"
    cat .env | grep "VITE_API"
else
    echo -e "${YELLOW}⚠ No local .env file (using Vercel env vars)${NC}"
fi

echo ""
echo -e "${BLUE}Expected Vercel Environment Variable:${NC}"
echo "VITE_API_URL=https://apex-backend-i7b0.onrender.com"
echo ""
echo -e "${YELLOW}⚠ IMPORTANT: Verify in Vercel dashboard that VITE_API_URL points to Render backend${NC}"
echo ""

# ====================================================================
# STEP 4: PUSH TO GITHUB (TRIGGERS VERCEL AUTO-DEPLOY)
# ====================================================================
echo -e "${YELLOW}[STEP 4/5] Deploying to Vercel via GitHub...${NC}"

echo "Pushing to GitHub main branch..."
git push origin main

echo -e "${GREEN}✓ Pushed to GitHub${NC}"
echo -e "${BLUE}→ Vercel will auto-deploy from GitHub (takes ~90 seconds)${NC}"
echo ""

# Wait for deployment
echo "Waiting 90 seconds for Vercel deployment..."
for i in {90..1}; do
    echo -ne "${YELLOW}$i seconds remaining...${NC}\r"
    sleep 1
done
echo ""

# ====================================================================
# STEP 5: TEST PRODUCTION FRONTEND LINKS
# ====================================================================
echo -e "${YELLOW}[STEP 5/5] Testing Production Frontend Links...${NC}"

FRONTEND_URL="https://apex-sales-intelligence.vercel.app"

# Test pages array
declare -a PAGES=(
    "/"
    "/contacts"
    "/contacts/2068"
    "/settings"
)

echo -e "${BLUE}Testing frontend pages:${NC}"
for PAGE in "${PAGES[@]}"; do
    echo -n "Testing $FRONTEND_URL$PAGE ... "
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$FRONTEND_URL$PAGE")
    if [[ "$STATUS" == "200" ]]; then
        echo -e "${GREEN}✓ OK (HTTP $STATUS)${NC}"
    else
        echo -e "${RED}✗ FAILED (HTTP $STATUS)${NC}"
    fi
done

echo ""

# ====================================================================
# STEP 6: BROWSER TESTING INSTRUCTIONS
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
echo -e "   ${BLUE}a) Landing Page → Should load contact list${NC}"
echo -e "   ${BLUE}b) Click any contact → View contact detail page${NC}"
echo -e "   ${BLUE}c) Click 'Enrich' button → Verify enrichment calls backend${NC}"
echo -e "   ${BLUE}d) Navigate to Settings → Verify playbook loads${NC}"
echo -e "   ${BLUE}e) Check browser console → No CORS errors${NC}"
echo ""
echo -e "${YELLOW}4. Test Robert Covarrubias contact (ID 2068):${NC}"
echo -e "   ${GREEN}$FRONTEND_URL/contacts/2068${NC}"
echo -e "   ${BLUE}→ Verify MBTI, DISC, and Communication Playbook display${NC}"
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
echo -e "${GREEN}✓ Deploy:${NC}   Vercel auto-deploy from GitHub"
echo -e "${GREEN}✓ Status:${NC}   Ready for testing"
echo ""
echo -e "${YELLOW}Next Action: Open browser and test all links above${NC}"
echo ""
