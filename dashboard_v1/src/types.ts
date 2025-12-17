export interface Contact {
  id: string;  // UUID STRING - never number
  name: string;
  title: string;
  company: string;
  email?: string;
  phone?: string;
  linkedin_url?: string;
  enrichment_status?: 'pending' | 'completed' | 'failed';
  enrichment_data?: any;
  enriched_at?: string;
  mdcp_score?: number;
  priority_score?: number;
  rss_score?: number;
  unified_qualification_score?: number;
  created_at: string;
  updated_at: string;
}

export interface EnrichmentData {
  version: string;
  markdown: string;
  raw_context: Record<string, string>;
  enriched_at: string;
}

export interface EnrichmentStatus {
  enrichment_status: 'pending' | 'completed' | 'failed';
  enriched_at?: string;
}
