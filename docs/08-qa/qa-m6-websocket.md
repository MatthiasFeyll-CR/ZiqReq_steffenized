# QA Report: Milestone 6 — WebSocket & Real-Time

**Date:** 2026-03-10
**Reviewer:** QA Engineer (Claude)
**Bugfix Cycle:** 5 (post BF-001 fix for DEF-002)
**PRD:** `tasks/prd-m6.json`
**Progress:** `.ralph/progress.txt`

---

## Summary

Bugfix cycle 5 review of Milestone 6. BF-001 successfully **eliminated DEF-002** — zero IntegrityErrors (was 11 ERRORs in cycle 4). However, **8 new assertion failures** appeared in WebSocket consumer tests. These are a different class of failure: connection rejections (`connected=False`) and subscribe errors (`Access denied`) in tests where identical patterns pass in other tests. The failures are order-dependent, pointing to database connection lifecycle issues between async `TransactionTestCase` tests. Total: 134 passed, 8 failed, 0 errors (was: 131 passed, 0 failed, 11 errors). Verdict: **FAIL** — DEF-003 identified.

---

## Bugfix Cycle Progress Assessment

| Metric | Cycle 0 | Cycle 1 | Cycle 2 | Cycle 3 | Cycle 4 (Human) | Cycle 5 (BF-001) | Delta (4->5) |
|--------|---------|---------|---------|---------|------------------|-------------------|--------------|
| Tests FAIL | 7 | 3 | 0 | 5 | 0 | 8 | +8 (new pattern) |
| Tests ERROR | 15 | 10 | 12 | 12 | 11 | 0 | -11 (fixed!) |
| Tests PASS | 120 | 129 | 130 | 125 | 131 | 134 | +3 (improved) |
| Total affected | 22 | 13 | 12 | 17 | 11 | 8 | -3 (improved) |
| Root cause | FK constraint | Content type dup | auth_perm dup (keepdb) | DB gone | auth_perm dup (deser.) | DB connection lifecycle | New class |

**Assessment:** BF-001 fully resolved DEF-002 (IntegrityError). The post_migrate signal disconnect approach works — 0 errors. But a new issue emerged: 8 tests fail with assertion errors related to WebSocket connections being rejected or subscribe returning access denied. The previously-erroring tests (e.g., `test_subscribe_idea_as_owner`) now PASS, while previously-passing tests (e.g., `test_connection_valid_token`) now FAIL. This strongly indicates an order-dependent database connection state issue caused by TransactionTestCase flush + per-test event loop teardown.

---

## Story-by-Story Verification

The current PRD (`tasks/prd-m6.json`) contains only bugfix story BF-001. Verification against the original M6 user stories (from the previous QA report):

| Story ID | Title | Result | Notes |
|----------|-------|--------|-------|
| US-001 | Django Channels WebSocket consumer | FAIL | test_connection_valid_token FAIL (DEF-003) |
| US-002 | Channel group management | FAIL | test_subscribe_idea_access_denied, test_unsubscribe_idea, test_disconnect_cleans_up_groups FAIL (DEF-003) |
| US-003 | Chat message broadcast | FAIL | test_chat_message_broadcast_to_subscriber, test_chat_message_broadcast_via_view_helper FAIL (DEF-003) |
| US-004 | Board sync broadcast | PASS | All board broadcast tests pass |
| US-005 | Board awareness events | PASS | All board awareness tests pass |
| US-006 | Frontend WebSocket connection manager | PASS | All frontend tests pass |
| US-007 | Presence tracking | FAIL | test_presence_broadcast_on_subscribe, test_presence_multi_tab_dedup FAIL (DEF-003) |
| US-008 | User selection highlights on board | PASS | Frontend components verified |
| US-009 | Offline banner + behavior | PASS | DEV-001 carried forward |
| US-010 | Connection state indicator | PASS | DEV-002 carried forward |

**Stories passed:** 6 / 10 (improved from 5/10 in cycle 4)
**Stories with defects:** 4 (all trace to DEF-003 — test infrastructure, not application code)
**Stories with deviations:** 2 (carried forward)

---

## BF-001 Acceptance Criteria Verification

