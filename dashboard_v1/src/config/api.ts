// APEX Dashboard_v1 API Configuration
// Backend: top-level api.py (port 8000)

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const ApexEndpoints = {
  // Contact Detail - single contact
  contactDetail: (id: number) => `${API_BASE_URL}/api/contacts/${id}`,
  
  // Contacts List
  contacts: `${API_BASE_URL}/api/contacts`,
  contactsV2: (limit = 50, offset = 0) => `${API_BASE_URL}/api/contacts?limit=${limit}&offset=${offset}`,
  
  // Enrichment
  enrichContact: (id: number) => `${API_BASE_URL}/api/contacts/${id}/enrich`,
  enrichmentStatus: (id: number) => `${API_BASE_URL}/api/contacts/${id}/enrichment-status`,
  batchEnrich: `${API_BASE_URL}/api/contacts/enrich-and-score/batch`,
  
  // Scoring
  scoreContact: (id: number) => `${API_BASE_URL}/api/contacts/${id}/score`,
  batchRescore: `${API_BASE_URL}/api/contacts/score/batch`,
  apexScores: `${API_BASE_URL}/api/apex-scores`,
  
  // Dashboard
  todaysBoard: `${API_BASE_URL}/api/todays-board`,
  analytics: `${API_BASE_URL}/api/analytics`,
  analyticsDashboard: `${API_BASE_URL}/api/analytics/dashboard`,
  contactDashboard: (id: number) => `${API_BASE_URL}/api/dashboard/${id}`,
  
  // ICP & Qualification
  icpMatch: (id: number) => `${API_BASE_URL}/api/contacts/${id}/icp-match`,
  qualifyBant: (id: number) => `${API_BASE_URL}/api/contacts/${id}/qualify/bant`,
  qualifySpice: (id: number) => `${API_BASE_URL}/api/contacts/${id}/qualify/spice`,
  qualificationReport: (id: number) => `${API_BASE_URL}/api/v2/contacts/${id}/qualification-report`,
  
  // Content Generation
  generateEmail: (id: number) => `${API_BASE_URL}/api/contacts/${id}/generate-email`,
  generateCallScript: (id: number) => `${API_BASE_URL}/api/contacts/${id}/generate-call-script`,
  generateLinkedIn: (id: number) => `${API_BASE_URL}/api/contacts/${id}/generate-linkedin`,
  
  // Lists & Queues
  smartLists: `${API_BASE_URL}/api/smart-lists`,
  coldCallQueue: `${API_BASE_URL}/api/cold-call/queue`,
  
  // Enrollments
  enrollContact: (id: number) => `${API_BASE_URL}/api/contacts/${id}/enroll`,
  enrollments: (id: number) => `${API_BASE_URL}/api/contacts/${id}/enrollments`,
  
  // Health
  health: `${API_BASE_URL}/health`,
};

export default API_BASE_URL;
