import React, { useState, useEffect } from 'react';
import { ChevronLeft, Zap, User, Building2, AlertCircle, TrendingUp, Sparkles, CheckCircle2, Clock } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { useParams, useNavigate } from 'react-router-dom';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface Contact {
    id: number;
    name: string;
    title: string;
    company: string;
    email: string;
    phone: string;
    linkedin_url: string;
    enrichment_status: 'pending' | 'in_progress' | 'completed' | 'failed' | null;
    enriched_at: string | null;
    enrichment_data: string | null;  // ← FIXED: matches api.py
    mdcp_score: number;
}

interface ParsedProfile {
    overview: string;
    professional: string;
    company: string;
    painPoints: string;
    sales: string;
}

const ContactDetailPage: React.FC = () => {
    const { id } = useParams<{ id: string }>();
    const navigate = useNavigate();
    const [contact, setContact] = useState<Contact | null>(null);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState<'overview' | 'professional' | 'company' | 'pain' | 'sales'>('overview');
    const [parsedProfile, setParsedProfile] = useState<ParsedProfile | null>(null);
    const [enriching, setEnriching] = useState(false);

    const contactId = id || '1';

    useEffect(() => {
        fetchContact();
        const interval = setInterval(fetchContact, 3000);
        return () => clearInterval(interval);
    }, [contactId]);

    const fetchContact = async () => {
        try {
            const response = await fetch(`${API_URL}/api/contacts/${contactId}`);
            const data = await response.json();
            setContact(data);
            
            // ← FIXED: Use enrichment_data
            if (data.enrichment_data) {
                setParsedProfile(parseProfile(data.enrichment_data));
            }
            
            setLoading(false);
        } catch (error) {
            console.error('Error fetching contact:', error);
            setLoading(false);
        }
    };

    const parseProfile = (content: string): ParsedProfile => {
        // Extract sections using === SECTION === markers
        const personMatch = content.match(/=== PERSON RESEARCH:[^=]*===\s*([\s\S]*?)(?====|$)/);
        const companyMatch = content.match(/=== COMPANY RESEARCH:[^=]*===\s*([\s\S]*?)(?====|$)/);
        const salesMatch = content.match(/=== SALES INTELLIGENCE ===\s*([\s\S]*?)(?====|$)/);
        const personalityMatch = content.match(/=== PERSONALITY ANALYSIS ===\s*([\s\S]*?)(?====|$)/);

        // If new format found
        if (personMatch || companyMatch || salesMatch) {
            return {
                overview: (personMatch?.[1] || '') + '\n\n' + (personalityMatch?.[1] || ''),
                professional: personalityMatch?.[1] || '',
                company: companyMatch?.[1] || '',
                painPoints: salesMatch?.[1]?.match(/pain point|challenge/i) ? salesMatch[1] : '',
                sales: salesMatch?.[1] || '',
            };
        }

        // Fallback: return full content in overview
        return {
            overview: content,
            professional: '',
            company: '',
            painPoints: '',
            sales: '',
        };
    };

    const triggerEnrichment = async () => {
        setEnriching(true);
        try {
            const response = await fetch(`${API_URL}/api/contacts/${contactId}/enrich`, {
                method: 'POST',
            });
            
            if (response.ok) {
                setContact(prev => prev ? { ...prev, enrichment_status: 'in_progress' } : null);
                
                // Poll for completion
                const pollInterval = setInterval(async () => {
                    const statusResponse = await fetch(`${API_URL}/api/contacts/${contactId}/enrichment-status`);
                    const statusData = await statusResponse.json();
                    
                    if (statusData.enrichment_status !== 'in_progress') {
                        clearInterval(pollInterval);
                        setEnriching(false);
                        fetchContact();
                    }
                }, 2000);
            }
        } catch (error) {
            console.error('Error triggering enrichment:', error);
            setEnriching(false);
        }
    };

    if (loading) {
        return (
            <div className="bg-[#0f1114] text-white min-h-screen flex items-center justify-center">
                <div className="text-center">
                    <Clock className="w-12 h-12 text-gray-600 mx-auto mb-4 animate-pulse" />
                    <p className="text-gray-400">Loading contact...</p>
                </div>
            </div>
        );
    }

    if (!contact) {
        return (
            <div className="bg-[#0f1114] text-white min-h-screen flex items-center justify-center">
                <p className="text-red-400">Contact not found</p>
            </div>
        );
    }

    const getStatusBadge = () => {
        const status = contact.enrichment_status || 'pending';
        const statusConfig: Record<string, { icon: any; color: string; bg: string }> = {
            pending: { icon: Clock, color: 'text-gray-400', bg: 'bg-gray-900' },
            in_progress: { icon: Zap, color: 'text-blue-400', bg: 'bg-blue-950' },
            completed: { icon: CheckCircle2, color: 'text-green-400', bg: 'bg-green-950' },
            failed: { icon: AlertCircle, color: 'text-red-400', bg: 'bg-red-950' },
        };
        
        const config = statusConfig[status] || statusConfig.pending;
        const Icon = config.icon;
        
        return (
            <div className={`${config.bg} px-3 py-1 rounded-full flex items-center gap-2 w-fit`}>
                <Icon className={`w-4 h-4 ${config.color}`} />
                <span className={`text-sm font-medium ${config.color} capitalize`}>
                    {status === 'in_progress' ? 'Enriching...' : status}
                </span>
            </div>
        );
    };

    const hasEnrichment = contact.enrichment_status === 'completed' && contact.enrichment_data;

    return (
        <div className="bg-[#0f1114] text-white min-h-screen">
            {/* HEADER */}
            <div className="bg-[#1a1d21] border-b border-gray-800 px-6 py-4">
                <div className="flex items-center justify-between max-w-7xl mx-auto">
                    <div className="flex items-center gap-4">
                        <button onClick={() => navigate(-1)} className="hover:bg-gray-800 p-2 rounded transition">
                            <ChevronLeft className="w-5 h-5" />
                        </button>
                        <div>
                            <h1 className="text-2xl font-bold text-white">{contact.name}</h1>
                            <p className="text-gray-400 text-sm">
                                {contact.title} at {contact.company}
                            </p>
                        </div>
                    </div>
                    <div className="flex items-center gap-4">
                        {getStatusBadge()}
                        {!hasEnrichment && (
                            <button
                                onClick={triggerEnrichment}
                                disabled={enriching || contact.enrichment_status === 'in_progress'}
                                className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white px-4 py-2 rounded-lg font-medium flex items-center gap-2 transition"
                            >
                                <Sparkles className="w-4 h-4" />
                                {enriching || contact.enrichment_status === 'in_progress' ? 'Enriching...' : 'Enrich Now'}
                            </button>
                        )}
                    </div>
                </div>
            </div>

            {/* CONTACT INFO CARDS */}
            <div className="bg-[#0f1114] px-6 py-6">
                <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div className="bg-[#1a1d21] rounded-lg p-4 border border-gray-800">
                        <p className="text-gray-500 text-xs font-semibold uppercase mb-1">Email</p>
                        <a href={`mailto:${contact.email}`} className="text-blue-400 hover:underline text-sm">
                            {contact.email || '—'}
                        </a>
                    </div>
                    <div className="bg-[#1a1d21] rounded-lg p-4 border border-gray-800">
                        <p className="text-gray-500 text-xs font-semibold uppercase mb-1">Phone</p>
                        <a href={`tel:${contact.phone}`} className="text-blue-400 hover:underline text-sm">
                            {contact.phone || '—'}
                        </a>
                    </div>
                    <div className="bg-[#1a1d21] rounded-lg p-4 border border-gray-800">
                        <p className="text-gray-500 text-xs font-semibold uppercase mb-1">LinkedIn</p>
                        {contact.linkedin_url ? (
                            <a href={contact.linkedin_url} target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:underline text-sm">
                                View Profile →
                            </a>
                        ) : (
                            <span className="text-gray-500 text-sm">—</span>
                        )}
                    </div>
                    <div className="bg-[#1a1d21] rounded-lg p-4 border border-gray-800">
                        <p className="text-gray-500 text-xs font-semibold uppercase mb-1">MDCP Score</p>
                        <p className="text-xl font-bold text-orange-400">{contact.mdcp_score || '—'}</p>
                    </div>
                </div>
            </div>

            {/* ENRICHMENT STATUS / CONTENT */}
            {contact.enrichment_status === 'in_progress' && (
                <div className="flex items-center justify-center py-16">
                    <div className="text-center">
                        <Zap className="w-12 h-12 text-blue-400 mx-auto mb-4 animate-bounce" />
                        <p className="text-blue-400 font-semibold">Enriching profile...</p>
                        <p className="text-gray-500 text-sm mt-2">This usually takes 30-60 seconds</p>
                    </div>
                </div>
            )}

            {contact.enrichment_status === 'failed' && (
                <div className="flex items-center justify-center py-16">
                    <div className="text-center">
                        <AlertCircle className="w-12 h-12 text-red-400 mx-auto mb-4" />
                        <p className="text-red-400 font-semibold">Enrichment failed</p>
                        <button onClick={triggerEnrichment} className="text-blue-400 hover:underline text-sm mt-2">
                            Try again
                        </button>
                    </div>
                </div>
            )}

            {!hasEnrichment && contact.enrichment_status !== 'in_progress' && contact.enrichment_status !== 'failed' && (
                <div className="flex items-center justify-center py-16">
                    <div className="text-center">
                        <Sparkles className="w-12 h-12 text-gray-600 mx-auto mb-4" />
                        <p className="text-gray-400">No enrichment data yet</p>
                        <p className="text-gray-500 text-sm mt-2">Click "Enrich Now" to generate insights</p>
                    </div>
                </div>
            )}

            {/* TAB NAVIGATION - Only show when enriched */}
            {hasEnrichment && parsedProfile && (
                <>
                    <div className="bg-[#0f1114] px-6 border-b border-gray-800">
                        <div className="max-w-7xl mx-auto flex gap-8 overflow-x-auto">
                            {[
                                { id: 'overview', label: 'Overview', icon: User },
                                { id: 'professional', label: 'Professional Style', icon: Sparkles },
                                { id: 'company', label: 'Company', icon: Building2 },
                                { id: 'pain', label: 'Pain Points', icon: AlertCircle },
                                { id: 'sales', label: 'Sales Intel', icon: TrendingUp },
                            ].map((tab) => {
                                const Icon = tab.icon;
                                return (
                                    <button
                                        key={tab.id}
                                        onClick={() => setActiveTab(tab.id as any)}
                                        className={`py-4 px-1 border-b-2 font-medium transition flex items-center gap-2 whitespace-nowrap ${
                                            activeTab === tab.id
                                                ? 'border-blue-500 text-white'
                                                : 'border-transparent text-gray-400 hover:text-gray-300'
                                        }`}
                                    >
                                        <Icon className="w-4 h-4" />
                                        {tab.label}
                                    </button>
                                );
                            })}
                        </div>
                    </div>

                    {/* TAB CONTENT */}
                    <div className="bg-[#0f1114] px-6 py-8">
                        <div className="max-w-4xl mx-auto prose prose-invert max-w-none">
                            <ReactMarkdown
                                remarkPlugins={[remarkGfm]}
                                components={{
                                    h1: ({ node, ...props }) => (
                                        <h1 className="text-3xl font-bold text-white mt-6 mb-4" {...props} />
                                    ),
                                    h2: ({ node, ...props }) => (
                                        <h2 className="text-2xl font-bold text-blue-400 mt-6 mb-3 border-l-4 border-blue-500 pl-4" {...props} />
                                    ),
                                    h3: ({ node, ...props }) => (
                                        <h3 className="text-xl font-semibold text-gray-100 mt-4 mb-2" {...props} />
                                    ),
                                    p: ({ node, ...props }) => (
                                        <p className="text-gray-300 leading-relaxed mb-3" {...props} />
                                    ),
                                    table: ({ node, ...props }) => (
                                        <div className="bg-[#1a1d21] rounded-lg border border-gray-800 overflow-hidden my-4">
                                            <table className="w-full" {...props} />
                                        </div>
                                    ),
                                    thead: ({ node, ...props }) => (
                                        <thead className="bg-gray-900 border-b border-gray-800" {...props} />
                                    ),
                                    th: ({ node, ...props }) => (
                                        <th className="px-4 py-3 text-left text-blue-400 font-semibold text-sm" {...props} />
                                    ),
                                    tr: ({ node, ...props }) => (
                                        <tr className="border-b border-gray-800 hover:bg-gray-900/50 transition" {...props} />
                                    ),
                                    td: ({ node, ...props }) => (
                                        <td className="px-4 py-3 text-gray-300 text-sm" {...props} />
                                    ),
                                    ul: ({ node, ...props }) => (
                                        <ul className="list-disc list-inside text-gray-300 space-y-2 my-3" {...props} />
                                    ),
                                    li: ({ node, ...props }) => (
                                        <li className="text-gray-300" {...props} />
                                    ),
                                    strong: ({ node, ...props }) => (
                                        <strong className="font-semibold text-white" {...props} />
                                    ),
                                    a: ({ node, ...props }) => (
                                        <a className="text-blue-400 hover:underline" {...props} />
                                    ),
                                }}
                            >
                                {activeTab === 'overview' && parsedProfile.overview}
                                {activeTab === 'professional' && (parsedProfile.professional || 'No personality data available.')}
                                {activeTab === 'company' && (parsedProfile.company || 'No company data available.')}
                                {activeTab === 'pain' && (parsedProfile.painPoints || parsedProfile.sales || 'No pain points data available.')}
                                {activeTab === 'sales' && (parsedProfile.sales || 'No sales intelligence available.')}
                            </ReactMarkdown>
                        </div>
                    </div>
                </>
            )}
        </div>
    );
};

export default ContactDetailPage;
