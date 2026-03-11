import type { ReactNode } from "react"
import { Navbar } from "./Navbar"

interface PageShellProps {
  children: ReactNode
}

export function PageShell({ children }: PageShellProps) {
  return (
    <div className="flex min-h-screen flex-col bg-background text-foreground">
      <Navbar />
      <main id="main-content" className="flex-1">{children}</main>
    </div>
  )
}
