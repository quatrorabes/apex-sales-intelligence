import React, { useState, useEffect } from "react";
import {
  X,
  Brain,
  User,
  Building2,
  Target,
  AlertCircle,
  Mail,
  Phone,
  Copy,
  Linkedin,
  RefreshCw,
  BarChart3,
  FileText
} from "lucide-react";

interface ContactEnrichmentViewProps {
  contactId: number;
  onClose: () => void;
}

export default function ContactEnrichmentView({
  contactId,
  onClose,
}: ContactEnrichmentViewProps) {
  const [activeTab, setActiveTab] = useState('overview');
  const [loading, setLoading] = useState(true);
  const [contact, setContact] = useState<any>(null);
  const [enrichmentData, setEnrichmentData] = useState<any>({});
  const [fullProfile, setFullProfile] = useState<string>("");
  const [error, setError] = useState<string | null>(null);

  const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

  useEffect(() => {
    fetchIntelligenceData();
  }, [contactId]);

  const fetchIntelligenceData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE}/api/contacts/${contactId}/intelligence`);
      
      if (!response.ok) {
        throw new Error('Failed to fetch intelligence data');
      }
      
      const data = await response.json();
      
      if (!data.success) {
        throw new Error(data.error || 'Failed to load data');
      }
      
      setContact(data.contact);
      
      const enrichment = data.enrichment_data || {};
      setEnrichmentData(enrichment);
      
      const profile = enrichment.full_profile_text || 
                     enrichment.perplexity_insights || 
                     enrichment.profile || 
                     "";
      setFullProfile(profile);
      
    } catch (err: any) {
      console.error("Error fetching intelligence:", err);
      setError(err.message || "Failed to load intelligence data");
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    alert("Copied to clipboard!");
  };

  const tabs = [
    { id: 'full', label: 'Full Profile', icon: FileText },
    { id: 'overview', label: 'Overview', icon: User },
    { id: 'company', label: 'Company', icon: Building2 },
    { id: 'outreach', label: 'Outreach', icon: Mail },
  ];

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-6 z-50">
        <div className="bg-slate-800 rounded-xl border border-slate-700 p-12 flex flex-col items-center gap-4">
          <RefreshCw className="w-8 h-8 text-cyan-400 animate-spin" />
          <p className="text-white">Loading Intelligence Report...</p>
        </div>
      </div>
    );
  }

  if (error || !contact) {
    return (
      <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-6 z-50">
        <div className="bg-slate-800 rounded-xl border border-slate-700 p-12">
          <div className="flex flex-col items-center gap-4">
            <AlertCircle className="w-12 h-12 text-red-400" />
            <p className="text-white text-lg">{error || "No contact data available"}</p>
            <p className="text-slate-400 text-sm">The contact may not be enriched yet. Try enriching this contact first.</p>
            <button
              onClick={onClose}
              className="px-6 py-2 bg-slate-700 text-white rounded-lg hover:bg-slate-600 transition-colors"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-6 z-50 overflow-y-auto">
      <div className="bg-slate-800 rounded-xl border border-slate-700 max-w-7xl w-full my-8 flex flex-col max-h-[90vh]">
        
        <div className="p-6 border-b border-slate-700 flex items-center justify-between bg-slate-900/50 flex-shrink-0">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-cyan-500 to-blue-600 rounded-lg flex items-center justify-center">
              <Brain className="w-6 h-6 text-white" />
            </div>
            <div>
              <h2 className="text-xl font-semibold text-white">
                Intelligence Report
              </h2>
              <p className="text-sm text-slate-400">
                {contact.name} @ {contact.company || "Unknown Company"}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-white transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        <div className="border-b border-slate-700 bg-slate-900/30 flex-shrink-0">
          <div className="flex gap-1 px-6 overflow-x-auto">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center gap-2 px-4 py-3 border-b-2 transition-all whitespace-nowrap ${
                    activeTab === tab.id
                      ? 'border-cyan-500 text-cyan-400 bg-slate-800/50'
                      : 'border-transparent text-slate-400 hover:text-white hover:bg-slate-800/30'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  {tab.label}
                </button>
              );
            })}
          </div>
        </div>

        <div className="flex-1 overflow-y-auto">
          <div className="p-6">

            {activeTab === 'full' && (
              <div className="space-y-4">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-medium text-cyan-400">Complete Intelligence Profile</h3>
                  <button
                    onClick={() => copyToClipboard(fullProfile)}
                    className="px-3 py-1 bg-slate-700 text-white rounded hover:bg-slate-600 flex items-center gap-1 text-sm"
                  >
                    <Copy className="w-3 h-3" />
                    Copy All
                  </button>
                </div>
                
                {fullProfile ? (
                  <div className="bg-slate-900/50 rounded-xl p-6 border border-slate-700">
                    <div className="text-slate-300 whitespace-pre-wrap text-sm leading-relaxed font-mono max-h-[600px] overflow-y-auto">
                      {fullProfile}
                    </div>
                  </div>
                ) : (
                  <div className="bg-slate-900/50 rounded-xl p-6 border border-slate-700">
                    <div className="flex flex-col items-center gap-4 py-8">
                      <AlertCircle className="w-12 h-12 text-yellow-400" />
                      <p className="text-slate-400 text-center">
                        No enrichment data available yet.<br/>
                        This contact needs to be enriched with AI intelligence.
                      </p>
                    </div>
                  </div>
                )}
              </div>
            )}

            {activeTab === 'overview' && (
              <div className="space-y-6">
                <div className="bg-slate-900/50 rounded-xl p-6 border border-slate-700">
                  <h3 className="text-lg font-medium text-cyan-400 mb-6 flex items-center gap-2">
                    <User className="w-5 h-5" />
                    Contact Information
                  </h3>
                  
                  <div className="grid grid-cols-2 gap-6">
                    <div className="space-y-4">
                      <div>
                        <p className="text-sm text-slate-400 mb-1">Full Name</p>
                        <p className="text-lg text-white font-medium">{contact.name}</p>
                      </div>
                      
                      <div>
                        <p className="text-sm text-slate-400 mb-1">Title</p>
                        <p className="text-lg text-white">{contact.title || "Not available"}</p>
                      </div>
                      
                      <div>
                        <p className="text-sm text-slate-400 mb-1">Company</p>
                        <p className="text-lg text-white">{contact.company || "Not available"}</p>
                      </div>
                    </div>
                    
                    <div className="space-y-4">
                      <div>
                        <p className="text-sm text-slate-400 mb-1">Email</p>
                        <a href={`mailto:${contact.email}`} className="text-lg text-cyan-400 hover:text-cyan-300 flex items-center gap-2">
                          <Mail className="w-4 h-4" />
                          {contact.email || "Not available"}
                        </a>
                      </div>
                      
                      <div>
                        <p className="text-sm text-slate-400 mb-1">Phone</p>
                        <p className="text-lg text-white flex items-center gap-2">
                          <Phone className="w-4 h-4" />
                          {contact.phone || "Not available"}
                        </p>
                      </div>
                      
                      <div>
                        <p className="text-sm text-slate-400 mb-1">LinkedIn</p>
                        {contact.linkedin_url ? (
                          <a 
                            href={contact.linkedin_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-lg text-cyan-400 hover:text-cyan-300 flex items-center gap-2"
                          >
                            <Linkedin className="w-4 h-4" />
                            View Profile
                          </a>
                        ) : (
                          <p className="text-lg text-slate-500">Not available</p>
                        )}
                      </div>
                    </div>
                  </div>
                </div>

                <div className="grid grid-cols-4 gap-4">
                  <div className="bg-slate-900/50 rounded-xl p-4 border border-slate-700">
                    <p className="text-xs text-slate-400 mb-1">MDCP Score</p>
                    <p className="text-2xl font-bold text-cyan-400">
                      {contact.mdcp_score ? Math.round(contact.mdcp_score) : "—"}
                    </p>
                  </div>
                  <div className="bg-slate-900/50 rounded-xl p-4 border border-slate-700">
                    <p className="text-xs text-slate-400 mb-1">Priority</p>
                    <p className="text-2xl font-bold text-green-400">
                      {contact.urgency_level || "—"}
                    </p>
                  </div>
                  <div className="bg-slate-900/50 rounded-xl p-4 border border-slate-700">
                    <p className="text-xs text-slate-400 mb-1">Status</p>
                    <p className="text-2xl font-bold text-yellow-400">
                      {contact.enrichment_status || "pending"}
                    </p>
                  </div>
                  <div className="bg-slate-900/50 rounded-xl p-4 border border-slate-700">
                    <p className="text-xs text-slate-400 mb-1">Profile Size</p>
                    <p className="text-2xl font-bold text-purple-400">
                      {fullProfile ? `${(fullProfile.length / 1000).toFixed(1)}K` : "—"}
                    </p>
                  </div>
                </div>

                {fullProfile && (
                  <div className="bg-slate-900/50 rounded-xl p-6 border border-slate-700">
                    <h3 className="text-lg font-medium text-cyan-400 mb-4">Profile Preview</h3>
                    <div className="text-slate-300 whitespace-pre-wrap text-sm leading-relaxed max-h-96 overflow-y-auto">
                      {fullProfile.substring(0, 2000)}...
                      <div className="mt-4">
                        <button
                          onClick={() => setActiveTab('full')}
                          className="text-cyan-400 hover:text-cyan-300 text-sm"
                        >
                          → View Full Profile
                        </button>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}

            {activeTab === 'company' && (
              <div className="space-y-6">
                <div className="bg-slate-900/50 rounded-xl p-6 border border-slate-700">
                  <h3 className="text-xl font-medium text-cyan-400 mb-4">Company Information</h3>
                  <div className="text-slate-300 whitespace-pre-wrap text-sm leading-relaxed">
                    {fullProfile || "No company data available"}
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'outreach' && (
              <div className="space-y-6">
                <div className="bg-slate-900/50 rounded-xl p-6 border border-slate-700">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="flex items-center gap-2 text-lg font-medium text-cyan-400">
                      <Mail className="w-5 h-5" />
                      Outreach Intelligence
                    </h3>
                    <button
                      onClick={() => copyToClipboard(fullProfile)}
                      className="px-3 py-1 bg-slate-700 text-white rounded hover:bg-slate-600 flex items-center gap-1 text-sm"
                    >
                      <Copy className="w-3 h-3" />
                      Copy
                    </button>
                  </div>
                  <div className="text-slate-300 whitespace-pre-wrap text-sm leading-relaxed">
                    {fullProfile || "No outreach data available"}
                  </div>
                </div>
              </div>
            )}

          </div>
        </div>

        <div className="p-6 border-t border-slate-700 bg-slate-900/50 flex-shrink-0">
          <div className="flex items-center justify-between">
            <div className="text-sm text-slate-400">
              <p>Enrichment Status: <span className="text-cyan-400 font-medium">{contact.enrichment_status || 'pending'}</span></p>
              <p>Last Updated: {contact.enrichment_date || 'Never'} • Profile Length: {fullProfile.length.toLocaleString()} chars</p>
            </div>
            <button
              onClick={onClose}
              className="px-6 py-2 bg-slate-700 text-white rounded-lg hover:bg-slate-600 transition-colors"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
