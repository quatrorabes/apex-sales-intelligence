import React, { useState, useEffect } from 'react';
import { 
  Target, 
  TrendingUp, 
  Users, 
  Zap,
  AlertCircle,
  CheckCircle,
  Clock,
  Sparkles,
  Filter,
  Download,
  RefreshCw
} from 'lucide-react';
import ContactDetailModal from './ContactDetailModal';

interface Contact {
  id: number;
  name: string;
  email?: string;
  phone?: string;
  company?: string;
  title?: string;
  job_title?: string;
  lifecycle_stage?: string;
  enrichment_status?: string;
  mdcp_score?: number;
  rss_score?: number;
  priority_score?: number;
  urgency_level?: string;
  recommended_action?: string;
  profile_content?: string;
  enrichment_data?: string;
}

export default function ApexIntelligence() {
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedContact, setSelectedContact] = useState<Contact | null>(null);
  const [filterTier, setFilterTier] = useState<string>('all');
  const [sortBy, setSortBy] = useState<'priority' | 'mdcp' | 'rss'>('priority');

  useEffect(() => {
    fetchContacts();
  }, []);

  const fetchContacts = async () => {
    setLoading(true);
    try {
      const res = await fetch('https://apex-intelligence-production.up.railway.app/api/contacts');
      const data = await res.json();
      const contactList = (data.contacts as Contact[]) || (data as Contact[]) || [];
      
      // Filter only enriched contacts with scores
      const enrichedContacts = contactList.filter(c => 
        c.enrichment_status === 'completed' && 
        (c.priority_score || c.mdcp_score || c.rss_score)
      );
      
      setContacts(enrichedContacts);
    } catch (err) {
      console.error('Failed to load contacts:', err);
      setError('Failed to load contacts');
    } finally {
      setLoading(false);
    }
  };

  // Calculate stats
  const stats = {
    total: contacts.length,
    highPriority: contacts.filter(c => (c.priority_score || 0) >= 75).length,
    enriched: contacts.filter(c => c.enrichment_status === 'completed').length,
    avgPriority: contacts.length > 0 
      ? Math.round(contacts.reduce((sum, c) => sum + (c.priority_score || 0), 0) / contacts.length)
      : 0,
  };

  // Sort contacts
  const sortedContacts = [...contacts].sort((a, b) => {
    if (sortBy === 'priority') {
      return (b.priority_score || 0) - (a.priority_score || 0);
    } else if (sortBy === 'mdcp') {
      return (b.mdcp_score || 0) - (a.mdcp_score || 0);
    } else {
      return (b.rss_score || 0) - (a.rss_score || 0);
    }
  });

  // Filter by tier if needed
  const filteredContacts = filterTier === 'all' 
    ? sortedContacts 
    : sortedContacts.filter(c => {
        const score = c.priority_score || 0;
        if (filterTier === 'hot') return score >= 75;
        if (filterTier === 'warm') return score >= 50 && score < 75;
        if (filterTier === 'cold') return score < 50;
        return true;
      });

  // Get score color
  const getScoreColor = (score: number) => {
    if (score >= 75) return '#22c55e';
    if (score >= 50) return '#f97316';
    return '#64748b';
  };

  // Get urgency color
  const getUrgencyColor = (urgency: string) => {
    if (urgency === 'HIGH' || urgency === 'IMMEDIATE') return '#ef4444';
    if (urgency === 'MEDIUM') return '#f97316';
    return '#64748b';
  };

  if (loading) {
    return (
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        height: '100vh',
        background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 100%)',
      }}>
        <RefreshCw size={48} style={{ color: '#6366f1', animation: 'spin 1s linear infinite' }} />
      </div>
    );
  }

  return (
    <div style={{ 
      padding: 32,
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 100%)',
    }}>
      {/* Header */}
      <div style={{ marginBottom: 32 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
          <div>
            <h1 style={{ 
              fontSize: 32, 
              fontWeight: 800, 
              color: '#e5e7eb',
              marginBottom: 8,
              letterSpacing: -0.5,
            }}>
              Apex Intelligence
            </h1>
            <p style={{ fontSize: 14, color: '#9ca3af' }}>
              CRE-focused scoring with MDCP + RSS prioritization
            </p>
          </div>
          <div style={{ display: 'flex', gap: 12 }}>
            <button
              onClick={async () => {
                setLoading(true);
                try {
                  const res = await fetch('https://apex-intelligence-production.up.railway.app/api/contacts/score-all', {
                    method: 'POST'
                  });
                  const data = await res.json();
                  if (data.success) {
                    alert(`✅ Scored ${data.scored} contacts!`);
                    fetchContacts();
                  } else {
                    alert(`❌ Scoring failed: ${data.error}`);
                  }
                } catch (err) {
                  console.error(err);
                  alert('❌ Scoring failed');
                } finally {
                  setLoading(false);
                }
              }}
              disabled={loading}
              style={{
                padding: '10px 20px',
                borderRadius: 8,
                border: '2px solid rgba(168,85,247,0.6)',
                background: loading 
                  ? 'rgba(71,85,105,0.5)'
                  : 'linear-gradient(135deg, rgba(168,85,247,0.25), rgba(147,51,234,0.25))',
                color: '#e5e7eb',
                fontSize: 13,
                fontWeight: 600,
                cursor: loading ? 'not-allowed' : 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: 8,
                boxShadow: '0 4px 12px rgba(168,85,247,0.3)',
              }}
            >
              {loading ? (
                <>
                  <RefreshCw size={16} style={{ animation: 'spin 1s linear infinite' }} />
                  Scoring...
                </>
              ) : (
                <>
                  <Zap size={16} />
                  Score All Contacts
                </>
              )}
            </button>
            <button
              onClick={fetchContacts}
              style={{
                padding: '10px 20px',
                borderRadius: 8,
                border: '1px solid rgba(99,102,241,0.5)',
                background: 'rgba(79,70,229,0.2)',
                color: '#e5e7eb',
                fontSize: 13,
                fontWeight: 600,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: 8,
              }}
            >
              <RefreshCw size={16} />
              Refresh
            </button>
            <button
              style={{
                padding: '10px 20px',
                borderRadius: 8,
                border: '1px solid rgba(34,197,94,0.5)',
                background: 'rgba(34,197,94,0.2)',
                color: '#e5e7eb',
                fontSize: 13,
                fontWeight: 600,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: 8,
              }}
            >
              <Download size={16} />
              Export
            </button>
          </div>
        </div>
      </div>
    
      {/* Stats Grid */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
        gap: 20,
        marginBottom: 32,
      }}>
        {[
          { 
            label: 'Total Scored', 
            value: stats.total,
            icon: Users,
            color: '#6366f1',
            gradient: 'linear-gradient(135deg, rgba(99,102,241,0.2), rgba(79,70,229,0.2))'
          },
          { 
            label: 'High Priority', 
            value: stats.highPriority,
            icon: Target,
            color: '#22c55e',
            gradient: 'linear-gradient(135deg, rgba(34,197,94,0.2), rgba(16,185,129,0.2))'
          },
          { 
            label: 'Enriched', 
            value: stats.enriched,
            icon: Sparkles,
            color: '#a855f7',
            gradient: 'linear-gradient(135deg, rgba(168,85,247,0.2), rgba(147,51,234,0.2))'
          },
          { 
            label: 'Avg Priority Score', 
            value: stats.avgPriority,
            icon: TrendingUp,
            color: '#f97316',
            gradient: 'linear-gradient(135deg, rgba(249,115,22,0.2), rgba(234,88,12,0.2))'
          }
        ].map((stat) => {
          const Icon = stat.icon;
          return (
            <div
              key={stat.label}
              style={{
                background: stat.gradient,
                borderRadius: 16,
                padding: 24,
                border: `1px solid ${stat.color}40`,
                boxShadow: `0 4px 16px ${stat.color}20`,
              }}
            >
              <div style={{ 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'space-between',
                marginBottom: 16 
              }}>
                <Icon size={24} style={{ color: stat.color }} />
              </div>
              <div style={{ 
                fontSize: 36, 
                fontWeight: 800, 
                color: '#e5e7eb',
                marginBottom: 6,
                lineHeight: 1,
              }}>
                {stat.value}
              </div>
              <div style={{ fontSize: 13, color: '#9ca3af', fontWeight: 500 }}>
                {stat.label}
              </div>
            </div>
          );
        })}
      </div>

      {/* Filters & Sort */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: 24,
        padding: '16px 20px',
        background: 'rgba(15,23,42,0.8)',
        borderRadius: 12,
        border: '1px solid rgba(148,163,184,0.3)',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <Filter size={18} style={{ color: '#9ca3af' }} />
          <span style={{ fontSize: 13, color: '#9ca3af', fontWeight: 600 }}>Filter:</span>
          {['all', 'hot', 'warm', 'cold'].map((tier) => (
            <button
              key={tier}
              onClick={() => setFilterTier(tier)}
              style={{
                padding: '6px 14px',
                borderRadius: 6,
                border: filterTier === tier 
                  ? '1px solid rgba(99,102,241,0.6)'
                  : '1px solid rgba(148,163,184,0.3)',
                background: filterTier === tier 
                  ? 'rgba(99,102,241,0.15)'
                  : 'transparent',
                color: filterTier === tier ? '#e5e7eb' : '#9ca3af',
                fontSize: 12,
                fontWeight: 600,
                cursor: 'pointer',
                textTransform: 'capitalize',
              }}
            >
              {tier === 'all' ? 'All Leads' : tier}
            </button>
          ))}
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <span style={{ fontSize: 13, color: '#9ca3af', fontWeight: 600 }}>Sort by:</span>
          {[
            { id: 'priority', label: 'Priority' },
            { id: 'mdcp', label: 'MDCP' },
            { id: 'rss', label: 'RSS' }
          ].map((sort) => (
            <button
              key={sort.id}
              onClick={() => setSortBy(sort.id as any)}
              style={{
                padding: '6px 14px',
                borderRadius: 6,
                border: sortBy === sort.id 
                  ? '1px solid rgba(99,102,241,0.6)'
                  : '1px solid rgba(148,163,184,0.3)',
                background: sortBy === sort.id 
                  ? 'rgba(99,102,241,0.15)'
                  : 'transparent',
                color: sortBy === sort.id ? '#e5e7eb' : '#9ca3af',
                fontSize: 12,
                fontWeight: 600,
                cursor: 'pointer',
              }}
            >
              {sort.label}
            </button>
          ))}
        </div>
      </div>

      {/* Results Count */}
      <div style={{ 
        fontSize: 13, 
        color: '#9ca3af',
        marginBottom: 16,
        fontWeight: 500,
      }}>
        Showing {filteredContacts.length} contacts · Sorted by {sortBy === 'priority' ? 'Priority Score' : sortBy === 'mdcp' ? 'MDCP Score' : 'RSS Score'} (70% role, 30% data completeness)
      </div>

      {/* Main Table */}
      {error ? (
        <div style={{
          padding: 40,
          textAlign: 'center',
          background: 'rgba(239,68,68,0.1)',
          borderRadius: 12,
          border: '1px solid rgba(239,68,68,0.3)',
        }}>
          <AlertCircle size={48} style={{ color: '#ef4444', marginBottom: 16 }} />
          <div style={{ fontSize: 16, fontWeight: 600, color: '#ef4444' }}>
            Error: {error}
          </div>
        </div>
      ) : filteredContacts.length === 0 ? (
        <div style={{
          padding: 60,
          textAlign: 'center',
          background: 'rgba(15,23,42,0.9)',
          borderRadius: 16,
          border: '1px solid rgba(148,163,184,0.3)',
        }}>
          <Zap size={56} style={{ color: '#64748b', marginBottom: 20 }} />
          <div style={{ fontSize: 18, fontWeight: 600, color: '#e5e7eb', marginBottom: 8 }}>
            No Scored Contacts Yet
          </div>
          <div style={{ fontSize: 14, color: '#9ca3af' }}>
            Enrich contacts to generate intelligence scores
          </div>
        </div>
      ) : (
        <div style={{
          background: 'rgba(15,23,42,0.95)',
          borderRadius: 16,
          border: '1px solid rgba(148,163,184,0.3)',
          overflow: 'hidden',
          boxShadow: '0 8px 24px rgba(0,0,0,0.4)',
        }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{
                borderBottom: '2px solid rgba(148,163,184,0.3)',
                background: 'rgba(15,23,42,0.8)',
              }}>
                <th style={thStyle}>Contact</th>
                <th style={thStyle}>Title & Company</th>
                <th style={thStyle}>Lifecycle</th>
                <th style={thStyle}>MDCP</th>
                <th style={thStyle}>RSS</th>
                <th style={thStyle}>Priority</th>
                <th style={thStyle}>Urgency</th>
                <th style={thStyle}>Recommended Action</th>
              </tr>
            </thead>
            <tbody>
              {filteredContacts.map((c) => {
                const priorityScore = c.priority_score || 0;
                const mdcpScore = c.mdcp_score || 0;
                const rssScore = c.rss_score || 0;
                
                return (
                  <tr
                    key={c.id}
                    onClick={() => setSelectedContact(c)}
                    style={{
                      borderBottom: '1px solid rgba(148,163,184,0.1)',
                      transition: 'all 0.2s',
                      cursor: 'pointer',
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.background = 'rgba(79,70,229,0.08)';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.background = 'transparent';
                    }}
                  >
                    {/* Contact */}
                    <td style={tdStyle}>
                      <div>
                        <div style={{ 
                          fontWeight: 600, 
                          color: '#e5e7eb',
                          marginBottom: 4,
                          fontSize: 14,
                        }}>
                          {c.name}
                        </div>
                        <div style={{ 
                          fontSize: 12, 
                          color: '#64748b',
                          display: 'flex',
                          alignItems: 'center',
                          gap: 6,
                        }}>
                          {c.email || 'No email'}
                        </div>
                      </div>
                    </td>

                    {/* Title & Company */}
                    <td style={tdStyle}>
                      <div>
                        <div style={{ 
                          fontSize: 13, 
                          color: '#d1d5db',
                          marginBottom: 3,
                        }}>
                          {c.title || c.job_title || '—'}
                        </div>
                        <div style={{ fontSize: 12, color: '#9ca3af' }}>
                          {c.company || 'No company'}
                        </div>
                      </div>
                    </td>

                    {/* Lifecycle */}
                    <td style={tdStyle}>
                      <span style={{
                        padding: '4px 10px',
                        borderRadius: 12,
                        fontSize: 11,
                        fontWeight: 600,
                        background: 'rgba(99,102,241,0.15)',
                        color: '#818cf8',
                        textTransform: 'uppercase',
                        letterSpacing: 0.5,
                      }}>
                        {c.lifecycle_stage || 'New'}
                      </span>
                    </td>

                    {/* MDCP Score */}
                    <td style={tdStyle}>
                      <div style={{
                        width: 48,
                        height: 48,
                        borderRadius: 10,
                        background: `linear-gradient(135deg, ${getScoreColor(mdcpScore)}20, ${getScoreColor(mdcpScore)}10)`,
                        border: `2px solid ${getScoreColor(mdcpScore)}`,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        fontSize: 16,
                        fontWeight: 700,
                        color: getScoreColor(mdcpScore),
                      }}>
                        {Math.round(mdcpScore) || '—'}
                      </div>
                    </td>

                    {/* RSS Score */}
                    <td style={tdStyle}>
                      <div style={{
                        width: 48,
                        height: 48,
                        borderRadius: 10,
                        background: `linear-gradient(135deg, ${getScoreColor(rssScore)}20, ${getScoreColor(rssScore)}10)`,
                        border: `2px solid ${getScoreColor(rssScore)}`,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        fontSize: 16,
                        fontWeight: 700,
                        color: getScoreColor(rssScore),
                      }}>
                        {Math.round(rssScore) || '—'}
                      </div>
                    </td>

                    {/* Priority Score */}
                    <td style={tdStyle}>
                      <div style={{
                        width: 56,
                        height: 56,
                        borderRadius: 12,
                        background: `linear-gradient(135deg, ${getScoreColor(priorityScore)}30, ${getScoreColor(priorityScore)}15)`,
                        border: `3px solid ${getScoreColor(priorityScore)}`,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        fontSize: 20,
                        fontWeight: 800,
                        color: getScoreColor(priorityScore),
                        boxShadow: `0 4px 12px ${getScoreColor(priorityScore)}30`,
                      }}>
                        {Math.round(priorityScore) || '—'}
                      </div>
                    </td>

                    {/* Urgency */}
                    <td style={tdStyle}>
                      <div style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: 6,
                        padding: '6px 12px',
                        borderRadius: 8,
                        background: `${getUrgencyColor(c.urgency_level || 'LOW')}15`,
                        border: `1px solid ${getUrgencyColor(c.urgency_level || 'LOW')}40`,
                      }}>
                        <Clock size={14} style={{ color: getUrgencyColor(c.urgency_level || 'LOW') }} />
                        <span style={{
                          fontSize: 12,
                          fontWeight: 600,
                          color: getUrgencyColor(c.urgency_level || 'LOW'),
                        }}>
                          {c.urgency_level || 'LOW'}
                        </span>
                      </div>
                    </td>

                    {/* Recommended Action */}
                    <td style={tdStyle}>
                      <div style={{ 
                        fontSize: 13, 
                        color: '#d1d5db',
                        maxWidth: 200,
                        lineHeight: 1.5,
                      }}>
                        {c.recommended_action || 'Score to get recommendation'}
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* Contact Detail Modal */}
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

      {/* CSS for animations */}
      <style>
        {`
          @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
          }
        `}
      </style>
    </div>
  );
}

const thStyle: React.CSSProperties = {
  padding: '16px 20px',
  textAlign: 'left',
  fontSize: 11,
  fontWeight: 700,
  textTransform: 'uppercase',
  letterSpacing: 1,
  color: '#9ca3af',
  background: 'rgba(15,23,42,0.5)',
};

const tdStyle: React.CSSProperties = {
  padding: '20px',
  fontSize: 13,
  color: '#e5e7eb',
  background: 'transparent',
  verticalAlign: 'middle',
};
