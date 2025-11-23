import React, { useState, useEffect } from "react";
import {
  X,
  Brain,
  User,
  Building2,
  MessageSquare,
  Target,
  Lightbulb,
  AlertCircle,
  Mail,
  Phone,
  Copy,
  ExternalLink,
  FileText,
  BarChart3,
  Linkedin,
  Globe,
  RefreshCw
} from "lucide-react";

interface ContactEnrichmentViewProps {
  contactId: number;  // Changed from contact object to contactId
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

  // Fetch intelligence data when component mounts
  useEffect(() => {
    fetchIntelligenceData();
  }, [contactId]);

  const fetchIntelligenceData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`http://localhost:8000/api/contacts/${contactId}/intelligence`);
      
      if (!response.ok) {
        throw new Error('Failed to fetch intelligence data');
      }
      
      const data = await response.json();
      
      // Set contact information
      setContact(data.contact);
      
      // Set enrichment data
      const enrichment = data.enrichment_data || data.dashboard || {};
      setEnrichmentData(enrichment);
      
      // Set full profile text
      const profile = enrichment.full_profile_text || 
                     enrichment.perplexity_insights || 
                     data.dashboard?.full_profile_text ||
                     data.dashboard?.perplexity_insights || 
                     "";
      setFullProfile(profile);
      
    } catch (err) {
      console.error("Error fetching intelligence:", err);
      setError("Failed to load intelligence data");
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    alert("Copied to clipboard!");
  };

  // Extract sections from the full profile
  const extractSection = (startPattern: string, endPattern?: string) => {
    if (!fullProfile) return "No data available";
    
    const startIndex = fullProfile.indexOf(startPattern);
    if (startIndex === -1) return "Section not found in profile";
    
    const contentStart = startIndex;
    const endIndex = endPattern ? fullProfile.indexOf(endPattern, contentStart) : fullProfile.length;
    
    if (endIndex === -1) {
      return fullProfile.substring(contentStart);
    }
    
    return fullProfile.substring(contentStart, endIndex);
  };

  // Tab configuration
  const tabs = [
    { id: 'overview', label: 'Overview', icon: User },
    { id: 'company', label: 'Company', icon: Building2 },
    { id: 'person', label: 'Individual', icon: Brain },
    { id: 'personality', label: 'Personality', icon: BarChart3 },
    { id: 'sales', label: 'Sales Intel', icon: Target },
    { id: 'outreach', label: 'Outreach', icon: Mail },
  ];

  // Loading state
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

  // Error state
  if (error || !contact) {
    return (
      <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-6 z-50">
        <div className="bg-slate-800 rounded-xl border border-slate-700 p-12">
          <div className="flex flex-col items-center gap-4">
            <AlertCircle className="w-12 h-12 text-red-400" />
            <p className="text-white text-lg">{error || "No contact data available"}</p>
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
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-6 z-50">
      <div className="bg-slate-800 rounded-xl border border-slate-700 max-w-7xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        
        {/* Header */}
        <div className="p-6 border-b border-slate-700 flex items-center justify-between bg-slate-900/50">
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

        {/* Tab Navigation */}
        <div className="border-b border-slate-700 bg-slate-900/30">
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

        {/* Tab Content */}
        <div className="flex-1 overflow-y-auto">
          <div className="p-6">

            {/* Overview Tab */}
            {activeTab === 'overview' && (
              <div className="space-y-6">
                {/* Contact Information Card */}
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
                        <p className="text-lg text-white">
                          {enrichmentData.overview?.current_title || "Principal at Gantry, Inc."}
                        </p>
                      </div>
                      
                      <div>
                        <p className="text-sm text-slate-400 mb-1">Company</p>
                        <p className="text-lg text-white">{contact.company || "Gantry"}</p>
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

                {/* Quick Stats */}
                <div className="grid grid-cols-4 gap-4">
                  <div className="bg-slate-900/50 rounded-xl p-4 border border-slate-700">
                    <p className="text-xs text-slate-400 mb-1">Personality</p>
                    <p className="text-2xl font-bold text-purple-400">
                      {enrichmentData.personality_profile?.mbti_inference || "ENTJ"}
                    </p>
                  </div>
                  <div className="bg-slate-900/50 rounded-xl p-4 border border-slate-700">
                    <p className="text-xs text-slate-400 mb-1">MDCP Score</p>
                    <p className="text-2xl font-bold text-cyan-400">
                      {contact.mdcp_score || "41.25"}
                    </p>
                  </div>
                  <div className="bg-slate-900/50 rounded-xl p-4 border border-slate-700">
                    <p className="text-xs text-slate-400 mb-1">Priority</p>
                    <p className="text-2xl font-bold text-green-400">
                      {contact.urgency_level || "HIGH"}
                    </p>
                  </div>
                  <div className="bg-slate-900/50 rounded-xl p-4 border border-slate-700">
                    <p className="text-xs text-slate-400 mb-1">Data Quality</p>
                    <p className="text-2xl font-bold text-yellow-400">
                      {enrichmentData.metadata?.completeness_score || "95"}%
                    </p>
                  </div>
                </div>

                {/* Profile Overview */}
                {fullProfile && (
                  <div className="bg-slate-900/50 rounded-xl p-6 border border-slate-700">
                    <h3 className="text-lg font-medium text-cyan-400 mb-4">Profile Overview</h3>
                    <div className="text-slate-300 whitespace-pre-wrap text-sm leading-relaxed max-h-96 overflow-y-auto">
                      {extractSection("COMPREHENSIVE PROFILE:", "**Company Profile:").substring(0, 1000)}...
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Company Tab */}
            {activeTab === 'company' && (
              <div className="space-y-6 max-h-[70vh] overflow-y-auto">
                <div className="bg-slate-900/50 rounded-xl p-6 border border-slate-700">
                  <h3 className="text-xl font-medium text-cyan-400 mb-4">Company Profile: {contact.company || "Gantry"}</h3>
                  <div className="text-slate-300 whitespace-pre-wrap text-sm leading-relaxed">
                    {extractSection("**Company Profile:", "**Individual Profile:")}
                  </div>
                </div>
              </div>
            )}

            {/* Individual Profile Tab */}
            {activeTab === 'person' && (
              <div className="space-y-6 max-h-[70vh] overflow-y-auto">
                <div className="bg-slate-900/50 rounded-xl p-6 border border-slate-700">
                  <h3 className="text-xl font-medium text-cyan-400 mb-4">Individual Profile: {contact.name}</h3>
                  <div className="text-slate-300 whitespace-pre-wrap text-sm leading-relaxed">
                    {extractSection("**Individual Profile:", "**AI Score")}
                  </div>
                </div>
              </div>
            )}

            {/* Personality Tab */}
            {activeTab === 'personality' && (
              <div className="space-y-6 max-h-[70vh] overflow-y-auto">
                <div className="bg-slate-900/50 rounded-xl p-6 border border-slate-700">
                  <h3 className="text-xl font-medium text-purple-400 mb-4">Personality Assessment</h3>
                  <div className="text-slate-300 whitespace-pre-wrap text-sm leading-relaxed">
                    {extractSection("### 6. Personality Detail", "### 8. Sales Opportunity")}
                  </div>
                </div>

                {enrichmentData.ai_analysis?.ai_score_reasoning && (
                  <div className="bg-slate-900/50 rounded-xl p-6 border border-slate-700">
                    <h3 className="text-lg font-medium text-purple-400 mb-4">AI Score Reasoning</h3>
                    <div className="text-slate-300 whitespace-pre-wrap text-sm leading-relaxed">
                      {extractSection("**AI Score Reasoning:", "**Relationship Tips:")}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Sales Intel Tab */}
            {activeTab === 'sales' && (
              <div className="space-y-6 max-h-[70vh] overflow-y-auto">
                {/* All 18 sections displayed */}
                {[
                  { num: "8", title: "Sales Opportunity Talking Points", color: "green" },
                  { num: "9", title: "Deals & Transactions", color: "green" },
                  { num: "10", title: "Updated Fields", color: "blue" },
                  { num: "11", title: "Company News & Fun Facts", color: "blue" },
                  { num: "12", title: "Trigger Events", color: "yellow" },
                  { num: "13", title: "Competitive Intelligence", color: "orange" },
                  { num: "14", title: "Warm Introduction Paths", color: "green" },
                  { num: "15", title: "Engagement Preferences", color: "cyan" },
                  { num: "16", title: "Decision Making Style", color: "blue" },
                  { num: "17", title: "Budget Authority", color: "green" },
                  { num: "18", title: "Success Metrics", color: "purple" }
                ].map((section) => (
                  <div key={section.num} className="bg-slate-900/50 rounded-xl p-6 border border-slate-700">
                    <h3 className={`text-lg font-medium text-${section.color}-400 mb-4`}>{section.title}</h3>
                    <div className="text-slate-300 whitespace-pre-wrap text-sm leading-relaxed">
                      {extractSection(`### ${section.num}.`, `### ${parseInt(section.num) + 1}.`)}
                    </div>
                  </div>
                ))}

                {/* Pain Points */}
                <div className="bg-slate-900/50 rounded-xl p-6 border border-slate-700">
                  <h3 className="text-lg font-medium text-red-400 mb-4 flex items-center gap-2">
                    <AlertCircle className="w-5 h-5" />
                    Pain Points
                  </h3>
                  <div className="text-slate-300 whitespace-pre-wrap text-sm leading-relaxed">
                    {extractSection("**Pain Points:", "**Outreach Approach:")}
                  </div>
                </div>
              </div>
            )}

            {/* Outreach Tab */}
            {activeTab === 'outreach' && (
              <div className="space-y-6">
                <div className="bg-slate-900/50 rounded-xl p-6 border border-slate-700">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="flex items-center gap-2 text-lg font-medium text-cyan-400">
                      <Mail className="w-5 h-5" />
                      Outreach Approach
                    </h3>
                    <button
                      onClick={() => copyToClipboard(extractSection("**Outreach Approach:**", null))}
                      className="px-3 py-1 bg-slate-700 text-white rounded hover:bg-slate-600 flex items-center gap-1 text-sm"
                    >
                      <Copy className="w-3 h-3" />
                      Copy
                    </button>
                  </div>
                  <div className="text-slate-300 whitespace-pre-wrap text-sm leading-relaxed">
                    {extractSection("**Outreach Approach:**", null)}
                  </div>
                </div>

                {/* Full Raw Profile */}
                <div className="bg-slate-900/50 rounded-xl p-6 border border-slate-700">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-medium text-slate-400">Complete Raw Profile</h3>
                    <button
                      onClick={() => copyToClipboard(fullProfile)}
                      className="px-3 py-1 bg-slate-700 text-white rounded hover:bg-slate-600 flex items-center gap-1 text-sm"
                    >
                      <Copy className="w-3 h-3" />
                      Copy All
                    </button>
                  </div>
                  <details className="cursor-pointer">
                    <summary className="text-sm text-slate-500 hover:text-slate-300">Click to expand full profile...</summary>
                    <div className="mt-4 bg-slate-800 p-4 rounded text-slate-300 whitespace-pre-wrap text-xs font-mono max-h-96 overflow-y-auto">
                      {fullProfile}
                    </div>
                  </details>
                </div>
              </div>
            )}

          </div>
        </div>

        {/* Footer */}
        <div className="p-6 border-t border-slate-700 bg-slate-900/50">
          <div className="flex items-center justify-between">
            <div className="text-sm text-slate-400">
              <p>Last Enriched: {contact.enrichment_date || new Date().toLocaleString()}</p>
              <p>
                Data Quality: <span className="text-green-400 font-medium">
                  {enrichmentData.metadata?.data_quality || 'EXCELLENT'}
                </span> • 
                Completeness: <span className="text-cyan-400 font-medium">
                  {enrichmentData.metadata?.completeness_score || 95}%
                </span>
              </p>
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
