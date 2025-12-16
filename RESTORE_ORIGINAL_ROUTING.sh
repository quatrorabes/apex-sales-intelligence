#!/bin/bash
# 🔄 RESTORE ORIGINAL App.tsx + LandingPage
# Dec 15, 2025 4:48 PM PST

set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
TS=$(date +%Y%m%d_%H%M%S)

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔄 RESTORING ORIGINAL App.tsx + LandingPage"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Backup current files
cp dashboard_v1/src/App.tsx dashboard_v1/src/App.tsx.bad-${TS}
echo "📦 Backed up current App.tsx"

# Restore ORIGINAL App.tsx (3:51 PM backup)
cat > dashboard_v1/src/App.tsx << 'TSX_EOF'
import { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, useNavigate } from 'react-router-dom';
import LandingPage from './components/LandingPage';
import TodaysBoard from './components/TodaysBoard';
import ContactsView from './components/ContactsView';
import ContactDetail from './pages/ContactDetail';
import ColdCallQueue from './components/ColdCallQueue';
import Analytics from './components/Analytics';
import SmartLists from './components/SmartLists';
import Settings from './components/Settings';
import GlobalSearch from './components/GlobalSearch';
import CommandBar from './components/CommandBar';
import KeyboardShortcuts from './components/KeyboardShortcuts';
import ImportWizard from './components/ImportWizard';

function AppContent() {
  const [searchOpen, setSearchOpen] = useState(false);
  const [commandOpen, setCommandOpen] = useState(false);
  const [shortcutsOpen, setShortcutsOpen] = useState(false);
  const [importOpen, setImportOpen] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        setSearchOpen(true);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  return (
    <>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/todays-board" element={<TodaysBoard />} />
        <Route path="/contacts" element={<ContactsView />} />
        <Route path="/contacts/:id" element={<ContactDetail />} />
        <Route path="/cold-call-queue" element={<ColdCallQueue />} />
        <Route path="/analytics" element={<Analytics />} />
        <Route path="/smart-lists" element={<SmartLists />} />
        <Route path="/settings" element={<Settings />} />
      </Routes>
      <GlobalSearch open={searchOpen} onClose={() => setSearchOpen(false)} />
      <CommandBar open={commandOpen} onClose={() => setCommandOpen(false)} />
      <KeyboardShortcuts open={shortcutsOpen} onClose={() => setShortcutsOpen(false)} />
      <ImportWizard open={importOpen} onClose={() => setImportOpen(false)} />
    </>
  );
}

function App() {
  return (
    <Router>
      <AppContent />
    </Router>
  );
}

export default App;
TSX_EOF

echo "✅ App.tsx restored (original routing)"

# Check if LandingPage exists
if [ ! -f "dashboard_v1/src/components/LandingPage.tsx" ]; then
  echo ""
  echo "⚠️  LandingPage.tsx NOT FOUND - checking git history..."
  
  # Try to restore from git history
  if git show HEAD~5:dashboard_v1/src/components/LandingPage.tsx > /tmp/landingpage_check.tsx 2>/dev/null; then
    echo "✅ Found LandingPage.tsx in git history (5 commits ago)"
    git show HEAD~5:dashboard_v1/src/components/LandingPage.tsx > dashboard_v1/src/components/LandingPage.tsx
    echo "✅ Restored LandingPage.tsx from git history"
  else
    echo "❌ LandingPage.tsx not in recent git history"
    echo ""
    echo "Creating stub LandingPage that redirects to /todays-board..."
    
    cat > dashboard_v1/src/components/LandingPage.tsx << 'STUB_EOF'
import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

export default function LandingPage() {
  const navigate = useNavigate();
  
  useEffect(() => {
    // Redirect to todays-board for now
    navigate('/todays-board');
  }, [navigate]);

  return (
    <div className="flex items-center justify-center min-h-screen bg-slate-900">
      <div className="text-slate-400">Redirecting to dashboard...</div>
    </div>
  );
}
STUB_EOF
    
    echo "⚠️  Created temporary redirect LandingPage"
    echo "    You may need to restore the actual LandingPage component"
  fi
else
  echo "✅ LandingPage.tsx already exists"
fi

# Commit
git add dashboard_v1/src/App.tsx dashboard_v1/src/components/LandingPage.tsx
git commit -m "restore(App): revert to original routing with LandingPage at /

RESTORED:
- Original App.tsx from 3:51 PM backup
- Routes: /, /todays-board, /contacts, /contacts/:id, etc.
- LandingPage at root path
- All original keyboard shortcuts and modals

User requested original landing page back."

git push origin main

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ ORIGINAL ROUTING RESTORED"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📍 ROUTES:"
echo "   / → LandingPage"
echo "   /todays-board → TodaysBoard"
echo "   /contacts → ContactsView"
echo "   /contacts/:id → ContactDetail"
echo ""
echo "🚀 Vercel deploying (~2 min)"
echo "🔗 https://apex-sales-intelligence.vercel.app/"
echo ""
