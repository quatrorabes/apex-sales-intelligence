import { useParams, useNavigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import {
    User, Building2, Target, MessageSquare, TrendingUp, ChevronLeft,
    Mail, Phone, RefreshCw, RotateCcw, Briefcase, GraduationCap,
    Award, Linkedin, Mic, Users, Brain, FileText, AlertTriangle,
    DollarSign, ShoppingCart, Zap, Shield, BarChart3, Lightbulb,
    Clock, CheckCircle2, XCircle
} from 'lucide-react';

// =============================================================================
// TYPE DEFINITIONS
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

interface ParsedCard {
    id: string;
    title: string;
    icon: React.ReactNode;
    content: string[];
}

interface ParsedSections {
    professional: ParsedCard[];
    company: ParsedCard[];
    salesIntel: ParsedCard[];
    painPoints: ParsedCard[];
    personality: {
        mbti: { type: string; confidence: string; dimensions: { dimension: string; preference: string; evidence: string }[] };
        disc: { primary: string; secondary: string; styles: { style: string; percent: string; evidence: string }[] };
        workStyle: string;
        doList: string[];
        dontList: string[];
        openingApproach: string;
    } | null;
    summary: string;
}

// =============================================================================
// PARSING UTILITIES
// =============================================================================

function cleanText(text: string): string {
    return text
        .replace(/\*\*/g, '')           // Remove bold markers
        .replace(/####\s*/g, '')        // Remove h4 markers
        .replace(/###\s*/g, '')         // Remove h3 markers
        .replace(/##\s*/g, '')          // Remove h2 markers
        .replace(/#\s*/g, '')           // Remove h1 markers
        .replace(/---+/g, '')           // Remove horizontal rules
        .replace(/\[(\d+)\]/g, '')      // Remove citation markers like [1]
        .replace(/^\s*[-•]\s*/gm, '')   // Remove bullet points at line start
        .replace(/\n{3,}/g, '\n\n')     // Collapse multiple newlines
        .trim();
}

function parseNumberedSection(content: string, sectionNumber: number): { title: string; content: string[] } | null {
    // Match patterns like "#### 1. **Current Role..." or "## 1. Current Role..."
    const patterns = [
        new RegExp(`(?:####?\\s*)?${sectionNumber}\\.\\s*\\*\\*([^*]+)\\*\\*([\\s\\S]*?)(?=(?:####?\\s*)?${sectionNumber + 1}\\.|===|$)`, 'i'),
        new RegExp(`(?:####?\\s*)?${sectionNumber}\\.\\s*([^\\n]+)([\\s\\S]*?)(?=(?:####?\\s*)?${sectionNumber + 1}\\.|===|$)`, 'i')
    ];

    for (const pattern of patterns) {
        const match = content.match(pattern);
        if (match) {
            const title = cleanText(match[1]).replace(/\*+$/, '').trim();
            const body = match[2] || '';
            const lines = body
                .split('\n')
                .map(line => cleanText(line))
                .filter(line => line.length > 0 && !line.match(/^-+$/));
            return { title, content: lines };
        }
    }
    return null;
}

function parseCompanySection(content: string, sectionNumber: number): { title: string; content: string[] } | null {
    const patterns = [
        new RegExp(`${sectionNumber}\\.\\s*\\*\\*([^*]+)\\*\\*([\\s\\S]*?)(?=${sectionNumber + 1}\\.|===|$)`, 'i'),
        new RegExp(`${sectionNumber}\\.\\s*([^\\n]+)([\\s\\S]*?)(?=${sectionNumber + 1}\\.|===|$)`, 'i')
    ];

    for (const pattern of patterns) {
        const match = content.match(pattern);
        if (match) {
            const title = cleanText(match[1]).replace(/\*+$/, '').trim();
            const body = match[2] || '';
            const lines = body
                .split('\n')
                .map(line => cleanText(line))
                .filter(line => line.length > 0 && !line.match(/^-+$/));
            return { title, content: lines };
        }
    }
    return null;
}

function parseSalesSection(content: string, sectionTitle: string): string[] {
    const pattern = new RegExp(`(?:##\\s*)?${sectionTitle}([\\s\\S]*?)(?=##\\s*[A-Z]|===|$)`, 'i');
    const match = content.match(pattern);
    if (match) {
        return match[1]
            .split('\n')
            .map(line => cleanText(line))
            .filter(line => line.length > 0 && !line.match(/^-+$/));
    }
    return [];
}

function parseEnrichmentData(rawData: string): ParsedSections {
    const sections: ParsedSections = {
        professional: [],
        company: [],
        salesIntel: [],
        painPoints: [],
        personality: null,
        summary: ''
    };

    // Extract main sections using === markers
    const personMatch = rawData.match(/=== PERSON RESEARCH:[^=]*===([\s\S]*?)(?====|$)/);
    const companyMatch = rawData.match(/=== COMPANY RESEARCH:[^=]*===([\s\S]*?)(?====|$)/);
    const salesMatch = rawData.match(/=== SALES INTELLIGENCE ===([\s\S]*?)(?====|$)/);
    const personalityMatch = rawData.match(/=== PERSONALITY ANALYSIS ===([\s\S]*?)(?====|$)/);

    const personContent = personMatch ? personMatch[1] : '';
    const companyContent = companyMatch ? companyMatch[1] : '';
    const salesContent = salesMatch ? salesMatch[1] : '';
    const personalityContent = personalityMatch ? personalityMatch[1] : '';

    // ==========================================================================
    // PROFESSIONAL TAB: Parse sections 1-9
    // ==========================================================================
    const professionalIcons = [
        <Briefcase size={18} />,      // 1. Current Role
        <FileText size={18} />,       // 2. Career History
        <GraduationCap size={18} />,  // 3. Education
        <Award size={18} />,          // 4. Achievements
        <Linkedin size={18} />,       // 5. LinkedIn Activity
        <Mic size={18} />,            // 6. Speaking Engagements
        <Users size={18} />,          // 7. Professional Associations
        <Brain size={18} />,          // 8. Management Style
        <Target size={18} />          // 9. Notable Deals
    ];

    for (let i = 1; i <= 9; i++) {
        const parsed = parseNumberedSection(personContent, i);
        if (parsed && parsed.content.length > 0) {
            sections.professional.push({
                id: `prof-${i}`,
                title: parsed.title,
                icon: professionalIcons[i - 1],
                content: parsed.content
            });
        }
    }

    // Parse Summary
    const summaryMatch = personContent.match(/###?\s*Summary([\s\S]*?)(?=###|===|$)/i);
    if (summaryMatch) {
        sections.summary = cleanText(summaryMatch[1]);
    }

    // ==========================================================================
    // COMPANY TAB: Parse sections 1-10
    // ==========================================================================
    const companyIcons = [
        <Building2 size={18} />,      // 1. Company Overview
        <DollarSign size={18} />,     // 2. Business Model
        <ShoppingCart size={18} />,   // 3. Products & Services
        <Target size={18} />,         // 4. Target Markets
        <BarChart3 size={18} />,      // 5. Competitive Landscape
        <Zap size={18} />,            // 6. Recent News
        <Users size={18} />,          // 7. Company Culture
        <Briefcase size={18} />,      // 8. Leadership Team
        <Shield size={18} />,         // 9. Technology Stack
        <TrendingUp size={18} />      // 10. Market Position
    ];

    for (let i = 1; i <= 10; i++) {
        const parsed = parseCompanySection(companyContent, i);
        if (parsed && parsed.content.length > 0) {
            sections.company.push({
                id: `company-${i}`,
                title: parsed.title,
                icon: companyIcons[i - 1] || <Building2 size={18} />,
                content: parsed.content
            });
        }
    }

    // ==========================================================================
    // SALES INTEL TAB
    // ==========================================================================
    const salesSections = [
        { key: 'industry-trends', title: 'Industry Trends', search: 'Industry Trends', icon: <TrendingUp size={18} /> },
        { key: 'buying-triggers', title: 'Buying Triggers', search: 'Buying Triggers', icon: <ShoppingCart size={18} /> },
        { key: 'budget-cycles', title: 'Budget Cycles', search: 'Budget Cycles', icon: <DollarSign size={18} /> },
        { key: 'key-initiatives', title: 'Key Initiatives', search: 'Key Initiatives', icon: <Lightbulb size={18} /> },
        { key: 'competitive-pressures', title: 'Competitive Pressures', search: 'Competitive Pressures', icon: <BarChart3 size={18} /> },
        { key: 'technology-trends', title: 'Technology Trends', search: 'Technology Trends', icon: <Zap size={18} /> },
        { key: 'economic-factors', title: 'Economic Factors', search: 'Economic Factors', icon: <DollarSign size={18} /> },
        { key: 'engagement-strategy', title: 'Engagement Strategy', search: 'Engagement Strategy|Sales Engagement', icon: <MessageSquare size={18} /> }
    ];

    for (const section of salesSections) {
        const content = parseSalesSection(salesContent, section.search);
        if (content.length > 0) {
            sections.salesIntel.push({
                id: section.key,
                title: section.title,
                icon: section.icon,
                content
            });
        }
    }

    // ==========================================================================
    // PAIN POINTS TAB
    // ==========================================================================
    const painPointSections = [
        { key: 'pain-general', title: 'Common Pain Points', search: 'Pain Points|Common Pain Points', icon: <AlertTriangle size={18} /> },
        { key: 'pain-regulatory', title: 'Regulatory Challenges', search: 'Regulatory|Compliance Challenges', icon: <Shield size={18} /> },
        { key: 'pain-company', title: 'Company Challenges', search: 'Company Challenges|Recent.*Challenges', icon: <Building2 size={18} /> }
    ];

    for (const section of painPointSections) {
        const content = parseSalesSection(salesContent, section.search);
        if (content.length > 0) {
            sections.painPoints.push({
                id: section.key,
                title: section.title,
                icon: section.icon,
                content
            });
        }
    }

    // ==========================================================================
    // PERSONALITY PARSING
    // ==========================================================================
    if (personalityContent) {
        // Parse MBTI
        const mbtiTypeMatch = personalityContent.match(/Inferred Type[:\s]*([A-Z]{4})/i);
        const mbtiConfidenceMatch = personalityContent.match(/Confidence[:\s]*(Low|Medium|High)/i);
        
        const mbtiDimensions: { dimension: string; preference: string; evidence: string }[] = [];
        const dimensionMatches = personalityContent.matchAll(/\|\s*(Energy|Information|Decisions|Structure)\s*\|\s*([A-Z])\s*[-–]\s*(\w+)\s*\|\s*([^|]+)\|/gi);
        for (const match of dimensionMatches) {
            mbtiDimensions.push({
                dimension: match[1],
                preference: `${match[2]} - ${match[3]}`,
                evidence: cleanText(match[4])
            });
        }

        // Parse DISC
        const discPrimaryMatch = personalityContent.match(/Primary Style[:\s]*([A-Z])\s*[-–]\s*(\w+)/i);
        const discSecondaryMatch = personalityContent.match(/Secondary Style[:\s]*([A-Z])\s*[-–]\s*(\w+)/i);
        
        const discStyles: { style: string; percent: string; evidence: string }[] = [];
        const discMatches = personalityContent.matchAll(/\|\s*([A-Z])\s*[-–]\s*(\w+)\s*\|\s*(\d+%?)\s*\|\s*([^|]+)\|/gi);
        for (const match of discMatches) {
            discStyles.push({
                style: `${match[1]} - ${match[2]}`,
                percent: match[3].includes('%') ? match[3] : `${match[3]}%`,
                evidence: cleanText(match[4])
            });
        }

        // Parse Work Style
        const workStyleMatch = personalityContent.match(/Work Style[:\s]*([^\n]+)/i);

        // Parse Do's and Don'ts
        const doMatch = personalityContent.match(/(?:✅\s*)?DO[:\s]*(?:How to Engage[^]*?)?([\s\S]*?)(?=(?:❌|DON'T|###|$))/i);
        const dontMatch = personalityContent.match(/(?:❌\s*)?DON'T[:\s]*(?:What to Avoid[^]*?)?([\s\S]*?)(?=(?:🎯|###|Best Opening|$))/i);
        
        const doList = doMatch ? doMatch[1].split('\n').map(l => cleanText(l)).filter(l => l.length > 0) : [];
        const dontList = dontMatch ? dontMatch[1].split('\n').map(l => cleanText(l)).filter(l => l.length > 0) : [];

        // Parse Opening Approach
        const openingMatch = personalityContent.match(/Best Opening Approach[:\s]*([\s\S]*?)(?=###|$)/i);

        sections.personality = {
            mbti: {
                type: mbtiTypeMatch ? mbtiTypeMatch[1] : 'Unknown',
                confidence: mbtiConfidenceMatch ? mbtiConfidenceMatch[1] : 'Unknown',
                dimensions: mbtiDimensions
            },
            disc: {
                primary: discPrimaryMatch ? `${discPrimaryMatch[1]} - ${discPrimaryMatch[2]}` : 'Unknown',
                secondary: discSecondaryMatch ? `${discSecondaryMatch[1]} - ${discSecondaryMatch[2]}` : 'Unknown',
                styles: discStyles
            },
            workStyle: workStyleMatch ? cleanText(workStyleMatch[1]) : '',
            doList,
            dontList,
            openingApproach: openingMatch ? cleanText(openingMatch[1]) : ''
        };
    }

    return sections;
}

// =============================================================================
// UI COMPONENTS
// =============================================================================

const SubsectionCard: React.FC<{ card: ParsedCard }> = ({ card }) => (
    <div className="bg-[rgba(255,255,255,0.02)] border border-[rgba(255,255,255,0.06)] rounded-lg p-4 mb-4">
        {/* Card Header */}
        <div className="flex items-center gap-3 mb-3 pb-2 border-b border-[rgba(255,255,255,0.06)]">
            <div className="text-blue-400">{card.icon}</div>
            <h4 className="text-[#f5f5f5] font-medium text-sm">{card.title}</h4>
        </div>
        
        {/* Card Content */}
        <div className="space-y-2">
            {card.content.map((line, idx) => {
                // Check if line is a label:value pair
                const colonIndex = line.indexOf(':');
                if (colonIndex > 0 && colonIndex < 40) {
                    const label = line.substring(0, colonIndex).trim();
                    const value = line.substring(colonIndex + 1).trim();
                    return (
                        <div key={idx} className="flex flex-col sm:flex-row sm:gap-2">
                            <span className="text-[#9ca3af] text-sm font-medium min-w-[140px]">{label}:</span>
                            <span className="text-[#f5f5f5] text-sm">{value}</span>
                        </div>
                    );
                }
                return (
                    <p key={idx} className="text-[#9ca3af] text-sm leading-relaxed">{line}</p>
                );
            })}
        </div>
    </div>
);

const PersonalityCard: React.FC<{ personality: ParsedSections['personality'] }> = ({ personality }) => {
    if (!personality) return null;

    return (
        <div className="space-y-4">
            {/* MBTI Card */}
            <div className="bg-[rgba(255,255,255,0.02)] border border-[rgba(255,255,255,0.06)] rounded-lg p-4">
                <div className="flex items-center gap-3 mb-3 pb-2 border-b border-[rgba(255,255,255,0.06)]">
                    <Brain size={18} className="text-purple-400" />
                    <h4 className="text-[#f5f5f5] font-medium">Myers-Briggs (MBTI) Assessment</h4>
                </div>
                <div className="flex items-center gap-4 mb-4">
                    <div className="bg-purple-500/20 px-4 py-2 rounded-lg">
                        <span className="text-purple-300 font-bold text-2xl">{personality.mbti.type}</span>
                    </div>
                    <div className="text-[#9ca3af] text-sm">
                        Confidence: <span className="text-[#f5f5f5]">{personality.mbti.confidence}</span>
                    </div>
                </div>
                {personality.mbti.dimensions.length > 0 && (
                    <table className="w-full text-sm">
                        <thead>
                            <tr className="text-[#9ca3af] border-b border-[rgba(255,255,255,0.06)]">
                                <th className="text-left py-2 font-medium">Dimension</th>
                                <th className="text-left py-2 font-medium">Preference</th>
                                <th className="text-left py-2 font-medium">Evidence</th>
                            </tr>
                        </thead>
                        <tbody>
                            {personality.mbti.dimensions.map((dim, idx) => (
                                <tr key={idx} className="border-b border-[rgba(255,255,255,0.03)]">
                                    <td className="py-2 text-[#f5f5f5]">{dim.dimension}</td>
                                    <td className="py-2 text-blue-300">{dim.preference}</td>
                                    <td className="py-2 text-[#9ca3af]">{dim.evidence}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                )}
                {personality.workStyle && (
                    <div className="mt-3 pt-3 border-t border-[rgba(255,255,255,0.06)]">
                        <span className="text-[#9ca3af] text-sm font-medium">Work Style: </span>
                        <span className="text-[#f5f5f5] text-sm">{personality.workStyle}</span>
                    </div>
                )}
            </div>

            {/* DISC Card */}
            <div className="bg-[rgba(255,255,255,0.02)] border border-[rgba(255,255,255,0.06)] rounded-lg p-4">
                <div className="flex items-center gap-3 mb-3 pb-2 border-b border-[rgba(255,255,255,0.06)]">
                    <BarChart3 size={18} className="text-orange-400" />
                    <h4 className="text-[#f5f5f5] font-medium">DISC Profile Assessment</h4>
                </div>
                <div className="flex flex-wrap gap-4 mb-4">
                    <div>
                        <span className="text-[#9ca3af] text-sm">Primary: </span>
                        <span className="text-orange-300 font-medium">{personality.disc.primary}</span>
                    </div>
                    <div>
                        <span className="text-[#9ca3af] text-sm">Secondary: </span>
                        <span className="text-orange-300 font-medium">{personality.disc.secondary}</span>
                    </div>
                </div>
                {personality.disc.styles.length > 0 && (
                    <table className="w-full text-sm">
                        <thead>
                            <tr className="text-[#9ca3af] border-b border-[rgba(255,255,255,0.06)]">
                                <th className="text-left py-2 font-medium">Style</th>
                                <th className="text-left py-2 font-medium">%</th>
                                <th className="text-left py-2 font-medium">Evidence</th>
                            </tr>
                        </thead>
                        <tbody>
                            {personality.disc.styles.map((style, idx) => (
                                <tr key={idx} className="border-b border-[rgba(255,255,255,0.03)]">
                                    <td className="py-2 text-[#f5f5f5]">{style.style}</td>
                                    <td className="py-2 text-orange-300">{style.percent}</td>
                                    <td className="py-2 text-[#9ca3af]">{style.evidence}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                )}
            </div>

            {/* Communication Playbook */}
            <div className="bg-[rgba(255,255,255,0.02)] border border-[rgba(255,255,255,0.06)] rounded-lg p-4">
                <div className="flex items-center gap-3 mb-3 pb-2 border-b border-[rgba(255,255,255,0.06)]">
                    <MessageSquare size={18} className="text-green-400" />
                    <h4 className="text-[#f5f5f5] font-medium">Communication Playbook</h4>
                </div>
                <div className="grid md:grid-cols-2 gap-4">
                    {personality.doList.length > 0 && (
                        <div>
                            <div className="flex items-center gap-2 mb-2">
                                <CheckCircle2 size={16} className="text-green-400" />
                                <span className="text-green-300 font-medium text-sm">DO: How to Engage</span>
                            </div>
                            <ul className="space-y-1">
                                {personality.doList.map((item, idx) => (
                                    <li key={idx} className="text-[#9ca3af] text-sm flex items-start gap-2">
                                        <span className="text-green-400 mt-1">•</span>
                                        <span>{item}</span>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    )}
                    {personality.dontList.length > 0 && (
                        <div>
                            <div className="flex items-center gap-2 mb-2">
                                <XCircle size={16} className="text-red-400" />
                                <span className="text-red-300 font-medium text-sm">DON'T: What to Avoid</span>
                            </div>
                            <ul className="space-y-1">
                                {personality.dontList.map((item, idx) => (
                                    <li key={idx} className="text-[#9ca3af] text-sm flex items-start gap-2">
                                        <span className="text-red-400 mt-1">•</span>
                                        <span>{item}</span>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    )}
                </div>
                {personality.openingApproach && (
                    <div className="mt-4 pt-3 border-t border-[rgba(255,255,255,0.06)]">
                        <div className="flex items-center gap-2 mb-2">
                            <Target size={16} className="text-blue-400" />
                            <span className="text-blue-300 font-medium text-sm">Best Opening Approach</span>
                        </div>
                        <p className="text-[#9ca3af] text-sm">{personality.openingApproach}</p>
                    </div>
                )}
            </div>
        </div>
    );
};

const SummaryCard: React.FC<{ summary: string }> = ({ summary }) => {
    if (!summary) return null;
    return (
        <div className="bg-[rgba(255,255,255,0.02)] border border-[rgba(255,255,255,0.06)] rounded-lg p-4 mb-4">
            <div className="flex items-center gap-3 mb-3 pb-2 border-b border-[rgba(255,255,255,0.06)]">
                <FileText size={18} className="text-emerald-400" />
                <h4 className="text-[#f5f5f5] font-medium">Summary</h4>
            </div>
            <p className="text-[#9ca3af] text-sm leading-relaxed">{summary}</p>
        </div>
    );
};

const EmptyState: React.FC<{ message: string }> = ({ message }) => (
    <div className="flex flex-col items-center justify-center py-12 text-center">
        <div className="w-16 h-16 rounded-full bg-[rgba(255,255,255,0.05)] flex items-center justify-center mb-4">
            <FileText size={24} className="text-[#9ca3af]" />
        </div>
        <p className="text-[#9ca3af]">{message}</p>
    </div>
);

// =============================================================================
// MAIN COMPONENT
// =============================================================================

export default function ContactDetailPage() {
    const { id } = useParams<{ id: string }>();
    const navigate = useNavigate();
    const [contact, setContact] = useState<Contact | null>(null);
    const [loading, setLoading] = useState(true);
    const [enriching, setEnriching] = useState(false);
    const [activeTab, setActiveTab] = useState('overview');
    const [parsedData, setParsedData] = useState<ParsedSections | null>(null);

    useEffect(() => {
        fetchContact();
    }, [id]);

    useEffect(() => {
        if (contact?.enrichment_data) {
            const parsed = parseEnrichmentData(contact.enrichment_data);
            setParsedData(parsed);
        }
    }, [contact?.enrichment_data]);

    const fetchContact = async () => {
        try {
            const response = await fetch(`http://localhost:8000/api/contacts/${id}`);
            const data = await response.json();
            setContact(data);
        } catch (error) {
            console.error('Error fetching contact:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleEnrich = async () => {
        setEnriching(true);
        try {
            await fetch(`http://localhost:8000/api/contacts/${id}/enrich`, { method: 'POST' });
            // Poll for completion
            const pollInterval = setInterval(async () => {
                const response = await fetch(`http://localhost:8000/api/contacts/${id}/enrichment-status`);
                const data = await response.json();
                if (data.status === 'enriched' || data.status === 'error') {
                    clearInterval(pollInterval);
                    fetchContact();
                    setEnriching(false);
                }
            }, 2000);
        } catch (error) {
            console.error('Error enriching:', error);
            setEnriching(false);
        }
    };

    const handleReset = async () => {
        try {
            await fetch(`http://localhost:8000/api/contacts/${id}/reset-enrichment`, { method: 'POST' });
            fetchContact();
        } catch (error) {
            console.error('Error resetting:', error);
        }
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-[#0f1114] flex items-center justify-center">
                <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-500"></div>
            </div>
        );
    }

    if (!contact) {
        return (
            <div className="min-h-screen bg-[#0f1114] flex items-center justify-center">
                <p className="text-[#9ca3af]">Contact not found</p>
            </div>
        );
    }

    const tabs = [
        { id: 'overview', label: 'Overview', icon: <User size={16} /> },
        { id: 'professional', label: 'Professional', icon: <Briefcase size={16} />, color: 'text-blue-400' },
        { id: 'company', label: 'Company', icon: <Building2 size={16} /> },
        { id: 'painPoints', label: 'Pain Points', icon: <AlertTriangle size={16} />, color: 'text-red-400' },
        { id: 'salesIntel', label: 'Sales Intel', icon: <TrendingUp size={16} />, color: 'text-orange-400' },
        { id: 'outreach', label: 'Outreach', icon: <MessageSquare size={16} /> }
    ];

    const isEnriched = contact.enrichment_status === 'enriched';

    return (
        <div className="min-h-screen bg-[#0f1114] text-[#f5f5f5]">
            {/* Header */}
            <div className="bg-[#1a1d21] border-b border-[rgba(255,255,255,0.06)]">
                <div className="max-w-7xl mx-auto px-6 py-4">
                    <button
                        onClick={() => navigate('/')}
                        className="flex items-center gap-2 text-[#9ca3af] hover:text-[#f5f5f5] mb-4 transition-colors"
                    >
                        <ChevronLeft size={20} />
                        <span>Back to Contacts</span>
                    </button>

                    <div className="flex justify-between items-start">
                        <div className="flex items-center gap-4">
                            <div className="w-16 h-16 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white text-xl font-bold">
                                {contact.first_name[0]}{contact.last_name[0]}
                            </div>
                            <div>
                                <h1 className="text-2xl font-bold">{contact.first_name} {contact.last_name}</h1>
                                <p className="text-[#9ca3af]">{contact.title}</p>
                                <p className="text-blue-400">{contact.company}</p>
                            </div>
                        </div>
                        <div className="flex items-center gap-3">
                            {isEnriched ? (
                                <span className="px-3 py-1 bg-green-500/20 text-green-400 rounded-full text-sm flex items-center gap-2">
                                    <CheckCircle2 size={14} />
                                    Enriched
                                </span>
                            ) : (
                                <button
                                    onClick={handleEnrich}
                                    disabled={enriching}
                                    className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-sm font-medium flex items-center gap-2 disabled:opacity-50 transition-colors"
                                >
                                    <RefreshCw size={16} className={enriching ? 'animate-spin' : ''} />
                                    {enriching ? 'Enriching...' : 'Enrich'}
                                </button>
                            )}
                            {isEnriched && (
                                <button
                                    onClick={handleReset}
                                    className="px-3 py-2 bg-[rgba(255,255,255,0.05)] hover:bg-[rgba(255,255,255,0.1)] rounded-lg text-sm flex items-center gap-2 transition-colors"
                                >
                                    <RotateCcw size={16} />
                                    Reset
                                </button>
                            )}
                        </div>
                    </div>

                    {/* Contact Info Row */}
                    <div className="flex gap-6 mt-4 text-sm">
                        <div className="flex items-center gap-2 text-[#9ca3af]">
                            <Mail size={14} />
                            <span>{contact.email}</span>
                        </div>
                        {contact.phone && (
                            <div className="flex items-center gap-2 text-[#9ca3af]">
                                <Phone size={14} />
                                <span>{contact.phone}</span>
                            </div>
                        )}
                        {contact.last_enriched && (
                            <div className="flex items-center gap-2 text-[#9ca3af]">
                                <Clock size={14} />
                                <span>Last: {new Date(contact.last_enriched).toLocaleString()}</span>
                            </div>
                        )}
                    </div>
                </div>
            </div>

            {/* Tabs */}
            <div className="bg-[#1a1d21] border-b border-[rgba(255,255,255,0.06)]">
                <div className="max-w-7xl mx-auto px-6">
                    <div className="flex gap-1">
                        {tabs.map(tab => (
                            <button
                                key={tab.id}
                                onClick={() => setActiveTab(tab.id)}
                                className={`
                                    px-4 py-3 flex items-center gap-2 text-sm font-medium border-b-2 transition-colors
                                    ${activeTab === tab.id 
                                        ? 'border-blue-500 text-blue-400' 
                                        : 'border-transparent text-[#9ca3af] hover:text-[#f5f5f5]'
                                    }
                                `}
                            >
                                <span className={activeTab === tab.id ? (tab.color || 'text-blue-400') : ''}>
                                    {tab.icon}
                                </span>
                                {tab.label}
                                {tab.id !== 'overview' && tab.id !== 'outreach' && parsedData && (
                                    <span className="w-2 h-2 rounded-full bg-green-500" />
                                )}
                            </button>
                        ))}
                    </div>
                </div>
            </div>

            {/* Content */}
            <div className="max-w-7xl mx-auto px-6 py-6">
                {/* Overview Tab */}
                {activeTab === 'overview' && (
                    <div className="grid md:grid-cols-2 gap-6">
                        <div className="bg-[#1a1d21] rounded-lg p-6 border border-[rgba(255,255,255,0.06)]">
                            <h3 className="text-lg font-medium mb-4 flex items-center gap-2">
                                <User size={18} className="text-blue-400" />
                                Contact Information
                            </h3>
                            <div className="space-y-3">
                                <div className="flex justify-between">
                                    <span className="text-[#9ca3af]">Full Name</span>
                                    <span>{contact.first_name} {contact.last_name}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-[#9ca3af]">Title</span>
                                    <span>{contact.title}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-[#9ca3af]">Company</span>
                                    <span>{contact.company}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-[#9ca3af]">Email</span>
                                    <span className="text-blue-400">{contact.email}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-[#9ca3af]">Phone</span>
                                    <span>{contact.phone || '—'}</span>
                                </div>
                            </div>
                        </div>

                        {parsedData?.personality && (
                            <div className="bg-[#1a1d21] rounded-lg p-6 border border-[rgba(255,255,255,0.06)]">
                                <h3 className="text-lg font-medium mb-4 flex items-center gap-2">
                                    <Brain size={18} className="text-purple-400" />
                                    Personality Snapshot
                                </h3>
                                <div className="space-y-4">
                                    <div className="flex items-center gap-4">
                                        <div className="bg-purple-500/20 px-4 py-2 rounded-lg">
                                            <span className="text-purple-300 font-bold text-xl">{parsedData.personality.mbti.type}</span>
                                        </div>
                                        <div>
                                            <p className="text-[#9ca3af] text-sm">MBTI Type</p>
                                            <p className="text-[#f5f5f5] text-sm">{parsedData.personality.mbti.confidence} Confidence</p>
                                        </div>
                                    </div>
                                    <div className="flex items-center gap-4">
                                        <div className="bg-orange-500/20 px-4 py-2 rounded-lg">
                                            <span className="text-orange-300 font-bold">{parsedData.personality.disc.primary.split(' - ')[0]}</span>
                                        </div>
                                        <div>
                                            <p className="text-[#9ca3af] text-sm">DISC Primary</p>
                                            <p className="text-[#f5f5f5] text-sm">{parsedData.personality.disc.primary}</p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>
                )}

                {/* Professional Tab */}
                {activeTab === 'professional' && (
                    <div>
                        {parsedData && parsedData.professional.length > 0 ? (
                            <>
                                {parsedData.professional.map(card => (
                                    <SubsectionCard key={card.id} card={card} />
                                ))}
                                <SummaryCard summary={parsedData.summary} />
                                {parsedData.personality && <PersonalityCard personality={parsedData.personality} />}
                            </>
                        ) : (
                            <EmptyState message="No professional data available. Enrich this contact to see details." />
                        )}
                    </div>
                )}

                {/* Company Tab */}
                {activeTab === 'company' && (
                    <div>
                        {parsedData && parsedData.company.length > 0 ? (
                            parsedData.company.map(card => (
                                <SubsectionCard key={card.id} card={card} />
                            ))
                        ) : (
                            <EmptyState message="No company data available. Enrich this contact to see details." />
                        )}
                    </div>
                )}

                {/* Pain Points Tab */}
                {activeTab === 'painPoints' && (
                    <div>
                        {parsedData && parsedData.painPoints.length > 0 ? (
                            parsedData.painPoints.map(card => (
                                <SubsectionCard key={card.id} card={card} />
                            ))
                        ) : (
                            <EmptyState message="No pain points identified. Enrich this contact to analyze challenges." />
                        )}
                    </div>
                )}

                {/* Sales Intel Tab */}
                {activeTab === 'salesIntel' && (
                    <div>
                        {parsedData && parsedData.salesIntel.length > 0 ? (
                            parsedData.salesIntel.map(card => (
                                <SubsectionCard key={card.id} card={card} />
                            ))
                        ) : (
                            <EmptyState message="No sales intelligence available. Enrich this contact to see insights." />
                        )}
                    </div>
                )}

                {/* Outreach Tab */}
                {activeTab === 'outreach' && (
                    <EmptyState message="Outreach sequences coming soon. This feature will generate AI-powered email sequences based on the contact profile." />
                )}
            </div>
        </div>
    );
}

