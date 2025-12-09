import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
    Flame, Phone, Zap, Clock, Crown, Sparkles,
    ChevronRight, Loader2, RefreshCw, ChevronLeft, Users
} from 'lucide-react';

const API_URL = 'https://apex-backend-i7b0.onrender.com';

interface SmartList {
    id: string;
    name: string;
    description: string;
    icon: string;
    color: string;
    count: number;
}

interface Contact {
    id: number;
    name?: string;
    first_name?: string;
    last_name?: string;
    title?: string;
    company?: string;
    match_score?: number;
    match_tier?: string;
}

const iconMap: Record<string, React.ReactNode> = {
    flame: <Flame size={20} />,
    phone: <Phone size={20} />,
    zap: <Zap size={20} />,
    clock: <Clock size={20} />,
    crown: <Crown size={20} />,
    sparkles: <Sparkles size={20} />,
};

const colorMap: Record<string, string> = {
    red: 'bg-red-500/20 text-red-400 border-red-500/50',
    green: 'bg-green-500/20 text-green-400 border-green-500/50',
    yellow: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/50',
    blue: 'bg-blue-500/20 text-blue-400 border-blue-500/50',
    purple: 'bg-purple-500/20 text-purple-400 border-purple-500/50',
    cyan: 'bg-cyan-500/20 text-cyan-400 border-cyan-500/50',
};

export default function SmartLists() {
    const [lists, setLists] = useState<SmartList[]>([]);
    const [selectedList, setSelectedList] = useState<string | null>(null);
    const [contacts, setContacts] = useState<Contact[]>([]);
    const [loading, setLoading] = useState(true);
    const [loadingContacts, setLoadingContacts] = useState(false);

    useEffect(() => {
        fetchLists();
    }, []);

    const fetchLists = async () => {
        try {
            setLoading(true);
            const res = await fetch(`${API_URL}/api/smart-lists`);
            const data = await res.json();
            setLists(data.lists || []);
        } catch (e) {
            console.error('Fetch error:', e);
        } finally {
            setLoading(false);
        }
    };

    const fetchListContacts = async (listId: string) => {
        try {
            setLoadingContacts(true);
            setSelectedList(listId);
            const res = await fetch(`${API_URL}/api/smart-lists/${listId}/contacts?limit=50`);
            const data = await res.json();
            setContacts(data.contacts || []);
        } catch (e) {
            console.error('Fetch contacts error:', e);
        } finally {
            setLoadingContacts(false);
        }
    };

    const getDisplayName = (c: Contact) => {
        if (c.name) return c.name;
        return `${c.first_name || ''} ${c.last_name || ''}`.trim() || 'Unknown';
    };

    const selectedListInfo = lists.find(l => l.id === selectedList);

    if (loading) {
        return (
            <div className="min-h-screen bg-[#0f1114] flex items-center justify-center">
                <Loader2 className="w-8 h-8 text-purple-400 animate-spin" />
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-[#0f1114] text-white">
            {/* Header */}
            <div className="bg-[#1a1d21] border-b border-gray-800 px-6 py-4">
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                        <Link to="/" className="text-gray-400 hover:text-white flex items-center gap-1">
                            <ChevronLeft size={20} /> Dashboard
                        </Link>
                        <h1 className="text-2xl font-bold flex items-center gap-2">
                            <Sparkles className="text-purple-400" /> Smart Lists
                        </h1>
                    </div>
                    <button onClick={fetchLists} className="p-2 hover:bg-gray-800 rounded-lg">
                        <RefreshCw size={20} className="text-gray-400" />
                    </button>
                </div>
            </div>

            <div className="p-6">
                <div className="grid lg:grid-cols-3 gap-6">
                    {/* Lists Panel */}
                    <div className="lg:col-span-1 space-y-3">
                        <h2 className="text-gray-400 text-sm font-medium mb-4">AUTO-GENERATED LISTS</h2>
                        {lists.map(list => (
                            <button
                                key={list.id}
                                onClick={() => fetchListContacts(list.id)}
                                className={`w-full p-4 rounded-xl border transition text-left ${
                                    selectedList === list.id 
                                        ? 'bg-purple-900/30 border-purple-500' 
                                        : 'bg-[#1e2228] border-gray-800 hover:border-gray-700'
                                }`}
                            >
                                <div className="flex items-center justify-between">
                                    <div className="flex items-center gap-3">
                                        <div className={`p-2 rounded-lg border ${colorMap[list.color]}`}>
                                            {iconMap[list.icon]}
                                        </div>
                                        <div>
                                            <h3 className="font-medium text-white">{list.name}</h3>
                                            <p className="text-gray-500 text-sm">{list.description}</p>
                                        </div>
                                    </div>
                                    <div className="flex items-center gap-2">
                                        <span className="text-2xl font-bold text-white">{list.count}</span>
                                        <ChevronRight size={18} className="text-gray-600" />
                                    </div>
                                </div>
                            </button>
                        ))}
                    </div>

                    {/* Contacts Panel */}
                    <div className="lg:col-span-2">
                        {!selectedList ? (
                            <div className="bg-[#1e2228] rounded-xl border border-gray-800 p-16 text-center">
                                <Users className="w-16 h-16 text-gray-700 mx-auto mb-4" />
                                <p className="text-gray-500">Select a list to view contacts</p>
                            </div>
                        ) : loadingContacts ? (
                            <div className="bg-[#1e2228] rounded-xl border border-gray-800 p-16 text-center">
                                <Loader2 className="w-8 h-8 text-purple-400 animate-spin mx-auto" />
                            </div>
                        ) : (
                            <div className="bg-[#1e2228] rounded-xl border border-gray-800 overflow-hidden">
                                <div className="px-5 py-4 border-b border-gray-800 flex items-center justify-between">
                                    <div className="flex items-center gap-3">
                                        <div className={`p-2 rounded-lg border ${colorMap[selectedListInfo?.color || 'purple']}`}>
                                            {iconMap[selectedListInfo?.icon || 'sparkles']}
                                        </div>
                                        <div>
                                            <h2 className="font-semibold text-white">{selectedListInfo?.name}</h2>
                                            <p className="text-gray-500 text-sm">{contacts.length} contacts</p>
                                        </div>
                                    </div>
                                </div>
                                <div className="divide-y divide-gray-800 max-h-[600px] overflow-y-auto">
                                    {contacts.map(c => (
                                        <Link
                                            key={c.id}
                                            to={`/contacts/${c.id}`}
                                            className="flex items-center justify-between p-4 hover:bg-gray-800/50 transition"
                                        >
                                            <div>
                                                <h4 className="font-medium text-white">{getDisplayName(c)}</h4>
                                                <p className="text-gray-400 text-sm">{c.title} at {c.company}</p>
                                            </div>
                                            {c.match_score !== undefined && (
                                                <div className="text-right">
                                                    <span className="text-xl font-bold text-white">{Math.round(c.match_score)}</span>
                                                    <span className="text-gray-500 text-sm ml-2">{c.match_tier}</span>
                                                </div>
                                            )}
                                        </Link>
                                    ))}
                                    {contacts.length === 0 && (
                                        <p className="text-gray-500 text-center py-8">No contacts in this list</p>
                                    )}
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}
