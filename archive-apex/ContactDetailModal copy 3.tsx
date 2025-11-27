import React, { useState, useEffect } from 'react';
import { X, Mail, Phone, Building2, Briefcase, Copy, Check, Sparkles, TrendingUp, Target, Brain, MessageSquare } from 'lucide-react';
import './ContactDetailModal.css';

interface Contact {
  id: number;
  name: string;
  email: string;
  phone: string;
  company: string;
  title: string;
  mdcp_score?: number;
  role_score?: number;
  data_score?: number;
  priority?: string;
  enrichment_status?: string;
  enriched_at?: string;
  times_enriched?: number;
  profile_content?: string;
  recommended_action?: string;
}

interface ContactDetailModalProps {
  contact: Contact;
  onClose: () => void;
  onEnrich?: (contactId: number) => void;
}

type TabId = 'overview' | 'personal' | 'company' | 'personality' | 'chat' | 'content';

interface ParsedIntelligence {
  overview: string;
  background: string[];
  education: string[];
  recent_mentions: string[];
  professional_network: string[];
  company_overview: string;
  company_products: string[];
  company_leadership: string[];
  company_news: string[];
  personality_assessment: string;
  mbti_type: string;
  key_traits: string[];
  pain_points: string[];
  sba_interests: string[];
  key_insights: string[];
  sales_talking_points: string[];
}

