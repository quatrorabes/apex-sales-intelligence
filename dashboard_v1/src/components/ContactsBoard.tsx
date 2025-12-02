import React, { useState, useEffect, useCallback } from 'react';
import { 
  RefreshCw, Search, Filter, Download, 
  CheckCircle, Clock, AlertCircle, ChevronDown, ArrowUpDown,
  Users, Zap, Flame, Briefcase
} from 'lucide-react';
import ContactDetailModal from './ContactDetailModal';
import { API_BASE } from '../config';

interface Contact {
  id: number;
  name: string;
  email?: string;
  phone?: string;
  company?: string;
  title?: string;
  job_title?: string;
  enrichment_status?: string;
  priority_score?: number;
  mdcp_score?: number;
  persona?: string;
  lifecyclestage?: string;
  lifecycle_stage?: string;
}

export default function ContactsBoard() {
  const [allContacts, setAllContacts] = useState<Contact[]>([]);
  const [filteredContacts, setFilteredContacts] = useState<Contact[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedContact, setSelectedContact] = useState<Contact | null>(null);
  
  // Sorting state
  const [sortField, setSortField] = useState<keyof Contact>('priority_score');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('desc');

  const fetchContacts = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/api/contacts?limit=1000`);
      if (!res.ok) throw new Error(`API error: ${res.status}`);
      const data = await res.json();
      const contactList: Contact[] = Array.isArray(data) ? data : (data.contacts || []);
      setAllContacts(contactList);
      setFilteredContacts(contactList);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchContacts();
    window.addEventListener('contacts-updated', fetchContacts);
    return () => window.removeEventListener('contacts-updated', fetchContacts);
  }, [fetchContacts]);

  // Handle Search & Sort
  useEffect(() => {
    let result = [...allContacts];

    // 1. Filter
    if (searchTerm.trim()) {
      const term = searchTerm.toLowerCase();
      result = result.filter(c => 
        (c.name || '').toLowerCase().includes(term) ||
        (c.email || '').toLowerCase().includes(term) ||
        (c.company || '').toLowerCase().includes(term) ||
        (c.title || '').toLowerCase().includes(term)
      );
    }

    // 2. Sort
    result.sort((a, b) => {
      const valA = a[sortField] || 0;
      const valB = b[sortField] || 0;
      
      // String comparison for text fields
      if (typeof valA === 'string' && typeof valB === 'string') {
        return sortDirection === 'asc' 
          ? valA.localeCompare(valB)
          : valB.localeCompare(valA);
      }
      
      // Numeric comparison
      if (valA < valB) return sortDirection === 'asc' ? -1 : 1;
      if (valA > valB) return sortDirection === 'asc' ? 1 : -1;
      return 0;
    });

    setFilteredContacts(result);
  }, [allContacts, searchTerm, sortField, sortDirection]);

  const handleSort = (field: keyof Contact) => {
    if (sortField === field) {
      setSortDirection(prev => prev === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('desc'); // Default to desc for new field
    }
  };

  // Matches Today's Board vivid colors
  const getScoreColor = (score: number = 0) => {
    if (score >= 80) return { text: '#ef4444', bg: 'rgba(239,68,68,0.1)', border: 'rgba(239,68,68,0.3)' }; // Red/Hot
    if (score >= 50) return { text: '#fbbf24', bg: 'rgba(251,191,36,0.1)', border: 'rgba(251,191,36,0.3)' }; // Yellow/Warm
    if (score >= 30) return { text: '#22c55e', bg: 'rgba(34,197,94,0.1)', border: 'rgba(34,197,94,0.3)' }; // Green/Nurture
    return { text: '#94a3b8', bg: 'rgba(148,163,184,0.1)', border: 'rgba(148,163,184,0.3)' }; // Gray/Stable
  };

  if (loading) return (
    <div style={{ padding: 60, textAlign: 'center', color: '#94a3b8' }}>
      <RefreshCw size={32} className="animate-spin" style={{ marginBottom: 16, opacity: 0.5 }} />
      <div>Loading contacts database...</div>
    </div>
  );

  if (error) return <div style={{ padding: 48, textAlign: 'center', color: '#ef4444' }}>Error: {error}</div>;

  return (
    <div style={{ padding: 12 }}>
      {/* HEADER */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <div style={{ 
            width: 40, height: 40, 
            background: 'linear-gradient(135deg, rgba(59,130,246,0.2), rgba(37,99,235,0.2))', 
            borderRadius: 10, 
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            border: '1px solid rgba(59,130,246,0.3)'
          }}>
            <Users size={20} color="#60a5fa" />
          </div>
          <div>
            <h2 style={{ fontSize: 24, fontWeight: 700, color: '#f8fafc', margin: 0 }}>All Contacts</h2>
            <p style={{ margin: '2px 0 0', color: '#94a3b8', fontSize: 13 }}>
              {allContacts.length} total • {filteredContacts.length} visible
            </p>
          </div>
        </div>
        
        <div style={{ display: 'flex', gap: 12 }}>
          <button 
            onClick={fetchContacts}
            style={{ 
              background: 'rgba(30, 41, 59, 0.6)', 
              border: '1px solid #334155', 
              borderRadius: 8, 
              padding: '8px 12px', 
              color: '#94a3b8', 
              cursor: 'pointer',
              display: 'flex', alignItems: 'center', gap: 8,
              fontSize: 13, fontWeight: 500,
              transition: 'all 0.2s'
            }}
          >
            <RefreshCw size={14} /> Refresh
          </button>
          <button style={{ background: 'rgba(30, 41, 59, 0.6)', border: '1px solid #334155', borderRadius: 8, padding: '8px 12px', color: '#94a3b8', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 8, fontSize: 13, fontWeight: 500 }}>
            <Download size={14}/> Export
          </button>
        </div>
      </div>

      {/* SEARCH BAR */}
      <div style={{ position: 'relative', marginBottom: 20 }}>
        <Search size={18} style={{ position: 'absolute', top: 12, left: 16, color: '#64748b' }} />
        <input 
          type="text"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          placeholder="Search by name, company, title, or email..."
          style={{
            width: '100%',
            padding: '12px 16px 12px 48px',
            background: 'rgba(30, 41, 59, 0.4)', // Transparent dark
            border: '1px solid #334155',
            borderRadius: 12,
            color: '#f8fafc',
            fontSize: 14,
            outline: 'none',
            backdropFilter: 'blur(12px)'
          }}
        />
      </div>

      {/* TABLE */}
      <div style={{ 
        borderRadius: 16, 
        border: '1px solid rgba(148,163,184,0.1)', 
        overflow: 'hidden', 
        background: 'rgba(15, 23, 42, 0.6)', // Deep semi-transparent
        backdropFilter: 'blur(20px)',
        boxShadow: '0 20px 40px -10px rgba(0,0,0,0.5)'
      }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ background: 'rgba(30, 41, 59, 0.8)', borderBottom: '1px solid rgba(148,163,184,0.1)' }}>
              {[
                { id: 'name', label: 'Contact' },
                { id: 'company', label: 'Company' },
                { id: 'lifecyclestage', label: 'Lead Status' }, // NEW
                { id: 'priority_score', label: 'Score' },
                { id: 'persona', label: 'Persona' },
                { id: 'enrichment_status', label: 'Enrichment' }
              ].map((col) => (
                <th 
                  key={col.id}
                  onClick={() => handleSort(col.id as keyof Contact)} 
                  style={{ 
                    padding: '16px 20px', 
                    textAlign: 'left', 
                    fontSize: 11, 
                    fontWeight: 700, 
                    color: '#64748b', 
                    cursor: 'pointer',
                    textTransform: 'uppercase',
                    letterSpacing: '0.05em',
                    userSelect: 'none'
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                    {col.label}
                    {sortField === col.id && (
                      <ArrowUpDown size={12} color={sortDirection === 'asc' ? '#60a5fa' : '#64748b'} />
                    )}
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {filteredContacts.map((c) => {
              const score = c.priority_score || c.mdcp_score || 0;
              const colors = getScoreColor(score);
              const leadStatus = c.lifecycle_stage || c.lifecyclestage || 'New';
              
              return (
                <tr 
                  key={c.id} 
                  onClick={() => setSelectedContact(c)}
                  style={{ borderTop: '1px solid rgba(148,163,184,0.05)', cursor: 'pointer', transition: 'all 0.1s ease-out' }}
                  className="contact-row"
                  onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(59, 130, 246, 0.08)'} // Blue hover
                  onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
                >
                  {/* Name & Email */}
                  <td style={{ padding: '16px 20px' }}>
                    <div style={{ fontWeight: 600, color: '#f1f5f9', fontSize: 14, marginBottom: 2 }}>{c.name}</div>
                    <div style={{ fontSize: 12, color: '#64748b' }}>{c.email || 'No email'}</div>
                  </td>

                  {/* Company & Title */}
                  <td style={{ padding: '16px 20px' }}>
                    <div style={{ color: '#e2e8f0', fontSize: 13, fontWeight: 500 }}>{c.company || 'No Company'}</div>
                    <div style={{ fontSize: 12, color: '#64748b' }}>{c.title || c.job_title || '-'}</div>
                  </td>

                  {/* Lead Status (NEW) */}
                  <td style={{ padding: '16px 20px' }}>
                    <span style={{ 
                      fontSize: 11, fontWeight: 600, padding: '4px 10px', borderRadius: 99,
                      background: '#1e293b', border: '1px solid #334155', color: '#94a3b8',
                      textTransform: 'capitalize'
                    }}>
                      {leadStatus}
                    </span>
                  </td>

                  {/* Score */}
                  <td style={{ padding: '16px 20px' }}>
                    <div style={{ 
                      display: 'inline-flex', alignItems: 'center', justifyContent: 'center', 
                      width: 36, height: 36, borderRadius: 10, 
                      background: colors.bg, color: colors.text, border: `1px solid ${colors.border}`,
                      fontWeight: 700, fontSize: 14,
                      boxShadow: `0 4px 10px -2px ${colors.bg}`
                    }}>
                      {Math.round(score)}
                    </div>
                  </td>

                  {/* Persona */}
                  <td style={{ padding: '16px 20px' }}>
                    {c.persona ? (
                      <span style={{ 
                        fontSize: 11, fontWeight: 600, padding: '4px 10px', borderRadius: 99, 
                        background: 'rgba(124, 58, 237, 0.1)', color: '#a78bfa', 
                        border: '1px solid rgba(124, 58, 237, 0.2)',
                        display: 'inline-flex', alignItems: 'center', gap: 4
                      }}>
                        <Briefcase size={10} />
                        {c.persona.replace(/_/g, ' ')}
                      </span>
                    ) : (
                      <span style={{ fontSize: 12, color: '#475569' }}>—</span>
                    )}
                  </td>

                  {/* Enrichment Status */}
                  <td style={{ padding: '16px 20px' }}>
                    {c.enrichment_status === 'completed' ? (
                      <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 12, color: '#4ade80', fontWeight: 600 }}>
                        <Zap size={14} fill="#4ade80" /> Enriched
                      </div>
                    ) : (
                      <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 12, color: '#64748b' }}>
                        <Clock size={14} /> Pending
                      </div>
                    )}
                  </td>
                </tr>
              );
            })}
            
            {filteredContacts.length === 0 && (
              <tr>
                <td colSpan={6} style={{ padding: 60, textAlign: 'center', color: '#64748b' }}>
                  <Search size={48} style={{ opacity: 0.2, margin: '0 auto 16px' }} />
                  No contacts found matching "{searchTerm}"
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {selectedContact && (
        <ContactDetailModal
          contact={selectedContact}
          onClose={() => setSelectedContact(null)}
          onEnrichmentComplete={(updated) => {
            setSelectedContact(updated);
            fetchContacts();
          }}
        />
      )}
    </div>
  );
}
