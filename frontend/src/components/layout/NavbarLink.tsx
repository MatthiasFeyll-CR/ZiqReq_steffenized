import { NavLink } from "react-router-dom"
import { cn } from "@/lib/utils"

interface NavbarLinkProps {
  to: string
  children: React.ReactNode
}

export function NavbarLink({ to, children }: NavbarLinkProps) {
  return (
    <NavLink
      to={to}
      className={({ isActive }) =>
        cn(
          "flex h-14 items-center border-b-2 px-3 text-sm font-medium text-white/80 transition-colors hover:bg-white/10 hover:text-white",
          isActive
            ? "border-primary text-white"
            : "border-transparent",
        )
      }
    >
      {children}
    </NavLink>
  )
}
