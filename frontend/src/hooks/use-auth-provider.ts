import { useState, useMemo, useCallback } from "react"
import { env } from "@/config/env"
import { getAccessToken } from "@/lib/auth-token"
import type { AuthUser, AuthContextValue } from "./use-auth"

export function useAuthProvider(): AuthContextValue {
  const [user, setUser] = useState<AuthUser | null>(null)

  const isDevBypass = env.authBypass

  const isAuthenticated = user !== null

  const hasRole = useCallback(
    (role: string) => user?.roles.includes(role) ?? false,
    [user],
  )

  const logout = useCallback(() => {
    setUser(null)
  }, [])

  const getAccessTokenFn = useCallback(async (): Promise<string | null> => {
    if (isDevBypass) {
      // In dev bypass mode, the WebSocket uses user.id as the token
      return user?.id ?? null
    }
    // In production mode, return the current cached token
    return getAccessToken()
  }, [isDevBypass, user?.id])

  return useMemo(
    () => ({
      user,
      isAuthenticated,
      isDevBypass,
      hasRole,
      logout,
      setUser,
      getAccessToken: getAccessTokenFn,
    }),
    [user, isAuthenticated, isDevBypass, hasRole, logout, getAccessTokenFn],
  )
}
