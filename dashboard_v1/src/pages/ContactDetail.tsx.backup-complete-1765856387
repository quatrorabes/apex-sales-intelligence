import { useParams, useNavigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import {
    User, Building2, Target, MessageSquare, TrendingUp, ChevronLeft,
    Mail, Phone, RefreshCw, Briefcase, GraduationCap, Award, Brain,
    FileText, AlertTriangle, DollarSign, Zap, Shield, BarChart3,
    Lightbulb, CheckCircle2, XCircle, Globe, Layers, UserCheck,
    ExternalLink, Download, Loader2, X
} from 'lucide-react';

// PRODUCTION FIX: Use env var or production URL
const API_BASE = import.meta.env.VITE_API_URL || import.meta.env.VITE_APEX_API_URL || 'https://apex-backend-i7b0.onrender.com';

// =============================================================================
// TYPES
// =============================================================================

interface Contact {
    id: number;
    first_name: string;
    last_name: string;
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
// PARSING UTILITIES
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

interface ParsedSection {
    title: string;
    content: string[];
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

function parseMBTI(text: string): { type: string; confidence: string; dimensions: any[] } {
    const typeMatch = text.match(/Inferred Type[:\s]*([A-Z]{4})/i);
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
    const styleRegex = /\|\s*([A-Z])\s*[-–]\s*(\w+)\s*\|\s*(\d+%?)\s*\|\s*([^|]+)\|/gi;
    let m;
    while ((m = styleRegex.exec(text)) !== null) {
        styles.push({ style: `${m[1]} - ${m[2]}`, pct: m[3], evidence: cleanText(m[4]) });
    }
    return { primary: primMatch ? `${primMatch[1]} - ${primMatch[2]}` : 'N/A', secondary: secMatch ? `${secMatch[1]} - ${secMatch[2]}` : 'N/A', styles };
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

// =============================================================================
// UI COMPONENTS
// =============================================================================

const Card: React.FC<{ title: string; icon: React.ReactNode; children: React.ReactNode; color?: string }> = ({ title, icon, children, color = 'text-blue-400' }) => (
    <div className="bg-[#161b22] border border-[#30363d] rounded-lg overflow-hidden">
        <div className={`px-4 py-3 border-b border-[#30363d] flex items-center gap-2 ${color}`}>
            {icon}
            <h3 className="font-semibold text-white">{title}</h3>
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
        className={`px-3 py-1 text-xs rounded-full transition-colors ${active ? 'bg-blue-600 text-white' : 'bg-[#21262d] text-[#8b919a] hover:text-white'}`}
    >
        {children}
    </button>
);

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

    useEffect(() => { if (id) fetchContact(); }, [id]);

    const fetchContact = async () => {
        try {
            const res = await fetch(`${API_BASE}/api/contacts/${id}`);
            const data = await res.json();
            // PRODUCTION FIX: Handle nested {success, contact} response
            setContact(data.contact || data);
        } catch (e) { console.error(e); }
        finally { setLoading(false); }
    };

    const handleEnrich = async () => {
        setEnriching(true);
        try {
            await fetch(`${API_BASE}/api/contacts/${id}/enrich`, { method: 'POST' });
            // Poll for status
            const poll = setInterval(async () => {
                const res = await fetch(`${API_BASE}/api/contacts/${id}`);
                const data = await res.json();
                const c = data.contact || data;
                if (c.enrichment_status === 'completed' || c.enrichment_status === 'error') {
                    clearInterval(poll);
                    setContact(c);
                    setEnriching(false);
                }
            }, 2000);
            // Timeout after 60s
            setTimeout(() => {
                clearInterval(poll);
                setEnriching(false);
                fetchContact();
            }, 60000);
        } catch (e) { setEnriching(false); }
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

    const raw = contact.enrichment_data || '';
    const isEnriched = contact.enrichment_status === 'completed' && raw.length > 100;

    const salesSection = extractSection(raw, '=== SALES INTELLIGENCE ===');
    const companySection = extractSection(raw, '=== COMPANY RESEARCH ===');
    const personalitySection = extractSection(raw, '=== PERSONALITY ASSESSMENT ===');

    const salesCards = parseNumberedSections(salesSection);
    const companyCards = parseNumberedSections(companySection);
    const mbti = parseMBTI(personalitySection);
    const disc = parseDISC(personalitySection);
    const comm = parseCommPlaybook(personalitySection);

    return (
        <div className="min-h-screen bg-[#0d1117] text-white">
            {/* HEADER */}
            <div className="bg-[#161b22] border-b border-[#30363d]">
                <div className="max-w-6xl mx-auto px-6 py-4">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-4">
                            <button onClick={() => navigate('/contacts')} className="text-[#8b919a] hover:text-white">
                                <ChevronLeft size={24} />
                            </button>
                            <div className="w-12 h-12 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-xl font-bold">
                                {contact.first_name?.charAt(0) || 'C'}
                            </div>
                            <div>
                                <h1 className="text-xl font-bold">{contact.first_name} {contact.last_name}</h1>
                                <p className="text-[#8b919a] text-sm">{contact.title} at {contact.company}</p>
                            </div>
                        </div>
                        <button
                            onClick={handleEnrich}
                            disabled={enriching}
                            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-600/50 rounded-lg flex items-center gap-2 transition"
                        >
                            {enriching ? <Loader2 className="animate-spin" size={16} /> : <Zap size={16} />}
                            {enriching ? 'Enriching...' : isEnriched ? 'Re-enrich' : 'Enrich'}
                        </button>
                    </div>

                    {/* Contact Info Row */}
                    <div className="flex gap-6 mt-4 text-sm text-[#8b919a]">
                        {contact.email && (
                            <div className="flex items-center gap-2">
                                <Mail size={14} />
                                <span>{contact.email}</span>
                            </div>
                        )}
                        {contact.phone && (
                            <div className="flex items-center gap-2">
                                <Phone size={14} />
                                <span>{contact.phone}</span>
                            </div>
                        )}
                        {contact.linkedin_url && (
                            <a href={contact.linkedin_url} target="_blank" rel="noopener noreferrer" className="flex items-center gap-2 text-blue-400 hover:text-blue-300">
                                <ExternalLink size={14} />
                                <span>LinkedIn</span>
                            </a>
                        )}
                    </div>

                    {/* Main Tabs */}
                    <div className="flex gap-4 mt-4 border-b border-[#30363d]">
                        <Tab active={mainTab === 'dossier'} onClick={() => setMainTab('dossier')}>
                            <Brain className="inline mr-2" size={16} />Dossier
                        </Tab>
                        <Tab active={mainTab === 'outreach'} onClick={() => setMainTab('outreach')}>
                            <MessageSquare className="inline mr-2" size={16} />Outreach
                        </Tab>
                    </div>
                </div>
            </div>

            {/* CONTENT */}
            <div className="max-w-6xl mx-auto px-6 py-6 space-y-6">
                {/* Sub Tabs for Dossier */}
                {mainTab === 'dossier' && (
                    <div className="flex gap-2">
                        <SubTab active={subTab === 'sales'} onClick={() => setSubTab('sales')}>Sales Intel</SubTab>
                        <SubTab active={subTab === 'company'} onClick={() => setSubTab('company')}>Company</SubTab>
                        <SubTab active={subTab === 'personality'} onClick={() => setSubTab('personality')}>Personality</SubTab>
                        <SubTab active={subTab === 'raw'} onClick={() => setSubTab('raw')}>Raw Data</SubTab>
                    </div>
                )}

                {/* DOSSIER - SALES */}
                {mainTab === 'dossier' && subTab === 'sales' && (
                    <Card title="Sales Intelligence" icon={<Target size={18} />} color="text-green-400">
                        {!isEnriched ? (
                            <div className="text-center py-8 text-[#8b919a]">
                                <Target size={48} className="mx-auto mb-4 opacity-30" />
                                <p>No sales intelligence available. Enrich this contact to generate insights.</p>
                            </div>
                        ) : salesCards.length > 0 ? (
                            <div className="space-y-4">
                                {salesCards.map((card, i) => (
                                    <div key={i} className="border-l-2 border-green-500 pl-4">
                                        <h4 className="font-semibold text-white mb-2">{card.title}</h4>
                                        <ul className="space-y-1 text-sm text-[#8b919a]">
                                            {card.content.map((line, j) => (
                                                <li key={j} className="flex items-start gap-2">
                                                    <span className="text-green-400 mt-1">•</span>
                                                    <span>{line}</span>
                                                </li>
                                            ))}
                                        </ul>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <p className="text-[#8b919a]">No structured sales data found.</p>
                        )}
                    </Card>
                )}

                {/* DOSSIER - COMPANY */}
                {mainTab === 'dossier' && subTab === 'company' && (
                    <Card title="Company Intelligence" icon={<Building2 size={18} />} color="text-blue-400">
                        {companyCards.length > 0 ? (
                            <div className="space-y-4">
                                {companyCards.map((card, i) => (
                                    <div key={i} className="border-l-2 border-blue-500 pl-4">
                                        <h4 className="font-semibold text-white mb-2">{card.title}</h4>
                                        <ul className="space-y-1 text-sm text-[#8b919a]">
                                            {card.content.map((line, j) => (
                                                <li key={j}>{line}</li>
                                            ))}
                                        </ul>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <p className="text-[#8b919a]">No company data available.</p>
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
                                <div className="text-sm text-[#8b919a]">
                                    <span className="text-white">Confidence</span>
                                    <span className={`ml-2 px-2 py-1 rounded text-xs ${mbti.confidence === 'High' ? 'bg-green-500/20 text-green-400' : mbti.confidence === 'Medium' ? 'bg-yellow-500/20 text-yellow-400' : 'bg-red-500/20 text-red-400'}`}>
                                        {mbti.confidence}
                                    </span>
                                </div>
                            </div>
                            {mbti.dimensions.length > 0 && (
                                <table className="w-full text-sm">
                                    <thead>
                                        <tr className="text-[#8b919a] border-b border-[#30363d]">
                                            <th className="text-left py-2">Dimension</th>
                                            <th className="text-left py-2">Preference</th>
                                            <th className="text-left py-2">Evidence</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {mbti.dimensions.map((d, i) => (
                                            <tr key={i} className="border-b border-[#30363d]">
                                                <td className="py-2">{d.dim}</td>
                                                <td className="py-2 text-purple-400">{d.pref}</td>
                                                <td className="py-2 text-[#8b919a]">{d.evidence}</td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            )}
                        </Card>

                        {/* Communication Playbook */}
                        <Card title="Communication Playbook" icon={<MessageSquare size={18} />} color="text-cyan-400">
                            <div className="grid md:grid-cols-2 gap-4">
                                <div>
                                    <h4 className="text-green-400 font-medium mb-2 flex items-center gap-2">
                                        <CheckCircle2 size={16} /> DO: How to Engage
                                    </h4>
                                    <ul className="space-y-2 text-sm">
                                        {comm.dos.map((item, i) => (
                                            <li key={i} className="flex items-start gap-2 text-[#8b919a]">
                                                <span className="text-green-400">✓</span>
                                                <span>{item}</span>
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                                <div>
                                    <h4 className="text-red-400 font-medium mb-2 flex items-center gap-2">
                                        <XCircle size={16} /> DON'T: What to Avoid
                                    </h4>
                                    <ul className="space-y-2 text-sm">
                                        {comm.donts.map((item, i) => (
                                            <li key={i} className="flex items-start gap-2 text-[#8b919a]">
                                                <span className="text-red-400">✗</span>
                                                <span>{item}</span>
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
