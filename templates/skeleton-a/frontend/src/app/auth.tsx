import { createContext, ReactNode, useCallback, useContext, useEffect, useState } from "react";
import { api, setToken, getToken } from "../shared/api/client";

export type User = { user_id: string; role: string };
type AuthState = {
  user: User | null;
  ready: boolean;
  login: (id: string, password: string) => Promise<User>;
  logout: () => Promise<void>;
};

const AuthContext = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    if (!getToken()) { setReady(true); return; }
    api<User>("/api/auth/me")
      .then(setUser)
      .catch(() => setToken(null))
      .finally(() => setReady(true));
  }, []);

  const login = useCallback(async (id: string, password: string) => {
    const r = await api<{ token: string; user_id: string; role: string }>("/api/auth/login", {
      method: "POST",
      body: { id, password },
      skipAuthRedirect: true,
    });
    setToken(r.token);
    const u = { user_id: r.user_id, role: r.role };
    setUser(u);
    return u;
  }, []);

  const logout = useCallback(async () => {
    try { await api("/api/auth/logout", { method: "POST" }); } catch { /* already logged out */ }
    setToken(null);
    setUser(null);
  }, []);

  return <AuthContext.Provider value={{ user, ready, login, logout }}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthState {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("AuthProvider missing");
  return ctx;
}
