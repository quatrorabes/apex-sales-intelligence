#!/bin/bash

# ============================================================================
# APEX SALES INTELLIGENCE - Complete ContactsView Fix & Deploy
# ============================================================================
# This script fixes ContactsView.tsx and deploys to Vercel
# All 6 changes automatically applied:
# 1. useNavigate import (already exists)
# 2. navigate hook initialization
# 3. handleContactClick function
# 4. onClick on table row
# 5. stopPropagation on checkbox
# 6. Remove Link from name cell
# ============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ROOT="${1:-.}"
CONTACTS_VIEW="$PROJECT_ROOT/dashboardv1/src/components/ContactsView.tsx"
FIXED_FILE="./ContactsView.tsx.FIXED"

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  APEX SALES INTELLIGENCE - ContactsView Fix & Deploy      ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if fixed file exists
if [ ! -f "$FIXED_FILE" ]; then
    echo -e "${RED}❌ Error: ContactsView.tsx.FIXED not found in current directory${NC}"
    echo "   Please ensure the file is in: $(pwd)"
    exit 1
fi

# Check if target file exists
if [ ! -f "$CONTACTS_VIEW" ]; then
    echo -e "${RED}❌ Error: Target file not found${NC}"
    echo "   Expected: $CONTACTS_VIEW"
    exit 1
fi

# Create backup
BACKUP_FILE="$CONTACTS_VIEW.backup.$(date +%s)"
cp "$CONTACTS_VIEW" "$BACKUP_FILE"
echo -e "${GREEN}✅ Backup created:${NC} $BACKUP_FILE"
echo ""

# Apply fix
echo -e "${BLUE}📝 Applying fix...${NC}"
cp "$FIXED_FILE" "$CONTACTS_VIEW"
echo -e "${GREEN}✅ ContactsView.tsx updated${NC}"
echo ""

# Show what changed
echo -e "${YELLOW}🔍 Changes Summary:${NC}"
echo "   ✓ Import: useNavigate hook"
echo "   ✓ Initialize: navigate hook"
echo "   ✓ Function: handleContactClick(contactId)"
echo "   ✓ Table Row: Added onClick handler + cursor-pointer"
echo "   ✓ Checkbox: Added stopPropagation"
echo "   ✓ Name Cell: Removed Link, using span"
echo ""

# Git operations
echo -e "${BLUE}🚀 Deploying to Vercel...${NC}"
echo ""

cd "$PROJECT_ROOT"

# Add file
git add dashboardv1/src/components/ContactsView.tsx
echo -e "${GREEN}✅ File added to git${NC}"

# Commit
git commit -m "fix: add onClick navigation to contact detail page

- Initialize useNavigate hook
- Add handleContactClick function
- Add onClick handler to table rows
- Add stopPropagation to checkbox
- Remove Link from name cell
- Use cursor-pointer class for visual feedback"

echo -e "${GREEN}✅ Changes committed${NC}"

# Push
echo -e "${BLUE}📤 Pushing to main branch...${NC}"
git push origin main
echo -e "${GREEN}✅ Pushed to main${NC}"
echo ""

# Final message
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                    ✅ DEPLOYMENT COMPLETE                 ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}⏱️  Vercel will auto-deploy in ~60 seconds${NC}"
echo -e "${YELLOW}🔗 Dashboard: https://apex-sales-intelligence.vercel.app${NC}"
echo ""
echo "Testing the fix:"
echo "  1. Click any contact row in the table"
echo "  2. Should navigate to /contacts/:id"
echo "  3. ContactDetailPage loads"
echo "  4. Enrich button appears"
echo ""
echo -e "${GREEN}✨ Done!${NC}"
