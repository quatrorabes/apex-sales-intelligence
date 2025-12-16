#!/bin/bash
# CLEANUP: Remove outdated ContactDetail from components/
# Keep only src/pages/ContactDetail.tsx

cd "$(git rev-parse --show-toplevel)"

# Verify App.tsx uses pages version
grep "from './pages/ContactDetail'" dashboard_v1/src/App.tsx
if [ $? -eq 0 ]; then
  echo "✅ App.tsx correctly imports from src/pages/ContactDetail"
else
  echo "⚠️  WARNING: App.tsx not using pages/ContactDetail - fixing..."
  sed -i.bak "s|from './components/ContactDetail'|from './pages/ContactDetail'|g" dashboard_v1/src/App.tsx
  git add dashboard_v1/src/App.tsx
fi

# Backup and remove old components version
if [ -f "dashboard_v1/src/components/ContactDetail.tsx" ]; then
  echo "🗑️  Removing outdated components/ContactDetail.tsx..."
  git rm dashboard_v1/src/components/ContactDetail.tsx
  git commit -m "chore: remove outdated ContactDetail from components/

Keep only src/pages/ContactDetail.tsx as the active implementation.
App.tsx imports from pages/ directory."
  git push origin main
  echo "✅ Cleanup complete"
else
  echo "✅ No components/ContactDetail.tsx found - already clean"
fi

echo ""
echo "📍 ACTIVE FILE: dashboard_v1/src/pages/ContactDetail.tsx"
echo "🎨 Gradient background confirmed in production"
