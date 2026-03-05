# Testing Strategy

## Framework Selection

| Layer | Framework | Purpose | Justification |
|-------|-----------|---------|---------------|
| Frontend unit | Vitest | Component + utility + hook tests | Vite-native, fast, same config as build tool, Jest-compatible API |
| Frontend component | React Testing Library | Component rendering + interaction tests | Standard for React; tests user behavior, not implementation details |
| Frontend E2E | Playwright | Full browser user flow tests | Cross-browser, reliable, parallel execution, built-in trace viewer |
| Backend unit | pytest + pytest-django | Service + model + serializer tests | Standard Python/Django testing; fixtures, parametrize, async support |
| Backend integration | pytest + Django TestCase | API endpoint tests with real DB | DRF's APIClient + test database per run; gRPC servicer tests with mock clients |
| gRPC contract | pytest + grpcio-testing | gRPC service contract tests | Validates proto contracts match implementation |
| WebSocket | pytest + channels.testing | WebSocket consumer tests | Django Channels provides test utilities for consumer testing |
| E2E (cross-service) | Playwright | Full stack user journeys | Browser → gateway → core → AI (mocked) → WebSocket → browser |

## Test File Organization

| Type | Location | Naming | Example |
|------|----------|--------|---------|
| Frontend unit/component | Co-located with source | `*.test.tsx` / `*.test.ts` | `src/components/chat/chat-message.test.tsx` |
| Frontend hook tests | Co-located with hooks | `*.test.ts` | `src/features/chat/use-chat.test.ts` |
| Frontend E2E | `frontend/e2e/` | `*.spec.ts` | `frontend/e2e/idea-workspace.spec.ts` |
| Backend unit | `tests/` per Django app | `test_*.py` | `services/core/apps/ideas/tests/test_services.py` |
| Backend integration | `tests/` per Django app | `test_*.py` | `services/gateway/apps/authentication/tests/test_views.py` |
| gRPC contract | `tests/` per service | `test_*_servicer.py` | `services/core/grpc_server/tests/test_idea_servicer.py` |
| WebSocket | `tests/` in gateway websocket app | `test_consumers.py` | `services/gateway/apps/websocket/tests/test_consumers.py` |
| E2E | `e2e/` at repo root | `*.spec.ts` | `e2e/review-workflow.spec.ts` |

### Co-location Rationale (Frontend)

Frontend tests live next to the code they test. This keeps the test discoverable when reading the source and ensures tests are updated when the component changes. The `e2e/` directory is the exception — those tests span multiple pages and features.

### Separate `tests/` Directory (Backend)

Django convention. Each app has a `tests/` package with one file per layer (`test_models.py`, `test_services.py`, `test_views.py`). This aligns with the service layer pattern defined in `project-structure.md`.

---

## Test Boundaries

### Unit Tests

- **Scope:** Single function, class, component, or hook in isolation
- **Dependencies:** Mocked — database, external APIs, gRPC clients, message broker, WebSocket
- **Speed target:** < 50ms per test
- **What to test:**
  - **Frontend:** Component rendering, user interaction (click, type, submit), hook behavior, utility functions, Redux slice reducers, form validation
  - **Backend:** Service methods (business logic), model methods (if any), serializer validation, utility functions, Celery task logic (with mocked broker)
- **What NOT to test:** Framework internals, third-party library behavior, trivial getters/setters

### Integration Tests

- **Scope:** Service + its dependencies (database, middleware, serialization chain)
- **Dependencies:** Real test database (Django creates/destroys per test run), mocked gRPC clients, mocked message broker
- **Speed target:** < 500ms per test
- **What to test:**
  - **Gateway:** REST endpoint request → middleware → view → serializer → gRPC client call → response. Validates HTTP status codes, response shapes, auth/permission checks, error codes.
  - **Core:** gRPC servicer → service layer → database write/read → event publishing (mocked broker). Validates business logic end-to-end within the service.
  - **WebSocket:** Consumer receives message → processes → sends to group. Uses Django Channels `WebsocketCommunicator`.
  - **gRPC:** Servicer receives request → returns correct response. Uses `grpcio-testing` in-process channel.

### E2E Tests

