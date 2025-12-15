// dashboard_v1/src/pages/ContactDetail.tsx
// PRODUCTION - Dashboard_v1 styling: gradient background + glass cards (fixes "still white" perception)

import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';

const API_BASE = import.meta.env.VITE_API_URL || "https://apex-backend-i7b0.onrender.com";

interface Contact {
  id: string;
  firstname?: string;
  lastname?: string;
  email?: string;
  phone?: string;
  company?: string;
  title?: string;
  linkedin_url?: string;
  enrichment_status?: string;
  enriched_at?: string;
  apex_score?: number;
  match_score?: number;
  enrichment?: {
    engine?: string;
    version?: string;
    sections?: Record<string, string>;
  };
}

function normalizeContact(api: any): Contact {
  return {
    id: String(api?.id ?? ''),
    firstname: api?.first_name ?? api?.firstname ?? '',
    lastname: api?.last_name ?? api?.lastname ?? '',
    email: api?.email ?? '',
    phone: api?.phone ?? '',
    company: api?.company ?? '',
    title: api?.title ?? '',
    linkedin_url: api?.linkedin_url ?? api?.linkedinUrl ?? '',
    enrichment_status: api?.enrichment_status ?? api?.enrichmentStatus ?? 'pending',
    enriched_at: api?.enriched_at ?? api?.enrichedAt ?? '',
    apex_score: api?.apex_score ?? api?.apexScore ?? 0,
    match_score: api?.match_score ?? api?.matchScore ?? 0,
    enrichment: api?.enrichment ?? null,
  };
}