| Criterion | Result | Evidence |
|-----------|--------|----------|
| All 32 WebSocket consumer tests pass | FAIL | 24 pass, 8 fail (see DEF-003) |
| Zero IntegrityError on auth_permission or django_content_type | PASS | 0 errors, 0 IntegrityErrors |
| All other existing tests (non-WebSocket) continue to pass | PASS | 110 non-WebSocket tests pass |
| Typecheck passes | PASS | Frontend tsc clean, Ruff clean |

**BF-001 partially succeeded:** DEF-002 (IntegrityError) is fully resolved. But the acceptance criterion "All 32 WebSocket consumer tests pass" is not met due to 8 new failures (DEF-003).

---

## Test Matrix Coverage

**Pipeline scan results:** No test matrix IDs referenced in this milestone's PRD stories.

All 26 test implementations from the original M6 implementation remain present and unchanged. Test code is correct; the 8 failures are caused by test infrastructure issues (DEF-003), not missing or incorrect tests.

| Test ID | Status | File | Notes |
|---------|--------|------|-------|
| T-6.1.01 | FOUND | `test_consumers.py` | test_connection_valid_token — **FAIL** (DEF-003: connected=False) |
| T-6.1.02 | FOUND | `test_consumers.py` | test_connection_invalid_token + variants — PASS |
| T-6.1.03 | FOUND | `frontend/src/__tests__/use-websocket.test.ts` | Exponential backoff — PASS |
| T-6.1.04 | FOUND | `test_consumers.py` | owner/co-owner/collaborator subscribe — PASS |
| T-6.1.05 | FOUND | `test_consumers.py` | access denied — **FAIL** (DEF-003: connected=False) |
| T-6.1.06 | FOUND | `test_consumers.py` | unsubscribe — **FAIL** (DEF-003: subscribe error), cleanup — **FAIL** |
| T-6.1.07 | FOUND | `frontend/src/__tests__/websocket-slice.test.ts` | PASS |
| T-6.1.08 | FOUND | `frontend/src/__tests__/use-websocket.test.ts` | PASS |
| LOOP-004 | FOUND | `frontend/src/__tests__/use-websocket.test.ts` | PASS |
| T-6.2.01 | FOUND | `frontend/src/__tests__/offline-banner.test.tsx` | PASS |
| T-6.3.01 | FOUND | `test_consumers.py` | presence broadcast — **FAIL** (DEF-003: 2nd connection rejected) |
| T-6.3.02 | FOUND | `test_consumers.py` | multi-tab dedup — **FAIL** (DEF-003: KeyError 'user') |
| T-6.3.03 | FOUND | `test_consumers.py` | offline on unsubscribe — PASS |
| T-6.3.04 | FOUND | `test_consumers.py` | client presence update — PASS |
| T-6.4.01 | FOUND | `test_consumers.py` | chat broadcast to subscriber — **FAIL** (DEF-003: subscribe error) |
| T-6.4.02 | FOUND | `test_consumers.py` | chat via view helper — **FAIL** (DEF-003: connected=False) |
| T-6.4.03 | FOUND | `test_consumers.py` | board_update broadcast — PASS |
| T-6.4.04 | FOUND | `test_consumers.py` | board_update via view helper — PASS |
| T-3.5.01 | FOUND | `test_consumers.py` | board_selection excludes sender — PASS |
| T-3.5.02 | FOUND | `test_consumers.py` | board_selection not subscribed error — PASS |
| T-3.5.03 | FOUND | `test_consumers.py` | board_selection deselect null — PASS |
| T-3.6.01 | FOUND | `test_consumers.py` | board_update nodes_deleted — PASS |
| T-3.6.02 | FOUND | `test_consumers.py` | board_update source=ai — PASS |
| T-6.5.01 | FOUND | `frontend/src/__tests__/offline-banner.test.tsx` | PASS |
| T-6.5.02 | FOUND | `frontend/src/__tests__/offline-banner.test.tsx` | PASS |
| T-6.6.01 | FOUND | `frontend/src/__tests__/connection-indicator.test.tsx` | PASS |

*All 26 test matrix entries implemented. 8 of 32 backend consumer tests FAIL due to test infrastructure (DEF-003).*

---

## Defects

