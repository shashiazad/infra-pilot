const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

async function parseError(response: Response): Promise<string> {
  const body = await response.text();
  try { return (JSON.parse(body) as { detail?: string }).detail ?? body; }
  catch { return body || `Request failed with status ${response.status}`; }
}

export async function apiGet<T>(path: string): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, { cache: "no-store" });
  if (!response.ok) throw new Error(await parseError(response));
  return response.json() as Promise<T>;
}

export async function apiPost<T>(path: string): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, { method: "POST" });
  if (!response.ok) throw new Error(await parseError(response));
  return response.json() as Promise<T>;
}
