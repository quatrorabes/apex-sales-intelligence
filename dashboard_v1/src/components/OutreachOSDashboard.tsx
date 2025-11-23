import React, { useState, useEffect } from 'react';
import type { Contact, DashboardMetrics } from '../lib/api';
import { getContacts, getDashboardMetrics, enrichContact, generateCallScript, generateEmail } from '../lib/api';

export default function OutreachOSDashboard() {
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [selectedContact, setSelectedContact] = useState<Contact | null>(null);
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [actionLoading, setActionLoading] = useState(false);
  const [generatedContent, setGeneratedContent] = useState<any>(null);

  // Load data on mount
  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [contactsData, metricsData] = await Promise.all([
        getContacts(),
        getDashboardMetrics()
      ]);
      setContacts(contactsData);
      setMetrics(metricsData);
      setError(null);
    } catch (err) {
      setError('Failed to load data from API');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleEnrichContact = async (contactId: number) => {
    try {
      setActionLoading(true);
      const result = await enrichContact(contactId);
      alert(result.message);
      loadData();
    } catch (err) {
      alert('Enrichment failed: ' + (err as Error).message);
    } finally {
      setActionLoading(false);
    }
  };

  const handleGenerateCallScript = async (contactId: number) => {
    try {
      setActionLoading(true);
      const result = await generateCallScript(contactId);
      setGeneratedContent(result);
      alert('Call script generated!');
    } catch (err) {
      alert('Script generation failed: ' + (err as Error).message);
    } finally {
      setActionLoading(false);
    }
  };

  const handleGenerateEmail = async (contactId: number) => {
    try {
      setActionLoading(true);
      const result = await generateEmail(contactId);
      setGeneratedContent(result);
      alert('Email generated!');
    } catch (err) {
      alert('Email generation failed: ' + (err as Error).message);
    } finally {
      setActionLoading(false);
    }
  };

  if (loading) return <div className="p-8 text-center">Loading APEX Intelligence...</div>;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-800 shadow-lg">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <h1 className="text-3xl font-bold text-white">APEX Sales Intelligence</h1>
          <p className="text-blue-100 mt-1">AI-powered outreach platform | Backend: {import.meta.env.VITE_API_URL}</p>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Dashboard Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-8">
          <div className="bg-white rounded-lg shadow p-6 border-l-4 border-blue-500">
            <h3 className="text-sm font-medium text-gray-500">Total Contacts</h3>
            <p className="text-3xl font-bold text-gray-900 mt-2">{metrics?.total_contacts || 0}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-6 border-l-4 border-green-500">
            <h3 className="text-sm font-medium text-gray-500">Enriched</h3>
            <p className="text-3xl font-bold text-gray-900 mt-2">{metrics?.enriched_contacts || 0}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-6 border-l-4 border-purple-500">
            <h3 className="text-sm font-medium text-gray-500">Open Rate</h3>
            <p className="text-3xl font-bold text-gray-900 mt-2">{(metrics?.open_rate || 0).toFixed(1)}%</p>
          </div>
          <div className="bg-white rounded-lg shadow p-6 border-l-4 border-orange-500">
            <h3 className="text-sm font-medium text-gray-500">Sent</h3>
            <p className="text-3xl font-bold text-gray-900 mt-2">{metrics?.total_sent || 0}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-6 border-l-4 border-red-500">
            <h3 className="text-sm font-medium text-gray-500">Errors</h3>
            <p className="text-3xl font-bold text-gray-900 mt-2">0</p>
          </div>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6 text-red-700">
            {error}
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Contacts Panel */}
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <div className="p-4 border-b bg-gray-50">
              <h2 className="text-lg font-semibold text-gray-900">
                Contacts ({contacts.length})
              </h2>
            </div>
            <div className="divide-y max-h-screen overflow-y-auto">
              {contacts.length === 0 ? (
                <div className="p-4 text-gray-500 text-center">No contacts found</div>
              ) : (
                contacts.map(contact => (
                  <div
                    key={contact.id}
                    onClick={() => setSelectedContact(contact)}
                    className={`p-4 cursor-pointer hover:bg-blue-50 transition ${
                      selectedContact?.id === contact.id ? 'bg-blue-100 border-l-4 border-blue-500' : ''
                    }`}
                  >
                    <div className="flex justify-between items-start gap-2">
                      <div className="flex-1 min-w-0">
                        <h3 className="font-semibold text-gray-900 truncate">
                          {contact.name || 'Unknown'}
                        </h3>
                        <p className="text-xs text-gray-600 truncate mt-1">
                          {contact.title || '—'}
                        </p>
                        <p className="text-xs text-gray-500 truncate mt-0.5">
                          {contact.company || 'No company'}
                        </p>
                      </div>
                      {contact.enriched ? (
                        <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded whitespace-nowrap font-semibold">
                          ✓ Enriched
                        </span>
                      ) : (
                        <span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded whitespace-nowrap">
                          Pending
                        </span>
                      )}
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Contact Details */}
          <div className="lg:col-span-2 bg-white rounded-lg shadow overflow-hidden">
            <div className="p-6">
              {selectedContact ? (
                <div>
                  {/* Header */}
                  <div className="mb-6">
                    <div className="flex justify-between items-start mb-4">
                      <div>
                        <h2 className="text-2xl font-bold text-gray-900">{selectedContact.name}</h2>
                        <p className="text-gray-600 mt-1">
                          {selectedContact.title || '—'}
                          {selectedContact.company && ` · ${selectedContact.company}`}
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="text-sm text-gray-500">
                          Score: <span className="font-bold text-gray-900">{selectedContact.opportunity_score || '—'}</span>
                        </p>
                        <p className="text-sm text-gray-500 mt-1">
                          Persona: <span className="font-bold text-gray-900">{selectedContact.persona_name || '—'}</span>
                        </p>
                      </div>
                    </div>
                    <div className="h-1 bg-gradient-to-r from-blue-500 to-purple-500 rounded"></div>
                  </div>

                  {/* Contact Info */}
                  <div className="grid grid-cols-2 gap-4 mb-6 p-4 bg-gray-50 rounded-lg">
                    <div>
                      <label className="text-xs font-semibold text-gray-500 uppercase">Email</label>
                      <p className="text-gray-900 mt-1 break-all">{selectedContact.email || '—'}</p>
                    </div>
                    <div>
                      <label className="text-xs font-semibold text-gray-500 uppercase">Phone</label>
                      <p className="text-gray-900 mt-1">{selectedContact.phone || '—'}</p>
                    </div>
                    <div className="col-span-2">
                      <label className="text-xs font-semibold text-gray-500 uppercase">LinkedIn</label>
                      <p className="text-gray-900 mt-1">
                        {selectedContact.linkedin_url ? (
                          <a href={selectedContact.linkedin_url} target="_blank" rel="noreferrer" className="text-blue-600 hover:underline">
                            View Profile →
                          </a>
                        ) : (
                          '—'
                        )}
                      </p>
                    </div>
                  </div>

                  {/* Action Buttons */}
                  <div className="mb-6 space-y-3">
                    <h3 className="text-sm font-semibold text-gray-900 uppercase">Generate Outreach Assets</h3>
                    <div className="flex flex-wrap gap-3">
                      {!selectedContact.enriched && (
                        <button
                          onClick={() => handleEnrichContact(selectedContact.id)}
                          disabled={actionLoading}
                          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 font-medium text-sm"
                        >
                          {actionLoading ? '⏳ Enriching...' : '🔍 Enrich with AI'}
                        </button>
                      )}
                      <button
                        onClick={() => handleGenerateCallScript(selectedContact.id)}
                        disabled={actionLoading}
                        className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50 font-medium text-sm"
                      >
                        {actionLoading ? '⏳ Generating...' : '📞 Call Script'}
                      </button>
                      <button
                        onClick={() => handleGenerateEmail(selectedContact.id)}
                        disabled={actionLoading}
                        className="px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700 disabled:opacity-50 font-medium text-sm"
                      >
                        {actionLoading ? '⏳ Generating...' : '✉️ Email'}
                      </button>
                    </div>
                  </div>

                  {/* Enrichment Data */}
                  {selectedContact.enriched && selectedContact.enrichment_data && (
                    <div className="border-t pt-4">
                      <h3 className="text-sm font-semibold text-gray-900 uppercase mb-3">AI Enrichment Data</h3>
                      <div className="bg-gray-50 p-4 rounded text-xs font-mono overflow-auto max-h-40">
                        <pre>{JSON.stringify(selectedContact.enrichment_data, null, 2)}</pre>
                      </div>
                    </div>
                  )}

                  {/* Generated Content */}
                  {generatedContent && (
                    <div className="border-t pt-4 mt-4">
                      <h3 className="text-sm font-semibold text-gray-900 uppercase mb-3">Generated Content</h3>
                      <div className="bg-blue-50 p-4 rounded text-sm border border-blue-200 max-h-40 overflow-auto">
                        <pre className="whitespace-pre-wrap break-words">
                          {JSON.stringify(generatedContent, null, 2)}
                        </pre>
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-center py-16 text-gray-500">
                  <p className="text-lg">👈 Select a contact to view details</p>
                  <p className="text-sm mt-2">Contact information and AI-generated assets will appear here</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}