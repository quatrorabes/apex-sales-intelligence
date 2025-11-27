import { useState, useEffect } from 'react';
import { X, Copy, Check, Sparkles, Mail, Phone, MessageSquare, Linkedin, FileText } from 'lucide-react';
import '../styles/ContactDetailModal.css';

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
  profile_content?: string;
  recommended_action?: string;
  times_enriched?: number;
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

function parseEnrichedProfile(text: string): ParsedIntelligence {
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

  const cleanText = (t: string) => t.replace(/\*\*/g, '').replace(/^[\s-•]+/, '').trim();
  const extractBullets = (t: string) => {
    const bullets = t.split(/\n/).filter(line => line.trim().match(/^[-•*]|^\d+\./));
    return bullets.map(b => cleanText(b.replace(/^[-•*\d.]+\s*/, '')));
  };

  // PROFESSIONAL PROFILE sections
  const profMatch = text.match(/PROFESSIONAL PROFILE[\s\S]*?(?=CORPORATE PROFILE|$)/i);
  if (profMatch) {
    const profText = profMatch[0];
    
    // 1. Overview
    const ov = profText.match(/1\.\s*Overview[\s\S]*?(?=2\.|$)/i);
    if (ov) sections.overview = cleanText(ov[0].replace(/1\.\s*Overview/i, ''));
    
    // 2. Background
    const bg = profText.match(/2\.\s*Background[\s\S]*?(?=3\.|$)/i);
    if (bg) sections.background = extractBullets(bg[0]);
    
    // 3. Education
    const ed = profText.match(/3\.\s*Education[\s\S]*?(?=4\.|$)/i);
    if (ed) sections.education = cleanText(ed[0].replace(/3\.\s*Education[^\n]*/i, ''));
    
    // 4. Recent Mentions
    const rm = profText.match(/4\.\s*Recent Mentions[\s\S]*?(?=5\.|$)/i);
    if (rm) sections.recentMentions = extractBullets(rm[0]);
    
    // 5. Social Profiles
    const sp = profText.match(/5\.\s*Social[\s\S]*?(?=6\.|$)/i);
    if (sp) sections.socialProfiles = cleanText(sp[0].replace(/5\.\s*Social[^\n]*/i, ''));
    
    // 6. Personality
    const pr = profText.match(/6\.\s*Personality[\s\S]*?(?=7\.|$)/i);
    if (pr) sections.personalityDetail = cleanText(pr[0].replace(/6\.\s*Personality[^\n]*/i, ''));
    
    // 7. Myers-Briggs
    const mb = profText.match(/7\.\s*Myers-Briggs[\s\S]*?(?=8\.|$)/i);
    if (mb) {
      sections.mbtiAssessment = cleanText(mb[0].replace(/7\.\s*Myers-Briggs[^\n]*/i, ''));
      const typeMatch = mb[0].match(/[EI][NS][TF][JP]/i);
      if (typeMatch) sections.mbtiType = typeMatch[0].toUpperCase();
    }
    
    // 8. Sales Opportunity
    const so = profText.match(/8\.\s*Sales[\s\S]*?(?=CORPORATE|---|$)/i);
    if (so) sections.salesTalkingPoints = extractBullets(so[0]);
  }

  // CORPORATE PROFILE sections
  const corpMatch = text.match(/CORPORATE PROFILE[\s\S]*?(?=STRATEGIC INTELLIGENCE|$)/i);
  if (corpMatch) {
    sections.companyFullProfile = cleanText(corpMatch[0]);
    const corpText = corpMatch[0];
    
    const co = corpText.match(/1\.\s*Overview[\s\S]*?(?=2\.|$)/i);
    if (co) sections.companyOverview = cleanText(co[0].replace(/1\.\s*Overview/i, ''));
    
    const cp = corpText.match(/2\.\s*Products[\s\S]*?(?=3\.|$)/i);
    if (cp) sections.companyProducts = cleanText(cp[0].replace(/2\.\s*Products[^\n]*/i, ''));
    
    const cl = corpText.match(/3\.\s*Leadership[\s\S]*?(?=4\.|$)/i);
    if (cl) sections.companyLeadership = cleanText(cl[0].replace(/3\.\s*Leadership/i, ''));
    
    const cm = corpText.match(/4\.\s*Market[\s\S]*?(?=5\.|$)/i);
    if (cm) sections.companyMarket = cleanText(cm[0].replace(/4\.\s*Market[^\n]*/i, ''));
    
    const cn = corpText.match(/5\.\s*Recent News[\s\S]*?(?=6\.|$)/i);
    if (cn) sections.companyNews = cleanText(cn[0].replace(/5\.\s*Recent News/i, ''));
    
    const cf = corpText.match(/6\.\s*Company Fun Facts[\s\S]*?(?=STRATEGIC|---|$)/i);
    if (cf) sections.companyFunFacts = extractBullets(cf[0]);
  }

  // STRATEGIC INTELLIGENCE sections
  const stratMatch = text.match(/STRATEGIC INTELLIGENCE[\s\S]*$/i);
  if (stratMatch) {
    const stratText = stratMatch[0];
    
    const pp = stratText.match(/Pain Points[\s\S]*?(?=SBA|Key Insights|$)/i);
    if (pp) sections.painPoints = extractBullets(pp[0]);
    
    const sba = stratText.match(/SBA Financing[\s\S]*?(?=Key Insights|$)/i);
    if (sba) sections.sbaInterests = extractBullets(sba[0]);
    
    const ki = stratText.match(/Key Insights[\s\S]*$/i);
    if (ki) sections.keyInsights = extractBullets(ki[0]);
  }

  return sections;
}

