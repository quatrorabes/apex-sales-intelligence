import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  ChevronLeft, Mail, Phone, ExternalLink, Loader2, Zap, Brain, Target,
  Building2, TrendingUp, MessageSquare, CheckCircle2, XCircle, Copy, Check, Clock
} from 'lucide-react';

const API_BASE = import.meta.env.VITE_API_URL || 'https://apex-backend-i7b0.onrender.com';

interface Contact {
  id: string;
  name: string;
  email: string;
  phone: string;
  company: string;
  title: string;
  linkedin_url?: string;
  enrichment_status: string;
  enrichment_data?: any;
  enrichment?: any;
  apex_score?: number;
  unified_qualification_score?: number;
  match_tier?: string;
  enriched_at?: string;
}

// CRITICAL FIX: Parse enrichment data from BOTH structures
function getEnrichmentSections(contact: Contact) {
  if (!contact) return { sections: {}, metadata: {} };

  // PRIMARY: enrichment_data.sections (new structure)
  if (contact.enrichment_data?.sections) {
    return {
      sections: contact.enrichment_data.sections,
      metadata: contact.enrichment?.metadata?.parsed_fields || {},
      format: 'structured'
    };
  }

  // SECONDARY: enrichment.sections.raw_text (legacy)
  if (contact.enrichment?.sections?.raw_text) {
    return {
      sections: { raw_text: contact.enrichment.sections.raw_text },
      metadata: contact.enrichment?.metadata?.parsed_fields || {},
      format: 'markdown'
    };
  }

  return { sections: {}, metadata: {}, format: 'none' };
}

// Card Component
const Card: React.FC<{
  title: string;
  icon: React.ReactNode;
  children: React.ReactNode;
  color?: string;
}> = ({ title, icon, children, color = 'text-blue-400' }) => (
  <div className="bg-161b22 border border-30363d rounded-lg overflow-hidden">
    <div className="px-4 py-3 border-b border-30363d flex items-center gap-2">
      <span className={color}>{icon}</span>
      <h3 className="font-semibold text-white">{title}</h3>
    </div>
    <div className="p-4">{children}</div>
  </div>
);

