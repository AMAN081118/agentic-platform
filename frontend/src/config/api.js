const trimTrailingSlashes = (value = "") => value.trim().replace(/\/+$/, "");

// In development Vite proxies API requests to the local backend. In a deployed
// build every API request must use the public backend URL, never Vercel's URL.
export const API_BASE_URL = import.meta.env.DEV
  ? ""
  : trimTrailingSlashes(import.meta.env.VITE_API_URL);

export function apiUrl(path) {
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  return `${API_BASE_URL}${normalizedPath}`;
}
