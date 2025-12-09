import { useState } from 'react';
import { 
    FileText, Loader2, Download, Copy, Check, Calendar,
    Target, AlertTriangle, Lightbulb, MessageSquare, Shield,
    Clock, Building2, User, Sparkles, Printer
} from 'lucide-react';

const API_URL = 'https://apex-backend-i7b0.onrender.com';

interface MeetingPrepData {
    contact_summary: string;
    company_overview: string;
    talking_points: string[];
    questions_to_ask: string[];
    potential_objections: { objection: string; response: string }[];
    ice_breakers: string[];
    goal: string;
    next_steps: string[];
    generated_at: string;
}

export default function MeetingPrep({ contactId, contactName }: { contactId: number; contactName: string }) {
    const [data, setData] = useState<MeetingPrepData | null>(null);
    const [loading, setLoading] = useState(false);
    const [copied, setCopied] = useState(false);
    const [meetingType, setMeetingType] = useState<'discovery' | 'demo' | 'closing'>('discovery');

    const generatePrep = async () => {
        setLoading(true);
        try {
            const res = await fetch(`${API_URL}/api/contacts/${contactId}/meeting-prep`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ meeting_type: meetingType })
            });
            const json = await res.json();
            setData(json.prep);
        } catch (e) {
            console.error('Failed to generate prep');
        } finally {
            setLoading(false);
        }
    };

    const copyAll = () => {
        if (!data) return;
        const text = `
MEETING PREP: ${contactName}
Generated: ${new Date(data.generated_at).toLocaleString()}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📌 GOAL
${data.goal}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👤 CONTACT SUMMARY
${data.contact_summary}

🏢 COMPANY OVERVIEW
${data.company_overview}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💬 TALKING POINTS
${data.talking_points.map((p, i) => `${i + 1}. ${p}`).join('\n')}

❓ QUESTIONS TO ASK
${data.questions_to_ask.map((q, i) => `${i + 1}. ${q}`).join('\n')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🛡️ OBJECTION HANDLERS
${data.potential_objections.map(o => `"${o.objection}"\n→ ${o.response}`).join('\n\n')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 NEXT STEPS
${data.next_steps.map((s, i) => `${i + 1}. ${s}`).join('\n')}
        `.trim();
        
        navigator.clipboard.writeText(text);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    const printPrep = () => {
        window.print();
    };

    if (!data) {
        return (
            <div className="text-center py-12">
                <Calendar className="w-16 h-16 text-gray-700 mx-auto mb-4" />
                <h3 className="text-xl text-white mb-2">Meeting Prep Generator</h3>
                <p className="text-gray-400 mb-6 max-w-md mx-auto">
                    Generate a comprehensive meeting prep doc with talking points, questions, 
                    and objection handlers tailored to {contactName}.
                </p>
                
                <div className="flex items-center justify-center gap-2 mb-6">
                    <span className="text-gray-400 text-sm">Meeting type:</span>
                    {(['discovery', 'demo', 'closing'] as const).map(type => (
                        <button
                            key={type}
                            onClick={() => setMeetingType(type)}
                            className={`px-4 py-2 rounded-lg text-sm font-medium capitalize transition ${
                                meetingType === type 
                                    ? 'bg-purple-600 text-white' 
                                    : 'bg-gray-800 text-gray-400 hover:text-white'
                            }`}
                        >
                            {type}
                        </button>
                    ))}
                </div>
                
                <button
                    onClick={generatePrep}
                    disabled={loading}
                    className="bg-purple-600 hover:bg-purple-700 disabled:opacity-50 text-white px-8 py-3 rounded-xl font-medium inline-flex items-center gap-2"
                >
                    {loading ? (
                        <><Loader2 size={20} className="animate-spin" /> Generating...</>
                    ) : (
                        <><Sparkles size={20} /> Generate Prep Doc</>
                    )}
                </button>
            </div>
        );
    }

    return (
        <div className="space-y-6 print:space-y-4">
            {/* Header Actions */}
            <div className="flex items-center justify-between print:hidden">
                <div className="text-sm text-gray-500">
                    Generated {new Date(data.generated_at).toLocaleString()}
                </div>
                <div className="flex items-center gap-2">
                    <button
                        onClick={copyAll}
                        className="px-4 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg text-sm flex items-center gap-2"
                    >
                        {copied ? <Check size={16} className="text-green-400" /> : <Copy size={16} />}
                        {copied ? 'Copied!' : 'Copy All'}
                    </button>
                    <button
                        onClick={printPrep}
                        className="px-4 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg text-sm flex items-center gap-2"
                    >
                        <Printer size={16} /> Print
                    </button>
                    <button
                        onClick={() => setData(null)}
                        className="px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg text-sm flex items-center gap-2"
                    >
                        <Sparkles size={16} /> Regenerate
                    </button>
                </div>
            </div>

            {/* Goal */}
            <div className="bg-gradient-to-r from-purple-900/30 to-blue-900/30 rounded-xl border border-purple-500/30 p-5">
                <div className="flex items-center gap-2 text-purple-300 mb-2">
                    <Target size={18} />
                    <h3 className="font-semibold">Meeting Goal</h3>
                </div>
                <p className="text-white text-lg">{data.goal}</p>
            </div>

            <div className="grid md:grid-cols-2 gap-4">
                {/* Contact Summary */}
                <div className="bg-[#1e2228] rounded-xl border border-gray-800 p-5">
                    <div className="flex items-center gap-2 text-blue-400 mb-3">
                        <User size={18} />
                        <h3 className="font-semibold">Contact Summary</h3>
                    </div>
                    <p className="text-gray-300 text-sm leading-relaxed">{data.contact_summary}</p>
                </div>

                {/* Company Overview */}
                <div className="bg-[#1e2228] rounded-xl border border-gray-800 p-5">
                    <div className="flex items-center gap-2 text-green-400 mb-3">
                        <Building2 size={18} />
                        <h3 className="font-semibold">Company Overview</h3>
                    </div>
                    <p className="text-gray-300 text-sm leading-relaxed">{data.company_overview}</p>
                </div>
            </div>

            {/* Talking Points */}
            <div className="bg-[#1e2228] rounded-xl border border-gray-800 p-5">
                <div className="flex items-center gap-2 text-yellow-400 mb-4">
                    <MessageSquare size={18} />
                    <h3 className="font-semibold">Talking Points</h3>
                </div>
                <div className="space-y-2">
                    {data.talking_points.map((point, i) => (
                        <div key={i} className="flex items-start gap-3 p-3 bg-[#0f1114] rounded-lg">
                            <span className="w-6 h-6 bg-yellow-500/20 text-yellow-400 rounded-full flex items-center justify-center text-sm font-bold">
                                {i + 1}
                            </span>
                            <p className="text-gray-300 text-sm">{point}</p>
                        </div>
                    ))}
                </div>
            </div>

            {/* Questions to Ask */}
            <div className="bg-[#1e2228] rounded-xl border border-gray-800 p-5">
                <div className="flex items-center gap-2 text-cyan-400 mb-4">
                    <Lightbulb size={18} />
                    <h3 className="font-semibold">Questions to Ask</h3>
                </div>
                <div className="grid md:grid-cols-2 gap-2">
                    {data.questions_to_ask.map((q, i) => (
                        <div key={i} className="p-3 bg-[#0f1114] rounded-lg text-gray-300 text-sm">
                            {q}
                        </div>
                    ))}
                </div>
            </div>

            {/* Objection Handlers */}
            <div className="bg-[#1e2228] rounded-xl border border-gray-800 p-5">
                <div className="flex items-center gap-2 text-red-400 mb-4">
                    <Shield size={18} />
                    <h3 className="font-semibold">Objection Handlers</h3>
                </div>
                <div className="space-y-3">
                    {data.potential_objections.map((obj, i) => (
                        <div key={i} className="p-4 bg-[#0f1114] rounded-lg border border-gray-800">
                            <p className="text-red-300 text-sm font-medium mb-2">"{obj.objection}"</p>
                            <p className="text-gray-300 text-sm">→ {obj.response}</p>
                        </div>
                    ))}
                </div>
            </div>

            {/* Ice Breakers */}
            <div className="bg-[#1e2228] rounded-xl border border-gray-800 p-5">
                <div className="flex items-center gap-2 text-pink-400 mb-4">
                    <Sparkles size={18} />
                    <h3 className="font-semibold">Ice Breakers</h3>
                </div>
                <div className="flex flex-wrap gap-2">
                    {data.ice_breakers.map((ice, i) => (
                        <span key={i} className="px-3 py-2 bg-pink-500/10 text-pink-300 rounded-lg text-sm">
                            {ice}
                        </span>
                    ))}
                </div>
            </div>

            {/* Next Steps */}
            <div className="bg-[#1e2228] rounded-xl border border-gray-800 p-5">
                <div className="flex items-center gap-2 text-green-400 mb-4">
                    <Target size={18} />
                    <h3 className="font-semibold">Suggested Next Steps</h3>
                </div>
                <div className="space-y-2">
                    {data.next_steps.map((step, i) => (
                        <div key={i} className="flex items-center gap-3 text-gray-300 text-sm">
                            <div className="w-6 h-6 border-2 border-green-500/50 rounded-full flex items-center justify-center">
                                <span className="text-green-400 text-xs">{i + 1}</span>
                            </div>
                            {step}
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
