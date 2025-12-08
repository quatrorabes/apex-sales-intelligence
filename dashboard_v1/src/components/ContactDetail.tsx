// =============================================================================
// ContactDetail.tsx - Apex Sales Intelligence Dashboard v1
// =============================================================================
// Universal parser for enrichment data + ICP Match integration
// Now includes "Why We're a Fit" powered by your Sales Playbook
// =============================================================================

import { useParams, useNavigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { 
  User, Building2, Target, MessageSquare, TrendingUp, 
  Mail, Phone, RefreshCw, Briefcase, GraduationCap, Brain, FileText, 
  AlertTriangle, DollarSign, Zap, Shield, BarChart3, Lightbulb, 
  CheckCircle2, XCircle, Layers, UserCheck, Download, Loader2, X,
  Sparkles, Award, ArrowRight, Settings, ThumbsUp,
  Play } from 'lucide-react';

import OutreachGenerator from './OutreachGenerator';
import EnrollCadenceModal from './EnrollCadenceModal';

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
  match_score?: number;
  match_tier?: string;
}

interface ParsedSection {
  title: string;
  content: string[];
}

interface MBTIDimension {
  dim: string;
  pref: string;
  evidence: string;
}

interface MBTIResult {
  type: string;
  confidence: string;
  dimensions: MBTIDimension[];
}

interface DISCResult {
  primary: string;
  secondary: string;
}

interface CommPlaybook {
  dos: string[];
  donts: string[];
  opening: string;
}

interface ICPMatch {
  score: number;
  reasons: string[];
  match_level: string;
}

interface WhyUsFitPoint {
  type: string;
  title: string;
  detail: string;
  impact?: string;
  proof?: string;
  metric?: string;
}

interface WhyUsFit {
  summary: string;
  points: WhyUsFitPoint[];
}

interface ICPMatchData {
  contact_id: number;
  icp_match: ICPMatch;
  why_us_fit: WhyUsFit;
  playbook_configured: boolean;
}

// =============================================================================
// SECTION EXTRACTION
// =============================================================================

