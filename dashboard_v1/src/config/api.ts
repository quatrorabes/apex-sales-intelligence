/**
 * APEX API Configuration - SINGLE SOURCE OF TRUTH
 * All components import from here ONLY
 * Backend: https://apex-backend-i7b0.onrender.com (FastAPI v2)
 */

export const API_BASE_URL = import.meta.env.VITE_API_URL || 
  'https://apex-backend-i7b0.onrender.com';

console.log('🔧 APEX API configured:', API_BASE_URL);

export interface Contact {
  id: string;
  hubspot_id?: string;
  first_name: string;
  last_name: string;
  email?: string;
  phone?: string;
  title?: string;
  company?: string;
  enrichment?: {
    version: string;
    raw_profile: string;
    character_count: number;
  };
  enriched_at?: string;
  created_at: string;
  updated_at: string;
}

export interface ContactsResponse {
  contacts: Contact[];
  total: number;
  limit: number;
  offset: number;
}

export interface StatsResponse {
  total_contacts: number;
  enriched_contacts: number;
  pending_enrichment: number;
}

export const API_ENDPOINTS = {
  LIST_CONTACTS: `${API_BASE_URL}/api/v2/contacts`,
  GET_CONTACT: (id: string) => `${API_BASE_URL}/api/v2/contacts/${id}`,
  STATS: `${API_BASE_URL}/api/v2/contacts/stats`,
  ENRICH_ONE: (id: string) => `${API_BASE_URL}/api/v2/contacts/${id}/enrich`,
  BULK_ENRICH: `${API_BASE_URL}/api/v2/contacts/bulk-enrich`,
  HEALTH: `${API_BASE_URL}/health`,
};

export async function httpRequest<T>(
  url: string,
  options: RequestInit = {}
): Promise<T> {
  try {
    const response = await fetch(url, {
      headers: { 'Content-Type': 'application/json' },
      ...options,
    });

    if (!response.ok) {
      const errorBody = await response.text();
      throw new Error(`HTTP ${response.status}: ${errorBody}`);
    }

    return await response.json();
  } catch (error) {
    console.error(`API Error [${options.method || 'GET'}] ${url}:`, error);
    throw error;
  }
}

export async function getContacts(
  limit: number = 50,
  offset: number = 0
): Promise<ContactsResponse> {
  const url = `${API_ENDPOINTS.LIST_CONTACTS}?limit=${limit}&offset=${offset}`;
  return httpRequest<ContactsResponse>(url);
}

export async function getContact(id: string): Promise<Contact> {
  return httpRequest<Contact>(API_ENDPOINTS.GET_CONTACT(id));
}

export async function getStats(): Promise<StatsResponse> {
  return httpRequest<StatsResponse>(API_ENDPOINTS.STATS);
}

export async function enrichContact(id: string): Promise<any> {
  return httpRequest<any>(API_ENDPOINTS.ENRICH_ONE(id), {
    method: 'POST',
    body: JSON.stringify({}),
  });
}

export async function bulkEnrich(limit: number = 10): Promise<any> {
  return httpRequest<any>(`${API_ENDPOINTS.BULK_ENRICH}?limit=${limit}`, {
    method: 'POST',
    body: JSON.stringify({}),
  });
}

export async function healthCheck(): Promise<any> {
  return httpRequest<any>(API_ENDPOINTS.HEALTH);
}
