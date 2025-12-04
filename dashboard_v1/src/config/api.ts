/**
 * APEX API Configuration
 * Centralized API endpoint management
 */

export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const API_ENDPOINTS = {
  health: `${API_BASE_URL}/api/health`,
  contacts: `${API_BASE_URL}/api/contacts`,
  todaysBoard: `${API_BASE_URL}/api/todays-board`,
  enrichContact: (id: number) => `${API_BASE_URL}/api/contacts/${id}/enrich`,
  enrichmentStatus: (id: number) => `${API_BASE_URL}/api/contacts/${id}/enrichment-status`,
  hubspotImport: `${API_BASE_URL}/api/hubspot/import`,
};

export default API_BASE_URL;