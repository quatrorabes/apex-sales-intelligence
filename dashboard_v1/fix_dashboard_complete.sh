#!/bin/bash

echo "🔧 APEX Dashboard - Complete Cleanup Script v2"
echo "==============================================="

cd src/components

# Backup all files first
echo "📦 Creating backups..."
for file in *.tsx; do
  [ -f "$file" ] && cp "$file" "${file}.backup-complete"
done

# Fix 1: Replace ALL Railway URLs with localhost in one pass
echo "🌐 Fixing all API URLs..."

for file in *.tsx; do
  if grep -q "apex-intelligence-production.up.railway.app" "$file" 2>/dev/null; then
    echo "   Fixing $file..."
    
    # Use perl instead of sed (works on macOS)
    perl -i -pe 's|https://apex-intelligence-production\.up\.railway\.app|\${import.meta.env.VITE_API_URL \|\| "http://localhost:8000"}|g' "$file"
    
    # Fix template literal syntax
    perl -i -pe 's/fetch\(\$\{import\.meta\.env\.VITE_API_URL/fetch(\`\${import.meta.env.VITE_API_URL/g' "$file"
    perl -i -pe 's/8000\}\/api/8000}\`\/api/g' "$file" 2>/dev/null || true
  fi
done

# Fix 2: Score null safety
echo "🔧 Fixing score displays..."

# ScoreExplainer.tsx
if [ -f "ScoreExplainer.tsx" ]; then
  perl -i -pe 's/\{contact\.priority_score\}/\{contact.priority_score ?? 0\}/g' ScoreExplainer.tsx
  perl -i -pe 's/\{contact\.rss_score\}/\{contact.rss_score ?? 0\}/g' ScoreExplainer.tsx
  perl -i -pe 's/\{contact\.mdcp_score\}/\{contact.mdcp_score ?? 0\}/g' ScoreExplainer.tsx
fi

# ContactDetailPage.tsx
if [ -f "ContactDetailPage.tsx" ]; then
  perl -i -pe 's/score=\{contact\.priority_score\}/score=\{contact.priority_score ?? 0\}/g' ContactDetailPage.tsx
  perl -i -pe 's/score=\{contact\.rss_score\}/score=\{contact.rss_score ?? 0\}/g' ContactDetailPage.tsx
  perl -i -pe 's/score=\{contact\.mdcp_score\}/score=\{contact.mdcp_score ?? 0\}/g' ContactDetailPage.tsx
fi

# Fix 3: Delete duplicate files
echo "🗑️  Cleaning up duplicates..."
rm -f "ApexIntelligence copy.tsx"
rm -f "ContactDetailModal copy.tsx"
rm -f "ContactDetailModal copy 2.tsx"
rm -f "app_tsx_updates.tsx"

echo ""
echo "✅ FIXES COMPLETE"
echo "=================="
echo "✅ API URLs updated (check manually if template literals look correct)"
echo "✅ Score displays protected"
echo "✅ Duplicate files removed"
echo ""
echo "🔍 Files that were modified:"
grep -l "import.meta.env.VITE_API_URL" *.tsx 2>/dev/null | head -10
echo ""
echo "🔄 Restart: npm run dev"

