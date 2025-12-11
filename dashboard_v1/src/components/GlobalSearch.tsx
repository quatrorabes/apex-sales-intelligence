import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
    Search, User, Building2, Command, ArrowRight,
    Zap, BarChart3, Phone, Sparkles, X, Loader2
} from 'lucide-react';

const API_URL = 'https://apex-backend-i7b0.onrender.com';

interface SearchResult {
    type: 'contact' | 'page';
    id?: number;
    name: string;
    subtitle?: string;
    path: string;
    icon?: React.ReactNode;
}

const PAGES: SearchResult[] = [
    { type: 'page', name: "Today's Board", path: '/board', icon: <Zap size={18} /> },
    { type: 'page', name: 'All Contacts', path: '/contacts', icon: <User size={18} /> },
    { type: 'page', name: 'Kanban View', path: '/contacts?view=kanban', icon: <Building2 size={18} /> },
    { type: 'page', name: 'Analytics', path: '/analytics', icon: <BarChart3 size={18} /> },
    { type: 'page', name: 'Smart Lists', path: '/smart-lists', icon: <Sparkles size={18} /> },
    { type: 'page', name: 'Cold Call Queue', path: '/cold-call', icon: <Phone size={18} /> },
];

export default function GlobalSearch({ isOpen, onClose }: { isOpen: boolean; onClose: () => void }) {
    const [query, setQuery] = useState('');
    const [results, setResults] = useState<SearchResult[]>([]);
    const [selectedIndex, setSelectedIndex] = useState(0);
    const [loading, setLoading] = useState(false);
    const inputRef = useRef<HTMLInputElement>(null);
    const navigate = useNavigate();

    useEffect(() => {
        if (isOpen) {
            setQuery('');
            setResults(PAGES);
            setSelectedIndex(0);
            setTimeout(() => inputRef.current?.focus(), 100);
        }
    }, [isOpen]);

    useEffect(() => {
        if (!query.trim()) {
            setResults(PAGES);
            return;
        }

        const searchContacts = async () => {
            setLoading(true);
            try {
                const res = await fetch(`${API_URL}/api/v2/contacts`);
                const data = await res.json();
                const contacts = (data.contacts || data || [])
                    .filter((c: any) => {
                        const name = c.name || `${c.first_name || ''} ${c.last_name || ''}`.trim();
                        const company = c.company || '';
                        const q = query.toLowerCase();
                        return name.toLowerCase().includes(q) || company.toLowerCase().includes(q);
                    })
                    .slice(0, 5)
                    .map((c: any) => ({
                        type: 'contact' as const,
                        id: c.id,
                        name: c.name || `${c.first_name || ''} ${c.last_name || ''}`.trim(),
                        subtitle: `${c.title || ''} at ${c.company || ''}`,
                        path: `/contacts/${c.id}`,
                        icon: <User size={18} />
                    }));

                const filteredPages = PAGES.filter(p => 
                    p.name.toLowerCase().includes(query.toLowerCase())
                );

                setResults([...contacts, ...filteredPages]);
            } catch (e) {
                setResults(PAGES.filter(p => p.name.toLowerCase().includes(query.toLowerCase())));
            } finally {
                setLoading(false);
            }
        };

        const debounce = setTimeout(searchContacts, 200);
        return () => clearTimeout(debounce);
    }, [query]);

    useEffect(() => {
        setSelectedIndex(0);
    }, [results]);

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'ArrowDown') {
            e.preventDefault();
            setSelectedIndex(i => Math.min(i + 1, results.length - 1));
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            setSelectedIndex(i => Math.max(i - 1, 0));
        } else if (e.key === 'Enter' && results[selectedIndex]) {
            navigate(results[selectedIndex].path);
            onClose();
        } else if (e.key === 'Escape') {
            onClose();
        }
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-black/70 flex items-start justify-center pt-[15vh] z-50" onClick={onClose}>
            <div 
                className="bg-[#1e2228] rounded-2xl border border-gray-700 w-full max-w-xl mx-4 overflow-hidden shadow-2xl"
                onClick={e => e.stopPropagation()}
            >
                {/* Search Input */}
                <div className="flex items-center gap-3 px-4 py-4 border-b border-gray-800">
                    <Search size={20} className="text-gray-500" />
                    <input
                        ref={inputRef}
                        type="text"
                        value={query}
                        onChange={e => setQuery(e.target.value)}
                        onKeyDown={handleKeyDown}
                        placeholder="Search contacts, pages..."
                        className="flex-1 bg-transparent text-white placeholder-gray-500 outline-none text-lg"
                        autoFocus
                    />
                    {loading && <Loader2 size={18} className="text-purple-400 animate-spin" />}
                    <kbd className="px-2 py-1 bg-gray-800 rounded text-gray-500 text-xs">ESC</kbd>
                </div>

                {/* Results */}
                <div className="max-h-[400px] overflow-y-auto">
                    {results.length === 0 ? (
                        <div className="text-center py-8 text-gray-500">
                            No results found
                        </div>
                    ) : (
                        <div className="py-2">
                            {results.map((result, i) => (
                                <button
                                    key={`${result.type}-${result.id || result.path}`}
                                    onClick={() => { navigate(result.path); onClose(); }}
                                    className={`w-full flex items-center gap-3 px-4 py-3 text-left transition ${
                                        i === selectedIndex ? 'bg-purple-600/20 text-white' : 'text-gray-300 hover:bg-gray-800'
                                    }`}
                                >
                                    <div className={`p-2 rounded-lg ${
                                        result.type === 'contact' ? 'bg-blue-500/20 text-blue-400' : 'bg-gray-800 text-gray-400'
                                    }`}>
                                        {result.icon}
                                    </div>
                                    <div className="flex-1 min-w-0">
                                        <p className="font-medium truncate">{result.name}</p>
                                        {result.subtitle && (
                                            <p className="text-gray-500 text-sm truncate">{result.subtitle}</p>
                                        )}
                                    </div>
                                    <ArrowRight size={16} className={`text-gray-600 ${i === selectedIndex ? 'text-purple-400' : ''}`} />
                                </button>
                            ))}
                        </div>
                    )}
                </div>

                {/* Footer */}
                <div className="px-4 py-3 bg-[#0f1114] border-t border-gray-800 flex items-center justify-between text-xs text-gray-500">
                    <div className="flex items-center gap-4">
                        <span className="flex items-center gap-1"><kbd className="px-1.5 py-0.5 bg-gray-800 rounded">↑↓</kbd> Navigate</span>
                        <span className="flex items-center gap-1"><kbd className="px-1.5 py-0.5 bg-gray-800 rounded">↵</kbd> Open</span>
                    </div>
                    <span>⌘K to open</span>
                </div>
            </div>
        </div>
    );
}
