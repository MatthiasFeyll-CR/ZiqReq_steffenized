# Test Plan

> **Status:** Definitive
> **Date:** 2026-03-04
> **Author:** Test Architect (Phase 4b)
> **Input:** All validated specs from phases [1]–[4] + Architect's `testing-strategy.md`

This document defines the overall test architecture for ZiqReq. It builds on the Software Architect's `testing-strategy.md` (which defines framework choices, file organization, test patterns, and CI pipeline) and goes deeper into concrete coverage standards, test utility design, and non-functional testing requirements.

**Relationship to `docs/02-architecture/testing-strategy.md`:** The architect's document remains the authoritative source for framework selection, test file organization, test boundaries, testing patterns (8 patterns), test data strategy, CI pipeline structure, and test environment configuration. This document extends it with coverage enforcement details, shared utility specifications, and non-functional testing requirements. There is no duplication — this plan references the architect's decisions and adds the layer needed for test case specification.

---

## Test Architecture Overview

| Layer | Scope | Framework | Speed Target | Mocking Strategy |
|-------|-------|-----------|-------------|-----------------|
| Frontend Unit | Single component, hook, utility, Redux slice | Vitest + React Testing Library | < 50ms | All external deps mocked (API, WebSocket, auth) |
| Frontend E2E | Full browser user flows | Playwright | < 15s | All services real, AI in mock mode |
| Backend Unit | Single service method, model method, serializer, utility | pytest + pytest-django | < 50ms | DB mocked or in-memory, gRPC mocked, broker mocked |
| Backend Integration | REST endpoint → middleware → view → serializer → gRPC/DB | pytest + Django TestCase | < 500ms | Real test DB, mocked gRPC clients, mocked broker |
| gRPC Contract | gRPC servicer request → response validation | pytest + grpcio-testing | < 200ms | In-process gRPC channel, real service logic, mocked deps |
| WebSocket | Consumer connect → subscribe → receive → process | pytest + channels.testing | < 500ms | WebsocketCommunicator, mocked auth |
| E2E (Cross-Service) | Full stack user journeys (browser → gateway → core → AI → WS → browser) | Playwright | < 15s per test | Docker Compose test profile, AI mock mode |
| AI Agent | Agent invocation → output validation | pytest | < 2s | Mocked Azure OpenAI (fixture responses), real Pydantic validation |

---

## Test Organization

Defined in `docs/02-architecture/testing-strategy.md` § Test File Organization. Summary:

| Layer | Location | Naming | Runner Command |
|-------|----------|--------|---------------|
| Frontend unit/component | Co-located: `src/**/*.test.tsx` / `*.test.ts` | `component-name.test.tsx` | `npx vitest run` |
| Frontend E2E | `frontend/e2e/` | `*.spec.ts` | `npx playwright test` |
| Backend unit | `services/{service}/apps/{app}/tests/test_*.py` | `test_services.py`, `test_models.py` | `pytest services/{service}/` |
| Backend integration | Same as unit (Django convention) | `test_views.py` | `pytest services/{service}/` |
| gRPC contract | `services/{service}/grpc_server/tests/test_*_servicer.py` | `test_idea_servicer.py` | `pytest services/{service}/` |
| WebSocket | `services/gateway/apps/websocket/tests/` | `test_consumers.py` | `pytest services/gateway/` |
| E2E cross-service | `e2e/` at repo root | `*.spec.ts` | `npx playwright test --config=e2e/playwright.config.ts` |
| AI agent | `services/ai/agents/*/tests/test_*.py` | `test_agent.py` | `pytest services/ai/` |

---

## Shared Test Utilities

These are utilities that tests will use across the project. They prevent duplication and standardize test patterns.

### Frontend

| Utility | Purpose | Location |
|---------|---------|----------|
| `renderWithProviders` | Wraps component with Redux store, QueryClient, Router, Theme, i18n providers | `frontend/src/test/helpers/render.tsx` |
| `createTestStore` | Creates a pre-configured Redux store with optional initial state overrides | `frontend/src/test/helpers/store.ts` |
| `createMockWebSocket` | Mock WebSocket connection that can emit server events | `frontend/src/test/helpers/websocket.ts` |
| `mockAuthUser` | Returns a mock MSAL user context with configurable roles | `frontend/src/test/helpers/auth.ts` |
| `buildIdeaFixture` | Factory for idea objects with sensible defaults | `frontend/src/test/fixtures/idea.ts` |
| `buildChatMessageFixture` | Factory for chat message objects | `frontend/src/test/fixtures/chat.ts` |
| `buildBoardNodeFixture` | Factory for board node objects | `frontend/src/test/fixtures/board.ts` |
| `buildBrdDraftFixture` | Factory for BRD draft objects | `frontend/src/test/fixtures/brd.ts` |
| `buildNotificationFixture` | Factory for notification objects | `frontend/src/test/fixtures/notification.ts` |
| `waitForQuerySettled` | Wait for TanStack Query to settle (no pending queries) | `frontend/src/test/helpers/query.ts` |

