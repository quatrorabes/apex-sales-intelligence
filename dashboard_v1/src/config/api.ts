// APEX API Configuration - FIXED Dec 16 2025
export const API_BASE_URL =
  import.meta.env.VITE_API_URL ||
  import.meta.env.VITE_APEX_API_URL ||
  'https://apex-backend-i7b0.onrender.com';

export function apiUrl(path: string) {
  return `${API_BASE_URL}${path}`;
}

export default {
  APIBASEURL: API_BASE_URL,
  apiUrl,
  baseURL: API_BASE_URL,
};
