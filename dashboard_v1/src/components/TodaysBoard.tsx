import { useEffect, useState, useCallback } from 'react';
import { ProspectCard } from './ProspectCard';
import { KPICard } from './KPICard';
import api from '../services/api';

interface Contact {
  id: number;
  name: string;
  company: string;
  email: string;
  title: string;
  urgency_tier?: string;
  urgency_label?: string;
  why_now?: string;
  contact_type?: string;
  mdcp_score?: number;
  priority_score?: number;
  enrichment_status?: 'pending' | 'processing' | 'completed' | 'failed';
  last_enriched?: string;
}

interface BoardData {
  success: boolean;
  date: string;
  time: string;
  total_actions: number;
  recommendation: string;
  relationships: {
    total: number;
    urgent_count: number;
    warm_count: number;
    nurture_count: number;
    stable_count: number;
    tiers: {
      urgent: Contact[];
      warm: Contact[];
      nurture: Contact[];
      stable: Contact[];
    };
  };
  new_prospects: {
    total: number;
    hot_count: number;
    qualified_count: number;
    potential_count: number;
    tiers: {
      hot: Contact[];
      qualified: Contact[];
      potential: Contact[];
    };
  };
}

export default function TodaysBoard() {
  const [board, setBoard] = useState<BoardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchBoard = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetch('http://localhost:8000/api/todays-board');
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      console.log('Today\'s Board API Response:', data);
      setBoard(data);
    } catch (err) {
      console.error('Failed to fetch Today\'s Board:', err);
      setError(err instanceof Error ? err.message : 'Failed to load board');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchBoard();
    const interval = setInterval(fetchBoard, 300000); // Refresh every 5 min
    return () => clearInterval(interval);
  }, [fetchBoard]);

  const handleEnrichComplete = useCallback(() => {
    // Refresh board data after enrichment
    setTimeout(() => {
      fetchBoard();
    }, 1000);
  }, [fetchBoard]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-midnight-950">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gold mx-auto mb-4"></div>
          <p className="text-text-secondary">Loading Today's Board...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 bg-midnight-950 min-h-screen">
        <div className="bg-red-900 bg-opacity-20 border border-red-500 rounded-card p-6 max-w-2xl mx-auto">
          <h3 className="text-red-400 font-semibold mb-2 text-lg">⚠️ Error Loading Board</h3>
          <p className="text-red-300 text-sm mb-2">{error}</p>
          <p className="text-red-400 text-xs mb-4">Make sure the backend is running on http://localhost:8000</p>
          <button
            onClick={fetchBoard}
            className="px-6 py-3 bg-gradient-to-r from-gold to-gold-hover text-midnight-950 font-semibold rounded-xl hover:shadow-gold-glow transition-all"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (!board) return null;

  // Extract contacts from the API structure
  const urgentContacts = board.relationships?.tiers?.urgent || [];
  const warmContacts = board.relationships?.tiers?.warm || [];
  const nurtureContacts = board.relationships?.tiers?.nurture || [];
  const stableContacts = board.relationships?.tiers?.stable || [];
  
  const hotProspects = board.new_prospects?.tiers?.hot || [];
  const qualifiedProspects = board.new_prospects?.tiers?.qualified || [];
  const potentialProspects = board.new_prospects?.tiers?.potential || [];

  // Calculate KPI metrics
  const totalHot = (board.relationships?.urgent_count || 0) + (board.new_prospects?.hot_count || 0);
  const pipelineValue = Math.round((totalHot * 45000) / 1000) / 1000; // Rough estimate
  const enrichedCount = [...urgentContacts, ...hotProspects, ...warmContacts].filter(c => c.why_now).length;
  const totalContacts = urgentContacts.length + hotProspects.length + warmContacts.length;
  const enrichmentRate = totalContacts > 0 ? Math.round((enrichedCount / totalContacts) * 100) : 0;

  return (
    <div className="min-h-screen bg-midnight-950 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-text-primary mb-2">📋 Today's Board</h1>
          <p className="text-text-secondary text-lg">{board.date} • {board.time}</p>
          <div className="mt-4 bg-blue-muted border-l-4 border-blue px-6 py-4 rounded-lg">
            <p className="text-blue font-semibold">{board.recommendation}</p>
          </div>
        </div>

        {/* KPI Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-12">
          <KPICard
            label="Total Actions Today"
            value={board.total_actions}
            trend={{ value: 15, isPositive: true }}
            delay={0}
          />
          <KPICard
            label="Hot Prospects"
            value={totalHot}
            delay={0.1}
          />
          <KPICard
            label="Est. Pipeline"
            value={`$${pipelineValue}M`}
            trend={{ value: 23, isPositive: true }}
            delay={0.2}
          />
          <KPICard
            label="AI Enrichment"
            value={`${enrichmentRate}%`}
            trend={{ value: enrichmentRate - 75, isPositive: enrichmentRate >= 75 }}
            delay={0.3}
          />
        </div>

        {/* Urgent Relationships */}
        {urgentContacts.length > 0 && (
          <section className="mb-12">
            <div className="flex items-center gap-3 mb-6">
              <h2 className="text-2xl font-bold text-red">🔥 URGENT</h2>
              <span className="text-text-secondary">
                {urgentContacts.length} Relationship{urgentContacts.length !== 1 ? 's' : ''} Going Cold
              </span>
            </div>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {urgentContacts.map(contact => (
                <ProspectCard
                  key={contact.id}
                  id={contact.id}
                  name={contact.name}
                  company={contact.company}
                  email={contact.email}
                  score={contact.mdcp_score || contact.priority_score || 50}
                  aiReason={contact.why_now}
                  enrichmentStatus={contact.enrichment_status || (contact.why_now ? 'completed' : 'none')}
                  lastEnriched={contact.last_enriched}
                  tags={[contact.urgency_label || 'Urgent', contact.contact_type || 'Relationship'].filter(Boolean)}
                  onClick={() => window.location.href = `/contacts/${contact.id}`}
                  onEnrichComplete={handleEnrichComplete}
                />
              ))}
            </div>
          </section>
        )}

        {/* Hot Prospects */}
        {hotProspects.length > 0 && (
          <section className="mb-12">
            <div className="flex items-center gap-3 mb-6">
              <h2 className="text-2xl font-bold text-gold">🎯 HOT PROSPECTS</h2>
              <span className="text-text-secondary">
                {hotProspects.length} Ready to Call
              </span>
            </div>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {hotProspects.map(contact => (
                <ProspectCard
                  key={contact.id}
                  id={contact.id}
                  name={contact.name}
                  company={contact.company}
                  email={contact.email}
                  score={contact.mdcp_score || contact.priority_score || 85}
                  aiReason={contact.why_now}
                  enrichmentStatus={contact.enrichment_status || (contact.why_now ? 'completed' : 'none')}
                  lastEnriched={contact.last_enriched}
                  tags={['Hot', 'New Prospect', contact.contact_type].filter(Boolean)}
                  onClick={() => window.location.href = `/contacts/${contact.id}`}
                  onEnrichComplete={handleEnrichComplete}
                />
              ))}
            </div>
          </section>
        )}

        {/* Warm Relationships */}
        {warmContacts.length > 0 && (
          <section className="mb-12">
            <div className="flex items-center gap-3 mb-6">
              <h2 className="text-2xl font-bold text-coral">⏰ THIS WEEK</h2>
              <span className="text-text-secondary">
                {warmContacts.length} Warm Relationship{warmContacts.length !== 1 ? 's' : ''}
              </span>
            </div>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {warmContacts.slice(0, 6).map(contact => (
                <ProspectCard
                  key={contact.id}
                  id={contact.id}
                  name={contact.name}
                  company={contact.company}
                  email={contact.email}
                  score={contact.mdcp_score || contact.priority_score || 70}
                  aiReason={contact.why_now}
                  enrichmentStatus={contact.enrichment_status || (contact.why_now ? 'completed' : 'none')}
                  lastEnriched={contact.last_enriched}
                  tags={[contact.urgency_label || 'Warm', 'Relationship'].filter(Boolean)}
                  onClick={() => window.location.href = `/contacts/${contact.id}`}
                  onEnrichComplete={handleEnrichComplete}
                />
              ))}
            </div>
          </section>
        )}

        {/* Qualified Prospects */}
        {qualifiedProspects.length > 0 && (
          <section className="mb-12">
            <div className="flex items-center gap-3 mb-6">
              <h2 className="text-2xl font-bold text-blue">✅ QUALIFIED</h2>
              <span className="text-text-secondary">
                {qualifiedProspects.length} Prospect{qualifiedProspects.length !== 1 ? 's' : ''}
              </span>
            </div>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {qualifiedProspects.slice(0, 6).map(contact => (
                <ProspectCard
                  key={contact.id}
                  id={contact.id}
                  name={contact.name}
                  company={contact.company}
                  email={contact.email}
                  score={contact.mdcp_score || contact.priority_score || 75}
                  aiReason={contact.why_now}
                  enrichmentStatus={contact.enrichment_status || (contact.why_now ? 'completed' : 'none')}
                  lastEnriched={contact.last_enriched}
                  tags={['Qualified', contact.contact_type || 'Prospect'].filter(Boolean)}
                  onClick={() => window.location.href = `/contacts/${contact.id}`}
                  onEnrichComplete={handleEnrichComplete}
                />
              ))}
            </div>
          </section>
        )}

        {/* Empty State */}
        {board.total_actions === 0 && (
          <div className="text-center py-20 bg-midnight-900 rounded-card border border-midnight-600">
            <p className="text-text-secondary text-xl mb-2">No actions for today</p>
            <p className="text-text-tertiary text-sm">Enrich and score contacts to populate your board</p>
          </div>
        )}
      </div>
    </div>
  );
}