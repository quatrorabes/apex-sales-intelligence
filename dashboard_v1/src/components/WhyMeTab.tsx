import { useState, useEffect } from 'react';
import { 
    Sparkles, Target, Lightbulb, MessageSquare, Shield, 
    Users, Clock, RefreshCw, Loader2, Copy, Check,
    Mail, Linkedin, Phone, AlertCircle
} from 'lucide-react';

const API_URL = 'https://apex-backend-production-production.up.railway.app';

interface WhyMeTabProps {
    contactId: number;
    contactName: string;
}

interface WhyMeData {
    hook?: string;
    proof_points?: string[];
    why_now?: string;
    suggested_opening?: string;
    talking_points?: string[];
    objection_handlers?: { objection: string; response: string }[];
    rapport_builders?: string[];
    best_channel?: string;
    generated_at?: string;
    fallback?: boolean;
}

export default function WhyMeTab({ contactId, contactName }: WhyMeTabProps) {
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
                setData(json);
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
            const res = await fetch(`${API_URL}/api/contacts/${contactId}/why-me`, {
                method: 'POST'
            });
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
            title="Copy to clipboard"
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
                        <>
                            <Loader2 size={18} className="animate-spin" /> Generating...
                        </>
                    ) : (
                        <>
                            <Sparkles size={18} /> Generate Why Me
                        </>
                    )}
                </button>
                {error && (
                    <p className="text-red-400 mt-4 flex items-center justify-center gap-2">
                        <AlertCircle size={16} /> {error}
                    </p>
                )}
            </div>
        );
    }

    const channelIcons: Record<string, React.ReactNode> = {
        email: <Mail size={16} />,
        linkedin: <Linkedin size={16} />,
        phone: <Phone size={16} />,
    };

    return (
        <div className="space-y-6">
            {/* Regenerate Button */}
            <div className="flex justify-between items-center">
                <div className="text-sm text-gray-500">
                    {data.generated_at && `Generated ${new Date(data.generated_at).toLocaleDateString()}`}
                    {data.fallback && <span className="text-yellow-500 ml-2">(Fallback - no OpenAI)</span>}
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
                        <h3 className="font-semibold">Suggested Opening Message</h3>
                        {data.best_channel && (
                            <span className="bg-green-900/30 text-green-300 px-2 py-0.5 rounded text-xs flex items-center gap-1">
                                {channelIcons[data.best_channel]} {data.best_channel}
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
                                    → {typeof obj === 'string' ? 'Prepare a thoughtful response' : obj.response}
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
}
