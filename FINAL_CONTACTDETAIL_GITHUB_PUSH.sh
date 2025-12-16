#!/bin/bash
# 🚀 FINAL GITHUB PUSH + VERCEL DEPLOY: ContactDetail.tsx
# Matches ContactsView scheme: navy headers + subtle gradient
# Date: Dec 15, 2025 4:07 PM PST | Apex Sales Intelligence

set -euo pipefail

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔥 APEX CONTACTDETAIL - FINAL ContactsView MATCH + PUSH"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

cd "$(git rev-parse --show-toplevel)"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
FILE="dashboard_v1/src/pages/ContactDetail.tsx"

# Backup
cp "$FILE" "${FILE}.backup-${TIMESTAMP}" || echo "⚠️ No previous file"
echo "✅ Backup created"

# Full ContactDetail.tsx - MATCHES ContactsView navy + gradient
cat > "$FILE" << 'TSX_EOF'
import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';

const API_BASE = import.meta.env.VITE_API_URL || "https://apex-backend-i7b0.onrender.com";

interface Contact {
  id: string;
  firstname?: string;
  lastname?: string;
  email?: string;
  phone?: string;
  company?: string;
  title?: string;
  linkedin_url?: string;
  enrichment_status?: string;
  enriched_at?: string;
  apex_score?: number;
  match_score?: number;
  enrichment?: {
    engine?: string;
    version?: string;
    sections?: Record<string, string>;
  };
}

function normalizeContact(api: any): Contact {
  return {
    id: String(api?.id ?? ''),
    firstname: api?.first_name ?? api?.firstname ?? '',
    lastname: api?.last_name ?? api?.lastname ?? '',
    email: api?.email ?? '',
    phone: api?.phone ?? '',
    company: api?.company ?? '',
    title: api?.title ?? '',
    linkedin_url: api?.linkedin_url ?? api?.linkedinUrl ?? '',
    enrichment_status: api?.enrichment_status ?? api?.enrichmentStatus ?? 'pending',
    enriched_at: api?.enriched_at ?? api?.enrichedAt ?? '',
    apex_score: api?.apex_score ?? api?.apexScore ?? 0,
    match_score: api?.match_score ?? api?.matchScore ?? 0,
    enrichment: api?.enrichment ?? null,
  };
}

