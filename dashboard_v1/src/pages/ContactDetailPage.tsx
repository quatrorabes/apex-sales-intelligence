// UPDATED: dashboard_v1/src/pages/ContactDetailPage.tsx
// Integration for v3.0 enrichment with 10 sections

import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import { Contact } from '../types';

type SectionsMap = Record<string, string>;

const ContactDetailPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const contactId = searchParams.get('id') || '';
  
  const [contact, setContact] = useState<Contact | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<string>('');
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!contactId) return;
    fetchContact(contactId);
  }, [contactId]);

  const fetchContact = async (id: string) => {
    try {
      setLoading(true);
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/contacts/${id}`);
      const data = await response.json();
      
      const contactData = data.contact || data;
      setContact(contactData);
      
      // Set first available section tab
      const sections = getSectionsFromEnrichment(contactData);
      const keys = Object.keys(sections);
      if (keys.length > 0) {
        setActiveTab(keys[0]);
      }
      
      setError(null);
    } catch (err) {
      setError(`Failed to load contact: ${err}`);
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="p-8">Loading contact details...</div>;
  if (error) return <div className="p-8 text-red-600">{error}</div>;
  if (!contact) return <div className="p-8">Contact not found</div>;

  const sections = getSectionsFromEnrichment(contact);
  const sectionKeys = Object.keys(sections);

  return (
    <div className="contact-detail-page p-8">
      {/* Contact Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold">{contact.name}</h1>
        <div className="text-lg text-gray-600 mt-2">
          <span>{contact.title}</span>
          <span className="mx-2">•</span>
          <span>{contact.company}</span>
        </div>
        
        {/* Enrichment Status Badge */}
        {contact.enrichment_status && (
          <div className="mt-4">
            <span className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${
              contact.enrichment_status === 'completed' 
                ? 'bg-green-100 text-green-800'
                : contact.enrichment_status === 'pending'
                ? 'bg-yellow-100 text-yellow-800'
                : 'bg-red-100 text-red-800'
            }`}>
              {contact.enrichment_status.charAt(0).toUpperCase() + contact.enrichment_status.slice(1)}
            </span>
            {contact.enriched_at && (
              <span className="text-sm text-gray-500 ml-2">
                Enriched on {new Date(contact.enriched_at).toLocaleDateString()}
              </span>
            )}
          </div>
        )}
      </div>

      {/* Tabs Container */}
      {sectionKeys.length > 0 ? (
        <div className="enrichment-tabs">
          {/* Tab Headers */}
          <div className="flex border-b border-gray-200 mb-6 overflow-x-auto">
            {sectionKeys.map((key) => (
              <button
                key={key}
                onClick={() => setActiveTab(key)}
                className={`px-4 py-2 font-medium text-sm whitespace-nowrap border-b-2 transition-colors ${
                  activeTab === key
                    ? 'border-blue-600 text-blue-600'
                    : 'border-transparent text-gray-600 hover:text-gray-900'
                }`}
              >
                {formatTabLabel(key)}
              </button>
            ))}
            <button
              onClick={() => setActiveTab('raw')}
              className={`px-4 py-2 font-medium text-sm whitespace-nowrap border-b-2 transition-colors ${
                activeTab === 'raw'
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-600 hover:text-gray-900'
              }`}
            >
              Raw Data
            </button>
          </div>

          {/* Tab Content */}
          <div className="tab-content">
            {sectionKeys.map((key) => (
              <div
                key={key}
                className={`tab-pane ${activeTab === key ? 'active' : 'hidden'}`}
              >
                <div className="bg-white rounded-lg border border-gray-200 p-6">
                  <h2 className="text-xl font-bold mb-4">{formatTabLabel(key)}</h2>
                  <div className="prose prose-sm max-w-none">
                    <ReactMarkdown>{sections[key]}</ReactMarkdown>
                  </div>
                </div>
              </div>
            ))}

            {/* Raw Data Tab */}
            <div className={`tab-pane ${activeTab === 'raw' ? 'active' : 'hidden'}`}>
              <div className="bg-white rounded-lg border border-gray-200 p-6">
                <h2 className="text-xl font-bold mb-4">Raw Enrichment Data</h2>
                <pre className="bg-gray-100 p-4 rounded text-sm overflow-x-auto">
                  {JSON.stringify(contact.enrichment_data, null, 2)}
                </pre>
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
          <p className="text-blue-900">
            No enrichment data available yet. Click the "Enrich" button to generate intelligence.
          </p>
        </div>
      )}

      {/* Additional Contact Info */}
      <div className="mt-8 grid grid-cols-2 gap-4">
        {contact.email && (
          <div>
            <label className="text-sm font-medium text-gray-600">Email</label>
            <p className="text-lg">{contact.email}</p>
          </div>
        )}
        {contact.phone && (
          <div>
            <label className="text-sm font-medium text-gray-600">Phone</label>
            <p className="text-lg">{contact.phone}</p>
          </div>
        )}
        {contact.linkedin_url && (
          <div>
            <label className="text-sm font-medium text-gray-600">LinkedIn</label>
            <a href={contact.linkedin_url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
              View Profile
            </a>
          </div>
        )}
      </div>
    </div>
  );
};

/**
 * Extract sections from enrichment_data with intelligent fallback
 */
function getSectionsFromEnrichment(contact: Contact): SectionsMap {
  const enrichmentData = (contact as any).enrichment_data;

  if (!enrichmentData) return {};

  // ✅ Case 1: v3.0 structured sections
  if (enrichmentData.sections && typeof enrichmentData.sections === 'object') {
    const keys = Object.keys(enrichmentData.sections);
    
    // Check if it's pre-structured (multiple section keys)
    if (keys.length > 1) {
      console.log('[APEX v3.0] Using pre-structured sections:', keys);
      return enrichmentData.sections;
    }
  }

  // ✅ Case 2: Parse raw_profile markdown if available
  if (enrichmentData.raw_profile) {
    console.log('[APEX v3.0] Parsing raw_profile');
    return parseMarkdownSections(enrichmentData.raw_profile);
  }

  // ✅ Case 3: Legacy support - try sections.raw_text
  if (enrichmentData.sections?.raw_text) {
    console.log('[APEX] Using legacy sections.raw_text');
    return parseMarkdownSections(enrichmentData.sections.raw_text);
  }

  return {};
}

/**
 * Parse markdown with ## headings into section object
 */
function parseMarkdownSections(markdownText: string): SectionsMap {
  const sections: SectionsMap = {};
  
  // Split by ## headings
  const parts = markdownText.split(/^## /m);

  for (const part of parts) {
    if (!part.trim()) continue;

    const lines = part.split('\n');
    const heading = lines[0].trim();
    const content = lines.slice(1).join('\n').trim();

    if (heading && content) {
      const key = normalizeKey(heading);
      sections[key] = content;
    }
  }

  return sections;
}

/**
 * Convert heading to section key
 * "1. EXECUTIVE SUMMARY" → "executive_summary"
 */
function normalizeKey(heading: string): string {
  return heading
    .toLowerCase()
    .replace(/^[\d.]+\s*/, '') // Remove leading numbers
    .replace(/[&]/g, 'and')
    .replace(/[^a-z0-9\s_]/g, '')
    .replace(/\s+/g, '_')
    .replace(/_+/g, '_')
    .replace(/^_+|_+$/g, '');
}

/**
 * Format section key for display
 * "executive_summary" → "Executive Summary"
 */
function formatTabLabel(key: string): string {
  return key
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}

export default ContactDetailPage;