### Backend

| Utility | Purpose | Location |
|---------|---------|----------|
| `UserFactory` | factory_boy factory for users with configurable roles | `services/core/tests/factories.py` (shared) |
| `IdeaFactory` | Factory for ideas in various states | `services/core/tests/factories.py` |
| `ChatMessageFactory` | Factory for chat messages (user + AI) | `services/core/tests/factories.py` |
| `BoardNodeFactory` | Factory for board nodes (box, group, free_text) | `services/core/tests/factories.py` |
| `BrdDraftFactory` | Factory for BRD drafts with section content | `services/core/tests/factories.py` |
| `ReviewAssignmentFactory` | Factory for reviewer assignments | `services/core/tests/factories.py` |
| `MergeRequestFactory` | Factory for merge requests in various states | `services/core/tests/factories.py` |
| `MockGrpcClient` | Reusable mock for gRPC client calls with configurable responses | `services/gateway/tests/helpers/grpc_mock.py` |
| `MockBrokerPublisher` | Captures published events for assertion | `services/core/tests/helpers/broker_mock.py` |
| `AuthenticatedAPIClient` | DRF APIClient with pre-authenticated user | `services/gateway/tests/helpers/api_client.py` |

### AI Service

| Utility | Purpose | Location |
|---------|---------|----------|
| `MockAzureOpenAI` | Returns fixture responses keyed by agent type and scenario | `services/ai/tests/helpers/mock_openai.py` |
| `AgentTestHarness` | Base class for testing any agent: sets up kernel, mocks, validates output | `services/ai/tests/helpers/agent_harness.py` |
| `FacilitatorFixtures` | Pre-built facilitator input scenarios (new idea, long conversation, delegation) | `services/ai/tests/fixtures/facilitator.py` |
| `BrdFixtures` | Pre-built BRD generation scenarios (full, selective, gaps mode) | `services/ai/tests/fixtures/brd.py` |

---

## Coverage Standards

| Layer | Minimum | Target | Enforcement | Rationale |
|-------|---------|--------|-------------|-----------|
| Backend services (business logic) | 80% | 90% | CI gate | Core business rules must be thoroughly tested |
| Backend views/serializers | 70% | 80% | CI gate | API contract validation |
| Backend gRPC servicers | 80% | 90% | CI gate | Inter-service contract reliability |
| Backend WebSocket consumers | 70% | 85% | CI gate | Real-time event handling correctness |
| Frontend components | 60% | 75% | Advisory | Component rendering and interaction |
| Frontend hooks/features | 70% | 85% | CI gate | State management and data fetching logic |
| Frontend utilities | 90% | 95% | CI gate | Pure functions with clear inputs/outputs |
| Redux slices | 90% | 95% | CI gate | Undo/redo, WebSocket state, UI state — critical for correctness |
| AI agent boundary tests | 70% | 85% | CI gate | Agent output validation, guardrail enforcement |
| E2E critical paths | 100% of 13 flows | — | CI gate | All flows listed in architect's testing-strategy.md |

### Coverage Exclusions
- Auto-generated code (proto stubs, migration files, Django management commands)
- Configuration files (settings, URLs, ASGI/WSGI)
- Type-only files (`types/*.ts`, proto message definitions)
- AI agent internals beyond boundary tests (prompt quality is not coverage-measurable)
- Third-party library wrappers with no custom logic

### Coverage Tool Configuration
- **Frontend:** Vitest built-in coverage with `@vitest/coverage-v8`. Config in `vitest.config.ts`.
- **Backend:** `pytest-cov` with `--cov-report=xml` for CI upload. Config in `pyproject.toml` per service.
- **Reports:** Coverage XML uploaded as CI artifact. PR comments show coverage delta.

---

## Test Execution Strategy

### Development (Watch Mode)
- **Frontend:** `npx vitest --watch` — runs affected tests on file save. Co-located tests run when source file changes.
- **Backend:** `pytest-watch` or `pytest --looponfail` — reruns failed tests on file save. Scoped to the service being developed.
- **AI tests:** Run manually (`pytest services/ai/agents/`) — not in watch mode (slow due to mock setup).

### Pre-Commit
- **Lint + Type Check:** ESLint + `tsc --noEmit` (frontend), Ruff + mypy (backend per service).
- **Fast unit subset:** Not enforced at pre-commit (too slow). Lint and type checks only.

### CI Pipeline (Per PR / Push)
Defined in `docs/02-architecture/testing-strategy.md` § CI Integration. Summary:

```
Stage 1: Lint + Type Check (parallel, < 30s)
  ├── Frontend: ESLint + tsc --noEmit
  └── Backend: Ruff + mypy (per service)

Stage 2: Unit + Integration Tests (parallel per service, < 2min)
  ├── Frontend: Vitest (all .test.tsx/.test.ts)
  ├── Gateway: pytest (unit + integration)
  ├── Core: pytest (unit + integration)
  ├── AI: pytest (unit + agent boundary tests)
  ├── Notification: pytest (unit)
  └── PDF: pytest (unit)

Stage 3: E2E Tests (sequential, < 10min)
  ├── Docker Compose up (test profile)
  ├── Seed test database
  ├── Playwright (all .spec.ts, 4 parallel workers)
  └── Docker Compose down

Stage 4: Coverage Report
  ├── Merge per-service coverage
  ├── Enforce minimum thresholds (gate)
  └── Post coverage delta to PR
```

### Nightly (Extended Suite)
- **Accessibility audit:** axe-core automated scan on all pages via Playwright
- **Bundle size check:** size-limit on frontend build output
- **Extended E2E:** Full E2E suite with longer timeouts and additional edge case scenarios
- **AI fixture regression:** Run all AI agent tests with updated fixture responses to detect model behavior drift

---

## Non-Functional Testing

| Type | Tool | When | Threshold | Features |
|------|------|------|-----------|----------|
| Accessibility | axe-core via @axe-core/playwright | Nightly + per-page in E2E | 0 critical/serious violations | NFR-A1 through NFR-A5 |
| Bundle size | size-limit | CI (Stage 4) | Main bundle < 500 kB gzipped | NFR-P1 (page load < 2s) |
| Lighthouse performance | Playwright + Lighthouse CI | Nightly | LCP < 2s, FID < 100ms, CLS < 0.1 | NFR-P1 |
| API response time | pytest benchmark plugin | Nightly | p95 < 500ms for REST, p95 < 100ms for WebSocket | NFR-P2, NFR-P3 |
| Security headers | Playwright response intercept | E2E (spot check) | CSP, X-Frame-Options, etc. present | NFR-S1 |
| i18n completeness | Custom script (compare de.json vs en.json keys) | CI (Stage 1) | 0 missing translation keys | FA-16 |

---

## AI Service Testing Strategy

The AI service has unique testing needs due to non-deterministic model outputs.

### Testing Layers for AI

| Layer | What It Tests | Mock Level |
|-------|--------------|------------|
| Agent unit | Pydantic input/output validation, context assembly logic, token budget calculation | All external calls mocked |
| Agent boundary | Full agent invocation with mocked Azure OpenAI → validate output schema, constraints, guardrails | Azure OpenAI returns fixture responses |
| Pipeline integration | Full pipeline orchestration (debounce → context assembly → agent → output → event publish) | Azure OpenAI mocked, gRPC mocked, broker captured |
| Guardrail tests | Input validation, output validation, fabrication detection, XML escaping | Agent output fixtures with known violations |
| E2E (AI mock mode) | Full stack with AI_MOCK_MODE=True returning deterministic fixtures | AI service returns pre-defined responses |

### What We Do NOT Test
- **Prompt quality** — not measurable via automated tests. Evaluated during development and through QA review.
- **Model behavior drift** — addressed by fixture-based regression tests, not live model calls in CI.
- **Azure OpenAI availability** — external dependency, not our responsibility to test.

---

## Test Database Strategy

| Layer | Strategy | Isolation |
|-------|----------|-----------|
| Backend unit | No database — all DB access mocked | N/A |
| Backend integration | Django test database (created/destroyed per test run) | `TestCase` for transaction rollback, `TransactionTestCase` for committed transactions |
| gRPC contract | Same as integration — test database | Same isolation |
| WebSocket | Same as integration — test database | Same isolation |
| E2E | Dedicated `ziqreq_test` database via Docker Compose test profile | Seeded before suite, database dropped/recreated between suites |

### Test Database Configuration
- PostgreSQL with pgvector extension (same as production)
- Faster password hasher in test settings (`django.contrib.auth.hashers.MD5PasswordHasher`)
- Disabled rate limiting in test settings
- Synchronous Celery execution (`CELERY_ALWAYS_EAGER=True`) for integration tests

---

## Relationship to Downstream Skills

| Skill | What It Reads | How It Uses It |
|-------|--------------|----------------|
| **PRD Writer** | `test-matrix.md` | Includes test IDs in story Notes fields as `Testing: T-X.X.01, T-X.X.02` |
| **Strategy Planner** | `test-plan.md`, `integration-scenarios.md` | Test overhead per milestone, cross-milestone test dependencies, test infrastructure stories |
| **QA Engineer** | `test-matrix.md`, `runtime-safety.md` | Verification checklist — validates Ralph wrote the specified tests |
| **Pipeline Configurator** | `test-plan.md` | Test runner commands for CI gate checks, coverage thresholds |