export default function ContactDetailModal({ contact, onClose, onEnrich }: ContactDetailModalProps) {
  const [activeTab, setActiveTab] = useState<TabId>('overview');
  const [copiedField, setCopiedField] = useState<string | null>(null);
  const [parsedData, setParsedData] = useState<ParsedIntelligence | null>(null);
  const [isEnriching, setIsEnriching] = useState(false);

  useEffect(() => {
    console.log('Contact profile_content:', contact.profile_content);
    if (contact.profile_content) {
      const parsed = parseEnrichedProfile(contact.profile_content);
      console.log('Parsed enrichment data:', parsed);
      setParsedData(parsed);
    }
  }, [contact.profile_content]);

  const copyToClipboard = async (text: string, field: string) => {
    await navigator.clipboard.writeText(text);
    setCopiedField(field);
    setTimeout(() => setCopiedField(null), 2000);
  };

  const handleEnrich = async () => {
    setIsEnriching(true);
    console.log('Starting enrichment for contact:', contact.id);
    
    try {
      const response = await fetch('http://localhost:8000/api/contacts/' + contact.id + '/enrich', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      const data = await response.json();
      console.log('Enrichment response:', data);
      
      if (data.success) {
        alert('Enrichment complete!');
        if (onEnrich) {
          onEnrich(contact.id);  // Still call parent if provided
        }
        window.location.reload();
      } else {
        alert('Enrichment failed: ' + (data.error || 'Unknown error'));
      }
    } catch (error) {
      console.error('Enrichment error:', error);
      alert('Enrichment failed - check console');
    } finally {
      setIsEnriching(false);
    }
  };
  
  const getStatusColor = (status?: string) => {
    switch (status) {
      case 'enriched': return '#10b981';
      case 'pending': return '#f59e0b';
      case 'failed': return '#ef4444';
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
        <div className="o3-modal-header">
          <button className="o3-close-btn" onClick={onClose}><X size={20} /></button>
          <div className="o3-contact-hero">
            <div className="o3-avatar">
              {contact.name.split(' ').map(n => n[0]).join('').substring(0, 2)}</div>
            <div className="o3-hero-info">
              <h1 className="o3-hero-name">{contact.name}</h1>
              <p className="o3-hero-title">{contact.title} at {contact.company}</p>
            </div>
          </div>
          <div className="o3-score-pills">
            <div className="o3-score-pill" style={{ '--score-color': getScoreColor(contact.mdcp_score || 0) } as React.CSSProperties}>
              <div className="o3-pill-value">{contact.mdcp_score || 0}</div><div className="o3-pill-label">PRIORITY</div>
            </div>
            <div className="o3-score-pill" style={{ '--score-color': getScoreColor(contact.role_score || 0) } as React.CSSProperties}>
              <div className="o3-pill-value">{contact.role_score || 0}</div><div className="o3-pill-label">ROLE</div>
            </div>
            <div className="o3-score-pill" style={{ '--score-color': getScoreColor(contact.data_score || 0) } as React.CSSProperties}>
              <div className="o3-pill-value">{contact.data_score || 0}</div><div className="o3-pill-label">DATA</div>
            </div>
          </div>
          <div className="o3-tab-nav">
            <button className={`o3-tab ${activeTab === 'overview' ? 'active' : ''}`} onClick={() => setActiveTab('overview')}>Overview</button>
            <button className={`o3-tab ${activeTab === 'personal' ? 'active' : ''}`} onClick={() => setActiveTab('personal')}>Personal</button>
            <button className={`o3-tab ${activeTab === 'company' ? 'active' : ''}`} onClick={() => setActiveTab('company')}>Company</button>
            <button className={`o3-tab ${activeTab === 'personality' ? 'active' : ''}`} onClick={() => setActiveTab('personality')}>Personality</button>
            <button className={`o3-tab ${activeTab === 'chat' ? 'active' : ''}`} onClick={() => setActiveTab('chat')}>Chat Things</button>
            <button className={`o3-tab ${activeTab === 'content' ? 'active' : ''}`} onClick={() => setActiveTab('content')}>Content</button>
          </div>
        </div>

        <div className="o3-modal-content">
          <div className="o3-stats-grid">
            <div className="o3-stat-card">
              <Mail className="o3-stat-icon" />
              <div className="o3-stat-info">
                <span className="o3-stat-label">Email</span>
                <span className="o3-stat-value">{contact.email}</span>
              </div>
              <button className="o3-copy-btn" onClick={() => copyToClipboard(contact.email, 'email')}>
                {copiedField === 'email' ? <Check size={14} /> : <Copy size={14} />}
              </button>
            </div>
            <div className="o3-stat-card">
              <Phone className="o3-stat-icon" />
              <div className="o3-stat-info">
                <span className="o3-stat-label">Phone</span>
                <span className="o3-stat-value">{contact.phone}</span>
              </div>
              <button className="o3-copy-btn" onClick={() => copyToClipboard(contact.phone, 'phone')}>
                {copiedField === 'phone' ? <Check size={14} /> : <Copy size={14} />}
              </button>
            </div>
            <div className="o3-stat-card">
              <div className="o3-stat-icon" style={{ backgroundColor: getStatusColor(contact.enrichment_status) }}>
                <Sparkles size={16} />
              </div>
              <div className="o3-stat-info">
                <span className="o3-stat-label">Status</span>
                <span className="o3-stat-value">{contact.enrichment_status || 'Not Enriched'}</span>
              </div>
              {contact.enrichment_status !== 'enriched' && (
                <button className="o3-enrich-btn" onClick={handleEnrich} disabled={isEnriching}>
                  {isEnriching ? 'Enriching...' : 'Enrich'}
                </button>
              )}
            </div>
          </div>

          {/* OVERVIEW TAB */}
          {activeTab === 'overview' && (
            <div className="o3-tab-content">
              {parsedData?.overview ? (
                <div className="o3-section">
                  <h3>Overview</h3>
                  <p>{parsedData.overview}</p>
                </div>
              ) : null}
              {parsedData?.painPoints?.length > 0 && (
                <div className="o3-section">
                  <h3>Pain Points</h3>
                  <ul>{parsedData.painPoints.map((p, i) => <li key={i}>{p}</li>)}</ul>
                </div>
              )}
              {parsedData?.sbaInterests?.length > 0 && (
                <div className="o3-section">
                  <h3>SBA Financing Interest</h3>
                  <ul>{parsedData.sbaInterests.map((s, i) => <li key={i}>{s}</li>)}</ul>
                </div>
              )}
              {parsedData?.keyInsights?.length > 0 && (
                <div className="o3-section">
                  <h3>Key Insights</h3>
                  <ul>{parsedData.keyInsights.map((k, i) => <li key={i}>{k}</li>)}</ul>
                </div>
              )}
              {!parsedData?.overview && !parsedData?.painPoints?.length && (
                <p className="o3-empty">No overview data available. Click Enrich to gather intelligence.</p>
              )}
            </div>
          )}

          {/* PERSONAL TAB */}
          {activeTab === 'personal' && (
            <div className="o3-tab-content">
              {parsedData?.background?.length > 0 && (
                <div className="o3-section">
                  <h3>Background</h3>
                  <ul>{parsedData.background.map((b, i) => <li key={i}>{b}</li>)}</ul>
                </div>
              )}
              {parsedData?.education && (
                <div className="o3-section">
                  <h3>Education</h3>
                  <p>{parsedData.education}</p>
                </div>
              )}
              {parsedData?.recentMentions?.length > 0 && (
                <div className="o3-section">
                  <h3>Recent Mentions</h3>
                  <ul>{parsedData.recentMentions.map((r, i) => <li key={i}>{r}</li>)}</ul>
                </div>
              )}
              {parsedData?.socialProfiles && (
                <div className="o3-section">
                  <h3>Social Profiles</h3>
                  <p>{parsedData.socialProfiles}</p>
                </div>
              )}
              {!parsedData?.background?.length && !parsedData?.education && (
                <p className="o3-empty">No personal data available. Click Enrich to gather intelligence.</p>
              )}
            </div>
          )}

          {/* COMPANY TAB */}
          {activeTab === 'company' && (
            <div className="o3-tab-content">
              {parsedData?.companyOverview && (
                <div className="o3-section">
                  <h3>Company Overview</h3>
                  <p>{parsedData.companyOverview}</p>
                </div>
              )}
              {parsedData?.companyProducts && (
                <div className="o3-section">
                  <h3>Products & Services</h3>
                  <p>{parsedData.companyProducts}</p>
                </div>
              )}
              {parsedData?.companyLeadership && (
                <div className="o3-section">
                  <h3>Leadership</h3>
                  <p>{parsedData.companyLeadership}</p>
                </div>
              )}
              {parsedData?.companyMarket && (
                <div className="o3-section">
                  <h3>Market Position</h3>
                  <p>{parsedData.companyMarket}</p>
                </div>
              )}
              {parsedData?.companyNews && (
                <div className="o3-section">
                  <h3>Recent News</h3>
                  <p>{parsedData.companyNews}</p>
                </div>
              )}
              {parsedData?.companyFunFacts?.length > 0 && (
                <div className="o3-section">
                  <h3>Fun Facts</h3>
                  <ul>{parsedData.companyFunFacts.map((f, i) => <li key={i}>{f}</li>)}</ul>
                </div>
              )}
              {!parsedData?.companyOverview && !parsedData?.companyProducts && (
                <p className="o3-empty">No company data available. Click Enrich to gather intelligence.</p>
              )}
            </div>
          )}

          {/* PERSONALITY TAB */}
          {activeTab === 'personality' && (
            <div className="o3-tab-content">
              {parsedData?.mbtiType && (
                <div className="o3-section o3-mbti-badge">
                  <span className="o3-mbti-type">{parsedData.mbtiType}</span>
                </div>
              )}
              {parsedData?.personalityDetail && (
                <div className="o3-section">
                  <h3>Personality Profile</h3>
                  <p>{parsedData.personalityDetail}</p>
                </div>
              )}
              {parsedData?.mbtiAssessment && (
                <div className="o3-section">
                  <h3>Myers-Briggs Assessment</h3>
                  <p>{parsedData.mbtiAssessment}</p>
                </div>
              )}
              {!parsedData?.personalityDetail && !parsedData?.mbtiAssessment && (
                <p className="o3-empty">No personality data available. Click Enrich to gather intelligence.</p>
              )}
            </div>
          )}

          {/* CHAT THINGS TAB */}
          {activeTab === 'chat' && (
            <div className="o3-tab-content">
              {parsedData?.salesTalkingPoints?.length > 0 && (
                <div className="o3-section">
                  <h3>Sales Talking Points</h3>
                  <ul>{parsedData.salesTalkingPoints.map((t, i) => <li key={i}>{t}</li>)}</ul>
                </div>
              )}
              {contact.recommended_action && (
                <div className="o3-section">
                  <h3>Recommended Action</h3>
                  <p>{contact.recommended_action}</p>
                </div>
              )}
              {!parsedData?.salesTalkingPoints?.length && !contact.recommended_action && (
                <p className="o3-empty">No chat data available. Click Enrich to gather intelligence.</p>
              )}
            </div>
          )}

          {/* CONTENT TAB */}
          {activeTab === 'content' && (
            <div className="o3-tab-content">
              <div className="o3-content-generator">
                <div className="o3-content-card">
                  <div className="o3-content-header">
                    <Mail size={20} />
                    <h4>Email Templates</h4>
                  </div>
                  <p className="o3-content-desc">Generate personalized email templates based on contact intelligence.</p>
                  <button className="o3-generate-btn">Generate Email</button>
                </div>
                <div className="o3-content-card">
                  <div className="o3-content-header">
                    <Phone size={20} />
                    <h4>Call Scripts</h4>
                  </div>
                  <p className="o3-content-desc">Create call scripts tailored to this contact's profile.</p>
                  <button className="o3-generate-btn">Generate Script</button>
                </div>
                <div className="o3-content-card">
                  <div className="o3-content-header">
                    <Linkedin size={20} />
                    <h4>LinkedIn Messages</h4>
                  </div>
                  <p className="o3-content-desc">Craft LinkedIn outreach messages for this contact.</p>
                  <button className="o3-generate-btn">Generate Message</button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}