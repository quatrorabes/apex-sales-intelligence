// dashboard_v1/src/pages/ContactDetail.tsx
// VERSION: World-Class-v1.0 | Dec 15, 2025
// Design: Deal Intelligence collapsible sections + Contact List color scheme

import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeft, ChevronDown, ChevronUp, Zap, Loader2, Mail, Phone, Linkedin,
  Target, Clock, MessageSquare, Brain, Lightbulb, Send, Phone as PhoneIcon,
  CheckCircle2, TrendingUp, Briefcase, Building2, User
} from 'lucide-react';

const API_BASE = import.meta.env.VITE_API_URL || import.meta.env.VITE_APEX_API_URL || 'https://apex-backend-i7b0.onrender.com';

interface Contact {
  id: string;
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

interface Section {
  id: string;
  title: string;
  stage: string;
  color: string;
  icon: any;
  expanded: boolean;
}

function parseEnrichment(contact: Contact) {
  const data = contact.enrichment_data;
  if (!data) return null;
  
  if (typeof data === 'string') {
    try {
      return JSON.parse(data);
    } catch {
      return { raw: data };
    }
  }
  return data;
}

export default function ContactDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  
  const [contact, setContact] = useState<Contact | null>(null);
  const [enrichment, setEnrichment] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [enriching, setEnriching] = useState(false);
  const [sections, setSections] = useState<Section[]>([
    { id: 'qualification', title: 'TARGET QUALIFICATION', stage: 'STAGE 1', color: 'purple', icon: Target, expanded: true },
    { id: 'timing', title: 'ENGAGEMENT TIMING', stage: 'STAGE 2', color: 'blue', icon: Clock, expanded: false },
    { id: 'conversation', title: 'CONVERSATION STRATEGY', stage: 'STAGE 3', color: 'cyan', icon: MessageSquare, expanded: false },
    { id: 'insights', title: 'AI-DRIVEN INSIGHTS', stage: 'STAGE 4', color: 'purple', icon: Brain, expanded: false },
    { id: 'talking', title: 'TALKING POINTS', stage: 'STAGE 5', color: 'green', icon: Lightbulb, expanded: false },
    { id: 'outreach', title: 'OUTREACH EXECUTION', stage: 'STAGE 6', color: 'red', icon: Send, expanded: false },
    { id: 'next', title: 'NEXT STEPS', stage: 'STAGE 7', color: 'blue', icon: CheckCircle2, expanded: false },
  ]);

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
      setEnrichment(parseEnrichment(data));
    } catch (err) {
      console.error('Failed to load contact:', err);
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
      if (!res.ok) throw new Error(`Enrichment failed`);
      await fetchContact();
    } catch (err: any) {
      alert(err.message);
    } finally {
      setEnriching(false);
    }
  }

  function toggleSection(id: string) {
    setSections(sections.map(s => s.id === id ? { ...s, expanded: !s.expanded } : s));
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0a0e1a] flex items-center justify-center">
        <Loader2 className="w-12 h-12 text-blue-500 animate-spin" />
      </div>
    );
  }

  if (!contact) {
    return (
      <div className="min-h-screen bg-[#0a0e1a] flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-400 text-xl mb-4">Contact not found</p>
          <button
            onClick={() => navigate('/contacts')}
            className="px-6 py-2 bg-[#1c2536] hover:bg-[#253447] text-white rounded-lg"
          >
            Back to Contacts
          </button>
        </div>
      </div>
    );
  }

  const displayName = contact.name || `${contact.first_name || ''} ${contact.lastname || ''}`.trim();
  const isEnriched = contact.enrichment_status === 'completed';
  const scoreColor = (contact.apex_score || 0) >= 75 ? 'text-green-400' : (contact.apex_score || 0) >= 50 ? 'text-yellow-400' : 'text-orange-400';
  const tierBadge = contact.match_tier === 'HIGH' ? 'bg-green-600' : contact.match_tier === 'MEDIUM' ? 'bg-yellow-600' : 'bg-orange-600';

  const colorMap: Record<string, string> = {
    purple: 'bg-gradient-to-r from-purple-600 to-purple-500',
    blue: 'bg-gradient-to-r from-blue-600 to-blue-500',
    cyan: 'bg-gradient-to-r from-cyan-600 to-cyan-500',
    green: 'bg-gradient-to-r from-green-600 to-green-500',
    red: 'bg-gradient-to-r from-red-600 to-red-500',
  };

  return (
    <div className="min-h-screen bg-[#0a0e1a] text-white">
      {/* HEADER CARD (Teal gradient like Deal Intelligence) */}
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
                <div className="flex items-center gap-3 mb-2">
                  <h1 className="text-3xl font-bold">{displayName}</h1>
                  {contact.match_tier && (
                    <span className={`px-3 py-1 ${tierBadge} text-white text-xs font-bold rounded`}>
                      {contact.match_tier}
                    </span>
                  )}
                </div>
                
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

            <div className="flex items-center gap-4">
              {contact.apex_score !== undefined && (
                <div className="text-center">
                  <div className={`text-4xl font-bold ${scoreColor}`}>{contact.apex_score}</div>
                  <div className="text-xs text-gray-400">APEX Score</div>
                </div>
              )}
              
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
      </div>

      {/* COLLAPSIBLE SECTIONS (Deal Intelligence style) */}
      <div className="max-w-7xl mx-auto px-6 py-8">
        {!isEnriched && (
          <div className="bg-[#1c2536] border border-gray-700 rounded-xl p-12 text-center mb-8">
            <Brain className="w-16 h-16 mx-auto mb-4 text-gray-500" />
            <p className="text-gray-400 text-lg">
              Click "Enrich Profile" to generate professional intelligence
            </p>
          </div>
        )}

        {isEnriched && sections.map((section) => (
          <div key={section.id} className="mb-4">
            <button
              onClick={() => toggleSection(section.id)}
              className={`w-full ${colorMap[section.color]} text-white px-6 py-4 rounded-t-xl flex items-center justify-between hover:opacity-90 transition`}
            >
              <div className="flex items-center gap-3">
                <section.icon size={24} />
                <div className="text-left">
                  <div className="text-xs font-semibold opacity-80">{section.stage}</div>
                  <div className="text-lg font-bold">{section.title}</div>
                </div>
              </div>
              {section.expanded ? <ChevronUp size={24} /> : <ChevronDown size={24} />}
            </button>
            
            {section.expanded && (
              <div className="bg-[#1c2536] border-x border-b border-gray-700 rounded-b-xl p-6">
                {/* QUALIFICATION */}
                {section.id === 'qualification' && (
                  <div className="space-y-4">
                    <div className="flex items-start gap-3">
                      <Target className="text-purple-400 mt-1" size={20} />
                      <div>
                        <h3 className="font-bold text-white mb-2">Who to Target</h3>
                        <p className="text-gray-300 text-sm">
                          {enrichment?.professional?.summary || 'Professional profile analysis will appear here after enrichment.'}
                        </p>
                      </div>
                    </div>
                    {enrichment?.professional?.key_skills && (
                      <div className="flex flex-wrap gap-2">
                        {enrichment.professional.key_skills.map((skill: string, i: number) => (
                          <span key={i} className="px-3 py-1 bg-purple-600/20 border border-purple-500/30 rounded-full text-xs">
                            {skill}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                )}

                {/* TIMING */}
                {section.id === 'timing' && (
                  <div className="space-y-4">
                    <div className="flex items-start gap-3">
                      <Clock className="text-blue-400 mt-1" size={20} />
                      <div>
                        <h3 className="font-bold text-white mb-2">When to Contact</h3>
                        <p className="text-gray-300 text-sm">Optimal engagement timing based on recent activity and signals.</p>
                      </div>
                    </div>
                    <div className="bg-[#0a0e1a] rounded-lg p-4">
                      <p className="text-green-400 text-sm">✓ Within 24 Hours - High engagement window detected</p>
                    </div>
                  </div>
                )}

                {/* CONVERSATION */}
                {section.id === 'conversation' && (
                  <div className="space-y-4">
                    <div className="flex items-start gap-3">
                      <MessageSquare className="text-cyan-400 mt-1" size={20} />
                      <div className="flex-1">
                        <h3 className="font-bold text-white mb-2">WHAT to Say</h3>
                        <div className="space-y-3">
                          <div className="bg-[#0a0e1a] rounded-lg p-4">
                            <p className="font-semibold text-white mb-2">Opening Hook</p>
                            <p className="text-gray-300 text-sm">
                              {enrichment?.personality?.communication_style 
                                ? `Adapt communication style to match: ${enrichment.personality.communication_style}`
                                : 'Personalized opening based on research and mutual connections.'}
                            </p>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* INSIGHTS */}
                {section.id === 'insights' && (
                  <div className="space-y-4">
                    <div className="flex items-start gap-3">
                      <Brain className="text-purple-400 mt-1" size={20} />
                      <div>
                        <h3 className="font-bold text-white mb-2">AI Reasoning</h3>
                        <p className="text-gray-300 text-sm">
                          {enrichment?.company?.description || 'AI-powered insights and relationship strategy recommendations.'}
                        </p>
                      </div>
                    </div>
                  </div>
                )}

                {/* TALKING POINTS */}
                {section.id === 'talking' && (
                  <div className="space-y-4">
                    <div className="flex items-start gap-3">
                      <Lightbulb className="text-green-400 mt-1" size={20} />
                      <div>
                        <h3 className="font-bold text-white mb-2">Sales Opportunity Discussion Points</h3>
                        <ul className="list-disc list-inside space-y-2 text-gray-300 text-sm">
                          <li>Industry trends and market positioning</li>
                          <li>Pain points and solution alignment</li>
                          <li>Competitive advantages and differentiators</li>
                        </ul>
                      </div>
                    </div>
                  </div>
                )}

                {/* OUTREACH */}
                {section.id === 'outreach' && (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <div className="flex items-center gap-2 mb-3">
                        <Mail className="text-blue-400" size={20} />
                        <h3 className="font-bold text-white">Email Templates</h3>
                      </div>
                      <div className="space-y-2">
                        <div className="bg-[#0a0e1a] rounded-lg p-3 hover:bg-[#141926] cursor-pointer transition">
                          <p className="text-sm text-white">Variant 1: Direct Value Proposition</p>
                        </div>
                        <div className="bg-[#0a0e1a] rounded-lg p-3 hover:bg-[#141926] cursor-pointer transition">
                          <p className="text-sm text-white">Variant 2: Industry Insight Share</p>
                        </div>
                      </div>
                    </div>
                    <div>
                      <div className="flex items-center gap-2 mb-3">
                        <PhoneIcon className="text-green-400" size={20} />
                        <h3 className="font-bold text-white">Call Scripts</h3>
                      </div>
                      <div className="space-y-2">
                        <div className="bg-[#0a0e1a] rounded-lg p-3 hover:bg-[#141926] cursor-pointer transition">
                          <p className="text-sm text-white">Variant 1: Cold call opener</p>
                        </div>
                        <div className="bg-[#0a0e1a] rounded-lg p-3 hover:bg-[#141926] cursor-pointer transition">
                          <p className="text-sm text-white">Variant 2: Warm follow-up</p>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* NEXT STEPS */}
                {section.id === 'next' && (
                  <div className="space-y-4">
                    <div className="flex items-start gap-3">
                      <CheckCircle2 className="text-blue-400 mt-1" size={20} />
                      <div>
                        <h3 className="font-bold text-white mb-2">Recommended Actions</h3>
                        <div className="space-y-2">
                          <div className="flex items-center gap-2 text-gray-300 text-sm">
                            <div className="w-2 h-2 bg-blue-400 rounded-full"></div>
                            <span>Send personalized email within 24 hours</span>
                          </div>
                          <div className="flex items-center gap-2 text-gray-300 text-sm">
                            <div className="w-2 h-2 bg-blue-400 rounded-full"></div>
                            <span>Follow up with LinkedIn connection request</span>
                          </div>
                          <div className="flex items-center gap-2 text-gray-300 text-sm">
                            <div className="w-2 h-2 bg-blue-400 rounded-full"></div>
                            <span>Schedule call if no response after 3 days</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
