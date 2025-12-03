const isDevelopment = import.meta.env.MODE === 'development';
const isLocalhost = typeof window !== 'undefined' && window.location.hostname === 'localhost';

export const API_URL = import.meta.env.VITE_API_URL || (
  isDevelopment || isLocalhost
    ? 'http://localhost:8000'
    : 'https://apex-intelligence-production.up.railway.app'
);

export const API_BASE = API_URL;

export const config = {
  API_BASE_URL: API_URL,
  ENDPOINTS: {
    HEALTH: '/api/health',
    CONTACTS: '/api/contacts',
    CONTACT_DETAIL: (id: number) => `/api/contacts/${id}`,
    CONTACT_ENRICH: (id: number) => `/api/contacts/${id}/enrich`,
    CONTACT_SCORE: (id: number) => `/api/contacts/${id}/score`,
    TODAYS_BOARD: '/api/todays-board',
    HUBSPOT_IMPORT: '/api/hubspot/import',
  },
  REFRESH_INTERVALS: {
    TODAYS_BOARD: 300000,
    CONTACTS_LIST: 600000,
  },
};

export default config;
