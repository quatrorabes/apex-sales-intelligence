import React, { useState, useEffect } from 'react';
import { 
  Phone, Mail, Linkedin, Calendar, Clock, Flame, 
  Zap, ChevronRight, RefreshCw, Star, TrendingUp,
  MessageCircle, ExternalLink, Sparkles, Target,
  Users, Award, Briefcase
} from 'lucide-react';

interface Contact {
  id: number;
  name: string;
  email: string;
  phone: string;
  company: string;
  title: string;
  priority_score?: number;
  mdcp_score?: number;
  apex_urgency?: number;
  urgency_tier: string;
  urgency_label: string;
  urgency_message: string;
  why_now: string;
  days_since_contact: number;
  contact_type: 'relationship' | 'prospect';
  email_1_subject?: string;
  email_1_body?: string;
  call_script_1?: string;
  linkedin_connect?: string;
  profile_content?: string;
}

interface TodaysBoardData {
  success: boolean;
  date: string;
  time: string;
  total_actions: number;
  recommendation: string;
  relationships: {
    total: number;
    urgent_count: number;
    warm_count: number;
    nurture_count: number;
    stable_count: number;
    tiers: {
      urgent: Contact[];
      warm: Contact[];
      nurture: Contact[];
      stable: Contact[];
    };
  };
  new_prospects: {
    total: number;
    hot_count: number;
    qualified_count: number;
    potential_count: number;
    tiers: {
      hot: Contact[];
      qualified: Contact[];
      potential: Contact[];
    };
  };
}

interface TodaysBoardProps {
  onContactSelect?: (contact: Contact) => void;
}

