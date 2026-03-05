# Software Architecture — Status

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
- docs_old/02-architecture/ (all files — carried forward valid decisions)

## Phase Status
| Phase | Name | Status | Completed |
|-------|------|--------|-----------|
| 1 | Tech Stack Selection | complete | 2026-03-02 |
| 2 | Data Model | complete | 2026-03-02 |
| 3 | API Design | complete | 2026-03-02 |
| 4 | Project Structure | complete | 2026-03-02 |
| 5 | Testing Strategy | complete | 2026-03-02 |
| 6 | Summary & Handoff | complete | 2026-03-02 |

## Handoff
- **Ready:** true
- **Next specialist(s):** UI/UX Designer (`/ui_ux_designer`) and AI Engineer (`/ai_engineer`) — run in parallel
- **Files produced:**
  - docs/02-architecture/tech-stack.md
  - docs/02-architecture/data-model.md
  - docs/02-architecture/api-design.md
  - docs/02-architecture/project-structure.md
  - docs/02-architecture/testing-strategy.md
- **Required input for next specialist:**
  - All files in docs/01-requirements/ and docs/02-architecture/
- **Briefing for next specialist:**
  - **Tech stack:** React 19 + Vite + TypeScript (SPA), Django 5 + DRF + Channels (backend), gRPC (inter-service), PostgreSQL 16 + pgvector, Redis, RabbitMQ/Azure Service Bus, Celery, MSAL (Azure AD auth)
  - **Frontend:** Tailwind CSS 4 + shadcn/ui (Radix primitives), Redux Toolkit (client state — board undo/redo, WebSocket, presence), TanStack Query (server state), React Flow (digital board), framer-motion (animations), react-i18next (German + English), Lucide icons
  - **Rendering strategy:** SPA, no SSR. CSS variable theming with Tailwind `dark:` variant for light/dark mode.
  - **Brand:** Gotham font (corporate, self-hosted), Lucide icons. Brand colors and full palette to be defined by UI/UX Designer.
  - **API pattern:** REST (frontend → gateway) + WebSocket (real-time) + gRPC (internal services) + message broker (async events)
  - **Architecture:** Event-driven microservices — 6 services (frontend, gateway, core, ai, notification, pdf), 12 Docker containers for local dev
  - **Real-time:** WebSocket via Django Channels. Session-level connection. Hybrid board sync (awareness events = WS-only, content changes = REST-first + WS broadcast).
  - **AI service boundary:** Architect defines external interface (gRPC contracts, DB tables, event contracts, container config). AI Engineer defines internal structure (agent framework, processing pipeline, context assembly, model selection, prompts).
  - **Testing:** Vitest + React Testing Library (frontend), pytest + pytest-django (backend), Playwright (E2E). AI mock mode for deterministic E2E.
- **Open questions:** None
