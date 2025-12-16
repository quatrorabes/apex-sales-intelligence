import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  Mail,
  Phone,
  Linkedin,
  Briefcase,
  Building2,
  Loader2,
  AlertCircle,
  DollarSign,
  TrendingUp,
  Users,
  Target,
  CheckCircle2,
  Lightbulb,
  Calendar
} from 'lucide-react';
import { ICPScoreBadge } from '../components/ICPScoreBadge';
import { OutreachGenerator } from '../components/OutreachGenerator';
import { EnrollCadenceModal } from '../components/EnrollCadenceModal';

interface Contact {
  id: string;
  first_name: string;
  last_name?: string | null;
  lastname?: string | null;
  email: string | null;
  phone: string | null;
  company: string | null;
  title: string | null;
  enrichment_status: string | null;
  enrichment: any | null;
  profile_content: string | null;
  linkedin_url: string | null;
  last_enriched?: string | null;
}

interface ICPMatch {
  score: number;
  match_level: string;
  reasons: string[];
  calculated_at?: string;
}

type SectionsMap = Record<string, string>;

const API_BASE = (import.meta as any).env?.VITE_API_BASE_URL || 'https://apex-backend-i7b0.onrender.com';

function getSectionsFromEnrichment(contact: Contact): SectionsMap {
  const enrichment = contact.enrichment || null;
  const legacyRaw = enrichment?.raw_profile || contact.profile_content || '';
  if (enrichment?.sections && typeof enrichment.sections === 'object') {
    const s = enrichment.sections as Record<string, string | undefined>;
    console.log('[APEX v2.0] Backend sections:', Object.keys(s));
    return s as SectionsMap;
  }
  if (legacyRaw && legacyRaw.length > 100) {
    console.log('[APEX v1.0] Using legacy raw profile');
    return { raw_profile: legacyRaw };
  }
  return {};
}

function renderMarkdownBlock(text: string): JSX.Element {
  if (!text || text.trim().length === 0) {
    return <p className="text-sm text-slate-400">No data available</p>;
  }
  const lines = text.split('\n').filter(l => l.trim().length > 0);
  return (
    <ul className="space-y-2 text-sm text-slate-200">
      {lines.map((line, idx) => {
        const cleaned = line.replace(/^[\-•*]\s*/, '').trim();
        if (cleaned.length === 0) return null;
        return (
          <li key={idx} className="flex items-start gap-2">
            <span className="text-sky-400 mt-1">•</span>
            <span>{cleaned}</span>
          </li>
        );
      })}
    </ul>
  );
}

function tabClass(active: boolean): string {
  return [
    'pb-2 px-1 border-b-2 -mb-px transition-colors text-sm font-medium',
    active ? 'border-sky-400 text-sky-300' : 'border-transparent text-slate-400 hover:text-slate-200'
  ].join(' ');
}

interface SectionCardProps {
  title: string;
  icon?: React.ReactNode;
  emptyText: string;
  children?: React.ReactNode;
}

const SectionCard: React.FC<SectionCardProps> = ({ title, icon, emptyText, children }) => {
  const hasContent = !!children;
  return (
    <div className="max-w-4xl space-y-3">
      <div className="flex items-center gap-2">
        {icon && <span className="text-slate-400">{icon}</span>}
        <h2 className="text-base font-semibold text-slate-100">{title}</h2>
      </div>
      <div className="rounded-lg border border-slate-800 bg-slate-950/60 p-4">
        {hasContent ? children : <p className="text-sm text-slate-400">{emptyText}</p>}
      </div>
    </div>
  );
};

