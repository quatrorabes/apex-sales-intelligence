import React, { useState, useEffect } from 'react';
import {
  Database,
  Search,
  ChevronDown,
  ChevronRight,
  Copy,
  CheckCircle2,
  Download
} from 'lucide-react';

interface Contact {
  id: number;
  [key: string]: any;
}

export default function RawDataViewer() {
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [selectedContact, setSelectedContact] = useState<Contact | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set(['Basic Info']));
  const [copiedField, setCopiedField] = useState<string>('');

  const API_BASE = 'https://apex-intelligence-production.up.railway.app';

  useEffect(() => {
    fetchContacts();
  }, []);

  const fetchContacts = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/contacts`);
      const data = await response.json();
      setContacts(data.contacts || []);
      if (data.contacts?.length > 0 && !selectedContact) {
        setSelectedContact(data.contacts[0]);
      }
    } catch (error) {
      console.error('Error fetching contacts:', error);
    }
  };

  const toggleSection = (section: string) => {
    const newExpanded = new Set(expandedSections);
    if (newExpanded.has(section)) {
      newExpanded.delete(section);
    } else {
      newExpanded.add(section);
    }
    setExpandedSections(newExpanded);
  };

  const copyToClipboard = (text: string, field: string) => {
    navigator.clipboard.writeText(text);
    setCopiedField(field);
    setTimeout(() => setCopiedField(''), 2000);
  };

  const exportJSON = () => {
    if (!selectedContact) return;
    
    const dataStr = JSON.stringify(selectedContact, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `contact_${selectedContact.id}_${selectedContact.name?.replace(/\s+/g, '_')}.json`;
    link.click();
  };

  const filteredContacts = contacts.filter(contact =>
    contact.name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    contact.email?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    contact.company?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // Group fields by category
  const categorizeFields = (contact: Contact) => {
    const categories: Record<string, Record<string, any>> = {
      'Basic Info': {},
      'Contact Details': {},
      'HubSpot Data': {},
      'Enrichment Data': {},
      'Scoring & Cadence': {},
      'Activity': {},
      'System': {}
    };

    const basicFields = ['id', 'name', 'first_name', 'last_name', 'title', 'company', 'industry'];
    const contactFields = ['email', 'phone', 'linkedin_url', 'sales_nav_url', 'profile_picture_url'];
    const hubspotFields = ['hubspot_id', 'hs_object_id', 'lifecycle_stage', 'linkedin_connection_date', 'birthday'];
    const enrichmentFields = ['enrichment_status', 'enriched_at', 'enrichment_data', 'data_quality_score'];
    const scoringFields = ['opportunity_score', 'lead_tier', 'tier', 'persona_name', 'cadence_id', 'cadence_status', 'cadence_started_at'];
    const activityFields = ['last_activity_date', 'last_engagement_date', 'last_email_received', 'num_sales_activities', 'num_times_contacted', 'last_cadence_touch_at'];
    const systemFields = ['created_at', 'updated_at', 'best_time', 'contact_unworked'];

    Object.keys(contact).forEach(key => {
      const value = contact[key];
      if (basicFields.includes(key)) categories['Basic Info'][key] = value;
      else if (contactFields.includes(key)) categories['Contact Details'][key] = value;
      else if (hubspotFields.includes(key)) categories['HubSpot Data'][key] = value;
      else if (enrichmentFields.includes(key)) categories['Enrichment Data'][key] = value;
      else if (scoringFields.includes(key)) categories['Scoring & Cadence'][key] = value;
      else if (activityFields.includes(key)) categories['Activity'][key] = value;
      else if (systemFields.includes(key)) categories['System'][key] = value;
    });

    return categories;
  };

  if (!selectedContact) {
    return (
      <div className="max-w-7xl mx-auto px-6 py-6">
        <div className="text-center py-12">
          <Database className="w-12 h-12 text-slate-600 mx-auto mb-4" />
          <p className="text-slate-400">No contacts available</p>
        </div>
      </div>
    );
  }

  const categories = categorizeFields(selectedContact);

  return (
    <div className="max-w-7xl mx-auto px-6 py-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-white mb-2">Raw HubSpot Data</h2>
          <p className="text-slate-400">
            View all imported and enriched data for each contact
          </p>
        </div>
        
        <button
          onClick={exportJSON}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-all"
        >
          <Download className="w-4 h-4" />
          Export JSON
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Contact List */}
        <div className="lg:col-span-1">
          <div className="bg-slate-800 rounded-lg border border-slate-700">
            <div className="p-4 border-b border-slate-700">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 w-4 h-4" />
                <input
                  type="text"
                  placeholder="Search contacts..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 bg-slate-900 border border-slate-600 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
            
            <div className="max-h-[600px] overflow-y-auto">
              {filteredContacts.map((contact) => (
                <button
                  key={contact.id}
                  onClick={() => setSelectedContact(contact)}
                  className={`w-full p-4 text-left border-b border-slate-700 hover:bg-slate-700/50 transition-all ${
                    selectedContact.id === contact.id ? 'bg-slate-700/50 border-l-4 border-l-blue-500' : ''
                  }`}
                >
                  <div className="font-medium text-white mb-1">{contact.name || 'Unnamed'}</div>
                  <div className="text-sm text-slate-400">{contact.company || 'No company'}</div>
                  <div className="text-xs text-slate-500 mt-1">{contact.email || 'No email'}</div>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Data Viewer */}
        <div className="lg:col-span-2">
          <div className="bg-slate-800 rounded-lg border border-slate-700">
            <div className="p-4 border-b border-slate-700">
              <h3 className="text-xl font-bold text-white">{selectedContact.name || 'Unnamed Contact'}</h3>
              <p className="text-sm text-slate-400">{selectedContact.company || 'No company'}</p>
            </div>

            <div className="p-4 space-y-4 max-h-[600px] overflow-y-auto">
              {Object.entries(categories).map(([category, fields]) => {
                const hasData = Object.keys(fields).length > 0;
                if (!hasData) return null;

                return (
                  <div key={category} className="border border-slate-700 rounded-lg overflow-hidden">
                    <button
                      onClick={() => toggleSection(category)}
                      className="w-full p-4 bg-slate-900 hover:bg-slate-800 flex items-center justify-between transition-all"
                    >
                      <span className="font-semibold text-white">{category}</span>
                      {expandedSections.has(category) ? (
                        <ChevronDown className="w-5 h-5 text-slate-400" />
                      ) : (
                        <ChevronRight className="w-5 h-5 text-slate-400" />
                      )}
                    </button>

                    {expandedSections.has(category) && (
                      <div className="p-4 space-y-3">
                        {Object.entries(fields).map(([key, value]) => (
                          <div key={key} className="flex items-start justify-between gap-4 pb-3 border-b border-slate-700 last:border-0">
                            <div className="flex-1">
                              <div className="text-sm font-medium text-slate-300 mb-1">{key}</div>
                              <div className="text-sm text-slate-400 font-mono break-all">
                                {value === null || value === undefined || value === '' ? (
                                  <span className="text-slate-600 italic">null</span>
                                ) : typeof value === 'object' ? (
                                  <pre className="text-xs overflow-x-auto bg-slate-900 p-2 rounded">
                                    {JSON.stringify(value, null, 2)}
                                  </pre>
                                ) : (
                                  String(value)
                                )}
                              </div>
                            </div>
                            
                            <button
                              onClick={() => copyToClipboard(
                                typeof value === 'object' ? JSON.stringify(value) : String(value || ''), 
                                key
                              )}
                              className="p-2 hover:bg-slate-700 rounded transition-all flex-shrink-0"
                              title="Copy value"
                            >
                              {copiedField === key ? (
                                <CheckCircle2 className="w-4 h-4 text-green-400" />
                              ) : (
                                <Copy className="w-4 h-4 text-slate-400" />
                              )}
                            </button>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