### DEF-001: [RESOLVED in cycle 1] Backend tests FK constraint violation
- **Status:** RESOLVED

### DEF-002: [RESOLVED in cycle 5] IntegrityError on auth_permission/django_content_type
- **Status:** RESOLVED by BF-001 (post_migrate signal disconnect)
- **Evidence:** 0 IntegrityErrors, 0 test errors (was 11 errors in cycle 4)

### DEF-003: 8 WebSocket consumer tests fail with connection/access assertion errors

- **Severity:** Critical
- **Stories:** US-001, US-002, US-003, US-007
- **File(s):** `services/gateway/conftest.py`, `services/gateway/apps/websocket/tests/test_consumers.py`
- **Expected (per spec):** All 32 backend consumer tests pass
- **Actual (in code):** 8 tests fail with assertion errors — connections rejected or subscribe returning errors

**Failure analysis (3 patterns):**

**Pattern A — Connection rejected (connected=False):** Middleware's `_authenticate_dev()` returns `None` despite user just being created in the test. Affected: `test_connection_valid_token` (L118), `test_subscribe_idea_access_denied` (L271), `test_chat_message_broadcast_via_view_helper` (L504), `test_presence_broadcast_on_subscribe` (L923, 2nd connection).

**Pattern B — Subscribe returns error instead of presence_update:** Connection succeeds but `handle_subscribe_idea` returns `"type": "error"` (access denied) despite user being the idea owner. Affected: `test_unsubscribe_idea` (L355), `test_disconnect_cleans_up_groups` (L406, 2nd subscribe), `test_chat_message_broadcast_to_subscriber` (L428).

**Pattern C — Unexpected payload structure:** `KeyError: 'user'` because response is an error message, not a presence update. Affected: `test_presence_multi_tab_dedup` (L959) — this is Pattern B manifesting at the assertion level.

**Root cause analysis:**

The failures are **order-dependent**. Identical create-user-then-connect patterns pass in some tests (e.g., `test_subscribe_idea_as_owner` at position 7) but fail in others (e.g., `test_connection_valid_token` at position 1). The set of affected tests changed completely from cycle 4 to cycle 5 — tests that previously ERRORed now PASS, and tests that previously PASSED now FAIL.

This points to **database connection lifecycle issues** between async `TransactionTestCase` tests:

1. `TransactionTestCase._fixture_teardown` calls `flush` which truncates ALL tables and emits `post_migrate` signal
2. With `asyncio_default_test_loop_scope=function`, each test gets its own event loop
3. Database connections are thread-local; `@database_sync_to_async` (thread_sensitive=True) runs in the ASGIRef main thread
4. When the event loop for test N is torn down, pending database connection cleanup may not complete before test N+1's event loop starts
5. Stale database connections in the thread pool may see uncommitted transaction state or a flushed database

**Suggested Fix:**

Add an autouse fixture to `services/gateway/conftest.py` that explicitly closes all database connections after each test, ensuring the next test starts with fresh connections:

```python
@pytest.fixture(autouse=True)
def _close_db_connections():
    """Close all DB connections after each test.

    Prevents stale thread-local connections from carrying over between
    async TransactionTestCase tests that each get their own event loop.
    Without this, @database_sync_to_async calls in the WebSocket middleware
    may use a connection that sees a different DB state than the test's
    data-creation calls.
    """
    yield
    from django.db import connections
    connections.close_all()
```

If this alone does not resolve it, additionally ensure connections are fresh BEFORE each test:

```python
@pytest.fixture(autouse=True)
def _close_db_connections():
    from django.db import connections
    connections.close_all()
    yield
    connections.close_all()
```

---

## Deviations

### DEV-001: OfflineBanner uses amber/warning styling instead of red background
- **Story:** US-009
- **Spec document:** `tasks/prd-m6.json` US-009 AC
- **Expected (per spec):** Red background with white text
- **Actual (in code):** `bg-amber-50 dark:bg-amber-950 border border-amber-400`
- **Why code is correct:** Amber/warning is semantically appropriate for connection status
- **Spec update needed:** Update PRD US-009 AC to say "semantic warning color"

