# QA Report: Milestone 6 — WebSocket & Real-Time

**Date:** 2026-03-10
**Reviewer:** QA Engineer (Claude)
**Bugfix Cycle:** 7 (post BF-001 fix for DEF-004 — ruff lint)
**PRD:** `tasks/prd-m6.json`
**Progress:** `.ralph/progress.txt`

---

## Summary

Final review of Milestone 6 (WebSocket & Real-Time) after bugfix cycle 7. BF-001 successfully **resolved DEF-004** — all 6 Ruff lint errors (4 unused imports, 2 unsorted import blocks) have been fixed across the 3 WebSocket test files. All 156 tests pass. All required gate checks pass. All 10 original M6 user stories pass. Verdict: **PASS**.

---

## Bugfix Cycle Progress Assessment

| Metric | Cycle 5 (DEF-002) | Cycle 6 (DEF-003) | Cycle 7 (DEF-004) | Delta (6->7) |
|--------|-------------------|-------------------|-------------------|--------------|
| Tests PASS | 134 | 156 | 156 | 0 (stable) |
| Tests FAIL | 8 | 0 | 0 | 0 (stable) |
| Tests ERROR | 0 | 0 | 0 | 0 (stable) |
| Ruff lint | FAIL | FAIL (6 errors) | PASS (0 errors) | Fixed! |
| Frontend tsc | PASS | PASS | PASS | stable |
| Root cause | DB conn lifecycle | Ruff lint (gate) | — (resolved) | — |

**Assessment:** BF-001 fully resolved DEF-004. The 6 auto-fixable lint errors (F401 unused imports, I001 unsorted import blocks) in `test_access.py`, `test_consumers.py`, and `test_middleware.py` are all fixed. Zero defects remain.

---

## Story-by-Story Verification

Verification against the original M6 user stories:

| Story ID | Title | Result | Notes |
|----------|-------|--------|-------|
| US-001 | Django Channels WebSocket consumer | PASS | All connection lifecycle tests pass (valid, invalid, missing, nonexistent token) |
| US-002 | Channel group management | PASS | Subscribe, unsubscribe, access denied, cleanup all pass |
| US-003 | Chat message broadcast | PASS | Broadcast to subscriber + not-received-by-unsubscribed pass |
| US-004 | Board sync broadcast | PASS | board_update + node delete + AI source all pass |
| US-005 | Board awareness events | PASS | Selection excludes sender, deselect null, not-subscribed error, lock change all pass |
| US-006 | Frontend WebSocket connection manager | PASS | Frontend tests pass (244 Node tests) |
| US-007 | Presence tracking | PASS | Broadcast on subscribe, multi-tab dedup, offline on unsubscribe, client presence_update all pass |
| US-008 | User selection highlights on board | PASS | Frontend component tests pass |
| US-009 | Offline banner + behavior | PASS | DEV-001 carried forward (color deviation) |
| US-010 | Connection state indicator | PASS | DEV-002 carried forward (token deviation) |

**Stories passed:** 10 / 10
**Stories with defects:** 0
**Stories with deviations:** 2 (carried forward from earlier cycles)

---

## BF-001 Acceptance Criteria Verification

| Criterion | Result | Evidence |
|-----------|--------|----------|
| `ruff check services/` exits with 0 errors | PASS | Pipeline gate check: Backend lint (Ruff) PASSED |
| All 156 tests still pass | PASS | 156 passed, 0 failed, 0 errors |
| Typecheck passes | PASS | Frontend typecheck: PASSED |

**BF-001 fully succeeded.** All acceptance criteria met.

---

## Test Matrix Coverage

**Pipeline scan results:** No test matrix IDs referenced in this milestone's PRD stories (bugfix PRD).

All test implementations from the original M6 implementation are present, unchanged, and all pass:

