# Milestone 1: Foundation & Scaffold

## Overview
- **Wave:** 0
- **Estimated stories:** 10
- **Must complete before starting:** None
- **Can run parallel with:** None
- **MVP:** Yes

## Features Included
| Feature ID | Feature Name | Priority | Source |
|-----------|-------------|----------|--------|
| FA-7 | Authentication (dev bypass only) | P1 | F-7.1 |
| FA-14 | Error Handling (foundation) | P1 | F-14.1 |
| FA-16 | i18n Setup (de/en skeletons) | P1 | F-16.1–F-16.4 |
| FA-17 | Theme System (light/dark) | P1 | F-17.1–F-17.5 |
| — | Infrastructure (Docker, DB, gRPC, WS, broker) | P1 | tech-stack.md, project-structure.md |

## Data Model References
| Table | Operation | Key Columns | Source |
|-------|-----------|-------------|--------|
| ALL 22 tables | CREATE (migrations) | All columns per data-model.md | data-model.md |
| users | SEED (4 dev users) | id, email, first_name, last_name, display_name, roles | F-7.1 |
| admin_parameters | SEED (all params) | key, value, default_value, description, data_type, category | data-model.md seed data |
| facilitator_context_bucket | SEED (empty singleton) | id, content='' | data-model.md |
| context_agent_bucket | SEED (empty singleton) | id, sections={}, free_text='' | data-model.md |

## API Endpoint References
| Endpoint | Method | Purpose | Auth | Source |
|----------|--------|---------|------|--------|
| POST /api/auth/validate | POST | Validate token, sync user | Bearer/bypass | api-design.md |
| GET /api/auth/dev-users | GET | List dev users (bypass only) | Bypass | api-design.md |
| POST /api/auth/dev-switch | POST | Switch dev user (bypass only) | Bypass | api-design.md |
| /ws/ | WebSocket | Connection handshake skeleton | Token/bypass | api-design.md |

## Page & Component References
| Page/Component | Type | Source |
|---------------|------|--------|
| All 16 UI Primitives (Button, Card, Input, Textarea, Select, Switch, Checkbox, Badge, Avatar, Tooltip, DropdownMenu, Dialog, Sheet, Tabs, Skeleton, Toast) | Shared UI | component-inventory.md |
| Navbar, NavbarLink, HamburgerMenu, UserDropdown, PageShell, ConnectionIndicator | Layout | component-inventory.md |
| DevUserSwitcher | Auth | component-inventory.md |
| ErrorBoundary, ErrorToast, ErrorLogModal, EmptyState, LoadingSpinner, SkipLink | Cross-cutting | component-inventory.md |
| LoginPage (placeholder) | Auth | component-inventory.md |

