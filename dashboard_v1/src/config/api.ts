import axios from 'axios';

export const API_BASE_URL =
  import.meta.env.VITE_API_URL ||
  import.meta.env.VITE_APEX_API_URL ||
  "https://apex-backend-i7b0.onrender.com";

export function apiUrl(path: string) {
  if (!path.startsWith("/")) path = "/" + path;
  return `${API_BASE_URL}${path}`;
}

// New: axios client for modern components
export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// New: typed API methods
export const api = {
  // Health
  health: () => apiClient.get('/health'),

  // Contacts
  getContacts: () => apiClient.get('/api/contacts'),
  getContact: (id: string) => apiClient.get(`/api/contacts/${id}`),
  
  // Enrichment
  enrichContact: (id: string) => apiClient.post(`/api/contacts/${id}/enrich`),
  
  // Outreach
  generateEmail: (id: string) => apiClient.post(`/api/contacts/${id}/generate-email`),
  generateColdcall: (id: string) => apiClient.post(`/api/contacts/${id}/generate-coldcall`),
  generateLinkedIn: (id: string) => apiClient.post(`/api/contacts/${id}/generate-linkedin`),
  generateAllContent: (id: string) => apiClient.post(`/api/contacts/${id}/generate-all-content`),
  getOutreachContent: (id: string) => apiClient.get(`/api/contacts/${id}/outreach-content`),
  
  // Call Assistant
  getCallAssistantData: (id: string) => apiClient.get(`/api/contacts/${id}/call-assistant-data`),
  
  // Stage Gate
  getStageGateStatus: (id: string) => apiClient.get(`/api/contacts/${id}/stage-gate-status`),
};

export default api;