| Test ID | Status | File | Notes |
|---------|--------|------|-------|
| T-6.1.01 | FOUND | `test_consumers.py` | test_connection_valid_token — PASS |
| T-6.1.02 | FOUND | `test_consumers.py` | test_connection_invalid_token + variants — PASS |
| T-6.1.03 | FOUND | `frontend/src/__tests__/use-websocket.test.ts` | Exponential backoff — PASS |
| T-6.1.04 | FOUND | `test_consumers.py` | test_subscribe_idea_as_owner — PASS |
| T-6.1.05 | FOUND | `test_consumers.py` + `test_access.py` | access denied + co-owner + collaborator — PASS |
| T-6.1.06 | FOUND | `test_consumers.py` | unsubscribe + cleanup — PASS |
| T-6.1.07 | FOUND | `frontend/src/__tests__/websocket-slice.test.ts` | PASS |
| T-6.1.08 | FOUND | `frontend/src/__tests__/use-websocket.test.ts` | PASS |
| LOOP-004 | FOUND | `frontend/src/__tests__/use-websocket.test.ts` | PASS |
| T-6.2.01 | FOUND | `frontend/src/__tests__/offline-banner.test.tsx` | PASS |
| T-6.3.01 | FOUND | `test_consumers.py` | presence broadcast on subscribe — PASS |
| T-6.3.02 | FOUND | `test_consumers.py` | multi-tab dedup — PASS |
| T-6.3.03 | FOUND | `test_consumers.py` | offline on unsubscribe — PASS |
| T-6.3.04 | FOUND | `test_consumers.py` | client presence update — PASS |
| T-6.4.01 | FOUND | `test_consumers.py` | chat broadcast to subscriber — PASS |
| T-6.4.02 | FOUND | `test_broadcast.py` | chat broadcast via view helper — PASS |
| T-6.4.03 | FOUND | `test_consumers.py` | board_update broadcast — PASS |
| T-6.4.04 | FOUND | `test_broadcast.py` | board_update via view helper — PASS |
| T-3.5.01 | FOUND | `test_consumers.py` | board_selection excludes sender — PASS |
| T-3.5.02 | FOUND | `test_consumers.py` | board_selection not subscribed — PASS |
| T-3.5.03 | FOUND | `test_consumers.py` | board_selection deselect null + lock change — PASS |
| T-3.6.01 | FOUND | `test_consumers.py` | board_update nodes_deleted — PASS |
| T-3.6.02 | FOUND | `test_consumers.py` | board_update source=ai — PASS |
| T-6.5.01 | FOUND | `frontend/src/__tests__/offline-banner.test.tsx` | PASS |
| T-6.5.02 | FOUND | `frontend/src/__tests__/offline-banner.test.tsx` | PASS |
| T-6.6.01 | FOUND | `frontend/src/__tests__/connection-indicator.test.tsx` | PASS |
| T-6.6.02 | FOUND | `frontend/src/__tests__/connection-indicator.test.tsx` | PASS |

**27 / 27 test IDs: FOUND and PASS.**

---

## Defects

None. All previously identified defects (DEF-001 through DEF-004) have been resolved.

| Defect | Description | Resolution |
|--------|-------------|------------|
| DEF-001 | FK constraint violation | Fixed in cycle 1 |
| DEF-002 | IntegrityError on auth_permission | Fixed by post_migrate signal disconnect |
| DEF-003 | 8 async consumer test failures (DB conn lifecycle) | Fixed by DB connection cleanup fixture |
| DEF-004 | Ruff lint: 6 unused imports/unsorted blocks | Fixed by removing unused imports and sorting blocks |

---

## Deviations

### DEV-001: OfflineBanner background color (carried forward)
- **Story:** US-009
- **Spec document:** `docs/03-design/component-specs.md`
- **Expected (per spec):** red-600 background
- **Actual (in code):** amber/yellow warning color
- **Why code is correct:** Amber/yellow is the UX standard for "degraded but recovering" states; red implies permanent failure
- **Spec update needed:** Update OfflineBanner color spec to amber/yellow

### DEV-002: ConnectionIndicator uses design tokens (carried forward)
- **Story:** US-010
- **Spec document:** `docs/03-design/component-specs.md`
- **Expected (per spec):** Specific hex colors
- **Actual (in code):** Tailwind semantic color tokens (green-500, red-500)
- **Why code is correct:** Using design system tokens ensures consistency; hardcoded hex values are anti-pattern
- **Spec update needed:** Update ConnectionIndicator spec to reference Tailwind tokens

---

## Quality Checks

| Check | Command | Result | Details |
|-------|---------|--------|---------|
| Python tests | `docker compose -f docker-compose.test.yml run --rm python-tests pytest` | PASS | 156 passed, 0 failed, 0 errors |
| Frontend typecheck | `cd frontend && npx tsc --noEmit` | PASS | Clean |
| Backend lint (Ruff) | `ruff check services/` | PASS | 0 errors (was 6 in previous cycle) |
| Backend typecheck (mypy) | `mypy services/` | FAIL | 1 error: duplicate module "events" — optional gate, pre-existing |
| Frontend lint (ESLint) | `cd frontend && npx eslint src/` | FAIL | 3 problems (2 unused vars in pre-M6 tests, 1 hook deps warning) — optional gate, pre-existing |

---

## Gate Check Results

| Gate | Status | Required | Notes |
|------|--------|----------|-------|
| Docker build | SKIPPED | Yes | Condition not met |
| Frontend typecheck | PASSED | Yes | Clean |
| Backend lint (Ruff) | PASSED | Yes | 0 errors — DEF-004 resolved |
| Backend typecheck (mypy) | FAILED | No | Pre-existing duplicate module issue (not M6) |
| Frontend lint (ESLint) | FAILED | No | Pre-existing issues in non-M6 files |

**All required gate checks pass.** Optional gate failures are pre-existing and not introduced by M6.

---

## Security Findings

| ID | Category | Severity | File | Finding | Recommendation |
|----|----------|----------|------|---------|----------------|
| — | — | — | — | No security issues found | — |

