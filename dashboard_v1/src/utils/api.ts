import { API_URL } from '../config';
import type { Contact, TodaysBoardData } from '../types';

class ApexApiClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const defaultOptions: RequestInit = {
      headers: { 'Content-Type': 'application/json' },
      ...options,
    };

    try {
      const response = await fetch(url, defaultOptions);
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || errorData.error || response.statusText);
      }
      return await response.json();
    } catch (error) {
      console.error(`API request failed: ${endpoint}`, error);
      throw error;
    }
  }

  async getHealth() { return this.request('/api/health'); }
  
  async getContacts(params?: { limit?: number; offset?: number; search?: string }) {
    const queryParams = new URLSearchParams();
    if (params?.limit) queryParams.append('limit', params.limit.toString());
    if (params?.offset) queryParams.append('offset', params.offset.toString());
    if (params?.search) queryParams.append('search', params.search);
    const query = queryParams.toString() ? `?${queryParams.toString()}` : '';
    return this.request<{ contacts: Contact[]; total: number }>(`/api/contacts${query}`);
  }
  
  async getContact(id: number) { 
    return this.request<Contact>(`/api/contacts/${id}`); 
  }
  
  async enrichContact(id: number) {
    return this.request(`/api/contacts/${id}/enrich`, { 
      method: 'POST', 
      body: JSON.stringify({}) 
    });
  }
  
  async scoreContact(id: number) {
    return this.request(`/api/contacts/${id}/score`, { 
      method: 'POST', 
      body: JSON.stringify({}) 
    });
  }
  
  async getTodaysBoard() { 
    return this.request<TodaysBoardData>('/api/todays-board'); 
  }
  
  async importFromHubSpot() {
    return this.request('/api/hubspot/import', { 
      method: 'POST', 
      body: JSON.stringify({}) 
    });
  }
  
  async generateCallScript(contactId: number, data?: any) {
    return this.request(`/api/contacts/${contactId}/generate-call-script`, {
      method: 'POST', 
      body: JSON.stringify(data || {})
    });
  }
  
  async generateLinkedInMessage(contactId: number, data?: any) {
    return this.request(`/api/contacts/${contactId}/generate-linkedin`, {
      method: 'POST', 
      body: JSON.stringify(data || {})
    });
  }
  
  async generateEmail(contactId: number, data?: any) {
    return this.request(`/api/contacts/${contactId}/generate-email`, {
      method: 'POST', 
      body: JSON.stringify(data || {})
    });
  }
  
  async getWhyMe(contactId: number) { 
    return this.request(`/api/contacts/${contactId}/why-me`); 
  }
}

export const apiClient = new ApexApiClient(API_URL);

export async function retryAsync<T>(
  fn: () => Promise<T>,
  maxRetries: number = 3,
  delayMs: number = 500
): Promise<T> {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn();
    } catch (error) {
      if (i === maxRetries - 1) throw error;
      const backoff = delayMs * Math.pow(2, i);
      await new Promise((resolve) => setTimeout(resolve, backoff));
    }
  }
  throw new Error('Retry exhausted');
}

export default apiClient;
