import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Users, TrendingUp, Target, Zap, Calendar, ArrowRight, Loader2 } from 'lucide-react';

interface Contact {
  id: string;
  first_name: string;
  last_name?: string | null;
  company: string | null;
  title: string | null;
  enrichment_status: string | null;
  last_enriched?: string | null;
}

interface KPIData {
  total_contacts: number;
  enriched_count: number;
  enriched_percentage: number;
  high_icp_matches: number;
  recent_enrichments: number;
}

const API_BASE = (import.meta as any).env?.VITE_API_BASE_URL || 'https://apex-backend-i7b0.onrender.com';

export function TodaysBoard(): JSX.Element {
  const navigate = useNavigate();
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [kpis, setKpis] = useState<KPIData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchDashboardData() {
      setLoading(true);
      try {
        const res = await fetch(`${API_BASE}/api/v2/contacts?limit=100`);
        if (!res.ok) throw new Error('Failed to fetch contacts');
        
        const data = await res.json();
        const contactsList = data.contacts || data || [];
        
        setContacts(contactsList);
        
        // Calculate KPIs
        const total = contactsList.length;
        const enriched = contactsList.filter((c: Contact) => c.enrichment_status === 'enriched').length;
        const recent = contactsList.filter((c: Contact) => {
          if (!c.last_enriched) return false;
          const enrichedDate = new Date(c.last_enriched);
          const dayAgo = new Date(Date.now() - 24 * 60 * 60 * 1000);
          return enrichedDate > dayAgo;
        }).length;
        
        setKpis({
          total_contacts: total,
          enriched_count: enriched,
          enriched_percentage: total > 0 ? Math.round((enriched / total) * 100) : 0,
          high_icp_matches: 0, // TODO: Add ICP score filtering
          recent_enrichments: recent
        });
        
      } catch (err) {
        console.error('[APEX] Dashboard fetch failed', err);
      } finally {
        setLoading(false);
      }
    }
    
    fetchDashboardData();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <Loader2 className="h-8 w-8 animate-spin text-sky-400" />
      </div>
    );
  }

  const recentContacts = contacts
    .filter(c => c.enrichment_status === 'enriched')
    .slice(0, 5);

  return (
    <div className="space-y-6">
      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard
          icon={<Users className="h-5 w-5" />}
          title="Total Contacts"
          value={kpis?.total_contacts || 0}
          color="sky"
        />
        <KPICard
          icon={<TrendingUp className="h-5 w-5" />}
          title="Enriched"
          value={`${kpis?.enriched_percentage || 0}%`}
          subtitle={`${kpis?.enriched_count || 0} contacts`}
          color="emerald"
        />
        <KPICard
          icon={<Target className="h-5 w-5" />}
          title="High ICP Matches"
          value={kpis?.high_icp_matches || 0}
          color="purple"
        />
        <KPICard
          icon={<Zap className="h-5 w-5" />}
          title="Enriched Today"
          value={kpis?.recent_enrichments || 0}
          color="amber"
        />
      </div>

      {/* Recent Enrichments */}
      <div className="rounded-lg border border-slate-800 bg-slate-950/60">
        <div className="px-6 py-4 border-b border-slate-800">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-slate-100">Recently Enriched Contacts</h2>
            <button
              onClick={() => navigate('/contacts')}
              className="text-sm text-sky-400 hover:text-sky-300 flex items-center gap-1"
            >
              View All
              <ArrowRight className="h-4 w-4" />
            </button>
          </div>
        </div>
        
        <div className="divide-y divide-slate-800">
          {recentContacts.length > 0 ? (
            recentContacts.map((contact) => (
              <ContactRow key={contact.id} contact={contact} />
            ))
          ) : (
            <div className="px-6 py-12 text-center text-slate-400">
              <Calendar className="h-12 w-12 mx-auto mb-3 opacity-50" />
              <p>No recently enriched contacts</p>
              <p className="text-xs mt-1">Enrich contacts to see them appear here</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

interface KPICardProps {
  icon: React.ReactNode;
  title: string;
  value: string | number;
  subtitle?: string;
  color: 'sky' | 'emerald' | 'purple' | 'amber';
}

function KPICard({ icon, title, value, subtitle, color }: KPICardProps) {
  const colorClasses = {
    sky: 'bg-sky-500/10 text-sky-400 border-sky-500/30',
    emerald: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
    purple: 'bg-purple-500/10 text-purple-400 border-purple-500/30',
    amber: 'bg-amber-500/10 text-amber-400 border-amber-500/30'
  };

  return (
    <div className="rounded-lg border border-slate-800 bg-slate-950/60 p-4">
      <div className="flex items-start justify-between mb-3">
        <div className={`p-2 rounded-lg border ${colorClasses[color]}`}>
          {icon}
        </div>
      </div>
      <div className="text-2xl font-bold text-slate-100 mb-1">{value}</div>
      <div className="text-sm text-slate-400">{title}</div>
      {subtitle && <div className="text-xs text-slate-500 mt-1">{subtitle}</div>}
    </div>
  );
}

interface ContactRowProps {
  contact: Contact;
}

function ContactRow({ contact }: ContactRowProps) {
  const navigate = useNavigate();
  const fullName = `${contact.first_name} ${contact.last_name || ''}`.trim();

  return (
    <div
      onClick={() => navigate(`/contacts/${contact.id}`)}
      className="px-6 py-4 hover:bg-slate-800/50 cursor-pointer transition-colors"
    >
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <div className="font-medium text-slate-100">{fullName}</div>
          <div className="text-sm text-slate-400 mt-0.5">
            {contact.title || 'No title'} • {contact.company || 'No company'}
          </div>
        </div>
        <div className="flex items-center gap-3">
          {contact.last_enriched && (
            <div className="text-xs text-slate-500">
              {new Date(contact.last_enriched).toLocaleDateString()}
            </div>
          )}
          <div className="px-2 py-1 rounded text-xs bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            Enriched
          </div>
        </div>
      </div>
    </div>
  );
}
