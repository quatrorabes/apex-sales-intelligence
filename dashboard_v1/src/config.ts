// API Configuration
export const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Export for use in components
export const config = {
  apiUrl: API_URL,
  isProduction: import.meta.env.PROD,
};