export default function TodaysBoard({ onContactSelect }: TodaysBoardProps) {
  const [data, setData] = useState<TodaysBoardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [viewMode, setViewMode] = useState<'relationships' | 'prospects'>('relationships');
  const [selectedTier, setSelectedTier] = useState<string>('urgent');

const fetchBoard = async () => {
  try {
    setLoading(true);
    const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
    
    // ADD THIS LINE - Actually call fetch()
    const res = await fetch(`${API_URL}/api/todays-board`);
    const json = await res.json();
    setData(json);
  } catch (err) {
    console.error('Failed to fetch today\'s board:', err);
  } finally {
    setLoading(false);
  }
};
  
  useEffect(() => {
    fetchBoard();
  }, []);

  useEffect(() => {
    // Auto-select first available tier when switching modes
    if (viewMode === 'relationships') {
      if (data?.relationships.urgent_count > 0) setSelectedTier('urgent');
      else if (data?.relationships.warm_count > 0) setSelectedTier('warm');
      else if (data?.relationships.nurture_count > 0) setSelectedTier('nurture');
      else setSelectedTier('stable');
    } else {
      if (data?.new_prospects.hot_count > 0) setSelectedTier('hot');
      else if (data?.new_prospects.qualified_count > 0) setSelectedTier('qualified');
      else setSelectedTier('potential');
    }
  }, [viewMode, data]);

  if (loading) {
    return (
      <div style={{ padding: 48, textAlign: 'center' }}>
        <RefreshCw size={32} style={{ animation: 'spin 1s linear infinite', color: '#6366f1', margin: '0 auto 16px' }} />
        <div style={{ fontSize: 18, fontWeight: 600, color: '#e5e7eb' }}>Loading your daily board...</div>
      </div>
    );
  }

  if (!data || !data.success) {
    return (
      <div style={{ padding: 48, textAlign: 'center', color: '#9ca3af' }}>
        <div style={{ fontSize: 18, fontWeight: 600, marginBottom: 8 }}>Unable to load board</div>
        <button onClick={fetchBoard} style={{ marginTop: 16, padding: '10px 20px', borderRadius: 8, background: '#6366f1', color: '#fff', border: 'none', cursor: 'pointer' }}>
          Retry
        </button>
      </div>
    );
  }

  const greeting = new Date().getHours() < 12 ? 'Good Morning' : new Date().getHours() < 18 ? 'Good Afternoon' : 'Good Evening';

  return (
    <div style={{ padding: '24px 0' }}>
      {/* HEADER */}
      <div style={{ 
        background: 'linear-gradient(135deg, rgba(79,70,229,0.15), rgba(147,51,234,0.15))',
        borderRadius: 16,
        padding: 32,
        marginBottom: 24,
        border: '1px solid rgba(99,102,241,0.3)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 20 }}>
          <div>
            <div style={{ fontSize: 28, fontWeight: 700, color: '#e5e7eb', marginBottom: 4 }}>
              {greeting} 👋
            </div>
            <div style={{ fontSize: 15, color: '#9ca3af' }}>
              {data.time} • {data.date}
            </div>
          </div>
          <button
            onClick={fetchBoard}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 8,
              padding: '10px 16px',
              borderRadius: 8,
              background: 'rgba(99,102,241,0.2)',
              border: '1px solid rgba(99,102,241,0.5)',
              color: '#a5b4fc',
              fontSize: 14,
              fontWeight: 600,
              cursor: 'pointer',
            }}
          >
            <RefreshCw size={16} />
            Refresh
          </button>
        </div>

        {/* AI RECOMMENDATION */}
        <div style={{
          background: 'rgba(99,102,241,0.15)',
          border: '1px solid rgba(99,102,241,0.4)',
          borderRadius: 12,
          padding: 16,
          marginBottom: 20,
          display: 'flex',
          alignItems: 'center',
          gap: 12,
        }}>
          <Sparkles size={24} color="#818cf8" />
          <div>
            <div style={{ fontSize: 12, fontWeight: 600, color: '#a5b4fc', marginBottom: 4 }}>
              🤖 AI Recommendation
            </div>
            <div style={{ fontSize: 14, color: '#e5e7eb' }}>
              {data.recommendation}
            </div>
          </div>
        </div>

        {/* STATS */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 16 }}>
          <div style={{ background: 'rgba(239,68,68,0.15)', borderRadius: 12, padding: 16, border: '1px solid rgba(239,68,68,0.3)' }}>
            <div style={{ fontSize: 32, fontWeight: 700, color: '#ef4444', marginBottom: 4 }}>
              {(data?.relationships?.tiers?.urgent?.length ?? 0) + (data?.relationships?.tiers?.warm?.length ?? 0)}
            </div>
            <div style={{ fontSize: 13, color: '#fca5a5' }}>🔥 Relationships Need Attention</div>
          </div>
          <div style={{ background: 'rgba(34,197,94,0.15)', borderRadius: 12, padding: 16, border: '1px solid rgba(34,197,94,0.3)' }}>
            <div style={{ fontSize: 32, fontWeight: 700, color: '#22c55e', marginBottom: 4 }}>
              {(data?.new_prospects?.tiers?.hot?.length ?? 0) + (data?.new_prospects?.tiers?.qualified?.length ?? 0)}
            </div>
            <div style={{ fontSize: 13, color: '#4ade80' }}>🎯 Hot New Prospects</div>
          </div>
          <div style={{ background: 'rgba(99,102,241,0.15)', borderRadius: 12, padding: 16, border: '1px solid rgba(99,102,241,0.3)' }}>
            <div style={{ fontSize: 32, fontWeight: 700, color: '#818cf8', marginBottom: 4 }}>
              {(data?.relationships?.total ?? 0) + (data?.new_prospects?.total ?? 0)}
            </div>
            <div style={{ fontSize: 13, color: '#a5b4fc' }}>✅ Total Actions Today</div>
          </div>
        </div>
      </div>

      {/* VIEW MODE TOGGLE */}
      <div style={{ display: 'flex', gap: 12, marginBottom: 20 }}>
        <button
          onClick={() => setViewMode('relationships')}
          style={{
            flex: 1,
            padding: '16px 24px',
            borderRadius: 12,
            border: viewMode === 'relationships' ? '2px solid rgba(239,68,68,0.8)' : '1px solid rgba(148,163,184,0.3)',
            background: viewMode === 'relationships' 
              ? 'linear-gradient(135deg, rgba(239,68,68,0.2), rgba(220,38,38,0.2))' 
              : 'rgba(30,41,59,0.6)',
            color: viewMode === 'relationships' ? '#ef4444' : '#9ca3af',
            fontSize: 16,
            fontWeight: 700,
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: 10,
          }}
        >
          <Users size={20} />
          <div>
            <div>🔥 Existing Relationships</div>
            <div style={{ fontSize: 12, fontWeight: 500, opacity: 0.8 }}>
              {data.relationships.total} contacts • {(data?.relationships?.tiers?.urgent?.length ?? 0) + (data?.relationships?.tiers?.warm?.length ?? 0)} priority
            </div>
          </div>
        </button>
        <button
          onClick={() => setViewMode('prospects')}
          style={{
            flex: 1,
            padding: '16px 24px',
            borderRadius: 12,
            border: viewMode === 'prospects' ? '2px solid rgba(34,197,94,0.8)' : '1px solid rgba(148,163,184,0.3)',
            background: viewMode === 'prospects' 
              ? 'linear-gradient(135deg, rgba(34,197,94,0.2), rgba(22,163,74,0.2))' 
              : 'rgba(30,41,59,0.6)',
            color: viewMode === 'prospects' ? '#22c55e' : '#9ca3af',
            fontSize: 16,
            fontWeight: 700,
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: 10,
          }}
        >
          <Target size={20} />
          <div>
            <div>🎯 New Prospects</div>
            <div style={{ fontSize: 12, fontWeight: 500, opacity: 0.8 }}>
              {data.new_prospects.total} prospects • {(data?.new_prospects?.tiers?.hot?.length ?? 0) + (data?.new_prospects?.tiers?.qualified?.length ?? 0)} qualified
            </div>
          </div>
        </button>
      </div>

      {/* TIER SELECTOR */}
      <div style={{ display: 'flex', gap: 12, marginBottom: 20, flexWrap: 'wrap' }}>
        {viewMode === 'relationships' ? (
          <>
            {(data?.relationships?.tiers?.urgent?.length ?? 0) > 0 && (
              <TierButton
                id="urgent"
                label="🔥 Urgent"
                count={(data?.relationships?.tiers?.urgent?.length ?? 0)}
                selected={selectedTier === 'urgent'}
                onClick={() => setSelectedTier('urgent')}
              />
            )}
            {(data?.relationships?.tiers?.warm?.length ?? 0) > 0 && (
              <TierButton
                id="warm"
                label="⏰ Warm"
                count={(data?.relationships?.tiers?.warm?.length ?? 0)}
                selected={selectedTier === 'warm'}
                onClick={() => setSelectedTier('warm')}
              />
            )}
            {(data?.relationships?.tiers?.nurture?.length ?? 0) > 0 && (
              <TierButton
                id="nurture"
                label="💎 Nurture"
                count={(data?.relationships?.tiers?.nurture?.length ?? 0)}
                selected={selectedTier === 'nurture'}
                onClick={() => setSelectedTier('nurture')}
              />
            )}
            {(data?.relationships?.tiers?.stable?.length ?? 0) > 0 && (
              <TierButton
                id="stable"
                label="📚 Stable"
                count={(data?.relationships?.tiers?.stable?.length ?? 0)}
                selected={selectedTier === 'stable'}
                onClick={() => setSelectedTier('stable')}
              />
            )}
          </>
        ) : (
          <>
            {(data?.new_prospects?.tiers?.hot?.length ?? 0) > 0 && (
              <TierButton
                id="hot"
                label="🎯 Hot"
                count={(data?.new_prospects?.tiers?.hot?.length ?? 0)}
                selected={selectedTier === 'hot'}
                onClick={() => setSelectedTier('hot')}
              />
            )}
            {(data?.new_prospects?.tiers?.qualified?.length ?? 0) > 0 && (
              <TierButton
                id="qualified"
                label="✅ Qualified"
                count={(data?.new_prospects?.tiers?.qualified?.length ?? 0)}
                selected={selectedTier === 'qualified'}
                onClick={() => setSelectedTier('qualified')}
              />
            )}
            {(data?.new_prospects?.tiers?.potential?.length ?? 0) > 0 && (
              <TierButton
                id="potential"
                label="🔍 Potential"
                count={(data?.new_prospects?.tiers?.potential?.length ?? 0)}
                selected={selectedTier === 'potential'}
                onClick={() => setSelectedTier('potential')}
              />
            )}
          </>
        )}
      </div>

      {/* CONTACT CARDS */}
      <div style={{ display: 'grid', gap: 16 }}>
        {(() => {
          let contacts: Contact[] = [];
          if (viewMode === 'relationships') {
            contacts = data.relationships.tiers[selectedTier as keyof typeof data.relationships.tiers] || [];
          } else {
            contacts = data.new_prospects.tiers[selectedTier as keyof typeof data.new_prospects.tiers] || [];
          }

          if (contacts.length === 0) {
            return (
              <div style={{ 
                padding: 48, 
                textAlign: 'center', 
                background: 'rgba(30,41,59,0.5)', 
                borderRadius: 16,
                border: '1px solid rgba(148,163,184,0.2)'
              }}>
                <div style={{ fontSize: 16, color: '#9ca3af' }}>
                  No contacts in this tier. Great job! 🎉
                </div>
              </div>
            );
          }

          return contacts.map((contact) => (
            <ContactCard 
              key={contact.id} 
              contact={contact} 
              onSelect={() => onContactSelect?.(contact)}
            />
          ));
        })()}
      </div>
    </div>
  );
}

