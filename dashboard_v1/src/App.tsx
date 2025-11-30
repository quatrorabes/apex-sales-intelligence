import React, { useState, useEffect } from 'react';
import { 
  ChevronUp, ChevronDown, Search, Download, Users, Gauge, 
  Activity, Sparkles, Database, Target, ChevronLeft, ChevronRight, Zap 
} from 'lucide-react';
import ApexIntelligence from './components/ApexIntelligence';
import CadenceDashboard from './components/CadenceDashboard';
import ContactEnrichmentView from './components/ContactEnrichmentView';
import RawDataViewer from './components/RawDataViewer';
import ContactDetailModal from './components/ContactDetailModal';
import WhyMeTab from './components/WhyMeTab';
import TodaysBoard from './components/TodaysBoard';

type MainTabId = 'board' | 'contacts' | 'cadence' | 'enrichment' | 'raw' | 'whyme';

interface MainTab {
  id: MainTabId;
  label: string;
  description: string;
  icon: React.ComponentType<{ size?: number }>;
}

interface Contact {
  id: number;
  name: string;
  email: string;
  phone: string;
  company: string;
  title: string;
  lead_status?: string;
  lifecycle_stage?: string;
  lifecyclestage?: string;
  mdcp_score?: number;
  rss_score?: number;
  priority_score?: number;
  urgency_level?: string;
  mdcp_tier?: string;
  rss_tier?: string;
  enrichment_status?: string;
  profile_content?: string;
  call_script_1?: string;
  email_1_body?: string;
  linkedin_connect?: string;
}

type SortField = 'name' | 'title' | 'company' | 'lifecycle_stage' | 'lead_status' | 'priority_score' | 'mdcp_score' | 'rss_score';

const MAIN_TABS: MainTab[] = [
  { id: 'board', label: "Today's Board", description: 'Your prioritized action list - who to call, when, and why', icon: Zap },
  { id: 'contacts', label: 'All Contacts', description: 'Full contact database with search and filters', icon: Users },
  { id: 'cadence', label: 'Cadence', description: 'Automated outreach sequences', icon: Activity },
  { id: 'enrichment', label: 'Intelligence Lab', description: 'Deep enrichment and research tools', icon: Sparkles },
  { id: 'raw', label: 'Raw Data', description: 'Full JSON HubSpot data', icon: Database },
  { id: 'whyme', label: 'Why Me?', description: 'Value proposition builder', icon: Target },
];

// ---------- HUBSPOT IMPORT BUTTON ----------
function HubSpotImportButton({ onImportComplete }: { onImportComplete?: () => void }) {
  const [importing, setImporting] = useState(false);
  const [result, setResult] = useState<any>(null);
  
  const handleImport = async () => {
    setImporting(true);
    setResult(null);
    try {
      const res = await fetch('https://apex-intelligence-production.up.railway.app/api/hubspot/import', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      });
      const data = await res.json();
      setResult(data);
      if (data.success) {
        onImportComplete?.();
        setTimeout(() => setResult(null), 5000);
      }
    } catch (err) {
      setResult({ success: false, error: 'Network error', message: String(err) });
    } finally {
      setImporting(false);
    }
  };
  
  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: 8 }}>
      <button
        onClick={handleImport}
        disabled={importing}
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: 8,
          padding: '10px 18px',
          borderRadius: 8,
          border: '1px solid rgba(99,102,241,0.7)',
          background: importing ? 'rgba(71,85,105,0.5)' : 'linear-gradient(135deg, rgba(79,70,229,0.5), rgba(99,102,241,0.4))',
          color: '#e5e7eb',
          fontSize: 14,
          fontWeight: 600,
          cursor: importing ? 'not-allowed' : 'pointer',
          boxShadow: importing ? 'none' : '0 4px 12px rgba(99,102,241,0.3)',
        }}
      >
        <Database size={18} />
        {importing ? 'Importing from HubSpot...' : 'Import from HubSpot'}
      </button>
      {result && (
        <div
          style={{
            padding: '8px 14px',
            borderRadius: 6,
            fontSize: 12,
            fontWeight: 500,
            background: result.success ? 'rgba(22,163,74,0.15)' : 'rgba(220,38,38,0.15)',
            border: result.success ? '1px solid rgba(22,163,74,0.5)' : '1px solid rgba(220,38,38,0.5)',
            color: result.success ? '#22c55e' : '#f87171',
          }}
        >
          {result.success ? `Imported ${result.imported} new contacts` : result.message || 'Import failed'}
        </div>
      )}
    </div>
  );
}

