// ContactEnrichmentView.tsx
// Complete working version with Chat Things tab and content generation

import React, { useState, useEffect } from 'react';

interface Contact {
  id: number;
  name: string;
  email?: string;
  phone?: string;
  company?: string;
  title?: string;
  enrichment_data?: string;
  enrichment_status?: string;
  profile_content?: string;
  priority_score?: number;
  rss_score?: number;
  mdcp_score?: number;
  email_1_subject?: string;
  email_1_body?: string;
  email_2_subject?: string;
  email_2_body?: string;
  email_3_subject?: string;
  email_3_body?: string;
  call_script_1?: string;
  call_script_2?: string;
  call_script_3?: string;
  linkedin_note?: string;
  linkedin_followup?: string;
}

interface ContactEnrichmentViewProps {
  contact: Contact | null;
  onClose: () => void;
  onUpdate: () => void;
}

const ContactEnrichmentView: React.FC<ContactEnrichmentViewProps> = ({ contact, onClose, onUpdate }) => {
  const [activeTab, setActiveTab] = useState('overview');
  const [enriching, setEnriching] = useState(false);
  const [copiedField, setCopiedField] = useState<string | null>(null);
  const [generatingContent, setGeneratingContent] = useState(false);
  const [contentType, setContentType] = useState<string | null>(null);
  
  if (!contact) {
    return null;
  }
  
  const handleEnrich = async () => {
    setEnriching(true);
    
    try {
      console.log('Starting enrichment for contact:', contact.id);
      
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
        window.location.reload();
      } else {
        alert('Enrichment failed: ' + data.error);
      }
    } catch (error) {
      console.error('Enrichment error:', error);
      alert('Enrichment failed');
    } finally {
      setEnriching(false);
    }
  };
  
  const handleGenerateContent = async (type: 'email' | 'call' | 'linkedin') => {
    setGeneratingContent(true);
    setContentType(type);
    
    try {
      const response = await fetch(`http://localhost:8000/api/contacts/${contact.id}/generate-content`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ content_type: type })
      });
      
      const result = await response.json();
      
      if (result.success) {
        alert(`✅ ${type.charAt(0).toUpperCase() + type.slice(1)} content generated successfully!`);
        onUpdate();
      } else {
        alert(`❌ Content generation failed: ${result.error || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Content generation error:', error);
      alert('❌ Failed to generate content');
    } finally {
      setGeneratingContent(false);
      setContentType(null);
    }
  };

  const copyText = (text: string, field: string) => {
    navigator.clipboard.writeText(text);
    setCopiedField(field);
    setTimeout(() => setCopiedField(null), 2000);
  };

  const isPeer = ['broker', 'principal', 'ccim', 'banker', 'lender'].some(
    term => (contact.title || '').toLowerCase().includes(term)
  );

  // Parse strategic intelligence from profile_content
  const parseStrategicIntelligence = () => {
    if (!contact.profile_content) return null;

    const content = contact.profile_content;
    const intelligence = {
      painPoints: [] as string[],
      sbaInterests: [] as string[],
      keyInsights: [] as string[],
      finalNote: ''
    };

    // Extract Pain Points
    const painMatch = content.match(/Pain Points:?\s*\n([\s\S]*?)(?=\n\n[A-Z]|SBA|$)/i);
    if (painMatch) {
      intelligence.painPoints = painMatch[1]
        .split(/\n/)
        .filter(line => line.trim().match(/^[-•\d.]/))
        .map(line => line.replace(/^[-•\d.\s]+/, '').trim())
        .filter(Boolean);
    }

    // Extract SBA Financing Interests
    const sbaMatch = content.match(/SBA.*?Interest:?\s*\n([\s\S]*?)(?=\n\n[A-Z]|Key|$)/i);
    if (sbaMatch) {
      intelligence.sbaInterests = sbaMatch[1]
        .split(/\n/)
        .filter(line => line.trim().match(/^[-•\d.]/))
        .map(line => line.replace(/^[-•\d.\s]+/, '').trim())
        .filter(Boolean);
    }

    // Extract Key Insights
    const insightsMatch = content.match(/Key Insights?:?\s*\n([\s\S]*?)(?=\n\n[A-Z]|Final|$)/i);
    if (insightsMatch) {
      intelligence.keyInsights = insightsMatch[1]
        .split(/\n/)
        .filter(line => line.trim().match(/^[-•\d.]/))
        .map(line => line.replace(/^[-•\d.\s]+/, '').trim())
        .filter(Boolean);
    }

    // Extract Final Note
    const noteMatch = content.match(/Final Note:?\s*\n([\s\S]*?)$/i);
    if (noteMatch) {
      intelligence.finalNote = noteMatch[1].trim();
    }

    return intelligence;
  };

  const strategicIntel = parseStrategicIntelligence();

  return (
    <div 
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: 'rgba(0, 0, 0, 0.6)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 9999,
        backdropFilter: 'blur(4px)'
      }}
      onClick={onClose}
    >
      <div 
        style={{
          backgroundColor: 'white',
          borderRadius: '16px',
          width: '90%',
          maxWidth: '1000px',
          maxHeight: '90vh',
          overflow: 'hidden',
          boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.3)',
          display: 'flex',
          flexDirection: 'column'
        }}
        onClick={e => e.stopPropagation()}
      >
        {/* Header */}
        <div style={{
          background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
          padding: '2rem',
          color: 'white'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
            <div style={{ flex: 1 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
                <div style={{
                  padding: '0.5rem',
                  backgroundColor: 'rgba(255, 255, 255, 0.2)',
                  borderRadius: '0.5rem',
                  backdropFilter: 'blur(10px)'
                }}>
                  <span style={{ fontSize: '1.5rem' }}>👤</span>
                </div>
                <div>
                  <h2 style={{ fontSize: '1.875rem', fontWeight: 'bold', margin: 0 }}>
                    {contact.name}
                  </h2>
                  <p style={{ 
                    fontSize: '0.875rem', 
                    opacity: 0.9, 
                    margin: '0.25rem 0 0 0',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem'
                  }}>
                    {contact.title} at {contact.company}
                    {isPeer && (
                      <span style={{
                        padding: '0.125rem 0.5rem',
                        backgroundColor: 'rgba(168, 85, 247, 0.3)',
                        borderRadius: '9999px',
                        fontSize: '0.75rem'
                      }}>
                        Referral Partner
                      </span>
                    )}
                  </p>
                </div>
              </div>
              
              {/* Quick Stats */}
              {contact.priority_score !== null && contact.priority_score !== undefined && (
                <div style={{ display: 'flex', gap: '1rem', marginTop: '1rem' }}>
                  <div style={{
                    backgroundColor: 'rgba(255, 255, 255, 0.1)',
                    backdropFilter: 'blur(10px)',
                    borderRadius: '0.5rem',
                    padding: '0.5rem 1rem'
                  }}>
                    <div style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>
                      {Math.round(contact.priority_score)}
                    </div>
                    <div style={{ fontSize: '0.75rem', opacity: 0.8 }}>Priority</div>
                  </div>
                  <div style={{
                    backgroundColor: 'rgba(255, 255, 255, 0.1)',
                    backdropFilter: 'blur(10px)',
                    borderRadius: '0.5rem',
                    padding: '0.5rem 1rem'
                  }}>
                    <div style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>
                      {Math.round(contact.rss_score || 0)}
                    </div>
                    <div style={{ fontSize: '0.75rem', opacity: 0.8 }}>Role</div>
                  </div>
                  <div style={{
                    backgroundColor: 'rgba(255, 255, 255, 0.1)',
                    backdropFilter: 'blur(10px)',
                    borderRadius: '0.5rem',
                    padding: '0.5rem 1rem'
                  }}>
                    <div style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>
                      {Math.round(contact.mdcp_score || 0)}
                    </div>
                    <div style={{ fontSize: '0.75rem', opacity: 0.8 }}>Data</div>
                  </div>
                </div>
              )}
            </div>
            
            <button
              onClick={onClose}
              style={{
                padding: '0.5rem',
                backgroundColor: 'rgba(255, 255, 255, 0.2)',
                border: 'none',
                color: 'white',
                fontSize: '1.5rem',
                cursor: 'pointer',
                borderRadius: '0.5rem',
                lineHeight: 1,
                width: '40px',
                height: '40px',
                transition: 'background-color 0.2s'
              }}
              onMouseEnter={(e) => e.currentTarget.style.backgroundColor = 'rgba(255, 255, 255, 0.3)'}
              onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'rgba(255, 255, 255, 0.2)'}
            >
              ✕
            </button>
          </div>
        </div>

        {/* Tabs */}
        <div style={{ 
          backgroundColor: '#f9fafb', 
          borderBottom: '1px solid #e5e7eb'
        }}>
          <div style={{ display: 'flex', gap: '0.25rem', padding: '0.5rem' }}>
            {[
              { id: 'overview', label: 'Overview', icon: '📋' },
              { id: 'intelligence', label: 'Intelligence', icon: '🧠' },
              { id: 'chat-things', label: 'Chat Things', icon: '💬' },
              { id: 'content', label: 'Content', icon: '✍️' }
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                  padding: '0.625rem 1rem',
                  borderRadius: '0.5rem',
                  fontWeight: activeTab === tab.id ? '600' : '500',
                  fontSize: '0.875rem',
                  transition: 'all 0.2s',
                  backgroundColor: activeTab === tab.id ? 'white' : 'transparent',
                  color: activeTab === tab.id ? '#6366f1' : '#6b7280',
                  border: 'none',
                  cursor: 'pointer',
                  boxShadow: activeTab === tab.id ? '0 1px 3px 0 rgba(0, 0, 0, 0.1)' : 'none'
                }}
              >
                <span>{tab.icon}</span>
                {tab.label}
              </button>
            ))}
          </div>
        </div>

        {/* Content Area */}
        <div style={{ 
          flex: 1, 
          overflowY: 'auto', 
          padding: '1.5rem', 
          backgroundColor: '#f9fafb' 
        }}>
          
          {/* OVERVIEW TAB */}
          {activeTab === 'overview' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {/* Contact Information Card */}
              <div style={{
                backgroundColor: 'white',
                borderRadius: '0.75rem',
                padding: '1.5rem',
                boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
                border: '1px solid #e5e7eb'
              }}>
                <h3 style={{
                  fontSize: '1.125rem',
                  fontWeight: '600',
                  marginBottom: '1rem',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                  color: '#111827'
                }}>
                  <span style={{ fontSize: '1.25rem' }}>🏢</span>
                  Contact Information
                </h3>
                
                <div style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(2, 1fr)',
                  gap: '1.5rem'
                }}>
                  {[
                    { label: 'Email', value: contact.email, icon: '📧', copyable: true },
                    { label: 'Phone', value: contact.phone, icon: '📱', copyable: true },
                    { label: 'Company', value: contact.company, icon: '🏢' },
                    { label: 'Title', value: contact.title, icon: '💼' }
                  ].map(field => field.value && (
                    <div key={field.label}>
                      <label style={{
                        fontSize: '0.75rem',
                        fontWeight: '500',
                        color: '#6b7280',
                        textTransform: 'uppercase',
                        letterSpacing: '0.05em',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.375rem',
                        marginBottom: '0.5rem'
                      }}>
                        <span>{field.icon}</span>
                        {field.label}
                      </label>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <p style={{
                          margin: 0,
                          fontSize: '0.875rem',
                          fontWeight: '500',
                          color: '#111827'
                        }}>
                          {field.value}
                        </p>
                        {field.copyable && (
                          <button
                            onClick={() => copyText(field.value!, field.label)}
                            style={{
                              padding: '0.25rem',
                              border: 'none',
                              backgroundColor: 'transparent',
                              cursor: 'pointer',
                              fontSize: '1rem'
                            }}
                          >
                            {copiedField === field.label ? '✅' : '📋'}
                          </button>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Enrichment Status Card */}
              <div style={{
                background: 'linear-gradient(135deg, #f3e8ff 0%, #e0e7ff 100%)',
                borderRadius: '0.75rem',
                padding: '1.5rem',
                border: '1px solid #c4b5fd'
              }}>
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  marginBottom: '1.5rem'
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                    <div style={{
                      padding: '0.625rem',
                      backgroundColor: '#c4b5fd',
                      borderRadius: '0.5rem'
                    }}>
                      <span style={{ fontSize: '1.25rem' }}>🧠</span>
                    </div>
                    <div>
                      <h3 style={{
                        fontSize: '1rem',
                        fontWeight: '600',
                        color: '#111827',
                        margin: 0
                      }}>
                        AI Intelligence Status
                      </h3>
                      <p style={{
                        fontSize: '0.875rem',
                        color: '#6b7280',
                        margin: 0
                      }}>
                        Enhanced enrichment with strategic insights
                      </p>
                    </div>
                  </div>
                  <span style={{
                    padding: '0.375rem 0.75rem',
                    borderRadius: '9999px',
                    fontSize: '0.75rem',
                    fontWeight: '600',
                    backgroundColor: contact.enrichment_status === 'complete' ? '#d1fae5' : '#e5e7eb',
                    color: contact.enrichment_status === 'complete' ? '#065f46' : '#374151'
                  }}>
                    {contact.enrichment_status === 'complete' ? '✓ Complete' : 'Not Enriched'}
                  </span>
                </div>

                {enrichmentData && (
                  <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(3, 1fr)',
                    gap: '1rem',
                    marginBottom: '1rem'
                  }}>
                    <div style={{
                      backgroundColor: 'rgba(255, 255, 255, 0.6)',
                      backdropFilter: 'blur(10px)',
                      borderRadius: '0.5rem',
                      padding: '0.75rem',
                      textAlign: 'center'
                    }}>
                      <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#7c3aed' }}>
                        {(enrichmentData.profile_length || 0).toLocaleString()}
                      </div>
                      <div style={{ fontSize: '0.75rem', color: '#6b7280', marginTop: '0.25rem' }}>
                        Characters
                      </div>
                    </div>
                    <div style={{
                      backgroundColor: 'rgba(255, 255, 255, 0.6)',
                      backdropFilter: 'blur(10px)',
                      borderRadius: '0.5rem',
                      padding: '0.75rem',
                      textAlign: 'center'
                    }}>
                      <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#7c3aed' }}>
                        ✓
                      </div>
                      <div style={{ fontSize: '0.75rem', color: '#6b7280', marginTop: '0.25rem' }}>
                        Pain Points
                      </div>
                    </div>
                    <div style={{
                      backgroundColor: 'rgba(255, 255, 255, 0.6)',
                      backdropFilter: 'blur(10px)',
                      borderRadius: '0.5rem',
                      padding: '0.75rem',
                      textAlign: 'center'
                    }}>
                      <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#7c3aed' }}>
                        ✓
                      </div>
                      <div style={{ fontSize: '0.75rem', color: '#6b7280', marginTop: '0.25rem' }}>
                        SBA Points
                      </div>
                    </div>
                  </div>
                )}

                <button
                  onClick={handleEnrich}
                  disabled={enriching}
                  style={{
                    width: '100%',
                    padding: '0.75rem 1rem',
                    background: 'linear-gradient(135deg, #7c3aed 0%, #6366f1 100%)',
                    color: 'white',
                    borderRadius: '0.5rem',
                    fontWeight: '500',
                    border: 'none',
                    cursor: enriching ? 'not-allowed' : 'pointer',
                    opacity: enriching ? 0.5 : 1,
                    boxShadow: '0 4px 6px -1px rgba(124, 58, 237, 0.3)',
                    transition: 'all 0.2s',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '0.5rem'
                  }}
                >
                  <span>{enriching ? '⏳' : '✨'}</span>
                  {enriching ? 'Enriching with AI...' : (contact.enrichment_status === 'complete' ? 'Re-enrich Contact' : 'Enrich with Intelligence')}
                </button>
              </div>
            </div>
          )}

          {/* INTELLIGENCE TAB */}
          {activeTab === 'intelligence' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {enrichmentData || contact.profile_content ? (
                <div style={{
                  backgroundColor: 'white',
                  borderRadius: '0.75rem',
                  padding: '1.5rem',
                  boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
                  border: '1px solid #e5e7eb'
                }}>
                  <h3 style={{
                    fontSize: '1.125rem',
                    fontWeight: '600',
                    marginBottom: '1rem',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem',
                    color: '#111827'
                  }}>
                    <span style={{ fontSize: '1.25rem' }}>📄</span>
                    AI-Powered Intelligence Profile
                  </h3>
                  <div style={{
                    backgroundColor: '#f9fafb',
                    padding: '1.5rem',
                    borderRadius: '0.75rem',
                    border: '2px solid #e5e7eb',
                    maxHeight: '500px',
                    overflowY: 'auto'
                  }}>
                    <pre style={{
                      fontSize: '0.8125rem',
                      whiteSpace: 'pre-wrap',
                      margin: 0,
                      fontFamily: 'ui-monospace, monospace',
                      lineHeight: '1.6',
                      color: '#374151'
                    }}>
                      {contact.profile_content || 'No enrichment data available'}
                    </pre>
                  </div>
                </div>
              ) : (
                <div style={{
                  backgroundColor: 'white',
                  borderRadius: '0.75rem',
                  padding: '3rem 2rem',
                  textAlign: 'center'
                }}>
                  <div style={{
                    width: '80px',
                    height: '80px',
                    backgroundColor: '#e5e7eb',
                    borderRadius: '50%',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    margin: '0 auto 1.5rem',
                    fontSize: '2.5rem'
                  }}>
                    🧠
                  </div>
                  <h3 style={{
                    fontSize: '1.25rem',
                    fontWeight: '600',
                    marginBottom: '0.5rem',
                    color: '#111827'
                  }}>
                    No Intelligence Data Yet
                  </h3>
                  <p style={{ color: '#6b7280', marginBottom: '2rem' }}>
                    Enrich this contact to generate AI-powered insights
                  </p>
                  <button
                    onClick={handleEnrich}
                    style={{
                      padding: '0.75rem 2rem',
                      backgroundColor: '#7c3aed',
                      color: 'white',
                      border: 'none',
                      borderRadius: '0.5rem',
                      cursor: 'pointer',
                      fontWeight: '600',
                      fontSize: '1rem'
                    }}
                  >
                    Enrich Contact Now
                  </button>
                </div>
              )}
            </div>
          )}

          {/* CHAT THINGS TAB */}
          {activeTab === 'chat-things' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {strategicIntel && (strategicIntel.painPoints.length > 0 || strategicIntel.sbaInterests.length > 0) ? (
                <>
                  {/* Pain Points */}
                  {strategicIntel.painPoints.length > 0 && (
                    <div style={{
                      backgroundColor: 'white',
                      borderRadius: '0.75rem',
                      padding: '1.5rem',
                      boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
                      border: '1px solid #e5e7eb'
                    }}>
                      <h3 style={{
                        fontSize: '1.125rem',
                        fontWeight: '600',
                        marginBottom: '1rem',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.5rem',
                        color: '#dc2626'
                      }}>
                        <span style={{ fontSize: '1.25rem' }}>⚠️</span>
                        Pain Points
                      </h3>
                      <ul style={{
                        margin: 0,
                        paddingLeft: '1.5rem',
                        display: 'flex',
                        flexDirection: 'column',
                        gap: '0.5rem'
                      }}>
                        {strategicIntel.painPoints.map((point, idx) => (
                          <li key={idx} style={{
                            fontSize: '0.875rem',
                            color: '#374151',
                            lineHeight: '1.5'
                          }}>
                            {point}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* SBA Financing Interest */}
                  {strategicIntel.sbaInterests.length > 0 && (
                    <div style={{
                      backgroundColor: 'white',
                      borderRadius: '0.75rem',
                      padding: '1.5rem',
                      boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
                      border: '1px solid #e5e7eb'
                    }}>
                      <h3 style={{
                        fontSize: '1.125rem',
                        fontWeight: '600',
                        marginBottom: '1rem',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.5rem',
                        color: '#059669'
                      }}>
                        <span style={{ fontSize: '1.25rem' }}>💰</span>
                        SBA Financing Interest
                      </h3>
                      <ul style={{
                        margin: 0,
                        paddingLeft: '1.5rem',
                        display: 'flex',
                        flexDirection: 'column',
                        gap: '0.5rem'
                      }}>
                        {strategicIntel.sbaInterests.map((interest, idx) => (
                          <li key={idx} style={{
                            fontSize: '0.875rem',
                            color: '#374151',
                            lineHeight: '1.5'
                          }}>
                            {interest}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Key Insights */}
                  {strategicIntel.keyInsights.length > 0 && (
                    <div style={{
                      backgroundColor: 'white',
                      borderRadius: '0.75rem',
                      padding: '1.5rem',
                      boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
                      border: '1px solid #e5e7eb'
                    }}>
                      <h3 style={{
                        fontSize: '1.125rem',
                        fontWeight: '600',
                        marginBottom: '1rem',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.5rem',
                        color: '#7c3aed'
                      }}>
                        <span style={{ fontSize: '1.25rem' }}>💡</span>
                        Key Insights
                      </h3>
                      <ul style={{
                        margin: 0,
                        paddingLeft: '1.5rem',
                        display: 'flex',
                        flexDirection: 'column',
                        gap: '0.5rem'
                      }}>
                        {strategicIntel.keyInsights.map((insight, idx) => (
                          <li key={idx} style={{
                            fontSize: '0.875rem',
                            color: '#374151',
                            lineHeight: '1.5'
                          }}>
                            {insight}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Final Note */}
                  {strategicIntel.finalNote && (
                    <div style={{
                      background: 'linear-gradient(135deg, #fef3c7 0%, #fde68a 100%)',
                      borderRadius: '0.75rem',
                      padding: '1.5rem',
                      border: '2px solid #fbbf24'
                    }}>
                      <h3 style={{
                        fontSize: '1.125rem',
                        fontWeight: '600',
                        marginBottom: '0.75rem',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.5rem',
                        color: '#92400e'
                      }}>
                        <span style={{ fontSize: '1.25rem' }}>📌</span>
                        Final Note
                      </h3>
                      <p style={{
                        margin: 0,
                        fontSize: '0.875rem',
                        color: '#78350f',
                        lineHeight: '1.6'
                      }}>
                        {strategicIntel.finalNote}
                      </p>
                    </div>
                  )}
                </>
              ) : (
                <div style={{
                  backgroundColor: 'white',
                  borderRadius: '0.75rem',
                  padding: '3rem 2rem',
                  textAlign: 'center'
                }}>
                  <div style={{
                    width: '80px',
                    height: '80px',
                    background: 'linear-gradient(135deg, #c4b5fd 0%, #a5b4fc 100%)',
                    borderRadius: '50%',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    margin: '0 auto 1.5rem',
                    fontSize: '2.5rem'
                  }}>
                    💬
                  </div>
                  <h3 style={{
                    fontSize: '1.25rem',
                    fontWeight: '600',
                    marginBottom: '0.5rem',
                    color: '#111827'
                  }}>
                    No Strategic Intelligence Yet
                  </h3>
                  <p style={{ color: '#6b7280', marginBottom: '2rem' }}>
                    Enrich this contact to extract pain points, SBA interests, and key insights
                  </p>
                  <button
                    onClick={handleEnrich}
                    style={{
                      padding: '0.75rem 2rem',
                      background: 'linear-gradient(135deg, #7c3aed 0%, #6366f1 100%)',
                      color: 'white',
                      border: 'none',
                      borderRadius: '0.5rem',
                      cursor: 'pointer',
                      fontWeight: '600',
                      fontSize: '1rem',
                      boxShadow: '0 4px 6px -1px rgba(124, 58, 237, 0.3)'
                    }}
                  >
                    Generate Intelligence
                  </button>
                </div>
              )}
            </div>
          )}

          {/* CONTENT TAB */}
          {activeTab === 'content' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {/* Content Generation Buttons */}
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(3, 1fr)',
                gap: '1rem'
              }}>
                {[
                  { type: 'email', icon: '📧', label: 'Generate Email Sequence', color: '#3b82f6' },
                  { type: 'call', icon: '📞', label: 'Generate Call Scripts', color: '#10b981' },
                  { type: 'linkedin', icon: '💼', label: 'Generate LinkedIn Message', color: '#0077b5' }
                ].map(item => (
                  <button
                    key={item.type}
                    onClick={() => handleGenerateContent(item.type as any)}
                    disabled={generatingContent || !contact.profile_content}
                    style={{
                      padding: '1.5rem 1rem',
                      backgroundColor: generatingContent && contentType === item.type ? '#d1d5db' : 'white',
                      border: `2px solid ${item.color}`,
                      borderRadius: '0.75rem',
                      cursor: (generatingContent || !contact.profile_content) ? 'not-allowed' : 'pointer',
                      opacity: (!contact.profile_content) ? 0.5 : 1,
                      transition: 'all 0.2s',
                      display: 'flex',
                      flexDirection: 'column',
                      alignItems: 'center',
                      gap: '0.75rem'
                    }}
                  >
                    <span style={{ fontSize: '2rem' }}>
                      {generatingContent && contentType === item.type ? '⏳' : item.icon}
                    </span>
                    <span style={{
                      fontSize: '0.875rem',
                      fontWeight: '600',
                      color: '#111827',
                      textAlign: 'center'
                    }}>
                      {generatingContent && contentType === item.type ? 'Generating...' : item.label}
                    </span>
                  </button>
                ))}
              </div>

              {!contact.profile_content && (
                <div style={{
                  backgroundColor: '#fef3c7',
                  border: '1px solid #fbbf24',
                  borderRadius: '0.5rem',
                  padding: '1rem',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.75rem'
                }}>
                  <span style={{ fontSize: '1.5rem' }}>⚠️</span>
                  <p style={{
                    margin: 0,
                    fontSize: '0.875rem',
                    color: '#78350f'
                  }}>
                    Enrich this contact first to generate personalized content
                  </p>
                </div>
              )}

              {/* Display Generated Content */}
              {contact.email_1_subject && (
                <div style={{
                  backgroundColor: 'white',
                  borderRadius: '0.75rem',
                  padding: '1.5rem',
                  boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
                  border: '1px solid #e5e7eb'
                }}>
                  <h3 style={{
                    fontSize: '1.125rem',
                    fontWeight: '600',
                    marginBottom: '1.5rem',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem',
                    color: '#111827'
                  }}>
                    <span style={{ fontSize: '1.25rem' }}>📧</span>
                    Email Sequence
                  </h3>
                  
                  {[
                    { num: 1, subject: contact.email_1_subject, body: contact.email_1_body },
                    { num: 2, subject: contact.email_2_subject, body: contact.email_2_body },
                    { num: 3, subject: contact.email_3_subject, body: contact.email_3_body }
                  ].filter(email => email.subject).map(email => (
                    <div key={email.num} style={{
                      marginBottom: '1.5rem',
                      paddingBottom: '1.5rem',
                      borderBottom: email.num < 3 ? '1px solid #e5e7eb' : 'none'
                    }}>
                      <div style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        marginBottom: '0.75rem'
                      }}>
                        <h4 style={{
                          fontSize: '0.875rem',
                          fontWeight: '600',
                          color: '#6b7280',
                          margin: 0
                        }}>
                          Email {email.num}
                        </h4>
                        <button
                          onClick={() => copyText(`Subject: ${email.subject}\n\n${email.body}`, `email-${email.num}`)}
                          style={{
                            padding: '0.375rem 0.75rem',
                            backgroundColor: '#f3f4f6',
                            border: 'none',
                            borderRadius: '0.375rem',
                            cursor: 'pointer',
                            fontSize: '0.875rem'
                          }}
                        >
                          {copiedField === `email-${email.num}` ? '✅ Copied' : '📋 Copy'}
                        </button>
                      </div>
                      <div style={{
                        backgroundColor: '#f9fafb',
                        padding: '1rem',
                        borderRadius: '0.5rem'
                      }}>
                        <p style={{
                          margin: '0 0 0.75rem 0',
                          fontSize: '0.875rem',
                          fontWeight: '600',
                          color: '#111827'
                        }}>
                          Subject: {email.subject}
                        </p>
                        <pre style={{
                          margin: 0,
                          fontSize: '0.8125rem',
                          whiteSpace: 'pre-wrap',
                          fontFamily: 'inherit',
                          color: '#374151',
                          lineHeight: '1.6'
                        }}>
                          {email.body}
                        </pre>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {contact.call_script_1 && (
                <div style={{
                  backgroundColor: 'white',
                  borderRadius: '0.75rem',
                  padding: '1.5rem',
                  boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
                  border: '1px solid #e5e7eb'
                }}>
                  <h3 style={{
                    fontSize: '1.125rem',
                    fontWeight: '600',
                    marginBottom: '1.5rem',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem',
                    color: '#111827'
                  }}>
                    <span style={{ fontSize: '1.25rem' }}>📞</span>
                    Call Scripts
                  </h3>
                  
                  {[
                    { num: 1, title: 'Cold Call', script: contact.call_script_1 },
                    { num: 2, title: 'Follow-up Call', script: contact.call_script_2 },
                    { num: 3, title: 'Executive Briefing', script: contact.call_script_3 }
                  ].filter(call => call.script).map(call => (
                    <div key={call.num} style={{
                      marginBottom: '1.5rem',
                      paddingBottom: '1.5rem',
                      borderBottom: call.num < 3 ? '1px solid #e5e7eb' : 'none'
                    }}>
                      <div style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        marginBottom: '0.75rem'
                      }}>
                        <h4 style={{
                          fontSize: '0.875rem',
                          fontWeight: '600',
                          color: '#6b7280',
                          margin: 0
                        }}>
                          Script {call.num}: {call.title}
                        </h4>
                        <button
                          onClick={() => copyText(call.script!, `call-${call.num}`)}
                          style={{
                            padding: '0.375rem 0.75rem',
                            backgroundColor: '#f3f4f6',
                            border: 'none',
                            borderRadius: '0.375rem',
                            cursor: 'pointer',
                            fontSize: '0.875rem'
                          }}
                        >
                          {copiedField === `call-${call.num}` ? '✅ Copied' : '📋 Copy'}
                        </button>
                      </div>
                      <div style={{
                        backgroundColor: '#f9fafb',
                        padding: '1rem',
                        borderRadius: '0.5rem'
                      }}>
                        <pre style={{
                          margin: 0,
                          fontSize: '0.8125rem',
                          whiteSpace: 'pre-wrap',
                          fontFamily: 'inherit',
                          color: '#374151',
                          lineHeight: '1.6'
                        }}>
                          {call.script}
                        </pre>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {contact.linkedin_note && (
                <div style={{
                  backgroundColor: 'white',
                  borderRadius: '0.75rem',
                  padding: '1.5rem',
                  boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
                  border: '1px solid #e5e7eb'
                }}>
                  <h3 style={{
                    fontSize: '1.125rem',
                    fontWeight: '600',
                    marginBottom: '1.5rem',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem',
                    color: '#111827'
                  }}>
                    <span style={{ fontSize: '1.25rem' }}>💼</span>
                    LinkedIn Messages
                  </h3>
                  
                  <div style={{ marginBottom: '1.5rem' }}>
                    <div style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      marginBottom: '0.75rem'
                    }}>
                      <h4 style={{
                        fontSize: '0.875rem',
                        fontWeight: '600',
                        color: '#6b7280',
                        margin: 0
                      }}>
                        Connection Request
                      </h4>
                      <button
                        onClick={() => copyText(contact.linkedin_note!, 'linkedin-note')}
                        style={{
                          padding: '0.375rem 0.75rem',
                          backgroundColor: '#f3f4f6',
                          border: 'none',
                          borderRadius: '0.375rem',
                          cursor: 'pointer',
                          fontSize: '0.875rem'
                        }}
                      >
                        {copiedField === 'linkedin-note' ? '✅ Copied' : '📋 Copy'}
                      </button>
                    </div>
                    <div style={{
                      backgroundColor: '#f9fafb',
                      padding: '1rem',
                      borderRadius: '0.5rem'
                    }}>
                      <pre style={{
                        margin: 0,
                        fontSize: '0.8125rem',
                        whiteSpace: 'pre-wrap',
                        fontFamily: 'inherit',
                        color: '#374151',
                        lineHeight: '1.6'
                      }}>
                        {contact.linkedin_note}
                      </pre>
                    </div>
                  </div>

                  {contact.linkedin_followup && (
                    <div>
                      <div style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        marginBottom: '0.75rem'
                      }}>
                        <h4 style={{
                          fontSize: '0.875rem',
                          fontWeight: '600',
                          color: '#6b7280',
                          margin: 0
                        }}>
                          Follow-up Message
                        </h4>
                        <button
                          onClick={() => copyText(contact.linkedin_followup!, 'linkedin-followup')}
                          style={{
                            padding: '0.375rem 0.75rem',
                            backgroundColor: '#f3f4f6',
                            border: 'none',
                            borderRadius: '0.375rem',
                            cursor: 'pointer',
                            fontSize: '0.875rem'
                          }}
                        >
                          {copiedField === 'linkedin-followup' ? '✅ Copied' : '📋 Copy'}
                        </button>
                      </div>
                      <div style={{
                        backgroundColor: '#f9fafb',
                        padding: '1rem',
                        borderRadius: '0.5rem'
                      }}>
                        <pre style={{
                          margin: 0,
                          fontSize: '0.8125rem',
                          whiteSpace: 'pre-wrap',
                          fontFamily: 'inherit',
                          color: '#374151',
                          lineHeight: '1.6'
                        }}>
                          {contact.linkedin_followup}
                        </pre>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ContactEnrichmentView;
      