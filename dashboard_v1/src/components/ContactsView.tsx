import { useState, useEffect, useRef } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { 
    Users, Grid, List, Columns, Search, Filter, RefreshCw,
    Loader2, ChevronLeft, Building2, Mail, Phone, Zap,
    ChevronRight, MoreHorizontal, Star, Clock, Target,
    ArrowUpDown, Check, X, Download, Upload, Sparkles,
    Eye, EyeOff, SlidersHorizontal, LayoutGrid, Trash2,
    UserPlus, Send, Linkedin, GripVertical, ChevronDown,
    BarChart3, TrendingUp, AlertCircle
} from 'lucide-react';

const API_URL = 'https://apex-backend-i7b0.onrender.com';

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
    apex_enrichment_data?: string;
    linkedin_url?: string;
}

type ViewMode = 'table' | 'cards' | 'kanban' | 'compact';
type SortField = 'name' | 'company' | 'match_score' | 'enriched_at' | 'title';

export default function ContactsView() {
    const [searchParams, setSearchParams] = useSearchParams();
    const [contacts, setContacts] = useState<Contact[]>([]);
    const [loading, setLoading] = useState(true);
    const [view, setView] = useState<ViewMode>((searchParams.get('view') as ViewMode) || 'table');
    const [search, setSearch] = useState('');
    const [sortField, setSortField] = useState<SortField>('match_score');
    const [sortDir, setSortDir] = useState<'asc' | 'desc'>('desc');
    const [filterTier, setFilterTier] = useState<string>('all');
    const [filterEnriched, setFilterEnriched] = useState<string>('all');
    const [selectedIds, setSelectedIds] = useState<Set<number>>(new Set());
    const [showFilters, setShowFilters] = useState(false);
    const [draggedContact, setDraggedContact] = useState<Contact | null>(null);
    const [dragOverTier, setDragOverTier] = useState<string | null>(null);
    const [quickViewId, setQuickViewId] = useState<number | null>(null);
    const [bulkAction, setBulkAction] = useState<string>('');
    const [actionLoading, setActionLoading] = useState(false);
    const [notification, setNotification] = useState<{type: 'success' | 'error', message: string} | null>(null);
    const [page, setPage] = useState(1);
    const [totalContacts, setTotalContacts] = useState(0);
    const pageSize = 50;
    
    useEffect(() => {
        fetchContacts();
    }, [page]);
    

    useEffect(() => {
        fetchContacts();
    }, []);

    useEffect(() => {
        setSearchParams({ view });
    }, [view]);

    useEffect(() => {
        if (notification) {
            const timer = setTimeout(() => setNotification(null), 3000);
            return () => clearTimeout(timer);
        }
    }, [notification]);

    const fetchContacts = async () => {
        try {
            setLoading(true);
            const offset = (page - 1) * pageSize;
            const res = await fetch(`${API_URL}/api/contacts?limit=${pageSize}&offset=${offset}`);
            const data = await res.json();
            setContacts(data.contacts || data || []);
            setTotalContacts(data.total || data.contacts?.length || 0);
        } catch (e) {
            console.error('Fetch error:', e);
        } finally {
            setLoading(false);
        }
    };
                
    const getDisplayName = (c: Contact) => {
        if (c.name) return c.name;
        return `${c.first_name || ''} ${c.last_name || ''}`.trim() || 'Unknown';
    };

    const filteredContacts = contacts
        .filter(c => {
            const name = getDisplayName(c).toLowerCase();
            const company = (c.company || '').toLowerCase();
            const title = (c.title || '').toLowerCase();
            const q = search.toLowerCase();
            const matchesSearch = name.includes(q) || company.includes(q) || title.includes(q);
            const matchesTier = filterTier === 'all' || c.match_tier === filterTier;
            const matchesEnriched = filterEnriched === 'all' ||
                (filterEnriched === 'yes' && !!c.apex_enrichment_data) ||
                (filterEnriched === 'no' && !c.apex_enrichment_data);
            return matchesSearch && matchesTier && matchesEnriched;
        })
        .sort((a, b) => {
            let aVal: any, bVal: any;
            if (sortField === 'name') {
                aVal = getDisplayName(a).toLowerCase();
                bVal = getDisplayName(b).toLowerCase();
            } else if (sortField === 'company') {
                aVal = (a.company || '').toLowerCase();
                bVal = (b.company || '').toLowerCase();
            } else if (sortField === 'title') {
                aVal = (a.title || '').toLowerCase();
                bVal = (b.title || '').toLowerCase();
            } else if (sortField === 'match_score') {
                aVal = a.match_score || 0;
                bVal = b.match_score || 0;
            } else {
                aVal = a.enriched_at || '';
                bVal = b.enriched_at || '';
            }
            if (sortDir === 'asc') return aVal > bVal ? 1 : -1;
            return aVal < bVal ? 1 : -1;
        });

    const tierColors: Record<string, string> = {
        HIGH: 'bg-green-500/20 text-green-400 border-green-500/50',
        MEDIUM: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/50',
        LOW: 'bg-orange-500/20 text-orange-400 border-orange-500/50',
        MINIMAL: 'bg-red-500/20 text-red-400 border-red-500/50',
    };

    const kanbanColumns = [
        { id: 'HIGH', label: 'High Priority', color: 'border-t-green-500', bg: 'bg-green-500/5' },
        { id: 'MEDIUM', label: 'Medium', color: 'border-t-yellow-500', bg: 'bg-yellow-500/5' },
        { id: 'LOW', label: 'Low', color: 'border-t-orange-500', bg: 'bg-orange-500/5' },
        { id: 'MINIMAL', label: 'Unscored', color: 'border-t-gray-600', bg: 'bg-gray-500/5' },
    ];

    const toggleSelect = (id: number) => {
        const newSet = new Set(selectedIds);
        if (newSet.has(id)) newSet.delete(id);
        else newSet.add(id);
        setSelectedIds(newSet);
    };

    const selectAll = () => {
        if (selectedIds.size === filteredContacts.length) {
            setSelectedIds(new Set());
        } else {
            setSelectedIds(new Set(filteredContacts.map(c => c.id)));
        }
    };

    // Drag & Drop handlers
    const handleDragStart = (e: React.DragEvent, contact: Contact) => {
        setDraggedContact(contact);
        e.dataTransfer.effectAllowed = 'move';
        e.dataTransfer.setData('text/plain', contact.id.toString());
    };

    const handleDragOver = (e: React.DragEvent, tier: string) => {
        e.preventDefault();
        e.dataTransfer.dropEffect = 'move';
        setDragOverTier(tier);
    };

    const handleDragLeave = () => {
        setDragOverTier(null);
    };

    const handleDrop = async (e: React.DragEvent, newTier: string) => {
        e.preventDefault();
        setDragOverTier(null);
        
        if (!draggedContact) return;
        
        // Update locally first (optimistic)
        setContacts(prev => prev.map(c => 
            c.id === draggedContact.id ? { ...c, match_tier: newTier } : c
        ));
        
        // Update on server
        try {
            await fetch(`${API_URL}/api/contacts/${draggedContact.id}/tier`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ tier: newTier })
            });
            setNotification({ type: 'success', message: `Moved ${getDisplayName(draggedContact)} to ${newTier}` });
        } catch (e) {
            // Revert on error
            fetchContacts();
            setNotification({ type: 'error', message: 'Failed to update tier' });
        }
        
        setDraggedContact(null);
    };

    // Bulk actions
    const handleBulkAction = async (action: string) => {
        if (selectedIds.size === 0) return;
        setActionLoading(true);
        
        try {
            if (action === 'enrich') {
                const ids = Array.from(selectedIds).slice(0, 5);
                await fetch(`${API_URL}/api/batch/enrich`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ contact_ids: ids })
                });
                setNotification({ type: 'success', message: `Enriching ${ids.length} contacts...` });
            } else if (action === 'rescore') {
                await fetch(`${API_URL}/api/batch/rescore`, { method: 'POST' });
                setNotification({ type: 'success', message: 'Re-scoring all contacts...' });
            } else if (action === 'export') {
                exportContacts();
            }
            fetchContacts();
        } catch (e) {
            setNotification({ type: 'error', message: 'Action failed' });
        } finally {
            setActionLoading(false);
            setBulkAction('');
        }
    };

    const exportContacts = () => {
        const exportData = filteredContacts.filter(c => selectedIds.has(c.id) || selectedIds.size === 0);
        const csv = [
            ['Name', 'Title', 'Company', 'Email', 'Phone', 'Match Score', 'Tier', 'LinkedIn'].join(','),
            ...exportData.map(c => [
                getDisplayName(c),
                c.title || '',
                c.company || '',
                c.email || '',
                c.phone || '',
                c.match_score || '',
                c.match_tier || '',
                c.linkedin_url || ''
            ].map(v => `"${v}"`).join(','))
        ].join('\n');
        
        const blob = new Blob([csv], { type: 'text/csv' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `apex-contacts-${new Date().toISOString().split('T')[0]}.csv`;
        a.click();
        setNotification({ type: 'success', message: `Exported ${exportData.length} contacts` });
    };

    // Quick View Modal
    const QuickViewModal = ({ contact }: { contact: Contact }) => (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50" onClick={() => setQuickViewId(null)}>
            <div className="bg-[#1e2228] rounded-2xl border border-gray-700 w-full max-w-lg mx-4 overflow-hidden" onClick={e => e.stopPropagation()}>
                <div className="p-6 border-b border-gray-800">
                    <div className="flex items-start justify-between">
                        <div>
                            <h2 className="text-xl font-bold text-white">{getDisplayName(contact)}</h2>
                            <p className="text-gray-400">{contact.title}</p>
                            <p className="text-blue-400 flex items-center gap-1 mt-1">
                                <Building2 size={14} /> {contact.company}
                            </p>
                        </div>
                        <div className="text-right">
                            <div className="text-4xl font-bold text-white">{Math.round(contact.match_score || 0)}</div>
                            {contact.match_tier && (
                                <span className={`px-2 py-1 rounded border text-xs font-bold ${tierColors[contact.match_tier]}`}>
                                    {contact.match_tier}
                                </span>
                            )}
                        </div>
                    </div>
                </div>
                
                <div className="p-6 space-y-4">
                    {/* Score Breakdown */}
                    <div className="grid grid-cols-3 gap-3">
                        <div className="bg-[#0f1114] rounded-lg p-3 text-center">
                            <p className="text-2xl font-bold text-green-400">{Math.round(contact.fit_score || 0)}</p>
                            <p className="text-gray-500 text-xs">FIT</p>
                        </div>
                        <div className="bg-[#0f1114] rounded-lg p-3 text-center">
                            <p className="text-2xl font-bold text-blue-400">{Math.round(contact.relevance_score || 0)}</p>
                            <p className="text-gray-500 text-xs">RELEVANCE</p>
                        </div>
                        <div className="bg-[#0f1114] rounded-lg p-3 text-center">
                            <p className="text-2xl font-bold text-orange-400">{Math.round(contact.timing_score || 0)}</p>
                            <p className="text-gray-500 text-xs">TIMING</p>
                        </div>
                    </div>
                    
                    {/* Contact Info */}
                    <div className="space-y-2">
                        {contact.email && (
                            <a href={`mailto:${contact.email}`} className="flex items-center gap-2 text-gray-300 hover:text-white">
                                <Mail size={16} className="text-gray-500" /> {contact.email}
                            </a>
                        )}
                        {contact.phone && (
                            <a href={`tel:${contact.phone}`} className="flex items-center gap-2 text-gray-300 hover:text-white">
                                <Phone size={16} className="text-gray-500" /> {contact.phone}
                            </a>
                        )}
                        {contact.linkedin_url && (
                            <a href={contact.linkedin_url} target="_blank" className="flex items-center gap-2 text-blue-400 hover:text-blue-300">
                                <Linkedin size={16} /> View LinkedIn
                            </a>
                        )}
                    </div>
                </div>
                
                <div className="p-4 bg-[#0f1114] border-t border-gray-800 flex items-center gap-3">
                    <Link 
                        to={`/contacts/${contact.id}`}
                        className="flex-1 bg-purple-600 hover:bg-purple-700 text-center py-2 rounded-lg font-medium"
                    >
                        Full Profile
                    </Link>
                    <button 
                        onClick={() => setQuickViewId(null)}
                        className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg"
                    >
                        Close
                    </button>
                </div>
            </div>
        </div>
    );

    // ===================
    // TABLE VIEW
    // ===================
    const TableView = () => (
        <div className="bg-[#1e2228] rounded-xl border border-gray-800 overflow-hidden">
            <div className="overflow-x-auto">
                <table className="w-full">
                    <thead className="bg-[#0f1114] border-b border-gray-800">
                        <tr>
                            <th className="px-4 py-3 text-left w-10">
                                <input 
                                    type="checkbox" 
                                    checked={selectedIds.size === filteredContacts.length && filteredContacts.length > 0}
                                    onChange={selectAll}
                                    className="rounded bg-gray-700 border-gray-600"
                                />
                            </th>
                            <th 
                                className="px-4 py-3 text-left text-gray-400 text-sm font-medium cursor-pointer hover:text-white group"
                                onClick={() => { setSortField('name'); setSortDir(d => d === 'asc' ? 'desc' : 'asc'); }}
                            >
                                <span className="flex items-center gap-1">
                                    Name 
                                    <ArrowUpDown size={14} className={sortField === 'name' ? 'text-purple-400' : 'opacity-0 group-hover:opacity-100'} />
                                </span>
                            </th>
                            <th 
                                className="px-4 py-3 text-left text-gray-400 text-sm font-medium cursor-pointer hover:text-white group"
                                onClick={() => { setSortField('company'); setSortDir(d => d === 'asc' ? 'desc' : 'asc'); }}
                            >
                                <span className="flex items-center gap-1">
                                    Company 
                                    <ArrowUpDown size={14} className={sortField === 'company' ? 'text-purple-400' : 'opacity-0 group-hover:opacity-100'} />
                                </span>
                            </th>
                            <th 
                                className="px-4 py-3 text-left text-gray-400 text-sm font-medium cursor-pointer hover:text-white group"
                                onClick={() => { setSortField('title'); setSortDir(d => d === 'asc' ? 'desc' : 'asc'); }}
                            >
                                <span className="flex items-center gap-1">
                                    Title
                                    <ArrowUpDown size={14} className={sortField === 'title' ? 'text-purple-400' : 'opacity-0 group-hover:opacity-100'} />
                                </span>
                            </th>
                            <th 
                                className="px-4 py-3 text-center text-gray-400 text-sm font-medium cursor-pointer hover:text-white group"
                                onClick={() => { setSortField('match_score'); setSortDir(d => d === 'asc' ? 'desc' : 'asc'); }}
                            >
                                <span className="flex items-center justify-center gap-1">
                                    Score 
                                    <ArrowUpDown size={14} className={sortField === 'match_score' ? 'text-purple-400' : 'opacity-0 group-hover:opacity-100'} />
                                </span>
                            </th>
                            <th className="px-4 py-3 text-center text-gray-400 text-sm font-medium">Tier</th>
                            <th className="px-4 py-3 text-center text-gray-400 text-sm font-medium">Contact</th>
                            <th className="px-4 py-3 text-center text-gray-400 text-sm font-medium">Status</th>
                            <th className="px-4 py-3 w-20"></th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-800">
                        {filteredContacts.map(c => (
                            <tr key={c.id} className="hover:bg-gray-800/50 transition group">
                                <td className="px-4 py-3">
                                    <input 
                                        type="checkbox"
                                        checked={selectedIds.has(c.id)}
                                        onChange={() => toggleSelect(c.id)}
                                        className="rounded bg-gray-700 border-gray-600"
                                    />
                                </td>
                                <td className="px-4 py-3">
                                    <Link to={`/contacts/${c.id}`} className="font-medium text-white hover:text-purple-400">
                                        {getDisplayName(c)}
                                    </Link>
                                </td>
                                <td className="px-4 py-3 text-gray-400">{c.company || '-'}</td>
                                <td className="px-4 py-3 text-gray-400 text-sm max-w-[200px] truncate">{c.title || '-'}</td>
                                <td className="px-4 py-3 text-center">
                                    <span className="text-xl font-bold text-white">
                                        {c.match_score !== undefined ? Math.round(c.match_score) : '-'}
                                    </span>
                                </td>
                                <td className="px-4 py-3 text-center">
                                    {c.match_tier && (
                                        <span className={`px-2 py-1 rounded border text-xs font-bold ${tierColors[c.match_tier]}`}>
                                            {c.match_tier}
                                        </span>
                                    )}
                                </td>
                                <td className="px-4 py-3">
                                    <div className="flex items-center justify-center gap-2">
                                        {c.email && (
                                            <a href={`mailto:${c.email}`} className="text-gray-500 hover:text-white">
                                                <Mail size={16} />
                                            </a>
                                        )}
                                        {c.phone && (
                                            <a href={`tel:${c.phone}`} className="text-gray-500 hover:text-white">
                                                <Phone size={16} />
                                            </a>
                                        )}
                                        {c.linkedin_url && (
                                            <a href={c.linkedin_url} target="_blank" className="text-gray-500 hover:text-blue-400">
                                                <Linkedin size={16} />
                                            </a>
                                        )}
                                    </div>
                                </td>
                                <td className="px-4 py-3 text-center">
                                    {(c.enrichment_status === 'completed' || c.apex_enrichment_data) ? (
                                        <span className="text-green-400" title="Enriched"><Check size={18} /></span>
                                    ) : (
                                        <span className="text-gray-600" title="Not enriched"><Clock size={18} /></span>
                                    )}
                                </td>
                                <td className="px-4 py-3">
                                    <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition">
                                        <button 
                                            onClick={() => setQuickViewId(c.id)}
                                            className="p-1 hover:bg-gray-700 rounded text-gray-500 hover:text-white"
                                            title="Quick View"
                                        >
                                            <Eye size={16} />
                                        </button>
                                        <Link 
                                            to={`/contacts/${c.id}`}
                                            className="p-1 hover:bg-gray-700 rounded text-gray-500 hover:text-white"
                                        >
                                            <ChevronRight size={16} />
                                        </Link>
                                    </div>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );

    // ===================
    // CARDS VIEW
    // ===================
    const CardsView = () => (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {filteredContacts.map(c => (
                <div
                    key={c.id}
                    className="bg-[#1e2228] border border-gray-800 rounded-xl overflow-hidden hover:border-gray-700 transition group relative"
                >
                    {/* Quick actions on hover */}
                    <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition flex items-center gap-1">
                        <button 
                            onClick={() => setQuickViewId(c.id)}
                            className="p-1.5 bg-gray-800 hover:bg-gray-700 rounded text-gray-400 hover:text-white"
                        >
                            <Eye size={14} />
                        </button>
                    </div>
                    
                    <Link to={`/contacts/${c.id}`} className="block p-5">
                        <div className="flex items-start justify-between mb-3">
                            <div className="flex-1 min-w-0">
                                <h3 className="font-semibold text-white truncate group-hover:text-purple-400">
                                    {getDisplayName(c)}
                                </h3>
                                <p className="text-gray-400 text-sm truncate">{c.title}</p>
                            </div>
                            {c.match_score !== undefined && (
                                <div className="text-right ml-3">
                                    <div className="text-2xl font-bold text-white">{Math.round(c.match_score)}</div>
                                </div>
                            )}
                        </div>
                        <div className="flex items-center gap-2 text-blue-400 text-sm mb-3">
                            <Building2 size={14} />
                            <span className="truncate">{c.company || 'No company'}</span>
                        </div>
                        <div className="flex items-center justify-between">
                            {c.match_tier && (
                                <span className={`px-2 py-1 rounded border text-xs font-bold ${tierColors[c.match_tier]}`}>
                                    {c.match_tier}
                                </span>
                            )}
                            <div className="flex items-center gap-2 text-gray-500">
                                {c.email && <Mail size={14} />}
                                {c.phone && <Phone size={14} />}
                                {c.linkedin_url && <Linkedin size={14} />}
                                {(c.enrichment_status === 'completed' || c.apex_enrichment_data) && <Zap size={14} className="text-purple-400" />}
                            </div>
                        </div>
                    </Link>
                    
                    {/* Score breakdown footer */}
                    {c.fit_score !== undefined && (
                        <div className="px-5 py-3 bg-[#0f1114] border-t border-gray-800 flex justify-between text-xs">
                            <span className="text-green-400">FIT: {Math.round(c.fit_score)}</span>
                            <span className="text-blue-400">REL: {Math.round(c.relevance_score || 0)}</span>
                            <span className="text-orange-400">TIME: {Math.round(c.timing_score || 0)}</span>
                        </div>
                    )}
                </div>
            ))}
        </div>
    );

    // ===================
    // KANBAN VIEW (with Drag & Drop)
    // ===================
    const KanbanView = () => (
        <div className="grid grid-cols-4 gap-4 h-[calc(100vh-220px)]">
            {kanbanColumns.map(col => {
                const colContacts = filteredContacts.filter(c => 
                    col.id === 'MINIMAL' 
                        ? (!c.match_tier || c.match_tier === 'MINIMAL')
                        : c.match_tier === col.id
                );
                const isDragOver = dragOverTier === col.id;
                
                return (
                    <div 
                        key={col.id} 
                        className="flex flex-col"
                        onDragOver={(e) => handleDragOver(e, col.id)}
                        onDragLeave={handleDragLeave}
                        onDrop={(e) => handleDrop(e, col.id)}
                    >
                        <div className={`bg-[#1e2228] rounded-t-xl border-t-4 ${col.color} px-4 py-3 border-x border-gray-800`}>
                            <div className="flex items-center justify-between">
                                <h3 className="font-semibold text-white">{col.label}</h3>
                                <span className="bg-gray-800 text-gray-400 px-2 py-0.5 rounded text-sm">
                                    {colContacts.length}
                                </span>
                            </div>
                        </div>
                        <div className={`flex-1 ${col.bg} border-x border-b border-gray-800 rounded-b-xl p-3 space-y-2 overflow-y-auto transition-all ${
                            isDragOver ? 'ring-2 ring-purple-500 ring-inset bg-purple-500/10' : ''
                        }`}>
                            {colContacts.map(c => (
                                <div
                                    key={c.id}
                                    draggable
                                    onDragStart={(e) => handleDragStart(e, c)}
                                    onDragEnd={() => setDraggedContact(null)}
                                    className={`bg-[#1e2228] border border-gray-700 rounded-lg p-3 cursor-grab active:cursor-grabbing hover:border-gray-600 transition group ${
                                        draggedContact?.id === c.id ? 'opacity-50' : ''
                                    }`}
                                >
                                    <div className="flex items-start gap-2">
                                        <GripVertical size={14} className="text-gray-600 mt-0.5 opacity-0 group-hover:opacity-100" />
                                        <div className="flex-1 min-w-0">
                                            <Link to={`/contacts/${c.id}`} className="hover:text-purple-400">
                                                <h4 className="font-medium text-white text-sm truncate">{getDisplayName(c)}</h4>
                                            </Link>
                                            <p className="text-gray-500 text-xs truncate">{c.title}</p>
                                            <p className="text-blue-400 text-xs truncate">{c.company}</p>
                                        </div>
                                    </div>
                                    <div className="flex items-center justify-between mt-2">
                                        <div className="flex items-center gap-1 text-gray-600">
                                            {c.email && <Mail size={12} />}
                                            {c.phone && <Phone size={12} />}
                                            {(c.enrichment_status === 'completed' || c.apex_enrichment_data) && <Zap size={12} className="text-purple-400" />}
                                        </div>
                                        {c.match_score !== undefined && (
                                            <span className="text-white font-bold text-sm">{Math.round(c.match_score)}</span>
                                        )}
                                    </div>
                                </div>
                            ))}
                            {colContacts.length === 0 && (
                                <div className={`text-center py-8 border-2 border-dashed rounded-lg transition ${
                                    isDragOver ? 'border-purple-500 text-purple-400' : 'border-gray-700 text-gray-600'
                                }`}>
                                    <p className="text-sm">Drop contacts here</p>
                                </div>
                            )}
                        </div>
                    </div>
                );
            })}
        </div>
    );

    // ===================
    // COMPACT VIEW
    // ===================
    const CompactView = () => (
        <div className="bg-[#1e2228] rounded-xl border border-gray-800 divide-y divide-gray-800">
            {filteredContacts.map(c => (
                <div key={c.id} className="flex items-center gap-4 px-4 py-2 hover:bg-gray-800/50 group">
                    <input 
                        type="checkbox"
                        checked={selectedIds.has(c.id)}
                        onChange={() => toggleSelect(c.id)}
                        className="rounded bg-gray-700 border-gray-600"
                    />
                    <Link to={`/contacts/${c.id}`} className="flex-1 flex items-center gap-4 min-w-0">
                        <span className="font-medium text-white truncate w-48">{getDisplayName(c)}</span>
                        <span className="text-gray-500 text-sm truncate w-32">{c.title}</span>
                        <span className="text-blue-400 text-sm truncate w-40">{c.company}</span>
                        <span className="text-white font-bold w-12 text-center">{Math.round(c.match_score || 0)}</span>
                        {c.match_tier && (
                            <span className={`px-2 py-0.5 rounded text-xs font-bold ${tierColors[c.match_tier]} w-20 text-center`}>
                                {c.match_tier}
                            </span>
                        )}
                    </Link>
                    <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100">
                        <button onClick={() => setQuickViewId(c.id)} className="p-1 text-gray-500 hover:text-white">
                            <Eye size={14} />
                        </button>
                    </div>
                </div>
            ))}
        </div>
    );

    if (loading) {
        return (
            <div className="min-h-screen bg-[#0f1114] flex items-center justify-center">
                <Loader2 className="w-8 h-8 text-purple-400 animate-spin" />
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-[#0f1114] text-white">
            {/* Notification Toast */}
            {notification && (
                <div className={`fixed top-4 right-4 z-50 px-4 py-3 rounded-lg shadow-lg flex items-center gap-2 animate-in slide-in-from-right ${
                    notification.type === 'success' ? 'bg-green-600' : 'bg-red-600'
                }`}>
                    {notification.type === 'success' ? <Check size={18} /> : <AlertCircle size={18} />}
                    {notification.message}
                </div>
            )}

            {/* Quick View Modal */}
            {quickViewId && (
                <QuickViewModal contact={contacts.find(c => c.id === quickViewId)!} />
            )}

            {/* Header */}
            <div className="bg-[#1a1d21] border-b border-gray-800 px-6 py-4">
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                        <Link to="/" className="text-gray-400 hover:text-white flex items-center gap-1">
                            <ChevronLeft size={20} /> Home
                        </Link>
                        <h1 className="text-2xl font-bold flex items-center gap-2">
                            <Users className="text-blue-400" /> Contacts
                        </h1>
                        <span className="bg-gray-800 text-gray-400 px-2 py-1 rounded text-sm">
                            {filteredContacts.length} of {contacts.length}
                        </span>
                    </div>
                    <div className="flex items-center gap-3">
                        {/* View Toggle */}
                        <div className="bg-[#0f1114] rounded-lg p-1 flex">
                            {[
                                { id: 'table', icon: <List size={18} />, label: 'Table' },
                                { id: 'cards', icon: <Grid size={18} />, label: 'Cards' },
                                { id: 'kanban', icon: <Columns size={18} />, label: 'Kanban' },
                                { id: 'compact', icon: <LayoutGrid size={18} />, label: 'Compact' },
                            ].map(v => (
                                <button
                                    key={v.id}
                                    onClick={() => setView(v.id as ViewMode)}
                                    className={`p-2 rounded transition ${view === v.id ? 'bg-purple-600 text-white' : 'text-gray-400 hover:text-white'}`}
                                    title={v.label}
                                >
                                    {v.icon}
                                </button>
                            ))}
                        </div>
                        
                        <button 
                            onClick={() => setShowFilters(!showFilters)}
                            className={`p-2 rounded-lg transition ${showFilters ? 'bg-purple-600 text-white' : 'hover:bg-gray-800 text-gray-400'}`}
                        >
                            <SlidersHorizontal size={20} />
                        </button>
                        
                        <button onClick={fetchContacts} className="p-2 hover:bg-gray-800 rounded-lg">
                            <RefreshCw size={20} className="text-gray-400" />
                        </button>
                        
                        <button 
                            onClick={exportContacts}
                            className="p-2 hover:bg-gray-800 rounded-lg text-gray-400 hover:text-white"
                            title="Export CSV"
                        >
                            <Download size={20} />
                        </button>
                    </div>
                </div>

                {/* Filters Row */}
                <div className="flex items-center gap-4 mt-4">
                    {/* Search */}
                    <div className="relative flex-1 max-w-md">
                        <Search size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
                        <input
                            type="text"
                            value={search}
                            onChange={e => setSearch(e.target.value)}
                            placeholder="Search name, company, title..."
                            className="w-full bg-[#0f1114] border border-gray-700 rounded-lg pl-10 pr-4 py-2 text-white placeholder-gray-500 focus:border-purple-500 focus:ring-1 focus:ring-purple-500"
                        />
                        {search && (
                            <button 
                                onClick={() => setSearch('')}
                                className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-white"
                            >
                                <X size={16} />
                            </button>
                        )}
                    </div>
                    
                    {/* Filters */}
                    {showFilters && (
                        <>
                            <select
                                value={filterTier}
                                onChange={e => setFilterTier(e.target.value)}
                                className="bg-[#0f1114] border border-gray-700 rounded-lg px-4 py-2 text-white"
                            >
                                <option value="all">All Tiers</option>
                                <option value="HIGH">🟢 High Priority</option>
                                <option value="MEDIUM">🟡 Medium</option>
                                <option value="LOW">🟠 Low</option>
                                <option value="MINIMAL">🔴 Minimal</option>
                            </select>
                            
                            <select
                                value={filterEnriched}
                                onChange={e => setFilterEnriched(e.target.value)}
                                className="bg-[#0f1114] border border-gray-700 rounded-lg px-4 py-2 text-white"
                            >
                                <option value="all">All Status</option>
                                <option value="yes">✅ Enriched</option>
                                <option value="no">⏳ Not Enriched</option>
                            </select>
                        </>
                    )}

                    {/* Bulk Actions */}
                    {selectedIds.size > 0 && (
                        <div className="flex items-center gap-2 bg-purple-900/30 border border-purple-500/50 rounded-lg px-4 py-2 ml-auto">
                            <span className="text-purple-300 text-sm font-medium">{selectedIds.size} selected</span>
                            <div className="w-px h-5 bg-purple-500/50" />
                            <button 
                                onClick={() => handleBulkAction('enrich')}
                                disabled={actionLoading}
                                className="text-purple-400 hover:text-white text-sm flex items-center gap-1"
                            >
                                <Zap size={14} /> Enrich
                            </button>
                            <button 
                                onClick={() => handleBulkAction('export')}
                                className="text-purple-400 hover:text-white text-sm flex items-center gap-1"
                            >
                                <Download size={14} /> Export
                            </button>
                            <button 
                                onClick={() => setSelectedIds(new Set())} 
                                className="text-gray-500 hover:text-white ml-2"
                            >
                                <X size={16} />
                            </button>
                        </div>
                    )}
                </div>
            </div>

            {/* Content */}
            <div className="p-6">
                {view === 'table' && <TableView />}
                {view === 'cards' && <CardsView />}
                {view === 'kanban' && <KanbanView />}
                {view === 'compact' && <CompactView />}

                {filteredContacts.length === 0 && (
                    <div className="text-center py-16">
                        <Users className="w-16 h-16 text-gray-700 mx-auto mb-4" />
                        <p className="text-gray-500">No contacts found</p>
                        {search && (
                            <button onClick={() => setSearch('')} className="text-purple-400 hover:text-purple-300 mt-2">
                                Clear search
                            </button>
                        )}
                    </div>
                )}
            </div>

            {/* ADD PAGINATION HERE */}
            {/* Pagination */}
            <div className="flex items-center justify-between px-6 py-4 bg-[#1a1d21] border-t border-gray-800">
                <div className="text-sm text-gray-400">
                    Showing {((page - 1) * pageSize) + 1} - {Math.min(page * pageSize, totalContacts)} of {totalContacts} contacts
                </div>
                <div className="flex items-center gap-2">
                    <button
                        onClick={() => setPage(p => Math.max(1, p - 1))}
                        disabled={page === 1}
                        className="px-3 py-1.5 bg-[#21262d] hover:bg-[#30363d] disabled:opacity-50 disabled:cursor-not-allowed rounded-lg text-sm flex items-center gap-1"
                    >
                        <ChevronLeft size={16} /> Previous
                    </button>
                    <span className="px-3 py-1.5 text-sm text-gray-300">
                        Page {page} of {Math.ceil(totalContacts / pageSize) || 1}
                    </span>
                    <button
                        onClick={() => setPage(p => p + 1)}
                        disabled={page >= Math.ceil(totalContacts / pageSize)}
                        className="px-3 py-1.5 bg-[#21262d] hover:bg-[#30363d] disabled:opacity-50 disabled:cursor-not-allowed rounded-lg text-sm flex items-center gap-1"
                    >
                        Next <ChevronRight size={16} />
                    </button>
                </div>
            </div>

        </div>
    );
}
