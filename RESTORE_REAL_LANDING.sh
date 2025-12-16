#!/bin/bash
# 🚨 RESTORE ORIGINAL LANDING PAGE FROM GIT HISTORY
# Dec 15, 2025 4:59 PM PST

set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

echo "🔄 RESTORING ORIGINAL LANDING PAGE FROM GIT HISTORY..."

# Get the commit that added the LandingPage
COMMIT=$(git log --all --full-history --format="%H" -- "dashboard_v1/src/components/LandingPage.tsx" | head -1)

echo "Found commit: $COMMIT"

# Restore the file from that commit
git show ${COMMIT}:dashboard_v1/src/components/LandingPage.tsx > dashboard_v1/src/components/LandingPage.tsx

echo "✅ LandingPage.tsx restored from git history"

# Verify it has the Good morning/afternoon text
grep -q "Good morning" dashboard_v1/src/components/LandingPage.tsx && echo "✅ Confirmed: Has greeting text"

# Commit and push
git add dashboard_v1/src/components/LandingPage.tsx
git commit -m "restore: original LandingPage with 'Good afternoon, Chris' + 6 quick action boxes

RESTORED FROM GIT HISTORY
Features:
- Time-based greeting (Good morning/afternoon/evening)
- 6 QuickAction boxes (Contacts, Analytics, Cold Call, etc.)
- Dark theme bg-[#0f1114]
- APEX Sales Intelligence hero section
- Purple/blue gradient background"

git push origin main

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ ORIGINAL LANDING PAGE RESTORED"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🚀 Vercel deploying (~2 min)"
echo "🔗 https://apex-sales-intelligence.vercel.app/"
echo ""
echo "FEATURES RESTORED:"
echo "  ✅ 'Good afternoon, Chris' greeting"
echo "  ✅ 6 QuickAction boxes"
echo "  ✅ APEX Sales Intelligence header"
echo "  ✅ Dark theme with purple/blue gradient"
