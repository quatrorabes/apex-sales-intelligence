import { useParams, useNavigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import {
    User, Building2, Target, MessageSquare, TrendingUp, ChevronLeft,
    Mail, Phone, RefreshCw, Briefcase, GraduationCap, Award, Brain,
    FileText, AlertTriangle, DollarSign, Zap, Shield, BarChart3,
    Lightbulb, CheckCircle2, XCircle, Globe, Layers, UserCheck,
    ExternalLink, Download, Loader2, Clock, Send, Copy, Check
} from 'lucide-react';

const API_BASE = import.meta.env.VITE_API_URL || import.meta.env.VITE_APEX_API_URL || 'https://apex-backend-i7b0.onrender.com';

// =============================================================================
// TYPES
// =============================================================================

interface Contact {
    id: number;
    first_name: string;
    last_name: string;
    name?: string;
    email: string;
    phone: string;
    company: string;
    title: string;
    enrichment_status: string;
    enrichment_data: string | object | null;
    linkedin_url: string | null;
    last_enriched: string | null;
    apex_score?: number;
    match_tier?: string;
    persona_type?: string;
}

interface ParsedSection {
    title: string;
    content: string[];
}

// =============================================================================
// PARSING UTILITIES - Handles both JSON and Markdown formats
// =============================================================================

function cleanText(text: string): string {
    return text
        .replace(/\*\*/g, '')
        .replace(/#{1,4}\s*/g, '')
        .replace(/\[\d+\]/g, '')
        .replace(/---+/g, '')
        .trim();
}

function extractSection(content: string, startMarker: string): string {
    const idx = content.indexOf(startMarker);
    if (idx === -1) return '';
    const afterMarker = content.substring(idx);
    const nextIdx = afterMarker.substring(10).indexOf('===');
    if (nextIdx !== -1) return afterMarker.substring(0, nextIdx + 10);
    return afterMarker;
}

function parseNumberedSections(text: string): ParsedSection[] {
    const sections: ParsedSection[] = [];
    const regex = /(\d+)\.\s*\*?\*?([^*\n:]+)\*?\*?[:\s]*([\s\S]*?)(?=\d+\.\s*\*?\*?[A-Z]|===|$)/gi;
    let match;
    while ((match = regex.exec(text)) !== null) {
        const title = cleanText(match[2]).trim();
        const body = match[3] || '';
        const lines = body.split('\n')
            .map(l => cleanText(l).trim())
            .filter(l => l.length > 2 && !l.match(/^-+$/));
        if (title && lines.length > 0) {
            sections.push({ title, content: lines });
        }
    }
    return sections;
}

function parseBulletSections(text: string): ParsedSection[] {
    const sections: ParsedSection[] = [];
    const lines = text.split('\n').filter(l => l.trim());
    let currentSection: ParsedSection | null = null;
    
    for (const line of lines) {
        const cleaned = cleanText(line);
        if (cleaned.match(/^[A-Z][^:]+:$/)) {
            if (currentSection && currentSection.content.length > 0) {
                sections.push(currentSection);
            }
            currentSection = { title: cleaned.replace(':', ''), content: [] };
        } else if (currentSection && cleaned.length > 3) {
            currentSection.content.push(cleaned.replace(/^[-•]\s*/, ''));
        }
    }
    if (currentSection && currentSection.content.length > 0) {
        sections.push(currentSection);
    }
    return sections;
}

function parseMBTI(text: string): { type: string; confidence: string; dimensions: any[] } {
    const typeMatch = text.match(/Inferred Type[:\s]*([A-Z]{4})/i) || text.match(/MBTI[:\s]*([A-Z]{4})/i);
    const confMatch = text.match(/Confidence[:\s]*(Low|Medium|High)/i);
    const dimensions: any[] = [];
    const dimRegex = /\|\s*(Energy|Information|Decisions|Structure)\s*\|\s*([A-Z])\s*[-–]\s*(\w+)\s*\|\s*([^|]+)\|/gi;
    let m;
    while ((m = dimRegex.exec(text)) !== null) {
        dimensions.push({ dim: m[1], pref: `${m[2]} - ${m[3]}`, evidence: cleanText(m[4]) });
    }
    return { type: typeMatch?.[1] || 'N/A', confidence: confMatch?.[1] || 'Medium', dimensions };
}

function parseDISC(text: string): { primary: string; secondary: string; styles: any[] } {
    const primMatch = text.match(/Primary Style[:\s]*([A-Z])\s*[-–]\s*(\w+)/i);
    const secMatch = text.match(/Secondary Style[:\s]*([A-Z])\s*[-–]\s*(\w+)/i);
    const styles: any[] = [];
    return { 
        primary: primMatch ? `${primMatch[1]} - ${primMatch[2]}` : 'N/A', 
        secondary: secMatch ? `${secMatch[1]} - ${secMatch[2]}` : '', 
        styles 
    };
}

function parseCommPlaybook(text: string): { dos: string[]; donts: string[]; opening: string } {
    const dos: string[] = [];
    const donts: string[] = [];
    let opening = '';
    
    const doMatch = text.match(/DO[:\s]*(?:How to Engage)?([\s\S]*?)(?=DON'T|❌|$)/i);
    if (doMatch) {
        doMatch[1].split('\n').forEach(l => {
            const c = cleanText(l);
            if (c.length > 5 && !c.match(/^DO$/i)) dos.push(c.replace(/^[-•✓]\s*/, ''));
        });
    }
    
    const dontMatch = text.match(/DON'T[:\s]*(?:What to Avoid)?([\s\S]*?)(?=Best Opening|🎯|$)/i);
    if (dontMatch) {
        dontMatch[1].split('\n').forEach(l => {
            const c = cleanText(l);
            if (c.length > 5 && !c.match(/^DON'T$/i)) donts.push(c.replace(/^[-•✗]\s*/, ''));
        });
    }
    
    const openMatch = text.match(/Best Opening Approach[:\s]*([\s\S]*?)(?=###|===|$)/i);
    if (openMatch) opening = cleanText(openMatch[1]);
    
    return { dos: dos.slice(0, 5), donts: donts.slice(0, 5), opening };
}

// Parse JSON enrichment data into sections
function parseJSONEnrichment(data: any): { sales: ParsedSection[], company: ParsedSection[], personality: string, raw: string } {
    const result = {
        sales: [] as ParsedSection[],
        company: [] as ParsedSection[],
        personality: '',
        raw: typeof data === 'string' ? data : JSON.stringify(data, null, 2)
    };
    
    if (!data) return result;
    
    // Handle various JSON structures
    const obj = typeof data === 'string' ? (() => { try { return JSON.parse(data); } catch { return null; } })() : data;
    
    if (!obj) return result;
    
    // Sales Intelligence
    if (obj.sales_intelligence || obj.sales || obj.pain_points) {
        const salesData = obj.sales_intelligence || obj.sales || {};
        if (salesData.pain_points) {
            result.sales.push({ title: 'Pain Points', content: Array.isArray(salesData.pain_points) ? salesData.pain_points : [salesData.pain_points] });
        }
        if (salesData.opportunities) {
            result.sales.push({ title: 'Opportunities', content: Array.isArray(salesData.opportunities) ? salesData.opportunities : [salesData.opportunities] });
        }
        if (salesData.buying_triggers) {
            result.sales.push({ title: 'Buying Triggers', content: Array.isArray(salesData.buying_triggers) ? salesData.buying_triggers : [salesData.buying_triggers] });
        }
        if (obj.pain_points && !salesData.pain_points) {
            result.sales.push({ title: 'Pain Points', content: Array.isArray(obj.pain_points) ? obj.pain_points : [obj.pain_points] });
        }
    }
    
    // Company Intelligence
    if (obj.company_research || obj.company || obj.company_overview) {
        const companyData = obj.company_research || obj.company || {};
        if (companyData.overview || obj.company_overview) {
            result.company.push({ title: 'Company Overview', content: [companyData.overview || obj.company_overview] });
        }
        if (companyData.industry) {
            result.company.push({ title: 'Industry', content: [companyData.industry] });
        }
        if (companyData.size || companyData.employees) {
            result.company.push({ title: 'Company Size', content: [companyData.size || companyData.employees] });
        }
        if (companyData.recent_news) {
            result.company.push({ title: 'Recent News', content: Array.isArray(companyData.recent_news) ? companyData.recent_news : [companyData.recent_news] });
        }
    }
    
    // Personality
    if (obj.personality_assessment || obj.personality || obj.communication_style) {
        result.personality = JSON.stringify(obj.personality_assessment || obj.personality || { style: obj.communication_style }, null, 2);
    }
    
    return result;
}

// =============================================================================
// UI COMPONENTS
// =============================================================================

const Card: React.FC<{ title: string; icon: React.ReactNode; children: React.ReactNode; color?: string; action?: React.ReactNode }> = 
    ({ title, icon, children, color = 'text-blue-400', action }) => (
    <div className="bg-[#161b22] border border-[#30363d] rounded-lg overflow-hidden">
        <div className={`px-4 py-3 border-b border-[#30363d] flex items-center justify-between ${color}`}>
            <div className="flex items-center gap-2">
                {icon}
                <h3 className="font-semibold text-white">{title}</h3>
            </div>
            {action}
        </div>
        <div className="p-4">{children}</div>
    </div>
);

const Tab: React.FC<{ active: boolean; onClick: () => void; children: React.ReactNode }> = ({ active, onClick, children }) => (
    <button
        onClick={onClick}
        className={`px-4 py-2 text-sm font-medium transition-colors ${active ? 'text-white border-b-2 border-blue-500' : 'text-[#8b919a] hover:text-white'}`}
    >
        {children}
    </button>
);

const SubTab: React.FC<{ active: boolean; onClick: () => void; children: React.ReactNode }> = ({ active, onClick, children }) => (
    <button
        onClick={onClick}
        className={`px-3 py-1.5 text-xs rounded-full transition-colors ${active ? 'bg-blue-600 text-white' : 'bg-[#21262d] text-[#8b919a] hover:text-white hover:bg-[#30363d]'}`}
    >
        {children}
    </button>
);

const Badge: React.FC<{ children: React.ReactNode; color: string }> = ({ children, color }) => (
    <span className={`px-2 py-1 text-xs font-medium rounded ${color}`}>{children}</span>
);

const CopyButton: React.FC<{ text: string }> = ({ text }) => {
    const [copied, setCopied] = useState(false);
    const handleCopy = () => {
        navigator.clipboard.writeText(text);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };
    return (
        <button onClick={handleCopy} className="text-[#8b919a] hover:text-white transition">
            {copied ? <Check size={14} /> : <Copy size={14} />}
        </button>
    );
};

// =============================================================================
// MAIN COMPONENT
// =============================================================================

export default function ContactDetail() {
    const { id } = useParams();
    const navigate = useNavigate();
    const [contact, setContact] = useState<Contact | null>(null);
    const [loading, setLoading] = useState(true);
    const [enriching, setEnriching] = useState(false);
    const [mainTab, setMainTab] = useState<'dossier' | 'outreach'>('dossier');
    const [subTab, setSubTab] = useState<'sales' | 'company' | 'personality' | 'raw'>('sales');
    const [copySuccess, setCopySuccess] = useState<string | null>(null);

    useEffect(() => { if (id) fetchContact(); }, [id]);

    const fetchContact = async () => {
        try {
            setLoading(true);
            const res = await fetch(`${API_BASE}/api/contacts/${id}`);
            const data = await res.json();
            const contactData = data.contact || data;
            console.log('Contact loaded:', contactData);
            setContact(contactData);
        } catch (e) { 
            console.error('Failed to fetch contact:', e); 
        } finally { 
            setLoading(false); 
        }
    };

    const handleEnrich = async () => {
        if (!id || enriching) return;
        setEnriching(true);
        
        try {
            console.log('Starting enrichment for contact:', id);
            const res = await fetch(`${API_BASE}/api/contacts/${id}/enrich`, { method: 'POST' });
            
            if (!res.ok) {
                throw new Error(`Enrichment failed: ${res.status}`);
            }
            
            const result = await res.json();
            console.log('Enrichment initiated:', result);
            
            // Poll for completion
            let attempts = 0;
            const maxAttempts = 30;
            
            const poll = setInterval(async () => {
                attempts++;
                try {
                    const statusRes = await fetch(`${API_BASE}/api/contacts/${id}`);
                    const statusData = await statusRes.json();
                    const c = statusData.contact || statusData;
                    
                    console.log(`Poll ${attempts}: status = ${c.enrichment_status}`);
                    
                    if (c.enrichment_status === 'completed' || c.enrichment_status === 'enriched' || c.enrichment_status === 'error' || attempts >= maxAttempts) {
                        clearInterval(poll);
                        setContact(c);
                        setEnriching(false);
                        
                        if (c.enrichment_status === 'completed' || c.enrichment_status === 'enriched') {
                            console.log('Enrichment completed successfully');
                        }
                    }
                } catch (e) {
                    console.error('Poll error:', e);
                }
            }, 2000);
            
        } catch (e) { 
            console.error('Enrichment error:', e);
            setEnriching(false);
            alert('Enrichment failed. Please try again.');
        }
    };

    const handleCopyEmail = (email: string) => {
        navigator.clipboard.writeText(email);
        setCopySuccess('email');
        setTimeout(() => setCopySuccess(null), 2000);
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-[#0d1117] flex items-center justify-center">
                <div className="text-center">
                    <Loader2 className="animate-spin text-blue-500 mx-auto mb-4" size={32} />
                    <p className="text-[#8b919a]">Loading contact...</p>
                </div>
            </div>
        );
    }

    if (!contact) {
        return (
            <div className="min-h-screen bg-[#0d1117] flex items-center justify-center">
                <div className="text-center">
                    <User className="mx-auto mb-4 text-[#30363d]" size={48} />
                    <p className="text-[#8b919a] text-lg mb-4">Contact not found</p>
                    <button 
                        onClick={() => navigate('/contacts')}
                        className="px-4 py-2 bg-[#21262d] hover:bg-[#30363d] rounded-lg transition"
                    >
                        ← Back to Contacts
                    </button>
                </div>
            </div>
        );
    }

    // Parse enrichment data
    const rawEnrichment = contact.enrichment_data || '';
    const raw = typeof rawEnrichment === 'string' ? rawEnrichment : JSON.stringify(rawEnrichment, null, 2);
    const isEnriched = (contact.enrichment_status === 'completed' || contact.enrichment_status === 'enriched') && raw.length > 50;

    // Try JSON parsing first, then markdown
    const jsonParsed = parseJSONEnrichment(rawEnrichment);
    
    // Markdown section extraction
    const salesSection = extractSection(raw, '=== SALES INTELLIGENCE ===') || extractSection(raw, '### Sales') || '';
    const companySection = extractSection(raw, '=== COMPANY RESEARCH ===') || extractSection(raw, '### Company') || '';
    const personalitySection = extractSection(raw, '=== PERSONALITY ASSESSMENT ===') || extractSection(raw, '### Personality') || jsonParsed.personality;

    // Parse sections - prefer JSON, fallback to markdown
    const salesCards = jsonParsed.sales.length > 0 ? jsonParsed.sales : parseNumberedSections(salesSection);
    const companyCards = jsonParsed.company.length > 0 ? jsonParsed.company : parseNumberedSections(companySection);
    
    // Personality parsing
    const mbti = parseMBTI(personalitySection);
    const disc = parseDISC(personalitySection);
    const comm = parseCommPlaybook(personalitySection);

    const displayName = contact.name || `${contact.first_name || ''} ${contact.last_name || ''}`.trim() || 'Unknown';
    const tierColor = contact.match_tier === 'HIGH' ? 'bg-green-500/20 text-green-400' : 
                      contact.match_tier === 'MEDIUM' ? 'bg-yellow-500/20 text-yellow-400' : 
                      'bg-orange-500/20 text-orange-400';

    return (
        <div className="min-h-screen bg-[#0d1117] text-white">
            {/* HEADER */}
            <div className="bg-[#161b22] border-b border-[#30363d]">
                <div className="max-w-6xl mx-auto px-6 py-4">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-4">
                            <button onClick={() => navigate('/contacts')} className="text-[#8b919a] hover:text-white transition">
                                <ChevronLeft size={24} />
                            </button>
                            <div className="w-14 h-14 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-2xl font-bold shadow-lg">
                                {displayName.charAt(0).toUpperCase()}
                            </div>
                            <div>
                                <div className="flex items-center gap-3">
                                    <h1 className="text-2xl font-bold">{displayName}</h1>
                                    {contact.match_tier && <Badge color={tierColor}>{contact.match_tier}</Badge>}
                                    {contact.apex_score !== undefined && contact.apex_score > 0 && (
                                        <Badge color="bg-blue-500/20 text-blue-400">{contact.apex_score} pts</Badge>
                                    )}
                                </div>
                                <p className="text-[#8b919a] text-sm mt-1">
                                    {contact.title}{contact.title && contact.company ? ' at ' : ''}{contact.company}
                                </p>
                            </div>
                        </div>
                        
                        <div className="flex items-center gap-3">
                            {isEnriched && contact.last_enriched && (
                                <span className="text-xs text-[#6e7681] flex items-center gap-1">
                                    <Clock size={12} />
                                    Enriched {new Date(contact.last_enriched).toLocaleDateString()}
                                </span>
                            )}
                            <button
                                onClick={handleEnrich}
                                disabled={enriching}
                                className="px-5 py-2.5 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 disabled:from-gray-600 disabled:to-gray-600 rounded-lg flex items-center gap-2 transition font-medium shadow-lg"
                            >
                                {enriching ? <Loader2 className="animate-spin" size={18} /> : <Zap size={18} />}
                                {enriching ? 'Enriching...' : isEnriched ? 'Re-enrich' : 'Enrich Profile'}
                            </button>
                        </div>
                    </div>

                    {/* Contact Info Row */}
                    <div className="flex flex-wrap gap-6 mt-4 text-sm">
                        {contact.email && (
                            <div className="flex items-center gap-2 text-[#8b919a] hover:text-white transition group">
                                <Mail size={14} />
                                <span>{contact.email}</span>
                                <button 
                                    onClick={() => handleCopyEmail(contact.email)}
                                    className="opacity-0 group-hover:opacity-100 transition"
                                >
                                    {copySuccess === 'email' ? <Check size={12} className="text-green-400" /> : <Copy size={12} />}
                                </button>
                            </div>
                        )}
                        {contact.phone && (
                            <div className="flex items-center gap-2 text-[#8b919a]">
                                <Phone size={14} />
                                <span>{contact.phone}</span>
                            </div>
                        )}
                        {contact.linkedin_url && (
                            <a href={contact.linkedin_url} target="_blank" rel="noopener noreferrer" className="flex items-center gap-2 text-blue-400 hover:text-blue-300 transition">
                                <ExternalLink size={14} />
                                <span>LinkedIn</span>
                            </a>
                        )}
                        {contact.persona_type && (
                            <div className="flex items-center gap-2 text-purple-400">
                                <User size={14} />
                                <span>{contact.persona_type}</span>
                            </div>
                        )}
                    </div>

                    {/* Main Tabs */}
                    <div className="flex gap-4 mt-4 border-b border-[#30363d] -mb-px">
                        <Tab active={mainTab === 'dossier'} onClick={() => setMainTab('dossier')}>
                            <Brain className="inline mr-2" size={16} />Dossier
                        </Tab>
                        <Tab active={mainTab === 'outreach'} onClick={() => setMainTab('outreach')}>
                            <Send className="inline mr-2" size={16} />Outreach
                        </Tab>
                    </div>
                </div>
            </div>

            {/* CONTENT */}
            <div className="max-w-6xl mx-auto px-6 py-6 space-y-6">
                {/* Sub Tabs for Dossier */}
                {mainTab === 'dossier' && (
                    <div className="flex gap-2 flex-wrap">
                        <SubTab active={subTab === 'sales'} onClick={() => setSubTab('sales')}>
                            <Target className="inline mr-1" size={12} />Sales Intel
                        </SubTab>
                        <SubTab active={subTab === 'company'} onClick={() => setSubTab('company')}>
                            <Building2 className="inline mr-1" size={12} />Company
                        </SubTab>
                        <SubTab active={subTab === 'personality'} onClick={() => setSubTab('personality')}>
                            <Brain className="inline mr-1" size={12} />Personality
                        </SubTab>
                        <SubTab active={subTab === 'raw'} onClick={() => setSubTab('raw')}>
                            <FileText className="inline mr-1" size={12} />Raw Data
                        </SubTab>
                    </div>
                )}

                {/* DOSSIER - SALES */}
                {mainTab === 'dossier' && subTab === 'sales' && (
                    <Card title="Sales Intelligence" icon={<Target size={18} />} color="text-green-400">
                        {!isEnriched ? (
                            <div className="text-center py-12">
                                <Target size={48} className="mx-auto mb-4 text-[#30363d]" />
                                <p className="text-[#8b919a] text-lg mb-2">No sales intelligence available</p>
                                <p className="text-[#6e7681] text-sm">Click "Enrich Profile" to generate AI-powered insights</p>
                            </div>
                        ) : salesCards.length > 0 ? (
                            <div className="space-y-6">
                                {salesCards.map((card, i) => (
                                    <div key={i} className="border-l-2 border-green-500 pl-4">
                                        <h4 className="font-semibold text-white mb-3 flex items-center gap-2">
                                            <Lightbulb size={16} className="text-green-400" />
                                            {card.title}
                                        </h4>
                                        <ul className="space-y-2 text-sm">
                                            {card.content.map((line, j) => (
                                                <li key={j} className="flex items-start gap-2 text-[#c9d1d9]">
                                                    <span className="text-green-400 mt-1">•</span>
                                                    <span>{line}</span>
                                                </li>
                                            ))}
                                        </ul>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <div className="text-center py-8">
                                <p className="text-[#8b919a]">No structured sales data found in enrichment.</p>
                                <button onClick={() => setSubTab('raw')} className="text-blue-400 hover:text-blue-300 text-sm mt-2">
                                    View raw data →
                                </button>
                            </div>
                        )}
                    </Card>
                )}

                {/* DOSSIER - COMPANY */}
                {mainTab === 'dossier' && subTab === 'company' && (
                    <Card title="Company Intelligence" icon={<Building2 size={18} />} color="text-blue-400">
                        {companyCards.length > 0 ? (
                            <div className="space-y-6">
                                {companyCards.map((card, i) => (
                                    <div key={i} className="border-l-2 border-blue-500 pl-4">
                                        <h4 className="font-semibold text-white mb-3">{card.title}</h4>
                                        <ul className="space-y-2 text-sm">
                                            {card.content.map((line, j) => (
                                                <li key={j} className="text-[#c9d1d9]">{line}</li>
                                            ))}
                                        </ul>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <div className="text-center py-12">
                                <Building2 size={48} className="mx-auto mb-4 text-[#30363d]" />
                                <p className="text-[#8b919a]">No company data available</p>
                                {!isEnriched && <p className="text-[#6e7681] text-sm mt-2">Enrich this contact to generate company insights</p>}
                            </div>
                        )}
                    </Card>
                )}

                {/* DOSSIER - PERSONALITY */}
                {mainTab === 'dossier' && subTab === 'personality' && (
                    <div className="space-y-6">
                        {/* MBTI */}
                        <Card title="MBTI Assessment" icon={<Brain size={18} />} color="text-purple-400">
                            <div className="flex items-center gap-4 mb-4">
                                <div className="text-4xl font-bold text-purple-400">{mbti.type}</div>
                                <div className="text-sm">
                                    <span className="text-[#8b919a]">Confidence:</span>
                                    <span className={`ml-2 px-2 py-1 rounded text-xs ${
                                        mbti.confidence === 'High' ? 'bg-green-500/20 text-green-400' : 
                                        mbti.confidence === 'Medium' ? 'bg-yellow-500/20 text-yellow-400' : 
                                        'bg-red-500/20 text-red-400'
                                    }`}>
                                        {mbti.confidence}
                                    </span>
                                </div>
                            </div>
                            {mbti.dimensions.length > 0 && (
                                <div className="overflow-x-auto">
                                    <table className="w-full text-sm">
                                        <thead>
                                            <tr className="text-[#8b919a] border-b border-[#30363d]">
                                                <th className="text-left py-2 px-2">Dimension</th>
                                                <th className="text-left py-2 px-2">Preference</th>
                                                <th className="text-left py-2 px-2">Evidence</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {mbti.dimensions.map((d, i) => (
                                                <tr key={i} className="border-b border-[#21262d]">
                                                    <td className="py-2 px-2 text-white">{d.dim}</td>
                                                    <td className="py-2 px-2 text-purple-400">{d.pref}</td>
                                                    <td className="py-2 px-2 text-[#8b919a]">{d.evidence}</td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            )}
                            {mbti.type === 'N/A' && (
                                <p className="text-[#8b919a] text-center py-4">MBTI assessment not available. Enrich to generate.</p>
                            )}
                        </Card>

                        {/* Communication Playbook */}
                        <Card title="Communication Playbook" icon={<MessageSquare size={18} />} color="text-cyan-400">
                            {(comm.dos.length > 0 || comm.donts.length > 0) ? (
                                <>
                                    <div className="grid md:grid-cols-2 gap-6">
                                        <div>
                                            <h4 className="text-green-400 font-medium mb-3 flex items-center gap-2">
                                                <CheckCircle2 size={16} /> DO: How to Engage
                                            </h4>
                                            <ul className="space-y-2 text-sm">
                                                {comm.dos.map((item, i) => (
                                                    <li key={i} className="flex items-start gap-2 text-[#c9d1d9]">
                                                        <span className="text-green-400 mt-0.5">✓</span>
                                                        <span>{item}</span>
                                                    </li>
                                                ))}
                                            </ul>
                                        </div>
                                        <div>
                                            <h4 className="text-red-400 font-medium mb-3 flex items-center gap-2">
                                                <XCircle size={16} /> DON'T: What to Avoid
                                            </h4>
                                            <ul className="space-y-2 text-sm">
                                                {comm.donts.map((item, i) => (
                                                    <li key={i} className="flex items-start gap-2 text-[#c9d1d9]">
                                                        <span className="text-red-400 mt-0.5">✗</span>
                                                        <span>{item}</span>
                                                    </li>
                                                ))}
                                            </ul>
                                        </div>
                                    </div>
                                    {comm.opening && (
                                        <div className="mt-6 pt-4 border-t border-[#30363d]">
                                            <h4 className="text-blue-400 font-medium mb-2 flex items-center gap-2">
                                                <Target size={16} /> Best Opening Approach
                                            </h4>
                                            <p className="bg-blue-500/10 border border-blue-500/30 rounded-lg p-4 text-[#c9d1d9]">
                                                {comm.opening}
                                            </p>
                                        </div>
                                    )}
                                </>
                            ) : (
                                <div className="text-center py-8">
                                    <MessageSquare size={48} className="mx-auto mb-4 text-[#30363d]" />
                                    <p className="text-[#8b919a]">Communication playbook not available</p>
                                    {!isEnriched && <p className="text-[#6e7681] text-sm mt-2">Enrich to generate personalized communication strategies</p>}
                                </div>
                            )}
                        </Card>
                    </div>
                )}

                {/* DOSSIER - RAW */}
                {mainTab === 'dossier' && subTab === 'raw' && (
                    <Card 
                        title="Raw Enrichment Data" 
                        icon={<FileText size={18} />}
                        action={raw && <CopyButton text={raw} />}
                    >
                        <pre className="text-xs text-[#8b919a] whitespace-pre-wrap font-mono bg-[#0d1117] p-4 rounded-lg max-h-[600px] overflow-y-auto border border-[#21262d]">
                            {raw || 'No enrichment data available. Click "Enrich Profile" to generate.'}
                        </pre>
                    </Card>
                )}

                {/* OUTREACH TAB */}
                {mainTab === 'outreach' && (
                    <div className="space-y-6">
                        <Card title="Email Sequences" icon={<Mail size={18} />} color="text-blue-400">
                            <div className="text-center py-12">
                                <Mail size={48} className="mx-auto text-[#30363d] mb-4" />
                                <p className="text-[#8b919a] text-lg mb-2">Coming Soon</p>
                                <p className="text-[#6e7681]">AI-powered email sequences based on the contact profile</p>
                            </div>
                        </Card>
                        
                        <Card title="Call Scripts" icon={<Phone size={18} />} color="text-green-400">
                            <div className="text-center py-12">
                                <Phone size={48} className="mx-auto text-[#30363d] mb-4" />
                                <p className="text-[#8b919a] text-lg mb-2">Coming Soon</p>
                                <p className="text-[#6e7681]">Personalized call scripts and talking points</p>
                            </div>
                        </Card>
                    </div>
                )}
            </div>
        </div>
    );
}
