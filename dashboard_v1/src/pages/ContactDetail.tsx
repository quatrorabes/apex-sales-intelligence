import { useEffect, useState, useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface Contact {
  id: number;
  name: string;
  firstname: string;
  lastname: string;
  email: string;
  phone: string;
  phone_mobile?: string;
  company: string;
  title: string;
  linkedin_url?: string;
  enrichment_status?: string;
  enriched_at?: string;
  mdcp_score?: number;
  priority_score?: number;
  profile_content?: string;
}

type TabKey = 'overview' | 'professional' | 'company' | 'pain' | 'sales' | 'outreach';

const TABS: { key: TabKey; label: string; icon: string }[] = [
  { key: 'overview', label: 'Overview', icon: '📋' },
  { key: 'professional', label: 'Professional', icon: '🧠' },
  { key: 'company', label: 'Company', icon: '🏢' },
  { key: 'pain', label: 'Pain Points', icon: '🎯' },
  { key: 'sales', label: 'Sales Intel', icon: '💰' },
  { key: 'outreach', label: 'Outreach', icon: '📧' },
];

// Parse by ## headers - match YOUR api.py output
function parseProfileContent(content: string): Record<TabKey, string> {
  const result: Record<TabKey, string> = {
    overview: '',
    professional: '',
    company: '',
    pain: '',
    sales: '',
    outreach: ''
  };
  
  if (!content) return result;
  
  // Split on ## headers
  const sections = content.split(/(?=^## )/m);
  
  for (const section of sections) {
    const headerMatch = section.match(/^## ([^\n]+)/);
    if (!headerMatch) continue;
    
    const header = headerMatch[1].toUpperCase();
    const sectionContent = section.trim();
    
    // Map headers to tabs
    if (header.includes('OVERVIEW') || header.includes('PROFILE OVERVIEW')) {
      result.overview += sectionContent + '\n\n';
    } else if (header.includes('BACKGROUND') || header.includes('PROFESSIONAL')) {
      result.professional += sectionContent + '\n\n';
    } else if (header.includes('PERSONALITY') || header.includes('MYERS') || header.includes('DISC')) {
      result.professional += sectionContent + '\n\n';
    } else if (header.includes('COMPANY') || header.includes('ORGANIZATION') || header.includes('BOK') || header.includes('BUSINESS')) {
      result.company += sectionContent + '\n\n';
    } else if (header.includes('PAIN') || header.includes('CHALLENGE')) {
      result.pain += sectionContent + '\n\n';
    } else if (header.includes('INSIGHT') || header.includes('STRATEGIC') || header.includes('TRIGGER') || header.includes('OPPORTUNITY')) {
      result.sales += sectionContent + '\n\n';
    } else if (header.includes('OPENING') || header.includes('OUTREACH') || header.includes('RECOMMENDED') || header.includes('ENGAGEMENT')) {
      result.outreach += sectionContent + '\n\n';
    } else if (header.includes('NOTE') || header.includes('ADDITIONAL')) {
      result.sales += sectionContent + '\n\n';
    }
  }
  
  // Trim all
  for (const key of Object.keys(result) as TabKey[]) {
    result[key] = result[key].trim();
  }
  
  // If nothing parsed, put everything in overview
  if (!Object.values(result).some(v => v.length > 0)) {
    result.overview = content;
  }
  
  return result;
}

export default function ContactDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [contact, setContact] = useState<Contact | null>(null);
  const [loading, setLoading] = useState(true);
  const [enriching, setEnriching] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<TabKey>('overview');

  useEffect(() => { fetchContact(); }, [id]);

  const fetchContact = async () => {
    try {
      setLoading(true);
      const res = await fetch(`${API_URL}/api/contacts/${id}`);
      if (!res.ok) throw new Error('Contact not found');
      setContact(await res.json());
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load');
    } finally {
      setLoading(false);
    }
  };

  const handleEnrich = async () => {
    if (!id) return;
    setEnriching(true);
    try {
      const res = await fetch(`${API_URL}/api/contacts/${id}/enrich`, { method: 'POST' });
      const data = await res.json();
      if (data.success) {
        const poll = setInterval(async () => {
          const s = await (await fetch(`${API_URL}/api/contacts/${id}/enrichment-status`)).json();
          if (s.status === 'completed' || s.status === 'failed') {
            clearInterval(poll);
            fetchContact();
            setEnriching(false);
          }
        }, 2000);
        setTimeout(() => { clearInterval(poll); fetchContact(); setEnriching(false); }, 120000);
      } else {
        alert('Enrichment failed: ' + (data.error || 'Unknown'));
        setEnriching(false);
      }
    } catch { setEnriching(false); }
  };

  const handleReset = async () => {
    if (!id || !confirm('Reset enrichment?')) return;
    await fetch(`${API_URL}/api/contacts/${id}/reset-enrichment`, { method: 'POST' });
    fetchContact();
  };

  const tabContent = useMemo(() => {
    if (!contact?.profile_content) return {} as Record<TabKey, string>;
    return parseProfileContent(contact.profile_content);
  }, [contact?.profile_content]);

  if (loading) return <div className="col-span-12 flex justify-center py-20"><div className="animate-spin h-8 w-8 border-2 border-azure-500 border-t-transparent rounded-full" /></div>;
  if (error || !contact) return <div className="col-span-12"><button onClick={() => navigate(-1)} className="text-azure-400 mb-4">← Back</button><div className="bg-rose-500/10 border border-rose-500/30 rounded-xl p-6 text-rose-400">{error || 'Not found'}</div></div>;

  const score = contact.mdcp_score || contact.priority_score || 0;
  const isEnriched = contact.enrichment_status === 'completed';
  const isProcessing = contact.enrichment_status === 'processing' || enriching;

  return (
    <>
      {/* Back */}
      <div className="col-span-12">
        <button onClick={() => navigate(-1)} className="text-azure-400 hover:text-azure-300 text-sm">← Back</button>
      </div>

      {/* Header */}
      <div className="col-span-12 bg-void-850 border border-glass-border rounded-xl p-6">
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-2xl font-bold text-slate-50">{contact.name}</h1>
            <p className="text-slate-300">{contact.title}</p>
            <p className="text-slate-500">{contact.company}</p>
          </div>
          <div className="text-center bg-void-900 rounded-xl px-6 py-4 border border-glass-border">
            <div className="text-4xl font-bold text-azure-400">{score.toFixed(0)}</div>
            <div className="text-xs text-slate-500">MDCP</div>
          </div>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6 pt-4 border-t border-glass-border text-sm">
          {contact.email && <div><div className="text-xs text-slate-500 mb-1">EMAIL</div><a href={`mailto:${contact.email}`} className="text-azure-400">{contact.email}</a></div>}
          {contact.phone && <div><div className="text-xs text-slate-500 mb-1">PHONE</div><a href={`tel:${contact.phone}`} className="text-azure-400">{contact.phone}</a></div>}
          {contact.phone_mobile && <div><div className="text-xs text-slate-500 mb-1">MOBILE</div><a href={`tel:${contact.phone_mobile}`} className="text-azure-400">{contact.phone_mobile}</a></div>}
          {contact.linkedin_url && <div><div className="text-xs text-slate-500 mb-1">LINKEDIN</div><a href={contact.linkedin_url} target="_blank" className="text-azure-400">Profile →</a></div>}
        </div>

        <div className="flex items-center gap-4 mt-6 pt-4 border-t border-glass-border">
          {isProcessing ? (
            <span className="px-4 py-2 bg-amber-500/20 text-amber-400 rounded-lg text-sm flex items-center gap-2">
              <span className="animate-spin h-4 w-4 border-2 border-amber-400 border-t-transparent rounded-full"></span> Enriching...
            </span>
          ) : isEnriched ? (
            <span className="px-4 py-2 bg-emerald-500/20 text-emerald-400 rounded-lg text-sm">✓ Enriched</span>
          ) : (
            <span className="px-4 py-2 bg-slate-500/20 text-slate-400 rounded-lg text-sm">⏳ Pending</span>
          )}
          <button onClick={handleEnrich} disabled={isProcessing} className="px-5 py-2 bg-azure-600 hover:bg-azure-500 text-white font-semibold rounded-lg disabled:opacity-50 text-sm">
            {isProcessing ? '⚡ Processing...' : isEnriched ? '🔄 Re-Enrich' : '⚡ Enrich Now'}
          </button>
          {isEnriched && <button onClick={handleReset} className="text-slate-400 hover:text-rose-400 text-sm">Reset</button>}
          {contact.enriched_at && <span className="text-xs text-slate-500 ml-auto">Last: {new Date(contact.enriched_at).toLocaleString()}</span>}
        </div>
      </div>

      {/* Tabs */}
      {isEnriched && (
        <div className="col-span-12 bg-void-850 border border-glass-border rounded-xl p-1.5 flex gap-1 overflow-x-auto">
          {TABS.map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={`flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium whitespace-nowrap transition-all ${
                activeTab === tab.key ? 'bg-azure-600 text-white' : 'text-slate-400 hover:text-slate-200 hover:bg-void-800'
              }`}
            >
              <span>{tab.icon}</span>
              <span>{tab.label}</span>
              {tabContent[tab.key]?.length > 0 && activeTab !== tab.key && <span className="w-1.5 h-1.5 bg-emerald-400 rounded-full"></span>}
            </button>
          ))}
        </div>
      )}

      {/* Content */}
      {isEnriched && (
        <div className="col-span-12 bg-void-850 border border-glass-border rounded-xl p-6 md:p-8">
          {tabContent[activeTab] ? (
            <div className="prose prose-invert prose-sm max-w-none
              prose-headings:text-slate-100 prose-headings:font-semibold
              prose-h2:text-lg prose-h2:text-azure-400 prose-h2:border-b prose-h2:border-glass-border prose-h2:pb-2 prose-h2:mb-4 prose-h2:mt-6 first:prose-h2:mt-0
              prose-h3:text-base prose-h3:text-slate-200 prose-h3:mt-4 prose-h3:mb-2
              prose-p:text-slate-300 prose-p:leading-relaxed
              prose-strong:text-slate-100
              prose-ul:text-slate-300 prose-li:my-0.5
              prose-table:text-sm
              prose-th:bg-void-900 prose-th:text-slate-400 prose-th:font-medium prose-th:px-4 prose-th:py-2 prose-th:text-left prose-th:border-b prose-th:border-glass-border
              prose-td:px-4 prose-td:py-2 prose-td:border-b prose-td:border-glass-border/50 prose-td:text-slate-300
              prose-blockquote:border-l-azure-500 prose-blockquote:bg-azure-500/10 prose-blockquote:text-azure-200 prose-blockquote:px-4 prose-blockquote:py-3 prose-blockquote:rounded-r-lg prose-blockquote:not-italic
            ">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>{tabContent[activeTab]}</ReactMarkdown>
            </div>
          ) : (
            <p className="text-slate-500 text-center py-8">No content for this section.</p>
          )}
        </div>
      )}

      {/* Empty State */}
      {!isEnriched && !isProcessing && (
        <div className="col-span-12 bg-void-850 border border-glass-border rounded-xl p-12 text-center">
          <div className="text-6xl mb-4">🤖</div>
          <h3 className="text-xl font-bold text-slate-50 mb-2">Ready for Intelligence</h3>
          <p className="text-slate-400 mb-6">Click "Enrich Now" to generate AI-powered insights.</p>
          <button onClick={handleEnrich} className="px-8 py-3 bg-azure-600 hover:bg-azure-500 text-white font-semibold rounded-xl">⚡ Enrich Now</button>
        </div>
      )}
    </>
  );
}
