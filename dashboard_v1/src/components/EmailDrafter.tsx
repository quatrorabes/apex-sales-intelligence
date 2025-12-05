import { useState } from 'react';
import { 
    Mail, Send, Copy, Check, Loader2, RefreshCw, 
    ChevronDown, Sparkles, Clock, MessageSquare
} from 'lucide-react';

const API_URL = 'http://localhost:8000';

interface EmailDrafterProps {
    contactId: number;
    contactName: string;
    contactEmail?: string;
}

interface EmailDraft {
    subject: string;
    body: string;
    cta_type: string;
    template: string;
    generated_at: string;
}

interface EmailSequence {
    subject: string;
    body: string;
    sequence_position: number;
    send_delay_days: number;
}

const TEMPLATES = [
    { id: 'intro', name: 'Introduction', desc: 'First outreach' },
    { id: 'follow_up', name: 'Follow Up', desc: 'After no response' },
    { id: 'value_add', name: 'Value Add', desc: 'Share something helpful' },
    { id: 'meeting_request', name: 'Meeting Request', desc: 'Direct ask' },
    { id: 'referral', name: 'Referral Intro', desc: 'Via mutual connection' },
];

export default function EmailDrafter({ contactId, contactName, contactEmail }: EmailDrafterProps) {
    const [template, setTemplate] = useState('intro');
    const [customContext, setCustomContext] = useState('');
    const [draft, setDraft] = useState<EmailDraft | null>(null);
    const [sequence, setSequence] = useState<EmailSequence[] | null>(null);
    const [loading, setLoading] = useState(false);
    const [copied, setCopied] = useState<string | null>(null);
    const [mode, setMode] = useState<'single' | 'sequence'>('single');
    const [showTemplates, setShowTemplates] = useState(false);

    const generateEmail = async () => {
        setLoading(true);
        setSequence(null);
        try {
            const res = await fetch(`${API_URL}/api/contacts/${contactId}/generate-email`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ template, context: customContext })
            });
            const data = await res.json();
            if (data.success) {
                setDraft(data.email);
            }
        } catch (e) {
            console.error('Generate error:', e);
        } finally {
            setLoading(false);
        }
    };

    const generateSequence = async () => {
        setLoading(true);
        setDraft(null);
        try {
            const res = await fetch(`${API_URL}/api/contacts/${contactId}/generate-sequence`, {
                method: 'POST'
            });
            const data = await res.json();
            if (data.success) {
                setSequence(data.sequence);
            }
        } catch (e) {
            console.error('Sequence error:', e);
        } finally {
            setLoading(false);
        }
    };

    const copyToClipboard = (text: string, id: string) => {
        navigator.clipboard.writeText(text);
        setCopied(id);
        setTimeout(() => setCopied(null), 2000);
    };

    const openInGmail = (subject: string, body: string) => {
        const gmailUrl = `https://mail.google.com/mail/?view=cm&fs=1&to=${contactEmail || ''}&su=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
        window.open(gmailUrl, '_blank');
    };

    const CopyBtn = ({ text, id }: { text: string; id: string }) => (
        <button
            onClick={() => copyToClipboard(text, id)}
            className="p-2 hover:bg-gray-700 rounded transition"
        >
            {copied === id ? <Check size={16} className="text-green-400" /> : <Copy size={16} className="text-gray-500" />}
        </button>
    );

    return (
        <div className="space-y-6">
            {/* Mode Toggle */}
            <div className="flex items-center gap-4">
                <div className="bg-[#0f1114] rounded-lg p-1 flex">
                    <button
                        onClick={() => setMode('single')}
                        className={`px-4 py-2 rounded-md text-sm font-medium transition ${
                            mode === 'single' ? 'bg-purple-600 text-white' : 'text-gray-400 hover:text-white'
                        }`}
                    >
                        <Mail size={16} className="inline mr-2" /> Single Email
                    </button>
                    <button
                        onClick={() => setMode('sequence')}
                        className={`px-4 py-2 rounded-md text-sm font-medium transition ${
                            mode === 'sequence' ? 'bg-purple-600 text-white' : 'text-gray-400 hover:text-white'
                        }`}
                    >
                        <MessageSquare size={16} className="inline mr-2" /> 3-Email Sequence
                    </button>
                </div>
            </div>

            {/* Single Email Options */}
            {mode === 'single' && (
                <div className="bg-[#1e2228] rounded-xl border border-gray-800 p-5">
                    <div className="flex items-center justify-between mb-4">
                        <h3 className="font-semibold text-white">Email Template</h3>
                        <div className="relative">
                            <button
                                onClick={() => setShowTemplates(!showTemplates)}
                                className="px-4 py-2 bg-[#0f1114] border border-gray-700 rounded-lg flex items-center gap-2 text-sm"
                            >
                                {TEMPLATES.find(t => t.id === template)?.name}
                                <ChevronDown size={16} />
                            </button>
                            {showTemplates && (
                                <div className="absolute right-0 mt-2 w-64 bg-[#1e2228] border border-gray-700 rounded-lg shadow-xl z-10">
                                    {TEMPLATES.map(t => (
                                        <button
                                            key={t.id}
                                            onClick={() => { setTemplate(t.id); setShowTemplates(false); }}
                                            className={`w-full px-4 py-3 text-left hover:bg-gray-800 first:rounded-t-lg last:rounded-b-lg ${
                                                template === t.id ? 'bg-purple-900/30' : ''
                                            }`}
                                        >
                                            <p className="text-white font-medium">{t.name}</p>
                                            <p className="text-gray-500 text-sm">{t.desc}</p>
                                        </button>
                                    ))}
                                </div>
                            )}
                        </div>
                    </div>

                    <div className="mb-4">
                        <label className="block text-gray-400 text-sm mb-2">Additional Context (optional)</label>
                        <textarea
                            value={customContext}
                            onChange={e => setCustomContext(e.target.value)}
                            placeholder="E.g., 'We met at ICSC last month' or 'Mention their recent acquisition'"
                            className="w-full bg-[#0f1114] border border-gray-700 rounded-lg px-4 py-2 text-white h-20 text-sm"
                        />
                    </div>

                    <button
                        onClick={generateEmail}
                        disabled={loading}
                        className="w-full bg-purple-600 hover:bg-purple-700 disabled:opacity-50 text-white py-3 rounded-lg font-medium flex items-center justify-center gap-2"
                    >
                        {loading ? (
                            <><Loader2 size={18} className="animate-spin" /> Generating...</>
                        ) : (
                            <><Sparkles size={18} /> Generate Email</>
                        )}
                    </button>
                </div>
            )}

            {/* Sequence Generator */}
            {mode === 'sequence' && (
                <div className="bg-[#1e2228] rounded-xl border border-gray-800 p-5">
                    <p className="text-gray-400 text-sm mb-4">
                        Generate a 3-email sequence: Introduction → Follow Up (Day 3) → Value Add (Day 7)
                    </p>
                    <button
                        onClick={generateSequence}
                        disabled={loading}
                        className="w-full bg-purple-600 hover:bg-purple-700 disabled:opacity-50 text-white py-3 rounded-lg font-medium flex items-center justify-center gap-2"
                    >
                        {loading ? (
                            <><Loader2 size={18} className="animate-spin" /> Generating Sequence...</>
                        ) : (
                            <><Sparkles size={18} /> Generate 3-Email Sequence</>
                        )}
                    </button>
                </div>
            )}

            {/* Single Draft Display */}
            {draft && mode === 'single' && (
                <div className="bg-[#1e2228] rounded-xl border border-gray-800 overflow-hidden">
                    <div className="px-5 py-3 border-b border-gray-700 flex items-center justify-between">
                        <span className="text-gray-400 text-sm">Generated Email</span>
                        <div className="flex items-center gap-2">
                            <button
                                onClick={generateEmail}
                                className="p-2 hover:bg-gray-700 rounded text-gray-400 hover:text-white"
                            >
                                <RefreshCw size={16} />
                            </button>
                        </div>
                    </div>
                    
                    {/* Subject */}
                    <div className="px-5 py-3 border-b border-gray-700 flex items-center justify-between">
                        <div>
                            <span className="text-gray-500 text-sm">Subject: </span>
                            <span className="text-white font-medium">{draft.subject}</span>
                        </div>
                        <CopyBtn text={draft.subject} id="subject" />
                    </div>

                    {/* Body */}
                    <div className="p-5">
                        <div className="flex items-start justify-between mb-2">
                            <span className="text-gray-500 text-sm">Body</span>
                            <CopyBtn text={draft.body} id="body" />
                        </div>
                        <div className="bg-[#0f1114] rounded-lg p-4 border border-gray-700">
                            <p className="text-gray-200 whitespace-pre-wrap text-sm">{draft.body}</p>
                        </div>
                    </div>

                    {/* Actions */}
                    <div className="px-5 py-4 bg-[#0f1114] border-t border-gray-700 flex items-center gap-3">
                        <button
                            onClick={() => copyToClipboard(`Subject: ${draft.subject}\n\n${draft.body}`, 'full')}
                            className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg text-sm flex items-center gap-2"
                        >
                            {copied === 'full' ? <Check size={16} /> : <Copy size={16} />}
                            Copy All
                        </button>
                        {contactEmail && (
                            <button
                                onClick={() => openInGmail(draft.subject, draft.body)}
                                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-sm flex items-center gap-2"
                            >
                                <Send size={16} /> Open in Gmail
                            </button>
                        )}
                    </div>
                </div>
            )}

            {/* Sequence Display */}
            {sequence && mode === 'sequence' && (
                <div className="space-y-4">
                    {sequence.map((email, i) => (
                        <div key={i} className="bg-[#1e2228] rounded-xl border border-gray-800 overflow-hidden">
                            <div className="px-5 py-3 border-b border-gray-700 flex items-center justify-between">
                                <div className="flex items-center gap-3">
                                    <span className="bg-purple-600 text-white w-6 h-6 rounded-full flex items-center justify-center text-sm font-bold">
                                        {email.sequence_position}
                                    </span>
                                    <span className="text-white font-medium">
                                        {email.sequence_position === 1 ? 'Introduction' : 
                                         email.sequence_position === 2 ? 'Follow Up' : 'Value Add'}
                                    </span>
                                    <span className="text-gray-500 text-sm flex items-center gap-1">
                                        <Clock size={12} />
                                        {email.send_delay_days === 0 ? 'Day 1' : `Day ${email.send_delay_days + 1}`}
                                    </span>
                                </div>
                                <CopyBtn text={`Subject: ${email.subject}\n\n${email.body}`} id={`seq-${i}`} />
                            </div>
                            <div className="px-5 py-3 border-b border-gray-700">
                                <span className="text-gray-500 text-sm">Subject: </span>
                                <span className="text-white">{email.subject}</span>
                            </div>
                            <div className="p-5">
                                <p className="text-gray-300 whitespace-pre-wrap text-sm">{email.body}</p>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
