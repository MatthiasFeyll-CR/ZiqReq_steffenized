import type { ReactNode } from "react"
import { Navbar } from "./Navbar"

interface PageShellProps {
  children: ReactNode
}

export function PageShell({ children }: PageShellProps) {
  return (
    <div className="flex h-screen flex-col overflow-hidden bg-background text-foreground">
      <Navbar />
      <main id="main-content" className="flex-1 min-h-0 overflow-auto">{children}</main>
    </div>
  )
}
