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
        <Route path="/board" element={<TodaysBoard />} />
        <Route path="/contacts" element={<ContactsView />} />
        <Route path="/contacts/:id" element={<ContactDetail />} />
        <Route path="/queue" element={<ColdCallQueue />} />
        <Route path="/analytics" element={<Analytics />} />
        <Route path="/lists" element={<SmartLists />} />
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
