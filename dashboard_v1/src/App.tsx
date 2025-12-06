import { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, useNavigate } from 'react-router-dom';
import LandingPage from './components/LandingPage';
import TodaysBoard from './components/TodaysBoard';
import ContactsView from './components/ContactsView';
import ContactDetail from './components/ContactDetail';
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
            // ⌘K - Global Search
            if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
                e.preventDefault();
                setSearchOpen(true);
            }
            // ⌘J - AI Command Bar
            if ((e.metaKey || e.ctrlKey) && e.key === 'j') {
                e.preventDefault();
                setCommandOpen(true);
            }
            // ? - Keyboard Shortcuts
            if (e.key === '?' && !e.metaKey && !e.ctrlKey) {
                const target = e.target as HTMLElement;
                if (target.tagName !== 'INPUT' && target.tagName !== 'TEXTAREA') {
                    e.preventDefault();
                    setShortcutsOpen(true);
                }
            }
            // Escape
            if (e.key === 'Escape') {
                setSearchOpen(false);
                setCommandOpen(false);
                setShortcutsOpen(false);
                setImportOpen(false);
            }
            // G + Key navigation (when no modal open)
            if (!searchOpen && !commandOpen && !shortcutsOpen) {
                const target = e.target as HTMLElement;
                if (target.tagName !== 'INPUT' && target.tagName !== 'TEXTAREA') {
                    if (e.key === 'g') {
                        // Wait for next key
                        const handler = (e2: KeyboardEvent) => {
                            if (e2.key === 'h') navigate('/');
                            if (e2.key === 'c') navigate('/contacts');
                            if (e2.key === 'a') navigate('/analytics');
                            if (e2.key === 'q') navigate('/cold-call');
                            if (e2.key === 's') navigate('/smart-lists');
                            if (e2.key === 'b') navigate('/board');
                            document.removeEventListener('keydown', handler);
                        };
                        document.addEventListener('keydown', handler, { once: true });
                        setTimeout(() => document.removeEventListener('keydown', handler), 1000);
                    }
                    // Number keys for view switching (on contacts page)
                    if (window.location.pathname === '/contacts') {
                        if (e.key === '1') navigate('/contacts?view=table');
                        if (e.key === '2') navigate('/contacts?view=cards');
                        if (e.key === '3') navigate('/contacts?view=kanban');
                        if (e.key === '4') navigate('/contacts?view=compact');
                    }
                    // I - Import
                    if (e.key === 'i' && !e.metaKey) {
                        setImportOpen(true);
                    }
                }
            }
        };

        document.addEventListener('keydown', handleKeyDown);
        return () => document.removeEventListener('keydown', handleKeyDown);
    }, [navigate, searchOpen, commandOpen, shortcutsOpen]);

    return (
        <>
            <GlobalSearch isOpen={searchOpen} onClose={() => setSearchOpen(false)} />
            <CommandBar isOpen={commandOpen} onClose={() => setCommandOpen(false)} />
            <KeyboardShortcuts isOpen={shortcutsOpen} onClose={() => setShortcutsOpen(false)} />
            <ImportWizard 
                isOpen={importOpen} 
                onClose={() => setImportOpen(false)}
                onComplete={() => navigate('/contacts')}
            />
            <Routes>
                <Route path="/" element={<LandingPage />} />
                <Route path="/board" element={<TodaysBoard />} />
                <Route path="/contacts" element={<ContactsView />} />
                <Route path="/contacts/:id" element={<ContactDetail />} />
                <Route path="/cold-call" element={<ColdCallQueue />} />
                <Route path="/analytics" element={<Analytics />} />
                <Route path="/smart-lists" element={<SmartLists />} />
                <Route path="/settings" element={<Settings />} />
            </Routes>
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
