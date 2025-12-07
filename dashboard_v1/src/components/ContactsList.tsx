import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
    Users, Search, Filter, RefreshCw, Loader2, 
    ChevronRight, Building2, Mail, Phone, Star,
    ArrowUpDown, CheckCircle, Clock, AlertCircle
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
    enrichment_status?: string;
    enriched_at?: string;
}

export default function ContactsList() {
    const [contacts, setContacts] = useState<Contact[]>([]);
    const [loading, setLoading] = useState(true);
    const [search, setSearch] = useState('');
    const [total, setTotal] = useState(0);
    const [page, setPage] = useState(0);
    const limit = 50;

    useEffect(() => {
        fetchContacts();
    }, [page]);

    const fetchContacts = async () => {
        try {
            setLoading(true);
            const res = await fetch(`${API_URL}/api/contacts?limit=${limit}&offset=${page * limit}`);
            const data = await res.json();
            setContacts(data.contacts || []);
            setTotal(data.total || 0);
        } catch (e) {
            console.error('Fetch error:', e);
        } finally {
            setLoading(false);
        }
    };

    const getDisplayName = (contact: Contact) => {
        if (contact.name) return contact.name;
        return `${contact.first_name || ''} ${contact.last_name || ''}`.trim() || 'Unknown';
    };

    const tierColors: Record<string, string> = {
        HIGH: 'bg-green-500/20 text-green-400 border-green-500/50',
        MEDIUM: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/50',
        LOW: 'bg-gray-500/20 text-gray-400 border-gray-500/50',
        MINIMAL: 'bg-red-500/20 text-red-400 border-red-500/50',
    };

    const statusIcons: Record<string, React.ReactNode> = {
        completed: <CheckCircle size={14} className="text-green-400" />,
        processing: <Loader2 size={14} className="text-yellow-400 animate-spin" />,
        pending: <Clock size={14} className="text-gray-400" />,
        failed: <AlertCircle size={14} className="text-red-400" />,
    };

    const filteredContacts = contacts.filter(c => {
        if (!search) return true;
        const searchLower = search.toLowerCase();
        const name = getDisplayName(c).toLowerCase();
        const company = (c.company || '').toLowerCase();
        const email = (c.email || '').toLowerCase();
        return name.includes(searchLower) || company.includes(searchLower) || email.includes(searchLower);
    });

    return (
        <div className="min-h-screen bg-[#0f1114] text-white">
            {/* Header */}
            <div className="bg-[#1a1d21] border-b border-gray-800 px-6 py-4">
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                        <Link to="/" className="text-gray-400 hover:text-white">
                            ← Dashboard
                        </Link>
                        <h1 className="text-xl font-bold flex items-center gap-2">
                            <Users className="text-purple-400" /> All Contacts
                        </h1>
                        <span className="text-gray-500">({total} total)</span>
                    </div>
                    <button 
                        onClick={fetchContacts}
                        className="p-2 hover:bg-gray-800 rounded-lg text-gray-400"
                    >
                        <RefreshCw size={20} />
                    </button>
                </div>

                {/* Search */}
                <div className="mt-4 relative">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" size={18} />
                    <input
                        type="text"
                        value={search}
                        onChange={e => setSearch(e.target.value)}
                        placeholder="Search by name, company, or email..."
                        className="w-full bg-[#0f1114] border border-gray-700 rounded-lg pl-10 pr-4 py-2 text-white placeholder-gray-500 focus:border-purple-500 outline-none"
                    />
                </div>
            </div>

            {/* Table */}
            <div className="p-6">
                {loading ? (
                    <div className="flex justify-center py-16">
                        <Loader2 className="w-8 h-8 text-purple-400 animate-spin" />
                    </div>
                ) : (
                    <>
                        <div className="bg-[#1e2228] rounded-xl border border-gray-800 overflow-hidden">
                            <table className="w-full">
                                <thead>
                                    <tr className="border-b border-gray-700 text-left">
                                        <th className="px-4 py-3 text-gray-400 font-medium text-sm">Name</th>
                                        <th className="px-4 py-3 text-gray-400 font-medium text-sm">Company</th>
                                        <th className="px-4 py-3 text-gray-400 font-medium text-sm">Title</th>
                                        <th className="px-4 py-3 text-gray-400 font-medium text-sm text-center">Match</th>
                                        <th className="px-4 py-3 text-gray-400 font-medium text-sm text-center">Status</th>
                                        <th className="px-4 py-3"></th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {filteredContacts.map(contact => (
                                        <tr 
                                            key={contact.id} 
                                            className="border-b border-gray-800 hover:bg-[#252a31] transition cursor-pointer"
                                            onClick={() => window.location.href = `/contacts/${contact.id}`}
                                        >
                                            <td className="px-4 py-3">
                                                <div>
                                                    <p className="font-medium text-white">{getDisplayName(contact)}</p>
                                                    {contact.email && (
                                                        <p className="text-gray-500 text-sm flex items-center gap-1">
                                                            <Mail size={12} /> {contact.email}
                                                        </p>
                                                    )}
                                                </div>
                                            </td>
                                            <td className="px-4 py-3">
                                                {contact.company && (
                                                    <span className="text-blue-400 flex items-center gap-1">
                                                        <Building2 size={14} /> {contact.company}
                                                    </span>
                                                )}
                                            </td>
                                            <td className="px-4 py-3 text-gray-400 text-sm">
                                                {contact.title || '-'}
                                            </td>
                                            <td className="px-4 py-3 text-center">
                                                {contact.match_score !== undefined && contact.match_score !== null ? (
                                                    <div className="flex flex-col items-center gap-1">
                                                        <span className="text-white font-bold">{Math.round(contact.match_score)}</span>
                                                        {contact.match_tier && (
                                                            <span className={`px-2 py-0.5 rounded text-xs border ${tierColors[contact.match_tier] || tierColors.LOW}`}>
                                                                {contact.match_tier}
                                                            </span>
                                                        )}
                                                    </div>
                                                ) : (
                                                    <span className="text-gray-600">-</span>
                                                )}
                                            </td>
                                            <td className="px-4 py-3 text-center">
                                                <div className="flex items-center justify-center gap-1">
                                                    {statusIcons[contact.enrichment_status || 'pending']}
                                                    <span className="text-gray-500 text-xs capitalize">
                                                        {contact.enrichment_status || 'pending'}
                                                    </span>
                                                </div>
                                            </td>
                                            <td className="px-4 py-3 text-right">
                                                <ChevronRight size={18} className="text-gray-600" />
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>

                        {/* Pagination */}
                        {total > limit && (
                            <div className="flex items-center justify-center gap-4 mt-6">
                                <button
                                    onClick={() => setPage(p => Math.max(0, p - 1))}
                                    disabled={page === 0}
                                    className="px-4 py-2 bg-gray-800 hover:bg-gray-700 disabled:opacity-30 rounded-lg"
                                >
                                    Previous
                                </button>
                                <span className="text-gray-400">
                                    Page {page + 1} of {Math.ceil(total / limit)}
                                </span>
                                <button
                                    onClick={() => setPage(p => p + 1)}
                                    disabled={(page + 1) * limit >= total}
                                    className="px-4 py-2 bg-gray-800 hover:bg-gray-700 disabled:opacity-30 rounded-lg"
                                >
                                    Next
                                </button>
                            </div>
                        )}
                    </>
                )}
            </div>
        </div>
    );
}
