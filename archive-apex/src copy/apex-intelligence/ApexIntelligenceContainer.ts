
import React, { useEffect, useState, useCallback } from 'react';
import {
  ApexPerson,
  ApexOpportunity,
  ApexAccount,
  ApexMetrics,
  ApexPipelineFilters,
  ApexIntelligenceState,
} from './types';
import { PersonTable } from './PersonTable'; // adjust paths
// import other views: PipelineView, AccountGrid, SummaryDashboard, etc.

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

const defaultFilters: ApexPipelineFilters = {
  stage: [],
  minScore: 0,
  industry: [],
  employeeRange: [0, 100000],
};

export function ApexIntelligenceContainer() {
  const [persons, setPersons] = useState<ApexPerson[]>([]);
  const [opportunities, setOpportunities] = useState<ApexOpportunity[]>([]);
  const [accounts, setAccounts] = useState<ApexAccount[]>([]);
  const [metrics, setMetrics] = useState<ApexMetrics | null>(null);
  const [selectedPerson, setSelectedPerson] = useState<ApexPerson | null>(null);
  const [pipelineFilters, setPipelineFilters] =
    useState<ApexPipelineFilters>(defaultFilters);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const fetchIntelligenceData = useCallback(async () => {
    try {
      setIsLoading(true);
      setErrorMessage(null);

      // TODO: replace with your real endpoints
      const [contactsRes, oppsRes, accountsRes, metricsRes] = await Promise.all([
        fetch(`${API_BASE}/api/apex/persons`),
        fetch(`${API_BASE}/api/apex/opportunities`),
        fetch(`${API_BASE}/api/apex/accounts`),
        fetch(`${API_BASE}/api/apex/metrics`),
      ]);

      if (!contactsRes.ok || !oppsRes.ok || !accountsRes.ok || !metricsRes.ok) {
        throw new Error('One or more Apex API calls failed');
      }

      const personsJson = await contactsRes.json();
      const oppsJson = await oppsRes.json();
      const accountsJson = await accountsRes.json();
      const metricsJson = await metricsRes.json();

      setPersons(personsJson.persons ?? personsJson);
      setOpportunities(oppsJson.opportunities ?? oppsJson);
      setAccounts(accountsJson.accounts ?? accountsJson);
      setMetrics(metricsJson.metrics ?? metricsJson);
    } catch (err: any) {
      console.error('Failed to load Apex intelligence:', err);
      setErrorMessage(err.message ?? 'Failed to load Apex intelligence');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchIntelligenceData();
  }, [fetchIntelligenceData]);

  const exportToCSV = () => {
    // Placeholder; wire later
    console.log('Exporting Apex intelligence to CSV...');
  };

  if (isLoading) {
    return (
      <div style={{ padding: 32, color: '#e5e7eb' }}>
        Loading Apex Intelligence...
      </div>
    );
  }

  if (errorMessage) {
    return (
      <div style={{ padding: 32, color: '#f87171' }}>
        Error: {errorMessage}
      </div>
    );
  }

  return (
    <div style={{ padding: 24 }}>
      {/* Example: render the person table for now */}
      <PersonTable
        persons={persons}
        onPersonSelect={(p) => setSelectedPerson(p)}
      />
      {/* Later: add PipelineView, AccountGrid, SummaryDashboard, etc. */}
    </div>
  );
}

