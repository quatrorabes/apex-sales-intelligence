// Centralized API configuration for Dashboard_v1
// Reads from environment variables with local fallback

export const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Helper for building API endpoints
export const apiEndpoint = (path: string): string => `${API_URL}${path}`;
