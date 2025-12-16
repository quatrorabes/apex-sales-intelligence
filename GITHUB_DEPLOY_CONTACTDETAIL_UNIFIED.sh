#!/bin/bash
# GITHUB_DEPLOY_CONTACTDETAIL_UNIFIED.sh
# Apex Sales Intelligence | Production-ready ContactDetail with reference design
# Dec 15, 2025 | Theme + Tabs + Parsing + Enrich wired

set -e

echo "========================================"
echo "APEX ContactDetail Unified Deployment"
echo "========================================"

cd ~/projects/apex/apex-sales-intelligence

echo "📋 Git status check..."
git status

echo ""
echo "⚠️  Only ContactDetail.tsx will be modified. Continue? (Enter/Ctrl+C)"
read

echo "💾 Backup existing..."
cp dashboard_v1/src/pages/ContactDetail.tsx dashboard_v1/src/pages/ContactDetail.tsx.backup-$(date +%s)

echo "✍️  Writing unified ContactDetail.tsx..."
cat > dashboard_v1/src/pages/ContactDetail.tsx << 'EOFCONTACT'
// dashboard_v1/src/pages/ContactDetail.tsx
// VERSION: Apex-v1.0-Unified | Dec 15, 2025
// Theme-matched tabbed layout + enrichment parser + current API endpoints

import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeft, Briefcase, Building2, Mail, Phone, Linkedin,
  TrendingUp, GraduationCap, User, MessageSquare, Brain,
  FileText, Layers, Target, Zap, Loader2, Shield, Lightbulb
} from 'lucide-react';

const API_BASE = import.meta.env.VITE_API_URL || import.meta.env.VITE_APEX_API_URL || 'https://apex-backend-i7b0.onrender.com';

// ============================================================================
// TYPES
// ============================================================================

interface Contact {
  id: number;
  name?: string;
  first_name?: string;
  lastname?: string;
  email?: string;
  phone?: string;
  company?: string;
  title?: string;
  enrichment_status?: string;
  enrichment_data?: string | any;
  profile_content?: string;
  apex_score?: number;
  match_tier?: string;
  linkedin_url?: string;
  last_enriched?: string;
}

interface ParsedSections {
  professional?: any;
  company?: any;
  personality?: any;
  sales?: any;
  raw?: string;
}

// ============================================================================
// PARSING ENGINE
// ============================================================================

function parseEnrichmentData(contact: Contact): ParsedSections {
  const enrichmentData = contact.enrichment_data;
  const profileContent = contact.profile_content;

  // Priority 1: enrichment_data as object
  if (enrichmentData && typeof enrichmentData === 'object') {
    return {
      professional: enrichmentData.professional || enrichmentData.person_research || extractProfessional(enrichmentData),
      company: enrichmentData.company || enrichmentData.company_research || extractCompany(enrichmentData),
      personality: enrichmentData.personality || enrichmentData.personality_analysis || extractPersonality(enrichmentData),
      sales: enrichmentData.sales || enrichmentData.sales_intelligence || null,
      raw: JSON.stringify(enrichmentData, null, 2)
    };
  }

  // Priority 2: enrichment_data as JSON string
  if (enrichmentData && typeof enrichmentData === 'string') {
    try {
      const parsed = JSON.parse(enrichmentData);
      return {
        professional: parsed.professional || parsed.person_research || extractProfessional(parsed),
        company: parsed.company || parsed.company_research || extractCompany(parsed),
        personality: parsed.personality || parsed.personality_analysis || extractPersonality(parsed),
        sales: parsed.sales || parsed.sales_intelligence || null,
        raw: enrichmentData
      };
    } catch {
      // Fallback: treat as raw text
      return parseRawText(enrichmentData);
    }
  }

  // Priority 3: profile_content (legacy)
  if (profileContent) {
    return parseRawText(profileContent);
  }

  return {};
}

// Extract professional data from flat structure
function extractProfessional(data: any): any {
  return {
    current_role: data.current_role || data.title,
    experience_years: data.experience_years,
    key_skills: data.key_skills || data.skills || [],
    achievements: data.achievements || [],
    summary: data.summary || data.executive_summary
  };
}

// Extract company data from flat structure
function extractCompany(data: any): any {
  return {
    name: data.company_name || data.company,
    industry: data.industry,
    size: data.company_size,
    revenue: data.revenue,
    description: data.company_description
  };
}

// Extract personality data from flat structure
function extractPersonality(data: any): any {
  return {
    communication_style: data.communication_style,
    interests: data.interests || [],
    education: data.education,
    fun_facts: data.fun_facts || []
  };
}

