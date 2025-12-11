/**
 * APEX Enrichment Schema v1.0
 * Mirrors backend Python schema exactly
 */

// =============================================================================
// PROFESSIONAL PROFILE
// =============================================================================
export interface CurrentRole {
  title: string;
  company: string;
  tenure?: string;
  responsibilities: string[];
}

export interface CareerTrajectory {
  previous_roles: string[];
  industry_experience: string[];
  expertise_areas: string[];
}

export interface ProfessionalProfile {
  executive_summary: string;
  current_role: CurrentRole;
  career_trajectory: CareerTrajectory;
  education: string[];
  achievements: string[];
  community_involvement: string[];
}

// =============================================================================
// COMPANY INTELLIGENCE
// =============================================================================
export interface CompanyOverview {
  name: string;
  industry: string;
  business_model: string;
  founded?: string;
  headquarters?: string;
  employee_count?: string;
}

export interface CompanyFinancials {
  revenue?: string;
  growth_rate?: string;
  funding?: string;
  key_metrics: string[];
}

export interface MarketPosition {
  target_market: string;
  competitive_advantages: string[];
  competitors: string[];
}

export interface CompanyIntelligence {
  overview: CompanyOverview;
  financials?: CompanyFinancials;
  market_position: MarketPosition;
  recent_news: string[];
  strategic_priorities: string[];
}

// =============================================================================
// SALES INTELLIGENCE
// =============================================================================
export interface PainPoint {
  title: string;
  description: string;
  priority: 'high' | 'medium' | 'low';
}

export interface Opportunity {
  title: string;
  description: string;
  alignment: string;
}

export interface Objection {
  objection: string;
  response: string;
}

export interface SalesIntelligence {
  match_score: number;
  match_reasoning: string;
  pain_points: PainPoint[];
  opportunities: Opportunity[];
  buying_triggers: string[];
  decision_factors: string[];
  objections: Objection[];
  why_now: string;
  why_us: string;
}

// =============================================================================
// PERSONALITY PROFILE
// =============================================================================
export interface MBTIDimension {
  dimension: string;
  preference: string;
  evidence: string;
}

export interface MBTI {
  type: string;
  dimensions: MBTIDimension[];
}

export interface DISC {
  primary: string;
  secondary?: string;
}

export interface CommunicationStyle {
  preferences: string[];
  dos: string[];
  donts: string[];
}

export interface PersonalityProfile {
  mbti?: MBTI;
  disc?: DISC;
  communication_style: CommunicationStyle;
  best_opening_approach: string;
}

// =============================================================================
// OUTREACH ASSETS
// =============================================================================
export interface CallScript {
  level: number;
  script: string;
}

export interface EmailTemplate {
  type: 'initial' | 'followup' | 'breakup';
  subject: string;
  body: string;
}

export interface OutreachAssets {
  talking_points: string[];
  call_scripts: CallScript[];
  email_templates: EmailTemplate[];
  linkedin_message?: string;
  voicemail_script?: string;
}

// =============================================================================
// MAIN ENRICHMENT DATA
// =============================================================================
export interface EnrichmentData {
  version: string;
  generated_at: string;
  professional: ProfessionalProfile;
  company: CompanyIntelligence;
  sales: SalesIntelligence;
  personality: PersonalityProfile;
  outreach: OutreachAssets;
}

// =============================================================================
// CONTACT
// =============================================================================
export interface Contact {
  id: string;
  hubspot_id?: string;
  first_name: string;
  last_name: string;
  email?: string;
  phone?: string;
  title?: string;
  company?: string;
  enrichment?: EnrichmentData;
  created_at: string;
  updated_at: string;
  enriched_at?: string;
}
