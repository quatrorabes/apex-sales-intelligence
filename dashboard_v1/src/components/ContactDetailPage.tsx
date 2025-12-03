import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { ArrowLeft, Loader } from 'lucide-react';
import { apiClient } from '../utils/api';
import { Contact } from '../types';
import { ActivityTimeline } from './ActivityTimeline';
import { ActivityLogger } from './ActivityLogger';
import { ScoreExplainer } from './ScoreExplainer';

export const ContactDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [contact, setContact] = useState<Contact | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (id) {
      loadContact(parseInt(id));
    }
  }, [id]);

  const loadContact = async (contactId: number) => {
    setLoading(true);
    try {
      const data = await apiClient.getContact(contactId);
      setContact(data);
    } catch (error) {
      console.error('Failed to load contact:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <Loader className="h-8 w-8 animate-spin text-blue-600" />
      </div>
    );
  }

  if (!contact) {
    return (
      <div className="flex items-center justify-center h-screen">
        <p className="text-gray-500">Contact not found</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <button
          onClick={() => window.history.back()}
          className="flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-6"
        >
          <ArrowLeft className="h-4 w-4" />
          Back
        </button>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Contact Info */}
          <div className="lg:col-span-2 space-y-6">
            <div className="bg-white rounded-lg border p-6">
              <h1 className="text-2xl font-bold text-gray-900 mb-2">{contact.name}</h1>
              <p className="text-gray-600">{contact.title}</p>
              <p className="text-gray-600">{contact.company}</p>
              
              <div className="mt-4 space-y-2">
                {contact.email && (
                  <a href={`mailto:${contact.email}`} className="text-blue-600 hover:underline block">
                    {contact.email}
                  </a>
                )}
                {contact.phone && <p className="text-gray-600">{contact.phone}</p>}
                {contact.linkedin_url && (
                  <a
                    href={contact.linkedin_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:underline block"
                  >
                    LinkedIn Profile
                  </a>
                )}
              </div>
            </div>

            {/* Activity Timeline */}
            <div className="bg-white rounded-lg border p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Activity Timeline</h2>
              <ActivityTimeline activities={[]} />
            </div>
          </div>

          {/* Right Column - Scores & Actions */}
          <div className="space-y-6">
            <ScoreExplainer
              mdcpScore={contact.mdcp_score}
              mdcpTier={contact.mdcp_tier}
              priorityScore={contact.priority_score}
              urgencyLevel={contact.urgency_level}
              rssScore={contact.rss_score}
            />

            <ActivityLogger
              contactId={contact.id}
              onActivityLogged={() => loadContact(contact.id)}
            />
          </div>
        </div>
      </div>
    </div>
  );
};
