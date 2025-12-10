
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeft, Mail, Phone, Building2, MapPin, Linkedin, Globe,
  Sparkles, TrendingUp, MessageSquare, Calendar, Star, Zap,
  Clock, Target, Users, Award, Briefcase, ChevronDown, ChevronRight,
  RefreshCw, Loader2, ExternalLink
} from 'lucide-react';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://apex-backend-i7b0.onrender.com';

interface Contact {
  id: number;
  name: string;
  email?: string;
  phone?: string;
  company?: string;
  title?: string;
  linkedin_url?: string;
  enrichment_status?: string;
  enrichment_data?: string;
  enriched_at?: string;
  match_score?: number;
  match_tier?: string;
}

export function ContactDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  
  const [contact, setContact] = useState<Contact | null>(null);
  const [loading, setLoading] = useState(true);
  const [enriching, setEnriching] = useState(false);
  const [mainTab, setMainTab] = useState<'overview' | 'intelligence' | 'fit'>('overview');
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({
    overview: true,
    background: false,
    company: false,
    opportunities: true
  });

  useEffect(() => {
    if (id) {
      fetchContact();
    }
  }, [id]);

  const fetchContact = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/api/contacts/${id}`);
      if (!response.ok) throw new Error('Failed to fetch contact');
      const data = await response.json();
      setContact(data);
    } catch (error) {
      console.error('Error fetching contact:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleEnrich = async () => {
    if (!id) return;
    
    try {
      setEnriching(true);
      const response = await fetch(`${API_BASE_URL}/api/contacts/${id}/enrich`, {
        method: 'POST'
      });
      
      if (!response.ok) throw new Error('Enrichment failed');
      
      const result = await response.json();
      console.log('✅ Enrichment completed:', result);
      
      // Refresh contact data
      await fetchContact();
      
      // Switch to intelligence tab to show results
      setMainTab('intelligence');
    } catch (error) {
      console.error('❌ Enrichment error:', error);
      alert('Enrichment failed. Please try again.');
    } finally {
      setEnriching(false);
    }
  };

  const toggleSection = (section: string) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="flex items-center gap-2">
          <Loader2 className="w-6 h-6 animate-spin text-blue-600" />
          <span className="text-gray-600">Loading contact...</span>
        </div>
      </div>
    );
  }

  if (!contact) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen">
        <p className="text-gray-600 mb-4">Contact not found</p>
        <button
          onClick={() => navigate('/contacts')}
          className="text-blue-600 hover:text-blue-700 flex items-center gap-2"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Contacts
        </button>
      </div>
    );
  }

  // Parse enrichment data
  let enrichmentData: any = null;
  try {
    if (contact.enrichment_data) {
      enrichmentData = typeof contact.enrichment_data === 'string' 
        ? JSON.parse(contact.enrichment_data)
        : contact.enrichment_data;
    }
  } catch (error) {
    console.error('Error parsing enrichment data:', error);
  }

  const sections = enrichmentData?.sections || {};
  const hasEnrichment = contact.enrichment_status === 'completed' && enrichmentData;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <button
            onClick={() => navigate('/contacts')}
            className="flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-4"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Contacts
          </button>

          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-2">
                <h1 className="text-3xl font-bold text-gray-900">{contact.name}</h1>
                {contact.match_tier && (
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                    contact.match_tier === 'HIGH' ? 'bg-green-100 text-green-800' :
                    contact.match_tier === 'MEDIUM' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-gray-100 text-gray-800'
                  }`}>
                    {contact.match_tier} Priority
                  </span>
                )}
              </div>

              {contact.title && contact.company && (
                <p className="text-lg text-gray-600 mb-4">
                  {contact.title} at {contact.company}
                </p>
              )}

              {/* Contact Info */}
              <div className="flex flex-wrap gap-4 text-sm text-gray-600">
                {contact.email && (
                  <a href={`mailto:${contact.email}`} className="flex items-center gap-2 hover:text-blue-600">
                    <Mail className="w-4 h-4" />
                    {contact.email}
                  </a>
                )}
                {contact.phone && (
                  <a href={`tel:${contact.phone}`} className="flex items-center gap-2 hover:text-blue-600">
                    <Phone className="w-4 h-4" />
                    {contact.phone}
                  </a>
                )}
                {contact.linkedin_url && (
                  <a 
                    href={contact.linkedin_url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="flex items-center gap-2 hover:text-blue-600"
                  >
                    <Linkedin className="w-4 h-4" />
                    LinkedIn
                  </a>
                )}
              </div>
            </div>

            {/* Actions */}
            <div className="flex gap-3">
              <button
                onClick={handleEnrich}
                disabled={enriching || contact.enrichment_status === 'enriching'}
                className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg hover:from-purple-700 hover:to-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {enriching || contact.enrichment_status === 'enriching' ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Enriching...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4" />
                    {hasEnrichment ? 'Re-enrich' : 'Enrich Profile'}
                  </>
                )}
              </button>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex gap-6 border-b">
            {[
              { id: 'overview', label: 'Overview', icon: Users },
              { id: 'intelligence', label: 'AI Intelligence', icon: Sparkles },
              { id: 'fit', label: 'Why We Fit', icon: Target }
            ].map(({ id, label, icon: Icon }) => (
              <button
                key={id}
                onClick={() => setMainTab(id as any)}
                className={`flex items-center gap-2 px-4 py-3 border-b-2 transition-colors ${
                  mainTab === id
                    ? 'border-blue-600 text-blue-600'
                    : 'border-transparent text-gray-600 hover:text-gray-900'
                }`}
              >
                <Icon className="w-4 h-4" />
                {label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* OVERVIEW TAB */}
        {mainTab === 'overview' && (
          <div className="space-y-6">
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold mb-4">Contact Information</h2>
              <dl className="grid grid-cols-2 gap-4">
                <div>
                  <dt className="text-sm text-gray-500">Name</dt>
                  <dd className="text-base font-medium">{contact.name}</dd>
                </div>
                <div>
                  <dt className="text-sm text-gray-500">Company</dt>
                  <dd className="text-base font-medium">{contact.company || 'N/A'}</dd>
                </div>
                <div>
                  <dt className="text-sm text-gray-500">Title</dt>
                  <dd className="text-base font-medium">{contact.title || 'N/A'}</dd>
                </div>
                <div>
                  <dt className="text-sm text-gray-500">Match Score</dt>
                  <dd className="text-base font-medium">{contact.match_score || 0}</dd>
                </div>
              </dl>
            </div>
          </div>
        )}

        {/* INTELLIGENCE TAB */}
        {mainTab === 'intelligence' && (
          <div className="space-y-6">
            {!hasEnrichment ? (
              <div className="bg-white rounded-lg shadow p-12 text-center">
                <Sparkles className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  No AI Intelligence Yet
                </h3>
                <p className="text-gray-600 mb-6">
                  Enrich this contact to generate deep sales intelligence powered by AI
                </p>
                <button
                  onClick={handleEnrich}
                  disabled={enriching}
                  className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg hover:from-purple-700 hover:to-blue-700"
                >
                  <Sparkles className="w-5 h-5" />
                  Enrich Now
                </button>
              </div>
            ) : (
              <>
                {/* Profile Overview */}
                {sections.overview && (
                  <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg shadow-lg overflow-hidden">
                    <button
                      onClick={() => toggleSection('overview')}
                      className="w-full flex items-center justify-between p-6 text-left hover:bg-white/50 transition-colors"
                    >
                      <div className="flex items-center gap-3">
                        <div className="p-2 bg-blue-600 rounded-lg">
                          <Users className="w-5 h-5 text-white" />
                        </div>
                        <h3 className="text-xl font-semibold text-gray-900">
                          Professional Overview
                        </h3>
                      </div>
                      {expandedSections.overview ? (
                        <ChevronDown className="w-5 h-5 text-gray-600" />
                      ) : (
                        <ChevronRight className="w-5 h-5 text-gray-600" />
                      )}
                    </button>
                    {expandedSections.overview && (
                      <div className="px-6 pb-6">
                        <div className="prose max-w-none text-gray-700">
                          <div className="whitespace-pre-wrap leading-relaxed">
                            {sections.overview}
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {/* Company Intelligence */}
                {sections.company_info && sections.company_info.trim() && (
                  <div className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-lg shadow-lg overflow-hidden">
                    <button
                      onClick={() => toggleSection('company')}
                      className="w-full flex items-center justify-between p-6 text-left hover:bg-white/50 transition-colors"
                    >
                      <div className="flex items-center gap-3">
                        <div className="p-2 bg-purple-600 rounded-lg">
                          <Briefcase className="w-5 h-5 text-white" />
                        </div>
                        <h3 className="text-xl font-semibold text-gray-900">
                          Company Intelligence
                        </h3>
                      </div>
                      {expandedSections.company ? (
                        <ChevronDown className="w-5 h-5 text-gray-600" />
                      ) : (
                        <ChevronRight className="w-5 h-5 text-gray-600" />
                      )}
                    </button>
                    {expandedSections.company && (
                      <div className="px-6 pb-6">
                        <div className="prose max-w-none text-gray-700">
                          <div className="whitespace-pre-wrap leading-relaxed">
                            {sections.company_info}
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {/* Sales Opportunities */}
                {sections.sales_opportunities && sections.sales_opportunities.trim() && (
                  <div className="bg-gradient-to-br from-amber-50 to-orange-50 rounded-lg shadow-lg overflow-hidden">
                    <button
                      onClick={() => toggleSection('opportunities')}
                      className="w-full flex items-center justify-between p-6 text-left hover:bg-white/50 transition-colors"
                    >
                      <div className="flex items-center gap-3">
                        <div className="p-2 bg-amber-600 rounded-lg">
                          <TrendingUp className="w-5 h-5 text-white" />
                        </div>
                        <h3 className="text-xl font-semibold text-gray-900">
                          Sales Opportunities
                        </h3>
                      </div>
                      {expandedSections.opportunities ? (
                        <ChevronDown className="w-5 h-5 text-gray-600" />
                      ) : (
                        <ChevronRight className="w-5 h-5 text-gray-600" />
                      )}
                    </button>
                    {expandedSections.opportunities && (
                      <div className="px-6 pb-6">
                        <div className="prose max-w-none text-gray-700">
                          <div className="whitespace-pre-wrap leading-relaxed">
                            {sections.sales_opportunities}
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {/* Metadata Footer */}
                <div className="bg-white rounded-lg shadow p-4">
                  <div className="flex items-center justify-between text-sm text-gray-500">
                    <div className="flex items-center gap-2">
                      <Clock className="w-4 h-4" />
                      <span>
                        Enriched {contact.enriched_at ? new Date(contact.enriched_at).toLocaleDateString() : 'recently'}
                      </span>
                    </div>
                    {enrichmentData?.character_count && (
                      <span>{enrichmentData.character_count.toLocaleString()} characters</span>
                    )}
                  </div>
                </div>
              </>
            )}
          </div>
        )}

        {/* FIT TAB */}
        {mainTab === 'fit' && (
          <div className="bg-white rounded-lg shadow p-12 text-center">
            <Target className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              ICP Analysis Coming Soon
            </h3>
            <p className="text-gray-600">
              Set up your Ideal Customer Profile to see how well this contact matches
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
