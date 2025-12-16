#!/bin/bash
# RESTORE ORIGINAL TodaysBoard from backup
# Dec 15, 2025 4:29 PM PST

set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

echo "🔄 RESTORING ORIGINAL TodaysBoard.tsx from backup..."

# Find most recent backup
BACKUP=$(ls -t dashboard_v1/src/components/TodaysBoard.tsx.bak* 2>/dev/null | head -1)

if [ -z "$BACKUP" ]; then
  echo "❌ No backup found. Cannot restore."
  echo ""
  echo "Available backups:"
  ls -la dashboard_v1/src/components/TodaysBoard.tsx.bak* 2>/dev/null || echo "None found"
  exit 1
fi

echo "✅ Found backup: $BACKUP"
echo ""

# Backup current (bad) version
TS=$(date +%Y%m%d_%H%M%S)
cp dashboard_v1/src/components/TodaysBoard.tsx dashboard_v1/src/components/TodaysBoard.tsx.bad-${TS}
echo "📦 Backed up current version to: TodaysBoard.tsx.bad-${TS}"

# Restore from backup
cp "$BACKUP" dashboard_v1/src/components/TodaysBoard.tsx
echo "✅ Restored from: $BACKUP"

# Commit
git add dashboard_v1/src/components/TodaysBoard.tsx
git commit -m "revert(TodaysBoard): restore EXACT original layout from backup

Reverted unauthorized changes made on Dec 15, 2025.
Restored from backup: $BACKUP

Original layout preserved - no modifications."

git push origin main

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ ORIGINAL TODAYSBOARD RESTORED"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📍 Restored from: $BACKUP"
echo "🚀 Vercel deploying original layout (~2 min)"
echo ""
echo "🔗 https://apex-sales-intelligence.vercel.app/todays-board"
echo ""
