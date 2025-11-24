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
  FileText,
  MessageSquare,
  Zap,
  Loader,
  Flag,
  RotateCcw,
  Newspaper
} from "lucide-react";

interface ContactEnrichmentViewProps {
  contactId: number;
  onClose: () => void;
}

interface GeneratedContent {
  email1?: string;
  email2?: string;
  email3?: string;
  call_script1?: string;
  call_script2?: string;
  call_script3?: string;
  linkedin_message?: string;
  linkedin_followup?: string;
}

export default function ContactEnrichmentView({
  contactId,
  onClose,
}: ContactEnrichmentViewProps) {
  const [activeTab, setActiveTab] = useState('overview');
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [reEnriching, setReEnriching] = useState(false);
  const [scoring, setScoring] = useState(false);
  const [contact, setContact] = useState<any>(null);
  const [enrichmentData, setEnrichmentData] = useState<any>({});
  const [fullProfile, setFullProfile] = useState<string>("");
  const [error, setError] = useState<string | null>(null);
  const [generatedContent, setGeneratedContent] = useState<GeneratedContent>({});

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

      if (enrichment.generated_content) {
        setGeneratedContent(enrichment.generated_content);
      }
      
    } catch (err: any) {
      console.error("Error fetching intelligence:", err);
      setError(err.message || "Failed to load intelligence data");
    } finally {
      setLoading(false);
    }
  };

  const handleScore = async () => {
    if (!confirm("Score this contact using APEX Intelligence algorithms?")) {
      return;
    }

    setScoring(true);
    try {
      const response = await fetch(`${API_BASE}/api/contacts/${contactId}/score`, {
        method: "POST",
      });

      const data = await response.json();

      if (data.success) {
        alert(
          `Contact scored successfully!\n\n` +
          `Priority Score: ${Math.round(data.scores.priority_score)}\n` +
          `MDCP: ${Math.round(data.scores.mdcp_score)} (${data.scores.mdcp_tier || 'N/A'})\n` +
          `RSS: ${Math.round(data.scores.rss_score)} (${data.scores.rss_tier || 'N/A'})\n` +
          `Urgency: ${data.scores.urgency_level || 'N/A'}`
        );
        await fetchIntelligenceData();
      } else {
        alert(`Scoring failed: ${data.error}`);
      }
    } catch (error) {
      console.error("Error scoring contact:", error);
      alert("Failed to score contact");
    } finally {
      setScoring(false);
    }
  };

  const handleReEnrich = async () => {
    if (!confirm("Re-enrich this contact? This will fetch fresh data from Perplexity API and may take 30-60 seconds.")) {
      return;
    }

    setReEnriching(true);
    try {
      await fetch(`${API_BASE}/api/contacts/${contactId}/reset-enrichment`, {
        method: "POST",
      });

      const response = await fetch(`${API_BASE}/api/contacts/${contactId}/enrich`, {
        method: "POST",
      });

      const data = await response.json();

      if (data.success) {
        alert("Contact re-enriched successfully! Refreshing data...");
        await fetchIntelligenceData();
      } else {
        alert(`Re-enrichment failed: ${data.error}`);
      }
    } catch (error) {
      console.error("Error re-enriching contact:", error);
      alert("Failed to re-enrich contact");
    } finally {
      setReEnriching(false);
    }
  };

  const handleReportIncorrect = async () => {
    const reason = prompt("What's incorrect about this profile? (This helps improve future enrichments)");
    if (!reason) return;

    try {
      await fetch(`${API_BASE}/api/contacts/${contactId}/report-issue`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ reason }),
      });
      alert("Thank you! Issue reported. You can re-enrich to generate a new profile.");
    } catch (error) {
      console.error("Error reporting issue:", error);
    }
  };

  const generateContent = async () => {
    if (!confirm("Generate outreach content using OpenAI? This will create 3 emails, 3 call scripts, and LinkedIn messages.")) {
      return;
    }

    setGenerating(true);
    try {
      const response = await fetch(`${API_BASE}/api/contacts/${contactId}/generate-content`, {
        method: "POST",
      });

      const data = await response.json();

      if (data.success) {
        setGeneratedContent(data.content);
        alert("Content generated successfully!");
      } else {
        alert(`Generation failed: ${data.error}`);
      }
    } catch (error) {
      console.error("Error generating content:", error);
      alert("Failed to generate content");
    } finally {
      setGenerating(false);
    }
  };

  const copyToClipboard = (text: string, label: string) => {
    navigator.clipboard.writeText(text);
    alert(`${label} copied to clipboard!`);
  };

  const extractSection = (markers: string[], endMarkers?: string[]): string => {
    if (!fullProfile) return "No data available";
    
    const profileLower = fullProfile.toLowerCase();
    
    let startIndex = -1;
    let usedMarker = "";
    
    for (const marker of markers) {
      const idx = profileLower.indexOf(marker.toLowerCase());
      if (idx !== -1) {
        startIndex = idx;
        usedMarker = marker;
        break;
      }
    }
    
    if (startIndex === -1) {
      return `Section not found in profile.`;
    }
    
    let endIndex = fullProfile.length;
    
    if (endMarkers) {
      for (const endMarker of endMarkers) {
        const idx = profileLower.indexOf(endMarker.toLowerCase(), startIndex + usedMarker.length);
        if (idx !== -1) {
          endIndex = idx;
          break;
        }
      }
    }
    
    return fullProfile.substring(startIndex, endIndex).trim();
  };

  const tabs = [
    { id: 'overview', label: 'Overview', icon: User },
    { id: 'scoring', label: 'APEX Scores', icon: Target },
    { id: 'personal', label: 'Individual Profile', icon: User },
    { id: 'company', label: 'Company', icon: Building2 },
    { id: 'personality', label: 'Personality', icon: BarChart3 },
    { id: 'news', label: 'Recent News', icon: Newspaper },
    { id: 'sales', label: 'Sales Intel', icon: Target },
    { id: 'outreach', label: 'Outreach Strategy', icon: Zap },
    { id: 'content', label: 'Generated Content', icon: MessageSquare },
    { id: 'full', label: 'Raw Profile', icon: FileText },
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
          <div className="flex items-center gap-2">
            <button
              onClick={handleScore}
              disabled={scoring}
              className="px-3 py-2 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 rounded-lg flex items-center gap-2 text-sm"
              title="Score this contact"
            >
              {scoring ? (
                <>
                  <Loader className="w-4 h-4 animate-spin" />
                  Scoring...
                </>
              ) : (
                <>
                  <Target className="w-4 h-4" />
                  Score
                </>
              )}
            </button>
            <button
              onClick={handleReEnrich}
              disabled={reEnriching}
              className="px-3 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 rounded-lg flex items-center gap-2 text-sm"
              title="Re-enrich with fresh data"
            >
              {reEnriching ? (
                <>
                  <Loader className="w-4 h-4 animate-spin" />
                  Re-enriching...
                </>
              ) : (
                <>
                  <RotateCcw className="w-4 h-4" />
                  Re-enrich
                </>
              )}
            </button>
            <button
              onClick={handleReportIncorrect}
              className="px-3 py-2 bg-orange-600 hover:bg-orange-700 rounded-lg flex items-center gap-2 text-sm"
              title="Report incorrect profile"
            >
              <Flag className="w-4 h-4" />
              Report
            </button>
            <button
              onClick={onClose}
              className="text-slate-400 hover:text-white transition-colors"
            >
              <X className="w-6 h-6" />
            </button>
          </div>
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

                <div className="grid grid-cols-5 gap-4">
                  <div className="bg-slate-900/50 rounded-xl p-4 border border-slate-700">
                    <p className="text-xs text-slate-400 mb-1">Priority Score</p>
                    <p className="text-2xl font-bold text-cyan-400">
                      {contact.priority_score ? Math.round(contact.priority_score) : "—"}
                    </p>
                    <p className="text-xs text-slate-500 mt-1">{contact.urgency_level || "Not scored"}</p>
                  </div>
                  <div className="bg-slate-900/50 rounded-xl p-4 border border-slate-700">
                    <p className="text-xs text-slate-400 mb-1">MDCP Score</p>
                    <p className="text-2xl font-bold text-purple-400">
                      {contact.mdcp_score ? Math.round(contact.mdcp_score) : "—"}
                    </p>
                    <p className="text-xs text-slate-500 mt-1">{contact.mdcp_tier || "—"}</p>
                  </div>
                  <div className="bg-slate-900/50 rounded-xl p-4 border border-slate-700">
                    <p className="text-xs text-slate-400 mb-1">RSS Score</p>
                    <p className="text-2xl font-bold text-green-400">
                      {contact.rss_score ? Math.round(contact.rss_score) : "—"}
                    </p>
                    <p className="text-xs text-slate-500 mt-1">{contact.rss_tier || "—"}</p>
                  </div>
                  <div className="bg-slate-900/50 rounded-xl p-4 border border-slate-700">
                    <p className="text-xs text-slate-400 mb-1">Enrichment</p>
                    <p className="text-2xl font-bold text-yellow-400">
                      {contact.enrichment_status || "pending"}
                    </p>
                    <p className="text-xs text-slate-500 mt-1">{contact.enrichment_date ? new Date(contact.enrichment_date).toLocaleDateString() : "—"}</p>
                  </div>
                  <div className="bg-slate-900/50 rounded-xl p-4 border border-slate-700">
                    <p className="text-xs text-slate-400 mb-1">Profile Size</p>
                    <p className="text-2xl font-bold text-blue-400">
                      {fullProfile ? `${(fullProfile.length / 1000).toFixed(1)}K` : "—"}
                    </p>
                    <p className="text-xs text-slate-500 mt-1">characters</p>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'scoring' && (
              <div className="space-y-6">
                <div className="bg-slate-900/50 rounded-xl p-6 border border-slate-700">
                  <h3 className="text-xl font-medium text-cyan-400 mb-6 flex items-center gap-2">
                    <Target className="w-5 h-5" />
                    APEX Intelligence Scoring
                  </h3>
                  
                  {!contact.priority_score ? (
                    <div className="text-center py-8">
                      <p className="text-slate-400 mb-4">Contact has not been scored yet.</p>
                      <button
                        onClick={handleScore}
                        className="px-6 py-3 bg-purple-600 hover:bg-purple-700 rounded-lg flex items-center gap-2 mx-auto"
                      >
                        <Target className="w-5 h-5" />
                        Score Contact Now
                      </button>
                    </div>
                  ) : (
                    <div className="space-y-6">
                      <div className="bg-slate-800/50 rounded-lg p-6">
                        <div className="flex items-center justify-between mb-4">
                          <h4 className="text-lg font-medium text-white">Overall Priority Score</h4>
                          <span className={`text-3xl font-bold ${
                            contact.priority_score >= 80 ? 'text-red-400' :
                            contact.priority_score >= 65 ? 'text-orange-400' :
                            contact.priority_score >= 50 ? 'text-yellow-400' :
                            'text-gray-400'
                          }`}>
                            {Math.round(contact.priority_score)}
                          </span>
                        </div>
                        <div className="w-full bg-slate-700 rounded-full h-3 overflow-hidden">
                          <div 
                            className={`h-full rounded-full ${
                              contact.priority_score >= 80 ? 'bg-gradient-to-r from-red-600 to-red-400' :
                              contact.priority_score >= 65 ? 'bg-gradient-to-r from-orange-600 to-orange-400' :
                              contact.priority_score >= 50 ? 'bg-gradient-to-r from-yellow-600 to-yellow-400' :
                              'bg-gradient-to-r from-gray-600 to-gray-400'
                            }`}
                            style={{ width: `${contact.priority_score}%` }}
                          />
                        </div>
                        <div className="mt-4 flex items-center justify-between text-sm">
                          <span className="text-slate-400">Urgency Level:</span>
                          <span className={`font-medium ${
                            contact.urgency_level === 'IMMEDIATE' ? 'text-red-400' :
                            contact.urgency_level === 'HIGH' ? 'text-orange-400' :
                            contact.urgency_level === 'MEDIUM' ? 'text-yellow-400' :
                            'text-gray-400'
                          }`}>
                            {contact.urgency_level || 'Not set'}
                          </span>
                        </div>
                      </div>

                      <div className="bg-slate-800/50 rounded-lg p-6">
                        <div className="flex items-center justify-between mb-4">
                          <div>
                            <h4 className="text-lg font-medium text-white">MDCP Score</h4>
                            <p className="text-sm text-slate-400">Market Dynamics & Company Position</p>
                          </div>
                          <div className="text-right">
                            <span className="text-3xl font-bold text-purple-400">
                              {contact.mdcp_score ? Math.round(contact.mdcp_score) : "—"}
                            </span>
                            <p className="text-sm text-slate-400">{contact.mdcp_tier || "—"}</p>
                          </div>
                        </div>
                        <div className="w-full bg-slate-700 rounded-full h-2 overflow-hidden">
                          <div 
                            className="h-full bg-gradient-to-r from-purple-600 to-purple-400 rounded-full"
                            style={{ width: `${contact.mdcp_score || 0}%` }}
                          />
                        </div>
                      </div>

                      <div className="bg-slate-800/50 rounded-lg p-6">
                        <div className="flex items-center justify-between mb-4">
                          <div>
                            <h4 className="text-lg font-medium text-white">RSS Score</h4>
                            <p className="text-sm text-slate-400">Role Seniority & Scope</p>
                          </div>
                          <div className="text-right">
                            <span className="text-3xl font-bold text-green-400">
                              {contact.rss_score ? Math.round(contact.rss_score) : "—"}
                            </span>
                            <p className="text-sm text-slate-400">{contact.rss_tier || "—"}</p>
                          </div>
                        </div>
                        <div className="w-full bg-slate-700 rounded-full h-2 overflow-hidden">
                          <div 
                            className="h-full bg-gradient-to-r from-green-600 to-green-400 rounded-full"
                            style={{ width: `${contact.rss_score || 0}%` }}
                          />
                        </div>
                      </div>

                      {contact.recommended_action && (
                        <div className="bg-blue-900/20 border border-blue-700/50 rounded-lg p-6">
                          <h4 className="text-lg font-medium text-blue-400 mb-3">Recommended Action</h4>
                          <p className="text-slate-300">{contact.recommended_action}</p>
                        </div>
                      )}

                      <div className="bg-slate-800/30 rounded-lg p-4 text-sm">
                        <div className="grid grid-cols-2 gap-4">
                          <div>
                            <p className="text-slate-400">Last Scored:</p>
                            <p className="text-white">{contact.last_scored ? new Date(contact.last_scored).toLocaleString() : 'Never'}</p>
                          </div>
                          <div>
                            <p className="text-slate-400">Algorithm Version:</p>
                            <p className="text-white">{contact.calculation_version || 'N/A'}</p>
                          </div>
                          <div>
                            <p className="text-slate-400">Persona Type:</p>
                            <p className="text-white">{contact.persona_type || 'Not determined'}</p>
                          </div>
                          <div>
                            <p className="text-slate-400">Persona Tier:</p>
                            <p className="text-white">{contact.persona_tier || 'Not determined'}</p>
                          </div>
                        </div>
                      </div>

                      <div className="text-center">
                        <button
                          onClick={handleScore}
                          disabled={scoring}
                          className="px-6 py-2 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 rounded-lg flex items-center gap-2 mx-auto"
                        >
                          <RefreshCw className={`w-4 h-4 ${scoring ? 'animate-spin' : ''}`} />
                          Re-score Contact
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}

            {activeTab === 'personal' && (
              <div className="bg-slate-900/50 rounded-xl p-6 border border-slate-700">
                <h3 className="text-xl font-medium text-cyan-400 mb-4">Individual Profile: {contact.name}</h3>
                <div className="text-slate-300 whitespace-pre-wrap text-sm leading-relaxed">
                  {extractSection(
                    ["## " + contact.name, "### " + contact.name, "Individual Profile"],
                    ["## " + (contact.company || ""), "###" + (contact.company || ""), "Company", "### 1.", "### 2."]
                  )}
                </div>
              </div>
            )}

            {activeTab === 'company' && (
              <div className="bg-slate-900/50 rounded-xl p-6 border border-slate-700">
                <h3 className="text-xl font-medium text-cyan-400 mb-4">Company Profile: {contact.company}</h3>
                <div className="text-slate-300 whitespace-pre-wrap text-sm leading-relaxed">
                  {extractSection(
                    ["## " + (contact.company || "Company"), "### " + (contact.company || "Company")],
                    ["## " + contact.name, "### " + contact.name, "Individual Profile", "### 1. Overview"]
                  )}
                </div>
              </div>
            )}

            {activeTab === 'personality' && (
              <div className="space-y-4">
                <div className="bg-slate-900/50 rounded-xl p-6 border border-slate-700">
                  <h3 className="text-xl font-medium text-purple-400 mb-4">Personality Profile</h3>
                  <div className="text-slate-300 whitespace-pre-wrap text-sm leading-relaxed">
                    {extractSection(
                      ["### 6. Personality", "Personality Detail", "Myers-Briggs"],
                      ["### 7.", "### 8.", "Sales Opportunity"]
                    )}
                  </div>
                </div>

                <div className="bg-slate-900/50 rounded-xl p-6 border border-slate-700">
                  <h3 className="text-lg font-medium text-blue-400 mb-4">Relationship Tips</h3>
                  <div className="text-slate-300 whitespace-pre-wrap text-sm leading-relaxed">
                    {extractSection(
                      ["### Relationship Tips", "Relationship Tips ("],
                      ["### Pain Points", "Pain Points"]
                    )}
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'news' && (
              <div className="space-y-4">
                <div className="bg-slate-900/50 rounded-xl p-6 border border-slate-700">
                  <h3 className="text-xl font-medium text-blue-400 mb-4 flex items-center gap-2">
                    <Newspaper className="w-5 h-5" />
                    Recent News & Developments
                  </h3>
                  <div className="text-slate-300 whitespace-pre-wrap text-sm leading-relaxed">
                    {extractSection(
                      ["### 5. Recent News", "Recent News", "### 11. Company News"],
                      ["### 6.", "### 12.", "Trigger Events"]
                    )}
                  </div>
                </div>

                <div className="bg-slate-900/50 rounded-xl p-6 border border-slate-700">
                  <h3 className="text-lg font-medium text-yellow-400 mb-4">Trigger Events</h3>
                  <div className="text-slate-300 whitespace-pre-wrap text-sm leading-relaxed">
                    {extractSection(
                      ["### 12. Trigger Events", "Trigger Events"],
                      ["### 13.", "Competitive Intelligence"]
                    )}
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'sales' && (
              <div className="space-y-4">
                <div className="bg-slate-900/50 rounded-xl p-6 border border-slate-700">
                  <h3 className="text-xl font-medium text-red-400 mb-4 flex items-center gap-2">
                    <AlertCircle className="w-5 h-5" />
                    Pain Points
                  </h3>
                  <div className="text-slate-300 whitespace-pre-wrap text-sm leading-relaxed">
                    {extractSection(
                      ["### Pain Points", "Pain Points ("],
                      ["### Outreach", "Outreach Approach"]
                    )}
                  </div>
                </div>

                <div className="bg-slate-900/50 rounded-xl p-6 border border-slate-700">
                  <h3 className="text-lg font-medium text-green-400 mb-4">Sales Talking Points</h3>
                  <div className="text-slate-300 whitespace-pre-wrap text-sm leading-relaxed">
                    {extractSection(
                      ["### 8. Sales Opportunity", "Sales Opportunity Talking Points"],
                      ["### 9.", "Deals Database"]
                    )}
                  </div>
                </div>

                <div className="bg-slate-900/50 rounded-xl p-6 border border-slate-700">
                  <h3 className="text-lg font-medium text-cyan-400 mb-4">AI Score Reasoning</h3>
                  <div className="text-slate-300 whitespace-pre-wrap text-sm leading-relaxed">
                    {extractSection(
                      ["### AI Score Reasoning", "AI Score Reasoning:"],
                      ["### Relationship", "Relationship Tips"]
                    )}
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'outreach' && (
              <div className="bg-slate-900/50 rounded-xl p-6 border border-slate-700">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-xl font-medium text-cyan-400">Outreach Approach</h3>
                  <button
                    onClick={() => copyToClipboard(extractSection(["### Outreach Approach", "Outreach Approach"], []), "Outreach Strategy")}
                    className="px-3 py-1 bg-slate-700 text-white rounded hover:bg-slate-600 flex items-center gap-1 text-sm"
                  >
                    <Copy className="w-3 h-3" />
                    Copy
                  </button>
                </div>
                <div className="text-slate-300 whitespace-pre-wrap text-sm leading-relaxed">
                  {extractSection(
                    ["### Outreach Approach", "Outreach Approach"],
                    []
                  )}
                </div>
              </div>
            )}

            {activeTab === 'content' && (
              <div className="space-y-6">
                <div className="flex items-center justify-between">
                  <h3 className="text-xl font-medium text-cyan-400">Generated Outreach Content</h3>
                  <button
                    onClick={generateContent}
                    disabled={generating}
                    className="px-4 py-2 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 rounded-lg flex items-center gap-2"
                  >
                    {generating ? (
                      <>
                        <Loader className="w-4 h-4 animate-spin" />
                        Generating...
                      </>
                    ) : (
                      <>
                        <Zap className="w-4 h-4" />
                        Generate Content
                      </>
                    )}
                  </button>
                </div>

                {Object.keys(generatedContent).length === 0 ? (
                  <div className="bg-slate-900/50 rounded-xl p-12 border border-slate-700 text-center">
                    <MessageSquare className="w-12 h-12 text-slate-600 mx-auto mb-4" />
                    <p className="text-slate-400">No content generated yet. Click "Generate Content" to create emails, call scripts, and LinkedIn messages using this intelligence profile.</p>
                  </div>
                ) : (
                  <div className="space-y-6">
                    <p className="text-slate-400">Content generation will be added in next update</p>
                  </div>
                )}
              </div>
            )}

            {activeTab === 'full' && (
              <div className="space-y-4">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-medium text-cyan-400">Complete Intelligence Profile</h3>
                  <button
                    onClick={() => copyToClipboard(fullProfile, "Full Profile")}
                    className="px-3 py-1 bg-slate-700 text-white rounded hover:bg-slate-600 flex items-center gap-1 text-sm"
                  >
                    <Copy className="w-3 h-3" />
                    Copy All
                  </button>
                </div>
                
                <div className="bg-slate-900/50 rounded-xl p-6 border border-slate-700">
                  <div className="text-slate-300 whitespace-pre-wrap text-sm leading-relaxed font-mono max-h-[600px] overflow-y-auto">
                    {fullProfile || "No profile data available"}
                  </div>
                </div>
              </div>
            )}

          </div>
        </div>

        <div className="p-6 border-t border-slate-700 bg-slate-900/50 flex-shrink-0">
          <div className="flex items-center justify-between">
            <div className="text-sm text-slate-400">
              <p>Enrichment: <span className="text-cyan-400 font-medium">{contact.enrichment_status || 'pending'}</span> • Last Updated: {contact.enrichment_date || 'Never'}</p>
              <p>Profile: {fullProfile.length.toLocaleString()} chars • Generated: {enrichmentData.enriched_at || 'Unknown'}</p>
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
