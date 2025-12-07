import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
    Zap, Users, Target, TrendingUp, RefreshCw, Loader2,
    Phone, Sparkles, ChevronRight, Building2, Star,
    Clock, Filter, BarChart3, ArrowUpRight, Settings
} from 'lucide-react';

const API_URL = 'https://apex-backend-production-production.up.railway.app';

interface Contact {
    id: number;
    name?: string;
    first_name?: string;
    last_name?: string;
    email?: string;
    phone?: string;
    company?: string;
    title?: string;
    match_score?: number;
    match_tier?: string;
    fit_score?: number;
    relevance_score?: number;
    timing_score?: number;
    enrichment_status?: string;
    enriched_at?: string;
}

interface BoardData {
    success: boolean;
    date: string;
    time: string;
    stats: {
        total_contacts: number;
        enriched: number;
        high_match: number;
        medium_match: number;
        low_match: number;
        cold_call_queue: number;
    };
    segments: {
        high: Contact[];
        medium: Contact[];
        low: Contact[];
    };
    top_priority: Contact[];
    cold_call_stats: {
        total?: number;
        new?: number;
        meeting_set?: number;
    };
}

export default function TodaysBoard() {
    const [data, setData] = useState<BoardData | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [batchScoring, setBatchScoring] = useState(false);
    const [showOnboarding, setShowOnboarding] = useState(false);

    useEffect(() => {
        fetchBoard();
        checkOnboarding();
    }, []);

    const checkOnboarding = async () => {
        try {
            const res = await fetch(`${API_URL}/api/user/profile?user_id=default`);
            const profile = await res.json();
            if (!profile.full_name) {
                setShowOnboarding(true);
            }
        } catch (e) {
            // Ignore
        }
    };

    const fetchBoard = async () => {
        try {
            setLoading(true);
            setError(null);
            const res = await fetch(`${API_URL}/api/todays-board`);
            if (!res.ok) throw new Error('Failed to fetch');
            const json = await res.json();
            setData(json);
        } catch (e) {
            setError('Failed to connect to API');
        } finally {
            setLoading(false);
        }
    };

    const batchRescore = async () => {
        setBatchScoring(true);
        try {
            const res = await fetch(`${API_URL}/api/batch/rescore`, { method: 'POST' });
            const result = await res.json();
            alert(`Re-scored ${result.scored} contacts!`);
            fetchBoard();
        } catch (e) {
            alert('Batch scoring failed');
        } finally {
            setBatchScoring(false);
        }
    };

    const getDisplayName = (c: Contact) => {
        if (c.name) return c.name;
        return `${c.first_name || ''} ${c.last_name || ''}`.trim() || 'Unknown';
    };

    const tierColors: Record<string, string> = {
        HIGH: 'border-l-green-500 bg-green-500/5',
        MEDIUM: 'border-l-yellow-500 bg-yellow-500/5',
        LOW: 'border-l-orange-500 bg-orange-500/5',
    };

    const tierBadgeColors: Record<string, string> = {
        HIGH: 'bg-green-500/20 text-green-400',
        MEDIUM: 'bg-yellow-500/20 text-yellow-400',
        LOW: 'bg-orange-500/20 text-orange-400',
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-[#0f1114] flex items-center justify-center">
                <Loader2 className="w-8 h-8 text-purple-400 animate-spin" />
            </div>
        );
    }

    if (error) {
        return (
            <div className="min-h-screen bg-[#0f1114] flex items-center justify-center">
                <div className="text-center">
                    <p className="text-red-400 mb-4">{error}</p>
                    <button onClick={fetchBoard} className="px-4 py-2 bg-purple-600 rounded-lg">
                        Retry
                    </button>
                </div>
            </div>
        );
    }

    const ContactCard = ({ contact, showScore = true }: { contact: Contact; showScore?: boolean }) => (
        <Link
            to={`/contacts/${contact.id}`}
            className={`block p-4 rounded-lg border-l-4 hover:bg-gray-800/50 transition ${tierColors[contact.match_tier || 'LOW']}`}
        >
            <div className="flex items-start justify-between">
                <div className="flex-1 min-w-0">
                    <h4 className="font-medium text-white truncate">{getDisplayName(contact)}</h4>
                    <p className="text-gray-400 text-sm truncate">{contact.title}</p>
                    <p className="text-blue-400 text-sm truncate flex items-center gap-1">
                        <Building2 size={12} /> {contact.company}
                    </p>
                </div>
                {showScore && contact.match_score !== undefined && (
                    <div className="text-right ml-3">
                        <div className="text-2xl font-bold text-white">{Math.round(contact.match_score)}</div>
                        <span className={`text-xs px-2 py-0.5 rounded ${tierBadgeColors[contact.match_tier || 'LOW']}`}>
                            {contact.match_tier}
                        </span>
                    </div>
                )}
            </div>
            {/* Score breakdown mini */}
            {contact.fit_score !== undefined && (
                <div className="flex gap-3 mt-2 text-xs text-gray-500">
                    <span>FIT: {Math.round(contact.fit_score)}</span>
                    <span>REL: {Math.round(contact.relevance_score || 0)}</span>
                    <span>TIME: {Math.round(contact.timing_score || 0)}</span>
                </div>
            )}
        </Link>
    );

    return (
        <div className="min-h-screen bg-[#0f1114] text-white">
            {/* Header */}
            <div className="bg-[#1a1d21] border-b border-gray-800 px-6 py-4">
                <div className="flex items-center justify-between">
                    <div>
                        <h1 className="text-2xl font-bold flex items-center gap-2">
                            <Zap className="text-yellow-400" /> Today's Board
                        </h1>
                        <p className="text-gray-400 text-sm">{data?.date} • {data?.time}</p>
                    </div>
                    <div className="flex items-center gap-3">
                        <button
                            onClick={batchRescore}
                            disabled={batchScoring}
                            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 rounded-lg flex items-center gap-2 text-sm"
                        >
                            {batchScoring ? <Loader2 size={16} className="animate-spin" /> : <BarChart3 size={16} />}
                            Re-score All
                        </button>
                        <button onClick={fetchBoard} className="p-2 hover:bg-gray-800 rounded-lg text-gray-400">
                            <RefreshCw size={20} />
                        </button>
                        <Link to="/contacts" className="px-4 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg flex items-center gap-2 text-sm">
                            <Users size={16} /> All Contacts
                        </Link>
                        <Link to="/analytics" className="px-4 py-2 bg-green-600 hover:bg-green-700 rounded-lg flex items-center gap-2 text-sm"><BarChart3 size={16} /> Analytics</Link>
                        <Link to="/cold-call" className="px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg flex items-center gap-2 text-sm">
                            <Phone size={16} /> Cold Call Queue
                        </Link>
                    </div>
                </div>
            </div>

            {/* Stats Row */}
            <div className="px-6 py-4 border-b border-gray-800 bg-[#1a1d21]/50">
                <div className="grid grid-cols-2 md:grid-cols-6 gap-4">
                    <div className="bg-[#1e2228] rounded-lg p-4 border border-gray-800">
                        <p className="text-gray-400 text-sm">Total Contacts</p>
                        <p className="text-2xl font-bold">{data?.stats.total_contacts || 0}</p>
                    </div>
                    <div className="bg-[#1e2228] rounded-lg p-4 border border-gray-800">
                        <p className="text-gray-400 text-sm">Enriched</p>
                        <p className="text-2xl font-bold text-purple-400">{data?.stats.enriched || 0}</p>
                    </div>
                    <div className="bg-[#1e2228] rounded-lg p-4 border border-gray-800">
                        <p className="text-green-400 text-sm">High Match</p>
                        <p className="text-2xl font-bold">{data?.stats.high_match || 0}</p>
                    </div>
                    <div className="bg-[#1e2228] rounded-lg p-4 border border-gray-800">
                        <p className="text-yellow-400 text-sm">Medium Match</p>
                        <p className="text-2xl font-bold">{data?.stats.medium_match || 0}</p>
                    </div>
                    <div className="bg-[#1e2228] rounded-lg p-4 border border-gray-800">
                        <p className="text-orange-400 text-sm">Low Match</p>
                        <p className="text-2xl font-bold">{data?.stats.low_match || 0}</p>
                    </div>
                    <div className="bg-[#1e2228] rounded-lg p-4 border border-gray-800">
                        <p className="text-blue-400 text-sm">Cold Queue</p>
                        <p className="text-2xl font-bold">{data?.stats.cold_call_queue || 0}</p>
                    </div>
                </div>
            </div>

            {/* Onboarding Banner */}
            {showOnboarding && (
                <div className="mx-6 mt-4 bg-purple-900/30 border border-purple-700 rounded-lg p-4 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <Settings className="text-purple-400" />
                        <div>
                            <p className="text-white font-medium">Complete your profile</p>
                            <p className="text-gray-400 text-sm">Set up your products and ideal client to enable personalized scoring</p>
                        </div>
                    </div>
                    <button 
                        onClick={() => window.location.reload()}
                        className="px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg text-sm"
                    >
                        Set Up Now
                    </button>
                </div>
            )}

            {/* Main Content */}
            <div className="p-6">
                <div className="grid lg:grid-cols-3 gap-6">
                    {/* HIGH PRIORITY */}
                    <div className="bg-[#1e2228] rounded-xl border border-gray-800 overflow-hidden">
                        <div className="px-4 py-3 border-b border-gray-800 flex items-center justify-between">
                            <div className="flex items-center gap-2 text-green-400">
                                <Star size={18} />
                                <h2 className="font-semibold">High Priority</h2>
                            </div>
                            <span className="bg-green-500/20 text-green-400 px-2 py-0.5 rounded text-sm">
                                {data?.segments.high.length || 0}
                            </span>
                        </div>
                        <div className="p-3 space-y-2 max-h-[500px] overflow-y-auto">
                            {data?.segments.high.length === 0 ? (
                                <p className="text-gray-500 text-center py-8">No high priority contacts</p>
                            ) : (
                                data?.segments.high.map(c => <ContactCard key={c.id} contact={c} />)
                            )}
                        </div>
                    </div>

                    {/* MEDIUM PRIORITY */}
                    <div className="bg-[#1e2228] rounded-xl border border-gray-800 overflow-hidden">
                        <div className="px-4 py-3 border-b border-gray-800 flex items-center justify-between">
                            <div className="flex items-center gap-2 text-yellow-400">
                                <Target size={18} />
                                <h2 className="font-semibold">Medium Priority</h2>
                            </div>
                            <span className="bg-yellow-500/20 text-yellow-400 px-2 py-0.5 rounded text-sm">
                                {data?.segments.medium.length || 0}
                            </span>
                        </div>
                        <div className="p-3 space-y-2 max-h-[500px] overflow-y-auto">
                            {data?.segments.medium.length === 0 ? (
                                <p className="text-gray-500 text-center py-8">No medium priority contacts</p>
                            ) : (
                                data?.segments.medium.map(c => <ContactCard key={c.id} contact={c} />)
                            )}
                        </div>
                    </div>

                    {/* LOW / QUICK ACTIONS */}
                    <div className="space-y-6">
                        {/* Quick Actions */}
                        <div className="bg-[#1e2228] rounded-xl border border-gray-800 p-4">
                            <h3 className="font-semibold text-white mb-4 flex items-center gap-2">
                                <Zap size={18} className="text-yellow-400" /> Quick Actions
                            </h3>
                            <div className="space-y-2">
                                <Link
                                    to="/cold-call"
                                    className="w-full p-3 bg-[#0f1114] hover:bg-gray-800 rounded-lg flex items-center justify-between group"
                                >
                                    <div className="flex items-center gap-3">
                                        <Phone size={18} className="text-purple-400" />
                                        <div>
                                            <p className="text-white font-medium">Cold Call Queue</p>
                                            <p className="text-gray-500 text-sm">{data?.cold_call_stats?.new || 0} new to call</p>
                                        </div>
                                    </div>
                                    <ChevronRight size={18} className="text-gray-600 group-hover:text-white transition" />
                                </Link>
                                <Link
                                    to="/contacts"
                                    className="w-full p-3 bg-[#0f1114] hover:bg-gray-800 rounded-lg flex items-center justify-between group"
                                >
                                    <div className="flex items-center gap-3">
                                        <Users size={18} className="text-blue-400" />
                                        <div>
                                            <p className="text-white font-medium">All Contacts</p>
                                            <p className="text-gray-500 text-sm">{data?.stats.total_contacts || 0} total</p>
                                        </div>
                                    </div>
                                    <ChevronRight size={18} className="text-gray-600 group-hover:text-white transition" />
                                </Link>
                            </div>
                        </div>

                        {/* Low Priority */}
                        <div className="bg-[#1e2228] rounded-xl border border-gray-800 overflow-hidden">
                            <div className="px-4 py-3 border-b border-gray-800 flex items-center justify-between">
                                <div className="flex items-center gap-2 text-orange-400">
                                    <Clock size={18} />
                                    <h2 className="font-semibold">Low Priority</h2>
                                </div>
                                <span className="bg-orange-500/20 text-orange-400 px-2 py-0.5 rounded text-sm">
                                    {data?.segments.low.length || 0}
                                </span>
                            </div>
                            <div className="p-3 space-y-2 max-h-[300px] overflow-y-auto">
                                {data?.segments.low.length === 0 ? (
                                    <p className="text-gray-500 text-center py-4">No low priority contacts</p>
                                ) : (
                                    data?.segments.low.slice(0, 5).map(c => <ContactCard key={c.id} contact={c} />)
                                )}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
