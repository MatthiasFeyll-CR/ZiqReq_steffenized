# E2E Test Infrastructure Setup — Interactive Session Prompt

Copy everything below the line into a new Claude Code session.

---

## Task: Set up E2E test infrastructure for the ZiqReq application

You are setting up the complete E2E test infrastructure for a large application. The app is fully implemented (16 milestones complete). We now need E2E tests. This session focuses ONLY on infrastructure — no test specs yet.

### Project Context

- **Repo root:** The current working directory
- **Tech stack:** React+TypeScript+Vite (frontend), Django+Python (backend), gRPC inter-service, PostgreSQL+pgvector, Redis, RabbitMQ, Django Channels/Daphne (WebSocket)
- **Services:** frontend, gateway (Django/Daphne:8000), core (Django/gRPC:50051), ai (gRPC:50052), notification, pdf (gRPC:50053), celery-worker, celery-beat
- **Existing docker-compose:** `infra/docker/docker-compose.yml` (development), `docker-compose.test.yml` (unit/integration tests — incomplete)
- **E2E test framework:** Playwright (already chosen in architecture docs)
- **E2E test location:** `e2e/` at repo root (currently only `.gitkeep`)
- **Frontend E2E:** `frontend/e2e/` (currently only `.gitkeep`) — NOT used, all E2E tests go in `e2e/` at root
- **Auth:** Development uses AUTH_BYPASS=True + DEBUG=True with 4 preconfigured dev users (User1: User, User2: User, User3: User+Reviewer, User4: User+Admin). No login screen in bypass mode — there's a user switcher in the navbar.
- **AI:** AI_MOCK_MODE=True makes the AI service return deterministic fixture responses from `services/ai/fixtures/`

### What to create (work with me interactively — propose each piece, I'll approve/adjust)

#### 1. `docker-compose.e2e.yml` (at repo root)
A **complete standalone** docker-compose file (not extending) for E2E tests. Should include:
- All infrastructure: postgres (pgvector:pg16), redis, rabbitmq
- All application services: frontend, gateway, core, ai, notification, pdf, celery-worker
- NO celery-beat (not needed for E2E)
- NO nginx (Playwright hits frontend dev server directly)
- Environment variables: `AI_MOCK_MODE=True`, `AUTH_BYPASS=True`, `DEBUG=True`, `EMAIL_BACKEND=django.core.mail.backends.filebased.EmailBackend`, `EMAIL_FILE_PATH=/tmp/e2e-emails/`
- Health checks on infrastructure services
- Service startup ordering (gateway waits for core, core waits for postgres, etc.)
- Reference `infra/docker/docker-compose.yml` for the existing service definitions — mirror the same build contexts, commands, ports, etc.

#### 2. `e2e/playwright.config.ts`
- Base URL: `http://localhost:5173` (Vite dev server, or adjust if using built frontend)
- Projects: Firefox (primary), 
-  Global setup/teardown scripts
- Timeout: 30s per test
- Retries: 1 on CI, 0 locally
- Reporter: HTML + list
- Output directory for traces and screenshots

#### 3. `e2e/global-setup.ts`
- Wait for all services to be healthy (poll gateway health endpoint or landing page)
- Run database seed (via API calls or management command)
- Verify app is reachable

#### 4. `e2e/global-teardown.ts`
- Cleanup test data if needed

#### 5. `e2e/helpers/auth.ts`
- Functions to authenticate as each of the 4 dev users
- The app uses a dev user switcher in the navbar (not a login page) when AUTH_BYPASS=True
- Should handle selecting/switching users via the UI or via cookie/session manipulation
- Read the frontend source to understand how the dev user switcher works

#### 6. `e2e/helpers/api.ts`
- Direct REST API call helpers for test setup/teardown
- Create idea, delete idea, submit idea for review, assign reviewer, create collaboration invitation, accept invitation
- Use `fetch` against `http://localhost:8000/api/...`
- Read the gateway URL patterns and views to discover actual API endpoints

#### 7. `e2e/helpers/websocket.ts`
- WebSocket connection helper for verifying real-time events in tests
- Connect to the gateway's WebSocket endpoint
- Subscribe to idea channels, wait for specific events

#### 8. `e2e/helpers/seed.ts`
- Programmatic seed functions callable from tests
- Create ideas in specific states (open, in_review, accepted, rejected, dropped)
- Create ideas with chat messages, board nodes, BRD drafts
- Uses the API helpers internally

#### 9. `e2e/helpers/assertions.ts`
- Common assertion helpers: toast visible with text, notification badge count, element has specific state
- Reusable across all test specs

#### 10. `e2e/helpers/email.ts`
- Read captured emails from the file-based email backend (`/tmp/e2e-emails/`)
- Assert email sent to recipient with expected subject/content
- Clear email directory between tests

#### 11. `e2e/pages/*.page.ts` — Page Object Models
- `landing.page.ts` — hero section, idea lists, search, filters, trash
- `workspace.page.ts` — chat panel, board tab, review tab, header, divider
- `review.page.ts` — categorized lists, search, self-assign
- `admin.page.ts` — 4 tabs (AI Context, Parameters, Monitoring, Users)
- `navbar.page.ts` — logo, navigation links, bell, user menu, dev switcher
- `components.page.ts` — toast, notification panel, error modal, banners

Each POM should:
- Accept a Playwright `Page` in constructor
- Expose locators for key elements
- Expose action methods (e.g., `createIdea(message)`, `switchUser(name)`)
- Use `data-testid` selectors where they exist, fall back to role/text selectors
- Read the actual frontend source code to find the correct selectors

#### 12. Smoke test `e2e/smoke.spec.ts`
- Navigate to `/`, verify landing page loads
- Verify dev user is authenticated (name visible in navbar)
- Trivial test to confirm the entire infrastructure works

### Guidelines
- Read the existing codebase before writing anything — understand the frontend component structure, API endpoints, WebSocket protocol, and auth mechanism
- Read `infra/docker/docker-compose.yml` to understand existing service definitions
- Read `docs/02-architecture/testing-strategy.md` and `docs/04-test-architecture/test-plan.md` for test architecture decisions
- Read the frontend source (`frontend/src/`) to understand component structure and find selectors for POMs
- Read the gateway URL patterns to discover API endpoints for helpers
- Propose each file, let me review and adjust before moving to the next
- Do NOT write any actual test specs (those come in M17+) — only infrastructure
- Install any needed npm packages (e.g., `@playwright/test`, `@axe-core/playwright`)
