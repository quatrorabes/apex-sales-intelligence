import { useParams, useNavigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { 
  User, Building2, Target, MessageSquare, TrendingUp, ChevronLeft, 
  Mail, Phone, RefreshCw, Briefcase, GraduationCap, Brain, FileText, 
  AlertTriangle, DollarSign, Zap, Shield, BarChart3, Lightbulb, 
  CheckCircle2, XCircle, Layers, UserCheck, Download, Loader2, X 
} from 'lucide-react';
import { QualificationTab } from '../components/QualificationTab';

// =============================================================================
// TYPES
// =============================================================================
interface Contact {
  id: number;
  firstname: string;
  lastname: string;
  email: string;
  phone: string;
  company: string;
  title: string;
  enrichment_status: string;
  enrichment_data: string | null;
  linkedin_url: string | null;
  last_enriched: string | null;
}

// =============================================================================
// PARSER - Matches your exact data format
// =============================================================================
function extractSection(content: string | null, sectionType: string): string {
  if (!content) return '';

  // Detect format: JSON blob vs Markdown
  const trimmed = content.trim();
  if (trimmed.startsWith('{') || trimmed.startsWith('"')) {
    // JSON format - parse and extract
    try {
      const data = JSON.parse(trimmed.startsWith('"') ? trimmed : trimmed);
      const jsonMap: Record<string, string[]> = {
        person: ['EXECUTIVE SUMMARY', 'EXECUTIVE_SUMMARY', 'summary', 'overview'],
        company: ['COMPANY', 'company_overview', 'company'],
        sales: ['PAIN_POINTS', 'PAIN POINTS', 'OPPORTUNITIES', 'BUYING_TRIGGERS', 'pain_points'],
        personality: ['PERSONALITY_ASSESSMENT', 'PERSONALITY', 'personality']
      };
      const keys = jsonMap[sectionType] || [];
      for (const key of keys) {
        if (data[key]) {
          return Array.isArray(data[key]) ? data[key].join('\n- ') : String(data[key]);
        }
      }
      return '';
    } catch {
      // Not valid JSON, try markdown
    }
  }

  // Markdown format - multiple pattern support
  const markdownPatterns: Record<string, RegExp[]> = {
    person: [
      /===\s*PERSON RESEARCH[^=]*===/i,
      /##\s*.+–\s*Professional Profile/i,
      /###?\s*Overview/i,
      /###?\s*Background/i
    ],
    company: [
      /===\s*COMPANY RESEARCH[^=]*===/i,
      /##\s*.+–\s*Company Intelligence/i,
      /###?\s*Company Overview/i
    ],
    sales: [
      /===\s*SALES INTELLIGENCE\s*===/i,
      /##\s*Sales Opportunities/i,
      /###?\s*Trigger Events/i,
      /###?\s*Pain Points/i
    ],
    personality: [
      /###?\s*PERSONALITY ANALYSIS/i,
      /###?\s*Personality\s*[&]?\s*Working Style/i,
      /###?\s*Communication style/i
    ]
  };

  const patterns = markdownPatterns[sectionType] || [];
  
  for (const pattern of patterns) {
    const match = content.match(pattern);
    if (match && match.index !== undefined) {
      const startIdx = match.index;
      const afterMarker = content.substring(startIdx);
      
      // Find next major section (## or === or ---)
      const nextMatch = afterMarker.substring(match[0].length).match(/\n##\s|\n===|\n---/);
      if (nextMatch && nextMatch.index !== undefined) {
        return afterMarker.substring(0, match[0].length + nextMatch.index).trim();
      }
      return afterMarker.trim();
    }
  }

  return '';
}

// Parse **Title:** sections with bullet points
function parseStarSections(text: string): ParsedSection[] {
  if (!text) return [];
  
  const sections: ParsedSection[] = [];
  
  // Match **Title:** or **Title** patterns
  const regex = /\*\*([^*\n:]+):?\*\*\s*([\s\S]*?)(?=\*\*[^*\n]+:?\*\*|####|===|###|$)/gi;
  
  let match;
  while ((match = regex.exec(text)) !== null) {
    const title = match[1].trim();
    const body = match[2] || '';
    
    // Parse lines - handle both bullet points and paragraphs
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
  
  // Match #### **1. Title** or just **1. Title**
  const regex = /(?:####\s*)?\*\*(\d+)\.\s*([^*]+)\*\*\s*([\s\S]*?)(?=(?:####\s*)?\*\*\d+\.|===|###|$)/gi;
  
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
  
  // Match "Extroversion (E):" or "**Extroversion (E):**" patterns
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
  
  // Match ✅ DO: or ### ✅ DO: sections
  const doMatch = text.match(/(?:###\s*)?[✅]?\s*DO:?\s*(?:How to Engage)?\s*([\s\S]*?)(?=(?:###\s*)?[❌]?\s*DON'?T|$)/i);
  if (doMatch) {
    doMatch[1].split('\n').forEach(l => {
      const cleaned = l.replace(/^[-•*]\s*/, '').replace(/\*\*/g, '').trim();
      if (cleaned.length > 5 && !cleaned.match(/^DO$/i) && !cleaned.match(/^###/)) dos.push(cleaned);
    });
  }
  
  // Match ❌ DON'T: sections
  const dontMatch = text.match(/(?:###\s*)?[❌]?\s*DON'?T:?\s*(?:What to Avoid)?\s*([\s\S]*?)(?=(?:###\s*)?[🎯]?\s*Best Opening|$)/i);
  if (dontMatch) {
    dontMatch[1].split('\n').forEach(l => {
      const cleaned = l.replace(/^[-•*]\s*/, '').replace(/\*\*/g, '').trim();
      if (cleaned.length > 5 && !cleaned.match(/^DON/i) && !cleaned.match(/^###/)) donts.push(cleaned);
    });
  }
  
  // Match 🎯 Best Opening Approach
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
export default function ContactDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  
  const [contact, setContact] = useState<Contact | null>(null);
  const [loading, setLoading] = useState(true);
  const [enriching, setEnriching] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [mainTab, setMainTab] = useState<'intelligence' | 'dossier' | 'outreach'>('dossier');
  const [subTab, setSubTab] = useState<'professional' | 'company' | 'personality' | 'raw'>('professional');

  useEffect(() => { fetchContact(); }, [id]);

  const fetchContact = async () => {
    try {
      const res = await fetch(`https://apex-backend-i7b0.onrender.com/api/contacts/${id}`);
      const data = await res.json(); setContact(data.contact);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleEnrich = async () => {
    setEnriching(true);
    try {
      await fetch(`https://apex-backend-i7b0.onrender.com/api/contacts/${id}/enrich`, { method: 'POST' });
      const poll = setInterval(async () => {
        const res = await fetch(`https://apex-backend-i7b0.onrender.com/api/contacts/${id}/enrichment-status`);
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
      const res = await fetch(`https://apex-backend-i7b0.onrender.com/api/contacts/${id}/generate-persona`, { method: 'POST' });
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

  if (loading) return <div className="min-h-screen bg-[#0d1117] flex items-center justify-center"><Loader2 className="animate-spin text-blue-500" size={32} /></div>;
  if (!contact) return <div className="min-h-screen bg-[#0d1117] flex items-center justify-center text-[#8b919a]">Contact not found</div>;

  // =============================================================================

  // Safety check - prevent crash during re-renders
  if (!contact) {
    return (
      <div className="min-h-screen bg-[#0d1117] flex items-center justify-center text-gray-400">
        Loading contact data...
      </div>
    );
  }

  // PARSE ENRICHMENT DATA
  // =============================================================================
  const raw = contact.profile_content || '';
  const isEnriched = contact.enrichment_status === 'enriched' && raw.length > 100;

  const personSection = extractSection(raw, 'person');
  const companySection = extractSection(raw, 'company');
  const salesSection = extractSection(raw, 'sales');
  const personalitySection = extractSection(raw, 'personality');

  // DEBUG - Remove after confirming it works
  console.log('=== APEX PARSER DEBUG ===');
  console.log('Raw length:', raw.length);
  console.log('Person section:', personSection.length, 'chars');
  console.log('Company section:', companySection.length, 'chars');
  console.log('Sales section:', salesSection.length, 'chars');
  console.log('Personality section:', personalitySection.length, 'chars');

  // Parse subsections
  const _personCards = parseStarSections(personSection);
  const personCards = _personCards.length > 20 ? [] : _personCards;
  const companyCards = parseNumberedSections(companySection);
  const salesCards = parseStarSections(salesSection);
  
  console.log('Person cards:', personCards.length, personCards.map(c => c.title));
  console.log('Company cards:', companyCards.length, companyCards.map(c => c.title));
  console.log('Sales cards:', salesCards.length, salesCards.map(c => c.title));

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
              <div className="w-12 h-12 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white font-bold text-lg">
                {contact.firstname[0]}{contact.lastname[0]}
              </div>
              <div>
                <div className="flex items-center gap-3">
                  <h1 className="text-xl font-bold">{contact.firstname} {contact.lastname}</h1>
                  {isEnriched && (
                    <span className="px-2 py-0.5 bg-emerald-500/20 text-emerald-400 rounded text-xs flex items-center gap-1">
                      <CheckCircle2 size={12} /> Enriched
                    </span>
                  )}
                </div>
                <p className="text-[#8b919a] text-sm">{contact.title} at {contact.company}</p>
              </div>
            </div>
            
            <div className="flex items-center gap-3">
              {isEnriched && (
                <button onClick={handleDownload} disabled={generating}
                  className="px-4 py-2 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 rounded-lg text-sm font-medium flex items-center gap-2 disabled:opacity-50">
                  {generating ? <Loader2 size={16} className="animate-spin" /> : <Download size={16} />}
                  {generating ? 'Generating...' : 'Download PDF'}
                </button>
              )}
              <button onClick={handleEnrich} disabled={enriching}
                className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 rounded-lg text-sm font-medium flex items-center gap-2 disabled:opacity-50">
                <RefreshCw size={16} className={enriching ? 'animate-spin' : ''} />
                {enriching ? 'Enriching...' : 'Re-Enrich'}
              </button>
              <button onClick={() => navigate(-1)} className="p-2 hover:bg-[#21262d] rounded-lg">
                <X size={20} />
              </button>
            </div>
          </div>
          
          <div className="flex items-center gap-6 mt-3 text-sm text-[#8b919a]">
            <span className="flex items-center gap-1"><Mail size={14} /> {contact.email}</span>
            {contact.phone && <span className="flex items-center gap-1"><Phone size={14} /> {contact.phone}</span>}
          </div>
        </div>
      </div>

      {/* MAIN TABS */}
      <div className="bg-[#161b22] border-b border-[#30363d]">
        <div className="max-w-6xl mx-auto flex">
          {[
            { id: 'intelligence', label: 'Intelligence', hasCheck: isEnriched },
            { id: 'dossier', label: 'Dossier' },
            { id: 'outreach', label: 'Outreach' }
          ].map(tab => (
            <button key={tab.id} onClick={() => setMainTab(tab.id as any)}
              className={`px-6 py-3 text-sm font-medium border-b-2 transition-all flex items-center gap-2
                ${mainTab === tab.id ? 'border-indigo-500 text-white' : 'border-transparent text-[#8b919a] hover:text-white'}`}>
              {tab.label}
              {tab.hasCheck && <CheckCircle2 size={14} className="text-emerald-400" />}
            </button>
          ))}
        </div>
      </div>

      {/* SUB TABS for Dossier */}
      {mainTab === 'dossier' && (
        <div className="bg-[#0d1117] border-b border-[#21262d] px-6">
          <div className="max-w-6xl mx-auto flex gap-1 pt-4">
            {[
              { id: 'professional', label: 'Professional', icon: <User size={14} /> },
              { id: 'company', label: 'Company', icon: <Building2 size={14} /> },
              { id: 'personality', label: 'Personality', icon: <Brain size={14} /> },
              { id: 'raw', label: 'Raw Profile', icon: <FileText size={14} /> }
            ].map(tab => (
              <button key={tab.id} onClick={() => setSubTab(tab.id as any)}
                className={`px-4 py-2 text-sm rounded-t-lg flex items-center gap-2 transition-all
                  ${subTab === tab.id ? 'bg-[#1e2128] text-white' : 'text-[#8b919a] hover:text-white'}`}>
                {tab.icon} {tab.label}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* CONTENT */}
      <div className="max-w-6xl mx-auto px-6 py-6">
        
        {/* INTELLIGENCE TAB */}
        {mainTab === 'intelligence' && (
          <div className="space-y-4">
            {salesCards.length > 0 ? salesCards.map((s, i) => (
              <Card key={i} title={s.title} icon={getIcon(s.title)} color="text-orange-400">
                <BulletList items={s.content} color="text-orange-400" />
              </Card>
            )) : (
              <Card title="Sales Intelligence" icon={<TrendingUp size={18} />}>
                <p>No sales intelligence available. Enrich this contact to generate insights.</p>
              </Card>
            )}
          </div>
        )}

        {/* DOSSIER - PROFESSIONAL */}
        {mainTab === 'dossier' && subTab === 'professional' && (
          <div className="space-y-4">
            {personCards.length > 0 ? personCards.map((s, i) => (
              <Card key={i} title={s.title} icon={getIcon(s.title)}>
                <BulletList items={s.content} />
              </Card>
            )) : (
              <Card title="Overview" icon={<User size={18} />}>
                <DataRow label="Name" value={`${contact.firstname} ${contact.lastname}`} />
                <DataRow label="Title" value={contact.title} />
                <DataRow label="Company" value={contact.company} />
                <DataRow label="Email" value={contact.email} />
                <DataRow label="Phone" value={contact.phone || 'N/A'} />
              </Card>
            )}
          </div>
        )}

        {/* DOSSIER - COMPANY */}
        {mainTab === 'dossier' && subTab === 'company' && (
          <div className="space-y-4">
            {companyCards.length > 0 ? companyCards.map((s, i) => (
              <Card key={i} title={s.title} icon={getIcon(s.title)} color="text-emerald-400">
                <BulletList items={s.content} color="text-emerald-400" />
              </Card>
            )) : (
              <Card title="Company" icon={<Building2 size={18} />}>
                <DataRow label="Company" value={contact.company} />
                <p className="mt-2 text-[#8b919a]">No company data available.</p>
              </Card>
            )}
          </div>
        )}

        {/* DOSSIER - PERSONALITY */}
        {mainTab === 'dossier' && subTab === 'personality' && (
          <div className="space-y-4">
            <Card title="Myers-Briggs (MBTI)" icon={<Brain size={18} />} color="text-purple-400">
              <div className="flex items-center gap-6 mb-4">
                <div className="bg-purple-500/20 border border-purple-500/40 px-6 py-3 rounded-xl">
                  <span className="text-purple-300 font-bold text-3xl">{mbti.type}</span>
                </div>
                <div>
                  <p className="text-[#8b919a] text-xs">Confidence</p>
                  <p className="text-white font-medium">{mbti.confidence}</p>
                </div>
              </div>
              {mbti.dimensions.length > 0 && (
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-[#30363d]">
                      <th className="text-left py-2 text-[#8b919a]">Dimension</th>
                      <th className="text-left py-2 text-[#8b919a]">Preference</th>
                      <th className="text-left py-2 text-[#8b919a]">Evidence</th>
                    </tr>
                  </thead>
                  <tbody>
                    {mbti.dimensions.map((d, i) => (
                      <tr key={i} className="border-b border-[#21262d]">
                        <td className="py-2 text-white">{d.dim}</td>
                        <td className="py-2 text-purple-300">{d.pref}</td>
                        <td className="py-2 text-[#8b919a]">{d.evidence}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </Card>

            <Card title="DISC Profile" icon={<BarChart3 size={18} />} color="text-orange-400">
              <div className="flex gap-4 mb-4">
                <div className="bg-orange-500/20 border border-orange-500/40 px-4 py-2 rounded-lg">
                  <span className="text-[#8b919a] text-xs block">Primary</span>
                  <span className="text-orange-300 font-bold">{disc.primary}</span>
                </div>
                <div className="bg-blue-500/20 border border-blue-500/40 px-4 py-2 rounded-lg">
                  <span className="text-[#8b919a] text-xs block">Secondary</span>
                  <span className="text-blue-300 font-bold">{disc.secondary}</span>
                </div>
              </div>
            </Card>

            <Card title="Communication Playbook" icon={<MessageSquare size={18} />} color="text-green-400">
              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <h4 className="flex items-center gap-2 text-green-400 font-medium mb-3">
                    <CheckCircle2 size={16} /> DO: How to Engage
                  </h4>
                  <ul className="space-y-2">
                    {comm.dos.map((d, i) => (
                      <li key={i} className="flex items-start gap-2">
                        <span className="text-green-400 mt-0.5">✓</span>
                        <span>{d}</span>
                      </li>
                    ))}
                  </ul>
                </div>
                <div>
                  <h4 className="flex items-center gap-2 text-red-400 font-medium mb-3">
                    <XCircle size={16} /> DON'T: What to Avoid
                  </h4>
                  <ul className="space-y-2">
                    {comm.donts.map((d, i) => (
                      <li key={i} className="flex items-start gap-2">
                        <span className="text-red-400 mt-0.5">✗</span>
                        <span>{d}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
              {comm.opening && (
                <div className="mt-4 pt-4 border-t border-[#30363d]">
                  <h4 className="text-blue-400 font-medium mb-2 flex items-center gap-2">
                    <Target size={16} /> Best Opening Approach
                  </h4>
                  <p className="bg-blue-500/10 border border-blue-500/30 rounded-lg p-3">{comm.opening}</p>
                </div>
              )}
            </Card>
          </div>
        )}

        {/* DOSSIER - RAW */}
        {mainTab === 'dossier' && subTab === 'raw' && (
          <Card title="Raw Enrichment Data" icon={<FileText size={18} />}>
            <pre className="text-xs text-[#8b919a] whitespace-pre-wrap font-mono bg-[#0d1117] p-4 rounded-lg max-h-[600px] overflow-y-auto">
              {raw || 'No enrichment data available.'}
            </pre>
          </Card>
        )}

        {/* OUTREACH TAB */}
        {mainTab === 'outreach' && (
          <Card title="Outreach Sequences" icon={<MessageSquare size={18} />}>
            <div className="text-center py-12">
              <MessageSquare size={48} className="mx-auto text-[#30363d] mb-4" />
              <p className="text-[#8b919a] text-lg mb-2">Coming Soon</p>
              <p className="text-[#6e7681]">AI-powered email sequences based on the contact profile.</p>
            </div>
          </Card>
        )}
      </div>
    </div>
  );
}

export { ContactDetailPage };
