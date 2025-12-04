import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { API_ENDPOINTS } from '../config/api';
import enrichmentService from '../services/enrichmentService';
import { IntelligenceSection } from '../components/intelligence/IntelligenceSection';
import { OpportunityBadge } from '../components/intelligence/OpportunityBadge';
import { TriggerEventsTimeline } from '../components/intelligence/TriggerEventsTimeline';
import { StrategicHighlights } from '../components/intelligence/StrategicHighlights';

interface Contact {
  id: number;
  name: string;
  firstname: string;
  lastname: string;
  email: string;
  phone: string;
  company: string;
  title: string;
  linkedin_url?: string;
  enrichment_status?: string;
  enriched_at?: string;
  mdcp_score?: number;
  priority_score?: number;
  profile_content?: string;
  // Structured intelligence fields
  executive_summary?: string;
  professional_overview?: string;
  background_experience?: string;
  education?: string;
  personality_style?: string;
  social_presence?: string;
  company_overview?: string;
  products_services?: string;
  market_position?: string;
  leadership?: string;
  recent_activity?: string;
  trigger_events?: string;
  pain_points?: string;
  engagement_strategy?: string;
  recommended_opening?: string;
  opportunity_level?: string;
  top_reasons?: string;
  strategic_summary?: string;
  competitive_intelligence?: string;
}

