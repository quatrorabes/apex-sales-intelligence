
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeft, Briefcase, Building2, Mail, Phone, Linkedin, MapPin,
  TrendingUp, GraduationCap, CheckCircle2, User, MessageSquare,
  UserCheck, Brain, FileText, DollarSign, Layers, Target, BarChart3,
  Zap, AlertTriangle, Shield, Lightbulb, Download, Loader2
} from 'lucide-react';

// =============================================================================
// TYPES
// =============================================================================
interface Contact {
  id: string;
  first_name: string;
  lastname: string;
  email: string;
  phone: string;
  company: string;
  title: string;
  enrichment_status: string;
  enrichment: any | null;          // v2.0 backend enrichment JSON
  profile_content: string | null;  // legacy raw profile (v1.0)
  linkedin_url: string | null;
  last_enriched: string | null;
}

interface ParsedSection {
  title: string;
  content: string[];
}

// =============================================================================
// BACKEND v2.0 SECTION READING (NEW) + v1.0 FALLBACK
// =============================================================================

function getSectionsFromEnrichment(contact: Contact): any | null {
  const enrichment = contact.enrichment || null;

  // v2.0: backend-parsed sections
  if (enrichment?.sections && Object.keys(enrichment.sections).length > 0) {
    console.log('[APEX v2.0] Using backend-parsed sections', {
      version: enrichment.version,
      sectionCount: Object.keys(enrichment.sections).length,
      format: enrichment.metadata?.format_detected
    });
    return enrichment.sections;
  }

  // v1.0: legacy raw text parsing
  const raw = enrichment?.raw_profile || contact.profile_content || '';
  if (raw && raw.length > 100) {
    console.log('[APEX v1.0] Fallback to frontend parsing (legacy data)');
    return parseRawProfileLegacy(raw);
  }

  return null;
}

// Legacy parser: break raw_profile into high-level sections
function parseRawProfileLegacy(raw: string): any {
  const sections: any = {};
  sections.person_research = extractSection(raw, 'person');
  sections.company_research = extractSection(raw, 'company');
  sections.sales_intelligence = extractSection(raw, 'sales');
  sections.personality_analysis = extractSection(raw, 'personality');
  return sections;
}

// =============================================================================
// LEGACY LOW-LEVEL PARSERS (KEPT INTACT)
// =============================================================================

function extractSection(content: string, type: 'person' | 'company' | 'sales' | 'personality'): string {
  if (!content) return '';

  const trimmed = content.trim();
  if (trimmed.startsWith('{') || trimmed.startsWith('"')) {
    try {
      const data = JSON.parse(trimmed.startsWith('"') ? trimmed : trimmed);
      const jsonMap: Record<string, string[]> = {
        person: ['EXECUTIVE SUMMARY', 'EXECUTIVE_SUMMARY', 'summary', 'overview'],
        company: ['COMPANY', 'company_overview', 'company'],
        sales: ['PAIN_POINTS', 'PAIN POINTS', 'OPPORTUNITIES', 'BUYING_TRIGGERS', 'pain_points'],
        personality: ['PERSONALITY_ASSESSMENT', 'PERSONALITY', 'personality']
      };

      for (const key of jsonMap[type]) {
        if (data[key]) {
          return typeof data[key] === 'string' ? data[key] : JSON.stringify(data[key], null, 2);
        }
      }
    } catch {
      // fall through
    }
  }

  const markdownPatterns: Record<string, RegExp[]> = {
    person: [
      /===\s*PERSON RESEARCH[\s\S]*?===/i,
      /##\s*.*?Professional Profile([\s\S]*?)(?=##\s*.*?Company|##\s*Sales|$)/i,
      /###\s*Overview([\s\S]*?)(?=###|##|$)/i
    ],
    company: [
      /===\s*COMPANY RESEARCH[\s\S]*?===/i,
      /##\s*.*?Company Intelligence([\s\S]*?)(?=##\s*Sales|$)/i,
      /####\s*\*\*1\.\s*Company Overview\*\*([\s\S]*?)(?=####\s*\*\*\d+\.|===|$)/i
    ],
    sales: [
      /===\s*SALES INTELLIGENCE[\s\S]*?===/i,
      /##\s*Sales Opportunities([\s\S]*?)(?=##|$)/i,
      /\*\*Pain Points[\s\S]*?\*\*([\s\S]*?)(?=\*\*|===|$)/i
    ],
    personality: [
      /===\s*PERSONALITY ANALYSIS[\s\S]*?===/i,
      /###\s*Personality[\s\S]*?Working Style([\s\S]*?)(?=###|##|$)/i,
      /MBTI Type:([\s\S]*?)(?=\n\n|$)/i
    ]
  };

  for (const pattern of markdownPatterns[type]) {
    const match = content.match(pattern);
    if (match) {
      const extracted = match[1] || match[0];
      if (extracted.length > 50) return extracted;
    }
  }

  return '';
}

