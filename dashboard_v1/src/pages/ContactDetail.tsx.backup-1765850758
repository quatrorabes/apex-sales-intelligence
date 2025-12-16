// dashboard_v1/src/pages/ContactDetail.tsx
// VERSION: Apex-v1.0 | Dec 15, 2025 | Theme-unified + Enrich wired + Parser integrated
// Matches LandingPage.tsx gradient aesthetic, wires POST /api/contacts/:id/enrich, parses enrichment JSON

import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';

const API_BASE = import.meta.env.VITE_API_URL || import.meta.env.VITE_APEX_API_URL || 'https://apex-backend-i7b0.onrender.com';

interface Contact {
  id: number;
  name?: string;
  firstname?: string;
  lastname?: string;
  email?: string;
  phone?: string;
  company?: string;
  title?: string;
  enrichment_status?: string;
  enrichment_data?: string | Record<string, any>;
  apex_score?: number;
  match_tier?: string;
  linkedin_url?: string;
}

interface EnrichmentData {
  professional?: {
    current_role?: string;
    experience_years?: number;
    key_skills?: string[];
    achievements?: string[];
  };
  company?: {
    name?: string;
    industry?: string;
    size?: string;
    revenue?: string;
  };
  personality?: {
    communication_style?: string;
    interests?: string[];
    education?: string;
  };
  fun_facts?: string[];
  raw?: string;
}

