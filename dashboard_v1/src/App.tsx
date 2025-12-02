import React, { useState, useEffect } from 'react';
import {
  LayoutDashboard,
  Users,
  Zap,
  Beaker,
  HelpCircle,
  Menu,
  X,
  Bell,
  Settings,
  ChevronRight,
  Search,
  Plus,
  Filter,
  Download,
  Upload,
  RefreshCw,
  CheckCircle2,
  AlertCircle,
  XCircle,
  Loader2,
  Target
} from 'lucide-react';

// Components
import TodaysBoard from './components/TodaysBoard';
import ContactsBoard from './components/ContactsBoard'; // <--- Using the working board
import CadenceDashboard from './components/CadenceDashboard';
import ContentGenerator from './components/ContentGenerator';
import WhyMeTab from './components/WhyMeTab';
import ApexIntelligence from './components/ApexIntelligence';
import ContactDetailModal from './components/ContactDetailModal';
import OnboardingModal from './components/OnboardingModal';

// Config
import { API_BASE } from './config';

// Toast System
interface Toast {
  id: string;
  type: 'success' | 'error' | 'info' | 'warning';
  title: string;
  message: string;
}

const ToastContainer = ({ toasts, removeToast }: { toasts: Toast[]; removeToast: (id: string) => void }) => {
  return (
    <div
      style={{
        position: 'fixed',
        bottom: 24,
        right: 24,
        zIndex: 9999,
        display: 'flex',
        flexDirection: 'column',
        gap: 12,
      }}
    >
      {toasts.map((toast) => (
        <div
          key={toast.id}
          style={{
            background: '#1e293b',
            border: `1px solid ${
              toast.type === 'success' ? '#22c55e' :
              toast.type === 'error' ? '#ef4444' :
              toast.type === 'warning' ? '#f59e0b' : '#3b82f6'
            }`,
            borderLeft: `4px solid ${
              toast.type === 'success' ? '#22c55e' :
              toast.type === 'error' ? '#ef4444' :
              toast.type === 'warning' ? '#f59e0b' : '#3b82f6'
            }`,
            borderRadius: 8,
            padding: '16px',
            minWidth: 300,
            maxWidth: 400,
            boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.5)',
            display: 'flex',
            alignItems: 'flex-start',
            gap: 12,
            animation: 'slideIn 0.3s ease-out',
            color: '#e2e8f0'
          }}
        >
          {toast.type === 'success' && <CheckCircle2 size={20} color="#22c55e" />}
          {toast.type === 'error' && <XCircle size={20} color="#ef4444" />}
          {toast.type === 'warning' && <AlertCircle size={20} color="#f59e0b" />}
          {toast.type === 'info' && <AlertCircle size={20} color="#3b82f6" />}
          
          <div style={{ flex: 1 }}>
            <h4 style={{ margin: '0 0 4px', fontSize: 14, fontWeight: 600 }}>{toast.title}</h4>
            <p style={{ margin: 0, fontSize: 13, color: '#94a3b8' }}>{toast.message}</p>
          </div>
          
          <button 
            onClick={() => removeToast(toast.id)}
            style={{ background: 'transparent', border: 'none', color: '#64748b', cursor: 'pointer', padding: 0 }}
          >
            <X size={16} />
          </button>
        </div>
      ))}
      <style>{`
        @keyframes slideIn {
          from { transform: translateX(100%); opacity: 0; }
          to { transform: translateX(0); opacity: 1; }
        }
      `}</style>
    </div>
  );
};

