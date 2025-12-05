import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface Contact {
  id: number;
  name: string;
  email: string;
  phone: string;
  phone_mobile?: string;
  company: string;
  title: string;
  linkedin_url?: string;
  enrichment_status: string;
  mdcp_score: number;
  priority_score: number;
  mdcp_tier?: string;
  urgency_level?: string;
  executive_summary?: string;
  trigger_events?: string;
}

type SortField = 'name' | 'company' | 'mdcp_score' | 'enrichment_status';
type SortDir = 'asc' | 'desc';

export default function Contacts() {
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [sortField, setSortField] = useState<SortField>('mdcp_score');
  const [sortDir, setSortDir] = useState<SortDir>('desc');
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [filterTier, setFilterTier] = useState<string>('all');
  const navigate = useNavigate();

  useEffect(() => {
    fetchContacts();
  }, []);

  const fetchContacts = async () => {
    try {
      const res = await fetch(`${API_URL}/api/contacts?limit=500`);
      const data = await res.json();
      setContacts(data.contacts || []);
    } catch (err) {
      console.error('Failed to fetch contacts:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDir(sortDir === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDir('desc');
    }
  };

  const getTier = (score: number): string => {
    if (score >= 80) return 'HOT';
    if (score >= 60) return 'WARM';
    if (score >= 40) return 'COOL';
    return 'COLD';
  };

  const getTierColor = (tier: string) => {
    switch (tier) {
      case 'HOT': return 'from-rose-500 to-orange-500';
      case 'WARM': return 'from-amber-500 to-yellow-500';
      case 'COOL': return 'from-azure-500 to-cyan-500';
      default: return 'from-slate-500 to-slate-600';
    }
  };

  const getTierBg = (tier: string) => {
    switch (tier) {
      case 'HOT': return 'bg-rose-500/10 border-rose-500/30 text-rose-400';
      case 'WARM': return 'bg-amber-500/10 border-amber-500/30 text-amber-400';
      case 'COOL': return 'bg-azure-500/10 border-azure-500/30 text-azure-400';
      default: return 'bg-slate-500/10 border-slate-500/30 text-slate-400';
    }
  };

  const filtered = contacts
    .filter(c => {
      const matchesSearch = 
        c.name?.toLowerCase().includes(search.toLowerCase()) ||
        c.company?.toLowerCase().includes(search.toLowerCase()) ||
        c.email?.toLowerCase().includes(search.toLowerCase());
      
      const matchesStatus = filterStatus === 'all' || c.enrichment_status === filterStatus;
      
      const tier = getTier(c.mdcp_score || c.priority_score || 0);
      const matchesTier = filterTier === 'all' || tier === filterTier;
      
      return matchesSearch && matchesStatus && matchesTier;
    })
    .sort((a, b) => {
      let aVal: any, bVal: any;
      
      switch (sortField) {
        case 'name':
          aVal = a.name?.toLowerCase() || '';
          bVal = b.name?.toLowerCase() || '';
          break;
        case 'company':
          aVal = a.company?.toLowerCase() || '';
          bVal = b.company?.toLowerCase() || '';
          break;
        case 'mdcp_score':
          aVal = a.mdcp_score || a.priority_score || 0;
          bVal = b.mdcp_score || b.priority_score || 0;
          break;
        case 'enrichment_status':
          aVal = a.enrichment_status || '';
          bVal = b.enrichment_status || '';
          break;
        default:
          return 0;
      }
      
      if (sortDir === 'asc') {
        return aVal > bVal ? 1 : -1;
      } else {
        return aVal < bVal ? 1 : -1;
      }
    });

  if (loading) {
    return (
      <div className="col-span-12 flex items-center justify-center h-64">
        <div className="animate-spin h-8 w-8 border-2 border-azure-500 border-t-transparent rounded-full" />
      </div>
    );
  }

  return (
    <>
      {/* Header */}
      <div className="col-span-12 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-50">Contacts</h1>
          <p className="text-sm text-slate-400">{contacts.length} total contacts</p>
        </div>
        <div className="flex items-center gap-2 text-sm">
          <span className="text-slate-500">Showing</span>
          <span className="text-azure-400 font-semibold">{filtered.length}</span>
          <span className="text-slate-500">of {contacts.length}</span>
        </div>
      </div>

      {/* Filters Bar */}
      <div className="col-span-12 bg-void-850 border border-glass-border rounded-xl p-4">
        <div className="flex flex-wrap items-center gap-4">
          <div className="flex-1 min-w-[200px]">
            <input
              type="text"
              placeholder="Search name, company, email..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full bg-void-900 border border-glass-border rounded-lg px-4 py-2 text-slate-100 placeholder-slate-500 focus:outline-none focus:border-azure-500/50 transition-colors"
            />
          </div>

          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="bg-void-900 border border-glass-border rounded-lg px-4 py-2 text-slate-100 focus:outline-none focus:border-azure-500/50"
          >
            <option value="all">All Status</option>
            <option value="completed">✓ Enriched</option>
            <option value="pending">⏳ Pending</option>
            <option value="failed">✗ Failed</option>
          </select>

          <select
            value={filterTier}
            onChange={(e) => setFilterTier(e.target.value)}
            className="bg-void-900 border border-glass-border rounded-lg px-4 py-2 text-slate-100 focus:outline-none focus:border-azure-500/50"
          >
            <option value="all">All Tiers</option>
            <option value="HOT">🔥 Hot</option>
            <option value="WARM">⚡ Warm</option>
            <option value="COOL">❄️ Cool</option>
            <option value="COLD">🧊 Cold</option>
          </select>

          <div className="flex items-center gap-1 bg-void-900 rounded-lg p-1 border border-glass-border">
            {(['mdcp_score', 'name', 'company'] as SortField[]).map((field) => (
              <button
                key={field}
                onClick={() => handleSort(field)}
                className={`px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
                  sortField === field
                    ? 'bg-azure-600 text-white'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                {field === 'mdcp_score' ? 'Score' : field.charAt(0).toUpperCase() + field.slice(1)}
                {sortField === field && (
                  <span className="ml-1">{sortDir === 'desc' ? '↓' : '↑'}</span>
                )}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Contact Cards Grid */}
      <div className="col-span-12 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filtered.map((contact) => {
          const score = contact.mdcp_score || contact.priority_score || 0;
          const tier = getTier(score);
          
          return (
            <div
              key={contact.id}
              onClick={() => navigate(`/contacts/${contact.id}`)}
              className="group relative bg-void-850 border border-glass-border rounded-2xl overflow-hidden cursor-pointer hover:border-azure-500/50 transition-all duration-300 hover:shadow-[0_0_30px_rgba(59,130,246,0.1)]"
            >
              {/* Top Gradient Bar */}
              <div className={`h-1 bg-gradient-to-r ${getTierColor(tier)}`} />
              
              {/* Card Content */}
              <div className="p-5">
                {/* Header Row */}
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1 min-w-0">
                    <h3 className="font-semibold text-lg text-slate-50 truncate group-hover:text-azure-300 transition-colors">
                      {contact.name}
                    </h3>
                    <p className="text-sm text-slate-400 truncate">{contact.title}</p>
                  </div>
                  
                  {/* Score Circle */}
                  <div className="relative ml-4">
                    <div className={`w-14 h-14 rounded-full bg-gradient-to-br ${getTierColor(tier)} p-[2px]`}>
                      <div className="w-full h-full rounded-full bg-void-900 flex items-center justify-center">
                        <span className="text-lg font-bold text-slate-50">{score.toFixed(0)}</span>
                      </div>
                    </div>
                    <div className={`absolute -bottom-1 left-1/2 -translate-x-1/2 px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider border ${getTierBg(tier)}`}>
                      {tier}
                    </div>
                  </div>
                </div>

                {/* Company */}
                <div className="flex items-center gap-2 mb-3">
                  <div className="w-8 h-8 rounded-lg bg-void-900 border border-glass-border flex items-center justify-center text-xs font-bold text-slate-400">
                    {contact.company?.charAt(0) || '?'}
                  </div>
                  <span className="text-sm text-slate-300 truncate">{contact.company}</span>
                </div>

                {/* Contact Info - Email, Phone, Mobile, LinkedIn */}
                <div className="grid grid-cols-2 gap-2 text-xs mb-3">
                  {contact.email && (
                    <div className="flex items-center gap-1.5 text-slate-400 truncate">
                      <span className="text-azure-500">✉</span>
                      <span className="truncate">{contact.email}</span>
                    </div>
                  )}
                  {contact.phone && (
                    <div className="flex items-center gap-1.5 text-slate-400">
                      <span className="text-azure-500">☎</span>
                      <span>{contact.phone}</span>
                    </div>
                  )}
                  {contact.phone_mobile && (
                    <div className="flex items-center gap-1.5 text-slate-400">
                      <span className="text-azure-500">📱</span>
                      <span>{contact.phone_mobile}</span>
                    </div>
                  )}
                  {contact.linkedin_url && (
                    <a 
                      href={contact.linkedin_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      onClick={(e) => e.stopPropagation()}
                      className="flex items-center gap-1.5 text-azure-400 hover:text-azure-300"
                    >
                      <span className="font-bold">in</span>
                      <span>LinkedIn →</span>
                    </a>
                  )}
                </div>

                {/* Enrichment Preview */}
                {contact.executive_summary && (
                  <div className="bg-void-900/50 border border-glass-border rounded-lg p-2 mb-3">
                    <p className="text-xs text-slate-400 line-clamp-2">
                      {contact.executive_summary.substring(0, 120)}...
                    </p>
                  </div>
                )}

                {/* Trigger Event Badge */}
                {contact.trigger_events && (
                  <div className="bg-amber-500/10 border border-amber-500/30 rounded-lg px-2 py-1 mb-3">
                    <p className="text-xs text-amber-400 truncate">
                      🔥 {contact.trigger_events.split('\n')[0]?.substring(0, 60)}...
                    </p>
                  </div>
                )}

                {/* Footer */}
                <div className="flex items-center justify-between pt-3 border-t border-glass-border">
                  <div className="flex items-center gap-2">
                    {contact.enrichment_status === 'completed' ? (
                      <span className="px-2 py-1 bg-emerald-500/10 text-emerald-400 rounded-md text-xs border border-emerald-500/30">
                        ✓ Enriched
                      </span>
                    ) : (
                      <span className="px-2 py-1 bg-slate-500/10 text-slate-400 rounded-md text-xs border border-slate-500/30">
                        ⏳ Pending
                      </span>
                    )}
                  </div>
                  <span className="text-xs text-slate-500 group-hover:text-azure-400 transition-colors">
                    View Details →
                  </span>
                </div>
              </div>

              {/* Hover Glow Effect */}
              <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none">
                <div className="absolute inset-0 bg-gradient-to-t from-azure-600/5 to-transparent" />
              </div>
            </div>
          );
        })}
      </div>

      {/* Empty State */}
      {filtered.length === 0 && (
        <div className="col-span-12 text-center py-12">
          <div className="text-4xl mb-4">🔍</div>
          <h3 className="text-lg font-semibold text-slate-300 mb-2">No contacts found</h3>
          <p className="text-slate-500">Try adjusting your search or filters</p>
        </div>
      )}
    </>
  );
}
