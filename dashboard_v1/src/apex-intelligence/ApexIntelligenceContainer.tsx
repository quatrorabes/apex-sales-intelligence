import React, { useState, useEffect, useCallback } from 'react';
import {
  ApexPerson,
  ApexOpportunity,
  ApexAccount,
  ApexMetrics,
  ApexPipelineFilters,
} from './types';
import { mapContactToApexPerson, RawContact } from './apexDataAdapter';

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

const defaultFilters: ApexPipelineFilters = {
  stage: [],
  minScore: 0,
  industry: [],
  employeeRange: [0, 100000],
};

export default function ApexIntelligenceContainer() {
  const [persons, setPersons] = useState<ApexPerson[]>([]);
  const [opportunities, setOpportunities] = useState<ApexOpportunity[]>([]);
  const [accounts, setAccounts] = useState<ApexAccount[]>([]);
  const [metrics, setMetrics] = useState<ApexMetrics | null>(null);
  const [selectedPerson, setSelectedPerson] = useState<ApexPerson | null>(null);
  const [pipelineFilters, setPipelineFilters] =
    useState<ApexPipelineFilters>(defaultFilters);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const refreshIntelligenceData = useCallback(async () => {
    try {
      setIsLoading(true);
      setErrorMessage(null);

      console.log('[ApexIntelligenceContainer] Fetching contacts from:', `${API_BASE}/api/contacts?limit=200`);

      const contactsRes = await fetch(`${API_BASE}/api/contacts?limit=200`);
      if (!contactsRes.ok) {
        throw new Error(`Contacts API failed: ${contactsRes.status}`);
      }

      const raw = await contactsRes.json();
      console.log('[ApexIntelligenceContainer] Raw API response:', raw);

      // Handle both formats: {contacts: [...]} or bare array [...]
      const contactsJson: RawContact[] = raw.contacts || raw || [];
      console.log('[ApexIntelligenceContainer] Parsed contacts count:', contactsJson.length);

      if (contactsJson.length === 0) {
        console.warn('[ApexIntelligenceContainer] No contacts returned from API');
      }

      const mappedPersons: ApexPerson[] = contactsJson.map(mapContactToApexPerson);
      console.log('[ApexIntelligenceContainer] Mapped persons count:', mappedPersons.length);

      setPersons(mappedPersons);

      // Placeholder data
      setOpportunities([]);
      setAccounts([]);
      setMetrics({
        totalPipelineValue: 0,
        avgIntelligenceScore:
          mappedPersons.length > 0
            ? mappedPersons.reduce(
                (sum, p) => sum + (p.intelligenceScore || 0),
                0,
              ) / mappedPersons.length
            : 0,
        highPriorityLeads: mappedPersons.filter(
          (p) => p.intelligenceScore >= 80,
        ).length,
        signalVelocity: 0,
        conversionPotential: 0,
        pipelineCoverage: 0,
      });
    } catch (err: any) {
      console.error('[ApexIntelligenceContainer] Failed to load:', err);
      setErrorMessage(err.message || 'Failed to load Apex intelligence');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    refreshIntelligenceData();
  }, [refreshIntelligenceData]);

  const exportToCSV = () => {
    const header = [
      'apexPersonId',
      'fullName',
      'emailAddress',
      'jobTitle',
      'companyDomain',
      'phoneNumber',
      'linkedinProfile',
      'intelligenceScore',
      'engagementStage',
      'lastActivityDate',
    ];
    const rows = persons.map((p) =>
      [
        p.apexPersonId,
        p.fullName,
        p.emailAddress,
        p.jobTitle,
        p.companyDomain,
        p.phoneNumber,
        p.linkedinProfile,
        p.intelligenceScore,
        p.engagementStage,
        p.lastActivityDate,
      ].join(','),
    );
    const csv = [header.join(','), ...rows].join('\n');
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'apex_intelligence_persons.csv';
    a.click();
    URL.revokeObjectURL(url);
  };

  if (isLoading) {
    return (
      <div style={{ padding: 32, color: '#e5e7eb', textAlign: 'center' }}>
        <div style={{ fontSize: 18, fontWeight: 600, marginBottom: 8 }}>
          Loading Apex Intelligence...
        </div>
        <div style={{ fontSize: 14, color: '#9ca3af' }}>
          Fetching from {API_BASE}
        </div>
      </div>
    );
  }

  if (errorMessage) {
    return (
      <div style={{ padding: 32, color: '#f87171', textAlign: 'center' }}>
        <div style={{ fontSize: 18, fontWeight: 600, marginBottom: 8 }}>
          Error loading Apex Intelligence
        </div>
        <div style={{ fontSize: 14, marginBottom: 16 }}>{errorMessage}</div>
        <button
          onClick={refreshIntelligenceData}
          style={{
            padding: '10px 20px',
            borderRadius: 8,
            border: '1px solid #f87171',
            background: 'rgba(248,113,113,0.1)',
            color: '#f87171',
            cursor: 'pointer',
            fontWeight: 600,
          }}
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div style={{ padding: 24 }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <div>
          <h2 style={{ fontSize: 24, fontWeight: 700, color: '#e5e7eb', marginBottom: 4 }}>
            Apex Intelligence
          </h2>
          <p style={{ fontSize: 14, color: '#9ca3af' }}>
            {persons.length} persons loaded • Avg score: {metrics?.avgIntelligenceScore.toFixed(1) || 0}
          </p>
        </div>
        <div style={{ display: 'flex', gap: 12 }}>
          <button
            onClick={refreshIntelligenceData}
            style={{
              padding: '10px 16px',
              borderRadius: 8,
              border: '1px solid rgba(99,102,241,0.5)',
              background: 'rgba(99,102,241,0.1)',
              color: '#a5b4fc',
              cursor: 'pointer',
              fontWeight: 600,
              fontSize: 14,
            }}
          >
            Refresh
          </button>
          <button
            onClick={exportToCSV}
            style={{
              padding: '10px 16px',
              borderRadius: 8,
              border: '1px solid rgba(34,197,94,0.5)',
              background: 'rgba(34,197,94,0.1)',
              color: '#4ade80',
              cursor: 'pointer',
              fontWeight: 600,
              fontSize: 14,
            }}
          >
            Export CSV
          </button>
        </div>
      </div>

      {/* Stats */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: 16, marginBottom: 24 }}>
        <div style={{ background: 'rgba(99,102,241,0.1)', border: '1px solid rgba(99,102,241,0.3)', borderRadius: 12, padding: 16 }}>
          <div style={{ fontSize: 28, fontWeight: 700, color: '#818cf8' }}>{persons.length}</div>
          <div style={{ fontSize: 13, color: '#9ca3af' }}>Total Persons</div>
        </div>
        <div style={{ background: 'rgba(34,197,94,0.1)', border: '1px solid rgba(34,197,94,0.3)', borderRadius: 12, padding: 16 }}>
          <div style={{ fontSize: 28, fontWeight: 700, color: '#4ade80' }}>{metrics?.highPriorityLeads || 0}</div>
          <div style={{ fontSize: 13, color: '#9ca3af' }}>High Priority (80+)</div>
        </div>
        <div style={{ background: 'rgba(251,191,36,0.1)', border: '1px solid rgba(251,191,36,0.3)', borderRadius: 12, padding: 16 }}>
          <div style={{ fontSize: 28, fontWeight: 700, color: '#fbbf24' }}>{metrics?.avgIntelligenceScore.toFixed(1) || 0}</div>
          <div style={{ fontSize: 13, color: '#9ca3af' }}>Avg Score</div>
        </div>
      </div>

      {/* Person List */}
      {persons.length === 0 ? (
        <div style={{ padding: 48, textAlign: 'center', background: 'rgba(30,41,59,0.5)', borderRadius: 12, border: '1px solid rgba(148,163,184,0.2)' }}>
          <div style={{ fontSize: 18, fontWeight: 600, color: '#e5e7eb', marginBottom: 8 }}>
            No contacts found
          </div>
          <div style={{ fontSize: 14, color: '#9ca3af' }}>
            Import contacts from HubSpot or check your API connection.
          </div>
        </div>
      ) : (
        <div style={{ background: 'rgba(15,23,42,0.9)', borderRadius: 12, border: '1px solid rgba(148,163,184,0.2)', overflow: 'hidden' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid rgba(148,163,184,0.2)', background: 'rgba(30,41,59,0.5)' }}>
                <th style={{ padding: '14px 16px', textAlign: 'left', fontSize: 12, fontWeight: 600, color: '#9ca3af' }}>Name</th>
                <th style={{ padding: '14px 16px', textAlign: 'left', fontSize: 12, fontWeight: 600, color: '#9ca3af' }}>Title</th>
                <th style={{ padding: '14px 16px', textAlign: 'left', fontSize: 12, fontWeight: 600, color: '#9ca3af' }}>Company</th>
                <th style={{ padding: '14px 16px', textAlign: 'left', fontSize: 12, fontWeight: 600, color: '#9ca3af' }}>Score</th>
                <th style={{ padding: '14px 16px', textAlign: 'left', fontSize: 12, fontWeight: 600, color: '#9ca3af' }}>Stage</th>
              </tr>
            </thead>
            <tbody>
              {persons.slice(0, 50).map((p) => (
                <tr
                  key={p.apexPersonId}
                  onClick={() => setSelectedPerson(p)}
                  style={{
                    borderBottom: '1px solid rgba(148,163,184,0.1)',
                    cursor: 'pointer',
                    background: selectedPerson?.apexPersonId === p.apexPersonId ? 'rgba(99,102,241,0.15)' : 'transparent',
                  }}
                >
                  <td style={{ padding: '14px 16px' }}>
                    <div style={{ fontWeight: 600, color: '#e5e7eb', fontSize: 14 }}>{p.fullName}</div>
                    <div style={{ fontSize: 12, color: '#9ca3af' }}>{p.emailAddress || 'No email'}</div>
                  </td>
                  <td style={{ padding: '14px 16px', fontSize: 13, color: '#cbd5e1' }}>{p.jobTitle || '-'}</td>
                  <td style={{ padding: '14px 16px', fontSize: 13, color: '#cbd5e1' }}>{p.companyDomain || '-'}</td>
                  <td style={{ padding: '14px 16px' }}>
                    <span style={{
                      padding: '4px 10px',
                      borderRadius: 8,
                      fontSize: 13,
                      fontWeight: 700,
                      color: p.intelligenceScore >= 80 ? '#22c55e' : p.intelligenceScore >= 50 ? '#fbbf24' : '#9ca3af',
                      background: p.intelligenceScore >= 80 ? 'rgba(34,197,94,0.15)' : p.intelligenceScore >= 50 ? 'rgba(251,191,36,0.15)' : 'rgba(148,163,184,0.15)',
                    }}>
                      {p.intelligenceScore.toFixed(0)}
                    </span>
                  </td>
                  <td style={{ padding: '14px 16px', fontSize: 13, color: '#a5b4fc' }}>{p.engagementStage}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {persons.length > 50 && (
            <div style={{ padding: 16, textAlign: 'center', fontSize: 13, color: '#9ca3af', borderTop: '1px solid rgba(148,163,184,0.2)' }}>
              Showing 50 of {persons.length} persons
            </div>
          )}
        </div>
      )}
    </div>
  );
}
