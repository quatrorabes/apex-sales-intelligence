import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { apiClient } from '../config/api';
import { Phone, Mail, Linkedin, FileText, Zap, AlertCircle } from 'lucide-react';

interface Contact {
  id: string;
  name: string;
  email: string;
  company: string;
  title: string;
  phone: string;
  apex_score: number;
  match_tier: string;
  enrichment_status: string;
}

interface OutreachContent {
  email_1_subject?: string;
  email_1_body?: string;
  call_script_1?: string;
  linkedin_connection_note?: string;
  has_content: boolean;
}

export default function ContactDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  
  const [contact, setContact] = useState<Contact | null>(null);
  const [outreach, setOutreach] = useState<OutreachContent | null>(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadContactData();
  }, [id]);

  const loadContactData = async () => {
    try {
      setLoading(true);
      const response = await apiClient.get(`/api/contacts/${id}`);
      setContact(response.data);
      
      // Load outreach content if exists
      try {
        const outreachRes = await apiClient.get(`/api/contacts/${id}/outreach-content`);
        setOutreach(outreachRes.data);
      } catch (err) {
        setOutreach({ has_content: false });
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const generateContent = async (type: string) => {
    try {
      setGenerating(type);
      setError(null);
      
      const endpoint = `/api/contacts/${id}/generate-${type}`;
      await apiClient.post(endpoint);
      
      // Reload outreach content
      await loadContactData();
      
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to generate content');
    } finally {
      setGenerating(null);
    }
  };

  const openCallAssistant = () => {
    navigate(`/contacts/${id}/call-assistant`);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  if (!contact) {
    return (
      <div className="text-center py-12">
        <AlertCircle className="mx-auto h-12 w-12 text-gray-400" />
        <h3 className="mt-2 text-sm font-medium text-gray-900">Contact not found</h3>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="bg-white shadow rounded-lg p-6 mb-6">
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">{contact.name}</h1>
            <p className="text-lg text-gray-600">{contact.title}</p>
            <p className="text-md text-gray-500">{contact.company}</p>
          </div>
          
          <div className="text-right">
            <div className="text-sm text-gray-500">APEX Score</div>
            <div className="text-4xl font-bold text-indigo-600">{contact.apex_score}</div>
            <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
              contact.match_tier === 'HIGH' ? 'bg-green-100 text-green-800' :
              contact.match_tier === 'MEDIUM' ? 'bg-yellow-100 text-yellow-800' :
              'bg-gray-100 text-gray-800'
            }`}>
              {contact.match_tier} TIER
            </div>
          </div>
        </div>

        {/* Contact Info */}
        <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="flex items-center text-gray-600">
            <Mail className="h-5 w-5 mr-2" />
            {contact.email || 'No email'}
          </div>
          <div className="flex items-center text-gray-600">
            <Phone className="h-5 w-5 mr-2" />
            {contact.phone || 'No phone'}
          </div>
          <div className="flex items-center text-gray-600">
            <Linkedin className="h-5 w-5 mr-2" />
            LinkedIn
          </div>
        </div>
      </div>

      {/* Outreach Actions */}
      <div className="bg-white shadow rounded-lg p-6 mb-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Outreach Tools</h2>
        
        {error && (
          <div className="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Call Assistant */}
          <button
            onClick={openCallAssistant}
            className="flex flex-col items-center p-6 border-2 border-indigo-600 rounded-lg hover:bg-indigo-50 transition-colors"
          >
            <Phone className="h-8 w-8 text-indigo-600 mb-2" />
            <span className="font-semibold text-gray-900">Call Assistant</span>
            <span className="text-sm text-gray-500 mt-1">Real-time guidance</span>
          </button>

          {/* Generate Email */}
          <button
            onClick={() => generateContent('email')}
            disabled={generating === 'email'}
            className="flex flex-col items-center p-6 border-2 border-gray-300 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50"
          >
            <Mail className="h-8 w-8 text-gray-600 mb-2" />
            <span className="font-semibold text-gray-900">
              {generating === 'email' ? 'Generating...' : 'Email Sequence'}
            </span>
            <span className="text-sm text-gray-500 mt-1">3 emails</span>
          </button>

          {/* Generate Call Scripts */}
          <button
            onClick={() => generateContent('coldcall')}
            disabled={generating === 'coldcall'}
            className="flex flex-col items-center p-6 border-2 border-gray-300 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50"
          >
            <FileText className="h-8 w-8 text-gray-600 mb-2" />
            <span className="font-semibold text-gray-900">
              {generating === 'coldcall' ? 'Generating...' : 'Call Scripts'}
            </span>
            <span className="text-sm text-gray-500 mt-1">3 variants</span>
          </button>

          {/* Generate LinkedIn */}
          <button
            onClick={() => generateContent('linkedin')}
            disabled={generating === 'linkedin'}
            className="flex flex-col items-center p-6 border-2 border-gray-300 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50"
          >
            <Linkedin className="h-8 w-8 text-gray-600 mb-2" />
            <span className="font-semibold text-gray-900">
              {generating === 'linkedin' ? 'Generating...' : 'LinkedIn Message'}
            </span>
            <span className="text-sm text-gray-500 mt-1">Connection + follow-up</span>
          </button>
        </div>

        {/* Generate All */}
        <button
          onClick={() => generateContent('all-content')}
          disabled={generating === 'all-content'}
          className="mt-4 w-full flex items-center justify-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50"
        >
          <Zap className="h-5 w-5 mr-2" />
          {generating === 'all-content' ? 'Generating All Content...' : 'Generate Complete Outreach Package'}
        </button>
      </div>

      {/* Generated Content Preview */}
      {outreach?.has_content && (
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Generated Content</h2>
          
          {outreach.email_1_subject && (
            <div className="mb-4">
              <h3 className="font-semibold text-gray-700">Email #1</h3>
              <p className="text-sm text-gray-600 font-medium">{outreach.email_1_subject}</p>
              <p className="text-sm text-gray-500 mt-1 whitespace-pre-wrap">{outreach.email_1_body?.substring(0, 200)}...</p>
            </div>
          )}
          
          {outreach.call_script_1 && (
            <div className="mb-4">
              <h3 className="font-semibold text-gray-700">Call Script #1</h3>
              <p className="text-sm text-gray-500 whitespace-pre-wrap">{outreach.call_script_1?.substring(0, 200)}...</p>
            </div>
          )}
          
          {outreach.linkedin_connection_note && (
            <div className="mb-4">
              <h3 className="font-semibold text-gray-700">LinkedIn Connection Request</h3>
              <p className="text-sm text-gray-500">{outreach.linkedin_connection_note}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
