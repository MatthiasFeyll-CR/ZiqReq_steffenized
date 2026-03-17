import { useCallback, useEffect, useState } from "react"
import { Link } from "react-router-dom"
import { Menu, X, Lightbulb, Search } from "lucide-react"
import { useTranslation } from "react-i18next"
import { useAuth } from "@/hooks/use-auth"
import { NavbarLink } from "./NavbarLink"
import { UserDropdown } from "./UserDropdown"
import { ConnectionIndicator } from "./ConnectionIndicator"
import { ProjectsListFloating } from "./ProjectsListFloating"
import { NotificationBell } from "./NotificationBell"
import { NotificationPanel } from "@/components/notifications/NotificationPanel"
import { QuickSearch } from "./QuickSearch"

export function Navbar() {
  const { user, hasRole } = useAuth()
  const [mobileOpen, setMobileOpen] = useState(false)
  const [projectsOpen, setProjectsOpen] = useState(false)
  const [notifPanelOpen, setNotifPanelOpen] = useState(false)
  const [quickSearchOpen, setQuickSearchOpen] = useState(false)
  const { t } = useTranslation()

  const closeProjects = useCallback(() => setProjectsOpen(false), [])
  const toggleNotifPanel = useCallback(() => setNotifPanelOpen((prev) => !prev), [])
  const closeNotifPanel = useCallback(() => setNotifPanelOpen(false), [])
  const closeQuickSearch = useCallback(() => setQuickSearchOpen(false), [])

  // Global Cmd/Ctrl+K shortcut
  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault()
        setQuickSearchOpen((prev) => !prev)
      }
    }
    document.addEventListener("keydown", handleKeyDown)
    return () => document.removeEventListener("keydown", handleKeyDown)
  }, [])

  return (
    <nav className="sticky top-0 z-40 flex h-14 items-center bg-[#002E3C] px-4 text-white dark:bg-[#1C1C22]">
      {/* Logo */}
      <Link to="/" className="mr-6 flex items-center gap-2 hover:opacity-80 transition-opacity">
        <span className="text-lg font-bold tracking-tight">ZiqReq</span>
      </Link>

      {/* Desktop nav links */}
      <div className="hidden md:flex md:items-center md:gap-1">
        <NavbarLink to="/">{t("nav.projects")}</NavbarLink>
        <NavbarLink to="/explore">{t("nav.explore")}</NavbarLink>
        {hasRole("reviewer") && <NavbarLink to="/reviews">{t("nav.reviews")}</NavbarLink>}
        {hasRole("admin") && <NavbarLink to="/admin">{t("nav.admin")}</NavbarLink>}
      </div>

      {/* Spacer */}
      <div className="flex-1" />

      {/* Right utility area */}
      <div className="flex items-center gap-3">
        <ConnectionIndicator />
        <button
          className="flex items-center gap-1.5 rounded-full px-2 py-1.5 text-sm text-white/70 transition-colors hover:bg-white/10 hover:text-white"
          onClick={() => setQuickSearchOpen(true)}
          aria-label={t("quickSearch.title", "Quick Search")}
        >
          <Search className="h-4 w-4" />
          <kbd className="hidden sm:inline-flex items-center rounded border border-white/20 px-1.5 py-0.5 text-[10px] font-medium text-white/50">
            {navigator.platform?.includes("Mac") ? "\u2318K" : "Ctrl+K"}
          </kbd>
        </button>
        <div className="relative">
          <button
            className="flex items-center gap-1 rounded-full px-2 py-1.5 text-sm text-white/70 transition-colors hover:bg-white/10 hover:text-white"
            onClick={() => setProjectsOpen((o) => !o)}
            aria-label={t("projectsFloat.title")}
          >
            <Lightbulb className="h-5 w-5" />
            <span className="hidden sm:inline">{t("nav.projects")}</span>
          </button>
          {projectsOpen && <ProjectsListFloating onClose={closeProjects} />}
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
        <div className="absolute left-0 top-14 z-50 w-full bg-[#002E3C] shadow-lg dark:bg-[#1C1C22] md:hidden">
          <div className="flex flex-col py-2">
            <MobileLink to="/" onClick={() => setMobileOpen(false)}>{t("nav.projects")}</MobileLink>
            <MobileLink to="/explore" onClick={() => setMobileOpen(false)}>{t("nav.explore")}</MobileLink>
            {hasRole("reviewer") && (
              <MobileLink to="/reviews" onClick={() => setMobileOpen(false)}>{t("nav.reviews")}</MobileLink>
            )}
            {hasRole("admin") && (
              <MobileLink to="/admin" onClick={() => setMobileOpen(false)}>{t("nav.admin")}</MobileLink>
            )}
          </div>
        </div>
      )}
      <QuickSearch open={quickSearchOpen} onClose={closeQuickSearch} />
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