export default function ContactDetail() {
  const { contactId } = useParams<{ contactId: string }>();
  const navigate = useNavigate();
  const [contact, setContact] = useState<Contact | null>(null);
  const [loading, setLoading] = useState(true);
  const [enriching, setEnriching] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [mainTab, setMainTab] = useState<'dossier' | 'outreach'>('dossier');
  const [copySuccess, setCopySuccess] = useState<string | null>(null);

  useEffect(() => {
    if (contactId) fetchContact();
  }, [contactId]);

  const fetchContact = async () => {
    if (!contactId) return;
    try {
      setLoading(true);
      const res = await fetch(`${API_BASE}/api/contacts/${contactId}`);
      if (!res.ok) throw new Error('Contact not found');
      const data = await res.json();
      setContact(data.contact || data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error loading contact');
      setContact(null);
    } finally {
      setLoading(false);
    }
  };

  const handleEnrich = async () => {
    if (!contactId || enriching) return;
    setEnriching(true);
    try {
      const res = await fetch(`${API_BASE}/api/contacts/${contactId}/enrich`, {
        method: 'POST'
      });
      if (!res.ok) throw new Error('Enrichment failed');

      // Poll for completion (max 90 seconds)
      let completed = false;
      let attempts = 0;
      const maxAttempts = 45;

      const poll = setInterval(async () => {
        try {
          const statusRes = await fetch(`${API_BASE}/api/contacts/${contactId}`);
          const data = await statusRes.json();
          const c = data.contact || data;

          if (c.enrichment_status === 'completed' || c.enrichment_status === 'enriched') {
            completed = true;
            clearInterval(poll);
            setContact(c);
            setEnriching(false);
          }
          attempts++;
          if (attempts >= maxAttempts) {
            clearInterval(poll);
            setEnriching(false);
            setError('Enrichment timed out');
          }
        } catch (e) {
          console.error('Poll error:', e);
        }
      }, 2000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Enrichment error');
      setEnriching(false);
    }
  };

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopySuccess(text.substring(0, 20));
    setTimeout(() => setCopySuccess(null), 2000);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-0d1117 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="animate-spin text-blue-500 mx-auto mb-4" size={32} />
          <p className="text-8b919a">Loading contact...</p>
        </div>
      </div>
    );
  }

  if (!contact) {
    return (
      <div className="min-h-screen bg-0d1117 flex items-center justify-center">
        <div className="text-center">
          <p className="text-8b919a text-lg mb-4">{error || 'Contact not found'}</p>
          <button
            onClick={() => navigate('/')}
            className="px-4 py-2 bg-21262d hover:bg-30363d rounded-lg transition"
          >
            Back to Contacts
          </button>
        </div>
      </div>
    );
  }

  const enrichmentData = getEnrichmentSections(contact);
  const isEnriched = contact.enrichment_status === 'completed' && Object.keys(enrichmentData.sections).length > 0;

  return (
    <div className="min-h-screen bg-0d1117 text-white">
      {/* HEADER */}
      <div className="bg-161b22 border-b border-30363d">
        <div className="max-w-6xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between mb-4">
            <button
              onClick={() => navigate('/')}
              className="text-8b919a hover:text-white transition"
            >
              <ChevronLeft size={24} />
            </button>
            <div className="flex-1 ml-4">
              <h1 className="text-2xl font-bold">{contact.name}</h1>
              <p className="text-8b919a text-sm">
                {contact.title} at {contact.company}
              </p>
            </div>
            <button
              onClick={handleEnrich}
              disabled={enriching || isEnriched}
              className="px-5 py-2.5 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 disabled:from-gray-600 disabled:to-gray-600 rounded-lg flex items-center gap-2 transition font-medium shadow-lg"
            >
              {enriching ? (
                <>
                  <Loader2 className="animate-spin" size={18} />
                  Enriching...
                </>
              ) : isEnriched ? (
                <>
                  <CheckCircle2 size={18} />
                  Enriched
                </>
              ) : (
                <>
                  <Zap size={18} />
                  Enrich Profile
                </>
              )}
            </button>
          </div>

          {/* CONTACT INFO ROW */}
          <div className="flex flex-wrap gap-6 text-sm">
            {contact.email && (
              <div className="flex items-center gap-2 text-8b919a hover:text-white transition group">
                <Mail size={14} />
                <span>{contact.email}</span>
                <button
                  onClick={() => handleCopy(contact.email)}
                  className="opacity-0 group-hover:opacity-100 transition text-8b919a hover:text-white"
                >
                  {copySuccess === contact.email.substring(0, 20) ? (
                    <Check size={12} className="text-green-400" />
                  ) : (
                    <Copy size={12} />
                  )}
                </button>
              </div>
            )}
            {contact.phone && (
              <div className="flex items-center gap-2 text-8b919a">
                <Phone size={14} />
                <span>{contact.phone}</span>
              </div>
            )}
            {contact.linkedin_url && (
              <a
                href={contact.linkedin_url}
                target="_blank"
                rel="noopener"
                className="flex items-center gap-2 text-blue-400 hover:text-blue-300 transition"
              >
                <ExternalLink size={14} />
                <span>LinkedIn</span>
              </a>
            )}
            {contact.apex_score && (
              <div className="flex items-center gap-2 px-3 py-1 bg-blue-50010 border border-blue-50030 rounded-lg">
                <TrendingUp size={14} className="text-blue-400" />
                <span className="text-blue-400 font-medium">{Math.round(contact.apex_score)}</span>
              </div>
            )}
            {isEnriched && contact.enriched_at && (
              <div className="flex items-center gap-2 text-6e7681 text-xs">
                <Clock size={12} />
                Enriched {new Date(contact.enriched_at).toLocaleDateString()}
              </div>
            )}
          </div>

          {/* TABS */}
          <div className="flex gap-4 mt-4 border-b border-30363d -mb-px">
            <button
              onClick={() => setMainTab('dossier')}
              className={`px-4 py-2 text-sm font-medium transition-colors ${
                mainTab === 'dossier'
                  ? 'text-white border-b-2 border-blue-500'
                  : 'text-8b919a hover:text-white'
              }`}
            >
              <Brain className="inline mr-2" size={16} />
              Dossier
            </button>
            <button
              onClick={() => setMainTab('outreach')}
              className={`px-4 py-2 text-sm font-medium transition-colors ${
                mainTab === 'outreach'
                  ? 'text-white border-b-2 border-blue-500'
                  : 'text-8b919a hover:text-white'
              }`}
            >
              <MessageSquare className="inline mr-2" size={16} />
              Outreach
            </button>
          </div>
        </div>
      </div>

      {/* CONTENT */}
      <div className="max-w-6xl mx-auto px-6 py-6 space-y-6">
        {/* DOSSIER TAB */}
        {mainTab === 'dossier' && (
          <>
            {isEnriched ? (
              <>
                {/* ENRICHMENT SECTIONS */}
                {Object.entries(enrichmentData.sections).map(([key, value]: [string, any]) => {
                  if (key === 'raw_text' || !value) return null;

                  const sectionTitle = key
                    .split('_')
                    .map(w => w.charAt(0).toUpperCase() + w.slice(1))
                    .join(' ');

                  return (
                    <Card key={key} title={sectionTitle} icon={<Target size={18} />} color="text-green-400">
                      <p className="text-c9d1d9 text-sm whitespace-pre-wrap">{value}</p>
                    </Card>
                  );
                })}

                {/* PAIN POINTS */}
                {enrichmentData.metadata?.pain_points && enrichmentData.metadata.pain_points.length > 0 && (
                  <Card title="Pain Points" icon={<XCircle size={18} />} color="text-red-400">
                    <ul className="space-y-2">
                      {enrichmentData.metadata.pain_points.map((point: string, i: number) => (
                        <li key={i} className="flex items-start gap-2 text-c9d1d9 text-sm">
                          <span className="text-red-400 mt-1">•</span>
                          <span>{point}</span>
                        </li>
                      ))}
                    </ul>
                  </Card>
                )}

                {/* TALKING POINTS */}
                {enrichmentData.metadata?.talking_points && enrichmentData.metadata.talking_points.length > 0 && (
                  <Card title="Talking Points" icon={<Target size={18} />} color="text-purple-400">
                    <ul className="space-y-2">
                      {enrichmentData.metadata.talking_points.map((point: string, i: number) => (
                        <li key={i} className="flex items-start gap-2 text-c9d1d9 text-sm">
                          <span className="text-purple-400 mt-1">•</span>
                          <span>{point}</span>
                        </li>
                      ))}
                    </ul>
                  </Card>
                )}

                {/* BEST CONTACT CHANNEL */}
                {enrichmentData.metadata?.best_contact_channel && (
                  <Card title="Best Contact Channel" icon={<MessageSquare size={18} />} color="text-blue-400">
                    <p className="text-c9d1d9 text-sm">{enrichmentData.metadata.best_contact_channel}</p>
                  </Card>
                )}
              </>
            ) : (
              <Card title="Profile" icon={<Brain size={18} />}>
                <div className="text-center py-12">
                  <Brain size={48} className="mx-auto mb-4 text-30363d" />
                  <p className="text-8b919a text-lg mb-2">No enrichment yet</p>
                  <p className="text-6e7681 text-sm">Click "Enrich Profile" to generate AI-powered insights</p>
                </div>
              </Card>
            )}
          </>
        )}

        {/* OUTREACH TAB */}
        {mainTab === 'outreach' && (
          <Card title="Coming Soon" icon={<MessageSquare size={18} />}>
            <div className="text-center py-8">
              <p className="text-8b919a">Email sequences, call scripts, and LinkedIn outreach coming soon</p>
            </div>
          </Card>
        )}

        {error && (
          <div className="bg-red-50010 border border-red-50030 rounded-lg p-4 text-red-400 text-sm">
            {error}
          </div>
        )}
      </div>
    </div>
  );
}