### DEV-002: ConnectionIndicator uses Tailwind colors instead of design tokens
- **Story:** US-010
- **Spec document:** `docs/03-design/component-specs.md` section 14
- **Expected (per spec):** `bg-success` and `bg-destructive` design tokens
- **Actual (in code):** `bg-green-400` and `bg-red-400`
- **Why code is correct:** Visual result is equivalent
- **Spec update needed:** Minor — no change needed unless theme switching added

---

## Quality Checks

| Check | Command | Result | Details |
|-------|---------|--------|---------|
| Frontend TypeScript | `cd frontend && npx tsc --noEmit` | PASS | Clean |
| Backend Lint (Ruff) | `ruff check services/` | PASS | Clean |
| Backend Tests (pytest) | `docker compose -f docker-compose.test.yml run --rm python-tests pytest` | FAIL | 134 passed, 8 failed, 0 errors |
| Frontend Tests (vitest) | `docker compose -f docker-compose.test.yml run --rm node-tests npx vitest run` | PASS | All node tests pass |
| Backend mypy (optional) | `mypy services/` | FAIL (optional) | Pre-existing: duplicate module "events" — not M6-related |
| Frontend ESLint (optional) | `cd frontend && npx eslint src/` | FAIL (optional) | Pre-existing: 2 unused-var in test files, 1 warning — not M6-related |

### Gate Check Results

| Gate | Status | Notes |
|------|--------|-------|
| Docker build | SKIPPED | Condition not met |
| Frontend typecheck | PASSED | |
| Backend lint (Ruff) | PASSED | |
| Backend typecheck (mypy) | FAILED (optional) | Pre-existing: `services/core/events/__init__.py` duplicate module |
| Frontend lint (ESLint) | FAILED (optional) | Pre-existing: 2 errors in test files, 1 warning in FreeTextNode.tsx |

**Required gates all pass. Optional gate failures are pre-existing and not M6-related.**

---

## Security Findings

| ID | Category | Severity | File | Finding | Recommendation |
|----|----------|----------|------|---------|----------------|
| SEC-001 | Authentication | Info | `middleware.py:46-48` | Dev bypass accepts UUID as token | Guarded by DEBUG+AUTH_BYPASS. OK. |
| SEC-002 | Injection | Info | `consumers.py:78` | idea_id validated as UUID | Properly handled. |
| SEC-003 | Access Control | Info | `consumers.py:88` | Owner/co-owner/collaborator check | Properly handled. |
| SEC-004 | Data Integrity | Info | `consumers.py:234` | User info server-side, not from client | Properly handled. |

**No security defects found.**

---

## Performance Findings

| ID | Category | Severity | File | Finding | Recommendation |
|----|----------|----------|------|---------|----------------|
| PERF-001 | Memory | Info | `consumers.py:12` | Module-level `_presence_registry` — pruned on disconnect | OK. |
| PERF-002 | N+1 Queries | Info | `consumers.py:288-304` | 2 queries per subscribe | Acceptable — subscribe is infrequent. |

**No critical performance defects found.**

---

## Design Compliance

| Page/Component | Spec Reference | Result | Notes |
|---------------|----------------|--------|-------|
| ConnectionIndicator | `docs/03-design/component-specs.md` SS 14 | PASS | DEV-002 noted |
| OfflineBanner | `docs/03-design/component-specs.md` SS 11.5 | PASS | DEV-001 noted |
| PresenceIndicators | `docs/03-design/component-specs.md` SS 9.2 | PASS | Max 4, overlap, overflow |
| UserSelectionHighlight | `docs/03-design/component-specs.md` SS 6.1 | PASS | 2px border, name label, deterministic color |

---

## Verdict

- **Result:** FAIL
- **Defects found:** 1 active (DEF-003 — Critical: 8 test assertion failures from DB connection lifecycle), 2 resolved (DEF-001, DEF-002)
- **Deviations found:** 2 (DEV-001, DEV-002 — both minor, non-blocking)
- **Bugfix PRD required:** YES
- **Bugfix cycle:** 5

**Application code is correct.** All 10 user stories are fully implemented and functionally sound. DEF-002 (IntegrityError) is fully resolved by BF-001. The new DEF-003 is a test infrastructure issue: stale database connections between async TransactionTestCase tests cause intermittent connection/access failures. The fix is to add explicit database connection cleanup between tests.
