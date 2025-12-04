/**
 * APEX Enrichment Service
 * Handles contact enrichment API calls
 */

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

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
  message: string;
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
    const response = await fetch(`${API_BASE}/api/contacts/${contactId}/enrich`, {
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
    const response = await fetch(`${API_BASE}/api/contacts/${contactId}/enrichment-status`);

    if (!response.ok) {
      throw new Error(`Failed to get status: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Batch enrich multiple contacts
   */
  async enrichBatch(contactIds: number[]): Promise<{
    success: boolean;
    queued: number;
    message: string;
  }> {
    const response = await fetch(`${API_BASE}/api/contacts/enrich-batch`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ contact_ids: contactIds }),
    });

    if (!response.ok) {
      throw new Error(`Batch enrichment failed: ${response.statusText}`);
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