import { useParams, useNavigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import OutreachTab from './OutreachTab';
import { 
    User, Building2, Target, MessageSquare, TrendingUp, ChevronLeft, 
    Mail, Phone, RefreshCw, Briefcase, GraduationCap, Award, Brain, 
    FileText, AlertTriangle, DollarSign, Zap, Shield, BarChart3, 
    Lightbulb, CheckCircle2, XCircle, Globe, Layers, UserCheck, 
    ExternalLink, Download, Loader2, X, Sparkles, Copy, Check,
    Clock, Users
} from 'lucide-react';

const API_URL = 'http://localhost:8000';

// =============================================================================
// TYPES
// =============================================================================
interface Contact {
    id: number;
    name?: string;
    first_name?: string;
    last_name?: string;
    email: string;
    phone: string;
    company: string;
    title: string;
    enrichment_status: string;
    enrichment_data: string | null;
    linkedin_url: string | null;
    enriched_at: string | null;
    match_score?: number;
    match_tier?: string;
    fit_score?: number;
    relevance_score?: number;
    timing_score?: number;
}

interface WhyMeData {
    hook?: string;
    proof_points?: string[];
    why_now?: string;
    suggested_opening?: string;
    talking_points?: string[];
    objection_handlers?: { objection: string; response: string }[] | string[];
    rapport_builders?: string[];
    best_channel?: string;
    generated_at?: string;
    fallback?: boolean;
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
    return {
        primary: primMatch ? `${primMatch[1]} - ${primMatch[2]}` : 'N/A',
        secondary: secMatch ? `${secMatch[1]} - ${secMatch[2]}` : 'N/A',
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

// =============================================================================
// UI COMPONENTS
// =============================================================================
const Card: React.FC<{ title: string; icon: React.ReactNode; children: React.ReactNode; color?: string }> = 
    ({ title, icon, children, color = 'text-blue-400' }) => (
    <div className="bg-[#1e2228] rounded-xl border border-gray-800 overflow-hidden">
        <div className={`flex items-center gap-2 px-4 py-3 border-b border-gray-800 ${color}`}>
            {icon}
            <h3 className="font-semibold text-white">{title}</h3>
        </div>
        <div className="p-4">{children}</div>
    </div>
);

const ScoreBadge: React.FC<{ score: number; tier: string }> = ({ score, tier }) => {
    const tierColors: Record<string, string> = {
        HIGH: 'bg-green-500/20 text-green-400 border-green-500/50',
        MEDIUM: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/50',
        LOW: 'bg-orange-500/20 text-orange-400 border-orange-500/50',
        MINIMAL: 'bg-red-500/20 text-red-400 border-red-500/50',
    };
    
    return (
        <div className="flex items-center gap-3">
            <div className="text-3xl font-bold text-white">{Math.round(score)}</div>
            <span className={`px-2 py-1 rounded border text-xs font-bold ${tierColors[tier] || tierColors.LOW}`}>
                {tier}
            </span>
        </div>
    );
};

// =============================================================================
// WHY ME TAB COMPONENT
// =============================================================================
const WhyMeTab: React.FC<{ contactId: number; contactName: string }> = ({ contactId, contactName }) => {
    const [data, setData] = useState<WhyMeData | null>(null);
    const [loading, setLoading] = useState(true);
    const [generating, setGenerating] = useState(false);
    const [copied, setCopied] = useState<string | null>(null);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        fetchWhyMe();
    }, [contactId]);

    const fetchWhyMe = async () => {
        try {
            setLoading(true);
            const res = await fetch(`${API_URL}/api/contacts/${contactId}/why-me`);
            if (res.ok) {
                const json = await res.json();
                if (json.hook) {
                    setData(json);
                } else {
                    setData(null);
                }
            } else {
                setData(null);
            }
        } catch (e) {
            setError('Failed to load');
        } finally {
            setLoading(false);
        }
    };

    const generateWhyMe = async () => {
        try {
            setGenerating(true);
            setError(null);
            const res = await fetch(`${API_URL}/api/contacts/${contactId}/why-me`, { method: 'POST' });
            const json = await res.json();
            if (json.success) {
                setData(json.why_me);
            } else {
                setError(json.error || 'Generation failed');
            }
        } catch (e) {
            setError('Failed to generate');
        } finally {
            setGenerating(false);
        }
    };

    const copyToClipboard = (text: string, id: string) => {
        navigator.clipboard.writeText(text);
        setCopied(id);
        setTimeout(() => setCopied(null), 2000);
    };

    const CopyButton = ({ text, id }: { text: string; id: string }) => (
        <button
            onClick={() => copyToClipboard(text, id)}
            className="p-1.5 hover:bg-gray-700 rounded transition"
            title="Copy"
        >
            {copied === id ? <Check size={14} className="text-green-400" /> : <Copy size={14} className="text-gray-500" />}
        </button>
    );

    if (loading) {
        return (
            <div className="flex items-center justify-center py-16">
                <Loader2 className="w-8 h-8 text-purple-400 animate-spin" />
            </div>
        );
    }

    if (!data) {
        return (
            <div className="text-center py-16">
                <Target className="w-16 h-16 text-gray-700 mx-auto mb-4" />
                <h3 className="text-xl text-white mb-2">Generate Your "Why Me"</h3>
                <p className="text-gray-400 mb-6 max-w-md mx-auto">
                    AI will analyze {contactName}'s profile and create personalized talking points 
                    based on YOUR strengths and track record.
                </p>
                <button
                    onClick={generateWhyMe}
                    disabled={generating}
                    className="bg-purple-600 hover:bg-purple-700 disabled:opacity-50 text-white px-6 py-3 rounded-lg font-medium inline-flex items-center gap-2"
                >
                    {generating ? (
                        <><Loader2 size={18} className="animate-spin" /> Generating...</>
                    ) : (
                        <><Sparkles size={18} /> Generate Why Me</>
                    )}
                </button>
                {error && <p className="text-red-400 mt-4">{error}</p>}
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Regenerate */}
            <div className="flex justify-between items-center">
                <div className="text-sm text-gray-500">
                    {data.generated_at && `Generated ${new Date(data.generated_at).toLocaleDateString()}`}
                </div>
                <button
                    onClick={generateWhyMe}
                    disabled={generating}
                    className="text-purple-400 hover:text-purple-300 text-sm flex items-center gap-1"
                >
                    {generating ? <Loader2 size={14} className="animate-spin" /> : <RefreshCw size={14} />}
                    Regenerate
                </button>
            </div>

            {/* THE HOOK */}
            <div className="bg-gradient-to-r from-purple-900/30 to-blue-900/30 rounded-xl border border-purple-800/50 p-5">
                <div className="flex items-start justify-between">
                    <div className="flex items-center gap-2 text-purple-300 mb-3">
                        <Target size={18} />
                        <h3 className="font-semibold">The Hook</h3>
                    </div>
                    <CopyButton text={data.hook || ''} id="hook" />
                </div>
                <p className="text-white text-lg leading-relaxed">"{data.hook}"</p>
            </div>

            {/* SUGGESTED OPENING */}
            <div className="bg-[#1e2228] rounded-xl border border-gray-800 p-5">
                <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center gap-2 text-green-400">
                        <MessageSquare size={18} />
                        <h3 className="font-semibold">Suggested Opening</h3>
                        {data.best_channel && (
                            <span className="bg-green-900/30 text-green-300 px-2 py-0.5 rounded text-xs">
                                via {data.best_channel}
                            </span>
                        )}
                    </div>
                    <CopyButton text={data.suggested_opening || ''} id="opening" />
                </div>
                <div className="bg-[#0f1114] rounded-lg p-4 border border-gray-700">
                    <p className="text-gray-200 whitespace-pre-wrap">{data.suggested_opening}</p>
                </div>
            </div>

            <div className="grid md:grid-cols-2 gap-4">
                {/* PROOF POINTS */}
                <div className="bg-[#1e2228] rounded-xl border border-gray-800 p-5">
                    <div className="flex items-center gap-2 text-blue-400 mb-4">
                        <Shield size={18} />
                        <h3 className="font-semibold">Your Proof Points</h3>
                    </div>
                    <ul className="space-y-2">
                        {(data.proof_points || []).map((point, i) => (
                            <li key={i} className="flex items-start gap-2 text-gray-300 text-sm">
                                <span className="text-blue-400 mt-0.5">•</span>
                                {point}
                            </li>
                        ))}
                    </ul>
                </div>

                {/* WHY NOW */}
                <div className="bg-[#1e2228] rounded-xl border border-gray-800 p-5">
                    <div className="flex items-center gap-2 text-orange-400 mb-4">
                        <Clock size={18} />
                        <h3 className="font-semibold">Why Now?</h3>
                    </div>
                    <p className="text-gray-300 text-sm leading-relaxed">{data.why_now}</p>
                </div>
            </div>

            {/* TALKING POINTS */}
            <div className="bg-[#1e2228] rounded-xl border border-gray-800 p-5">
                <div className="flex items-center gap-2 text-cyan-400 mb-4">
                    <Lightbulb size={18} />
                    <h3 className="font-semibold">Talking Points</h3>
                </div>
                <div className="grid md:grid-cols-2 gap-3">
                    {(data.talking_points || []).map((point, i) => (
                        <div key={i} className="bg-[#0f1114] rounded-lg p-3 border border-gray-700 text-gray-300 text-sm">
                            {point}
                        </div>
                    ))}
                </div>
            </div>

            {/* OBJECTION HANDLERS */}
            {data.objection_handlers && data.objection_handlers.length > 0 && (
                <div className="bg-[#1e2228] rounded-xl border border-gray-800 p-5">
                    <div className="flex items-center gap-2 text-red-400 mb-4">
                        <Shield size={18} />
                        <h3 className="font-semibold">Objection Handlers</h3>
                    </div>
                    <div className="space-y-3">
                        {data.objection_handlers.map((obj, i) => (
                            <div key={i} className="bg-[#0f1114] rounded-lg p-4 border border-gray-700">
                                <p className="text-red-300 text-sm font-medium mb-2">
                                    "{typeof obj === 'string' ? obj : obj.objection}"
                                </p>
                                <p className="text-gray-300 text-sm">
                                    → {typeof obj === 'string' ? 'Prepare response' : obj.response}
                                </p>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* RAPPORT BUILDERS */}
            {data.rapport_builders && data.rapport_builders.length > 0 && (
                <div className="bg-[#1e2228] rounded-xl border border-gray-800 p-5">
                    <div className="flex items-center gap-2 text-yellow-400 mb-4">
                        <Users size={18} />
                        <h3 className="font-semibold">Rapport Builders</h3>
                    </div>
                    <div className="flex flex-wrap gap-2">
                        {data.rapport_builders.map((item, i) => (
                            <span key={i} className="bg-yellow-900/30 text-yellow-300 px-3 py-1.5 rounded-lg text-sm">
                                {item}
                            </span>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
};

// =============================================================================
// MAIN COMPONENT
// =============================================================================
export default function ContactDetail() {
    const { id } = useParams<{ id: string }>();
    const navigate = useNavigate();
    const [contact, setContact] = useState<Contact | null>(null);
    const [loading, setLoading] = useState(true);
    const [enriching, setEnriching] = useState(false);
    const [scoring, setScoring] = useState(false);
    const [mainTab, setMainTab] = useState<'intel' | 'company' | 'personality' | 'whyme' | 'raw'>('intel');

    useEffect(() => {
        if (id) fetchContact();
    }, [id]);

    const fetchContact = async () => {
        try {
            const res = await fetch(`${API_URL}/api/contacts/${id}`);
            const data = await res.json();
            setContact(data);
        } catch (e) {
            console.error('Fetch error:', e);
        } finally {
            setLoading(false);
        }
    };

    const handleEnrich = async () => {
        if (!contact) return;
        setEnriching(true);
        try {
            const res = await fetch(`${API_URL}/api/contacts/${contact.id}/enrich`, { method: 'POST' });
            if (res.ok) {
                await fetchContact();
            }
        } catch (e) {
            console.error('Enrich error:', e);
        } finally {
            setEnriching(false);
        }
    };

    const handleRescore = async () => {
        if (!contact) return;
        setScoring(true);
        try {
            const res = await fetch(`${API_URL}/api/contacts/${contact.id}/score`, { method: 'POST' });
            if (res.ok) {
                await fetchContact();
            }
        } catch (e) {
            console.error('Score error:', e);
        } finally {
            setScoring(false);
        }
    };

    const getDisplayName = () => {
        if (!contact) return '';
        if (contact.name) return contact.name;
        return `${contact.first_name || ''} ${contact.last_name || ''}`.trim() || 'Unknown';
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-[#0f1114] flex items-center justify-center">
                <Loader2 className="w-8 h-8 text-purple-400 animate-spin" />
            </div>
        );
    }

    if (!contact) {
        return (
            <div className="min-h-screen bg-[#0f1114] flex items-center justify-center text-white">
                Contact not found
            </div>
        );
    }

    const raw = contact.enrichment_data || '';
    const salesSection = extractSection(raw, '=== SALES INTELLIGENCE ===');
    const companySection = extractSection(raw, '=== COMPANY RESEARCH');
    const personSection = extractSection(raw, '=== PERSON RESEARCH');
    const personalitySection = extractSection(raw, '=== PERSONALITY ANALYSIS ===');
    
    const salesItems = parseNumberedSections(salesSection);
    const mbti = parseMBTI(personalitySection);
    const disc = parseDISC(personalitySection);
    const comm = parseCommPlaybook(personalitySection);
    
    const contactName = getDisplayName();

    return (
        <div className="min-h-screen bg-[#0f1114] text-white">
            {/* Header */}
            <div className="bg-[#1a1d21] border-b border-gray-800 px-6 py-4">
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                        <button onClick={() => navigate(-1)} className="text-gray-400 hover:text-white flex items-center gap-1">
                            <ChevronLeft size={20} /> Back
                        </button>
                        <div>
                            <h1 className="text-2xl font-bold">{contactName}</h1>
                            <p className="text-gray-400">{contact.title} at {contact.company}</p>
                        </div>
                    </div>
                    <div className="flex items-center gap-3">
                        {/* Match Score */}
                        {contact.match_score !== undefined && contact.match_score !== null && (
                            <div className="flex items-center gap-2 bg-[#0f1114] px-4 py-2 rounded-lg border border-gray-700">
                                <span className="text-gray-400 text-sm">MATCH</span>
                                <ScoreBadge score={contact.match_score} tier={contact.match_tier || 'LOW'} />
                            </div>
                        )}
                        
                        {/* Re-score Button */}
                        <button
                            onClick={handleRescore}
                            disabled={scoring}
                            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 rounded-lg flex items-center gap-2"
                        >
                            {scoring ? <Loader2 size={16} className="animate-spin" /> : <BarChart3 size={16} />}
                            Re-score
                        </button>
                        
                        {/* Enrich Button */}
                        <button
                            onClick={handleEnrich}
                            disabled={enriching}
                            className="px-4 py-2 bg-purple-600 hover:bg-purple-700 disabled:opacity-50 rounded-lg flex items-center gap-2"
                        >
                            {enriching ? <Loader2 size={16} className="animate-spin" /> : <RefreshCw size={16} />}
                            {contact.enrichment_status === 'completed' ? 'Re-enrich' : 'Enrich'}
                        </button>
                    </div>
                </div>

                {/* Contact Info Bar */}
                <div className="flex items-center gap-6 mt-4 text-sm">
                    {contact.email && (
                        <a href={`mailto:${contact.email}`} className="flex items-center gap-1 text-gray-400 hover:text-white">
                            <Mail size={14} /> {contact.email}
                        </a>
                    )}
                    {contact.phone && (
                        <a href={`tel:${contact.phone}`} className="flex items-center gap-1 text-gray-400 hover:text-white">
                            <Phone size={14} /> {contact.phone}
                        </a>
                    )}
                    {contact.linkedin_url && (
                        <a href={contact.linkedin_url} target="_blank" className="flex items-center gap-1 text-blue-400 hover:text-blue-300">
                            <ExternalLink size={14} /> LinkedIn
                        </a>
                    )}
                    {contact.enriched_at && (
                        <span className="text-gray-500">
                            Enriched: {new Date(contact.enriched_at).toLocaleDateString()}
                        </span>
                    )}
                </div>

                {/* Score Breakdown */}
                {contact.match_score !== undefined && (
                    <div className="flex items-center gap-6 mt-4 text-sm">
                        <span className="text-gray-500">Score Breakdown:</span>
                        <span className="text-green-400">FIT: {Math.round(contact.fit_score || 0)}</span>
                        <span className="text-blue-400">RELEVANCE: {Math.round(contact.relevance_score || 0)}</span>
                        <span className="text-orange-400">TIMING: {Math.round(contact.timing_score || 0)}</span>
                    </div>
                )}

                {/* Tabs */}
                <div className="flex gap-1 mt-4">
                    {[
                        { id: 'intel', label: 'Sales Intel', icon: <Target size={16} /> },
                        { id: 'company', label: 'Company', icon: <Building2 size={16} /> },
                        { id: 'personality', label: 'Personality', icon: <Brain size={16} /> },
                        { id: 'whyme', label: 'Why Me', icon: <Sparkles size={16} /> },
                        { id: 'raw', label: 'Raw Data', icon: <FileText size={16} /> },
                        { id: 'outreach', label: 'Outreach', icon: <Mail size={16} /> },
                    ].map(tab => (
                        <button
                            key={tab.id}
                            onClick={() => setMainTab(tab.id as any)}
                            className={`px-4 py-2 rounded-lg flex items-center gap-2 transition ${
                                mainTab === tab.id 
                                    ? 'bg-purple-600 text-white' 
                                    : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
                            }`}
                        >
                            {tab.icon} {tab.label}
                        </button>
                    ))}
                </div>
            </div>

            {/* Tab Content */}
            <div className="p-6">
                {/* INTEL TAB */}
                {mainTab === 'intel' && (
                    <div className="space-y-6">
                        {salesItems.length > 0 ? (
                            <div className="grid md:grid-cols-2 gap-4">
                                {salesItems.map((item, i) => (
                                    <Card key={i} title={item.title} icon={<Zap size={18} />} color="text-yellow-400">
                                        <ul className="space-y-2">
                                            {item.content.slice(0, 5).map((line, j) => (
                                                <li key={j} className="text-gray-300 text-sm flex items-start gap-2">
                                                    <span className="text-yellow-400">•</span> {line}
                                                </li>
                                            ))}
                                        </ul>
                                    </Card>
                                ))}
                            </div>
                        ) : (
                            <div className="text-center py-16 text-gray-500">
                                <Target className="w-16 h-16 mx-auto mb-4 opacity-30" />
                                <p>No sales intelligence available. Enrich this contact to generate insights.</p>
                            </div>
                        )}
                    </div>
                )}

                {/* COMPANY TAB */}
                {mainTab === 'company' && (
                    <div className="bg-[#1e2228] rounded-xl border border-gray-800 p-6">
                        <div className="prose prose-invert max-w-none">
                            {companySection ? (
                                <div className="text-gray-300 whitespace-pre-wrap">{cleanText(companySection)}</div>
                            ) : (
                                <p className="text-gray-500">No company data available.</p>
                            )}
                        </div>
                    </div>
                )}

                {/* PERSONALITY TAB */}
                {mainTab === 'personality' && (
                    <div className="space-y-6">
                        <div className="grid md:grid-cols-2 gap-6">
                            {/* MBTI */}
                            <Card title="MBTI Profile" icon={<Brain size={18} />} color="text-purple-400">
                                <div className="flex items-center gap-4 mb-4">
                                    <div className="text-4xl font-bold text-purple-400">{mbti.type}</div>
                                    <div className="text-sm text-gray-400">
                                        Confidence: <span className="text-white">{mbti.confidence}</span>
                                    </div>
                                </div>
                                {mbti.dimensions.length > 0 && (
                                    <div className="space-y-2">
                                        {mbti.dimensions.map((d, i) => (
                                            <div key={i} className="text-sm">
                                                <span className="text-gray-400">{d.dim}:</span>{' '}
                                                <span className="text-white">{d.pref}</span>
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </Card>

                            {/* DISC */}
                            <Card title="DISC Profile" icon={<Layers size={18} />} color="text-blue-400">
                                <div className="space-y-2">
                                    <div className="flex justify-between">
                                        <span className="text-gray-400">Primary:</span>
                                        <span className="text-white font-semibold">{disc.primary}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-gray-400">Secondary:</span>
                                        <span className="text-white">{disc.secondary}</span>
                                    </div>
                                </div>
                            </Card>
                        </div>

                        {/* Communication Playbook */}
                        <Card title="Communication Playbook" icon={<MessageSquare size={18} />} color="text-green-400">
                            <div className="grid md:grid-cols-2 gap-6">
                                <div>
                                    <h4 className="text-green-400 font-semibold mb-2 flex items-center gap-2">
                                        <CheckCircle2 size={16} /> DO
                                    </h4>
                                    <ul className="space-y-1">
                                        {comm.dos.map((item, i) => (
                                            <li key={i} className="text-gray-300 text-sm">• {item}</li>
                                        ))}
                                    </ul>
                                </div>
                                <div>
                                    <h4 className="text-red-400 font-semibold mb-2 flex items-center gap-2">
                                        <XCircle size={16} /> DON'T
                                    </h4>
                                    <ul className="space-y-1">
                                        {comm.donts.map((item, i) => (
                                            <li key={i} className="text-gray-300 text-sm">• {item}</li>
                                        ))}
                                    </ul>
                                </div>
                            </div>
                            {comm.opening && (
                                <div className="mt-4 pt-4 border-t border-gray-700">
                                    <h4 className="text-yellow-400 font-semibold mb-2">🎯 Best Opening Approach</h4>
                                    <p className="text-gray-300 text-sm">{comm.opening}</p>
                                </div>
                            )}
                        </Card>
                    </div>
                )}

                {/* WHY ME TAB */}
                {mainTab === 'whyme' && (
                    <WhyMeTab contactId={contact.id} contactName={contactName} />
                )}

                {/* OUTREACH TAB */}
                {mainTab === 'outreach' && contact && (
                    <OutreachTab
                        contactId={contact.id}
                        contactName={contactName}
                        contactEmail={contact.email}
                    />
                )}

                {/* RAW DATA TAB */}
                {mainTab === 'raw' && (
                    <div className="bg-[#1e2228] rounded-xl border border-gray-800 p-6">
                        <pre className="text-gray-300 text-sm whitespace-pre-wrap font-mono overflow-auto max-h-[70vh]">
                            {raw || 'No enrichment data available.'}
                        </pre>
                    </div>
                )}
            </div>
        </div>
    );
}

// Note: EmailDrafter imported at top, Outreach tab added to tabs array
