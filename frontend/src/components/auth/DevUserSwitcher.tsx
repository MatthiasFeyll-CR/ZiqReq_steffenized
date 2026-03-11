import { useState, useEffect } from "react"
import { useTranslation } from "react-i18next"
import { useAuth } from "@/hooks/use-auth"
import type { AuthUser } from "@/hooks/use-auth"
import { apiClient } from "@/lib/api-client"

interface DevUser {
  id: string
  email: string
  first_name: string
  last_name: string
  display_name: string
  roles: string[]
}

export function DevUserSwitcher() {
  const { isDevBypass, user, setUser } = useAuth()
  const { t } = useTranslation()
  const [devUsers, setDevUsers] = useState<DevUser[]>([])

  useEffect(() => {
    if (!isDevBypass) return
    apiClient<{ users: DevUser[] }>("/auth/dev-users")
      .then((data) => setDevUsers(data.users))
      .catch(() => {
        // Fallback: use hardcoded dev users if API not available
        setDevUsers([
          { id: "00000000-0000-0000-0000-000000000001", email: "alice@dev.local", first_name: "Alice", last_name: "Admin", display_name: "Alice Admin", roles: ["admin", "reviewer", "user"] },
          { id: "00000000-0000-0000-0000-000000000002", email: "bob@dev.local", first_name: "Bob", last_name: "Reviewer", display_name: "Bob Reviewer", roles: ["reviewer", "user"] },
          { id: "00000000-0000-0000-0000-000000000003", email: "carol@dev.local", first_name: "Carol", last_name: "User", display_name: "Carol User", roles: ["user"] },
          { id: "00000000-0000-0000-0000-000000000004", email: "dave@dev.local", first_name: "Dave", last_name: "User", display_name: "Dave User", roles: ["user"] },
        ])
      })
  }, [isDevBypass])

  if (!isDevBypass) return null

  const handleSelect = (devUser: DevUser) => {
    setUser(devUser as AuthUser)
  }

  return (
    <div className="fixed bottom-4 left-4 z-50 rounded-lg border border-amber-500/50 bg-amber-50 p-3 shadow-lg dark:bg-amber-950/80">
      <p className="mb-2 text-xs font-bold uppercase tracking-wider text-amber-700 dark:text-amber-400">
        {t("dev.userSwitcher")}
      </p>
      <div className="flex flex-col gap-1">
        {devUsers.map((du) => (
          <button
            key={du.id}
            onClick={() => handleSelect(du)}
            className={`rounded px-3 py-1.5 text-left text-xs transition-colors ${
              user?.id === du.id
                ? "bg-amber-200 font-semibold text-amber-900 dark:bg-amber-800 dark:text-amber-100"
                : "text-amber-800 hover:bg-amber-100 dark:text-amber-300 dark:hover:bg-amber-900/50"
            }`}
          >
            <span className="font-medium">{du.display_name}</span>
            <span className="ml-2 text-amber-600 dark:text-amber-500">
              {du.roles.join(", ")}
            </span>
          </button>
        ))}
      </div>
    </div>
  )
}
