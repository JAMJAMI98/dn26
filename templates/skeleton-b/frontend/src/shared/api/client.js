// fetch wrapper: Bearer token (no cookies), one error shape {code, message, details}, 401 -> login.
const KEY = "auth_token";
let memoryToken = null;

export function getToken() {
  if (memoryToken) return memoryToken;
  try { memoryToken = sessionStorage.getItem(KEY); } catch { /* storage blocked */ }
  return memoryToken;
}

export function setToken(token) {
  memoryToken = token;
  try { token ? sessionStorage.setItem(KEY, token) : sessionStorage.removeItem(KEY); } catch { /* storage blocked */ }
}

export class ApiError extends Error {
  constructor(status, code, message, details) {
    super(message);
    this.status = status; this.code = code; this.details = details;
  }
}

/** api(path, {method, body, skipAuthRedirect}) -> parsed JSON. Throws ApiError with a user-facing message. */
export async function api(path, opts = {}) {
  const headers = { Accept: "application/json" };
  const token = getToken();
  if (token) headers.Authorization = `Bearer ${token}`;
  if (opts.body !== undefined) headers["Content-Type"] = "application/json";
  let res;
  try {
    res = await fetch(path, { method: opts.method ?? "GET", headers, body: opts.body !== undefined ? JSON.stringify(opts.body) : undefined });
  } catch {
    throw new ApiError(0, "network", "서버에 연결하지 못했습니다. 잠시 후 다시 시도하세요.");
  }
  if (res.status === 204) return undefined;
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    if (res.status === 401 && !opts.skipAuthRedirect) {
      setToken(null);
      if (location.pathname !== "/login") { history.replaceState(null, "", "/login"); dispatchEvent(new PopStateEvent("popstate")); }
    }
    throw new ApiError(res.status, data.code ?? "error", data.message ?? "요청을 처리하지 못했습니다.", data.details);
  }
  return data;
}
