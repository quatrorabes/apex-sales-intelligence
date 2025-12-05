cat > /Users/chrisrabenold/projects/apex/dashboard_v1/src/pages/ContactDetailPage.tsx << 'ENDOFFILE'
// =============================================================================
// FILE: /dashboard_v1/src/pages/ContactDetailPage.tsx
// APEX SALES INTELLIGENCE - HULY-STYLE CONTACT DETAIL PAGE
// Version: 3.0 | Flexible Parser | December 4, 2025
// =============================================================================

import React, { useState, useEffect, useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';

// =============================================================================
// DESIGN TOKENS - HULY DARK THEME
// =============================================================================
const colors = {
  bg: {
    app: '#050608',
    sidebar: '#111319',
    surface: '#151821',
    surfaceAlt: '#1a1e28',
    surfaceElevated: '#1e2230',
  },
  text: {
    primary: '#F5F7FB',
    secondary: '#A2A8B8',
    muted: '#6B7180',
  },
  accent: {
    blue: '#4B8AFF',
    orange: '#FF9A4A',
    pink: '#F27AD6',
    violet: '#A56BFF',
    lime: '#34D399',
    danger: '#FF6A4F',
  },
  border: {
    subtle: 'rgba(255,255,255,0.04)',
    medium: 'rgba(255,255,255,0.08)',
  },
};

// =============================================================================
// TYPES
// =============================================================================
interface Contact {
  id: number;
  name: string;
  title: string;
  company: string;
  email: string;
  phone?: string;
  linkedin_url?: string;
  mdcp_score?: number;
  enrichment_status?: string;
  enriched_at?: string;
  profile_content?: string;
}

type TabKey = 'overview' | 'professional' | 'company' | 'pain' | 'sales' | 'outreach';

// =============================================================================
// TAB CONFIGURATION
// =============================================================================
const TABS: { key: TabKey; label: string; icon: string }[] = [
  { key: 'overview', label: 'Overview', icon: '📊' },
  { key: 'professional', label: 'Professional', icon: '🧠' },
  { key: 'company', label: 'Company', icon: '🏢' },
  { key: 'pain', label: 'Pain Points', icon: '🎯' },
  { key: 'sales', label: 'Sales Intel', icon: '💰' },
  { key: 'outreach', label: 'Outreach', icon: '✉️' },
];

// =============================================================================
// FLEXIBLE CONTENT PARSER - Handles multiple formats
// =============================================================================
function parseProfileContent(content: string, contactName: string, company: string): Record<TabKey, string> {
  const result: Record<TabKey, string> = {
    overview: '', professional: '', company: '', pain: '', sales: '', outreach: ''
  };
  
  if (!content) return result;

  // ============================================
  // FORMAT 1: Numbered sections (# 1., # 2., etc.)
  // ============================================
  const numberedMatch = content.match(/^# \d+\./m);
  if (numberedMatch) {
    const sections = content.split(/(?=^# \d+\. )/m);
    for (const section of sections) {
      const match = section.match(/^# (\d+)\./);
      if (!match) continue;
      const num = match[1];
      const sectionContent = section.replace(/^# \d+\.[^\n]*\n?/, '').trim();
      
      switch (num) {
        case '1': result.overview = sectionContent; break;
        case '2': result.professional = sectionContent; break;
        case '3': result.professional += '\n\n---\n\n' + sectionContent; break; // Personality goes with Professional
        case '4': result.company = sectionContent; break;
        case '5': result.pain = sectionContent; break;
        case '6': result.sales = sectionContent; break;
      }
    }
    return result;
  }

  // ============================================
  // FORMAT 2: Raw Perplexity with named headers
  // ============================================
  
  // Helper to extract section between patterns
  const extractBetween = (startPatterns: RegExp[], endPatterns: RegExp[]): string => {
    for (const startPattern of startPatterns) {
      const startMatch = content.match(startPattern);
      if (startMatch && startMatch.index !== undefined) {
        const startIdx = startMatch.index + startMatch[0].length;
        let endIdx = content.length;
        
        for (const endPattern of endPatterns) {
          const searchContent = content.slice(startIdx);
          const endMatch = searchContent.match(endPattern);
          if (endMatch && endMatch.index !== undefined) {
            const possibleEnd = startIdx + endMatch.index;
            if (possibleEnd < endIdx) endIdx = possibleEnd;
          }
        }
        
        return content.slice(startIdx, endIdx).trim();
      }
    }
    return '';
  };

  // Major section boundaries
  const sectionBoundaries = [
    /\n#{1,2}\s+[A-Z][A-Z\s&-]+-\s+(PROFESSIONAL PROFILE|COMPANY INTELLIGENCE)/,
    /\n#{1,2}\s+(EXECUTIVE SUMMARY|SALES OPPORTUNITY|STRATEGIC RECOMMENDATIONS)/i,
    /\n---\n/,
  ];

  // OVERVIEW / EXECUTIVE SUMMARY
  result.overview = extractBetween(
    [
      /#{1,2}\s*EXECUTIVE SUMMARY\s*\n+/i,
      /#{1,2}\s*Summary\s*\n+/i,
    ],
    [
      /\n#{1,2}\s+[A-Z]/,
      /\n---\n/,
    ]
  );

  // PROFESSIONAL PROFILE (includes personality/MBTI/DISC)
  const firstName = contactName.split(' ')[0].toUpperCase();
  const fullNameUpper = contactName.toUpperCase();
  result.professional = extractBetween(
    [
      new RegExp(`#{1,2}\\s*${fullNameUpper}\\s*-\\s*PROFESSIONAL PROFILE\\s*\\n+`, 'i'),
      new RegExp(`#{1,2}\\s*${firstName}[A-Z\\s]*-\\s*PROFESSIONAL PROFILE\\s*\\n+`, 'i'),
      /#{1,2}\s+PROFESSIONAL PROFILE\s*\n+/i,
      /#{1,2}\s+Professional Background\s*\n+/i,
    ],
    [
      new RegExp(`#{1,2}\\s+[A-Z][A-Z\\s&-]+-\\s+COMPANY INTELLIGENCE`, 'i'),
      /#{1,2}\s+COMPANY INTELLIGENCE\s*\n/i,
      /#{1,2}\s+SALES OPPORTUNITY/i,
    ]
  );

  // COMPANY INTELLIGENCE
  const companyUpper = company.toUpperCase();
  result.company = extractBetween(
    [
      new RegExp(`#{1,2}\\s*${companyUpper}\\s*-\\s*COMPANY INTELLIGENCE\\s*\\n+`, 'i'),
      new RegExp(`#{1,2}\\s+[A-Z][A-Z\\s&]+\\s*-\\s*COMPANY INTELLIGENCE\\s*\\n+`, 'i'),
      /#{1,2}\s+COMPANY INTELLIGENCE\s*\n+/i,
      /#{1,2}\s+Company Overview\s*\n+/i,
    ],
    [
      /#{1,2}\s+SALES OPPORTUNITY/i,
      /#{1,2}\s+STRATEGIC RECOMMENDATIONS/i,
      /\n---\n/,
    ]
  );

  // PAIN POINTS (usually in Sales Opportunity section)
  result.pain = extractBetween(
    [
      /#{1,2}\s+SALES OPPORTUNITY ANALYSIS\s*\n+/i,
      /\*\*Pain Points & Business Challenges\*\*\s*\n+/i,
      /#{2,3}\s+Pain Points/i,
    ],
    [
      /#{1,2}\s+STRATEGIC RECOMMENDATIONS/i,
      /#{1,2}\s+OUTREACH/i,
      /\n---\n/,
    ]
  );

  // SALES INTEL / STRATEGIC RECOMMENDATIONS
  result.sales = extractBetween(
    [
      /#{1,2}\s+STRATEGIC RECOMMENDATIONS\s*\n+/i,
      /#{2,3}\s+Trigger Events/i,
      /\*\*Current Conditions Creating Opportunity\*\*/i,
    ],
    [
      /#{1,2}\s+OUTREACH/i,
      /$/,
    ]
  );

  // If we got nothing, put everything in overview as fallback
  if (!result.overview && !result.professional && !result.company) {
    result.overview = content;
  }

  return result;
}

// =============================================================================
// MARKDOWN RENDERER - Renders content with proper styling
// =============================================================================
const MarkdownContent: React.FC<{ content: string }> = ({ content }) => {
  if (!content || content.trim().length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-center">
        <div className="text-5xl mb-4 opacity-30">📭</div>
        <p style={{ color: colors.text.muted }}>No content available for this section</p>
      </div>
    );
  }

  const renderContent = () => {
    const lines = content.split('\n');
    const elements: React.ReactNode[] = [];
    let i = 0;
    let key = 0;

    while (i < lines.length) {
      const line = lines[i];
      const trimmed = line.trim();

      // Skip empty lines
      if (!trimmed) { i++; continue; }

      // Horizontal rule
      if (trimmed === '---') {
        elements.push(<hr key={key++} style={{ border: 'none', borderTop: `1px solid ${colors.border.subtle}`, margin: '32px 0' }} />);
        i++; continue;
      }

      // H2 Headers (## or ### with ALL CAPS or title case)
      if (/^#{2,3}\s+/.test(trimmed)) {
        const text = trimmed.replace(/^#{2,3}\s+/, '');
        elements.push(
          <div key={key++} style={{ marginTop: '32px', marginBottom: '16px' }}>
            <h2 style={{ 
              fontSize: '17px', 
              fontWeight: 600, 
              color: colors.text.primary,
              display: 'flex',
              alignItems: 'center',
              gap: '12px'
            }}>
              <span style={{ 
                width: '6px', 
                height: '6px', 
                borderRadius: '50%', 
                backgroundColor: colors.accent.orange 
              }} />
              {text}
            </h2>
            <div style={{ 
              height: '1px', 
              background: `linear-gradient(to right, ${colors.border.medium}, transparent)`,
              marginTop: '12px'
            }} />
          </div>
        );
        i++; continue;
      }

      // Bold section headers (**Title**)
      if (trimmed.startsWith('**') && trimmed.endsWith('**') && !trimmed.includes(':')) {
        const text = trimmed.slice(2, -2);
        elements.push(
          <h3 key={key++} style={{ 
            fontSize: '15px', 
            fontWeight: 600, 
            color: colors.text.primary,
            marginTop: '24px',
            marginBottom: '12px'
          }}>
            {text}
          </h3>
        );
        i++; continue;
      }

      // Tables (| col | col |)
      if (trimmed.startsWith('|') && trimmed.endsWith('|')) {
        const tableRows: string[][] = [];
        let headers: string[] = [];
        let j = i;
        
        while (j < lines.length && lines[j].trim().startsWith('|')) {
          const row = lines[j].trim();
          const cells = row.slice(1, -1).split('|').map(c => c.trim());
          
          if (cells.every(c => /^[-:]+$/.test(c))) { j++; continue; }
          
          if (headers.length === 0) {
            headers = cells;
          } else {
            tableRows.push(cells);
          }
          j++;
        }

        elements.push(
          <div key={key++} style={{ 
            margin: '20px 0', 
            borderRadius: '12px', 
            overflow: 'hidden',
            border: `1px solid ${colors.border.subtle}`,
            backgroundColor: colors.bg.surface
          }}>
            <table style={{ width: '100%', fontSize: '13px', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ backgroundColor: colors.bg.surfaceAlt }}>
                  {headers.map((h, idx) => (
                    <th key={idx} style={{ 
                      textAlign: 'left', 
                      padding: '12px 16px', 
                      fontWeight: 600,
                      color: colors.text.secondary,
                      borderBottom: `1px solid ${colors.border.subtle}`
                    }}>
                      {formatText(h)}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {tableRows.map((row, rowIdx) => (
                  <tr key={rowIdx}>
                    {row.map((cell, cellIdx) => (
                      <td key={cellIdx} style={{ 
                        padding: '12px 16px', 
                        color: colors.text.primary,
                        borderBottom: rowIdx < tableRows.length - 1 ? `1px solid ${colors.border.subtle}` : 'none'
                      }}>
                        {formatText(cell)}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        );
        i = j;
        continue;
      }

      // Bullet lists
      if (trimmed.startsWith('- ') || trimmed.startsWith('* ')) {
        const listItems: string[] = [];
        let j = i;
        while (j < lines.length && (lines[j].trim().startsWith('- ') || lines[j].trim().startsWith('* '))) {
          listItems.push(lines[j].trim().slice(2));
          j++;
        }
        
        elements.push(
          <ul key={key++} style={{ margin: '16px 0', paddingLeft: 0, listStyle: 'none' }}>
            {listItems.map((item, idx) => (
              <li key={idx} style={{ 
                display: 'flex', 
                alignItems: 'flex-start', 
                gap: '12px',
                marginBottom: '8px',
                fontSize: '13px',
                color: colors.text.secondary,
                lineHeight: 1.6
              }}>
                <span style={{ 
                  marginTop: '8px',
                  width: '5px', 
                  height: '5px', 
                  borderRadius: '50%', 
                  backgroundColor: colors.accent.blue,
                  flexShrink: 0
                }} />
                <span dangerouslySetInnerHTML={{ __html: formatText(item) }} />
              </li>
            ))}
          </ul>
        );
        i = j;
        continue;
      }

      // Bold label with value (**Label:** Value or **Label**: Value)
      if (trimmed.match(/^\*\*[^*]+\*\*:?\s*.+/)) {
        elements.push(
          <p key={key++} style={{ 
            margin: '8px 0', 
            fontSize: '13px', 
            lineHeight: 1.7,
            color: colors.text.secondary
          }} dangerouslySetInnerHTML={{ __html: formatText(trimmed) }} />
        );
        i++; continue;
      }

      // Regular paragraph
      elements.push(
        <p key={key++} style={{ 
          margin: '12px 0', 
          fontSize: '13px', 
          lineHeight: 1.7,
          color: colors.text.secondary
        }} dangerouslySetInnerHTML={{ __html: formatText(trimmed) }} />
      );
      i++;
    }

    return elements;
  };

  return <div>{renderContent()}</div>;
};

// Format inline text (bold, etc.)
function formatText(text: string): string {
  return text
    .replace(/\*\*([^*]+)\*\*/g, `<strong style="color: ${colors.text.primary}; font-weight: 600;">$1</strong>`)
    .replace(/🟢/g, `<span style="color: ${colors.accent.lime}">●</span>`)
    .replace(/🟡/g, `<span style="color: ${colors.accent.orange}">●</span>`)
    .replace(/🔴/g, `<span style="color: ${colors.accent.danger}">●</span>`)
    .replace(/✅/g, `<span style="color: ${colors.accent.lime}">✓</span>`)
    .replace(/❌/g, `<span style="color: ${colors.accent.danger}">✗</span>`)
    .replace(/\[(\d+)\]/g, `<sup style="color: ${colors.text.muted}; font-size: 10px;">[$1]</sup>`);
}

// =============================================================================
// SCORE BADGE
// =============================================================================
const ScoreBadge: React.FC<{ score: number }> = ({ score }) => {
  const getStyle = () => {
    if (score >= 80) return { bg: 'rgba(52,211,153,0.15)', color: colors.accent.lime, glow: '0 0 24px rgba(52,211,153,0.3)' };
    if (score >= 50) return { bg: 'rgba(255,154,74,0.15)', color: colors.accent.orange, glow: '0 0 24px rgba(255,154,74,0.3)' };
    return { bg: 'rgba(107,113,128,0.15)', color: colors.text.muted, glow: 'none' };
  };
  const style = getStyle();

  return (
    <div style={{ 
      display: 'flex', 
      flexDirection: 'column', 
      alignItems: 'center', 
      justifyContent: 'center',
      width: '96px',
      height: '96px',
      borderRadius: '16px',
      backgroundColor: style.bg,
      boxShadow: style.glow,
      border: `1px solid ${colors.border.medium}`
    }}>
      <span style={{ fontSize: '36px', fontWeight: 700, color: style.color }}>{score}</span>
      <span style={{ fontSize: '10px', textTransform: 'uppercase', letterSpacing: '0.1em', color: colors.text.muted, marginTop: '4px' }}>MDCP</span>
    </div>
  );
};

// =============================================================================
// TAB NAVIGATION
// =============================================================================
const TabNav: React.FC<{
  activeTab: TabKey;
  onTabChange: (tab: TabKey) => void;
  hasContent: Record<TabKey, boolean>;
}> = ({ activeTab, onTabChange, hasContent }) => (
  <div style={{ 
    display: 'flex', 
    gap: '4px', 
    padding: '6px',
    borderRadius: '12px',
    backgroundColor: colors.bg.surface,
    border: `1px solid ${colors.border.subtle}`,
    overflowX: 'auto'
  }}>
    {TABS.map((tab) => {
      const isActive = activeTab === tab.key;
      const hasData = hasContent[tab.key];
      
      return (
        <motion.button
          key={tab.key}
          onClick={() => onTabChange(tab.key)}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            padding: '10px 16px',
            borderRadius: '8px',
            fontSize: '13px',
            fontWeight: 500,
            whiteSpace: 'nowrap',
            border: 'none',
            cursor: 'pointer',
            transition: 'all 0.15s ease',
            backgroundColor: isActive ? colors.bg.surfaceElevated : 'transparent',
            color: isActive ? colors.text.primary : colors.text.secondary,
            boxShadow: isActive ? '0 4px 12px rgba(0,0,0,0.3)' : 'none',
          }}
        >
          <span style={{ fontSize: '16px' }}>{tab.icon}</span>
          <span>{tab.label}</span>
          {hasData && !isActive && (
            <span style={{ 
              width: '6px', 
              height: '6px', 
              borderRadius: '50%', 
              backgroundColor: colors.accent.lime 
            }} />
          )}
        </motion.button>
      );
    })}
  </div>
);

// =============================================================================
// MAIN COMPONENT
// =============================================================================
const ContactDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [contact, setContact] = useState<Contact | null>(null);
  const [activeTab, setActiveTab] = useState<TabKey>('overview');
  const [loading, setLoading] = useState(true);
  const [enriching, setEnriching] = useState(false);

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  useEffect(() => {
    const fetchContact = async () => {
      try {
        const response = await fetch(`${API_URL}/api/contacts/${id}`);
        if (response.ok) setContact(await response.json());
      } catch (error) {
        console.error('Failed to fetch contact:', error);
      } finally {
        setLoading(false);
      }
    };
    if (id) fetchContact();
  }, [id, API_URL]);

  const handleEnrich = async () => {
    if (!contact || enriching) return;
    setEnriching(true);
    try {
      const response = await fetch(`${API_URL}/api/contacts/${contact.id}/enrich`, { method: 'POST' });
      const result = await response.json();
      if (result.success) {
        const poll = setInterval(async () => {
          const statusRes = await fetch(`${API_URL}/api/contacts/${contact.id}/enrichment-status`);
          const status = await statusRes.json();
          if (status.status === 'completed' || status.status === 'failed') {
            clearInterval(poll);
            const updated = await fetch(`${API_URL}/api/contacts/${contact.id}`);
            if (updated.ok) setContact(await updated.json());
            setEnriching(false);
          }
        }, 2000);
        setTimeout(() => { clearInterval(poll); setEnriching(false); }, 120000);
      }
    } catch (error) {
      console.error('Enrichment failed:', error);
      setEnriching(false);
    }
  };

  const tabContent = useMemo(() => {
    if (!contact?.profile_content) return {} as Record<TabKey, string>;
    return parseProfileContent(contact.profile_content, contact.name, contact.company);
  }, [contact?.profile_content, contact?.name, contact?.company]);

  const hasContent = useMemo(() => ({
    overview: !!tabContent.overview?.trim(),
    professional: !!tabContent.professional?.trim(),
    company: !!tabContent.company?.trim(),
    pain: !!tabContent.pain?.trim(),
    sales: !!tabContent.sales?.trim(),
    outreach: !!tabContent.outreach?.trim(),
  }), [tabContent]);

  if (loading) {
    return (
      <div style={{ 
        minHeight: '100vh', 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center',
        backgroundColor: colors.bg.app 
      }}>
        <div style={{ 
          width: '40px', 
          height: '40px', 
          border: `3px solid ${colors.accent.blue}`,
          borderTopColor: 'transparent',
          borderRadius: '50%',
          animation: 'spin 1s linear infinite'
        }} />
        <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
      </div>
    );
  }

  if (!contact) {
    return (
      <div style={{ minHeight: '100vh', padding: '32px', backgroundColor: colors.bg.app, color: colors.text.primary }}>
        <button onClick={() => navigate(-1)} style={{ color: colors.accent.blue, background: 'none', border: 'none', cursor: 'pointer', marginBottom: '16px' }}>← Back</button>
        <p>Contact not found</p>
      </div>
    );
  }

  const score = contact.mdcp_score || 0;
  const isEnriched = contact.enrichment_status === 'completed';
  const isProcessing = contact.enrichment_status === 'processing' || enriching;

  return (
    <div style={{ minHeight: '100vh', backgroundColor: colors.bg.app, color: colors.text.primary }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '32px 24px' }}>
        
        {/* Back Button */}
        <button 
          onClick={() => navigate(-1)} 
          style={{ 
            display: 'flex', 
            alignItems: 'center', 
            gap: '8px',
            fontSize: '13px', 
            fontWeight: 500,
            color: colors.text.secondary,
            background: 'none',
            border: 'none',
            cursor: 'pointer',
            marginBottom: '24px',
            padding: 0
          }}
        >
          ← Back
        </button>

        {/* Contact Header Card */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          style={{ 
            borderRadius: '16px',
            padding: '24px',
            marginBottom: '24px',
            backgroundColor: colors.bg.surface,
            border: `1px solid ${colors.border.subtle}`,
            boxShadow: '0 8px 32px rgba(0,0,0,0.4)'
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '24px' }}>
            <div style={{ flex: 1 }}>
              <h1 style={{ fontSize: '24px', fontWeight: 700, marginBottom: '4px' }}>{contact.name}</h1>
              <p style={{ fontSize: '15px', color: colors.text.secondary, marginBottom: '2px' }}>{contact.title}</p>
              <p style={{ fontSize: '13px', color: colors.text.muted }}>{contact.company}</p>
              
              {/* Contact Links */}
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '16px', marginTop: '20px' }}>
                {contact.email && (
                  <a href={`mailto:${contact.email}`} style={{ fontSize: '13px', color: colors.accent.blue, textDecoration: 'none' }}>
                    ✉️ {contact.email}
                  </a>
                )}
                {contact.phone && (
                  <a href={`tel:${contact.phone}`} style={{ fontSize: '13px', color: colors.accent.blue, textDecoration: 'none' }}>
                    📞 {contact.phone}
                  </a>
                )}
                {contact.linkedin_url && (
                  <a href={contact.linkedin_url} target="_blank" rel="noopener noreferrer" style={{ fontSize: '13px', color: colors.accent.blue, textDecoration: 'none' }}>
                    🔗 LinkedIn →
                  </a>
                )}
              </div>

              {/* Actions */}
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginTop: '24px' }}>
                {isProcessing ? (
                  <span style={{ 
                    padding: '8px 16px', 
                    borderRadius: '8px', 
                    fontSize: '12px', 
                    fontWeight: 500,
                    backgroundColor: 'rgba(255,154,74,0.15)', 
                    color: colors.accent.orange,
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px'
                  }}>
                    <span style={{ width: '12px', height: '12px', border: `2px solid ${colors.accent.orange}`, borderTopColor: 'transparent', borderRadius: '50%', animation: 'spin 1s linear infinite' }} />
                    Enriching...
                  </span>
                ) : isEnriched ? (
                  <span style={{ 
                    padding: '8px 16px', 
                    borderRadius: '8px', 
                    fontSize: '12px', 
                    fontWeight: 500,
                    backgroundColor: 'rgba(52,211,153,0.15)', 
                    color: colors.accent.lime 
                  }}>
                    ✓ Enriched
                  </span>
                ) : (
                  <span style={{ 
                    padding: '8px 16px', 
                    borderRadius: '8px', 
                    fontSize: '12px', 
                    fontWeight: 500,
                    backgroundColor: 'rgba(107,113,128,0.15)', 
                    color: colors.text.muted 
                  }}>
                    ⏳ Pending
                  </span>
                )}
                
                <button 
                  onClick={handleEnrich}
                  disabled={isProcessing}
                  style={{ 
                    padding: '8px 20px', 
                    borderRadius: '8px', 
                    fontSize: '13px', 
                    fontWeight: 600,
                    backgroundColor: colors.accent.blue,
                    color: '#fff',
                    border: 'none',
                    cursor: isProcessing ? 'not-allowed' : 'pointer',
                    opacity: isProcessing ? 0.5 : 1,
                    boxShadow: '0 0 20px rgba(75,138,255,0.3)'
                  }}
                >
                  {isProcessing ? '⚡ Processing...' : isEnriched ? '🔄 Re-Enrich' : '⚡ Enrich Now'}
                </button>

                {contact.enriched_at && (
                  <span style={{ fontSize: '11px', color: colors.text.muted, marginLeft: 'auto' }}>
                    Last: {new Date(contact.enriched_at).toLocaleString()}
                  </span>
                )}
              </div>
            </div>

            <ScoreBadge score={score} />
          </div>
        </motion.div>

        {/* Tabs */}
        {isEnriched && <TabNav activeTab={activeTab} onTabChange={setActiveTab} hasContent={hasContent} />}

        {/* Tab Content */}
        {isEnriched && (
          <AnimatePresence mode="wait">
            <motion.div
              key={activeTab}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -12 }}
              transition={{ duration: 0.2 }}
              style={{ 
                marginTop: '24px',
                borderRadius: '16px',
                padding: '32px',
                backgroundColor: colors.bg.surface,
                border: `1px solid ${colors.border.subtle}`,
                boxShadow: '0 8px 32px rgba(0,0,0,0.4)'
              }}
            >
              <MarkdownContent content={tabContent[activeTab]} />
            </motion.div>
          </AnimatePresence>
        )}

        {/* Empty state */}
        {!isEnriched && !isProcessing && (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            style={{ 
              marginTop: '24px',
              borderRadius: '16px',
              padding: '64px 32px',
              textAlign: 'center',
              backgroundColor: colors.bg.surface,
              border: `1px solid ${colors.border.subtle}`
            }}
          >
            <div style={{ fontSize: '64px', marginBottom: '20px' }}>🤖</div>
            <h3 style={{ fontSize: '20px', fontWeight: 700, marginBottom: '8px' }}>Ready for Intelligence</h3>
            <p style={{ color: colors.text.secondary, marginBottom: '32px', maxWidth: '400px', margin: '0 auto 32px' }}>
              Click "Enrich Now" to generate a comprehensive sales intelligence dossier.
            </p>
            <button 
              onClick={handleEnrich}
              style={{ 
                padding: '12px 32px', 
                borderRadius: '12px', 
                fontSize: '14px', 
                fontWeight: 600,
                backgroundColor: colors.accent.blue,
                color: '#fff',
                border: 'none',
                cursor: 'pointer',
                boxShadow: '0 0 24px rgba(75,138,255,0.4)'
              }}
            >
              ⚡ Enrich Now
            </button>
          </motion.div>
        )}
      </div>
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  );
};

export default ContactDetailPage;
ENDOFFILE
