import React, { useState } from 'react';
import {
  Target,
  Calendar,
  MessageSquare,
  Brain,
  TrendingUp,
  Mail,
  Phone,
  Linkedin,
  Building2,
  X,
  ChevronDown,
  ChevronUp,
  Copy,
  CheckCircle2,
  Zap,
  Users,
  Clock,
  Lightbulb,
  Heart,
  Star,
  Award,
  ArrowRight
} from 'lucide-react';

interface EnrichmentData {
  full_profile?: string;
  overview?: string;
  background?: string;
  education?: string;
  recent_mentions?: string;
  myers_briggs?: string;
  mbti_type?: string;
  pain_points?: string;
  relationship_tips?: string;
  outreach_approach?: string;
  talking_points?: string;
  ai_score_reasoning?: string;
  trigger_events?: string;
  deals_database?: string;
  warm_intros?: string;
  kernel?: {
    who?: {
      persona_type?: string;
      decision_role?: string;
      influence_level?: string;
    };
    when?: {
      timing_signal?: string;
      urgency_level?: string;
      optimal_contact_time?: string;
      follow_up_cadence?: string;
    };
    what?: {
      opening_hook?: string;
      value_props?: string[];
      discovery_questions?: string[];
      objection_handlers?: any;
      call_to_action?: string;
    };
  };
  outreach?: {
    emails?: Array<{
      variant: number;
      subject: string;
      body: string;
    }>;
    call_scripts?: Array<{
      variant: number;
      opening: string;
      questions?: string[];
      close: string;
    }>;
  };
  scores?: {
    opportunity_score?: number;
    tier?: string;
    confidence?: string;
  };
  mbti_assessment?: string;
}

interface Contact {
  id: number;
  name: string;
  title?: string;
  company?: string;
  email?: string;
  phone?: string;
  linkedin_url?: string;
  profile_picture_url?: string;
  enrichment_status?: string;
  lead_tier?: string;
  opportunity_score?: number;
  enrichment_data?: string;
}

interface Props {
  contact: Contact;
  onClose: () => void;
}

