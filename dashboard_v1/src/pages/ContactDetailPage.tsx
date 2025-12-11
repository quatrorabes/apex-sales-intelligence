
import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  Mail,
  Phone,
  Linkedin,
  Briefcase,
  Building2,
  Loader2
} from 'lucide-react';

// ===================================================================================
// TYPES
// ===================================================================================

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

type SectionsMap = Record<string, string>;

// ===================================================================================
// HELPERS
// ===================================================================================

const API_BASE =
  (import.meta as any).env?.VITE_API_BASE_URL ||
  'https://apex-backend-i7b0.onrender.com';

// Normalize v2 backend sections into legacy buckets (overview/company/sales/personality)
function getSectionsFromEnrichment(contact: Contact): SectionsMap {
  const enrichment = contact.enrichment || null;
  const legacyRaw = enrichment?.raw_profile || contact.profile_content || '';

  if (enrichment?.sections && typeof enrichment.sections === 'object') {
    const s = enrichment.sections as Record<string, string | undefined>;
    const mapped: SectionsMap = {};

    // High‑level overview
    mapped.overview =
      s.overview ||
      s.background_and_experience ||
      '';

    // Company intelligence (business model, market position, news, leadership)
    mapped.company_research = [
      s.company_overview,
      s.market_position,
      s.recent_activity_and_news,
      s.leadership_and_culture
    ]
      .filter(Boolean)
      .join('\n\n');

    // Sales intelligence (pain points + budget/authority)
    mapped.sales_intelligence = [
      s.pain_points_and_challenges,
      s.budget_and_authority
    ]
      .filter(Boolean)
      .join('\n\n');

    // Personality / communication style
    mapped.personality_analysis =
      s.personality_and_communication ||
      '';

    // Always keep raw for debugging
    if (legacyRaw) {
      mapped.raw_profile = legacyRaw;
    }

    // Also expose original keys for future use
    Object.entries(s).forEach(([k, v]) => {
      if (v && !mapped[k]) {
        mapped[k] = v;
      }
    });

    console.log('[APEX v2.0] Using backend‑parsed sections', {
      version: enrichment.version,
      keys: Object.keys(s || {})
    });

    return mapped;
  }

  // Legacy path – just expose raw text
  if (legacyRaw && legacyRaw.length > 100) {
    console.log('[APEX v1.0] Using legacy raw profile');
    return { raw_profile: legacyRaw };
  }

  return {};
}

// Simple markdown-ish splitter for display
function renderMarkdownBlock(text: string): JSX.Element {
  const lines = text.split('\n').filter(l => l.trim().length > 0);
  return (
    <ul className="space-y-1 list-disc list-inside text-sm text-slate-200">
      {lines.map((line, idx) => (
        <li key={idx}>{line.replace(/^[\-•*]\s*/, '')}</li>
      ))}
    </ul>
  );
}

function tabClass(active: boolean): string {
  return [
    'pb-2 border-b-2 -mb-px transition-colors',
    active
      ? 'border-sky-400 text-sky-300'
      : 'border-transparent text-slate-400 hover:text-slate-200'
  ].join(' ');
}

interface SectionCardProps {
  title: string;
  emptyText: string;
  children?: React.ReactNode;
}

const SectionCard: React.FC<SectionCardProps> = ({ title, emptyText, children }) => {
  const hasContent = !!children;

  return (
    <div className="max-w-4xl space-y-2">
      <h2 className="text-sm font-semibold text-slate-100">{title}</h2>
      <div className="rounded-lg border border-slate-800 bg-slate-950/60 p-4">
        {hasContent ? (
          children
        ) : (
          <p className="text-sm text-slate-400">{emptyText}</p>
        )}
      </div>
    </div>
  );
};

// ===================================================================================
// COMPONENT
// ===================================================================================

