import React, { useState, useEffect } from 'react';
import {
  X, Sparkles, Loader, Mail, Phone, Linkedin, Target, Lightbulb,
  PhoneCall, StickyNote, Copy, Check, Zap, FileText, User, Building2, 
  Award, TrendingUp, Package
} from 'lucide-react';

interface Contact {
  id: number;
  name: string;
  email: string;
  phone: string;
  company: string;
  title: string;
  enrichment_status?: string;
  profile_content?: string;
  enrichment_data?: string;
  pain_points?: string;
  talking_points?: string;
  product_match?: string;
  match_reasoning?: string;
  recommended_action?: string;
  mdcp_score?: number;
  rss_score?: number;
  priority_score?: number;
  notes?: string;
  email_1_subject?: string;
  email_1_body?: string;
  email_2_subject?: string;
  email_2_body?: string;
  email_3_subject?: string;
  email_3_body?: string;
  call_script_1?: string;
  call_script_2?: string;
  call_script_3?: string;
  linkedin_connect?: string;
  linkedin_followup?: string;
  linkedin_inmail?: string;
  linkedin_warmup?: string;
  linkedin_url?: string;
}

interface ContactDetailModalProps {
  contact: Contact;
  onClose: () => void;
  onEnrichmentComplete?: (contact: Contact) => void;
}

type ViewMode = 'intelligence' | 'outreach' | 'dossier';
type IntelTab = 'pain-points' | 'product-fit' | 'insights' | 'call-prep' | 'notes';
type DossierTab = 'professional' | 'company' | 'personality';
type ContentTab = 'email' | 'call' | 'linkedin';

