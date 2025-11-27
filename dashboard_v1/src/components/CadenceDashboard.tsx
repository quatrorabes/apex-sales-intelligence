import React, { useState, useEffect } from 'react';
import { ChevronUp, ChevronDown } from 'lucide-react';
import ContactDetailModal from './ContactDetailModal';

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

type SortField = 'name' | 'title' | 'company' | 'lifecycle_stage' | 'lead_status' | 'priority_score' | 'mdcp_score' | 'rss_score';

export default function CadenceDashboard() {
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [loading, setLoading] = useState(true);
  const [sortField, setSortField] = useState<SortField>('priority_score');
  const [sortDir, setSortDir] = useState<'asc' | 'desc'>('desc');
  const [selectedContact, setSelectedContact] = useState<Contact | null>(null);

  useEffect(() => {
    fetchContacts();
  }, []);

  const fetchContacts = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/contacts');
      const data = await res.json();
      setContacts(data);
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

  const sorted = [...contacts].sort((a, b) => {
    let aVal: any = a[sortField];
    let bVal: any = b[sortField];
    if (aVal == null) aVal = sortDir === 'asc' ? Infinity : -Infinity;
    if (bVal == null) bVal = sortDir === 'asc' ? Infinity : -Infinity;
    if (typeof aVal === 'string') {
      aVal = aVal.toLowerCase();
      bVal = bVal?.toLowerCase() || '';
    }
    if (aVal < bVal) return sortDir === 'asc' ? -1 : 1;
    if (aVal > bVal) return sortDir === 'asc' ? 1 : -1;
    return 0;
  });

  const SortIcon = ({ field }: { field: SortField }) => {
    if (sortField !== field) return null;
    return sortDir === 'asc' ? <ChevronUp size={14} /> : <ChevronDown size={14} />;
  };

  const getScoreColor = (score?: number) => {
    if (!score) return '#6b7280';
    if (score >= 80) return '#10b981';
    if (score >= 60) return '#f59e0b';
    return '#ef4444';
  };

  const getTierBadge = (tier?: string) => {
    const colors: any = { HOT: '#10b981', WARM: '#f59e0b', COLD: '#6b7280' };
    return (
      <span style={{
        padding: '2px 8px', borderRadius: '12px', fontSize: '11px', fontWeight: 600,
        backgroundColor: colors[tier || 'COLD'] + '20', color: colors[tier || 'COLD']
      }}>
        {tier || '—'}
      </span>
    );
  };

  if (loading) return <div style={{ padding: '2rem', textAlign: 'center' }}>Loading...</div>;

  return (
    <>
      <div style={{ padding: '1.5rem', maxWidth: '100%', overflowX: 'auto' }}>
        <h2 style={{ marginBottom: '1.5rem', fontSize: '1.5rem', fontWeight: 600 }}>Cadence Dashboard</h2>
        
        <div style={{ backgroundColor: 'white', borderRadius: '12px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', overflow: 'hidden' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead style={{ backgroundColor: '#f9fafb', borderBottom: '2px solid #e5e7eb' }}>
              <tr>
                <th onClick={() => handleSort('name')} style={th}>Name <SortIcon field="name" /></th>
                <th onClick={() => handleSort('title')} style={th}>Title <SortIcon field="title" /></th>
                <th onClick={() => handleSort('company')} style={th}>Company <SortIcon field="company" /></th>
                <th onClick={() => handleSort('lifecycle_stage')} style={th}>Lifecycle <SortIcon field="lifecycle_stage" /></th>
                <th onClick={() => handleSort('lead_status')} style={th}>Lead Status <SortIcon field="lead_status" /></th>
                <th onClick={() => handleSort('priority_score')} style={th}>Priority <SortIcon field="priority_score" /></th>
                <th onClick={() => handleSort('mdcp_score')} style={th}>MDCP <SortIcon field="mdcp_score" /></th>
                <th onClick={() => handleSort('rss_score')} style={th}>RSS <SortIcon field="rss_score" /></th>
                <th style={{ ...th, cursor: 'default' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {sorted.map((c) => (
                <tr key={c.id} onClick={() => setSelectedContact(c)} style={{
                  borderBottom: '1px solid #e5e7eb', cursor: 'pointer', transition: 'background 0.15s'
                }}
                onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#f9fafb'}
                onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'white'}>
                  <td style={td}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <div style={{ width: '32px', height: '32px', borderRadius: '50%', backgroundColor: '#6366f1', color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '12px', fontWeight: 600 }}>
                        {c.name.split(' ').map(n => n[0]).join('').substring(0, 2)}
                      </div>
                      <div>
                        <div style={{ fontWeight: 500 }}>{c.name}</div>
                        <div style={{ fontSize: '12px', color: '#6b7280' }}>{c.email}</div>
                      </div>
                    </div>
                  </td>
                  <td style={td}>{c.title || '—'}</td>
                  <td style={td}>{c.company || '—'}</td>
                  <td style={td}>{c.lifecycle_stage || '—'}</td>
                  <td style={td}>{c.lead_status || '—'}</td>
                  <td style={td}><span style={{ fontWeight: 600, color: getScoreColor(c.priority_score) }}>{c.priority_score != null ? Math.round(c.priority_score) : '—'}</span></td>
                  <td style={td}>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                      <span style={{ fontWeight: 500, color: getScoreColor(c.mdcp_score) }}>{c.mdcp_score != null ? Math.round(c.mdcp_score) : '—'}</span>
                      {getTierBadge(c.mdcp_tier)}
                    </div>
                  </td>
                  <td style={td}>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                      <span style={{ fontWeight: 500, color: getScoreColor(c.rss_score) }}>{c.rss_score != null ? Math.round(c.rss_score) : '—'}</span>
                      {getTierBadge(c.rss_tier)}
                    </div>
                  </td>
                  <td style={td}>
                    <button onClick={(e) => { e.stopPropagation(); setSelectedContact(c); }} style={{ padding: '6px 12px', backgroundColor: '#6366f1', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', fontSize: '13px', fontWeight: 500 }}>
                      View
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {sorted.length === 0 && <div style={{ padding: '3rem', textAlign: 'center', color: '#6b7280' }}>No contacts found</div>}
        </div>
      </div>
      {selectedContact && <ContactDetailModal contact={selectedContact} onClose={() => setSelectedContact(null)} />}
    </>
  );
}

const th: React.CSSProperties = { padding: '12px 16px', textAlign: 'left', fontSize: '13px', fontWeight: 600, color: '#374151', cursor: 'pointer', userSelect: 'none', whiteSpace: 'nowrap' };
const td: React.CSSProperties = { padding: '12px 16px', fontSize: '14px', color: '#1f2937' };
