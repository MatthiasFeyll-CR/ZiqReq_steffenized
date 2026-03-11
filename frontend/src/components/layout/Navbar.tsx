import { useCallback, useState } from "react"
import { Menu, X, Lightbulb } from "lucide-react"
import { useTranslation } from "react-i18next"
import { useAuth } from "@/hooks/use-auth"
import { NavbarLink } from "./NavbarLink"
import { UserDropdown } from "./UserDropdown"
import { ConnectionIndicator } from "./ConnectionIndicator"
import { IdeasListFloating } from "./IdeasListFloating"
import { NotificationBell } from "./NotificationBell"
import { NotificationPanel } from "@/components/notifications/NotificationPanel"

export function Navbar() {
  const { user, hasRole } = useAuth()
  const [mobileOpen, setMobileOpen] = useState(false)
  const [ideasOpen, setIdeasOpen] = useState(false)
  const [notifPanelOpen, setNotifPanelOpen] = useState(false)
  const { t } = useTranslation()

  const closeIdeas = useCallback(() => setIdeasOpen(false), [])
  const toggleNotifPanel = useCallback(() => setNotifPanelOpen((prev) => !prev), [])
  const closeNotifPanel = useCallback(() => setNotifPanelOpen(false), [])

  return (
    <nav className="sticky top-0 z-40 flex h-14 items-center bg-[#002E3C] px-4 text-white dark:bg-[#0F1A2E]">
      {/* Logo */}
      <div className="mr-6 flex items-center gap-2">
        <span className="text-lg font-bold tracking-tight">ZiqReq</span>
      </div>

      {/* Desktop nav links */}
      <div className="hidden md:flex md:items-center md:gap-1">
        <NavbarLink to="/">{t("nav.ideas")}</NavbarLink>
        {hasRole("reviewer") && <NavbarLink to="/reviews">{t("nav.reviews")}</NavbarLink>}
        {hasRole("admin") && <NavbarLink to="/admin">{t("nav.admin")}</NavbarLink>}
      </div>

      {/* Spacer */}
      <div className="flex-1" />

      {/* Right utility area */}
      <div className="flex items-center gap-3">
        <ConnectionIndicator />
        <div className="relative">
          <button
            className="flex items-center gap-1 rounded-full px-2 py-1.5 text-sm text-white/70 transition-colors hover:bg-white/10 hover:text-white"
            onClick={() => setIdeasOpen((o) => !o)}
            aria-label={t("ideasFloat.title")}
          >
            <Lightbulb className="h-5 w-5" />
            <span className="hidden sm:inline">{t("nav.ideas")}</span>
          </button>
          {ideasOpen && <IdeasListFloating onClose={closeIdeas} />}
        </div>
        <div className="relative">
          <NotificationBell onTogglePanel={toggleNotifPanel} />
          {notifPanelOpen && <NotificationPanel onClose={closeNotifPanel} />}
        </div>
        {user && <UserDropdown />}

        {/* Mobile hamburger */}
        <button
          className="rounded p-1 text-white/80 hover:bg-white/10 md:hidden"
          onClick={() => setMobileOpen((o) => !o)}
          aria-label={mobileOpen ? t("nav.closeMenu") : t("nav.openMenu")}
        >
          {mobileOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
        </button>
      </div>

      {/* Mobile menu overlay */}
      {mobileOpen && (
        <div className="absolute left-0 top-14 z-50 w-full bg-[#002E3C] shadow-lg dark:bg-[#0F1A2E] md:hidden">
          <div className="flex flex-col py-2">
            <MobileLink to="/" onClick={() => setMobileOpen(false)}>{t("nav.ideas")}</MobileLink>
            {hasRole("reviewer") && (
              <MobileLink to="/reviews" onClick={() => setMobileOpen(false)}>{t("nav.reviews")}</MobileLink>
            )}
            {hasRole("admin") && (
              <MobileLink to="/admin" onClick={() => setMobileOpen(false)}>{t("nav.admin")}</MobileLink>
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