- **Scope:** Full user flows across frontend + backend services
- **Dependencies:** All services running via Docker Compose. AI service responses mocked (deterministic fixtures).
- **Speed target:** < 15s per test
- **What to test:** Critical user journeys only (see Critical Test Flows below)
- **Environment:** Dedicated `docker-compose.test.yml` profile with:
  - Test database (seeded, reset between test suites)
  - AI service in mock mode (returns fixture responses)
  - All other services running normally

---

## Critical Test Flows

These flows must have E2E coverage. They represent the core user journeys and the highest-risk paths.

| Flow | Description | Features Covered |
|------|-------------|-----------------|
| **Idea creation** | User types message on landing page → idea created → redirected to workspace → chat message visible → AI responds (mocked) | FA-1, FA-2 |
| **Board interaction** | User creates box → edits content → creates connection → undo → redo | FA-3 |
| **BRD generation** | User opens Review tab → BRD generates (mocked) → sections visible → user edits section → section locks | FA-4 |
| **Submit for review** | Owner submits idea → state changes to in_review → workspace locks → reviewer sees idea on review page | FA-9, FA-10 |
| **Review cycle** | Reviewer self-assigns → posts comment → accepts idea → state changes to accepted → owner notified | FA-10, FA-12 |
| **Reject and resubmit** | Reviewer rejects → workspace unlocks → owner edits → resubmits → new BRD version created | FA-10, FA-4 |
| **Collaboration** | Owner invites user → invitee sees invitation → accepts → appears as collaborator → can edit | FA-8 |
| **Merge flow** | Similar idea detected (mocked) → owner sees suggestion → requests merge → target owner accepts → merged idea created (mocked) | FA-5 |
| **Auth bypass** | Dev login screen → select user → redirected to landing page → user identity visible | FA-7 |
| **Admin panel** | Admin navigates to admin panel → edits parameter → parameter saved → views monitoring dashboard | FA-11 |
| **Notifications** | Action triggers notification → bell badge increments → click shows notification → mark as read | FA-12 |
| **i18n** | Switch language → all visible text changes → preference persisted → reload maintains language | FA-16 |
| **Dark mode** | Toggle theme → all components switch to dark theme → preference persisted → reload maintains theme | NFR-T2 |

---

## Testing Patterns

### Pattern 1: Testing Authenticated Endpoints

**Backend (Gateway):**
```python
# tests/test_views.py
class TestIdeaCreation:
    def test_create_idea_authenticated(self, api_client, auth_user):
        """Authenticated user can create an idea."""
        api_client.force_authenticate(user=auth_user)
        response = api_client.post('/api/ideas', {'first_message': 'My idea'})
        assert response.status_code == 201

    def test_create_idea_unauthenticated(self, api_client):
        """Unauthenticated request returns 401."""
        response = api_client.post('/api/ideas', {'first_message': 'My idea'})
        assert response.status_code == 401
```

**Frontend:**
```typescript
// use-create-idea.test.ts
it('sends authenticated request', async () => {
  // Mock MSAL to return a token
  // Mock fetch to capture the request
  // Call the hook
  // Assert Authorization header present
});
```

### Pattern 2: Testing WebSocket Consumers

```python
# tests/test_consumers.py
from channels.testing import WebsocketCommunicator

async def test_subscribe_idea():
    """User subscribes to idea and receives events."""
    communicator = WebsocketCommunicator(IdeaConsumer.as_asgi(), "/ws/?token=valid")
    connected, _ = await communicator.connect()
    assert connected

    await communicator.send_json_to({"type": "subscribe_idea", "idea_id": "uuid"})
    # Trigger an event on the idea's channel group
    # Assert communicator receives the broadcast
    await communicator.disconnect()
```

### Pattern 3: Testing gRPC Servicers

```python
# tests/test_idea_servicer.py
from grpc_testing import server_from_dictionary

def test_get_idea_context():
    """GetIdeaContext returns full context for an idea."""
    servicer = IdeaServicer()
    server = server_from_dictionary({...}, servicer)
    request = IdeaContextRequest(idea_id="uuid", recent_message_limit=20)
    response, _, code, _ = server.unary_unary(request)
    assert code == grpc.StatusCode.OK
    assert response.metadata.idea_id == "uuid"
```

