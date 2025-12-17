# dashboardv1/src/pages/ContactDetailPage.tsx
//"""
//CRITICAL FIX: Contact Detail Page was missing
//This allows users to view contact details and enrichment data
//"""

import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, RefreshCw, Eye, Copy, Check } from 'lucide-react';
import { config } from '../config/api';

interface Contact {
  id: string;
  name: string;
  title?: string;
  company?: string;
  email?: string;
  phone?: string;
  linkedinurl?: string;
  enrichmentdata?: any;
  enrichmentstatus?: string;
  enrichedat?: string;
}

interface EnrichmentSection {
  [key: string]: string;
}

export const ContactDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [contact, setContact] = useState<Contact | null>(null);
  const [loading, setLoading] = useState(true);
  const [enriching, setEnriching] = useState(false);
  const [activeTab, setActiveTab] = useState<'overview' | 'enrichment' | 'raw'>('overview');
  const [copied, setCopied] = useState(false);
  const [sections, setSections] = useState<EnrichmentSection>({});

  // Fetch contact on load
  useEffect(() => {
    fetchContact();
  }, [id]);

  // Poll enrichment status if pending
  useEffect(() => {
    if (contact?.enrichmentstatus === 'pending') {
      const interval = setInterval(() => {
        checkEnrichmentStatus();
      }, 3000);
      return () => clearInterval(interval);
    }
  }, [contact?.enrichmentstatus, id]);

  const fetchContact = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${config.APIBASEURL}/api/contacts/${id}`);
      const data = await response.json();
      
      if (data.success && data.contact) {
        const contactData = data.contact;
        setContact(contactData);
        
        // Parse enrichment sections
        if (contactData.enrichmentdata?.sections) {
          setSections(contactData.enrichmentdata.sections);
        }
      }
    } catch (error) {
      console.error('Error fetching contact:', error);
    } finally {
      setLoading(false);
    }
  };

  const checkEnrichmentStatus = async () => {
    try {
      const response = await fetch(
        `${config.APIBASEURL}/api/contacts/${id}/enrichment-status`
      );
      const data = await response.json();
      
      if (data.enrichment_status === 'completed') {
        // Refresh contact data
        fetchContact();
      }
      
      setContact(prev => prev ? {
        ...prev,
        enrichmentstatus: data.enrichment_status,
        enrichedat: data.enriched_at
      } : null);
    } catch (error) {
      console.error('Error checking enrichment status:', error);
    }
  };

  const startEnrichment = async () => {
    if (!id) return;
    
    try {
      setEnriching(true);
      const response = await fetch(
        `${config.APIBASEURL}/api/contacts/${id}/enrich`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' }
        }
      );
      
      const data = await response.json();
      
      if (data.success) {
        setContact(prev => prev ? {
          ...prev,
          enrichmentstatus: 'pending'
        } : null);
        
        // Start polling
        const pollInterval = setInterval(async () => {
          const statusRes = await fetch(
            `${config.APIBASEURL}/api/contacts/${id}/enrichment-status`
          );
          const statusData = await statusRes.json();
          
          if (statusData.enrichment_status === 'completed') {
            clearInterval(pollInterval);
            setEnriching(false);
            fetchContact();
          }
        }, 3000);
      }
    } catch (error) {
      console.error('Error starting enrichment:', error);
      setEnriching(false);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const getSectionTitle = (key: string): string => {
    return key
      .replace(/_/g, ' ')
      .split(' ')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-gray-600">Loading contact...</p>
        </div>
      </div>
    );
  }

  if (!contact) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen">
        <div className="text-center">
          <p className="text-2xl font-bold text-gray-900 mb-4">Contact Not Found</p>
          <button
            onClick={() => navigate('/contacts')}
            className="text-primary hover:underline flex items-center gap-2"
          >
            <ArrowLeft size={20} />
            Back to Contacts
          </button>
        </div>
      </div>
    );
  }

  const enrichmentDataJson = contact.enrichmentdata 
    ? JSON.stringify(contact.enrichmentdata, null, 2)
    : null;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 sticky top-0 z-40">
        <div className="max-w-6xl mx-auto px-6 py-6">
          <div className="flex items-center justify-between mb-4">
            <button
              onClick={() => navigate('/contacts')}
              className="flex items-center gap-2 text-gray-600 hover:text-gray-900"
            >
              <ArrowLeft size={20} />
              Back
            </button>
            
            {contact.enrichmentstatus === 'completed' ? (
              <span className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm font-medium">
                ✅ Enriched
              </span>
            ) : contact.enrichmentstatus === 'pending' ? (
              <span className="px-3 py-1 bg-yellow-100 text-yellow-700 rounded-full text-sm font-medium animate-pulse">
                ⏳ Enriching...
              </span>
            ) : (
              <button
                onClick={startEnrichment}
                disabled={enriching}
                className="flex items-center gap-2 px-4 py-2 bg-primary text-white rounded-lg hover:bg-blue-600 disabled:opacity-50"
              >
                <RefreshCw size={18} />
                {enriching ? 'Enriching...' : 'Enrich'}
              </button>
            )}
          </div>

          {/* Contact Header */}
          <div className="flex items-start gap-6">
            <div className="flex-1">
              <h1 className="text-3xl font-bold text-gray-900 mb-2">{contact.name}</h1>
              <div className="space-y-1 text-gray-600">
                {contact.title && <p>{contact.title}</p>}
                {contact.company && <p className="font-medium text-gray-900">{contact.company}</p>}
                {contact.email && <p>{contact.email}</p>}
              </div>
            </div>

            {/* Quick Links */}
            <div className="flex flex-col gap-2">
              {contact.linkedinurl && (
                <a
                  href={contact.linkedinurl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm"
                >
                  LinkedIn
                </a>
              )}
              {contact.phone && (
                <a
                  href={`tel:${contact.phone}`}
                  className="px-4 py-2 bg-gray-100 text-gray-900 rounded-lg hover:bg-gray-200 text-sm"
                >
                  {contact.phone}
                </a>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-6xl mx-auto px-6">
          <div className="flex gap-8">
            {(['overview', 'enrichment', 'raw'] as const).map(tab => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`py-4 px-1 border-b-2 font-medium transition ${
                  activeTab === tab
                    ? 'border-primary text-primary'
                    : 'border-transparent text-gray-600 hover:text-gray-900'
                }`}
              >
                {tab.charAt(0).toUpperCase() + tab.slice(1)}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-6xl mx-auto px-6 py-8">
        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {contact.title && (
              <div className="bg-white p-6 rounded-lg border border-gray-200">
                <p className="text-gray-600 text-sm font-medium mb-2">Title</p>
                <p className="text-lg font-medium text-gray-900">{contact.title}</p>
              </div>
            )}
            {contact.company && (
              <div className="bg-white p-6 rounded-lg border border-gray-200">
                <p className="text-gray-600 text-sm font-medium mb-2">Company</p>
                <p className="text-lg font-medium text-gray-900">{contact.company}</p>
              </div>
            )}
            {contact.email && (
              <div className="bg-white p-6 rounded-lg border border-gray-200">
                <p className="text-gray-600 text-sm font-medium mb-2">Email</p>
                <p className="text-lg font-medium text-gray-900 break-all">{contact.email}</p>
              </div>
            )}
            {contact.phone && (
              <div className="bg-white p-6 rounded-lg border border-gray-200">
                <p className="text-gray-600 text-sm font-medium mb-2">Phone</p>
                <p className="text-lg font-medium text-gray-900">{contact.phone}</p>
              </div>
            )}
          </div>
        )}

        {/* Enrichment Tab */}
        {activeTab === 'enrichment' && (
          <div>
            {contact.enrichmentstatus === 'completed' && Object.keys(sections).length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {Object.entries(sections).map(([key, value]) => (
                  <div key={key} className="bg-white p-6 rounded-lg border border-gray-200">
                    <h3 className="font-bold text-gray-900 mb-3">
                      {getSectionTitle(key)}
                    </h3>
                    <p className="text-gray-700 text-sm whitespace-pre-wrap leading-relaxed">
                      {typeof value === 'string' ? value : JSON.stringify(value)}
                    </p>
                  </div>
                ))}
              </div>
            ) : contact.enrichmentstatus === 'pending' ? (
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-8 text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-yellow-600 mx-auto mb-4"></div>
                <p className="text-yellow-900 font-medium">Enrichment in progress...</p>
                <p className="text-yellow-700 text-sm mt-2">This usually takes 60-90 seconds</p>
              </div>
            ) : (
              <div className="bg-gray-50 border border-gray-200 rounded-lg p-8 text-center">
                <Eye size={32} className="mx-auto text-gray-400 mb-4" />
                <p className="text-gray-600">No enrichment data yet</p>
                <button
                  onClick={startEnrichment}
                  className="mt-4 px-4 py-2 bg-primary text-white rounded-lg hover:bg-blue-600"
                >
                  Start Enrichment
                </button>
              </div>
            )}
          </div>
        )}

        {/* Raw Data Tab */}
        {activeTab === 'raw' && (
          <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
            <div className="flex items-center justify-between p-4 bg-gray-50 border-b border-gray-200">
              <p className="text-sm font-medium text-gray-600">Raw Enrichment JSON</p>
              <button
                onClick={() => enrichmentDataJson && copyToClipboard(enrichmentDataJson)}
                className="flex items-center gap-2 px-3 py-1 text-sm text-gray-600 hover:text-gray-900 bg-white border border-gray-200 rounded"
              >
                {copied ? (
                  <>
                    <Check size={16} />
                    Copied!
                  </>
                ) : (
                  <>
                    <Copy size={16} />
                    Copy
                  </>
                )}
              </button>
            </div>
            <pre className="p-6 overflow-x-auto text-xs text-gray-700 bg-gray-50">
              {enrichmentDataJson || 'No enrichment data available'}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
};

export default ContactDetailPage;
