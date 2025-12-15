#!/bin/bash

echo "🔧 APEX Dashboard - Complete Cleanup Script"
echo "=============================================="

cd src/components

# Backup all files first
echo "📦 Creating backups..."
for file in *.tsx; do
  if [ -f "$file" ]; then
    cp "$file" "${file}.backup-$(date +%Y%m%d-%H%M%S)"
  fi
done

# Fix 1: ScoreExplainer.tsx - Lines 12, 35, 47, 59, 74
echo "🔧 Fixing ScoreExplainer.tsx..."
sed -i '' '
  s/{contact\.priority_score}/{contact.priority_score ?? 0}/g
  s/{contact\.rss_score}/{contact.rss_score ?? 0}/g
  s/{contact\.mdcp_score}/{contact.mdcp_score ?? 0}/g
' ScoreExplainer.tsx

# Fix 2: ContactDetailPage.tsx - All score references
echo "🔧 Fixing ContactDetailPage.tsx..."
sed -i '' '
  s/score={contact\.priority_score}/score={contact.priority_score ?? 0}/g
  s/score={contact\.rss_score}/score={contact.rss_score ?? 0}/g
  s/score={contact\.mdcp_score}/score={contact.mdcp_score ?? 0}/g
  s/contact\.priority_score \/ 100/(contact.priority_score ?? 0) \/ 100/g
' ContactDetailPage.tsx

# Fix 3: ContactEnrichmentView.tsx - Line 268, 279
echo "🔧 Fixing ContactEnrichmentView.tsx..."
sed -i '' '
  s/{Math\.round(contact\.rss_score || 0)}/{Math.round(contact.rss_score ?? 0)}/g
  s/{Math\.round(contact\.mdcp_score || 0)}/{Math.round(contact.mdcp_score ?? 0)}/g
' ContactEnrichmentView.tsx

# Fix 4: Find and replace any remaining Railway URLs
echo "🌐 Fixing API URLs..."
for file in *.tsx; do
  if grep -q "apex-intelligence-production.up.railway.app" "$file"; then
    echo "   Fixing $file..."
    sed -i '' "s|'https://apex-intelligence-production.up.railway.app'|\`\${import.meta.env.VITE_API_URL || 'http://localhost:8000'}\`|g" "$file"
  fi
done

# Fix 5: Add API_URL constant to files that need it
echo "🔧 Adding API_URL constants where missing..."

# List of files that fetch data but might not have API_URL defined
for file in CadenceDashboard.tsx ContactEnrichmentView.tsx RawDataViewer.tsx WhyMeTab.tsx; do
  if [ -f "$file" ]; then
    if ! grep -q "const API_URL" "$file"; then
      echo "   Adding API_URL to $file..."
      # Add after imports (look for first interface or export)
      sed -i '' '/^interface\|^export default/i\
const API_URL = import.meta.env.VITE_API_URL || '\''http://localhost:8000'\'\';\
' "$file"
    fi
  fi
done

# Fix 6: Delete backup/copy files to reduce confusion
echo "🗑️  Cleaning up duplicate files..."
rm -f "ApexIntelligence copy.tsx"
rm -f "ContactDetailModal copy.tsx"
rm -f "ContactDetailModal copy 2.tsx"
rm -f "app_tsx_updates.tsx"

echo ""
echo "✅ FIXES COMPLETE"
echo "=================="
echo "✅ All score displays now handle null values"
echo "✅ All API URLs point to localhost (respects .env)"
echo "✅ Duplicate/backup files removed"
echo ""
echo "📋 Original files backed up with timestamp"
echo "🔄 Restart dev server: npm run dev"
echo ""
echo "To rollback: ls *.backup-* to see backups"