### Pattern 4: Testing Board Undo/Redo (Redux)

```typescript
// board-slice.test.ts
it('undoes AI action with correct label', () => {
  const store = createTestStore();
  // Dispatch an AI board mutation
  store.dispatch(addNode({ id: '1', source: 'ai', ... }));
  // Assert undo entry exists with AI label
  expect(store.getState().board.undoStack[0].source).toBe('ai');
  // Dispatch undo
  store.dispatch(undo());
  // Assert node removed from state
  expect(store.getState().board.nodes).not.toContainEqual(expect.objectContaining({ id: '1' }));
});
```

### Pattern 5: Testing Real-Time Cache Invalidation

```typescript
// use-chat.test.ts
it('invalidates chat query on WebSocket message', async () => {
  const queryClient = new QueryClient();
  // Render hook with QueryClientProvider
  // Simulate WebSocket chat_message event
  // Assert queryClient.invalidateQueries was called for the chat query key
});
```

### Pattern 6: Testing Event-Driven Flows (Message Broker)

```python
# tests/test_services.py
def test_submit_idea_publishes_event(mock_broker):
    """Submitting an idea publishes idea.submitted event."""
    submit_idea_for_review(idea_id="uuid", user_id="uuid", message="Ready", reviewer_ids=[])
    mock_broker.assert_published('idea.submitted', {
        'idea_id': 'uuid',
        'user_id': 'uuid',
    })
```

### Pattern 7: Testing AI Service Responses (Mocked)

> The AI Engineer defines how AI agents are tested internally (prompt testing, output validation, etc.) in `docs/03-ai/`. The Architect's testing strategy covers the integration boundary: does the rest of the system handle AI service responses correctly?

```python
# Gateway integration test
def test_ai_chat_response_event_creates_message(mock_ai_event):
    """ai.chat_response.ready event creates a chat message and broadcasts via WebSocket."""
    mock_ai_event.publish('ai.chat_response.ready', {
        'idea_id': 'uuid',
        'content': 'AI response text',
        'message_type': 'regular',
    })
    # Assert message persisted in chat_messages
    # Assert WebSocket broadcast sent
```

### Pattern 8: Testing Idempotent Event Handlers

```python
# tests/test_consumers.py
def test_duplicate_event_is_idempotent():
    """Processing the same event twice produces no duplicate side effects."""
    event = {'event_id': 'unique-123', 'idea_id': 'uuid', ...}
    handle_event(event)  # First processing
    handle_event(event)  # Duplicate
    # Assert only one chat message created, not two
```

---

## Test Data Strategy

### Unit Tests
- **Factory functions** using `factory_boy` (backend) and inline object builders (frontend).
- Each test creates only the data it needs. No shared fixtures across unrelated tests.
- Use `pytest.fixture` for common setups (authenticated user, idea with collaborators, etc.).

