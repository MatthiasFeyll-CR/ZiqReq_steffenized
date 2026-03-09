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
  isDevBypass: boolean
  hasRole: (role: string) => boolean
  logout: () => void
  setUser: (user: AuthUser | null) => void
}

export const AuthContext = createContext<AuthContextValue>({
  user: null,
  isAuthenticated: false,
  isDevBypass: false,
  hasRole: () => false,
  logout: () => {},
  setUser: () => {},
})

export function useAuth(): AuthContextValue {
  return useContext(AuthContext)
}