export default function ContactDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [contact, setContact] = useState<Contact | null>(null);
  const [loading, setLoading] = useState(true);
  const [enriching, setEnriching] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchContact();
  }, [id]);

  const fetchContact = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_ENDPOINTS.contacts}/${id}`);
      if (!response.ok) throw new Error('Contact not found');
      const data = await response.json();
      setContact(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load contact');
    } finally {
      setLoading(false);
    }
  };

  const handleEnrich = async (reEnrich: boolean = false) => {
    if (!id) return;
    
    try {
      setEnriching(true);
      
      if (reEnrich) {
        await fetch(`${API_ENDPOINTS.contacts}/${id}/reset-enrichment`, {
          method: 'POST'
        });
      }
      
      await enrichmentService.enrichContact(parseInt(id));
      
      await enrichmentService.waitForEnrichment(
        parseInt(id),
        (status) => {
          console.log('Enrichment status:', status);
          if (status.status === 'completed') {
            fetchContact();
          }
        }
      );
    } catch (err) {
      console.error('Enrichment failed:', err);
      alert('Enrichment failed. Please try again.');
    } finally {
      setEnriching(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-midnight-950 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gold"></div>
      </div>
    );
  }

  if (error || !contact) {
    return (
      <div className="min-h-screen bg-midnight-950 p-8">
        <div className="max-w-4xl mx-auto">
          <button
            onClick={() => navigate('/todays-board')}
            className="text-gold hover:text-gold-hover mb-6"
          >
            ← Back to Today's Board
          </button>
          <div className="bg-red-900/20 border border-red-500 rounded-card p-6">
            <h2 className="text-red-400 text-xl font-semibold mb-2">Error</h2>
            <p className="text-red-300">{error || 'Contact not found'}</p>
          </div>
        </div>
      </div>
    );
  }

  const enrichmentStatus = contact.enrichment_status || 'none';
  const score = contact.mdcp_score || contact.priority_score || 0;
  const hasIntelligence = contact.executive_summary || contact.professional_overview || contact.trigger_events;

  return (
    <div className="min-h-screen bg-midnight-950 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <button
          onClick={() => navigate('/todays-board')}
          className="text-gold hover:text-gold-hover mb-6 flex items-center gap-2"
        >
          ← Back to Today's Board
        </button>

        {/* Contact Header Card */}
        <div className="bg-midnight-900 border border-midnight-700 rounded-xl p-8 mb-6">
          <div className="flex justify-between items-start mb-6">
            <div>
              <h1 className="text-4xl font-bold text-text-primary mb-2">
                {contact.name}
              </h1>
              <p className="text-xl text-text-secondary mb-1">{contact.title}</p>
              <p className="text-lg text-text-tertiary">{contact.company}</p>
            </div>
            
            <div className="text-center">
              <div className="text-5xl font-bold text-gold mb-1">{score.toFixed(0)}</div>
              <div className="text-sm text-text-secondary">MDCP Score</div>
            </div>
          </div>

          {/* Contact Info */}
          <div className="grid grid-cols-2 gap-4 mb-6">
            <div>
              <div className="text-sm text-text-tertiary mb-1">Email</div>
              <a href={`mailto:${contact.email}`} className="text-gold hover:text-gold-hover">
                {contact.email}
              </a>
            </div>
            {contact.phone && (
              <div>
                <div className="text-sm text-text-tertiary mb-1">Phone</div>
                <a href={`tel:${contact.phone}`} className="text-gold hover:text-gold-hover">
                  {contact.phone}
                </a>
              </div>
            )}
            {contact.linkedin_url && (
              <div>
                <div className="text-sm text-text-tertiary mb-1">LinkedIn</div>
                <a 
                  href={contact.linkedin_url} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-gold hover:text-gold-hover"
                >
                  View Profile →
                </a>
              </div>
            )}
          </div>

          {/* Enrichment Status & Actions */}
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <span className="text-text-secondary">Enrichment:</span>
              {enrichmentStatus === 'completed' && (
                <span className="px-3 py-1 bg-green-500/20 text-green-400 rounded-full text-sm">
                  ✓ Enriched
                </span>
              )}
              {enrichmentStatus === 'processing' && (
                <span className="px-3 py-1 bg-blue-500/20 text-blue-400 rounded-full text-sm animate-pulse">
                  ⚡ Processing...
                </span>
              )}
              {enrichmentStatus === 'pending' && (
                <span className="px-3 py-1 bg-midnight-700 text-text-tertiary rounded-full text-sm">
                  ⏳ Pending
                </span>
              )}
            </div>

            <div className="flex gap-2">
              {enrichmentStatus === 'completed' && (
                <button
                  onClick={() => handleEnrich(true)}
                  disabled={enriching}
                  className="px-4 py-2 bg-midnight-800 text-text-secondary font-semibold rounded-xl hover:bg-midnight-700 transition-all disabled:opacity-50 border border-midnight-600"
                >
                  {enriching ? '⚡ Re-Enriching...' : '🔄 Re-Enrich'}
                </button>
              )}
              
              {enrichmentStatus !== 'completed' && enrichmentStatus !== 'processing' && (
                <button
                  onClick={() => handleEnrich(false)}
                  disabled={enriching}
                  className="px-6 py-2 bg-gradient-to-r from-gold to-gold-hover text-midnight-950 font-semibold rounded-xl hover:shadow-gold-glow transition-all disabled:opacity-50"
                >
                  {enriching ? '⚡ Enriching...' : '⚡ Enrich Now'}
                </button>
              )}
            </div>

            {contact.enriched_at && (
              <span className="text-sm text-text-tertiary">
                Last enriched: {new Date(contact.enriched_at).toLocaleDateString()}
              </span>
            )}
          </div>
        </div>

        {/* STRUCTURED INTELLIGENCE DISPLAY */}
        {hasIntelligence && (
          <div className="space-y-6">
            <h2 className="text-3xl font-bold text-text-primary mb-6">🤖 AI Intelligence Profile</h2>

            {/* Strategic Highlights */}
            {(contact.recommended_opening || contact.opportunity_level || contact.top_reasons) && (
              <StrategicHighlights
                opening_line={contact.recommended_opening}
                opportunity_level={contact.opportunity_level}
                top_reasons={contact.top_reasons}
              />
            )}

            {/* Executive Summary */}
            {contact.executive_summary && (
              <IntelligenceSection
                title="Executive Summary"
                content={contact.executive_summary}
                icon="📋"
                defaultOpen={true}
              />
            )}

            {/* Trigger Events - Special Timeline Display */}
            {contact.trigger_events && (
              <div className="bg-midnight-900 border border-midnight-700 rounded-xl p-6">
                <h3 className="text-lg font-semibold text-text-primary mb-4 flex items-center gap-3">
                  <span className="text-2xl">🔥</span>
                  Trigger Events - Why Reach Out NOW
                </h3>
                <TriggerEventsTimeline content={contact.trigger_events} />
              </div>
            )}

            {/* Professional Profile Sections */}
            {contact.professional_overview && (
              <IntelligenceSection
                title="Professional Overview"
                content={contact.professional_overview}
                icon="👤"
                defaultOpen={false}
              />
            )}

            {contact.background_experience && (
              <IntelligenceSection
                title="Background & Experience"
                content={contact.background_experience}
                icon="💼"
              />
            )}

            {contact.personality_style && (
              <IntelligenceSection
                title="Personality & Working Style"
                content={contact.personality_style}
                icon="🧠"
              />
            )}

            {/* Company Intelligence */}
            {contact.company_overview && (
              <IntelligenceSection
                title="Company Overview"
                content={contact.company_overview}
                icon="🏢"
              />
            )}

            {contact.recent_activity && (
              <IntelligenceSection
                title="Recent Activity & News"
                content={contact.recent_activity}
                icon="📰"
                defaultOpen={true}
              />
            )}

            {/* Sales Intelligence */}
            {contact.pain_points && (
              <IntelligenceSection
                title="Pain Points & Challenges"
                content={contact.pain_points}
                icon="🎯"
                defaultOpen={true}
              />
            )}

            {contact.engagement_strategy && (
              <IntelligenceSection
                title="Engagement Strategy"
                content={contact.engagement_strategy}
                icon="💡"
                defaultOpen={true}
                copyable={true}
              />
            )}

            {contact.competitive_intelligence && (
              <IntelligenceSection
                title="Competitive Intelligence"
                content={contact.competitive_intelligence}
                icon="🔍"
              />
            )}

            {/* Additional Sections */}
            {contact.education && (
              <IntelligenceSection
                title="Education & Credentials"
                content={contact.education}
                icon="🎓"
              />
            )}

            {contact.social_presence && (
              <IntelligenceSection
                title="Social Presence & Engagement"
                content={contact.social_presence}
                icon="🌐"
              />
            )}

            {contact.products_services && (
              <IntelligenceSection
                title="Products & Services"
                content={contact.products_services}
                icon="📦"
              />
            )}

            {contact.market_position && (
              <IntelligenceSection
                title="Market Position"
                content={contact.market_position}
                icon="📊"
              />
            )}

            {contact.leadership && (
              <IntelligenceSection
                title="Leadership Team"
                content={contact.leadership}
                icon="👥"
              />
            )}
          </div>
        )}

        {/* Empty State */}
        {!hasIntelligence && enrichmentStatus !== 'processing' && (
          <div className="bg-midnight-900 border border-midnight-700 rounded-xl p-12 text-center">
            <div className="text-6xl mb-4">🤖</div>
            <h3 className="text-2xl font-bold text-text-primary mb-2">
              No Intelligence Data Yet
            </h3>
            <p className="text-text-secondary mb-6">
              Click "Enrich Now" to generate AI-powered insights for this contact
            </p>
            <button
              onClick={() => handleEnrich(false)}
              disabled={enriching}
              className="px-8 py-3 bg-gradient-to-r from-gold to-gold-hover text-midnight-950 font-semibold rounded-xl hover:shadow-gold-glow transition-all"
            >
              ⚡ Enrich Now
            </button>
          </div>
        )}
      </div>
    </div>
  );
}