// ============= TIER BUTTON =============
function TierButton({ id, label, count, selected, onClick }: any) {
  return (
    <button
      onClick={onClick}
      style={{
        padding: '10px 16px',
        borderRadius: 8,
        border: selected ? '1px solid rgba(99,102,241,0.9)' : '1px solid rgba(148,163,184,0.3)',
        background: selected ? 'rgba(99,102,241,0.2)' : 'rgba(30,41,59,0.6)',
        color: selected ? '#e5e7eb' : '#9ca3af',
        fontSize: 14,
        fontWeight: 600,
        cursor: 'pointer',
      }}
    >
      {label} ({count})
    </button>
  );
}

// ============= CONTACT CARD (UNCHANGED FROM PREVIOUS) =============
function ContactCard({ contact, onSelect }: { contact: Contact; onSelect: () => void }) {
  const [showContent, setShowContent] = useState(false);

  const tierColors: Record<string, any> = {
    urgent: { bg: 'rgba(239,68,68,0.1)', border: 'rgba(239,68,68,0.5)', text: '#ef4444', icon: '🔥' },
    warm: { bg: 'rgba(251,191,36,0.1)', border: 'rgba(251,191,36,0.5)', text: '#fbbf24', icon: '⏰' },
    nurture: { bg: 'rgba(34,197,94,0.1)', border: 'rgba(34,197,94,0.5)', text: '#22c55e', icon: '💎' },
    stable: { bg: 'rgba(148,163,184,0.1)', border: 'rgba(148,163,184,0.5)', text: '#94a3b8', icon: '📚' },
    hot_prospect: { bg: 'rgba(239,68,68,0.1)', border: 'rgba(239,68,68,0.5)', text: '#ef4444', icon: '🎯' },
    qualified_prospect: { bg: 'rgba(34,197,94,0.1)', border: 'rgba(34,197,94,0.5)', text: '#22c55e', icon: '✅' },
    potential_prospect: { bg: 'rgba(99,102,241,0.1)', border: 'rgba(99,102,241,0.5)', text: '#818cf8', icon: '🔍' },
  };

  const colors = tierColors[contact.urgency_tier] || tierColors.stable;
  const hasContent = contact.email_1_body || contact.call_script_1 || contact.linkedin_connect;

  return (
    <div
      style={{
        background: 'rgba(30,41,59,0.5)',
        borderRadius: 16,
        border: `2px solid ${colors.border}`,
        borderLeft: `6px solid ${colors.border}`,
        overflow: 'hidden',
        transition: 'all 0.2s',
      }}
    >
      {/* CARD HEADER */}
      <div style={{ padding: 24 }}>
        <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 16 }}>
          <div style={{ display: 'flex', gap: 16, flex: 1 }}>
            {/* AVATAR */}
            <div
              style={{
                width: 64,
                height: 64,
                borderRadius: 12,
                background: `linear-gradient(135deg, ${colors.border}, ${colors.text})`,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: 24,
                fontWeight: 700,
                color: '#fff',
                flexShrink: 0,
                position: 'relative',
              }}
            >
              {contact.name
                .split(' ')
                .map((n) => n[0])
                .join('')
                .substring(0, 2)
                .toUpperCase()}
              {contact.contact_type === 'prospect' && (
                <div style={{
                  position: 'absolute',
                  top: -6,
                  right: -6,
                  width: 24,
                  height: 24,
                  borderRadius: 999,
                  background: '#22c55e',
                  border: '3px solid #020617',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: 12,
                }}>
                  ✨
                </div>
              )}
            </div>

            {/* INFO */}
            <div style={{ flex: 1 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6, flexWrap: 'wrap' }}>
                <div style={{ fontSize: 20, fontWeight: 700, color: '#e5e7eb' }}>{contact.name}</div>
                <span style={{
                  fontSize: 11,
                  fontWeight: 700,
                  padding: '3px 8px',
                  borderRadius: 4,
                  background: colors.bg,
                  border: `1px solid ${colors.border}`,
                  color: colors.text,
                }}>
                  {contact.urgency_label}
                </span>
                {contact.contact_type === 'prospect' && (
                  <span style={{
                    fontSize: 11,
                    fontWeight: 700,
                    padding: '3px 8px',
                    borderRadius: 4,
                    background: 'rgba(34,197,94,0.15)',
                    border: '1px solid rgba(34,197,94,0.5)',
                    color: '#22c55e',
                  }}>
                    NEW PROSPECT
                  </span>
                )}
              </div>
              <div style={{ fontSize: 14, color: '#cbd5e1', marginBottom: 4 }}>
                {contact.title} at {contact.company}
              </div>
              <div style={{ fontSize: 13, color: '#9ca3af', display: 'flex', alignItems: 'center', gap: 6 }}>
                {contact.contact_type === 'relationship' ? (
                  <>
                    <Clock size={14} />
                    {contact.days_since_contact === 0
                      ? 'Contacted today'
                      : `Last contact: ${contact.days_since_contact} days ago`}
                  </>
                ) : (
                  <>
                    <Sparkles size={14} />
                    Never contacted before
                  </>
                )}
              </div>
            </div>
          </div>

          {/* SCORES */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 4, alignItems: 'flex-end' }}>
            {contact.priority_score && (
              <div style={{ fontSize: 24, fontWeight: 700, color: '#22c55e' }}>
                {(contact.priority_score ?? 0).toFixed(0)}
              </div>
            )}
            <div style={{ fontSize: 11, color: '#9ca3af' }}>Priority</div>
          </div>
        </div>

        {/* WHY NOW */}
        <div
          style={{
            background: colors.bg,
            borderRadius: 8,
            padding: 12,
            marginBottom: 16,
            border: `1px solid ${colors.border}`,
          }}
        >
          <div style={{ fontSize: 12, fontWeight: 600, color: colors.text, marginBottom: 4 }}>
            💡 {contact.contact_type === 'relationship' ? 'Why Reach Out Now' : 'Why This Prospect'}:
          </div>
          <div style={{ fontSize: 13, color: '#cbd5e1' }}>{contact.why_now}</div>
        </div>

        {/* ACTION BUTTONS */}
        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
          {contact.phone && (
            <button
              style={{
                flex: 1,
                minWidth: 120,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: 6,
                padding: '10px 16px',
                borderRadius: 8,
                background: 'linear-gradient(135deg, rgba(34,197,94,0.3), rgba(22,163,74,0.3))',
                border: '1px solid rgba(34,197,94,0.6)',
                color: '#22c55e',
                fontSize: 14,
                fontWeight: 600,
                cursor: 'pointer',
              }}
              onClick={() => window.open(`tel:${contact.phone}`)}
            >
              <Phone size={16} />
              Call
            </button>
          )}
          {contact.email && (
            <button
              style={{
                flex: 1,
                minWidth: 120,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: 6,
                padding: '10px 16px',
                borderRadius: 8,
                background: 'linear-gradient(135deg, rgba(99,102,241,0.3), rgba(79,70,229,0.3))',
                border: '1px solid rgba(99,102,241,0.6)',
                color: '#818cf8',
                fontSize: 14,
                fontWeight: 600,
                cursor: 'pointer',
              }}
              onClick={() => window.open(`mailto:${contact.email}`)}
            >
              <Mail size={16} />
              Email
            </button>
          )}
          <button
            style={{
              flex: 1,
              minWidth: 120,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: 6,
              padding: '10px 16px',
              borderRadius: 8,
              background: 'linear-gradient(135deg, rgba(14,165,233,0.3), rgba(2,132,199,0.3))',
              border: '1px solid rgba(14,165,233,0.6)',
              color: '#38bdf8',
              fontSize: 14,
              fontWeight: 600,
              cursor: 'pointer',
            }}
            onClick={() => window.open(`https://linkedin.com/search/results/all/?keywords=${encodeURIComponent(contact.name + ' ' + contact.company)}`)}
          >
            <Linkedin size={16} />
            LinkedIn
          </button>
          <button
            onClick={onSelect}
            style={{
              flex: 1,
              minWidth: 120,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: 6,
              padding: '10px 16px',
              borderRadius: 8,
              background: 'rgba(148,163,184,0.2)',
              border: '1px solid rgba(148,163,184,0.5)',
              color: '#cbd5e1',
              fontSize: 14,
              fontWeight: 600,
              cursor: 'pointer',
            }}
          >
            <ExternalLink size={16} />
            Full Dossier
          </button>
        </div>

        {/* SHOW CONTENT TOGGLE */}
        {hasContent && (
          <button
            onClick={() => setShowContent(!showContent)}
            style={{
              width: '100%',
              marginTop: 12,
              padding: '8px 12px',
              borderRadius: 8,
              background: 'rgba(99,102,241,0.1)',
              border: '1px solid rgba(99,102,241,0.3)',
              color: '#a5b4fc',
              fontSize: 13,
              fontWeight: 600,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: 6,
            }}
          >
            <Sparkles size={14} />
            {showContent ? 'Hide' : 'Show'} AI-Generated Content
            <ChevronRight size={14} style={{ transform: showContent ? 'rotate(90deg)' : 'rotate(0deg)', transition: 'transform 0.2s' }} />
          </button>
        )}
      </div>

      {/* EXPANDABLE CONTENT */}
      {showContent && hasContent && (
        <div style={{ borderTop: '1px solid rgba(148,163,184,0.2)', padding: 24, background: 'rgba(15,23,42,0.5)' }}>
          {contact.email_1_body && (
            <div style={{ marginBottom: 16 }}>
              <div style={{ fontSize: 13, fontWeight: 600, color: '#9ca3af', marginBottom: 8, display: 'flex', alignItems: 'center', gap: 6 }}>
                <Mail size={14} />
                Email Draft
              </div>
              <div style={{ fontSize: 13, color: '#cbd5e1', whiteSpace: 'pre-wrap', background: 'rgba(30,41,59,0.5)', padding: 12, borderRadius: 8, border: '1px solid rgba(148,163,184,0.2)' }}>
                <strong>Subject:</strong> {contact.email_1_subject}<br /><br />
                {contact.email_1_body}
              </div>
            </div>
          )}
          {contact.call_script_1 && (
            <div style={{ marginBottom: 16 }}>
              <div style={{ fontSize: 13, fontWeight: 600, color: '#9ca3af', marginBottom: 8, display: 'flex', alignItems: 'center', gap: 6 }}>
                <Phone size={14} />
                Call Script
              </div>
              <div style={{ fontSize: 13, color: '#cbd5e1', whiteSpace: 'pre-wrap', background: 'rgba(30,41,59,0.5)', padding: 12, borderRadius: 8, border: '1px solid rgba(148,163,184,0.2)' }}>
                {contact.call_script_1}
              </div>
            </div>
          )}
          {contact.linkedin_connect && (
            <div>
              <div style={{ fontSize: 13, fontWeight: 600, color: '#9ca3af', marginBottom: 8, display: 'flex', alignItems: 'center', gap: 6 }}>
                <Linkedin size={14} />
                LinkedIn Message
              </div>
              <div style={{ fontSize: 13, color: '#cbd5e1', whiteSpace: 'pre-wrap', background: 'rgba(30,41,59,0.5)', padding: 12, borderRadius: 8, border: '1px solid rgba(148,163,184,0.2)' }}>
                {contact.linkedin_connect}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
                  