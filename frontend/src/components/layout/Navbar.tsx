import { useState } from "react"
import { Menu, X, Bell } from "lucide-react"
import { useAuth } from "@/hooks/use-auth"
import { NavbarLink } from "./NavbarLink"
import { UserDropdown } from "./UserDropdown"
import { ConnectionIndicator } from "./ConnectionIndicator"

export function Navbar() {
  const { user, hasRole } = useAuth()
  const [mobileOpen, setMobileOpen] = useState(false)

  return (
    <nav className="sticky top-0 z-40 flex h-14 items-center bg-[#002E3C] px-4 text-white dark:bg-[#0F1A2E]">
      {/* Logo */}
      <div className="mr-6 flex items-center gap-2">
        <span className="text-lg font-bold tracking-tight">ZiqReq</span>
      </div>

      {/* Desktop nav links */}
      <div className="hidden md:flex md:items-center md:gap-1">
        <NavbarLink to="/">Ideas</NavbarLink>
        {hasRole("reviewer") && <NavbarLink to="/reviews">Reviews</NavbarLink>}
        {hasRole("admin") && <NavbarLink to="/admin">Admin</NavbarLink>}
      </div>

      {/* Spacer */}
      <div className="flex-1" />

      {/* Right utility area */}
      <div className="flex items-center gap-3">
        <ConnectionIndicator />
        <button
          className="rounded-full p-1.5 text-white/70 transition-colors hover:bg-white/10 hover:text-white"
          aria-label="Notifications"
        >
          <Bell className="h-5 w-5" />
        </button>
        {user && <UserDropdown />}

        {/* Mobile hamburger */}
        <button
          className="rounded p-1 text-white/80 hover:bg-white/10 md:hidden"
          onClick={() => setMobileOpen((o) => !o)}
          aria-label={mobileOpen ? "Close menu" : "Open menu"}
        >
          {mobileOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
        </button>
      </div>

      {/* Mobile menu overlay */}
      {mobileOpen && (
        <div className="absolute left-0 top-14 z-50 w-full bg-[#002E3C] shadow-lg dark:bg-[#0F1A2E] md:hidden">
          <div className="flex flex-col py-2">
            <MobileLink to="/" onClick={() => setMobileOpen(false)}>Ideas</MobileLink>
            {hasRole("reviewer") && (
              <MobileLink to="/reviews" onClick={() => setMobileOpen(false)}>Reviews</MobileLink>
            )}
            {hasRole("admin") && (
              <MobileLink to="/admin" onClick={() => setMobileOpen(false)}>Admin</MobileLink>
            )}
          </div>
        </div>
      )}
    </nav>
  )
}

function MobileLink({
  to,
  onClick,
  children,
}: {
  to: string
  onClick: () => void
  children: React.ReactNode
}) {
  return (
    <a
      href={to}
      onClick={(e) => {
        e.preventDefault()
        onClick()
        window.location.href = to
      }}
      className="px-4 py-3 text-sm font-medium text-white/80 transition-colors hover:bg-white/10 hover:text-white"
    >
      {children}
    </a>
  )
}