// Parse **Title:** sections with bullet points
function parseStarSections(text: string): ParsedSection[] {
  if (!text) return [];
  const sections: ParsedSection[] = [];
  const regex = /\*\*([^*\n:]+):?\*\*\s*([\s\S]*?)(?=\*\*[^*\n]+:?\*\*|####|===|###|$)/gi;

  let match;
  while ((match = regex.exec(text)) !== null) {
    const title = match[1].trim();
    const body = match[2] || '';
    const lines = body
      .split('\n')
      .map(l => l.replace(/^[-•*]\s*/, '').replace(/\[\d+\]/g, '').trim())
      .filter(l => l.length > 3 && !l.match(/^-+$/) && !l.startsWith('**') && !l.startsWith('####'));

    if (title && lines.length > 0) {
      sections.push({ title, content: lines });
    }
  }

  return sections;
}

// Parse #### **1. Title** sections (Company format)
function parseNumberedSections(text: string): ParsedSection[] {
  if (!text) return [];
  const sections: ParsedSection[] = [];
  const regex = /(?:####\s*)?\*\*(\d+)\s*\.\s*([^*]+)\*\*\s*([\s\S]*?)(?=(?:####\s*)?\*\*\d+\.|===|###|$)/gi;

  let match;
  while ((match = regex.exec(text)) !== null) {
    const title = match[2].trim();
    const body = match[3] || '';
    const lines = body
      .split('\n')
      .map(l => l.replace(/^[-•*]\s*/, '').replace(/\[\d+\]/g, '').replace(/\*\*/g, '').trim())
      .filter(l => l.length > 3 && !l.match(/^-+$/) && !l.startsWith('####'));

    if (title && lines.length > 0) {
      sections.push({ title, content: lines });
    }
  }

  return sections;
}

function parseMBTI(text: string) {
  const typeMatch = text.match(/Inferred Type:?\s*\*?\*?([A-Z]{4})\*?\*?/i);
  const confMatch = text.match(/Confidence:?\s*\*?\*?(Low|Medium|High)\*?\*?/i);

  const dimensions: { dim: string; pref: string; evidence: string }[] = [];
  const dimPatterns = [
    /\*?\*?(Extroversion|Introversion)\s*\(([EI])\):?\*?\*?\s*([^\n]+)/gi,
    /\*?\*?(Intuition|Sensing)\s*\(([NS])\):?\*?\*?\s*([^\n]+)/gi,
    /\*?\*?(Thinking|Feeling)\s*\(([TF])\):?\*?\*?\s*([^\n]+)/gi,
    /\*?\*?(Judging|Perceiving)\s*\(([JP])\):?\*?\*?\s*([^\n]+)/gi
  ];

  const dimNames = ['Energy', 'Information', 'Decisions', 'Structure'];

  dimPatterns.forEach((pattern, idx) => {
    const m = text.match(pattern);
    if (m) {
      dimensions.push({
        dim: dimNames[idx],
        pref: `${m[2]} - ${m[1]}`,
        evidence: m[3].replace(/\*\*/g, '').trim()
      });
    }
  });

  return { type: typeMatch?.[1] || 'N/A', confidence: confMatch?.[1] || 'N/A', dimensions };
}

function parseDISC(text: string) {
  const primMatch = text.match(/Primary Style:?\s*\*?\*?([DISC])\s*[-–]\s*(\w+)\*?\*?/i);
  const secMatch = text.match(/Secondary Style:?\s*\*?\*?([DISC])\s*[-–]\s*(\w+)\*?\*?/i);

  return {
    primary: primMatch ? `${primMatch[1].toUpperCase()} - ${primMatch[2]}` : 'N/A',
    secondary: secMatch ? `${secMatch[1].toUpperCase()} - ${secMatch[2]}` : 'N/A'
  };
}

function parseCommPlaybook(text: string) {
  const dos: string[] = [];
  const donts: string[] = [];
  let opening = '';

  const doMatch = text.match(/(?:###\s*)?[✅]?\s*DO:?\s*(?:How to Engage)?\s*([\s\S]*?)(?=(?:###\s*)?[❌]?\s*DON'?T|$)/i);
  if (doMatch) {
    doMatch[1].split('\n').forEach(l => {
      const cleaned = l.replace(/^[-•*]\s*/, '').replace(/\*\*/g, '').trim();
      if (cleaned.length > 5 && !cleaned.match(/^DO$/i) && !cleaned.match(/^###/)) dos.push(cleaned);
    });
  }

  const dontMatch = text.match(/(?:###\s*)?[❌]?\s*DON'?T:?\s*(?:What to Avoid)?\s*([\s\S]*?)(?=(?:###\s*)?[🎯]?\s*Best Opening|$)/i);
  if (dontMatch) {
    dontMatch[1].split('\n').forEach(l => {
      const cleaned = l.replace(/^[-•*]\s*/, '').replace(/\*\*/g, '').trim();
      if (cleaned.length > 5 && !cleaned.match(/^DON/i) && !cleaned.match(/^###/)) donts.push(cleaned);
    });
  }

  const openMatch = text.match(/[🎯]?\s*Best Opening(?: Approach)?:?\s*([\s\S]*?)(?=\n\n\n|$)/i);
  if (openMatch) opening = openMatch[1].replace(/\*\*/g, '').replace(/^[-•*]\s*/gm, '').trim();

  return { dos: dos.slice(0, 5), donts: donts.slice(0, 5), opening };
}

// =============================================================================
// UI COMPONENTS
// =============================================================================

const Card: React.FC<{ title: string; icon: React.ReactNode; children: React.ReactNode; color?: string }> =
  ({ title, icon, children, color = 'text-blue-400' }) => (
    <div className="bg-[#1e2128] border border-[#2a2f38] rounded-xl mb-4 overflow-hidden">
      <div className="flex items-center gap-3 px-5 py-4 border-b border-[#2a2f38] bg-[#1a1d23]">
        <span className={color}>{icon}</span>
        <h3 className="text-white font-semibold">{title}</h3>
      </div>
      <div className="px-5 py-4 text-[#b8bcc4] text-sm leading-relaxed">{children}</div>
    </div>
  );

const DataRow: React.FC<{ label: string; value: string }> = ({ label, value }) => (
  <div className="py-2 border-b border-[#2a2f38] last:border-0 flex">
    <span className="text-[#8b919a] min-w-[160px]">{label}</span>
    <span className="text-[#e1e4e8]">{value}</span>
  </div>
);

const BulletList: React.FC<{ items: string[]; color?: string }> = ({ items, color = 'text-blue-400' }) => (
  <ul className="space-y-2">
    {items.map((item, i) => (
      <li key={i} className="flex items-start gap-2">
        <span className={`${color} mt-1`}>•</span>
        <span className="text-[#b8bcc4]">{item}</span>
      </li>
    ))}
  </ul>
);

const getIcon = (title: string) => {
  const t = title.toLowerCase();
  if (t.includes('overview') || t.includes('role') || t.includes('current')) return <Briefcase size={18} />;
  if (t.includes('career') || t.includes('history')) return <TrendingUp size={18} />;
  if (t.includes('education')) return <GraduationCap size={18} />;
  if (t.includes('achievement') || t.includes('award')) return <CheckCircle2 size={18} />;
  if (t.includes('linkedin') || t.includes('activity')) return <User size={18} />;
  if (t.includes('speaking') || t.includes('public')) return <MessageSquare size={18} />;
  if (t.includes('board') || t.includes('position')) return <UserCheck size={18} />;
  if (t.includes('management') || t.includes('style')) return <Brain size={18} />;
  if (t.includes('revenue') || t.includes('funding') || t.includes('budget')) return <DollarSign size={18} />;
  if (t.includes('product') || t.includes('service')) return <Layers size={18} />;
  if (t.includes('market') || t.includes('customer') || t.includes('target')) return <Target size={18} />;
  if (t.includes('competit')) return <BarChart3 size={18} />;
  if (t.includes('news') || t.includes('recent') || t.includes('trend')) return <Zap size={18} />;
  if (t.includes('pain') || t.includes('challenge')) return <AlertTriangle size={18} />;
  if (t.includes('regulatory') || t.includes('compliance')) return <Shield size={18} />;
  if (t.includes('trigger') || t.includes('technology')) return <Lightbulb size={18} />;
  if (t.includes('culture') || t.includes('value')) return <UserCheck size={18} />;
  if (t.includes('headquarters') || t.includes('location')) return <Building2 size={18} />;
  return <FileText size={18} />;
};

// =============================================================================
// MAIN COMPONENT
// =============================================================================

export function ContactDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [contact, setContact] = useState<Contact | null>(null);
  const [loading, setLoading] = useState(true);
  const [enriching, setEnriching] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [mainTab, setMainTab] = useState<'intelligence' | 'dossier' | 'outreach'>('dossier');
  const [subTab, setSubTab] = useState<'professional' | 'company' | 'personality' | 'raw'>('professional');

  useEffect(() => {
    fetchContact();
  }, [id]);

  const fetchContact = async () => {
    try {
      const res = await fetch(`https://apex-backend-i7b0.onrender.com/api/v2/contacts/${id}`);
      const data = await res.json();
      setContact(data.contact);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleEnrich = async () => {
    setEnriching(true);
    try {
      await fetch(`https://apex-backend-i7b0.onrender.com/api/v2/contacts/${id}/enrich`, { method: 'POST' });
      const poll = setInterval(async () => {
        const res = await fetch(`https://apex-backend-i7b0.onrender.com/api/v2/contacts/${id}/enrichment-status`);
        const data = await res.json();
        if (data.status === 'enriched' || data.status === 'error') {
          clearInterval(poll);
          fetchContact();
          setEnriching(false);
        }
      }, 2000);
    } catch (e) {
      setEnriching(false);
    }
  };

  const handleDownload = async () => {
    setGenerating(true);
    try {
      const res = await fetch(`https://apex-backend-i7b0.onrender.com/api/v2/contacts/${id}/generate-persona`, { method: 'POST' });
      if (res.ok) {
        const data = await res.json();
        if (data.files?.pdf_landscape) {
          window.open(`https://apex-backend-i7b0.onrender.com/api/download?path=${encodeURIComponent(data.files.pdf_landscape)}`, '_blank');
        }
      }
    } catch (e) {
      console.error(e);
    } finally {
      setGenerating(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0d1117] flex items-center justify-center">
        <Loader2 className="animate-spin text-blue-500" size={32} />
      </div>
    );
  }

  if (!contact) {
    return (
      <div className="min-h-screen bg-[#0d1117] flex items-center justify-center text-[#8b919a]">
        Contact not found
      </div>
    );
  }

  // =============================================================================
  // PARSE ENRICHMENT DATA (v2.0 + v1.0 fallback)
  // =============================================================================

  const sections = getSectionsFromEnrichment(contact);
  const rawText = contact.enrichment?.raw_profile || contact.profile_content || '';
  const isEnriched = contact.enrichment_status === 'enriched' && !!sections;

  const personSection =
    sections?.person_overview ||
    sections?.person_profile ||
    sections?.person_research ||
    '';

  const companySection =
    sections?.company_overview ||
    sections?.company_intelligence ||
    sections?.company_research ||
    '';

  const salesSection =
    sections?.sales_opportunities ||
    sections?.sales_intelligence ||
    '';

  const personalitySection =
    sections?.personality_analysis ||
    sections?.person_personality_and_working_style_inferred_from_role_and_quotes ||
    '';

  console.log('=== APEX PARSER DEBUG ===');
  console.log('Enrichment version:', contact.enrichment?.version || 'v1.0');
  console.log('Person section:', personSection.length, 'chars');
  console.log('Company section:', companySection.length, 'chars');
  console.log('Sales section:', salesSection.length, 'chars');

  const _personCards = parseStarSections(personSection);
  const personCards = _personCards.length > 20 ? [] : _personCards;
  const companyCards = parseNumberedSections(companySection);
  const salesCards = parseStarSections(salesSection);

  const mbti = parseMBTI(personalitySection);
  const disc = parseDISC(personalitySection);
  const comm = parseCommPlaybook(personalitySection);

  // =============================================================================
  // RENDER
  // =============================================================================

  return (
    <div className="min-h-screen bg-[#0d1117] text-white">
      {/* HEADER */}
      <div className="bg-[#161b22] border-b border-[#30363d] px-6 py-4">
        <div className="max-w-6xl mx-auto">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button
                onClick={() => navigate('/contacts')}
                className="text-[#8b919a] hover:text-white transition"
              >
                <ArrowLeft size={20} />
              </button>
              <div>
                <h1 className="text-2xl font-bold text-white">
                  {contact.first_name} {contact.lastname}
                </h1>
                <p className="text-[#8b919a] text-sm">
                  {contact.title} • {contact.company}
                </p>
              </div>
            </div>
            <div className="flex gap-3">
              {isEnriched && (
                <button
                  onClick={handleDownload}
                  disabled={generating}
                  className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg flex items-center gap-2 transition disabled:opacity-50"
                >
                  {generating ? <Loader2 className="animate-spin" size={16} /> : <Download size={16} />}
                  {generating ? 'Generating...' : 'Download PDF'}
                </button>
              )}
              <button
                onClick={handleEnrich}
                disabled={enriching}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg flex items-center gap-2 transition disabled:opacity-50"
              >
                {enriching ? <Loader2 className="animate-spin" size={16} /> : <Zap size={16} />}
                {enriching ? 'Enriching...' : isEnriched ? 'Re-enrich' : 'Enrich'}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* CONTACT INFO */}
      <div className="max-w-6xl mx-auto px-6 py-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="bg-[#161b22] border border-[#30363d] rounded-lg p-4">
            <div className="flex items-center gap-3 text-[#8b919a] mb-2">
              <Mail size={16} />
              <span className="text-xs uppercase">Email</span>
            </div>
            <p className="text-white">{contact.email || 'N/A'}</p>
          </div>
          <div className="bg-[#161b22] border border-[#30363d] rounded-lg p-4">
            <div className="flex items-center gap-3 text-[#8b919a] mb-2">
              <Phone size={16} />
              <span className="text-xs uppercase">Phone</span>
            </div>
            <p className="text-white">{contact.phone || 'N/A'}</p>
          </div>
          <div className="bg-[#161b22] border border-[#30363d] rounded-lg p-4">
            <div className="flex items-center gap-3 text-[#8b919a] mb-2">
              <Linkedin size={16} />
              <span className="text-xs uppercase">LinkedIn</span>
            </div>
            {contact.linkedin_url ? (
              <a
                href={contact.linkedin_url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-400 hover:underline"
              >
                View Profile
              </a>
            ) : (
              <p className="text-white">N/A</p>
            )}
          </div>
        </div>

        {/* MAIN TABS */}
        <div className="flex gap-2 mb-6 border-b border-[#30363d]">
          {(['dossier', 'intelligence', 'outreach'] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setMainTab(tab)}
              className={`px-6 py-3 font-medium transition ${
                mainTab === tab
                  ? 'text-blue-400 border-b-2 border-blue-400'
                  : 'text-[#8b919a] hover:text-white'
              }`}
            >
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          ))}
        </div>

        {/* DOSSIER TAB */}
        {mainTab === 'dossier' && (
          <>
            {!isEnriched ? (
              <div className="bg-[#161b22] border border-[#30363d] rounded-lg p-12 text-center">
                <Zap className="mx-auto text-[#8b919a] mb-4" size={48} />
                <h3 className="text-xl font-semibold mb-2">No Enrichment Data</h3>
                <p className="text-[#8b919a] mb-6">
                  Click &quot;Enrich&quot; to generate professional intelligence
                </p>
              </div>
            ) : (
              <>
                <div className="flex gap-2 mb-6">
                  {(['professional', 'company', 'personality', 'raw'] as const).map((tab) => (
                    <button
                      key={tab}
                      onClick={() => setSubTab(tab)}
                      className={`px-4 py-2 rounded-lg font-medium transition ${
                        subTab === tab
                          ? 'bg-blue-600 text-white'
                          : 'bg-[#161b22] text-[#8b919a] hover:bg-[#1e2128]'
                      }`}
                    >
                      {tab.charAt(0).toUpperCase() + tab.slice(1)}
                    </button>
                  ))}
                </div>

                {/* PROFESSIONAL */}
                {subTab === 'professional' && (
                  <>
                    {personCards.length > 0 ? (
                      personCards.map((section, i) => (
                        <Card key={i} title={section.title} icon={getIcon(section.title)}>
                          <BulletList items={section.content} />
                        </Card>
                      ))
                    ) : personSection.length > 100 ? (
                      <Card title="Professional Background" icon={<Briefcase size={18} />}>
                        <div className="whitespace-pre-wrap">
                          {personSection.slice(0, 2000)}
                        </div>
                      </Card>
                    ) : (
                      <div className="text-center text-[#8b919a] py-12">
                        No professional data available
                      </div>
                    )}
                  </>
                )}

                {/* COMPANY */}
                {subTab === 'company' && (
                  <>
                    {companyCards.length > 0 ? (
                      companyCards.map((section, i) => (
                        <Card
                          key={i}
                          title={section.title}
                          icon={getIcon(section.title)}
                          color="text-green-400"
                        >
                          <BulletList items={section.content} color="text-green-400" />
                        </Card>
                      ))
                    ) : companySection.length > 100 ? (
                      <Card
                        title="Company Intelligence"
                        icon={<Building2 size={18} />}
                        color="text-green-400"
                      >
                        <div className="whitespace-pre-wrap">
                          {companySection.slice(0, 2000)}
                        </div>
                      </Card>
                    ) : (
                      <div className="text-center text-[#8b919a] py-12">
                        No company data available
                      </div>
                    )}
                  </>
                )}

                {/* PERSONALITY */}
                {subTab === 'personality' && (
                  <>
                    {personalitySection.length > 100 ? (
                      <>
                        <Card
                          title="Myers-Briggs (MBTI)"
                          icon={<Brain size={18} />}
                          color="text-purple-400"
                        >
                          <DataRow label="Type" value={mbti.type} />
                          <DataRow label="Confidence" value={mbti.confidence} />
                          {mbti.dimensions.map((d, i) => (
                            <div key={i} className="mt-3">
                              <div className="text-white font-medium mb-1">
                                {d.dim}: {d.pref}
                              </div>
                              <div className="text-[#8b919a] text-sm">
                                {d.evidence}
                              </div>
                            </div>
                          ))}
                        </Card>

                        <Card
                          title="DISC Profile"
                          icon={<Target size={18} />}
                          color="text-orange-400"
                        >
                          <DataRow label="Primary Style" value={disc.primary} />
                          <DataRow label="Secondary Style" value={disc.secondary} />
                        </Card>

                        <Card
                          title="Communication Playbook"
                          icon={<MessageSquare size={18} />}
                          color="text-cyan-400"
                        >
                          <div className="mb-4">
                            <h4 className="text-white font-semibold mb-2 flex items-center gap-2">
                              <span className="text-green-400">✅</span> DO
                            </h4>
                            <BulletList items={comm.dos} color="text-green-400" />
                          </div>
                          <div className="mb-4">
                            <h4 className="text-white font-semibold mb-2 flex items-center gap-2">
                              <span className="text-red-400">❌</span> DON&apos;T
                            </h4>
                            <BulletList items={comm.donts} color="text-red-400" />
                          </div>
                          {comm.opening && (
                            <div className="mt-4 p-4 bg-[#0d1117] rounded-lg border border-[#30363d]">
                              <h4 className="text-white font-semibold mb-2 flex items-center gap-2">
                                <span className="text-yellow-400">🎯</span> Best Opening Approach
                              </h4>
                              <p className="text-[#b8bcc4]">{comm.opening}</p>
                            </div>
                          )}
                        </Card>
                      </>
                    ) : (
                      <div className="text-center text-[#8b919a] py-12">
                        No personality data available
                      </div>
                    )}
                  </>
                )}

                {/* RAW */}
                {subTab === 'raw' && (
                  <Card title="Raw Enrichment Data" icon={<FileText size={18} />}>
                    <pre className="text-xs text-[#8b919a] whitespace-pre-wrap overflow-x-auto">
                      {rawText || 'No raw data available'}
                    </pre>
                  </Card>
                )}
              </>
            )}
          </>
        )}

        {/* INTELLIGENCE TAB */}
        {mainTab === 'intelligence' && (
          <div className="bg-[#161b22] border border-[#30363d] rounded-lg p-12 text-center">
            <Target className="mx-auto text-[#8b919a] mb-4" size={48} />
            <h3 className="text-xl font-semibold mb-2">Sales Intelligence</h3>
            <p className="text-[#8b919a]">
              Coming soon: Pain points, buying triggers, and engagement strategy
            </p>
          </div>
        )}

        {/* OUTREACH TAB */}
        {mainTab === 'outreach' && (
          <div className="bg-[#161b22] border border-[#30363d] rounded-lg p-12 text-center">
            <Mail className="mx-auto text-[#8b919a] mb-4" size={48} />
            <h3 className="text-xl font-semibold mb-2">Outreach Tools</h3>
            <p className="text-[#8b919a]">
              Coming soon: Email drafts, LinkedIn messages, and call scripts
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

