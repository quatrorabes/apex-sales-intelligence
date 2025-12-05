import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
    Sparkles, Loader2, Send, X, Zap, Users, Target,
    TrendingUp, Mail, Phone, Building2, Brain, Wand2
} from 'lucide-react';

const API_URL = 'http://localhost:8000';

interface CommandResult {
    type: 'contacts' | 'action' | 'insight' | 'navigation';
    message: string;
    data?: any[];
    action?: string;
}

const EXAMPLE_COMMANDS = [
    "Show me all CEOs",
    "Find high priority contacts at banks",
    "Who should I call today?",
    "Draft email to my top 3 leads",
    "What's my pipeline health?",
    "Find contacts I haven't reached out to",
    "Show decision makers in real estate",
    "Who has the highest match score?",
];

export default function CommandBar({ isOpen, onClose }: { isOpen: boolean; onClose: () => void }) {
    const [query, setQuery] = useState('');
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState<CommandResult | null>(null);
    const [history, setHistory] = useState<string[]>([]);
    const inputRef = useRef<HTMLInputElement>(null);
    const navigate = useNavigate();

    useEffect(() => {
        if (isOpen) {
            setQuery('');
            setResult(null);
            setTimeout(() => inputRef.current?.focus(), 100);
        }
    }, [isOpen]);

    const executeCommand = async () => {
        if (!query.trim()) return;
        
        setLoading(true);
        setHistory(prev => [query, ...prev.slice(0, 9)]);
        
        try {
            const res = await fetch(`${API_URL}/api/ai/command`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ command: query })
            });
            const data = await res.json();
            setResult(data);
            
            // Auto-navigate if it's a navigation command
            if (data.type === 'navigation' && data.action) {
                setTimeout(() => {
                    navigate(data.action);
                    onClose();
                }, 1000);
            }
        } catch (e) {
            setResult({
                type: 'insight',
                message: 'Sorry, I had trouble understanding that. Try rephrasing.',
            });
        } finally {
            setLoading(false);
        }
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            executeCommand();
        } else if (e.key === 'Escape') {
            onClose();
        }
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-black/80 flex items-start justify-center pt-[10vh] z-50" onClick={onClose}>
            <div 
                className="bg-gradient-to-b from-[#1e2228] to-[#15171a] rounded-2xl border border-purple-500/30 w-full max-w-2xl mx-4 overflow-hidden shadow-2xl shadow-purple-500/20"
                onClick={e => e.stopPropagation()}
            >
                {/* Header */}
                <div className="px-5 py-4 border-b border-gray-800 flex items-center gap-3">
                    <div className="p-2 bg-purple-500/20 rounded-lg">
                        <Wand2 size={20} className="text-purple-400" />
                    </div>
                    <div>
                        <h2 className="font-semibold text-white">AI Command Bar</h2>
                        <p className="text-gray-500 text-sm">Ask anything about your pipeline</p>
                    </div>
                    <button onClick={onClose} className="ml-auto text-gray-500 hover:text-white">
                        <X size={20} />
                    </button>
                </div>

                {/* Input */}
                <div className="p-4 border-b border-gray-800">
                    <div className="flex items-center gap-3 bg-[#0f1114] rounded-xl px-4 py-3 border border-gray-700 focus-within:border-purple-500">
                        <Sparkles size={20} className="text-purple-400" />
                        <input
                            ref={inputRef}
                            type="text"
                            value={query}
                            onChange={e => setQuery(e.target.value)}
                            onKeyDown={handleKeyDown}
                            placeholder="Ask me anything... (e.g., 'Show CEOs in tech companies')"
                            className="flex-1 bg-transparent text-white placeholder-gray-500 outline-none"
                        />
                        <button
                            onClick={executeCommand}
                            disabled={loading || !query.trim()}
                            className="p-2 bg-purple-600 hover:bg-purple-700 disabled:opacity-50 rounded-lg transition"
                        >
                            {loading ? <Loader2 size={18} className="animate-spin" /> : <Send size={18} />}
                        </button>
                    </div>
                </div>

                {/* Results */}
                <div className="max-h-[400px] overflow-y-auto">
                    {result ? (
                        <div className="p-4">
                            {/* Message */}
                            <div className="flex items-start gap-3 mb-4">
                                <div className="p-2 bg-purple-500/20 rounded-lg">
                                    <Brain size={18} className="text-purple-400" />
                                </div>
                                <div className="flex-1">
                                    <p className="text-white">{result.message}</p>
                                </div>
                            </div>

                            {/* Contact Results */}
                            {result.type === 'contacts' && result.data && (
                                <div className="space-y-2 mt-4">
                                    {result.data.slice(0, 5).map((c: any) => (
                                        <button
                                            key={c.id}
                                            onClick={() => { navigate(`/contacts/${c.id}`); onClose(); }}
                                            className="w-full flex items-center gap-3 p-3 bg-[#0f1114] hover:bg-gray-800 rounded-lg text-left transition"
                                        >
                                            <div className="w-10 h-10 bg-blue-500/20 rounded-full flex items-center justify-center text-blue-400">
                                                {(c.name || c.first_name || '?')[0].toUpperCase()}
                                            </div>
                                            <div className="flex-1 min-w-0">
                                                <p className="font-medium text-white truncate">
                                                    {c.name || `${c.first_name} ${c.last_name}`}
                                                </p>
                                                <p className="text-gray-500 text-sm truncate">{c.title} at {c.company}</p>
                                            </div>
                                            <div className="text-right">
                                                <span className="text-xl font-bold text-white">{Math.round(c.match_score || 0)}</span>
                                            </div>
                                        </button>
                                    ))}
                                    {result.data.length > 5 && (
                                        <p className="text-gray-500 text-sm text-center py-2">
                                            +{result.data.length - 5} more results
                                        </p>
                                    )}
                                </div>
                            )}

                            {/* Insight Results */}
                            {result.type === 'insight' && result.data && (
                                <div className="grid grid-cols-3 gap-3 mt-4">
                                    {Object.entries(result.data).map(([key, value]: [string, any]) => (
                                        <div key={key} className="bg-[#0f1114] rounded-lg p-4 text-center">
                                            <p className="text-2xl font-bold text-white">{value}</p>
                                            <p className="text-gray-500 text-sm capitalize">{key.replace(/_/g, ' ')}</p>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    ) : (
                        <div className="p-4">
                            <p className="text-gray-500 text-sm mb-3">Try these commands:</p>
                            <div className="flex flex-wrap gap-2">
                                {EXAMPLE_COMMANDS.map((cmd, i) => (
                                    <button
                                        key={i}
                                        onClick={() => setQuery(cmd)}
                                        className="px-3 py-1.5 bg-[#0f1114] hover:bg-gray-800 border border-gray-700 rounded-full text-sm text-gray-400 hover:text-white transition"
                                    >
                                        {cmd}
                                    </button>
                                ))}
                            </div>
                        </div>
                    )}
                </div>

                {/* Footer */}
                <div className="px-4 py-3 bg-[#0f1114] border-t border-gray-800 flex items-center justify-between text-xs text-gray-500">
                    <span>Powered by AI</span>
                    <div className="flex items-center gap-4">
                        <span><kbd className="px-1.5 py-0.5 bg-gray-800 rounded">Enter</kbd> Execute</span>
                        <span><kbd className="px-1.5 py-0.5 bg-gray-800 rounded">⌘J</kbd> Open</span>
                    </div>
                </div>
            </div>
        </div>
    );
}
