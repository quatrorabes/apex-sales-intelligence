const API_BASE_URL = import.meta.env.VITE_API_URL || 
  (window.location.hostname === 'localhost'
    ? 'http://localhost:8000'
    : 'https://apex-backend-i7b0.onrender.com');

export const config = {
  API_BASE_URL,
  API_ENDPOINTS: {
    CONTACTS: '/api/contacts',
    CONTACT_DETAIL: (id: string) => `/api/contacts/${id}`,
    CONTACT_ENRICH_V2: (id: string) => `/api/v2/contacts/${id}/enrich`,
    ENRICHMENT_STATUS: (id: string) => `/api/v2/contacts/${id}/enrichment-status`,
    CONTACT_ICP_MATCH: (id: string) => `/api/contacts/${id}/icp-match`,
    TODAYS_BOARD: '/api/todays-board',
    BATCH_ENRICH: '/api/batch/enrich',
  }
};