// ---------- CONTACTS BOARD WITH PAGINATION AND ENRICHMENT HIGHLIGHTING ----------
interface ContactsBoardProps {
  selectedContact: Contact | null;
  onSelectContact: (contact: Contact) => void;
  refreshTrigger?: number;
}

function ContactsBoard({ selectedContact, onSelectContact, refreshTrigger }: ContactsBoardProps) {
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [loading, setLoading] = useState(true);
  const [sortField, setSortField] = useState<SortField>('priority_score');
  const [sortDir, setSortDir] = useState<'asc' | 'desc'>('desc');
  const [searchTerm, setSearchTerm] = useState('');
  const [filterTier, setFilterTier] = useState<string>('all');
  const [filterEnriched, setFilterEnriched] = useState<string>('all');
  
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(50);
  
  const fetchContacts = async () => {
    try {
      setLoading(true);
      const res = await fetch('https://apex-intelligence-production.up.railway.app/api/contacts?limit=500');
      const data = await res.json();
      setContacts(data.contacts || data);
    } catch (err) {
      console.error('Failed to fetch contacts', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchContacts();
  }, [refreshTrigger]);

  useEffect(() => {
    setCurrentPage(1);
  }, [searchTerm, filterTier, filterEnriched, sortField, sortDir]);

  const filteredContacts = contacts
    .filter((c) => {
      const term = searchTerm.toLowerCase();
      const matchesSearch = !term || 
        c.name?.toLowerCase().includes(term) ||
        c.email?.toLowerCase().includes(term) ||
        c.company?.toLowerCase().includes(term) ||
        c.title?.toLowerCase().includes(term);
      
      const matchesTier = filterTier === 'all' || 
        c.mdcp_tier === filterTier ||
        c.rss_tier === filterTier;
      
      const isEnriched = c.enrichment_status === 'completed' || (c.profile_content && c.profile_content.length > 100);
      const matchesEnrichment = filterEnriched === 'all' || 
        (filterEnriched === 'enriched' && isEnriched) ||
        (filterEnriched === 'unenriched' && !isEnriched);
      
      return matchesSearch && matchesTier && matchesEnrichment;
    })
    .sort((a, b) => {
      const aVal = a[sortField] ?? '';
      const bVal = b[sortField] ?? '';
      const cmp = aVal < bVal ? -1 : aVal > bVal ? 1 : 0;
      return sortDir === 'asc' ? cmp : -cmp;
    });

  const totalContacts = filteredContacts.length;
  const totalPages = Math.ceil(totalContacts / pageSize);
  const startIndex = (currentPage - 1) * pageSize;
  const endIndex = startIndex + pageSize;
  const paginatedContacts = filteredContacts.slice(startIndex, endIndex);

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDir(sortDir === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDir('desc');
    }
  };

  const goToPage = (page: number) => {
    setCurrentPage(Math.max(1, Math.min(page, totalPages)));
  };

  if (loading) {
    return (
      <div style={{ marginTop: 24, padding: 48, textAlign: 'center', color: '#9ca3af' }}>
        <div style={{ fontSize: 18, fontWeight: 600 }}>Loading contacts...</div>
      </div>
    );
  }

  return (
    <div style={{ marginTop: 16 }}>
      {/* FILTERS */}
      <div style={{ display: 'flex', gap: 12, marginBottom: 16, alignItems: 'center', flexWrap: 'wrap' }}>
        <div style={{ position: 'relative', flex: 1, minWidth: 250 }}>
          <Search size={18} style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)', color: '#9ca3af' }} />
          <input
            type="text"
            placeholder="Search contacts..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            style={{
              width: '100%',
              padding: '10px 12px 10px 40px',
              borderRadius: 8,
              border: '1px solid rgba(148,163,184,0.3)',
              background: 'rgba(15,23,42,0.6)',
              color: '#e5e7eb',
              fontSize: 14,
            }}
          />
        </div>
        <select
          value={filterTier}
          onChange={(e) => setFilterTier(e.target.value)}
          style={{
            padding: '10px 14px',
            borderRadius: 8,
            border: '1px solid rgba(148,163,184,0.3)',
            background: 'rgba(15,23,42,0.6)',
            color: '#e5e7eb',
            fontSize: 14,
          }}
        >
          <option value="all">All Tiers</option>
          <option value="Platinum">Platinum</option>
          <option value="Gold">Gold</option>
          <option value="Silver">Silver</option>
          <option value="Bronze">Bronze</option>
        </select>
        <select
          value={filterEnriched}
          onChange={(e) => setFilterEnriched(e.target.value)}
          style={{
            padding: '10px 14px',
            borderRadius: 8,
            border: '1px solid rgba(148,163,184,0.3)',
            background: 'rgba(15,23,42,0.6)',
            color: '#e5e7eb',
            fontSize: 14,
          }}
        >
          <option value="all">All Contacts</option>
          <option value="enriched">✅ Enriched Only</option>
          <option value="unenriched">⏳ Unenriched Only</option>
        </select>
        <select
          value={pageSize}
          onChange={(e) => {
            setPageSize(Number(e.target.value));
            setCurrentPage(1);
          }}
          style={{
            padding: '10px 14px',
            borderRadius: 8,
            border: '1px solid rgba(148,163,184,0.3)',
            background: 'rgba(15,23,42,0.6)',
            color: '#e5e7eb',
            fontSize: 14,
          }}
        >
          <option value="25">25 per page</option>
          <option value="50">50 per page</option>
          <option value="100">100 per page</option>
          <option value="200">200 per page</option>
        </select>
      </div>

      <div style={{ marginBottom: 12, fontSize: 13, color: '#9ca3af' }}>
        Showing {startIndex + 1}-{Math.min(endIndex, totalContacts)} of {totalContacts} contacts
        {totalPages > 1 && ` (Page ${currentPage} of ${totalPages})`}
      </div>

      {/* TABLE */}
      <div style={{ background: '#020617', borderRadius: 16, overflow: 'hidden', border: '1px solid rgba(148,163,184,0.2)' }}>
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid rgba(148,163,184,0.25)', background: 'rgba(30,41,59,0.5)' }}>
                {[
                  { field: 'name' as SortField, label: 'Contact' },
                  { field: 'title' as SortField, label: 'Title' },
                  { field: 'company' as SortField, label: 'Company' },
                  { field: 'lifecycle_stage' as SortField, label: 'Stage' },
                  { field: 'priority_score' as SortField, label: 'Priority' },
                  { field: 'mdcp_score' as SortField, label: 'MDCP' },
                  { field: 'rss_score' as SortField, label: 'RSS' },
                ].map(({ field, label }) => (
                  <th
                    key={field}
                    onClick={() => handleSort(field)}
                    style={{
                      padding: '14px 16px',
                      textAlign: 'left',
                      fontSize: 12,
                      fontWeight: 600,
                      color: '#9ca3af',
                      cursor: 'pointer',
                      userSelect: 'none',
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                      {label}
                      {sortField === field && (sortDir === 'asc' ? <ChevronUp size={14} /> : <ChevronDown size={14} />)}
                    </div>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {paginatedContacts.length === 0 ? (
                <tr>
                  <td colSpan={7} style={{ padding: 32, textAlign: 'center', color: '#9ca3af' }}>
                    No contacts match your filters.
                  </td>
                </tr>
              ) : (
                paginatedContacts.map((c) => {
                  const isEnriched = c.enrichment_status === 'completed' || (c.profile_content && c.profile_content.length > 100);
                  
                  return (
                    <tr
                      key={c.id}
                      onClick={() => {
                        console.log('🖱️ Contact clicked:', { id: c.id, name: c.name });
                        onSelectContact(c);
                      }}
                      style={{
                        borderBottom: '1px solid rgba(148,163,184,0.15)',
                        cursor: 'pointer',
                        transition: 'all 0.15s',
                        background: selectedContact?.id === c.id 
                          ? 'rgba(99,102,241,0.15)' 
                          : isEnriched 
                            ? 'rgba(34,197,94,0.08)' 
                            : 'transparent',
                        borderLeft: isEnriched ? '3px solid rgba(34,197,94,0.6)' : '3px solid transparent',
                      }}
                      onMouseEnter={(e) => {
                        if (selectedContact?.id !== c.id) {
                          e.currentTarget.style.background = isEnriched ? 'rgba(34,197,94,0.15)' : 'rgba(30,41,59,0.6)';
                        }
                      }}
                      onMouseLeave={(e) => {
                        if (selectedContact?.id !== c.id) {
                          e.currentTarget.style.background = isEnriched ? 'rgba(34,197,94,0.08)' : 'transparent';
                        }
                      }}
                    >
                      <td style={{ padding: '14px 16px' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                          <div
                            style={{
                              width: 32,
                              height: 32,
                              borderRadius: 999,
                              background: isEnriched 
                                ? 'linear-gradient(135deg, rgba(34,197,94,0.6), rgba(22,163,74,0.6))'
                                : 'linear-gradient(135deg, rgba(99,102,241,0.6), rgba(147,51,234,0.6))',
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                              fontSize: 11,
                              fontWeight: 700,
                              color: '#e5e7eb',
                              position: 'relative',
                            }}
                          >
                            {c.name
                              .split(' ')
                              .map((n) => n[0])
                              .join('')
                              .substring(0, 3)
                              .toUpperCase()}
                            {isEnriched && (
                              <div style={{
                                position: 'absolute',
                                top: -4,
                                right: -4,
                                width: 14,
                                height: 14,
                                borderRadius: 999,
                                background: '#22c55e',
                                border: '2px solid #020617',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                              }}>
                                <Zap size={8} color="#020617" fill="#020617" />
                              </div>
                            )}
                          </div>
                          <div>
                            <div style={{ fontWeight: 600, fontSize: 14, display: 'flex', alignItems: 'center', gap: 6 }}>
                              {c.name}
                              {isEnriched && (
                                <span style={{
                                  fontSize: 10,
                                  fontWeight: 700,
                                  color: '#22c55e',
                                  background: 'rgba(34,197,94,0.15)',
                                  padding: '2px 6px',
                                  borderRadius: 4,
                                  border: '1px solid rgba(34,197,94,0.3)',
                                }}>
                                  ENRICHED
                                </span>
                              )}
                            </div>
                            <div style={{ fontSize: 12, color: '#9ca3af' }}>{c.email}</div>
                          </div>
                        </div>
                      </td>
                      <td style={{ padding: '14px 16px', fontSize: 13, color: '#cbd5e1' }}>{c.title}</td>
                      <td style={{ padding: '14px 16px', fontSize: 13, color: '#cbd5e1' }}>{c.company}</td>
                      <td style={{ padding: '14px 16px', fontSize: 13 }}>
                        <span
                          style={{
                            padding: '4px 10px',
                            borderRadius: 999,
                            background: 'rgba(99,102,241,0.2)',
                            border: '1px solid rgba(99,102,241,0.5)',
                            color: '#a5b4fc',
                            fontSize: 11,
                            fontWeight: 600,
                          }}
                        >
                          {c.lifecycle_stage || c.lifecyclestage || 'N/A'}
                        </span>
                      </td>
                      <td style={{ padding: '14px 16px', fontSize: 14, fontWeight: 600, color: '#22c55e' }}>
                        {c.priority_score?.toFixed(1) || 'N/A'}
                      </td>
                      <td style={{ padding: '14px 16px', fontSize: 14, fontWeight: 600, color: '#eab308' }}>
                        {c.mdcp_score?.toFixed(1) || 'N/A'}
                      </td>
                      <td style={{ padding: '14px 16px', fontSize: 14, fontWeight: 600, color: '#06b6d4' }}>
                        {c.rss_score?.toFixed(1) || 'N/A'}
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* PAGINATION */}
      {totalPages > 1 && (
        <div style={{ marginTop: 16, display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 16 }}>
          <button
            onClick={() => goToPage(currentPage - 1)}
            disabled={currentPage === 1}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 6,
              padding: '10px 16px',
              borderRadius: 8,
              border: '1px solid rgba(148,163,184,0.3)',
              background: currentPage === 1 ? 'rgba(71,85,105,0.3)' : 'rgba(30,41,59,0.6)',
              color: currentPage === 1 ? '#64748b' : '#e5e7eb',
              fontSize: 14,
              fontWeight: 600,
              cursor: currentPage === 1 ? 'not-allowed' : 'pointer',
            }}
          >
            <ChevronLeft size={16} />
            Previous
          </button>

          <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
            {Array.from({ length: Math.min(7, totalPages) }, (_, i) => {
              let pageNum: number;
              if (totalPages <= 7) {
                pageNum = i + 1;
              } else if (currentPage <= 4) {
                pageNum = i + 1;
              } else if (currentPage >= totalPages - 3) {
                pageNum = totalPages - 6 + i;
              } else {
                pageNum = currentPage - 3 + i;
              }

              return (
                <button
                  key={pageNum}
                  onClick={() => goToPage(pageNum)}
                  style={{
                    width: 36,
                    height: 36,
                    borderRadius: 8,
                    border: currentPage === pageNum ? '1px solid rgba(99,102,241,0.9)' : '1px solid rgba(148,163,184,0.3)',
                    background: currentPage === pageNum ? 'linear-gradient(135deg, rgba(79,70,229,0.4), rgba(99,102,241,0.4))' : 'rgba(30,41,59,0.6)',
                    color: currentPage === pageNum ? '#e5e7eb' : '#9ca3af',
                    fontSize: 13,
                    fontWeight: 600,
                    cursor: 'pointer',
                  }}
                >
                  {pageNum}
                </button>
              );
            })}
          </div>

          <button
            onClick={() => goToPage(currentPage + 1)}
            disabled={currentPage === totalPages}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 6,
              padding: '10px 16px',
              borderRadius: 8,
              border: '1px solid rgba(148,163,184,0.3)',
              background: currentPage === totalPages ? 'rgba(71,85,105,0.3)' : 'rgba(30,41,59,0.6)',
              color: currentPage === totalPages ? '#64748b' : '#e5e7eb',
              fontSize: 14,
              fontWeight: 600,
              cursor: currentPage === totalPages ? 'not-allowed' : 'pointer',
            }}
          >
            Next
            <ChevronRight size={16} />
          </button>
        </div>
      )}
    </div>
  );
}

// ---------- ROOT APP SHELL ----------
export default function App() {
  const [activeTab, setActiveTab] = useState<MainTabId>('board');
  const [selectedContact, setSelectedContact] = useState<Contact | null>(null);
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const current = MAIN_TABS.find((t) => t.id === activeTab)!;
  
  const handleEnrichmentComplete = (updatedContact: Contact) => {
    console.log('🎉 Enrichment completed for:', {
      id: updatedContact.id,
      name: updatedContact.name,
      hasProfile: !!updatedContact.profile_content,
      profileLength: updatedContact.profile_content?.length || 0
    });
    setSelectedContact(updatedContact);
    setRefreshTrigger(p => p + 1);
  };
  
  const handleCloseModal = () => {
    setSelectedContact(null);
    setRefreshTrigger(p => p + 1);
  };
  
  const handleRefresh = () => setRefreshTrigger(p => p + 1);
  
  return (
    <div style={{ minHeight: '100vh', background: 'linear-gradient(135deg, #0a0f1f 0%, #1e293b 100%)', color: '#e5e7eb', fontFamily: "system-ui, -apple-system, BlinkMacSystemFont, 'Inter', sans-serif" }}>
      <header style={{ padding: '24px 32px 16px 32px', borderBottom: '1px solid rgba(148,163,184,0.25)', display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 16 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <div style={{ width: 32, height: 32, borderRadius: 999, background: 'conic-gradient(from 180deg at 50% 50%, #6366f1 0deg, #22c55e 120deg, #eab308 240deg, #6366f1 360deg)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#0f172a', fontWeight: 800, fontSize: 16 }}>AI</div>
          <div>
            <div style={{ fontSize: 22, fontWeight: 700, letterSpacing: 0.4 }}>Apex Intelligence</div>
            <div style={{ fontSize: 13, color: '#9ca3af' }}>End-to-end AI sales intelligence · Enrichment · Scoring · Content</div>
          </div>
        </div>
        <HubSpotImportButton onImportComplete={handleRefresh} />
      </header>
    
      <nav style={{ display: 'flex', gap: 8, padding: '12px 32px 4px 32px', borderBottom: '1px solid rgba(148,163,184,0.25)', background: 'rgba(15,23,42,0.85)', backdropFilter: 'blur(12px)', position: 'sticky', top: 0, zIndex: 50 }}>
        {MAIN_TABS.map((tab) => {
          const Icon = tab.icon;
          const active = tab.id === activeTab;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 6,
                padding: '8px 14px',
                borderRadius: 999,
                border: active ? '1px solid rgba(129,140,248,0.9)' : '1px solid rgba(148,163,184,0.35)',
                background: active ? 'linear-gradient(135deg, rgba(79,70,229,0.35), rgba(147,51,234,0.35))' : 'transparent',
                color: active ? '#e5e7eb' : '#9ca3af',
                fontSize: 13,
                fontWeight: 600,
                cursor: 'pointer',
                transition: 'all 0.18s',
              }}
            >
              <Icon size={16} />
              {tab.label}
            </button>
          );
        })}
      </nav>
    
      <div style={{ padding: '12px 32px 8px 32px', fontSize: 12, color: '#9ca3af' }}>
        {current.description}
      </div>
    
      <main style={{ padding: '0 24px 32px 24px' }}>
        {activeTab === 'board' && (
          <TodaysBoard onContactSelect={setSelectedContact} />
        )}
        {activeTab === 'contacts' && (
          <ContactsBoard
            selectedContact={selectedContact}
            onSelectContact={setSelectedContact}
            refreshTrigger={refreshTrigger}
          />
        )}
        {activeTab === 'cadence' && (
          <div style={{ marginTop: 16, borderRadius: 16, overflow: 'hidden', background: '#020617' }}>
            <CadenceDashboard />
          </div>
        )}
        {activeTab === 'enrichment' && (
          <div style={{ marginTop: 16, borderRadius: 16, overflow: 'hidden', background: '#020617' }}>
            <ContactEnrichmentView />
          </div>
        )}
        {activeTab === 'raw' && (
          <div style={{ marginTop: 16, borderRadius: 16, overflow: 'hidden', background: '#020617' }}>
            <RawDataViewer />
          </div>
        )}
        {activeTab === 'whyme' && (
          <div style={{ marginTop: 16, borderRadius: 16, overflow: 'hidden', background: '#020617' }}>
            <WhyMeTab />
          </div>
        )}
      </main>
    
      {selectedContact && (
        <ContactDetailModal
          key={selectedContact.id}
          contact={selectedContact}
          onClose={handleCloseModal}
          onEnrichmentComplete={handleEnrichmentComplete}
        />
      )}
    </div>
  );
}
