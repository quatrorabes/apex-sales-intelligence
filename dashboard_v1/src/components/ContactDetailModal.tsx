import { useState, useEffect } from 'react';
import { X } from 'lucide-react';

interface Contact {
  id: number;
  name: string;
  email: string;
  company: string;
  title: string;
  phone?: string;
  linkedin_url?: string;
  enrichment_status?: string;
  profile_content?: string;
  mdcp_score?: number;
  mdcp_tier?: string;
  rss_score?: number;
  priority_score?: number;
  last_enriched?: string;
  created_at?: string;
}

interface ContactDetailModalProps {
  contactId: number;
  onClose: () => void;
}

export default function ContactDetailModal({ contactId, onClose }: ContactDetailModalProps) {
  const [contact, setContact] = useState<Contact | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'profile' | 'scores' | 'activity'>('profile');

  useEffect(() => {
    fetchContactDetails();
  }, [contactId]);

  const fetchContactDetails = async () => {
    try {
      setLoading(true);
      const response = await fetch(`http://localhost:8000/api/contacts/${contactId}`);
      if (!response.ok) throw new Error('Failed to fetch contact');
      const data = await response.json();
      setContact(data);
    } catch (error) {
      console.error('Error fetching contact:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatProfileContent = (content: string) => {
    if (!content) return null;

    // Split by headings (###) to create sections
    const sections = content.split(/###\s+/);
    
    return sections.filter(s => s.trim()).map((section, idx) => {
      const lines = section.trim().split('\n');
      const heading = lines[0];
      const body = lines.slice(1).join('\n').trim();

      if (!body) return null;

      return (
        <div key={idx} className="mb-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-2 border-b pb-1">
            {heading}
          </h3>
          <div className="text-gray-700 whitespace-pre-wrap leading-relaxed">
            {body}
          </div>
        </div>
      );
    });
  };

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-8">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="text-gray-600 mt-4">Loading contact details...</p>
        </div>
      </div>
    );
  }

  if (!contact) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-8 max-w-md">
          <p className="text-red-600">Failed to load contact details</p>
          <button
            onClick={onClose}
            className="mt-4 px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700"
          >
            Close
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-2xl max-w-5xl w-full max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white p-6 rounded-t-lg flex justify-between items-start">
          <div className="flex-1">
            <h2 className="text-2xl font-bold mb-1">{contact.name}</h2>
            <p className="text-indigo-100">{contact.title}</p>
            <p className="text-indigo-200 text-sm">{contact.company}</p>
            <div className="mt-3 flex gap-3 text-sm">
              {contact.email && (
                <a href={`mailto:${contact.email}`} className="hover:text-white">
                  📧 {contact.email}
                </a>
              )}
              {contact.linkedin_url && (
                <a 
                  href={contact.linkedin_url} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="hover:text-white"
                >
                  🔗 LinkedIn
                </a>
              )}
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-white hover:bg-white hover:bg-opacity-20 rounded-full p-2"
          >
            <X size={24} />
          </button>
        </div>

        {/* Scores Bar */}
        {(contact.mdcp_score || contact.rss_score) && (
          <div className="bg-gray-50 px-6 py-3 border-b flex gap-6">
            {contact.mdcp_score && (
              <div>
                <span className="text-xs text-gray-600">MDCP Score</span>
                <div className="flex items-center gap-2">
                  <span className="text-xl font-bold text-indigo-600">{contact.mdcp_score}</span>
                  <span className={`text-xs px-2 py-1 rounded ${
                    contact.mdcp_tier === 'HOT' ? 'bg-red-100 text-red-700' :
                    contact.mdcp_tier === 'WARM' ? 'bg-orange-100 text-orange-700' :
                    'bg-blue-100 text-blue-700'
                  }`}>
                    {contact.mdcp_tier}
                  </span>
                </div>
              </div>
            )}
            {contact.rss_score && (
              <div>
                <span className="text-xs text-gray-600">RSS Score</span>
                <div className="text-xl font-bold text-purple-600">{contact.rss_score}</div>
              </div>
            )}
            {contact.enrichment_status && (
              <div className="ml-auto">
                <span className="text-xs text-gray-600">Enrichment</span>
                <div className={`text-sm font-semibold ${
                  contact.enrichment_status === 'completed' ? 'text-green-600' :
                  contact.enrichment_status === 'pending' ? 'text-yellow-600' :
                  'text-gray-600'
                }`}>
                  {contact.enrichment_status.toUpperCase()}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Tabs */}
        <div className="border-b px-6">
          <div className="flex gap-6">
            <button
              onClick={() => setActiveTab('profile')}
              className={`py-3 border-b-2 font-semibold transition-colors ${
                activeTab === 'profile'
                  ? 'border-indigo-600 text-indigo-600'
                  : 'border-transparent text-gray-600 hover:text-gray-900'
              }`}
            >
              📋 Profile
            </button>
            <button
              onClick={() => setActiveTab('scores')}
              className={`py-3 border-b-2 font-semibold transition-colors ${
                activeTab === 'scores'
                  ? 'border-indigo-600 text-indigo-600'
                  : 'border-transparent text-gray-600 hover:text-gray-900'
              }`}
            >
              📊 Scores
            </button>
            <button
              onClick={() => setActiveTab('activity')}
              className={`py-3 border-b-2 font-semibold transition-colors ${
                activeTab === 'activity'
                  ? 'border-indigo-600 text-indigo-600'
                  : 'border-transparent text-gray-600 hover:text-gray-900'
              }`}
            >
              📅 Activity
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {activeTab === 'profile' && (
            <div>
              {contact.profile_content ? (
                <div className="prose max-w-none">
                  {formatProfileContent(contact.profile_content)}
                </div>
              ) : (
                <div className="text-center py-12 bg-gray-50 rounded-lg">
                  <p className="text-gray-500 mb-4">No enrichment data available</p>
                  <p className="text-sm text-gray-400">
                    {contact.enrichment_status === 'pending' 
                      ? 'Enrichment in progress...'
                      : 'Click "Enrich" to generate profile intelligence'}
                  </p>
                </div>
              )}
            </div>
          )}

          {activeTab === 'scores' && (
            <div className="space-y-4">
              <div className="bg-white border rounded-lg p-4">
                <h3 className="font-semibold text-gray-900 mb-3">Scoring Summary</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm text-gray-600">MDCP Score</label>
                    <div className="text-2xl font-bold text-indigo-600">
                      {contact.mdcp_score || 'N/A'}
                    </div>
                  </div>
                  <div>
                    <label className="text-sm text-gray-600">RSS Score</label>
                    <div className="text-2xl font-bold text-purple-600">
                      {contact.rss_score || 'N/A'}
                    </div>
                  </div>
                  <div>
                    <label className="text-sm text-gray-600">Priority</label>
                    <div className="text-2xl font-bold text-green-600">
                      {contact.priority_score || 'N/A'}
                    </div>
                  </div>
                  <div>
                    <label className="text-sm text-gray-600">Tier</label>
                    <div className="text-lg font-semibold">
                      {contact.mdcp_tier || 'UNSCORED'}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'activity' && (
            <div>
              <p className="text-gray-500">Activity timeline coming soon...</p>
              {contact.last_enriched && (
                <div className="mt-4 text-sm text-gray-600">
                  Last enriched: {new Date(contact.last_enriched).toLocaleString()}
                </div>
              )}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="border-t p-4 bg-gray-50 rounded-b-lg flex justify-between items-center">
          <div className="text-xs text-gray-500">
            Contact ID: {contact.id}
          </div>
          <div className="flex gap-2">
            <button
              onClick={onClose}
              className="px-4 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300"
            >
              Close
            </button>
            <button className="px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700">
              Edit Contact
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
