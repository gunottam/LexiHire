/**
 * Backend URL helper.
 * - In dev, default `/api` is proxied by Vite to Flask (same origin as the UI → fewer browser blocks).
 * - Override with VITE_API_BASE_URL (e.g. http://127.0.0.1:8000) if you run without the proxy.
 */
export function apiUrl(path) {
  const p = path.startsWith("/") ? path : `/${path}`;
  const base = import.meta.env.VITE_API_BASE_URL;
  if (base != null && String(base).trim() !== "") {
    return `${String(base).replace(/\/$/, "")}${p}`;
  }
  return `/api${p}`;
}
