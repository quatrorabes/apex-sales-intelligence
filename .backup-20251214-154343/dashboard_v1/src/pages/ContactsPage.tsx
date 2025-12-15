import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    Users, Search, RefreshCw, Download, CheckCircle2,
    Clock, AlertCircle, ChevronRight, Loader2
} from 'lucide-react';

interface Contact {
    id: number;
    first_name: string;
    last_name: string;
    email: string;
    company: string;
    title: string;
    enrichment_status: string;
    last_enriched: string | null;
}

export default function ContactsPage() {
    const navigate = useNavigate();
    const [contacts, setContacts] = useState<Contact[]>([]);
    const [loading, setLoading] = useState(true);
    const [search, setSearch] = useState('');
    const [generatingId, setGeneratingId] = useState<number | null>(null);

    useEffect(() => {
        fetchContacts();
    }, []);

    const fetchContacts = async () => {
        try {
            const response = await fetch('https://apex-backend-i7b0.onrender.com/api/v2/contacts');
            const data = await response.json();
            setContacts(data.contacts || data);
        } catch (error) {
            console.error('Error fetching contacts:', error);
        } finally {
            setLoading(false);
        }
    };

    const generatePersona = async (e: React.MouseEvent, contactId: number) => {
        e.stopPropagation(); // Prevent row click
        setGeneratingId(contactId);
        
        try {
            const response = await fetch(`https://apex-backend-i7b0.onrender.com/api/v2/contacts/${contactId}/generate-persona`, {
                method: 'POST'
            });
            
            if (response.ok) {
                const data = await response.json();
                // Open landscape PDF in new tab
                if (data.files?.pdf_landscape) {
                    window.open(`https://apex-backend-i7b0.onrender.com/api/download?path=${encodeURIComponent(data.files.pdf_landscape)}`, '_blank');
                }
            }
        } catch (error) {
            console.error('Error generating persona:', error);
        } finally {
            setGeneratingId(null);
        }
    };

    const filteredContacts = contacts.filter(c => {
        const searchLower = search.toLowerCase();
        return (
            c.first_name.toLowerCase().includes(searchLower) ||
            c.last_name.toLowerCase().includes(searchLower) ||
            c.email.toLowerCase().includes(searchLower) ||
            c.company.toLowerCase().includes(searchLower)
        );
    });

    const getStatusBadge = (status: string) => {
        switch (status) {
            case 'enriched':
                return (
                    <span className="px-2 py-1 bg-green-500/20 text-green-400 rounded-full text-xs flex items-center gap-1">
                        <CheckCircle2 size={12} />
                        Enriched
                    </span>
                );
            case 'pending':
                return (
                    <span className="px-2 py-1 bg-yellow-500/20 text-yellow-400 rounded-full text-xs flex items-center gap-1">
                        <Clock size={12} />
                        Pending
                    </span>
                );
            default:
                return (
                    <span className="px-2 py-1 bg-gray-500/20 text-gray-400 rounded-full text-xs flex items-center gap-1">
                        <AlertCircle size={12} />
                        Not Enriched
                    </span>
                );
        }
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-[#0f1114] flex items-center justify-center">
                <div className="animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-blue-500"></div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-[#0f1114] text-[#f5f5f5]">
            {/* Header */}
            <div className="bg-[#1a1d21] border-b border-[rgba(255,255,255,0.06)]">
                <div className="max-w-7xl mx-auto px-6 py-6">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            <Users size={28} className="text-blue-400" />
                            <h1 className="text-2xl font-bold">Contacts</h1>
                            <span className="px-2 py-1 bg-blue-500/20 text-blue-400 rounded-full text-sm">
                                {contacts.length}
                            </span>
                        </div>
                        
                        <button
                            onClick={fetchContacts}
                            className="px-3 py-2 bg-[rgba(255,255,255,0.05)] hover:bg-[rgba(255,255,255,0.1)] rounded-lg text-sm flex items-center gap-2 transition-colors"
                        >
                            <RefreshCw size={16} />
                            Refresh
                        </button>
                    </div>
                    
                    {/* Search */}
                    <div className="mt-4 relative">
                        <Search size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-[#6b7280]" />
                        <input
                            type="text"
                            placeholder="Search contacts..."
                            value={search}
                            onChange={(e) => setSearch(e.target.value)}
                            className="w-full pl-10 pr-4 py-2.5 bg-[#0f1114] border border-[rgba(255,255,255,0.1)] rounded-lg text-[#f5f5f5] placeholder-[#6b7280] focus:outline-none focus:border-blue-500 transition-colors"
                        />
                    </div>
                </div>
            </div>

            {/* Contacts Table */}
            <div className="max-w-7xl mx-auto px-6 py-6">
                <div className="bg-[#1a1d21] border border-[rgba(255,255,255,0.08)] rounded-xl overflow-hidden">
                    <table className="w-full">
                        <thead>
                            <tr className="border-b border-[rgba(255,255,255,0.06)]">
                                <th className="text-left px-6 py-4 text-[#9ca3af] font-medium text-sm">Name</th>
                                <th className="text-left px-6 py-4 text-[#9ca3af] font-medium text-sm">Title</th>
                                <th className="text-left px-6 py-4 text-[#9ca3af] font-medium text-sm">Company</th>
                                <th className="text-left px-6 py-4 text-[#9ca3af] font-medium text-sm">Status</th>
                                <th className="text-left px-6 py-4 text-[#9ca3af] font-medium text-sm">Actions</th>
                                <th className="px-6 py-4"></th>
                            </tr>
                        </thead>
                        <tbody>
                            {filteredContacts.map((contact) => (
                                <tr
                                    key={contact.id}
                                    onClick={() => navigate(`/contact/${contact.id}`)}
                                    className="border-b border-[rgba(255,255,255,0.03)] hover:bg-[rgba(255,255,255,0.02)] cursor-pointer transition-colors"
                                >
                                    <td className="px-6 py-4">
                                        <div className="flex items-center gap-3">
                                            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white text-sm font-bold">
                                                {contact.first_name[0]}{contact.last_name[0]}
                                            </div>
                                            <div>
                                                <p className="text-[#f5f5f5] font-medium">{contact.first_name} {contact.last_name}</p>
                                                <p className="text-[#6b7280] text-sm">{contact.email}</p>
                                            </div>
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 text-[#c9cdd3] text-sm">{contact.title}</td>
                                    <td className="px-6 py-4 text-blue-400 text-sm">{contact.company}</td>
                                    <td className="px-6 py-4">{getStatusBadge(contact.enrichment_status)}</td>
                                    <td className="px-6 py-4">
                                        {contact.enrichment_status === 'enriched' && (
                                            <button
                                                onClick={(e) => generatePersona(e, contact.id)}
                                                disabled={generatingId === contact.id}
                                                className="px-3 py-1.5 bg-cyan-600/20 hover:bg-cyan-600/30 text-cyan-400 rounded-lg text-xs flex items-center gap-1.5 transition-colors disabled:opacity-50"
                                            >
                                                {generatingId === contact.id ? (
                                                    <>
                                                        <Loader2 size={12} className="animate-spin" />
                                                        Generating...
                                                    </>
                                                ) : (
                                                    <>
                                                        <Download size={12} />
                                                        Download PDF
                                                    </>
                                                )}
                                            </button>
                                        )}
                                    </td>
                                    <td className="px-6 py-4">
                                        <ChevronRight size={18} className="text-[#4b5563]" />
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                    
                    {filteredContacts.length === 0 && (
                        <div className="text-center py-12">
                            <Users size={48} className="mx-auto text-[#4b5563] mb-4" />
                            <p className="text-[#9ca3af]">No contacts found</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