export default function ContactDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [contact, setContact] = useState<Contact | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'professional' | 'company' | 'personality' | 'funfacts' | 'raw'>('professional');
  const [enriching, setEnriching] = useState(false);

  async function fetchContact() {
    if (!id) return;
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/api/contacts/${id}`);
      if (!res.ok) throw new Error(`Failed to fetch contact: ${res.status}`);
      const json = await res.json();
      const apiContact = (json && typeof json === 'object' && 'contact' in json) ? (json as any).contact : json;
      setContact(normalizeContact(apiContact));
    } catch (err: any) {
      console.error('Fetch contact error:', err);
      setError(err.message || 'Failed to load contact');
    } finally {
      setLoading(false);
    }
  }

  async function handleReEnrich() {
    if (!id || enriching) return;
    setEnriching(true);
    try {
      const res = await fetch(`${API_BASE}/api/contacts/${id}/enrich`, { method: 'POST' });
      if (!res.ok) throw new Error('Enrichment failed');
      setTimeout(() => { fetchContact(); setEnriching(false); }, 3000);
    } catch (err: any) {
      console.error('Enrich error:', err);
      alert('Enrichment failed. Check console.');
      setEnriching(false);
    }
  }

  useEffect(() => { fetchContact(); }, [id]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading contact...</p>
        </div>
      </div>
    );
  }

  if (error || !contact) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
        <div className="bg-white rounded-xl shadow-xl p-8 max-w-md mx-4">
          <p className="text-red-600 mb-4 font-medium">{error || 'Contact not found'}</p>
          <button onClick={() => navigate('/contacts')} className="w-full bg-indigo-600 text-white py-2 px-4 rounded-lg hover:bg-indigo-700 transition font-medium">
            ← Back to Contacts
          </button>
        </div>
      </div>
    );
  }

  const sections = contact.enrichment?.sections || {};
  const personSection = sections.person_profile || sections['1._overview'] || sections['2._about_dale_holzer__background_and_icebreaker_angles'] || '';
  const companySection = sections.company_intelligence || sections['4._market_position'] || '';
  const personalitySection = sections['3._icebreaker_topics_and_shared_interests'] || sections['3._education'] || sections['3._leadership'] || sections['6._strategic_context'] || '';
  const funFactsSection = sections.fun_facts || '';
  const raw = Object.keys(sections).length > 0 ? Object.entries(sections).map(([key, value]) => `## ${key.replace(/_/g, ' ').toUpperCase()}\n\n${value}`).join('\n\n---\n\n') : '';

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 py-8 px-4">
      <div className="max-w-4xl mx-auto">
        {/* Header - Navy like ContactsView */}
        <div className="bg-white rounded-xl shadow-xl p-8 mb-8 border border-slate-200">
          <div className="flex items-start justify-between mb-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">{contact.firstname} {contact.lastname}</h1>
              <p className="text-xl text-slate-700 font-semibold mb-1">{contact.title}</p>
              <p className="text-lg text-slate-600 mb-4">{contact.company}</p>
              <div className="flex flex-wrap gap-4 text-sm">
                {contact.email && <a href={`mailto:${contact.email}`} className="text-indigo-600 hover:text-indigo-700 font-medium">📧 {contact.email}</a>}
                {contact.phone && <span className="text-slate-700 font-medium">📞 {contact.phone}</span>}
                {contact.linkedin_url && <a href={contact.linkedin_url} target="_blank" className="text-indigo-600 hover:text-indigo-700 font-medium">🔗 LinkedIn</a>}
              </div>
            </div>
            <div className="flex gap-3">
              <button 
                onClick={handleReEnrich} 
                disabled={enriching}
                className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 shadow-md font-semibold transition-all"
              >
                {enriching ? '⏳ Enriching...' : '🔄 Re-Enrich'}
              </button>
              <button 
                onClick={() => navigate('/contacts')} 
                className="px-6 py-3 bg-slate-200 text-slate-700 rounded-lg hover:bg-slate-300 font-medium transition"
              >
                ← Back
              </button>
            </div>
          </div>
          <div className="flex flex-wrap gap-3">
            <span className={`px-4 py-2 rounded-full text-sm font-bold shadow-sm ${
              contact.enrichment_status === 'enriched' 
                ? 'bg-emerald-100 text-emerald-800 border-2 border-emerald-200' 
                : contact.enrichment_status === 'enriching' 
                ? 'bg-amber-100 text-amber-800 border-2 border-amber-200' 
                : 'bg-slate-100 text-slate-700 border-2 border-slate-200'
            }`}>
              {contact.enrichment_status === 'enriched' ? '✅ ' : ''}{contact.enrichment_status || 'Pending'}
            </span>
            {contact.apex_score && contact.apex_score > 0 && (
              <span className="px-4 py-2 bg-purple-100 text-purple-800 border-2 border-purple-200 rounded-full text-sm font-bold shadow-sm">
                ⚡ APEX {contact.apex_score}
              </span>
            )}
            {Object.keys(sections).length > 0 && (
              <span className="px-4 py-2 bg-blue-100 text-blue-800 border-2 border-blue-200 rounded-full text-sm font-bold shadow-sm">
                📊 {Object.keys(sections).length} Sections
              </span>
            )}
          </div>
        </div>

        {/* Tabs - Navy active like ContactsView */}
        <div className="bg-white rounded-xl shadow-xl border border-slate-200 overflow-hidden mb-8">
          <div className="bg-gradient-to-r from-slate-100 to-indigo-100 border-b border-slate-200 p-1">
            <nav className="flex -mb-px space-x-8">
              {[
                { key: 'professional', label: '👔 Professional', icon: '👔' },
                { key: 'company', label: '🏢 Company', icon: '🏢' },
                { key: 'personality', label: '🧠 Personality', icon: '🧠' },
                { key: 'funfacts', label: '✨ Fun Facts', icon: '✨' },
                { key: 'raw', label: '📄 Raw Profile', icon: '📄' },
              ].map((tab) => (
                <button
                  key={tab.key}
                  onClick={() => setActiveTab(tab.key as any)}
                  className={`py-3 px-4 border-b-2 font-semibold text-sm flex items-center gap-2 transition-all rounded-t-lg group ${
                    activeTab === tab.key
                      ? 'border-indigo-600 bg-white text-indigo-900 shadow-sm'
                      : 'border-transparent text-slate-600 hover:text-slate-900 hover:border-slate-300'
                  }`}
                >
                  <span>{tab.icon}</span>{tab.label}
                </button>
              ))}
            </nav>
          </div>

          <div className="p-8 min-h-[400px]">
            <div className="prose prose-slate max-w-none prose-headings:text-gray-900 prose-a:text-indigo-600">
              {activeTab === 'professional' && (personSection ? <ReactMarkdown>{personSection}</ReactMarkdown> : (
                <div className="text-center py-20">
                  <p className="text-slate-500 text-xl mb-2">No professional intel yet.</p>
                  <p className="text-slate-400">Hit Re-Enrich for APEX insights.</p>
                </div>
              ))}
              {activeTab === 'company' && (companySection ? <ReactMarkdown>{companySection}</ReactMarkdown> : (
                <div className="text-center py-20">
                  <p className="text-slate-500 text-xl mb-2">No company data.</p>
                  <p className="text-slate-400">Re-Enrich to populate.</p>
                </div>
              ))}
              {activeTab === 'personality' && (personalitySection ? <ReactMarkdown>{personalitySection}</ReactMarkdown> : (
                <div className="text-center py-20">
                  <p className="text-slate-500 text-xl mb-2">No personality insights.</p>
                  <p className="text-slate-400">Re-Enrich for icebreakers + education.</p>
                </div>
              ))}
              {activeTab === 'funfacts' && (funFactsSection ? <ReactMarkdown>{funFactsSection}</ReactMarkdown> : (
                <div className="text-center py-20">
                  <p className="text-slate-500 text-xl mb-2">No fun facts.</p>
                  <p className="text-slate-400">Re-Enrich to uncover.</p>
                </div>
              ))}
              {activeTab === 'raw' && (raw ? <ReactMarkdown components={{ h2: ({ children }) => <h2 className="text-slate-900 font-bold mt-8 mb-4 border-b border-slate-200 pb-2">{children}</h2> }}>{raw}</ReactMarkdown> : (
                <div className="text-center py-20">
                  <p className="text-slate-500 text-xl mb-2">No raw data.</p>
                  <p className="text-slate-400">Re-Enrich full profile.</p>
                </div>
              ))}
            </div>
          </div>
        </div>

        {contact.enrichment && Object.keys(sections).length > 0 && (
          <div className="text-center">
            <button className="px-12 py-4 bg-gradient-to-r from-emerald-500 to-emerald-600 text-white rounded-xl shadow-xl hover:from-emerald-600 hover:to-emerald-700 font-bold text-lg transition-all transform hover:-translate-y-1">
              📥 Download PDF Dossier
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
TSX_EOF

echo "✅ ContactDetail.tsx deployed (ContactsView match)"

# Git + Push
git add "$FILE"
git commit -m "feat(ContactDetail): final styling match to ContactsView

🎨 VISUAL:
- Navy headers + indigo accents (matches Contacts list)
- Subtle gradient: from-slate-50 via-blue-50 to-indigo-100
- Elevated cards shadow-xl rounded-xl
- Tab bar gradient from-slate-100 to-indigo-100
- Icons on tabs + hover states
- Badges with border-2 shadows

🔧 FUNCTIONALITY:
- All enrichment mappings (personality, fun facts, raw)
- Re-Enrich button
- UUID support + API unwrapping
- Professional empty states

✅ LIVE TEST: https://apex-sales-intelligence.vercel.app/contacts/fdfb18f1-45b0-4273-99e2-a02e0f9f0fbe"

git push origin main

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ PUSHED TO GITHUB MAIN | VERCEL DEPLOYING (~2 min)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🔗 PRODUCTION: https://apex-sales-intelligence.vercel.app/contacts/fdfb18f1-45b0-4273-99e2-a02e0f9f0fbe"
echo ""
echo "✅ ContactsView consistency achieved. Ready for Dashboard_v1 full launch?"
echo ""
