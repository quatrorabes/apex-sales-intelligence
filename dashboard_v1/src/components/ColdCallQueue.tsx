import { useState, useEffect } from 'react';
import { 
    Phone, Plus, RefreshCw, Loader2, Search, Filter,
    CheckCircle, XCircle, Clock, ArrowUpRight, User,
    Building2, Linkedin, Mail, MoreVertical, Zap
} from 'lucide-react';

const API_URL = 'https://apex-backend-i7b0.onrender.com';

interface QueueItem {
    id: number;
    name: string;
    phone?: string;
    mobile?: string;
    email?: string;
    linkedin_url?: string;
    company?: string;
    title?: string;
    source?: string;
    source_context?: string;
    quick_fit_score?: number;
    quick_fit_reason?: string;
    priority: number;
    status: string;
    attempts: number;
    last_attempt?: string;
    outcome?: string;
    contact_id?: number;
}

interface QueueStats {
    total: number;
    new: number;
    attempted: number;
    connected: number;
    meeting_set: number;
    high_priority: number;
    avg_score: number;
}

export default function ColdCallQueue() {
    const [queue, setQueue] = useState<QueueItem[]>([]);
    const [stats, setStats] = useState<QueueStats | null>(null);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState<string>('');
    const [showAddModal, setShowAddModal] = useState(false);
    const [newContact, setNewContact] = useState({
        name: '', phone: '', email: '', linkedin_url: '', company: '', title: '', source: 'manual', notes: ''
    });

    useEffect(() => { fetchQueue(); }, [filter]);

    const fetchQueue = async () => {
        try {
            setLoading(true);
            const url = filter 
                ? `${API_URL}/api/cold-call/queue?status=${filter}`
                : `${API_URL}/api/cold-call/queue`;
            const res = await fetch(url);
            const data = await res.json();
            setQueue(data.queue || []);
            setStats(data.stats || null);
        } catch (e) {
            console.error('Fetch error:', e);
        } finally {
            setLoading(false);
        }
    };

    const addToQueue = async () => {
        if (!newContact.name) return;
        try {
            await fetch(`${API_URL}/api/cold-call/queue`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(newContact)
            });
            setShowAddModal(false);
            setNewContact({ name: '', phone: '', email: '', linkedin_url: '', company: '', title: '', source: 'manual', notes: '' });
            fetchQueue();
        } catch (e) {
            console.error('Add error:', e);
        }
    };

    const logAttempt = async (id: number, outcome?: string) => {
        try {
            await fetch(`${API_URL}/api/cold-call/queue/${id}/attempt`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ outcome })
            });
            fetchQueue();
        } catch (e) {
            console.error('Log error:', e);
        }
    };

    const updateStatus = async (id: number, status: string) => {
        try {
            await fetch(`${API_URL}/api/cold-call/queue/${id}/status`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ status })
            });
            fetchQueue();
        } catch (e) {
            console.error('Status error:', e);
        }
    };

    const promoteToContact = async (id: number) => {
        try {
            const res = await fetch(`${API_URL}/api/cold-call/queue/${id}/promote`, { method: 'POST' });
            const data = await res.json();
            if (data.success) {
                alert(`Promoted! Contact ID: ${data.contact_id}`);
                fetchQueue();
            }
        } catch (e) {
            console.error('Promote error:', e);
        }
    };

    const priorityColors = {
        1: 'bg-red-500/20 text-red-400 border-red-500/50',
        2: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/50',
        3: 'bg-gray-500/20 text-gray-400 border-gray-500/50',
    };

    const statusColors: Record<string, string> = {
        new: 'bg-blue-500/20 text-blue-400',
        attempted: 'bg-yellow-500/20 text-yellow-400',
        connected: 'bg-green-500/20 text-green-400',
        meeting_set: 'bg-purple-500/20 text-purple-400',
        not_interested: 'bg-red-500/20 text-red-400',
    };

    return (
        <div className="min-h-screen bg-[#0f1114] text-white p-6">
            {/* Header */}
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h1 className="text-2xl font-bold flex items-center gap-2">
                        <Phone className="text-purple-400" /> Cold Call Queue
                    </h1>
                    <p className="text-gray-400 text-sm">Quick-score contacts before enrichment</p>
                </div>
                <div className="flex gap-3">
                    <button onClick={fetchQueue} className="p-2 hover:bg-gray-800 rounded-lg text-gray-400">
                        <RefreshCw size={20} />
                    </button>
                    <button 
                        onClick={() => setShowAddModal(true)}
                        className="bg-purple-600 hover:bg-purple-700 px-4 py-2 rounded-lg font-medium flex items-center gap-2"
                    >
                        <Plus size={18} /> Add Contact
                    </button>
                </div>
            </div>

            {/* Stats */}
            {stats && (
                <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-4 mb-6">
                    <div className="bg-[#1e2228] rounded-lg p-4 border border-gray-800">
                        <p className="text-gray-400 text-sm">Total</p>
                        <p className="text-2xl font-bold">{stats.total}</p>
                    </div>
                    <div className="bg-[#1e2228] rounded-lg p-4 border border-gray-800">
                        <p className="text-blue-400 text-sm">New</p>
                        <p className="text-2xl font-bold">{stats.new}</p>
                    </div>
                    <div className="bg-[#1e2228] rounded-lg p-4 border border-gray-800">
                        <p className="text-yellow-400 text-sm">Attempted</p>
                        <p className="text-2xl font-bold">{stats.attempted}</p>
                    </div>
                    <div className="bg-[#1e2228] rounded-lg p-4 border border-gray-800">
                        <p className="text-green-400 text-sm">Connected</p>
                        <p className="text-2xl font-bold">{stats.connected}</p>
                    </div>
                    <div className="bg-[#1e2228] rounded-lg p-4 border border-gray-800">
                        <p className="text-purple-400 text-sm">Meetings</p>
                        <p className="text-2xl font-bold">{stats.meeting_set}</p>
                    </div>
                    <div className="bg-[#1e2228] rounded-lg p-4 border border-gray-800">
                        <p className="text-red-400 text-sm">High Priority</p>
                        <p className="text-2xl font-bold">{stats.high_priority}</p>
                    </div>
                    <div className="bg-[#1e2228] rounded-lg p-4 border border-gray-800">
                        <p className="text-gray-400 text-sm">Avg Score</p>
                        <p className="text-2xl font-bold">{Math.round(stats.avg_score || 0)}</p>
                    </div>
                </div>
            )}

            {/* Filters */}
            <div className="flex gap-2 mb-6">
                {['', 'new', 'attempted', 'connected', 'meeting_set'].map(f => (
                    <button
                        key={f}
                        onClick={() => setFilter(f)}
                        className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
                            filter === f ? 'bg-purple-600 text-white' : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
                        }`}
                    >
                        {f || 'All'}
                    </button>
                ))}
            </div>

            {/* Queue List */}
            {loading ? (
                <div className="flex justify-center py-16">
                    <Loader2 className="w-8 h-8 text-purple-400 animate-spin" />
                </div>
            ) : queue.length === 0 ? (
                <div className="text-center py-16 text-gray-500">
                    <Phone className="w-16 h-16 mx-auto mb-4 opacity-30" />
                    <p>No contacts in queue</p>
                </div>
            ) : (
                <div className="space-y-3">
                    {queue.map(item => (
                        <div key={item.id} className="bg-[#1e2228] rounded-xl border border-gray-800 p-4 hover:border-gray-700 transition">
                            <div className="flex items-start justify-between">
                                <div className="flex items-start gap-4">
                                    {/* Priority Badge */}
                                    <div className={`px-2 py-1 rounded text-xs font-bold border ${priorityColors[item.priority as keyof typeof priorityColors] || priorityColors[3]}`}>
                                        P{item.priority}
                                    </div>
                                    
                                    {/* Contact Info */}
                                    <div>
                                        <h3 className="font-semibold text-white">{item.name}</h3>
                                        {item.title && <p className="text-gray-400 text-sm">{item.title}</p>}
                                        {item.company && (
                                            <p className="text-blue-400 text-sm flex items-center gap-1">
                                                <Building2 size={12} /> {item.company}
                                            </p>
                                        )}
                                        <div className="flex gap-3 mt-2 text-sm">
                                            {item.phone && (
                                                <a href={`tel:${item.phone}`} className="text-gray-400 hover:text-white flex items-center gap-1">
                                                    <Phone size={12} /> {item.phone}
                                                </a>
                                            )}
                                            {item.linkedin_url && (
                                                <a href={item.linkedin_url} target="_blank" className="text-gray-400 hover:text-blue-400 flex items-center gap-1">
                                                    <Linkedin size={12} /> LinkedIn
                                                </a>
                                            )}
                                        </div>
                                    </div>
                                </div>

                                {/* Score & Status */}
                                <div className="flex items-center gap-3">
                                    {item.quick_fit_score !== undefined && (
                                        <div className="text-right">
                                            <p className="text-lg font-bold text-white">{Math.round(item.quick_fit_score)}</p>
                                            <p className="text-gray-500 text-xs">Fit Score</p>
                                        </div>
                                    )}
                                    <span className={`px-2 py-1 rounded text-xs ${statusColors[item.status] || statusColors.new}`}>
                                        {item.status}
                                    </span>
                                </div>
                            </div>

                            {/* Actions */}
                            <div className="flex items-center gap-2 mt-4 pt-4 border-t border-gray-700">
                                <button
                                    onClick={() => logAttempt(item.id, 'no_answer')}
                                    className="px-3 py-1.5 bg-gray-700 hover:bg-gray-600 rounded text-sm"
                                >
                                    <Clock size={14} className="inline mr-1" /> No Answer
                                </button>
                                <button
                                    onClick={() => updateStatus(item.id, 'connected')}
                                    className="px-3 py-1.5 bg-green-700 hover:bg-green-600 rounded text-sm"
                                >
                                    <CheckCircle size={14} className="inline mr-1" /> Connected
                                </button>
                                <button
                                    onClick={() => updateStatus(item.id, 'meeting_set')}
                                    className="px-3 py-1.5 bg-purple-700 hover:bg-purple-600 rounded text-sm"
                                >
                                    <Zap size={14} className="inline mr-1" /> Meeting Set
                                </button>
                                <button
                                    onClick={() => updateStatus(item.id, 'not_interested')}
                                    className="px-3 py-1.5 bg-red-700 hover:bg-red-600 rounded text-sm"
                                >
                                    <XCircle size={14} className="inline mr-1" /> Not Interested
                                </button>
                                <div className="flex-1" />
                                <button
                                    onClick={() => promoteToContact(item.id)}
                                    className="px-3 py-1.5 bg-blue-700 hover:bg-blue-600 rounded text-sm"
                                >
                                    <ArrowUpRight size={14} className="inline mr-1" /> Promote & Enrich
                                </button>
                            </div>
                        </div>
                    ))}
                </div>
            )}

            {/* Add Modal */}
            {showAddModal && (
                <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
                    <div className="bg-[#1a1d21] rounded-xl w-full max-w-md p-6">
                        <h2 className="text-xl font-bold mb-4">Add to Cold Call Queue</h2>
                        <div className="space-y-3">
                            <input
                                type="text"
                                placeholder="Name *"
                                value={newContact.name}
                                onChange={e => setNewContact(c => ({ ...c, name: e.target.value }))}
                                className="w-full bg-[#0f1114] border border-gray-700 rounded-lg px-4 py-2 text-white"
                            />
                            <input
                                type="text"
                                placeholder="Phone"
                                value={newContact.phone}
                                onChange={e => setNewContact(c => ({ ...c, phone: e.target.value }))}
                                className="w-full bg-[#0f1114] border border-gray-700 rounded-lg px-4 py-2 text-white"
                            />
                            <input
                                type="text"
                                placeholder="Company"
                                value={newContact.company}
                                onChange={e => setNewContact(c => ({ ...c, company: e.target.value }))}
                                className="w-full bg-[#0f1114] border border-gray-700 rounded-lg px-4 py-2 text-white"
                            />
                            <input
                                type="text"
                                placeholder="Title"
                                value={newContact.title}
                                onChange={e => setNewContact(c => ({ ...c, title: e.target.value }))}
                                className="w-full bg-[#0f1114] border border-gray-700 rounded-lg px-4 py-2 text-white"
                            />
                            <input
                                type="text"
                                placeholder="LinkedIn URL"
                                value={newContact.linkedin_url}
                                onChange={e => setNewContact(c => ({ ...c, linkedin_url: e.target.value }))}
                                className="w-full bg-[#0f1114] border border-gray-700 rounded-lg px-4 py-2 text-white"
                            />
                            <select
                                value={newContact.source}
                                onChange={e => setNewContact(c => ({ ...c, source: e.target.value }))}
                                className="w-full bg-[#0f1114] border border-gray-700 rounded-lg px-4 py-2 text-white"
                            >
                                <option value="manual">Manual Entry</option>
                                <option value="linkedin">LinkedIn</option>
                                <option value="referral">Referral</option>
                                <option value="event">Event/Conference</option>
                                <option value="list">Purchased List</option>
                            </select>
                        </div>
                        <div className="flex gap-3 mt-6">
                            <button
                                onClick={() => setShowAddModal(false)}
                                className="flex-1 px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg"
                            >
                                Cancel
                            </button>
                            <button
                                onClick={addToQueue}
                                disabled={!newContact.name}
                                className="flex-1 px-4 py-2 bg-purple-600 hover:bg-purple-700 disabled:opacity-50 rounded-lg"
                            >
                                Add to Queue
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