### Integration Tests
- **Django test database** — created fresh per test run, rolled back per test case (Django's `TransactionTestCase` for tests that need committed transactions, regular `TestCase` for the rest).
- **Fixtures via factory_boy** — `IdeaFactory`, `UserFactory`, `ChatMessageFactory`, etc. Create realistic test data with sensible defaults and easy overrides.
- **gRPC mocking** — `unittest.mock.patch` on gRPC client methods. Return predefined responses.
- **Message broker mocking** — mock the `publish_event` function. Assert events published with correct payloads.

### E2E Tests
- **Seed script** — `scripts/seed-e2e.py` creates baseline data: dev users, a few ideas in various states, chat history, board content, BRD drafts.
- **AI mock mode** — AI service runs with `AI_MOCK_MODE=True`, returns fixture responses from `services/ai/fixtures/`. This makes E2E tests deterministic.
- **Database reset** — test database dropped and recreated + re-seeded between test suites (not between individual tests — too slow).
- **File cleanup** — generated PDF files in test storage directory cleaned up after each suite.

---

## Coverage Standards

| Layer | Minimum | Target | Enforced |
|-------|---------|--------|----------|
| Backend services (business logic) | 80% | 90% | CI gate |
| Backend views/serializers | 70% | 80% | CI gate |
| Backend gRPC servicers | 80% | 90% | CI gate |
| Frontend components | 60% | 75% | Advisory |
| Frontend hooks/features | 70% | 85% | CI gate |
| Frontend utilities | 90% | 95% | CI gate |
| Redux slices | 90% | 95% | CI gate |
| E2E critical paths | 100% of listed flows | — | CI gate |

### Coverage Exclusions
- Auto-generated code (proto stubs, migration files)
- Configuration files (settings, URLs, routing)
- Type-only files (`types/*.ts`, proto message definitions)
- AI agent internals (covered by AI Engineer's testing strategy in `docs/03-ai/`)

---

## CI Integration

### Test Execution Pipeline

```
PR opened / Push to branch
│
├── Stage 1: Lint + Type Check (parallel, fast — < 30s)
│   ├── Frontend: ESLint + tsc --noEmit
│   └── Backend: Ruff + mypy (per service)
│
├── Stage 2: Unit Tests (parallel per service — < 2min)
│   ├── Frontend: Vitest (all .test.tsx/.test.ts files)
│   ├── Gateway: pytest (unit + integration)
│   ├── Core: pytest (unit + integration)
│   └── AI: pytest (unit — boundary tests only)
│
├── Stage 3: E2E Tests (sequential — < 10min)
│   ├── Docker Compose up (test profile)
│   ├── Seed test database
│   ├── Playwright (all .spec.ts files, parallelized across workers)
│   └── Docker Compose down
│
└── Results
    ├── Coverage reports uploaded (per service)
    ├── Playwright trace artifacts (on failure)
    └── Gate: all stages must pass to merge
```

### Parallelization
- **Unit tests:** Each service's tests run in parallel (separate CI jobs). Frontend tests parallelized by Vitest's built-in worker pool.
- **E2E tests:** Playwright runs tests in parallel across workers (default: 4). Tests are designed to be independent — each test creates its own data context.

### Failure Behavior
- **Stages 1-2:** Block merge. Must fix before merging.
- **Stage 3 (E2E):** Block merge. Playwright traces and screenshots attached as CI artifacts for debugging.
- **Coverage below minimum:** Block merge for CI-gated layers. Advisory warning for non-gated layers.

---

## Test Environment Configuration

### Docker Compose Test Profile

```yaml
# docker-compose.test.yml (extends docker-compose.yml)
services:
  postgresql:
    # Same image, separate test database name
    environment:
      POSTGRES_DB: ziqreq_test

  ai:
    # AI mock mode — returns fixture responses
    environment:
      AI_MOCK_MODE: "true"
      AI_FIXTURES_PATH: "/app/fixtures/"

  # No celery-beat in test profile (periodic tasks not needed)
  # celery-worker runs but with short timeouts
```

### Test-Specific Environment Variables

| Variable | Value | Purpose |
|----------|-------|---------|
| DJANGO_SETTINGS_MODULE | `*.settings.test` | Test settings (test DB, faster password hasher, disabled rate limiting) |
| AI_MOCK_MODE | true | AI service returns fixture responses |
| AUTH_BYPASS | true | E2E tests use dev auth bypass |
| DEBUG | true | Enable auth bypass + verbose errors |

---

## AI Service Testing Boundary

> The Architect defines testing for the system boundary with the AI service. The AI Engineer defines testing for AI internals (prompt quality, agent behavior, output validation, model regression) in `docs/03-ai/`.

**What the Architect's tests cover:**
- Gateway correctly forwards requests to AI service gRPC
- Gateway correctly handles AI service events (ai.chat_response.ready, ai.board.updated, etc.)
- Gateway correctly persists AI outputs via Core gRPC
- Gateway correctly broadcasts AI events via WebSocket
- Core correctly resets rate limit on ai.processing.complete
- Error handling when AI service is unavailable or returns errors
- E2E flows with mocked AI responses (deterministic)

**What the AI Engineer's tests cover:**
- Agent prompt effectiveness and quality
- Context assembly correctness
- Tool/plugin behavior
- Model output parsing and validation
- Embedding generation and similarity accuracy
- Processing pipeline orchestration
- Fabrication detection
- Security guardrails (content filtering, injection detection)
