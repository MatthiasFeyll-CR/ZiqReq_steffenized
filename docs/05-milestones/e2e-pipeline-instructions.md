# E2E Pipeline Instructions (M17–M21)

Instructions for the pipeline configurator and implementing agents.

## What changed since the last pipeline cycle

The application (M1–M16) is complete. This cycle adds E2E tests only. The E2E test infrastructure is already built and committed:

```
e2e/
├── playwright.config.ts       # Chromium + Firefox, 30s timeout, retries on CI
├── global-setup.ts            # Polls gateway + frontend, verifies dev users
├── global-teardown.ts
├── helpers/
│   ├── auth.ts                # loginAs(page, "carol"), switchUser(page, "bob")
│   ├── api.ts                 # REST helpers: createIdea, submitIdea, assignReview, etc.
│   ├── websocket.ts           # TestWebSocket class for verifying real-time events
│   ├── seed.ts                # seedOpenIdea, seedInReviewIdea, seedAcceptedIdea, etc.
│   ├── assertions.ts          # expectToast, expectNotificationCount, etc.
│   └── email.ts               # Read file-based email backend, assert email sent
├── pages/
│   ├── landing.page.ts        # HeroSection, FilterBar, idea lists, search
│   ├── workspace.page.ts      # WorkspaceHeader, ChatPanel, BoardTab, ReviewTab
│   ├── review.page.ts         # Collapsible categories, review cards
│   ├── admin.page.ts          # 4 tabs with testid-based locators
│   ├── navbar.page.ts         # Logo, nav links, bell, user menu
│   └── components.page.ts     # Toasts, notification panel, dev switcher, banners
├── smoke.spec.ts              # 4 passing smoke tests (infrastructure validation)
├── package.json               # @playwright/test, @axe-core/playwright, ws, typescript
└── tsconfig.json

docker-compose.e2e.yml         # Standalone full-stack: all services, AI_MOCK_MODE, AUTH_BYPASS
```

A passing smoke test validates the infrastructure works.

## Pipeline config changes needed

### New milestones (append to milestones array)

```json
{ "id": 17, "slug": "e2e-foundation",       "name": "E2E Foundation Tests",                "stories": 5,  "dependencies": [16] },
{ "id": 18, "slug": "e2e-workspace",        "name": "E2E Workspace, Chat & Board Tests",   "stories": 10, "dependencies": [17] },
{ "id": 19, "slug": "e2e-review-collab",    "name": "E2E BRD, Review & Collaboration",     "stories": 10, "dependencies": [18] },
{ "id": 20, "slug": "e2e-similarity-admin", "name": "E2E Similarity, Merge & Admin",       "stories": 9,  "dependencies": [19] },
{ "id": 21, "slug": "e2e-journeys-edge",    "name": "E2E Error Handling & User Journeys",  "stories": 8,  "dependencies": [20] }
```

### E2E test execution config

Add an `e2e` section under `test_execution`:

```json
"e2e": {
  "compose_file": "docker-compose.e2e.yml",
  "setup_command": "docker compose -f docker-compose.e2e.yml up -d --build",
  "teardown_command": "docker compose -f docker-compose.e2e.yml down",
  "force_teardown_command": "docker compose -f docker-compose.e2e.yml down -v --remove-orphans",
  "test_command": "cd e2e && npx playwright test",
  "test_single_command": "cd e2e && npx playwright test {spec_file}",
  "setup_timeout_seconds": 180,
  "timeout_seconds": 900,
  "health_poll": {
    "gateway": "http://localhost:8000/api/auth/dev-users",
    "frontend": "http://localhost:5173",
    "poll_interval_ms": 2000,
    "max_wait_ms": 120000
  }
}
```

### Gate checks for E2E milestones

Add to `gate_checks.checks`:

```json
{
  "name": "E2E typecheck",
  "command": "cd e2e && npx tsc --noEmit",
  "condition": "test -f e2e/tsconfig.json",
  "required": true
},
{
  "name": "E2E tests",
  "command": "cd e2e && npx playwright test",
  "condition": "test -f e2e/playwright.config.ts",
  "required": true
}
```

The E2E test gate check replaces the unit test gate for milestones 17–21. The implementing agent must run all E2E tests (not just the current milestone's) after each story.

## How the implementing agent should work

### Auth in tests

The app uses `AUTH_BYPASS=True` with 4 dev users. No login form — auth is via API.
All API calls (including auth) go through the Vite proxy at `localhost:5173/api/...`
so cookies stay on the same origin as the page. Never call `localhost:8000` directly
from `page.request` — use the proxy.

Dev users match the DB seed migration (`0002_seed_dev_users.py`):
- `user1`: basic user (`[user]`), display: "Dev User 1"
- `user2`: basic user (`[user]`), display: "Dev User 2"
- `user3`: reviewer (`[user, reviewer]`), display: "Dev User 3"
- `user4`: admin (`[user, admin]`), display: "Dev User 4"

```typescript
import { loginAs } from "./helpers/auth";
// Calls POST /api/auth/dev-login via Vite proxy, sets session cookie, navigates to /
await loginAs(page, "user1");   // basic user
await loginAs(page, "user4");   // admin
await loginAs(page, "user3");   // reviewer
```

For multi-user tests, use separate browser contexts:
```typescript
const ctxA = await browser.newContext();
const ctxB = await browser.newContext();
const pageA = await ctxA.newPage();
const pageB = await ctxB.newPage();
await loginAs(pageA, "carol");
await loginAs(pageB, "dave");
```

### Seeding test data

Use `helpers/seed.ts` for API-level setup, not UI clicks:
```typescript
import { authenticateRequest, seedInReviewIdea } from "./helpers/seed";
await authenticateRequest(request, "user1");
const idea = await seedInReviewIdea(request);
```

### Running tests

```bash
# Full suite
cd e2e && npx playwright test

# Single spec
cd e2e && npx playwright test auth.spec.ts

# With UI for debugging
cd e2e && npx playwright test --ui
```

The docker-compose must be running first. Global setup polls for readiness automatically.

### File naming convention

Each story produces one spec file in `e2e/`:
```
e2e/auth.spec.ts           # M17 S1
e2e/landing-crud.spec.ts   # M17 S2
e2e/landing-filter.spec.ts # M17 S3
e2e/theme.spec.ts          # M17 S4
e2e/i18n.spec.ts           # M17 S5
e2e/workspace-layout.spec.ts  # M18 S1
...
```

### When tests fail

**If the test itself is wrong:** fix the test.

**If a production bug is found:** fix the production code in `services/` or `frontend/src/`. This is expected — E2E tests are the final verification layer. Document fixes with a brief comment in the commit message. Run the full E2E suite after every production fix to catch regressions.

### What NOT to do

- Do not modify `e2e/helpers/`, `e2e/pages/`, `e2e/playwright.config.ts`, or `docker-compose.e2e.yml` unless a bug is found in them. The infrastructure is tested and working.
- Do not write unit tests. This cycle is E2E only.
- Do not refactor production code unless required to fix a bug exposed by E2E tests.
- Do not add new features.

## Milestone scope files

Each milestone's full story breakdown, acceptance criteria, and execution rules are in:
- `docs/05-milestones/milestone-17.md` through `milestone-21.md`
- `docs/05-milestones/release-plan-e2e.md`
- `docs/05-milestones/dependency-analysis-e2e.md`

The milestone files are the source of truth for what each story must test.