export function ContactDetailPage(): JSX.Element {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [contact, setContact] = useState<Contact | null>(null);
  const [sections, setSections] = useState<SectionsMap>({});
  const [icpMatch, setIcpMatch] = useState<ICPMatch | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [loadingICP, setLoadingICP] = useState<boolean>(false);
  const [showCadenceModal, setShowCadenceModal] = useState<boolean>(false);
  const [mainTab, setMainTab] = useState<'overview' | 'company' | 'sales' | 'fit' | 'outreach' | 'personality' | 'raw'>('overview');

  useEffect(() => {
    async function fetchContact() {
      if (!id) return;
      setLoading(true);
      try {
        const url = `${API_BASE}/api/contacts/${id}`;
        console.log('[APEX] Fetching contact detail', url);
        const res = await fetch(url);
        if (!res.ok) {
          console.error('[APEX] Failed to fetch contact', res.status);
          setContact(null);
          setSections({});
          return;
        }
        const data = await res.json();
        const contactData = (data as any).contact ?? data;
        if (!contactData || !contactData.id) {
          console.warn('[APEX] No contact payload');
          setContact(null);
          setSections({});
          return;
        }
        const typedContact = contactData as Contact;
        setContact(typedContact);
        const parsedSections = getSectionsFromEnrichment(typedContact);
        setSections(parsedSections);
      } catch (err) {
        console.error('[APEX] Error loading contact', err);
        setContact(null);
        setSections({});
      } finally {
        setLoading(false);
      }
    }
    fetchContact();
  }, [id]);

  useEffect(() => {
    async function fetchICPMatch() {
      if (!id || mainTab !== 'fit') return;
      setLoadingICP(true);
      try {
        const url = `${API_BASE}/api/contacts/${id}/icp-match`;
        console.log('[APEX] Fetching ICP match', url);
        const res = await fetch(url);
        if (!res.ok) {
          console.error('[APEX] ICP match failed', res.status);
          setIcpMatch(null);
          return;
        }
        const data = await res.json();
        setIcpMatch(data);
      } catch (err) {
        console.error('[APEX] Error loading ICP match', err);
        setIcpMatch(null);
      } finally {
        setLoadingICP(false);
      }
    }
    fetchICPMatch();
  }, [id, mainTab]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-slate-200">
        <Loader2 className="h-8 w-8 animate-spin mb-3" />
        <div>Loading contact…</div>
      </div>
    );
  }

  if (!contact) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-slate-400">
        <div className="mb-4 text-sm">Contact not found</div>
        <button
          onClick={() => navigate(-1)}
          className="inline-flex items-center px-3 py-1.5 text-xs rounded-md border border-slate-600 text-slate-100 hover:bg-slate-800"
        >
          <ArrowLeft className="h-3 w-3 mr-1" />
          Back to contacts
        </button>
      </div>
    );
  }

  const fullName = `${contact.first_name || ''} ${contact.last_name || contact.lastname || ''}`.trim() || 'Unnamed contact';
  const overviewText = sections['1._overview'] || sections.person_profile || sections.overview || sections.person_research || '';
  const backgroundText = sections['2._background_(work_history_and_achievements)'] || sections.skills_expertise || sections.background_and_experience || '';
  const companyOverviewText = sections.company_intelligence || sections['1._overview'] || sections.company_overview || '';
  const marketPositionText = sections['4._market_position'] || sections.market_position || '';
  const leadershipText = sections['3._leadership'] || sections.leadership_and_culture || '';
  const recentNewsText = sections.recent_activity || sections.recent_activity_and_news || '';
  const painPointsText = sections['6._strategic_context'] || sections.pain_points_and_challenges || '';
  const budgetAuthorityText = sections.skills_expertise || sections['2._professional_skills__leadership,_industry_expertise'] || sections.budget_and_authority || '';
  const personalityText = sections.social_profiles || sections['2._icebreaker_topics'] || sections.personality_and_communication || sections.personality_analysis || '';
  const rawText = contact.enrichment ? JSON.stringify(contact.enrichment, null, 2) : (sections.raw_profile || contact.profile_content || '');

  return (
    <div className="flex flex-col h-full text-slate-50 bg-slate-900">
      <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800 bg-slate-950">
        <div className="flex items-center gap-4">
          <button
            onClick={() => navigate(-1)}
            className="inline-flex items-center justify-center h-9 w-9 rounded-md border border-slate-700 hover:bg-slate-800 transition"
          >
            <ArrowLeft className="h-4 w-4" />
          </button>
          <div>
            <div className="text-xl font-semibold">{fullName}</div>
            <div className="flex items-center gap-2 text-sm text-slate-300 mt-1">
              <Briefcase className="h-3.5 w-3.5" />
              <span>{contact.title || 'No title'}</span>
              <span>•</span>
              <Building2 className="h-3.5 w-3.5" />
              <span>{contact.company || 'No company'}</span>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <button
            onClick={() => setShowCadenceModal(true)}
            className="px-4 py-2 bg-sky-500 hover:bg-sky-600 text-white rounded-lg font-medium transition-colors flex items-center gap-2"
          >
            <Calendar className="h-4 w-4" />
            Start Cadence
          </button>

          <div className="flex flex-col items-end gap-1.5 text-xs text-slate-300">
            {contact.email && (
              <div className="flex items-center gap-2">
                <Mail className="h-3.5 w-3.5" />
                <span>{contact.email}</span>
              </div>
            )}
            {contact.phone && (
              <div className="flex items-center gap-2">
                <Phone className="h-3.5 w-3.5" />
                <span>{contact.phone}</span>
              </div>
            )}
            {contact.linkedin_url && (
              <a
                href={contact.linkedin_url}
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center gap-1.5 text-sky-400 hover:underline"
              >
                <Linkedin className="h-3.5 w-3.5" />
                LinkedIn Profile
              </a>
            )}
            <div className="mt-1 px-2 py-0.5 rounded text-[11px] bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              {contact.enrichment_status || 'unknown'}
            </div>
          </div>
        </div>
      </div>

      <div className="px-6 pt-4 border-b border-slate-800 bg-slate-950">
        <div className="flex gap-6">
          <button className={tabClass(mainTab === 'overview')} onClick={() => setMainTab('overview')}>
            Overview
          </button>
          <button className={tabClass(mainTab === 'company')} onClick={() => setMainTab('company')}>
            Company
          </button>
          <button className={tabClass(mainTab === 'sales')} onClick={() => setMainTab('sales')}>
            Sales Intel
          </button>
          <button className={tabClass(mainTab === 'fit')} onClick={() => setMainTab('fit')}>
            Why We Fit
          </button>
          <button className={tabClass(mainTab === 'outreach')} onClick={() => setMainTab('outreach')}>
            Outreach
          </button>
          <button className={tabClass(mainTab === 'personality')} onClick={() => setMainTab('personality')}>
            Personality
          </button>
          <button className={tabClass(mainTab === 'raw')} onClick={() => setMainTab('raw')}>
            Raw Data
          </button>
        </div>
      </div>

      <div className="flex-1 overflow-auto px-6 py-6 space-y-6">
        {mainTab === 'overview' && (
          <>
            <SectionCard title="Executive Summary" emptyText="No overview available. Enrich this contact to generate insights.">
              {overviewText ? renderMarkdownBlock(overviewText) : null}
            </SectionCard>
            {backgroundText && (
              <SectionCard title="Background & Experience" icon={<TrendingUp className="h-4 w-4" />} emptyText="">
                {renderMarkdownBlock(backgroundText)}
              </SectionCard>
            )}
          </>
        )}
    
        {mainTab === 'company' && (
          <>
            <SectionCard title="Company Overview" icon={<Building2 className="h-4 w-4" />} emptyText="No company data available.">
              {companyOverviewText ? renderMarkdownBlock(companyOverviewText) : null}
            </SectionCard>
            {marketPositionText && (
              <SectionCard title="Market Position & Competitors" icon={<Target className="h-4 w-4" />} emptyText="">
                {renderMarkdownBlock(marketPositionText)}
              </SectionCard>
            )}
            {leadershipText && (
              <SectionCard title="Leadership & Culture" icon={<Users className="h-4 w-4" />} emptyText="">
                {renderMarkdownBlock(leadershipText)}
              </SectionCard>
            )}
            {recentNewsText && (
              <SectionCard title="Recent Activity & News" emptyText="">
                {renderMarkdownBlock(recentNewsText)}
              </SectionCard>
            )}
          </>
        )}
    
        {mainTab === 'sales' && (
          <>
            <SectionCard
              title="Pain Points & Buying Triggers"
              icon={<AlertCircle className="h-4 w-4" />}
              emptyText="No pain points identified. Enrich this contact to generate sales insights."
            >
              {painPointsText ? renderMarkdownBlock(painPointsText) : null}
            </SectionCard>
            <SectionCard
              title="Budget & Decision Authority"
              icon={<DollarSign className="h-4 w-4" />}
              emptyText="No budget or authority information available."
            >
              {budgetAuthorityText ? renderMarkdownBlock(budgetAuthorityText) : null}
            </SectionCard>
          </>
        )}
    
        {mainTab === 'fit' && (
          <div className="max-w-4xl space-y-6">
            {loadingICP ? (
              <div className="flex items-center justify-center py-12">
                <Loader2 className="h-6 w-6 animate-spin text-sky-400" />
              </div>
            ) : icpMatch ? (
              <>
                <ICPScoreBadge score={icpMatch.score} matchLevel={icpMatch.match_level} />
                <SectionCard
                  title="Why We're a Perfect Fit"
                  icon={<CheckCircle2 className="h-4 w-4" />}
                  emptyText="No match reasons available."
                >
                  {icpMatch.reasons && icpMatch.reasons.length > 0 ? (
                    <ul className="space-y-3">
                      {icpMatch.reasons.map((reason, idx) => (
                        <li key={idx} className="flex items-start gap-3 text-sm text-slate-200">
                          <CheckCircle2 className="h-5 w-5 text-emerald-400 mt-0.5 flex-shrink-0" />
                          <span>{reason}</span>
                        </li>
                      ))}
                    </ul>
                  ) : null}
                </SectionCard>
              </>
            ) : (
              <div className="text-center py-12 text-slate-400">
                <Lightbulb className="h-12 w-12 mx-auto mb-3 opacity-50" />
                <p>No ICP match data available.</p>
                <p className="text-xs mt-1">Enrich this contact first, then score against your ICP.</p>
              </div>
            )}
          </div>
        )}
    
        {mainTab === 'outreach' && (
          <div>
            <h2 className="text-lg font-semibold text-slate-100 mb-4">Generate Outreach</h2>
            <OutreachGenerator contactId={contact.id} />
          </div>
        )}
    
        {mainTab === 'personality' && (
          <SectionCard
            title="Personality & Communication Style"
            emptyText="No personality analysis available. Enrich to generate communication insights."
          >
            {personalityText ? renderMarkdownBlock(personalityText) : null}
          </SectionCard>
        )}
    
        {mainTab === 'raw' && (
          <SectionCard title="Raw Enrichment Data" emptyText="No raw data available.">
            {rawText && (
              <pre className="whitespace-pre-wrap text-xs text-slate-200 bg-slate-900/80 rounded-md p-4 border border-slate-700 overflow-auto max-h-96 font-mono">
                {rawText}
              </pre>
            )}
          </SectionCard>
        )}
      </div>
    
      <EnrollCadenceModal
        isOpen={showCadenceModal}
        onClose={() => setShowCadenceModal(false)}
        contactId={contact.id}
        contactName={fullName}
      />
    </div>
  );
}
      
export default ContactDetailPage;
      