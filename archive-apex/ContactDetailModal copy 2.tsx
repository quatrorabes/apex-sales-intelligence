// ContactDetailModal.tsx
// Complete contact detail view with enriched data display

import React, { useState, useEffect } from 'react';
import { 
  X, User, Building, Mail, Phone, Globe, Calendar, 
  Brain, Target, DollarSign, Lightbulb, FileText, 
  TrendingUp, CheckCircle, AlertCircle, Loader,
  ChevronDown, ChevronUp, Copy, ExternalLink
} from 'lucide-react';

interface Contact {
  id: number;
  name: string;
  email: string;
  company: string;
  title: string;
  phone?: string;
  linkedin_url?: string;
  enrichment_status?: string;
  enrichment_data?: string;
  perplexity_data?: string;
  priority_score?: number;
  rss_score?: number;
  mdcp_score?: number;
  created_at?: string;
  enriched_at?: string;
  last_activity?: string;
}

interface ContactDetailModalProps {
  contact: Contact;
  onClose: () => void;
  onUpdate: () => void;
}

const ContactDetailModal: React.FC<ContactDetailModalProps> = ({ 
  contact, 
  onClose, 
  onUpdate 
}) => {
  const [activeTab, setActiveTab] = useState('overview');
  const [enrichmentData, setEnrichmentData] = useState<any>(null);
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({
    painPoints: false,
    sbaInterest: false,
    keyInsights: false,
    companyProfile: false,
    personProfile: false
  });
  const [enriching, setEnriching] = useState(false);
  const [copiedField, setCopiedField] = useState<string | null>(null);

  useEffect(() => {
    // Parse enrichment data on load
    if (contact.enrichment_data) {
      try {
        const data = JSON.parse(contact.enrichment_data);
        setEnrichmentData(data);
        console.log('Parsed enrichment data:', data);
      } catch (e) {
        console.error('Failed to parse enrichment data:', e);
      }
    }
  }, [contact]);

  const handleEnrich = async () => {
    setEnriching(true);
    try {
      const response = await fetch(`http://localhost:8000/api/contacts/${contact.id}/enrich`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ force: false })
      });
      
      const result = await response.json();
      
      if (result.success) {
        alert(`✅ Enhanced enrichment complete!\n\nProfile size: ${result.data_size?.toLocaleString()} characters\nNew Priority Score: ${result.scores?.priority_score?.toFixed(0) || 'N/A'}`);
        onUpdate();
        
        // Reload enrichment data
        const updatedResponse = await fetch(`http://localhost:8000/api/contacts/${contact.id}`);
        const updatedContact = await updatedResponse.json();
        if (updatedContact.enrichment_data) {
          setEnrichmentData(JSON.parse(updatedContact.enrichment_data));
        }
      } else {
        alert(`❌ Enrichment failed: ${result.error || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Enrichment error:', error);
      alert('❌ Failed to enrich contact');
    } finally {
      setEnriching(false);
    }
  };

  const copyToClipboard = (text: string, field: string) => {
    navigator.clipboard.writeText(text);
    setCopiedField(field);
    setTimeout(() => setCopiedField(null), 2000);
  };

  const toggleSection = (section: string) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  const extractStrategicSections = () => {
    if (!enrichmentData?.perplexity_insights && !enrichmentData?.full_profile_text) {
      return { painPoints: '', sbaInterest: '', keyInsights: '', company: '', person: '' };
    }

    const fullText = enrichmentData.perplexity_insights || enrichmentData.full_profile_text || '';
    
    // Try to extract sections based on headers
    const sections: any = {};
    
    // Extract pain points
    const painPointsMatch = fullText.match(/PAIN POINTS[:\s]+([\s\S]*?)(?=SBA|KEY|$)/i);
    sections.painPoints = painPointsMatch ? painPointsMatch[1].trim() : '';
    
    // Extract SBA interest
    const sbaMatch = fullText.match(/SBA.*?INTEREST[:\s]+([\s\S]*?)(?=KEY|PAIN|$)/i);
    sections.sbaInterest = sbaMatch ? sbaMatch[1].trim() : '';
    
    // Extract key insights
    const insightsMatch = fullText.match(/KEY INSIGHTS[:\s]+([\s\S]*?)(?=PAIN|SBA|$)/i);
    sections.keyInsights = insightsMatch ? insightsMatch[1].trim() : '';
    
    // Extract company profile
    const companyMatch = fullText.match(/COMPANY PROFILE[:\s]+([\s\S]*?)(?=PERSON|STRATEGIC|$)/i);
    sections.company = companyMatch ? companyMatch[1].trim() : '';
    
    // Extract person profile  
    const personMatch = fullText.match(/PERSON PROFILE[:\s]+([\s\S]*?)(?=COMPANY|STRATEGIC|$)/i);
    sections.person = personMatch ? personMatch[1].trim() : '';
    
    return sections;
  };

  const sections = extractStrategicSections();
  const isPeer = ['broker', 'principal', 'ccim', 'banker', 'lender'].some(
    term => (contact.title || '').toLowerCase().includes(term)
  );

  const renderOverviewTab = () => (
    <div className="space-y-4">
      {/* Basic Information Card */}
      <div className="bg-white rounded-lg p-6 shadow-sm">
        <h3 className="text-lg font-semibold mb-4 flex items-center">
          <User className="w-5 h-5 mr-2 text-blue-600" />
          Contact Information
        </h3>
        
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-3">
            <div>
              <label className="text-xs text-gray-500 uppercase tracking-wider">Name</label>
              <div className="flex items-center mt-1">
                <p className="text-sm font-medium">{contact.name}</p>
                <button
                  onClick={() => copyToClipboard(contact.name, 'name')}
                  className="ml-2 text-gray-400 hover:text-gray-600"
                >
                  {copiedField === 'name' ? (
                    <CheckCircle className="w-4 h-4 text-green-500" />
                  ) : (
                    <Copy className="w-4 h-4" />
                  )}
                </button>
              </div>
            </div>
            
            <div>
              <label className="text-xs text-gray-500 uppercase tracking-wider">Title</label>
              <p className="text-sm font-medium mt-1">{contact.title || 'Not specified'}</p>
            </div>
            
            <div>
              <label className="text-xs text-gray-500 uppercase tracking-wider">Email</label>
              <div className="flex items-center mt-1">
                <a href={`mailto:${contact.email}`} className="text-sm text-blue-600 hover:underline">
                  {contact.email}
                </a>
                <button
                  onClick={() => copyToClipboard(contact.email, 'email')}
                  className="ml-2 text-gray-400 hover:text-gray-600"
                >
                  {copiedField === 'email' ? (
                    <CheckCircle className="w-4 h-4 text-green-500" />
                  ) : (
                    <Copy className="w-4 h-4" />
                  )}
                </button>
              </div>
            </div>
          </div>
          
          <div className="space-y-3">
            <div>
              <label className="text-xs text-gray-500 uppercase tracking-wider">Company</label>
              <p className="text-sm font-medium mt-1">{contact.company || 'Not specified'}</p>
            </div>
            
            <div>
              <label className="text-xs text-gray-500 uppercase tracking-wider">Phone</label>
              <div className="flex items-center mt-1">
                {contact.phone ? (
                  <>
                    <a href={`tel:${contact.phone}`} className="text-sm text-blue-600 hover:underline">
                      {contact.phone}
                    </a>
                    <button
                      onClick={() => copyToClipboard(contact.phone!, 'phone')}
                      className="ml-2 text-gray-400 hover:text-gray-600"
                    >
                      {copiedField === 'phone' ? (
                        <CheckCircle className="w-4 h-4 text-green-500" />
                      ) : (
                        <Copy className="w-4 h-4" />
                      )}
                    </button>
                  </>
                ) : (
                  <span className="text-sm text-gray-400">Not specified</span>
                )}
              </div>
            </div>
            
            <div>
              <label className="text-xs text-gray-500 uppercase tracking-wider">Type</label>
              <p className="text-sm font-medium mt-1">
                {isPeer ? (
                  <span className="text-purple-600">🤝 Industry Peer / Referral Partner</span>
                ) : (
                  <span className="text-green-600">🎯 Prospect / Potential Client</span>
                )}
              </p>
            </div>
          </div>
        </div>
        
        {contact.linkedin_url && (
          <div className="mt-4 pt-4 border-t">
            <a 
              href={contact.linkedin_url} 
              target="_blank" 
              rel="noopener noreferrer"
              className="inline-flex items-center text-sm text-blue-600 hover:underline"
            >
              <Globe className="w-4 h-4 mr-1" />
              View LinkedIn Profile
              <ExternalLink className="w-3 h-3 ml-1" />
            </a>
          </div>
        )}
      </div>

      {/* Enrichment Status Card */}
      <div className="bg-white rounded-lg p-6 shadow-sm">
        <h3 className="text-lg font-semibold mb-4 flex items-center">
          <Brain className="w-5 h-5 mr-2 text-purple-600" />
          Intelligence Status
        </h3>
        
        <div className="flex items-center justify-between mb-4">
          <div>
            <p className="text-sm text-gray-600">Enrichment Status</p>
            <span className={`inline-block mt-1 px-3 py-1 rounded-full text-xs font-medium ${
              contact.enrichment_status === 'complete'
                ? 'bg-green-100 text-green-800'
                : 'bg-gray-100 text-gray-800'
            }`}>
              {contact.enrichment_status === 'complete' ? 'Complete' : 'Not Enriched'}
            </span>
          </div>
          
          {enrichmentData && (
            <div className="text-right">
              <p className="text-sm text-gray-600">Profile Size</p>
              <p className="text-lg font-semibold">
                {(enrichmentData.profile_length || 0).toLocaleString()} chars
              </p>
            </div>
          )}
        </div>
        
        {contact.enriched_at && (
          <p className="text-xs text-gray-500 mb-4">
            Last enriched: {new Date(contact.enriched_at).toLocaleDateString()}
          </p>
        )}
        
        <button
          onClick={handleEnrich}
          disabled={enriching}
          className={`w-full py-2 px-4 rounded-lg font-medium transition-colors ${
            enriching 
              ? 'bg-gray-300 cursor-not-allowed' 
              : 'bg-gradient-to-r from-purple-600 to-blue-600 text-white hover:from-purple-700 hover:to-blue-700'
          }`}
        >
          {enriching ? (
            <span className="flex items-center justify-center">
              <Loader className="w-4 h-4 mr-2 animate-spin" />
              Enriching...
            </span>
          ) : (
            <span className="flex items-center justify-center">
              <Brain className="w-4 h-4 mr-2" />
              {contact.enrichment_status === 'complete' ? 'Re-enrich Contact' : 'Enrich with Intelligence'}
            </span>
          )}
        </button>
      </div>

      {/* Scoring Card */}
      {contact.priority_score !== null && contact.priority_score !== undefined && (
        <div className="bg-white rounded-lg p-6 shadow-sm">
          <h3 className="text-lg font-semibold mb-4 flex items-center">
            <TrendingUp className="w-5 h-5 mr-2 text-green-600" />
            Scoring Analysis
          </h3>
          
          <div className="grid grid-cols-3 gap-4">
            <div className="text-center">
              <p className="text-3xl font-bold text-purple-600">
                {Math.round(contact.priority_score || 0)}
              </p>
              <p className="text-xs text-gray-600 mt-1">Priority Score</p>
            </div>
            <div className="text-center">
              <p className="text-3xl font-bold text-blue-600">
                {Math.round(contact.rss_score || 0)}
              </p>
              <p className="text-xs text-gray-600 mt-1">Role Score</p>
            </div>
            <div className="text-center">
              <p className="text-3xl font-bold text-green-600">
                {Math.round(contact.mdcp_score || 0)}
              </p>
              <p className="text-xs text-gray-600 mt-1">Data Score</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );

  const renderIntelligenceTab = () => (
    <div className="space-y-4">
      {enrichmentData ? (
        <>
          {/* Strategic Intelligence Sections */}
          {sections.painPoints && (
            <div className="bg-white rounded-lg shadow-sm">
              <button
                onClick={() => toggleSection('painPoints')}
                className="w-full p-6 flex items-center justify-between hover:bg-gray-50 transition-colors"
              >
                <h3 className="text-lg font-semibold flex items-center">
                  <Target className="w-5 h-5 mr-2 text-red-600" />
                  Pain Points Analysis
                </h3>
                {expandedSections.painPoints ? (
                  <ChevronUp className="w-5 h-5 text-gray-400" />
                ) : (
                  <ChevronDown className="w-5 h-5 text-gray-400" />
                )}
              </button>
              
              {expandedSections.painPoints && (
                <div className="px-6 pb-6">
                  <div className="bg-red-50 rounded-lg p-4">
                    <pre className="text-sm text-gray-700 whitespace-pre-wrap font-sans">
                      {sections.painPoints}
                    </pre>
                  </div>
                </div>
              )}
            </div>
          )}

          {sections.sbaInterest && (
            <div className="bg-white rounded-lg shadow-sm">
              <button
                onClick={() => toggleSection('sbaInterest')}
                className="w-full p-6 flex items-center justify-between hover:bg-gray-50 transition-colors"
              >
                <h3 className="text-lg font-semibold flex items-center">
                  <DollarSign className="w-5 h-5 mr-2 text-green-600" />
                  SBA Financing Interest Points
                </h3>
                {expandedSections.sbaInterest ? (
                  <ChevronUp className="w-5 h-5 text-gray-400" />
                ) : (
                  <ChevronDown className="w-5 h-5 text-gray-400" />
                )}
              </button>
              
              {expandedSections.sbaInterest && (
                <div className="px-6 pb-6">
                  <div className="bg-green-50 rounded-lg p-4">
                    <pre className="text-sm text-gray-700 whitespace-pre-wrap font-sans">
                      {sections.sbaInterest}
                    </pre>
                  </div>
                </div>
              )}
            </div>
          )}

          {sections.keyInsights && (
            <div className="bg-white rounded-lg shadow-sm">
              <button
                onClick={() => toggleSection('keyInsights')}
                className="w-full p-6 flex items-center justify-between hover:bg-gray-50 transition-colors"
              >
                <h3 className="text-lg font-semibold flex items-center">
                  <Lightbulb className="w-5 h-5 mr-2 text-yellow-600" />
                  Key Conversation Insights
                </h3>
                {expandedSections.keyInsights ? (
                  <ChevronUp className="w-5 h-5 text-gray-400" />
                ) : (
                  <ChevronDown className="w-5 h-5 text-gray-400" />
                )}
              </button>
              
              {expandedSections.keyInsights && (
                <div className="px-6 pb-6">
                  <div className="bg-yellow-50 rounded-lg p-4">
                    <pre className="text-sm text-gray-700 whitespace-pre-wrap font-sans">
                      {sections.keyInsights}
                    </pre>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Full Profile */}
          <div className="bg-white rounded-lg shadow-sm">
            <button
              onClick={() => toggleSection('fullProfile')}
              className="w-full p-6 flex items-center justify-between hover:bg-gray-50 transition-colors"
            >
              <h3 className="text-lg font-semibold flex items-center">
                <FileText className="w-5 h-5 mr-2 text-blue-600" />
                Complete Intelligence Profile
              </h3>
              {expandedSections.fullProfile ? (
                <ChevronUp className="w-5 h-5 text-gray-400" />
              ) : (
                <ChevronDown className="w-5 h-5 text-gray-400" />
              )}
            </button>
            
            {expandedSections.fullProfile && (
              <div className="px-6 pb-6">
                <div className="bg-gray-50 rounded-lg p-4 max-h-96 overflow-y-auto">
                  <pre className="text-xs text-gray-700 whitespace-pre-wrap font-mono">
                    {enrichmentData.full_profile_text || enrichmentData.perplexity_insights || 'No profile data'}
                  </pre>
                </div>
              </div>
            )}
          </div>
        </>
      ) : (
        <div className="bg-white rounded-lg p-12 text-center">
          <Brain className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-500 mb-4">No intelligence data available</p>
          <button
            onClick={handleEnrich}
            className="py-2 px-6 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
          >
            Enrich Contact Now
          </button>
        </div>
      )}
    </div>
  );

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-5xl max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="bg-gradient-to-r from-purple-600 to-blue-600 text-white p-6 rounded-t-xl">
          <div className="flex justify-between items-start">
            <div>
              <h2 className="text-2xl font-bold mb-1">{contact.name}</h2>
              <p className="text-purple-100">
                {contact.title} at {contact.company}
              </p>
            </div>
            <button
              onClick={onClose}
              className="text-white hover:bg-white/20 p-2 rounded-lg transition-colors"
            >
              <X className="w-6 h-6" />
            </button>
          </div>
        </div>

        {/* Tabs */}
        <div className="bg-gray-50 border-b">
          <div className="flex">
            <button
              onClick={() => setActiveTab('overview')}
              className={`flex-1 py-3 px-4 font-medium transition-colors ${
                activeTab === 'overview'
                  ? 'bg-white text-purple-600 border-b-2 border-purple-600'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              Overview
            </button>
            <button
              onClick={() => setActiveTab('intelligence')}
              className={`flex-1 py-3 px-4 font-medium transition-colors ${
                activeTab === 'intelligence'
                  ? 'bg-white text-purple-600 border-b-2 border-purple-600'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              Intelligence
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6 bg-gray-50">
          {activeTab === 'overview' && renderOverviewTab()}
          {activeTab === 'intelligence' && renderIntelligenceTab()}
        </div>
      </div>
    </div>
  );
};

export default ContactDetailModal;
