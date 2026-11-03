// Typed fetch wrapper: Bearer token (no cookies), one error shape {code, message, details}, 401 -> login.
const KEY = "auth_token";
let memoryToken: string | null = null;

export function getToken(): string | null {
  if (memoryToken) return memoryToken;
  try { memoryToken = sessionStorage.getItem(KEY); } catch { /* storage blocked */ }
  return memoryToken;
}

export function setToken(token: string | null): void {
  memoryToken = token;
  try { token ? sessionStorage.setItem(KEY, token) : sessionStorage.removeItem(KEY); } catch { /* storage blocked */ }
}

export class ApiError extends Error {
  constructor(public status: number, public code: string, message: string, public details?: unknown) {
    super(message);
  }
}

type Options = { method?: string; body?: unknown; skipAuthRedirect?: boolean };

export async function api<T = unknown>(path: string, opts: Options = {}): Promise<T> {
  const headers: Record<string, string> = { Accept: "application/json" };
  const token = getToken();
  if (token) headers.Authorization = `Bearer ${token}`;
  if (opts.body !== undefined) headers["Content-Type"] = "application/json";
  const res = await fetch(path, {
    method: opts.method ?? "GET",
    headers,
    body: opts.body !== undefined ? JSON.stringify(opts.body) : undefined,
  });
  if (res.status === 204) return undefined as T;
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    if (res.status === 401 && !opts.skipAuthRedirect) {
      setToken(null);
      if (location.pathname !== "/login") location.assign("/login");
    }
    throw new ApiError(res.status, data.code ?? "error", data.message ?? "요청을 처리하지 못했습니다.", data.details);
  }
  return data as T;
}
