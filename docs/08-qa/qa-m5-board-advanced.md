# QA Report: Milestone 5 — Board Advanced

**Date:** 2026-03-10
**Reviewer:** QA Engineer (Claude)
**Bugfix Cycle:** 1
**PRD:** tasks/prd-m5.json
**Progress:** .ralph/progress.txt

---

## Summary

Bugfix cycle 1 review for M5 (Board Advanced). The single defect from cycle 0 (DEF-001: locked nodes cannot be unlocked via PATCH API) has been fixed. The fix correctly allows `is_locked`-only PATCH requests to bypass the lock check while still rejecting mixed updates. All 110 backend tests and 191 frontend tests pass. All required gate checks pass.

---

## Story-by-Story Verification

| Story ID | Title | Result | Notes |
|----------|-------|--------|-------|
| BF-001 | Fix: Allow lock toggle on locked nodes via PATCH API | PASS | Lock bypass logic at `views.py:199-207`. Two new tests added (lines 252, 271). All 6 acceptance criteria verified. |

**Stories passed:** 1 / 1
**Stories with defects:** 0
**Stories with deviations:** 0

### BF-001 Acceptance Criteria Detail

| # | Criterion | Result | Evidence |
|---|-----------|--------|----------|
| 1 | PATCH {is_locked: false} on locked node returns 200 and unlocks | PASS | `test_unlock_locked_node_returns_200` (test_views.py:252) — asserts 200, is_locked=False in response and DB |
| 2 | PATCH {title: 'new'} on locked node returns 403 NODE_LOCKED | PASS | `test_update_locked_node_returns_403` (test_views.py:240) — pre-existing test, still passes |
| 3 | PATCH {is_locked: true, title: 'new'} on locked node returns 403 | PASS | `test_lock_toggle_with_other_fields_on_locked_node_returns_403` (test_views.py:271) — new test |
| 4 | New backend test: test_unlock_locked_node_returns_200 | PASS | Present at test_views.py:252 |
| 5 | All existing backend tests still pass | PASS | 110 passed (pipeline output) |
| 6 | Typecheck passes | PASS | Frontend typecheck gate PASSED |

---

## Test Matrix Coverage

**Pipeline scan results:** No test matrix IDs referenced in bugfix PRD

This bugfix cycle did not introduce new test matrix IDs. The 13 test IDs from the original M5 review (T-3.2.01 through T-3.8.02) remain FOUND and verified from cycle 0.

| Test ID | Status | File | Notes |
|---------|--------|------|-------|
| T-3.2.01 | FOUND | `frontend/src/__tests__/board-interactions.test.tsx` | Drag position — unchanged |
| T-3.2.02 | FOUND | `frontend/src/__tests__/board-interactions.test.tsx` | Drag into group — unchanged |
| T-3.2.03 | FOUND | `frontend/src/__tests__/board-interactions.test.tsx` | Drag out of group — unchanged |
| T-3.2.07 | FOUND | `frontend/src/__tests__/board-interactions.test.tsx` | Lock toggle — unchanged |
| T-3.4.01 | FOUND | `frontend/src/__tests__/ai-modified-indicator.test.tsx` | AI indicator visible — unchanged |
| T-3.4.02 | FOUND | `frontend/src/__tests__/ai-modified-indicator.test.tsx` | Indicator clears on click — unchanged |
| T-3.7.01 | FOUND | `frontend/src/__tests__/board-undo.test.ts` | Undo reverses action — unchanged |
| T-3.7.02 | FOUND | `frontend/src/__tests__/board-undo.test.ts` | Redo reapplies — unchanged |
| T-3.7.03 | FOUND | `frontend/src/__tests__/board-toolbar-undo.test.tsx` | AI action label — unchanged |
| T-3.7.04 | FOUND | `frontend/src/__tests__/board-undo.test.ts` | Stack bounded at 100 — unchanged |
| T-3.7.05 | FOUND | `frontend/src/__tests__/board-undo-integration.test.ts` | Undo sends PATCH — unchanged |
| T-3.8.01 | FOUND | `frontend/src/__tests__/chat-board-reference.test.tsx` | Reference button — unchanged |
| T-3.8.02 | FOUND | `frontend/src/__tests__/chat-board-reference.test.tsx` | @board[uuid] insertion — unchanged |

