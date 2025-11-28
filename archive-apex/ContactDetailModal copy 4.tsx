import React, { useState, useEffect } from 'react';
import { X, Mail, Phone, Building2, Briefcase, Copy, Check, Sparkles, TrendingUp, Target, Brain, MessageSquare, Lightbulb } from 'lucide-react';
import './ContactDetailModal.css';
import ContentGenerator from './ContentGenerator';


interface ParsedIntelligence {
  overview: string;
  background: string[];
  education: string;
  recentMentions: string[];
  socialProfiles: string;
  personalityDetail: string;
  mbtiAssessment: string;
  mbtiType: string;
  salesTalkingPoints: string[];
  companyOverview: string;
  companyProducts: string;
  companyLeadership: string;
  companyMarket: string;
  companyNews: string;
  companyFunFacts: string[];
  companyFullProfile: string;
  painPoints: string[];
  sbaInterests: string[];
  keyInsights: string[];
}

interface ContactDetailModalProps {
  contact: Contact;
  onClose: () => void;
  onEnrich?: (contactId: number) => void;
}

type TabId = 'overview' | 'personal' | 'company' | 'personality' | 'chat' | 'content';

interface ParsedIntelligence {
  // Personal sections
  overview: string;
  background: string[];
  education: string[];
  recent_mentions: string[];
  sales_talking_points: string[];
  
  // Company profile - ENTIRE section
  company_full_profile: string;
  
  // Personality
  personality_detail: string;
  mbti_assessment: string;
  mbti_type: string;
  
  // Strategic Intelligence (Chat Things)
  pain_points: string[];
  sba_interests: string[];
  key_insights: string[];
}

