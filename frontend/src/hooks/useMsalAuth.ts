import { useEffect, useCallback, useRef } from "react";
import { useMsal, useIsAuthenticated } from "@azure/msal-react";
import { InteractionRequiredAuthError } from "@azure/msal-browser";
import { loginRequest } from "@/config/msalConfig";
import { setAccessToken } from "@/lib/auth-token";
import { env } from "@/config/env";
import type { AuthUser } from "./use-auth";

const TOKEN_REFRESH_MARGIN_MS = 5 * 60 * 1000; // 5 minutes before expiry

interface MsalAuthResult {
  user: AuthUser | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  logout: () => void;
  getAccessToken: () => Promise<string | null>;
}

export function useMsalAuth(): MsalAuthResult {
  const { instance, accounts, inProgress } = useMsal();
  const isMsalAuthenticated = useIsAuthenticated();
  const refreshTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const userRef = useRef<AuthUser | null>(null);
  const isLoading = inProgress !== "none";

  const acquireToken = useCallback(async (): Promise<string | null> => {
    const account = accounts[0];
    if (!account) return null;

    try {
      const response = await instance.acquireTokenSilent({
        ...loginRequest,
        account,
      });
      setAccessToken(response.accessToken);
      return response.accessToken;
    } catch (error) {
      if (error instanceof InteractionRequiredAuthError) {
        // Silent refresh failed — redirect to login
        setAccessToken(null);
        await instance.loginRedirect(loginRequest);
        return null;
      }
      console.error("[MSAL] Token acquisition failed:", error);
      setAccessToken(null);
      return null;
    }
  }, [instance, accounts]);

  // Schedule silent token refresh before expiry
  const scheduleRefresh = useCallback(
    (expiresOn: Date) => {
      if (refreshTimerRef.current) {
        clearTimeout(refreshTimerRef.current);
      }
      const msUntilExpiry = expiresOn.getTime() - Date.now();
      const refreshIn = Math.max(msUntilExpiry - TOKEN_REFRESH_MARGIN_MS, 0);
      refreshTimerRef.current = setTimeout(() => {
        acquireToken();
      }, refreshIn);
    },
    [acquireToken],
  );

  // Validate token with backend and sync user
  const syncUser = useCallback(
    async (accessToken: string): Promise<AuthUser | null> => {
      try {
        const res = await fetch(`${env.apiBaseUrl}/auth/validate`, {
          method: "POST",
          headers: {
            Authorization: `Bearer ${accessToken}`,
            "Content-Type": "application/json",
          },
        });
        if (!res.ok) return null;
        const data = await res.json();
        return {
          id: data.id,
          email: data.email,
          first_name: data.first_name,
          last_name: data.last_name,
          display_name: data.display_name,
          roles: data.roles,
        };
      } catch {
        console.error("[MSAL] User sync failed");
        return null;
      }
    },
    [],
  );

  // On mount / account change: acquire token, sync user, schedule refresh
  useEffect(() => {
    if (!isMsalAuthenticated || accounts.length === 0 || isLoading) return;

    let cancelled = false;

    async function init() {
      const account = accounts[0];
      try {
        const response = await instance.acquireTokenSilent({
          ...loginRequest,
          account,
        });
        if (cancelled) return;

        setAccessToken(response.accessToken);
        const user = await syncUser(response.accessToken);
        if (cancelled) return;

        userRef.current = user;

        if (response.expiresOn) {
          scheduleRefresh(response.expiresOn);
        }
      } catch (error) {
        if (cancelled) return;
        if (error instanceof InteractionRequiredAuthError) {
          await instance.loginRedirect(loginRequest);
        }
      }
    }

    init();

    return () => {
      cancelled = true;
      if (refreshTimerRef.current) {
        clearTimeout(refreshTimerRef.current);
      }
    };
  }, [isMsalAuthenticated, accounts, isLoading, instance, syncUser, scheduleRefresh]);

  // Redirect unauthenticated users to Azure AD
  useEffect(() => {
    if (isLoading) return;
    if (!isMsalAuthenticated && accounts.length === 0) {
      instance.loginRedirect(loginRequest);
    }
  }, [isMsalAuthenticated, accounts.length, isLoading, instance]);

  const logout = useCallback(() => {
    setAccessToken(null);
    if (refreshTimerRef.current) {
      clearTimeout(refreshTimerRef.current);
    }
    instance.logoutRedirect();
  }, [instance]);

  return {
    user: userRef.current,
    isAuthenticated: isMsalAuthenticated && userRef.current !== null,
    isLoading,
    logout,
    getAccessToken: acquireToken,
  };
}
