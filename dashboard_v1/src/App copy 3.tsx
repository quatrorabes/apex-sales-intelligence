import React, { useState, useEffect } from 'react';
import {
  ChevronUp,
  ChevronDown,
  Search,
  Download,
  Users,
  Gauge,
  Activity,
  Sparkles,
  Database,
} from 'lucide-react';

import ApexIntelligence from "./components/ApexIntelligence";
import CadenceDashboard from "./components/CadenceDashboard";
import ContactEnrichmentView from "./components/ContactEnrichmentView";
import RawDataViewer from "./components/RawDataViewer";
import ContactDetailModal from "./components/ContactDetailModal";
import WhyMeTab from './components/WhyMeTab';


type MainTabId = 'contacts' | 'apex' | 'cadence' | 'enrichment' | 'raw';

interface MainTab {
  id: MainTabId;
  label: string;
  description: string;
  icon: React.ComponentType<{ size?: number }>;
}

const MAIN_TABS: MainTab[] = [
  {
    id: 'contacts',
    label: 'All Contacts',
    description: 'Scored contact list with MDCP/RSS/priority',
    icon: Users,
  },
  {
    id: 'apex',import WhyMeTab from './components/WhyMeTab';
    label: 'Apex Intelligence',
    description: 'CRE-focused scoring and urgency board',
    icon: Gauge,
  },
  {
    id: 'cadence',
    label: 'Cadence',
    description: 'Outreach sequencing and prioritization',
    icon: Activity,
  },
  {
    id: 'enrichment',
    label: 'Enrichment',
    description: 'Enhanced Perplexity + OpenAI research view',
    icon: Sparkles,
  },
  {
    id: 'raw',
    label: 'Raw Data',
    description: 'Full JSON / HubSpot raw contact data',
    icon: Database,
  },
];

// ---------- HUBSPOT IMPORT BUTTON ----------

function HubSpotImportButton() {
  const [importing, setImporting] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleImport = async () => {
    setImporting(true);
    setResult(null);
    
    try {
      const res = await fetch('http://localhost:8000/api/hubspot/import', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      });
      
      const data = await res.json();
      setResult(data);
      
      // Auto-hide success message after 5 seconds
      if (data.success) {
        setTimeout(() => setResult(null), 5000);
      }
    } catch (err) {
      setResult({ 
        success: false, 
        error: 'Network error', 
        message: String(err) 
      });
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
          background: importing 
            ? 'rgba(71,85,105,0.5)' 
            : 'linear-gradient(135deg, rgba(79,70,229,0.5), rgba(99,102,241,0.4))',
          color: '#e5e7eb',
          fontSize: 14,
          fontWeight: 600,
          cursor: importing ? 'not-allowed' : 'pointer',
          transition: 'all 0.2s',
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
            background: result.success 
              ? 'rgba(22,163,74,0.15)' 
              : 'rgba(220,38,38,0.15)',
            border: `1px solid ${result.success ? 'rgba(22,163,74,0.5)' : 'rgba(220,38,38,0.5)'}`,
            color: result.success ? '#22c55e' : '#f87171',
            maxWidth: 320,
          }}
        >
          {result.success ? (
            <>
              ✅ Imported {result.imported} new contacts
              {result.filtered > 0 && ` (${result.filtered} filtered)`}
            </>
          ) : (
            <>❌ {result.message || 'Import failed'}</>
          )}
        </div>
      )}
    </div>
  );
}

// ---------- ROOT APP SHELL WITH O3PRO TABS ----------

