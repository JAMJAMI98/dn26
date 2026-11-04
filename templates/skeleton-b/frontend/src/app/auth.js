// Session state: current user from /api/auth/me (token in memory + sessionStorage via client.js).
import { api, getToken, setToken } from "../shared/api/client.js";

let user = null;

export const currentUser = () => user;
export const homePath = (u) => (u.role === "admin" ? "/admin" : "/me");

/** Restore session on page load. Returns user or null. */
export async function restore() {
  if (!getToken()) return (user = null);
  try {
    const me = await api("/api/auth/me", { skipAuthRedirect: true });
    user = { user_id: me.user_id, role: me.role };
  } catch {
    setToken(null);
    user = null;
  }
  return user;
}

export async function login(id, password) {
  const r = await api("/api/auth/login", { method: "POST", body: { id, password }, skipAuthRedirect: true });
  setToken(r.token);
  user = { user_id: r.user_id, role: r.role };
  return user;
}

export async function logout() {
  try { await api("/api/auth/logout", { method: "POST", skipAuthRedirect: true }); } catch { /* already gone */ }
  setToken(null);
  user = null;
}
