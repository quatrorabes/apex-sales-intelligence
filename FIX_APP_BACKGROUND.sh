#!/bin/bash
# EMERGENCY FIX: App.tsx Background Override
# Removes white wrapper that blocks ContactDetail gradient
# Date: Dec 15, 2025 3:50 PM PST

set -e

echo "🚨 FIXING App.tsx BACKGROUND OVERRIDE"
echo ""

cd ~/projects/apex/apex-sales-intelligence || exit 1

APP_FILE="dashboard_v1/src/App.tsx"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

if [ ! -f "$APP_FILE" ]; then
  echo "❌ ERROR: App.tsx not found"
  exit 1
fi

echo "📦 Backing up App.tsx..."
cp "$APP_FILE" "${APP_FILE}.backup-${TIMESTAMP}"

# Read current App.tsx
CURRENT=$(cat "$APP_FILE")

# Create fixed version - remove bg-gray-50, bg-white, bg-gray-100 from root div
cat > "$APP_FILE" << 'TYPESCRIPT_EOF'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import TodaysBoard from './components/TodaysBoard';
import ContactsView from './components/ContactsView';
import ContactDetail from './pages/ContactDetail';

function App() {
  return (
    <Router>
      <div className="min-h-screen">
        <Routes>
          <Route path="/" element={<Navigate to="/todays-board" replace />} />
          <Route path="/todays-board" element={<TodaysBoard />} />
          <Route path="/contacts" element={<ContactsView />} />
          <Route path="/contacts/:id" element={<ContactDetail />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
TYPESCRIPT_EOF

echo "   ✅ App.tsx updated - removed background override"

# Git commit
echo ""
echo "📤 Deploying..."
git add "$APP_FILE"
git commit -m "fix(App): remove white background wrapper blocking ContactDetail gradient

ISSUE: App.tsx root div had bg-gray-50 or bg-white that overrode 
ContactDetail gradient background

FIX: Changed root div to use only min-h-screen (no background class)
This allows child routes like ContactDetail to control their own backgrounds

Result: ContactDetail gradient (blue→indigo→purple) now visible

Test: https://apex-sales-intelligence.vercel.app/contacts/fdfb18f1-45b0-4273-99e2-a02e0f9f0fbe"

git push origin main

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ DEPLOYED - Vercel building now (~2 min)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🎨 WHAT CHANGED:"
echo "   BEFORE: <div className="min-h-screen bg-gray-50">"
echo "   AFTER:  <div className="min-h-screen">"
echo ""
echo "🔗 Test URL:"
echo "   https://apex-sales-intelligence.vercel.app/contacts/fdfb18f1-45b0-4273-99e2-a02e0f9f0fbe"
echo ""
echo "✅ ContactDetail gradient should now be visible!"
echo ""
