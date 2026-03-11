import { env } from "@/config/env";
import { getAccessToken } from "@/lib/auth-token";
import { useCallback, useEffect, useMemo, useState } from "react";
import type { AuthContextValue, AuthUser } from "./use-auth";

export function useAuthProvider(): AuthContextValue {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [checked, setChecked] = useState(false);

  const isDevBypass = env.authBypass;

  // On mount, try to restore user from existing backend session
  useEffect(() => {
    const apiBase = import.meta.env.VITE_API_BASE_URL ?? "/api";
    fetch(`${apiBase}/auth/me`, { credentials: "include" })
      .then((res) => (res.ok ? res.json() : null))
      .then((data) => {
        if (data?.id) {
          setUser(data as AuthUser);
        }
      })
      .catch(() => {})
      .finally(() => setChecked(true));
  }, []);

  const isAuthenticated = user !== null;

  const hasRole = useCallback((role: string) => user?.roles.includes(role) ?? false, [user]);

  const logout = useCallback(() => {
    setUser(null);
  }, []);

  const getAccessTokenFn = useCallback(async (): Promise<string | null> => {
    if (isDevBypass) {
      return user?.id ?? null;
    }
    return getAccessToken();
  }, [isDevBypass, user?.id]);

  return useMemo(
    () => ({
      user,
      isAuthenticated,
      isLoading: !checked,
      isDevBypass,
      hasRole,
      logout,
      setUser,
      getAccessToken: getAccessTokenFn,
    }),
    [user, isAuthenticated, checked, isDevBypass, hasRole, logout, getAccessTokenFn],
  );
}