export default function App() {
  const [activeTab, setActiveTab] = useState<MainTabId>('contacts');
  const [selectedContact, setSelectedContact] = useState<Contact | null>(null);

  const current = MAIN_TABS.find((t) => t.id === activeTab)!;

  // Callback for when enrichment completes
  const handleEnrichmentComplete = async (updatedContact: Contact) => {
    console.log("Enrichment completed for:", updatedContact);
    // Close modal and refresh contact list
    setSelectedContact(null);
    // Trigger refresh in ContactsBoard (passed down as prop)
  };

  return (
    <div
      style={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #0a0f1f 0%, #1e293b 100%)',
        color: '#e5e7eb',
        fontFamily: 'system-ui, -apple-system, BlinkMacSystemFont, "Inter", sans-serif',
      }}
    >
      {/* GLOBAL HEADER */}
      <header
        style={{
          padding: '24px 32px 16px 32px',
          borderBottom: '1px solid rgba(148,163,184,0.25)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: '16px',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <div
            style={{
              width: 32,
              height: 32,
              borderRadius: 999,
              background:
                'conic-gradient(from 180deg at 50% 50%, #6366f1 0deg, #22c55e 120deg, #eab308 240deg, #6366f1 360deg)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#0f172a',
              fontWeight: 800,
              fontSize: 16,
            }}
          >
            AI
          </div>
          <div>
            <div
              style={{
                fontSize: 22,
                fontWeight: 700,
                letterSpacing: 0.4,
              }}
            >
              Apex Intelligence
            </div>
            <div style={{ fontSize: 13, color: '#9ca3af' }}>
              End-to-end AI sales intelligence · Enrichment · Scoring · Content
            </div>
          </div>
        </div>
        
        {/* HubSpot Import Button */}
        <HubSpotImportButton />
      </header>

      {/* MAIN NAV TABS */}
      <nav
        style={{
          display: 'flex',
          gap: 8,
          padding: '12px 32px 4px 32px',
          borderBottom: '1px solid rgba(148,163,184,0.25)',
          background: 'rgba(15,23,42,0.85)',
          backdropFilter: 'blur(12px)',
          position: 'sticky',
          top: 0,
          zIndex: 50,
        }}
      >
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
                borderRadius: '999px',
                border: active
                  ? '1px solid rgba(129,140,248,0.9)'
                  : '1px solid rgba(148,163,184,0.35)',
                background: active
                  ? 'linear-gradient(135deg, rgba(79,70,229,0.35), rgba(147,51,234,0.35))'
                  : 'transparent',
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

      {/* CURRENT TAB DESCRIPTION */}
      <div
        style={{
          padding: '12px 32px 8px 32px',
          fontSize: 12,
          color: '#9ca3af',
        }}
      >
        {current.description}
      </div>

      {/* TAB CONTENT AREA */}
      <main style={{ padding: '0 24px 32px 24px' }}>
        {activeTab === 'contacts' && (
          <ContactsBoard 
            selectedContact={selectedContact}
            onSelectContact={setSelectedContact}
          />
        )}
        {activeTab === 'apex' && (
          <div
            style={{
              marginTop: 16,
              borderRadius: 16,
              overflow: 'hidden',
              background: '#020617',
            }}
          >
            <ApexIntelligence />
          </div>
        )}
        {activeTab === 'cadence' && (
          <div
            style={{
              marginTop: 16,
              borderRadius: 16,
              overflow: 'hidden',
              background: '#020617',
            }}
          >
            <CadenceDashboard />
          </div>
        )}
        {activeTab === 'enrichment' && (
          <div
            style={{
              marginTop: 16,
              borderRadius: 16,
              overflow: 'hidden',
              background: '#020617',
            }}
          >
            <ContactEnrichmentView />
          </div>
        )}
        {activeTab === 'raw' && (
          <div
            style={{
              marginTop: 16,
              borderRadius: 16,
              overflow: 'hidden',
              background: '#020617',
            }}
          >
            <RawDataViewer />
          </div>
        )}
      </main>

      {/* CONTACT DETAIL MODAL */}
      {selectedContact && (
        <ContactDetailModal
          contact={selectedContact}
          onClose={() => setSelectedContact(null)}
          onEnrichmentComplete={handleEnrichmentComplete}
        />
      )}
    </div>
  );
}

// ---------- CONTACTS BOARD (YOUR DARK MAIN DASH) ----------

interface Contact {
  id: number;
  name: string;
  email: string;
  phone: string;
  company: string;
  title: string;
  lead_status?: string;
  lifecycle_stage?: string;
  mdcp_score?: number;
  rss_score?: number;
  priority_score?: number;
  urgency_level?: string;
  mdcp_tier?: string;
  rss_tier?: string;
  enrichment_status?: string;
  profile_content?: string;
}

type SortField =
  | 'name'
  | 'title'
  | 'company'
  | 'lifecycle_stage'
  | 'lead_status'
  | 'priority_score'
  | 'mdcp_score'
  | 'rss_score';

interface ContactsBoardProps {
  selectedContact: Contact | null;
  onSelectContact: (contact: Contact) => void;
}

function ContactsBoard({ selectedContact, onSelectContact }: ContactsBoardProps) {
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [loading, setLoading] = useState(true);
  const [sortField, setSortField] = useState<SortField>('priority_score');
  const [sortDir, setSortDir] = useState<'asc' | 'desc'>('desc');
  const [searchTerm, setSearchTerm] = useState('');
  const [filterTier, setFilterTier] = useState<string>('all');

  useEffect(() => {
    fetchContacts();
  }, []);

  const fetchContacts = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/contacts');
      const data = await res.json();
      // backend returns a flat list in many places; support either shape
      setContacts((data.contacts as Contact[]) || (data as Contact[]) || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDir(sortDir === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDir('desc');
    }
  };

  const filtered = contacts.filter((c) => {
    const q = searchTerm.toLowerCase();
    const matchesSearch =
      c.name.toLowerCase().includes(q) ||
      c.company?.toLowerCase().includes(q) ||
      c.email?.toLowerCase().includes(q) ||
      c.title?.toLowerCase().includes(q);

    const matchesTier = filterTier === 'all' || c.mdcp_tier === filterTier;

    return matchesSearch && matchesTier;
  });

  const sorted = [...filtered].sort((a, b) => {
    let aVal: any = a[sortField];
    let bVal: any = b[sortField];
    if (aVal == null) aVal = sortDir === 'asc' ? Infinity : -Infinity;
    if (bVal == null) bVal = sortDir === 'asc' ? Infinity : -Infinity;
    if (typeof aVal === 'string') {
      aVal = aVal.toLowerCase();
      bVal = (bVal as string | undefined)?.toLowerCase() || '';
    }
    if (aVal < bVal) return sortDir === 'asc' ? -1 : 1;
    if (aVal > bVal) return sortDir === 'asc' ? 1 : -1;
    return 0;
  });

  const stats = [
    { label: 'Total Contacts', value: contacts.length, color: '#6366f1' },
    {
      label: 'HOT Leads',
      value: contacts.filter((c) => c.mdcp_tier === 'HOT').length,
      color: '#22c55e',
    },
    {
      label: 'Warm',
      value: contacts.filter((c) => c.mdcp_tier === 'WARM').length,
      color: '#f97316',
    },
    {
      label: 'Scored',
      value: contacts.filter((c) => c.priority_score != null).length,
      color: '#0ea5e9',
    },
  ];

  if (loading) {
    return (
      <div
        style={{
          height: '70vh',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: '#9ca3af',
          fontSize: 18,
        }}
      >
        Loading contacts…
      </div>
    );
  }

  return (
    <div style={{ padding: '16px 8px 0 8px' }}>
      {/* Stats */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
          gap: 16,
          marginBottom: 24,
        }}
      >
        {stats.map((s) => (
          <div
            key={s.label}
            style={{
              background: 'rgba(15,23,42,0.9)',
              borderRadius: 12,
              padding: 16,
              border: '1px solid rgba(148,163,184,0.35)',
              boxShadow: '0 6px 20px rgba(0,0,0,0.35)',
            }}
          >
            <div
              style={{
                fontSize: 11,
                textTransform: 'uppercase',
                letterSpacing: 0.6,
                color: '#9ca3af',
                marginBottom: 6,
              }}
            >
              {s.label}
            </div>
            <div style={{ fontSize: 26, fontWeight: 700, color: s.color }}>
              {s.value}
            </div>
          </div>
        ))}
      </div>

      {/* Search + Tier Filter */}
      <div
        style={{
          display: 'flex',
          gap: 12,
          marginBottom: 16,
          flexWrap: 'wrap',
          alignItems: 'center',
        }}
      >
        <div style={{ flex: 1, minWidth: 260, position: 'relative' }}>
          <Search
            size={18}
            style={{ position: 'absolute', left: 12, top: 10, color: '#64748b' }}
          />
          <input
            type="text"
            placeholder="Search name, company, email, or title…"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            style={{
              width: '100%',
              paddingLeft: 38,
              paddingRight: 14,
              paddingTop: 8,
              paddingBottom: 8,
              borderRadius: 8,
              border: '1px solid rgba(148,163,184,0.4)',
              background: 'rgba(15,23,42,0.85)',
              color: '#e5e7eb',
              fontSize: 14,
              outline: 'none',
            }}
          />
        </div>
        <select
          value={filterTier}
          onChange={(e) => setFilterTier(e.target.value)}
          style={{
            padding: '8px 12px',
            borderRadius: 8,
            border: '1px solid rgba(148,163,184,0.5)',
            background: 'rgba(15,23,42,0.9)',
            color: '#e5e7eb',
            fontSize: 13,
            cursor: 'pointer',
          }}
        >
          <option value="all">All tiers</option>
          <option value="HOT">🔥 HOT</option>
          <option value="WARM">🟡 WARM</option>
          <option value="COLD">❄️ COLD</option>
        </select>
        <button
          type="button"
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 6,
            padding: '8px 12px',
            borderRadius: 8,
            border: '1px solid rgba(99,102,241,0.6)',
            background: 'rgba(79,70,229,0.25)',
            color: '#e5e7eb',
            fontSize: 13,
            fontWeight: 500,
            cursor: 'pointer',
          }}
        >
          <Download size={16} />
          Export
        </button>
      </div>

      {/* Table */}
      <div
        style={{
          background: 'rgba(15,23,42,0.95)',  // This should already be dark
          borderRadius: 14,
          border: '1px solid rgba(30,64,175,0.7)',
          boxShadow: '0 20px 45px rgba(15,23,42,0.95)',
          overflow: 'hidden',
        }}
      >
        <div style={{ overflowX: 'auto' }}>
          <table
            style={{
              width: '100%',
              borderCollapse: 'collapse',
              fontSize: 13,
            }}
          >
            <thead>
              <tr
                style={{
                  background: 'rgba(15,23,42,1)',
                  borderBottom: '1px solid rgba(51,65,85,0.8)',
                }}
              >
                <SortableTh label="Name" field="name" sortField={sortField} sortDir={sortDir} onSort={handleSort} />
                <SortableTh label="Title" field="title" sortField={sortField} sortDir={sortDir} onSort={handleSort} />
                <SortableTh
                  label="Company"
                  field="company"
                  sortField={sortField}
                  sortDir={sortDir}
                  onSort={handleSort}
                />
                <SortableTh
                  label="Lifecycle"
                  field="lifecycle_stage"
                  sortField={sortField}
                  sortDir={sortDir}
                  onSort={handleSort}
                />
                <SortableTh
                  label="Status"
                  field="lead_status"
                  sortField={sortField}
                  sortDir={sortDir}
                  onSort={handleSort}
                />
                <SortableTh
                  label="Priority"
                  field="priority_score"
                  sortField={sortField}
                  sortDir={sortDir}
                  onSort={handleSort}
                />
                <SortableTh
                  label="MDCP"
                  field="mdcp_score"
                  sortField={sortField}
                  sortDir={sortDir}
                  onSort={handleSort}
                />
                <SortableTh
                  label="RSS"
                  field="rss_score"
                  sortField={sortField}
                  sortDir={sortDir}
                  onSort={handleSort}
                />
              </tr>
            </thead>
            <tbody>
              {sorted.map((c) => {
                const priorityColor = getScoreColor(c.priority_score);
                const mdcpColor = getScoreColor(c.mdcp_score);
                const rssColor = getScoreColor(c.rss_score);
                const isSelected = selectedContact?.id === c.id;
                
                return (
                  <tr
                    key={c.id}
                    onClick={() => onSelectContact(c)}
                    style={{
                      borderBottom: '1px solid rgba(31,41,55,0.9)',
                      transition: 'background 0.18s',
                      cursor: 'pointer',
                      background: isSelected 
                        ? 'rgba(33, 128, 141, 0.15)' 
                        : 'transparent',
                    }}
                    onMouseEnter={(e) => {
                      if (!isSelected) {
                        e.currentTarget.style.background = 'rgba(30,64,175,0.25)';
                      }
                    }}
                    onMouseLeave={(e) => {
                      if (!isSelected) {
                        e.currentTarget.style.background = 'transparent';
                      } else {
                        e.currentTarget.style.background = 'rgba(33, 128, 141, 0.15)';
                      }
                    }}
                  >
                    <td style={tdStyle}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                        <div
                          style={{
                            width: 32,
                            height: 32,
                            borderRadius: 999,
                            background:
                              'linear-gradient(135deg, #6366f1 0%, #4f46e5 40%, #0ea5e9 100%)',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            color: 'white',
                            fontSize: 12,
                            fontWeight: 700,
                          }}
                        >
                          {c.name
                            .split(' ')
                            .map((n) => n[0])
                            .join('')
                            .substring(0, 3)
                            .toUpperCase()}
                        </div>
                        <div>
                          <div style={{ fontWeight: 500, color: '#e5e7eb' }}>
                            {c.name}
                          </div>
                          <div style={{ fontSize: 11, color: '#9ca3af' }}>
                            {c.email}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td style={tdStyle}>{c.title || '—'}</td>
                    <td style={tdStyle}>{c.company || '—'}</td>
                    <td style={tdStyle}>
                      <span style={{ color: '#9ca3af' }}>
                        {c.lifecycle_stage || '—'}
                      </span>
                    </td>
                    <td style={tdStyle}>
                      <span style={{ color: '#9ca3af' }}>
                        {c.lead_status || '—'}
                      </span>
                    </td>
                    <td style={tdStyle}>
                      <ScorePill value={c.priority_score} colors={priorityColor} />
                    </td>
                    <td style={tdStyle}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                        <ScorePill value={c.mdcp_score} colors={mdcpColor} />
                        <TierBadge tier={c.mdcp_tier} />
                      </div>
                    </td>
                    <td style={tdStyle}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                        <ScorePill value={c.rss_score} colors={rssColor} />
                        <TierBadge tier={c.rss_tier} />
                      </div>
                    </td>
                  </tr>
                );
              })}
              {sorted.length === 0 && (
                <tr>
                  <td colSpan={8} style={{ padding: 32, textAlign: 'center', color: '#9ca3af' }}>
                    No contacts match your filters.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      <div
        style={{
          marginTop: 16,
          fontSize: 12,
          color: '#9ca3af',
          textAlign: 'right',
        }}
      >
        Showing {sorted.length} of {contacts.length} contacts
      </div>
    </div>
  );
}

