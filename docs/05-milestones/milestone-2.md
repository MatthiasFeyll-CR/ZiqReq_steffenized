# Milestone 2: Shell + Landing Page

## Overview
- **Execution order:** 2 (runs after M1)
- **Estimated stories:** 9
- **Dependencies:** M1
- **MVP:** Yes

## Features Included

| Feature ID | Feature Name | Priority | Source |
|-----------|-------------|----------|--------|
| F-9.1 | Landing Page Structure | Must-have | features.md |
| F-9.2 | Idea Creation | Must-have | features.md |
| F-9.3 | Soft Delete | Must-have | features.md |
| F-9.4 | Search & Filter | Must-have | features.md |
| F-16.1 | Available Languages | Must-have | features.md |
| F-16.2 | Language Switcher | Must-have | features.md |
| F-16.3 | i18n Scope | Must-have | features.md |
| F-17.1 | Available Themes | Must-have | features.md |
| F-17.2 | Theme Switcher | Must-have | features.md |
| F-17.3 | System Preference Detection | Must-have | features.md |
| F-17.4 | Theme Scope | Must-have | features.md |
| F-17.5 | Brand Assets | Must-have | features.md |
| F-14.1 | Universal Error Pattern | Must-have | features.md |
| F-12.2 | Toast Notifications | Must-have | features.md |
| — | Accessibility foundations (NFR-A1–A5) | Must-have | nonfunctional.md |
| — | Responsive layout foundations + mobile breakpoints | Must-have | nonfunctional.md §Compatibility |

## Data Model References

| Table | Operation | Key Columns | Source |
|-------|-----------|-------------|--------|
| ideas | CREATE, READ, SOFT DELETE, RESTORE | id, title, state, owner_id, deleted_at, created_at | data-model.md |
| idea_collaborators | READ | idea_id, user_id | data-model.md |
| collaboration_invitations | READ | invitee_id, status | data-model.md |
| users | READ | id, display_name, roles | data-model.md |

## API Endpoint References

| Endpoint | Method | Purpose | Auth | Source |
|----------|--------|---------|------|--------|
| /api/ideas | GET | List user's ideas (owned + collaborating + invitations + trash) | Bearer/bypass | api-design.md |
| /api/ideas | POST | Create new idea with first message | Bearer/bypass | api-design.md |
| /api/ideas/:id | DELETE | Soft delete idea | Bearer/bypass | api-design.md |
| /api/ideas/:id/restore | POST | Restore idea from trash | Bearer/bypass | api-design.md |

## Page & Component References

| Page/Component | Type | Source |
|---------------|------|--------|
| GlobalNavbar | Shared layout | design-system.md §9.1, page-layouts.md §2 |
| LandingPage | Page | page-layouts.md §3 |
| HeroSection | Component | page-layouts.md §3, component-specs.md |
| IdeaCard | Component | component-specs.md |
| IdeasListFloating | Floating window | page-layouts.md §11 |
| UserMenuDropdown | Component | design-system.md §9.1 |
| LanguageSwitcher | Component | component-specs.md |
| ThemeToggle | Component | component-specs.md |
| DevUserSwitcher | Component (dev only) | component-specs.md |
| ToastContainer | Shared component | component-specs.md §11.1 |
| ErrorToast | Component | component-specs.md |
| ErrorLogModal | Component | component-specs.md |
| SearchBar | Component | component-specs.md |
| FilterControls | Component | component-specs.md |

## Shared Components Required

| Component | Status | Introduced In |
|-----------|--------|---------------|
| GlobalNavbar | New | M2 |
| Theme system (CSS variables, dark class toggle) | New | M2 |
| i18n setup (react-i18next, de.json, en.json) | New | M2 |
| Toast notification system (react-toastify) | New | M2 |
| Error handling pattern (ErrorToast + ErrorLogModal) | New | M2 |
| Accessibility foundations (focus ring style, reduced motion utility, screen reader utilities) | New | M2 |
| Responsive layout utilities (breakpoints, mobile/tablet/desktop adaptations) | New | M2 |

## Story Outline (Suggested Order)