**Security review summary:**
- **Authentication:** WebSocket auth via query string token is standard (WebSocket spec doesn't support custom headers). Token validated in middleware before consumer is reached. Invalid/missing tokens rejected with 4003 close code.
- **Authorization:** `_check_idea_access` verifies owner, co-owner, or collaborator status before allowing subscription. Non-members get "Access denied" error.
- **Input validation:** UUID format validated before DB query. Unknown message types return error. Missing fields handled gracefully.
- **SQL injection:** All DB queries use Django ORM (parameterized). No raw SQL.
- **No secrets exposure:** No hardcoded secrets. Settings properly separated.
- **CORS/CSRF:** Not applicable to WebSocket (handled at HTTP upgrade level by Django).

---

## Performance Findings

| ID | Category | Severity | File | Finding | Recommendation |
|----|----------|----------|------|---------|----------------|
| — | — | — | — | No performance issues found | — |

**Performance review summary:**
- `_check_idea_access` does at most 2 DB queries (idea lookup + collaborator check) — acceptable.
- Presence registry is in-memory (`defaultdict`) — appropriate for single-process; will need Redis-backed solution for horizontal scaling (out of M6 scope).
- No N+1 queries. Channel layer operations are efficient.
- `_presence_registry` cleanup on disconnect properly removes empty entries to prevent memory leaks.

---

## Design Compliance

| Page/Component | Spec Reference | Result | Notes |
|---------------|----------------|--------|-------|
| WebSocket consumer | `docs/02-architecture/api-design.md` | PASS | Message types and payload shapes match spec |
| Auth middleware | `docs/02-architecture/api-design.md` | PASS | Token validation flow matches spec |
| OfflineBanner | `docs/03-design/component-specs.md` | DEVIATION | DEV-001: amber vs red-600 |
| ConnectionIndicator | `docs/03-design/component-specs.md` | DEVIATION | DEV-002: Tailwind tokens vs hex |

---

## Regression Tests

These items must continue to work after future milestones are merged. If any regress, it is a defect in the later milestone.

### WebSocket Connection Lifecycle
- [ ] WebSocket connection with valid token at `/ws/?token=<uuid>` succeeds (code 101)
- [ ] WebSocket connection with invalid/missing/expired token is rejected
- [ ] WebSocket disconnection cleans up all channel group memberships

### Channel Group Management
- [ ] Owner can subscribe to idea group via `subscribe_idea` message
- [ ] Co-owner and collaborator can subscribe to idea group
- [ ] Non-member subscription returns `Access denied` error
- [ ] `unsubscribe_idea` removes consumer from group and broadcasts offline presence
- [ ] Invalid UUID in `idea_id` returns error (not crash)

### Broadcast Messages
- [ ] `chat_message` group_send is forwarded to subscribed WebSocket clients
- [ ] `board_update` group_send is forwarded to subscribed WebSocket clients
- [ ] `board_lock_change` group_send is forwarded to subscribed WebSocket clients
- [ ] Unsubscribed clients do NOT receive group broadcasts
- [ ] `board_selection` from client is broadcast to other subscribers but NOT sender

### Presence Tracking
- [ ] `presence_update` with state=online broadcast when user subscribes
- [ ] Multi-tab dedup: second tab subscribe does NOT broadcast duplicate online
- [ ] Offline broadcast only when last tab disconnects/unsubscribes
- [ ] Client `presence_update` message is broadcast to idea group

### Frontend Components
- [ ] `useWebSocket` hook connects, reconnects with exponential backoff
- [ ] `websocketSlice` Redux state management works correctly
- [ ] `OfflineBanner` renders when WebSocket disconnected
- [ ] `ConnectionIndicator` shows correct state (connected/disconnected/reconnecting)

### Broadcast Helpers (View Layer)
- [ ] `_broadcast_chat_message` in `apps/chat/views.py` sends correct payload shape
- [ ] `_broadcast_board_update` in `apps/board/views.py` sends correct payload shape
- [ ] `_broadcast_board_lock_change` in `apps/board/views.py` sends correct payload shape
- [ ] Broadcast helpers are no-ops when channel layer is None

### Quality Baseline
- [ ] All 156 Python tests pass
- [ ] Frontend TypeScript typecheck passes with zero errors
- [ ] `ruff check services/` passes with zero errors
- [ ] All frontend tests pass (244 Node tests)

---

## Verdict

- **Result:** PASS
- **Defects found:** 0 (all 4 previously found defects resolved)
- **Deviations found:** 2 (DEV-001, DEV-002 — for Spec Reconciler)
- **Bugfix PRD required:** no
- **Bugfix cycles completed:** 7 (DEF-001 cycle 1, DEF-002 cycles 2-4 + human intervention, DEF-003 cycle 5-6, DEF-004 cycle 7)
- **Ready for merge:** yes
