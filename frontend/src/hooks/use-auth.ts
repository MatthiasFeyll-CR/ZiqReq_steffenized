import { createContext, useContext } from "react"

export interface AuthUser {
  id: string
  email: string
  first_name: string
  last_name: string
  display_name: string
  roles: string[]
}

export interface AuthContextValue {
  user: AuthUser | null
  isAuthenticated: boolean
  isLoading: boolean
  isDevBypass: boolean
  hasRole: (role: string) => boolean
  logout: () => void
  setUser: (user: AuthUser | null) => void
  getAccessToken: () => Promise<string | null>
}

export const AuthContext = createContext<AuthContextValue>({
  user: null,
  isAuthenticated: false,
  isLoading: true,
  isDevBypass: false,
  hasRole: () => false,
  logout: () => {},
  setUser: () => {},
  getAccessToken: () => Promise.resolve(null),
})

export function useAuth(): AuthContextValue {
  return useContext(AuthContext)
}