1. **[Shared] Theme system + accessibility + responsive foundations** — CSS variable-based theming with shadcn/ui. Dark mode via `.dark` class on `<html>`. Theme toggle component. localStorage persistence. `prefers-color-scheme` detection for initial default. Gotham font setup with fallback stack. Accessibility foundations: focus ring style (visible 2px ring on all interactive elements, NFR-A2), 4.5:1 contrast ratio in both themes (NFR-A3), `prefers-reduced-motion` CSS utility and hook (NFR-A5), screen reader labels on all interactive elements (aria-label patterns, NFR-A4), keyboard-first navigation setup (NFR-A1). Responsive foundations: Tailwind breakpoints for desktop/tablet/mobile, responsive layout utilities, mobile viewport meta.
2. **[Shared] i18n setup** — react-i18next configuration. German (default) + English translation files (de.json, en.json). Language switcher component. localStorage persistence. Initial translation keys for navbar, landing page, common actions.
3. **[Shared] Global navbar** — Logo + brand block (left). Role-gated nav links: Ideas list button, Reviews (Reviewer only), Admin (Admin only). Right side: connection state indicator placeholder, notification bell placeholder, user menu dropdown (language, theme, logout, dev user switcher in bypass mode).
4. **[Shared] Error handling pattern** — Universal error toast with "Show Logs" and "Retry" buttons. ErrorLogModal: console output, network response, technical details, support contact. react-toastify setup for success/info/warning/error toasts with auto-dismiss timers.
5. **[Backend] Idea list + create + soft delete APIs** — Gateway REST endpoints: GET /api/ideas (with query params for state filter, ownership filter, search), POST /api/ideas (create with first_message), DELETE /api/ideas/:id (soft delete), POST /api/ideas/:id/restore. Gateway→Core gRPC calls for all operations.
6. **[Frontend] Landing page structure** — Four ordered lists: My Ideas, Collaborating, Invitations (placeholder), Trash. IdeaCard component showing title, state badge, timestamp. Soft delete with undo toast. Restore from trash.
7. **[Frontend] Idea creation (hero section)** — Text input in hero area. On submit: POST /api/ideas → receive idea UUID → navigate to /idea/:uuid. First message becomes opening chat message.
8. **[Frontend] Search & filter** — Search bar filtering by idea title (client-side or server-side). Filter tabs/buttons: All, Open, In Review, Accepted, Dropped, Rejected. Ownership filter: My Ideas / Collaborating.
9. **[Frontend] Ideas list floating window + Celery soft delete cleanup** — Navbar button opens floating window with tabbed idea lists (Active, In Review, Accepted, Closed). Click navigates to idea. Backend: Celery periodic task for permanent deletion of ideas past trash countdown.

## Milestone Acceptance Criteria
- [ ] Global navbar renders with correct role-gated items per dev user
- [ ] Theme toggle switches light/dark mode, persists across page reloads
- [ ] Language switcher changes all UI text between German and English
- [ ] Landing page shows My Ideas, Collaborating, Invitations, Trash sections
- [ ] Creating an idea from hero section creates idea and redirects to workspace URL
- [ ] Soft delete moves idea to trash with undo toast, restore works
- [ ] Search filters ideas by title, state filters work correctly
- [ ] Ideas list floating window shows tabbed lists
- [ ] Error toast with Show Logs + Retry pattern works for simulated errors
- [ ] Celery soft delete cleanup job deletes expired trash items
- [ ] Accessibility: visible focus indicators on all interactive elements
- [ ] Accessibility: 4.5:1 contrast ratio met in both light and dark themes
- [ ] Accessibility: `prefers-reduced-motion` disables animations
- [ ] Responsive: layout adapts to desktop, tablet, and mobile viewports
- [ ] TypeScript typecheck passes
- [ ] No regressions on M1

## Notes
- Notification bell and connection state indicator are rendered as placeholders in the navbar — full functionality in M9 and M3 respectively.
- Invitations list on landing page shows structure but invite flow comes in M9.
- Gotham font requires corporate license — use fallback stack during development if font files unavailable.
- Translation files start with keys for M2 features; subsequent milestones add their own keys.
- Accessibility and responsive foundations are established here; all subsequent milestone components must follow these patterns (focus rings, aria-labels, reduced motion, responsive breakpoints).
- Design system CSS variables (brand colors, semantic colors, surface/text tokens for both themes) from docs/03-design/design-system.md must be set up in the theme system story.
- Animation infrastructure (framer-motion setup, useReducedMotion hook, animation principles from docs/03-design/interactions.md) is established here. Subsequent milestones implement specific animations per component.
- Mobile-specific behaviors (e.g., board read-only on mobile) are implemented in the respective feature milestone (M4 for board).