function extractSection(content: string | null, sectionType: string): string {
  if (!content) return '';
  
  // === FORMAT 1: Legacy === SECTION === format ===
  const legacyMarkers: Record<string, RegExp> = {
    person: /===\s*PERSON RESEARCH[^=]*===/i,
    company: /===\s*COMPANY RESEARCH[^=]*===/i,
    sales: /===\s*SALES INTELLIGENCE\s*===/i,
    personality: /###?\s*PERSONALITY ANALYSIS/i
  };
  
  const marker = legacyMarkers[sectionType];
  if (marker) {
    const match = content.match(marker);
    if (match && match.index !== undefined) {
      const startIdx = match.index + match[0].length;
      const afterMarker = content.substring(startIdx);
      const nextMatch = afterMarker.match(/===\s*(PERSON|COMPANY|SALES)|###?\s*PERSONALITY/i);
      if (nextMatch && nextMatch.index !== undefined) {
        return afterMarker.substring(0, nextMatch.index).trim();
      }
      return afterMarker.trim();
    }
  }
  
  // === FORMAT 2: Markdown ## Header format ===
  const headerMappings: Record<string, string[]> = {
    person: ['Professional Background', 'Educational', 'Professional Credentials', 'Career', 'Communication Style'],
    company: ['Company Overview', 'Industry Context', 'Organization'],
    sales: ['Potential Business Challenges', 'Relevant Talking Points', 'Talking Points', 'Recent Activity', 'Pain Points'],
    personality: ['Communication and Contact', 'Personality']
  };
  
  const headers = headerMappings[sectionType];
  if (!headers) return '';
  
  const sections: string[] = [];
  const parts = content.split(/(?=^## )/m);
  
  for (const part of parts) {
    const headerMatch = part.match(/^## (.+)/m);
    if (headerMatch) {
      const header = headerMatch[1].trim();
      if (headers.some(h => header.toLowerCase().includes(h.toLowerCase().split(' ')[0]))) {
        sections.push(part.trim());
      }
    }
  }
  
  return sections.join('\n\n');
}


// =============================================================================
// UNIVERSAL SECTION PARSER
// =============================================================================

function parseAllSections(text: string): ParsedSection[] {
  if (!text) return [];
  
  const sections: ParsedSection[] = [];
  const seen = new Set<string>();
  
  // Pattern 1: ## or ### or #### headers
  const headerRegex = /^(#{2,4})\s+(?:\*\*)?([^#*\n]+?)(?:\*\*)?\s*$/gm;
  let match;
  const headerPositions: { title: string; start: number; end: number }[] = [];
  
  while ((match = headerRegex.exec(text)) !== null) {
    const title = match[2].replace(/\*\*/g, '').replace(/^\d+\.\s*/, '').trim();
    if (title && title.length > 2 && title.length < 80) {
      headerPositions.push({ title, start: match.index + match[0].length, end: text.length });
    }
  }
  
  for (let i = 0; i < headerPositions.length - 1; i++) {
    headerPositions[i].end = headerPositions[i + 1].start - 50;
  }
  
  headerPositions.forEach(({ title, start, end }) => {
    const key = title.toLowerCase();
    if (seen.has(key)) return;
    
    const body = text.substring(start, end);
    const lines = body
      .split('\n')
      .map(l => l.replace(/^[-•*]\s*/, '').replace(/\[\d+\]/g, '').replace(/\*\*/g, '').trim())
      .filter(l => l.length > 3 && !l.match(/^#{2,}/) && !l.match(/^-+$/));
    
    if (lines.length > 0) {
      seen.add(key);
      sections.push({ title, content: lines.slice(0, 10) });
    }
  });
  
  // Pattern 2: **Title:** or **Title**
  const boldRegex = /^\*\*([^*\n:]+):?\*\*\s*$/gm;
  const boldPositions: { title: string; start: number; end: number }[] = [];
  
  while ((match = boldRegex.exec(text)) !== null) {
    const title = match[1].trim();
    const key = title.toLowerCase();
    if (title && title.length > 2 && title.length < 60 && !seen.has(key)) {
      boldPositions.push({ title, start: match.index + match[0].length, end: text.length });
    }
  }
  
  for (let i = 0; i < boldPositions.length - 1; i++) {
    boldPositions[i].end = boldPositions[i + 1].start - 20;
  }
  
  boldPositions.forEach(({ title, start, end }) => {
    const key = title.toLowerCase();
    if (seen.has(key)) return;
    
    const body = text.substring(start, Math.min(end, start + 2000));
    const lines = body
      .split('\n')
      .map(l => l.replace(/^[-•*]\s*/, '').replace(/\[\d+\]/g, '').replace(/\*\*/g, '').trim())
      .filter(l => l.length > 3 && !l.match(/^\*\*/) && !l.match(/^-+$/));
    
    if (lines.length > 0) {
      seen.add(key);
      sections.push({ title, content: lines.slice(0, 10) });
    }
  });
  
  // Pattern 3: #### **1. Title** numbered format
  const numberedRegex = /####\s*\*\*(\d+)\.\s*([^*]+)\*\*/g;
  while ((match = numberedRegex.exec(text)) !== null) {
    const title = match[2].trim();
    const key = title.toLowerCase();
    
    if (title && !seen.has(key)) {
      const startPos = match.index + match[0].length;
      const nextMatch = text.substring(startPos).match(/####\s*\*\*\d+\./);
      const endPos = nextMatch && nextMatch.index !== undefined ? startPos + nextMatch.index : startPos + 2000;
      
      const body = text.substring(startPos, endPos);
      const lines = body
        .split('\n')
        .map(l => l.replace(/^[-•*]\s*/, '').replace(/\*\*/g, '').trim())
        .filter(l => l.length > 3 && !l.match(/^####/));
      
      if (lines.length > 0) {
        seen.add(key);
        sections.push({ title, content: lines.slice(0, 10) });
      }
    }
  }
  
  return sections;
}

// =============================================================================
// PERSONALITY PARSERS
// =============================================================================

function parseMBTI(text: string): MBTIResult {
  if (!text) return { type: 'N/A', confidence: 'N/A', dimensions: [] };
  
  const typePatterns = [
    /Inferred Type:?\s*\*?\*?\s*([A-Z]{4})(?:\s*\(|\s*\*|\s*$|\n)/i,
    /Type:?\s*\*?\*?\s*([A-Z]{4})(?:\s*\(|\s*\*|\s*$|\n)/i,
    /MBTI[:\s]+\*?\*?\s*([A-Z]{4})/i,
  ];
  
  let mbtiType = 'N/A';
  for (const pattern of typePatterns) {
    const match = text.match(pattern);
    if (match && match[1]) {
      mbtiType = match[1].toUpperCase();
      break;
    }
  }
  
  const confMatch = text.match(/Confidence:?\s*\*?\*?\s*(Low|Medium|High)\*?\*?/i);
  const confidence = confMatch ? confMatch[1] : 'Medium';
  
  const dimensions: MBTIDimension[] = [];
  const seenDims = new Set<string>();
  
  const dimPatterns = [
    { regex: /\*?\*?Extrav[a-z]*\s*\(E\):?\*?\*?\s*([^\n]+)/i, dim: 'Energy', letter: 'E' },
    { regex: /\*?\*?Introv[a-z]*\s*\(I\):?\*?\*?\s*([^\n]+)/i, dim: 'Energy', letter: 'I' },
    { regex: /\*?\*?Intui[a-z]*\s*\(N\):?\*?\*?\s*([^\n]+)/i, dim: 'Information', letter: 'N' },
    { regex: /\*?\*?Sens[a-z]*\s*\(S\):?\*?\*?\s*([^\n]+)/i, dim: 'Information', letter: 'S' },
    { regex: /\*?\*?Think[a-z]*\s*\(T\):?\*?\*?\s*([^\n]+)/i, dim: 'Decisions', letter: 'T' },
    { regex: /\*?\*?Feel[a-z]*\s*\(F\):?\*?\*?\s*([^\n]+)/i, dim: 'Decisions', letter: 'F' },
    { regex: /\*?\*?Judg[a-z]*\s*\(J\):?\*?\*?\s*([^\n]+)/i, dim: 'Structure', letter: 'J' },
    { regex: /\*?\*?Perceiv[a-z]*\s*\(P\):?\*?\*?\s*([^\n]+)/i, dim: 'Structure', letter: 'P' },
  ];
  
  dimPatterns.forEach(({ regex, dim, letter }) => {
    if (seenDims.has(dim)) return;
    const m = text.match(regex);
    if (m && m[1]) {
      seenDims.add(dim);
      dimensions.push({
        dim,
        pref: letter,
        evidence: m[1].replace(/\*\*/g, '').trim().substring(0, 120)
      });
    }
  });
  
  return { type: mbtiType, confidence, dimensions };
}

function parseDISC(text: string): DISCResult {
  if (!text) return { primary: 'N/A', secondary: 'N/A' };
  
  const primPatterns = [
    /\*?\*?Primary\s*Style:?\*?\*?\s*([DISC])\s*[-–]\s*(\w+)/i,
    /Primary:?\s*([DISC])\s*[-–]\s*(\w+)/i,
  ];
  
  let primary = 'N/A';
  for (const pattern of primPatterns) {
    const match = text.match(pattern);
    if (match && match[1] && match[2]) {
      primary = `${match[1].toUpperCase()} - ${match[2]}`;
      break;
    }
  }
  
  const secPatterns = [
    /\*?\*?Secondary\s*Style:?\*?\*?\s*([DISC])\s*[-–]\s*(\w+)/i,
    /Secondary:?\s*([DISC])\s*[-–]\s*(\w+)/i,
  ];
  
  let secondary = 'N/A';
  for (const pattern of secPatterns) {
    const match = text.match(pattern);
    if (match && match[1] && match[2]) {
      secondary = `${match[1].toUpperCase()} - ${match[2]}`;
      break;
    }
  }
  
  return { primary, secondary };
}

function parseCommPlaybook(text: string): CommPlaybook {
  const dos: string[] = [];
  const donts: string[] = [];
  let opening = '';
  
  const playbookMatch = text.match(/Communication Playbook/i);
  if (!playbookMatch || playbookMatch.index === undefined) {
    return { dos, donts, opening };
  }
  
  const playbookText = text.substring(playbookMatch.index);
  
  const doMatch = playbookText.match(/[✅]?\s*DO:?\s*(?:How to Engage)?\s*([\s\S]*?)(?=[❌]?\s*DON'?T:|$)/i);
  if (doMatch && doMatch[1]) {
    doMatch[1].split('\n').forEach(line => {
      const cleaned = line.replace(/^[-•*]\s*/, '').replace(/\*\*/g, '').trim();
      const isValid = cleaned.length > 15 &&
        !cleaned.match(/^DO$/i) &&
        !cleaned.match(/^#{2,}/) &&
        !cleaned.match(/Style:/i) &&
        !cleaned.match(/^(Dominance|Conscientiousness|Influence|Steadiness)/i) &&
        !cleaned.match(/^\w+\s*\([DISC]\):/i) &&
        !cleaned.match(/^(Primary|Secondary)/i);
      if (isValid) dos.push(cleaned);
    });
  }
  
  const dontMatch = playbookText.match(/[❌]?\s*DON'?T:?\s*(?:What to Avoid)?\s*([\s\S]*?)(?=[🎯]?\s*Best Opening|$)/i);
  if (dontMatch && dontMatch[1]) {
    dontMatch[1].split('\n').forEach(line => {
      const cleaned = line.replace(/^[-•*]\s*/, '').replace(/\*\*/g, '').trim();
      const isValid = cleaned.length > 15 && !cleaned.match(/^DON'?T$/i) && !cleaned.match(/^#{2,}/);
      if (isValid) donts.push(cleaned);
    });
  }
  
  const openMatch = playbookText.match(/[🎯]?\s*Best Opening(?: Approach)?:?\s*([\s\S]*?)(?=\n\n\n|={3,}|$)/i);
  if (openMatch && openMatch[1]) {
    opening = openMatch[1].replace(/\*\*/g, '').replace(/^[-•*]\s*/gm, '').trim().substring(0, 400);
  }
  
  return { dos: dos.slice(0, 5), donts: donts.slice(0, 5), opening };
}

// =============================================================================
// UI COMPONENTS
// =============================================================================

interface CardProps {
  title: string;
  icon: React.ReactNode;
  children: React.ReactNode;
  color?: string;
  badge?: React.ReactNode;
}

const Card: React.FC<CardProps> = ({ title, icon, children, color = 'text-blue-400', badge }) => (
  <div className="bg-[#1e2128] border border-[#2a2f38] rounded-xl mb-4 overflow-hidden">
    <div className="flex items-center justify-between px-5 py-4 border-b border-[#2a2f38] bg-[#1a1d23]">
      <div className="flex items-center gap-3">
        <span className={color}>{icon}</span>
        <h3 className="text-white font-semibold">{title}</h3>
      </div>
      {badge}
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

function getIcon(title: string): React.ReactNode {
  const t = title.toLowerCase();
  if (t.includes('overview') || t.includes('role') || t.includes('current')) return <Briefcase size={18} />;
  if (t.includes('career') || t.includes('history')) return <TrendingUp size={18} />;
  if (t.includes('education') || t.includes('background')) return <GraduationCap size={18} />;
  if (t.includes('achievement') || t.includes('award')) return <CheckCircle2 size={18} />;
  if (t.includes('linkedin') || t.includes('activity')) return <User size={18} />;
  if (t.includes('speaking') || t.includes('public')) return <MessageSquare size={18} />;
  if (t.includes('board') || t.includes('position')) return <UserCheck size={18} />;
  if (t.includes('management') || t.includes('style')) return <Brain size={18} />;
  if (t.includes('revenue') || t.includes('funding') || t.includes('budget') || t.includes('financial')) return <DollarSign size={18} />;
  if (t.includes('product') || t.includes('service')) return <Layers size={18} />;
  if (t.includes('market') || t.includes('customer') || t.includes('target')) return <Target size={18} />;
  if (t.includes('competit')) return <BarChart3 size={18} />;
  if (t.includes('news') || t.includes('recent') || t.includes('trend')) return <Zap size={18} />;
  if (t.includes('pain') || t.includes('challenge')) return <AlertTriangle size={18} />;
  if (t.includes('regulatory') || t.includes('compliance')) return <Shield size={18} />;
  if (t.includes('trigger') || t.includes('technology')) return <Lightbulb size={18} />;
  if (t.includes('culture') || t.includes('value')) return <UserCheck size={18} />;
  if (t.includes('headquarters') || t.includes('location') || t.includes('founding')) return <Building2 size={18} />;
  return <FileText size={18} />;
}

// =============================================================================
// ICP MATCH SCORE BADGE
// =============================================================================

const ICPScoreBadge: React.FC<{ score: number; level: string }> = ({ score, level }) => {
  const getColor = () => {
    if (score >= 85) return { bg: 'from-emerald-500 to-green-500', text: 'text-emerald-300', border: 'border-emerald-500/30' };
    if (score >= 70) return { bg: 'from-blue-500 to-indigo-500', text: 'text-blue-300', border: 'border-blue-500/30' };
    if (score >= 55) return { bg: 'from-yellow-500 to-orange-500', text: 'text-yellow-300', border: 'border-yellow-500/30' };
    return { bg: 'from-gray-500 to-slate-500', text: 'text-gray-300', border: 'border-gray-500/30' };
  };
  
  const colors = getColor();
  
  return (
    <div className={`flex items-center gap-2 px-3 py-1.5 rounded-lg bg-gradient-to-r ${colors.bg} bg-opacity-20 border ${colors.border}`}>
      <Target size={14} className={colors.text} />
      <span className={`text-sm font-bold ${colors.text}`}>{score}%</span>
      <span className="text-xs text-white/70">{level} Match</span>
    </div>


      );
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
  const [mainTab, setMainTab] = useState<'intelligence' | 'dossier' | 'fit' | 'outreach'>('dossier');
  const [subTab, setSubTab] = useState<'professional' | 'company' | 'personality' | 'raw'>('professional');

  // Cadence State
  const [showEnrollModal, setShowEnrollModal] = useState(false);
  const [enrollments, setEnrollments] = useState<any[]>([]);

  // ICP Match State
  const [icpData, setIcpData] = useState<ICPMatchData | null>(null);
  const [loadingIcp, setLoadingIcp] = useState(false);

  useEffect(() => { 
    fetchContact(); 
  }, [id]);

  // Fetch ICP match when contact loads
  // Fetch cadence enrollments
  const fetchEnrollments = async () => {
    if (!contact?.id) return;
    try {
      const res = await fetch(`https://apex-backend-production-production.up.railway.app/api/contacts/${contact.id}/enrollments`);
      const data = await res.json();
      setEnrollments(data.enrollments || []);
    } catch (e) {
      console.error('Failed to fetch enrollments:', e);
    }
  };
        
  useEffect(() => {
    if (contact) {
      fetchIcpMatch();
      fetchEnrollments();
    }
  }, [contact?.id]);
        
  const fetchContact = async () => {
    try {
      const res = await fetch(`https://apex-backend-production-production.up.railway.app/api/contacts/${id}`);
      if (res.ok) {
        setContact(await res.json());
      }
    } catch (e) {
      console.error('Failed to fetch contact:', e);
    } finally {
      setLoading(false);
    }
  };

  const fetchIcpMatch = async () => {
    setLoadingIcp(true);
    try {
      const res = await fetch(`https://apex-backend-production-production.up.railway.app/api/contacts/${id}/icp-match`);
      if (res.ok) {
        const data = await res.json();
        setIcpData(data.data);
      }
    } catch (e) {
      console.error('Failed to fetch ICP match:', e);
    } finally {
      setLoadingIcp(false);
    }
  };

  const handleEnrich = async () => {
    setEnriching(true);
    try {
      await fetch(`https://apex-backend-production-production.up.railway.app/api/contacts/${id}/enrich`, { method: 'POST' });
      const poll = setInterval(async () => {
        const res = await fetch(`https://apex-backend-production-production.up.railway.app/api/contacts/${id}/enrichment-status`);
        const data = await res.json();
        if (data.status === 'enriched' || data.status === 'error') {
          clearInterval(poll);
          fetchContact();
          setEnriching(false);
        }
      }, 2000);
      setTimeout(() => { clearInterval(poll); setEnriching(false); }, 120000);
    } catch (e) {
      setEnriching(false);
    }
  };

  const handleDownload = async () => {
    setGenerating(true);
    try {
      const res = await fetch(`https://apex-backend-production-production.up.railway.app/api/contacts/${id}/generate-persona`, { method: 'POST' });
      if (res.ok) {
        const data = await res.json();
        if (data.files?.pdf_landscape) {
          window.open(`https://apex-backend-production-production.up.railway.app/api/download?path=${encodeURIComponent(data.files.pdf_landscape)}`, '_blank');
        }
      }
    } catch (e) {
      console.error('PDF generation failed:', e);
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

  // Parse enrichment data
  const raw = contact.enrichment_data || '';
  const isEnriched = contact.enrichment_status === 'enriched' && raw.length > 100;

  const personSection = extractSection(raw, 'person');
  const companySection = extractSection(raw, 'company');
  const salesSection = extractSection(raw, 'sales');
  const personalitySection = extractSection(raw, 'personality');

  const personCards = parseAllSections(personSection);
  const companyCards = parseAllSections(companySection);
  const salesCards = parseAllSections(salesSection);

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
                  {icpData && icpData.icp_match && (
                    <ICPScoreBadge score={icpData.icp_match.score} level={icpData.icp_match.match_level} />
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

                {/* Cadence Button */}
                {enrollments.some(e => e.status === 'active') ? (
                  <div className="px-3 py-1.5 bg-emerald-500/20 border border-emerald-500/50 rounded-lg text-emerald-300 text-sm flex items-center gap-2">
                    <Play size={14} />
                    {enrollments.find(e => e.status === 'active')?.cadence_name}
                  </div>
                ) : (
                  <button
                    onClick={() => setShowEnrollModal(true)}
                    className="px-4 py-2 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 rounded-xl text-sm font-medium flex items-center gap-2"
                  >
                    <Play size={16} />
                    Start Cadence
                  </button>
                )}
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
            { id: 'intelligence', label: 'Intelligence', icon: <Zap size={14} /> },
            { id: 'dossier', label: 'Dossier', icon: <FileText size={14} /> },
            { id: 'fit', label: 'Why We Fit', icon: <ThumbsUp size={14} />, highlight: icpData?.playbook_configured },
            { id: 'outreach', label: 'Outreach', icon: <MessageSquare size={14} /> }
          ].map(tab => (
            <button 
              key={tab.id} 
              onClick={() => setMainTab(tab.id as typeof mainTab)}
              className={`px-6 py-3 text-sm font-medium border-b-2 transition-all flex items-center gap-2
                ${mainTab === tab.id 
                  ? 'border-indigo-500 text-white' 
                  : 'border-transparent text-[#8b919a] hover:text-white'}`}
            >
              {tab.icon}
              {tab.label}
              {tab.highlight && <Sparkles size={12} className="text-amber-400" />}
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
              <button key={tab.id} onClick={() => setSubTab(tab.id as typeof subTab)}
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
                    {comm.dos.length > 0 ? comm.dos.map((d, i) => (
                      <li key={i} className="flex items-start gap-2">
                        <span className="text-green-400 mt-0.5">✓</span>
                        <span>{d}</span>
                      </li>
                    )) : <li className="text-[#8b919a]">No data available</li>}
                  </ul>
                </div>
                <div>
                  <h4 className="flex items-center gap-2 text-red-400 font-medium mb-3">
                    <XCircle size={16} /> DON'T: What to Avoid
                  </h4>
                  <ul className="space-y-2">
                    {comm.donts.length > 0 ? comm.donts.map((d, i) => (
                      <li key={i} className="flex items-start gap-2">
                        <span className="text-red-400 mt-0.5">✗</span>
                        <span>{d}</span>
                      </li>
                    )) : <li className="text-[#8b919a]">No data available</li>}
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

        {/* ================================================================= */}
        {/* WHY WE FIT TAB - Powered by Sales Playbook */}
        {/* ================================================================= */}
        {mainTab === 'fit' && (
          <div className="space-y-6">
            {/* ICP Match Score Card */}
            {loadingIcp ? (
              <div className="bg-[#161b22] border border-[#30363d] rounded-xl p-8 text-center">
                <Loader2 size={32} className="animate-spin text-indigo-500 mx-auto mb-4" />
                <p className="text-[#8b919a]">Analyzing fit against your ICP...</p>
              </div>
            ) : !icpData?.playbook_configured ? (
              <div className="bg-gradient-to-br from-amber-500/10 to-orange-500/10 border border-amber-500/30 rounded-xl p-8 text-center">
                <div className="w-16 h-16 rounded-full bg-amber-500/20 flex items-center justify-center mx-auto mb-4">
                  <Settings size={32} className="text-amber-400" />
                </div>
                <h3 className="text-white font-semibold text-lg mb-2">Configure Your Sales Playbook</h3>
                <p className="text-[#8b919a] mb-6 max-w-md mx-auto">
                  Set up your Ideal Customer Profile, products, and value propositions to see how well this contact matches.
                </p>
                <button
                  onClick={() => navigate('/settings')}
                  className="px-6 py-2.5 bg-gradient-to-r from-amber-600 to-orange-600 hover:from-amber-500 hover:to-orange-500 rounded-lg text-sm font-medium inline-flex items-center gap-2"
                >
                  <Settings size={16} /> Configure Playbook
                  <ArrowRight size={16} />
                </button>
              </div>
            ) : (
              <>
                {/* ICP Match Summary */}
                <div className="bg-[#161b22] border border-[#30363d] rounded-xl overflow-hidden">
                  <div className="px-6 py-4 border-b border-[#30363d] bg-gradient-to-r from-indigo-600/10 to-purple-600/10">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-4">
                        <div className={`w-16 h-16 rounded-xl flex items-center justify-center text-2xl font-bold ${
                          icpData.icp_match.score >= 85 ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' :
                          icpData.icp_match.score >= 70 ? 'bg-blue-500/20 text-blue-400 border border-blue-500/30' :
                          icpData.icp_match.score >= 55 ? 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30' :
                          'bg-gray-500/20 text-gray-400 border border-gray-500/30'
                        }`}>
                          {icpData.icp_match.score}%
                        </div>
                        <div>
                          <h3 className="text-white font-semibold text-lg">ICP Match Score</h3>
                          <p className={`text-sm font-medium ${
                            icpData.icp_match.score >= 85 ? 'text-emerald-400' :
                            icpData.icp_match.score >= 70 ? 'text-blue-400' :
                            icpData.icp_match.score >= 55 ? 'text-yellow-400' :
                            'text-gray-400'
                          }`}>
                            {icpData.icp_match.match_level} Match
                          </p>
                        </div>
                      </div>
                      <button
                        onClick={() => navigate('/settings')}
                        className="px-3 py-1.5 bg-[#21262d] hover:bg-[#30363d] rounded-lg text-xs text-[#8b919a] hover:text-white flex items-center gap-1"
                      >
                        <Settings size={12} /> Edit ICP
                      </button>
                    </div>
                  </div>
                  
                  {/* Match Reasons */}
                  {icpData.icp_match.reasons.length > 0 && (
                    <div className="px-6 py-4">
                      <h4 className="text-sm text-[#8b919a] mb-3">Why They Match</h4>
                      <div className="flex flex-wrap gap-2">
                        {icpData.icp_match.reasons.map((reason, i) => (
                          <span key={i} className="px-3 py-1.5 bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 rounded-lg text-sm flex items-center gap-1.5">
                            <CheckCircle2 size={12} />
                            {reason}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                {/* Why We're a Fit Points */}
                {icpData.why_us_fit.points.length > 0 && (
                  <Card 
                    title="Why We're a Great Fit" 
                    icon={<Sparkles size={18} />} 
                    color="text-amber-400"
                    badge={
                      <span className="text-xs bg-amber-500/20 text-amber-300 px-2 py-1 rounded">
                        Powered by Playbook
                      </span>
                    }
                  >
                    <div className="space-y-4">
                      {icpData.why_us_fit.points.map((point, i) => (
                        <div key={i} className="bg-[#0d1117] border border-[#30363d] rounded-lg p-4">
                          <div className="flex items-start gap-3">
                            <div className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 ${
                              point.type === 'pain_point' ? 'bg-red-500/20 text-red-400' :
                              point.type === 'value_prop' ? 'bg-amber-500/20 text-amber-400' :
                              'bg-blue-500/20 text-blue-400'
                            }`}>
                              {point.type === 'pain_point' ? <AlertTriangle size={16} /> :
                               point.type === 'value_prop' ? <Sparkles size={16} /> :
                               <Award size={16} />}
                            </div>
                            <div className="flex-1">
                              <h5 className="text-white font-medium mb-1">{point.title}</h5>
                              <p className="text-[#8b919a] text-sm">{point.detail}</p>
                              {point.impact && (
                                <p className="text-emerald-400 text-sm mt-2 flex items-center gap-1">
                                  <TrendingUp size={12} /> {point.impact}
                                </p>
                              )}
                              {point.proof && (
                                <p className="text-blue-400 text-sm mt-1 flex items-center gap-1">
                                  <Award size={12} /> {point.proof}
                                </p>
                              )}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </Card>
                )}

                {/* Quick Actions */}
                <div className="grid md:grid-cols-2 gap-4">
                  <button className="bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 rounded-xl p-4 text-left transition-all group">
                    <div className="flex items-center justify-between">
                      <div>
                        <h4 className="text-white font-semibold flex items-center gap-2">
                          <MessageSquare size={18} />
                          Generate Outreach
                        </h4>
                        <p className="text-white/70 text-sm mt-1">Create personalized email based on fit analysis</p>
                      </div>
                      <ArrowRight size={20} className="text-white/50 group-hover:translate-x-1 transition-transform" />
                    </div>
                  </button>
                  
                  <button 
                    onClick={() => setMainTab('intelligence')}
                    className="bg-[#21262d] hover:bg-[#30363d] border border-[#30363d] rounded-xl p-4 text-left transition-all group"
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <h4 className="text-white font-semibold flex items-center gap-2">
                          <Zap size={18} />
                          View Intelligence
                        </h4>
                        <p className="text-[#8b919a] text-sm mt-1">See industry trends, pain points, and triggers</p>
                      </div>
                      <ArrowRight size={20} className="text-[#6e7681] group-hover:translate-x-1 transition-transform" />
                    </div>
                  </button>
                </div>
              </>
            )}
          </div>
        )}

        {/* OUTREACH TAB */}
        {mainTab === 'outreach' && (
          <OutreachGenerator
            contactId={contact.id}
            contactName={`${contact.firstname} ${contact.lastname}`.trim()}
            company={contact.company}
            title={contact.title}
            icpScore={icpData?.icp_match?.score}
            matchReasons={icpData?.icp_match?.reasons}
          />
        )}
      </div>


      {/* Cadence Enrollment Modal */}
      <EnrollCadenceModal
        contactId={contact.id}
        contactName={`${contact.firstname} ${contact.lastname}`.trim()}
        isOpen={showEnrollModal}
        onClose={() => setShowEnrollModal(false)}
        onEnrolled={() => fetchEnrollments()}
      />
    </div>
  );
}