// Parse raw text (markdown or plain text)
function parseRawText(text: string): ParsedSections {
  const sections: ParsedSections = { raw: text };
  
  // Try to extract markdown sections
  const professionalMatch = text.match(/###?\s*(?:Professional|Person|Executive)[\s\S]*?(?=###?\s|$)/i);
  const companyMatch = text.match(/###?\s*(?:Company|Organization)[\s\S]*?(?=###?\s|$)/i);
  const personalityMatch = text.match(/###?\s*(?:Personality|Personal|Interests)[\s\S]*?(?=###?\s|$)/i);
  
  if (professionalMatch) sections.professional = { summary: professionalMatch[0] };
  if (companyMatch) sections.company = { description: companyMatch[0] };
  if (personalityMatch) sections.personality = { summary: personalityMatch[0] };
  
  return sections;
}

// ============================================================================
// COMPONENT
// ============================================================================

export default function ContactDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [contact, setContact] = useState<Contact | null>(null);
  const [sections, setSections] = useState<ParsedSections>({});
  const [loading, setLoading] = useState(true);
  const [enriching, setEnriching] = useState(false);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState<'profile' | 'intelligence' | 'outreach'>('profile');

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
      setSections(parseEnrichmentData(data));
      setError('');
    } catch (err: any) {
      setError(err.message || 'Failed to load contact');
    } finally {
      setLoading(false);
    }
  }

  async function handleEnrich() {
    if (!id) return;
    try {
      setEnriching(true);
      const res = await fetch(`${API_BASE}/api/contacts/${id}/enrich`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      if (!res.ok) throw new Error(`Enrichment failed: ${res.status}`);
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
        <Loader2 className="w-12 h-12 text-white animate-spin" />
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
            <ArrowLeft className="inline mr-2" size={16} /> Back to Contacts
          </button>
        </div>
      </div>
    );
  }

  const displayName = contact.name || `${contact.first_name || ''} ${contact.lastname || ''}`.trim() || 'Unknown';
  const enriched = contact.enrichment_status === 'completed';

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-900 via-purple-900 to-pink-900 text-white">
      {/* Header */}
      <div className="bg-white/5 backdrop-blur-sm border-b border-white/10">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <button
            onClick={() => navigate('/contacts')}
            className="flex items-center gap-2 text-white/70 hover:text-white transition mb-4"
          >
            <ArrowLeft size={20} />
            <span>Back to Contacts</span>
          </button>

          <div className="flex justify-between items-start">
            <div className="flex gap-4">
              <div className="w-20 h-20 rounded-full bg-gradient-to-br from-purple-400 to-pink-400 flex items-center justify-center text-3xl font-bold">
                {displayName.charAt(0).toUpperCase()}
              </div>
              
              <div>
                <h1 className="text-3xl font-bold mb-1">{displayName}</h1>
                {contact.title && (
                  <div className="flex items-center gap-2 text-purple-200 mb-1">
                    <Briefcase size={16} />
                    <span>{contact.title}</span>
                  </div>
                )}
                {contact.company && (
                  <div className="flex items-center gap-2 text-purple-300">
                    <Building2 size={16} />
                    <span>{contact.company}</span>
                  </div>
                )}
                
                <div className="flex gap-4 mt-3 text-sm">
                  {contact.email && (
                    <div className="flex items-center gap-1 text-purple-200">
                      <Mail size={14} />
                      <span>{contact.email}</span>
                    </div>
                  )}
                  {contact.phone && (
                    <div className="flex items-center gap-1 text-purple-200">
                      <Phone size={14} />
                      <span>{contact.phone}</span>
                    </div>
                  )}
                  {contact.linkedin_url && (
                    <a
                      href={contact.linkedin_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-1 text-blue-400 hover:text-blue-300"
                    >
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
              className={`px-6 py-3 rounded-lg font-semibold transition shadow-lg flex items-center gap-2 ${
                enriching
                  ? 'bg-gray-500 cursor-not-allowed'
                  : 'bg-gradient-to-r from-green-400 to-blue-500 hover:from-green-500 hover:to-blue-600'
              }`}
            >
              {enriching ? (
                <>
                  <Loader2 className="animate-spin" size={20} />
                  <span>Enriching...</span>
                </>
              ) : enriched ? (
                <>
                  <Zap size={20} />
                  <span>Re-Enrich</span>
                </>
              ) : (
                <>
                  <Zap size={20} />
                  <span>Enrich Profile</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="max-w-7xl mx-auto px-6 py-6">
        <div className="flex gap-2 mb-6">
          <button
            onClick={() => setActiveTab('profile')}
            className={`px-6 py-3 rounded-lg font-semibold transition flex items-center gap-2 ${
              activeTab === 'profile'
                ? 'bg-white/20 text-white'
                : 'bg-white/5 text-white/60 hover:bg-white/10'
            }`}
          >
            <User size={20} />
            <span>Profile</span>
          </button>
          <button
            onClick={() => setActiveTab('intelligence')}
            className={`px-6 py-3 rounded-lg font-semibold transition flex items-center gap-2 ${
              activeTab === 'intelligence'
                ? 'bg-white/20 text-white'
                : 'bg-white/5 text-white/60 hover:bg-white/10'
            }`}
          >
            <Brain size={20} />
            <span>Intelligence</span>
          </button>
          <button
            onClick={() => setActiveTab('outreach')}
            className={`px-6 py-3 rounded-lg font-semibold transition flex items-center gap-2 ${
              activeTab === 'outreach'
                ? 'bg-white/20 text-white'
                : 'bg-white/5 text-white/60 hover:bg-white/10'
            }`}
          >
            <MessageSquare size={20} />
            <span>Outreach</span>
          </button>
        </div>

        {/* Tab Content */}
        <div className="space-y-6">
          {/* PROFILE TAB */}
          {activeTab === 'profile' && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Professional Intel */}
              <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6">
                <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
                  <Briefcase className="text-purple-400" />
                  Professional Intel
                </h2>
                {sections.professional ? (
                  <div className="space-y-3 text-sm">
                    {sections.professional.current_role && (
                      <div>
                        <span className="text-purple-300 font-semibold">Role:</span>{' '}
                        <span className="text-white">{sections.professional.current_role}</span>
                      </div>
                    )}
                    {sections.professional.experience_years && (
                      <div>
                        <span className="text-purple-300 font-semibold">Experience:</span>{' '}
                        <span className="text-white">{sections.professional.experience_years} years</span>
                      </div>
                    )}
                    {sections.professional.key_skills && sections.professional.key_skills.length > 0 && (
                      <div>
                        <div className="text-purple-300 font-semibold mb-2">Skills:</div>
                        <div className="flex flex-wrap gap-2">
                          {sections.professional.key_skills.map((skill: string, i: number) => (
                            <span key={i} className="px-3 py-1 bg-purple-500/30 rounded-full text-xs">
                              {skill}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                    {sections.professional.summary && (
                      <div className="mt-3 p-3 bg-black/20 rounded-lg text-gray-200 text-sm">
                        {sections.professional.summary}
                      </div>
                    )}
                  </div>
                ) : (
                  <p className="text-gray-400 italic">Click "Enrich" to generate professional intelligence</p>
                )}
              </div>

              {/* Company Research */}
              <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6">
                <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
                  <Building2 className="text-blue-400" />
                  Company Research
                </h2>
                {sections.company ? (
                  <div className="space-y-3 text-sm">
                    {sections.company.name && (
                      <div>
                        <span className="text-blue-300 font-semibold">Name:</span>{' '}
                        <span className="text-white">{sections.company.name}</span>
                      </div>
                    )}
                    {sections.company.industry && (
                      <div>
                        <span className="text-blue-300 font-semibold">Industry:</span>{' '}
                        <span className="text-white">{sections.company.industry}</span>
                      </div>
                    )}
                    {sections.company.size && (
                      <div>
                        <span className="text-blue-300 font-semibold">Size:</span>{' '}
                        <span className="text-white">{sections.company.size}</span>
                      </div>
                    )}
                    {sections.company.description && (
                      <div className="mt-3 p-3 bg-black/20 rounded-lg text-gray-200 text-sm">
                        {sections.company.description}
                      </div>
                    )}
                  </div>
                ) : (
                  <p className="text-gray-400 italic">Click "Enrich" to research company</p>
                )}
              </div>

              {/* Personality & Interests */}
              <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6">
                <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
                  <GraduationCap className="text-pink-400" />
                  Personality & Interests
                </h2>
                {sections.personality ? (
                  <div className="space-y-3 text-sm">
                    {sections.personality.communication_style && (
                      <div>
                        <span className="text-pink-300 font-semibold">Style:</span>{' '}
                        <span className="text-white">{sections.personality.communication_style}</span>
                      </div>
                    )}
                    {sections.personality.education && (
                      <div>
                        <span className="text-pink-300 font-semibold">Education:</span>{' '}
                        <span className="text-white">{sections.personality.education}</span>
                      </div>
                    )}
                    {sections.personality.interests && sections.personality.interests.length > 0 && (
                      <div>
                        <div className="text-pink-300 font-semibold mb-2">Interests:</div>
                        <div className="flex flex-wrap gap-2">
                          {sections.personality.interests.map((interest: string, i: number) => (
                            <span key={i} className="px-3 py-1 bg-pink-500/30 rounded-full text-xs">
                              {interest}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                    {sections.personality.fun_facts && sections.personality.fun_facts.length > 0 && (
                      <div className="mt-3">
                        <div className="text-pink-300 font-semibold mb-2">Fun Facts:</div>
                        <ul className="list-disc list-inside space-y-1 text-gray-200">
                          {sections.personality.fun_facts.map((fact: string, i: number) => (
                            <li key={i}>{fact}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                ) : (
                  <p className="text-gray-400 italic">Click "Enrich" to discover personality insights</p>
                )}
              </div>

              {/* Scoring */}
              <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6">
                <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
                  <TrendingUp className="text-green-400" />
                  APEX Scoring
                </h2>
                <div className="space-y-4">
                  <div>
                    <div className="flex justify-between mb-2">
                      <span className="text-sm font-semibold">APEX Score</span>
                      <span className="text-lg font-bold text-green-400">
                        {contact.apex_score || 0}/100
                      </span>
                    </div>
                    <div className="w-full bg-black/30 rounded-full h-3">
                      <div
                        className="bg-gradient-to-r from-green-400 to-blue-500 h-3 rounded-full transition-all"
                        style={{ width: `${contact.apex_score || 0}%` }}
                      />
                    </div>
                  </div>
                  {contact.match_tier && (
                    <div className="p-3 bg-black/20 rounded-lg">
                      <span className="text-sm text-gray-300">Match Tier:</span>{' '}
                      <span className="font-bold text-white">{contact.match_tier}</span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* INTELLIGENCE TAB */}
          {activeTab === 'intelligence' && (
            <div className="bg-white/10 backdrop-blur-lg rounded-xl p-8">
              <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
                <Brain className="text-purple-400" />
                Sales Intelligence
              </h2>
              {sections.sales ? (
                <div className="space-y-4">
                  {/* Sales intelligence content if available */}
                  <pre className="p-4 bg-black/30 rounded-lg text-sm overflow-auto">
                    {JSON.stringify(sections.sales, null, 2)}
                  </pre>
                </div>
              ) : (
                <div className="text-center py-12">
                  <Target className="w-16 h-16 mx-auto mb-4 text-purple-400/50" />
                  <p className="text-gray-400 text-lg">
                    Coming soon: Pain points, buying triggers, and engagement strategy
                  </p>
                </div>
              )}
            </div>
          )}

          {/* OUTREACH TAB */}
          {activeTab === 'outreach' && (
            <div className="bg-white/10 backdrop-blur-lg rounded-xl p-8">
              <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
                <MessageSquare className="text-blue-400" />
                Outreach Tools
              </h2>
              <div className="text-center py-12">
                <Lightbulb className="w-16 h-16 mx-auto mb-4 text-blue-400/50" />
                <p className="text-gray-400 text-lg">
                  Coming soon: Email drafts, LinkedIn messages, and call scripts
                </p>
              </div>
            </div>
          )}

          {/* Raw Data Debug */}
          {sections.raw && (
            <details className="bg-white/5 backdrop-blur-lg rounded-xl p-6">
              <summary className="text-xl font-bold cursor-pointer hover:text-purple-300 transition flex items-center gap-2">
                <FileText size={20} />
                <span>Raw Enrichment Data (Debug)</span>
              </summary>
              <pre className="mt-4 p-4 bg-black/30 rounded-lg text-xs overflow-auto max-h-96 text-gray-300">
                {sections.raw}
              </pre>
            </details>
          )}
        </div>
      </div>
    </div>
  );
}
EOFCONTACT

echo "✅ ContactDetail.tsx written"
echo ""
echo "📤 Committing to GitHub..."

git add dashboard_v1/src/pages/ContactDetail.tsx
git commit -m "feat(dashboard): ContactDetail unified design with tabs + enrichment parser

- Tabbed interface: Profile / Intelligence / Outreach
- Smart enrichment parser (handles object, JSON string, raw text)
- Theme-matched gradient design (indigo→purple→pink)
- Wired to current endpoints: GET /api/contacts/:id, POST /api/contacts/:id/enrich
- Lucide icons throughout
- Legacy parsing support for profile_content fallback

Ref: ContactDetailPage-copy-2.tsx design
Dec 15, 2025 | Apex Sales Intelligence | Dashboard_v1"

git push origin main

echo ""
echo "✅ DEPLOYED TO GITHUB"
echo "🚀 Vercel auto-deploy triggered"
echo ""
echo "Monitor: https://vercel.com/your-project"
echo "Live in ~2-3 minutes"
echo "========================================"
