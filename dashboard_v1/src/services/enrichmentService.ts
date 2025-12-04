/**
 * APEX Enrichment Service
 * Handles contact enrichment API calls
 */

import { API_ENDPOINTS } from '../config/api';

export interface EnrichmentStatus {
  contact_id: number;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  last_enriched?: string;
  mdcp_score?: number;
  priority_score?: number;
  why_now?: string;
  error?: string;
}

export interface EnrichmentResponse {
  success: boolean;
  message?: string;
  contact_id: number;
  status: string;
  data?: {
    mdcp_score?: number;
    priority_score?: number;
    why_now?: string;
    enrichment_data?: any;
  };
}

class EnrichmentService {
  /**
   * Trigger enrichment for a single contact
   */
  async enrichContact(contactId: number): Promise<EnrichmentResponse> {
    const response = await fetch(API_ENDPOINTS.enrichContact(contactId), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Enrichment failed: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Get enrichment status for a contact
   */
  async getEnrichmentStatus(contactId: number): Promise<EnrichmentStatus> {
    const response = await fetch(API_ENDPOINTS.enrichmentStatus(contactId));

    if (!response.ok) {
      throw new Error(`Failed to get status: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Poll enrichment status until complete
   */
  async waitForEnrichment(
    contactId: number,
    onProgress?: (status: EnrichmentStatus) => void,
    maxAttempts = 60
  ): Promise<EnrichmentStatus> {
    for (let i = 0; i < maxAttempts; i++) {
      const status = await this.getEnrichmentStatus(contactId);
      
      if (onProgress) {
        onProgress(status);
      }

      if (status.status === 'completed' || status.status === 'failed') {
        return status;
      }

      // Wait 2 seconds before next poll
      await new Promise(resolve => setTimeout(resolve, 2000));
    }

    throw new Error('Enrichment timeout');
  }
}

export default new EnrichmentService();