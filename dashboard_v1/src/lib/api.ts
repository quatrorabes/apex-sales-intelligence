// src/lib/api.ts - APEX Backend API Integration
const API_BASE_URL = import.meta.env.VITE_API_URL || "https://apex-backend-production-production.up.railway.app";

// Types matching your backend
export interface Contact {
  id: number;
  name: string;
  company: string;
  email?: string;
  phone?: string;
  title?: string;
  linkedin_url?: string;
  enriched: number;
  enrichment_data?: any;
  opportunity_score?: number;
  persona_name?: string;
}

export interface DashboardMetrics {
  total_contacts: number;
  total_sent: number;
  total_opens: number;
  open_rate: number;
  enriched_contacts: number;
}

// HTTP helper
async function http<T>(path: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE_URL}${path}`;
  
  try {
    const res = await fetch(url, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...(options.headers || {}),
      },
    });
    
    if (!res.ok) {
      const errorText = await res.text();
      throw new Error(`API ${res.status}: ${errorText || path}`);
    }
    
    return (await res.json()) as T;
  } catch (error) {
    console.error(`API Error: ${path}`, error);
    throw error;
  }
}

// API Endpoints
export async function getContacts(): Promise<Contact[]> {
  const response = await http<{ status: string; contacts: Contact[] }>("/api/contacts");
  return response.contacts || [];
}

export async function getDashboardMetrics(): Promise<DashboardMetrics> {
  try {
    const response = await http<{ status: string; summary: DashboardMetrics }>("/api/analytics/dashboard");
    return response.summary;
  } catch {
    // Return mock data if API fails
    return {
      total_contacts: 0,
      total_sent: 0,
      total_opens: 0,
      open_rate: 0,
      enriched_contacts: 0,
    };
  }
}

export async function enrichContact(contactId: number): Promise<{ status: string; message: string }> {
  return await http<{ status: string; message: string }>(`/api/contacts/${contactId}/enrich`, {
    method: "POST",
  });
}

export async function generateCallScript(contactId: number): Promise<any> {
  return await http<any>(`/api/v1/outreach/contacts/${contactId}/call-scripts`, {
    method: "POST",
  });
}

export async function generateEmail(contactId: number): Promise<any> {
  return await http<any>(`/api/v1/outreach/contacts/${contactId}/emails`, {
    method: "POST",
  });
}

export async function getKernelIntelligence(contactId: number): Promise<any> {
  return await http<any>(`/api/v1/outreach/contacts/${contactId}/kernel-intelligence`);
}
