import {
  ApexPerson,
  ApexOpportunity,
  ApexAccount,
} from './types';

// Raw contact type as returned by your existing API
export interface RawContact {
  id: number;
  name: string;
  email?: string;
  phone?: string;
  phonemobile?: string;
  company?: string;
  title?: string;
  linkedinurl?: string;
  linkedin_url?: string;
  mdcpscore?: number;
  priorityscore?: number;
  persona?: string;
  lastcontactdate?: string;
  enrichmentstatus?: string;
  urgencylevel?: string;
}

// Simple helper to map urgency / enrichment to engagement stage
export function mapEngagementStage(
  contact: RawContact,
): 'Prospect' | 'Qualified' | 'Contacted' | 'Demo' | 'Proposal' {
  const status = (contact.enrichmentstatus || '').toLowerCase();
  const urgency = (contact.urgencylevel || '').toUpperCase();

  if (status === 'completed' && urgency === 'IMMEDIATE') return 'Proposal';
  if (status === 'completed' && (urgency === 'HIGH' || urgency === 'MEDIUM'))
    return 'Demo';
  if (status === 'completed') return 'Contacted';
  if (status === 'pending') return 'Qualified';
  return 'Prospect';
}

// Map a raw contact row into ApexPerson
export function mapContactToApexPerson(contact: RawContact): ApexPerson {
  const phone =
    (contact.phonemobile && contact.phonemobile.trim()) ||
    (contact.phone && contact.phone.trim()) ||
    '';

  const linkedin =
    (contact.linkedin_url && contact.linkedin_url.trim()) ||
    (contact.linkedinurl && contact.linkedinurl.trim()) ||
    '';

  const score =
    typeof contact.priorityscore === 'number'
      ? contact.priorityscore
      : typeof contact.mdcpscore === 'number'
      ? contact.mdcpscore
      : 0;

  const companyDomain = (contact.company || '').trim();

  const signals: string[] = [];
  if (contact.persona) {
    signals.push(`Persona: ${contact.persona}`);
  }
  if (contact.enrichmentstatus) {
    signals.push(`Enrichment: ${contact.enrichmentstatus}`);
  }
  if (contact.urgencylevel) {
    signals.push(`Urgency: ${contact.urgencylevel}`);
  }

  return {
    apexPersonId: String(contact.id),
    fullName: contact.name || 'Unknown',
    emailAddress: contact.email || '',
    jobTitle: contact.title || '',
    companyDomain,
    phoneNumber: phone,
    linkedinProfile: linkedin,
    intelligenceScore: Math.max(0, Math.min(100, score || 0)),
    engagementStage: mapEngagementStage(contact),
    lastActivityDate: contact.lastcontactdate || '',
    apexSignals: signals,
  };
}

// Placeholder mappers for opportunities/accounts; wire real data later
export interface RawOpportunity {
  id: string;
  accountid: string;
  value: number;
  stage: string;
  targetclosedate?: string;
  winprobability?: number;
  salesrep?: string;
  pipelinename?: string;
  priority?: 'High' | 'Medium' | 'Low';
}

export function mapRawOppToApexOpportunity(
  opp: RawOpportunity,
): ApexOpportunity {
  return {
    apexOppId: String(opp.id),
    accountId: String(opp.accountid),
    pipelineValue: opp.value || 0,
    opportunityStage: opp.stage || 'Unknown',
    targetCloseDate: opp.targetclosedate || '',
    winProbability:
      typeof opp.winprobability === 'number' ? opp.winprobability : 0,
    salesRepId: opp.salesrep || '',
    apexPipelineName: opp.pipelinename || 'Default',
    intelligencePriority: opp.priority || 'Medium',
  };
}

export interface RawAccount {
  id: string;
  name: string;
  industry?: string;
  annualrevenue?: number;
  employeecount?: number;
  buyingsignals?: number;
  apexintelligencescore?: number;
  techstack?: string[];
}

export function mapRawAccountToApexAccount(acc: RawAccount): ApexAccount {
  return {
    apexAccountId: String(acc.id),
    accountName: acc.name || 'Unknown',
    industryVertical: acc.industry || 'Unknown',
    annualRevenue: acc.annualrevenue || 0,
    employeeCount: acc.employeecount || 0,
    buyingSignals: acc.buyingsignals || 0,
    apexIntelligenceScore: acc.apexintelligencescore || 0,
    techStack: acc.techstack || [],
  };
}