## Story Outline (Suggested Order)
1. **[Infra] Monorepo scaffold + Docker Compose** — Create monorepo structure per project-structure.md. Docker Compose with all containers: frontend (Vite), gateway (Django+Channels), core (Django), ai (Django), notification (Python), pdf (Python+WeasyPrint), celery-worker, celery-beat, postgresql (pgvector/pgvector:pg16), redis, rabbitmq, nginx. All Dockerfiles. Nginx reverse proxy config (/ → frontend, /api/* → gateway, /ws/* → gateway). Environment variables per tech-stack.md.
2. **[Schema] PostgreSQL + pgvector + all Django models + migrations** — Create Django models for all 22 tables across gateway (users, notifications, monitoring_alert_configs), core (ideas, idea_collaborators, chat_messages, ai_reactions, user_reactions, board_nodes, board_connections, brd_drafts, brd_versions, review_assignments, review_timeline_entries, collaboration_invitations, idea_keywords, merge_requests, admin_parameters), ai (chat_context_summaries, facilitator_context_bucket, context_agent_bucket, context_chunks, idea_embeddings). All indexes per data-model.md. pgvector extension creation migration. Seed data migrations for admin_parameters, singleton tables, dev users (conditional on DEBUG=True).
3. **[Auth] Auth bypass middleware + dev users + route protection** — Implement double-gated bypass (AUTH_BYPASS=True AND DEBUG=True). Session-based fake auth with 4 dev users per F-7.1. Auth middleware for REST (Bearer token extraction + validation skeleton) and WebSocket (handshake token). All routes protected — unauthenticated redirects to login. User sync to shadow table on validation.
4. **[Infra] gRPC infrastructure** — Proto definitions for all service contracts per api-design.md gRPC section: CoreService (GetIdeaContext, GetFullChatHistory, PersistChatMessage, PersistBoardUpdate, etc.), AIService (TriggerChatProcessing, TriggerBrdGeneration, UpdateFacilitatorBucket, UpdateContextAgentBucket), PDFService (GeneratePdf), NotificationService stubs. Generated Python stubs. gRPC server setup per service. Logging/error interceptors.
5. **[Infra] WebSocket infrastructure** — Django Channels setup with Redis channel layer. Base WebSocket consumer with auth handshake, subscribe_idea/unsubscribe_idea message handling, channel group management. Connection lifecycle skeleton (connect, subscribe, unsubscribe, disconnect). WebSocket URL routing.
6. **[Infra] Message broker + Celery** — RabbitMQ connection. Celery worker + beat configuration in core service. DLQ setup per queue (x-dead-letter-exchange). Base event publisher/consumer patterns. Celery periodic task registration skeleton (soft_delete_cleanup, monitoring_health_check, keyword_matching_sweep — all as no-op stubs with correct scheduling).
7. **[Frontend] Frontend scaffold** — React 19 + Vite 7 + TypeScript 5 setup. React Router with route definitions for /, /idea/:id, /reviews, /admin, /login. MSAL.js integration skeleton (MsalProvider, auth bypass detection). TanStack Query setup (QueryClient, devtools). Redux Toolkit store (empty slices for board, websocket, ui). Axios/fetch API client with auth header injection. WebSocket client class with reconnection logic skeleton.
8. **[Frontend] Design system foundation** — Tailwind CSS 4 (CSS-native config, no tailwind.config.ts). shadcn/ui initialization. CSS custom properties for theming on :root and .dark. Gotham font setup (self-hosted, fallback stack). Color tokens per design-system.md (Commerz Real Gold primary, teal accent, semantic colors). Dark mode toggle (class-based, localStorage persistence, prefers-color-scheme initial). react-i18next setup with de.json and en.json skeleton files. Language switcher (localStorage persistence).
9. **[Frontend] Shared UI primitives** — Implement all 16 shadcn/ui customized components per component-specs.md: Button (6 variants, 5 sizes), Card (base + variant slots), Input + Textarea (auto-grow), Select, Switch, Checkbox (indeterminate), Badge (state colors), Avatar (4 sizes, initials fallback, presence dot), Tooltip (300ms delay), DropdownMenu, Dialog (3 widths), Sheet, Tabs (gold underline), Skeleton (pulse), Toast (4 variants via react-toastify). All components support light/dark theme.
10. **[Frontend] Layout + cross-cutting components + state setup** — Navbar (logo+app name left, utility items right, role-gated links for Reviews/Admin, mobile hamburger). PageShell (Navbar + content wrapper). UserDropdown (language toggle, theme toggle, email prefs placeholder, logout). ConnectionIndicator (green/red dot + label). DevUserSwitcher (dev mode only). ErrorBoundary (React error boundary with fallback UI). ErrorToast (persistent toast with "Show Logs" + "Retry" buttons per F-14.1). ErrorLogModal (monospace error details + copy button). EmptyState (icon + message + optional action). LoadingSpinner. SkipLink (sr-only). NotificationBell stub (bell icon, 0 count, no panel). IdeasListFloating stub (empty floating panel in navbar).

## File Ownership (for parallel milestones)
This milestone is single (Wave 0) — no parallel ownership concerns. All files created here become the shared foundation.

Exclusive directories created:
- Root: `docker-compose.yml`, `nginx/`, `proto/`
- `services/gateway/` (Django project + apps skeleton)
- `services/core/` (Django project + apps skeleton)
- `services/ai/` (Django project skeleton)
- `services/notification/` (Python service skeleton)
- `services/pdf/` (Python service skeleton)
- `frontend/` (React app)
- `e2e/` (Playwright config skeleton)

## Milestone Acceptance Criteria
- [ ] `docker-compose up` starts all containers without errors
- [ ] PostgreSQL has all 22 tables with correct schemas, indexes, and seed data
- [ ] Auth bypass works: dev user switcher in navbar, all routes protected
- [ ] gRPC health checks pass between gateway ↔ core, gateway ↔ ai, gateway ↔ pdf
- [ ] WebSocket connects and responds to subscribe/unsubscribe
- [ ] RabbitMQ queues created with DLQ pairs
- [ ] Celery worker starts and beat schedules registered
- [ ] Frontend renders Navbar + PageShell with theme toggle (light/dark works)
- [ ] Language switch (de/en) updates UI labels
- [ ] All 16 UI primitives render correctly in both themes
- [ ] Error toast with "Show Logs" + "Retry" renders correctly
- [ ] 4 dev users switchable via navbar switcher
- [ ] TypeScript typecheck passes (`tsc --noEmit`)
- [ ] Backend lint passes (Ruff)
- [ ] All existing tests pass

## Notes
- **Stub: NotificationBell** — Renders bell icon with hardcoded 0 count. No floating panel. Panel + real notification data implemented in M10.
- **Stub: IdeasListFloating** — Empty floating panel attached to navbar button. Real idea lists implemented in M2.
- **Stub: Navbar review/admin links** — Conditionally visible based on user role, but link to empty route placeholder pages. Real pages in M2/M3.
- **Stub: Celery periodic tasks** — Registered with correct schedules but task body is a no-op pass statement. Real implementations: soft_delete_cleanup in M2, monitoring_health_check in M3, keyword_matching_sweep in M11.
- **Stub: gRPC service methods** — All proto-defined methods have stub implementations that return empty/default responses. Real implementations added per milestone.
- **Stub: WebSocket consumer** — Handles connect/disconnect/subscribe/unsubscribe. Does not broadcast any domain events yet. Chat events in M4, board events in M5, presence in M8.
- **Stub: LoginPage** — Renders logo + "Sign in with Microsoft" button. MSAL redirect skeleton. Full Azure AD flow is production-only configuration, not tested in dev bypass mode.
- **All 22 DB tables created here** to avoid migration conflicts in parallel milestones. Later milestones only add application logic, not schema changes.
