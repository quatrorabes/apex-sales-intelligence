// src/hooks/useApi.ts
export const useApi = () => {
  const api = import.meta.env.VITE_API_URL;
  const post = async (url: string, body = {}) =>
    fetch(`${api}${url}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    }).then(res => res.json());
  return { post };
};
