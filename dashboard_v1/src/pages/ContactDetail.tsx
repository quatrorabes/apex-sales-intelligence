// dashboard_v1/src/pages/ContactDetail.tsx
// PRODUCTION VERSION - All Enrichment Data Mapping Fixed
// Last Updated: Dec 15, 2025 3:11 PM PST

import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';

// API Configuration
const API_BASE = import.meta.env.VITE_API_URL || "https://apex-backend-i7b0.onrender.com";

// Contact Interface (UUID support)
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

// Normalize API response to UI format
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

  // Fetch contact data
  async function fetchContact() {
    if (!id) return;

    setLoading(true);
    setError(null);

    try {
      const res = await fetch(`${API_BASE}/api/contacts/${id}`);

      if (!res.ok) {
        throw new Error(`Failed to fetch contact: ${res.status}`);
      }

      const json = await res.json();

      // Unwrap {success: true, contact: {...}} wrapper
      const apiContact = (json && typeof json === 'object' && 'contact' in json) 
        ? (json as any).contact 
        : json;

      setContact(normalizeContact(apiContact));
    } catch (err: any) {
      console.error('Fetch contact error:', err);
      setError(err.message || 'Failed to load contact');
    } finally {
      setLoading(false);
    }
  }

  // Re-enrich contact
  async function handleReEnrich() {
    if (!id || enriching) return;

    setEnriching(true);

    try {
      const res = await fetch(`${API_BASE}/api/contacts/${id}/enrich`, {
        method: 'POST',
      });

      if (!res.ok) {
        throw new Error('Enrichment failed');
      }

      // Poll for completion (3 seconds)
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

  useEffect(() => {
    fetchContact();
  }, [id]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading contact...</p>
        </div>
      </div>
    );
  }

  if (error || !contact) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50">
        <div className="text-center">
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

  // ==========================================
  // ENRICHMENT SECTION MAPPING (FIXED)
  // ==========================================

  const sections = contact.enrichment?.sections || {};

  // Professional: person_profile + background
  const personSection = sections.person_profile || 
                       sections['1._overview'] || 
                       sections['2._about_dale_holzer__background_and_icebreaker_angles'] || '';

  // Company: company_intelligence + market data
  const companySection = sections.company_intelligence || 
                        sections['4._market_position'] || '';

  // Personality: icebreaker topics, education, soft skills
  const personalitySection = sections['3._icebreaker_topics_and_shared_interests'] || 
                            sections['3._education'] || 
                            sections['3._leadership'] || 
                            sections['6._strategic_context'] || '';

  // Fun Facts: fun_facts section
  const funFactsSection = sections.fun_facts || '';

  // Raw profile: all sections joined
  const raw = Object.keys(sections).length > 0
    ? Object.entries(sections)
        .map(([key, value]) => `## ${key.replace(/_/g, ' ').toUpperCase()}\n\n${value}`)
        .join('\n\n---\n\n')
    : '';

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-4">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                {contact.firstname} {contact.lastname}
              </h1>
              <p className="text-lg text-gray-600 mt-1">{contact.title}</p>
              <p className="text-md text-gray-500">{contact.company}</p>

              <div className="flex gap-4 mt-4">
                {contact.email && (
                  <a href={`mailto:${contact.email}`} className="text-blue-600 hover:underline">
                    {contact.email}
                  </a>
                )}
                {contact.phone && (
                  <span className="text-gray-600">{contact.phone}</span>
                )}
                {contact.linkedin_url && (
                  <a 
                    href={contact.linkedin_url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:underline"
                  >
                    LinkedIn
                  </a>
                )}
              </div>
            </div>

            <div className="flex gap-3">
              <button
                onClick={handleReEnrich}
                disabled={enriching}
                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-gray-400"
              >
                {enriching ? 'Enriching...' : 'Re-Enrich'}
              </button>
              <button
                onClick={() => navigate('/contacts')}
                className="px-4 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300"
              >
                Back
              </button>
            </div>
          </div>

          {/* Status Badges */}
          <div className="mt-4 flex gap-2">
            <span className={`px-3 py-1 rounded-full text-sm font-medium ${
              contact.enrichment_status === 'enriched' 
                ? 'bg-green-100 text-green-800'
                : contact.enrichment_status === 'enriching'
                ? 'bg-yellow-100 text-yellow-800'
                : 'bg-gray-100 text-gray-800'
            }`}>
              {contact.enrichment_status || 'pending'}
            </span>
            {contact.apex_score && contact.apex_score > 0 && (
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                contact.apex_score >= 75 
                  ? 'bg-purple-100 text-purple-800'
                  : contact.apex_score >= 50
                  ? 'bg-blue-100 text-blue-800'
                  : 'bg-gray-100 text-gray-800'
              }`}>
                APEX: {contact.apex_score}
              </span>
            )}
            {Object.keys(sections).length > 0 && (
              <span className="px-3 py-1 bg-indigo-100 text-indigo-800 rounded-full text-sm font-medium">
                {Object.keys(sections).length} sections available
              </span>
            )}
          </div>
        </div>

        {/* Tabs */}
        <div className="bg-white rounded-lg shadow-sm">
          <div className="border-b border-gray-200">
            <nav className="flex space-x-8 px-6" aria-label="Tabs">
              {[
                { key: 'professional', label: 'Professional', count: personSection.length },
                { key: 'company', label: 'Company', count: companySection.length },
                { key: 'personality', label: 'Personality', count: personalitySection.length },
                { key: 'funfacts', label: 'Fun Facts', count: funFactsSection.length },
                { key: 'raw', label: 'Raw Profile', count: raw.length },
              ].map((tab) => (
                <button
                  key={tab.key}
                  onClick={() => setActiveTab(tab.key as any)}
                  className={`py-4 px-1 border-b-2 font-medium text-sm ${
                    activeTab === tab.key
                      ? 'border-blue-600 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  {tab.label}
                  {tab.count > 0 && (
                    <span className="ml-2 text-xs text-gray-400">
                      ({Math.round(tab.count / 1000)}k)
                    </span>
                  )}
                </button>
              ))}
            </nav>
          </div>

          {/* Tab Content */}
          <div className="p-6">
            {activeTab === 'professional' && (
              <div className="prose max-w-none">
                {personSection ? (
                  <ReactMarkdown>{personSection}</ReactMarkdown>
                ) : (
                  <p className="text-gray-500">No professional data available. Click "Re-Enrich" to generate.</p>
                )}
              </div>
            )}

            {activeTab === 'company' && (
              <div className="prose max-w-none">
                {companySection ? (
                  <ReactMarkdown>{companySection}</ReactMarkdown>
                ) : (
                  <p className="text-gray-500">No company data available.</p>
                )}
              </div>
            )}

            {activeTab === 'personality' && (
              <div className="prose max-w-none">
                {personalitySection ? (
                  <ReactMarkdown>{personalitySection}</ReactMarkdown>
                ) : (
                  <p className="text-gray-500">No personality/icebreaker data available.</p>
                )}
              </div>
            )}

            {activeTab === 'funfacts' && (
              <div className="prose max-w-none">
                {funFactsSection ? (
                  <ReactMarkdown>{funFactsSection}</ReactMarkdown>
                ) : (
                  <p className="text-gray-500">No fun facts available.</p>
                )}
              </div>
            )}

            {activeTab === 'raw' && (
              <div className="bg-gray-50 p-4 rounded border border-gray-200">
                {raw ? (
                  <div className="prose max-w-none">
                    <ReactMarkdown>{raw}</ReactMarkdown>
                  </div>
                ) : (
                  <p className="text-gray-500">No enrichment data available.</p>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Download PDF */}
        {contact.enrichment && Object.keys(sections).length > 0 && (
          <div className="mt-6 text-center">
            <button className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 shadow-sm">
              📄 Download PDF Dossier
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

