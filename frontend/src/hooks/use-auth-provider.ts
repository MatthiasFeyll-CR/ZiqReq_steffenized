import { useState, useMemo, useCallback } from "react"
import type { AuthUser, AuthContextValue } from "./use-auth"

export function useAuthProvider(): AuthContextValue {
  const [user, setUser] = useState<AuthUser | null>(null)

  const isDevBypass =
    (import.meta.env.VITE_AUTH_BYPASS ?? "false") === "true"

  const isAuthenticated = user !== null

  const hasRole = useCallback(
    (role: string) => user?.roles.includes(role) ?? false,
    [user],
  )

  const logout = useCallback(() => {
    setUser(null)
  }, [])

  return useMemo(
    () => ({ user, isAuthenticated, isDevBypass, hasRole, logout, setUser }),
    [user, isAuthenticated, isDevBypass, hasRole, logout],
  )
}