export default function ContactDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [contact, setContact] = useState<Contact | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'professional' | 'company' | 'personality' | 'funfacts' | 'raw'>('professional');
  const [enriching, setEnriching] = useState(false);

  async function fetchContact() {
    if (!id) return;
    setLoading(true);
    setError(null);

    try {
      const res = await fetch(`${API_BASE}/api/contacts/${id}`);
      if (!res.ok) throw new Error(`Failed to fetch contact: ${res.status}`);
      const json = await res.json();
      const apiContact = (json && typeof json === 'object' && 'contact' in json) ? (json as any).contact : json;
      setContact(normalizeContact(apiContact));
    } catch (err: any) {
      console.error('Fetch contact error:', err);
      setError(err.message || 'Failed to load contact');
    } finally {
      setLoading(false);
    }
  }

  async function handleReEnrich() {
    if (!id || enriching) return;
    setEnriching(true);

    try {
      const res = await fetch(`${API_BASE}/api/contacts/${id}/enrich`, { method: 'POST' });
      if (!res.ok) throw new Error('Enrichment failed');

      setTimeout(() => {
        fetchContact();
        setEnriching(false);
      }, 3000);
    } catch (err: any) {
      console.error('Enrich error:', err);
      alert('Enrichment failed. Check console.');
      setEnriching(false);
    }
  }

  useEffect(() => { fetchContact(); }, [id]);

  // Shared gradient background (Dashboard_v1)
  const pageBg = "min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50";

  if (loading) {
    return (
      <div className={`flex items-center justify-center ${pageBg}`}>
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading contact...</p>
        </div>
      </div>
    );
  }

  if (error || !contact) {
    return (
      <div className={`flex items-center justify-center ${pageBg}`}>
        <div className="text-center bg-white/85 backdrop-blur-sm rounded-lg shadow-lg p-8 border border-gray-100">
          <p className="text-red-600 mb-4">{error || 'Contact not found'}</p>
          <button
            onClick={() => navigate('/contacts')}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Back to Contacts
          </button>
        </div>
      </div>
    );
  }

  const sections = contact.enrichment?.sections || {};
  const personSection =
    sections.person_profile ||
    sections['1._overview'] ||
    sections['2._about_dale_holzer__background_and_icebreaker_angles'] ||
    '';

  const companySection =
    sections.company_intelligence ||
    sections['4._market_position'] ||
    '';

  const personalitySection =
    sections['3._icebreaker_topics_and_shared_interests'] ||
    sections['3._education'] ||
    sections['3._leadership'] ||
    sections['6._strategic_context'] ||
    '';

  const funFactsSection = sections.fun_facts || '';

  const raw = Object.keys(sections).length > 0
    ? Object.entries(sections)
        .map(([key, value]) => `## ${key.replace(/_/g, ' ').toUpperCase()}\n\n${value}`)
        .join('\n\n---\n\n')
    : '';

  // Glass card styling (keeps white scheme, but stops “everything looks white”)
  const card = "bg-white/85 backdrop-blur-sm rounded-lg shadow-lg border border-gray-100";
  const tabBar = "border-b border-gray-200 bg-white/70 backdrop-blur-sm";

  return (
    <div className={`${pageBg} py-8`}>
      <div className="max-w-6xl mx-auto px-4">
        {/* Header */}
        <div className={`${card} p-6 mb-6`}>
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <h1 className="text-3xl font-bold text-gray-900">
                {contact.firstname} {contact.lastname}
              </h1>
              <p className="text-lg text-gray-600 mt-1">{contact.title}</p>
              <p className="text-md text-gray-500">{contact.company}</p>

              <div className="flex gap-4 mt-4">
                {contact.email && (
                  <a href={`mailto:${contact.email}`} className="text-blue-600 hover:text-blue-700 hover:underline font-medium">
                    {contact.email}
                  </a>
                )}
                {contact.phone && <span className="text-gray-600 font-medium">{contact.phone}</span>}
                {contact.linkedin_url && (
                  <a href={contact.linkedin_url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:text-blue-700 hover:underline font-medium">
                    LinkedIn
                  </a>
                )}
              </div>
            </div>

            <div className="flex gap-3">
              <button
                onClick={handleReEnrich}
                disabled={enriching}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 shadow-sm font-medium transition-colors"
              >
                {enriching ? 'Enriching...' : 'Re-Enrich'}
              </button>
              <button
                onClick={() => navigate('/contacts')}
                className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 font-medium transition-colors"
              >
                Back
              </button>
            </div>
          </div>

          <div className="mt-4 flex gap-2 flex-wrap">
            <span
              className={`px-3 py-1 rounded-full text-sm font-semibold shadow-sm ${
                contact.enrichment_status === 'enriched'
                  ? 'bg-green-100 text-green-800 border border-green-200'
                  : contact.enrichment_status === 'enriching'
                  ? 'bg-yellow-100 text-yellow-800 border border-yellow-200'
                  : 'bg-gray-100 text-gray-700 border border-gray-200'
              }`}
            >
              {contact.enrichment_status || 'pending'}
            </span>

            {contact.apex_score && contact.apex_score > 0 && (
              <span className="px-3 py-1 bg-purple-100 text-purple-800 border border-purple-200 rounded-full text-sm font-semibold shadow-sm">
                APEX: {contact.apex_score}
              </span>
            )}

            {Object.keys(sections).length > 0 && (
              <span className="px-3 py-1 bg-blue-100 text-blue-800 border border-blue-200 rounded-full text-sm font-semibold shadow-sm">
                {Object.keys(sections).length} sections
              </span>
            )}
          </div>
        </div>

        {/* Tabs */}
        <div className={`${card} overflow-hidden`}>
          <div className={tabBar}>
            <nav className="flex space-x-8 px-6" aria-label="Tabs">
              {[
                { key: 'professional', label: 'Professional' },
                { key: 'company', label: 'Company' },
                { key: 'personality', label: 'Personality' },
                { key: 'funfacts', label: 'Fun Facts' },
                { key: 'raw', label: 'Raw Profile' },
              ].map((tab) => (
                <button
                  key={tab.key}
                  onClick={() => setActiveTab(tab.key as any)}
                  className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                    activeTab === tab.key
                      ? 'border-blue-600 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  {tab.label}
                </button>
              ))}
            </nav>
          </div>

          {/* IMPORTANT: this is what was making the whole page “look white” */}
          <div className="p-8 bg-white/70 backdrop-blur-sm min-h-[320px]">
            {activeTab === 'professional' && (
              <div className="prose prose-blue max-w-none">
                {personSection ? (
                  <ReactMarkdown>{personSection}</ReactMarkdown>
                ) : (
                  <div className="text-center py-12">
                    <p className="text-gray-500 text-lg">No professional data available.</p>
                    <p className="text-gray-400 text-sm mt-2">Click “Re-Enrich” to generate intelligence.</p>
                  </div>
                )}
              </div>
            )}

            {activeTab === 'company' && (
              <div className="prose prose-blue max-w-none">
                {companySection ? (
                  <ReactMarkdown>{companySection}</ReactMarkdown>
                ) : (
                  <div className="text-center py-12">
                    <p className="text-gray-500 text-lg">No company data available.</p>
                    <p className="text-gray-400 text-sm mt-2">Click “Re-Enrich” to generate intelligence.</p>
                  </div>
                )}
              </div>
            )}

            {activeTab === 'personality' && (
              <div className="prose prose-blue max-w-none">
                {personalitySection ? (
                  <ReactMarkdown>{personalitySection}</ReactMarkdown>
                ) : (
                  <div className="text-center py-12">
                    <p className="text-gray-500 text-lg">No personality/icebreaker data available.</p>
                    <p className="text-gray-400 text-sm mt-2">Click “Re-Enrich” to generate intelligence.</p>
                  </div>
                )}
              </div>
            )}

            {activeTab === 'funfacts' && (
              <div className="prose prose-blue max-w-none">
                {funFactsSection ? (
                  <ReactMarkdown>{funFactsSection}</ReactMarkdown>
                ) : (
                  <div className="text-center py-12">
                    <p className="text-gray-500 text-lg">No fun facts available.</p>
                    <p className="text-gray-400 text-sm mt-2">Click “Re-Enrich” to discover interesting details.</p>
                  </div>
                )}
              </div>
            )}

            {activeTab === 'raw' && (
              <div className="bg-white/60 backdrop-blur-sm p-6 rounded-lg border border-gray-200">
                {raw ? (
                  <div className="prose prose-sm max-w-none">
                    <ReactMarkdown>{raw}</ReactMarkdown>
                  </div>
                ) : (
                  <div className="text-center py-12">
                    <p className="text-gray-500 text-lg">No enrichment data available.</p>
                    <p className="text-gray-400 text-sm mt-2">Click “Re-Enrich” to generate full profile.</p>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {contact.enrichment && Object.keys(sections).length > 0 && (
          <div className="mt-6 text-center">
            <button className="px-8 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 shadow-lg font-semibold transition-colors">
              Download PDF Dossier
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