export default function ContactDetailModal({ contact, onClose, onEnrich }: ContactDetailModalProps) {
  const [activeTab, setActiveTab] = useState<TabId>('overview');
  const [copiedField, setCopiedField] = useState<string | null>(null);
  const [parsedData, setParsedData] = useState<ParsedIntelligence | null>(null);
  const [isEnriching, setIsEnriching] = useState(false);

  useEffect(() => {
    if (contact.profile_content) {
      const parsed = parseProfileContent(contact.profile_content);
      setParsedData(parsed);
    }
  }, [contact.profile_content]);

  const parseProfileContent = (text: string): ParsedIntelligence => {
    const sections: ParsedIntelligence = {
      overview: '',
      background: [],
      education: [],
      recent_mentions: [],
      professional_network: [],
      company_overview: '',
      company_products: [],
      company_leadership: [],
      company_news: [],
      personality_assessment: '',
      mbti_type: '',
      key_traits: [],
      pain_points: [],
      sba_interests: [],
      key_insights: [],
      sales_talking_points: []
    };

    const cleanText = (str: string) => 
      str.replace(/\*\*/g, '')
         .replace(/###?#?/g, '')
         .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
         .trim();

    // Parse sections with flexible regex patterns
    const overviewMatch = text.match(/###?\s*\d+\.?\s*Overview[^\n]*\n+(.*?)(?=###?\s*\d+\.?\s*Background|$)/is);
    if (overviewMatch) sections.overview = cleanText(overviewMatch[1]);

    const backgroundMatch = text.match(/###?\s*\d+\.?\s*Background[^\n]*\n+(.*?)(?=###?\s*\d+\.?\s*Education|$)/is);
    if (backgroundMatch) {
      sections.background = backgroundMatch[1]
        .split(/\n\s*[-•]\s*/)
        .map(s => cleanText(s))
        .filter(s => s.length > 20);
    }

    const educationMatch = text.match(/###?\s*\d+\.?\s*Education[^\n]*\n+(.*?)(?=###?\s*\d+\.?\s*Recent|$)/is);
    if (educationMatch) {
      sections.education = educationMatch[1]
        .split(/\n\s*[-•]\s*/)
        .map(s => cleanText(s))
        .filter(s => s.length > 5);
    }

    const recentMatch = text.match(/###?\s*\d+\.?\s*Recent\s+Mentions[^\n]*\n+(.*?)(?=###?\s*\d+\.?\s*Social|$)/is);
    if (recentMatch) {
      sections.recent_mentions = recentMatch[1]
        .split(/\n\s*[-•]\s*/)
        .map(s => cleanText(s))
        .filter(s => s.length > 20);
    }

    const socialMatch = text.match(/###?\s*\d+\.?\s*Social\s+Profiles[^\n]*\n+(.*?)(?=###?\s*\d+\.?\s*Personality|$)/is);
    if (socialMatch) {
      sections.professional_network = socialMatch[1]
        .split(/\n/)
        .map(s => cleanText(s))
        .filter(s => s.includes('linkedin') || s.includes('twitter') || s.includes('http'));
    }

    const personalityMatch = text.match(/###?\s*\d+\.?\s*Personality[^\n]*\n+(.*?)(?=###?\s*\d+\.?\s*Myers|###?\s*\d+\.?\s*Sales|$)/is);
    if (personalityMatch) {
      sections.personality_assessment = cleanText(personalityMatch[1]);
      const mbtiMatch = personalityMatch[1].match(/\b(INTJ|INTP|ENTJ|ENTP|INFJ|INFP|ENFJ|ENFP|ISTJ|ISFJ|ESTJ|ESFJ|ISTP|ISFP|ESTP|ESFP)\b/);
      if (mbtiMatch) sections.mbti_type = mbtiMatch[1];
    }

    const companyMatch = text.match(/CORPORATE PROFILE[^\n]*\n+.*?###?\s*\d+\.?\s*Overview[^\n]*\n+(.*?)(?=###?\s*\d+\.?\s*Products|$)/is);
    if (companyMatch) sections.company_overview = cleanText(companyMatch[1]);

    const painMatch = text.match(/###?\s*Pain\s+Points[^\n]*\n+(.*?)(?=###?\s*SBA|$)/is);
    if (painMatch) {
      sections.pain_points = painMatch[1]
        .split(/\n\s*[-•]\s*/)
        .map(s => cleanText(s))
        .filter(s => s.length > 20);
    }

    const sbaMatch = text.match(/###?\s*SBA\s+Financing[^\n]*\n+(.*?)(?=###?\s*Key\s+Insights|$)/is);
    if (sbaMatch) {
      sections.sba_interests = sbaMatch[1]
        .split(/\n\s*[-•]\s*/)
        .map(s => cleanText(s))
        .filter(s => s.length > 20);
    }

    const insightsMatch = text.match(/###?\s*Key\s+Insights[^\n]*\n+(.*?)(?=---|$)/is);
    if (insightsMatch) {
      sections.key_insights = insightsMatch[1]
        .split(/\n\s*[-•]\s*/)
        .map(s => cleanText(s))
        .filter(s => s.length > 20);
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
      case 'complete': return 'var(--success-green)';
      case 'pending': return 'var(--warning-amber)';
      case 'enriching': return 'var(--info-blue)';
      default: return 'var(--neutral-gray)';
    }
  };

  const getPriorityColor = (priority?: string) => {
    switch (priority?.toLowerCase()) {
      case 'immediate': return 'var(--danger-red)';
      case 'hot': return 'var(--success-green)';
      default: return 'var(--neutral-gray)';
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'var(--success-green)';
    if (score >= 60) return 'var(--warning-amber)';
    return 'var(--danger-red)';
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
            {activeTab === 'overview' && (
              <div className="o3-tab-panel">
                {parsedData?.overview ? (
                  <>
                    <div className="o3-content-card">
                      <h3>Professional Overview</h3>
                      <p>{parsedData.overview}</p>
                    </div>
                    {contact.recommended_action && (
                      <div className="o3-content-card o3-highlight-card">
                        <h3>
                          <Target size={18} />
                          Recommended Action
                        </h3>
                        <p>{contact.recommended_action}</p>
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

            {activeTab === 'personal' && (
              <div className="o3-tab-panel">
                {parsedData?.background.length ? (
                  <>
                    <div className="o3-content-card">
                      <h3>Background & Experience</h3>
                      <ul className="o3-list">
                        {parsedData.background.map((item, i) => (
                          <li key={i}>{item}</li>
                        ))}
                      </ul>
                    </div>
                    {parsedData.education.length > 0 && (
                      <div className="o3-content-card">
                        <h3>Education</h3>
                        <ul className="o3-list">
                          {parsedData.education.map((item, i) => (
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

            {activeTab === 'company' && (
              <div className="o3-tab-panel">
                {parsedData?.company_overview ? (
                  <div className="o3-content-card">
                    <h3>{contact.company}</h3>
                    <p>{parsedData.company_overview}</p>
                  </div>
                ) : (
                  <div className="o3-empty-state">
                    <Building2 size={48} />
                    <p>No company data available</p>
                  </div>
                )}
              </div>
            )}

            {activeTab === 'personality' && (
              <div className="o3-tab-panel">
                {parsedData?.personality_assessment ? (
                  <>
                    {parsedData.mbti_type && (
                      <div className="o3-mbti-badge">
                        {parsedData.mbti_type}
                      </div>
                    )}
                    <div className="o3-content-card">
                      <h3>Personality Assessment</h3>
                      <p>{parsedData.personality_assessment}</p>
                    </div>
                  </>
                ) : (
                  <div className="o3-empty-state">
                    <Brain size={48} />
                    <p>No personality data available</p>
                  </div>
                )}
              </div>
            )}

            {activeTab === 'chat' && (
              <div className="o3-tab-panel">
                {parsedData?.pain_points.length || parsedData?.key_insights.length ? (
                  <>
                    {parsedData.pain_points.length > 0 && (
                      <div className="o3-content-card">
                        <h3>Pain Points</h3>
                        <ul className="o3-list">
                          {parsedData.pain_points.map((item, i) => (
                            <li key={i}>{item}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                    {parsedData.key_insights.length > 0 && (
                      <div className="o3-content-card">
                        <h3>Key Insights</h3>
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

            {activeTab === 'content' && (
              <div className="o3-tab-panel">
                <div className="o3-empty-state">
                  <MessageSquare size={48} />
                  <p>Content generation coming soon</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
