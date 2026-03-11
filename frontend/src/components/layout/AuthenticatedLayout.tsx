import { Navigate, Outlet } from "react-router-dom"
import { useAuth } from "@/hooks/use-auth"
import { PageShell } from "./PageShell"

export function AuthenticatedLayout() {
  const { isAuthenticated } = useAuth()

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  return (
    <PageShell>
      <Outlet />
    </PageShell>
  )
}
