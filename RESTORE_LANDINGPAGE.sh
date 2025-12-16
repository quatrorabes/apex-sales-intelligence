#!/bin/bash
# 🔄 RESTORE ORIGINAL LandingPage.tsx (PRE-CHANGES)
# Find and restore from most recent backup
# Dec 15, 2025 4:41 PM PST

set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
TS=$(date +%Y%m%d_%H%M%S)

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔄 RESTORING ORIGINAL LandingPage.tsx"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check for backups
echo "Looking for LandingPage.tsx backups..."
ls -lah dashboard_v1/src/components/LandingPage.tsx.bak* 2>/dev/null || echo "No .bak backups found"
ls -lah dashboard_v1/src/components/LandingPage.tsx.backup* 2>/dev/null || echo "No .backup backups found"

# Find most recent backup
BACKUP=$(ls -t dashboard_v1/src/components/LandingPage.tsx.bak* 2>/dev/null | head -1)

if [ -z "$BACKUP" ]; then
  echo "❌ No backup found."
  echo ""
  echo "Checking git history for previous version..."
  git log --oneline --all -- dashboard_v1/src/components/LandingPage.tsx | head -5
  echo ""
  echo "To restore from git history, run:"
  echo "git show HEAD~1:dashboard_v1/src/components/LandingPage.tsx > dashboard_v1/src/components/LandingPage.tsx"
  exit 1
fi

echo "✅ Found backup: $BACKUP"

# Backup current version
cp dashboard_v1/src/components/LandingPage.tsx dashboard_v1/src/components/LandingPage.tsx.bad-${TS}
echo "📦 Backed up current version"

# Restore from backup
cp "$BACKUP" dashboard_v1/src/components/LandingPage.tsx
echo "✅ Restored from: $BACKUP"

# Commit and push
git add dashboard_v1/src/components/LandingPage.tsx
git commit -m "restore(LandingPage): revert to original pre-changes version

Restored from backup: $BACKUP
User requested original LandingPage layout from before unauthorized changes."

git push origin main

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ ORIGINAL LANDINGPAGE RESTORED"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🚀 Vercel deploying (~2 min)"
echo "🔗 https://apex-sales-intelligence.vercel.app/"
echo ""