export default function ContactDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [contact, setContact] = useState<Contact | null>(null);
  const [enrichmentData, setEnrichmentData] = useState<EnrichmentData>({});
  const [loading, setLoading] = useState(true);
  const [enriching, setEnriching] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!id) return;
    fetchContact();
  }, [id]);

  async function fetchContact() {
    try {
      setLoading(true);
      const res = await fetch(`${API_BASE}/api/contacts/${id}`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setContact(data);
      parseEnrichment(data.enrichment_data);
      setError('');
    } catch (err: any) {
      setError(err.message || 'Failed to load contact');
    } finally {
      setLoading(false);
    }
  }

  function parseEnrichment(raw: string | Record<string, any> | undefined) {
    if (!raw) {
      setEnrichmentData({});
      return;
    }

    let parsed: any = {};
    if (typeof raw === 'string') {
      try {
        parsed = JSON.parse(raw);
      } catch {
        setEnrichmentData({ raw });
        return;
      }
    } else {
      parsed = raw;
    }

    setEnrichmentData({
      professional: parsed.professional || {
        current_role: parsed.current_role || parsed.title,
        experience_years: parsed.experience_years,
        key_skills: parsed.key_skills || parsed.skills || [],
        achievements: parsed.achievements || [],
      },
      company: parsed.company || {
        name: parsed.company_name || parsed.company,
        industry: parsed.industry,
        size: parsed.company_size,
        revenue: parsed.revenue,
      },
      personality: parsed.personality || {
        communication_style: parsed.communication_style,
        interests: parsed.interests || [],
        education: parsed.education,
      },
      fun_facts: parsed.fun_facts || [],
      raw: typeof raw === 'string' ? raw : JSON.stringify(parsed, null, 2),
    });
  }

  async function handleEnrich() {
    if (!id) return;
    try {
      setEnriching(true);
      const res = await fetch(`${API_BASE}/api/contacts/${id}/enrich`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      });
      if (!res.ok) throw new Error(`Enrichment failed: HTTP ${res.status}`);
      await fetchContact();
    } catch (err: any) {
      alert(err.message || 'Enrichment error');
    } finally {
      setEnriching(false);
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-indigo-900 via-purple-900 to-pink-900 flex items-center justify-center">
        <div className="text-white text-xl animate-pulse">Loading contact...</div>
      </div>
    );
  }

  if (error || !contact) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-indigo-900 via-purple-900 to-pink-900 flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-400 text-xl mb-4">{error || 'Contact not found'}</div>
          <button
            onClick={() => navigate('/contacts')}
            className="px-6 py-2 bg-white/10 hover:bg-white/20 text-white rounded-lg transition"
          >
            ← Back to Contacts
          </button>
        </div>
      </div>
    );
  }

  const displayName = contact.name || `${contact.firstname || ''} ${contact.lastname || ''}`.trim() || 'Unknown';
  const enriched = contact.enrichment_status === 'completed';

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-900 via-purple-900 to-pink-900 text-white p-8">
      <div className="max-w-7xl mx-auto mb-8">
        <button
          onClick={() => navigate('/contacts')}
          className="mb-4 px-4 py-2 bg-white/10 hover:bg-white/20 rounded-lg transition flex items-center gap-2"
        >
          <span>←</span> Back
        </button>
        
        <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 shadow-2xl">
          <div className="flex justify-between items-start">
            <div>
              <h1 className="text-4xl font-bold mb-2">{displayName}</h1>
              {contact.title && <p className="text-xl text-purple-200">{contact.title}</p>}
              {contact.company && <p className="text-lg text-purple-300">{contact.company}</p>}
              <div className="flex gap-4 mt-4 text-sm">
                {contact.email && <span>📧 {contact.email}</span>}
                {contact.phone && <span>📞 {contact.phone}</span>}
              </div>
            </div>
            
            <button
              onClick={handleEnrich}
              disabled={enriching}
              className={`px-6 py-3 rounded-lg font-semibold transition shadow-lg ${
                enriching
                  ? 'bg-gray-500 cursor-not-allowed'
                  : 'bg-gradient-to-r from-green-400 to-blue-500 hover:from-green-500 hover:to-blue-600'
              }`}
            >
              {enriching ? '⏳ Enriching...' : enriched ? '🔄 Re-Enrich' : '✨ Enrich'}
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6">
          <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">💼 Professional Intel</h2>
          {enrichmentData.professional && Object.keys(enrichmentData.professional).length > 0 ? (
            <div className="space-y-3">
              {enrichmentData.professional.current_role && (
                <div><span className="font-semibold">Role:</span> {enrichmentData.professional.current_role}</div>
              )}
              {enrichmentData.professional.experience_years && (
                <div><span className="font-semibold">Experience:</span> {enrichmentData.professional.experience_years} years</div>
              )}
              {enrichmentData.professional.key_skills && enrichmentData.professional.key_skills.length > 0 && (
                <div>
                  <span className="font-semibold">Skills:</span>
                  <div className="flex flex-wrap gap-2 mt-2">
                    {enrichmentData.professional.key_skills.map((skill, i) => (
                      <span key={i} className="px-3 py-1 bg-purple-500/30 rounded-full text-sm">{skill}</span>
                    ))}
                  </div>
                </div>
              )}
              {enrichmentData.professional.achievements && enrichmentData.professional.achievements.length > 0 && (
                <div>
                  <span className="font-semibold">Achievements:</span>
                  <ul className="list-disc list-inside mt-2 space-y-1">
                    {enrichmentData.professional.achievements.map((ach, i) => <li key={i}>{ach}</li>)}
                  </ul>
                </div>
              )}
            </div>
          ) : (
            <p className="text-gray-300 italic">No professional intel yet. Hit Re-Enrich for APEX insights.</p>
          )}
        </div>

        <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6">
          <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">🏢 Company Data</h2>
          {enrichmentData.company && Object.keys(enrichmentData.company).length > 0 ? (
            <div className="space-y-3">
              {enrichmentData.company.name && <div><span className="font-semibold">Name:</span> {enrichmentData.company.name}</div>}
              {enrichmentData.company.industry && <div><span className="font-semibold">Industry:</span> {enrichmentData.company.industry}</div>}
              {enrichmentData.company.size && <div><span className="font-semibold">Size:</span> {enrichmentData.company.size}</div>}
              {enrichmentData.company.revenue && <div><span className="font-semibold">Revenue:</span> {enrichmentData.company.revenue}</div>}
            </div>
          ) : (
            <p className="text-gray-300 italic">No company data. Re-Enrich to populate.</p>
          )}
        </div>

        <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6">
          <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">🎭 Personality & Interests</h2>
          {enrichmentData.personality && Object.keys(enrichmentData.personality).length > 0 ? (
            <div className="space-y-3">
              {enrichmentData.personality.communication_style && (
                <div><span className="font-semibold">Style:</span> {enrichmentData.personality.communication_style}</div>
              )}
              {enrichmentData.personality.interests && enrichmentData.personality.interests.length > 0 && (
                <div>
                  <span className="font-semibold">Interests:</span>
                  <div className="flex flex-wrap gap-2 mt-2">
                    {enrichmentData.personality.interests.map((int, i) => (
                      <span key={i} className="px-3 py-1 bg-pink-500/30 rounded-full text-sm">{int}</span>
                    ))}
                  </div>
                </div>
              )}
              {enrichmentData.personality.education && (
                <div><span className="font-semibold">Education:</span> {enrichmentData.personality.education}</div>
              )}
            </div>
          ) : (
            <p className="text-gray-300 italic">No personality insights. Re-Enrich for icebreakers + education.</p>
          )}
        </div>

        <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6">
          <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">🎉 Fun Facts</h2>
          {enrichmentData.fun_facts && enrichmentData.fun_facts.length > 0 ? (
            <ul className="list-disc list-inside space-y-2">
              {enrichmentData.fun_facts.map((fact, i) => <li key={i}>{fact}</li>)}
            </ul>
          ) : (
            <p className="text-gray-300 italic">No fun facts. Re-Enrich to uncover.</p>
          )}
        </div>
      </div>

      {enrichmentData.raw && (
        <div className="max-w-7xl mx-auto mt-6">
          <details className="bg-white/10 backdrop-blur-lg rounded-xl p-6">
            <summary className="text-xl font-bold cursor-pointer hover:text-purple-300 transition">
              🔍 Raw Enrichment Data (Debug)
            </summary>
            <pre className="mt-4 p-4 bg-black/30 rounded-lg text-xs overflow-auto max-h-96">
              {enrichmentData.raw}
            </pre>
          </details>
        </div>
      )}
    </div>
  );
}
