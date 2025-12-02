import React, { useState, useEffect, useCallback } from 'react';
import { RefreshCw, Search, Upload, Filter, Download, Zap, AlertCircle, CheckCircle, Clock } from 'lucide-react';
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
  enrichment_status?: 'completed' | 'pending' | 'failed' | string;
  priority_score?: number;
  mdcp_score?: number;
  rss_score?: number;
  lifecyclestage?: string;
  persona?: string;
}

export default function ContactEnrichmentView() {
  const [allContacts, setAllContacts] = useState<Contact[]>([]);
  const [filteredContacts, setFilteredContacts] = useState<Contact[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedContact, setSelectedContact] = useState<Contact | null>(null);
  const [sortField, setSortField] = useState('priority_score');
  const [sortDir, setSortDir] = useState<'asc' | 'desc'>('desc');

  const fetchContacts = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/api/contacts?limit=1000`);
      if (!res.ok) throw new Error(`API error: ${res.status}`);
      const data = await res.json();
      
      const contactList: Contact[] = Array.isArray(data) ? data : (data.contacts || []);
      
      setAllContacts(contactList);
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

  useEffect(() => {
    let sorted = [...allContacts];
    
    // Sort
    sorted.sort((a, b) => {
      const valA = (a as any)[sortField] || 0;
      const valB = (b as any)[sortField] || 0;
      if (sortDir === 'asc') return valA - valB;
      return valB - valA;
    });

    // Filter
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      sorted = sorted.filter(c => 
        (c.name || '').toLowerCase().includes(term) ||
        (c.email || '').toLowerCase().includes(term) ||
        (c.company || '').toLowerCase().includes(term) ||
        (c.title || '').toLowerCase().includes(term)
      );
    }
    setFilteredContacts(sorted);
  }, [allContacts, searchTerm, sortField, sortDir]);

  const getScoreColor = (score: number = 0) => {
    if (score >= 80) return { text: '#22c55e', bg: 'rgba(34,197,94,0.15)', border: 'rgba(34,197,94,0.5)' };
    if (score >= 50) return { text: '#fbbf24', bg: 'rgba(251,191,36,0.15)', border: 'rgba(251,191,36,0.5)' };
    return { text: '#94a3b8', bg: 'rgba(148,163,184,0.15)', border: 'rgba(148,163,184,0.5)' };
  };

  const handleSort = (field: string) => {
    if (field === sortField) {
      setSortDir(prev => prev === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDir('desc');
    }
  };

  if (loading) {
    return <div style={{ padding: 48, textAlign: 'center' }}>Loading contacts...</div>;
  }
  if (error) {
    return <div style={{ padding: 48, textAlign: 'center', color: '#ef4444' }}>Error: {error}</div>;
  }

  return (
    <div style={{ padding: 12 }}>
      {/* HEADER */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <div>
          <h2 style={{ fontSize: 24, fontWeight: 700, margin: 0 }}>All Contacts</h2>
          <p style={{ margin: '4px 0 0', color: '#94a3b8' }}>{allContacts.length} contacts found</p>
        </div>
        <div style={{ display: 'flex', gap: 12 }}>
          <button style={{ background: 'transparent', border: '1px solid #334155', borderRadius: 8, padding: '8px 14px', color: '#94a3b8', display: 'flex', alignItems: 'center', gap: 8 }}><Filter size={16}/> Filter</button>
          <button style={{ background: 'transparent', border: '1px solid #334155', borderRadius: 8, padding: '8px 14px', color: '#94a3b8', display: 'flex', alignItems: 'center', gap: 8 }}><Download size={16}/> Export</button>
        </div>
      </div>
      
      {/* SEARCH */}
      <div style={{ position: 'relative', marginBottom: 16 }}>
        <Search size={18} style={{ position: 'absolute', top: 13, left: 14, color: '#64748b' }}/>
        <input 
          type="text"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          placeholder="Search by name, company, title, or email..."
          style={{
            width: '100%',
            padding: '12px 16px 12px 48px',
            background: '#1e293b',
            border: '1px solid #334155',
            borderRadius: 8,
            color: '#f8fafc',
            fontSize: 14
          }}
        />
      </div>

      {/* TABLE */}
      <div style={{ borderRadius: 12, border: '1px solid #334155', overflow: 'hidden', background: '#1e293b' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ background: '#33415550' }}>
              {['name', 'company', 'priority_score', 'mdcp_score', 'persona', 'enrichment_status'].map(field => (
                <th key={field} onClick={() => handleSort(field)} style={{ padding: '12px 16px', textAlign: 'left', fontSize: 12, fontWeight: 600, color: '#94a3b8', textTransform: 'uppercase', cursor: 'pointer' }}>
                  {field.replace('_', ' ')} {sortField === field ? (sortDir === 'asc' ? '▲' : '▼') : ''}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {filteredContacts.map(contact => {
              const scoreColors = getScoreColor(contact.priority_score);
              return (
              <tr key={contact.id} onClick={() => setSelectedContact(contact)} style={{ borderTop: '1px solid #334155', cursor: 'pointer' }}>
                <td style={{ padding: '14px 16px' }}>
                  <div style={{ fontWeight: 600, color: '#f8fafc' }}>{contact.name}</div>
                  <div style={{ fontSize: 12, color: '#64748b' }}>{contact.email}</div>
                </td>
                <td style={{ padding: '14px 16px' }}>
                  <div style={{ color: '#cbd5e1' }}>{contact.title || contact.job_title}</div>
                  <div style={{ fontSize: 12, color: '#64748b' }}>{contact.company}</div>
                </td>
                <td style={{ padding: '14px 16px' }}>
                  <span style={{ color: scoreColors.text, background: scoreColors.bg, border: `1px solid ${scoreColors.border}`, padding: '4px 8px', borderRadius: 6, fontWeight: 700, fontSize: 13 }}>
                    {contact.priority_score?.toFixed(0) || '0'}
                  </span>
                </td>
                <td style={{ padding: '14px 16px', color: '#94a3b8' }}>{contact.mdcp_score?.toFixed(0) || '-'}</td>
                <td style={{ padding: '14px 16px' }}>
                  {contact.persona ? 
                    <span style={{ padding: '4px 8px', borderRadius: 6, fontSize: 11, background: 'rgba(168, 85, 247, 0.1)', color: '#c084fc', fontWeight: 600 }}>
                      {contact.persona}
                    </span> : 
                    <span style={{color: '#64748b'}}>N/A</span>
                  }
                </td>
                <td style={{ padding: '14px 16px' }}>
                  {contact.enrichment_status === 'completed' ?
                    <span style={{ color: '#22c55e', display: 'flex', alignItems: 'center', gap: 6, fontWeight: 600 }}>
                      <CheckCircle size={16}/> Enriched
                    </span> :
                    <span style={{ color: '#64748b', display: 'flex', alignItems: 'center', gap: 6 }}>
                      <Clock size={16}/> Pending
                    </span>
                  }
                </td>
              </tr>
            )})}
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