---

## Defects

None.

---

## Deviations

None.

---

## Quality Checks

| Check | Command | Result | Details |
|-------|---------|--------|---------|
| Backend Tests (pytest) | `docker compose -f docker-compose.test.yml run --rm python-tests pytest` | PASS | 110 passed in 5.01s |
| Frontend TypeScript | `cd frontend && npx tsc --noEmit` | PASS | Clean |
| Backend Lint (Ruff) | `ruff check services/` | PASS | Clean |
| Backend Typecheck (mypy) | `mypy services/` | SKIPPED (optional) | Pre-existing: duplicate module name `events` between core/ai services |
| Frontend Lint (ESLint) | `cd frontend && npx eslint src/` | INFO (optional) | 2 errors (unused vars in test files), 1 warning (missing useEffect dep) — pre-existing from M5, not introduced by bugfix |

### Gate Check Results

| Gate | Status | Notes |
|------|--------|-------|
| Docker build | SKIPPED | Condition not met |
| Frontend typecheck | PASSED | Required gate |
| Backend lint (Ruff) | PASSED | Required gate |
| Backend typecheck (mypy) | FAILED (optional) | Pre-existing duplicate module name — not M5 related |
| Frontend lint (ESLint) | FAILED (optional) | Pre-existing from M5 original implementation — not introduced by bugfix |

All **required** gate checks pass.

---

## Security Findings

| ID | Category | Severity | File | Finding | Recommendation |
|----|----------|----------|------|---------|----------------|
| — | — | — | — | No new security issues in bugfix | — |

**Notes:**
- The lock bypass uses strict equality (`request_fields == {"is_locked"}`), ensuring only pure lock-toggle requests skip the lock check
- Mixed updates (is_locked + other fields) on locked nodes are still rejected with 403
- Authentication and authorization checks remain in place before the lock check

---

## Performance Findings

| ID | Category | Severity | File | Finding | Recommendation |
|----|----------|----------|------|---------|----------------|
| — | — | — | — | No performance issues | — |

**Notes:**
- The bugfix adds a lightweight set comparison (`set(request.data.keys()) == {"is_locked"}`) — negligible overhead

---

## Design Compliance

No design changes in this bugfix cycle. All design compliance items from cycle 0 remain PASS.

---

## Regression Tests

These items must continue to work after future milestones are merged.

### Pages & Navigation
- [ ] Board canvas still renders with dot background at 20px gap
- [ ] Box, Group, FreeText nodes still render correctly with all data props

### API Endpoints
- [ ] PATCH node with `{is_locked: false}` on locked node returns 200 and unlocks
- [ ] PATCH node with other fields on locked node returns 403 NODE_LOCKED
- [ ] PATCH node with `{is_locked: true, title: "x"}` on locked node returns 403
- [ ] Node CRUD API endpoints still return expected shapes (GET, POST, PATCH, DELETE)
- [ ] Connection CRUD API endpoints still work correctly

### Features
- [ ] Drag to move nodes persists position via PATCH
- [ ] Group nesting (drag into/out of groups) works with visual feedback
- [ ] Node lock toggle works on all 3 node types (lock and unlock)
- [ ] Multi-select with Ctrl+drag selection box works
- [ ] Undo/redo reverses and reapplies board actions with PATCH persistence
- [ ] Undo/redo buttons show context-aware labels for AI actions
- [ ] Board item reference inserts `@board[uuid]` into chat input
- [ ] AI modification indicators (gold dot) appear and clear on click
- [ ] Chat input still sends messages and shows mention dropdown

### Data Integrity
- [ ] Board nodes schema unchanged (all columns, types, constraints)
- [ ] Board connections schema unchanged

### Quality Baseline
- [ ] TypeScript typecheck passes with zero errors
- [ ] All 191 frontend tests pass
- [ ] All 110 backend tests pass
- [ ] Ruff lint passes
- [ ] Build completes successfully

---

## Verdict

- **Result:** PASS
- **Defects found:** 0
- **Deviations found:** 0
- **Bugfix PRD required:** no
- **Bugfix cycle:** 1 (DEF-001 from cycle 0 fixed successfully)
