const DEFAULT_API_BASE_URL = "http://localhost:8000";

export function getApiBaseUrl() {
  const value = process.env.NEXT_PUBLIC_API_BASE_URL?.trim();
  return (value && value.length > 0 ? value : DEFAULT_API_BASE_URL).replace(/\/+$/, "");
}