export default function ContactDetailModal({ contact, onClose, onEnrichmentComplete }: ContactDetailModalProps) {
  const [viewMode, setViewMode] = useState<ViewMode>('intelligence');
  const [activeIntelTab, setActiveIntelTab] = useState<IntelTab>('pain-points');
  const [activeDossierTab, setActiveDossierTab] = useState<DossierTab>('professional');
  const [activeContentTab, setActiveContentTab] = useState<ContentTab>('email');
  const [enriching, setEnriching] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [localContact, setLocalContact] = useState<Contact>(contact);
  const [notes, setNotes] = useState(contact.notes || '');
  const [copiedField, setCopiedField] = useState<string | null>(null);
  const [showEnrichSuccess, setShowEnrichSuccess] = useState(false);

  useEffect(() => {
    fetch(`http://localhost:8000/api/contacts/${contact.id}`)
      .then(res => res.json())
      .then(data => {
        setLocalContact(data);
        setNotes(data.notes || '');
      })
      .catch(err => console.error('Fetch failed:', err));
  }, [contact.id]);

  const isEnriched = localContact.enrichment_status === 'completed' && localContact.profile_content && localContact.profile_content.length > 0;
  const hasContent = localContact.email_1_subject || localContact.email_1_body || localContact.call_script_1 || localContact.linkedin_connect;

  const extractSection = (sectionNumber: string, sectionName: string): string | null => {
    const profile = localContact.profile_content || '';
    const regex = new RegExp(`${sectionNumber}\\.\\s*${sectionName}[:\\s]*`, 'i');
    const match = profile.match(regex);
    if (!match) return null;
    const startPos = match.index! + match[0].length;
    let endPos = profile.length;
    for (let i = startPos; i < profile.length - 3; i++) {
      if (profile[i].match(/\d/) && profile[i + 1] === '.' && profile[i + 2] === ' ') {
        endPos = i;
        break;
      }
    }
    return profile.substring(startPos, endPos).trim();
  };

  const dossierData = {
    overview: extractSection('1', 'Overview'),
    background: extractSection('2', 'Background'),
    education: extractSection('3', 'Education'),
    recentMentions: extractSection('4', 'Recent Mentions'),
    socialProfiles: extractSection('5', 'Social Profiles'),
    personality: extractSection('6', 'Personality'),
    myersBriggs: extractSection('7', 'Myers-Briggs'),
    companyOverview: extractSection('8', 'Company'),
    painPoints: extractSection('9', 'Pain Points'),
    productFit: extractSection('10', 'Product Fit'),
    keyInsights: extractSection('11', 'Key Insights'),
    finalNote: extractSection('12', 'Final'),
  };

  const handleEnrich = async () => {
    setEnriching(true);
    setShowEnrichSuccess(false);
    try {
      const res = await fetch(`http://localhost:8000/api/contacts/${contact.id}/enrich`, { method: 'POST' });
      const data = await res.json();
      if (data.success) {
        const updatedRes = await fetch(`http://localhost:8000/api/contacts/${contact.id}`);
        const updatedContact = await updatedRes.json();
        setLocalContact(updatedContact);
        onEnrichmentComplete?.(updatedContact);
        setShowEnrichSuccess(true);
        setTimeout(() => setShowEnrichSuccess(false), 3000);
      }
    } catch (err) {
      console.error('Enrichment failed:', err);
    } finally {
      setEnriching(false);
    }
  };

  const handleGenerateContent = async () => {
    setGenerating(true);
    try {
      await fetch(`http://localhost:8000/api/contacts/${contact.id}/generate-content`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content_type: 'all' }),
      });
      // Always refresh to get any content that was saved
      const updatedRes = await fetch(`http://localhost:8000/api/contacts/${contact.id}`);
      const updatedContact = await updatedRes.json();
      setLocalContact(updatedContact);
    } catch (err) {
      console.error('Content generation failed:', err);
      // Still try to refresh
      try {
        const updatedRes = await fetch(`http://localhost:8000/api/contacts/${contact.id}`);
        const updatedContact = await updatedRes.json();
        setLocalContact(updatedContact);
      } catch {}
    } finally {
      setGenerating(false);
    }
  };

  const handleSaveNotes = async () => {
    try {
      await fetch(`http://localhost:8000/api/contacts/${contact.id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ notes }),
      });
    } catch (err) {
      console.error('Failed to save notes:', err);
    }
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

  return (
    <div onClick={onClose} style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.8)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
      <div onClick={(e) => e.stopPropagation()} style={{ background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 100%)', borderRadius: 20, width: '95%', maxWidth: 1400, height: '90vh', overflow: 'hidden', boxShadow: '0 25px 50px -12px rgba(0,0,0,0.95)', border: '1px solid rgba(99,102,241,0.3)', display: 'flex', flexDirection: 'column' }}>

        {/* HEADER */}
        <div style={{ padding: '20px 24px', borderBottom: '1px solid rgba(148,163,184,0.2)', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexShrink: 0 }}>
          <div>
            <h2 style={{ margin: 0, color: '#f1f5f9', fontSize: 24, fontWeight: 700 }}>{localContact.name}</h2>
            <p style={{ margin: '4px 0 0', color: '#94a3b8', fontSize: 14 }}>{localContact.title} at {localContact.company}</p>
            <div style={{ display: 'flex', gap: 16, marginTop: 8 }}>
              {localContact.email && <span style={{ color: '#64748b', fontSize: 13 }}>{localContact.email}</span>}
              {localContact.phone && <span style={{ color: '#64748b', fontSize: 13 }}>{localContact.phone}</span>}
            </div>
          </div>
          <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
            <button onClick={handleEnrich} disabled={enriching} style={{ padding: '10px 20px', borderRadius: 8, border: 'none', background: showEnrichSuccess ? 'rgba(16,185,129,0.2)' : 'linear-gradient(135deg, #6366f1, #8b5cf6)', color: showEnrichSuccess ? '#10b981' : '#fff', fontSize: 13, fontWeight: 600, cursor: enriching ? 'not-allowed' : 'pointer', display: 'flex', alignItems: 'center', gap: 8 }}>
              {enriching ? <><Loader size={16} className="animate-spin" />Enriching...</> : showEnrichSuccess ? <><Check size={16} />Enriched!</> : <><Sparkles size={16} />{isEnriched ? 'Re-Enrich' : 'Enrich'}</>}
            </button>
            <button onClick={onClose} style={{ background: 'rgba(148,163,184,0.1)', border: 'none', borderRadius: 8, padding: 8, cursor: 'pointer', color: '#94a3b8' }}><X size={20} /></button>
          </div>
        </div>

        {/* MODE TABS */}
        <div style={{ display: 'flex', borderBottom: '1px solid rgba(148,163,184,0.2)', flexShrink: 0 }}>
          {[{ id: 'intelligence', label: 'Intelligence', icon: Target }, { id: 'dossier', label: 'Dossier', icon: FileText }, { id: 'outreach', label: 'Outreach', icon: Mail }].map((mode) => {
            const Icon = mode.icon;
            return (
              <button key={mode.id} onClick={() => setViewMode(mode.id as ViewMode)} style={{ flex: 1, padding: 16, border: 'none', borderBottom: viewMode === mode.id ? '3px solid #6366f1' : '3px solid transparent', background: viewMode === mode.id ? 'rgba(99,102,241,0.1)' : 'transparent', color: viewMode === mode.id ? '#e5e7eb' : '#9ca3af', fontSize: 15, fontWeight: 600, cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 10 }}>
                <Icon size={18} />{mode.label}
              </button>
            );
          })}
        </div>

        {/* INTELLIGENCE TAB */}
        {viewMode === 'intelligence' && (
          <>
            <div style={{ display: 'flex', gap: 8, padding: '12px 24px', borderBottom: '1px solid rgba(148,163,184,0.2)', background: 'rgba(15,23,42,0.5)', flexShrink: 0 }}>
              {[{ id: 'pain-points', label: 'Pain Points', icon: Target }, { id: 'product-fit', label: 'Product Fit', icon: Sparkles }, { id: 'insights', label: 'Insights', icon: Lightbulb }, { id: 'call-prep', label: 'Call Prep', icon: PhoneCall }, { id: 'notes', label: 'Notes', icon: StickyNote }].map((tab) => {
                const Icon = tab.icon;
                return (<button key={tab.id} onClick={() => setActiveIntelTab(tab.id as IntelTab)} style={{ padding: '8px 16px', borderRadius: 6, border: 'none', background: activeIntelTab === tab.id ? 'rgba(99,102,241,0.15)' : 'transparent', color: activeIntelTab === tab.id ? '#e5e7eb' : '#9ca3af', fontSize: 13, fontWeight: 600, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 6 }}><Icon size={14} />{tab.label}</button>);
              })}
            </div>
            <div style={{ flex: 1, overflowY: 'auto', padding: 24 }}>
              {!isEnriched ? (
                <EmptyState icon={<Sparkles size={48} />} title="Ready to Unlock Intelligence" subtitle="Click the Enrich button above." />
              ) : (
                <>
                  {activeIntelTab === 'pain-points' && <ContentSection title="Pain Points" content={localContact.pain_points || dossierData.painPoints} icon={<Target size={18} color="#6366f1" />} />}
                  {activeIntelTab === 'product-fit' && <ContentSection title="Product Fit" content={localContact.product_match || dossierData.productFit} icon={<Sparkles size={18} color="#6366f1" />} />}
                  {activeIntelTab === 'insights' && <ContentSection title="Key Insights" content={localContact.talking_points || dossierData.keyInsights} icon={<Lightbulb size={18} color="#6366f1" />} />}
                  {activeIntelTab === 'call-prep' && (
                    <>
                      <ContentSection title="Recommended Action" content={localContact.recommended_action || dossierData.finalNote} icon={<PhoneCall size={18} color="#6366f1" />} />
                      <div style={{ display: 'flex', gap: 16, marginTop: 24 }}>
                        <ScoreCard label="MDCP" value={localContact.mdcp_score} color="#6366f1" />
                        <ScoreCard label="RSS" value={localContact.rss_score} color="#10b981" />
                        <ScoreCard label="Priority" value={localContact.priority_score} color="#f59e0b" />
                      </div>
                    </>
                  )}
                  {activeIntelTab === 'notes' && (
                    <div>
                      <h4 style={{ color: '#e5e7eb', marginBottom: 12 }}>Internal Notes</h4>
                      <textarea value={notes} onChange={(e) => setNotes(e.target.value)} onBlur={handleSaveNotes} placeholder="Add notes..." style={{ width: '100%', minHeight: 250, padding: 16, borderRadius: 10, border: '1px solid rgba(148,163,184,0.3)', background: 'rgba(15,23,42,0.6)', color: '#e5e7eb', fontSize: 14, lineHeight: 1.6, resize: 'vertical' }} />
                    </div>
                  )}
                </>
              )}
            </div>
          </>
        )}

        {/* DOSSIER TAB */}
        {viewMode === 'dossier' && (
          <>
            <div style={{ display: 'flex', gap: 8, padding: '12px 24px', borderBottom: '1px solid rgba(148,163,184,0.2)', background: 'rgba(15,23,42,0.5)', flexShrink: 0 }}>
              {[{ id: 'professional', label: 'Professional', icon: User }, { id: 'company', label: 'Company', icon: Building2 }, { id: 'personality', label: 'Personality', icon: Award }].map((tab) => {
                const Icon = tab.icon;
                return (<button key={tab.id} onClick={() => setActiveDossierTab(tab.id as DossierTab)} style={{ padding: '8px 16px', borderRadius: 6, border: 'none', background: activeDossierTab === tab.id ? 'rgba(99,102,241,0.15)' : 'transparent', color: activeDossierTab === tab.id ? '#e5e7eb' : '#9ca3af', fontSize: 13, fontWeight: 600, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 6 }}><Icon size={14} />{tab.label}</button>);
              })}
            </div>
            <div style={{ flex: 1, overflowY: 'auto', padding: 24 }}>
              {!isEnriched ? (
                <EmptyState icon={<FileText size={48} />} title="No Dossier Available" subtitle="Enrich this contact first." />
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
                  {activeDossierTab === 'professional' && (
                    <>
                      <DossierCard title="Overview" content={dossierData.overview} icon={<User size={16} color="#6366f1" />} />
                      <DossierCard title="Background" content={dossierData.background} icon={<FileText size={16} color="#6366f1" />} />
                      <DossierCard title="Education" content={dossierData.education} icon={<Award size={16} color="#6366f1" />} />
                      <DossierCard title="Recent Mentions" content={dossierData.recentMentions} icon={<TrendingUp size={16} color="#6366f1" />} />
                    </>
                  )}
                  {activeDossierTab === 'company' && (
                    <>
                      <DossierCard title="Company Overview" content={dossierData.companyOverview} icon={<Building2 size={16} color="#6366f1" />} />
                    </>
                  )}
                  {activeDossierTab === 'personality' && (
                    <>
                      <DossierCard title="Personality" content={dossierData.personality} icon={<Award size={16} color="#6366f1" />} />
                      <DossierCard title="Myers-Briggs" content={dossierData.myersBriggs} icon={<User size={16} color="#6366f1" />} />
                      <DossierCard title="Social Profiles" content={dossierData.socialProfiles} icon={<Linkedin size={16} color="#6366f1" />} />
                    </>
                  )}
                </div>
              )}
            </div>
          </>
        )}

        {/* OUTREACH TAB */}
        {viewMode === 'outreach' && (
          <>
            <div style={{ display: 'flex', gap: 8, padding: '12px 24px', borderBottom: '1px solid rgba(148,163,184,0.2)', background: 'rgba(15,23,42,0.5)', flexShrink: 0, alignItems: 'center' }}>
              {[{ id: 'email', label: 'Email', icon: Mail, color: '#6366f1' }, { id: 'call', label: 'Call Scripts', icon: PhoneCall, color: '#10b981' }, { id: 'linkedin', label: 'LinkedIn', icon: Linkedin, color: '#0ea5e9' }].map((tab) => {
                const Icon = tab.icon;
                return (<button key={tab.id} onClick={() => setActiveContentTab(tab.id as ContentTab)} style={{ padding: '10px 20px', borderRadius: 8, border: activeContentTab === tab.id ? `1px solid ${tab.color}` : '1px solid transparent', background: activeContentTab === tab.id ? `${tab.color}15` : 'transparent', color: activeContentTab === tab.id ? tab.color : '#9ca3af', fontSize: 13, fontWeight: 600, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 8 }}><Icon size={16} />{tab.label}</button>);
              })}
              <button onClick={handleGenerateContent} disabled={generating || !isEnriched} style={{ marginLeft: 'auto', padding: '10px 20px', borderRadius: 8, border: 'none', background: generating ? 'rgba(99,102,241,0.3)' : 'linear-gradient(135deg, #6366f1, #8b5cf6)', color: '#fff', fontSize: 13, fontWeight: 600, cursor: generating || !isEnriched ? 'not-allowed' : 'pointer', display: 'flex', alignItems: 'center', gap: 8, opacity: !isEnriched ? 0.5 : 1 }}>
                {generating ? <><Loader size={16} className="animate-spin" />Generating...</> : <><Zap size={16} />Generate All Content</>}
              </button>
            </div>

            <div style={{ flex: 1, overflowY: 'auto', padding: 24 }}>
              {!isEnriched ? (
                <EmptyState icon={<Mail size={48} />} title="Enrich First" subtitle="Generate intelligence before creating outreach content." />
              ) : !hasContent ? (
                <EmptyState icon={<Zap size={48} />} title="Ready to Generate" subtitle='Click "Generate All Content" to create personalized outreach.' />
              ) : (
                <>
                  {/* EMAIL TAB */}
                  {activeContentTab === 'email' && (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
                      {(localContact.email_1_subject || localContact.email_1_body) ? (
                        [1, 2, 3].map((num) => {
                          const subject = localContact[`email_${num}_subject` as keyof Contact] as string;
                          const body = localContact[`email_${num}_body` as keyof Contact] as string;
                          if (!subject && !body) return null;
                          return <EmailCard key={num} number={num} subject={subject || ''} body={body || ''} onCopy={copyToClipboard} copiedField={copiedField} />;
                        })
                      ) : (
                        <EmptyState icon={<Mail size={40} />} title="" subtitle='No emails generated yet. Click "Generate All Content" above.' small />
                      )}
                    </div>
                  )}

                  {/* CALL SCRIPTS TAB */}
                  {activeContentTab === 'call' && (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
                      {(localContact.call_script_1 || localContact.call_script_2 || localContact.call_script_3) ? (
                        [1, 2, 3].map((num) => {
                          const script = localContact[`call_script_${num}` as keyof Contact] as string;
                          if (!script) return null;
                          const labels = ['Direct & Value-Focused', 'Consultative & Rapport-Building', 'Executive / Insight-Led'];
                          return <CallScriptCard key={num} number={num} label={labels[num - 1]} content={script} onCopy={copyToClipboard} copiedField={copiedField} />;
                        })
                      ) : (
                        <EmptyState icon={<PhoneCall size={40} />} title="" subtitle='No call scripts generated yet. Click "Generate All Content" above.' small />
                      )}
                    </div>
                  )}

                  {/* LINKEDIN TAB */}
                  {activeContentTab === 'linkedin' && (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
                      {(localContact.linkedin_connect || localContact.linkedin_followup || localContact.linkedin_inmail) ? (
                        <>
                          <LinkedInCard title="Connection Request" content={localContact.linkedin_connect} onCopy={copyToClipboard} copiedField={copiedField} fieldKey="linkedin_connect" maxChars={300} />
                          <LinkedInCard title="Follow-up Message" content={localContact.linkedin_followup} onCopy={copyToClipboard} copiedField={copiedField} fieldKey="linkedin_followup" />
                          <LinkedInCard title="InMail" content={localContact.linkedin_inmail} onCopy={copyToClipboard} copiedField={copiedField} fieldKey="linkedin_inmail" />
                          {localContact.linkedin_warmup && <WarmupSequenceCard warmupJson={localContact.linkedin_warmup} />}
                          {localContact.linkedin_url && (
                            <a href={localContact.linkedin_url} target="_blank" rel="noopener noreferrer" style={{ display: 'flex', alignItems: 'center', gap: 8, color: '#0ea5e9', fontSize: 13, textDecoration: 'none' }}>
                              <Linkedin size={16} />View LinkedIn Profile →
                            </a>
                          )}
                        </>
                      ) : (
                        <EmptyState icon={<Linkedin size={40} />} title="" subtitle='No LinkedIn messages generated yet. Click "Generate All Content" above.' small />
                      )}
                    </div>
                  )}
                </>
              )}
            </div>
          </>
        )}

        <style>{`@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } } .animate-spin { animation: spin 1s linear infinite; }`}</style>
      </div>
    </div>
  );
}

// ============ HELPER COMPONENTS ============

function EmptyState({ icon, title, subtitle, small }: { icon: React.ReactNode; title: string; subtitle: string; small?: boolean }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: small ? 'auto' : '100%', padding: small ? 40 : 0, color: '#64748b' }}>
      <div style={{ opacity: 0.5, marginBottom: 16 }}>{icon}</div>
      {title && <h3 style={{ margin: 0, color: '#94a3b8', fontSize: small ? 14 : 18 }}>{title}</h3>}
      <p style={{ marginTop: 8, fontSize: small ? 13 : 14, textAlign: 'center' }}>{subtitle}</p>
    </div>
  );
}

function ContentSection({ title, content, icon }: { title: string; content?: string | null; icon?: React.ReactNode }) {
  return (
    <div style={{ marginBottom: 24 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 12 }}>
        {icon}
        <h3 style={{ margin: 0, color: '#e5e7eb', fontSize: 16, fontWeight: 600 }}>{title}</h3>
      </div>
      <div style={{ background: 'rgba(15,23,42,0.6)', borderRadius: 10, padding: 20, border: '1px solid rgba(148,163,184,0.2)' }}>
        <p style={{ margin: 0, color: '#cbd5e1', fontSize: 14, lineHeight: 1.7, whiteSpace: 'pre-wrap' }}>{content || 'No data available'}</p>
      </div>
    </div>
  );
}

function DossierCard({ title, content, icon }: { title: string; content?: string | null; icon?: React.ReactNode }) {
  if (!content) return null;
  return (
    <div style={{ background: 'rgba(15,23,42,0.6)', borderRadius: 10, padding: 16, border: '1px solid rgba(148,163,184,0.2)' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 10 }}>
        {icon}
        <h4 style={{ margin: 0, color: '#e5e7eb', fontSize: 14, fontWeight: 600 }}>{title}</h4>
      </div>
      <p style={{ margin: 0, color: '#94a3b8', fontSize: 13, lineHeight: 1.6, whiteSpace: 'pre-wrap' }}>{content}</p>
    </div>
  );
}

function ScoreCard({ label, value, color }: { label: string; value?: number; color: string }) {
  return (
    <div style={{ background: 'rgba(15,23,42,0.6)', borderRadius: 10, padding: 16, border: `1px solid ${color}30`, minWidth: 100, textAlign: 'center' }}>
      <div style={{ fontSize: 11, color: '#64748b', textTransform: 'uppercase', marginBottom: 4 }}>{label}</div>
      <div style={{ fontSize: 28, fontWeight: 700, color }}>{value != null ? Math.round(value) : '—'}</div>
    </div>
  );
}

function EmailCard({ number, subject, body, onCopy, copiedField }: { number: number; subject: string; body: string; onCopy: (t: string, f: string) => void; copiedField: string | null }) {
  const labels = ['Initial Outreach', 'Follow-up', 'Break-up Email'];
  const colors = ['#6366f1', '#8b5cf6', '#a855f7'];
  const color = colors[number - 1];
  return (
    <div style={{ background: 'rgba(15,23,42,0.6)', borderRadius: 12, border: `1px solid ${color}30`, overflow: 'hidden' }}>
      <div style={{ padding: '12px 16px', background: `${color}15`, borderBottom: `1px solid ${color}30`, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <span style={{ background: color, color: '#fff', fontSize: 11, fontWeight: 700, padding: '4px 10px', borderRadius: 20 }}>Email {number}</span>
          <span style={{ color: '#94a3b8', fontSize: 13 }}>{labels[number - 1]}</span>
        </div>
        <button onClick={() => onCopy(`Subject: ${subject}\n\n${body}`, `email_${number}`)} style={{ background: 'transparent', border: 'none', color: copiedField === `email_${number}` ? '#10b981' : '#64748b', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 6, fontSize: 12 }}>
          {copiedField === `email_${number}` ? <Check size={14} /> : <Copy size={14} />}{copiedField === `email_${number}` ? 'Copied!' : 'Copy'}
        </button>
      </div>
      <div style={{ padding: '12px 16px', borderBottom: '1px solid rgba(148,163,184,0.1)' }}>
        <div style={{ fontSize: 11, color: '#64748b', marginBottom: 4 }}>SUBJECT</div>
        <div style={{ color: '#e5e7eb', fontSize: 14, fontWeight: 500 }}>{subject}</div>
      </div>
      <div style={{ padding: '12px 16px' }}>
        <div style={{ fontSize: 11, color: '#64748b', marginBottom: 4 }}>BODY</div>
        <div style={{ color: '#cbd5e1', fontSize: 13, lineHeight: 1.7, whiteSpace: 'pre-wrap' }}>{body}</div>
      </div>
    </div>
  );
}

function CallScriptCard({ number, label, content, onCopy, copiedField }: { number: number; label: string; content: string; onCopy: (t: string, f: string) => void; copiedField: string | null }) {
  const colors = ['#10b981', '#22c55e', '#16a34a'];
  const color = colors[number - 1];
  return (
    <div style={{ background: 'rgba(15,23,42,0.6)', borderRadius: 12, border: `1px solid ${color}30`, overflow: 'hidden' }}>
      <div style={{ padding: '12px 16px', background: `${color}15`, borderBottom: `1px solid ${color}30`, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <span style={{ background: color, color: '#fff', fontSize: 11, fontWeight: 700, padding: '4px 10px', borderRadius: 20 }}>Script {number}</span>
          <span style={{ color: '#94a3b8', fontSize: 13 }}>{label}</span>
        </div>
        <button onClick={() => onCopy(content, `call_script_${number}`)} style={{ background: 'transparent', border: 'none', color: copiedField === `call_script_${number}` ? '#10b981' : '#64748b', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 6, fontSize: 12 }}>
          {copiedField === `call_script_${number}` ? <Check size={14} /> : <Copy size={14} />}Copy
        </button>
      </div>
      <div style={{ padding: 16, maxHeight: 400, overflowY: 'auto' }}>
        <div style={{ color: '#cbd5e1', fontSize: 13, lineHeight: 1.7, whiteSpace: 'pre-wrap' }}>{content}</div>
      </div>
    </div>
  );
}

function LinkedInCard({ title, content, onCopy, copiedField, fieldKey, maxChars }: { title: string; content?: string; onCopy: (t: string, f: string) => void; copiedField: string | null; fieldKey: string; maxChars?: number }) {
  if (!content) return null;
  return (
    <div style={{ background: 'rgba(15,23,42,0.6)', borderRadius: 12, border: '1px solid rgba(14,165,233,0.3)', overflow: 'hidden' }}>
      <div style={{ padding: '12px 16px', background: 'rgba(14,165,233,0.1)', borderBottom: '1px solid rgba(14,165,233,0.2)', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, color: '#0ea5e9' }}>
          <Linkedin size={16} /><span style={{ fontWeight: 600, fontSize: 14 }}>{title}</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          {maxChars && <span style={{ fontSize: 11, color: content.length > maxChars ? '#ef4444' : '#64748b' }}>{content.length}/{maxChars}</span>}
          <button onClick={() => onCopy(content, fieldKey)} style={{ background: 'transparent', border: 'none', color: copiedField === fieldKey ? '#10b981' : '#64748b', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 6, fontSize: 12 }}>
            {copiedField === fieldKey ? <Check size={14} /> : <Copy size={14} />}
          </button>
        </div>
      </div>
      <div style={{ padding: 16 }}>
        <p style={{ color: '#cbd5e1', fontSize: 13, lineHeight: 1.7, margin: 0, whiteSpace: 'pre-wrap' }}>{content}</p>
      </div>
    </div>
  );
}

function WarmupSequenceCard({ warmupJson }: { warmupJson: string }) {
  let warmup: Record<string, string[]> = {};
  try { warmup = JSON.parse(warmupJson); } catch { return null; }

  const phases: Record<string, { label: string; color: string }> = {
    'day_1_3': { label: '📅 Days 1-3: Initial Engagement', color: '#f59e0b' },
    'day_4_7': { label: '📅 Days 4-7: Build Familiarity', color: '#8b5cf6' },
    'day_8': { label: '📅 Day 8: Connect', color: '#10b981' },
    'post_connect': { label: '📅 After Connection', color: '#0ea5e9' }
  };

  return (
    <div style={{ background: 'rgba(15,23,42,0.6)', borderRadius: 12, border: '1px solid rgba(249,115,22,0.3)', overflow: 'hidden' }}>
      <div style={{ padding: '12px 16px', background: 'rgba(249,115,22,0.1)', borderBottom: '1px solid rgba(249,115,22,0.2)', display: 'flex', alignItems: 'center', gap: 10 }}>
        <span style={{ fontSize: 18 }}>🔥</span>
        <span style={{ fontWeight: 600, fontSize: 14, color: '#f59e0b' }}>LinkMatch Pro Warmup Sequence</span>
      </div>
      <div style={{ padding: 16 }}>
        {Object.entries(warmup).map(([phase, actions]) => (
          <div key={phase} style={{ marginBottom: 16 }}>
            <div style={{ fontSize: 13, fontWeight: 600, color: phases[phase]?.color || '#94a3b8', marginBottom: 8 }}>
              {phases[phase]?.label || phase}
            </div>
            <div style={{ paddingLeft: 12 }}>
              {(actions || []).map((action, idx) => (
                <div key={idx} style={{ display: 'flex', alignItems: 'flex-start', gap: 8, marginBottom: 6, fontSize: 13, color: '#cbd5e1' }}>
                  <span style={{ color: '#64748b' }}>•</span><span>{action}</span>
                </div>
              ))}
            </div>
          </div>
        ))}
        <div style={{ marginTop: 16, padding: 12, background: 'rgba(16,185,129,0.1)', borderRadius: 8, border: '1px solid rgba(16,185,129,0.2)' }}>
          <div style={{ fontSize: 12, color: '#10b981', fontWeight: 600 }}>💡 Pro Tip</div>
          <div style={{ fontSize: 12, color: '#94a3b8', marginTop: 4 }}>This warmup sequence increases acceptance rates by 40-60%.</div>
        </div>
      </div>
    </div>
  );
}