// Main App Component
function App() {
  // --- STATE ---
  const [activeTab, setActiveTab] = useState('today');
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [showOnboarding, setShowOnboarding] = useState(false);
  const [selectedContact, setSelectedContact] = useState<any | null>(null);
  const [toasts, setToasts] = useState<Toast[]>([]);
  const [importLoading, setImportLoading] = useState(false);

  // --- EFFECTS ---
  useEffect(() => {
    const hasSeenOnboarding = localStorage.getItem('apex_has_seen_onboarding');
    if (!hasSeenOnboarding) {
      setShowOnboarding(true);
    }
  }, []);

  // --- HELPERS ---
  const addToast = (type: Toast['type'], title: string, message: string) => {
    const id = Math.random().toString(36).substring(2, 9);
    setToasts((prev) => [...prev, { id, type, title, message }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 5000);
  };

  const removeToast = (id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  };

  const handleHubSpotImport = async () => {
    setImportLoading(true);
    addToast('info', 'Import Started', 'Connecting to HubSpot...');
    
    try {
      const response = await fetch(`${API_BASE}/api/hubspot/import`, { method: 'POST' });
      const data = await response.json();
      
      if (data.success) {
        addToast('success', 'Import Complete', `Successfully imported contacts.`);
        window.dispatchEvent(new Event('contacts-updated'));
      } else {
        throw new Error(data.error || 'Import failed');
      }
    } catch (error: any) {
      console.error('Import error:', error);
      addToast('error', 'Import Failed', error.message || 'Could not connect to HubSpot');
    } finally {
      setImportLoading(false);
    }
  };

  const handleContactSelect = (contact: any) => {
    console.log('[App] Selected Contact:', contact);
    setSelectedContact(contact);
  };

  const handleEnrichmentComplete = (updatedContact: any) => {
    console.log('[App] Enrichment Complete:', updatedContact);
    setSelectedContact(updatedContact);
    addToast('success', 'Enrichment Complete', `${updatedContact.name} has been enriched.`);
    window.dispatchEvent(new Event('contacts-updated'));
  };

  // --- RENDER CONTENT ---
  const renderContent = () => {
    switch (activeTab) {
      case 'today':
        return <TodaysBoard onContactSelect={handleContactSelect} />;
      case 'contacts':
        // This uses the simple, working table we made, but inside the "good" App shell
        return <ContactsBoard />;
      case 'cadence':
        return <CadenceDashboard />;
      case 'lab':
        return <ContentGenerator />;
      case 'why':
        return <WhyMeTab />;
      case 'apex':
        return <ApexIntelligence />;
      default:
        return <TodaysBoard onContactSelect={handleContactSelect} />;
    }
  };

  // --- RENDER UI ---
  return (
    <div style={{ 
      minHeight: '100vh', 
      background: '#0f172a', 
      color: '#f8fafc',
      fontFamily: '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
    }}>
      
      {/* HEADER / NAV */}
      <header style={{
        position: 'sticky',
        top: 0,
        zIndex: 50,
        background: 'rgba(15, 23, 42, 0.8)',
        backdropFilter: 'blur(12px)',
        borderBottom: '1px solid rgba(51, 65, 85, 0.5)'
      }}>
        <div style={{
          maxWidth: 1600,
          margin: '0 auto',
          padding: '0 24px',
          height: 72,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between'
        }}>
          
          {/* Logo & Title */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
            <div style={{
              width: 40,
              height: 40,
              background: 'linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%)',
              borderRadius: 10,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 0 20px rgba(79, 70, 229, 0.3)'
            }}>
              <Zap size={24} color="white" fill="white" />
            </div>
            <div>
              <h1 style={{ 
                fontSize: 20, 
                fontWeight: 700, 
                letterSpacing: '-0.02em',
                margin: 0,
                background: 'linear-gradient(to right, #fff, #94a3b8)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent'
              }}>
                Apex Intelligence
              </h1>
              <span style={{ fontSize: 11, color: '#64748b', fontWeight: 500, letterSpacing: '0.05em', textTransform: 'uppercase' }}>
                Sales Intelligence Platform
              </span>
            </div>
          </div>

          {/* Desktop Nav */}
          <nav style={{ display: 'flex', gap: 8, background: '#1e293b', padding: '4px', borderRadius: 99, border: '1px solid #334155' }} className="hidden md:flex">
            {[
              { id: 'today', label: "Today's Board", icon: LayoutDashboard },
              { id: 'contacts', label: 'All Contacts', icon: Users },
              { id: 'cadence', label: 'Cadence', icon: ActivityIcon },
              { id: 'lab', label: 'Intelligence Lab', icon: Beaker },
              { id: 'why', label: 'Why Me?', icon: HelpCircle },
              { id: 'apex', label: 'Apex Intelligence', icon: Zap },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 8,
                  padding: '8px 16px',
                  borderRadius: 99,
                  border: 'none',
                  background: activeTab === tab.id ? '#334155' : 'transparent',
                  color: activeTab === tab.id ? '#fff' : '#94a3b8',
                  fontSize: 13,
                  fontWeight: 600,
                  cursor: 'pointer',
                  transition: 'all 0.2s ease'
                }}
              >
                <tab.icon size={16} />
                {tab.label}
              </button>
            ))}
          </nav>

          {/* Right Actions */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
            <button
              onClick={handleHubSpotImport}
              disabled={importLoading}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 8,
                padding: '8px 16px',
                borderRadius: 8,
                border: '1px solid rgba(99, 102, 241, 0.5)',
                background: 'rgba(79, 70, 229, 0.1)',
                color: '#818cf8',
                fontSize: 13,
                fontWeight: 600,
                cursor: importLoading ? 'not-allowed' : 'pointer',
                transition: 'all 0.2s ease'
              }}
            >
              {importLoading ? <Loader2 size={16} className="animate-spin" /> : <Upload size={16} />}
              {importLoading ? 'Importing...' : 'Import from HubSpot'}
            </button>

            <div style={{ width: 1, height: 24, background: '#334155' }} />

            <button style={{ background: 'transparent', border: 'none', color: '#64748b', cursor: 'pointer' }}>
              <Bell size={20} />
            </button>
            <button style={{ background: 'transparent', border: 'none', color: '#64748b', cursor: 'pointer' }}>
              <Settings size={20} />
            </button>
          </div>
        </div>
      </header>

      {/* MAIN CONTENT AREA */}
      <main style={{ 
        maxWidth: 1600, 
        margin: '0 auto', 
        padding: '32px 24px',
        animation: 'fadeIn 0.4s ease-out'
      }}>
        {renderContent()}
      </main>

      {/* MODALS & OVERLAYS */}
      {showOnboarding && (
        <OnboardingModal onClose={() => setShowOnboarding(false)} />
      )}

      {selectedContact && (
        <ContactDetailModal
          contact={selectedContact}
          onClose={() => setSelectedContact(null)}
          onEnrichmentComplete={handleEnrichmentComplete}
        />
      )}

      <ToastContainer toasts={toasts} removeToast={removeToast} />

      <style>{`
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(10px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .animate-spin {
          animation: spin 1s linear infinite;
        }
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
        @media (max-width: 768px) {
          .hidden.md\\:flex { display: none !important; }
        }
      `}</style>
    </div>
  );
}

// Helper icon component since 'Activity' wasn't imported or conflicts
const ActivityIcon = ({ size, ...props }: any) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    {...props}
  >
    <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
  </svg>
);

export default App;
