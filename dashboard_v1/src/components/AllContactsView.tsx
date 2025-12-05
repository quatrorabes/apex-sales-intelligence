import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, RefreshCw, Mail, Phone, Linkedin, CheckCircle2, Clock } from 'lucide-react';

interface Contact {
    id: number;
    name: string;
    email: string;
    company: string;
    title: string;
    phone?: string;
    linkedin_url?: string;
    mdcp_score?: number;
    priority_score?: number;
    enrichment_status?: string;
}

export default function AllContactsView() {
    const navigate = useNavigate();
    const [contacts, setContacts] = useState<Contact[]>([]);
    const [filteredContacts, setFilteredContacts] = useState<Contact[]>([]);
    const [searchQuery, setSearchQuery] = useState('');
    const [sortBy, setSortBy] = useState<'mdcp_score' | 'name' | 'company'>('mdcp_score');
    const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
    const [loading, setLoading] = useState(true);

    useEffect(() => { fetchContacts(); }, []);
    useEffect(() => { filterAndSortContacts(); }, [contacts, searchQuery, sortBy, sortOrder]);

    const fetchContacts = async () => {
        try {
            setLoading(true);
            const response = await fetch('http://localhost:8000/api/contacts?limit=200');
            const data = await response.json();
            setContacts(data.contacts || []);
        } catch (error) {
            console.error('Failed to fetch contacts:', error);
        } finally {
            setLoading(false);
        }
    };

    const filterAndSortContacts = () => {
        let filtered = contacts;
        if (searchQuery) {
            const query = searchQuery.toLowerCase();
            filtered = filtered.filter(c =>
                c.name?.toLowerCase().includes(query) ||
                c.company?.toLowerCase().includes(query) ||
                c.email?.toLowerCase().includes(query)
            );
        }
        filtered = [...filtered].sort((a, b) => {
            let aVal: string | number = sortBy === 'name' ? (a.name || '') :
                sortBy === 'company' ? (a.company || '') : (a.mdcp_score || 0);
            let bVal: string | number = sortBy === 'name' ? (b.name || '') :
                sortBy === 'company' ? (b.company || '') : (b.mdcp_score || 0);
            if (typeof aVal === 'string') {
                return sortOrder === 'asc' ? aVal.localeCompare(bVal as string) : (bVal as string).localeCompare(aVal);
            }
            return sortOrder === 'asc' ? (aVal as number) - (bVal as number) : (bVal as number) - (aVal as number);
        });
        setFilteredContacts(filtered);
    };

    const handleCardClick = (contactId: number) => {
        navigate(`/contacts/${contactId}`);
    };

    const getAvatarColor = (name: string) => {
        const colors = [
            'from-blue-500 to-blue-600', 'from-purple-500 to-purple-600',
            'from-green-500 to-green-600', 'from-orange-500 to-orange-600',
            'from-pink-500 to-pink-600', 'from-indigo-500 to-indigo-600',
        ];
        return colors[name?.charCodeAt(0) % colors.length || 0];
    };

    const getStatusIcon = (status?: string) => {
        if (status === 'completed') return <CheckCircle2 size={14} className="text-green-500" />;
        if (status === 'processing') return <Clock size={14} className="text-yellow-500 animate-spin" />;
        return null;
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-[#0f1114] flex items-center justify-center">
                <div className="animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-blue-500"></div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-[#0f1114] text-white p-6">
            <div className="max-w-7xl mx-auto">
                {/* Header */}
                <div className="flex items-center justify-between mb-6">
                    <h1 className="text-2xl font-bold">All Contacts</h1>
                    <button onClick={fetchContacts} className="p-2 hover:bg-gray-800 rounded-lg">
                        <RefreshCw size={20} />
                    </button>
                </div>

                {/* Search & Sort */}
                <div className="flex flex-col md:flex-row gap-4 mb-6">
                    <div className="relative flex-1">
                        <Search size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
                        <input
                            type="text"
                            placeholder="Search contacts..."
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            className="w-full pl-10 pr-4 py-3 bg-[#1a1d21] border border-gray-700 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent text-white placeholder-gray-500"
                        />
                    </div>
                    <div className="flex items-center gap-2">
                        <span className="text-gray-400 text-sm">Sort:</span>
                        <select
                            value={sortBy}
                            onChange={(e) => setSortBy(e.target.value as any)}
                            className="px-3 py-2 bg-[#1a1d21] border border-gray-700 rounded-lg text-sm text-white"
                        >
                            <option value="mdcp_score">MDCP Score</option>
                            <option value="name">Name</option>
                            <option value="company">Company</option>
                        </select>
                        <button
                            onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
                            className="text-blue-400 text-sm font-medium hover:text-blue-300 px-2"
                        >
                            {sortOrder === 'desc' ? '↓ Desc' : '↑ Asc'}
                        </button>
                        <span className="text-gray-500 text-sm ml-4">{filteredContacts.length} contacts</span>
                    </div>
                </div>

                {/* Cards Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                    {filteredContacts.map(contact => (
                        <div
                            key={contact.id}
                            onClick={() => handleCardClick(contact.id)}
                            className="bg-[#1a1d21] rounded-xl border border-gray-800 p-5 hover:border-blue-500 hover:shadow-lg transition-all cursor-pointer group"
                        >
                            <div className="flex items-start gap-3 mb-3">
                                <div className={`w-12 h-12 rounded-full bg-gradient-to-br ${getAvatarColor(contact.name)} flex items-center justify-center text-white font-bold text-lg`}>
                                    {contact.name?.charAt(0) || '?'}
                                </div>
                                <div className="flex-1 min-w-0">
                                    <div className="flex items-center gap-2">
                                        <h3 className="font-semibold text-white truncate">{contact.name}</h3>
                                        {getStatusIcon(contact.enrichment_status)}
                                    </div>
                                    <p className="text-gray-400 text-sm truncate">{contact.title}</p>
                                    <p className="text-blue-400 text-sm truncate">{contact.company}</p>
                                </div>
                            </div>

                            <div className="flex items-center gap-4 mb-3">
                                <div className="text-center">
                                    <p className="text-xs text-gray-500">MDCP</p>
                                    <p className="text-lg font-bold text-orange-400">{contact.mdcp_score || 0}</p>
                                </div>
                                <div className="text-center">
                                    <p className="text-xs text-gray-500">Priority</p>
                                    <p className="text-lg font-bold text-purple-400">{contact.priority_score || 0}</p>
                                </div>
                            </div>

                            <div className="flex items-center gap-2 pt-3 border-t border-gray-800">
                                {contact.email && (
                                    <button onClick={(e) => { e.stopPropagation(); window.location.href = `mailto:${contact.email}`; }}
                                        className="p-2 text-gray-500 hover:text-blue-400 hover:bg-blue-900/30 rounded-lg transition" title={contact.email}>
                                        <Mail size={16} />
                                    </button>
                                )}
                                {contact.phone && (
                                    <button onClick={(e) => { e.stopPropagation(); window.location.href = `tel:${contact.phone}`; }}
                                        className="p-2 text-gray-500 hover:text-green-400 hover:bg-green-900/30 rounded-lg transition" title={contact.phone}>
                                        <Phone size={16} />
                                    </button>
                                )}
                                {contact.linkedin_url && (
                                    <button onClick={(e) => { e.stopPropagation(); window.open(contact.linkedin_url, '_blank'); }}
                                        className="p-2 text-gray-500 hover:text-blue-400 hover:bg-blue-900/30 rounded-lg transition" title="LinkedIn">
                                        <Linkedin size={16} />
                                    </button>
                                )}
                            </div>
                        </div>
                    ))}
                </div>

                {filteredContacts.length === 0 && !loading && (
                    <div className="text-center py-12">
                        <p className="text-gray-500">No contacts found</p>
                    </div>
                )}
            </div>
        </div>
    );
}
