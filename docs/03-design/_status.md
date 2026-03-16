# UI/UX Design — Status

## Project
- **Name:** ZiqReq
- **Started:** 2026-03-02
- **Last updated:** 2026-03-02

## Input Consumed
- docs/01-requirements/vision.md
- docs/01-requirements/user-roles.md
- docs/01-requirements/features.md
- docs/01-requirements/pages.md
- docs/01-requirements/data-entities.md
- docs/01-requirements/nonfunctional.md
- docs/01-requirements/constraints.md
- docs/01-requirements/traceability.md
- docs/02-architecture/tech-stack.md
- docs/02-architecture/data-model.md
- docs/02-architecture/api-design.md
- docs/02-architecture/project-structure.md
- docs/02-architecture/testing-strategy.md
- docs/02-architecture/_status.md
- docs_old/03-design/ (all files — carried forward valid decisions)

## Phase Status
| Phase | Name | Status | Completed |
|-------|------|--------|-----------|
| 1 | Design System | complete | 2026-03-02 |
| 2 | Page Layouts | complete | 2026-03-02 |
| 3 | Component Specifications | complete | 2026-03-02 |
| 4 | Interaction & Animation | complete | 2026-03-02 |
| 5 | Component Inventory, Summary & Handoff | complete | 2026-03-02 |

## Handoff
- **Ready:** true
- **Next specialist(s):** Milestone Planner (`/milestone_planner`). If AI features exist and Arch+AI Integrator hasn't run, wait for that first.
- **Files produced:**
  - docs/03-design/design-system.md
  - docs/03-design/page-layouts.md
  - docs/03-design/component-specs.md
  - docs/03-design/interactions.md
  - docs/03-design/component-inventory.md
- **Required input for next specialist:**
  - All files in docs/01-requirements/, docs/02-architecture/, and docs/03-design/
- **Briefing for next specialist:**
  - **Design style:** Clean & Professional (Soft UI Evolution) — Commerzbank Gold (#FFD700) + Dark Teal (#002E3C) brand palette, light/dark mode with CSS variable theming
  - **Pages designed:** 5 — Landing Page, Project Workspace (chat + requirements panel), Review Page, Admin Panel, Login Page
  - **Shared component count:** 32 shared components out of 81 total. Key reusable: 16 UI primitives (shadcn/ui), 8 layout components (Navbar, PageShell, Divider), notification components, ProjectCard, error handling components
  - **AI-specific UI surfaces:** Chat panel with AI messages/delegation/processing indicator, requirements panel AI modification indicator, requirements document auto-generation progress, context window indicator.
  - **Responsive breakpoints:** sm (640px), md (768px), lg (1024px), xl (1280px), 2xl (1536px). Mobile-first with bottom sheets for modals.
  - **Typography:** Gotham (self-hosted, 3 weights: Book/Medium/Bold), 7-step type scale from 12px to 30px
  - **Animation:** framer-motion, all 100-300ms, all respect prefers-reduced-motion (NFR-A5)
  - **Accessibility:** WCAG 2.1 AA verified, gold focus rings, 44px touch targets, contrast ratios verified (all primary combos pass AAA)
- **Open questions:** None

## Upstream Modifications
None. All design decisions work within the existing requirements and architecture. Theme support (FA-17) and related NFRs (NFR-T1 through NFR-T6) were already present in the requirements.

## Key Design Decisions
| Decision | Choice |
|----------|--------|
| Visual mood | Clean & Professional (Soft UI Evolution) |
| Primary color | #FFD700 (Commerzbank Gold) — accent/highlights only |
| Secondary color | #002E3C (Commerzbank Dark Teal) — primary action color in light mode |
| Button strategy | Light: teal buttons. Dark: gold buttons (color inversion) |
| Font | Gotham (self-hosted, commercial license) |
| Icons | Lucide React (no emojis as UI icons) |
| Themes | Light (default) + Dark mode (FA-17) |
| Corner radius | Subtle rounded (6-8px) |
| Spacing | Comfortable (8px base) |
| Shadows | Soft elevation (light), ring borders (dark) |
| Workspace split | 40% chat / 60% requirements panel, draggable divider |
| Navbar | Brand (CR logo + ZiqReq) left, nav links + utilities right, dark teal bg |
| Animations | framer-motion, 100-300ms, all respect prefers-reduced-motion |

## Pre-Delivery Checklist
- [x] No emojis used as icons (use SVG via Lucide React)
- [x] All icons from consistent icon set (Lucide React)
- [x] Brand logos specified (CR ribbon, not full wordmark)
- [x] Hover states don't cause layout shift (translateY -1px only)
- [x] Use theme colors directly (bg-primary) not var() wrapper
- [x] All clickable elements have cursor-pointer
- [x] Hover states provide clear visual feedback
- [x] Transitions are smooth (150-300ms)
- [x] Focus states visible for keyboard navigation (gold ring)
- [x] Light mode text has sufficient contrast (4.5:1 minimum, most AAA)
- [x] Glass/transparent elements visible in light mode (N/A — not used)
- [x] Borders visible in both modes (gray-200 light, white/0.08 dark)
- [x] Both modes designed consistently
- [x] Floating elements have proper spacing from edges
- [x] No content hidden behind fixed navbars (sticky, not fixed)
- [x] Responsive at 375px, 768px, 1024px, 1440px
- [x] No horizontal scroll on mobile
- [x] All images have alt text (specified in component specs)
- [x] Form inputs have labels (Form layout spec in component-specs.md)
- [x] Color is not the only indicator (state dots + text labels + badges)
- [x] prefers-reduced-motion respected (all animations)
