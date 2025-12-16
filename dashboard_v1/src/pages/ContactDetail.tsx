// dashboard_v1/src/pages/ContactDetail.tsx
// VERSION: Debug | Dec 15, 2025
// Added console logging to diagnose API fetch issue

import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeft, ChevronDown, ChevronUp, Zap, Loader2, Mail, Phone, Linkedin,
  Target, Clock, MessageSquare, Brain, Lightbulb, Send, Phone as PhoneIcon,
  CheckCircle2, Briefcase, Building2
} from 'lucide-react';

const API_BASE = import.meta.env.VITE_API_URL || import.meta.env.VITE_APEX_API_URL || 'https://apex-backend-i7b0.onrender.com';

interface Contact {
  id: string | number;
  first_name?: string;
  lastname?: string;
  name?: string;
  email?: string;
  phone?: string;
  company?: string;
  title?: string;
  enrichment_status?: string;
  enrichment_data?: any;
  profile_content?: string;
  apex_score?: number;
  match_tier?: string;
  linkedin_url?: string;
}

export default function ContactDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  
  const [contact, setContact] = useState<Contact | null>(null);
  const [loading, setLoading] = useState(true);
  const [enriching, setEnriching] = useState(false);
  const [error, setError] = useState<string>('');

  useEffect(() => {
    console.log('=== APEX ContactDetail Debug ===');
    console.log('Contact ID from URL:', id);
    console.log('API Base:', API_BASE);
    
    if (!id) {
      console.error('No contact ID in URL!');
      setError('No contact ID provided');
      setLoading(false);
      return;
    }
    fetchContact();
  }, [id]);

  async function fetchContact() {
    const url = `${API_BASE}/api/contacts/${id}`;
    console.log('Fetching from:', url);
    
    try {
      setLoading(true);
      const res = await fetch(url);
      console.log('Response status:', res.status);
      
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}: ${res.statusText}`);
      }
      
      const data = await res.json();
      console.log('Contact data received:', data);
      console.log('Contact keys:', Object.keys(data));
      
      setContact(data);
      setError('');
    } catch (err: any) {
      console.error('Fetch error:', err);
      setError(err.message || 'Failed to load contact');
    } finally {
      setLoading(false);
    }
  }

  async function handleEnrich() {
    if (!id) return;
    const url = `${API_BASE}/api/contacts/${id}/enrich`;
    console.log('Enriching via:', url);
    
    try {
      setEnriching(true);
      const res = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      console.log('Enrich response status:', res.status);
      
      if (!res.ok) throw new Error(`Enrichment failed: ${res.status}`);
      
      const result = await res.json();
      console.log('Enrich result:', result);
      
      await fetchContact();
    } catch (err: any) {
      console.error('Enrich error:', err);
      alert(err.message);
    } finally {
      setEnriching(false);
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0a0e1a] flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-12 h-12 text-blue-500 animate-spin mx-auto mb-4" />
          <p className="text-gray-400">Loading contact ID: {id}</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-[#0a0e1a] flex items-center justify-center">
        <div className="text-center max-w-2xl mx-auto p-8">
          <div className="text-red-400 text-xl mb-4">❌ Error Loading Contact</div>
          <div className="bg-red-900/20 border border-red-500/30 rounded-lg p-4 mb-4">
            <p className="text-white font-mono text-sm">{error}</p>
          </div>
          <div className="text-left text-sm text-gray-400 bg-gray-800 rounded-lg p-4 mb-4">
            <p className="font-semibold mb-2">Debug Info:</p>
            <p>• Contact ID: {id}</p>
            <p>• API Base: {API_BASE}</p>
            <p>• Full URL: {API_BASE}/api/contacts/{id}</p>
          </div>
          <button
            onClick={() => navigate('/contacts')}
            className="px-6 py-2 bg-[#1c2536] hover:bg-[#253447] text-white rounded-lg"
          >
            ← Back to Contacts
          </button>
        </div>
      </div>
    );
  }

  if (!contact) {
    return (
      <div className="min-h-screen bg-[#0a0e1a] flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-400 text-xl mb-4">Contact not found (ID: {id})</p>
          <button
            onClick={() => navigate('/contacts')}
            className="px-6 py-2 bg-[#1c2536] hover:bg-[#253447] text-white rounded-lg"
          >
            ← Back to Contacts
          </button>
        </div>
      </div>
    );
  }

  const displayName = contact.name || `${contact.first_name || ''} ${contact.lastname || ''}`.trim() || 'Unknown Contact';
  const isEnriched = contact.enrichment_status === 'completed';

  console.log('Rendering contact:', displayName);

  return (
    <div className="min-h-screen bg-[#0a0e1a] text-white">
      {/* HEADER */}
      <div className="bg-gradient-to-r from-[#1a4d4d] to-[#2d6a6a] border-b border-gray-700">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <button
            onClick={() => navigate('/contacts')}
            className="flex items-center gap-2 text-gray-300 hover:text-white mb-4"
          >
            <ArrowLeft size={20} />
            <span>Back to Contacts</span>
          </button>

          <div className="flex justify-between items-start">
            <div className="flex gap-4">
              <div className="w-20 h-20 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-3xl font-bold shadow-xl">
                {displayName.charAt(0).toUpperCase()}
              </div>
              
              <div>
                <h1 className="text-3xl font-bold mb-2">{displayName}</h1>
                
                {contact.title && (
                  <div className="flex items-center gap-2 text-gray-200 mb-1">
                    <Briefcase size={16} />
                    <span>{contact.title}</span>
                  </div>
                )}
                {contact.company && (
                  <div className="flex items-center gap-2 text-gray-300">
                    <Building2 size={16} />
                    <span>{contact.company}</span>
                  </div>
                )}

                <div className="flex gap-4 mt-3 text-sm">
                  {contact.email && (
                    <div className="flex items-center gap-1 text-gray-300">
                      <Mail size={14} />
                      <span>{contact.email}</span>
                    </div>
                  )}
                  {contact.phone && (
                    <div className="flex items-center gap-1 text-gray-300">
                      <Phone size={14} />
                      <span>{contact.phone}</span>
                    </div>
                  )}
                  {contact.linkedin_url && (
                    <a href={contact.linkedin_url} target="_blank" rel="noopener" className="flex items-center gap-1 text-blue-400 hover:text-blue-300">
                      <Linkedin size={14} />
                      <span>LinkedIn</span>
                    </a>
                  )}
                </div>
              </div>
            </div>

            <button
              onClick={handleEnrich}
              disabled={enriching}
              className={`px-6 py-3 rounded-lg font-semibold flex items-center gap-2 shadow-lg ${
                enriching
                  ? 'bg-gray-700 cursor-not-allowed'
                  : 'bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700'
              }`}
            >
              {enriching ? <Loader2 className="animate-spin" size={20} /> : <Zap size={20} />}
              {enriching ? 'Enriching...' : isEnriched ? 'Re-enrich' : 'Enrich Profile'}
            </button>
          </div>
        </div>
      </div>

      {/* MAIN CONTENT */}
      <div className="max-w-7xl mx-auto px-6 py-8">
        {!isEnriched ? (
          <div className="bg-[#1c2536] border border-gray-700 rounded-xl p-12 text-center">
            <Brain className="w-16 h-16 mx-auto mb-4 text-gray-500" />
            <p className="text-gray-400 text-lg mb-2">
              Click "Enrich Profile" to generate professional intelligence
            </p>
            <p className="text-gray-600 text-sm">
              Contact data loaded: {contact.email || 'No email'} • {contact.company || 'No company'}
            </p>
          </div>
        ) : (
          <div className="bg-[#1c2536] border border-gray-700 rounded-xl p-6">
            <h2 className="text-xl font-bold mb-4">Enrichment Data Available</h2>
            <p className="text-gray-300">Full collapsible sections will render here once enrichment completes.</p>
          </div>
        )}
      </div>
    </div>
  );
}
