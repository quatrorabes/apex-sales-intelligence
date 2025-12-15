export const API_BASE_URL =
  import.meta.env.VITE_API_URL ||
  import.meta.env.VITE_APEX_API_URL ||
  "https://apex-backend-i7b0.onrender.com";

export function apiUrl(path: string) {
  if (!path.startsWith("/")) path = "/" + path;
  return `${API_BASE_URL}${path}`;
}
