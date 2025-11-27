import React, { useState, useEffect } from 'react';
import { X, Mail, Phone, Building2, Briefcase, Copy, Check, Sparkles, TrendingUp, Target, Brain, MessageSquare, Lightbulb } from 'lucide-react';
import './ContactDetailModal.css';
import ContentGenerator from './ContentGenerator';

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

  const parseEnrichedProfile = (text: string): ParsedIntelligence => {
    const sections: ParsedIntelligence = {
      overview: '',
      background: [],
      education: [],
      recent_mentions: [],
      sales_talking_points: [],
      company_full_profile: '',
      personality_detail: '',
      mbti_assessment: '',
      mbti_type: '',
      pain_points: [],
      sba_interests: [],
      key_insights: []
    };

    const cleanText = (str: string) => 
      str.replace(/\*\*/g, '')
         .replace(/###/g, '')
         .replace(/##/g, '')
         .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
         .trim();

    // Extract section 1: Overview
    const overviewMatch = text.match(/###\s*1\.\s*Overview[^\n]*\n+(.*?)(?=###\s*2\.|$)/is);
    if (overviewMatch) {
      sections.overview = cleanText(overviewMatch[1]);
    }

    // Extract section 2: Background
    const backgroundMatch = text.match(/###\s*2\.\s*Background[^\n]*\n+(.*?)(?=###\s*3\.|$)/is);
    if (backgroundMatch) {
      const bullets = backgroundMatch[1].match(/[-•]\s*(.+)/g);
      if (bullets) {
        sections.background = bullets.map(b => cleanText(b.replace(/^[-•]\s*/, '')));
      }
    }

    // Extract section 3: Education
    const educationMatch = text.match(/###\s*3\.\s*Education[^\n]*\n+(.*?)(?=###\s*4\.|$)/is);
    if (educationMatch) {
      sections.education = [cleanText(educationMatch[1])];
    }

    // Extract section 4: Recent Mentions
    const recentMatch = text.match(/###\s*4\.\s*Recent Mentions[^\n]*\n+(.*?)(?=###\s*5\.|$)/is);
    if (recentMatch) {
      const bullets = recentMatch[1].match(/[-•]\s*(.+)/g);
      if (bullets) {
        sections.recent_mentions = bullets.map(b => cleanText(b.replace(/^[-•]\s*/, '')));
      }
    }

    // Extract section 6: Personality Detail
    const personalityMatch = text.match(/###\s*6\.\s*Personality Detail[^\n]*\n+(.*?)(?=###\s*7\.|$)/is);
    if (personalityMatch) {
      sections.personality_detail = cleanText(personalityMatch[1]);
      const mbtiMatch = personalityMatch[1].match(/\b(INTJ|INTP|ENTJ|ENTP|INFJ|INFP|ENFJ|ENFP|ISTJ|ISFJ|ESTJ|ESFJ|ISTP|ISFP|ESTP|ESFP)\b/);
      if (mbtiMatch) sections.mbti_type = mbtiMatch[1];
    }

    // Extract section 7: Myers-Briggs Assessment
    const mbtiAssessmentMatch = text.match(/###\s*7\.\s*Myers-Briggs[^\n]*\n+(.*?)(?=###\s*8\.|$)/is);
    if (mbtiAssessmentMatch) {
      sections.mbti_assessment = cleanText(mbtiAssessmentMatch[1]);
    }

    // Extract section 8: Sales Talking Points
    const salesMatch = text.match(/###\s*8\.\s*Sales Opportunity[^\n]*\n+(.*?)(?=---|CORPORATE PROFILE|$)/is);
    if (salesMatch) {
      const bullets = salesMatch[1].match(/[-•]\s*(.+)/g);
      if (bullets) {
        sections.sales_talking_points = bullets.map(b => cleanText(b.replace(/^[-•]\s*/, '')));
      }
    }

    // Extract ENTIRE Company Profile section
    const companyMatch = text.match(/CORPORATE PROFILE\*\*\s*\n+(.*?)(?=\*\*STRATEGIC INTELLIGENCE|$)/is);
    if (companyMatch) {
      sections.company_full_profile = cleanText(companyMatch[1]);
    }

    // Extract Strategic Intelligence: Pain Points
    const painMatch = text.match(/\*\*Pain Points[^\n]*\n+(.*?)(?=\*\*SBA|$)/is);
    if (painMatch) {
      const bullets = painMatch[1].match(/[-•]\s*(.+?)(?=\n[-•]|\n\*\*|\n\n|$)/gs);
      if (bullets) {
        sections.pain_points = bullets.map(b => cleanText(b.replace(/^[-•]\s*/, '')));
      }
    }

    // Extract Strategic Intelligence: SBA Financing
    const sbaMatch = text.match(/\*\*SBA Financing Interest[^\n]*\n+(.*?)(?=\*\*Key Insights|$)/is);
    if (sbaMatch) {
      const bullets = sbaMatch[1].match(/[-•]\s*(.+?)(?=\n[-•]|\n\*\*|\n\n|$)/gs);
      if (bullets) {
        sections.sba_interests = bullets.map(b => cleanText(b.replace(/^[-•]\s*/, '')));
      }
    }

    // Extract Strategic Intelligence: Key Insights
    const insightsMatch = text.match(/\*\*Key Insights\*\*\s*\n+(.*?)(?====|$)/is);
    if (insightsMatch) {
      const bullets = insightsMatch[1].match(/[-•]\s*(.+?)(?=\n[-•]|\n====|$)/gs);
      if (bullets) {
        sections.key_insights = bullets.map(b => cleanText(b.replace(/^[-•]\s*/, '')));
      }
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
                    
                    {parsedData.sales_talking_points.length > 0 && (
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
                        <div>
                          {parsedData.education.map((item, i) => (
                            <p key={i}>{item}</p>
                          ))}
                        </div>
                      </div>
                    )}
                    
                    {parsedData.recent_mentions.length > 0 && (
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
                {parsedData?.pain_points.length || parsedData?.sba_interests.length || parsedData?.key_insights.length ? (
                  <>
                    {parsedData.pain_points.length > 0 && (
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
                    
                    {parsedData.sba_interests.length > 0 && (
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
                    
                    {parsedData.key_insights.length > 0 && (
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