// ---------- SMALL PRESENTATIONAL HELPERS ----------

function getScoreColor(score?: number) {
  if (score == null) {
    return { color: '#9ca3af', bg: 'rgba(31,41,55,0.9)' };
  }
  if (score >= 80) {
    return { color: '#22c55e', bg: 'rgba(22,163,74,0.16)' };
  }
  if (score >= 60) {
    return { color: '#f97316', bg: 'rgba(245,158,11,0.14)' };
  }
  return { color: '#f97373', bg: 'rgba(220,38,38,0.18)' };
}

function TierBadge({ tier }: { tier?: string }) {
  const map: Record<
    string,
    { bg: string; border: string; color: string }
  > = {
    HOT: {
      bg: 'rgba(22,163,74,0.12)',
      border: 'rgba(22,163,74,0.6)',
      color: '#22c55e',
    },
    WARM: {
      bg: 'rgba(245,158,11,0.10)',
      border: 'rgba(245,158,11,0.6)',
      color: '#fbbf24',
    },
    COLD: {
      bg: 'rgba(148,163,184,0.15)',
      border: 'rgba(148,163,184,0.6)',
      color: '#e5e7eb',
    },
  };
  const style = map[tier || 'COLD'] || map['COLD'];
  return (
    <span
      style={{
        padding: '3px 8px',
        borderRadius: 999,
        fontSize: 11,
        border: `1px solid ${style.border}`,
        background: style.bg,
        color: style.color,
        textTransform: 'uppercase',
        fontWeight: 600,
      }}
    >
      {tier || 'COLD'}
    </span>
  );
}

