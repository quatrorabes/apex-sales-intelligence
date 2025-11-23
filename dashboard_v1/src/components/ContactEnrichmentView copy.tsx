// ContactEnrichmentView.tsx
import React from 'react';
import { X, Brain, User, Building2, MessageSquare, Target, Lightbulb, AlertCircle } from 'lucide-react';

interface ContactEnrichmentViewProps {
  contact: any;
  onClose: () => void;
}

export default function ContactEnrichmentView({ contact, onClose }: ContactEnrichmentViewProps) {
  // Safely parse enrichment data
  let enrichmentData: any = {};

  try {
    if (typeof contact.enrichment_data === 'string') {
      enrichmentData = JSON.parse(contact.enrichment_data);
    } else if (contact.enrichment_data) {
      enrichmentData = contact.enrichment_data;
    }
  } catch (error) {
    console.error('Failed to parse enrichment data:', error);
    enrichmentData = { 
      error: 'Failed to parse enrichment data',
      raw: contact.enrichment_data 
    };
  }

  // Safely parse pain points and talking points
  let painPoints: string[] = [];
  let talkingPoints: string[] = [];

  try {
    if (contact.pain_points) {
      if (typeof contact.pain_points === 'string') {
        painPoints = JSON.parse(contact.pain_points);
      } else if (Array.isArray(contact.pain_points)) {
        painPoints = contact.pain_points;
      }
    }
  } catch {
    painPoints = [];
  }

  try {
    if (contact.talking_points) {
      if (typeof contact.talking_points === 'string') {
        talkingPoints = JSON.parse(contact.talking_points);
      } else if (Array.isArray(contact.talking_points)) {
        talkingPoints = contact.talking_points;
      }
    }
  } catch {
    talkingPoints = [];
  }

  // Extract pain points and talking points from enrichment data if not in separate fields
  if (!painPoints.length && enrichmentData.pain_points) {
    painPoints = Array.isArray(enrichmentData.pain_points) ? enrichmentData.pain_points : [];
  }

  if (!talkingPoints.length && enrichmentData.talking_points) {
    talkingPoints = Array.isArray(enrichmentData.talking_points) ? enrichmentData.talking_points : [];
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4 overflow-y-auto">
      <div className="bg-slate-800 rounded-xl max-w-6xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-slate-800 border-b border-slate-700 p-6 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-gradient-to-br from-cyan-500 to-blue-600 rounded-lg">
              <Brain className="w-6 h-6 text-white" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-slate-100">Intelligence Report</h2>
              <p className="text-sm text-slate-400">{contact.name} @ {contact.company || 'Unknown Company'}</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-slate-700 rounded-lg transition-colors"
          >
            <X className="w-5 h-5 text-slate-400" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Contact Overview */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Person Overview */}
            <div className="bg-slate-700/50 rounded-lg p-5">
              <div className="flex items-center gap-2 mb-4">
                <User className="w-5 h-5 text-cyan-400" />
                <h3 className="text-lg font-semibold text-slate-100">Person Profile</h3>
              </div>
              <div className="space-y-3 text-slate-300">
                {enrichmentData.overview && (
                  <div>
                    <p className="text-sm font-medium text-slate-400 mb-1">Overview</p>
                    <p className="text-sm">{enrichmentData.overview}</p>
                  </div>
                )}
                {enrichmentData.background && (
                  <div>
                    <p className="text-sm font-medium text-slate-400 mb-1">Background</p>
                    <p className="text-sm">{enrichmentData.background}</p>
                  </div>
                )}
                {enrichmentData.education && (
                  <div>
                    <p className="text-sm font-medium text-slate-400 mb-1">Education</p>
                    <p className="text-sm">{enrichmentData.education}</p>
                  </div>
                )}
                {enrichmentData.myers_briggs && (
                  <div>
                    <p className="text-sm font-medium text-slate-400 mb-1">Personality Type</p>
                    <span className="inline-block px-3 py-1 bg-cyan-500/20 text-cyan-400 rounded-full text-sm font-medium">
                      {enrichmentData.myers_briggs}
                    </span>
                  </div>
                )}
              </div>
            </div>
            
    
            {contact.generated_scripts && (
              <div className="mt-6">
                <h3 className="text-lg font-semibold mb-4">Generated Scripts</h3>
              
                {contact.generated_scripts.email && (
                  <div className="mb-4 p-4 bg-gray-50 rounded-lg">
                    <h4 className="font-medium mb-2">Email Template</h4>
                    <p className="text-sm text-gray-700 whitespace-pre-wrap">
                      <strong>Subject:</strong> {contact.generated_scripts.email.subject}
                    </p>
                    <p className="text-sm text-gray-700 whitespace-pre-wrap mt-2">
                      {contact.generated_scripts.email.body}
                    </p>
                  </div>
                )}
              
                {contact.generated_scripts.call_script && (
                  <div className="mb-4 p-4 bg-gray-50 rounded-lg">
                    <h4 className="font-medium mb-2">Call Script</h4>
                    <p className="text-sm text-gray-700 whitespace-pre-wrap">
                      {contact.generated_scripts.call_script}
                    </p>
                  </div>
                )}
              
                {contact.generated_scripts.linkedin && (
                  <div className="mb-4 p-4 bg-gray-50 rounded-lg">
                    <h4 className="font-medium mb-2">LinkedIn Message</h4>
                    <p className="text-sm text-gray-700 whitespace-pre-wrap">
                      {contact.generated_scripts.linkedin}
                    </p>
                  </div>
                )}
              </div>
            )}
    

            {/* Company Overview */}
            <div className="bg-slate-700/50 rounded-lg p-5">
              <div className="flex items-center gap-2 mb-4">
                <Building2 className="w-5 h-5 text-blue-400" />
                <h3 className="text-lg font-semibold text-slate-100">Company Intel</h3>
              </div>
              <div className="space-y-3 text-slate-300">
                {enrichmentData.company_overview && (
                  <div>
                    <p className="text-sm font-medium text-slate-400 mb-1">Overview</p>
                    <p className="text-sm">{enrichmentData.company_overview}</p>
                  </div>
                )}
                {enrichmentData.products_services && (
                  <div>
                    <p className="text-sm font-medium text-slate-400 mb-1">Products & Services</p>
                    <p className="text-sm">{enrichmentData.products_services}</p>
                  </div>
                )}
                {enrichmentData.market_position && (
                  <div>
                    <p className="text-sm font-medium text-slate-400 mb-1">Market Position</p>
                    <p className="text-sm">{enrichmentData.market_position}</p>
                  </div>
                )}
                {enrichmentData.recent_company_news && (
                  <div>
                    <p className="text-sm font-medium text-slate-400 mb-1">Recent News</p>
                    <p className="text-sm">{enrichmentData.recent_company_news}</p>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Sales Intelligence */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Pain Points */}
            <div className="bg-slate-700/50 rounded-lg p-5">
              <div className="flex items-center gap-2 mb-4">
                <AlertCircle className="w-5 h-5 text-red-400" />
                <h3 className="text-lg font-semibold text-slate-100">Pain Points</h3>
              </div>
              <ul className="space-y-2">
                {painPoints.length > 0 ? (
                  painPoints.map((point, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm text-slate-300">
                      <span className="text-red-400 mt-1">•</span>
                      <span>{point}</span>
                    </li>
                  ))
                ) : (
                  <li className="text-sm text-slate-500 italic">No pain points identified</li>
                )}
              </ul>
            </div>

            {/* Talking Points */}
            <div className="bg-slate-700/50 rounded-lg p-5">
              <div className="flex items-center gap-2 mb-4">
                <MessageSquare className="w-5 h-5 text-green-400" />
                <h3 className="text-lg font-semibold text-slate-100">Talking Points</h3>
              </div>
              <ul className="space-y-2">
                {talkingPoints.length > 0 ? (
                  talkingPoints.map((point, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm text-slate-300">
                      <span className="text-green-400 mt-1">•</span>
                      <span>{point}</span>
                    </li>
                  ))
                ) : (
                  <li className="text-sm text-slate-500 italic">No talking points identified</li>
                )}
              </ul>
            </div>

            {/* Trigger Events */}
            <div className="bg-slate-700/50 rounded-lg p-5">
              <div className="flex items-center gap-2 mb-4">
                <Lightbulb className="w-5 h-5 text-yellow-400" />
                <h3 className="text-lg font-semibold text-slate-100">Trigger Events</h3>
              </div>
              <ul className="space-y-2">
                {enrichmentData.trigger_events && enrichmentData.trigger_events.length > 0 ? (
                  enrichmentData.trigger_events.map((event: string, i: number) => (
                    <li key={i} className="flex items-start gap-2 text-sm text-slate-300">
                      <span className="text-yellow-400 mt-1">•</span>
                      <span>{event}</span>
                    </li>
                  ))
                ) : (
                  <li className="text-sm text-slate-500 italic">No trigger events identified</li>
                )}
              </ul>
            </div>
          </div>

          {/* Outreach Strategy */}
          {enrichmentData.outreach_approach && (
            <div className="bg-slate-700/50 rounded-lg p-5">
              <div className="flex items-center gap-2 mb-4">
                <Target className="w-5 h-5 text-purple-400" />
                <h3 className="text-lg font-semibold text-slate-100">Outreach Strategy</h3>
              </div>
              <p className="text-sm text-slate-300 whitespace-pre-wrap">{enrichmentData.outreach_approach}</p>
            </div>
          )}

          {/* AI Reasoning */}
          {enrichmentData.ai_score_reasoning && (
            <div className="bg-gradient-to-r from-cyan-500/10 to-blue-600/10 border border-cyan-500/30 rounded-lg p-5">
              <div className="flex items-center gap-2 mb-4">
                <Brain className="w-5 h-5 text-cyan-400" />
                <h3 className="text-lg font-semibold text-slate-100">AI Analysis</h3>
              </div>
              <p className="text-sm text-slate-300">{enrichmentData.ai_score_reasoning}</p>
            </div>
          )}

          {/* Debug Section - Only show if there's an error */}
          {enrichmentData.error && (
            <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-5">
              <h3 className="text-lg font-semibold text-red-400 mb-2">Data Error</h3>
              <p className="text-sm text-slate-300 mb-2">There was an issue parsing the enrichment data. Raw data:</p>
              <pre className="text-xs text-slate-400 overflow-x-auto bg-slate-900 p-3 rounded">
                {JSON.stringify(enrichmentData.raw || contact.enrichment_data, null, 2)}
              </pre>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}