export default function ContactEnrichmentView({ contact, onClose }: Props) {
  const [expandedStages, setExpandedStages] = useState<Set<number>>(new Set([1, 2, 3, 4, 5, 6]));
  const [copiedText, setCopiedText] = useState<string>('');

  // Parse enrichment data
  let enrichmentData: EnrichmentData = {};
  try {
    if (contact.enrichment_data) {
      enrichmentData = JSON.parse(contact.enrichment_data);
    }
  } catch (e) {
    console.error('Error parsing enrichment data:', e);
  }

  const kernel = enrichmentData.kernel || {};
  const who = kernel.who || {};
  const when = kernel.when || {};
  const what = kernel.what || {};
  const outreach = enrichmentData.outreach || {};
  const scores = enrichmentData.scores || {};

  const toggleStage = (stage: number) => {
    const newExpanded = new Set(expandedStages);
    if (newExpanded.has(stage)) {
      newExpanded.delete(stage);
    } else {
      newExpanded.add(stage);
    }
    setExpandedStages(newExpanded);
  };

  const copyToClipboard = (text: string, label: string) => {
    navigator.clipboard.writeText(text);
    setCopiedText(label);
    setTimeout(() => setCopiedText(''), 2000);
  };

  const getTierColor = (tier: string | undefined) => {
    switch (tier?.toUpperCase()) {
      case 'HOT': return 'from-red-600 to-orange-600';
      case 'WARM': return 'from-orange-500 to-yellow-500';
      case 'QUALIFIED': return 'from-blue-500 to-cyan-500';
      default: return 'from-gray-500 to-gray-600';
    }
  };

  // Text cleaning functions
  const cleanText = (text: string): string => {
    if (!text) return '';
    
    // Remove numbered section headers (1. 2. 3. etc.)
    let cleaned = text.replace(/^\d+\.\s+\*?\*?/gm, '');
    
    // Remove -** artifacts
    cleaned = cleaned.replace(/-\*\*/g, '');
    
    // Remove ** markdown bold markers at line starts and ends
    cleaned = cleaned.replace(/^\*\*/gm, '');
    cleaned = cleaned.replace(/\*\*$/gm, '');
    
    // Clean up extra whitespace
    cleaned = cleaned.replace(/\n{3,}/g, '\n\n');
    
    // Trim
    cleaned = cleaned.trim();
    
    return cleaned;
  };

  const formatSection = (text: string): string => {
    if (!text) return 'Information not available';
    
    const cleaned = cleanText(text);
    
    // If it's very short and doesn't have proper structure, return as-is
    if (cleaned.length < 100 && !cleaned.includes('\n')) {
      return cleaned;
    }
    
    return cleaned;
  };

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 overflow-y-auto">
      <div className="min-h-screen px-4 py-8">
        <div className="max-w-6xl mx-auto">
          
          {/* Hero Header */}
          <div className={`relative bg-gradient-to-r ${getTierColor(contact.lead_tier)} rounded-2xl p-8 mb-6`}>
            <div className="absolute inset-0 bg-black/20 rounded-2xl"></div>
            <div className="relative z-10">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <div className="flex items-center gap-3 mb-2">
                    <Target className="w-8 h-8 text-white" />
                    <h1 className="text-3xl font-bold text-white">DEAL INTELLIGENCE: {contact.name}</h1>
                  </div>
                  <p className="text-xl text-white/90">{contact.title || 'No title'}</p>
                  <p className="text-lg text-white/80 flex items-center gap-2 mt-1">
                    <Building2 className="w-5 h-5" />
                    {contact.company || 'No company'}
                  </p>
                </div>
                
                <button
                  onClick={onClose}
                  className="p-3 bg-white/20 hover:bg-white/30 text-white rounded-lg backdrop-blur-sm transition-all"
                >
                  <X className="w-6 h-6" />
                </button>
              </div>

              {/* Executive Summary Bar */}
              <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 mt-4">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-white">
                  <div>
                    <div className="text-sm text-white/70">Opportunity Score</div>
                    <div className="text-2xl font-bold">{scores.opportunity_score || contact.opportunity_score || 0}/100</div>
                  </div>
                  <div>
                    <div className="text-sm text-white/70">Persona Type</div>
                    <div className="text-lg font-semibold capitalize">{who.persona_type?.replace(/_/g, ' ') || 'Unknown'}</div>
                  </div>
                  <div>
                    <div className="text-sm text-white/70">Decision Role</div>
                    <div className="text-lg font-semibold capitalize">{who.decision_role || 'Unknown'}</div>
                  </div>
                  <div>
                    <div className="text-sm text-white/70">Influence Level</div>
                    <div className="text-lg font-semibold capitalize">{who.influence_level || 'Unknown'}</div>
                  </div>
                </div>
                
                <div className="mt-4 pt-4 border-t border-white/20 flex flex-wrap items-center gap-4 text-white/90 text-sm">
                  {contact.email && (
                    <a href={`mailto:${contact.email}`} className="flex items-center gap-2 hover:text-white">
                      <Mail className="w-4 h-4" />
                      {contact.email}
                    </a>
                  )}
                  {contact.phone && (
                    <a href={`tel:${contact.phone}`} className="flex items-center gap-2 hover:text-white">
                      <Phone className="w-4 h-4" />
                      {contact.phone}
                    </a>
                  )}
                  {contact.linkedin_url && (
                    <a href={contact.linkedin_url} target="_blank" rel="noopener noreferrer" className="flex items-center gap-2 hover:text-white">
                      <Linkedin className="w-4 h-4" />
                      LinkedIn
                    </a>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* 6-STAGE DEAL FLOW */}
          
          {/* STAGE 1: TARGET QUALIFICATION */}
          <DealStage
            stage={1}
            title="TARGET QUALIFICATION"
            icon={<Target className="w-6 h-6" />}
            color="from-purple-600 to-purple-700"
            expanded={expandedStages.has(1)}
            onToggle={() => toggleStage(1)}
          >
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <StageCard title="WHO to Target" icon={<Users className="w-5 h-5" />}>
                <InfoRow label="Decision Role" value={who.decision_role || 'Unknown'} />
                <InfoRow label="Influence Level" value={who.influence_level || 'Unknown'} />
                <InfoRow label="Persona" value={who.persona_type?.replace(/_/g, ' ') || 'Unknown'} />
              </StageCard>
              
              <StageCard title="WHY This Opportunity Matters" icon={<Lightbulb className="w-5 h-5" />}>
                <div className="space-y-2">
                  <p className="text-sm font-semibold text-slate-300">Pain Points:</p>
                  <div className="text-sm text-slate-400 leading-relaxed whitespace-pre-wrap">
                    {formatSection(enrichmentData.pain_points || 'Analyzing pain points based on role and industry...')}
                  </div>
                </div>
              </StageCard>
            </div>
          </DealStage>

          {/* STAGE 2: ENGAGEMENT TIMING */}
          <DealStage
            stage={2}
            title="ENGAGEMENT TIMING"
            icon={<Calendar className="w-6 h-6" />}
            color="from-blue-600 to-blue-700"
            expanded={expandedStages.has(2)}
            onToggle={() => toggleStage(2)}
          >
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <StageCard title="WHEN to Contact" icon={<Clock className="w-5 h-5" />}>
                <div className="space-y-3">
                  <div className="flex items-center gap-2">
                    <span className={`px-3 py-1 rounded-full text-xs font-bold ${
                      when.urgency_level === 'high' ? 'bg-red-500' :
                      when.urgency_level === 'medium' ? 'bg-yellow-500' :
                      'bg-blue-500'
                    } text-white`}>
                      {when.timing_signal || 'WARMING'}
                    </span>
                  </div>
                  <InfoRow label="Best Time" value={when.optimal_contact_time?.replace(/_/g, ' ') || 'This week'} />
                  <InfoRow label="Follow-up Cadence" value={when.follow_up_cadence?.replace(/_/g, ' ') || 'Weekly'} />
                </div>
              </StageCard>
              
              <StageCard title="Trigger Events (Recent Activity)" icon={<Zap className="w-5 h-5 text-yellow-400" />}>
                <div className="text-sm text-slate-300 leading-relaxed whitespace-pre-wrap">
                  {formatSection(enrichmentData.trigger_events || enrichmentData.deals_database || 'Monitoring for recent activity and business developments...')}
                </div>
              </StageCard>
            </div>
          </DealStage>

          {/* STAGE 3: CONVERSATION STRATEGY */}
          <DealStage
            stage={3}
            title="CONVERSATION STRATEGY"
            icon={<MessageSquare className="w-6 h-6" />}
            color="from-cyan-600 to-cyan-700"
            expanded={expandedStages.has(3)}
            onToggle={() => toggleStage(3)}
          >
            <StageCard title="WHAT to Say" icon={<Target className="w-5 h-5" />}>
              <div className="space-y-4">
                <div>
                  <p className="text-sm font-semibold text-slate-300 mb-2">Opening Hook:</p>
                  <p className="text-white font-medium">{cleanText(what.opening_hook || 'Building personalized approach...')}</p>
                </div>
                
                {what.value_props && what.value_props.length > 0 && (
                  <div>
                    <p className="text-sm font-semibold text-slate-300 mb-2">Value Proposition:</p>
                    <ul className="space-y-1">
                      {what.value_props.map((prop, idx) => (
                        <li key={idx} className="flex items-start gap-2 text-slate-300 text-sm">
                          <CheckCircle2 className="w-4 h-4 text-cyan-400 mt-0.5 flex-shrink-0" />
                          <span>{cleanText(prop)}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                <div className="pt-3 border-t border-slate-700">
                  <p className="text-sm font-semibold text-slate-300 mb-1">Call to Action:</p>
                  <p className="text-cyan-400 font-medium">{cleanText(what.call_to_action || 'Schedule a discovery call')}</p>
                </div>
              </div>
            </StageCard>
          </DealStage>

          {/* STAGE 4: AI-DRIVEN INSIGHTS */}
          <DealStage
            stage={4}
            title="AI-DRIVEN INSIGHTS"
            icon={<Brain className="w-6 h-6" />}
            color="from-indigo-600 to-indigo-700"
            expanded={expandedStages.has(4)}
            onToggle={() => toggleStage(4)}
          >
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <StageCard title="AI Reasoning" icon={<Star className="w-5 h-5" />}>
                <div className="text-sm text-slate-300 leading-relaxed whitespace-pre-wrap">
                  {formatSection(enrichmentData.ai_score_reasoning || enrichmentData.overview || 'High-value contact based on role, company, and timing signals.')}
                </div>
              </StageCard>
              
              <StageCard title="Relationship Strategy" icon={<Heart className="w-5 h-5" />}>
                <div className="text-sm text-slate-300 leading-relaxed whitespace-pre-wrap">
                  {formatSection(enrichmentData.relationship_tips || enrichmentData.mbti_assessment || 'Professional, consultative approach recommended based on personality assessment.')}
                </div>
              </StageCard>
            </div>
          </DealStage>

          {/* STAGE 5: TALKING POINTS */}
          <DealStage
            stage={5}
            title="TALKING POINTS"
            icon={<TrendingUp className="w-6 h-6" />}
            color="from-green-600 to-green-700"
            expanded={expandedStages.has(5)}
            onToggle={() => toggleStage(5)}
          >
            <StageCard title="Sales Opportunity Discussion Points" icon={<MessageSquare className="w-5 h-5" />}>
              <div className="prose prose-invert prose-sm max-w-none">
                <div className="text-slate-300 leading-relaxed whitespace-pre-wrap">
                  {formatSection(enrichmentData.talking_points || enrichmentData.full_profile || 'Building comprehensive talking points based on research...')}
                </div>
              </div>
            </StageCard>
          </DealStage>

          {/* STAGE 6: OUTREACH EXECUTION */}
          <DealStage
            stage={6}
            title="OUTREACH EXECUTION"
            icon={<Mail className="w-6 h-6" />}
            color="from-rose-600 to-rose-700"
            expanded={expandedStages.has(6)}
            onToggle={() => toggleStage(6)}
          >
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Email Templates */}
              {outreach.emails && outreach.emails.length > 0 && (
                <StageCard title="Email Templates" icon={<Mail className="w-5 h-5" />}>
                  <div className="space-y-4">
                    {outreach.emails.map((email, idx) => (
                      <div key={idx} className="bg-slate-900 rounded-lg p-4 border border-slate-700">
                        <div className="flex items-center justify-between mb-3">
                          <span className="text-sm font-bold text-blue-400">Variant {email.variant}</span>
                          <button
                            onClick={() => copyToClipboard(`Subject: ${cleanText(email.subject)}\n\n${cleanText(email.body)}`, `email-${idx}`)}
                            className="text-xs px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white rounded transition-colors flex items-center gap-1"
                          >
                            {copiedText === `email-${idx}` ? (
                              <>
                                <CheckCircle2 className="w-3 h-3" />
                                Copied!
                              </>
                            ) : (
                              <>
                                <Copy className="w-3 h-3" />
                                Copy
                              </>
                            )}
                          </button>
                        </div>
                        <div className="space-y-2">
                          <div>
                            <p className="text-xs text-slate-400 mb-1">Subject:</p>
                            <p className="text-white font-medium text-sm">{cleanText(email.subject)}</p>
                          </div>
                          <div>
                            <p className="text-xs text-slate-400 mb-1">Body:</p>
                            <p className="text-slate-300 text-sm whitespace-pre-wrap">{cleanText(email.body)}</p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </StageCard>
              )}

              {/* Call Scripts */}
              {outreach.call_scripts && outreach.call_scripts.length > 0 && (
                <StageCard title="Call Scripts" icon={<Phone className="w-5 h-5" />}>
                  <div className="space-y-4">
                    {outreach.call_scripts.map((script, idx) => (
                      <div key={idx} className="bg-slate-900 rounded-lg p-4 border border-slate-700">
                        <div className="flex items-center justify-between mb-3">
                          <span className="text-sm font-bold text-green-400">Variant {script.variant}</span>
                          <button
                            onClick={() => copyToClipboard(`Opening: ${cleanText(script.opening)}\n\nQuestions:\n${script.questions?.map(q => cleanText(q)).join('\n')}\n\nClose: ${cleanText(script.close)}`, `call-${idx}`)}
                            className="text-xs px-3 py-1 bg-green-600 hover:bg-green-700 text-white rounded transition-colors flex items-center gap-1"
                          >
                            {copiedText === `call-${idx}` ? (
                              <>
                                <CheckCircle2 className="w-3 h-3" />
                                Copied!
                              </>
                            ) : (
                              <>
                                <Copy className="w-3 h-3" />
                                Copy
                              </>
                            )}
                          </button>
                        </div>
                        <div className="space-y-3">
                          <div>
                            <p className="text-xs text-slate-400 mb-1">Opening:</p>
                            <p className="text-white text-sm">{cleanText(script.opening)}</p>
                          </div>
                          {script.questions && script.questions.length > 0 && (
                            <div>
                              <p className="text-xs text-slate-400 mb-1">Discovery Questions:</p>
                              <ul className="space-y-1">
                                {script.questions.map((q, qIdx) => (
                                  <li key={qIdx} className="text-slate-300 text-sm flex items-start gap-2">
                                    <ArrowRight className="w-4 h-4 text-green-400 mt-0.5 flex-shrink-0" />
                                    <span>{cleanText(q)}</span>
                                  </li>
                                ))}
                              </ul>
                            </div>
                          )}
                          <div>
                            <p className="text-xs text-slate-400 mb-1">Close:</p>
                            <p className="text-green-400 font-medium text-sm">{cleanText(script.close)}</p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </StageCard>
              )}
            </div>
          </DealStage>

          {/* NEXT STEPS - Always Visible */}
          <div className="bg-gradient-to-r from-purple-600 to-blue-600 rounded-2xl p-6 mt-6">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-2xl font-bold text-white mb-2 flex items-center gap-2">
                  <Award className="w-6 h-6" />
                  NEXT STEPS
                </h3>
                <p className="text-white/90">Immediate Actions:</p>
                <ul className="mt-2 space-y-1 text-white/80 text-sm">
                  <li>✓ Send initial outreach within 24 hours</li>
                  <li>✓ Prepare discovery questions</li>
                  <li>✓ Set follow-up reminder for {when.follow_up_cadence?.replace(/_/g, ' ') || '2 days'}</li>
                </ul>
              </div>
              
              <button
                onClick={onClose}
                className="px-8 py-4 bg-white hover:bg-gray-100 text-purple-600 text-lg font-bold rounded-xl shadow-lg hover:shadow-xl transition-all transform hover:scale-105"
              >
                <span className="flex items-center gap-2">
                  <Target className="w-5 h-5" />
                  Ready to Close This Deal
                </span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// Helper Components
function DealStage({ stage, title, icon, color, expanded, onToggle, children }: any) {
  return (
    <div className="mb-4">
      <button
        onClick={onToggle}
        className={`w-full bg-gradient-to-r ${color} rounded-xl p-4 flex items-center justify-between hover:opacity-90 transition-opacity`}
      >
        <div className="flex items-center gap-3 text-white">
          <div className="p-2 bg-white/20 rounded-lg">
            {icon}
          </div>
          <div className="text-left">
            <div className="text-sm font-medium opacity-90">STAGE {stage}</div>
            <div className="text-xl font-bold">{title}</div>
          </div>
        </div>
        {expanded ? (
          <ChevronUp className="w-6 h-6 text-white" />
        ) : (
          <ChevronDown className="w-6 h-6 text-white" />
        )}
      </button>
      
      {expanded && (
        <div className="mt-2 p-6 bg-slate-800 rounded-xl border border-slate-700">
          {children}
        </div>
      )}
    </div>
  );
}

function StageCard({ title, icon, children }: any) {
  return (
    <div className="bg-slate-900 rounded-lg p-4 border border-slate-700">
      <div className="flex items-center gap-2 mb-4 text-slate-300">
        {icon}
        <h4 className="font-semibold">{title}</h4>
      </div>
      {children}
    </div>
  );
}

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between items-center py-2 border-b border-slate-700 last:border-0">
      <span className="text-sm text-slate-400">{label}</span>
      <span className="text-white font-medium capitalize text-sm">{value}</span>
    </div>
  );
}
