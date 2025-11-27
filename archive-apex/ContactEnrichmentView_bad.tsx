// ContactEnrichmentView.tsx
// Complete working version - replace entire file with this

import React, { useState, useEffect } from 'react';

interface ContactEnrichmentViewProps {
  contact: any;
  onClose: () => void;
  onUpdate: () => void;
}

const ContactEnrichmentView: React.FC<ContactEnrichmentViewProps> = ({
  contact,
  onClose,
  onUpdate
}) => {
  useEffect(() => {
    if (contact?.enrichment_data) {
      try {
        const data = JSON.parse(contact.enrichment_data);
        setEnrichmentData(data);
      } catch (e) {
        console.error('Failed to parse enrichment data:', e);
      }
    }
  }, [contact]);

    if (contact?.enrichment_data) {
      try {
        const data = JSON.parse(contact.enrichment_data);
        setEnrichmentData(data);
      } catch (e) {
        console.error('Failed to parse enrichment data:', e);
      }
    }
  }, [contact]);
        

  const handleEnrich = async () => {
    setEnriching(true);
    try {
      const response = await fetch(`http://localhost:8000/api/contacts/${contact.id}/enrich`, {
        method: 'POST'
      });
      const result = await response.json();
      if (result.success) {
        alert(`✔ Enrichment complete!\nProfile: ${result.data_size?.toLocaleString()} chars`);
        onUpdate();
      } else {
        alert(`❌ Enrichment failed: ${result.error || 'Unknown error'}`);
      }
    } catch (e) {
      console.error('Enrichment error:', e);
      alert(`❌ Enrichment failed: ${e}`);
    } finally {
      setEnriching(false);
    }
  };

  const handleCopy = (field: string, value: string) => {
    navigator.clipboard.writeText(value);
    setCopiedField(field);
    setTimeout(() => setCopiedField(null), 2000);
  };

  const isPeer = contact.lifecycle_stage === 'subscriber';

  const contactFields = [
    { label: 'Name', value: contact.name, copyable: true },
    { label: 'Email', value: contact.email, copyable: true },
    { label: 'Title', value: contact.title || '—', copyable: false },
    { label: 'Company', value: contact.company || '—', copyable: false },
    { label: 'Lifecycle', value: contact.lifecycle_stage || '—', copyable: false },
    { label: 'Status', value: contact.lead_status || '—', copyable: false }
  ];

  return (
    <div className="contact-enrichment-view">
      <div className="enrichment-header">
        <div className="header-info">
          <h2>{contact.name}</h2>
          <p className="subtitle">
            {contact.title} at {contact.company}
            {isPeer && (
              <span className="peer-badge">🤝 Referral Partner</span>
            )}
          </p>
        </div>
        <button className="close-btn" onClick={onClose}>✕</button>
      </div>

      <div className="enrichment-tabs">
        <button
          className={`tab ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          Overview
        </button>
        <button
          className={`tab ${activeTab === 'enrichment' ? 'active' : ''}`}
          onClick={() => setActiveTab('enrichment')}
        >
          AI Insights
        </button>
        <button
          className={`tab ${activeTab === 'raw' ? 'active' : ''}`}
          onClick={() => setActiveTab('raw')}
        >
          Raw Data
        </button>
      </div>

      <div className="enrichment-content">
        {activeTab === 'overview' && (
          <div className="overview-tab">
            <div className="contact-details">
              <h3>Contact Information</h3>
              <div className="details-grid">
                {contactFields.map((field) => (
                  <div key={field.label} className="detail-field">
                    <label>{field.label}</label>
                    <div className="field-value">
                      <span>{field.value}</span>
                      {field.copyable && (
                        <button
                          className="copy-btn"
                          onClick={() => handleCopy(field.label, field.value)}
                          title="Copy to clipboard"
                        >
                          {copiedField === field.label ? '✓' : '📋'}
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="enrichment-status">
              <h3>Enrichment Status</h3>
              {enrichmentData ? (
                <div className="status-enriched">
                  <span className="status-icon">✓</span>
                  <span>Contact enriched with AI insights</span>
                </div>
              ) : (
                <div className="status-not-enriched">
                  <span className="status-icon">○</span>
                  <span>Not enriched yet</span>
                </div>
              )}
              <button
                className="btn-enrich"
                onClick={handleEnrich}
                disabled={enriching}
              >
                {enriching ? 'Enriching...' : enrichmentData ? 'Re-Enrich' : 'Enrich Contact'}
              </button>
            </div>
          </div>
        )}

        {activeTab === 'enrichment' && (
          <div className="enrichment-tab">
            <h3>Enhanced enrichment with strategic insights</h3>
            {enrichmentData ? (
              <div className="enrichment-insights">
                <pre>{enrichmentData.perplexity_insights || enrichmentData.full_profile_text || 'No enrichment data available'}</pre>
              </div>
            ) : (
              <div className="empty-state">
                <p>Enrich this contact to generate AI-powered insights</p>
                <p className="help-text">
                  Pain points, SBA interest analysis, and key conversation insights will appear here after enrichment
                </p>
                {!enrichmentData && (
                  <button
                    className="btn-enrich-primary"
                    onClick={handleEnrich}
                    disabled={enriching}
                  >
                    {enriching ? 'Enriching...' : 'Enrich Now'}
                  </button>
                )}
              </div>
            )}
          </div>
        )}

        {activeTab === 'raw' && (
          <div className="raw-tab">
            <h3>Raw Enrichment Data</h3>
            {enrichmentData ? (
              <pre className="raw-data">{JSON.stringify(enrichmentData, null, 2)}</pre>
            ) : (
              <p>No enrichment data available</p>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default ContactEnrichmentView;