export function ContactDetailPage(): JSX.Element {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [contact, setContact] = useState<Contact | null>(null);
  const [sections, setSections] = useState<SectionsMap>({});
  const [loading, setLoading] = useState<boolean>(true);
  const [mainTab, setMainTab] = useState<'overview' | 'company' | 'sales' | 'personality' | 'raw'>('overview');

  useEffect(() => {
    async function fetchContact() {
      if (!id) return;

      setLoading(true);
      try {
        const url = `${API_BASE}/api/v2/contacts/${id}`;
        console.log('[APEX] Fetching contact detail', url);

        const res = await fetch(url);
        if (!res.ok) {
          console.error('[APEX] Failed to fetch contact', res.status, res.statusText);
          setContact(null);
          setSections({});
          return;
        }

        const data = await res.json();
        console.log('[APEX_CONTACT_DEBUG] raw response', data);

        const contactData = (data as any).contact ?? data;

        if (!contactData || !contactData.id) {
          console.warn('[APEX] No contact payload in response for id', id);
          setContact(null);
          setSections({});
          return;
        }

        const typedContact = contactData as Contact;
        setContact(typedContact);
        setSections(getSectionsFromEnrichment(typedContact));
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

  const overviewText =
    sections.overview ||
    sections.person_research ||
    sections.background_and_experience ||
    '';

  const companyText =
    sections.company_research ||
    sections.company_overview ||
    sections.market_position ||
    '';

  const salesText =
    sections.sales_intelligence ||
    sections.pain_points_and_challenges ||
    sections.budget_and_authority ||
    '';

  const personalityText =
    sections.personality_analysis ||
    sections.personality_and_communication ||
    '';

  const rawText =
    sections.raw_profile ||
    contact.profile_content ||
    (contact.enrichment && contact.enrichment.raw_profile) ||
    '';

  return (
    <div className="flex flex-col h-full text-slate-50">
      {/* Header */}
      <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800">
        <div className="flex items-center gap-4">
          <button
            onClick={() => navigate(-1)}
            className="inline-flex items-center justify-center h-8 w-8 rounded-md border border-slate-700 hover:bg-slate-800"
          >
            <ArrowLeft className="h-4 w-4" />
          </button>
          <div>
            <div className="text-lg font-semibold">{fullName}</div>
            <div className="flex items-center gap-2 text-sm text-slate-300">
              <Briefcase className="h-3 w-3" />
              <span>{contact.title || 'No title'}</span>
              <span>•</span>
              <Building2 className="h-3 w-3" />
              <span>{contact.company || 'No company'}</span>
            </div>
          </div>
        </div>

        <div className="flex flex-col items-end gap-1 text-xs text-slate-300">
          <div className="flex items-center gap-2">
            <Mail className="h-3 w-3" />
            <span>{contact.email || 'N/A'}</span>
          </div>
          <div className="flex items-center gap-2">
            <Phone className="h-3 w-3" />
            <span>{contact.phone || 'N/A'}</span>
          </div>
          {contact.linkedin_url && (
            <a
              href={contact.linkedin_url}
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-1 text-sky-400 hover:underline"
            >
              <Linkedin className="h-3 w-3" />
              View LinkedIn
            </a>
          )}
          <div className="mt-1 text-[11px] text-slate-400">
            Enrichment: {contact.enrichment_status || 'unknown'}
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="px-6 pt-3 border-b border-slate-800">
        <div className="flex gap-4 text-sm">
          <button className={tabClass(mainTab === 'overview')} onClick={() => setMainTab('overview')}>
            Overview
          </button>
          <button className={tabClass(mainTab === 'company')} onClick={() => setMainTab('company')}>
            Company
          </button>
          <button className={tabClass(mainTab === 'sales')} onClick={() => setMainTab('sales')}>
            Sales Intel
          </button>
          <button className={tabClass(mainTab === 'personality')} onClick={() => setMainTab('personality')}>
            Personality
          </button>
          <button className={tabClass(mainTab === 'raw')} onClick={() => setMainTab('raw')}>
            Raw
          </button>
        </div>
      </div>

      {/* Body */}
      <div className="flex-1 overflow-auto px-6 py-4 space-y-4">
        {mainTab === 'overview' && (
          <SectionCard title="Executive Overview" emptyText="No overview available.">
            {overviewText ? renderMarkdownBlock(overviewText) : null}
          </SectionCard>
        )}

        {mainTab === 'company' && (
          <SectionCard title="Company Intelligence" emptyText="No company data available.">
            {companyText ? renderMarkdownBlock(companyText) : null}
          </SectionCard>
        )}

        {mainTab === 'sales' && (
          <SectionCard
            title="Sales Intelligence"
            emptyText="No sales intelligence available. Enrich this contact to generate insights."
          >
            {salesText ? renderMarkdownBlock(salesText) : null}
          </SectionCard>
        )}

        {mainTab === 'personality' && (
          <SectionCard title="Personality & Communication" emptyText="No personality analysis available.">
            {personalityText ? renderMarkdownBlock(personalityText) : null}
          </SectionCard>
        )}

        {mainTab === 'raw' && (
          <SectionCard title="Raw Enrichment Data" emptyText="No raw data available.">
            {rawText && (
              <pre className="whitespace-pre-wrap text-xs text-slate-200 bg-slate-900/60 rounded-md p-4 border border-slate-800 overflow-auto">
                {rawText}
              </pre>
            )}
          </SectionCard>
        )}
      </div>
    </div>
  );
}

export default ContactDetailPage;

