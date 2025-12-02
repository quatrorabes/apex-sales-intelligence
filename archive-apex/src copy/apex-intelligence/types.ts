cat > dashboardv1/src/apex-intelligence/types.ts << 'EOF'
export type EngagementStage =
  | 'Prospect'
  | 'Qualified'
  | 'Contacted'
  | 'Demo'
  | 'Proposal';

export type IntelligencePriority = 'High' | 'Medium' | 'Low';

export interface ApexPerson {
  apexPersonId: string;
  fullName: string;
  emailAddress: string;
  jobTitle: string;
  companyDomain: string;
  phoneNumber: string;
  linkedinProfile: string;
  intelligenceScore: number; // 0-100
  engagementStage: EngagementStage;
  lastActivityDate: string;  // ISO date string
  apexSignals: string[];
}

export interface ApexOpportunity {
  apexOppId: string;
  accountId: string;
  pipelineValue: number;
  opportunityStage: string;
  targetCloseDate: string; // ISO date
  winProbability: number;  // 0-100
  salesRepId: string;
  apexPipelineName: string;
  intelligencePriority: IntelligencePriority;
}

export interface ApexAccount {
  apexAccountId: string;
  accountName: string;
  industryVertical: string;
  annualRevenue: number;
  employeeCount: number;
  buyingSignals: number;
  apexIntelligenceScore: number;
  techStack: string[];
}

export interface ApexPipelineFilters {
  stage: string[];
  minScore: number;
  industry: string[];
  employeeRange: [number, number];
}

export interface ApexMetrics {
  totalPipelineValue: number;
  avgIntelligenceScore: number;
  highPriorityLeads: number;
  signalVelocity: number;     // signals/hour
  conversionPotential: number;
  pipelineCoverage: number;   // days
}

export interface ApexUser {
  id: string;
  name: string;
  email: string;
  role: string;
}

export interface ApexSignal {
  id: string;
  personId?: string;
  accountId?: string;
  type: string;
  description: string;
  createdAt: string; // ISO date
}

export interface ApexRecommendation {
  id: string;
  title: string;
  description: string;
  priority: IntelligencePriority;
}

export interface ApexIntelligenceState {
  userIntelligenceProfile: ApexUser | null;
  activePipelineFilters: ApexPipelineFilters;
  aiRecommendations: ApexRecommendation[];
  realTimeSignals: ApexSignal[];
  dashboardMetrics: ApexMetrics | null;
  lastSync: string | null;
}

export interface ApexIntelligenceProps {
  persons: ApexPerson[];
  opportunities: ApexOpportunity[];
  accounts: ApexAccount[];
  metrics: ApexMetrics | null;
  selectedPerson: ApexPerson | null;
  pipelineFilters: ApexPipelineFilters;
  isLoading: boolean;
  errorMessage: string | null;
  onPersonSelect: (person: ApexPerson) => void;
  refreshIntelligenceData: () => Promise<void>;
  exportToCSV: () => void;
}
EOF
