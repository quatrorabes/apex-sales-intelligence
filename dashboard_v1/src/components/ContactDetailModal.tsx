import React, { useState } from "react";
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
  TrendingUp,
  Users,
  Linkedin,
  Globe
} from "lucide-react";

interface ContactEnrichmentViewProps {
  contact: any;
  onClose: () => void;
}

export default function ContactEnrichmentView({
  contact,
  onClose,
}: ContactEnrichmentViewProps) {
  const [activeTab, setActiveTab] = useState('overview');
  
  // Parse enrichment data
  let enrichmentData: any = {};
  let fullProfile: string = "";

  try {
    if (contact.dashboard) {
      enrichmentData = contact.dashboard;
    } else if (contact.enrichment_data) {
      if (typeof contact.enrichment_data === "string") {
        enrichmentData = JSON.parse(contact.enrichment_data);
      } else {
        enrichmentData = contact.enrichment_data;
      }
    }
    
    // Get the full profile text
    fullProfile = enrichmentData.full_profile_text || enrichmentData.perplexity_insights || "";
    
  } catch (error) {
    console.error("Failed to parse enrichment data:", error);
  }

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    alert("Copied to clipboard!");
  };

  // Extract sections from the full profile
  const extractSection = (startPattern: string, endPattern?: string) => {
    const startIndex = fullProfile.indexOf(startPattern);
    if (startIndex === -1) return "";
    
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
                {contact.name} @ {contact.company || "Gantry"}
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

            {/* Overview Tab - Contact Info */}
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
                        <p className="text-lg text-white">Principal at Gantry, Inc.</p>
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
                          {contact.email || "abratt@gantryinc.com"}
                        </a>
                      </div>
                      
                      <div>
                        <p className="text-sm text-slate-400 mb-1">Phone</p>
                        <p className="text-lg text-white flex items-center gap-2">
                          <Phone className="w-4 h-4" />
                          {contact.phone || "+1 949-356-6678"}
                        </p>
                      </div>
                      
                      <div>
                        <p className="text-sm text-slate-400 mb-1">LinkedIn</p>
                        <a 
                          href={contact.linkedin_url || "#"}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-lg text-cyan-400 hover:text-cyan-300 flex items-center gap-2"
                        >
                          <Linkedin className="w-4 h-4" />
                          View Profile
                        </a>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Quick Stats */}
                <div className="grid grid-cols-4 gap-4">
                  <div className="bg-slate-900/50 rounded-xl p-4 border border-slate-700">
                    <p className="text-xs text-slate-400 mb-1">Personality</p>
                    <p className="text-2xl font-bold text-purple-400">ENTJ</p>
                  </div>
                  <div className="bg-slate-900/50 rounded-xl p-4 border border-slate-700">
                    <p className="text-xs text-slate-400 mb-1">MDCP Score</p>
                    <p className="text-2xl font-bold text-cyan-400">{contact.mdcp_score || "41.25"}</p>
                  </div>
                  <div className="bg-slate-900/50 rounded-xl p-4 border border-slate-700">
                    <p className="text-xs text-slate-400 mb-1">Priority</p>
                    <p className="text-2xl font-bold text-green-400">HIGH</p>
                  </div>
                  <div className="bg-slate-900/50 rounded-xl p-4 border border-slate-700">
                    <p className="text-xs text-slate-400 mb-1">Data Quality</p>
                    <p className="text-2xl font-bold text-yellow-400">95%</p>
                  </div>
                </div>
              </div>
            )}

            {/* Company Tab */}
            {activeTab === 'company' && (
              <div className="space-y-6 max-h-[70vh] overflow-y-auto">
                <div className="bg-slate-900/50 rounded-xl p-6 border border-slate-700">
                  <h3 className="text-xl font-medium text-cyan-400 mb-4">Company Profile: Gantry</h3>
                  <div className="text-slate-300 whitespace-pre-wrap text-sm leading-relaxed">
                    {extractSection("**Company Profile: Gantry**", "**Individual Profile:")}
                  </div>
                </div>
              </div>
            )}

            {/* Individual Profile Tab */}
            {activeTab === 'person' && (
              <div className="space-y-6 max-h-[70vh] overflow-y-auto">
                <div className="bg-slate-900/50 rounded-xl p-6 border border-slate-700">
                  <h3 className="text-xl font-medium text-cyan-400 mb-4">Individual Profile: Andy Bratt</h3>
                  <div className="text-slate-300 whitespace-pre-wrap text-sm leading-relaxed">
                    {extractSection("**Individual Profile: Andy Bratt", "**Pain Points:")}
                  </div>
                </div>
              </div>
            )}

            {/* Personality Tab */}
            {activeTab === 'personality' && (
              <div className="space-y-6 max-h-[70vh] overflow-y-auto">
                {/* Myers-Briggs Assessment */}
                <div className="bg-slate-900/50 rounded-xl p-6 border border-slate-700">
                  <h3 className="text-xl font-medium text-purple-400 mb-4 flex items-center gap-2">
                    <Brain className="w-5 h-5" />
                    Personality Assessment
                  </h3>
                  <div className="text-slate-300 whitespace-pre-wrap text-sm leading-relaxed">
                    {extractSection("### 6. Personality Detail", "### 8. Sales Opportunity")}
                  </div>
                </div>

                {/* AI Score Reasoning */}
                <div className="bg-slate-900/50 rounded-xl p-6 border border-slate-700">
                  <h3 className="text-lg font-medium text-purple-400 mb-4">AI Score Reasoning</h3>
                  <div className="text-slate-300 whitespace-pre-wrap text-sm leading-relaxed">
                    {extractSection("**AI Score Reasoning:**", "**Relationship Tips:")}
                  </div>
                </div>

                {/* Relationship Tips */}
                <div className="bg-slate-900/50 rounded-xl p-6 border border-slate-700">
                  <h3 className="text-lg font-medium text-purple-400 mb-4">Relationship Tips</h3>
                  <div className="text-slate-300 whitespace-pre-wrap text-sm leading-relaxed">
                    {extractSection("**Relationship Tips:", "**Pain Points:")}
                  </div>
                </div>
              </div>
            )}

            {/* Sales Intel Tab */}
            {activeTab === 'sales' && (
              <div className="space-y-6 max-h-[70vh] overflow-y-auto">
                {/* Sales Talking Points */}
                <div className="bg-slate-900/50 rounded-xl p-6 border border-slate-700">
                  <h3 className="text-lg font-medium text-green-400 mb-4">Sales Opportunity Talking Points</h3>
                  <div className="text-slate-300 whitespace-pre-wrap text-sm leading-relaxed">
                    {extractSection("### 8. Sales Opportunity", "### 9. Deals")}
                  </div>
                </div>

                {/* Deals Database */}
                <div className="bg-slate-900/50 rounded-xl p-6 border border-slate-700">
                  <h3 className="text-lg font-medium text-green-400 mb-4">Deals & Transactions</h3>
                  <div className="text-slate-300 whitespace-pre-wrap text-sm leading-relaxed">
                    {extractSection("### 9. Deals Database", "### 10. Updated")}
                  </div>
                </div>

                {/* Company News & Fun Facts */}
                <div className="bg-slate-900/50 rounded-xl p-6 border border-slate-700">
                  <h3 className="text-lg font-medium text-blue-400 mb-4">Company News & Fun Facts</h3>
                  <div className="text-slate-300 whitespace-pre-wrap text-sm leading-relaxed">
                    {extractSection("### 11. Company News", "### 12. Trigger")}
                  </div>
                </div>

                {/* Trigger Events */}
                <div className="bg-slate-900/50 rounded-xl p-6 border border-slate-700">
                  <h3 className="text-lg font-medium text-yellow-400 mb-4">Trigger Events</h3>
                  <div className="text-slate-300 whitespace-pre-wrap text-sm leading-relaxed">
                    {extractSection("### 12. Trigger Events", "### 13. Competitive")}
                  </div>
                </div>

                {/* Competitive Intelligence */}
                <div className="bg-slate-900/50 rounded-xl p-6 border border-slate-700">
                  <h3 className="text-lg font-medium text-orange-400 mb-4">Competitive Intelligence</h3>
                  <div className="text-slate-300 whitespace-pre-wrap text-sm leading-relaxed">
                    {extractSection("### 13. Competitive Intelligence", "### 14. Warm")}
                  </div>
                </div>

                {/* Warm Introduction Paths */}
                <div className="bg-slate-900/50 rounded-xl p-6 border border-slate-700">
                  <h3 className="text-lg font-medium text-green-400 mb-4">Warm Introduction Paths</h3>
                  <div className="text-slate-300 whitespace-pre-wrap text-sm leading-relaxed">
                    {extractSection("### 14. Warm Introduction", "### 15. Engagement")}
                  </div>
                </div>

                {/* Engagement Preferences */}
                <div className="bg-slate-900/50 rounded-xl p-6 border border-slate-700">
                  <h3 className="text-lg font-medium text-cyan-400 mb-4">Engagement Preferences</h3>
                  <div className="text-slate-300 whitespace-pre-wrap text-sm leading-relaxed">
                    {extractSection("### 15. Engagement Preferences", "### 16. Decision")}
                  </div>
                </div>

                {/* Decision Making Style */}
                <div className="bg-slate-900/50 rounded-xl p-6 border border-slate-700">
                  <h3 className="text-lg font-medium text-blue-400 mb-4">Decision Making Style</h3>
                  <div className="text-slate-300 whitespace-pre-wrap text-sm leading-relaxed">
                    {extractSection("### 16. Decision Making", "### 17. Budget")}
                  </div>
                </div>

                {/* Budget Authority */}
                <div className="bg-slate-900/50 rounded-xl p-6 border border-slate-700">
                  <h3 className="text-lg font-medium text-green-400 mb-4">Budget Authority</h3>
                  <div className="text-slate-300 whitespace-pre-wrap text-sm leading-relaxed">
                    {extractSection("### 17. Budget Authority", "### 18. Success")}
                  </div>
                </div>

                {/* Success Metrics */}
                <div className="bg-slate-900/50 rounded-xl p-6 border border-slate-700">
                  <h3 className="text-lg font-medium text-purple-400 mb-4">Success Metrics</h3>
                  <div className="text-slate-300 whitespace-pre-wrap text-sm leading-relaxed">
                    {extractSection("### 18. Success Metrics", "**AI Score")}
                  </div>
                </div>

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
                {/* Outreach Approach */}
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

                {/* Generated Scripts if available */}
                {contact.generated_scripts && (
                  <div className="bg-slate-900/50 rounded-xl p-6 border border-slate-700">
                    <h3 className="flex items-center gap-2 text-lg font-medium text-purple-400 mb-4">
                      <FileText className="w-5 h-5" />
                      Generated Scripts
                    </h3>
                    <div className="space-y-4">
                      {contact.generated_scripts.email && (
                        <div>
                          <h4 className="text-sm font-medium text-slate-400 mb-2">Email Template</h4>
                          <div className="bg-slate-800 p-4 rounded text-sm text-slate-300">
                            <p className="font-medium mb-2">Subject: {contact.generated_scripts.email.subject}</p>
                            <p className="whitespace-pre-wrap">{contact.generated_scripts.email.body}</p>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                )}

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
              <p>Last Enriched: {enrichmentData.metadata?.compiled_at || new Date().toLocaleString()}</p>
              <p>Data Quality: <span className="text-green-400 font-medium">{enrichmentData.metadata?.data_quality || 'EXCELLENT'}</span> • Completeness: <span className="text-cyan-400 font-medium">{enrichmentData.metadata?.completeness_score || 95}%</span></p>
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