function ScorePill({
  value,
  colors,
}: {
  value?: number;
  colors: { color: string; bg: string };
}) {
  return (
    <span
      style={{
        display: 'inline-block',
        minWidth: 32,
        padding: '4px 10px',
        borderRadius: 999,
        fontSize: 13,
        textAlign: 'center',
        background: colors.bg,
        color: colors.color,
        fontWeight: 600,
      }}
    >
      {value != null ? Math.round(value) : '—'}
    </span>
  );
}

function SortableTh(props: {
  label: string;
  field: SortField;
  sortField: SortField;
  sortDir: 'asc' | 'desc';
  onSort: (field: SortField) => void;
}) {
  const { label, field, sortField, sortDir, onSort } = props;
  const active = sortField === field;
  return (
    <th
      onClick={() => onSort(field)}
      style={{
        padding: 12,
        textAlign: 'left',
        fontSize: 11,
        fontWeight: 600,
        textTransform: 'uppercase',
        letterSpacing: 0.6,
        cursor: 'pointer',
        color: active ? '#e5e7eb' : '#9ca3af',
        whiteSpace: 'nowrap',
      }}
    >
      <span style={{ display: 'inline-flex', alignItems: 'center', gap: 6 }}>
        {label}
        {active && (sortDir === 'asc' ? <ChevronUp size={14} /> : <ChevronDown size={14} />)}
      </span>
    </th>
  );
}

const tdStyle: React.CSSProperties = {
  padding: 12,
  fontSize: 13,
  color: '#e5e7eb',  // Make sure this is light
  background: 'transparent',  // Add this if missing
};