export default function ContactDetailModal({ contact, onClose, onEnrich }: ContactDetailModalProps) {
  const [activeTab, setActiveTab] = useState<TabId>('overview');
  const [copiedField, setCopiedField] = useState<string | null>(null);
  const [parsedData, setParsedData] = useState<ParsedIntelligence | null>(null);
  const [isEnriching, setIsEnriching] = useState(false);

  useEffect(() => {
    if (contact.profile_content) {
      const parsed = parseEnrichedProfile(contact.profile_content);
      setParsedData(parsed);
    }
  }, [contact.profile_content]);

  // ContactDetailModal.tsx - FIXED parseEnrichedProfile function
  // Replace your existing parseEnrichedProfile function with this one
  
  interface ParsedIntelligence {
    // Personal sections (PROFESSIONAL PROFILE)
    overview: string;
    background: string[];
    education: string;
    recentMentions: string[];
    socialProfiles: string;
    personalityDetail: string;
    mbtiAssessment: string;
    mbtiType: string;
    salesTalkingPoints: string[];
    
    // Company sections (CORPORATE PROFILE)
    companyOverview: string;
    companyProducts: string;
    companyLeadership: string;
    companyMarket: string;
    companyNews: string;
    companyFunFacts: string[];
    companyFullProfile: string;
    
    // Strategic Intelligence
    painPoints: string[];
    sbaInterests: string[];
    keyInsights: string[];
  }
  
  const parseEnrichedProfile = (text: string): ParsedIntelligence => {
    const sections: ParsedIntelligence = {
      overview: '',
      background: [],
      education: '',
      recentMentions: [],
      socialProfiles: '',
      personalityDetail: '',
      mbtiAssessment: '',
      mbtiType: '',
      salesTalkingPoints: [],
      companyOverview: '',
      companyProducts: '',
      companyLeadership: '',
      companyMarket: '',
      companyNews: '',
      companyFunFacts: [],
      companyFullProfile: '',
      painPoints: [],
      sbaInterests: [],
      keyInsights: [],
    };
    
    if (!text) return sections;
    
    // Helper to clean text
    const cleanText = (str: string): string =>
      str.replace(/\*\*/g, '').replace(/\*/g, '').replace(/^#+\s*/gm, '').trim();
    
    // Helper to extract bullets from a section
    const extractBullets = (content: string): string[] => {
      const bullets = content.match(/^\s*[-•]\s*.+$/gm);
      if (bullets) {
        return bullets.map(b => cleanText(b.replace(/^\s*[-•]\s*/, '')));
      }
      return [];
    };
    
    // ========== PROFESSIONAL PROFILE SECTIONS ==========
    
    // 1. Overview (Person)
    const overviewMatch = text.match(/1\.\s*Overview[\s\S]*?(?=2\.\s*Background|$)/i);
    if (overviewMatch) {
      sections.overview = cleanText(overviewMatch[0].replace(/1\.\s*Overview/i, ''));
    }
    
    // 2. Background
    const backgroundMatch = text.match(/2\.\s*Background[\s\S]*?(?=3\.\s*Education|$)/i);
    if (backgroundMatch) {
      sections.background = extractBullets(backgroundMatch[0]);
      if (sections.background?.length === 0) {
        sections.background = [cleanText(backgroundMatch[0].replace(/2\.\s*Background/i, ''))];
      }
    }
    
    // 3. Education
    const educationMatch = text.match(/3\.\s*Education[\s\S]*?(?=4\.\s*Recent|$)/i);
    if (educationMatch) {
      sections.education = cleanText(educationMatch[0].replace(/3\.\s*Education/i, ''));
    }
    
    // 4. Recent Mentions
    const recentMatch = text.match(/4\.\s*Recent Mentions[\s\S]*?(?=5\.\s*Social|$)/i);
    if (recentMatch) {
      sections.recentMentions = extractBullets(recentMatch[0]);
      if (sections.recentMentions?.length === 0) {
        sections.recentMentions = [cleanText(recentMatch[0].replace(/4\.\s*Recent Mentions/i, ''))];
      }
    }
    
    // 5. Social Profiles
    const socialMatch = text.match(/5\.\s*Social Profiles[\s\S]*?(?=6\.\s*Personality|$)/i);
    if (socialMatch) {
      sections.socialProfiles = cleanText(socialMatch[0].replace(/5\.\s*Social Profiles/i, ''));
    }
    
    // 6. Personality Detail
    const personalityMatch = text.match(/6\.\s*Personality Detail[\s\S]*?(?=7\.\s*Myers|$)/i);
    if (personalityMatch) {
      sections.personalityDetail = cleanText(personalityMatch[0].replace(/6\.\s*Personality Detail/i, ''));
      // Try to extract MBTI type
      const mbtiMatch = personalityMatch[0].match(/(INTJ|INTP|ENTJ|ENTP|INFJ|INFP|ENFJ|ENFP|ISTJ|ISFJ|ESTJ|ESFJ|ISTP|ISFP|ESTP|ESFP)/i);
      if (mbtiMatch) sections.mbtiType = mbtiMatch[1].toUpperCase();
    }
    
    // 7. Myers-Briggs Assessment
    const mbtiAssessMatch = text.match(/7\.\s*Myers-Briggs[\s\S]*?(?=8\.\s*Sales|CORPORATE PROFILE|$)/i);
    if (mbtiAssessMatch) {
      sections.mbtiAssessment = cleanText(mbtiAssessMatch[0].replace(/7\.\s*Myers-Briggs[^\n]*/i, ''));
    }
    
    // 8. Sales Opportunity / Talking Points
    const salesMatch = text.match(/8\.\s*Sales Opportunity[\s\S]*?(?=CORPORATE PROFILE|------|$)/i);
    if (salesMatch) {
      sections.salesTalkingPoints = extractBullets(salesMatch[0]);
    }
    
    // ========== CORPORATE PROFILE SECTIONS ==========
    
    // Extract entire corporate profile section
    const corpProfileMatch = text.match(/CORPORATE PROFILE[\s\S]*?(?=STRATEGIC INTELLIGENCE|$)/i);
    if (corpProfileMatch) {
      sections.companyFullProfile = cleanText(corpProfileMatch[0]);
      
      // Company 1. Overview
      const compOverviewMatch = corpProfileMatch[0].match(/1\.\s*Overview[\s\S]*?(?=2\.\s*Products|$)/i);
      if (compOverviewMatch) {
        sections.companyOverview = cleanText(compOverviewMatch[0].replace(/1\.\s*Overview/i, ''));
      }
      
      // Company 2. Products/Services
      const compProductsMatch = corpProfileMatch[0].match(/2\.\s*Products[\s\S]*?(?=3\.\s*Leadership|$)/i);
      if (compProductsMatch) {
        sections.companyProducts = cleanText(compProductsMatch[0].replace(/2\.\s*Products[^\n]*/i, ''));
      }
      
      // Company 3. Leadership
      const compLeadershipMatch = corpProfileMatch[0].match(/3\.\s*Leadership[\s\S]*?(?=4\.\s*Market|$)/i);
      if (compLeadershipMatch) {
        sections.companyLeadership = cleanText(compLeadershipMatch[0].replace(/3\.\s*Leadership/i, ''));
      }
      
      // Company 4. Market/Competitors
      const compMarketMatch = corpProfileMatch[0].match(/4\.\s*Market[\s\S]*?(?=5\.\s*Recent|$)/i);
      if (compMarketMatch) {
        sections.companyMarket = cleanText(compMarketMatch[0].replace(/4\.\s*Market[^\n]*/i, ''));
      }
      
      // Company 5. Recent News
      const compNewsMatch = corpProfileMatch[0].match(/5\.\s*Recent News[\s\S]*?(?=6\.\s*Company Fun|$)/i);
      if (compNewsMatch) {
        sections.companyNews = cleanText(compNewsMatch[0].replace(/5\.\s*Recent News/i, ''));
      }
      
      // Company 6. Fun Facts
      const compFunMatch = corpProfileMatch[0].match(/6\.\s*Company Fun Facts[\s\S]*?(?=STRATEGIC|------|$)/i);
      if (compFunMatch) {
        sections.companyFunFacts = extractBullets(compFunMatch[0]);
      }
    }
    
    // ========== STRATEGIC INTELLIGENCE ==========
    
    // Pain Points
    const painMatch = text.match(/Pain Points[\s\S]*?(?=SBA Financing|$)/i);
    if (painMatch) {
      sections.painPoints = extractBullets(painMatch[0]);
    }
    
    // SBA Financing Interest
    const sbaMatch = text.match(/SBA Financing Interest[\s\S]*?(?=Key Insights|$)/i);
    if (sbaMatch) {
      sections.sbaInterests = extractBullets(sbaMatch[0]);
    }
    
    // Key Insights
    const insightsMatch = text.match(/Key Insights[\s\S]*$/i);
    if (insightsMatch) {
      sections.keyInsights = extractBullets(insightsMatch[0]);
    }
    
    return sections;
  };
  

  const copyToClipboard = async (text: string, field: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedField(field);
      setTimeout(() => setCopiedField(null), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  const handleEnrich = async () => {
    if (onEnrich && !isEnriching) {
      setIsEnriching(true);
      try {
        await onEnrich(contact.id);
      } finally {
        setIsEnriching(false);
      }
    }
  };

  const getStatusColor = (status?: string) => {
    switch (status) {
      case 'complete': return '#10b981';
      case 'pending': return '#f59e0b';
      case 'enriching': return '#3b82f6';
      default: return '#6b7280';
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return '#10b981';
    if (score >= 60) return '#f59e0b';
    return '#ef4444';
  };

  return (
    <div className="o3-modal-overlay" onClick={onClose}>
      <div className="o3-modal-container" onClick={(e) => e.stopPropagation()}>
        
        {/* HEADER - STICKY GRADIENT */}
        <div className="o3-modal-header">
          <button className="o3-close-btn" onClick={onClose}>
            <X size={20} />
          </button>

          {/* Contact Hero */}
          <div className="o3-contact-hero">
            <div className="o3-avatar">
              {contact.name.split(' ').map(n => n[0]).join('').substring(0, 2)}
            </div>
            <div className="o3-hero-info">
              <h1 className="o3-hero-name">{contact.name}</h1>
              <p className="o3-hero-title">{contact.title} at {contact.company}</p>
            </div>
          </div>

          {/* Score Pills */}
          <div className="o3-score-pills">
            <div className="o3-score-pill" style={{ '--score-color': getScoreColor(contact.mdcp_score || 0) } as React.CSSProperties}>
              <div className="o3-pill-value">{contact.mdcp_score || 0}</div>
              <div className="o3-pill-label">PRIORITY</div>
            </div>
            <div className="o3-score-pill" style={{ '--score-color': getScoreColor(contact.role_score || 0) } as React.CSSProperties}>
              <div className="o3-pill-value">{contact.role_score || 0}</div>
              <div className="o3-pill-label">ROLE</div>
            </div>
            <div className="o3-score-pill" style={{ '--score-color': getScoreColor(contact.data_score || 0) } as React.CSSProperties}>
              <div className="o3-pill-value">{contact.data_score || 0}</div>
              <div className="o3-pill-label">DATA</div>
            </div>
          </div>

          {/* Tab Navigation */}
          <div className="o3-tab-nav">
            <button 
              className={`o3-tab ${activeTab === 'overview' ? 'active' : ''}`}
              onClick={() => setActiveTab('overview')}
            >
              Overview
            </button>
            <button 
              className={`o3-tab ${activeTab === 'personal' ? 'active' : ''}`}
              onClick={() => setActiveTab('personal')}
            >
              Personal
            </button>
            <button 
              className={`o3-tab ${activeTab === 'company' ? 'active' : ''}`}
              onClick={() => setActiveTab('company')}
            >
              Company
            </button>
            <button 
              className={`o3-tab ${activeTab === 'personality' ? 'active' : ''}`}
              onClick={() => setActiveTab('personality')}
            >
              Personality
            </button>
            <button 
              className={`o3-tab ${activeTab === 'chat' ? 'active' : ''}`}
              onClick={() => setActiveTab('chat')}
            >
              Chat Things
            </button>
            <button 
              className={`o3-tab ${activeTab === 'content' ? 'active' : ''}`}
              onClick={() => setActiveTab('content')}
            >
              Content
            </button>
          </div>
        </div>

        {/* CONTENT AREA */}
        <div className="o3-modal-content">
          
          {/* Quick Stats Grid */}
          <div className="o3-stats-grid">
            {/* Contact Info Card */}
            <div className="o3-card">
              <h3 className="o3-card-title">
                <Mail size={16} />
                Contact Information
              </h3>
              <div className="o3-info-list">
                <div className="o3-info-row">
                  <span className="o3-info-label">Email</span>
                  <div className="o3-info-value-group">
                    <span className="o3-info-value">{contact.email}</span>
                    <button 
                      className="o3-copy-btn"
                      onClick={() => copyToClipboard(contact.email, 'email')}
                    >
                      {copiedField === 'email' ? <Check size={14} /> : <Copy size={14} />}
                    </button>
                  </div>
                </div>
                <div className="o3-info-row">
                  <span className="o3-info-label">Phone</span>
                  <div className="o3-info-value-group">
                    <span className="o3-info-value">{contact.phone}</span>
                    <button 
                      className="o3-copy-btn"
                      onClick={() => copyToClipboard(contact.phone, 'phone')}
                    >
                      {copiedField === 'phone' ? <Check size={14} /> : <Copy size={14} />}
                    </button>
                  </div>
                </div>
                <div className="o3-info-row">
                  <span className="o3-info-label">Company</span>
                  <span className="o3-info-value">{contact.company}</span>
                </div>
                <div className="o3-info-row">
                  <span className="o3-info-label">Title</span>
                  <span className="o3-info-value">{contact.title}</span>
                </div>
              </div>
            </div>

            {/* AI Intelligence Card */}
            <div className="o3-card">
              <h3 className="o3-card-title">
                <Sparkles size={16} />
                AI Intelligence
              </h3>
              <div className="o3-info-list">
                <div className="o3-info-row">
                  <span className="o3-info-label">Status</span>
                  <div className="o3-status-badge" style={{ '--status-color': getStatusColor(contact.enrichment_status) } as React.CSSProperties}>
                    {contact.enrichment_status || 'pending'}
                  </div>
                </div>
                <div className="o3-info-row">
                  <span className="o3-info-label">Last Enriched</span>
                  <span className="o3-info-value">
                    {contact.enriched_at ? new Date(contact.enriched_at).toLocaleDateString() : 'Never'}
                  </span>
                </div>
                <div className="o3-info-row">
                  <span className="o3-info-label">Times Enriched</span>
                  <span className="o3-info-value">{contact.times_enriched || 0}</span>
                </div>
              </div>
              <button 
                className="o3-enrich-btn"
                onClick={handleEnrich}
                disabled={isEnriching}
              >
                {isEnriching ? 'Enriching...' : 'Enrich Contact'}
              </button>
            </div>
          </div>

          {/* Tab Content */}
          <div className="o3-tab-content">
            {/* OVERVIEW TAB */}
            {activeTab === 'overview' && (
              <div className="o3-tab-panel">
                {parsedData?.overview ? (
                  <>
                    <div className="o3-content-card">
                      <h3>Professional Overview</h3>
                      <p>{parsedData.overview}</p>
                    </div>
                    
                    {parsedData.sales_talking_points?.length > 0 && (
                      <div className="o3-content-card o3-highlight-card">
                        <h3>
                          <Target size={18} />
                          Sales Talking Points
                        </h3>
                        <ul className="o3-list">
                          {parsedData.sales_talking_points.map((item, i) => (
                            <li key={i}>{item}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </>
                ) : (
                  <div className="o3-empty-state">
                    <Sparkles size={48} />
                    <p>No enrichment data available</p>
                    <button className="o3-btn-secondary" onClick={handleEnrich}>
                      Enrich Contact
                    </button>
                  </div>
                )}
              </div>
            )}

            {/* PERSONAL TAB */}
            {activeTab === 'personal' && (
              <div className="o3-tab-panel">
                {parsedData?.background?.length ? (
                  <>
                    <div className="o3-content-card">
                      <h3>Background & Experience</h3>
                      <ul className="o3-list">
                        {parsedData.background.map((item, i) => (
                          <li key={i}>{item}</li>
                        ))}
                      </ul>
                    </div>
                    
                    {parsedData.education?.length > 0 && (
                      <div className="o3-content-card">
                        <h3>Education</h3>
                        <div>
                          {parsedData.education.map((item, i) => (
                            <p key={i}>{item}</p>
                          ))}
                        </div>
                      </div>
                    )}
                    
                    {parsedData.recent_mentions?.length > 0 && (
                      <div className="o3-content-card">
                        <h3>Recent Mentions</h3>
                        <ul className="o3-list">
                          {parsedData.recent_mentions.map((item, i) => (
                            <li key={i}>{item}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </>
                ) : (
                  <div className="o3-empty-state">
                    <Brain size={48} />
                    <p>No personal data available</p>
                  </div>
                )}
              </div>
            )}

            {/* COMPANY TAB */}
            {activeTab === 'company' && (
              <div className="o3-tab-panel">
                {parsedData?.company_full_profile ? (
                  <div className="o3-content-card o3-company-card">
                    <h3>{contact.company}</h3>
                    <div className="o3-company-content">
                      {parsedData.company_full_profile}
                    </div>
                  </div>
                ) : (
                  <div className="o3-empty-state">
                    <Building2 size={48} />
                    <p>No company data available</p>
                  </div>
                )}
              </div>
            )}

            {/* PERSONALITY TAB */}
            {activeTab === 'personality' && (
              <div className="o3-tab-panel">
                {parsedData?.personality_detail || parsedData?.mbti_assessment ? (
                  <>
                    {parsedData.mbti_type && (
                      <div className="o3-mbti-badge">
                        {parsedData.mbti_type}
                      </div>
                    )}
                    
                    {parsedData.personality_detail && (
                      <div className="o3-content-card">
                        <h3>Personality Detail</h3>
                        <p>{parsedData.personality_detail}</p>
                      </div>
                    )}
                    
                    {parsedData.mbti_assessment && (
                      <div className="o3-content-card">
                        <h3>Myers-Briggs Assessment</h3>
                        <p>{parsedData.mbti_assessment}</p>
                      </div>
                    )}
                  </>
                ) : (
                  <div className="o3-empty-state">
                    <Brain size={48} />
                    <p>No personality data available</p>
                  </div>
                )}
              </div>
            )}

            {/* CHAT THINGS TAB (Strategic Intelligence) */}
            {activeTab === 'chat' && (
              <div className="o3-tab-panel">
                {parsedData?.pain_points?.length || parsedData?.sba_interests?.length || parsedData?.key_insights?.length ? (
                  <>
                    {parsedData.pain_points?.length > 0 && (
                      <div className="o3-content-card">
                        <h3>
                          <MessageSquare size={18} />
                          Pain Points
                        </h3>
                        <ul className="o3-list">
                          {parsedData.pain_points.map((item, i) => (
                            <li key={i}>{item}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                    
                    {parsedData.sba_interests?.length > 0 && (
                      <div className="o3-content-card o3-highlight-card">
                        <h3>
                          <Lightbulb size={18} />
                          SBA Financing Interests
                        </h3>
                        <ul className="o3-list">
                          {parsedData.sba_interests.map((item, i) => (
                            <li key={i}>{item}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                    
                    {parsedData.key_insights?.length > 0 && (
                      <div className="o3-content-card">
                        <h3>
                          <Target size={18} />
                          Key Insights
                        </h3>
                        <ul className="o3-list">
                          {parsedData.key_insights.map((item, i) => (
                            <li key={i}>{item}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </>
                ) : (
                  <div className="o3-empty-state">
                    <MessageSquare size={48} />
                    <p>No conversation intelligence available</p>
                  </div>
                )}
              </div>
            )}

            {/* CONTENT TAB */}
            {activeTab === 'content' && (
              <div className="o3-tab-panel">
                <ContentGenerator 
                  contactId={contact.id}
                  contactName={contact.name}
                  profileContent={contact.profile_content}
                />
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}